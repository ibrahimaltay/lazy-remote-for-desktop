import Foundation
import RemoteProtocol

/// Turns the phone field's text changes into edits at the end of the Mac's focused text.
/// The phone cursor is kept at the end (otherwise the caller re-baselines), so only the
/// common prefix matters: everything after it is deleted and retyped.
public struct LiveTextSync: Sendable {
    public struct Edit: Sendable, Equatable {
        public let delete: Int
        public let insert: String
    }

    public private(set) var text = ""

    public init() {}

    /// Edits that take the Mac from `text` to `new`, split to the wire limits; empty if unchanged.
    public mutating func update(_ new: String) -> [Edit] {
        let old = Array(text)
        let target = Array(new)
        let common = zip(old, target).prefix { $0 == $1 }.count
        text = new
        var remaining = old.count - common
        var edits: [Edit] = []
        var insert = ""
        for character in target[common...] {
            let next = String(character)
            if insert.utf8.count + next.utf8.count > SecureMessage.maxTextEditInsertBytes {
                edits.append(Edit(delete: Self.take(&remaining), insert: insert))
                insert = ""
            }
            insert += next
        }
        if !insert.isEmpty || remaining > 0 { edits.append(Edit(delete: Self.take(&remaining), insert: insert)) }
        while remaining > 0 { edits.append(Edit(delete: Self.take(&remaining), insert: "")) }
        return edits
    }

    /// Backspace pressed in an empty phone field: deletes one on the Mac.
    public func emptyBackspace() -> Edit { Edit(delete: 1, insert: "") }

    /// Forgets what was sent without sending anything (cursor moved, bar closed, reconnect).
    public mutating func reset(to text: String = "") { self.text = text }

    private static func take(_ remaining: inout Int) -> Int {
        let n = min(remaining, SecureMessage.maxTextEditDelete)
        remaining -= n
        return n
    }
}
