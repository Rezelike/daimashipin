"""Full-film timeline. The 12.4 s opening is used as-is; later scenes follow it back to back.

Every scene after the opening has:
    LEN                      its length in seconds
    draw(canvas, theme, u)   u = seconds since the scene started
"""
from opening import END as OPEN_END
from theme import FORMAT

if FORMAT == 'wide':
    from opening_wide import OpeningWide as Opening
else:
    from opening import Opening


def scene_classes():
    from pendulum_scene import PendulumScene
    from coin_scene import CoinScene
    from weather_scene import WeatherScene
    from lorenz_scene import LorenzScene
    return [PendulumScene, CoinScene, WeatherScene, LorenzScene]


class Film:
    def __init__(self, only=None):
        self.opening = Opening()
        self.parts = []                     # (start time, scene)
        t = OPEN_END
        for cls in scene_classes():
            scene = cls() if (only is None or cls.__name__ in only) else None
            self.parts.append((t, scene))
            t += cls.LEN
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
        t0, scene = self.part_at(min(t, self.end - 1e-6))
        if scene is None:
            th.draw_background(c)
            return
        scene.draw(c, th, t - t0)
