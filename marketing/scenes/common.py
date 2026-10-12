"""Shared visuals for LazyRemote promo GIFs: black stage, MacBook left, iPhone right.

Scenes do `from common import *`. Add reusable pieces here, never inline in a scene.
Every iPhone helper mirrors a SwiftUI view (named in its comment) and is laid out in
iPhone points (393 x 852, origin top-left) through `phone.pt(x, y)`; colors are the
iOS dark-mode system colors. The Mac side is not defined by the app's code: it follows
the look of the original 13 GIFs (silver MacBook, purple wallpaper, dark app windows).
SF Symbols are the real glyphs, rendered by marketing/sfsymbol.swift.
"""
import hashlib
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import manimgx as m

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SYM_DIR = os.path.join(ROOT, ".build", "marketing", "symbols")
FONT = "Helvetica Neue"   # SF Pro is not loadable by the text engine; closest system face

# iOS dark-mode system colors (accent is the default systemBlue; the app sets no AccentColor).
ACCENT = "#0A84FF"
GREEN = "#30D158"
ORANGE = "#FF9F0A"
GRAY3 = "#48484A"
GRAY4 = "#3A3A3C"
GRAY5 = "#2C2C2E"
GRAY6 = "#1C1C1E"
SECONDARY = "#8E8E93"      # .secondary label on black
TERTIARY = "#5E5E63"       # .tertiary label / placeholder on systemGray5
WHITE = "#FFFFFF"

PH_W, PH_H = 393, 852      # iPhone points
S = 6.3 / PH_H             # scene units per iPhone point
PH_C = (4.85, -0.05)       # iPhone screen center
SAFE_TOP, SAFE_BOTTOM = 59, 34
KB_H = 291                 # iOS keyboard height incl. the globe / mic row
MAC_W, MAC_H = 1100, 715   # Mac screen in "looks-like" points
MS = 8.4 / MAC_W
MAC_C = (-2.05, 0.3)


def P(x, y):
    return np.array([x, y, 0.0])


def font_size(pt, scale=S):
    """m.Text font_size whose cap height matches `pt` points (cap = 0.7 em; 0.449 units at 48)."""
    return pt * scale * 0.7 * 48 / 0.449


def T(s, pt, color=WHITE, scale=S, bold=False, semibold=False):
    w = m.BOLD if bold else (m.SEMIBOLD if semibold else m.NORMAL)
    return m.Text(s, font=FONT, font_size=font_size(pt, scale), color=color, weight=w)


def emoji(ch, pt, scale=S):
    """Apple Color Emoji glyph (the text engine's fallback emoji is monochrome)."""
    from PIL import ImageDraw, ImageFont
    font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 160)
    im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=font, embedded_color=True)
    img = m.ImageMobject(np.array(im.crop(im.getbbox())))
    img.height = pt * 0.95 * scale
    return img


def rich_text(s, pt, color=WHITE, scale=S):
    """Text whose emoji are color images; a left-aligned Group, vertically centered."""
    parts, run = [], ""                       # (mobject, space before it)
    for ch in s + "\0":
        if ch == "\0" or ord(ch) >= 0x1F000:
            if run.strip():
                parts.append((T(run.strip(), pt, color, scale=scale), run[0] == " "))
            if ch != "\0":
                parts.append((emoji(ch, pt, scale), run.endswith(" ")))
            run = ""
        else:
            run += ch
    g, x = m.Group(), 0.0
    for part, spaced in parts:
        part.move_to(P(x + (0.28 * pt * scale if spaced and len(g) else 0), 0), aligned_edge=m.LEFT)
        x = part.get_right()[0]
        g.add(part)
    return g


