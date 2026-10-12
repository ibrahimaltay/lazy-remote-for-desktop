import XCTest
@testable import RemoteClientCore

@MainActor
final class SpotlightSubmitterTests: XCTestCase {
    private var sent: [String] = []
    private var enters = 0

    private func make(sendResult: Bool = true) -> SpotlightSubmitter {
        sent = []
        enters = 0
        return SpotlightSubmitter(
            send: { [unowned self] in self.sent.append($0); return sendResult },
            pressEnter: { [unowned self] in self.enters += 1 })
    }

    func testDeliveredPressesEnterOnce() {
        let s = make()
        s.submit("safari")
        s.textDelivered(true)
        XCTAssertEqual(sent, ["safari"])
        XCTAssertEqual(enters, 1)
    }

    func testFailedDeliveryPressesNoEnterAndDisarms() {
        let s = make()
        s.submit("safari")
        s.textDelivered(false)
        s.textDelivered(true)
        XCTAssertEqual(enters, 0)
    }

    func testSendRefusedArmsNothing() {
        let s = make(sendResult: false)
        s.submit("safari")
        s.textDelivered(true)
        XCTAssertEqual(enters, 0)
    }

    func testPlainSendAfterFailedSubmitPressesNoEnter() {
        let s = make()
        s.submit("a")
        s.textDelivered(false)
        s.textDelivered(true) // delivery of an unrelated plain send
        XCTAssertEqual(enters, 0)
    }

    func testSecondDeliveryPressesNoEnterAgain() {
        let s = make()
        s.submit("a")
        s.textDelivered(true)
        s.textDelivered(true)
        XCTAssertEqual(enters, 1)
    }

    func testResetDisarms() {
        let s = make()
        s.submit("a")
        s.reset()
        s.textDelivered(true)
        XCTAssertEqual(enters, 0)
    }
}
