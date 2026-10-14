import RemoteClientCore
import RemoteProtocol
import SwiftUI
import UIKit

@MainActor
@Observable
final class RemoteViewModel {
    private(set) var status: RemoteClient.Status = .stopped
    /// What the Mac's Spotlight shows; nil unless the overlay is open.
    private var spotlightResults: SpotlightResults?
    /// The list to draw: only for a non-empty query the Mac has caught up with. Keeps the
    /// last matching list while a newer one loads.
    private(set) var spotlightCard: SpotlightResults?

    private let client = RemoteClient()
    private let tuning = TrackpadTuning.bundled
    private let haptics = UIImpactFeedbackGenerator(style: .rigid)
    /// Bumped when the phone field must be cleared because an edit was dropped.
    private(set) var textResetCount = 0
    @ObservationIgnored private var liveText = LiveTextSync()
    private var isSpotlightOpen = false
    /// Set when the overlay closed while "go" was pending; watch-off waits for the Enter.
    private var closeAfterGo = false
    @ObservationIgnored private lazy var spotlight = SpotlightQuerySync(
        send: { [unowned self] in
            if self.isConnected { self.client.setSpotlightQuery($0) }
        },
        enter: { [unowned self] in self.client.tap(.enter) })

    var isConnected: Bool {
        if case .connected = status { return true }
        return false
    }

    var statusText: String {
        switch status {
        case .stopped: "Off"
        case .poweredOff: "Turn on Bluetooth"
        case .unauthorized: "Allow Bluetooth in Settings"
        case .unsupported: "Bluetooth not supported"
        case .scanning: "Looking for your Mac…"
        case .connecting(let name): "Connecting to \(name)…"
        case .securing(let name): "Securing connection to \(name)…"
        case .failed(let message): message
        case .awaitingApproval(let name): "Allow this iPhone on \(name)"
        case .connected(let name): name
        }
    }

    init() {
        client.onStatus = { [weak self] status in
            // RemoteClient always reports on the main queue.
            MainActor.assumeIsolated {
                guard let self else { return }
                self.status = status
                if !self.isConnected {
                    self.spotlight.reset()
                    self.spotlightResults = nil
                    self.updateSpotlightCard()
                } else if self.isSpotlightOpen {
                    self.client.setSpotlightWatch(true)
                    self.spotlight.update(self.spotlight.query)
                }
                UIApplication.shared.isIdleTimerDisabled = self.isConnected
            }
        }
        client.onTextEditDropped = { [weak self] in
            // RemoteClient always reports on the main queue.
            MainActor.assumeIsolated {
                self?.liveText.reset()
                self?.textResetCount += 1
            }
        }
        client.onSpotlightResults = { [weak self] results in
            // RemoteClient always reports on the main queue.
            MainActor.assumeIsolated {
                guard let self, self.isSpotlightOpen else { return }
                self.spotlightResults = results
                self.spotlight.snapshot(typed: results.typed)
                self.updateSpotlightCard()
            }
        }
        haptics.prepare()
    }

    /// Asks the Mac for its Spotlight results while the overlay is open.
    func setSpotlightOpen(_ isOpen: Bool) {
        if isOpen {
            closeAfterGo = false
            isSpotlightOpen = true
            if isConnected { client.setSpotlightWatch(true) }
            spotlight.open()
        } else if spotlight.isGoPending {
            closeAfterGo = true
            return
        } else {
            isSpotlightOpen = false
            spotlightResults = nil
            if isConnected { client.setSpotlightWatch(false) }
        }
        updateSpotlightCard()
    }

    func start() {
        client.start()
    }

    func stop() {
        client.stop()
        UIApplication.shared.isIdleTimerDisabled = false
    }

    func reconnect() {
        client.stop()
        client.start()
    }

    func forgetMac() {
        client.forgetMac()
    }

    func press(_ command: Command) {
        haptics.impactOccurred()
        client.send(KeyEvent(command: command, isDown: true))
    }

    func release(_ command: Command) {
        client.send(KeyEvent(command: command, isDown: false))
    }

