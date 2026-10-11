# File Minimization Report

Date: 2026-10-11

**Implementation note:** The findings below are the original audit and retain the
reviewer's comments. The approved cleanup has now been implemented; see
[Implementation results and recovery](#implementation-results-and-recovery) for
the actual disposition. Historical paths and line numbers describe the baseline,
not the cleaned checkout.

## Summary

The best cleanup targets are obsolete plaintext-protocol helpers, three
byte-identical Mac icon copies, an unused website screenshot, and a tracked
generated plist. The largest local disk savings come from two unused Python
environments, not from application source.

These recommendations preserve the existing iPhone/Mac functionality unless
explicitly marked as a workflow or presentation tradeoff. This report does not
delete files or implement any recommended cleanup.

Before adding this report, the repository contained **86 tracked files**, totaling
**7,449,892 bytes (7.10 MiB)** of working-tree content. That excludes ignored
artifacts, Git history, and the existing untracked
`.github/copilot-instructions.md`. Measurements below describe this checkout;
they are not estimates of compressed downloads or installed app size.

## Method and confidence

I inspected the SwiftPM and XcodeGen target definitions, application entry points
and consumers, protocol specification, test references, scripts, documentation,
asset catalogs, and Pages deployment. I also decoded the website's embedded
manifest/template and compared duplicate assets using SHA-256.

An absent reference is not automatically proof of uselessness: SwiftUI app entry
points, asset-catalog metadata, privacy declarations, and manually invoked scripts
have consumers outside ordinary Swift symbol references. Public package APIs may
also have external consumers that this checkout cannot reveal.

**High confidence** means the duplication or lack of in-repository runtime use
was directly verified. **Conditional** means removal needs a workflow decision,
replacement, or preservation of useful content. Each finding includes the
required companion changes; none authorizes blind deletion.

## Recommended repository cleanup

### 1. Remove the legacy text-chunk codec and its dedicated tests

**Candidates:** `Sources/RemoteProtocol/TextChunk.swift` and
`Tests/RemoteProtocolTests/TextChunkTests.swift`.

**Confidence:** High for in-repository runtime non-use.
**Saving:** 2 tracked files, 3,592 bytes, and 92 lines of legacy code/tests.

**Justification:** All Swift references to `TextChunk` are confined to its
implementation, its dedicated tests, and a negative secure-transport test.
The current client sends whole `.text` messages
(`Sources/RemoteClientCore/RemoteClient.swift:239-258`); `SecureMessage` enforces
the 4096-byte limit, and the encrypted record is fragmented by `SecureFrame`.
The canonical specification explicitly says legacy TextChunk is not the secure
transport (`docs/secure-protocol.md:309-310`). Its dedicated tests therefore
exercise a superseded codec, not either app's current text delivery.

**Required companion changes:** Keep
`SecureTransportTests.testRawLegacyInputCannotBecomeSecureRecord`
(`Tests/RemoteSecurityTests/SecureTransportTests.swift:54-63`), replacing its
TextChunk construction with explicit legacy bytes, such as
`Data([3, 1]) + Data("secret".utf8)`. Update the codec inventory in `CLAUDE.md:12`
and the specification's description of helpers remaining in the package.
Preserve historical tag reservations and the prohibition on plaintext fallback;
do not reuse pointer tag 3. Retain current secure text, receipt, size-limit, and
fragmentation tests. Removing this public type is a package API change even
though it does not change the current wire protocol.

### 2. Remove unused plaintext approval and characteristic APIs

**Candidates:** `RemoteService.keyEventUUID`, `RemoteService.controlUUID`, and
the entire `ApprovalState` enum in
`Sources/RemoteProtocol/RemoteService.swift:11-15,23-36`.

**Confidence:** High for in-repository non-use.
**Saving:** Code only; retain `RemoteService.swift`.

**Justification:** A repository-wide Swift reference search found only these
declarations and `ApprovalState`'s self-reference. The client discovers only
secure characteristics (`RemoteClient.swift:597-606`), and the server publishes
and accepts only those secure characteristics
(`RemoteServer.swift:248-252,599-614`). Current approval uses authenticated
`SecureMessage.pending`, `.approved`, and `.revoked`, not `ApprovalState`.
The old comments describe plaintext traffic that is no longer supported.

**Required companion changes:** Keep the service UUID, secure UUIDs, and
`defaultName`. Update `docs/secure-protocol.md:47-50` so it no longer says these
constants remain in the package. Do not alter secure UUIDs, tags, or message
formats. Consider external package consumers before removing public APIs.

### 3. Deduplicate three Mac app-icon files

**Candidates:** Three redundant PNGs in
`macApp/Assets.xcassets/AppIcon.appiconset/`.

**Confidence:** High; each pair has identical SHA-256 hashes.
**Saving:** 3 tracked files, **207,206 bytes (202.35 KiB)**.

| Remove this copy | Reuse this identical file | Bytes saved |
| --- | --- | ---: |
| `icon_32x32.png` | `icon_16x16@2x.png` | 1,314 |
| `icon_256x256.png` | `icon_128x128@2x.png` | 44,028 |
| `icon_512x512.png` | `icon_256x256@2x.png` | 161,864 |

**Justification:** These are equal pixel-size representations with different
logical size/scale slots. The catalog currently stores the same bytes twice for
32px, 256px, and 512px images. Reusing the filename preserves the artwork and
all icon slots rather than removing supported sizes.

**Required companion changes:** Change the corresponding filenames in
`Contents.json:5,9,11` before deleting the copies. Keep all ten slot entries and
validate asset compilation with the Mac app build. The 1024px `AppIcon.png` and
the other unique PNGs are not duplicates. This reduces source files/bytes;
compiled asset-size savings are not guaranteed.

### 4. Remove the unused source screenshot and its Pages copy step

**Candidate:** `docs/screenshots/remote.png`.

**Confidence:** High for current checked-in website/README non-use.
**Saving:** 1 tracked file, **130,471 bytes (127.41 KiB)**; its deployed copy can
also disappear.

**Justification:** The README uses the four GIFs, not this screenshot. The only
tracked textual references to `docs/screenshots` are the Pages workflow and an
ignore-file comment. The website already embeds a byte-identical copy of this
PNG in its manifest, but explicitly removes the corresponding homepage image
before mounting the template (`site/index.html:339`). No decoded template link
points to `screenshots/remote.png`.

**Required companion changes:** Remove the screenshot copy step and matching
path trigger from `.github/workflows/pages.yml:9,30`, and retire the obsolete
`site/screenshots/` ignore entry/comment if nothing else generates it. Otherwise
the workflow's `cp docs/screenshots/*.png` will fail after the last PNG is
removed. Handle the embedded duplicate separately in finding 7.
If a previously published screenshot URL has external consumers, preserve that
URL or explicitly accept its retirement; local evidence cannot rule those out.

### 5. Stop tracking the generated Mac Info.plist

**Candidate:** `macApp/Info.plist` as a tracked file, not as a build input.

**Confidence:** High for redundancy; conditional on the generation workflow.
**Saving:** 1 tracked file, 1,110 bytes.

**Justification:** `project.yml:55-65` defines the plist path and its app-specific
properties, and the checked-in plist repeats those values plus standard bundle
keys. The iPhone plist and Xcode project already follow a generate-and-ignore
policy (`.gitignore:9-11`). Both the launcher and Mac release script run
`xcodegen generate` before building.

**Required companion changes:** Add `macApp/Info.plist` to `.gitignore` and remove
it from Git tracking. Keep `project.yml` as the source of truth and retain the
generated plist on disk when building. Verify a fresh generation/build recreates
it, and document that generation precedes direct Xcode use. Do not merely delete
the file and try to build an existing project without regenerating it.

### 6. Remove the unused server initializer argument

**Candidate:** `defaults: UserDefaults = .standard` in
`Sources/RemoteServerCore/RemoteServer.swift:75-85`.

**Confidence:** High for non-use.
**Saving:** Code only; no file removed.

**Justification:** The parameter is never read or stored. Server trust uses
`PeerTrustStore` and the injected `SecureKeyStore`, while the Mac view model owns
the actual Enabled preference. Every in-repository server construction either
uses defaults implicitly or passes only `keyStore:`.
This is a vestigial API parameter, not a reason to remove UserDefaults from the
client or Mac preference UI.

**Required companion changes:** Remove only this server parameter and check
external API consumers. Retain the key-store injection used by trust-reset
tests. No trust migration or wire-format change is needed.

## Website simplification

### 7. Remove the hidden screenshot from the bundled website

**Candidate:** Manifest entry
`20a252dd-24cf-4316-99d6-e07ac83e01ec`, its image element in the serialized
template, and the runtime image-removal statement.

**Confidence:** High.
**Saving:** No file removed, but **173,964 base64 data characters** plus manifest,
template, and runtime overhead can be removed from `site/index.html`.

**Justification:** The decoded image is exactly `docs/screenshots/remote.png`
(130,471 bytes). Although the loader decodes every manifest asset, line 339
removes this image from the parsed document before rendering. It therefore adds
source/download/decode work without contributing a visible image.

**Required companion changes:** Remove the manifest entry and template element
together, then remove the now-unnecessary statement at line 339. Verify the
homepage and all four demos still render. This saving is separate from the
tracked PNG saving in finding 4; the source PNG and its base64 copy are distinct
bytes. Do not count this again if implementing finding 8.

### 8. Replace the generated website wrapper with ordinary static HTML

**Candidate:** Most of the bundler/embedded component runtime in
`site/index.html:48-429`.

**Confidence:** High that it is disproportionate to the site's needs;
conditional because this is a rewrite, not a standalone deletion.
**Saving:** Substantial code and embedded data, but no guaranteed file-count
reduction. Exact savings depend on the replacement.

**Justification:** A 306,467-byte file implements three mostly static screens
through a manifest loader, gzip/base64 decoding, blob URLs, a document swap,
script re-execution, nested-frame relay machinery, and an embedded component
runtime. The page-order list is empty (`site/index.html:422-424`), and the
decoded template contains no iframes. Its navigation changes component state
between Home, Support, and Privacy. Ordinary HTML sections with anchor links
could provide this content without that machinery.

The decoded assets include 69,150 bytes of component runtime, 10,751 bytes of
React, and 131,835 bytes of ReactDOM. **React and ReactDOM are not currently
unused:** the runtime resolves them through `__resources` and mounts using
`ReactDOM.createRoot`. Removing those manifest entries alone would break the
site. Their removal becomes justified only after replacing their consumer.

**Required companion changes:** Preserve the download link, App Store badge,
four demos, support instructions, and privacy policy. Keep the existing Pages
workflow unless deployment is deliberately changed. Choose one maintainable
source for privacy text. Also resolve the existing URL mismatch: `PRIVACY.md:5`
points to `privacy.html`, and `plan.md:102` refers to that file, but no such file
is tracked or generated by the workflow; current privacy navigation is
in-memory state behind `href="#"`. A static rewrite should provide the promised
public route, even if that requires a useful additional file rather than fewer
files at any cost.

## Local disk cleanup, not repository file reduction

// I reviewed the section 9 manually, and I will need the python files in the animations folder to generate documentations for the future releases. But perhaps I do not need everything in this folder, a better approach would be to keep the environment and the py file that generated the latest animations, so that I can iterate on it next time and remove anything unnecessary / irrelevant.
### 9. Remove unused Python virtual environments

**Candidates:** `.venv/` and `animations/.venv/`; afterward `animations/` has
only Finder metadata and can be retired if no local work needs it.
**Confidence:** High for absence from documented app build/deployment flows;
conditional on whether the developer still uses them to author demos.
**Saving:** Approximately **400 MiB locally**: each directory occupies about
200 MiB. **Zero tracked files**.

**Justification:** There are no tracked Python sources, requirements files,
Python project manifests, or lockfiles. The inspected build and deployment
scripts use Swift, XcodeGen, Xcode, and shell tooling. Both environments contain
the same package/version inventory, including animation tooling, Pillow, and
NumPy. `animations/` contains no animation source outside its environment.
These are not app dependencies, although they may have been used to produce
the useful checked-in demo GIFs.

**Required precautions:** Preserve any desired environment/package inventory
before removal if future media generation relies on it. The environments are
currently hidden by their own internal `.gitignore` files, not root ignore
rules; add explicit root ignores if this tooling will be recreated. Do not
delete the GIFs merely because their authoring environments are removed.

### 10. Prune build caches and generated IDE artifacts selectively

**Candidates:** Rebuildable portions of `.build/`, generated
`MacRemote.xcodeproj/`, `.swiftpm/` workspace metadata, and `.DS_Store` files.

**Confidence:** High that these are not tracked application source.
**Saving:** `.build/` currently occupies about **1.86 GiB**; the Xcode project
about 72 KiB and `.swiftpm/` about 4 KiB. These are upper bounds, not promises
that all contents should be removed. **Zero tracked files**.

**Justification:** `.gitignore:1-3,9-11` already excludes build output, SwiftPM
metadata, Finder metadata, and the generated project. SwiftPM/XcodeGen can
recreate their build/project artifacts.

**Required precautions:** This checkout's `.build/` also contains release and
iOS archives, screenshots, trace logs, export configuration, and a signed CLI
app, not just caches. Preserve desired release artifacts, evidence, and local
configuration before pruning. Preserve custom schemes or IDE user state before
regenerating the project. Stop relevant builds first; subsequent builds will be
slower, and the CLI bundle needs rebuilding before injection tests.
Do not remove `project.yml` or `Package.swift`.

## Conditional workflow and organization reductions

// skip this one: 11
### 11. Retire the CLI harness only if that testing workflow is no longer wanted

**Candidates:** `Sources/remotectl/main.swift` and `scripts/make-app.sh`.

**Confidence:** Conditional; these are useful development tools, not dead code.
**Saving:** 2 tracked files and the executable target/product.

**Justification:** The shipping app targets depend on library products, not the
CLI (`project.yml:42-46,75-79`). The CLI is a separate executable
(`Package.swift:12,23-26`) for key injection, swipe shortcuts, BLE serving, and
client command sending. Its packaging script exists to supply a stable code
identity for Accessibility-controlled event injection. Removing both leaves the
apps' library dependency graph intact but sacrifices phone-free/manual testing.

**Required companion changes:** Remove the executable product/target from
`Package.swift` and update `CLAUDE.md`, `plan.md`, and
`.github/copilot-instructions.md` if that untracked instruction file is retained.
Keep the injectors and BLE libraries, which the apps still use.
**Recommendation:** Keep unless the harness is demonstrably abandoned; two
files are a modest cost for the documented testing capabilities.

### 12. Remove the convenience launcher if direct builds/installed launches suffice

**Candidate:** `Start Mac Remote.command`.

**Confidence:** Conditional.
**Saving:** 1 tracked file.

**Justification:** The script adds Finder double-click convenience: it opens an
installed app, otherwise finds or builds a Debug app. It is not part of an app
target or the release script. A documented Xcode build and normal application
launch can replace it, but the convenience is intentional.

**Required companion changes:** Remove the launcher reference from
`CLAUDE.md:29` and retain explicit generation/build instructions.
Do not remove `scripts/release-mac.sh`, which performs signing, notarization,
stapling, and DMG production that this launcher does not replace.

### 13. Consolidate redundant documentation only after preserving its unique purpose

**Candidates:** `plan.md`; overlapping guidance in `CLAUDE.md` and the existing
untracked `.github/copilot-instructions.md`.

**Confidence:** Conditional.
**Saving:** Potentially 1 tracked file by retiring `plan.md`; no automatic saving
from the two agent instruction entry points.

**Justification:** `plan.md` repeats architecture, transport, and build
information found in `CLAUDE.md` and `docs/secure-protocol.md`, but also records
distribution expectations and outstanding release gates. Deleting it without
preserving those gates loses useful information. The two agent instruction
files overlap substantially but are entry points for different tools; neither
is dead merely because their prose is similar.

**Required companion changes:** If retiring `plan.md`, move any unique release
requirements into an appropriate existing document and update `CLAUDE.md:7`.
If both agent tools remain in use, keep concise tool-specific entry points and
refer to shared existing documentation instead of maintaining two full copies.
Do not delete or overwrite the pre-existing untracked Copilot file as cleanup.
Keep the canonical secure-protocol specification.

// skip this one 14
### 14. Merge tiny app-local/model files only if file count outweighs discoverability

**Candidates:** `Sources/RemoteServerCore/PairedDeviceStore.swift` into
`RemoteServer.swift`, and `macApp/Models/LaunchAtLogin.swift` into
`macApp/ViewModels/ServerViewModel.swift`.

**Confidence:** Conditional; this is organization, not dead-code removal.
**Saving:** Up to 2 tracked files; no meaningful code or binary-size reduction.

**Justification:** `PairedDeviceStore.swift` contains only the active 20-line
`PairedDevice` value type, not a persistence store. The server publishes it and
the Mac menu and CLI use it. `LaunchAtLogin.swift` contains an active 25-line
helper used only by `ServerViewModel`. Both could live with their consumers.

**Required companion changes:** Preserve the declarations and visibility, add
the necessary `ServiceManagement` import when moving that helper, regenerate
the Xcode project after removing an app file, and update architecture references.
Renaming `PairedDeviceStore.swift` to `PairedDevice.swift` is the clearer
alternative but does not reduce file count. **Recommendation:** Low priority;
do not remove functionality or merge larger cohesive units merely to lower a
file-count metric.

## Files that should stay

| Files or group | Why removal is not justified |
| --- | --- |
| `Package.swift` and `project.yml` | Separate sources of truth for shared libraries/tests and platform application targets; neither replaces the other. |
| Current protocol, security, client, and server implementation files | Consumers exist in the apps or current tests. Framing, handshake, trust, approval, input injection, and lifecycle logic are essential, not optional compatibility debris. |
| `Command.swift` and `PointerEvent.swift` codecs | Despite historical comments about plaintext payloads, `SecureMessage` still uses both inner encodings. Removing them would break current secure messages. |
| Current `Tests/` other than the legacy TextChunk suite | Protect wire compatibility, fail-closed trust/reset behavior, encryption, input decoding, text receipts, and trackpad behavior. Small test files are not useless files. |
| `TrackpadTuning.json`, `TrackpadTuning.swift`, and `ScrollMomentum.swift` | The resource is declared in `Package.swift:20`, decoded by the client library, and used by the iPhone view model/trackpad; tests exercise tuning and momentum behavior. |
| `TextDeliveryTracker.swift` and `SecureInputDecoder.swift` | Small but active, directly tested helpers for receipt correlation and approval-gated secure input. |
| iPhone views and view model | RootView connects the trackpad, text input, floating remote button, and D-pad; gesture/keyboard behavior is live functionality, not unused alternative screens. |
| `RemoteIcon` and `RemoteIconFill` asset sets | Both are selected by `ServerViewModel.swift:74` for disconnected/connected menu-bar state. |
| App icons and asset `Contents.json` files | Catalog metadata and unique icon images are consumed by Xcode. Identical root metadata in the two app catalogs is not an invitation to delete one catalog's metadata. |
| `iOSApp/PrivacyInfo.xcprivacy`, `PRIVACY.md`, and `LICENSE` | Privacy declarations, published policy content, and licensing have purposes outside runtime symbol references. Resolve policy duplication/routes rather than dropping disclosures. |
| `readme-gifs/*.gif` | All four are referenced by both `README.md:17-35` and the website demo template. They total 4,671,311 bytes, about 62.7% of tracked bytes, but are useful product demonstrations. Compression is a size project; deletion is a presentation tradeoff. |
| `site/index.html` and `.github/workflows/pages.yml` | Provide the documented public website/support/privacy surface and its deployment. Simplify the implementation rather than discarding that surface. |
| `scripts/release-mac.sh` | Provides the distinct release/signing/notarization workflow and the unversioned DMG filename expected by the website. |

## Suggested order and expected outcome

1. Retire the legacy APIs/codecs and preserve the explicit rejection fixture
   (findings 1, 2, 6). This removes genuinely obsolete implementation rather than
   active features.
2. Deduplicate icons, remove the unused source screenshot with its workflow
   references, and stop tracking the generated Mac plist (findings 3-5).
3. Remove the hidden embedded screenshot or replace the website wrapper
   (finding 7 or 8). Do not add the two estimates together.
4. Separately prune unused environments and selected generated artifacts
   (findings 9-10), preserving local evidence/releases.
5. Consider workflow and organization cuts only after deciding that their
   useful capabilities are unnecessary (findings 11-14).

Findings **1, 3, 4, and 5** would remove **7 tracked files** and **342,379 bytes
(334.35 KiB)**, reducing the original tracked count from 86 to 79. Retaining
this report makes that 80. Findings 2 and 6 reduce code but not file count.
The hidden website screenshot offers additional content-size savings.
Deleting working-tree files does not remove their bytes from existing Git
history; no history rewrite is recommended.

After implementing actual removals, run targeted protocol/transport tests and
the relevant app builds; run `xcodegen generate` for app-file/project changes.
For website changes, check Home, Support, Privacy, the promised privacy route,
all demos, and Pages artifact construction. These are future cleanup acceptance
checks, not claims that this report implemented or built those changes.

This report was validated against the tracked inventory, symbol/reference
searches, asset hashes/catalog entries, and decoded website data. No application
source, configuration, asset, or existing untracked file was modified.

## Implementation results and recovery

The results below record the pre-merge cleanup checkpoint. After deploying these
builds to the connected physical iPhone and `/Applications/LazyRemote.app`, the
secure handshake reused the existing pairing and the user reported that manual
testing was successful, then authorized committing, merging to main, and pushing.
This supersedes the earlier no-commit/no-push restriction for publication.

Implemented on **`cleanup/file-minimization`**, based on
`6413dddbd985c18542a28f811b9f9bf1185d1a26` from `release/1.5-beta`.
**No commits, pushes, releases, or deployment were made.** Changes are left for
review. The path-specific removal of `macApp/Info.plist` from Git tracking is
staged; other edits are unstaged and added files are untracked.

| Findings | Actual disposition |
| --- | --- |
| 1, 2, 6 | Removed the legacy TextChunk implementation/tests, plaintext UUID/approval APIs, and unused server defaults argument. Kept the explicit legacy-rejection fixture and all current wire formats. |
| 3 | Removed three duplicate Mac PNGs, retaining all ten icon slots with identical image data. |
| 4, 5 | Removed the unused source screenshot and Pages copy references. Mac Info.plist is generated, present on disk, and ignored instead of tracked. |
| 7, 8 | Replaced the bundled website with static Home/Support and a directly accessible `privacy.html`. Removed the embedded hidden screenshot and runtime. Kept all four GIFs and the original badge as a local SVG, avoiding a frontend dependency. |
| 9 | The user's final instruction superseded the earlier preservation note: removed `animations/` completely and the root `.venv/` from the working directory into verified quarantine. No scripts were recovered into the active repository. |
| 10 | Quarantined selected stale Xcode cache/build directories, old site preview, empty SwiftPM metadata, and inventoried Finder metadata. Kept active `.build/out`, `.build/dd`, archives, export configuration, logs, screenshots, and IDE user state. |
| 11, 14 | Skipped as requested. CLI/packaging and separate model/helper files are unchanged. |
| 12, 13 | Removed the convenience launcher and repository `plan.md`. Migrated build/distribution instructions to README and preserved unfinished release gates in the canonical protocol document. Kept concise CLAUDE/Copilot entry points. |

Nine baseline tracked files are retired; two useful website files are added
(privacy page and original badge). This reduces the application/documentation
file set from **86 to 79**. Including this report and the pre-existing Copilot
instruction file makes **81 files** in the intended final tracked set; the added
files have not been staged.

The website's HTML and local badge total **32,214 bytes**, versus the former
306,467-byte bundled index: **274,253 bytes smaller (89.5%)**, excluding unchanged
demo GIFs in both cases. The GIFs themselves are byte-for-byte unchanged.
Local quarantine contains **995,740,641 bytes (about 950 MiB)** from 25 explicitly
identified paths. Those bytes remain in the recovery backup, so this is a
working-directory reduction, **not a claim of freed total disk space**.

Retained package tests, the `remotectl` product, the Mac app, and the iPhone
simulator app build passed. The staged Pages artifact's links, fragments, SVG,
and resource bytes were checked over local HTTP. Chrome checks at 320px and
1280px with page JavaScript disabled passed, including no horizontal overflow,
loaded demos/badge, navigation targets, and no external resource dependencies.
Screenshots were reviewed. Physical BLE and release certification gates remain
open; no cleanup check establishes those.

### Recovery backup

The verified private local backup is:

```text
~/.copilot/session-state/d55216d4-bc2f-4004-8bd8-d53707cdbef8/files/cleanup-recovery-6413ddd/
```

It contains the baseline file archive (including your edited report and original
untracked Copilot instructions), Git bundle, index/status snapshots, phase
checkpoints, quarantine with SHA-256 inventories, validation logs, screenshots,
and a path-specific recovery tool. Nothing was uploaded or committed.

From the repository, inspect recovery without making changes:

```sh
python3 "$HOME/.copilot/session-state/d55216d4-bc2f-4004-8bd8-d53707cdbef8/files/cleanup-recovery-6413ddd/restore.py" --check
```

To undo the cleanup, first stop builds/app processes using affected paths, then
run the same command with `--restore` instead of `--check`. The tool checks HEAD
and expected file hashes, refuses to overwrite later source edits, saves a
pre-restore snapshot, restores only listed cleanup paths and the original Mac
plist index entry, and copies quarantined local artifacts back without purging
the backup. If it reports newer edits, preserve/reconcile them before recovery.

After reviewing the restored status, `git switch release/1.5-beta` returns to the
original branch. **Switching branches alone does not undo uncommitted changes.**
No broad reset, history rewrite, or backup purge is required.

### Publication and main integration

The user approved publication after successful manual testing on the physical
iPhone and Mac. The cleanup was committed as `e2f3ed6` and merged into `main`.
Main's newer 13 feature-demo GIFs and matching README/site descriptions were
preserved during the website conflict resolution; they were not replaced with
the release branch's older four-demo collection. The inventory and byte counts
above describe the pre-merge cleanup checkpoint, not this combined main tree.

The local recovery tool intentionally refuses restoration after HEAD changes,
so it is **not an in-place rollback tool for the published merge**. The verified
baseline archive/Git bundle and quarantined data remain available privately.
For published code rollback, revert the merge with main as its first parent
(`git revert -m 1 <merge-commit>`), then validate and push normally rather than
rewriting shared history. Restore local quarantined artifacts separately if needed.
