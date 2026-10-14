# Spotlight results mirror

Status: in progress

## Goal

When the phone's Spotlight overlay is open and the user types, the overlay lists the results the Mac's Spotlight is showing, as text, updating as the Mac refines them. Display only: no tapping a result.

## Design inputs

- [Spotlight Results.html](Spotlight%20Results.html) and [design.md](design.md), as downloaded and never edited. They build on the shipped overlay ([spotlight_search_design_update](../spotlight_search_design_update/design.md)): scrim, pill and keyboard are unchanged.
- Replicate them exactly; the values live in design.md, not here. Card fill blur 30 is approximated with `.ultraThinMaterial` under the fill, as the pill is.
- Deviations from the design: the design shows tapping a row (pressed fill, then Spotlight closes). Tap is out of scope here, so rows have no press state and no action (see Open questions 4 and 6).

## Decisions

| # | Decision | Options considered | Choice | Why |
|---|----------|--------------------|--------|-----|
| 1 | How the Mac reads results | `mdfind`/`NSMetadataQuery`; OCR; Accessibility (AX) | AX tree of the Spotlight panel | Only AX returns what Spotlight actually shows (ranking, actions, settings rows). Spike proved it |
| 2 | Which process to read | `com.apple.Spotlight`; `com.apple.campo` | `com.apple.campo` (`Siri AI.app`), fall back to `com.apple.Spotlight`, else send nothing | On this macOS the panel lives in `Siri AI.app`; `com.apple.Spotlight` has no windows. Fail closed: no process means an empty list |
| 3 | What is sent | typed + titles; plus subtitles, chips, selection | Mac's typed text and the visible result titles, top to bottom | User choice; titles only, no icons, no tap |
| 4 | Row order and visibility | AX list order; sort by Y | Sort cells by Y and keep cells inside the panel window | Spike: row ids are unreliable, positions are not; screen shows ~7-8 rows |
| 5 | Refresh model | stream every change; send settled result only | Full replacement on every change, de-duplicated | Matches what the Mac shows, lag included. Settling is Open question 2 |
| 6 | Poll or observe | poll; `AXObserver` | Poll every 0.2s, only while a peer has the overlay open | Spike used polling and worked; observer is an upgrade |
| 7 | Compatibility | always push; client opts in | Client opts in with a new message; server pushes only to opted-in peers | An old phone fails the session on an unknown tag; an opt-in keeps old phones safe. A new phone on an old Mac still fails when it opts in, same as the 1.5 key precedent, so release both apps together |
| 8 | Wire shape | newline-joined; length-prefixed | UInt16BE length-prefixed UTF-8 strings | Titles can contain newlines; existing messages have a single trailing string, this has several |
| 9 | Tap a result | in scope; out | Out | User choice. The tap-vs-refresh race is a QA item |
| 10 | Privacy | filter; send all | Send all | User choice: the user's own phone |
| 11 | Stale rows vs typed text | tag and wait; ignore | ~~Ignore~~ Superseded by 16 after QA round 1 | Leftover Mac text showed rows for text the user never typed |
| 12 | Rows that fail the design's match rule | filter them out; show all, bold matches | Show every row the Mac sends; bold only matched characters | Mirrors the Mac. The "no matches" state means the Mac sent no rows |
| 13 | Row cap | 8 (what AX shows); 20 | 8 on the wire | User choice: the Mac exposes ~8 rows and that is enough. Raising it later changes the wire contract (old phones reject longer lists), so it needs an opt-in/version step |
| 14 | How live keystrokes travel (QA 1.1) | whole string per key (needs select-all, a new command); new tag 12 that sets the field via AX (unproven); diff over existing text tag 3 + backspace key | Diff over existing messages. A pure `SpotlightTyper` in `RemoteClientCore` replaces `SpotlightSubmitter`: common-prefix diff, backspace once per removed character, untrimmed text for the rest, one text in flight, edits typed meanwhile merge into the next flush | No wire change, no old/new compatibility cost; the ordered input queue keeps backspaces ahead of later sends. User approved. The AX set-value route stays an upgrade if the diff proves flaky on device |
| 15 | What "go" sends now | text then Enter; Enter only | Enter only, once the Mac's field equals the query and nothing is in flight; a failed send never presses Enter; empty query still just closes | The text is already on the Mac. Supersedes decision 1 and AC5 of spotlight_search_design_update |
| 16 | Leftover Mac text (QA 1.2) | one backspace on open; blind n backspaces; filter display only; adopt via tag 10 + gate | If a snapshot arrives before the typer has sent anything since open or reconnect, adopt its `typed` as the Mac's text and mark it dirty; the first flush then sends backspace x leftover length plus the full query (no shared prefix). The card shows only when the query is non-empty and equals the Mac's typed text, keeping the last matching list while a newer one loads | Correct whether or not macOS selects the leftover on open; backspace-on-open can delete in the user's document. The gate also hides stale rows (replaces decision 11) |
| 17 | Streaming scope and safety | all keyboards; Spotlight overlay only | Spotlight overlay only; the text bar still trims and sends on submit. Overlay query is capped at 256 UTF-8 bytes and newlines become spaces (a newline would press Return and open the top hit) | User requirement. 256 bytes bounds the worst-case backspace burst (512 key messages) under the client queue limit |
| 18 | Spotlight already open on the Mac | accept; guard that needs a new "open but empty" signal | Accept and check in device QA | User choice. If the phone's Cmd+Space closes an open Spotlight, live keystrokes go to the frontmost app; the shipped overlay had this for one send, live typing makes it worse. A guard needs a wire change |

