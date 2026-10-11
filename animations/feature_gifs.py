"""One short looping clip per LazyRemote feature (animations/specs.md), for README / store GIFs.

Each scene reuses the Mac, iPhone and D-pad builders from lazyremote_promo.py and stays under 3 s.
Render all of them as GIFs with ./make_feature_gifs.sh.
"""
import numpy as np

import lazyremote_promo as base
from lazyremote_promo import (ACCENT, BG, DB, DH, DL, DR, DT, DW, GRAY4, GRAY5, GREEN, MX, MY, PS, PX, PY,
                              SECONDARY, P, _img, arrow_up_icon, at_left, nebula, pbox, poster, ppoly, rrect,
                              tip_of, touch_dot, wallpaper, T)

import manimgx as m

K = 923 / 393                        # screenshot px per iOS pt
SLOT = (660, 209)                    # header slot for the docked remote button
LENS = (752, 209)                    # header Spotlight button


def magnifier_px(cx, cy, color=ACCENT, s=1.0):
    ring = m.Circle(radius=12 * PS * s, stroke_color=color, stroke_width=2.2 * s).move_to(P(cx - 4 * s, cy - 4 * s))
    return m.VGroup(ring, ppoly([(cx + 5 * s, cy + 5 * s), (cx + 14 * s, cy + 14 * s)], color, 5.5 * s))


def magnifier(center, r=0.035, color="#8E8E93"):
    return m.VGroup(m.Circle(radius=r, stroke_color=color, stroke_width=1.6),
                    m.Line([r * 0.7, -r * 0.7, 0], [r * 1.9, -r * 1.9, 0], stroke_color=color, stroke_width=1.6)
                    ).move_to(center)


