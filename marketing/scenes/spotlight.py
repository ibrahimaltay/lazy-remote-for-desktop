import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

# What the Mac's Spotlight lists after each letter (titles from docs/features/spotlight_results_mirror/design.md);
# the phone's card mirrors the same titles in the same order. Mac icon colors are illustrative only.
APPS = {"Preview.app": "#4A90E2", "Pages.app": "#F5A623", "Raspberry Pi Imager.app": "#C51A4A", "Phone.app": "#34C759",
        "Photos.app": "#F2C94C", "Podcasts.app": "#9B51E0", "Passwords.app": "#8E8E93", "Photo Booth.app": "#D0021B"}
STEPS = [("p", list(APPS)),
         ("ph", ["Photos.app", "Phone.app", "Photo Booth.app"]),
         ("pho", ["Photos.app", "Phone.app", "Photo Booth.app"]),
         ("phot", ["Photos.app", "Photo Booth.app"])]


def photos_window(mac):
    """The opened top hit: a dark window with a grid of photo thumbnails."""
    x0, y0 = 140, 60
    g = mac_window(mac, x0, y0, 960, 640, "Photos")
    for i in range(12):
        top, bot = MOVIES[i % len(MOVIES)][1:]
        art = m.ImageMobject(landscape(top, bot, seed=20 + i, sun=(0.25 + 0.1 * (i % 5), 0.38), w=304, h=240))
        cx, cy = x0 + 15 + 95 + (i % 4) * 200, y0 + 50 + 75 + (i // 4) * 165
        g.add(art.stretch_to_fit_width(190 * MS).stretch_to_fit_height(150 * MS).move_to(mac.pt(cx, cy)))
    return g


class Spotlight(m.Scene):
    """Magnifier opens Spotlight on the Mac and the phone's pill; each letter lands in the Mac's field at once and the
    Mac's results show on the phone; "go" opens the top hit."""

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

        # each letter: pill and Mac field update together (tag 12), then both lists show the Mac's results
        card = None
        for query, titles in STEPS:
            tap(self, kb.keys[query[-1]].get_center(), t=0.09)
            new_pill, new_sp = spotlight_pill(phone, query), mac_spotlight(mac, query, [(t, APPS[t]) for t in titles])
            new_card = spotlight_results(phone, query, titles)
            self.remove(pill, sp, *([card] if card else []))
            self.add(new_pill, new_sp, new_card)
            pill, sp, card = new_pill, new_sp, new_card
            self.wait(0.16)
        self.wait(0.35)

        # go: Enter on the Mac opens the top hit; the overlay closes
        tap(self, kb.keys["return"].get_center(), t=0.12)
        self.play(m.FadeOut(sp), m.FadeOut(blur), m.FadeOut(dim), m.FadeOut(pill), m.FadeOut(card),
                  m.FadeIn(screen.button), kb.animate.shift(P(0, -KB_H * S)),
                  run_time=0.25, rate_func=m.ease_out_cubic)
        self.remove(kb, bar)
        photos = photos_window(mac)
        self.play(m.FadeIn(photos, scale=0.96), run_time=0.25)
        self.wait(0.6)

        # back to the start (loop)
        self.play(m.FadeOut(photos), run_time=0.25)
