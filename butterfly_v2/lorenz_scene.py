"""42.4-60.4 s: two runs of the Lorenz equations draw the butterfly, then it slowly turns and fades.

First run starts at x = 0.506127, second at x = 0.506 (Lorenz's rounding); y, z identical.
Like the pendulum's long exposure, slow parts of the path leave more ink.
"""
import math

import numpy as np
import skia

import film_common as fc
import lorenz as lz
from theme import paint, clamp01, smooth, ease_out, ease_in_out, lerp

LEN = 18.0
T_END = 28.0                    # Lorenz time drawn by the end of the drawing phase
U_DRAW = (0.35, 11.0)
U_TITLE = 4.6                   # 蝴蝶效应
U_TURN = (10.6, 17.6)           # slow turn about the vertical axis
PHI0, TURN_DEG = -30.0, -65.0     # view angle while drawing, then how far it turns
U_FADE = (14.8, 17.4)           # the attractor fades back into the paper
U_END1, U_END2 = 11.7, 13.3     # 世界遵守规则， / 却拒绝被预测。
STEP = 2                        # draw every 2nd sample (dt = 0.004)
CHUNK = 20
S = 17.5                        # px per unit
CENTER = (540.0, 1010.0)
Z_MID = 25.0
TAIL = 70                       # drawn points in the bright tail


def lorenz_time(u):
    k = clamp01((u - U_DRAW[0]) / (U_DRAW[1] - U_DRAW[0]))
    # a gentle start (so the first loop can be followed), then steady, easing into the end
    return T_END * (0.55 * k ** 1.6 + 0.45 * ease_in_out(k))


def u_of_lorenz(t):
    lo, hi = U_DRAW
    for _ in range(50):
        mid = (lo + hi) / 2
        if lorenz_time(mid) < t:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


class LorenzScene:
    LEN = LEN

    def __init__(self):
        full = lz.runs(T_END + 0.1)
        self.pts = [r[::STEP] for r in full]
        self.dt = lz.DT * STEP
        sp = [np.linalg.norm(np.diff(p, axis=0), axis=1) / self.dt for p in self.pts]
        self.speed = [np.concatenate([s[:1], s]) for s in sp]
        gap = np.linalg.norm(self.pts[0] - self.pts[1], axis=1)
        self.gap = np.maximum.accumulate(gap)
        # moments a run switches wing (x changes sign) - used by the score
        self.switch_u = []
        for p in self.pts:
            sgn = np.sign(p[:, 0])
            idx = np.nonzero((sgn[1:] != sgn[:-1]) & (np.arange(1, len(sgn)) * self.dt > 1.0))[0] + 1
            self.switch_u.append([(u_of_lorenz(i * self.dt), int(sgn[i])) for i in idx
                                  if i * self.dt <= T_END])

    # ------------------------------------------------------------ projection
    def project(self, p, phi, scale):
        x, y, z = p[:, 0], p[:, 1], p[:, 2]
        sx = x * math.cos(phi) - y * math.sin(phi)
        return np.stack([CENTER[0] + S * scale * sx, CENTER[1] - S * scale * (z - Z_MID)], 1)

    @staticmethod
    def density(v):
        return np.clip(1.0 / (v / 38.0 + 0.45), 0.2, 1.7)

    def draw_runs(self, c, th, e, phi, scale, alpha, tail_a):
        if e < 2 or alpha <= 0:
            return
        blend = None if th.glow else skia.BlendMode.kMultiply
        heads = []
        for k in range(2):
            rgb = th.a if k == 0 else th.b
            xy = self.project(self.pts[k][:e + 1], phi, scale)
            dens = self.density(self.speed[k][:e + 1])
            lst = xy.tolist()
            for j0 in range(0, e, CHUNK):
                j1 = min(j0 + CHUNK, e)
                a = alpha * 0.58 * float(dens[j0:j1 + 1].mean())
                path = skia.Path.Polygon([skia.Point(*q) for q in lst[j0:j1 + 1]], False)
                pp = paint(rgb, min(a, 255), stroke=1.7, blend=blend)
                pp.setStrokeCap(skia.Paint.kButt_Cap)
                c.drawPath(path, pp)
            if tail_a > 0:
                start = max(0, e - TAIL)
                for j0 in range(start, e, 5):
                    j1 = min(j0 + 5, e)
                    fade = 1 - (e - j1) / TAIL
                    path = skia.Path.Polygon([skia.Point(*q) for q in lst[j0:j1 + 1]], False)
                    c.drawPath(path, paint(rgb, tail_a * 0.75 * fade * fade, stroke=2.6, blend=blend))
            heads.append(lst[e])
        if tail_a > 0:
            (xa, ya), (xb, yb) = heads
            c.drawCircle(xa, ya, 8.5, paint(th.a, tail_a * 0.95))
            c.drawCircle(xb, yb, 11, paint(th.b, tail_a, stroke=1.8))

    def draw(self, c, th, u):
        th.draw_background(c)
        t = lorenz_time(u)
        e = min(int(t / self.dt), len(self.pts[0]) - 1)
        turn = ease_in_out((u - U_TURN[0]) / (U_TURN[1] - U_TURN[0]))
        phi = math.radians(PHI0 + TURN_DEG * turn)
        scale = lerp(1.0, 0.94, turn) * lerp(0.96, 1.0, ease_out(u / 3.0))
        a_all = 255 * (1 - smooth((u - U_FADE[0]) / (U_FADE[1] - U_FADE[0])))
        tail_a = a_all * (1 - smooth((u - (U_DRAW[1] - 0.2)) / 0.8))
        self.draw_runs(c, th, e, phi, scale, a_all, tail_a)
        # text
        fc.caption(c, th, '蝴蝶效应', u, U_TITLE, U_END1 - 0.3, y=200, size=84, spacing=0.4)
        fc.caption(c, th, '世界遵守规则，', u, U_END1, LEN + 1, y=185)
        fc.caption(c, th, '却拒绝被预测。', u, U_END2, LEN + 1, y=275)
        a_sub = 255 * min(smooth((u - 1.0) / 0.8), 1 - smooth((u - (U_TITLE + 2.4)) / 0.6))
        if a_sub > 0:
            th.text(c, '洛伦兹方程，起点只差 0.000127', 540, 1590, 32, th.soft, alpha=a_sub, spacing=0.3)
        a_hud = 255 * smooth((u - 0.8) / 0.5) * (1 - smooth((u - U_TURN[0]) / 0.6))
        g = float(self.gap[e])
        fc.hud(c, th, a_hud, '时间', f'{t:5.2f}', '最大偏差', f'{g:.6f}' if g < 0.01 else f'{g:7.3f}')
        fc.legend(c, th, a_hud)
        fc.dip(c, th, u, LEN, fade_out=0.8)


if __name__ == '__main__':
    sc = LorenzScene()
    for thr in (0.01, 0.5, 5):
        i = int(np.argmax(sc.gap > thr))
        print(f'gap > {thr}: lorenz t={i * sc.dt:.2f}, scene u={u_of_lorenz(i * sc.dt):.2f}')
    print('wing switches (run 1):', len(sc.switch_u[0]), ' (run 2):', len(sc.switch_u[1]))
