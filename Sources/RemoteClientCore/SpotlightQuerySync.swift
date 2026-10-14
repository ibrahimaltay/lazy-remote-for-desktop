import Foundation

/// Keeps the Mac's Spotlight field equal to the overlay's query (cleaned, deduped) and
/// presses Enter for "go" once the Mac's results have settled on that query.
@MainActor
public final class SpotlightQuerySync {
    static let maxBytes = 256
    /// No new snapshot for this long after `typed == query` counts as settled.
    static let settleDelay: TimeInterval = 0.3
    /// Enter goes out anyway after this long (a slow search may open the wrong hit).
    static let goTimeout: TimeInterval = 2

    private let send: (String) -> Void
    private let enter: () -> Void
    private let now: () -> TimeInterval
    private var lastSent: String?
    private var typed: String?
    private var snapshotAt: TimeInterval = 0
    private var goStarted: TimeInterval?

    /// The cleaned query the Mac should show.
    public private(set) var query = ""
    public var isGoPending: Bool { goStarted != nil }

    public init(
        send: @escaping (String) -> Void,
        enter: @escaping () -> Void,
        now: @escaping () -> TimeInterval = { ProcessInfo.processInfo.systemUptime }
    ) {
        self.send = send
        self.enter = enter
        self.now = now
    }

    /// The overlay opened: forget everything and clear the Mac's field.
    public func open() {
        reset()
        query = ""
        push()
    }

    public func update(_ raw: String) {
        var text = ""
        for character in raw {
            // A newline would press Return and open the top hit.
            let isLine = character.unicodeScalars.allSatisfy { CharacterSet.newlines.contains($0) }
            let next = isLine ? " " : String(character)
            guard text.utf8.count + next.utf8.count <= Self.maxBytes else { break }
            text += next
        }
        query = text
        push()
    }

    public func snapshot(typed: String) {
        self.typed = typed
        snapshotAt = now()
        tick()
    }

    /// Starts a pending Enter; false (and nothing pending) for an empty query.
    @discardableResult
    public func go() -> Bool {
        guard !query.isEmpty else { return false }
        goStarted = now()
        tick()
        return true
    }

    /// Call while `isGoPending`; fires Enter once when settled or timed out.
    public func tick() {
        guard let started = goStarted else { return }
        let settled = typed == query && now() - snapshotAt >= Self.settleDelay
        guard settled || now() - started >= Self.goTimeout else { return }
        goStarted = nil
        enter()
    }

    /// Cancels a pending Enter and forgets what was sent, so the next `update` resends.
    public func reset() {
        goStarted = nil
        lastSent = nil
        typed = nil
    }

    private func push() {
        guard query != lastSent else { return }
        lastSent = query
        typed = nil // results shown so far are for an older query; wait for a fresh snapshot
        send(query)
    }
}
