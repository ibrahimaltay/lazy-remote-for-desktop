import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

QUERY = "safari"


class Spotlight(m.Scene):
    """Header magnifier opens Spotlight on the Mac (Cmd+Space) and focuses the field; type, send, Enter opens it."""

    def construct(self):
        stage(self)
        mac, phone = MacFrame(), PhoneFrame()
        win = cinema_window(mac)
        cur = cursor(mac.pt(860, 600))
        screen = remote_screen(phone)
        self.add(mac, win, cur, mac.front, phone, screen, phone.front)

        # magnifier: Spotlight opens on the Mac, the phone's field focuses with the Spotlight prompt
        tap(self, screen.header.magnifier)
        sp = mac_spotlight(mac)
        self.play(m.FadeIn(sp, scale=0.97), run_time=0.15)
        kb, bar = open_keyboard(self, phone, screen, spotlight=True, run_time=0.28)
        bottom = PH_H - KB_H
        self.wait(0.3)

        # type the query in the phone's field
        ready = input_bar(phone, True, bottom, can_send=True)
        ready.remove(*ready[1:2])
        draft = None
        for i in range(1, len(QUERY) + 1):
            new = typed_field(phone, QUERY[:i], bottom)
            if i == 1:
                self.remove(bar)
                self.add(ready)
                bar = ready
            if draft:
                self.remove(draft)
            self.add(new)
            draft = new
            self.wait(0.09)

        # send: the keyboard closes; the query lands in Spotlight with results
        tap(self, bar.send.get_center())
        self.remove(draft)
        close_keyboard(self, phone, screen, kb, bar, run_time=0.25)
        found = mac_spotlight(mac, QUERY, [("Safari", "#1E88E5"), ("Safari Downloads", "#6E6E73")])
        self.play(m.FadeOut(sp), m.FadeIn(found), run_time=0.15)
        self.wait(0.6)

        # Enter: Spotlight opens the top hit
        tap(self, screen.bar.enter.get_center())
        safari = browser_window(mac, 140, 60, 960, 640, "lazyremote.app")
        page = m.ImageMobject(blog_page(w=816, rows=534)).stretch_to_fit_width(818 * MS).stretch_to_fit_height(534 * MS)
        safari.add(page.move_to(mac.pt(550, 60 + 44 + 267)))
        self.play(m.FadeOut(found), m.FadeIn(safari, scale=0.96), run_time=0.25)
        self.wait(0.7)

        # back to the start (loop)
        self.play(m.FadeOut(safari), run_time=0.25)
