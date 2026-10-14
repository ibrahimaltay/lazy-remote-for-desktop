import XCTest
import RemoteProtocol
@testable import RemoteClientCore

@MainActor
final class SpotlightTyperTests: XCTestCase {
    /// Ordered log: "t:<text>", "bs", "enter".
    private var log: [String] = []

    private func make(sendResult: Bool = true) -> SpotlightTyper {
        log = []
        return SpotlightTyper(
            sendText: { [unowned self] in self.log.append("t:\($0)"); return sendResult },
            tap: { [unowned self] in
                switch $0 {
                case .backspace: self.log.append("bs")
                case .enter: self.log.append("enter")
                default: self.log.append("other")
                }
            })
    }

    private func bs(_ n: Int) -> [String] { Array(repeating: "bs", count: n) }

    func testAppend() {
        let t = make()
        t.update("ab")
        t.textDelivered(true)
        t.update("abc")
        XCTAssertEqual(log, ["t:ab", "t:c"])
    }

    func testDelete() {
        let t = make()
        t.update("abc")
        t.textDelivered(true)
        t.update("a")
        XCTAssertEqual(log, ["t:abc"] + bs(2))
    }

    func testMiddleReplace() {
        let t = make()
        t.update("abc")
        t.textDelivered(true)
        t.update("axc")
        XCTAssertEqual(log, ["t:abc"] + bs(2) + ["t:xc"])
    }

    func testBackspacesCountCharacters() {
        let t = make()
        t.update("a\u{E9}\u{1F600}") // multibyte characters
        t.textDelivered(true)
        t.update("a")
        XCTAssertEqual(log, ["t:a\u{E9}\u{1F600}"] + bs(2))
    }

    func testEditsWhileInFlightMergeInOrder() {
        let t = make()
        t.update("a")
        t.update("ab")
        t.update("abc")
        XCTAssertEqual(log, ["t:a"])
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a", "t:bc"])
    }

    func testEditsWhileInFlightMergeWithDeletion() {
        let t = make()
        t.update("abc")
        t.update("ab")
        t.update("abd")
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:abc"] + bs(1) + ["t:d"])
    }

    func testGoInSyncPressesEnterOnce() {
        let t = make()
        t.update("a")
        t.textDelivered(true)
        t.go()
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a", "enter"])
    }

    func testGoWhileInFlightPressesEnterOnlyAfterReceipt() {
        let t = make()
        t.update("safari")
        t.go()
        XCTAssertEqual(log, ["t:safari"])
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:safari", "enter"])
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:safari", "enter"])
    }

    func testGoPendingEditSendsThenEnter() {
        let t = make()
        t.update("a")
        t.update("ab")
        t.go()
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a", "t:b"])
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a", "t:b", "enter"])
    }

    func testGoWithEmptyTargetPressesNothing() {
        let t = make()
        t.update("a")
        t.textDelivered(true)
        t.update("")
        XCTAssertEqual(log, ["t:a", "bs"])
        t.go()
        XCTAssertEqual(log, ["t:a", "bs"])
    }

    func testNoEnterAfterFailedSend() {
        let t = make()
        t.update("a")
        t.go()
        t.textDelivered(false)
        t.textDelivered(true) // unrelated receipt
        XCTAssertEqual(log, ["t:a"])
    }

    func testRefusedSendArmsNothing() {
        let t = make(sendResult: false)
        t.update("a")
        t.go()
        t.textDelivered(true)
        XCTAssertFalse(t.inFlight)
        XCTAssertFalse(log.contains("enter"))
    }

    func testResetDisarmsEnter() {
        let t = make()
        t.update("a")
        t.go()
        t.reset()
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a"])
    }

    func testTextDeliveredIgnoredWhenNothingInFlight() {
        let t = make()
        t.textDelivered(true)
        t.textDelivered(false)
        XCTAssertEqual(log, [])
        t.update("a")
        t.textDelivered(true)
        t.go()
        t.textDelivered(true) // nothing in flight: no extra effect
        XCTAssertEqual(log, ["t:a", "enter"])
    }

    func testLeftoverAdoption() {
        let t = make()
        t.macTyped("photos")
        t.update("p")
        XCTAssertEqual(log, bs(6) + ["t:p"])
    }

