# Marketing plan

Owned by the marketer agent. Update it before changing any GIF.

## Feature inventory

Every user-facing feature and how its promo should look. Group features that
live in the same part of the app into one promo.

| Feature | App section | Promo look |
|---------|-------------|------------|
| Move cursor | Trackpad | One finger drags; Mac cursor follows |
| Tap / double / triple tap to click | Trackpad | Tap ripple on phone, click on Mac |
| Two-finger double-tap right-click | Trackpad | Context menu opens on Mac |
| Two-finger scroll with momentum | Trackpad | Window scrolls and glides |
| Long-press drag | Trackpad | Item picked up and moved |
| Three-finger swipe (desktops, Mission Control, App windows) | Trackpad | Desktop switch / Mission Control |
| Floating remote button (drag anywhere, dock in top bar) | Floating remote | Tap opens the D-pad. Drag / dock is no longer shown in floating-remote.gif (user, 2026-10-12); the feature still exists |
| D-pad arrows (hold to repeat) | Floating remote | Slides / menu navigation |
| Play / Pause (media capsule under the pad) | Floating remote | Video pauses and resumes |
| Space (D-pad center key) | Floating remote | Shown on the pad; not animated yet |
| Brightness and volume keys (side capsules, hold to repeat) | Floating remote | Shown on the pad; not animated yet |
| Previous / next track (media capsule) | Floating remote | Shown on the pad; not animated yet |
| Text keyboard | Keyboard | Text typed on phone appears on Mac |
| Any language and emoji | Keyboard | Mixed-script text and emoji sent |
| Backspace / Enter (hold to delete) | Keyboard | Fast delete, then Enter |
| Spotlight (sends Cmd+Space; custom shortcut not supported) | Spotlight | Magnifier tap opens Spotlight, search typed |

## GIFs

One row per GIF in `readme-gifs/`. Source scenes live in `marketing/scenes/`
(shared visuals in `common.py`).

| GIF | Features covered | Scene source | Status |
|-----|------------------|--------------|--------|
| trackpad-basics.gif | Move, tap / double tap (triple not shown), right-click | scenes/trackpad_basics.py (TrackpadBasics) | published (v4, 4.3 s, 1.5 MB) |
| trackpad-gestures.gif | Scroll with momentum, long-press drag, three-finger swipe | scenes/trackpad_gestures.py (TrackpadGestures) | published (v4, 4.9 s, 4.7 MB) |
| floating-remote.gif | Floating button tap (drag / dock not shown), D-pad arrows, Play / Pause | scenes/floating_remote.py (FloatingRemote) | published (v5, 2.6 s, 0.8 MB) |
| keyboard.gif | Text keyboard, any language and emoji, Backspace / Enter | scenes/keyboard.py (Keyboard) | published (v4, 4.4 s, 2.9 MB) |
| spotlight.gif | Spotlight | scenes/spotlight.py (Spotlight) | published (v4, 4.0 s, 1.5 MB) |

Quality: the user lifted the 2 MB cap (2026-10-12). `make-gif.sh` now renders 1920x1080 at 60 fps and writes a 30 fps, 256-color, sierra-dithered 960x540 GIF with no size limit (set `MAX_KB` to re-enable one). Its `inspect` step is not fatal: faithful UI has small text and overlays the checker flags, so read its list and the storyboard. SF Symbols and the Mac menu-bar icon are rendered from the real assets by `marketing/sfsymbol.swift` (cached in `.build/marketing/symbols/`).

## Style decisions

Settled; follow without re-asking. Add to this list when the user decides or
implies something new.

- Not tutorials: no captions, titles, step labels or badges. Only real UI text and the small LazyRemote mark.
- Fast, eased, loopable motion (last frame matches the first); about 3-5 s per GIF; show the feature, not the setup.
- Visible touch feedback on the phone: fading trail for moving fingers, ring on taps and key presses.
- Quality first: 960x540 from a 1080p/60 fps render, no size cap.
- The UI matches the real app's SwiftUI code. Accent is the system blue (the app sets none). Dark mode only. Triple-tap is not shown.
- The Mac side copies the look of the original GIFs (silver MacBook, purple wallpaper, menu bar, Notes, "Cinema" app, Spotlight bar); common.py is now its reference.
- Brightness, volume, Space and previous/next appear on the D-pad but are not animated.
- floating-remote shows tap to open, use, close. Moving and docking the button is not shown; README and site captions must mention it.

## UI reference

What the app really shows, taken from the Swift source (2026-10-12). `marketing/scenes/common.py`
mirrors these; each helper names its Swift file. iPhone layout is in points on a 393 x 852 screen,
dark appearance, default accent (systemBlue).

