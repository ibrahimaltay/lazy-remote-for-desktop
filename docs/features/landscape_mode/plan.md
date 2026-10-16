# Landscape mode

Status: draft

## Goal

Use the iPhone remote in landscape orientation. (Details pending the design.)

## Design inputs

- [design.dc.html](design.dc.html) and [design.md](design.md), as downloaded and never edited.
- Replicate them exactly; the values live in design.md, not here.
- Deviations from the design: none | list them, with the reason.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|

## Scope

In:
Out (deliberately):

## Constraints

AGENTS.md rules this touches (BLE only, fail-closed security, wire compatibility,
Swift 6 concurrency). If wire format or pairing changes, say so and link
docs/secure-protocol.md.

## Steps

- [ ] Ordered implementation steps. Say where the logic lives (package vs. app shell).

## Acceptance criteria

Observable behaviors that must hold when done. The tester agent reviews these
against the code and existing tests, then adds missing tests and removes
redundant ones.

## Done when

- [ ] Acceptance criteria verified by tests
- [ ] `swift test` passes
- [ ] Both app targets build
- [ ] Tester findings resolved with the developer
- [ ] Last QA round: every acceptance criterion passes on device, no open issues
- [ ] Marketer has reviewed the promo GIFs for this feature (after QA passes)

## QA log

Only the user and the tester agent may add or change rows here. One row per
issue found in manual QA. Minor bug (code wrong, plan right) goes to the developer, then the tester, then a redeploy. Design or behavior problem
(plan wrong) goes back to the architect and gets a new row in Decisions.

| Round | Build | Issue | Severity | Routed to | Status |
|-------|-------|-------|----------|-----------|--------|

## Open questions
