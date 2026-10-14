# Live Keyboard

Status: in progress

## Goal

Typing in the iPhone text bar updates whatever input is focused on the Mac live, key by key, instead of sending the whole message on submit. Autocorrect, predictive text and dictation edits show up on the Mac as they happen.

## Design inputs

No design changes, therefore no inputs.

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | Base branch | stay on old main; fast-forward to origin/main | origin/main (c96573d) | Live Spotlight (tags 10-12) is merged there; avoids tag collisions |
| 2 | Mechanism | Phone-side diff to keystrokes; set value via Accessibility; raw `UIKeyInput` | Phone-side diff to keystrokes | Works in any app (web, Electron, Terminal); keeps autocorrect/dictation; no Mac text sent to the phone |
| 3 | Current send-on-submit bar | Replace; toggle; live default plus send for pastes | Live replaces it | User choice |
| 4 | Wire | New tag 13 `textEdit`; reuse key + tag-3 text | New tag 13, iPhone and Mac released together | Fire-and-forget, no one-outstanding-text limit, no lag at typing speed |
| 5 | Phone cursor leaves the end | Ignore; re-baseline and clear; mirror with arrows | Re-baseline (clear phone field, send nothing) | Mid-text edits would otherwise land wrong on the Mac. *Proposed* |
| 6 | Phone field contents | Only this session's typing, cleared on close; keep; fill from Mac | Session only, cleared on close | No Mac content goes to the phone. *Proposed* |
| 7 | Return key | Always presses Return; newline plus separate Enter button | Always presses Return on the Mac | Matches a real keyboard. *Proposed* |
| 8 | IME composition (Japanese/Chinese) | Send committed text only; send in-progress too | Committed only (skip while `markedTextRange` is set) | Avoids flicker on the Mac. *Proposed* |
| 9 | Password fields | Type like any keyboard; detect and block | Type like any keyboard | Traffic is encrypted; no AX detection needed. *Proposed* |
| 10 | Spotlight overlay | Keep AX value-set path; move to live-edit path | Unchanged | Already works. *Proposed* |
| 11 | Backspace in empty phone field | Deletes on the Mac; nothing | Deletes on the Mac | Real-keyboard feel. *Proposed* |
| 12 | Disconnect/reconnect | Replay pending edits; re-baseline without sending | Re-baseline, never replay | Edits are not idempotent; matches the no-retry rule. *Proposed* |
| 13 | Release | iphone / mac / both | both | Mac must understand tag 13 |
| 14 | Phone cursor (supersedes 5, from QA) | Clear field on cursor move; lock cursor to end; retype tail; select-all replace; mirror with arrows | Lock the phone cursor to the end of the text | Tapping mid-text cleared the phone but not the Mac, so they differed. Locking keeps the cursor equal to the Mac's; no wire change. Typos are fixed by backspacing. Reset stays as a safety net |

## Scope

In: `LiveTextSync` in `Sources/RemoteClientCore/` (diff the last-sent text against the new text by common prefix/suffix, emit delete count plus insert string; `reset(to:)` re-baselines without sending); tag 13 `textEdit` on the client-input lane (`deleteCount` UInt16 big-endian, capped, then UTF-8 insert; at least one non-empty); Mac `KeyInjector.edit(delete:insert:)` (backspace N times, then existing `type`); `RemoteServer` handling on its serial queue; iOS text bar becomes a `UIViewRepresentable` text field that overrides `deleteBackward()` and respects `markedTextRange`; remove the send button and the one-outstanding-text path for the bar; update `docs/secure-protocol.md`.
Out (deliberately): reading the Mac's focused text via Accessibility, mirroring phone cursor moves to the Mac, Spotlight overlay changes, promo GIFs unless the marketer proposes one after QA.

## Constraints

Wire format changes: new tag 13 (confirm the next free tag in `docs/secure-protocol.md` before coding; tags 10-12 belong to live Spotlight). Update the spec plus `SecureMessage` and `SecureInputDecoder` tests. Fail-closed: out-of-range delete count, invalid UTF-8, empty edit, or tag 13 on the control lane fails the session; no legacy fallback, so an old Mac fails closed. Bytes are delivered with response, never replayed. Swift 6 strict concurrency; injection stays on the server's serialized queue. Logic in the package, app shell thin. Backspace counts are grapheme clusters; a few apps delete complex emoji per code point (known limit).

## Steps

- [x] Protocol: add tag 13 `textEdit` to `SecureMessage` and the input decoder with limits; update `docs/secure-protocol.md`
- [x] `RemoteClientCore/LiveTextSync` (diff, reset) and `RemoteClient` send path
- [x] `RemoteServerCore`: `KeyInjector.edit(delete:insert:)` and `RemoteServer` handling
- [x] iOS: live text field (`UIViewRepresentable`) in the text bar, remove send button, re-baseline on cursor move, disconnect and close
- [x] Tests: codec, decoder, `LiveTextSync` (autocorrect replace, emoji boundary, newline, delete-only, reset), `KeyInjector`
- [x] Both app targets build
- [x] iOS (decision 14): lock the `LiveTextField` cursor to the end (`closestPosition(to:)` returns end; `selectedTextRange` setter snaps to end except during `markedTextRange`; drop Select/Select All from the edit menu); keep the reset as a safety net
- [x] Both app targets build again after the cursor lock

## Acceptance criteria

- Each character typed on the phone appears in the Mac's focused input without pressing send.
- Backspace on the phone deletes on the Mac, including when the phone field is empty.
- An autocorrect or dictation replacement results in the right text on the Mac (delete then insert).
- Return on the phone presses Return on the Mac.
- Tapping, long-pressing or dragging in the phone field never moves the cursor away from the end, and text cannot be selected (cursor lock, decision 14).
- Closing the bar or reconnecting clears the phone field and sends nothing.
- While Japanese/Chinese composition is in progress, nothing is sent until it commits.
- An out-of-range or malformed tag 13 frame, or tag 13 on the control lane, fails the session.
- Spotlight overlay behaves as before.

## Done when

- [x] Acceptance criteria verified by tests (UI-only and Mac-injection criteria need device QA)
- [x] `swift test` passes
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
| 1 | iPhone 2.0 (16) / Mac 2.0 (6), commit 5146dbc | Tapping elsewhere in the phone text field clears the phone field but the Mac keeps its text, so phone and Mac differ (user-reported). | Design/behavior (plan wrong) | Architect, resolved by Decision 14 (lock phone cursor to end); developer implementing | Open until the cursor lock is verified on device |
| 1 | iPhone 2.0, commit 677ca2c | After opening the keyboard and dismissing it by tapping elsewhere (the scrim), the layout does not return: the text bar stays raised and the trackpad stays shrunk, leaving an empty black band at the bottom (user-reported, screen recording). | Minor bug (plan right, code wrong) | Developer, then tester | Open |

## Open questions

- Decisions 5-12 ("Proposed") were the architect's defaults, approved together with the plan.
- Confirm the next free tag number in `docs/secure-protocol.md`.
