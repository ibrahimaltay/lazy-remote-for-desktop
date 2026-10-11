import CoreBluetooth
import Foundation

/// The BLE service the Mac advertises and the iPhone looks for.
///
/// These are computed rather than stored because `CBUUID` is a non-Sendable class,
/// which a `static let` cannot hold under strict concurrency.
public enum RemoteService {
    public static var uuid: CBUUID { CBUUID(string: "CD7662C9-9F43-489F-BDD2-9E82E334D46B") }

    public static var secureControlUUID: CBUUID { CBUUID(string: "64B1C682-BC10-48CF-93F5-8242F02396DD") }
    public static var secureInputUUID: CBUUID { CBUUID(string: "3F728627-E19A-4DF6-84CB-81E06DA0C7E9") }

    public static let defaultName = "LazyRemote"
}
