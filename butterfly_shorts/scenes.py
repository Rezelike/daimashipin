"""Part 1 scenes (0-26 s): billiards hook, 0.001° reveal, title, double pendulum."""
import math
import numpy as np
import skia

import billiards as bl
import pendulum as pd
from common import *  # noqa: F403

# ---------------------------------------------------------------- timeline
T_STRIKE = 2.0          # cue hits the ball
A_END = 8.2
B_START, B_END = 7.9, 11.2
C_START, C_END = 10.9, 14.2
D_START, D_END = 13.9, 26.0
P_RELEASE = 16.1        # pendulums released
P_SPEED = 1.25          # pendulum playback speed (simulation time / video time)
BREAK_SPEED = 8.5
ANGLE_DIFF = 0.001      # degrees - used in BOTH demos, as stated on screen
P_ANGLE = 130.0
P_ANGLE2 = 160.0

BALL_COLORS = {
    1: (255, 196, 36), 2: (58, 120, 232), 3: (240, 72, 62), 4: (146, 92, 206),
    5: (255, 140, 46), 6: (36, 168, 96), 7: (176, 62, 70), 8: (46, 48, 56),
}
for k in range(9, 16):
    BALL_COLORS[k] = BALL_COLORS[k - 8]

# ---------------------------------------------------------------- billiards scene
TABLE_S = 900 / bl.TABLE_W          # px per metre
RAIL_W = 34
TABLE_CY = (660, 1300)


class BreakSim:
    def __init__(self, angle):
        self.pos, self.alive, self.events = bl.simulate(angle, speed=BREAK_SPEED, duration=A_END - T_STRIKE + 0.1)
        n = self.pos.shape[1]
        self.death = np.full(n, 10 ** 9)
        for i in range(n):
            dead = np.nonzero(~self.alive[:, i])[0]
            if len(dead):
                self.death[i] = dead[0]

    def frame(self, t):
        return int(np.clip(round((t - T_STRIKE) * FPS), 0, len(self.pos) - 1))


def table_origin(cy):
    return (W / 2 - bl.TABLE_W * TABLE_S / 2, cy - bl.TABLE_H * TABLE_S / 2)


def to_px(cy, p):
    ox, oy = table_origin(cy)
    return ox + p[0] * TABLE_S, oy + p[1] * TABLE_S


def draw_table(c, cy):
    ox, oy = table_origin(cy)
    pw, ph = bl.TABLE_W * TABLE_S, bl.TABLE_H * TABLE_S
    outer = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(ox - RAIL_W, oy - RAIL_W, pw + 2 * RAIL_W, ph + 2 * RAIL_W), 30, 30)
    c.drawRRect(outer.makeOffset(0, 14), paint((0, 0, 0), 40, blur=18))
    c.drawRRect(outer, paint(RAIL))
    c.drawRRect(outer, paint(RAIL_DARK, stroke=4))
    felt = skia.Rect.MakeXYWH(ox - 6, oy - 6, pw + 12, ph + 12)
    c.drawRRect(skia.RRect.MakeRectXY(felt, 10, 10), paint(FELT_DARK))
    c.drawRect(skia.Rect.MakeXYWH(ox, oy, pw, ph), paint(FELT))
    # diamonds
    for k in range(1, 8):
        if k == 4:
            continue
        x = ox + pw * k / 8
        c.drawCircle(x, oy - RAIL_W / 2, 4, paint(WHITE, 200))
        c.drawCircle(x, oy + ph + RAIL_W / 2, 4, paint(WHITE, 200))
    for k in (1, 2, 3):
        y = oy + ph * k / 4
        c.drawCircle(ox - RAIL_W / 2, y, 4, paint(WHITE, 200))
        c.drawCircle(ox + pw + RAIL_W / 2, y, 4, paint(WHITE, 200))
    # head string
    hx = ox + pw * 0.25
    c.drawLine(hx, oy, hx, oy + ph, paint(WHITE, 60, stroke=2))
    for p in bl.POCKETS:
        x, y = ox + p[0] * TABLE_S, oy + p[1] * TABLE_S
        c.drawCircle(x, y, 25, paint(POCKET))


