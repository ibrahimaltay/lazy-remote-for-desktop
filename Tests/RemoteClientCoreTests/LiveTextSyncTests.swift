import RemoteProtocol
import XCTest

@testable import RemoteClientCore

final class LiveTextSyncTests: XCTestCase {
    private typealias Edit = LiveTextSync.Edit

    func testAppendAndUnchanged() {
        var s = LiveTextSync()
        XCTAssertEqual(s.update("h"), [Edit(delete: 0, insert: "h")])
        XCTAssertEqual(s.update("hi"), [Edit(delete: 0, insert: "i")])
        XCTAssertEqual(s.update("hi"), [])
        XCTAssertEqual(s.update(""), [Edit(delete: 2, insert: "")])
        XCTAssertEqual(s.update(""), [])
    }

    func testAutocorrectReplaceAndDeleteOnly() {
        var s = LiveTextSync()
        _ = s.update("teh")
        XCTAssertEqual(s.update("the "), [Edit(delete: 2, insert: "he ")])
        XCTAssertEqual(s.update("the"), [Edit(delete: 1, insert: "")])
    }

    func testGraphemeBoundariesAndNewline() {
        var s = LiveTextSync()
        _ = s.update("a\u{1F468}\u{200D}\u{1F469}")           // one family-style cluster
        XCTAssertEqual(s.update("a"), [Edit(delete: 1, insert: "")])
        _ = s.update("e")
        XCTAssertEqual(s.update("e\u{301}"), [Edit(delete: 1, insert: "e\u{301}")]) // combining mark: whole cluster
        XCTAssertEqual(s.update("e\u{301}\n"), [Edit(delete: 0, insert: "\n")])
    }

    func testChunksAboveWireLimits() throws {
        var s = LiveTextSync()
        let long = String(repeating: "a", count: 4096 * 2 + 5)
        let edits = s.update(long)
        XCTAssertEqual(edits.count, 3)
        XCTAssertEqual(edits.map(\.insert).joined(), long)
        for e in edits { XCTAssertNoThrow(try SecureMessage.textEdit(delete: e.delete, insert: e.insert).encoded()) }
        // multibyte never splits a character and stays within 4096 bytes
        var m = LiveTextSync()
        let emoji = String(repeating: "\u{1F600}", count: 1100)
        let me = m.update(emoji)
        XCTAssertEqual(me.map(\.insert).joined(), emoji)
        for e in me { XCTAssertLessThanOrEqual(e.insert.utf8.count, 4096) }
        // deletes above 4096 are split; total preserved
        var d = LiveTextSync()
        _ = d.update(String(repeating: "b", count: 9000))
        let de = d.update("")
        XCTAssertEqual(de.map(\.delete), [4096, 4096, 808])
        XCTAssertTrue(de.allSatisfy { $0.insert.isEmpty })
        // delete + large insert: total delete preserved, each edit valid
        var r = LiveTextSync()
        _ = r.update(String(repeating: "x", count: 5000))
        let re = r.update(String(repeating: "y", count: 5000))
        XCTAssertEqual(re.map(\.delete).reduce(0, +), 5000)
        XCTAssertEqual(re.map(\.insert).joined().count, 5000)
        for e in re { XCTAssertNoThrow(try SecureMessage.textEdit(delete: e.delete, insert: e.insert).encoded()) }
    }

    func testResetAndEmptyBackspace() {
        var s = LiveTextSync()
        _ = s.update("abc")
        s.reset()
        XCTAssertEqual(s.text, "")
        XCTAssertEqual(s.update("d"), [Edit(delete: 0, insert: "d")])
        s.reset(to: "xy")
        XCTAssertEqual(s.update("xyz"), [Edit(delete: 0, insert: "z")])
        XCTAssertEqual(s.emptyBackspace(), Edit(delete: 1, insert: ""))
    }
}
