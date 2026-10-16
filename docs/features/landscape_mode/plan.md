# Landscape mode

Status: in progress

## Goal

Use the iPhone remote in landscape (both directions) with the layout from the
design, so the trackpad gets the whole screen and the controls stay out of its way.

## Design inputs

- [design.dc.html](design.dc.html) and [design.md](design.md), as downloaded and never edited.
- Replicate them exactly; the values live in design.md, not here.
- Deviations from the design:
  - Controls column sits on the side opposite the Dynamic Island (design draws it on the Island side); see decision 1.
  - Remote overlay keeps the two-tap backdrop close and "Tap again to close" hint (decision 3).
  - Text bar stays single line (decision 5).
  - Delivery error pill is not built (decision 6).
  - More menu and Forget confirmation stay the system `Menu` / `confirmationDialog` (decision 7).
  - Follows system light/dark instead of forced dark (decision 8).
  - Portrait is unchanged.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | Landscape directions and column side | Both mirrored on Island side; both with column opposite the Island; Island-left only | Both directions; controls column on the side opposite the Island | User choice: keeps the controls clear of the Island. Costs about 40pt of trackpad width (the Island-side inset stays empty). |
| 2 | Phones without an Island | Same layout; real safe area on the notch side | Use the real safe area on the notch side (larger of design inset and safe area) | Nothing clips on notch/Home-button models. |
| 3 | Remote overlay close | One tap on backdrop (design); keep two taps within 1s | Keep two-tap rule and hint; X moves to the design's top-right spot (one tap closes); hint sits just below the X | Two-tap was a deliberate shipped fix (`close_remote_controller_view_on_double_tap`). |
| 4 | Remote button default | Docked both; docked landscape only; keep floating | Docked in both orientations (one saved setting, new installs only) | Matches the design; avoids per-orientation state. Floating position stays one shared fraction, clamped to the landscape snap range. |
| 5 | Text bar height | Single line; 1-3 lines with `UITextView` | Single line | Avoids reopening `live_keyboard` cursor-lock and Return decisions. |
| 6 | Delivery error pill | Build it; out of scope | Out of scope | No visible failure path exists today; would apply to portrait too, so a separate feature. |
| 7 | More menu and Forget sheet | Custom per design; keep system | Keep system components | System positions them correctly in landscape. |
| 8 | Color scheme | Force dark in landscape; follow system | Follow system with existing system colors | Rotating must not flip appearance; dark values already match closely. |
| 9 | Rotation behavior | Rebuild views; keep same views | Keep the same views across rotation; follow system rotation lock; overlays re-lay out while open | Keyboard, typed text and gestures survive rotation. |
| 10 | Promo GIFs and marketer | Marketer reviews after QA; skip | Skip the marketer entirely: no promo GIFs, no marketer phase | User decision. |

## Scope

In:
- Add both landscape orientations to `project.yml`.
- Landscape `RootView` layout: controls column (•••, Spotlight, dock slot), vertical connection status, trackpad, text bar; mirrored by Island side.
- Landscape positions for the floating remote button and its dock slot.
- Landscape sizes for the remote overlay and Spotlight.
- Protect the top edge from system swipes in landscape (as the bottom edge is today).
- Docked default for the remote button.

Out (deliberately):
- Portrait changes (apart from the docked default).
- Multi-line text bar, error pill, custom menu/sheet, forced dark mode, iPad.
- The "Mac Menu Bar" screen in `design.dc.html`.
- Anything under `Sources/`, wire format, BLE, or the Mac app.

## Constraints

- iPhone-only change: no wire format, pairing or Mac app change, so `docs/secure-protocol.md` is untouched.
- Keep testable logic in the package; the layout is an app-shell concern.
- Island side is not exposed by SwiftUI; read it from the window scene's interface orientation. This is the main risk.
- Swift 6 strict concurrency; app Info.plist is generated, so edit `project.yml` and run `xcodegen generate`.

## Steps

- [x] Add `UIInterfaceOrientationLandscapeLeft` and `UIInterfaceOrientationLandscapeRight` to `project.yml`; run `xcodegen generate`.
- [x] `RootView`: pick layout from size (wide = landscape) and keep the same views with `AnyLayout`. Ignore horizontal and bottom safe areas, lay out by hand per design.md, with the column opposite the Island and the Island-side inset taken from the safe area.
- [x] Vertical connection status in the column, ellipsis truncation.
- [x] `TrackpadView` and `TextInputBar`: paddings follow orientation.
- [x] `FloatingRemoteButton`: landscape snap range, dock slot in the column, docked default.
- [x] `DPadOverlay`: landscape sizes, X top-right, hint below X, two-tap close kept.
- [x] `SpotlightOverlay`: 540 pill 12 from top, results capped near 108.
- [x] Defer system gestures on the top edge in landscape.
- [x] Build both app targets, run `swift test`.

## Acceptance criteria

- Rotates to both landscape directions and back to portrait; the system rotation lock is respected.
- Portrait looks and behaves exactly as before.
- In landscape the frames and insets match design.md; the column is opposite the Island; nothing is clipped by the Island or home indicator, including on phones without an Island.
- Rotating while typing keeps the keyboard and text and sends no reset; rotating mid-drag or mid-scroll leaves no stuck mouse button.
- The remote button docks, floats and snaps to the trackpad's left or right edge within the landscape range; a dashed ring shows the dock slot during a drag; docked is the default for new installs.
- Remote overlay fits landscape with the design sizes; the X closes in one tap; empty space needs two taps within 1s and shows the hint.
- Spotlight pill is 540 wide in landscape and results stay clear of the keyboard; live query and "go" behave as before.
- Send button shows only while typing; cursor lock and Return behave as in `live_keyboard`.
- A swipe starting near the top or bottom of the trackpad does not trigger a system gesture on the first try.
- Release is iPhone only.

## Done when

- [x] Acceptance criteria verified by tests: none; user accepted device QA as the only verification (layout logic is app-shell, not extracted)
- [x] `swift test` passes
- [x] Both app targets build
- [x] Tester findings resolved with the developer
- [x] Last QA round: every acceptance criterion passes on device, no open issues
- [x] Marketer skipped by user decision (decision 10); no promo GIFs

## QA log

Only the user and the tester agent may add or change rows here. One row per
issue found in manual QA. Minor bug (code wrong, plan right) goes to the developer, then the tester, then a redeploy. Design or behavior problem
(plan wrong) goes back to the architect and gets a new row in Decisions.

| Round | Build | Issue | Severity | Routed to | Status |
|-------|-------|-------|----------|-----------|--------|
| 1 | commit 85715d5 | In landscape the remote button docks to the trackpad instead of the side. User's screenshot (device, Island on left, column on the right) shows the dashed dock ring inside the trackpad about 60pt left of the controls column, level with the gap under the search button, instead of in the reserved dock slot in the column (third slot under More and Spotlight). Expected: ring and docked button sit in the column's dock slot. | Minor (plan right, code wrong) | developer | closed (fixed in 8efb22d, verified on device by the user) |

## Open questions

- Resolved (plan approved): with the column opposite the Island, the column keeps the design's mirrored insets (x 14, trackpad starts at 56 from that edge) and the Island-side trackpad inset is the system safe area (about 59pt) instead of 16.
