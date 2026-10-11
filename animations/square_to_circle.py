import manimgx as m


class SquareToCircle(m.Scene):
    def construct(self):
        square = m.Square(side_length=3, color=m.BLUE, fill_opacity=0.5)
        circle = m.Circle(radius=1.5, color=m.RED, fill_opacity=0.5)
        self.play(m.Create(square))
        self.play(m.Transform(square, circle), run_time=2)
        self.wait(0.5)
