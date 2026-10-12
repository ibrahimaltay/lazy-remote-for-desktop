# Close Remote Controller View on Double Tap

Status: in progress

## Goal

When the D-pad is open, users sometimes accidentally click in the space between the volume up button and the arrow keys, which closes the d-pad unwantedly. we want to make it in such a way that tapping it once would not close the d-pad. Tapping the x icon should close it as usual, but tapping the empty space should require a double tap to close. Tapping one time should show a small hint (tap again to close)

## Design inputs

- No changes to the design, hence no inputs.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | Backdrop gesture | Tap on lift; keep touch-down | Tap on lift | Swipes/drags on empty space no longer close the pad; simplest code |
| 2 | Double-tap window and hint duration | 1s, 1.5s, 2s | 1s for both | One timer from the first tap drives both; tighter window makes a stray later tap less likely to close |
| 3 | Hint | Above X; near the tap | "Tap again to close" above the X button | Text only, existing caption pill style, does not block taps; shown every time the pad is unarmed and empty space is tapped |
| 4 | Testing | Device QA only; extract logic into RemoteClientCore | Device QA only | One Bool and one Task in the view; no new package logic |
| 5 | Key press between the two taps | Disarm; let the timer run out | Timer runs out | Less state |
| 6 | VoiceOver | Change; leave | Leave | Backdrop stays hidden; X ("Close") and the escape gesture still close in one step |
| 7 | Release | iphone / mac / both | iphone | Mac app and wire format unchanged |

## Scope

In: the D-pad backdrop in `iOSApp/Views/DPadOverlay.swift`: one tap on empty space shows the hint and arms for 1s, a second tap while armed closes; the X button still closes in one tap.
Out (deliberately): Updating gifs / marketing is out of scope, no need to document this one, it is a small change. Also out: the typing scrim in `RootView.swift`, key-press gestures, and anything in `Sources/`.

## Constraints

iPhone app shell only. No wire, pairing or BLE change and no new `Command`, so `docs/secure-protocol.md` is unaffected. Swift 6 strict concurrency: the timer is a cancellable `Task` in the view (use `@MainActor`-safe state); no CoreBluetooth work.

## Steps

- [ ] `DPadOverlay.swift`: replace the backdrop's touch-down `DragGesture` with a single tap-on-lift gesture; add an `armed` Bool and a cancellable 1s `Task` that clears it
- [ ] First tap sets `armed` and shows the "Tap again to close" hint pill above the X button (existing caption/`.regularMaterial` capsule style, `allowsHitTesting(false)`, 0.2s fade); second tap while armed calls `close()`
- [ ] Cancel the timer when the overlay closes; X button and VoiceOver escape keep closing immediately
- [ ] Both app targets build

## Acceptance criteria

- One tap on empty space (e.g. between volume-up and the arrow keys) does not close the D-pad and shows "Tap again to close" above the X button.
- A second tap on empty space within 1s closes the D-pad.
- After 1s without a second tap the hint disappears and the next tap on empty space counts as a first tap again.
- The X button closes the D-pad with one tap, with or without the hint showing.
- A swipe or drag starting on empty space does not close the D-pad.
- Tapping keys (arrows, volume, media) works as before and is not affected by the hint.
- VoiceOver: the X button ("Close") and the escape gesture close the D-pad in one step.

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
