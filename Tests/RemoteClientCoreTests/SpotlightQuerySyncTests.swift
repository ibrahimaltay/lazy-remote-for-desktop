import XCTest
@testable import RemoteClientCore

@MainActor
final class SpotlightQuerySyncTests: XCTestCase {
    private var sent: [String] = []
    private var enters = 0
    private var clock: TimeInterval = 100

    private func make() -> SpotlightQuerySync {
        sent = []
        enters = 0
        clock = 100
        return SpotlightQuerySync(
            send: { [unowned self] in self.sent.append($0) },
            enter: { [unowned self] in self.enters += 1 },
            now: { [unowned self] in self.clock })
    }

    func testOpenSendsEmpty() {
        let s = make()
        s.open()
        XCTAssertEqual(sent, [""])
    }

    func testDedupesAgainstLastSent() {
        let s = make()
        s.open()
        s.update("a")
        s.update("a")
        s.update("ab")
        s.update("ab\n") // cleans to "ab ", differs
        s.update("ab ")
        XCTAssertEqual(sent, ["", "a", "ab", "ab "])
        s.update("")
        XCTAssertEqual(sent.last, "")
    }

    func testNewlineBecomesSpace() {
        let s = make()
        s.update("a\nb\r\nc")
        XCTAssertEqual(sent, ["a b c"])
    }

    func testCapsAt256BytesOnCharacterBoundary() {
        let s = make()
        s.update(String(repeating: "a", count: 300))
        XCTAssertEqual(sent.last, String(repeating: "a", count: 256))
        s.update(String(repeating: "a", count: 255) + "\u{E9}\u{E9}")
        XCTAssertEqual(sent.last, String(repeating: "a", count: 255))
        s.update(String(repeating: "\u{E9}", count: 200))
        XCTAssertEqual(sent.last, String(repeating: "\u{E9}", count: 128))
    }

    func testUpdateAfterResetResends() {
        let s = make()
        s.update("a")
        s.reset()
        s.update("a")
        XCTAssertEqual(sent, ["a", "a"])
    }

    func testGoReturnsFalseForEmptyQuery() {
        let s = make()
        XCTAssertFalse(s.go())
        s.update("a")
        s.update("")
        XCTAssertFalse(s.go())
        XCTAssertFalse(s.isGoPending)
        XCTAssertEqual(enters, 0)
    }

    func testEnterAfterSettleDelayOnly() {
        let s = make()
        s.update("abc")
        s.snapshot(typed: "abc")
        XCTAssertTrue(s.go())
        XCTAssertEqual(enters, 0)
        clock += 0.29
        s.tick()
        XCTAssertEqual(enters, 0)
        clock += 0.01
        s.tick()
        XCTAssertEqual(enters, 1)
        XCTAssertFalse(s.isGoPending)
    }

    func testNewSnapshotRestartsSettleWindow() {
        let s = make()
        s.update("abc")
        s.snapshot(typed: "abc")
        s.go()
        clock += 0.25
        s.snapshot(typed: "abc")
        clock += 0.25
        s.tick()
        XCTAssertEqual(enters, 0)
        clock += 0.1
        s.tick()
        XCTAssertEqual(enters, 1)
    }

    func testMismatchedTypedWaitsThenTimesOut() {
        let s = make()
        s.update("abc")
        s.snapshot(typed: "ab")
        s.go()
        clock += 1.9
        s.tick()
        XCTAssertEqual(enters, 0)
        clock += 0.1
        s.tick()
        XCTAssertEqual(enters, 1)
    }

    func testTimeoutFiresWithoutAnySnapshot() {
        let s = make()
        s.update("abc")
        s.go()
        clock += 1.99
        s.tick()
        XCTAssertEqual(enters, 0)
        clock += 0.01
        s.tick()
        XCTAssertEqual(enters, 1)
    }

    func testLateSnapshotDoesNotFireTwice() {
        let s = make()
        s.update("abc")
        s.go()
        clock += 2
        s.tick()
        s.snapshot(typed: "abc")
        clock += 1
        s.tick()
        s.tick()
        XCTAssertEqual(enters, 1)
    }

    func testChangedQueryInvalidatesStaleSnapshot() {
        let s = make()
        s.update("a")
        s.snapshot(typed: "a")
        clock += 5
        s.update("ab")
        s.update("a")
        s.go()
        XCTAssertEqual(enters, 0)
        clock += 1
        s.tick()
        XCTAssertEqual(enters, 0) // the old "a" snapshot no longer counts
        s.snapshot(typed: "a")
        clock += 0.2
        s.tick()
        XCTAssertEqual(enters, 0)
        clock += 0.2
        s.tick()
        XCTAssertEqual(enters, 1)
    }

    func testChangedQueryStaleSnapshotFallsBackToTimeout() {
        let s = make()
        s.update("a")
        s.snapshot(typed: "a")
        clock += 5
        s.update("ab")
        s.update("a")
        s.go()
        clock += 1.9
        s.tick()
        XCTAssertEqual(enters, 0)
        clock += 0.1
        s.tick()
        XCTAssertEqual(enters, 1)
    }

    func testDedupedUpdateKeepsSnapshot() {
        let s = make()
        s.update("a")
        s.snapshot(typed: "a")
        clock += 1
        s.update("a") // same as last sent: nothing sent, snapshot still valid
        XCTAssertEqual(sent, ["a"])
        s.go()
        XCTAssertEqual(enters, 1)
    }

    func testResetCancelsPendingGo() {
        let s = make()
        s.update("abc")
        s.snapshot(typed: "abc")
        s.go()
        s.reset()
        clock += 5
        s.tick()
        s.snapshot(typed: "abc")
        s.tick()
        XCTAssertEqual(enters, 0)
        XCTAssertFalse(s.isGoPending)
    }
}
