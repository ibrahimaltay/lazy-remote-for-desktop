# Spotlight Search: Design Specs

Reference: `Spotlight Search.html`. Frame 1 is closed, frame 2 is open.
Units are pt on a 393×852 screen (iPhone 15/16 Pro), dark appearance.

## Closed state

### Spotlight button (header)
| Property | Value |
|---|---|
| Hit area | 32×32 |
| Icon | Magnifier, 18×18 |
| Icon shape | Circle (center 7.6, 7.6; radius 5.9; stroke 1.7) + handle line from (12, 12) to (16.3, 16.3), stroke 1.9, round cap |
| Icon color | `#0A84FF` |
| Disabled (not connected) | 50% opacity |
| Position | Header row, between the status label and the options button. 12pt spacing between items. Row padding: 20 left/right, 14 top/bottom |

## Open state

### Layers (bottom → top)
1. Existing screen. Visible and blurred.
2. Scrim
3. Search pill
4. Keyboard

The floating remote button is hidden while Spotlight is open.

### Scrim
| Property | Value |
|---|---|
| Size | Full screen, edge to edge |
| Color | `#000000` at 45% opacity |
| Background blur | 14 |

### Search pill
| Property | Value |
|---|---|
| Top | 70 from the screen top |
| Left / right inset | 14 |
| Width | 365 |
| Height | 56 |
| Shape | Capsule, corner radius 28 |
| Fill | `#4A4644` (rgb 74, 70, 68) at 82% opacity |
| Background blur | 30 |
| Border | 0.5 inner stroke, `#FFFFFF` at 18% opacity |
| Shadow | x 0, y 10, blur 30, `#000000` at 40% opacity |
| Padding | 20 left/right |
| Icon to text gap | 12 |

### Pill icon
| Property | Value |
|---|---|
| Size | 22×22 |
| Shape | Same magnifier as the header (circle stroke 1.6, handle stroke 1.8, round cap) |
| Color | `#EBEBF5` at 60% opacity |
| Vertical alignment | Centered in the pill |

### Pill text
| Property | Value |
|---|---|
| Font | SF Pro, Regular |
| Size / line height | 22 / 28 |
| Text color | `#FFFFFF` |
| Placeholder | "Spotlight Search" |
| Placeholder color | `#EBEBF5` at 55% opacity |
| Caret | `#FFFFFF` |
| Lines | Single line |

### Keyboard
| Property | Value |
|---|---|
| Type | System keyboard, dark |
| Height (this device) | 336 |
| Return key label | "go" |

## Color summary
| Token | Value |
|---|---|
| Accent (header icon) | `#0A84FF` |
| Scrim | `#000000` @ 45% |
| Pill fill | `#4A4644` @ 82% |
| Pill border | `#FFFFFF` @ 18% |
| Pill shadow | `#000000` @ 40% |
| Pill icon | `#EBEBF5` @ 60% |
| Text | `#FFFFFF` |
| Placeholder | `#EBEBF5` @ 55% |

## Blur / shadow summary
| Element | Value |
|---|---|
| Scrim background blur | 14 |
| Pill background blur | 30 |
| Pill shadow | 0 / 10 / 30 |

## States
| State | Look |
|---|---|
| Closed | Normal remote screen. Header magnifier in `#0A84FF` |
| Open, empty | Scrim + pill with placeholder + keyboard. Floating remote button hidden |
| Open, typing | Same, with the query in white |
| Close | Tap the dimmed area or press "go". The screen goes back to closed |
