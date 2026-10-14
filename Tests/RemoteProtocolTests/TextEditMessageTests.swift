import Foundation
import XCTest

@testable import RemoteProtocol

final class TextEditMessageTests: XCTestCase {
    func testRoundTripAndLayout() throws {
        let cases: [SecureMessage] = [
            .textEdit(delete: 0, insert: "a"), .textEdit(delete: 1, insert: ""),
            .textEdit(delete: 3, insert: "caf\u{e9} \u{1F600}\n"),
            .textEdit(delete: 4096, insert: ""),
            .textEdit(delete: 0, insert: String(repeating: "a", count: 4096)),
        ]
        for message in cases {
            XCTAssertEqual(try SecureMessage(wire: message.encoded()), message)
        }
        XCTAssertEqual(try SecureMessage.textEdit(delete: 258, insert: "hi").encoded(), Data([13, 1, 2, 0x68, 0x69]))
        XCTAssertEqual(try SecureMessage.textEdit(delete: 4096, insert: "").encoded(), Data([13, 0x10, 0, ]))
    }

    func testEncodeRejects() {
        for message in [SecureMessage.textEdit(delete: 4097, insert: "a"), .textEdit(delete: -1, insert: "a"),
                        .textEdit(delete: 0, insert: String(repeating: "a", count: 4097))] {
            XCTAssertThrowsError(try message.encoded())
        }
        XCTAssertThrowsError(try SecureMessage.textEdit(delete: 0, insert: "").encoded())
    }

    func testDecodeRejects() {
        let bad: [Data] = [
            Data([13]), Data([13, 0]), Data([13, 0, 0]),                 // truncated / empty edit
            Data([13, 0x10, 0x01]),                                      // delete 4097
            Data([13, 0xff, 0xff, 0x61]),
            Data([13, 0, 0]) + Data(repeating: 0x61, count: 4097),       // insert too long
            Data([13, 0, 1, 0xff]), Data([13, 0, 1, 0xc3, 0x28]),        // invalid UTF-8
        ]
        for wire in bad { XCTAssertThrowsError(try SecureMessage(wire: wire), "\(Array(wire))") }
        XCTAssertEqual(try SecureMessage(wire: Data([13, 0, 0]) + Data(repeating: 0x61, count: 4096)),
                       .textEdit(delete: 0, insert: String(repeating: "a", count: 4096)))
        XCTAssertEqual(try SecureMessage(wire: Data([13, 0x10, 0x00])), .textEdit(delete: 4096, insert: ""))
    }
}
