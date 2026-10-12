import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from common import *


class FloatingRemote(m.Scene):
    """Tap the floating remote, seek with the D-pad arrows, pause and play with the media key, close."""

    def construct(self):
        stage(self)
        mac, phone = MacFrame(), PhoneFrame()
        player = video_player(mac)
        bar = player.progress(0.39, "0:42:10")
        glyph = player.glyph(True)
        screen = remote_screen(phone)
        self.add(mac, player, bar, glyph, mac.front, phone, screen, phone.front)

        # tap the floating button: the D-pad opens
        tap(self, phone.pt(*FLOAT_HOME))
        pad = dpad_overlay(phone)
        keys = pad.keys
        pressable(*keys.values())
        self.play(m.FadeIn(pad, scale=0.92), run_time=0.2, rate_func=m.ease_out_cubic)   # easeOut 0.2, scale 0.92 -> 1

        def key(name, mac_change, hold=0.18):
            at = keys[name].get_center()
            f = finger(at)
            self.play(*touch(self, f), press(keys[name]), *mac_change, run_time=0.12)
            self.wait(hold)
            self.play(m.FadeOut(f), press(keys[name], False), run_time=0.12)

        # right arrow seeks forward, left back
        bar2 = player.progress(0.45, "0:48:40")
        key("right", [m.FadeOut(bar), m.FadeIn(bar2)])
        bar3 = player.progress(0.39, "0:42:10")
        key("left", [m.FadeOut(bar2), m.FadeIn(bar3)])

        # play / pause media key: the movie pauses, then plays again
        big = m.Group(circle(0.9, "#000000", 0.55, at=player.center),
                      symbol("pause.fill", 34, WHITE, scale=MS, at=player.center))
        paused = player.glyph(False)
        key("playpause", [m.FadeOut(glyph), m.FadeIn(paused), m.FadeIn(big, scale=1.2)], hold=0.3)
        key("playpause", [m.FadeOut(paused), m.FadeIn(glyph), m.FadeOut(big)], hold=0.05)

        # close
        tap(self, keys["close"].get_center())
        self.play(m.FadeOut(pad), run_time=0.2)

        self.wait(0.2)                                       # let the last ripple fade before the loop
