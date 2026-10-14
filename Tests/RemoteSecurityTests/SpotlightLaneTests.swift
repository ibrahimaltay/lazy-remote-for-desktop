import CryptoKit
import Foundation
import RemoteProtocol
@testable import RemoteSecurity
import XCTest

final class SpotlightLaneTests: XCTestCase {
    func testSpotlightMessagesOnlyOpenOnTheirOwnLane() throws {
        let clientKey = Curve25519.KeyAgreement.PrivateKey()
        let serverKey = Curve25519.KeyAgreement.PrivateKey()
        let transcript = Data("t".utf8)
        var client = SecureSession(sharedSecret: try clientKey.sharedSecretFromKeyAgreement(with: serverKey.publicKey), transcript: transcript, role: .client)
        var server = SecureSession(sharedSecret: try serverKey.sharedSecretFromKeyAgreement(with: clientKey.publicKey), transcript: transcript, role: .server)
        // Tag 10 travels on the server-control lane only.
        let expected = SecureMessage.spotlightResults(typed: "a", titles: ["b"])
        let record = try server.seal(expected.encoded(), lane: .serverControl)
        XCTAssertThrowsError(try client.open(record, lane: .clientControl))
        XCTAssertThrowsError(try client.open(record, lane: .clientInput))
        XCTAssertEqual(try SecureMessage(wire: client.open(record, lane: .serverControl)), expected)
        // Tag 11 travels on the client-control lane only.
        let watch = try client.seal(SecureMessage.spotlightWatch(true).encoded(), lane: .clientControl)
        XCTAssertThrowsError(try server.open(watch, lane: .clientInput))
        XCTAssertThrowsError(try server.open(watch, lane: .serverControl))
        XCTAssertEqual(try SecureMessage(wire: server.open(watch, lane: .clientControl)), .spotlightWatch(true))
        // The largest tag 10 fits the session limit.
        let big = String(repeating: "a", count: 256)
        let max = try SecureMessage.spotlightResults(typed: big, titles: Array(repeating: big, count: 8)).encoded()
        XCTAssertNoThrow(try server.seal(max, lane: .serverControl))
    }
}
