import numpy as np
import manimgx as m

W, D = 4.0, 2.8
BASE_T, LID_T = 0.15, 0.08
SILVER = "#D5D8DC"
DARK = "#0B0C0E"

ALU = m.Material(metallic=0.9, roughness=0.4)
KEY = m.Material(metallic=0.0, roughness=0.55, reflectance=0.4)
GLASS = m.Material(metallic=0.0, roughness=0.08, reflectance=0.9)
PAD = m.Material(metallic=0.6, roughness=0.5)
FLOOR = m.Material(metallic=0.0, roughness=0.85, reflectance=0.3)


def _sp(x, p):
    return np.sign(x) * np.abs(x) ** p


def slab(w, d, h, zc, color, n=18.0, res=128):
    """Rounded (squircle) slab: side wall + top + bottom, centered at (0, 0, zc)."""
    def ring(t):
        c, s = np.cos(t), np.sin(t)
        return (w / 2) * _sp(c, 2 / n), (d / 2) * _sp(s, 2 / n)

    def wall(t, z):
        x, y = ring(t)
        return np.array([x, y, zc - h / 2 + z * h])

    ts = np.linspace(0, m.TAU, 240, endpoint=False)

    def cap(zz):
        pts = [np.array([*ring(t), zz]) for t in ts]
        return m.Polygon(*pts, fill_color=color, fill_opacity=1, stroke_width=0)

    parts = [
        m.Surface(wall, u_range=(0, m.TAU), v_range=(0, 1), resolution=(res, 2)),
        cap(zc + h / 2),
        cap(zc - h / 2),
    ]
    g = m.VGroup(*parts)
    for part in parts:
        part.set_fill(color, opacity=1)
        part.set_stroke(width=0)
        if isinstance(part, m.Polygon):
            part.set_shade_in_3d(True)
    return g


class MacBookReal(m.ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=72 * m.DEGREES, theta=-85 * m.DEGREES, zoom=1.1)

        # lighting: key sun with shadows, soft studio fill, a little ambient
        self.add(m.SunLight(location=5 * m.LEFT + 4 * m.DOWN + 8 * m.OUT,
                            intensity=2.2, shadows=True))
        self.add(m.EnvironmentLight(intensity=1.3, shadows=False))
        self.add(m.AmbientLight(intensity=0.08))

        floor = m.Rectangle(width=300, height=300, fill_color="#5A5D64",
                            fill_opacity=1, stroke_width=0)
        floor.set_material(FLOOR).set_shade_in_3d(True)

        base = slab(W, D, BASE_T, BASE_T / 2, SILVER)
        base.set_material(ALU)
        top = BASE_T + 0.004

        well = m.Rectangle(width=3.5, height=1.2, fill_color=DARK, fill_opacity=1, stroke_width=0)
        well.move_to([0, 0.55, top]).set_material(KEY).set_shade_in_3d(True)
        keys = m.VGroup()
        rows, cols = 5, 14
        kw, kh, gap = 0.2, 0.18, 0.04
        for r in range(rows):
            for c in range(cols):
                k = m.Prism(dimensions=[kw, kh, 0.02], fill_color="#1A1C20", fill_opacity=1)
                x = (c - (cols - 1) / 2) * (kw + gap)
                y = 0.55 + ((rows - 1) / 2 - r) * (kh + gap)
                k.move_to([x, y, top + 0.012])
                keys.add(k)
        keys.set_material(KEY)
        trackpad = m.RoundedRectangle(width=1.5, height=0.85, corner_radius=0.06,
                                      fill_color="#A9ADB3", fill_opacity=1, stroke_width=0)
        trackpad.move_to([0, -0.75, top]).set_material(PAD).set_shade_in_3d(True)

        lid_z = BASE_T + 0.05 + LID_T / 2
        lid_body = slab(W, D, LID_T, lid_z, SILVER)
        lid_body.set_material(ALU)
        bezel = m.RoundedRectangle(width=W - 0.16, height=D - 0.16, corner_radius=0.08,
                                   fill_color="#050506", fill_opacity=1, stroke_width=0)
        bezel.move_to([0, 0, lid_z - LID_T / 2 - 0.003])
        screen = m.RoundedRectangle(width=W - 0.4, height=D - 0.4, corner_radius=0.04,
                                    fill_color="#050506", fill_opacity=1, stroke_width=0)
        screen.move_to([0, 0, lid_z - LID_T / 2 - 0.006])
        bezel.set_material(GLASS).set_shade_in_3d(True)
        screen.set_shade_in_3d(False)  # unlit so it glows
        logo = m.Circle(radius=0.2, fill_color="#F2F3F5", fill_opacity=1, stroke_width=0)
        logo.move_to([0, 0, lid_z + LID_T / 2 + 0.004]).set_material(ALU).set_shade_in_3d(True)
        lid = m.VGroup(lid_body, bezel, screen, logo)
        hinge = np.array([0, D / 2, BASE_T + 0.05])

        self.add(floor, base, well, keys, trackpad, lid)
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(1)
        self.play(m.Rotate(lid, -105 * m.DEGREES, axis=m.RIGHT, about_point=hinge),
                  run_time=2.5)
        self.play(screen.animate.set_fill("#2F6BFF"), run_time=1)
        self.wait(2)
