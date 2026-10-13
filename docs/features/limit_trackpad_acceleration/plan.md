# Limit trackpad acceleration

Status: draft

## Goal

A fast, short swipe on the phone trackpad no longer sends the Mac view flying. Like a real MacBook trackpad, output is capped so a rapid short-distance flick moves a bounded amount.

## Design inputs

None. Behavior-only change, no UI.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|

## Scope

In: capping the gain/output for fast short swipes, for page scrolling only; new tuning keys in `TrackpadTuning.json` with decoding tests.
Out (deliberately): cursor movement (confirmed unaffected); wire format changes; changing slow-finger precision; changing momentum decay (`velocityKeptPerSecond`).

## Constraints

Client-side only; no wire change. Tuning lives in `Sources/RemoteClientCore/Resources/TrackpadTuning.json` and must stay covered by `RemoteClientCoreTests`. Gain is computed in `TrackpadTuning.swift` and applied in `iOSApp/ViewModels/RemoteViewModel.swift`.

## Steps

- [ ] Reproduce: record fingerSpeed, gain and output pixels for a short fast swipe vs. a slow long one.
- [ ] Decide the cap (see Open questions) and record it in Decisions.
- [ ] Implement in `RemoteClientCore` (package), not the app shell; add keys to `TrackpadTuning.json` and update its `_help`.
- [ ] Cap momentum start velocity too if it is the source of the fly-away (`ScrollMomentum`).
- [ ] Tests in `TrackpadTuningTests` / scroll momentum tests.

## Acceptance criteria

- A short (few cm), very fast swipe scrolls a bounded distance, comparable to the Mac trackpad.
- Slow, precise movement and long deliberate flicks still feel as they do today.
- Output never exceeds the configured cap regardless of finger speed.
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

- Cap on per-event output, on gain, or on finger-speed input (scroll only)?
- Does the fly-away come from the gain or from the momentum coast after lift-off?
