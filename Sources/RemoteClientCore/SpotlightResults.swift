import Foundation

/// The Mac's typed text and the result titles it shows, top to bottom.
public struct SpotlightResults: Sendable, Equatable {
    public let typed: String
    public let titles: [String]

    public init(typed: String, titles: [String]) {
        self.typed = typed
        self.titles = titles
    }

    /// Where `typed` matches the start of a word in `title`; words split on space, `.`, `_`, `-`.
    /// Case-insensitive. Empty when nothing matches.
    public func matchedRanges(in title: String) -> [Range<String.Index>] {
        let query = typed.lowercased()
        guard !query.isEmpty else { return [] }
        var ranges: [Range<String.Index>] = []
        var index = title.startIndex
        while index < title.endIndex {
            if " ._-".contains(title[index]) {
                index = title.index(after: index)
                continue
            }
            let wordEnd = title[index...].firstIndex { " ._-".contains($0) } ?? title.endIndex
            if title[index..<wordEnd].lowercased().hasPrefix(query) {
                let end = title.index(index, offsetBy: query.count, limitedBy: wordEnd) ?? wordEnd
                ranges.append(index..<end)
            }
            index = wordEnd
        }
        return ranges
    }
}
