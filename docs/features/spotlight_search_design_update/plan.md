# Spotlight search design update

Status: in progress

## Goal

Tapping the header magnifier opens a dimmed, blurred Spotlight overlay with a floating search pill, matching the design. "go" types the query on the Mac and opens the top hit.

## Design inputs

- [Spotlight Search.html](Spotlight%20Search.html) and [design.md](design.md), as downloaded and never edited.
- Replicate them exactly; the values live in design.md, not here.
- Deviations from the design: pill background blur 30 is approximated with `.ultraThinMaterial` under the 82% fill (SwiftUI cannot set an exact backdrop radius). The scrim blur of 14 is exact.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | What "go" sends | text only; text then Enter; live-type | Text, then Enter once `textStatus` is `.sent`; no Enter on failure | It is what "go" means; avoids Enter racing the text |
| 2 | Tap on dimmed area | close overlay only; also close Mac Spotlight | Close overlay, clear query, send `.spotlight` again unless a send is in flight | Keeps Mac and phone in step, as today |
| 3 | "go" with empty query | do nothing; close overlay | Close the overlay (same as scrim tap) | User choice (differs from the HTML) |
| 4 | Header icon | SF Symbol; custom `Shape` | Custom `Shape` with the design geometry | Design values win; about 15 lines |
| 5 | Pill blur | material; fill only; `UIVisualEffectView` | `.ultraThinMaterial` under the fill | Closest in pure SwiftUI |
| 6 | Appearance | dark only; add light | Literal design hex values in both appearances, no light variant | Design is dark only |
| 7 | Mac Spotlight drift | detect; keep limitation | Keep the limitation | Out of scope |

## Scope

In: header icon, Spotlight overlay (scrim, blur, pill, field), open/close behaviour, removing the Spotlight mode from `TextInputBar`, VoiceOver labels (scrim "Close Spotlight" action).
Out (deliberately): showing Mac results on the phone, custom shortcuts, protocol/server changes, light mode, new animations beyond the existing 0.2s ease-out fade.

## Constraints

No wire change; `docs/secure-protocol.md` untouched. `Command.spotlight` already exists. App shells stay thin: the send-text-then-Enter logic goes in `RemoteViewModel` (or `RemoteClientCore` if it needs package tests). Swift 6: UI work is main-actor. A new view file needs `xcodegen generate`. Do not edit design files.

## Steps

- [x] Add a magnifier `Shape` with stroke parameters (header 1.7/1.9, pill 1.6/1.8)
- [x] Replace the header icon: `#0A84FF`, explicit 50% opacity when disconnected
- [x] Build `SpotlightOverlay` (own query and `@FocusState`), presented from `RootView`; blur content 14, hide FAB
- [x] Wire closing: scrim tap and "go" (empty) close and clear; scrim also sends `.spotlight`; "go" with text sends it, then Enter on `.sent`
- [x] Remove `isSpotlight` from `TextInputBar` and `RootView`
- [x] Test send-then-Enter-on-`.sent` and no Enter on failure
- [x] `swift test`, build both app targets, `xcodegen generate` if a file was added

## Acceptance criteria

1. Header magnifier is `#0A84FF`, 18pt, in a 32x32 hit area; at 50% opacity and inert when disconnected.
2. Tapping it sends one `.spotlight`, shows the full-screen scrim (45% black, blur 14) and the pill per design.md, focuses the field with a "go" return key. FAB and its docked slot are hidden.
3. Empty query shows the "Spotlight Search" placeholder at `#EBEBF5`/55%; typed text is white, 22pt, one line.
4. Tapping the scrim closes the overlay, clears the query, sends one `.spotlight`. Nothing reaches the trackpad, keys or bottom bar.
5. "go" with a query sends it (trimmed, at most 4096 UTF-8 bytes), closes the overlay, then sends Enter only after `.sent`. A failed send shows "Not confirmed" and sends no Enter.
6. "go" with an empty query closes the overlay.
7. The bottom `TextInputBar` always shows "Type to send…" and behaves as before.
8. VoiceOver can open Spotlight and close it via a labelled scrim action.

## Done when

- [ ] Acceptance criteria verified by tests
- [x] `swift test` passes
- [x] Both app targets build
- [x] Tester findings resolved with the developer
- [x] Last QA round: every acceptance criterion passes on device, no open issues
- [x] Marketer has reviewed the promo GIFs for this feature (after QA passes)

## QA log

Only the user and the tester agent may add or change rows here. One row per
issue found in manual QA. Minor bug (code wrong, plan right) goes to the developer, then the tester, then a redeploy. Design or behavior problem
(plan wrong) goes back to the architect and gets a new row in Decisions.

| Round | Build | Issue | Severity | Routed to | Status |
|-------|-------|-------|----------|-----------|--------|

## Open questions

- Do key and text messages share an ordered lane? Developer to check; the Enter-after-`.sent` rule holds either way.
  - Answer: yes. Key and text are both clientInput-lane messages through the same FIFO `enqueueInput` queue in `RemoteClient`, so a key sent after text cannot overtake it. Enter still waits for `.sent` (decision 1), because the receipt means the Mac injected the text.
