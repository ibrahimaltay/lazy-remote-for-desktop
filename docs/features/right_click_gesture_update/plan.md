# Right Click Gesture Update 

Status: shipped

## Goal

update the right click gesture in the trackpad to a single tap with two fingers to match the real macbook trackpad.

## Design inputs

no design changes, therefore no inputs.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | On-screen hint | Reword to "Two-finger tap"; drop right-click part; remove hint entirely | Remove the whole hint text | User: unnecessary |
| 2 | Two-finger touch that stops scroll momentum then lifts | Allow; suppress | Allow | Matches one-finger tap behavior; no extra code. Revisit if QA finds stray context menus |
| 3 | Keep two-finger double-tap too | Replace; keep both | Replace | Keeping both delays the single tap |
| 4 | Docs text | Update README/site/marketing plan; app only | Update them | Keep docs truthful. GIF scene scripts untouched |
| 5 | Release | iphone / mac / both | iphone | Mac app and wire format unchanged |

## Scope

In: right-click recognizer in `iOSApp/Views/TrackpadView.swift` becomes a two-finger single tap; remove the trackpad hint text and the "deliberately not the Mac's" comment; update "double-tap" wording in `README.md` (lines 15, 45), `site/index.html` (87, 116), `marketing/marketing-plan.md` (14, 67).
Out (deliberately): Updating Gifs is out of scope. Even though previous gifs show two taps, it is difficult for users to notice the difference because the gif is fast, so just ignore the whole gif generation process. Leave `marketing/scenes/*` and the design HTML in `docs/features/spotlight_search_design_update/` alone.

## Constraints

No wire, pairing or BLE change: pointer click frame `[2] + button + count` and `.right` already exist (docs/secure-protocol.md). iPhone-only change in the app shell; no package logic.

## Steps

- [x] `TrackpadView.swift`: set the right-click `UITapGestureRecognizer` to one tap (drop `numberOfTapsRequired = 2`), keep two touches; remove the old comment
- [x] `TrackpadView.swift`: remove the hint text view/string
- [x] Update wording in README.md, site/index.html, marketing/marketing-plan.md
- [x] Both app targets build

## Acceptance criteria

- A single quick tap with two fingers sends one right-click, with no wait for a second tap.
- A two-finger double tap no longer is a special gesture (two taps send two right-clicks).
- One-finger tap, double/triple tap, drag, two-finger scroll and three-finger swipe behave as before.
- The trackpad shows no gesture hint text.
- README, site and marketing plan say "two-finger tap" for right-click.

## Done when

- [ ] Acceptance criteria verified by tests
- [x] `swift test` passes
- [x] Both app targets build
- [x] Tester findings resolved with the developer
- [x] Last QA round: every acceptance criterion passes on device, no open issues
- [x] Marketer has reviewed the promo GIFs for this feature (skipped: GIFs out of scope per Scope)

## QA log

Only the user and the tester agent may add or change rows here. One row per
issue found in manual QA. Minor bug (code wrong, plan right) goes to the developer, then the tester, then a redeploy. Design or behavior problem
(plan wrong) goes back to the architect and gets a new row in Decisions.

| Round | Build | Issue | Severity | Routed to | Status |
|-------|-------|-------|----------|-----------|--------|

## Open questions
