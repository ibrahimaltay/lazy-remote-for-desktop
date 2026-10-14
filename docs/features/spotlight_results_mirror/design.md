# Spotlight Search Results: Design Specs

Reference: `Spotlight Results.html`. Frame 1 shows the query "P" with results. Frame 2 shows a query with no matches.
This builds on `design_handoff_spotlight_search/design.md`. The scrim, search pill, and keyboard are unchanged.
Units are pt on a 393×852 screen (iPhone 15/16 Pro), dark appearance.

## Scope
- The results list appears as soon as the query has at least one character and at least one match.
- - Results arrive as text only (for example `Preview.app`), so each row uses a generic letter icon instead of the real app icon.

## Layers (bottom → top)
1. Existing screen. Visible and blurred.
2. Scrim
3. Search pill
4. Results card (directly below the pill)
5. Keyboard

## Results card
| Property | Value |
|---|---|
| Position | 10 below the search pill (top = 136) |
| Left / right inset | 14 (same as the pill). Width 365 |
| Max height | 370. Scrolls vertically when there are more rows |
| Corner radius | 22 |
| Fill | `#3A3837` (rgb 58, 56, 55) at 82% opacity |
| Background blur | 30 |
| Border | 0.5 inner stroke, `#FFFFFF` at 14% opacity |
| Shadow | x 0, y 10, blur 30, `#000000` at 40% opacity |
| Padding | 6 |
| Gap between rows | 2 |
| Empty | No card at all (empty query or no matches) |

## Result row
| Property | Value |
|---|---|
| Height | 52 (minimum) |
| Corner radius | 16 |
| Padding | 8 left, 12 right |
| Icon to text gap | 12 |
| Fill, default | None |
| Fill, top hit (first row) | `#FFFFFF` at 12% opacity |
| Fill, pressed | `#FFFFFF` at 16% opacity |

### Generic icon
| Property | Value |
|---|---|
| Size | 36×36 |
| Corner radius | 9 |
| Fill | Vertical gradient, `#8E8E93` (top) → `#636366` (bottom) |
| Border | 0.5 inner stroke, `#FFFFFF` at 22% opacity |
| Glyph | The first character of the result, uppercased |
| Glyph font | SF Pro Semibold, 17, `#FFFFFF`, centered |
| Same for all rows | Yes. Do not use per-app colors |

### Title
| Property | Value |
|---|---|
| Text | The result string exactly as received (keep `.app`) |
| Font | SF Pro Regular, 17 / 22 |
| Color | `#FFFFFF` |
| Matched characters | SF Pro Semibold. This is the part of the word that matches the query |
| Overflow | Single line, ellipsis at the end |

### Top-hit tag (first row only)
| Property | Value |
|---|---|
| Label | "Open" |
| Height | 24, padding 9 left/right |
| Corner radius | 7 |
| Fill | `#FFFFFF` at 16% opacity |
| Font | SF Pro Medium, 13 |
| Color | `#EBEBF5` at 75% opacity |
| Position | Right edge of the row, vertically centered |

## Matching and order (visual rules)
- A result matches when any word in it starts with the query. Words are split on spaces, `.`, `_`, and `-`. Matching is case-insensitive.
  - Example: "P" matches `Raspberry Pi Imager.app` through "Pi", and only the "P" of "Pi" is bold.
- Rows appear in the order received. The first row is the top hit.

## Sample data (query "P")
Preview.app · Pages.app · Raspberry Pi Imager.app · Phone.app · Photos.app · Podcasts.app · Passwords.app · Photo Booth.app

## States
| State | Look |
|---|---|
| Empty query | Pill with placeholder. No card |
| Typing, matches | Card with rows. First row highlighted with the "Open" tag |
| Typing, no matches | No card. The pill stays as it is |
| Many matches | Card stops at 370 tall and scrolls inside |
| Tap row | Row shows the pressed fill, then Spotlight closes |
| Press "go" | Opens the top hit and Spotlight closes |

## Color summary
| Token | Value |
|---|---|
| Card fill | `#3A3837` @ 82% |
| Card border | `#FFFFFF` @ 14% |
| Top-hit row | `#FFFFFF` @ 12% |
| Pressed row | `#FFFFFF` @ 16% |
| Icon gradient | `#8E8E93` → `#636366` |
| Icon border | `#FFFFFF` @ 22% |
| Title | `#FFFFFF` |
| Tag fill | `#FFFFFF` @ 16% |
| Tag text | `#EBEBF5` @ 75% |
