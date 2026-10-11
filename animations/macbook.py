import numpy as np
import manimgx as m

W, D = 4.0, 2.8          # width, depth
BASE_T, LID_T = 0.15, 0.08
SILVER = "#C9CCD1"
DARK = "#16181C"


class MacBook(m.ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=72 * m.DEGREES, theta=-85 * m.DEGREES)

        # base
        base = m.Prism(dimensions=[W, D, BASE_T], fill_color=SILVER, fill_opacity=1)
        base.move_to([0, 0, BASE_T / 2])
        top = BASE_T + 0.004

        # keyboard well + keys
        well = m.Rectangle(width=3.5, height=1.2, fill_color=DARK, fill_opacity=1, stroke_width=0)
        well.move_to([0, 0.55, top])
        keys = m.VGroup()
        rows, cols = 5, 14
        kw, kh, gap = 0.2, 0.18, 0.04
        for r in range(rows):
            for c in range(cols):
                k = m.Rectangle(width=kw, height=kh, fill_color="#2B2E35",
                                fill_opacity=1, stroke_width=0)
                x = (c - (cols - 1) / 2) * (kw + gap)
                y = 0.55 + ((rows - 1) / 2 - r) * (kh + gap)
                k.move_to([x, y, top + 0.004])
                keys.add(k)
        trackpad = m.RoundedRectangle(width=1.5, height=0.85, corner_radius=0.06,
                                      fill_color="#B4B8BE", fill_opacity=1, stroke_width=0)
        trackpad.move_to([0, -0.75, top])

        # lid (modelled closed, lying on the base; hinge on the back edge)
        lid_z = BASE_T + 0.05 + LID_T / 2
        lid_body = m.Prism(dimensions=[W, D, LID_T], fill_color=SILVER, fill_opacity=1)
        lid_body.move_to([0, 0, lid_z])
        screen = m.Rectangle(width=W - 0.3, height=D - 0.3, fill_color="#000000",
                             fill_opacity=1, stroke_width=0)
        screen.move_to([0, 0, lid_z - LID_T / 2 - 0.004])   # underside of lid
        logo = m.Circle(radius=0.2, fill_color="#F2F3F5", fill_opacity=1, stroke_width=0)
        logo.move_to([0, 0, lid_z + LID_T / 2 + 0.004])
        lid = m.VGroup(lid_body, screen, logo)
        hinge = np.array([0, D / 2, BASE_T + 0.05])

        laptop = m.VGroup(base, well, keys, trackpad, lid)
        self.add(laptop)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(1)
        self.play(m.Rotate(lid, -105 * m.DEGREES, axis=m.RIGHT, about_point=hinge),
                  run_time=2.5)
        self.play(screen.animate.set_fill("#2F6BFF"), run_time=1)
        self.wait(2)
