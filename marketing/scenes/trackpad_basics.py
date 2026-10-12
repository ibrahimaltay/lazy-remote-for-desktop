import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *


class TrackpadBasics(m.Scene):
    """Move the cursor, tap / double-tap to click, two-finger double-tap to right-click."""

    def construct(self):
        stage(self)
        mac, phone = MacFrame(), PhoneFrame()
        win = cinema_window(mac)
        screen = remote_screen(phone)
        tile = win.tiles[1]
        home = mac.pt(860, 600)
        cur = cursor(home)
        self.add(mac, win, cur, mac.front, phone, screen, phone.front)

        # one finger moves the cursor up-left onto "Night Train"
        f0, f1 = phone.pt(250, 560), phone.pt(140, 330)
        f = finger(f0)
        target = tile.art.get_center() + P(0.25, -0.1)
        self.play(*touch(self, f), run_time=0.12)
        trail(self, f)
        self.play(f.animate.move_to(f1), cur.animate.shift(target - home), run_time=0.85, rate_func=m.ease_in_out_sine)
        self.play(m.FadeOut(f), run_time=0.08)

        # tap: the tile is selected; double-tap: it is clicked twice
        ring = select_ring(mac, tile)
        tap(self, f1)
        self.add(ring)
        self.wait(0.15)
        tap(self, f1, 2, 0.12)
        self.play(m.Group(tile.art, ring).animate.scale(1.05), run_time=0.25, rate_func=m.there_and_back)

        # two-finger double-tap: context menu at the cursor
        f2c = phone.pt(PH_W / 2, 430)
        for _ in range(2):
            f2 = finger(f2c, 2).scale(1.15)
            self.add(f2)
            for d in f2:
                ripple(self, d.get_center())
            self.play(f2.animate.scale(0.85).set_opacity(0),
                      run_time=0.12, rate_func=m.rush_from)
            self.remove(f2)
        menu = context_menu(mac, ["Play", "Add to Watchlist", "Share…"], target + P(0.05, -0.05))
        self.play(m.FadeIn(menu, scale=0.96), run_time=0.15)
        self.wait(0.7)

        # back to the start for the loop
        f = finger(f1)
        self.play(m.FadeOut(menu), m.FadeOut(ring), *touch(self, f), run_time=0.15)
        trail(self, f)
        self.play(f.animate.move_to(f0), cur.animate.move_to(cursor(home).get_center()),
                  run_time=0.7, rate_func=m.ease_in_out_sine)
        self.play(m.FadeOut(f), run_time=0.1)
        self.wait(0.3)                                       # let the finger trail fade before the loop