def window(w, h, center, title=None, color="#1E1E21"):
    center = np.asarray(center, dtype=float)
    top = center[1] + h / 2
    win = rrect(w, h, 0.12, color).set_stroke("#3A3A3F", width=1.2).move_to(center)
    lights = m.VGroup(*[m.Circle(radius=0.045, fill_color=c, fill_opacity=1, stroke_width=0)
                        .move_to([center[0] - w / 2 + 0.2 + i * 0.15, top - 0.18, 0])
                        for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"])])
    g = m.VGroup(win, lights)
    if title:
        g.add(T(title, 0.07, "#B8B8BE", weight=m.BOLD).move_to([center[0], top - 0.18, 0]))
    return g


def folder_icon(center, label):
    c = np.asarray(center, dtype=float)
    tab = rrect(0.22, 0.1, 0.03, "#3E9BE6").move_to(c + [-0.12, 0.17, 0])
    back = rrect(0.52, 0.36, 0.04, "#3E9BE6").move_to(c + [0, 0.03, 0])
    front = rrect(0.52, 0.3, 0.04, "#6CBBF6").move_to(c + [0, -0.01, 0])
    lab = T(label, 0.055).next_to(back, m.DOWN, buff=0.1)
    return m.VGroup(tab, back, front, lab)


def movie_icon(center, label, seed=2):
    c = np.asarray(center, dtype=float)
    frame = rrect(0.54, 0.38, 0.03, "#F2F2F5").move_to(c)
    pic = _img(poster(seed, 240, 160)).stretch_to_fit_width(0.48).stretch_to_fit_height(0.32).move_to(c)
    lab = T(label, 0.055).next_to(frame, m.DOWN, buff=0.1)
    return m.Group(frame, pic, lab)


def hold_ring(point):
    return m.Arc(radius=0.24, start_angle=np.pi / 2, angle=-2 * np.pi, stroke_color=ACCENT,
                 stroke_width=5).move_to(point).set_z_index(9)


class Feature(base.LazyRemotePromo):
    title = ""
    sub = ""

    def construct(self):
        self.camera.background_color = BG
        self.build_mac()
        self.build_phone()
        self.scene()

    # ------------------------------------------------------------------ stage
    def stage(self, content=(), overlay=(), masked=False):
        """Everything already connected and on screen. `content` sits on the Mac's display under the menu bar;
        `masked` hides whatever of it strays off the display; `overlay` covers the menu bar (full screen apps)."""
        self.status_dot.set_fill(GREEN)
        self.status_text.become(at_left(T("MacBook Air", 24 * PS, SECONDARY), P(86, 209)))
        self.phone.remove(self.veil)
        self.lens = magnifier_px(*LENS)
        self.phone.add(self.lens)

        shadow, basem, lip, lid, wall = self.mac[:5]
        screen = m.Rectangle(width=DW, height=DH).move_to([MX, MY, 0])
        frame = m.Difference(lid, screen, fill_color="#0B0B0D", fill_opacity=1, stroke_width=0)
        outline = lid.copy().set_fill(opacity=0)
        self.wall = wall
        self.add(wall, *content)
        if masked:
            self.add(m.Difference(m.Rectangle(width=16, height=10), screen, fill_color=BG, fill_opacity=1,
                                  stroke_width=0))
        self.add(shadow, basem, lip, frame, outline, *self.mac[5:9], *overlay, self.mac[9], self.phone)

        wordmark = at_left(T("LazyRemote", 0.2, weight=m.BOLD), [-6.75, 3.62, 0])
        title = T(self.title, 0.2, weight=m.BOLD)
        sub = T(self.sub, 0.14, SECONDARY)
        self.add(wordmark, m.VGroup(title, sub).arrange(m.DOWN, buff=0.17).move_to([MX, -2.95, 0]))

    def put_cursor(self, point):
        self.cursor.shift(np.asarray(point) - tip_of(self.cursor))
        self.add(self.cursor)

    def notes(self, lines, title="Notes"):
        """A Notes window; returns it and the left edge / y of each text line."""
        w, h = 5.2, 3.1
        c = np.array([MX, MY - 0.1, 0])
        win = window(w, h, c, title)
        x0, y0 = c[0] - w / 2 + 0.35, c[1] + h / 2 - 0.7
        self.note_line = lambda i: np.array([x0, y0 - 0.34 * i, 0])
        texts = m.VGroup(*[at_left(T(s, 0.12 if i == 0 else 0.085, weight=m.BOLD if i == 0 else m.NORMAL),
                                   self.note_line(i)) for i, s in enumerate(lines)])
        return win, texts

    def typing_state(self, placeholder=None):
        """Phone with the text field focused and the keyboard up (as in the promo's type_and_send)."""
        y0 = self.kb_y0 = 1135
        scrim = rrect(3.0, 2000 * PS, 0.42, "#000000", 0.45).move_to([PX, PY, 0])
        kb = self.keyboard()
        self.field.become(pbox(48, y0, 520, y0 + 100, 47, GRAY5))
        self.placeholder = placeholder or at_left(T("Type to send…", 28 * PS, "#6E6E73"), P(86, y0 + 50))
        self.bksp.move_to(P(583, y0 + 52))
        self.ret.move_to(P(705, y0 + 52))
        self.send = m.VGroup(m.Circle(radius=49 * PS, fill_color=ACCENT, fill_opacity=1, stroke_width=0)
                             .move_to(P(827, y0 + 52)), arrow_up_icon(827, y0 + 52))
        self.phone.remove(self.fab)
        self.remove(self.fab)
        self.add(scrim, kb, self.field, self.placeholder, self.bksp, self.ret, self.send)

    # ------------------------------------------------------------------ gestures
    def zap(self, label, start, end, run_time=0.3, land=(), land_time=0.2):
        """A quick command chip over Bluetooth; `land` plays as it arrives."""
        chip_t = T(label, 0.11, weight=m.BOLD)
        chip = m.VGroup(rrect(chip_t.width + 0.32, 0.3, 0.15, ACCENT), chip_t).set_z_index(20).move_to(start)
        path = m.ArcBetweenPoints(np.asarray(start), np.asarray(end), angle=0.6)
        trail = m.TracedPath(chip.get_center, dissipating_time=0.2, stroke_color=ACCENT, stroke_width=5)
        self.add(trail.set_z_index(19), chip)
        self.play(m.MoveAlongPath(chip, path, rate_func=m.ease_in_out_sine), run_time=run_time)
        burst = m.Circle(radius=0.1, stroke_color=ACCENT, stroke_width=4).move_to(end).set_z_index(19)
        self.play(m.FadeOut(chip, scale=0.4), burst.animate.scale(3).set_stroke(opacity=0), *land, run_time=land_time)
        self.remove(trail, burst)

    def quick_tap(self, point, highlight=None, extra=()):
        dot = self.tap(point, highlight, run_time=0.08)
        self.release(dot, highlight, extra=extra, run_time=0.12)

    def drive(self, dots, pts_px, run_time, cursor_to=None, followers=(), extra=(), rate=m.ease_in_out_sine):
        """Fingers follow a path on the trackpad; the cursor (and anything dragged with it) follows with gain."""
        path = m.CubicBezier(*[P(*p) for p in pts_px])
        t = m.ValueTracker(0.0)
        d0 = path.get_start()
        for dot in dots:
            off = dot.get_center() - d0
            dot.add_updater(lambda d, off=off: d.move_to(path.point_from_proportion(t.get_value()) + off))
        movers = []
        if cursor_to is not None:
            c0 = tip_of(self.cursor)
            dd = (path.get_end() - d0)[:2]
            gain = np.divide((np.asarray(cursor_to) - c0)[:2], dd, out=np.zeros(2), where=np.abs(dd) > 1e-6)
            for mob in [self.cursor, *followers]:
                off = mob.get_center() - c0

                def follow(mob, off=off):
                    p = path.point_from_proportion(t.get_value())
                    mob.move_to(c0 + np.array([*((p - d0)[:2] * gain), 0]) + off)
                mob.add_updater(follow)
                movers.append(mob)
        self.play(t.animate.set_value(1.0), *extra, run_time=run_time, rate_func=rate)
        for mob in [*dots, *movers]:
            mob.clear_updaters()


# ====================================================================== trackpad
class TrackpadMove(Feature):
    title = "Trackpad"
    sub = "Move the cursor with one finger"

    def scene(self):
        self.stage(content=[self.app])
        self.put_cursor([MX + 2.2, MY - 1.3, 0])
        target = self.grid[1][0].get_center() + m.UP * 0.05
        self.wait(0.15)
        self.swipe([(700, 1250), (760, 820), (480, 560), (330, 470)], target, run_time=1.35)
        hover = m.SurroundingRectangle(self.grid[1][0], buff=0.03, corner_radius=0.04, stroke_color="#FFFFFF",
                                       stroke_width=2.5)
        self.play(m.Create(hover), run_time=0.25)
        self.wait(0.2)


class TapClick(Feature):
    title = "Tap to click"
    sub = "Double-tap and triple-tap work too"

    def scene(self):
        win, texts = self.notes(["Movie night", "Bring snacks for everyone", "Doors open at eight"])
        self.stage(content=[win, texts])
        line = texts[1]
        word = m.VGroup(*line[5:11])                     # "snacks"
        y, hgt = line.get_y(), 0.2

        def sel(x0, x1):
            r = rrect(x1 - x0 + 0.06, hgt, 0.03, ACCENT, 0.45).move_to([(x0 + x1) / 2, y, 0])
            return r
        w_sel = sel(word.get_left()[0], word.get_right()[0])
        l_sel = sel(line.get_left()[0], line.get_right()[0])
        self.add(w_sel.set_fill(opacity=0), l_sel.set_fill(opacity=0), texts)
        self.put_cursor(word.get_center() + m.DOWN * 0.02 + m.RIGHT * 0.02)

        tp = P(460, 900)
        labels = {n: T(s, 26 * PS, SECONDARY).move_to(P(460, 1120)) for n, s in
                  [(1, "Tap · click"), (2, "Double-tap · select word"), (3, "Triple-tap · select line")]}
        caret = m.Line(m.UP * 0.08, m.DOWN * 0.08, stroke_color=ACCENT, stroke_width=2.4).move_to(word[2].get_left())
        ring = m.Circle(radius=0.06, stroke_color="#FFFFFF", stroke_width=3).move_to(tip_of(self.cursor)).set_z_index(7)
        shown = None
        self.wait(0.15)
        for n, effect in [(1, [m.FadeIn(caret)]),
                          (2, [m.FadeOut(caret), w_sel.animate.set_fill(opacity=0.45)]),
                          (3, [w_sel.animate.set_fill(opacity=0), l_sel.animate.set_fill(opacity=0.45)])]:
            swap = [m.FadeIn(labels[n])] + ([m.FadeOut(shown)] if shown else [])
            shown = labels[n]
            for i in range(n):
                last = i == n - 1
                r = ring.copy()
                self.add(r)
                self.quick_tap(tp, extra=[*(swap if i == 0 else []),
                                          r.animate.scale(3).set_stroke(opacity=0),
                                          *(effect if last else [])])
                self.remove(r)
            self.wait(0.25 if n < 3 else 0.45)


class RightClick(Feature):
    title = "Right-click"
    sub = "Two-finger double-tap"

    def scene(self):
        icons = m.Group(folder_icon([DR - 0.6, DT - 0.75, 0], "Projects"),
                        folder_icon([DR - 0.6, DT - 1.65, 0], "Photos"),
                        movie_icon([DR - 0.6, DT - 2.55, 0], "Trailer.mov"))
        self.stage(content=[icons])
        target = icons[0][1].get_center() + m.LEFT * 0.05
        self.put_cursor(target)
        sel = rrect(0.72, 0.62, 0.08, "#FFFFFF", 0.18).move_to(icons[0][1]).shift(m.DOWN * 0.02)

        items = ["Open", "Open in New Tab", "Get Info", "Rename", "Compress “Projects”", "Copy", "Quick Look"]
        rows = m.VGroup(*[T(s, 0.065, "#EDEDF0") for s in items]).arrange(m.DOWN, buff=0.13, aligned_edge=m.LEFT)
        menu_bg = rrect(rows.width + 0.5, rows.height + 0.3, 0.1, "#2A2A2E", 0.97).set_stroke("#4A4A50", width=1)
        hi = rrect(menu_bg.width - 0.12, 0.17, 0.04, ACCENT)
        menu = m.VGroup(menu_bg, hi, rows)
        rows.move_to(menu_bg)
        hi.move_to([menu_bg.get_x(), rows[0].get_y(), 0])
        menu.set_z_index(5).move_to(tip_of(self.cursor), aligned_edge=m.UR).shift(m.LEFT * 0.02 + m.DOWN * 0.02)
        hi.set_fill(opacity=0)

        a, b = P(390, 950), P(560, 950)
        self.wait(0.15)
        for _ in range(2):
            d1, d2 = touch_dot().move_to(a), touch_dot().move_to(b)
            self.play(m.FadeIn(d1, scale=1.8), m.FadeIn(d2, scale=1.8), run_time=0.08)
            self.play(m.FadeOut(d1, scale=0.6), m.FadeOut(d2, scale=0.6), run_time=0.12)
        self.zap("Right-click", (a + b) / 2, tip_of(self.cursor), run_time=0.35,
                 land=[m.FadeIn(sel), m.FadeIn(menu, scale=0.94)], land_time=0.25)
        self.wait(0.35)
        self.play(hi.animate.set_fill(opacity=1), run_time=0.15)
        self.wait(0.9)


class Scroll(Feature):
    title = "Two-finger scroll"
    sub = "With smooth momentum"

    def scene(self):
        top = DT - 0.17
        page_bg = m.Rectangle(width=DW, height=DH - 0.17, fill_color="#F5F5F7", fill_opacity=1,
                              stroke_width=0).move_to([MX, MY - 0.085, 0])
        page = self.article(top - 0.55)
        bar = m.Rectangle(width=DW, height=0.65, fill_color="#E4E4E8", fill_opacity=1, stroke_width=0)
        bar.move_to([MX, DT - 0.325, 0])
        url = rrect(3.0, 0.26, 0.13, "#FFFFFF").move_to([MX, top - 0.24, 0])
        toolbar = m.VGroup(bar, url, T("lazyremote.app/blog", 0.07, "#55555A").move_to(url),
                           *[m.Circle(radius=0.045, fill_color=c, fill_opacity=1, stroke_width=0)
                             .move_to([DL + 0.2 + i * 0.15, url.get_y(), 0])
                             for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"])])
        knob = rrect(0.05, 0.9, 0.025, "#8E8E93", 0.8).move_to([DR - 0.07, top - 1.0, 0])
        self.stage(content=[page_bg, page, toolbar, knob], masked=True)
        self.put_cursor([MX + 1.5, MY - 0.4, 0])

        off = m.ValueTracker(0.0)
        y0, k0 = page.get_y(), knob.get_y()
        travel = page.height - (DH - 0.7)
        page.add_updater(lambda g: g.set_y(y0 + off.get_value()))
        knob.add_updater(lambda g: g.set_y(k0 - off.get_value() / travel * (DH - 1.7)))

        dots = [touch_dot().move_to(P(380, 1350)), touch_dot().move_to(P(560, 1350))]
        self.wait(0.15)
        self.play(*[m.FadeIn(d, scale=1.8) for d in dots], run_time=0.1)
        self.drive(dots, [(470, 1350), (470, 1150), (470, 950), (470, 780)], 0.35,
                   extra=[off.animate.set_value(1.2)], rate=m.linear)
        k = 3.2                                         # momentum: exponential decay, picking up the finger's speed
        self.play(*[m.FadeOut(d, scale=0.6) for d in dots], run_time=0.12)
        self.play(off.animate.set_value(1.2 + 2.6),
                  rate_func=lambda a: (1 - np.exp(-k * a)) / (1 - np.exp(-k)), run_time=1.6)
        self.wait(0.35)

    def article(self, top):
        col = 4.6
        x0 = MX - col / 2
        g = m.Group()
        y = top
        g.add(at_left(T("Your iPhone is now your Mac’s remote", 0.17, "#1C1C1E", weight=m.BOLD), [x0, y - 0.1, 0]))
        y -= 0.45
        rng = np.random.default_rng(4)
        for block in range(5):
            for _ in range(4):
                w = col * rng.uniform(0.7, 1.0)
                g.add(rrect(w, 0.07, 0.035, "#B8B8BE").move_to([x0 + w / 2, y, 0]))
                y -= 0.2
            y -= 0.12
            img = _img(poster(block + 2)).stretch_to_fit_width(col).stretch_to_fit_height(1.5)
            g.add(img.move_to([MX, y - 0.75, 0]))
            y -= 1.75
        return g


class Drag(Feature):
    title = "Drag"
    sub = "Long-press, then move"

    def scene(self):
        movie = movie_icon([DL + 1.3, DT - 1.2, 0], "Trailer.mov")
        folder = folder_icon([DR - 1.2, DB + 1.3, 0], "Movies")
        self.stage(content=[movie, folder])
        self.put_cursor(movie[0].get_center() + m.LEFT * 0.05)
        sel = rrect(0.68, 0.52, 0.08, "#FFFFFF", 0.18).move_to(movie[0])

        p0 = (300, 600)
        dot = touch_dot().move_to(P(*p0))
        ring = hold_ring(P(*p0))
        self.wait(0.15)
        self.play(m.FadeIn(dot, scale=1.8), run_time=0.1)
        self.play(m.Create(ring), run_time=0.45, rate_func=m.linear)
        ghost = m.Group(movie[0].copy(), movie[1].copy()).set_opacity(0.85)
        self.add(sel, ghost, self.cursor)
        self.play(m.FadeOut(ring, scale=1.3), m.FadeIn(sel), ghost.animate.scale(1.08), run_time=0.15)
        fhi = rrect(0.72, 0.56, 0.08, "#FFFFFF", 0.22).move_to(folder[1])
        self.drive([dot], [p0, (420, 900), (600, 1150), (680, 1350)], 1.0,
                   cursor_to=folder[1].get_center() + m.UP * 0.05, followers=[ghost],
                   extra=[m.Succession(m.Wait(0.75), m.FadeIn(fhi, run_time=0.25))])
        self.release(dot, run_time=0.25,
                     extra=[ghost.animate.scale(0.2).move_to(folder[1]).set_opacity(0),
                            m.FadeOut(movie), m.FadeOut(sel)])
        self.play(m.Indicate(folder[:3], scale_factor=1.12, color=None), m.FadeOut(fhi), run_time=0.35)
        self.wait(0.3)


class ThreeFingerSwipe(Feature):
    title = "Three-finger swipe"
    sub = "Switch desktops, open Mission Control"

    def scene(self):
        d1 = m.Group(self.app)
        wall2 = _img(nebula(seed=5)).stretch_to_fit_width(DW).stretch_to_fit_height(DH).move_to([MX + DW, MY, 0])
        w_a = window(3.6, 2.4, [MX - 1.4 + DW, MY + 0.2, 0], "Notes")
        w_b = window(3.2, 2.2, [MX + 1.6 + DW, MY - 0.5, 0], "Music", color="#24202A")
        w_a.add(*[rrect(2.8 * f, 0.07, 0.035, "#5A5A60").move_to(
            [MX - 1.4 + DW - 1.45 + 1.4 * f, MY + 0.75 - 0.25 * i, 0]) for i, f in enumerate([0.8, 1, 0.6, 0.9])])
        art = _img(poster(6, 240, 240)).scale_to_fit_width(1.1).move_to([MX + 1.6 + DW - 0.7, MY - 0.55, 0])
        w_b.add(*[rrect(1.2 * f, 0.07, 0.035, "#77707F").move_to([MX + 1.6 + DW + 0.55 + 0.6 * f - 0.6,
                                                                    MY - 0.25 - 0.25 * i, 0]) for i, f in enumerate([1, 0.7])])
        d2 = m.Group(wall2, w_a, w_b, art)
        self.stage(content=[d1, d2], masked=True)
        self.put_cursor([MX + 0.4, MY - 0.8, 0])

        xs = [300, 460, 620]
        dots = [touch_dot().move_to(P(x, 1050)) for x in xs]
        self.wait(0.12)
        self.play(*[m.FadeIn(d, scale=1.8) for d in dots], run_time=0.1)
        self.drive(dots, [(460, 1050), (360, 1050), (260, 1050), (160, 1050)], 0.55,
                   extra=[d1.animate.shift(m.LEFT * DW), d2.animate.shift(m.LEFT * DW),
                          self.wall.animate.shift(m.LEFT * DW)], rate=m.ease_in_out_cubic)
        self.play(*[m.FadeOut(d, scale=0.6) for d in dots], run_time=0.12)
        self.wait(0.3)

        # swipe up: Mission Control
        dots = [touch_dot().move_to(P(x, 1300)) for x in xs]
        self.play(*[m.FadeIn(d, scale=1.8) for d in dots], run_time=0.1)
        dim = m.Rectangle(width=DW, height=DH, fill_color="#000000", fill_opacity=0.35, stroke_width=0)
        dim.move_to([MX, MY, 0])
        spaces = m.Group()
        for i, (pic, label) in enumerate([(wallpaper(300, 190), "Desktop 1"), (nebula(300, 190, seed=5), "Desktop 2")]):
            th = _img(pic).stretch_to_fit_width(1.0).stretch_to_fit_height(0.62).move_to([MX - 0.65 + 1.3 * i, DT - 0.62, 0])
            box = m.SurroundingRectangle(th, buff=0.02, corner_radius=0.03,
                                         stroke_color="#FFFFFF" if i else "#FFFFFF", stroke_width=2 if i else 0)
            spaces.add(m.Group(th, box, T(label, 0.05, "#E5E5EA").next_to(th, m.DOWN, buff=0.07)))
        self.drive(dots, [(460, 1300), (460, 1150), (460, 1000), (460, 850)], 0.45,
                   extra=[m.FadeIn(dim), m.FadeIn(spaces, shift=m.DOWN * 0.3),
                          m.Group(w_a).animate.scale(0.7).move_to([MX - 1.7, MY - 0.3, 0]),
                          m.Group(w_b, art).animate.scale(0.7).move_to([MX + 1.7, MY - 0.3, 0])],
                   rate=m.ease_in_out_cubic)
        self.play(*[m.FadeOut(d, scale=0.6) for d in dots], run_time=0.12)
        self.wait(0.7)


# ====================================================================== floating remote
class FloatingRemote(Feature):
    title = "Floating remote"
    sub = "Place it anywhere, or dock it in the top bar"

    def scene(self):
        self.stage(content=[self.app])
        fab = self.fab
        bg = fab[1]
        glyph = fab[2]

        def stick(dot):
            def upd(f):
                f.shift(dot.get_center() - bg.get_center())
            return upd

        slot = P(*SLOT)
        target = m.DashedVMobject(m.Circle(radius=18 * K * PS, stroke_color=SECONDARY, stroke_width=2),
                                  num_dashes=14).move_to(slot)
        target_fill = m.Circle(radius=18 * K * PS, fill_color=ACCENT, fill_opacity=0.18, stroke_width=0).move_to(slot)

        self.wait(0.12)
        dot = touch_dot().move_to(self.fab_pt)
        self.play(m.FadeIn(dot, scale=1.8), run_time=0.1)
        fab.add_updater(stick(dot))
        self.drive([dot], [(838, 1290), (700, 1200), (420, 1020), (300, 960)], 0.55)
        fab.clear_updaters()
        self.release(dot, run_time=0.3,
                     extra=[fab.animate(rate_func=m.ease_out_back).shift(P(96, 960) - bg.get_center())])
        self.wait(0.12)

        dot = touch_dot().move_to(P(96, 960))
        self.play(m.FadeIn(dot, scale=1.8), m.FadeIn(target), run_time=0.12)
        fab.add_updater(stick(dot))
        self.drive([dot], [(96, 960), (200, 640), (520, 300), SLOT], 0.6,
                   extra=[m.Succession(m.Wait(0.35), m.AnimationGroup(
                       target.animate.set_stroke(ACCENT, width=3), m.FadeIn(target_fill), run_time=0.2))])
        fab.clear_updaters()
        self.release(dot, run_time=0.25,
                     extra=[fab[0].animate.set_opacity(0), bg.animate.set_opacity(0),
                            glyph.animate.scale(0.75).set_color(ACCENT).move_to(slot),
                            m.FadeOut(target), m.FadeOut(target_fill)])
        self.wait(0.7)


class DPadArrows(Feature):
    title = "Arrow keys"
    sub = "Slides, menus and videos · hold to repeat"

    def scene(self):
        names = ["Q4 Roadmap", "Highlights", "Growth", "Launch plan", "Next steps", "Thank you"]
        cols = [("#1E3A8A", "#0B1026"), ("#7C2D12", "#1C0A05"), ("#065F46", "#04130E"),
                ("#5B21B6", "#140829"), ("#9D174D", "#22050F"), ("#0F172A", "#020409")]
        self.slides = []
        for i, (name, (c1, c2)) in enumerate(zip(names, cols)):
            bgr = m.Rectangle(width=DW, height=DH, stroke_width=0).move_to([MX, MY, 0])
            bgr.set_fill([c1, c2], opacity=1).set_sheen_direction(m.DR)
            head = T(name, 0.32, weight=m.BOLD).move_to([MX, MY + 0.35, 0])
            line = rrect(1.2, 0.05, 0.025, "#FFFFFF", 0.6).next_to(head, m.DOWN, buff=0.3)
            num = T(f"{i + 1} / {len(names)}", 0.07, "#FFFFFF").move_to([DR - 0.4, DB + 0.25, 0])
            self.slides.append(m.VGroup(bgr, head, line, num))
        self.stage(overlay=[self.slides[0]])
        self.add(self.dpad_backdrop, self.dpad)
        self.cur = 0
        screen = np.array([MX + 1.6, MY, 0])

        self.wait(0.12)
        hl = self.hl["right"]
        self.quick_tap(self.key_pt["right"], hl)
        self.zap("→", self.key_pt["right"], screen, run_time=0.28, land=self.next_slide(), land_time=0.22)
        self.wait(0.2)

        # hold → repeats
        dot = self.tap(self.key_pt["right"], hl, run_time=0.08)
        ring = hold_ring(self.key_pt["right"])
        self.play(m.Create(ring), run_time=0.3, rate_func=m.linear)
        for _ in range(3):
            self.zap("→", self.key_pt["right"], screen, run_time=0.17, land=self.next_slide(), land_time=0.13)
        self.release(dot, hl, extra=[m.FadeOut(ring)], run_time=0.15)
        self.wait(0.3)

    def next_slide(self):
        old, new = self.slides[self.cur], self.slides[self.cur + 1]
        self.cur += 1
        # stays under the menu-bar notch and the D-pad (added later) by being inserted at the old slide's place
        idx = self.mobjects.index(old)
        self.mobjects.insert(idx + 1, new)
        new.set_opacity(0)
        return [old.animate.set_opacity(0), new.animate.set_opacity(1)]


class PlayPause(Feature):
    title = "Play / Pause"
    sub = "Right in the center of the D-pad"

    def scene(self):
        self.ft = m.ValueTracker(12 * 60 + 34)
        self.playing = False
        movie = self.build_player()
        self.stage(overlay=[movie])
        self.add(self.dpad_backdrop, self.dpad)
        screen = np.array([MX + 0.4, MY + 0.2, 0])
        hl = self.hl["mid"]
        self.wait(0.12)
        for playing in (True, False):
            self.quick_tap(self.key_pt["mid"], hl)
            flash = self.center_flash(playing)
            self.zap("Space", self.key_pt["mid"], screen, run_time=0.26, land_time=0.22,
                     land=[m.FadeIn(flash, scale=0.7), self.small_play.animate.set_opacity(0 if playing else 1),
                           self.small_pause.animate.set_opacity(1 if playing else 0),
                           self.player_title.animate.set_opacity(0 if playing else 1)])
            self.playing = playing
            self.play(flash.animate.scale(1.4).set_opacity(0), run_time=0.3)
            self.remove(flash)
            self.wait(0.55 if playing else 0.3)


# ====================================================================== keyboard
class TypeAndSend(Feature):
    title = "Keyboard"
    sub = "Type on your iPhone, send it to your Mac"

    def scene(self):
        win, texts = self.notes(["Movie night", "Bring snacks for everyone"])
        self.stage(content=[win, texts])
        self.typing_state()
        y0 = self.kb_y0
        mac_caret = m.Line(m.UP * 0.08, m.DOWN * 0.08, stroke_color=ACCENT, stroke_width=2.4)
        mac_caret.move_to(self.note_line(2) + m.LEFT * 0.02)
        self.add(mac_caret)

        phrase = "popcorn is ready"
        caret = m.Line(P(86, y0 + 28), P(86, y0 + 72), stroke_color=ACCENT, stroke_width=2.4)
        self.remove(self.placeholder)
        self.add(caret)
        finger = touch_dot()
        draft = None
        self.wait(0.1)
        for i, ch in enumerate(phrase):
            key = self.keys[ch]
            new = at_left(T(phrase[:i + 1], 28 * PS), P(86, y0 + 50))
            if draft is not None:
                self.remove(draft)
            self.add(new)
            draft = new
            self.play(finger.animate.move_to(key.get_center()) if i else m.FadeIn(finger.move_to(key), scale=1.5),
                      key.animate(rate_func=m.there_and_back).set_fill("#A4A4AA"),
                      caret.animate.move_to(draft.get_right() + m.RIGHT * 0.03), run_time=0.075)
        self.play(m.FadeOut(finger), run_time=0.1)
        self.quick_tap(self.send.get_center())
        mac_text = at_left(T(phrase, 0.085), self.note_line(2))
        self.zap(f"“{phrase}”", self.send.get_center(), mac_text.get_center(), run_time=0.4,
                 land=[m.FadeOut(draft), m.FadeOut(caret)], land_time=0.15)
        self.play(m.AddTextLetterByLetter(mac_text, time_per_char=0.02),
                  mac_caret.animate.move_to(mac_text.get_right() + m.RIGHT * 0.03), run_time=0.3)
        self.wait(0.4)


class AnyLanguage(Feature):
    title = "Any language"
    sub = "Emoji included"

    def scene(self):
        win, texts = self.notes(["Hello, world"])
        self.stage(content=[win, texts])
        self.typing_state()
        y0 = self.kb_y0
        self.wait(0.1)
        for i, s in enumerate(["Merhaba! 👋", "こんにちは 🌸", "¡Olé! café ☕"]):
            draft = at_left(T(s, 28 * PS), P(86, y0 + 50))
            self.play(m.FadeOut(self.placeholder) if i == 0 else m.Wait(0), m.FadeIn(draft, shift=m.UP * 0.05),
                      run_time=0.15)
            self.quick_tap(self.send.get_center())
            mac_text = at_left(T(s, 0.085), self.note_line(i + 1))
            self.zap(s, self.send.get_center(), mac_text.get_center(), run_time=0.28, land_time=0.15,
                     land=[m.FadeOut(draft), m.FadeIn(mac_text, shift=m.UP * 0.05)])
        self.wait(0.35)


class BackspaceEnter(Feature):
    title = "Backspace & Enter"
    sub = "Hold Backspace to delete quickly"

    def scene(self):
        full = "Doors open at eight tonihgt"
        keep = "Doors open at eight"
        win, texts = self.notes(["Movie night", "Bring snacks for everyone"])
        self.stage(content=[win, texts])
        y = self.note_line(2)
        n = m.ValueTracker(len(full))
        cache = {}

        def line():
            k = int(round(n.get_value()))
            if k not in cache:
                cache[k] = at_left(T(full[:k], 0.085), y)
            return cache[k].copy()
        text = m.always_redraw(line)
        caret = m.always_redraw(lambda: m.Line(m.UP * 0.08, m.DOWN * 0.08, stroke_color=ACCENT, stroke_width=2.4)
                                .move_to([line().get_right()[0] + 0.03, y[1], 0]))
        self.add(text, caret)

        key_bg = self.bksp[0]
        dot_pt = key_bg.get_center()
        stream = m.ArcBetweenPoints(dot_pt, np.array([DR - 0.6, y[1], 0]), angle=0.6)
        sparks = [m.Dot(radius=0.05, color=ACCENT).set_z_index(20).set_opacity(0) for _ in range(9)]

        def spark(s):
            return m.UpdateFromAlphaFunc(s, lambda mob, a: mob.move_to(stream.point_from_proportion(a))
                                         .set_opacity(np.sin(np.pi * a)))
        self.wait(0.12)
        dot = self.tap(dot_pt, run_time=0.08)
        ring = hold_ring(dot_pt)
        self.play(key_bg.animate.set_fill("#5A5A5E"), m.Create(ring), run_time=0.25, rate_func=m.linear)
        # held: the Mac's key repeat speeds up
        self.play(n.animate.set_value(len(keep)), m.LaggedStart(*[spark(s) for s in sparks], lag_ratio=0.12),
                  rate_func=lambda a: a ** 1.8, run_time=1.0)
        self.remove(*sparks)
        self.release(dot, extra=[key_bg.animate.set_fill(GRAY5), m.FadeOut(ring)], run_time=0.15)
        text.clear_updaters()
        caret.clear_updaters()

        self.quick_tap(self.ret.get_center())
        self.zap("Return", self.ret.get_center(), caret.get_center() + m.RIGHT * 0.1, run_time=0.3,
                 land=[caret.animate.move_to(self.note_line(3) + m.RIGHT * 0.0)], land_time=0.2)
        self.wait(0.45)


# ====================================================================== spotlight
class Spotlight(Feature):
    title = "Spotlight"
    sub = "Open it from your iPhone, then type your search"

    def scene(self):
        self.stage(content=[self.app])
        self.put_cursor([MX + 2.2, MY - 1.3, 0])
        cx, cy = MX, MY + 1.0
        w = 4.2
        bar = rrect(w, 0.46, 0.2, "#2A2A2F", 0.97).set_stroke("#55555B", width=1).move_to([cx, cy, 0])
        icon = magnifier([cx - w / 2 + 0.25, cy, 0], r=0.05, color="#AEAEB2")
        ph = at_left(T("Spotlight Search", 0.1, "#7C7C82"), [cx - w / 2 + 0.45, cy, 0])
        spot = m.VGroup(bar, icon, ph).set_z_index(5)

        # phone: tap the header magnifier
        self.wait(0.1)
        self.quick_tap(P(*LENS))
        y0 = 1135
        lens = magnifier_px(98, y0 + 50, "#6E6E73", 0.9)
        phph = m.VGroup(lens, at_left(T("Spotlight Search", 28 * PS, "#6E6E73"), P(122, y0 + 50)))
        self.zap("⌘ Space", P(*LENS), bar.get_center(), run_time=0.3, land_time=0.2,
                 land=[m.FadeIn(spot, scale=0.96)])
        self.typing_state(placeholder=phph)
        self.wait(0.1)

        word = "safari"
        finger = touch_dot()
        draft = None
        for i, ch in enumerate(word):
            new = at_left(T(word[:i + 1], 28 * PS), P(86, y0 + 50))
            self.remove(*([draft] if draft else [phph]))
            self.add(new)
            draft = new
            key = self.keys[ch]
            self.play(finger.animate.move_to(key.get_center()) if i else m.FadeIn(finger.move_to(key), scale=1.5),
                      key.animate(rate_func=m.there_and_back).set_fill("#A4A4AA"), run_time=0.08)
        self.play(m.FadeOut(finger), run_time=0.08)
        self.quick_tap(self.send.get_center())

        typed = at_left(T("safari", 0.1), ph.get_left())
        big = rrect(w, 1.72, 0.2, "#2A2A2F", 0.97).set_stroke("#55555B", width=1)
        big.move_to(bar.get_top(), aligned_edge=m.UP)
        rows = m.VGroup()
        hit_y = cy - 0.45
        hit = rrect(w - 0.2, 0.36, 0.08, ACCENT).move_to([cx, hit_y, 0])
        safari = m.VGroup(m.Circle(radius=0.12, fill_color="#1B8BFF", fill_opacity=1, stroke_color="#FFFFFF",
                                   stroke_width=1.5),
                          m.Polygon([0, 0.09, 0], [0.025, 0, 0], [0, -0.09, 0], [-0.025, 0, 0], fill_color="#FF3B30",
                                    fill_opacity=1, stroke_width=0).rotate(-0.7)).move_to([cx - w / 2 + 0.32, hit_y, 0])
        rows.add(hit, safari, at_left(T("Safari", 0.09, weight=m.BOLD), [cx - w / 2 + 0.55, hit_y, 0]),
                 T("Application", 0.07, "#D6E6FF").move_to([cx + w / 2 - 0.25, hit_y, 0], aligned_edge=m.RIGHT))
        for j, (name, kind) in enumerate([("Safari Downloads", "Folder"), ("safari-trip.pdf", "PDF Document")]):
            ry = hit_y - 0.4 * (j + 1)
            rows.add(rrect(0.2, 0.2, 0.04, "#3E9BE6" if j == 0 else "#E5E5EA").move_to([cx - w / 2 + 0.32, ry, 0]),
                     at_left(T(name, 0.08, "#E5E5EA"), [cx - w / 2 + 0.55, ry, 0]),
                     T(kind, 0.07, "#8E8E93").move_to([cx + w / 2 - 0.25, ry, 0], aligned_edge=m.RIGHT))
        rows.set_z_index(6)
        big.set_z_index(5)
        self.zap("“safari”", self.send.get_center(), typed.get_center(), run_time=0.3, land_time=0.15,
                 land=[m.FadeOut(draft), m.FadeOut(ph), m.FadeIn(typed.set_z_index(6))])
        self.play(m.Transform(bar, big), m.FadeIn(rows, shift=m.DOWN * 0.08), run_time=0.25)
        self.wait(0.5)
