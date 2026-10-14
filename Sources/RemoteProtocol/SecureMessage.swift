import Foundation

public enum SecureMessage: Sendable, Equatable {
    case key(KeyEvent)
    case pointer(PointerEvent)
    case text(id: UInt64, value: String)
    case name(String)
    case pending
    case approved
    case revoked
    case textResult(id: UInt64, success: Bool)
    case finish
    case spotlightResults(typed: String, titles: [String])
    case spotlightWatch(Bool)

    public static let maxSpotlightRows = 8

    public func encoded() throws -> Data {
        switch self {
        case .key(let event):
            return Data([1]) + event.encoded
        case .pointer(let event):
            return Data([2]) + event.encoded
        case .text(let id, let value):
            return Data([3]) + Self.encodeID(id) + (try Self.encodeString(value, limit: 4096))
        case .name(let value):
            return Data([4]) + (try Self.encodeString(value, limit: 128))
        case .pending: return Data([5])
        case .approved: return Data([6])
        case .revoked: return Data([7])
        case .textResult(let id, let success):
            return Data([8]) + Self.encodeID(id) + Data([success ? 1 : 0])
        case .finish: return Data([9])
        case .spotlightResults(let typed, let titles):
            guard titles.count <= Self.maxSpotlightRows else { throw SecureWireError.oversized }
            return try ([typed] + titles).reduce(Data([10, UInt8(titles.count)])) {
                let bytes = Data($1.utf8)
                guard bytes.count <= Int(UInt16.max) else { throw SecureWireError.oversized }
                return $0 + Data([UInt8(bytes.count >> 8), UInt8(bytes.count & 0xff)]) + bytes
            }
        case .spotlightWatch(let isOn): return Data([11, isOn ? 1 : 0])
        }
    }

    public init(wire: Data) throws {
        let bytes = [UInt8](wire)
        guard let tag = bytes.first else { throw SecureWireError.malformed }
        let payload = Data(bytes.dropFirst())
        switch tag {
        case 1:
            guard bytes.count == 3, bytes[2] <= 1, let event = KeyEvent(wire: payload)
            else { throw SecureWireError.malformed }
            self = .key(event)
        case 2:
            guard let event = PointerEvent(wire: payload) else { throw SecureWireError.malformed }
            self = .pointer(event)
        case 3:
            guard bytes.count > 9 else { throw SecureWireError.malformed }
            self = .text(
                id: Self.decodeID(bytes[1..<9]),
                value: try Self.decodeString(Data(bytes[9...]), limit: 4096)
            )
        case 4:
            self = .name(try Self.decodeString(payload, limit: 128))
        case 5, 6, 7, 9:
            guard bytes.count == 1 else { throw SecureWireError.malformed }
            switch tag {
            case 5: self = .pending
            case 6: self = .approved
            case 7: self = .revoked
            default: self = .finish
            }
        case 8:
            guard bytes.count == 10, bytes[9] <= 1 else { throw SecureWireError.malformed }
            self = .textResult(id: Self.decodeID(bytes[1..<9]), success: bytes[9] == 1)
        case 10:
            guard bytes.count >= 4, bytes[1] <= UInt8(Self.maxSpotlightRows) else { throw SecureWireError.malformed }
            var offset = 2
            var strings: [String] = []
            for _ in 0...Int(bytes[1]) {
                guard offset + 2 <= bytes.count else { throw SecureWireError.malformed }
                let end = offset + 2 + (Int(bytes[offset]) << 8 | Int(bytes[offset + 1]))
                guard end <= bytes.count, let value = String(bytes: bytes[(offset + 2)..<end], encoding: .utf8)
                else { throw SecureWireError.malformed }
                strings.append(value)
                offset = end
            }
            guard offset == bytes.count else { throw SecureWireError.malformed }
            self = .spotlightResults(typed: strings[0], titles: Array(strings.dropFirst()))
        case 11:
            guard bytes.count == 2, bytes[1] <= 1 else { throw SecureWireError.malformed }
            self = .spotlightWatch(bytes[1] == 1)
        default:
            throw SecureWireError.malformed
        }
    }

    private static func encodeID(_ id: UInt64) -> Data {
        Data(stride(from: 56, through: 0, by: -8).map { UInt8(truncatingIfNeeded: id >> $0) })
    }

    private static func decodeID(_ bytes: ArraySlice<UInt8>) -> UInt64 {
        bytes.reduce(UInt64(0)) { ($0 << 8) | UInt64($1) }
    }

    private static func encodeString(_ value: String, limit: Int) throws -> Data {
        let data = Data(value.utf8)
        guard !data.isEmpty else { throw SecureWireError.malformed }
        guard data.count <= limit else { throw SecureWireError.oversized }
        return data
    }

    private static func decodeString(_ data: Data, limit: Int) throws -> String {
        guard !data.isEmpty else { throw SecureWireError.malformed }
        guard data.count <= limit else { throw SecureWireError.oversized }
        guard let value = String(data: data, encoding: .utf8) else { throw SecureWireError.malformed }
        return value
    }
}