| Screen / state | Swift source | What is on screen |
|----------------|--------------|-------------------|
| Idle | iOSApp/Views/RootView.swift, TrackpadView.swift, TextInputBar.swift, FloatingRemoteButton.swift | Header: green dot + Mac name (footnote, secondary), `magnifyingglass`, `ellipsis.circle` (32 pt buttons, accent). Trackpad: systemGray5, corner 28, full height, caption2 tertiary hint "Tap to click · Two fingers to scroll · Two-finger double-tap to right-click". Input bar: "Type to send…" field (systemGray5, corner 20) + 42 pt `delete.left` and `return` circles. Floating button: 58 pt material circle, `appletvremote.gen4` 28 pt, default spot right edge (inset 41) at 66% height |
| Docked button | FloatingRemoteButton.swift, RootView.swift | 22 pt accent `appletvremote.gen4`, no background, left of the magnifier. While dragging: 36 pt dashed ring at the dock, accent with 18% fill when near |
| Keyboard open | RootView.swift, TextInputBar.swift | Black 40% scrim over header + trackpad (trackpad is not resized; keyboard covers it). Input bar rides above the keyboard; 42 pt `arrow.up` send button appears (accent when there is text, systemGray4 otherwise). Floating button hidden. Sending closes the keyboard and clears the field |
| Spotlight | RootView.swift, TextInputBar.swift | Magnifier sends Cmd+Space and opens the keyboard state with the prompt "􀊫 Spotlight Search" |
| Hold backspace | TextInputBar.swift | Button turns accent with white glyph; one delete now, repeats after 450 ms every 60 ms |
| D-pad open | iOSApp/Views/DPadOverlay.swift | Dark material + black 60% backdrop. 236 pt pad 44 pt below center: four wedges (systemGray4, 5 pt gaps, `chevron.*` 26 pt semibold), center Space key (100 pt, systemGray3, `space` 30 pt). Side capsules 48 x 148: `sun.max`/`sun.min` left, `speaker.wave.3`/`speaker.wave.1` right. Media capsule below: `backward`, `playpause`, `forward` (70 x 56 segments). 44 pt `xmark` close 40 pt from the bottom. Pressed key = accent fill |
| Mac menu bar item | macApp/MacRemoteApp.swift, macApp/Views/StatusMenu.swift, ServerViewModel.swift | `RemoteIcon` / `RemoteIconFill` (connected) template image; the menu has status text, Enabled, pairing items, Launch at Login, About, Quit |
| Mac side otherwise | none (not in the code) | Follows the original 13 GIFs: silver MacBook, purple wallpaper, menu bar with clock, dark "Cinema" app, Notes, light browser, Spotlight bar |

## Decision log

Each run: what was kept, updated, deleted or added, and why.

| Date | Feature / GIF | Decision (keep / update / delete / add / merge) | Why |
|------|---------------|-------------------------------------------------|-----|
| 2026-10-12 | All 13 old GIFs | merge 13 -> 5 | Fewest GIFs that still show every feature: one per app section, gestures split in two to stay under about 5 s each. Old GIFs had captions inside the frame and no scene source; the new ones are text-free, loopable and rebuilt from `marketing/scenes/` |
| 2026-10-12 | trackpad-move, tap-click, right-click | merge into trackpad-basics.gif | Same part of the app (one-finger and tap interactions on the trackpad) |
| 2026-10-12 | scroll, drag, three-finger-swipe | merge into trackpad-gestures.gif | Same kind of interaction (multi-finger and held gestures) |
| 2026-10-12 | floating-remote, dpad-arrows, play-pause | merge into floating-remote.gif | Same part of the app (floating button and D-pad). User asked to drop the drag / dock steps to save time; the README caption covers placing and docking instead |
| 2026-10-12 | keyboard, any-language, backspace-enter | merge into keyboard.gif | Same part of the app (text input bar) |
| 2026-10-12 | spotlight | update (spotlight.gif re-rendered) | Kept as its own GIF; redrawn to match the real UI |
| 2026-10-12 | All 5 new GIFs | update | First drafts were drawn from README wording; user found the UI did not match, so every helper was redone from the SwiftUI source (v3), then finger trails and tap ripples added so the touch is visible (v4) |
| 2026-10-12 | 13 old GIF files | delete | Deleted by the user after approving the 5 replacements; the 3 "-new" files were renamed to the freed names |
| 2026-10-12 | README "See It in Action" and Features | update | 13 images -> 5 with one short caption each; Features list gained Floating remote, Gestures, and Any language and emoji. Site updated in a separate step (next row) |
| 2026-10-12 | site/index.html "See It in Action" and Features | update | User approved the site update: 13 figures -> the 5 final GIFs with the README captions and alt text; Features list gained the same three bullets; the wrong "Play/Pause in the center" caption replaced (center key is Space). pages.yml copies readme-gifs/*.gif, so it needs no change |
