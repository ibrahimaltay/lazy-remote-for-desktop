import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

QUERY = "safari"


class Spotlight(m.Scene):
    """Header magnifier opens Spotlight on the Mac and the phone's search pill; type, "go" sends it plus Enter."""

    def construct(self):
        stage(self)
        mac, phone = MacFrame(), PhoneFrame()
        win = cinema_window(mac)
        cur = cursor(mac.pt(860, 600))
        screen = remote_screen(phone)
        self.add(mac, win, cur, mac.front, phone, screen, phone.front)

        # magnifier: Cmd+Space on the Mac; the phone blurs and dims, pill and keyboard appear (RootView 0.2 s ease-out)
        tap(self, screen.header.magnifier)
        sp = mac_spotlight(mac)
        blur, dim, bar = blurred_screen(phone), spotlight_scrim(phone), phone.status_bar()
        pill = spotlight_pill(phone)
        kb = keyboard(phone, "go").set_z_index(3)       # above the overlay, below touch rings
        kb.shift(P(0, -KB_H * S))
        self.add(kb)
        self.play(m.FadeIn(sp, scale=0.97), m.FadeIn(blur), m.FadeIn(dim), m.FadeIn(bar), m.FadeIn(pill),
                  m.FadeOut(screen.button), kb.animate.shift(P(0, KB_H * S)),
                  run_time=0.25, rate_func=m.ease_out_cubic)

        # type the query in the pill
        for i in range(1, len(QUERY) + 1):
            tap(self, kb.keys[QUERY[i - 1]].get_center(), t=0.09)
            new = spotlight_pill(phone, QUERY[:i])
            self.remove(pill)
            self.add(new)
            pill = new

        # go: the overlay closes; on the Mac the text lands in Spotlight, then Enter opens the top hit
        tap(self, kb.keys["return"].get_center(), t=0.12)
        found = mac_spotlight(mac, QUERY, [("Safari", "#1E88E5"), ("Safari Downloads", "#6E6E73")])
        self.play(m.FadeOut(sp), m.FadeIn(found), m.FadeOut(blur), m.FadeOut(dim), m.FadeOut(pill),
                  m.FadeIn(screen.button), kb.animate.shift(P(0, -KB_H * S)),
                  run_time=0.25, rate_func=m.ease_out_cubic)
        self.remove(kb, bar)
        self.wait(0.15)
        safari = browser_window(mac, 140, 60, 960, 640, "lazyremote.app")
        page = m.ImageMobject(blog_page(w=816, rows=534)).stretch_to_fit_width(818 * MS).stretch_to_fit_height(534 * MS)
        safari.add(page.move_to(mac.pt(550, 60 + 44 + 267)))
        self.play(m.FadeOut(found), m.FadeIn(safari, scale=0.96), run_time=0.25)
        self.wait(0.7)

        # back to the start (loop)
        self.play(m.FadeOut(safari), run_time=0.25)