def symbol(name, pt, color=WHITE, weight="regular", scale=S, at=None):
    """A real SF Symbol `pt` points tall-as-set, tinted `color` (cached PNG from sfsymbol.swift)."""
    path = os.path.join(SYM_DIR, f"{name}-{weight}.png")
    if not os.path.exists(path):
        os.makedirs(SYM_DIR, exist_ok=True)
        subprocess.run(["swift", os.path.join(ROOT, "marketing", "sfsymbol.swift"), name, weight, path], check=True)
    px = np.array(Image.open(path).convert("RGBA"))
    rgb = [int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    px[..., :3] = rgb
    img = m.ImageMobject(px)
    img.height = px.shape[0] / 4 * pt / 100 * scale    # rendered at 100 pt, 4x
    if at is not None:
        img.move_to(at)
    return img


def rrect(w, h, r, fill, opacity=1.0, stroke=None, stroke_width=0, stroke_opacity=1.0):
    return m.RoundedRectangle(corner_radius=min(r, w / 2, h / 2) if r else 0.0001, width=w, height=h,
                              fill_color=fill, fill_opacity=opacity, stroke_color=stroke or fill,
                              stroke_width=stroke_width, stroke_opacity=stroke_opacity if stroke else 0)


def circle(d, fill, opacity=1.0, at=None, stroke=None, stroke_width=0, stroke_opacity=1.0):
    c = m.Circle(radius=d / 2, fill_color=fill, fill_opacity=opacity, stroke_color=stroke or fill,
                 stroke_width=stroke_width, stroke_opacity=stroke_opacity if stroke else 0)
    return c.move_to(at) if at is not None else c


def stage(scene):
    """Black background plus the small LazyRemote mark (the only non-UI text)."""
    scene.camera.background_color = "#000000"
    mark = m.Text("LazyRemote", font=FONT, font_size=26, weight=m.BOLD, color=WHITE)
    scene.add(mark.move_to(P(-6.95, 3.62), aligned_edge=m.LEFT).set_z_index(60))


# ---------------------------------------------------------------- iPhone


class PhoneFrame(m.Group):
    """iPhone body with status bar; black screen = Color(.systemBackground) dark (RootView.swift)."""

    def __init__(self):
        w, h = PH_W * S, PH_H * S
        body = rrect(w + 0.2, h + 0.2, 0.5, "#000000", stroke="#5C5C60", stroke_width=3)
        screen = rrect(w, h, 0.42, "#000000")
        buttons = m.VGroup(rrect(0.05, 0.42, 0.02, "#3A3A3C").move_to(P(-w / 2 - 0.12, 1.3)),
                           rrect(0.05, 0.42, 0.02, "#3A3A3C").move_to(P(-w / 2 - 0.12, 0.75)),
                           rrect(0.05, 0.65, 0.02, "#3A3A3C").move_to(P(w / 2 + 0.12, 1.0)))
        super().__init__(buttons, body, screen)
        self.shift(P(*PH_C))
        self.buttons = buttons
        self.screen = screen
        self.add(self.status_bar())
        self.front = self.mask()

    def mask(self):
        """Rim and side buttons above MacFrame's cover (which hides everything outside both screens)."""
        w, h = PH_W * S, PH_H * S
        rim = rrect(w + 0.2, h + 0.2, 0.5, "#000000", 0, stroke="#5C5C60", stroke_width=3).move_to(P(*PH_C))
        return m.VGroup(self.buttons.copy(), rim).set_z_index(50)

    def pt(self, x, y):
        """Scene point for iPhone point (x, y), origin at the screen's top-left."""
        return P(PH_C[0] - PH_W * S / 2 + x * S, PH_C[1] + PH_H * S / 2 - y * S)

    def rect(self, x0, y0, x1, y1, r, fill, opacity=1.0, **kw):
        """Rounded rect from iPhone-point corners."""
        return rrect((x1 - x0) * S, (y1 - y0) * S, r * S, fill, opacity, **kw).move_to(
            self.pt((x0 + x1) / 2, (y0 + y1) / 2))

    def status_bar(self):
        island = self.rect(133, 11, 260, 48, 18.5, "#000000")
        time = T("10:01", 17, semibold=True).move_to(self.pt(64, 30))
        bars = m.VGroup(*[self.rect(300 + i * 5, 34 - 3 * (i + 1), 303 + i * 5, 34, 1, WHITE) for i in range(4)])
        g5 = T("5G", 12, semibold=True).move_to(self.pt(330, 30))
        batt = m.VGroup(self.rect(343, 24, 368, 36, 4, WHITE, 0, stroke=WHITE, stroke_width=1.2, stroke_opacity=0.5),
                        self.rect(345, 26, 360, 34, 2.5, GREEN))
        return m.Group(island, time, bars, g5, batt,
                       self.rect(130, PH_H - 13, 263, PH_H - 8, 2.5, WHITE))   # home indicator


HEADER_Y = SAFE_TOP + 14 + 16            # header row center (RootView.header padding 14 + 32 pt row)
HEADER_BOTTOM = SAFE_TOP + 14 + 32 + 14
MAGNIFIER_X, ELLIPSIS_X = 313, 357        # 32 pt buttons, 12 pt spacing, 20 pt trailing padding
DOCK = (MAGNIFIER_X - 16 - 12 - 16, HEADER_Y)   # FloatingRemoteButton dock = magnifier minX - 12 - 16
INPUT_H = 66                              # TextInputBar: 42 pt row + 12 pt vertical padding
IDLE_BAR_BOTTOM = PH_H - SAFE_BOTTOM
FLOAT_HOME = (PH_W - 41, SAFE_TOP + 0.66 * (PH_H - SAFE_TOP - SAFE_BOTTOM))  # default spot, snapped to edge inset 41


def header(phone, name="MacBook Air"):
    """RootView.header: StatusLabel (green dot + name, footnote secondary), Spotlight magnifier, ellipsis.circle."""
    dot = circle(8 * S, GREEN, at=phone.pt(24, HEADER_Y))
    label = T(name, 13, SECONDARY)
    label.move_to(phone.pt(36, HEADER_Y), aligned_edge=m.LEFT)   # HStack(spacing: 8) after the 8 pt dot
    g = m.Group(dot, label, magnifier(phone.pt(MAGNIFIER_X, HEADER_Y), 18, 1.7, 1.9, ACCENT),
                symbol("ellipsis.circle", 17, ACCENT, at=phone.pt(ELLIPSIS_X, HEADER_Y)))
    g.magnifier = phone.pt(MAGNIFIER_X, HEADER_Y)
    return g


def magnifier(at, size, ring, handle, color, opacity=1.0, scale=S):
    """SpotlightOverlay.swift `Magnifier`: ring (7.6, 7.6) r 5.9 + round-cap handle (12, 12)-(16.3, 16.3) in an 18-unit box."""
    u = size / 18 * scale
    c = P(*at[:2]) + P(-9 * u, 9 * u)            # box top-left
    ring_m = m.Circle(radius=5.9 * u, stroke_color=color, stroke_width=ring * u * 100, stroke_opacity=opacity,
                      fill_opacity=0).move_to(c + P(7.6 * u, -7.6 * u))
    line = m.Line(c + P(12 * u, -12 * u), c + P(16.3 * u, -16.3 * u), stroke_color=color,
                  stroke_width=handle * u * 100, stroke_opacity=opacity).set_cap_style(m.CapStyleType.ROUND)
    return m.VGroup(ring_m, line)


def trackpad(phone):
    """TrackpadView: systemGray5 surface, corner 28, 20 pt side / 14 pt bottom padding, caption2 tertiary hint."""
    top, bottom = HEADER_BOTTOM, IDLE_BAR_BOTTOM - INPUT_H - 14
    pad = phone.rect(20, top, PH_W - 20, bottom, 28, GRAY5)
    hint = T("Tap to click · Two fingers to scroll · Two-finger double-tap to right-click", 11, TERTIARY)
    if hint.width > (PH_W - 72) * S:
        hint.scale_to_fit_width((PH_W - 72) * S)
    hint.move_to(phone.pt(PH_W / 2, bottom - 16 - 7))
    g = m.VGroup(pad, hint)
    g.center_pt = (PH_W / 2, (top + bottom) / 2)
    return g


def input_bar(phone, focused=False, bottom=IDLE_BAR_BOTTOM, text="", can_send=False):
    """TextInputBar: systemGray5 field (corner 20), 42 pt delete.left / return circles, arrow.up send when focused."""
    y = bottom - INPUT_H / 2
    right = PH_W - 20
    send_x = right - 21 if focused else None
    enter_x = (send_x - 52) if focused else right - 21
    back_x = enter_x - 52
    field_right = back_x - 21 - 10
    field = phone.rect(20, y - 21, field_right, y + 21, 20, GRAY5)
    g = m.Group(field)
    g.field_left = phone.pt(36, y)
    if text:
        g.add(T(text, 17).move_to(g.field_left, aligned_edge=m.LEFT))
    else:
        g.add(T("Type to send…", 17, TERTIARY).move_to(g.field_left, aligned_edge=m.LEFT))
    g.backspace = circle(42 * S, GRAY5, at=phone.pt(back_x, y))
    g.enter = circle(42 * S, GRAY5, at=phone.pt(enter_x, y))
    g.add(g.backspace, symbol("delete.left", 17, WHITE, "semibold", at=phone.pt(back_x, y)),
          g.enter, symbol("return", 17, WHITE, "semibold", at=phone.pt(enter_x, y)))
    if focused:
        g.send = circle(42 * S, ACCENT if can_send else GRAY4, at=phone.pt(send_x, y))
        g.add(g.send, symbol("arrow.up", 18, WHITE, "bold", at=phone.pt(send_x, y)))
    return g


def typed_field(phone, text, bottom, caret=True):
    """Draft text in the focused TextInputBar field, with the accent caret after it."""
    y = bottom - INPUT_H / 2
    g = m.Group()
    x = phone.pt(36, y)
    if text:
        t = rich_text(text, 17).move_to(x, aligned_edge=m.LEFT)
        g.add(t)
        x = t.get_right() + P(0.045, 0)
    if caret:
        g.add(m.Rectangle(width=2 * S, height=22 * S, fill_color=ACCENT, fill_opacity=1, stroke_width=0).move_to(x))
    return g


def scrim(phone):
    """RootView.scrim: black 0.4 over the header and trackpad while typing."""
    return phone.rect(0, SAFE_TOP, PH_W, PH_H - SAFE_BOTTOM, 0, "#000000", 0.4)


def keyboard(phone, return_label="return"):
    """iOS system keyboard, dark (not app code; approximated). Keys by character in `.keys` (plus "return").
    A "go" return key is drawn blue, as iOS does for .submitLabel(.go)."""
    top = PH_H - KB_H
    g = m.Group(phone.rect(0, top, PH_W, PH_H - 60, 0, "#2B2B2D"), phone.rect(0, PH_H - 120, PH_W, PH_H, 56, "#2B2B2D"))
    g.keys = {}
    rows = ("qwertyuiop", "asdfghjkl", "zxcvbnm")
    kw, kh, pitch = 33.5, 42, 54
    for i, row in enumerate(rows):
        y = top + 8 + kh / 2 + i * pitch
        x0 = PH_W / 2 - (len(row) - 1) * (kw + 5.6) / 2
        for j, ch in enumerate(row):
            x = x0 + j * (kw + 5.6)
            g.keys[ch] = phone.rect(x - kw / 2, y - kh / 2, x + kw / 2, y + kh / 2, 5, "#6B6B6E")
            g.add(g.keys[ch], T(ch, 16).move_to(phone.pt(x, y + 1)))
    y = top + 8 + kh / 2 + 2 * pitch
    for x, sym in ((24, "shift"), (PH_W - 24, "delete.left")):
        g.add(phone.rect(x - 21, y - kh / 2, x + 21, y + kh / 2, 5, "#464649"), symbol(sym, 17, WHITE, at=phone.pt(x, y)))
    y += pitch
    g.add(phone.rect(3, y - kh / 2, 90, y + kh / 2, 5, "#464649"), T("123", 15).move_to(phone.pt(47, y)),
          phone.rect(96, y - kh / 2, 297, y + kh / 2, 5, "#6B6B6E"), T("space", 15).move_to(phone.pt(196, y)),
          (ret := phone.rect(303, y - kh / 2, PH_W - 3, y + kh / 2, 5, ACCENT if return_label == "go" else "#464649")),
          T(return_label, 15).move_to(phone.pt(347, y)),
          symbol("globe", 22, WHITE, at=phone.pt(36, PH_H - 52)), symbol("mic", 22, WHITE, at=phone.pt(PH_W - 36, PH_H - 52)))
    g.keys["return"] = ret
    return g


def remote_button(phone, at_pt=FLOAT_HOME, docked=False):
    """FloatingRemoteButton: 58 pt material circle with appletvremote.gen4 28 pt; docked = 22 pt accent glyph only."""
    c = phone.pt(*at_pt)
    if docked:
        return m.Group(symbol("appletvremote.gen4", 22, ACCENT, at=c))
    shadow = m.VGroup(*[circle((58 + 2 * k) * S, "#000000", 0.09, at=c + P(0, -8 * S)) for k in range(0, 24, 4)])
    disc = circle(58 * S, "#1E1E20", at=c, stroke=WHITE, stroke_width=0.8, stroke_opacity=0.18)
    return m.Group(shadow, disc, symbol("appletvremote.gen4", 28, WHITE, at=c))


def dock_target(phone, near=False):
    """FloatingRemoteButton.dockTarget: 36 pt dashed ring, accent + 18% fill when the button is near."""
    ring = m.Circle(radius=17.25 * S, stroke_color=ACCENT if near else SECONDARY,
                    stroke_opacity=1 if near else 0.6, stroke_width=1.6)
    g = m.VGroup(m.DashedVMobject(ring, num_dashes=15, dashed_ratio=4 / 7))
    if near:
        g.add(circle(36 * S, ACCENT, 0.18))
    return g.move_to(phone.pt(*DOCK))


# D-pad geometry (DPadOverlay.swift), in iPhone points.
PAD_C = (PH_W / 2, PH_H / 2 + 44)      # .offset(y: 44) on the full screen
PAD_R = 118


def _wedge(phone, deg):
    """DPadOverlay.Wedge: quarter of the 236 pt pad, neighbors 5 pt apart, clipped to the pad circle."""
    a = math.radians(deg)
    shift = 2.5 * math.sqrt(2)
    d = math.asin(2.5 / PAD_R)
    pts = [(PAD_C[0] + shift * math.cos(a), PAD_C[1] + shift * math.sin(a))]
    for k in range(25):
        t = a - math.pi / 4 + d + (math.pi / 2 - 2 * d) * k / 24
        pts.append((PAD_C[0] + PAD_R * math.cos(t), PAD_C[1] + PAD_R * math.sin(t)))
    return m.Polygon(*[phone.pt(*p) for p in pts], fill_color=GRAY4, fill_opacity=0.92, stroke_width=0)


def _capsule_keys(phone, cx, cy, seg_w, seg_h, n, vertical, symbols):
    """DPadOverlay.capsule: equal segments 5 pt apart, clipped to one capsule."""
    total_w = seg_w if vertical else n * seg_w + (n - 1) * 5
    total_h = n * seg_h + (n - 1) * 5 if vertical else seg_h
    cap = rrect(total_w * S, total_h * S, min(total_w, total_h) / 2 * S, GRAY4).move_to(phone.pt(cx, cy))
    keys, icons = [], []
    for i, sym in enumerate(symbols):
        if vertical:
            x, y = cx, cy - total_h / 2 + seg_h / 2 + i * (seg_h + 5)
        else:
            x, y = cx - total_w / 2 + seg_w / 2 + i * (seg_w + 5), cy
        box = m.Rectangle(width=seg_w * S, height=seg_h * S).move_to(phone.pt(x, y))
        k = m.Intersection(cap, box, fill_color=GRAY4, fill_opacity=0.92, stroke_width=0)
        keys.append(k)
        icons.append(symbol(sym, 20, WHITE, at=phone.pt(x, y)))
    return keys, icons


def dpad_overlay(phone):
    """DPadOverlay: dark material backdrop, 236 pt pad (wedges + Space), brightness / volume side capsules,
    media capsule below, xmark close. Keys: up/right/down/left/space/bright_up/bright_down/vol_up/vol_down/
    prev/playpause/next/close (each a fillable shape)."""
    backdrop = phone.rect(0, 0, PH_W, PH_H, 56, "#050507", 0.78)
    keys, icons = {}, []
    for name, deg, sym in (("up", -90, "chevron.up"), ("right", 0, "chevron.right"),
                           ("down", 90, "chevron.down"), ("left", 180, "chevron.left")):
        keys[name] = _wedge(phone, deg)
        a = math.radians(deg)
        icons.append(symbol(sym, 26, WHITE, "semibold",
                            at=phone.pt(PAD_C[0] + 80 * math.cos(a), PAD_C[1] + 80 * math.sin(a))))
    ring = circle(114 * S, "#0A0A0C", 0.85, at=phone.pt(*PAD_C))
    keys["space"] = circle(100 * S, GRAY3, at=phone.pt(*PAD_C))
    icons.append(symbol("space", 30, WHITE, "semibold", at=phone.pt(*PAD_C)))
    # HStack(alignment: .top, spacing: 6), side capsules 48 x 148 offset y -69.
    pad_top = PAD_C[1] - PAD_R
    side_cy = pad_top + 148 / 2 - 69
    for names, cx, syms in ((("bright_up", "bright_down"), PAD_C[0] - PAD_R - 6 - 24, ("sun.max", "sun.min")),
                            (("vol_up", "vol_down"), PAD_C[0] + PAD_R + 6 + 24, ("speaker.wave.3", "speaker.wave.1"))):
        ks, ic = _capsule_keys(phone, cx, side_cy, 48, 71.5, 2, True, syms)
        keys.update(zip(names, ks))
        icons += ic
    # Bottom-aligned overlay on the 236 pt row, offset y 60 + 56.
    ks, ic = _capsule_keys(phone, PAD_C[0], PAD_C[1] + PAD_R - 28 + 116, 70, 56, 3, False,
                           ("backward", "playpause", "forward"))
    keys.update(zip(("prev", "playpause", "next"), ks))
    icons += ic
    keys["close"] = circle(44 * S, GRAY4, 0.8, at=phone.pt(PH_W / 2, PH_H - 40 - 22))
    icons.append(symbol("xmark", 15, WHITE, "semibold", at=phone.pt(PH_W / 2, PH_H - 62)))
    order = [keys[k] for k in ("up", "right", "down", "left")] + [ring, keys["space"]] + \
            [keys[k] for k in ("bright_up", "bright_down", "vol_up", "vol_down", "prev", "playpause", "next", "close")]
    g = m.Group(backdrop, *order, *icons)
    g.keys = keys
    g.key_pt = lambda name: keys[name].get_center()
    return g


def press(key, on=True):
    """DPadKey / TextInputBar pressed state: fill turns accent (easeOut 0.12 s in the app)."""
    return key.animate.set_fill(ACCENT if on else key.rest_color, opacity=1 if on else key.rest_opacity)


def pressable(*keys):
    for k in keys:
        k.rest_color, k.rest_opacity = k.get_fill_color(), k.get_fill_opacity()


# ---------------------------------------------------------------- touch indicator, trail and ripple
# Demo overlays showing what the finger does; not app UI, so no Swift counterpart.


def finger(at, n=1, spread=0.42):
    """Gray fingertip circles (n side by side), as in the original GIFs."""
    dots = m.VGroup(*[m.Circle(radius=22 * S, fill_color="#B8B8BD", fill_opacity=0.55, stroke_color=WHITE,
                               stroke_width=2, stroke_opacity=0.8) for _ in range(n)])
    dots.arrange(m.RIGHT, buff=spread - 44 * S).move_to(at)
    return dots


def ripple(scene, at, life=0.4):
    """White ring rippling out of a touch point; runs on its own clock (dt updater), so it outlives short plays."""
    ring = m.Circle(radius=22 * S, stroke_color=WHITE, stroke_width=3.5, fill_opacity=0).move_to(at).set_z_index(5)
    base = ring.copy()
    age = [0.0]

    def grow(mob, dt):
        age[0] = min(age[0] + dt, life)
        k = age[0] / life
        mob.become(base.copy().scale(1 + 1.6 * (1 - (1 - k) ** 2)).set_stroke(opacity=0.95 * (1 - k)))
    ring.add_updater(grow)
    scene.add(ring)


def touch(scene, f):
    """Finger landing: ripples from each fingertip; returns the fade-in. Use as self.play(*touch(self, f), ...)."""
    for d in f:
        ripple(scene, d.get_center())
    return [m.FadeIn(f, scale=1.2)]


def trail(scene, f, linger=0.35):
    """Fading white trail behind each fingertip while it moves (call before animating the finger)."""
    paths = [m.TracedPath(d.get_center, dissipating_time=linger, stroke_color=WHITE, stroke_width=7,
                          stroke_opacity=0.45) for d in f]
    scene.add(*paths, f)          # trail under the finger
    return paths


def tap(scene, at, n=1, t=0.16):
    """Quick finger taps at `at` (each: appear slightly large, settle, lift, with a ripple ring)."""
    for _ in range(n):
        f = finger(at).scale(1.25)
        scene.add(f)
        ripple(scene, at)
        scene.play(f.animate.scale(0.8).set_opacity(0), run_time=t, rate_func=m.rush_from)
        scene.remove(f)


# ---------------------------------------------------------------- Mac (look of the original GIFs)


def _wallpaper(w=1100, h=715):
    yy, xx = np.mgrid[0:h, 0:w] / np.array([h, w])[:, None, None]
    img = np.zeros((h, w, 3)) + np.array([22, 10, 42])
    for (cx, cy, r, col) in ((0.22, 0.28, 0.35, (40, 60, 190)), (0.8, 0.2, 0.4, (120, 40, 170)),
                             (0.6, 0.85, 0.35, (170, 50, 110)), (0.05, 0.95, 0.25, (190, 100, 50))):
        g = np.exp(-((xx - cx) ** 2 + ((yy - cy) * h / w) ** 2) / (2 * (r * 0.5) ** 2))
        img += g[..., None] * np.array(col)
    return np.clip(img, 0, 255).astype(np.uint8)


def landscape(sky_top, sky_bottom, sun=(0.55, 0.42), seed=0, w=320, h=190):
    """Movie poster art (sky gradient, sun, mountain ridges), like the original GIFs' Cinema tiles."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 1, h)[:, None, None]
    img = (1 - t) * np.array(sky_top) + t * np.array(sky_bottom)
    img = np.repeat(img, w, axis=1)
    yy, xx = np.mgrid[0:h, 0:w]
    img[(xx - sun[0] * w) ** 2 + (yy - sun[1] * h) ** 2 < (0.11 * w) ** 2] = (255, 228, 180)
    for k, shade in enumerate((0.35, 0.2)):
        ph = rng.uniform(0, 6, 3)
        ridge = h * (0.62 + 0.12 * k) + sum(h * 0.06 * np.sin(xx[0] / w * (2 + 3 * i) * math.pi + ph[i]) for i in range(3))
        mask = yy > ridge[None, :]
        img[mask] = np.array(sky_bottom) * shade + np.array((10, 10, 20)) * (1 - shade)
    return img.astype(np.uint8)


class MacFrame(m.Group):
    """MacBook: silver rim, black bezel, notch, wallpaper, menu bar (app menus, LazyRemote item, clock)."""

    def __init__(self, app="Cinema", wallpaper=None):
        w, h = MAC_W * MS, MAC_H * MS
        rim = rrect(w + 0.26, h + 0.26, 0.2, "#0B0B0C", stroke="#C9C9CE", stroke_width=3).move_to(P(*MAC_C))
        wall = m.ImageMobject(_wallpaper() if wallpaper is None else wallpaper)
        wall.stretch_to_fit_width(w).stretch_to_fit_height(h).move_to(P(*MAC_C))
        base = m.Polygon(P(-w / 2 - 0.42, 0), P(w / 2 + 0.42, 0), P(w / 2 + 0.3, -0.13), P(-w / 2 - 0.3, -0.13),
                         fill_color="#C9C9CE", fill_opacity=1, stroke_width=0)
        base.shift(P(MAC_C[0], MAC_C[1] - h / 2 - 0.13))
        lip = rrect(1.2, 0.05, 0.02, "#9A9AA0").move_to(P(MAC_C[0], MAC_C[1] - h / 2 - 0.155))
        super().__init__(rim, wall)
        self.wall = wall
        self.bar = self.menu_bar(app)
        # Front layer: black cover over everything outside the Mac and iPhone screens, then the
        # Mac's bezel, rim, base and menu bar, so sliding desktops and the rising keyboard are
        # clipped to their screens. Scenes add `mac.front` (and `phone.front`).
        holes = m.Union(m.Rectangle(width=w, height=h).move_to(P(*MAC_C)),
                        rrect(PH_W * S, PH_H * S, 0.42, "#000000").move_to(P(*PH_C)))
        cover = m.Difference(m.Rectangle(width=14.4, height=8.2), holes,
                             fill_color="#000000", fill_opacity=1, stroke_width=0)
        bezel = m.Difference(rrect(w + 0.26, h + 0.26, 0.2, "#000000").move_to(P(*MAC_C)),
                             m.Rectangle(width=w, height=h).move_to(P(*MAC_C)),
                             fill_color="#0B0B0C", fill_opacity=1, stroke_width=0)
        edge = rrect(w + 0.26, h + 0.26, 0.2, "#000000", 0, stroke="#C9C9CE", stroke_width=3).move_to(P(*MAC_C))
        self.front = m.Group(cover, bezel, edge, base, lip, self.bar).set_z_index(40)

    def pt(self, x, y):
        """Scene point for Mac point (x, y), origin at the screen's top-left."""
        return P(MAC_C[0] - MAC_W * MS / 2 + x * MS, MAC_C[1] + MAC_H * MS / 2 - y * MS)

    def rect(self, x0, y0, x1, y1, r, fill, opacity=1.0, **kw):
        return rrect((x1 - x0) * MS, (y1 - y0) * MS, r * MS, fill, opacity, **kw).move_to(
            self.pt((x0 + x1) / 2, (y0 + y1) / 2))

    def text(self, s, pt, color=WHITE, **kw):
        return T(s, pt, color, scale=MS, **kw)

    def menu_bar(self, app):
        """macOS menu bar; the LazyRemote item is the app's RemoteIconFill (connected) template image."""
        g = m.Group(self.rect(0, 0, MAC_W, 24, 0, "#000000", 0.28))
        x = 18
        for i, s in enumerate((app, "File", "Edit", "View", "Window", "Help")):
            t = self.text(s, 12, bold=(i == 0)).move_to(self.pt(x, 12), aligned_edge=m.LEFT)
            g.add(t)
            x += t.width / MS + 18
        g.add(self.rect(MAC_W / 2 - 90, 0, MAC_W / 2 + 90, 26, 9, "#000000"))     # notch
        clock = self.text("Fri Oct 9  10:01", 12).move_to(self.pt(MAC_W - 16, 12), aligned_edge=m.RIGHT)
        icon = mac_icon("RemoteIconFill", 16, at=self.pt(MAC_W - 16 - clock.width / MS - 22, 12))
        g.add(clock, icon)
        return g


def mac_icon(name, pt, at):
    """The Mac app's menu-bar template image (macApp/Assets.xcassets/<name>.imageset), white."""
    path = os.path.join(SYM_DIR, f"{name}.png")
    if not os.path.exists(path):
        os.makedirs(SYM_DIR, exist_ok=True)
        svg = os.path.join(ROOT, "macApp", "Assets.xcassets", f"{name}.imageset", f"{name}.svg")
        subprocess.run(["swift", os.path.join(ROOT, "marketing", "sfsymbol.swift"), svg, "regular", path], check=True)
    img = m.ImageMobject(np.array(Image.open(path).convert("RGBA")))
    img.height = pt * MS
    return img.move_to(at)


def mac_window(mac, x0, y0, x1, y1, title=None, fill="#1E1E20"):
    """Dark macOS window with traffic lights (and centered title when given)."""
    g = m.Group(mac.rect(x0, y0, x1, y1, 12, fill, stroke="#4A4A4E", stroke_width=1))
    for i, col in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        g.add(circle(12 * MS, col, at=mac.pt(x0 + 20 + i * 20, y0 + 20)))
    if title:
        g.add(mac.text(title, 12, SECONDARY, semibold=True).move_to(mac.pt((x0 + x1) / 2, y0 + 20)))
    return g


MOVIES = [("Ocean Drift", (230, 110, 60), (90, 40, 90)), ("Night Train", (30, 70, 170), (15, 20, 60)),
          ("Red Desert", (230, 170, 60), (150, 60, 40)), ("Northern Lights", (40, 170, 140), (15, 40, 50)),
          ("Paper Cities", (200, 205, 220), (90, 95, 120)), ("The Long Run", (220, 60, 90), (90, 30, 60)),
          ("Violet Hour", (110, 70, 220), (40, 25, 90)), ("Golden Coast", (240, 160, 50), (120, 70, 40))]


def cinema_window(mac):
    """The original GIFs' 'Cinema' app: search field, 'Trending now', 2 x 4 movie grid. .tiles = tile groups."""
    x0, y0, x1, y1 = 60, 70, 1040, 680
    g = mac_window(mac, x0, y0, x1, y1)
    g.add(mac.rect(450, 48 + 30, 650, 48 + 54, 12, "#2E2E32"),
          symbol("magnifyingglass", 11, SECONDARY, scale=MS, at=mac.pt(466, 90)),
          mac.text("Search movies", 11, SECONDARY).move_to(mac.pt(478, 90), aligned_edge=m.LEFT),
          mac.text("Trending now", 17, bold=True).move_to(mac.pt(x0 + 40, 150), aligned_edge=m.LEFT))
    g.tiles = []
    tw, th = 205, 120
    for i, (name, top, bot) in enumerate(MOVIES):
        cx = x0 + 40 + tw / 2 + (i % 4) * (tw + 27)
        cy = 180 + th / 2 + (i // 4) * (th + 85)
        art = m.ImageMobject(landscape(top, bot, seed=i, sun=(0.3 + 0.12 * (i % 4), 0.35)))
        art.stretch_to_fit_width(tw * MS).stretch_to_fit_height(th * MS).move_to(mac.pt(cx, cy))
        label = mac.text(name, 11, "#D0D0D4").move_to(mac.pt(cx - tw / 2, cy + th / 2 + 16), aligned_edge=m.LEFT)
        tile = m.Group(art, label)
        tile.art = art
        g.tiles.append(tile)
        g.add(tile)
    return g


def select_ring(mac, tile):
    """Accent focus ring around a Cinema tile (clicked)."""
    a = tile.art
    return rrect(a.width + 8 * MS, a.height + 8 * MS, 8 * MS, ACCENT, 0, stroke=ACCENT, stroke_width=3).move_to(a)


def cursor(at, scale=1.0):
    """macOS arrow: black with a white outline, tip at `at`."""
    pts = [(0, 0), (0, -17), (4, -13), (7, -20), (10, -19), (7, -12), (12.5, -12)]
    arrow = m.Polygon(*[P(x, y) for x, y in pts], fill_color="#000000", fill_opacity=1,
                      stroke_color=WHITE, stroke_width=2.2)
    arrow.scale(MS * 1.35 * scale, about_point=P(0, 0)).shift(np.array(at) * np.array([1, 1, 0]))
    return arrow.set_z_index(45)   # above the menu bar layer


def context_menu(mac, items, at):
    """macOS dark context menu, top-left corner at `at`."""
    rows = m.VGroup(*[mac.text(s, 13) for s in items]).arrange(m.DOWN, aligned_edge=m.LEFT, buff=12 * MS)
    box = rrect(rows.width + 34 * MS, rows.height + 18 * MS, 8 * MS, "#2C2C30", 0.97, stroke="#55555A", stroke_width=1)
    box.move_to(rows)
    hl = rrect(box.width - 10 * MS, rows[0].height + 9 * MS, 5 * MS, ACCENT).move_to(P(box.get_center()[0], rows[0].get_center()[1]))
    g = m.VGroup(box, hl, rows)
    g.move_to(at, aligned_edge=m.UP + m.LEFT)
    return g


def mac_spotlight(mac, query="", results=()):
    """macOS Spotlight bar (+ result rows: (name, color)), as in the original GIFs."""
    x0, x1, y0 = 330, 770, 150
    g = m.Group(mac.rect(x0, y0, x1, y0 + 48, 14 if not results else 14, "#262629", 0.98, stroke="#5A5A5E", stroke_width=1),
                symbol("magnifyingglass", 18, SECONDARY, scale=MS, at=mac.pt(x0 + 26, y0 + 24)))
    g.add(mac.text(query or "Spotlight Search", 19, WHITE if query else SECONDARY)
          .move_to(mac.pt(x0 + 48, y0 + 24), aligned_edge=m.LEFT))
    if results:
        g.add(mac.rect(x0, y0 + 54, x1, y0 + 54 + 46 * len(results) + 8, 14, "#262629", 0.98, stroke="#5A5A5E", stroke_width=1))
        for i, (name, col) in enumerate(results):
            y = y0 + 54 + 4 + 23 + i * 46
            if i == 0:
                g.add(mac.rect(x0 + 6, y - 20, x1 - 6, y + 20, 9, ACCENT))
            g.add(mac.rect(x0 + 18, y - 14, x0 + 46, y + 14, 7, col), mac.text(name, 15).move_to(mac.pt(x0 + 58, y), aligned_edge=m.LEFT))
    return g


def scroll_view(tall, view_rows, tracker, width, at):
    """Image showing rows [o, o + view_rows) of the tall RGB array `tall`, o = tracker (fake clipping)."""
    rgba = np.concatenate([tall, np.full((*tall.shape[:2], 1), 255, np.uint8)], 2)
    img = m.ImageMobject(rgba[:view_rows]).stretch_to_fit_width(width)
    img.stretch_to_fit_height(width * view_rows / tall.shape[1]).move_to(at)

    def follow(mob):
        o = int(max(0, min(tracker.get_value(), tall.shape[0] - view_rows)))
        a = rgba[o:o + view_rows].copy()
        a.flags.writeable = False
        mob.paint = mob.paint.but(texture=a)
    img.add_updater(follow)
    return img


def blog_page(w=640, rows=2200):
    """Light web page: photo cards and gray text lines (the original scroll GIF's blog)."""
    img = np.full((rows, w, 3), 245, np.uint8)
    y, k = 30, 0
    while y < rows - 260:
        for i in range(4):
            if y + 14 < rows:
                img[y:y + 9, 60:w - 60 - (i % 3) * 70] = 190
            y += 22
        y += 20
        top, bot = MOVIES[k % len(MOVIES)][1:]
        art = landscape(top, bot, seed=k + 3, w=w - 120, h=210)
        img[y:y + 210, 60:w - 60] = art
        y += 250
        k += 1
    return img


def browser_window(mac, x0, y0, x1, y1, url="lazyremote.app/blog"):
    """Light browser window: toolbar with traffic lights and address field."""
    g = m.Group(mac.rect(x0, y0, x1, y1, 12, "#F5F5F7", stroke="#8A8A90", stroke_width=1),
                mac.rect(x0, y0, x1, y0 + 44, 12, "#E3E3E7"), mac.rect(x0, y0 + 30, x1, y0 + 44, 0, "#E3E3E7"))
    for i, col in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        g.add(circle(12 * MS, col, at=mac.pt(x0 + 20 + i * 20, y0 + 22)))
    cx = (x0 + x1) / 2
    g.add(mac.rect(cx - 150, y0 + 10, cx + 150, y0 + 34, 8, WHITE), mac.text(url, 11, "#555").move_to(mac.pt(cx, y0 + 22)))
    return g


def folder_icon(mac, name, at_pt):
    """macOS blue folder with its name under it."""
    x, y = at_pt
    g = m.Group(mac.rect(x - 34, y - 26, x - 6, y - 16, 4, "#5AB0F5"), mac.rect(x - 34, y - 20, x + 34, y + 24, 6, "#66BBFA"),
                mac.rect(x - 34, y - 12, x + 34, y + 24, 6, "#4FA7EF"))
    g.add(mac.text(name, 11).move_to(mac.pt(x, y + 40)))
    return g


def notes_window(mac):
    """Dark Notes window with a title and one line; .line(i) = left anchor of text line i."""
    x0, y0, x1, y1 = 250, 150, 850, 560
    g = mac_window(mac, x0, y0, x1, y1, "Notes")
    g.add(mac.text("Movie night", 19, bold=True).move_to(mac.pt(x0 + 40, y0 + 80), aligned_edge=m.LEFT),
          mac.text("Bring snacks for everyone", 14).move_to(mac.pt(x0 + 40, y0 + 118), aligned_edge=m.LEFT))
    g.line = lambda i: mac.pt(x0 + 40, y0 + 156 + 36 * i)
    return g


def mac_caret(mac, at):
    return m.Rectangle(width=2 * MS, height=20 * MS, fill_color=ACCENT, fill_opacity=1, stroke_width=0).move_to(at)


def video_player(mac, movie=1):
    """Cinema playback: full-window poster frame and a control bar. .progress(f, time) builds the
    played bar, knob and time label; .glyph(playing) the play/pause button glyph."""
    x0, y0, x1, y1 = 60, 70, 1040, 680
    g = m.Group(mac.rect(x0, y0, x1, y1, 12, "#000000", stroke="#4A4A4E", stroke_width=1))
    name, top, bot = MOVIES[movie]
    art = m.ImageMobject(landscape(top, bot, seed=movie, w=640, h=380, sun=(0.62, 0.38)))
    art.stretch_to_fit_width((x1 - x0 - 2) * MS).stretch_to_fit_height((y1 - y0 - 70) * MS)
    art.move_to(mac.pt((x0 + x1) / 2, y0 + 1 + (y1 - y0 - 70) / 2))
    g.add(art)
    g.add(*[circle(12 * MS, c, at=mac.pt(x0 + 20 + i * 20, y0 + 20)) for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840"))])
    ty = y1 - 35
    tx0, tx1 = x0 + 80, x1 - 160
    g.add(mac.rect(tx0, ty - 2.5, tx1, ty + 2.5, 2.5, "#5A5A5E"))

    def progress(f, time):
        x = tx0 + f * (tx1 - tx0)
        return m.Group(mac.rect(tx0, ty - 2.5, x, ty + 2.5, 2.5, WHITE), circle(14 * MS, WHITE, at=mac.pt(x, ty)),
                       mac.text(f"{time} / 1:48:20", 11, "#D0D0D4").move_to(mac.pt(tx1 + 18, ty), aligned_edge=m.LEFT))
    g.progress = progress
    g.glyph = lambda playing: symbol("pause.fill" if playing else "play.fill", 16, WHITE, scale=MS, at=mac.pt(x0 + 40, ty))
    g.center = mac.pt((x0 + x1) / 2, y0 + (y1 - y0 - 70) / 2)
    return g


def remote_screen(phone, docked=False):
    """RootView idle: header, trackpad, TextInputBar and the FloatingRemoteButton. Parts as attributes."""
    g = m.Group()
    g.header, g.pad, g.bar = header(phone), trackpad(phone), input_bar(phone)
    g.button = remote_button(phone, DOCK if docked else FLOAT_HOME, docked)
    g.add(g.header, g.pad, g.bar, g.button)
    return g


def open_keyboard(scene, phone, screen, run_time=0.3):
    """Focus the TextInputBar: scrim fades in, bar rises with the keyboard, send button appears, remote button hides.
    Returns (keyboard, focused bar)."""
    kb = keyboard(phone)
    bottom = PH_H - KB_H
    bar = input_bar(phone, True, bottom)
    kb.shift(P(0, -KB_H * S))
    bar.shift(P(0, (bottom - IDLE_BAR_BOTTOM) * S))          # starts where the idle bar is
    sc = scrim(phone).set_opacity(0)
    scene.remove(screen.button)                              # RootView drops it while typing, unanimated
    scene.add(sc, kb, bar)                                   # scrim below the rising bar and keyboard
    scene.play(sc.animate.set_fill(opacity=0.4), m.FadeOut(screen.bar),
               kb.animate.shift(P(0, KB_H * S)), bar.animate.shift(P(0, (IDLE_BAR_BOTTOM - bottom) * S)),
               run_time=run_time, rate_func=m.ease_out_cubic)
    scene.remove(screen.bar)
    kb.scrim = sc
    return kb, bar


def close_keyboard(scene, phone, screen, kb, bar, run_time=0.3):
    """Unfocus: keyboard and bar slide down, scrim fades, idle bar and remote button return."""
    scene.play(kb.animate.shift(P(0, -KB_H * S)), bar.animate.shift(P(0, (PH_H - KB_H - IDLE_BAR_BOTTOM) * S)).set_opacity(0),
               m.FadeOut(kb.scrim), m.FadeIn(screen.bar),
               run_time=run_time, rate_func=m.ease_in_out_cubic)
    scene.remove(kb, bar, kb.scrim)
    scene.add(screen.button)


# ---------------------------------------------------------------- Spotlight overlay (iOSApp/Views/SpotlightOverlay.swift)

PILL = (14, 70, PH_W - 14, 126)            # design.md: top 70, insets 14, height 56
PILL_TEXT_X = 14 + 20 + 22 + 12            # padding 20, 22 pt icon, 12 gap
SPOT_GRAY = "#EBEBF5"


def _png(px, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(px).save(path)


def blurred_screen(phone, radius=14):
    """RootView with Spotlight open: header, trackpad and input bar under .blur(radius: 14), floating button hidden.
    ManimGX has no blur, so that screen is rendered once by a tiny scene, Gaussian-blurred with PIL and cached
    (keyed on this file). Black is made transparent so the status bar stays visible through the bleed."""
    out = os.path.join(ROOT, ".build", "marketing")
    key = hashlib.sha1(open(__file__, "rb").read()).hexdigest()[:10]
    path = os.path.join(out, f"blurred-screen-{key}-{radius}.png")
    if not os.path.exists(path):
        os.makedirs(out, exist_ok=True)
        src, mp4, frame = (os.path.join(out, n) for n in ("snap_scene.py", "snap.mp4", "snap.png"))
        with open(src, "w") as f:
            f.write(f"import sys\nsys.path.insert(0, {HERE!r})\nfrom common import *\n\n\n"
                    "class Snap(m.Scene):\n    def construct(self):\n        self.camera.background_color = '#000000'\n"
                    "        s = remote_screen(PhoneFrame())\n        self.add(s.header, s.pad, s.bar)\n        self.wait(1)\n")
        mg = os.path.join(os.path.dirname(sys.executable), "manimgx")
        subprocess.run([mg, "render", src, "Snap", "-r", "1920x1080", "--fps", "1", "-o", mp4], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-frames:v", "1", frame], check=True)
        k = 1080 / 8                                                   # px per scene unit at 1080p
        x0, y0 = phone.pt(0, 0)[:2]
        box = (round(960 + x0 * k), round(540 - y0 * k), round(960 + (x0 + PH_W * S) * k), round(540 - (y0 - PH_H * S) * k))
        img = Image.open(frame).convert("RGB").filter(ImageFilter.GaussianBlur(radius * S * k)).crop(box)
        rgb = np.asarray(img).astype(float)
        a = rgb.max(axis=2, keepdims=True)                             # un-premultiply over black
        px = np.concatenate([np.where(a > 0, rgb * 255 / np.maximum(a, 1), 0), a], axis=2)
        _png(np.clip(px, 0, 255).astype(np.uint8), path)
    img = m.ImageMobject(path)
    return img.stretch_to_fit_width(PH_W * S).stretch_to_fit_height(PH_H * S).move_to(P(*PH_C))


def spotlight_scrim(phone):
    """SpotlightOverlay scrim: black 45%, full screen (the status bar stays on top, as iOS draws it)."""
    return phone.rect(0, 0, PH_W, PH_H, 0, "#000000", 0.45)


def _pill_shadow(phone):
    """Pill shadow: y 10, blur 30, black 40% (`.shadow(radius: 15, y: 10)`), as a blurred PNG."""
    path = os.path.join(ROOT, ".build", "marketing", "spotlight-pill-shadow.png")
    x0, y0, x1, y1 = PILL
    pad, k = 60, 4                                                     # pt margin, px per pt
    if not os.path.exists(path):
        im = Image.new("L", ((x1 - x0 + 2 * pad) * k, (y1 - y0 + 2 * pad) * k), 0)
        ImageDraw.Draw(im).rounded_rectangle((pad * k, pad * k, (x1 - x0 + pad) * k, (y1 - y0 + pad) * k), 28 * k, fill=255)
        a = np.asarray(im.filter(ImageFilter.GaussianBlur(15 * k))).astype(float) * 0.4
        px = np.zeros(a.shape + (4,), np.uint8)
        px[..., 3] = a.astype(np.uint8)
        _png(px, path)
    img = m.ImageMobject(path)
    img.stretch_to_fit_width((x1 - x0 + 2 * pad) * S).stretch_to_fit_height((y1 - y0 + 2 * pad) * S)
    return img.move_to(phone.pt((x0 + x1) / 2, (y0 + y1) / 2 + 10))


def spotlight_pill(phone, text=""):
    """SpotlightOverlay pill: capsule #4A4644 82% (the .ultraThinMaterial under it is not drawn), 0.5 pt white 18%
    border, shadow; 22 pt magnifier #EBEBF5 60%; 22 pt white text or the "Spotlight Search" placeholder at 55%."""
    x0, y0, x1, y1 = PILL
    y = (y0 + y1) / 2
    g = m.Group(_pill_shadow(phone),
                phone.rect(x0, y0, x1, y1, 28, "#4A4644", 0.82, stroke=WHITE, stroke_width=0.5 * S * 100, stroke_opacity=0.18),
                magnifier(phone.pt(x0 + 20 + 11, y), 22, 1.6, 1.8, SPOT_GRAY, 0.6))
    left = phone.pt(PILL_TEXT_X, y)
    if text:
        t = T(text, 22).move_to(left, aligned_edge=m.LEFT)
        g.add(t)
        left = t.get_right() + P(0.03, 0)
    else:
        g.add(T("Spotlight Search", 22, SPOT_GRAY).set_opacity(0.55).move_to(left, aligned_edge=m.LEFT))
    g.add(m.Rectangle(width=2 * S, height=26 * S, fill_color=WHITE, fill_opacity=1, stroke_width=0).move_to(left))
    return g
