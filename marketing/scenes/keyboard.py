import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

KEYS = "popcron"          # autocapitalized "P"; the typo is fixed by autocorrect on space
FIXED = "Popcorn "


class Keyboard(m.Scene):
    """Live keyboard: each key lands in Mac Notes at once, autocorrect syncs, Send presses Return and clears
    the phone field, tapping outside closes the keyboard. Remote button shown docked (a real state)."""

    def construct(self):
        stage(self)
        mac, phone = MacFrame("Notes"), PhoneFrame()
        notes = notes_window(mac)
        caret = mac_caret(mac, notes.line(0))
        screen = remote_screen(phone, docked=True, live=True)
        self.add(mac, notes, caret, mac.front, phone, screen, phone.front)

        # tap the field: keyboard rises, Send fades in, remote button dims
        field = screen.bar[0].get_center()
        tap(self, field)
        kb, bar = open_live_keyboard(self, phone, screen)
        bottom = PH_H - KB_H
        draft = live_typed_field(phone, "", bottom)
        self.add(draft)

        line = m.Group()

        def show(text):
            nonlocal draft, line
            new_draft = live_typed_field(phone, text, bottom)
            new_line = rich_text(text, 14, scale=MS).move_to(notes.line(0), aligned_edge=m.LEFT) if text.strip() else m.Group()
            self.remove(draft, line)
            self.add(new_draft, new_line)
            draft, line = new_draft, new_line
            end = new_line.get_right() if text.strip() else notes.line(0)
            caret.move_to(end + P(0.03 + (0.045 if text.endswith(" ") else 0), 0))

        # every key press shows up on the Mac at the same moment
        typed = ""
        for ch in KEYS:
            tap(self, kb.keys[ch].get_center(), t=0.09)
            typed += ch.upper() if not typed else ch
            show(typed)
            self.wait(0.03)

        # space: autocorrect swaps the word on the phone, and the Mac follows (delete + insert)
        tap(self, kb.keys[" "].get_center(), t=0.09)
        show(FIXED)
        self.wait(0.35)

        # Send: Return on the Mac, phone field clears, keyboard stays open
        tap(self, bar.send.get_center())
        self.remove(draft)
        draft = live_typed_field(phone, "", bottom)
        self.add(draft)
        self.play(caret.animate.move_to(notes.line(1)), run_time=0.12)
        self.wait(0.35)

        # tap outside: keyboard closes, remote button back to full opacity
        tap(self, phone.pt(*screen.pad.center_pt))
        self.remove(draft)
        bar.add(bar.placeholder)                         # unfocused, empty: just the placeholder
        close_live_keyboard(self, phone, screen, kb, bar)
        self.wait(0.3)

        # back to the start (loop)
        self.play(m.FadeOut(line), caret.animate.move_to(notes.line(0)), run_time=0.25)
