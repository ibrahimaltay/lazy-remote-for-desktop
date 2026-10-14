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
| 11 | Stale rows vs typed text | tag and wait; ignore | Ignore | User choice: assume the lag is invisible; judge in device QA |
| 12 | Rows that fail the design's match rule | filter them out; show all, bold matches | Show every row the Mac sends; bold only matched characters | Mirrors the Mac. The "no matches" state means the Mac sent no rows |
| 13 | Row cap | 8 (what AX shows); 20 | 8 on the wire | User choice: the Mac exposes ~8 rows and that is enough. Raising it later changes the wire contract (old phones reject longer lists), so it needs an opt-in/version step |

## Scope

In: AX reader and parser on the Mac; two new wire messages; server push to opted-in peers; client decode; view model state; a minimal results list in the existing overlay; `docs/secure-protocol.md` update; tests.
Out (deliberately): tapping or selecting results, icons, subtitles, chips, scrolling for rows below the fold, a settled/spinner indicator, `AXObserver`, a design for the list, Wi-Fi anything.

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

## Open questions

1. **Row races.** The spike showed rows can trail the typed text ("pho" showed "ph" results, "l" showed "photos" results). Mirrored faithfully, but the phone is also ahead over BLE. Judge in device QA; the fix is to tag rows with the typed text.
2. **Settled indicator.** Does the phone need a spinner or dimmed list while rows are stale? Needs the same typed-text tagging.
3. **OS fragility.** The panel host (`com.apple.campo`) and AX identifiers (`SpotlightSearchField`, `ResultCell`) were found on this macOS only. Test on another macOS version before shipping.
5. **Rows below the fold.** AX exposes only ~8 rows; showing more needs scroll handling.
6. **Tap to open.** The design already includes row tap (pressed fill, closes Spotlight). It is out of scope here; when added, tap needs a snapshot sequence so a tap maps to the row the user saw.
7. **Open tag.** The "Open" tag on the first row marks the top hit; the Mac's first row is the top hit, so it needs no extra field.
