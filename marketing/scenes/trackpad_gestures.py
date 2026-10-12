import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

PAGE = blog_page(w=680)


def desktop_one(mac):
    """Desktop 1: browser on the left, a folder on the desktop; .tracker scrolls the page."""
    x0, y0, x1, y1 = 40, 50, 720, 690
    win = browser_window(mac, x0, y0, x1, y1)
    tracker = m.ValueTracker(0)
    view = scroll_view(PAGE, y1 - y0 - 46, tracker, (x1 - x0 - 2) * MS, mac.pt((x0 + x1) / 2, (y0 + 44 + y1) / 2 + 1))
    folder = folder_icon(mac, "Movies", (900, 230))
    g = m.Group(win, view, folder)
    g.tracker, g.folder = tracker, folder
    return g


class TrackpadGestures(m.Scene):
    """Two-finger scroll with momentum, long-press drag, three-finger swipe between desktops."""

    def construct(self):
        stage(self)
        mac, phone = MacFrame("Safari"), PhoneFrame()
        d1 = desktop_one(mac)
        screen = remote_screen(phone)
        cur = cursor(mac.pt(560, 420))
        self.add(mac, d1, cur, mac.front, phone, screen, phone.front)

        # two fingers push up: the page scrolls, then glides on
        f = finger(phone.pt(PH_W / 2, 560), 2)
        self.play(*touch(self, f), run_time=0.1)
        trail(self, f)
        self.play(f.animate.shift(P(0, 1.5)), d1.tracker.animate.set_value(420), run_time=0.45, rate_func=m.linear)
        self.play(m.FadeOut(f), d1.tracker.animate.set_value(1150), run_time=0.75, rate_func=m.rush_from)
        d1[1].clear_updaters()

        # move to the folder, long-press to pick it up, drag it down
        fa, fb = phone.pt(170, 420), phone.pt(250, 300)
        f = finger(fa)
        grip = d1.folder.get_center() + P(0.12, 0.05)
        self.play(*touch(self, f), run_time=0.08)
        trail(self, f)
        self.play(f.animate.move_to(fb), cur.animate.move_to(cursor(grip).get_center()), run_time=0.45, rate_func=m.ease_in_out_sine)
        lift = rrect(d1.folder.width + 16 * MS, d1.folder.height + 10 * MS, 8 * MS, WHITE, 0.16).move_to(d1.folder)
        self.wait(0.3)                                       # held: TrackpadTuning dragHoldSeconds
        ripple(self, fb)                                     # long-press registers
        self.play(m.FadeIn(lift), run_time=0.1)
        carried = m.Group(lift, d1.folder)
        fc = phone.pt(250, 540)
        shift = mac.pt(900, 520) - mac.pt(900, 230)
        self.play(f.animate.move_to(fc), carried.animate.shift(shift), cur.animate.shift(shift),
                  run_time=0.6, rate_func=m.ease_in_out_sine)
        self.play(m.FadeOut(f), m.FadeOut(lift), run_time=0.1)

        # three fingers swipe left: the next desktop slides in; swipe right: back
        w = MAC_W * MS
        d2 = m.Group(m.ImageMobject(landscape((40, 120, 140), (10, 40, 60), seed=9, w=640, h=416, sun=(0.7, 0.3)))
                     .stretch_to_fit_width(w).stretch_to_fit_height(MAC_H * MS).move_to(P(*MAC_C)),
                     notes_window(mac)).shift(P(w, 0))
        self.add(d2, phone, screen, phone.front)              # phone stays above the sliding desktop
        d1_all = m.Group(mac.wall, d1, cur)
        f3 = finger(phone.pt(260, 430), 3)
        self.play(*touch(self, f3), run_time=0.08)
        trail(self, f3)
        self.play(f3.animate.shift(P(-1.1, 0)), d1_all.animate.shift(P(-w, 0)), d2.animate.shift(P(-w, 0)),
                  run_time=0.55, rate_func=m.ease_in_out_cubic)
        self.play(m.FadeOut(f3), run_time=0.08)
        self.wait(0.25)

        # back to desktop 1, as it was at the start (loop)
        fresh = desktop_one(mac)
        fresh_cur = cursor(mac.pt(560, 420))
        self.remove(d1, cur)
        m.Group(fresh, fresh_cur).shift(P(-w, 0))
        back = m.Group(mac.wall, fresh, fresh_cur)
        self.add(fresh, fresh_cur, phone, screen, phone.front)
        f3 = finger(phone.pt(140, 430), 3)
        self.play(*touch(self, f3), run_time=0.08)
        trail(self, f3)
        self.play(f3.animate.shift(P(1.1, 0)), back.animate.shift(P(w, 0)), d2.animate.shift(P(w, 0)),
                  run_time=0.55, rate_func=m.ease_in_out_cubic)
        self.play(m.FadeOut(f3), run_time=0.08)
        self.wait(0.3)                                       # let the finger trail fade before the loop
