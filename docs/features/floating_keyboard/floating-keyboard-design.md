# LazyRemote — iPhone Design Spec

Design-only reference for the remote screen in portrait and landscape. All measurements are in points. Canvas: 393 × 852 portrait, 852 × 393 landscape (iPhone 15/16 Pro class).

## 1. Principles
- Dark, quiet, content-first. The trackpad is the product; everything else stays out of its way.
- The trackpad fills every area not taken by the header (portrait) or the controls column (landscape). There is no persistent text field.
- Two floating tools — **Remote** and **Keyboard** — each with its own fixed dock slot. Tap to open, drag to float or re-dock.
- One accent color (system blue) for every interactive glyph and pressed state.
- Landscape: the Dynamic Island side is trackpad only. All controls sit on the opposite edge.

## 2. Color

| Role | Value |
|---|---|
| Screen background | `#000000` |
| Surface (trackpad, text field) | `#2C2C2E` |
| Surface raised (inactive send) | `#3A3A3C` |
| D-pad center | `#48484A` |
| Overlay controls (d-pad, ears, media) | `rgba(58,58,60,0.92)` |
| Round close button | `rgba(58,58,60,0.80)` |
| Floating button fill | `rgba(44,44,46,0.86)` + blur |
| Accent / pressed / caret / docked glyphs | `#0A84FF` |
| Connected dot | `#30D158` |
| Not-connected dot | `#FF9F0A` |
| Destructive / error | `#FF453A` |
| Primary text | `#FFFFFF` |
| Secondary text (status) | `rgba(235,235,245,0.60)` |
| Placeholder | `rgba(235,235,245,0.30)` |
| Separator | `rgba(84,84,88,0.65)` |
| Hairline inner stroke | `rgba(255,255,255,0.18)` |
| Tool overlay scrim (Remote, Keyboard) | `rgba(10,10,12,0.74)` + 10 blur |
| Spotlight scrim | `rgba(0,0,0,0.45)` + 14 blur |
| Sheet scrim | `rgba(0,0,0,0.40)` |

Disabled (not connected): trackpad 35% opacity; header/rail controls and floating buttons 50%; taps on tools do nothing.

## 3. Typography
System font (SF Pro).

| Use | Size / line height | Weight |
|---|---|---|
| Text field input | 17 / 22 | Regular |
| Menu items | 17 | Regular |
| Action sheet buttons | 20 | Regular (Cancel: Semibold) |
| Spotlight input | 22 / 28 | Regular |
| Spotlight result | 17 / 22 | Regular, matched part Semibold |
| Status text | 13 / 18 | Regular |
| Error pill | 12 / 16 | Regular |

## 4. Layout — Portrait

### Header (below status bar, starts y 59)
Padding 14 vertical / 20 horizontal, 12 gap, all items 32 × 32. Left to right:
1. Status: 8 dot, 8 gap, status text (truncates).
2. Keyboard dock slot (reserved while the keyboard is docked).
3. Remote dock slot (reserved while either tool is docked).
4. Spotlight button.
5. More (•••) button.

Fixed dock centers: Keyboard x 225, Remote x 269, both y 89. A slot never moves when the other tool leaves.

### Trackpad
Full width minus 20 each side, from below the header to 14 above the home-indicator zone (34). Radius 28. Empty surface.

### Floating buttons
- Snap to left (x 41) or right (x 352) edge, vertical range 150–760.
- Default: both floating on the right — Remote at y 560, Keyboard at y 632.
- Dropping into the header area (above y 120) or within 60 of the slot docks it.

## 5. Layout — Landscape

### Controls column (edge opposite the Dynamic Island)
x 14 from the edge, 32 wide, from y 20, 8 gap, items 32 × 32:
1. More (•••)
2. Spotlight
3. Remote dock slot — center y 116
4. Keyboard dock slot — center y 156

Slots are always reserved and fixed.

### Connection status
Same column, y 190 → 16 from bottom: 8 dot, 8 gap, status text set vertically, truncates.

### Trackpad
56 inset on both sides (Island side clearance; controls column on the other), 12 from top, 20 from bottom. Radius 28. Empty surface.

### Floating buttons
- Snap to the trackpad's island-side edge (center 93 from that edge) or controls-side edge (center 93 from that edge, clear of the column), vertical range 49–340.
- Default: both docked.
- Dropping in line with a slot near the column, or within 60 of it, docks it.