    /// `feedback` is off while a key auto-repeats, where a buzz per press would be
    /// a continuous rumble.
    func tap(_ command: Command, feedback: Bool = true) {
        guard isConnected else { return }
        if feedback { haptics.impactOccurred() }
        client.tap(command)
    }

    func moveCursor(by translation: CGPoint, velocity: CGPoint) {
        guard isConnected else { return }
        let gain = tuning.cursor.gain(forFingerSpeed: hypot(velocity.x, velocity.y))
        client.move(dx: translation.x * gain, dy: translation.y * gain)
    }

    func scroll(by translation: CGPoint, velocity: CGPoint, phase: RemoteProtocol.ScrollPhase) {
        guard isConnected else { return }
        let delta = scrollContent(translation, fingerVelocity: velocity)
        client.scroll(dx: delta.x, dy: delta.y, phase: phase)
    }

    /// Nil when the release was too slow to coast or momentum is turned off.
    func momentum(afterReleaseAt velocity: CGPoint, fingerTravel: Double) -> ScrollMomentum? {
        guard isConnected else { return nil }
        let content = scrollContent(velocity, fingerVelocity: velocity)
        return ScrollMomentum(velocityX: content.x, velocityY: content.y, fingerTravel: fingerTravel, tuning: tuning.scroll.momentum)
    }

    /// Momentum deltas are already in Mac pixels, so no gain is applied.
    func coast(dx: Double, dy: Double, phase: RemoteProtocol.ScrollPhase) {
        client.scroll(dx: dx, dy: dy, phase: phase)
    }

    /// Finger travel in points to content travel in Mac pixels.
    private func scrollContent(_ value: CGPoint, fingerVelocity: CGPoint) -> CGPoint {
        let gain = tuning.scroll.gain.gain(forFingerSpeed: hypot(fingerVelocity.x, fingerVelocity.y))
        let sign: Double = tuning.scroll.naturalDirection ? 1 : -1
        return CGPoint(x: value.x * gain * sign, y: value.y * gain * sign)
    }

    func click(_ button: MouseButton, count: UInt8) {
        guard isConnected else { return }
        haptics.impactOccurred()
        client.click(button, count: count)
    }

    var gestures: TrackpadTuning.Gestures { tuning.gestures }

    func swipe(_ direction: SwipeDirection) {
        guard isConnected else { return }
        haptics.impactOccurred()
        client.swipe(direction)
    }

    func beginDrag() {
        guard isConnected else { return }
        haptics.impactOccurred()
        client.press(.left, isDown: true)
    }

    /// Not gated on the connection: a release must never be skipped.
    func endDrag() {
        client.press(.left, isDown: false)
    }

    /// The phone field's text changed: mirror the difference on the Mac, live.
    func textChanged(_ text: String) {
        guard isConnected else { return liveText.reset(to: text) }
        for edit in liveText.update(text) { client.sendEdit(delete: edit.delete, insert: edit.insert) }
    }

    /// Backspace in an empty phone field still deletes on the Mac.
    func emptyBackspace() {
        guard isConnected else { return }
        let edit = liveText.emptyBackspace()
        client.sendEdit(delete: edit.delete, insert: edit.insert)
    }

    /// The phone field was cleared or replaced locally; send nothing.
    func resetText() { liveText.reset() }

    /// Sets the Mac's Spotlight field to the overlay's query.
    func typeSpotlight(_ query: String) {
        spotlight.update(query)
        updateSpotlightCard()
    }

    /// Presses Enter once the Mac's results have settled on the query (or after a timeout).
    func goSpotlight() {
        guard !spotlight.isGoPending, spotlight.go() else { return }
        Task {
            while spotlight.isGoPending {
                try? await Task.sleep(for: .milliseconds(100))
                spotlight.tick()
            }
            if closeAfterGo { setSpotlightOpen(false) }
        }
    }

    private func updateSpotlightCard() {
        if spotlight.query.isEmpty {
            spotlightCard = nil
        } else if let results = spotlightResults, results.typed == spotlight.query {
            spotlightCard = results
        }
    }
}
