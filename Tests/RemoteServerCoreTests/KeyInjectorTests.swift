import RemoteProtocol
import XCTest

@testable import RemoteServerCore

final class KeyInjectorTests: XCTestCase {
    func testEveryCommandHasExactlyOneMacAction() {
        let system: [Command: Int] = [
            .volumeUp: 0, .volumeDown: 1, .brightnessUp: 2, .brightnessDown: 3,
            .playPause: 16, .nextTrack: 17, .previousTrack: 18,
        ]
        for command in Command.allCases {
            XCTAssertEqual(command.systemKey, system[command], "\(command)")
            XCTAssertNotEqual(command.keyCode == nil, command.systemKey == nil, "\(command)")
        }
        XCTAssertEqual(Command.mid.keyCode, 49)
    }
}
