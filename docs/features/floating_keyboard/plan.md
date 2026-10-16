# Floating Keyboard

Status: in progress

## Goal

The Keyboard becomes a second floating tool beside Remote. Each tool has its own fixed dock slot, can be dragged to float or re-dock, and opens on tap. The persistent text bar goes away; the trackpad fills the space, and typing happens in a Keyboard overlay.

## Design inputs

- [floating-keyboard-design.html](floating-keyboard-design.html) and [floating-keyboard-design.md](floating-keyboard-design.md), as downloaded and never edited. Values are taken from the `.md`.
- Replicate them exactly; the values live in the design, not here.
- Deviations from the design:
  - Default dock state: both tools docked in both orientations (design: portrait both floating on the right). Decision 1.
  - Compose field stays single line (design: grows 1-5 / 1-3 lines). Decision 2.
  - No delivery error pill; a dropped edit still clears the field (design: text is kept). Decision 3.
  - SF Symbols for the Remote and Keyboard glyphs instead of custom drawn ones. Decision 5.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | Default dock state | Follow design (portrait floating, landscape docked); one flag per tool; both floating | Both tools docked by default | User choice. One flag per tool, same in both orientations; existing `remoteFab.*` state is kept |
| 2 | Compose field growth | Keep single line; move to `UITextView` | Keep single line | Moving would reopen live_keyboard decisions 7, 11, 14 (Return, empty-field backspace, cursor lock) and IME handling |
| 3 | Delivery error pill | Out of scope; pill plus keep reset; keep text on drop | Out of scope | Keeping text on a drop breaks the fail-closed re-baseline. Same as landscape decision 6 |
| 4 | Keyboard overlay vs focus | Overlay open = field focused; separate overlay state | Open means the field is focused (`isTyping`) | Reuses the existing focus binding and its stale-inset fix; rotation survival comes free. *Proposed* |
| 5 | Tool glyphs | SF Symbols (`appletvremote.gen4`, `keyboard`); custom Shapes | SF Symbols | User choice; same precedent as the existing Remote |
| 6 | Remote overlay scrim | Keyboard only gets the design scrim; both | Both use the design scrim; Remote keeps two-tap close | One-value change, tools look alike. *Proposed* |
| 7 | Overlap after rotation | Stack rule on release only; also at layout | Also at layout, Keyboard yields | Same pure function. *Proposed* |
| 8 | Colors | Follow system; force dark on compose row | Follow system, force dark on the compose row | The scrim is always dark, as `DPadOverlay` does. *Proposed* |
| 9 | Release | iphone / mac / both | iphone | iPhone-only change, no wire or Mac change |

## Scope

In: second floating/dockable Keyboard tool; two fixed dock slots in the portrait header and the landscape column; drag, snap, dock per tool; the 70pt stacking rule; hiding both tools while the Keyboard overlay or Spotlight is open; removing the persistent text bar; Keyboard overlay with design scrim and compose row (Close, field, Send); Send accent only with text and a connection; disconnected state (tools 50%, taps ignored); motion timings per the design.
Out (deliberately): multi-line field, error pill, custom glyphs, custom More menu or sheet, wire/BLE/Mac/Spotlight changes, any change to live-keyboard semantics. Promo GIFs are decided by the marketer after QA (the existing `keyboard.gif` will be stale).

## Constraints

BLE only; no wire or protocol change, so `docs/secure-protocol.md` is untouched. Live-keyboard guarantees stay: cursor lock, Return presses Return on the Mac, empty-field backspace deletes on the Mac, IME held until committed, close or reconnect clears the field and sends nothing, edits never replayed. Swift 6 strict concurrency; view model stays `@MainActor`. Testable logic in the package (no iOS test target), app shells thin. Remote overlay two-tap close preserved. Design files not edited. Run `xcodegen generate` if app files are added, renamed or removed.

## Steps

- [x] Package: pure `FloatingToolLayout` helper in `Sources/RemoteClientCore/` (stack-70 rule with range clamp and fallback side) plus `RemoteClientCoreTests`
- [x] App: generalize `FloatingRemoteButton` into `FloatingToolButton` (glyph, label, storage prefix, own dock center, other tool's floating center); 0.28s ease-out position / 0.2s size; keep `remoteFab.*`, add `keyboardFab.*`
- [x] App: portrait header with Keyboard slot (x 225) and Remote slot (x 269), fixed dock centers
- [x] App: landscape column with Remote slot (y 116) and Keyboard slot (y 156), status from y 190, dock when dropped in line with a slot
- [x] App: remove the persistent bar; trackpad bottom 14 portrait / 20 landscape; snap ranges portrait 150-760, landscape 49-340
- [x] App: Keyboard overlay (tool opens focus, design scrim, tap scrim or Close dismisses, both tools hidden, modal accessibility)
- [x] App: restyle `TextInputBar` (Close, field, Send per design; Send state from has-text and connected; force dark)
- [x] App: `DPadOverlay` backdrop to the design scrim, keep two-tap close
- [x] `xcodegen generate` if needed; `swift test` passes; both app targets build

## Acceptance criteria

1. No text field is visible unless the Keyboard overlay is open. The trackpad reaches 14 above the home-indicator zone in portrait and 20 from the bottom in landscape.
2. Portrait header: Keyboard slot at x 225, Remote slot at x 269 (393 wide); the Keyboard slot does not move when Remote leaves. Landscape: Remote slot y 116, Keyboard slot y 156, always reserved.
3. Each tool docks only into its own slot (portrait: dropped above y 120 or within 60; landscape: within 60 or in line with the slot). The dashed 36 ring marks the dragged tool's slot and turns blue when a release would dock.
4. A release that does not dock snaps to the nearer edge within the design range; within 70 of the other floating button on the same edge it lands exactly 70 away, inside the range (package tests).
5. A drag under 5pt is a tap. When disconnected, tools are 50% and taps do nothing.
6. Tapping Keyboard shows the scrim and compose row on the system keyboard and hides both tools. Scrim tap, Close, or dismissing the system keyboard closes it; the field is cleared and nothing is sent.
7. Send is accent only with text and a connection; it presses Return on the Mac, clears the field and keeps the keyboard open.
8. All live_keyboard criteria still hold.
9. Rotating with the overlay open keeps keyboard and text and sends no reset. Rotating with both tools floating leaves them non-overlapping.
10. Remote overlay works as before (two-tap close). Spotlight hides both tools and works as before.
11. Positions and dock state of both tools persist across launches; existing installs keep their Remote state.

## Done when

- [ ] Acceptance criteria verified by tests (UI-only criteria need device QA)
- [x] `swift test` passes
- [x] Both app targets build
- [x] Tester findings resolved with the developer
- [ ] Last QA round: every acceptance criterion passes on device, no open issues
- [ ] Marketer has reviewed the promo GIFs for this feature (after QA passes)

## QA log

Only the user and the tester agent may add or change rows here. One row per
issue found in manual QA. Minor bug (code wrong, plan right) goes to the developer, then the tester, then a redeploy. Design or behavior problem
(plan wrong) goes back to the architect and gets a new row in Decisions.

| Round | Build | Issue | Severity | Routed to | Status |
|-------|-------|-------|----------|-----------|--------|

## Open questions

- Decisions 4, 6, 7, 8 are the architect's recommendations, marked *Proposed*; confirm or change on approval.
