"""MacBook Air (13.6", silver, Turkish Q keyboard) modelled from real dimensions.

Scene units: 1 unit = 76 mm, so the 304 mm width is 4.0 units.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import manimgx as m

K = 4.0 / 304.1                 # units per mm
W, D = 304.1 * K, 215.0 * K     # 4.0 x 2.83
BASE_T = 7.4 * K                # aluminium base
LID_T = 3.6 * K                 # display lid
GAP = 0.4 * K                   # closed gap between the two halves
FILLET = 1.2 * K                # edge rounding

ALU_COLOR = "#CFD1D5"
KEY_COLOR = "#0C0C0E"
GLASS_COLOR = "#040405"

ALU = m.Material(metallic=0.6, roughness=0.45)
KEYMAT = m.Material(metallic=0.0, roughness=0.6, reflectance=0.35)
GLASS = m.Material(metallic=0.0, roughness=0.08, reflectance=0.45)
PAD = m.Material(metallic=0.7, roughness=0.5)
FLOOR = m.Material(metallic=0.0, roughness=0.5, reflectance=0.06)


# --------------------------------------------------------------------------- body
def _sp(x, p):
    return np.sign(x) * np.abs(x) ** p


def slab(w, d, h, z0, color, n=22.0, f=FILLET, res=160):
    """Rounded slab (squircle outline, filleted top and bottom edges), bottom at z0."""
    def ring(t, ww, dd):
        c, s = np.cos(t), np.sin(t)
        return (ww / 2) * _sp(c, 2 / n), (dd / 2) * _sp(s, 2 / n)

    arc = np.pi * f / 2
    total = 2 * arc + (h - 2 * f)

    def profile(v):
        s = v * total
        if s < arc:                                  # bottom fillet
            phi = s / f
            return f * (1 - np.sin(phi)), f * (1 - np.cos(phi))
        if s < arc + (h - 2 * f):                    # straight wall
            return 0.0, f + (s - arc)
        phi = (s - arc - (h - 2 * f)) / f            # top fillet
        return f * (1 - np.cos(phi)), h - f + f * np.sin(phi)

    def wall(t, v):
        inset, z = profile(v)
        x, y = ring(t + np.pi / 2, w - 2 * inset, d - 2 * inset)   # seam at the back edge
        return np.array([x, y, z0 + z])

    def cap(zz):
        ts = np.linspace(0, m.TAU, 320, endpoint=False)
        pts = [np.array([*ring(t, w - 2 * f, d - 2 * f), zz]) for t in ts]
        return m.Polygon(*pts)

    wall_s = m.Surface(wall, u_range=(0, m.TAU), v_range=(0, 1), resolution=(res, 28))
    top, bot = cap(z0 + h), cap(z0)
    for p in (wall_s, top, bot):
        p.set_fill(color, opacity=1)
        p.set_stroke(width=0)
    top.set_shade_in_3d(True)
    bot.set_shade_in_3d(True)
    return m.VGroup(wall_s, top, bot)


# --------------------------------------------------------------------------- screen picture
def make_wallpaper(px_w=1664, px_h=1082):
    """A macOS-style wallpaper with menu bar and notch, as an RGBA array."""
    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:px_h, 0:px_w].astype(np.float32)
    u, v = xx / px_w, yy / px_h
    img = np.zeros((px_h, px_w, 3), np.float32)
    img += np.array([0.05, 0.07, 0.22]) * (1 - v)[..., None] + np.array([0.10, 0.04, 0.18]) * v[..., None]
    blobs = [  # cx, cy, radius, colour
        (0.25, 0.30, 0.45, (0.20, 0.35, 0.95)),
        (0.75, 0.25, 0.40, (0.65, 0.25, 0.85)),
        (0.55, 0.80, 0.50, (0.95, 0.35, 0.45)),
        (0.10, 0.90, 0.35, (1.00, 0.60, 0.25)),
    ]
    for cx, cy, r, col in blobs:
        d2 = ((u - cx) * px_w / px_h) ** 2 + (v - cy) ** 2
        img += np.exp(-d2 / (r * r * 0.55))[..., None] * np.array(col) * 0.75
    img = np.clip(img, 0, 1)
    im = Image.fromarray((img * 255).astype(np.uint8)).convert("RGBA")
    im = im.filter(ImageFilter.GaussianBlur(2))

    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    bar = 34
    dr.rectangle([0, 0, px_w, bar], fill=(20, 20, 30, 120))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 150)
        mid = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 34)
    except OSError:
        font = big = mid = ImageFont.load_default()
    x = 24
    for label in ("", "Finder", "File", "Edit", "View", "Go", "Window", "Help"):
        if label:
            dr.text((x, 6), label, fill=(255, 255, 255, 235), font=font)
        else:
            dr.ellipse([x, 8, x + 16, 26], fill=(255, 255, 255, 235))
        x += 28 + dr.textlength(label or "  ", font=font)
    dr.text((px_w - 330, 6), "Fri Oct 9   12:11", fill=(255, 255, 255, 235), font=font)
    t = "12:11"
    tw = dr.textlength(t, font=big)
    dr.text(((px_w - tw) / 2, 250), t, fill=(255, 255, 255, 215), font=big)
    dt = "Friday, October 9"
    dw = dr.textlength(dt, font=mid)
    dr.text(((px_w - dw) / 2, 215), dt, fill=(255, 255, 255, 200), font=mid)
    # notch
    nw, nh = 190, 36
    dr.rounded_rectangle([(px_w - nw) / 2, -20, (px_w + nw) / 2, nh], radius=14, fill=(2, 2, 3, 255))
    im = Image.alpha_composite(im, ov)
    return np.array(im)


def make_phone_image(px_w=700, px_h=1440):
    """iPhone lock screen as an RGBA array with rounded corners and a Dynamic Island."""
    yy, xx = np.mgrid[0:px_h, 0:px_w].astype(np.float32)
    u, v = xx / px_w, yy / px_h
    img = np.zeros((px_h, px_w, 3), np.float32)
    img += np.array([0.06, 0.05, 0.20]) * (1 - v)[..., None] + np.array([0.18, 0.05, 0.16]) * v[..., None]
    for cx, cy, r, col in [(0.20, 0.25, 0.30, (0.25, 0.40, 1.00)), (0.85, 0.45, 0.28, (0.70, 0.30, 0.95)),
                           (0.40, 0.85, 0.35, (1.00, 0.40, 0.50)), (0.9, 0.95, 0.22, (1.00, 0.65, 0.30))]:
        d2 = ((u - cx) * px_w / px_h) ** 2 + (v - cy) ** 2
        img += np.exp(-d2 / (r * r * 0.5))[..., None] * np.array(col) * 0.8
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    try:
        big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 200)
        mid = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 46)
        sm = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 34)
    except OSError:
        big = mid = sm = ImageFont.load_default()
    dt = "Friday, October 9"
    dr.text(((px_w - dr.textlength(dt, font=mid)) / 2, 230), dt, fill=(255, 255, 255, 215), font=mid)
    t = "12:11"
    dr.text(((px_w - dr.textlength(t, font=big)) / 2, 290), t, fill=(255, 255, 255, 225), font=big)
    dr.text((46, 34), "12:11", fill=(255, 255, 255, 235), font=sm)
    dr.rounded_rectangle([(px_w - 215) / 2, 30, (px_w + 215) / 2, 30 + 62], radius=31, fill=(0, 0, 0, 255))
    dr.rounded_rectangle([(px_w - 260) / 2, px_h - 34, (px_w + 260) / 2, px_h - 24], radius=5,
                         fill=(255, 255, 255, 230))
    im = Image.alpha_composite(im, ov)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, px_w - 1, px_h - 1], radius=int(px_w * 0.115), fill=255)
    im.putalpha(Image.composite(im.getchannel("A"), Image.new("L", im.size, 0), mask))
    return np.array(im)


# --------------------------------------------------------------------------- keyboard
# (label, width in key units); rows follow the Turkish Q layout on a Mac ISO board
ROWS = [
    ("fn", [("esc", 1.5)] + [(f"F{i}", 1.0) for i in range(1, 13)] + [("", 1.0)]),
    ("num", [("\"\né", 1)] + [(c, 1) for c in "1234567890"] + [("*\n?", 1), ("-\n_", 1), ("⌫", 1.5)]),
    ("top", [("⇥", 1.5)] + [(c, 1) for c in "QWERTYUIOPĞÜ"] + [("↩", 1.0)]),
    ("home", [("⇪", 1.75)] + [(c, 1) for c in "ASDFGHJKLŞİ"] + [(",", 0.75), ("", 1.0)]),
    ("bot", [("⇧", 1.25), ("<", 1)] + [(c, 1) for c in "ZXCVBNMÖÇ."] + [("⇧", 2.25)]),
    ("mod", [("fn", 1), ("control", 1), ("option", 1), ("command", 1.25), ("", 5),
             ("command", 1.25), ("option", 1), ("◀", 1), ("▲▼", 1), ("▶", 1)]),
]


def build_keyboard(top_z, pitch=0.24, y_back=D / 2 - 0.18):
    face = m.VGroup()      # keycaps
    legends = m.VGroup()
    cap_gap = 0.032
    key_h = 0.016
    row_h = {"fn": 0.55}
    total_w = 14.5 * pitch
    y = y_back
    for name, row in ROWS:
        rh = row_h.get(name, 1.0) * pitch
        yc = y - rh / 2
        x = -total_w / 2
        for label, wu in row:
            wk = wu * pitch
            xc = x + wk / 2
            if label == "▲▼":                       # stacked half-height arrow keys
                for sgn, g in ((+1, "▲"), (-1, "▼")):
                    _add_key(face, legends, g, xc, yc + sgn * pitch * 0.245, wk - cap_gap,
                             pitch * 0.5 - cap_gap, top_z, key_h, 0.075)
            elif name == "mod" and label in ("◀", "▶"):
                _add_key(face, legends, label, xc, yc - pitch * 0.245, wk - cap_gap,
                         pitch * 0.5 - cap_gap, top_z, key_h, 0.075)
            elif label == "" and name == "fn":      # Touch ID / power key
                base_k = m.Prism(dimensions=[wk - cap_gap, rh - cap_gap, key_h],
                                 fill_color=KEY_COLOR, fill_opacity=1)
                base_k.move_to([xc, yc, top_z + key_h / 2])
                face.add(base_k)
            elif label == "" and name == "mod":     # space bar
                _add_key(face, legends, "", xc, yc, wk - cap_gap, rh - cap_gap, top_z, key_h, 0.07)
            elif label == "" and name == "home":    # lower part of the ISO return key
                _add_key(face, legends, "", xc, yc, wk - cap_gap, rh - cap_gap, top_z, key_h, 0.07)
            else:
                size = 0.07 if len(label.replace("\n", "")) <= 1 else (0.045 if name == "fn" else 0.05)
                _add_key(face, legends, label, xc, yc, wk - cap_gap, rh - cap_gap, top_z, key_h, size)
            x += wk
        y -= rh
    return face, legends


def _add_key(face, legends, label, xc, yc, kw, kh, top_z, key_h, size):
    cap = m.Prism(dimensions=[kw, kh, key_h], fill_color=KEY_COLOR, fill_opacity=1)
    cap.move_to([xc, yc, top_z + key_h / 2])
    face.add(cap)
    if label:
        t = m.Text(label, font="Helvetica Neue", font_size=24, color="#F2F2F4", weight="MEDIUM")
        if label in ("command", "option", "control", "esc"):
            t.scale_to_fit_height(size * 0.6)
        elif "\n" in label:
            t.scale_to_fit_height(size * 2.1)
        else:
            t.scale_to_fit_height(size)
        t.move_to([xc, yc, top_z + key_h + 0.002])
        t.set_shade_in_3d(False)
        legends.add(t)


# --------------------------------------------------------------------------- scene
class MacBookAir(m.ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=52 * m.DEGREES, theta=-90 * m.DEGREES, zoom=1.2, frame_center=[0, -0.9, 1.3])

        # ceiling light: a spot overhead, slightly toward the camera so the shadow falls behind
        self.add(m.SpotLight(location=np.array([0.0, -1.2, 10.0]), toward=m.ORIGIN, intensity=22.0,
                             radius=40.0, angle=m.PI / 4.2, softness=0.7, shadows=True))
        self.add(m.EnvironmentLight(intensity=1.1, shadows=False))
        self.add(m.AmbientLight(intensity=0.02))

        floor = m.Rectangle(width=400, height=400, fill_color="#020203", fill_opacity=1, stroke_width=0)
        floor.set_material(FLOOR).set_shade_in_3d(True)

        # --- base
        base = slab(W, D, BASE_T, 0, ALU_COLOR).set_material(ALU)
        deck = BASE_T + 0.002

        # keyboard recess (dark tray) and keys
        tray = m.RoundedRectangle(width=14.5 * 0.24 + 0.05, height=5.55 * 0.24 + 0.04, corner_radius=0.03,
                                  fill_color="#050506", fill_opacity=1, stroke_width=0)
        tray.move_to([0, D / 2 - 0.18 - (5.55 * 0.24) / 2, deck]).set_material(KEYMAT).set_shade_in_3d(True)
        caps, legends = build_keyboard(deck)
        caps.set_material(KEYMAT)

        # trackpad: flush with the deck, 130 x 80 mm
        tp_w, tp_h = 130 * K, 82 * K
        tp_y = D / 2 - 0.18 - 5.55 * 0.24 - 0.20 - tp_h / 2
        trackpad = m.RoundedRectangle(width=tp_w, height=tp_h, corner_radius=0.05,
                                      fill_color="#C4C6CA", fill_opacity=1,
                                      stroke_color="#8E9096", stroke_width=1.2)
        trackpad.move_to([0, tp_y, deck]).set_material(PAD).set_shade_in_3d(True)

        # --- lid
        lid_z0 = BASE_T + GAP
        lid_body = slab(W, D, LID_T, lid_z0, ALU_COLOR).set_material(ALU)
        under = lid_z0 - 0.0015
        glass = m.RoundedRectangle(width=W - 0.04, height=D - 0.04, corner_radius=0.09,
                                   fill_color=GLASS_COLOR, fill_opacity=1, stroke_width=0)
        glass.move_to([0, 0, under]).set_material(GLASS).set_shade_in_3d(True)

        # display: 2560x1664 -> 289 x 188 mm, top bezel ~6.5 mm (the lid's top is its -y edge)
        sw, sh = 289.0 * K, 188.0 * K
        top_edge = -D / 2 + 0.085
        screen_y = top_edge + sh / 2
        picture = m.ImageMobject(np.flipud(make_wallpaper()).copy())
        picture.scale_to_fit_width(sw)
        picture.move_to([0, screen_y, under - 0.0015])

        logo = m.Circle(radius=0.17, fill_color="#E8E9EC", fill_opacity=1, stroke_width=0)
        logo.move_to([0, 0, lid_z0 + LID_T + 0.002]).set_material(ALU).set_shade_in_3d(True)

        lid = m.VGroup(lid_body, glass, picture, logo)
        hinge = np.array([0, D / 2, lid_z0])

        # --- iPhone lying flat in front of the MacBook (146.7 x 71.5 x 7.8 mm, titanium)
        ph_w, ph_h, ph_t = 71.5 * K, 146.7 * K, 7.8 * K
        ph_y = -D / 2 - 0.30 - ph_h / 2
        phone_body = slab(ph_w, ph_h, ph_t, 0, "#B7B2A8", n=5.5, f=0.028, res=128)
        phone_body.set_material(m.Material(metallic=0.85, roughness=0.3))
        phone_glass = m.RoundedRectangle(width=ph_w - 0.03, height=ph_h - 0.03, corner_radius=0.1,
                                         fill_color="#030304", fill_opacity=1, stroke_width=0)
        phone_glass.move_to([0, 0, ph_t + 0.002]).set_material(GLASS).set_shade_in_3d(True)
        phone_pic = m.ImageMobject(make_phone_image())
        phone_pic.scale_to_fit_width(ph_w - 0.052)
        phone_pic.move_to([0, 0, ph_t + 0.004])
        phone = m.VGroup(phone_body, phone_glass, phone_pic)
        phone.shift([0, ph_y, 0])

        lid.rotate(-102 * m.DEGREES, axis=m.RIGHT, about_point=hinge)   # open from the first frame
        self.add(floor, base, tray, caps, legends, trackpad, lid, phone)
        self.wait(4)