def draw_ball(c, x, y, num, r, alpha=255):
    c.drawCircle(x + 3, y + 4, r, paint((0, 0, 0), 0.25 * alpha, blur=3))
    if num == 0:
        c.drawCircle(x, y, r, paint(WHITE, alpha))
        c.drawCircle(x, y, r, paint((200, 200, 205), alpha, stroke=1.5))
    elif num <= 8:
        c.drawCircle(x, y, r, paint(BALL_COLORS[num], alpha))
    else:
        c.drawCircle(x, y, r, paint(WHITE, alpha))
        c.save()
        clip = skia.Path()
        clip.addCircle(x, y, r)
        c.clipPath(clip, doAntiAlias=True)
        c.drawRect(skia.Rect.MakeXYWH(x - r, y - r * 0.55, 2 * r, r * 1.1), paint(BALL_COLORS[num], alpha))
        c.restore()
    c.drawCircle(x - r * 0.35, y - r * 0.38, r * 0.28, paint(WHITE, 0.75 * alpha))


def draw_balls(c, cy, sim, t):
    r = bl.R * TABLE_S
    f = sim.frame(t)
    n = sim.pos.shape[1]
    # trails
    for i in range(n):
        if f >= sim.death[i]:
            continue
        rgb = BALL_COLORS.get(i, (230, 230, 235))
        for k in range(1, 10):
            f0, f1 = max(f - k, 0), max(f - k + 1, 0)
            x0, y0 = to_px(cy, sim.pos[f0, i])
            x1, y1 = to_px(cy, sim.pos[f1, i])
            if abs(x1 - x0) + abs(y1 - y0) < 0.5:
                continue
            c.drawLine(x0, y0, x1, y1, paint(rgb if i else WHITE, 110 * (1 - k / 10), stroke=r * 1.3))
    for i in range(n):
        if f >= sim.death[i]:
            k = f - sim.death[i]
            if k < 10:  # shrink into pocket
                x, y = to_px(cy, sim.pos[sim.death[i] - 1, i])
                draw_ball(c, x, y, i, r * (1 - k / 10), 255 * (1 - k / 10))
            continue
        x, y = to_px(cy, sim.pos[f, i])
        draw_ball(c, x, y, i, r)


def draw_cue(c, tip_x, tip_y, angle, alpha=255, length=560, thick=1.0):
    c.save()
    c.translate(tip_x, tip_y)
    c.rotate(math.degrees(angle) + 180)
    c.scale(thick, thick)
    length /= thick
    path = skia.Path()
    path.moveTo(0, -5); path.lineTo(length, -10); path.lineTo(length, 10); path.lineTo(0, 5); path.close()
    c.drawPath(path.makeOffset(3, 6) if hasattr(path, 'makeOffset') else path, paint((0, 0, 0), alpha * 0.18, blur=4))
    c.drawPath(path, paint((226, 188, 136), alpha))
    c.drawRect(skia.Rect.MakeLTRB(length - 170, -10, length, 10), paint((96, 64, 44), alpha))
    c.drawRect(skia.Rect.MakeLTRB(0, -5, 10, 5), paint((90, 150, 220), alpha))
    c.drawRect(skia.Rect.MakeLTRB(10, -5.5, 26, 5.5), paint(WHITE, alpha))
    c.restore()


def pill(c, x, y, text, rgb, size=38):
    f = font(size, 'Bold')
    w = f.measureText(text)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y - size * 0.8, w + 36, size * 1.45), 26, 26)
    c.drawRRect(rr, paint(rgb))
    c.drawString(text, x + 18, y + size * 0.28, f, paint(WHITE))


def pocket_label(sim, t):
    f = sim.frame(t)
    gone = [i for i in range(sim.pos.shape[1]) if sim.death[i] <= f]
    if not gone:
        return '进袋：还没有'
    return '进袋：' + '、'.join('白球' if i == 0 else f'{i}号' for i in gone)


