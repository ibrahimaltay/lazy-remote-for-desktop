import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *

MSG = "Hola 你好 👋"


class Keyboard(m.Scene):
    """Type in the TextInputBar (any language, emoji) and send; hold backspace to delete on the Mac; Enter."""

    def construct(self):
        stage(self)
        mac, phone = MacFrame("Notes"), PhoneFrame()
        notes = notes_window(mac)
        caret = mac_caret(mac, notes.line(0))
        screen = remote_screen(phone)
        self.add(mac, notes, caret, mac.front, phone, screen, phone.front)

        # tap the field: keyboard rises, scrim dims the trackpad, send button appears
        tap(self, phone.pt(110, IDLE_BAR_BOTTOM - INPUT_H / 2))
        kb, bar = open_keyboard(self, phone, screen)
        bottom = PH_H - KB_H

        # type the draft; send turns accent once there is text
        draft = typed_field(phone, "", bottom)
        self.add(draft)
        ready = input_bar(phone, True, bottom, can_send=True)
        ready.remove(*ready[1:2])                       # no placeholder once typing
        for i in range(1, len(MSG) + 1):
            if MSG[i - 1] == " ":
                continue
            new = typed_field(phone, MSG[:i], bottom)
            if i == 1:
                self.remove(bar)
                self.add(ready)
                bar = ready
            self.remove(draft)
            self.add(new)
            draft = new
            self.wait(0.1)

        # send: the keyboard closes, the text lands on the Mac
        tap(self, bar.send.get_center())
        self.remove(draft)
        close_keyboard(self, phone, screen, kb, bar, run_time=0.25)
        line = rich_text(MSG, 14, scale=MS).move_to(notes.line(0), aligned_edge=m.LEFT)
        self.play(m.FadeIn(line), caret.animate.move_to(line.get_right() + P(0.03, 0)), run_time=0.15)
        self.wait(0.45)

        # hold backspace: deletes on the Mac, repeating
        back = screen.bar.backspace
        pressable(back)
        f = finger(back.get_center())
        self.play(*touch(self, f), press(back), run_time=0.1)
        # TextInputBar: one backspace now, repeats after 450 ms
        for n, pause in ((len(MSG) - 1, 0.4), (len(MSG) - 2, 0.07), (len(MSG) - 3, 0.07), (len(MSG) - 4, 0.2)):
            short = rich_text(MSG[:n], 14, scale=MS).move_to(notes.line(0), aligned_edge=m.LEFT)
            self.remove(line)
            self.add(short)
            line = short
            caret.move_to(short.get_right() + P(0.03, 0))
            self.wait(pause)
        self.play(m.FadeOut(f), press(back, False), run_time=0.1)

        # Enter: new line on the Mac
        tap(self, screen.bar.enter.get_center())
        self.play(caret.animate.move_to(notes.line(1)), run_time=0.12)
        self.wait(0.7)

        # back to the start (loop)
        self.play(m.FadeOut(line), caret.animate.move_to(notes.line(0)), run_time=0.25)
