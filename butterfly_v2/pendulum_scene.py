"""12.4-24.4 s: two double pendulums released 0.001° apart, drawn as a long exposure.

Physics: ../butterfly_shorts/pendulum.py (equal arms and masses, RK4, step 1/2400 s).
The only difference between the two runs is the starting angle of the upper arm.
Like a real long exposure, slow parts of the path leave more ink than fast ones.
"""
import math
import os
import sys

import numpy as np
import skia

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'butterfly_shorts'))
import pendulum as pd  # noqa: E402

import film_common as fc  # noqa: E402
from theme import paint, clamp01, smooth, ease_out, ease_in_out, lerp  # noqa: E402

LEN = 12.0
START = (135.0, 135.0)          # upper / lower arm, degrees from hanging straight down
ANGLE = 0.001
RATE = 240                      # simulation samples per second (4 per video frame)

# ---------------------------------------------------------------- local timeline (seconds into the scene)
U_DRAW = (0.25, 1.15)           # dial draws on, arms extend
U_RELEASE = 1.5
U_FIRST = 0.6                   # 起点相同。
U_SUB = (1.0, 7.4)              # 两次放手，角度只差 0.001°
U_SECOND = 8.4                  # 终点无关。
U_DEV = (10.2, 10.9)            # arms and bobs fade - only the exposure is left
SIM_LEN = LEN - U_RELEASE + 0.1

# ---------------------------------------------------------------- geometry
S = 195                         # px per metre (each arm is 1 m)
PIVOT = np.array([540.0, 1000.0])
REACH = 2 * pd.L * S
TAIL = int(0.55 * RATE)


class Run:
    def __init__(self, upper_deg):
        st = pd.simulate(upper_deg, START[1], SIM_LEN, fps=RATE, substeps=10)
        p1, p2 = pd.bob_positions(st)
        self.m2 = p2                                  # metres, for the HUD
        self.p1 = PIVOT + p1 * S
        self.p2 = PIVOT + p2 * S
        v = np.linalg.norm(np.diff(self.p2, axis=0), axis=1) * RATE
        self.v = np.concatenate([v[:1], v])           # px/s of the lower bob
        self.n = len(self.p2)

    def at(self, s):
        """Interpolated (upper, lower) bob position at fractional sample s."""
        s = min(max(s, 0.0), self.n - 1.001)
        i = int(s)
        f = s - i
        return (self.p1[i] + (self.p1[i + 1] - self.p1[i]) * f,
                self.p2[i] + (self.p2[i + 1] - self.p2[i]) * f)


