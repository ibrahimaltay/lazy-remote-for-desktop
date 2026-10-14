import Foundation
import XCTest

@testable import RemoteProtocol

final class SpotlightMessageTests: XCTestCase {
    private func str(_ s: String) -> Data {
        let b = Data(s.utf8)
        return Data([UInt8(b.count >> 8), UInt8(b.count & 0xff)]) + b
    }

    func testSpotlightResultsRoundTripAndLayout() throws {
        let cases: [SecureMessage] = [
            .spotlightResults(typed: "", titles: []),
            .spotlightResults(typed: "pho", titles: ["Photos", "", "Two\nLines", "caf\u{e9} \u{1F600}"]),
            .spotlightResults(typed: "", titles: Array(repeating: "", count: 8)),
            .spotlightWatch(true), .spotlightWatch(false),
        ]
        for message in cases {
            let wire = try message.encoded()
            XCTAssertEqual(try SecureMessage(wire: wire), message)
            XCTAssertEqual(try SecureMessage(wire: (Data([9, 9]) + wire).dropFirst(2)), message)
        }
        XCTAssertEqual(try SecureMessage.spotlightResults(typed: "a", titles: ["b"]).encoded(),
                       Data([10, 1]) + str("a") + str("b"))
        XCTAssertEqual(try SecureMessage.spotlightWatch(true).encoded(), Data([11, 1]))
        XCTAssertEqual(try SecureMessage.spotlightWatch(false).encoded(), Data([11, 0]))
    }

    func testMaxPlaintextIs2324Bytes() throws {
        let big = String(repeating: "a", count: 256)
        let message = SecureMessage.spotlightResults(typed: big, titles: Array(repeating: big, count: 8))
        let wire = try message.encoded()
        XCTAssertEqual(wire.count, 2324)
        XCTAssertEqual(try SecureMessage(wire: wire), message)
    }

    func testRejectsMalformedResults() throws {
        let good = Data([10, 1]) + str("a") + str("b")
        let malformed: [Data] = [
            Data([10]), Data([10, 0]), Data([10, 0, 0]),                // too short
            Data([10, 9]) + str("") + Data(repeating: 0, count: 18),    // count above 8
            Data([10, 255]) + str(""),
            Data([10, 1]) + str("a"),                                    // missing title
            Data([10, 1, 0, 1, 0x61, 0, 5, 0x62]),                       // length past end
            Data([10, 1, 0, 1, 0x61, 0]),                                // truncated length
            good + Data([0]),                                            // trailing byte
            Data([10, 0]) + str("") + str("x"),                          // trailing string
            Data([10, 1, 0, 1, 0xff, 0, 1, 0x62]),                       // invalid UTF-8
            Data([10, 1, 0, 1, 0x61, 0, 2, 0xc3, 0x28]),
        ]
        for wire in malformed {
            XCTAssertThrowsError(try SecureMessage(wire: wire), "\(Array(wire))") {
                XCTAssertEqual($0 as? SecureWireError, .malformed)
            }
        }
        XCTAssertNoThrow(try SecureMessage(wire: good))
    }

    func testRejectsMalformedWatch() {
        for wire in [Data([11]), Data([11, 2]), Data([11, 255]), Data([11, 1, 0]), Data([11, 0, 0])] {
            XCTAssertThrowsError(try SecureMessage(wire: wire)) { XCTAssertEqual($0 as? SecureWireError, .malformed) }
        }
    }

    func testEncoderRejectsTooManyRowsAndOversizedString() {
        XCTAssertThrowsError(try SecureMessage.spotlightResults(typed: "", titles: Array(repeating: "x", count: 9)).encoded()) {
            XCTAssertEqual($0 as? SecureWireError, .oversized)
        }
        XCTAssertThrowsError(try SecureMessage.spotlightResults(typed: String(repeating: "a", count: 65536), titles: []).encoded())
    }
}