class SceneA:
    def __init__(self):
        self.sims = [BreakSim(0.0), BreakSim(ANGLE_DIFF)]
        self.caps = [
            Caption('同一杆，打两次', 0.25, 3.5, 230, size=80),
            Caption([('结果', INK), ('……', INK), ('不一样？', CORAL)], 4.2, A_END, 230, size=84),
        ]

    def draw(self, c, t):
        for k, (cy, sim) in enumerate(zip(TABLE_CY, self.sims)):
            draw_table(c, cy)
            ox, oy = table_origin(cy)
            pill(c, ox - RAIL_W + 4, oy - RAIL_W - 42, f'第 {k + 1} 次', (CORAL, SKY)[k])
            draw_balls(c, cy, sim, t)
            # cue stick
            cbx, cby = to_px(cy, bl.initial_positions()[0])
            r = bl.R * TABLE_S
            if t < T_STRIKE + 0.5:
                a_in = clamp01((t - 0.9) / 0.3)
                if t < 1.25:
                    gap = 14
                elif t < 1.8:
                    gap = lerp(14, 80, ease_in_out((t - 1.25) / 0.55))
                elif t < T_STRIKE:
                    gap = lerp(80, 0, ((t - 1.8) / 0.2) ** 2)
                else:
                    gap = lerp(0, -10, ease_out_cubic((t - T_STRIKE) / 0.15))
                fade = 1 - clamp01((t - T_STRIKE - 0.15) / 0.35)
                tip_x = (cbx - r - gap) if t < T_STRIKE else (to_px(cy, sim.pos[0, 0])[0] - r - gap)
                draw_cue(c, tip_x, cby, math.radians(ANGLE_DIFF * k), 255 * a_in * fade)
            if t > T_STRIKE + 0.6:
                a = clamp01((t - T_STRIKE - 0.6) / 0.3)
                f = font(40, 'Medium')
                txt = pocket_label(sim, t)
                right = ox + bl.TABLE_W * TABLE_S + RAIL_W - 6
                c.drawString(txt, right - f.measureText(txt), oy - RAIL_W - 28, f, paint(INK_SOFT, 255 * a))
        draw_captions(c, self.caps, t)


# ---------------------------------------------------------------- 0.001° reveal
class SceneB:
    def __init__(self):
        self.caps = [
            Caption('其实，两杆只差了', 8.25, B_END, 360, size=74),
            Caption([('0.001°', CORAL)], 8.6, B_END, 560, size=190, weight='Black'),
            Caption('差距比一根头发丝还细', 9.5, B_END, 1420, size=58, color=INK_SOFT, weight='Medium'),
        ]

    def draw(self, c, t):
        bx, by, r = 640, 1010, 120
        zoom = 1 + 0.06 * ease_in_out((t - B_START) / (B_END - B_START))
        c.save()
        c.translate(W / 2, by)
        c.scale(zoom, zoom)
        c.translate(-W / 2, -by)
        # aim lines (both drawn - they overlap completely)
        for rgb, ang in ((SKY, ANGLE_DIFF), (CORAL, 0.0)):
            a = math.radians(ang)
            x0 = bx + r + 30
            p = paint(rgb, 230, stroke=8)
            p.setPathEffect(skia.DashPathEffect.Make([26, 18], -(t * 80) % 44))
            c.drawLine(x0, by, x0 + 600 * math.cos(a), by + 600 * math.sin(a), p)
        c.drawCircle(bx + 6, by + 10, r, paint((0, 0, 0), 50, blur=12))
        c.drawCircle(bx, by, r, paint(WHITE))
        c.drawCircle(bx, by, r, paint((210, 210, 215), stroke=3))
        c.drawCircle(bx - r * 0.35, by - r * 0.38, r * 0.25, paint((235, 235, 240)))
        poke = 18 * math.sin(clamp01((t - 8.3) / 0.6) * math.pi)
        draw_cue(c, bx - r - 26 + poke, by, 0.0, 255, length=900, thick=3.2)
        c.restore()
        draw_captions(c, self.caps, t)


