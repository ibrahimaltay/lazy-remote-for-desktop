# Limit trackpad acceleration

Status: draft

## Goal

A fast, short swipe on the phone trackpad no longer sends the Mac view flying. Like a real MacBook trackpad, output is capped so a rapid short-distance flick moves a bounded amount.

## Design inputs

None. Behavior-only change, no UI.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | Where the fly-away comes from | Gain while fingers are down; momentum coast after lift-off | Momentum coast | User tested: the page moves normally under the fingers and flies after lift-off. Gain is left alone. |

## Scope

In: capping the momentum coast (start velocity and/or distance) after a fast short swipe, for page scrolling only; new tuning keys in `TrackpadTuning.json` with decoding tests.
Out (deliberately): scroll gain while fingers are down; cursor movement (confirmed unaffected); wire format changes; changing slow-finger precision; changing momentum decay (`velocityKeptPerSecond`).

## Constraints

Client-side only; no wire change. Tuning lives in `Sources/RemoteClientCore/Resources/TrackpadTuning.json` and must stay covered by `RemoteClientCoreTests`. Gain is computed in `TrackpadTuning.swift` and applied in `iOSApp/ViewModels/RemoteViewModel.swift`.

## Steps

- [ ] Reproduce: record fingerSpeed, gain and output pixels for a short fast swipe vs. a slow long one.
- [ ] Decide how to limit the coast (see Open questions) and record it in Decisions.
- [ ] Implement in `RemoteClientCore` (package), not the app shell; add keys to `TrackpadTuning.json` and update its `_help`.
- [ ] Limit the coast in `ScrollMomentum` (`maxVelocity` is currently 8000 px/s, far too high for a short flick).
- [ ] Tests in `TrackpadTuningTests` / scroll momentum tests.

## Acceptance criteria

- A short (few cm), very fast swipe scrolls a bounded distance, comparable to the Mac trackpad.
- Slow, precise movement and long deliberate flicks still feel as they do today.
- The coast after lift-off never exceeds the configured limit regardless of finger speed.
- Tuning JSON decodes and the new keys are tested.

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

- How to limit the coast: lower `maxVelocity`, scale start velocity by how far the fingers travelled, or cap total coast distance?
