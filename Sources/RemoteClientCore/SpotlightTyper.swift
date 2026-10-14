import Foundation
import RemoteProtocol

/// Mirrors the Spotlight overlay's query onto the Mac as live edits: a diff over the text
/// the Mac already has, sent as backspace keys plus one untrimmed text, one text in flight.
@MainActor
public final class SpotlightTyper {
    private static let maxBytes = 256

    private let sendText: (String) -> Bool
    private let tap: (Command) -> Void
    private var mac = ""
    /// The Mac text before the text in flight, restored if that send fails.
    private var macBeforeSend = ""
    private var target = ""
    public private(set) var inFlight = false
    private var enterArmed = false
    /// The Mac's text is leftover we did not type, so nothing in it can be reused.
    private var dirty = false
    /// Nothing sent since open/reconnect: the first snapshot may reveal leftover text.
    private var fresh = true

    public init(sendText: @escaping (String) -> Bool, tap: @escaping (Command) -> Void) {
        self.sendText = sendText
        self.tap = tap
    }

    public func update(_ query: String) {
        var text = ""
        for character in query {
            // A newline would press Return and open the top hit.
            let isLine = character.unicodeScalars.allSatisfy { CharacterSet.newlines.contains($0) }
            let next = isLine ? " " : String(character)
            guard text.utf8.count + next.utf8.count <= Self.maxBytes else { break }
            text += next
        }
        target = text
        flush()
    }

    /// Enter goes out only once the Mac's text equals the query and nothing is in flight.
    public func go() {
        enterArmed = true
        flush()
    }

    /// Feed every text receipt; receipts of sends this typer did not make are ignored.
    public func textDelivered(_ delivered: Bool) {
        guard inFlight else { return }
        inFlight = false
        guard delivered else {
            // The Mac may not have the text: forget it so Enter cannot fire until a resend.
            mac = macBeforeSend
            enterArmed = false
            return
        }
        flush()
    }

    /// Drops edits not yet sent (the overlay closed with Mac Spotlight, so keys would hit
    /// another app). A pending Enter from `go()` keeps its edits.
    public func stop() {
        if !enterArmed { target = mac }
    }

    /// Adopts the Mac's typed text from the first snapshot, before anything was sent.
    public func macTyped(_ typed: String) {
        guard fresh, !inFlight, !typed.isEmpty else { return }
        mac = typed
        dirty = true
        fresh = false
    }

    /// Keeps `inFlight`: its receipt is still coming and must not be mistaken for a new one.
    public func reset() {
        mac = ""
        macBeforeSend = ""
        target = ""
        enterArmed = false
        dirty = false
        fresh = true
    }

    private func flush() {
        if target.isEmpty { enterArmed = false }
        guard !inFlight else { return }
        let old = Array(mac), new = Array(target)
        var shared = 0
        if !dirty {
            while shared < min(old.count, new.count), old[shared] == new[shared] { shared += 1 }
        }
        if shared < old.count || shared < new.count { fresh = false }
        for _ in shared..<old.count { tap(.backspace) }
        mac = String(old[..<shared])
        dirty = false
        if shared < new.count {
            macBeforeSend = mac
            guard sendText(String(new[shared...])) else {
                enterArmed = false
                return
            }
            mac = target
            inFlight = true
        } else if enterArmed, !target.isEmpty {
            enterArmed = false
            tap(.enter)
        }
    }
}
