# LazyRemote — iPhone Landscape Design Spec

Design-only reference for the landscape remote screen. All measurements are in points on an 852 × 393 canvas (iPhone 15/16 Pro class), Dynamic Island on the left.

## 1. Principles
- Dark, quiet, content-first. The trackpad is the product; everything else stays out of its way.
- Use as much of the screen as possible. Only the Dynamic Island side gets a generous inset; all other edges are tight.
- One accent color (system blue) for every interactive glyph and pressed state.

## 2. Color

| Role | Value |
|---|---|
| Screen background | `#000000` |
| Surface (trackpad, text field, round buttons) | `#2C2C2E` |
| Surface raised (inactive send, pad center) | `#3A3A3C` / `#48484A` |
| Overlay controls (d-pad, ears, media) | `rgba(58,58,60,0.92)` |
| Accent / pressed / caret | `#0A84FF` |
| Connected dot | `#30D158` |
| Not-connected dot | `#FF9F0A` |
| Destructive / error | `#FF453A` |
| Primary text | `#FFFFFF` |
| Secondary text (status) | `rgba(235,235,245,0.60)` |
| Tertiary text (placeholders) | `rgba(235,235,245,0.30)` |
| Separator | `rgba(84,84,88,0.65)` |
| Remote-overlay scrim | `rgba(10,10,12,0.74)` + 10pt blur |
| Spotlight scrim | `rgba(0,0,0,0.45)` + 14pt blur |
| Typing scrim | `rgba(0,0,0,0.40)` |

Disabled state (not connected): trackpad at 35% opacity, controls at 50%.

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

## 4. Layout (landscape)

### Insets
- Left (Dynamic Island side): controls column at x 14; content starts at x 56.
- Right: 16.
- Top: 12 to trackpad.
- Bottom: text bar sits 16 above the screen edge (clear of the home indicator).

### Regions
1. **Left column** (x 14, 32 wide), stacked top to bottom from y 20, 8 gap:
   - More (•••) button — 32 × 32
   - Spotlight button — 32 × 32
   - Remote dock slot — 32 × 32 (always reserved, even when the remote is floating)
2. **Connection status** — below the Dynamic Island (y 268 → 34 from bottom), same column: 8pt dot, 8 gap, status text set vertically. Truncates with ellipsis.
3. **Trackpad** — x 56 → right 16, y 12 → 76 from bottom. Corner radius 28. No text inside — the surface is left fully empty.
4. **Text bar** — x 56 → right 16, 8 vertical padding. Field: radius 20, padding 11 / 16, grows 1–3 lines. Send button (42 round) appears only while typing, 10 gap. Uses the system keyboard's own delete and return keys; no custom ones.

### Keyboard
- Landscape keyboard height: 200. Text bar rides on top of it; the rest of the screen dims.

## 5. Floating Remote Button
- Floating: 58 round, `rgba(44,44,46,0.86)` + blur, hairline inner stroke `rgba(255,255,255,0.18)`, shadow 0 8 24 `rgba(0,0,0,0.5)`, white 28pt glyph.
- Docked: 32 slot in the left column, no background, blue 22pt glyph.
- Default: docked.
- Drag: while dragging, a dashed 36 ring marks the dock slot (blue when close enough to snap).
- Release: snaps to the left (x 93) or right (x 799) edge of the trackpad, vertical range 49–280.
- Animation: 0.28s ease-out position, 0.2s size/background.

## 6. Remote Overlay (tap the remote)
Full-screen scrim, controls centered in a column, 18 gap:

- **Row** (14 gap): Brightness ear — D-pad — Volume ear, vertically centered.
  - Ears: 44 × 132, radius 22, two halves with 5 gap, 24pt glyphs.
  - D-pad: 210 circle, four quadrants rotated 45°, 5 gap, 26pt chevrons (3pt stroke).
  - Center (Space): 88 circle, `#48484A`, 7pt dark ring, inner top highlight.
- **Media row**: 210 × 50, radius 25, three equal segments (prev / play-pause / next), 5 gap.
- **Close**: 44 round, `rgba(58,58,60,0.8)`, top-right (20 from top, 72 from right).
- All controls: shadow 0 20 50 `rgba(0,0,0,0.5)`. Pressed = accent fill, 0.12s.

## 7. Spotlight
- Search field: 540 wide, centered, 12 from top. 56 tall, pill shape, `rgba(74,70,68,0.82)` + blur, 22pt icon.
- Results: card radius 22, `rgba(58,56,55,0.82)`, 6 padding, 2 gap. Rows 52 min height, radius 16, 36pt rounded-square initial icon (radius 9). Top hit highlighted `rgba(255,255,255,0.12)` with an "Open" tag.
- Results area capped at about 108 so it clears the keyboard.

## 8. Menus & Sheets
- **More menu**: 250 wide, opens to the right of the ••• button (x 54, y 16). `rgba(37,37,39,0.92)` + blur, radius 13, 44 rows, hairline separators. Items: Reconnect, Forget Mac (red).
- **Forget confirmation**: centered action sheet, 380 wide, 29 from bottom. Message card radius 14 + separate Cancel card, both 57 rows, 8 gap.
- **Delivery error pill**: above the text bar, right-aligned, radius full, red text with warning glyph, auto-hides after 1.5s.

## 9. Radii summary
Trackpad 28 · Media row 25 · Ears 22 · Spotlight results 22 · Text field 20 · Menu 13 · Sheet 14 · Result row 16 · Icons 9 · Round buttons full.

## 10. Spacing scale
5 (segment gaps) · 8 (column gap, bar padding) · 10 (bar gap) · 12 (top inset) · 14 (row gap, left column x) · 16 (right/bottom inset) · 18 (overlay stack gap) · 20 (close button offset).