## Scope

In: AX reader and parser on the Mac; two new wire messages; server push to opted-in peers; client decode; view model state; a minimal results list in the existing overlay; `docs/secure-protocol.md` update; tests.
Added after QA round 1: live per-keystroke typing in the Spotlight overlay only, `go` as Enter only, leftover-text adoption and the display gate (decisions 14-18). No wire change.
Out (deliberately): tapping or selecting results, automatic repair if the Mac and phone text drift apart, a guard for an already-open Mac Spotlight, the AX set-value route, icons, subtitles, chips, scrolling for rows below the fold, a settled/spinner indicator, `AXObserver`, a design for the list, Wi-Fi anything.

## Constraints

- **Wire change.** Update [docs/secure-protocol.md](../../secure-protocol.md) and codec/transport tests. Tags 1-9 are taken (9 is control confirmation only). New tags:
  - `10 spotlightResults`, **serverControl** lane: `count1` (0..8), `typed` then `count` titles, each as `len2 (UInt16BE) + UTF-8`. The server truncates typed to 256 and each title to 256 UTF-8 bytes on a character boundary and keeps only the first 8 rows (top to bottom), so the plaintext is at most 2,324 bytes, well under the 8,192 reassembly limit. `count 0` means nothing to show (also sent when Spotlight closes). The decoder rejects counts above 8, lengths past the end, trailing bytes and invalid UTF-8.
  - `11 spotlightWatch`, **clientControl** lane: `isOn1` (0 or 1). Only an approved peer may send it.
  - Existing decoders fail on unknown tags, so the client must not send tag 11 unless the overlay is open, and the server must not send tag 10 to a peer that has not opted in.
- **Security fail-closed.** No plaintext path. Malformed 10/11 fail the session like other tags. Server reads AX only for an approved, subscribed peer with the overlay open, and stops on off, disconnect or revoke.
- **Concurrency.** Swift 6. AX calls on one serialized queue off the main thread; hand results to the BLE queue with `Sendable` values. The parser is a pure function over plain value nodes so it is testable without AX.
- **Mac permission.** Accessibility is already required for input injection; no new prompt. Retain `remotectl` and use `scripts/make-app.sh` for bundled testing.
- **Structure.** Logic in the Swift package (`Sources/RemoteProtocol`, `RemoteServerCore`, `RemoteClientCore`); app shells stay thin. A new view file needs `xcodegen generate`.
- **Release.** Needs both iPhone and Mac to update (see the release-platform rule).

## Steps

- [x] Port the spike parser (`scripts/spike/spotlight_ax.swift` on `spike/spotlight-ax-results`) into `RemoteServerCore` as a pure `SpotlightSnapshot` parser over value nodes, plus a thin AX walker
- [x] `RemoteProtocol`: add `SecureMessage` cases and encode/decode for tags 10 and 11 with the limits above
- [x] `RemoteServerCore`: decode tag 11 in the approved client-control path; per-peer watch state; 0.2s poll while any peer watches; send tag 10 on change only, and only when that peer's notification queue is empty (mark a snapshot sent only when actually sent, so a skipped one is retried next tick with newer data; a full queue makes `enqueue` throw and ends the session); send an empty list when Spotlight closes; stop and clear on off, disconnect, revoke
- [x] `RemoteClientCore`: decode tag 10 from the server control lane; expose `spotlightResults` (`typed`, `titles`); `RemoteClient` sends tag 11 on/off
- [x] `RemoteViewModel`: publish results; overlay open sends watch on, close and disconnect send off; clear results on close
- [x] iOS overlay: minimal text list under the pill, VoiceOver-readable, no tap action
- [x] Update `docs/secure-protocol.md` (message table, limits, compatibility note, release gates note)
- [x] `xcodegen generate`; build both app targets; run `swift test`

Round 1 fixes (decisions 14-18):

