"""Four still scenes (trackpad, D-pad, keyboard, search) reusing marketing/scenes/common.py; rendered to 4K frames by
render-stills.sh. Store artwork must not show Apple names or trade dress, so this file swaps in a generic laptop (no
notch), a phone without the Dynamic Island, windows without traffic lights, and non-Apple search results. The device
name comes from LAZYREMOTE_DEVICE_NAME, which render-stills.sh sets."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "marketing", "scenes"))
import common
from common import *

RESULTS = [("Photos from Lisbon", "#F2C94C"), ("Phone bill.pdf", "#34C759"), ("Photography notes.txt", "#4A90E2")]
assert all(common.match_ranges(t, "ph") for t, _ in RESULTS)   # every row highlights the typed "ph"


def plain_window(mac, x0, y0, x1, y1, title=None, fill="#1E1E20"):
    """common.mac_window without the macOS traffic lights."""
    g = m.Group(mac.rect(x0, y0, x1, y1, 12, fill, stroke="#4A4A4E", stroke_width=1))
    if title:
        g.add(mac.text(title, 12, SECONDARY, semibold=True).move_to(mac.pt((x0 + x1) / 2, y0 + 20)))
    return g


common.mac_window = plain_window   # cinema_window and notes_window look it up in common at call time


class Laptop(MacFrame):
    def menu_bar(self, app):
        g = super().menu_bar(app)
        g.remove(g[7])   # the notch: bar, six menu titles, then notch, clock, icon
        return g


class Phone(PhoneFrame):
    def status_bar(self):
        g = super().status_bar()
        g.remove(g[0])   # the Dynamic Island
        return g


class StillRemote(m.Scene):
    def construct(self):
        stage(self)
        mac, phone = Laptop(), Phone()
        player = video_player(mac)
        player.remove(*player[2:5])   # its own traffic lights: frame, poster, then the three dots
        screen = remote_screen(phone)
        self.add(mac, player, player.progress(0.39, "0:42:10"), player.glyph(True), mac.front, phone, screen, phone.front)
        self.remove(screen.tools)
        self.add(dpad_overlay(phone))
        self.wait(0.4)


class StillKeyboard(m.Scene):
    def construct(self):
        stage(self)
        mac, phone = Laptop("Notes"), Phone()
        notes = notes_window(mac)
        screen = remote_screen(phone)
        self.add(mac, notes, mac.front, phone, screen, phone.front)
        self.remove(screen.tools)
        text = "Popcorn "
        self.add(tool_scrim(phone), compose_row(phone, True), keyboard(phone), compose_text(phone, text),
                 rich_text(text, 14, scale=MS).move_to(notes.line(0), aligned_edge=m.LEFT))
        self.wait(0.4)


class StillSpotlight(m.Scene):
    def construct(self):
        stage(self)
        mac, phone = Laptop(), Phone()
        win = cinema_window(mac)
        screen = remote_screen(phone)
        self.add(mac, win, mac.front, phone, screen, phone.front)
        titles = [t for t, _ in RESULTS]
        kb = keyboard(phone, "go").set_z_index(3)
        self.add(mac_spotlight(mac, "ph", RESULTS), blurred_screen(phone), spotlight_scrim(phone),
                 phone.status_bar(), spotlight_pill(phone, "ph"), spotlight_results(phone, "ph", titles), kb)
        self.wait(0.4)


class StillTrackpad(m.Scene):
    def construct(self):
        stage(self)
        mac, phone = Laptop(), Phone()
        self.add(mac, mac.front, phone, remote_screen(phone), phone.front)
        self.wait(0.4)