## 6. Floating Tool Buttons (Remote & Keyboard)
- Floating: 58 round, floating fill + blur, hairline inner stroke, shadow 0 8 24 `rgba(0,0,0,0.5)`, white 28 glyph.
- Docked: 32 slot, no background, blue 22 glyph.
- Glyphs: Remote — rounded phone outline with a ring and two dots. Keyboard — rounded rectangle with four key dots and a space bar.
- Drag: dashed 36 ring marks that tool's own slot; turns blue with `rgba(10,132,255,0.18)` fill when close enough to snap.
- Release: snaps to the nearer edge. If it would land within 70 of the other floating button on the same edge, it stacks 70 away.
- Motion: 0.28s ease-out position, 0.2s size/background. No transition while dragging.
- Both hidden while the Keyboard overlay or Spotlight is open.

## 7. Remote Overlay (tap Remote)
Tool overlay scrim; tap scrim or Close to dismiss. All controls: shadow 0 20 50 `rgba(0,0,0,0.5)`; pressed = accent fill, 0.12s.

| | Portrait | Landscape |
|---|---|---|
| Row | Brightness ear · D-pad · Volume ear, 6 gap, ears raised 69 | Same, 14 gap, vertically centered |
| Ears | 48 × 148, radius 24 | 44 × 132, radius 22 |
| D-pad | 236 circle | 210 circle |
| Center (Space) | 100 circle | 88 circle |
| Media row | 220 × 56, radius 28, at y 648 | 210 × 50, radius 25, 18 below row |
| Close | 44 round, bottom center, 40 from bottom | 44 round, top, 20 from top / 72 from controls edge |

- Ears: two halves, 5 gap, 24 glyphs.
- D-pad: four quadrants rotated 45°, 5 gap, 26 chevrons (3 stroke).
- Center: `#48484A`, 7 dark ring, inner top highlight.
- Media: three equal segments (prev / play-pause / next), 5 gap.

## 8. Keyboard Overlay (tap Keyboard)
Tool overlay scrim; system keyboard rises from the bottom with a compose row on top of it.
- Keyboard height: 336 portrait, 200 landscape.
- Compose row: Close (44 round, overlay fill) · Text field · Send (44 round), 10 gap.
  - Portrait: 12 vertical / 20 horizontal padding.
  - Landscape: 8 vertical padding, 56 inset each side.
- Field: `#2C2C2E`, radius 22, padding 11 / 16, hairline inner stroke, shadow 0 10 30 `rgba(0,0,0,0.4)`. Grows 1–5 lines portrait, 1–3 landscape.
- Send: accent when there is text and the Mac is connected, otherwise `#3A3A3C`. Sending clears the field and keeps the keyboard open.
- Uses the system keyboard's own delete and return keys.
- Delivery error pill: above the row, right-aligned, full radius, red text + warning glyph, auto-hides after 1.5s; text is kept.
- Dismiss: tap scrim or Close.

## 9. Spotlight
- Search field: 56 tall pill, `rgba(74,70,68,0.82)` + blur, 22 icon, hairline stroke.
  - Portrait: 14 side insets, y 70. Landscape: 540 wide, centered, 12 from top.
- Results card: radius 22, `rgba(58,56,55,0.82)`, 6 padding, 2 gap. Rows 52 min, radius 16, 36 rounded-square initial icon (radius 9). Top hit `rgba(255,255,255,0.12)` with an "Open" tag.
- Results cap: 370 portrait, 108 landscape (clears the keyboard).

## 10. Menus & Sheets
- **More menu**: 250 wide, `rgba(37,37,39,0.92)` + blur, radius 13, 44 rows, hairline separators. Items: Reconnect, Forget Mac (red). Portrait: below header, 16 from right. Landscape: beside the controls column, y 16.
- **Forget confirmation**: action sheet, message card radius 14 + separate Cancel card, 57 rows, 8 gap. Portrait: 8 side insets, 34 from bottom. Landscape: 380 wide centered, 29 from bottom.

## 11. Radii
Trackpad 28 · Media row 28/25 · Ears 24/22 · Spotlight results 22 · Text field 22 · Result row 16 · Sheet 14 · Menu 13 · Icons 9 · Round buttons full.

## 12. Spacing scale
5 (segment gaps) · 8 (column gap, dot gap) · 10 (compose gap) · 12 (header gap, top inset) · 14 (header padding, column offset) · 16 (menu offset) · 20 (portrait side insets) · 34 (home-indicator zone) · 56 (landscape side insets) · 70 (floating stack spacing).