    func testLeftoverNotReusedEvenWhenPrefixMatches() {
        let t = make()
        t.macTyped("photos")
        t.update("photos")
        XCTAssertEqual(log, bs(6) + ["t:photos"])
    }

    func testNoAdoptionAfterFirstSend() {
        let t = make()
        t.update("a")
        t.textDelivered(true)
        t.macTyped("zzz")
        t.update("ab")
        XCTAssertEqual(log, ["t:a", "t:b"])
    }

    func testNoAdoptionWhileInFlight() {
        let t = make()
        t.update("a")
        t.macTyped("zzz")
        t.textDelivered(true)
        t.update("ab")
        XCTAssertEqual(log, ["t:a", "t:b"])
    }

    func testResetKeepsInFlightGate() {
        let t = make()
        t.update("a")
        t.reset()
        XCTAssertTrue(t.inFlight)
        t.update("b")
        XCTAssertEqual(log, ["t:a"])
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a", "t:b"])
    }

    func testNewlineReplacedBySpace() {
        let t = make()
        t.update("a\nb\r\nc")
        XCTAssertEqual(log, ["t:a b c"])
    }

    func testCapsAt256Bytes() {
        let t = make()
        t.update(String(repeating: "a", count: 300))
        XCTAssertEqual(log, ["t:" + String(repeating: "a", count: 256)])
    }

    func testCapCutsOnCharacterBoundary() {
        let t = make()
        t.update(String(repeating: "a", count: 255) + "\u{E9}\u{E9}")
        XCTAssertEqual(log, ["t:" + String(repeating: "a", count: 255)])
        let u = make()
        u.update(String(repeating: "\u{E9}", count: 200))
        XCTAssertEqual(log, ["t:" + String(repeating: "\u{E9}", count: 128)])
    }

    func testStopDropsParkedEditsOnReceipt() {
        let t = make()
        t.update("a")
        t.update("ab")
        t.stop()
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a"])
    }

    func testStopKeepsEditsWhenEnterArmed() {
        let t = make()
        t.update("a")
        t.update("ab")
        t.go()
        t.stop()
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a", "t:b"])
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a", "t:b", "enter"])
    }

    func testFailedSendRestoresMacTextAndResends() {
        let t = make()
        t.update("a")
        t.textDelivered(true)
        t.update("abc")
        t.go()
        t.textDelivered(false)
        XCTAssertEqual(log, ["t:a", "t:bc"])
        t.update("abc") // next edit resends only the missing part
        XCTAssertEqual(log, ["t:a", "t:bc", "t:bc"])
        t.textDelivered(true)
        XCTAssertFalse(log.contains("enter"))
    }

    func testFailedSendWithBackspacesResendsFromPrefix() {
        let t = make()
        t.update("abc")
        t.textDelivered(true)
        t.update("axy")
        t.textDelivered(false)
        t.update("axy")
        XCTAssertEqual(log, ["t:abc"] + bs(2) + ["t:xy", "t:xy"])
    }

    func testNoEnterUntilMacEqualsQueryAfterFailure() {
        let t = make()
        t.update("ab")
        t.textDelivered(false)
        t.go() // resends, re-arms
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:ab", "t:ab", "enter"])
    }

    func testRefusedSendRestoresAndNextEditResends() {
        var accept = false
        log = []
        let t = SpotlightTyper(
            sendText: { [unowned self] in self.log.append("t:\($0)"); return accept },
            tap: { [unowned self] in self.log.append($0 == .enter ? "enter" : "bs") })
        t.update("ab")
        t.go()
        accept = true
        t.update("abc")
        XCTAssertEqual(log, ["t:ab", "t:ab", "t:abc"])
        t.textDelivered(true)
        XCTAssertFalse(log.contains("enter"))
    }

    func testGoEmptyDoesNotLeaveEnterArmed() {
        let t = make()
        t.go()
        t.update("a")
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a"])
    }

    func testGoThenDeleteBeforeReceiptClearsEnter() {
        let t = make()
        t.update("a")
        t.go()
        t.update("")
        t.textDelivered(true)
        XCTAssertEqual(log, ["t:a", "bs"])
        t.update("b")
        t.textDelivered(true)
        XCTAssertFalse(log.contains("enter"))
    }
}
