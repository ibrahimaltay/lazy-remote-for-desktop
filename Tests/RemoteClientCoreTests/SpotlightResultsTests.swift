@testable import RemoteClientCore
import XCTest

final class SpotlightResultsTests: XCTestCase {
    private func matches(_ typed: String, _ title: String) -> [String] {
        SpotlightResults(typed: typed, titles: []).matchedRanges(in: title).map { String(title[$0]) }
    }

    func testPrefixOfWordsOnly() {
        XCTAssertEqual(matches("P", "Raspberry Pi Imager.app"), ["P"])
        XCTAssertEqual(matches("pi", "Raspberry Pi Imager.app"), ["Pi"])
        XCTAssertEqual(matches("ima", "Raspberry Pi Imager.app"), ["Ima"])
        XCTAssertEqual(matches("a", "Raspberry Pi Imager.app"), ["a"])  // only "app"
    }

    func testCaseInsensitive() {
        XCTAssertEqual(matches("PHO", "photos"), ["pho"])
        XCTAssertEqual(matches("pho", "PHOTOS"), ["PHO"])
    }

    func testSeparators() {
        XCTAssertEqual(matches("b", "a.b_b-b c"), ["b", "b", "b"])
    }

    func testNoMatchAndEmptyQuery() {
        XCTAssertEqual(matches("z", "Photos"), [])
        XCTAssertEqual(matches("", "Photos"), [])
        XCTAssertEqual(matches("p", ""), [])
    }

    func testMultiWordQueryYieldsNoMatchCurrentBehavior() {
        XCTAssertEqual(matches("raspberry pi", "Raspberry Pi Imager.app"), [])
    }
}
