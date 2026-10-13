# Limit trackpad acceleration

Status: in progress

## Goal

A fast, short swipe on the phone trackpad no longer sends the Mac view flying. Like a real MacBook trackpad, output is capped so a rapid short-distance flick moves a bounded amount.

## Design inputs

None. Behavior-only change, no UI.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | Where the fly-away comes from | Gain while fingers are down; momentum coast after lift-off | Momentum coast | User tested: the page moves normally under the fingers and flies after lift-off. Gain is left alone. |
| 2 | How to limit the coast | Lower `maxVelocity`; scale start velocity by finger travel; cap total coast distance | Scale start velocity by finger travel, keep `maxVelocity` as a backstop | User's choice. A short swipe gets a weaker coast than a long one at the same speed, like the Mac trackpad, without shortening long deliberate flicks. |

## Scope

In: capping the momentum coast (start velocity and/or distance) after a fast short swipe, for page scrolling only; new tuning keys in `TrackpadTuning.json` with decoding tests.
Out (deliberately): scroll gain while fingers are down; cursor movement (confirmed unaffected); wire format changes; changing slow-finger precision; changing momentum decay (`velocityKeptPerSecond`).

## Constraints

Client-side only; no wire change. Tuning lives in `Sources/RemoteClientCore/Resources/TrackpadTuning.json` and must stay covered by `RemoteClientCoreTests`. Gain is computed in `TrackpadTuning.swift` and applied in `iOSApp/ViewModels/RemoteViewModel.swift`.

## Steps

- [ ] Reproduce: record fingerSpeed, gain and output pixels for a short fast swipe vs. a slow long one.
- [x] Decide how to limit the coast: scale start velocity by finger travel (Decision 2).
- [x] Pass the gesture's total finger travel from `RemoteViewModel` into `ScrollMomentum`; add a tuning key for the full-coast travel distance.
- [x] Implement in `RemoteClientCore` (package), not the app shell; add keys to `TrackpadTuning.json` and update its `_help`.
- [x] Limit the coast in `ScrollMomentum` (`maxVelocity` is currently 8000 px/s, far too high for a short flick).
- [x] Tests in `TrackpadTuningTests` / scroll momentum tests.

## Acceptance criteria

- A short (few cm), very fast swipe scrolls a bounded distance, comparable to the Mac trackpad.
- Slow, precise movement and long deliberate flicks still feel as they do today.
- The coast after lift-off never exceeds the configured limit regardless of finger speed.
- Tuning JSON decodes and the new keys are tested.

## Done when

- [x] Acceptance criteria verified by tests
- [x] `swift test` passes
- [x] Both app targets build
- [ ] Tester findings resolved with the developer
- [x] Last QA round: every acceptance criterion passes on device, no open issues
- [x] Marketer has reviewed the promo GIFs for this feature (skipped: user decided no promo change for a behavior fix)

## QA log

Only the user and the tester agent may add or change rows here. One row per
issue found in manual QA. Minor bug (code wrong, plan right) goes to the developer, then the tester, then a redeploy. Design or behavior problem
(plan wrong) goes back to the architect and gets a new row in Decisions.

| Round | Build | Issue | Severity | Routed to | Status |
|-------|-------|-------|----------|-----------|--------|

## Open questions

- Exact scaling curve and the travel distance (points) at which a flick gets its full coast: linear ramp, or something gentler? Set the number during device QA.
