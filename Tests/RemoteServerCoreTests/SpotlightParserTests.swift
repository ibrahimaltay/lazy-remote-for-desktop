import CoreGraphics
@testable import RemoteServerCore
import XCTest

final class SpotlightParserTests: XCTestCase {
    private let window = SpotlightNode(depth: 0, role: "AXWindow", frame: CGRect(x: 0, y: 0, width: 600, height: 400))

    private func field(_ value: String) -> SpotlightNode {
        SpotlightNode(depth: 1, role: "AXTextField", id: "SpotlightSearchField", value: value)
    }

    private func row(_ title: String, y: CGFloat, x: CGFloat = 10) -> [SpotlightNode] {
        [SpotlightNode(depth: 1, role: "AXCell", frame: CGRect(x: x, y: y, width: 500, height: 30)),
         SpotlightNode(depth: 2, role: "AXStaticText", value: title)]
    }

    func testSortsRowsByYNotTreeOrder() {
        let nodes = [window, field("p")] + row("Third", y: 120) + row("First", y: 40) + row("Second", y: 80)
        XCTAssertEqual(SpotlightParser.parse(nodes), SpotlightSnapshot(typed: "p", titles: ["First", "Second", "Third"]))
    }

    func testDropsCellsOutsideWindow() {
        let nodes = [window, field("p")] + row("In", y: 40) + row("Below", y: 900) + row("Right", y: 40, x: 5000)
        XCTAssertEqual(SpotlightParser.parse(nodes).titles, ["In"])
    }

    func testCapsAtEightRows() {
        let nodes = [window, field("p")] + (0..<12).flatMap { row("R\($0)", y: CGFloat($0) * 30) }
        XCTAssertEqual(SpotlightParser.parse(nodes).titles, (0..<8).map { "R\($0)" })
    }

    func testEmptyOrMissingFieldGivesEmpty() {
        let rows = row("A", y: 10)
        XCTAssertEqual(SpotlightParser.parse([window, field("")] + rows), .empty)
        XCTAssertEqual(SpotlightParser.parse([window] + rows), .empty)
        XCTAssertEqual(SpotlightParser.parse([field("x")] + rows), .empty)  // no window
        XCTAssertEqual(SpotlightParser.parse([]), .empty)
    }

    func testCellWithoutTitleIsSkipped() {
        let empty = SpotlightNode(depth: 1, role: "AXCell", frame: CGRect(x: 0, y: 10, width: 10, height: 10))
        let nodes = [window, field("p"), empty] + row("Real", y: 50)
        XCTAssertEqual(SpotlightParser.parse(nodes).titles, ["Real"])
    }

    func testKeepsNewlinesAndCleansNbspAndBidi() {
        let nodes = [window, field("a\u{a0}b\u{2068}c\u{2069}")] + row("Two\nLines", y: 10)
            + row("\u{2068}Foo\u{2069}\u{a0}Bar", y: 50)
        let snapshot = SpotlightParser.parse(nodes)
        XCTAssertEqual(snapshot.typed, "a bc")
        XCTAssertEqual(snapshot.titles, ["Two\nLines", "Foo Bar"])
    }

    func testTruncatesOnCharacterBoundary() {
        XCTAssertEqual(SpotlightSnapshot.truncate(String(repeating: "a", count: 300)).utf8.count, 256)
        // 255 ASCII + 2-byte char = 257 bytes: the char is dropped whole.
        XCTAssertEqual(SpotlightSnapshot.truncate(String(repeating: "a", count: 255) + "\u{e9}"),
                       String(repeating: "a", count: 255))
        // 4-byte emoji: 64 fit exactly, the 65th is dropped whole.
        let emoji = String(repeating: "\u{1F600}", count: 65)
        XCTAssertEqual(SpotlightSnapshot.truncate(emoji), String(repeating: "\u{1F600}", count: 64))
        XCTAssertEqual(SpotlightSnapshot.truncate("short"), "short")
        XCTAssertEqual(SpotlightSnapshot.truncate(""), "")
        let snapshot = SpotlightSnapshot(typed: emoji, titles: Array(repeating: emoji, count: 10))
        XCTAssertEqual(snapshot.titles.count, 8)
        XCTAssertTrue(snapshot.titles.allSatisfy { $0.utf8.count == 256 })
        XCTAssertEqual(snapshot.typed.utf8.count, 256)
    }
}