- [x] `RemoteClientCore`: replace `SpotlightSubmitter` with a main-actor `SpotlightTyper` (closures `sendText(String) -> Bool` and `tap(Command)`; state `mac`, `target`, `inFlight`, `enterArmed`, `dirty`): `update(query)` caps at 256 UTF-8 bytes and replaces newlines with spaces; flush = common-prefix diff, backspace per removed character, untrimmed remainder as one text; `textDelivered` flushes what was typed meanwhile and presses Enter once in sync; a failed send stops and disarms Enter; `reset()` clears `mac`, `target`, `enterArmed` but keeps `inFlight`; adopt leftover from the first snapshot before any send and clear it with backspaces plus the full query
- [x] `RemoteViewModel`: `typeSpotlight(query)` and `goSpotlight()` replace `submitSpotlight`; the typer calls `client.send(text:)` directly (no trimming, no `.sending` guard, no bar status); every receipt goes to the typer, and the bar shows "Sent" only for sends from the bar; feed tag 10 `typed` to the typer; expose the display gate (non-empty query and `results.typed == query`, keep the last matching list while a newer one loads)
- [x] Overlay: `.onChange(of: query)` calls `typeSpotlight`; "go" calls `goSpotlight`; show the card through the gate
- [x] `docs/secure-protocol.md` Delivery section: the text bar trims; the Spotlight overlay streams untrimmed edits plus backspace keys
- [x] Rewrite `SpotlightSubmitterTests` as `SpotlightTyperTests` (append, delete, middle replace, merge while in flight, Enter once in sync, no Enter on failure, refused send arms nothing, reset disarms, leftover adoption incl. "photos" to "p", no adoption after the first send, reset keeps the in-flight gate, newline replaced, 256-byte cap); `xcodegen generate`; both targets build; `swift test`

## Acceptance criteria

- Opening the overlay turns the watch on; closing it, disconnecting or revoking turns it off and the Mac stops reading AX.
- With the overlay open and "Photos" typed, the list shows the titles visible in the Mac's Spotlight, in the same order, and updates as the Mac refines them.
- A title with a newline, over 256 bytes, or non-ASCII is delivered intact or truncated on a character boundary.
- Closing Spotlight on the Mac empties the phone's list.
- A peer that never opted in never receives tag 10.
- Malformed tag 10 or 11 (bad count, short length, trailing bytes, invalid UTF-8, wrong lane) fails the session; no plaintext fallback.
- No AX process found, or Accessibility denied, yields an empty list and no crash.
- Unchanged snapshots are not re-sent.
- Rapid result changes never fill a peer's notification queue: an update is skipped while that peer has frames queued, and the latest snapshot is sent once it drains.
- Each keystroke and deletion in the Spotlight overlay reaches the Mac without pressing "go"; the normal text bar is unchanged.
- "go" sends only Enter, after the Mac's text equals the query; no Enter if a send failed; an empty query only closes.
- Leftover text on the Mac is cleared by the first keystroke, whether or not macOS selected it (including leftover "photos" then typing "p" leaving exactly "p").
- No result card while the phone's query is empty or differs from the Mac's typed text; the last matching list stays while a newer one loads.
- No newline is ever injected, and the overlay query never exceeds 256 UTF-8 bytes.
- Rapid typing keeps one text in flight; edits made meanwhile are merged into the next send, in order.

## Done when

- [ ] Acceptance criteria verified by tests
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
| 1 | 2.0 (13) | Spotlight query is only sent to the Mac on "go"/Enter, but results are now live, so the Mac only searches after the whole word is sent. Expected: every keystroke typed in the phone's Spotlight overlay reaches the Mac's Spotlight live, for the Spotlight overlay only, not the general keyboard. (User-reported, device QA) | Major | architect (behavior change) | open |
| 1 | 2.0 (13) | When Spotlight opens on the Mac it sometimes shows leftover text from the previous search; the phone field is empty so the phone shows results for text the user never typed. (User-reported, device QA) | Major | architect | open |

## Open questions

1. **Row races.** Resolved by the display gate (decision 16): rows show only when the Mac's typed text equals the query.
2. **Settled indicator.** Does the phone need a spinner while rows load after the gate hides them? Judge in device QA.
8. **Device checks for live typing.** (a) Does this macOS select the leftover text on Cmd+Space? (b) Does Backspace on an empty Spotlight field do anything? (c) Does Spotlight's AX field value ever include inline autocomplete? The spike showed it holds only the typed text with the suggestion in a separate node, so exact equality should hold (it never matches for a query with a newline or over 256 bytes, since the phone sends it changed); if not, relax the gate to a case-insensitive prefix match. (d) Emoji, IME and some scripts (Thai, Indic, Korean) may delete less per Backspace; drift hides rows until the overlay is reopened.
9. **Already-open Spotlight** (decision 18): confirm in QA how often the phone's Cmd+Space closes an open Mac Spotlight and sends keystrokes to the frontmost app.
3. **OS fragility.** The panel host (`com.apple.campo`) and AX identifiers (`SpotlightSearchField`, `ResultCell`) were found on this macOS only. Test on another macOS version before shipping.
5. **Rows below the fold.** AX exposes only ~8 rows; showing more needs scroll handling.
6. **Tap to open.** The design already includes row tap (pressed fill, closes Spotlight). It is out of scope here; when added, tap needs a snapshot sequence so a tap maps to the row the user saw.
7. **Open tag.** The "Open" tag on the first row marks the top hit; the Mac's first row is the top hit, so it needs no extra field.