# ---------------------------------------------------------------- title
def butterfly_path(sign):
    up = skia.Path()
    up.moveTo(0, -8)
    up.cubicTo(sign * -50, -150, sign * -220, -175, sign * -205, -45)
    up.cubicTo(sign * -195, 10, sign * -80, 12, 0, 0)
    low = skia.Path()
    low.moveTo(0, 6)
    low.cubicTo(sign * -120, 20, sign * -175, 120, sign * -95, 150)
    low.cubicTo(sign * -40, 168, sign * -8, 80, 0, 10)
    return up, low


def draw_butterfly(c, x, y, t, scale=1.0, alpha=255):
    c.save()
    c.translate(x, y)
    c.scale(scale, scale)
    flap = 0.55 + 0.45 * math.cos(2 * math.pi * 2.0 * t)
    shader = skia.GradientShader.MakeLinear([skia.Point(-220, 0), skia.Point(220, 0)],
                                            [col(CORAL, alpha), col(SKY, alpha)])
    for sign in (1, -1):
        c.save()
        c.scale(flap, 1)
        up, low = butterfly_path(sign)
        p = skia.Paint(AntiAlias=True, Shader=shader)
        c.drawPath(low, p)
        c.drawPath(up, p)
        c.drawCircle(sign * -140, -80, 18, paint(WHITE, alpha * 0.8))
        c.drawCircle(sign * -95, 105, 12, paint(WHITE, alpha * 0.8))
        c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(-9, -60, 9, 120), 9, 9), paint(INK, alpha))
    for sign in (1, -1):
        p = paint(INK, alpha, stroke=4)
        path = skia.Path()
        path.moveTo(0, -55)
        path.quadTo(sign * 20, -110, sign * 48, -130)
        c.drawPath(path, p)
        c.drawCircle(sign * 48, -130, 7, paint(INK, alpha))
    c.restore()


class SceneC:
    def __init__(self):
        self.caps = [
            Caption('这叫', 11.25, C_END, 870, size=66, color=INK_SOFT, weight='Medium'),
            Caption([('「', SKY), ('蝴蝶效应', INK), ('」', CORAL)], 11.45, C_END, 1030, size=150, weight='Black'),
        ]
        rng = np.random.default_rng(3)
        self.dots = [(rng.uniform(0, 2 * math.pi), rng.uniform(260, 520), rng.uniform(8, 18),
                      (CORAL, SKY, (255, 206, 84))[k % 3]) for k in range(26)]

    def draw(self, c, t):
        s = t - 11.2
        burst = ease_out_cubic(s / 0.9)
        for ang, dist, rr, rgb in self.dots:
            a = 255 * (1 - clamp01((s - 0.5) / 1.2))
            c.drawCircle(W / 2 + math.cos(ang) * dist * burst, 900 + math.sin(ang) * dist * burst * 1.2,
                         rr, paint(rgb, a * 0.8))
        hl = ease_out_cubic((t - 11.75) / 0.35)
        if hl > 0:
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W / 2 - 330, 1064, 660 * hl, 36), 18, 18),
                        paint((255, 214, 102), 200))
        draw_captions(c, self.caps, t)
        bs = ease_out_back(s / 0.6)
        if bs > 0:
            draw_butterfly(c, W / 2, 590 - 14 * math.sin(t * 2.4), t, scale=1.05 * bs)


# ---------------------------------------------------------------- double pendulum
PIVOT = (540, 960)
ARM = 250


