"""LazyRemote (github.com/ibrahimaltay/macbook-remote) marketing animation.

An iPhone running LazyRemote drives a MacBook: a swipe on the trackpad moves the cursor,
text typed on the phone lands in a search field, and the floating remote button opens a
D-pad overlay whose play/pause sends Space and whose arrows send arrow keys to a movie player.

The phone UI is traced from docs/screenshots/remote.png: `P(px, py)` maps a pixel of that
923x2000 screenshot onto the phone screen in the scene.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import manimgx as m

FONT = "Helvetica Neue"
BG = "#060609"
ACCENT = "#0A84FF"          # iOS dark-mode system blue (Color.accentColor)
GRAY5 = "#2C2C2E"           # systemGray5, dark
GRAY4 = "#3A3A3C"           # systemGray4, dark
SECONDARY = "#9A9AA0"
GREEN = "#30D158"
ORANGE = "#FF9F0A"

# --------------------------------------------------------------------------- text
_REF = {}


def T(s, size, color="#FFFFFF", weight=m.NORMAL):
    """Text whose capital letters are `size` units tall."""
    if weight not in _REF:
        _REF[weight] = m.Text("H", font=FONT, weight=weight).height
    t = m.Text(s, font=FONT, weight=weight, color=color)
    t.scale(size / _REF[weight])
    return t


def at_left(mob, point):
    return mob.move_to(point, aligned_edge=m.LEFT)


def rrect(w, h, r, color, opacity=1.0, **kw):
    return m.RoundedRectangle(width=w, height=h, corner_radius=r, fill_color=color,
                              fill_opacity=opacity, stroke_width=0, **kw)


class Outline(m.VMobject):
    """A stroke-only path: fades and set_opacity never give it a fill."""

    def set_fill(self, color=None, opacity=None, family=True, **kw):
        return super().set_fill(color, opacity=0, family=family)

    def set_opacity(self, opacity, family=True):
        return self.set_stroke(opacity=opacity, family=family)


def poly(points, color="#FFFFFF", width=3.0, closed=False, fill=None):
    v = m.VMobject() if fill else Outline()
    pts = [np.array([*p[:2], 0.0]) for p in points]
    if closed:
        pts.append(pts[0])
    v.set_points_as_corners(pts)
    v.set_stroke(color, width=width)
    v.joint_type = m.LineJointType.ROUND
    if fill:
        v.set_fill(fill, opacity=1)
    return v


# --------------------------------------------------------------------------- pictures
def _img(arr):
    return m.ImageMobject(np.asarray(arr))


def wallpaper(w=1500, h=940):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = xx / w, yy / h
    img = np.array([0.04, 0.05, 0.16]) * (1 - v)[..., None] + np.array([0.09, 0.03, 0.14]) * v[..., None]
    for cx, cy, r, col in [(0.2, 0.3, 0.45, (0.15, 0.3, 0.9)), (0.8, 0.2, 0.4, (0.6, 0.2, 0.8)),
                           (0.6, 0.85, 0.5, (0.9, 0.3, 0.4)), (0.05, 0.95, 0.3, (1.0, 0.55, 0.2))]:
        d2 = ((u - cx) * w / h) ** 2 + (v - cy) ** 2
        img = img + np.exp(-d2 / (r * r * 0.55))[..., None] * np.array(col) * 0.6
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def nebula(w=1500, h=940, seed=3):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u, v = xx / w, yy / h
    img = np.zeros((h, w, 3), np.float32) + np.array([0.01, 0.01, 0.03])
    for cx, cy, r, col in [(0.3, 0.45, 0.35, (0.35, 0.1, 0.6)), (0.55, 0.6, 0.3, (0.1, 0.35, 0.7)),
                           (0.15, 0.7, 0.25, (0.7, 0.2, 0.45)), (0.7, 0.3, 0.2, (0.15, 0.2, 0.5))]:
        d2 = ((u - cx) * w / h) ** 2 + (v - cy) ** 2
        img += np.exp(-d2 / (r * r * 0.5))[..., None] * np.array(col) * 0.55
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    for _ in range(260):       # fixed faint background stars
        x, y, b = rng.uniform(0, w), rng.uniform(0, h), int(rng.uniform(90, 200))
        dr.point((x, y), fill=(b, b, b))
    return np.array(im.filter(ImageFilter.GaussianBlur(0.6)))


def planet(px=520):
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:px, 0:px].astype(np.float32)
    c = px / 2
    r = px * 0.3
    d = np.sqrt((xx - c) ** 2 + (yy - c) ** 2)
    nx, ny = (xx - c) / r, (yy - c) / r
    lit = np.clip(-0.55 * nx - 0.65 * ny + 0.5 * np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1)), 0, 1)
    band = 0.5 + 0.5 * np.sin(ny * 9 + nx * 1.5)
    col = np.stack([0.95 * lit * (0.75 + 0.25 * band), 0.6 * lit * (0.7 + 0.3 * band), 0.4 * lit], -1)
    a = np.clip((r - d) * 1.5, 0, 1)
    glow = np.exp(-np.clip(d - r, 0, None) / (px * 0.035)) * 0.35 * (d > r)
    rgb = np.where(a[..., None] > 0, col, np.array([1.0, 0.6, 0.35]))
    alpha = np.maximum(a, glow)
    arr = np.dstack([np.clip(rgb, 0, 1) * 255, alpha * 255]).astype(np.uint8)
    return arr


def poster(seed, w=480, h=300):
    rng = np.random.default_rng(seed)
    hues = [((0.95, 0.45, 0.25), (0.25, 0.1, 0.35)), ((0.1, 0.4, 0.8), (0.02, 0.05, 0.2)),
            ((0.9, 0.75, 0.3), (0.6, 0.15, 0.1)), ((0.2, 0.8, 0.6), (0.05, 0.1, 0.25)),
            ((0.85, 0.85, 0.9), (0.3, 0.35, 0.5)), ((0.95, 0.3, 0.4), (0.15, 0.05, 0.15)),
            ((0.4, 0.3, 0.9), (0.05, 0.02, 0.15)), ((0.95, 0.6, 0.2), (0.1, 0.2, 0.3))]
    top, bot = hues[seed % len(hues)]
    v = np.linspace(0, 1, h)[:, None, None]
    img = np.array(top) * (1 - v) + np.array(bot) * v
    img = np.repeat(img, w, axis=1)
    im = Image.fromarray((img * 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    sx, sy, sr = rng.uniform(0.2, 0.8) * w, rng.uniform(0.25, 0.45) * h, rng.uniform(25, 45)
    dr.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 235, 200))
    for layer in range(3):                      # mountain / skyline silhouettes
        base = h * (0.62 + 0.12 * layer)
        pts = [(0, h)]
        for x in np.linspace(0, w, 9):
            pts.append((x, base - rng.uniform(10, 60)))
        pts.append((w, h))
        k = 0.55 - 0.18 * layer
        dr.polygon(pts, fill=tuple(int(c * 255 * k) for c in bot))
    return np.array(im)


# --------------------------------------------------------------------------- layout
MX, MY = -2.45, 0.6          # MacBook display centre
DW, DH = 7.5, 4.7            # display size
DL, DR = MX - DW / 2, MX + DW / 2
DB, DT = MY - DH / 2, MY + DH / 2

PX, PY = 4.85, 0.0           # iPhone screen centre
PS = 3.0 / 923               # scene units per screenshot pixel


def P(px, py):
    return np.array([PX + (px - 461.5) * PS, PY + (1000 - py) * PS, 0.0])


def pbox(x0, y0, x1, y1, r, color, opacity=1.0):
    b = rrect((x1 - x0) * PS, (y1 - y0) * PS, min(r, (y1 - y0) / 2, (x1 - x0) / 2) * PS, color, opacity)
    return b.move_to(P((x0 + x1) / 2, (y0 + y1) / 2))


def ppoly(points, color="#FFFFFF", width=3.0, closed=False, fill=None):
    # widths are in screenshot terms; manimgx strokes render ~2.6x wider at this scale
    return poly([P(x, y) for x, y in points], color, width * 0.4, closed, fill)


def chevron(cx, cy, d, size=24, width=4.2):
    pts = {"r": [(cx - size / 2, cy - size), (cx + size / 2, cy), (cx - size / 2, cy + size)],
           "l": [(cx + size / 2, cy - size), (cx - size / 2, cy), (cx + size / 2, cy + size)],
           "u": [(cx - size, cy + size / 2), (cx, cy - size / 2), (cx + size, cy + size / 2)],
           "d": [(cx - size, cy - size / 2), (cx, cy + size / 2), (cx + size, cy - size / 2)]}[d]
    return ppoly(pts, width=width)


def playpause_icon(cx, cy):
    tri = ppoly([(cx - 46, cy - 24), (cx - 46, cy + 24), (cx - 6, cy)], width=2, closed=True, fill="#FFFFFF")
    tri.set_stroke("#FFFFFF", width=2.5)
    b1 = pbox(cx + 6, cy - 24, cx + 20, cy + 24, 3, "#FFFFFF")
    b2 = pbox(cx + 32, cy - 24, cx + 46, cy + 24, 3, "#FFFFFF")
    return m.VGroup(tri, b1, b2)


def delete_icon(cx, cy):
    shape = ppoly([(cx - 24, cy), (cx - 10, cy - 17), (cx + 22, cy - 17), (cx + 22, cy + 17), (cx - 10, cy + 17)],
                  width=2.6, closed=True)
    x1 = ppoly([(cx - 2, cy - 7), (cx + 12, cy + 7)], width=2.6)
    x2 = ppoly([(cx - 2, cy + 7), (cx + 12, cy - 7)], width=2.6)
    return m.VGroup(shape, x1, x2)


def return_icon(cx, cy):
    line = ppoly([(cx + 20, cy - 16), (cx + 20, cy + 5), (cx - 20, cy + 5)], width=2.8)
    head = ppoly([(cx - 9, cy - 6), (cx - 20, cy + 5), (cx - 9, cy + 16)], width=2.8)
    return m.VGroup(line, head)


def arrow_up_icon(cx, cy):
    return m.VGroup(ppoly([(cx, cy + 16), (cx, cy - 16)], width=3.4),
                    ppoly([(cx - 13, cy - 3), (cx, cy - 16), (cx + 13, cy - 3)], width=3.4))


def mac_cursor(scale=1.0):
    pts = [(0, 0), (0, -0.25), (0.06, -0.195), (0.1, -0.285), (0.135, -0.27), (0.096, -0.18), (0.175, -0.18)]
    c = poly([(x * scale, y * scale) for x, y in pts], "#FFFFFF", 1.6, closed=True, fill="#000000")
    c.set_z_index(6)
    return c


def tip_of(cursor):
    return cursor.get_corner(m.UL)


def touch_dot():
    d = m.Circle(radius=0.15, fill_color="#FFFFFF", fill_opacity=0.45, stroke_color="#FFFFFF",
                 stroke_width=2.5, stroke_opacity=0.95)
    d.set_z_index(8)
    return d


def fmt(sec):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


# --------------------------------------------------------------------------- scene
class LazyRemotePromo(m.Scene):
    def construct(self):
        self.camera.background_color = BG
        self.build_mac()
        self.build_phone()
        self.intro()
        self.connect()
        self.swipe_and_click()
        self.type_and_send()
        self.open_movie()
        self.play_pause_and_arrows()
        self.outro()

    # ------------------------------------------------------------------ building
    def build_mac(self):
        lid = rrect(DW + 0.3, DH + 0.3, 0.24, "#0B0B0D")
        lid.set_stroke("#A9ACB2", width=2.4).move_to([MX, MY, 0])
        wall = _img(wallpaper()).stretch_to_fit_width(DW).stretch_to_fit_height(DH).move_to([MX, MY, 0])
        menubar = m.Rectangle(width=DW, height=0.17, fill_color="#000000", fill_opacity=0.35, stroke_width=0)
        menubar.move_to([MX, DT - 0.085, 0])
        items = m.VGroup()
        x = DL + 0.18
        for i, label in enumerate(["Cinema", "File", "Edit", "View", "Window", "Help"]):
            t = at_left(T(label, 0.055, weight=m.BOLD if i == 0 else m.NORMAL), [x, DT - 0.085, 0])
            items.add(t)
            x += t.width + 0.17
        clock = T("Fri Oct 9  10:01", 0.055)
        clock.move_to([DR - 0.18, DT - 0.085, 0], aligned_edge=m.RIGHT)
        # LazyRemote's menu bar icon: a tiny remote
        remote = m.VGroup(rrect(0.07, 0.11, 0.02, "#FFFFFF"), m.Circle(radius=0.016, fill_color="#000000",
                          fill_opacity=1, stroke_width=0).shift(m.UP * 0.02))
        remote.next_to(clock, m.LEFT, buff=0.16)
        notch = rrect(0.7, 0.16, 0.06, "#0B0B0D").move_to([MX, DT - 0.05, 0])
        base = m.Polygon([MX - DW / 2 - 0.55, DB - 0.15, 0], [MX + DW / 2 + 0.55, DB - 0.15, 0],
                         [MX + DW / 2 + 0.4, DB - 0.33, 0], [MX - DW / 2 - 0.4, DB - 0.33, 0],
                         fill_color="#C9CBD0", fill_opacity=1, stroke_width=0)
        base.set_sheen_direction(m.DOWN).set_fill(["#E2E4E8", "#8D9096"])
        lip = rrect(1.2, 0.07, 0.03, "#8E9095").move_to([MX, DB - 0.18, 0])
        shadow = m.Ellipse(width=DW + 1.4, height=0.25, fill_color="#000000", fill_opacity=0.6,
                           stroke_width=0).move_to([MX, DB - 0.38, 0])

        # the Cinema app window
        win_w, win_h = 6.9, 4.05
        wy = MY - 0.1
        win = rrect(win_w, win_h, 0.12, "#1B1B1E").set_stroke("#3A3A3F", width=1.2).move_to([MX, wy, 0])
        wt = wy + win_h / 2
        lights = m.VGroup(*[m.Circle(radius=0.045, fill_color=c, fill_opacity=1, stroke_width=0)
                            .move_to([MX - win_w / 2 + 0.2 + i * 0.15, wt - 0.21, 0])
                            for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"])])
        divider = m.Line([MX - win_w / 2, wt - 0.42, 0], [MX + win_w / 2, wt - 0.42, 0],
                         stroke_color="#2E2E33", stroke_width=1.2)
        self.search = rrect(2.4, 0.25, 0.125, "#2C2C31").move_to([MX, wt - 0.21, 0])
        sl = self.search.get_left()
        lens = m.VGroup(m.Circle(radius=0.035, stroke_color="#8E8E93", stroke_width=1.6),
                        m.Line([0.025, -0.025, 0], [0.065, -0.065, 0], stroke_color="#8E8E93", stroke_width=1.6))
        lens.move_to(sl + m.RIGHT * 0.16)
        self.search_ph = at_left(T("Search movies", 0.058, "#7C7C82"), sl + m.RIGHT * 0.27)
        self.search_ring = rrect(2.46, 0.31, 0.155, "#000000", 0).set_stroke(ACCENT, width=2.6, opacity=0)
        self.search_ring.move_to(self.search)

        grid_top = wt - 0.42 - 0.22
        self.heading = at_left(T("Trending now", 0.095, weight=m.BOLD), [MX - win_w / 2 + 0.28, grid_top - 0.05, 0])
        names = ["Ocean Drift", "Night Train", "Red Desert", "Northern Lights",
                 "Paper Cities", "The Long Run", "Violet Hour", "Golden Coast"]
        pw, ph, gap = 1.5, 0.94, 0.14
        self.grid = m.Group()
        for i, name in enumerate(names):
            r, c = divmod(i, 4)
            cx = MX - 1.5 * (pw + gap) + c * (pw + gap)
            cy = grid_top - 0.32 - ph / 2 - r * (ph + 0.42)
            img = _img(poster(i)).stretch_to_fit_width(pw).stretch_to_fit_height(ph).move_to([cx, cy, 0])
            cap = at_left(T(name, 0.068, "#D8D8DC"), [cx - pw / 2, cy - ph / 2 - 0.12, 0])
            self.grid.add(m.Group(img, cap))
        self.grid_geo = (pw, ph, gap, grid_top)

        self.cursor = mac_cursor()
        self.cursor.shift(np.array([MX + 2.2, MY - 1.3, 0]) - tip_of(self.cursor))
        self.mac = m.Group(shadow, base, lip, lid, wall, menubar, items, clock, remote, notch)
        self.app = m.Group(win, lights, divider, self.search, lens, self.search_ph, self.search_ring,
                           self.heading, self.grid)

    def build_phone(self):
        body = rrect(3.0 + 0.24, 2000 * PS + 0.24, 0.5, "#1A1A1C").move_to([PX, PY, 0])
        body.set_stroke("#6B6A70", width=3)
        buttons = m.VGroup(rrect(0.05, 0.45, 0.02, "#55555A").move_to([PX - 1.645, PY + 1.6, 0]),
                           rrect(0.05, 0.45, 0.02, "#55555A").move_to([PX - 1.645, PY + 1.0, 0]),
                           rrect(0.05, 0.7, 0.02, "#55555A").move_to([PX + 1.645, PY + 1.3, 0]))
        screen = rrect(3.0, 2000 * PS, 0.42, "#000000").move_to([PX, PY, 0])
        island = pbox(330, 34, 593, 104, 40, "#101012")

        status = m.VGroup(T("10:01", 30 * PS, weight=m.BOLD).move_to(P(167, 68)))
        bars = m.VGroup(*[pbox(662 + i * 13, 74 - 8 * i, 671 + i * 13, 84, 2, "#FFFFFF") for i in range(4)])
        g5 = T("5G", 26 * PS).move_to(P(743, 70))
        batt = m.VGroup(pbox(782, 54, 840, 84, 9, "#3A3A3C"), pbox(782, 54, 812, 84, 9, GREEN),
                        pbox(842, 63, 846, 75, 1, "#3A3A3C"))
        status.add(bars, g5, batt)

        self.status_dot = m.Circle(radius=9 * PS, fill_color=ORANGE, fill_opacity=1, stroke_width=0).move_to(P(57, 209))
        self.status_text = at_left(T("Connecting…", 24 * PS, SECONDARY), P(86, 209))
        menu = m.VGroup(m.Circle(radius=19 * PS, stroke_color=ACCENT, stroke_width=2.2).move_to(P(838, 209)),
                        *[m.Dot(P(838 + dx, 209), radius=3.2 * PS, color=ACCENT) for dx in (-9, 0, 9)])

        # 1.4: the control row is gone and the trackpad fills its space
        pad = pbox(48, 280, 876, 1760, 66, GRAY5)
        hint = T("Tap to click · Two-finger double-tap to right-click", 18 * PS, "#5E5E63").move_to(P(461, 1708))
        self.pad_box = (48, 280, 876, 1760)

        # floating remote button (58pt), snapped to the right edge about 2/3 down
        self.fab_pt = P(838, 1290)
        fab_bg = m.Circle(radius=68 * PS, fill_color=GRAY4, fill_opacity=0.95, stroke_color="#FFFFFF",
                          stroke_width=1.2, stroke_opacity=0.18).move_to(self.fab_pt)
        fab_shadow = m.Circle(radius=74 * PS, fill_color="#000000", fill_opacity=0.45, stroke_width=0)
        fab_shadow.move_to(self.fab_pt + m.DOWN * 18 * PS)
        remote = m.VGroup(rrect(30 * PS, 66 * PS, 12 * PS, "#000000", 0).set_stroke("#FFFFFF", width=2),
                          m.Circle(radius=9 * PS, fill_color="#FFFFFF", fill_opacity=1, stroke_width=0).shift(m.UP * 14 * PS),
                          m.Dot(radius=3.2 * PS, color="#FFFFFF").shift(m.DOWN * 8 * PS),
                          m.Dot(radius=3.2 * PS, color="#FFFFFF").shift(m.DOWN * 20 * PS))
        remote.move_to(self.fab_pt)
        self.fab = m.VGroup(fab_shadow, fab_bg, remote)
        self.build_dpad()

        self.field = pbox(48, 1790, 630, 1890, 47, GRAY5)
        self.placeholder = at_left(T("Type to send…", 28 * PS, "#6E6E73"), P(86, 1840))
        self.bksp = m.VGroup(m.Circle(radius=49 * PS, fill_color=GRAY5, fill_opacity=1, stroke_width=0).move_to(P(704, 1842)),
                             delete_icon(704, 1842))
        self.ret = m.VGroup(m.Circle(radius=49 * PS, fill_color=GRAY5, fill_opacity=1, stroke_width=0).move_to(P(826, 1842)),
                            return_icon(826, 1842))

        # Trackpad sits at 0.35 opacity (the remote button at 0.5) until connected: a black veil does the same
        self.veil = pbox(30, 270, 893, 1775, 0, "#000000", 0.65)
        self.phone = m.Group(body, buttons, screen, island, status, self.status_dot, self.status_text, menu,
                             pad, hint, self.fab, self.veil,
                             self.field, self.placeholder, self.bksp, self.ret)

    def build_dpad(self):
        """The D-pad overlay (DPadOverlay.swift): 300pt ring of four wedges around Play/Pause, plus a close button."""
        k = 923 / 393                                  # screenshot px per pt
        cx, cy = 461.5, 915                            # pad + 28pt + close, centred on the screen
        R, groove_r, center_r = 150 * k, 65 * k, 58 * k
        C = P(cx, cy)
        self.dpad_backdrop = rrect(3.0, 2000 * PS, 0.42, "#0A0A0C", 0.74).move_to([PX, PY, 0])
        shadow = m.Circle(radius=R * PS, fill_color="#000000", fill_opacity=0.5, stroke_width=0)
        shadow.move_to(C + m.DOWN * 20 * k * PS)
        groove = m.Circle(radius=groove_r * PS, fill_color="#0A0A0C", fill_opacity=0.85, stroke_width=0).move_to(C)
        center = m.Circle(radius=center_r * PS, fill_color="#48484A", fill_opacity=1, stroke_color="#FFFFFF",
                          stroke_width=1, stroke_opacity=0.12).move_to(C)

        def wedge(deg, color, opacity):
            # a quarter circle pushed out along its bisector so neighbours sit 5pt apart
            a = np.radians(deg)
            tip = (cx + 2.5 * np.sqrt(2) * k * np.cos(a), cy + 2.5 * np.sqrt(2) * k * np.sin(a))
            arc = [(tip[0] + R * np.cos(t), tip[1] + R * np.sin(t)) for t in np.linspace(a - np.pi / 4, a + np.pi / 4, 40)]
            w = m.VMobject().set_points_as_corners([P(*p) for p in [tip, *arc, tip]])
            return w.set_fill(color, opacity=opacity).set_stroke(width=0)

        dirs = {"up": (90, "u"), "right": (0, "r"), "down": (-90, "d"), "left": (180, "l")}
        # screenshot y grows downward, so angles are mirrored: "up" is at -90° in pixel space
        segs = m.VGroup(*[wedge(-deg, GRAY4, 0.92) for deg, _ in dirs.values()])
        self.hl = {name: m.Difference(wedge(-deg, ACCENT, 1), groove, fill_color=ACCENT, fill_opacity=1, stroke_width=0)
                   for name, (deg, _) in dirs.items()}
        self.hl["mid"] = m.Circle(radius=center_r * PS, fill_color=ACCENT, fill_opacity=1, stroke_width=0).move_to(C)
        key_px = {name: (cx + 102 * k * np.cos(np.radians(deg)), cy - 102 * k * np.sin(np.radians(deg)))
                  for name, (deg, _) in dirs.items()}
        self.key_pt = {name: P(*p) for name, p in key_px.items()}
        self.key_pt["mid"] = C
        self.icons = m.VGroup(*[chevron(*key_px[n], d, size=24, width=4.6) for n, (_, d) in dirs.items()],
                              playpause_icon(cx, cy))

        close_y = cy + R + 28 * k + 22 * k
        self.close_pt = P(cx, close_y)
        close = m.VGroup(m.Circle(radius=22 * k * PS, fill_color=GRAY4, fill_opacity=0.8, stroke_width=0).move_to(self.close_pt),
                         ppoly([(cx - 16, close_y - 16), (cx + 16, close_y + 16)], width=4.6),
                         ppoly([(cx - 16, close_y + 16), (cx + 16, close_y - 16)], width=4.6))
        self.dpad = m.VGroup(shadow, segs, groove, center, self.icons, close)

    # ------------------------------------------------------------------ helpers
    def caption(self, n, text):
        badge = m.VGroup(m.Circle(radius=0.17, fill_color=ACCENT, fill_opacity=1, stroke_width=0),
                         T(str(n), 0.13, weight=m.BOLD)) if n else m.VGroup()
        label = T(text, 0.17, weight=m.MEDIUM)
        group = m.VGroup(badge, label).arrange(m.RIGHT, buff=0.2) if n else m.VGroup(label)
        group.move_to([MX, -2.85, 0])
        anims = [m.FadeIn(group, shift=m.UP * 0.15)]
        if getattr(self, "_caption", None) is not None:
            anims.append(m.FadeOut(self._caption, shift=m.UP * 0.15))
        self._caption = group
        return anims

    def tap(self, point, highlight=None, run_time=0.22):
        """Finger touches `point`; returns the touch dot (still on screen)."""
        dot = touch_dot().move_to(point)
        anims = [m.FadeIn(dot, scale=1.8)]
        if highlight is not None:
            highlight.set_opacity(0)
            self.add(highlight)
            self.add(*[i for i in self.icons]) if highlight in self.hl.values() else None
            anims.append(highlight.animate.set_fill(opacity=1))
        self.play(*anims, run_time=run_time, rate_func=m.ease_out_cubic)
        return dot

    def release(self, dot, highlight=None, extra=(), run_time=0.35):
        ring = m.Circle(radius=0.15, stroke_color="#FFFFFF", stroke_width=3).move_to(dot).set_z_index(8)
        anims = [m.FadeOut(dot, scale=0.6), ring.animate.scale(2.6).set_stroke(opacity=0), *extra]
        if highlight is not None:
            anims.append(highlight.animate.set_fill(opacity=0))
        self.play(*anims, run_time=run_time)
        self.remove(ring)
        if highlight is not None:
            self.remove(highlight)

    def packet(self, label, start, end, run_time=0.6, extra=()):
        """A message chip flies over Bluetooth from the phone to the Mac."""
        chip_t = T(label, 0.12, weight=m.BOLD)
        chip = m.VGroup(rrect(chip_t.width + 0.36, 0.34, 0.17, ACCENT), chip_t).set_z_index(20)
        chip.move_to(start)
        path = m.ArcBetweenPoints(start, end, angle=0.7)
        trail = m.TracedPath(chip.get_center, dissipating_time=0.25, stroke_color=ACCENT, stroke_width=5)
        trail.set_z_index(19)
        self.add(trail)
        self.play(m.FadeIn(chip, scale=0.5), run_time=0.12)
        self.play(m.MoveAlongPath(chip, path, rate_func=m.ease_in_out_sine), *extra, run_time=run_time)
        burst = m.Circle(radius=0.12, stroke_color=ACCENT, stroke_width=4).move_to(end).set_z_index(19)
        self.play(m.FadeOut(chip, scale=0.4), burst.animate.scale(3).set_stroke(opacity=0), run_time=0.25)
        self.remove(trail, burst)

    def press_button(self, name, label, end, effect=(), effect_time=0.5):
        dot = self.tap(self.key_pt[name], self.hl[name])
        self.release(dot, self.hl[name], run_time=0.25)
        self.packet(label, self.key_pt[name] + m.UP * 0.05, end)
        if effect:
            self.play(*effect, run_time=effect_time)

    def swipe(self, pts_px, cursor_to, run_time=1.6):
        """A one-finger drag on the trackpad, drawn as a glowing trail; the Mac cursor follows."""
        path = m.CubicBezier(*[P(*p) for p in pts_px])
        t = m.ValueTracker(0.001)
        d0 = path.get_start()
        d1 = path.get_end()
        c0 = tip_of(self.cursor)
        gain = (np.asarray(cursor_to) - c0)[:2] / (d1 - d0)[:2]

        dot = touch_dot().move_to(d0)
        dot.add_updater(lambda d: d.move_to(path.point_from_proportion(t.get_value())))

        def tail(width, color, opacity, span):
            def draw():
                v = m.VMobject()
                v.pointwise_become_partial(path, max(0.0, t.get_value() - span), t.get_value())
                return v.set_stroke(color, width=width, opacity=opacity).set_z_index(7)
            return m.always_redraw(draw)

        glow = tail(26, ACCENT, 0.28, 1.0)
        core = tail(7, "#FFFFFF", 0.85, 1.0)

        def follow(c):
            p = path.point_from_proportion(t.get_value())
            target = c0 + np.array([*((p - d0)[:2] * gain), 0])
            c.shift(target - tip_of(c))
        self.cursor.add_updater(follow)

        # pointer events stream to the Mac while the finger moves
        stream_start = P(80, 700)
        stream_path = m.ArcBetweenPoints(stream_start, np.array([DR - 0.35, MY + 0.4, 0]), angle=0.7)
        sparks = []
        for _ in range(7):
            s = m.Dot(radius=0.05, color=ACCENT).set_z_index(20).set_opacity(0)
            sparks.append(s)

        def spark_anim(s):
            def upd(mob, a):
                mob.move_to(stream_path.point_from_proportion(a))
                mob.set_opacity(np.sin(np.pi * a))
            return m.UpdateFromAlphaFunc(s, upd)

        self.add(glow, core, dot)
        self.play(m.FadeIn(dot, scale=1.8), run_time=0.15)
        self.play(t.animate.set_value(1.0), m.LaggedStart(*[spark_anim(s) for s in sparks], lag_ratio=0.18),
                  run_time=run_time, rate_func=m.ease_in_out_sine)
        self.cursor.remove_updater(follow)
        dot.clear_updaters()
        # an arrow head at the end says which way the finger went
        tan = path.point_from_proportion(1.0) - path.point_from_proportion(0.96)
        ang = np.arctan2(tan[1], tan[0])
        head = m.Triangle(fill_color="#FFFFFF", fill_opacity=0.9, stroke_width=0).scale(0.11)
        head.rotate(ang - np.pi / 2).move_to(d1 + 0.12 * np.array([np.cos(ang), np.sin(ang), 0])).set_z_index(8)
        self.play(m.FadeIn(head, scale=0.5), m.FadeOut(dot, scale=0.6), run_time=0.25)
        glow.clear_updaters()
        core.clear_updaters()
        self.play(m.FadeOut(m.VGroup(glow, core, head)), *[m.FadeOut(s) for s in sparks], run_time=0.5)
        self.remove(*sparks)

    def mac_click(self):
        tip = tip_of(self.cursor)
        ring = m.Circle(radius=0.06, stroke_color="#FFFFFF", stroke_width=3).move_to(tip).set_z_index(7)
        return [ring.animate.scale(3.2).set_stroke(opacity=0),
                m.Indicate(self.cursor, scale_factor=0.8, color=None)], ring

    def trackpad_tap(self, point_px):
        dot = self.tap(P(*point_px))
        self.release(dot, run_time=0.25)
        self.packet("Click", P(*point_px), tip_of(self.cursor) + m.RIGHT * 0.05, run_time=0.5)
        anims, ring = self.mac_click()
        return anims, ring

    # ------------------------------------------------------------------ beats
    def intro(self):
        title = T("LazyRemote", 0.62, weight=m.BOLD)
        sub = T("Your iPhone is now your Mac’s remote.", 0.24, SECONDARY)
        m.VGroup(title, sub).arrange(m.DOWN, buff=0.38).move_to(m.ORIGIN)
        self.play(m.FadeIn(title, shift=m.UP * 0.3), run_time=0.9)
        self.play(m.FadeIn(sub, shift=m.UP * 0.2), run_time=0.7)
        self.wait(0.9)
        self.play(m.FadeOut(m.VGroup(title, sub), shift=m.UP * 0.4), run_time=0.6)

        self.wordmark = at_left(T("LazyRemote", 0.2, weight=m.BOLD), [-6.75, 3.62, 0])
        self.play(m.FadeIn(self.mac, shift=m.RIGHT * 0.4), m.FadeIn(self.app, shift=m.RIGHT * 0.4),
                  m.FadeIn(self.phone, shift=m.LEFT * 0.4), m.FadeIn(self.wordmark), run_time=1.1)
        self.add(self.cursor)
        self.play(m.FadeIn(self.cursor), run_time=0.3)

    def connect(self):
        anims = self.caption(0, "Connects over Bluetooth · encrypted · no Wi‑Fi needed")
        waves = m.VGroup(*[m.Arc(radius=0.3 + 0.28 * i, start_angle=np.pi - 0.6, angle=1.2, stroke_color=ACCENT,
                                 stroke_width=4) for i in range(3)])
        waves.move_to([PX - 1.95, PY + 0.2, 0])
        self.play(*anims, run_time=0.6)
        self.play(m.LaggedStart(*[m.Succession(m.FadeIn(w, run_time=0.3), m.FadeOut(w, run_time=0.4))
                                  for w in waves], lag_ratio=0.35), run_time=1.3)
        connected = at_left(T("MacBook Air", 24 * PS, SECONDARY), P(86, 209))
        self.play(m.Transform(self.status_text, connected), self.status_dot.animate.set_fill(GREEN),
                  m.FadeOut(self.veil), m.Flash(self.status_dot, color=GREEN, line_length=0.08,
                                                         flash_radius=0.1), run_time=0.6)
        self.wait(0.8)

    def swipe_and_click(self):
        self.play(*self.caption(1, "Swipe the trackpad to move the cursor"), run_time=0.5)
        target = self.search.get_left() + m.RIGHT * 0.95 + m.DOWN * 0.03
        self.swipe([(700, 1250), (760, 820), (420, 520), (190, 420)], target, run_time=1.7)
        self.play(*self.caption(1, "Tap to click"), run_time=0.4)
        anims, ring = self.trackpad_tap((300, 760))
        caret = m.Line(m.UP * 0.075, m.DOWN * 0.075, stroke_color=ACCENT, stroke_width=2.4)
        caret.move_to(self.search_ph.get_left() + m.LEFT * 0.02)
        self.play(*anims, self.search_ring.animate.set_stroke(opacity=1), m.FadeOut(self.search_ph),
                  m.FadeIn(caret), run_time=0.45)
        self.remove(ring)
        self.caret = caret
        self.wait(0.3)

    def type_and_send(self):
        self.play(*self.caption(2, "Type on your iPhone, send it to your Mac"), run_time=0.5)
        # tap the text field: keyboard rises, the bar sits above it, the rest gets a scrim
        dot = self.tap(P(300, 1840))
        self.release(dot, run_time=0.2)

        scrim = m.Rectangle(width=3.0, height=2000 * PS, fill_color="#000000", fill_opacity=0.45, stroke_width=0)
        scrim.move_to([PX, PY, 0])
        kb = self.keyboard()
        y0 = 1135
        field_f = pbox(48, y0, 520, y0 + 100, 47, GRAY5)
        ph_f = at_left(T("Type to send…", 28 * PS, "#6E6E73"), P(86, y0 + 50))
        send = m.VGroup(m.Circle(radius=49 * PS, fill_color=GRAY4, fill_opacity=1, stroke_width=0).move_to(P(827, y0 + 52)),
                        arrow_up_icon(827, y0 + 52))
        self.add(scrim)
        scrim.set_fill(opacity=0)
        self.add(self.field, self.placeholder, self.bksp, self.ret)
        self.play(scrim.animate.set_fill(opacity=0.45), m.FadeIn(kb, shift=m.UP * 0.6),
                  m.Transform(self.field, field_f), m.Transform(self.placeholder, ph_f),
                  self.bksp.animate.move_to(P(583, y0 + 52)), self.ret.animate.move_to(P(705, y0 + 52)),
                  m.FadeIn(send, scale=0.6), m.FadeOut(self.fab), run_time=0.45, rate_func=m.ease_out_cubic)

        phrase = "deep space"
        draft = None
        caret = m.Line(P(86, y0 + 28), P(86, y0 + 72), stroke_color=ACCENT, stroke_width=2.4)
        self.play(m.FadeOut(self.placeholder), m.FadeIn(caret), run_time=0.15)
        finger = touch_dot()
        for i, ch in enumerate(phrase):
            key = self.keys[ch]
            new = at_left(T(phrase[:i + 1], 28 * PS), P(86, y0 + 50))
            if draft is not None:
                self.remove(draft)
            self.add(new)
            draft = new
            anims = [finger.animate.move_to(key.get_center()) if i else m.FadeIn(finger.move_to(key), scale=1.5),
                     key.animate(rate_func=m.there_and_back).set_fill("#A4A4AA"),
                     caret.animate.move_to(draft.get_right() + m.RIGHT * 0.03)]
            if i == 0:
                anims.append(send[0].animate.set_fill(ACCENT))
            self.play(*anims, run_time=0.17)
        self.play(m.FadeOut(finger), run_time=0.15)
        self.wait(0.2)

        # send ↑ — the text goes over, the draft clears and the keyboard drops
        dot = self.tap(send.get_center())
        self.release(dot, run_time=0.2)
        mac_text = at_left(T(phrase, 0.075), self.search_ph.get_left())
        end = mac_text.get_center()
        self.packet("“deep space”", send.get_center(), end, run_time=0.65,
                    extra=[m.FadeOut(draft), m.FadeOut(caret)])
        field0 = pbox(48, 1790, 630, 1890, 47, GRAY5)
        ph0 = at_left(T("Type to send…", 28 * PS, "#6E6E73"), P(86, 1840))
        self.play(m.AddTextLetterByLetter(mac_text, time_per_char=0.04),
                  self.caret.animate.move_to(mac_text.get_right() + m.RIGHT * 0.025 + m.UP * 0 * 0),
                  scrim.animate.set_fill(opacity=0), m.FadeOut(kb, shift=m.DOWN * 0.6), m.FadeOut(send, scale=0.6),
                  m.Transform(self.field, field0), m.FadeIn(ph0),
                  self.bksp.animate.move_to(P(704, 1842)), self.ret.animate.move_to(P(826, 1842)),
                  m.FadeIn(self.fab), run_time=0.6)
        self.caret.move_to([mac_text.get_right()[0] + 0.03, self.search.get_y(), 0])
        self.remove(scrim)
        self.placeholder = ph0
        self.mac_text = mac_text
        self.wait(0.4)

        # ↵ Return runs the search
        self.play(*self.caption(2, "Return and backspace keys too"), run_time=0.4)
        dot = self.tap(self.ret.get_center())
        self.release(dot, run_time=0.2)
        self.packet("Return", self.ret.get_center(), self.search.get_right() + m.LEFT * 0.2, run_time=0.55)

        pw, ph, gap, grid_top = self.grid_geo
        res_head = at_left(T("Results for “deep space”", 0.095, weight=m.BOLD), self.heading.get_left())
        results = m.Group()
        for i, (name, seed) in enumerate([("Deep Space", None), ("Deep Space II", 6), ("Space Station", 1)]):
            cx = MX - 1.5 * (pw + gap) + i * (pw + gap)
            cy = grid_top - 0.32 - ph / 2
            pic = nebula(480, 300, seed=3 + i) if seed is None or i == 1 else poster(seed)
            img = _img(pic).stretch_to_fit_width(pw).stretch_to_fit_height(ph).move_to([cx, cy, 0])
            cap = at_left(T(name, 0.068, "#D8D8DC"), [cx - pw / 2, cy - ph / 2 - 0.12, 0])
            results.add(m.Group(img, cap))
        self.results = results
        self.play(m.FadeOut(self.grid, shift=m.DOWN * 0.1), m.FadeOut(self.heading),
                  m.FadeIn(res_head), m.LaggedStart(*[m.FadeIn(r, shift=m.UP * 0.1) for r in results], lag_ratio=0.2),
                  m.FadeOut(self.caret), run_time=0.8)
        self.res_head = res_head
        self.wait(0.3)

    def open_movie(self):
        self.play(*self.caption(1, "Swipe to the movie, tap to open"), run_time=0.45)
        first = self.results[0][0]
        self.swipe([(260, 470), (300, 760), (560, 980), (600, 1150)], first.get_center() + m.UP * 0.05,
                   run_time=1.3)
        hover = m.SurroundingRectangle(first, buff=0.03, corner_radius=0.04, stroke_color="#FFFFFF", stroke_width=2.5)
        self.play(m.Create(hover), run_time=0.25)
        anims, ring = self.trackpad_tap((480, 900))
        self.play(*anims, run_time=0.35)
        self.remove(ring)

        # the player opens full screen, paused
        self.ft = m.ValueTracker(12 * 60 + 34)
        self.playing = False
        movie = self.build_player()
        grow = first.copy()
        self.add(grow)
        self.play(grow.animate.stretch_to_fit_width(DW).stretch_to_fit_height(DH).move_to([MX, MY, 0]),
                  m.FadeOut(hover), run_time=0.6, rate_func=m.ease_in_out_cubic)
        self.add(movie, self.cursor)
        self.play(m.FadeIn(movie), run_time=0.35)
        gone = m.Group(grow, self.app, self.grid, self.results, self.res_head, self.mac_text, self.caret)
        self.remove(*gone.get_family())
        self.play(m.FadeOut(self.cursor), run_time=0.3)

    def build_player(self):
        ft = self.ft
        frame = _img(nebula()).stretch_to_fit_width(DW).stretch_to_fit_height(DH).move_to([MX, MY, 0])
        rng = np.random.default_rng(11)
        stars = m.VGroup()
        seeds = []
        for _ in range(70):
            x0, y0 = rng.uniform(0, DW), rng.uniform(0.25, DH - 0.1)
            speed, r = rng.uniform(0.02, 0.09), rng.uniform(0.008, 0.024)
            seeds.append((x0, y0, speed))
            stars.add(m.Dot(radius=r, color="#FFFFFF").set_opacity(rng.uniform(0.5, 1)))

        def drift(g):
            f = ft.get_value()
            for d, (x0, y0, sp) in zip(g, seeds):
                d.move_to([DL + (x0 - sp * f * 4) % DW, DB + y0, 0])
        stars.add_updater(drift)
        drift(stars)
        orb = _img(planet()).scale_to_fit_width(2.6)
        orb.add_updater(lambda o: o.move_to([MX + 1.6 - 0.004 * (ft.get_value() - 754),
                                             MY + 0.3 + 0.12 * np.sin((ft.get_value() - 754) * 0.25), 0]))
        clock = m.Mobject()
        clock.add_updater(lambda _, dt: ft.increment_value(dt) if self.playing else None)

        # controls: gradient strip, progress bar, time readout
        shade = m.Rectangle(width=DW, height=0.75, stroke_width=0).move_to([MX, DB + 0.375, 0])
        shade.set_fill(["#000000", "#000000"], opacity=0.55)
        x0, x1 = DL + 0.75, DR - 1.55
        by = DB + 0.24
        track = m.Line([x0, by, 0], [x1, by, 0], stroke_color="#FFFFFF", stroke_width=4, stroke_opacity=0.3)
        total = 6500.0

        def bar_x():
            return x0 + (x1 - x0) * ft.get_value() / total
        filled = m.always_redraw(lambda: m.Line([x0, by, 0], [bar_x(), by, 0], stroke_color=ACCENT, stroke_width=4))
        knob = m.always_redraw(lambda: m.Dot([bar_x(), by, 0], radius=0.055, color="#FFFFFF"))
        cache = {}

        def readout():
            s = fmt(ft.get_value())
            if s not in cache:
                cache[s] = T(f"{s} / 1:48:20", 0.075, "#E5E5EA").move_to([x1 + 0.08, by, 0], aligned_edge=m.LEFT)
            return cache[s].copy()
        time_text = m.always_redraw(readout)
        self.small_pp = m.VGroup()
        self.small_play = m.Triangle(fill_color="#FFFFFF", fill_opacity=1, stroke_width=0).scale(0.06).rotate(-np.pi / 2)
        self.small_play.move_to([DL + 0.38, by, 0])
        self.small_pause = m.VGroup(rrect(0.035, 0.12, 0.01, "#FFFFFF").shift(m.LEFT * 0.035),
                                    rrect(0.035, 0.12, 0.01, "#FFFFFF").shift(m.RIGHT * 0.035)).move_to([DL + 0.38, by, 0])
        self.small_pause.set_opacity(0)
        title = at_left(T("Deep Space", 0.13, weight=m.BOLD), [DL + 0.35, DT - 0.35, 0])
        self.player_title = title
        self.player_ui = m.VGroup(shade, track, filled, knob, time_text, self.small_play, self.small_pause, title)
        return m.Group(frame, stars, orb, clock, self.player_ui)

    def center_flash(self, playing):
        bg = m.Circle(radius=0.48, fill_color="#000000", fill_opacity=0.55, stroke_width=0)
        if playing:
            icon = m.Triangle(fill_color="#FFFFFF", fill_opacity=1, stroke_width=0).scale(0.22).rotate(-np.pi / 2)
            icon.shift(m.RIGHT * 0.04)
        else:
            icon = m.VGroup(rrect(0.1, 0.36, 0.02, "#FFFFFF").shift(m.LEFT * 0.09),
                            rrect(0.1, 0.36, 0.02, "#FFFFFF").shift(m.RIGHT * 0.09))
        g = m.VGroup(bg, icon).move_to([MX, MY, 0]).set_z_index(5)
        return g

    def seek_overlay(self, forward):
        side = 1 if forward else -1
        panel = rrect(DW / 3.2, DH - 0.6, 0.5, "#FFFFFF", 0.16)
        panel.move_to([MX + side * (DW / 2 - DW / 6.4 - 0.2), MY + 0.15, 0])
        tris = m.VGroup(*[m.Triangle(fill_color="#FFFFFF", fill_opacity=1, stroke_width=0).scale(0.13)
                          .rotate(-side * np.pi / 2) for _ in range(3)]).arrange(m.RIGHT, buff=0.03)
        if not forward:
            tris = m.VGroup(*reversed(tris))
        label = T("+5 seconds" if forward else "−5 seconds", 0.13, weight=m.BOLD)
        inner = m.VGroup(tris, label).arrange(m.DOWN, buff=0.2).move_to(panel)
        return m.VGroup(panel, inner).set_z_index(5), tris

    def play_pause_and_arrows(self):
        screen_pt = np.array([MX + 0.4, MY + 0.2, 0])

        # the floating remote button opens the D-pad overlay
        self.play(*self.caption(3, "Tap the floating remote for the D‑pad"), run_time=0.45)
        dot = self.tap(self.fab_pt)
        self.release(dot, run_time=0.25)
        self.play(m.FadeIn(self.dpad_backdrop), m.FadeIn(self.dpad, scale=0.92), run_time=0.3,
                  rate_func=m.ease_out_cubic)
        self.wait(0.5)

        # Space: play
        self.play(*self.caption(3, "Play / pause sends Space"), run_time=0.45)
        self.press_button("mid", "Space", screen_pt)
        self.playing = True
        flash = self.center_flash(True)
        self.play(m.FadeIn(flash, scale=0.7), self.small_play.animate.set_opacity(0),
                  self.small_pause.animate.set_opacity(1), self.player_title.animate.set_opacity(0), run_time=0.3)
        self.play(flash.animate.scale(1.4).set_opacity(0), run_time=0.5)
        self.remove(flash)
        self.wait(1.4)

        # → seek forward twice, ← back once
        self.play(*self.caption(4, "Arrow keys skip, scrub and set the volume"), run_time=0.45)
        for forward, label in [(True, "→"), (True, "→"), (False, "←")]:
            name = "right" if forward else "left"
            self.press_button(name, label, screen_pt + (m.RIGHT if forward else m.LEFT) * 1.8)
            ov, tris = self.seek_overlay(forward)
            self.ft.increment_value(5 if forward else -5)
            self.play(m.FadeIn(ov, scale=0.92), m.LaggedStart(*[m.Indicate(t, color=None, scale_factor=1.35)
                                                                for t in tris], lag_ratio=0.3), run_time=0.55)
            self.wait(0.2)
            self.play(m.FadeOut(ov), run_time=0.3)

        # ↑ volume
        self.press_button("up", "↑", np.array([DR - 1.0, DT - 0.4, 0]))
        hud_bg = rrect(1.6, 0.36, 0.18, "#000000", 0.6).move_to([DR - 1.05, DT - 0.4, 0])
        spk = m.VGroup(m.Polygon([-0.05, -0.03, 0], [-0.02, -0.03, 0], [0.03, -0.07, 0], [0.03, 0.07, 0],
                                 [-0.02, 0.03, 0], [-0.05, 0.03, 0], fill_color="#FFFFFF", fill_opacity=1, stroke_width=0),
                       m.Arc(radius=0.06, start_angle=-0.8, angle=1.6, stroke_color="#FFFFFF", stroke_width=2).shift(m.RIGHT * 0.03))
        spk.move_to(hud_bg.get_left() + m.RIGHT * 0.22)
        vx0, vx1 = hud_bg.get_left()[0] + 0.42, hud_bg.get_right()[0] - 0.18
        vy = hud_bg.get_y()
        vol_track = m.Line([vx0, vy, 0], [vx1, vy, 0], stroke_color="#FFFFFF", stroke_width=5, stroke_opacity=0.3)
        vol = m.ValueTracker(0.55)
        vol_fill = m.always_redraw(lambda: m.Line([vx0, vy, 0], [vx0 + (vx1 - vx0) * vol.get_value(), vy, 0],
                                                  stroke_color="#FFFFFF", stroke_width=5))
        hud = m.VGroup(hud_bg, spk, vol_track, vol_fill).set_z_index(5)
        self.play(m.FadeIn(hud), run_time=0.25)
        self.play(vol.animate.set_value(0.8), run_time=0.4)
        self.wait(0.4)
        self.play(m.FadeOut(hud), run_time=0.3)
        self.wait(0.6)

        # Space: pause
        self.play(*self.caption(3, "Tap again to pause"), run_time=0.45)
        self.press_button("mid", "Space", screen_pt)
        self.playing = False
        flash = self.center_flash(False)
        self.play(m.FadeIn(flash, scale=0.7), self.small_play.animate.set_opacity(1),
                  self.small_pause.animate.set_opacity(0), self.player_title.animate.set_opacity(1), run_time=0.3)
        self.play(flash.animate.scale(1.4).set_opacity(0), run_time=0.5)
        self.remove(flash)
        self.wait(0.5)

        # × closes the overlay
        dot = self.tap(self.close_pt)
        self.release(dot, run_time=0.25)
        self.play(m.FadeOut(self.dpad_backdrop), m.FadeOut(self.dpad, scale=0.92), run_time=0.25)
        self.wait(0.5)

    def keyboard(self):
        top = 1262
        screen = rrect(3.0, 2000 * PS, 0.42, "#000000").move_to([PX, PY, 0])
        clip = m.Rectangle(width=3.2, height=(2000 - top) * PS).move_to(P(461.5, (top + 2000) / 2))
        kb = m.VGroup(m.Intersection(screen, clip, fill_color="#232325", fill_opacity=1, stroke_width=0))
        self.keys = {}
        kw, kh, g = 80.0, 100.0, 12.0
        rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
        for r, row in enumerate(rows):
            y = top + 22 + r * (kh + 22) + kh / 2
            n = len(row)
            x = (923 - (n * kw + (n - 1) * g)) / 2
            for ch in row:
                key = pbox(x, y - kh / 2, x + kw, y + kh / 2, 12, "#5A5A5E")
                lab = T(ch, 30 * PS).move_to(P(x + kw / 2, y - 4))
                kb.add(key, lab)
                self.keys[ch] = key
                x += kw + g
        y = top + 22 + 2 * (kh + 22) + kh / 2
        kb.add(pbox(8, y - kh / 2, 112, y + kh / 2, 12, "#3A3A3D"), pbox(811, y - kh / 2, 915, y + kh / 2, 12, "#3A3A3D"))
        kb.add(ppoly([(60, y + 18), (60, y - 2), (44, y - 2), (60, y - 22), (76, y - 2), (60, y - 2)], width=2.4))
        kb.add(delete_icon(863, y))
        y = top + 22 + 3 * (kh + 22) + kh / 2
        b123 = pbox(8, y - kh / 2, 200, y + kh / 2, 12, "#3A3A3D")
        space = pbox(212, y - kh / 2, 711, y + kh / 2, 12, "#5A5A5E")
        retk = pbox(723, y - kh / 2, 915, y + kh / 2, 12, "#3A3A3D")
        kb.add(b123, T("123", 24 * PS).move_to(b123), space, T("space", 24 * PS).move_to(space),
               retk, T("return", 24 * PS).move_to(retk))
        self.keys[" "] = space
        kb.add(pbox(330, 1968, 593, 1978, 5, "#FFFFFF"))
        return kb

    def outro(self):
        self.play(*self.caption(0, "Free · open source · no ads, no tracking"), run_time=0.45)
        self.wait(0.6)
        everything = m.Group(*[mob for mob in self.mobjects])
        self.play(m.FadeOut(everything), run_time=0.7)
        title = T("LazyRemote", 0.6, weight=m.BOLD)
        sub = T("Use your iPhone as a remote for your Mac, over Bluetooth.", 0.2, SECONDARY)
        feats = m.VGroup(*[T(s, 0.15, "#E5E5EA") for s in [
            "Floating D‑pad & play/pause", "Trackpad: swipe, tap, right-click",
            "Type on iPhone, send to Mac", "Direct and encrypted"]])
        dots = m.VGroup(*[m.Dot(radius=0.05, color=ACCENT) for _ in feats])
        rows = m.VGroup(*[m.VGroup(d, f).arrange(m.RIGHT, buff=0.18) for d, f in zip(dots, feats)])
        rows.arrange_in_grid(rows=2, cols=2, buff=(0.8, 0.32), cell_alignment=m.LEFT)
        url = T("github.com/ibrahimaltay/macbook-remote", 0.17, ACCENT, weight=m.MEDIUM)
        block = m.VGroup(title, sub, rows, url).arrange(m.DOWN, buff=0.45).move_to(m.ORIGIN)
        self.play(m.FadeIn(title, shift=m.UP * 0.2), run_time=0.6)
        self.play(m.FadeIn(sub), run_time=0.4)
        self.play(m.LaggedStart(*[m.FadeIn(r, shift=m.UP * 0.1) for r in rows], lag_ratio=0.2), run_time=1.0)
        self.play(m.FadeIn(url, shift=m.UP * 0.1), run_time=0.5)
        self.wait(2.2)
