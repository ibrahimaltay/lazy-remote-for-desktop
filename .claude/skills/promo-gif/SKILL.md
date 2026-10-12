---
name: promo-gif
description: Create or update a LazyRemote promo GIF with ManimGX. Use when asked to make, redo, merge or shrink a feature demo GIF for the README and website.
argument-hint: <scene description or existing gif name>
---

Make the promo GIF described in $ARGUMENTS. Follow the `manimgx` skill, including
fetching https://manimgx.academa.ai/llms.txt each run; this skill adds the repo
conventions.

0. The real app is the source of truth for every pixel of UI. Before drawing
   anything, read the SwiftUI views for the screens involved: `iOSApp/Views/`
   (TrackpadView, DPadOverlay, FloatingRemoteButton, TextInputBar, RootView) and
   `macApp/Views/` plus the view models they use. Take layout, proportions, colors,
   SF Symbol names, labels, and which elements appear in each state from the code.
   Do not invent UI elements or guess; if the code does not show something, leave
   it out or ask. When you change `common.py`, note which Swift file each helper
   mirrors in a one-line comment.
1. Check `marketing/marketing-plan.md` for what the GIF must show and which
   features it covers. Do not invent features that are not in the inventory.
2. Reuse before creating. Read `marketing/scenes/common.py` and the existing
   scenes next to it first. Build the scene from the shared helpers (iPhone
   frame, Mac window, cursor, touch ripple, colors) with
   `from common import ...`. If a piece will be needed by more than one GIF and
   is missing, add it to `common.py` instead of writing it inline; never
   duplicate a helper. If `common.py` does not exist yet, create it from the
   first scene's shared pieces, matching the look of the existing GIFs in
   `readme-gifs/` (view a frame first). Keep helpers backward compatible, since
   old scenes must still render; if a visual change to a helper is intended,
   list which GIFs need re-rendering and tell the marketer.
3. Write the scene to `marketing/scenes/<name>.py`, one `m.Scene` subclass.
   Show the iPhone gesture and the resulting Mac reaction together. Not a
   tutorial: no captions, titles, badges or explanatory text in the GIF, only
   text that is part of the real UI being shown. Fast, smooth, eased motion with
   no idle waits; aim for 4-6 seconds, loopable.
4. Run `marketing/make-gif.sh marketing/scenes/<name>.py <SceneClass> <name>`.
   It inspects (fix any layout problems it reports), renders, and converts to
   `readme-gifs/<name>.gif` at 960x540, high quality, no size cap. Do not convert by hand.
5. Open the GIF and check it. Say what you did not check.
6. Update the GIF table in `marketing/marketing-plan.md`.

README and site edits are the marketer agent's job, not this skill's.
