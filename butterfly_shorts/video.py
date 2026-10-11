"""The full ~86 s video: Part 1 (scenes.py) + Part 2 (scenes2.py) on one timeline."""

import scenes as s1
import scenes2 as s2
from common import draw_background, clamp01

END = s2.VIDEO_END


class Video:
    def __init__(self):
        self.A, self.B, self.C, self.D = s1.SceneA(), s1.SceneB(), s1.SceneC(), s1.SceneD()
        self.E, self.F, self.G = s2.SceneE(), s2.SceneF(), s2.SceneG()
        self.Hs, self.I, self.J = s2.SceneH(), s2.SceneI(), s2.SceneJ(self.A)
        self.windows = [
            (self.A, -1, s1.A_END), (self.B, s1.B_START, s1.B_END), (self.C, s1.C_START, s1.C_END),
            (self.D, s1.D_START, s1.D_END + 0.3),
            (self.E, s2.E_START, s2.E_END), (self.F, s2.F_START, s2.F_END), (self.G, s2.G_START, s2.G_END),
            (self.Hs, s2.H_START, s2.H_END), (self.I, s2.I_START, s2.I_END), (self.J, s2.J_START, END + 1),
        ]

    def draw(self, c, t):
        draw_background(c)
        for scene, t0, t1 in self.windows:
            if t < t0 or t > t1:
                continue
            a = min(clamp01((t - t0) / 0.3), clamp01((t1 - t) / 0.3))
            if a >= 0.999:
                scene.draw(c, t)
            else:
                c.saveLayerAlpha(None, int(255 * a))
                scene.draw(c, t)
                c.restore()
