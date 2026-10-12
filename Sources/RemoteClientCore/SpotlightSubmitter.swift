/// Types text into Spotlight, then presses Enter once, only after the Mac confirms the text.
@MainActor
public final class SpotlightSubmitter {
    private let send: (String) -> Bool
    private let pressEnter: () -> Void
    private var armed = false

    public init(send: @escaping (String) -> Bool, pressEnter: @escaping () -> Void) {
        self.send = send
        self.pressEnter = pressEnter
    }

    public func submit(_ text: String) {
        armed = send(text)
    }

    /// Feed every text delivery result; Enter fires at most once per submit.
    public func textDelivered(_ delivered: Bool) {
        guard armed else { return }
        armed = false
        if delivered { pressEnter() }
    }

    /// Drop a pending Enter (e.g. on disconnect) so a later plain send never presses it.
    public func reset() { armed = false }
}
