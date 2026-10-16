import XCTest
@testable import RemoteClientCore

final class FloatingToolLayoutTests: XCTestCase {
    private func y(_ y: Double, other: Double?, range: ClosedRange<Double> = 100...500) -> Double {
        FloatingToolLayout.stackedY(y, other: other, range: range)
    }

    func testNoOtherToolOnlyClamps() {
        XCTAssertEqual(y(300, other: nil), 300)
        XCTAssertEqual(y(0, other: nil), 100)
        XCTAssertEqual(y(900, other: nil), 500)
    }

    func testAtOrBeyondSeventyIsUnchanged() {
        XCTAssertEqual(y(400, other: 300), 400)
        XCTAssertEqual(y(370, other: 300), 370)
        XCTAssertEqual(y(230, other: 300), 230)
    }

    func testInsideSeventyLandsExactlySeventyAwayOnSameSide() {
        XCTAssertEqual(y(330, other: 300), 370)
        XCTAssertEqual(y(270, other: 300), 230)
    }

    func testTieGoesBelow() {
        XCTAssertEqual(y(300, other: 300), 370)
    }

    func testPreferredSideOutOfRangeFlips() {
        XCTAssertEqual(y(490, other: 480), 410)
        XCTAssertEqual(y(110, other: 120), 190)
    }

    func testNeitherSideFitsFallsBackToClamp() {
        XCTAssertEqual(y(130, other: 125, range: 100...150), 130)
    }

    func testClampsIntoRangeBeforeStacking() {
        XCTAssertEqual(y(900, other: 480), 410)
        XCTAssertEqual(y(0, other: 120), 190)
    }
}
