# Copilot instructions

## Shared references

[README.md](../README.md) maintains architecture, build/test commands, CLI usage,
website maintenance, and distribution instructions. Use `swift test` for package
tests and Xcode builds for both app targets. Filter by test target, class, or
`ClassName/testMethodName` for targeted validation. There is no configured lint
command.

[docs/secure-protocol.md](../docs/secure-protocol.md) is the canonical wire format,
connection state, trust policy, and security specification. Read it before
changing handshake, framing, message encoding, or pairing. Its release gates are
not satisfied by builds/tests alone.

## Repository conventions

- LazyRemote uses Bluetooth LE only: the iPhone is the central/client and the Mac
  menu-bar app is the peripheral/server. Do not introduce Wi-Fi or Bonjour.
- Keep testable logic in the shared Swift package under `Sources/`; the SwiftUI
  app shells are thin.
- Security is fail-closed. Never add plaintext/legacy fallback, silently replace
  a changed pin, or discard malformed/failed trust state to proceed. Keep client
  and server policy aligned.
- Wire bytes are a compatibility contract. Preserve documented sizes, limits,
  tags, historical reservations, lanes, and byte order. Update the protocol
  specification and relevant codec/transport tests for intentional changes.
- Swift 6 strict concurrency is enabled. Keep CoreBluetooth work on serialized
  queues and preserve callback queue guarantees. `CBUUID` is not `Sendable`; use
  computed values rather than storing them across concurrency boundaries.
- `project.yml` is the XcodeGen source of truth. Run `xcodegen generate` after
  project setting or app-file changes; the Xcode project and both app Info.plists
  are generated and ignored.
- Trackpad tuning is bundled from
  `Sources/RemoteClientCore/Resources/TrackpadTuning.json`; keep decoding and
  behavior covered by `RemoteClientCoreTests`.
- Mac input injection requires Accessibility permission and a stable code
  identity. Retain `remotectl` and use `scripts/make-app.sh` for bundled injection
  tests.