class SceneD:
    def __init__(self):
        dur = (D_END - P_RELEASE) * P_SPEED + 0.2
        sim_fps = FPS / P_SPEED
        self.states = [pd.simulate(P_ANGLE, P_ANGLE2, dur, fps=sim_fps, substeps=32),
                       pd.simulate(P_ANGLE + ANGLE_DIFF, P_ANGLE2, dur, fps=sim_fps, substeps=32)]
        self.bobs = [pd.bob_positions(s) for s in self.states]
        d = np.linalg.norm(self.bobs[0][1] - self.bobs[1][1], axis=1) * ARM
        k = int(np.argmax(d > 25))
        self.t_split = P_RELEASE + k / FPS
        ts = self.t_split
        self.caps = [
            Caption('再看这两个摆', 14.2, 16.9, 210, size=80),
            Caption('起点几乎一样', 17.1, ts - 0.1, 210, size=80),
            Caption('然后……', ts, ts + 1.9, 210, size=80),
            Caption([('结局', INK), ('毫不相干', CORAL)], ts + 2.1, D_END, 210, size=88),
        ]

    def frame(self, t):
        return int(np.clip(round((t - P_RELEASE) * FPS), 0, len(self.states[0]) - 1))

    def draw_pend(self, c, px, py, b1, b2, rgb, scale, alpha):
        x1, y1 = px + b1[0] * ARM * scale, py + b1[1] * ARM * scale
        x2, y2 = px + b2[0] * ARM * scale, py + b2[1] * ARM * scale
        c.drawLine(px, py, x1, y1, paint(rgb, alpha, stroke=10 * scale))
        c.drawLine(x1, y1, x2, y2, paint(rgb, alpha, stroke=10 * scale))
        c.drawCircle(x1, y1, 20 * scale, paint(rgb, alpha))
        c.drawCircle(x2, y2, 28 * scale, paint(rgb, alpha))
        c.drawCircle(x2 - 8 * scale, y2 - 9 * scale, 8 * scale, paint(WHITE, alpha * 0.6))

    def draw(self, c, t):
        f = self.frame(t)
        merge = ease_in_out((t - 15.0) / 0.9)
        scale = lerp(0.5, 1.0, merge)
        appear = ease_out_back((t - 14.0) / 0.5)
        pivots = [(lerp(310, PIVOT[0], merge), PIVOT[1]), (lerp(770, PIVOT[0], merge), PIVOT[1])]
        # trails
        if t > P_RELEASE:
            for k, rgb in ((1, SKY), (0, CORAL)):
                b2 = self.bobs[k][1]
                n, step = 96, 8
                start = max(0, f - n)
                for j0 in range(start, f, step):
                    j1 = min(j0 + step, f)
                    path = skia.Path()
                    path.moveTo(PIVOT[0] + b2[j0, 0] * ARM, PIVOT[1] + b2[j0, 1] * ARM)
                    for j in range(j0 + 1, j1 + 1):
                        path.lineTo(PIVOT[0] + b2[j, 0] * ARM, PIVOT[1] + b2[j, 1] * ARM)
                    a = 170 * (1 - (f - j1) / n)
                    p = paint(rgb, a, stroke=7)
                    p.setStrokeCap(skia.Paint.kButt_Cap)
                    c.drawPath(path, p)
        # pivot mount
        for k, (px, py) in enumerate(pivots):
            if appear <= 0:
                break
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(px - 60 * scale, py - 18 * scale, 120 * scale,
                                                                 14 * scale), 7, 7), paint(INK_SOFT, 255))
            if merge >= 1:
                break
        for k, rgb, a in ((1, SKY, 255), (0, CORAL, 205)):
            b1, b2 = self.bobs[k][0][f], self.bobs[k][1][f]
            px, py = pivots[k]
            c.save()
            c.translate(px, py)
            c.scale(max(appear, 0.01), max(appear, 0.01))
            c.translate(-px, -py)
            self.draw_pend(c, px, py, b1, b2, rgb, scale, a)
            c.restore()
        for px, py in pivots[:1] if merge >= 1 else pivots:
            c.drawCircle(px, py, 10 * scale, paint(INK))
        draw_captions(c, self.caps, t)


# ---------------------------------------------------------------- compositing
class Part1:
    def __init__(self):
        self.A, self.B, self.C, self.D = SceneA(), SceneB(), SceneC(), SceneD()
        self.windows = [(self.A, -1, A_END), (self.B, B_START, B_END), (self.C, C_START, C_END),
                        (self.D, D_START, D_END + 1)]

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
        end = clamp01((t - (D_END - 0.4)) / 0.4)
        if end > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint(BG, 255 * end))
