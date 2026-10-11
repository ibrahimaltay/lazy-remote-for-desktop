# Claude Code guidance

Follow the shared repository conventions in
[.github/copilot-instructions.md](.github/copilot-instructions.md).
Architecture, build/test commands, CLI usage, website maintenance, and distribution
instructions are maintained in [README.md](README.md).

Read [docs/secure-protocol.md](docs/secure-protocol.md) before changing handshake,
framing, message encoding, or pairing. It is the canonical wire/state/trust
specification and includes the still-open release gates.

Keep application behavior in the shared Swift package where it can be tested.
The SwiftUI shells remain thin. `project.yml` is the source of truth for generated
Xcode configuration; never make lasting changes only to generated files.
