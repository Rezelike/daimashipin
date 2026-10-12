"""Full-film timeline. The 12.4 s opening is used as-is; later scenes follow it back to back.

Every scene after the opening has:
    LEN                      its length in seconds
    draw(canvas, theme, u)   u = seconds since the scene started
"""
from opening import Opening, END as OPEN_END
from pendulum_scene import PendulumScene


class Film:
    def __init__(self):
        self.opening = Opening()
        self.parts = []                     # (start time, scene)
        t = OPEN_END
        for scene in (PendulumScene(),):
            self.parts.append((t, scene))
            t += scene.LEN
        self.end = t

    def part_at(self, t):
        for t0, scene in reversed(self.parts):
            if t >= t0:
                return t0, scene
        return None

    def draw(self, c, th, t):
        if t < OPEN_END:
            self.opening.draw(c, th, t)
            return
        t0, scene = self.part_at(t)
        scene.draw(c, th, t - t0)
