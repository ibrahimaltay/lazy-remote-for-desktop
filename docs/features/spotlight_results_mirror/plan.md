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
| 14 | How live keystrokes travel (QA 1.1) | whole string per key (needs select-all, a new command); new tag 12 that sets the field via AX (unproven); diff over existing text tag 3 + backspace key | ~~Diff over existing messages (`SpotlightTyper`)~~ **Superseded by 19** | No wire change was the appeal | Drifted on device (QA round 2): Spotlight's inline completion suffix swallows the first Backspace on the Mac |
| 15 | What "go" sends now | text then Enter; Enter only | ~~Enter only, once the Mac's field equals the query and nothing is in flight~~ **Readiness rule superseded by 20**; "go" still sends no text, only Enter, and an empty query still just closes | The text is already on the Mac. Supersedes decision 1 and AC5 of spotlight_search_design_update |
| 16 | Leftover Mac text (QA 1.2) | one backspace on open; blind n backspaces; filter display only; adopt via tag 10 + gate | ~~Adopt leftover via tag 10 and clear with backspaces~~ **Adoption superseded by 21**. The display gate stays: the card shows only when the query is non-empty and equals the Mac's typed text, keeping the last matching list while a newer one loads | The gate hides stale rows (replaces decision 11) |
| 17 | Streaming scope and safety | all keyboards; Spotlight overlay only | Spotlight overlay only; the text bar still trims and sends on submit. Overlay query is capped at 256 UTF-8 bytes and newlines become spaces (a newline would press Return and open the top hit) | User requirement. The cap now also matches tag 12's 256-byte limit (decision 19) |
| 18 | Spotlight already open on the Mac | accept; guard that needs a new "open but empty" signal | ~~Accept~~ **Mostly obsolete after 19**: queries are written only to the Spotlight search field, never as keystrokes, so typing can no longer reach the frontmost app. Only the Enter from "go" could (see decision 20) | Mac writes the element `SpotlightSearchField` only; if the panel is closed the write is dropped |
| 19 | How the query reaches the Mac (QA round 2) | keystroke diff (tried, drifted); set the field value through Accessibility | New message **tag 12 `spotlightQuery`**, clientInput lane, `[12] + UTF-8 (0..256 bytes)`, no length prefix, empty allowed (clears). The phone sends its full cleaned query on every change in the Spotlight overlay; the Mac sets the search field's value through AX. Newlines become spaces and the query is capped at 256 UTF-8 bytes on a character boundary on the phone; the decoder rejects over 256 bytes and invalid UTF-8 and fails the session. The text bar and tag 3 are unchanged | Spike on the user's Mac: the field accepts writes (set, replace and clear), the search re-runs within about 1s and the field value excludes the completion suffix. Idempotent, so no drift. User approved. Same lane as keys so it stays ordered ahead of the Enter key and Cmd+Space |
| 20 | When "go" presses Enter | immediately; wait for settle | Enter once the Mac's tag 10 `typed` equals the query and no new snapshot has arrived for 0.3s (the Mac sends only on change). If not settled after 2s, press Enter anyway. Empty query only closes. Reset on open, disconnect and reopen while pending | Setting the text re-runs the search, which takes up to ~1s; immediate Enter would open the previous top hit. User choice: Enter anyway on timeout, accepting that a slow search may open the wrong hit. Watch-off is held back until the pending "go" ends |
| 21 | Leftover Mac text (replaces 16's adoption) | adopt and backspace; clear by setting | On overlay open, after watch-on, the phone sends an empty tag 12, which clears the Mac field. The Mac retries the field lookup every 0.05s for up to 0.5s (the panel may not exist yet after Cmd+Space). After a reconnect with the overlay open, the phone resends the current query | Setting is exact whether or not macOS selects the leftover |
| 22 | Mac-side behaviour | any peer, focused element; watching peers only | Only for a peer that is watching; writes only the element with identifier `SpotlightSearchField` in `com.apple.campo` then `com.apple.Spotlight` (same 500-node, depth-25 caps, 0.5s messaging timeout); on the existing `spotlightQueue`, never the BLE queue; single latest-wins slot shared by all peers (at most one write running and one waiting). Field missing after the retry: log and drop; no keystroke fallback and the session stays up. Tag 12 from a non-watching peer is ignored | Fail closed, bounded, and nothing can be typed into another app |
| 23 | Phone-side coalescing and compatibility | keep every query; latest only | `RemoteClient.setSpotlightQuery` replaces the payload of a queued, not-yet-written tag 12 in place, otherwise enqueues on the input queue. `SpotlightTyper` is replaced by `SpotlightQuerySync` in `RemoteClientCore` (cleaning, dedupe against the last value sent, the `go` readiness rule with an injectable clock). A new phone against a Mac without tag 12 fails the session on the open-time tag 12 (same as the 1.5 key precedent); old phones (builds 13 and 14) keep working against a new Mac | Latest query is all that matters; both apps ship together |

## Scope

In: AX reader and parser on the Mac; two new wire messages; server push to opted-in peers; client decode; view model state; a minimal results list in the existing overlay; `docs/secure-protocol.md` update; tests.
Added after QA rounds 1-2: the Spotlight overlay sets the Mac's search field live through a new wire message (tag 12, decisions 19-23), `go` as Enter after the results settle, clearing leftover text on open, and the display gate.
Out (deliberately): tapping or selecting results, a guard for the Enter from "go" if the user closes Spotlight on the Mac inside the 0.3s settle window, multi-phone arbitration (last writer wins), icons, subtitles, chips, scrolling for rows below the fold, a settled/spinner indicator, `AXObserver`, a design for the list, Wi-Fi anything.

## Constraints

- **Wire change.** Update [docs/secure-protocol.md](../../secure-protocol.md) and codec/transport tests. Tags 1-9 are taken (9 is control confirmation only). New tags:
  - `10 spotlightResults`, **serverControl** lane: `count1` (0..8), `typed` then `count` titles, each as `len2 (UInt16BE) + UTF-8`. The server truncates typed to 256 and each title to 256 UTF-8 bytes on a character boundary and keeps only the first 8 rows (top to bottom), so the plaintext is at most 2,324 bytes, well under the 8,192 reassembly limit. `count 0` means nothing to show (also sent when Spotlight closes). The decoder rejects counts above 8, lengths past the end, trailing bytes and invalid UTF-8.
  - `11 spotlightWatch`, **clientControl** lane: `isOn1` (0 or 1). Only an approved peer may send it.
  - `12 spotlightQuery`, **clientInput** lane: `[12] + UTF-8 (0..256 bytes)`, plaintext 1..257 bytes, empty allowed (clear), no length prefix, no trailing-byte case. The decoder rejects over 256 bytes and invalid UTF-8; the encoder does not use `encodeString` (it rejects empty). `SecureInputDecoder` accepts key, pointer, text and spotlightQuery; tag 12 on the control lane fails with `wrongPhase`, and arriving at the phone fails as malformed. Update the "Only key, pointer, and text messages are accepted" sentence in docs/secure-protocol.md.
  - Existing decoders fail on unknown tags, so the client must not send tag 11 or 12 unless the overlay is open, and the server must not send tag 10 to a peer that has not opted in.
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

Round 2 fixes (decisions 19-23; replaces the Round 1 typer):

- [x] `RemoteProtocol`: add `SecureMessage.spotlightQuery(String)` (tag 12): encode `[12] + UTF-8` (0..256, empty allowed, throws oversized above 256), decode with the strictness in Constraints
- [x] `RemoteServerCore`: `SecureInputDecoder` accepts `.spotlightQuery`; `SpotlightReader.setQuery(_:) -> Bool` finds `SpotlightSearchField` in `com.apple.campo` then `com.apple.Spotlight` (same caps and 0.5s timeout), retries the lookup every 0.05s up to 0.5s, then `AXUIElementSetAttributeValue`; `RemoteServer` handles tag 12 only for watching peers, single latest-wins slot, writes on `spotlightQueue`, never keystrokes; drop and log if the field is missing
- [x] `RemoteClientCore`: `RemoteClient.setSpotlightQuery(_:)` (replace a queued tag 12 payload in place, else enqueue on the input queue; `Job.payload` becomes `var`); delete `SpotlightTyper`; add `SpotlightQuerySync` (`init(send:enter:)` plus injectable clock; `open()` resets and sends `""`; `update(_:)` cleans, caps and dedupes; `snapshot(typed:)` records arrival time; `go()` presses Enter once when `typed == query` and 0.3s have passed since the last snapshot, or after 2s anyway; `reset()` cancels, disarms and forgets the last value sent)
- [x] `RemoteViewModel` and overlay: replace the typer wiring with `SpotlightQuerySync`; the gate compares the cleaned query; resend the current query after reconnect; hold watch-off back until a pending `go` ends and accept results while it is pending; restore `onTextDelivered` to plain `show(...)`; remove `abandonSpotlightEdits`
- [x] `docs/secure-protocol.md`: tag 12 row (`12 spotlightQuery | UTF-8 (0..256 bytes) | 1..257 | clientInput`), the input-decoder sentence, the Delivery paragraph and limits, the "tag 12 is the one string that may be empty" note, the compatibility note (new phone with a Mac lacking tag 12 fails the session; old phones keep working)
- [x] Tests: codec cases in `SpotlightMessageTests` (empty, 256, 257, invalid UTF-8); input-lane accept and control-lane reject (`SecureInputDecoderTests` / `SpotlightLaneTests`); delete `SpotlightTyperTests`; new `SpotlightQuerySyncTests` (open sends "", dedupe, cleaning, Enter once after settling, Enter after the 2s timeout, no Enter on reset or empty query, reset clears the last-sent value so a reconnect resends); `xcodegen generate`; both targets build; `swift test`

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
- Every query change in the Spotlight overlay sets the Mac's Spotlight field through tag 12 with no key events and without pressing "go"; the normal text bar is unchanged.
- The Mac's field always equals the phone's cleaned query, including after deleting, replacing and pasting, and when Spotlight shows an inline completion suffix.
- Opening the overlay clears leftover text on the Mac (leftover "photos" then typing "p" leaves exactly "p").
- "go" sends only Enter: once the Mac's `typed` equals the query and 0.3s have passed with no new snapshot, or after 2s anyway; no Enter on reset, disconnect or reopen; an empty query only closes.
- At most one tag 12 is queued on the phone (latest replaces earlier) and at most one AX write waits on the Mac (latest wins).
- No result card while the phone's query is empty or differs from the Mac's typed text; the last matching list stays while a newer one loads.
- No newline reaches the Mac, and the overlay query never exceeds 256 UTF-8 bytes; the decoder rejects a 257-byte tag 12.
- Spotlight closed or field missing: nothing is typed anywhere and the session stays up.
- Malformed tag 12 (over 256 bytes, invalid UTF-8, on the control lane, from an unapproved peer) fails the session; tag 12 from a peer that is not watching is ignored.

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
| 1 | 2.0 (13) | Spotlight query is only sent to the Mac on "go"/Enter, but results are now live, so the Mac only searches after the whole word is sent. Expected: every keystroke typed in the phone's Spotlight overlay reaches the Mac's Spotlight live, for the Spotlight overlay only, not the general keyboard. (User-reported, device QA) | Major | architect (behavior change) | fixed (build 2.0 (15)) |
| 1 | 2.0 (13) | When Spotlight opens on the Mac it sometimes shows leftover text from the previous search; the phone field is empty so the phone shows results for text the user never typed. (User-reported, device QA) | Major | architect | fixed (build 2.0 (15)) |
| 2 | 2.0 (14) | Mac and phone text drift apart while typing live: Spotlight's inline completion suffix (e.g. 'chrome' + selected '— Google Chrome') swallows the first Backspace on the Mac, while the phone deletes a letter, so the two stay one letter apart (turning off Show all filename extensions does not help). Spike showed the Mac can set the search field value via Accessibility and the search re-runs. (User-reported, device QA) | Major | architect (design change: set the field value instead of replaying keystrokes) | fixed (build 2.0 (15)) |

## Open questions

1. **Row races.** Resolved by the display gate (decision 16): rows show only when the Mac's typed text equals the query.
2. **Settled indicator.** Does the phone need a spinner while rows load after the gate hides them? Judge in device QA.
8. **Device checks for set-the-field.** (a) Stale top hit: measure the time from the set to the rows changing; if old rows stay unchanged for over 0.3s, Enter opens the previous hit, so require a snapshot newer than the last send or a longer settle. (b) After Cmd+Space, is the 0.5s field lookup enough, and does macOS restore leftover text after the empty set? (c) Does AX list the field while the panel is hidden (a set would be harmless)? (d) The reader strips bidi isolates and turns NBSP into a space, so a phone query containing those never matches the gate. (e) Hung panel process: each write can block `spotlightQueue` for several 0.5s timeouts and delay reads, bounded and never on the BLE queue.
9. **Multiple phones** overwrite each other's query (last writer wins), and a Mac build that has tags 10 and 11 but not 12 fails the session as soon as a new phone opens the overlay. Confirm no such Mac build was released outside beta.
3. **OS fragility.** The panel host (`com.apple.campo`) and AX identifiers (`SpotlightSearchField`, `ResultCell`) were found on this macOS only. Test on another macOS version before shipping.
5. **Rows below the fold.** AX exposes only ~8 rows; showing more needs scroll handling.
6. **Tap to open.** The design already includes row tap (pressed fill, closes Spotlight). It is out of scope here; when added, tap needs a snapshot sequence so a tap maps to the row the user saw.
7. **Open tag.** The "Open" tag on the first row marks the top hit; the Mac's first row is the top hit, so it needs no extra field.
