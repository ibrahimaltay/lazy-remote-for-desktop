import CoreGraphics
import Foundation
import RemoteProtocol

/// What Spotlight shows right now. Typed text and titles are already cut to the wire limits.
struct SpotlightSnapshot: Sendable, Equatable {
    static let maxBytes = 256
    static let empty = SpotlightSnapshot(typed: "", titles: [])

    let typed: String
    let titles: [String]

    init(typed: String, titles: [String]) {
        self.typed = Self.truncate(typed)
        self.titles = titles.prefix(SecureMessage.maxSpotlightRows).map(Self.truncate)
    }

    /// Cuts to `maxBytes` of UTF-8 on a character boundary.
    static func truncate(_ value: String) -> String {
        var used = 0
        var result = ""
        for character in value {
            used += character.utf8.count
            guard used <= maxBytes else { break }
            result.append(character)
        }
        return result
    }
}

/// A flattened Accessibility element, in tree order.
struct SpotlightNode: Sendable, Equatable {
    var depth: Int
    var role: String
    var id: String
    var value: String
    var frame: CGRect

    init(depth: Int, role: String = "", id: String = "", value: String = "", frame: CGRect = .zero) {
        self.depth = depth
        self.role = role
        self.id = id
        self.value = value
        self.frame = frame
    }
}

enum SpotlightParser {
    /// Empty when there is no search field or it holds no text. Rows are the cells inside
    /// the panel window, sorted by Y (row ids are unreliable, positions are not).
    static func parse(_ nodes: [SpotlightNode]) -> SpotlightSnapshot {
        guard let field = nodes.first(where: { $0.id == "SpotlightSearchField" }), !field.value.isEmpty,
              let window = nodes.first(where: { $0.role == "AXWindow" })
        else { return .empty }
        var rows: [(y: CGFloat, title: String)] = []
        for (index, cell) in nodes.enumerated() where cell.role == "AXCell" && cell.frame.intersects(window.frame) {
            let title = nodes[(index + 1)...].prefix { $0.depth > cell.depth }
                .first { $0.role == "AXStaticText" && !$0.value.isEmpty }
            if let title { rows.append((cell.frame.minY, clean(title.value))) }
        }
        return SpotlightSnapshot(typed: clean(field.value), titles: rows.sorted { $0.y < $1.y }.map(\.title))
    }

    /// Drops bidi isolates and turns no-break spaces into spaces.
    private static func clean(_ value: String) -> String {
        value.replacingOccurrences(of: "\u{2068}", with: "").replacingOccurrences(of: "\u{2069}", with: "")
            .replacingOccurrences(of: "\u{a0}", with: " ")
    }
}
