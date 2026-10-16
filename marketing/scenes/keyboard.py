import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

KEYS = "popcron"          # autocapitalized "P"; the typo is fixed by autocorrect on space
FIXED = "Popcorn "


class Keyboard(m.Scene):
    """Keyboard tool (floating_keyboard): tap the docked Keyboard, each key lands in Mac Notes at once, autocorrect
    syncs, Send presses Return and clears the field, Close ends it. Drag / dock and landscape not shown."""

    def construct(self):
        stage(self)
        mac, phone = MacFrame("Notes"), PhoneFrame()
        notes = notes_window(mac)
        caret = mac_caret(mac, notes.line(0))
        screen = remote_screen(phone)
        self.add(mac, notes, caret, mac.front, phone, screen, phone.front)

        # tap the docked Keyboard tool: scrim, compose row and keyboard come up, both tools hide
        tap(self, phone.pt(*KB_DOCK))
        kb, sc, row = open_keyboard_overlay(self, phone, screen)
        draft = compose_text(phone, "")
        self.add(draft)

        line = m.Group()

        def show(text):
            nonlocal draft, line, row
            new_draft = compose_text(phone, text)
            new_line = rich_text(text, 14, scale=MS).move_to(notes.line(0), aligned_edge=m.LEFT) if text.strip() else m.Group()
            new_row = compose_row(phone, can_send=bool(text))
            self.remove(draft, line, row)
            self.add(new_row, new_draft, new_line)
            draft, line, row = new_draft, new_line, new_row
            end = new_line.get_right() if text.strip() else notes.line(0)
            caret.move_to(end + P(0.03 + (0.045 if text.endswith(" ") else 0), 0))

        # every key press shows up on the Mac at the same moment; Send turns blue with the first letter
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

        # Send: Return on the Mac, field clears (Send grey again), keyboard stays open
        tap(self, row.send.get_center())
        empty_draft, grey_row = compose_text(phone, ""), compose_row(phone)
        self.remove(draft, row)
        self.add(grey_row, empty_draft)
        draft, row = empty_draft, grey_row
        self.play(caret.animate.move_to(notes.line(1)), run_time=0.12)
        self.wait(0.3)

        # Close: overlay goes away, the tools come back
        tap(self, row.close.get_center())
        self.remove(draft)
        close_keyboard_overlay(self, screen, kb, sc, row)
        self.wait(0.2)

        # back to the start (loop)
        self.play(m.FadeOut(line), caret.animate.move_to(notes.line(0)), run_time=0.25)