class PendulumScene:
    LEN = LEN

    def __init__(self):
        self.runs = [Run(START[0]), Run(START[0] + ANGLE)]
        gap = np.linalg.norm(self.runs[0].m2 - self.runs[1].m2, axis=1) * 100           # cm, lower bobs
        self.sep = np.maximum.accumulate(gap)          # largest gap so far, same idea as the opening's 最大偏差

    # ------------------------------------------------------------ clock
    @staticmethod
    def sample(u):
        return max(0.0, (u - U_RELEASE) * RATE)

    # ------------------------------------------------------------ dial
    def draw_dial(self, c, th, u, alpha):
        k = ease_in_out((u - U_DRAW[0]) / (U_DRAW[1] - U_DRAW[0]))
        if k <= 0:
            return
        x, y = PIVOT
        ring = skia.Path()
        ring.addCircle(x, y, REACH + 34)
        p = paint(th.hair, alpha * 0.32, stroke=1.2)
        if k < 0.999:
            p.setPathEffect(skia.TrimPathEffect.Make(0, k, skia.TrimPathEffect.Mode.kNormal))
        c.save()
        c.rotate(-90, x, y)                              # start drawing from the top
        c.drawPath(ring, p)
        c.restore()
        inner = paint(th.hair, alpha * 0.16 * k, stroke=1)
        inner.setPathEffect(skia.DashPathEffect.Make([4, 9], 0))
        c.drawCircle(x, y, pd.L * S, inner)
        a2 = alpha * smooth((u - (U_DRAW[0] + 0.5)) / 0.5)
        for j in range(12):                              # one dot every 30°, like the table diamonds
            ang = math.radians(j * 30)
            c.drawCircle(x + (REACH + 54) * math.sin(ang), y - (REACH + 54) * math.cos(ang), 2.2,
                         paint(th.hair, a2 * 0.45))

    # ------------------------------------------------------------ exposure
    @staticmethod
    def density(v):
        """Ink per unit length ~ 1 / speed, as on a real long-exposure photograph."""
        return np.clip(1.0 / (v / 420.0 + 0.55), 0.22, 1.6)

    def draw_exposure(self, c, th, s, alpha, develop=0.0):
        """develop: 0 -> 1 at the end, the exposure darkens like a print coming up in the tray."""
        e = int(s)
        if e < 2:
            return
        step = 3
        blend = None if th.glow else skia.BlendMode.kMultiply
        gain = 0.62 * (1 + 0.45 * develop)
        for k, run in enumerate(self.runs):
            rgb = th.a if k == 0 else th.b
            dens = self.density(run.v)
            pts = run.p2
            for j0 in range(0, e, step):
                j1 = min(j0 + step, e)
                a = alpha * gain * float(dens[j0:j1 + 1].mean())
                seg = skia.Path()
                seg.moveTo(*pts[j0])
                for j in range(j0 + 1, j1 + 1):
                    seg.lineTo(*pts[j])
                pp = paint(rgb, min(a, 255), stroke=2.0 + 0.4 * develop, blend=blend)
                pp.setStrokeCap(skia.Paint.kButt_Cap)
                c.drawPath(seg, pp)
            # a stronger, fading tail of the last ~0.5 s (gone once the rigs fade)
            start = max(0, e - TAIL)
            for j0 in range(start, e, 6):
                j1 = min(j0 + 6, e)
                seg = skia.Path()
                seg.moveTo(*pts[j0])
                for j in range(j0 + 1, j1 + 1):
                    seg.lineTo(*pts[j])
                fade = 1 - (e - j1) / TAIL
                c.drawPath(seg, paint(rgb, alpha * 0.8 * fade * fade * (1 - develop), stroke=2.8, blend=blend))

    # ------------------------------------------------------------ the pendulums themselves
    def draw_rigs(self, c, th, u, s, alpha):
        if alpha <= 0:
            return
        grow = ease_out((u - (U_DRAW[0] + 0.35)) / 0.6)
        if grow <= 0:
            return
        x, y = PIVOT
        for k, run in enumerate(self.runs):
            p1, p2 = run.at(s)
            p1 = PIVOT + (p1 - PIVOT) * grow
            p2 = PIVOT + (p2 - PIVOT) * grow
            arm = paint(th.ink, alpha * (0.8 if k == 0 else 0.55), stroke=2.0 if k == 0 else 1.4)
            c.drawLine(x, y, p1[0], p1[1], arm)
            c.drawLine(p1[0], p1[1], p2[0], p2[1], arm)
        pop = ease_out((u - (U_DRAW[0] + 0.7)) / 0.5)
        for k, run in enumerate(self.runs):
            p1, p2 = run.at(s)
            p1 = PIVOT + (p1 - PIVOT) * grow
            p2 = PIVOT + (p2 - PIVOT) * grow
            if k == 0:
                c.drawCircle(p1[0], p1[1], 10 * pop, paint(th.a, alpha * 0.92))
                c.drawCircle(p2[0], p2[1], 17 * pop, paint(th.a, alpha * 0.92))
            else:
                if pop > 0.05:
                    c.drawCircle(p1[0], p1[1], 10 * pop + 2.5, paint(th.b, alpha, stroke=1.6))
                    c.drawCircle(p2[0], p2[1], 17 * pop + 2.5, paint(th.b, alpha, stroke=1.8))
        c.drawCircle(x, y, 6.5, paint(th.ink, alpha))
        c.drawCircle(x, y, 12, paint(th.ink, alpha * 0.35, stroke=1))

    # ------------------------------------------------------------ frame
    def draw(self, c, th, u):
        th.draw_background(c)
        s = self.sample(u)
        # a very slow push-in, so the still parts don't feel frozen
        z = lerp(1.0, 1.045, ease_in_out(u / LEN))
        c.save()
        c.translate(PIVOT[0], PIVOT[1])
        c.scale(z, z)
        c.translate(-PIVOT[0], -PIVOT[1])
        self.draw_dial(c, th, u, 255)
        self.draw_exposure(c, th, s, 255, develop=smooth((u - U_DEV[0]) / 1.0))
        self.draw_rigs(c, th, u, s, 255 * (1 - smooth((u - U_DEV[0]) / (U_DEV[1] - U_DEV[0]))))
        c.restore()
        # text
        fc.caption(c, th, '起点相同。', u, U_FIRST, LEN + 1, y=185)
        fc.caption(c, th, '终点无关。', u, U_SECOND, LEN + 1, y=275)
        a_sub = 255 * min(smooth((u - U_SUB[0]) / 0.8), 1 - smooth((u - (U_SUB[1] - 0.6)) / 0.6))
        if a_sub > 0:
            th.text(c, '两次放手，角度只差 0.001°', 540, 1590, 32, th.soft, alpha=a_sub, spacing=0.3)
        a_hud = 255 * smooth((u - 1.0) / 0.5) * (1 - smooth((u - U_DEV[0]) / 0.6))
        i = min(int(s), len(self.sep) - 1)
        fc.hud(c, th, a_hud, '时间', f'{s / RATE:5.2f} s', '最大偏差', fc.fmt_cm(float(self.sep[i])))
        fc.legend(c, th, a_hud)
        fc.dip(c, th, u, LEN)


if __name__ == '__main__':
    sc = PendulumScene()
    for sec in (2, 3, 4, 4.5, 5, 6, 7, 8, 9):
        i = int(sec * RATE)
        print(f'{sec:4.1f}s after release: largest gap so far {sc.sep[i]:8.3f} cm')
