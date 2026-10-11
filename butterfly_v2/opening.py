"""0-12 s: one table, two breaks overlaid -> rewind -> push in on the cue ball -> 0.001°.

Run A (first break) is drawn as solid discs, run B (second break) as rings, so for the
first second the two runs sit exactly on top of each other and read as one.
"""
import math
import os
import sys

import numpy as np
import skia

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'butterfly_shorts'))
import billiards as bl  # noqa: E402

from theme import W, H, FPS, paint, clamp01, smooth, ease_out, ease_in_out, lerp  # noqa: E402

# ---------------------------------------------------------------- timeline
T_DRAW = (0.0, 1.2)          # table lines draw on
T_BALLS = 0.9
T_CUE_IN, T_PULL, T_STRIKE = 1.2, 1.35, 2.0
SIM_LEN = 5.8                # seconds of simulated motion shown
T_REWIND = (7.9, 8.9)
T_ZOOM = (8.9, 10.0)
T_NUMBER = 9.75
T_SPREAD = (10.7, 11.4)
END = 12.4
ANGLE = 0.001
SPEED = 8.5

# ---------------------------------------------------------------- geometry (table stands upright)
S = 1340 / bl.TABLE_W                      # px per metre
CX, CY = 540, 985
R = bl.R * S
ZOOM_TO = (540, 1180)                      # where the cue ball ends up after the push-in
ZOOM = 4.0


def to_px(p):
    """sim (x along length, y across) -> screen. Break travels upward."""
    return CX + (p[1] - bl.TABLE_H / 2) * S, CY + (bl.TABLE_W / 2 - p[0]) * S


class Run:
    def __init__(self, angle):
        self.pos, self.alive, self.events = bl.simulate(angle, speed=SPEED, duration=SIM_LEN + 0.05)
        self.px = np.stack([CX + (self.pos[..., 1] - bl.TABLE_H / 2) * S,
                            CY + (bl.TABLE_W / 2 - self.pos[..., 0]) * S], -1)
        n = self.pos.shape[1]
        self.death = np.full(n, 10 ** 9)
        for i in range(n):
            d = np.nonzero(~self.alive[:, i])[0]
            if len(d):
                self.death[i] = d[0]


class Opening:
    def __init__(self):
        self.runs = [Run(0.0), Run(ANGLE)]
        self.n = self.runs[0].pos.shape[1]
        self.cue0 = to_px(bl.initial_positions()[0])
        self.last_frame = len(self.runs[0].pos) - 1
        self.sim_events = [ev for ev in self.runs[0].events]

    # ------------------------------------------------------------ clock
    def sim_frame(self, t):
        """Frame index of the simulation shown at video time t (handles the rewind)."""
        if t < T_STRIKE:
            return 0.0
        forward = min((t - T_STRIKE) * FPS, self.last_frame)
        if t < T_REWIND[0]:
            return forward
        k = ease_in_out((t - T_REWIND[0]) / (T_REWIND[1] - T_REWIND[0]))
        held = min((T_REWIND[0] - T_STRIKE) * FPS, self.last_frame)
        return held * (1 - k)

    def camera(self, t):
        k = ease_in_out((t - T_ZOOM[0]) / (T_ZOOM[1] - T_ZOOM[0]))
        scale = lerp(1.0, ZOOM, k)
        fx, fy = self.cue0
        # keep the cue ball travelling smoothly from its table position to ZOOM_TO
        tx, ty = lerp(fx, ZOOM_TO[0], k), lerp(fy, ZOOM_TO[1], k)
        return scale, (fx, fy), (tx, ty), k

    # ------------------------------------------------------------ table
    def table_paths(self):
        hw, hh = bl.TABLE_H * S / 2, bl.TABLE_W * S / 2
        inner = skia.Path()
        inner.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(CX - hw, CY - hh, CX + hw, CY + hh), 6, 6))
        outer = skia.Path()
        m = 40
        outer.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(CX - hw - m, CY - hh - m, CX + hw + m,
                                                                CY + hh + m), 26, 26))
        return inner, outer

    def draw_table(self, c, th, t, alpha):
        k = ease_in_out((t - T_DRAW[0]) / (T_DRAW[1] - T_DRAW[0]))
        if k <= 0:
            return
        inner, outer = self.table_paths()
        if th.surface is not None:
            fill = paint(th.surface, alpha * k)
            c.drawPath(inner, fill)
        for path, w, a in ((outer, 1.2, 0.55), (inner, 2.0, 0.9)):
            p = paint(th.hair, alpha * a, stroke=w)
            if k < 0.999:
                p.setPathEffect(skia.TrimPathEffect.Make(0, k, skia.TrimPathEffect.Mode.kNormal))
            c.drawPath(path, p)
        a2 = alpha * smooth((t - 0.8) / 0.5)
        if a2 <= 0:
            return
        for p in bl.POCKETS:
            x, y = to_px(p)
            c.drawCircle(x, y, 25, paint(th.pocket, a2 * (0.9 if th.name != 'dark' else 1.0)))
            if th.name == 'dark':
                c.drawCircle(x, y, 25, paint(th.hair, a2 * 0.35, stroke=1.2))
        # head string + foot spot + diamonds
        hy = to_px((bl.TABLE_W * 0.25, 0))[1]
        hw = bl.TABLE_H * S / 2
        dash = paint(th.hair, a2 * 0.25, stroke=1)
        dash.setPathEffect(skia.DashPathEffect.Make([6, 8], 0))
        c.drawLine(CX - hw, hy, CX + hw, hy, dash)
        fx, fy = to_px((bl.TABLE_W * 0.72, bl.TABLE_H / 2))
        c.drawCircle(fx, fy - 0, 2.5, paint(th.hair, a2 * 0.4))
        hh = bl.TABLE_W * S / 2
        for k2 in range(1, 8):
            if k2 == 4:
                continue
            y = CY - hh + 2 * hh * k2 / 8
            for x in (CX - hw - 20, CX + hw + 20):
                c.drawCircle(x, y, 2.2, paint(th.hair, a2 * 0.45))
        for k2 in (1, 2, 3):
            x = CX - hw + 2 * hw * k2 / 4
            for y in (CY - hh - 20, CY + hh + 20):
                c.drawCircle(x, y, 2.2, paint(th.hair, a2 * 0.45))

    # ------------------------------------------------------------ balls
    def draw_trails(self, c, th, f, alpha):
        """Faint full history (long exposure) + a brighter fading tail of the last ~0.8 s."""
        fi = int(f)
        if fi < 2:
            return
        hist_a = 0.06 if th.glow else 0.10
        tail = 48
        for k, run in enumerate(self.runs):
            rgb = th.a if k == 0 else th.b
            for i in range(self.n):
                end = min(fi, run.death[i] - 1)
                if end < 2:
                    continue
                pts = run.px[:end + 1, i]
                if np.abs(pts[-1] - pts[0]).sum() < 2:
                    continue
                hist = skia.Path()
                hist.moveTo(*pts[0])
                for p in pts[1:end + 1:3]:
                    hist.lineTo(*p)
                hist.lineTo(*pts[end])
                c.drawPath(hist, paint(rgb, alpha * hist_a, stroke=1.2))
                start = max(0, end - tail)
                for j0 in range(start, end, 6):
                    j1 = min(j0 + 6, end)
                    seg = skia.Path()
                    seg.moveTo(*pts[j0])
                    for j in range(j0 + 1, j1 + 1):
                        seg.lineTo(*pts[j])
                    fade = 1 - (end - j1) / tail
                    if th.glow:
                        c.drawPath(seg, paint(rgb, alpha * 0.35 * fade, stroke=2.0, blend=skia.BlendMode.kPlus))
                    else:
                        c.drawPath(seg, paint(rgb, alpha * 0.45 * fade, stroke=1.8))

    def ball_xy(self, run, i, f):
        fi = int(f)
        fr = f - fi
        p0 = run.px[min(fi, self.last_frame), i]
        p1 = run.px[min(fi + 1, self.last_frame), i]
        return p0 + (p1 - p0) * fr

    def draw_connectors(self, c, th, f, alpha):
        a_, b_ = self.runs
        for i in range(self.n):
            if f >= a_.death[i] or f >= b_.death[i]:
                continue
            pa, pb = self.ball_xy(a_, i, f), self.ball_xy(b_, i, f)
            d = np.linalg.norm(pa - pb)
            if d < 2 * R:
                continue
            p = paint(th.soft, alpha * 0.55 * clamp01((d - 2 * R) / 30), stroke=1)
            p.setPathEffect(skia.DashPathEffect.Make([3, 5], 0))
            c.drawLine(pa[0], pa[1], pb[0], pb[1], p)

    def draw_balls(self, c, th, f, alpha, appear=1.0):
        for k, run in enumerate(self.runs):
            rgb = th.a if k == 0 else th.b
            for i in range(self.n):
                shrink = 1.0
                if f >= run.death[i]:
                    shrink = 1 - (f - run.death[i]) / 12
                    if shrink <= 0:
                        continue
                    x, y = run.px[run.death[i] - 1, i]
                else:
                    x, y = self.ball_xy(run, i, f)
                r = R * appear * shrink
                if r <= 0.3:
                    continue
                if k == 0:
                    fill = th.ink if i == 0 else rgb
                    if th.glow:
                        c.drawCircle(x, y, r * 1.6, paint(fill, alpha * 0.14, blur=8, blend=skia.BlendMode.kPlus))
                    c.drawCircle(x, y, r - 1, paint(fill, alpha * 0.92))
                else:
                    c.drawCircle(x, y, r + 2.5, paint(rgb, alpha, stroke=1.8))

    def draw_cue(self, c, th, t, alpha):
        if t < T_CUE_IN or t > T_STRIKE + 0.5:
            return
        a = alpha * min(smooth((t - T_CUE_IN) / 0.3), 1 - smooth((t - T_STRIKE - 0.1) / 0.4))
        if t < T_PULL:
            gap = 16
        elif t < T_STRIKE - 0.12:
            gap = lerp(16, 110, ease_in_out((t - T_PULL) / (T_STRIKE - 0.12 - T_PULL)))
        elif t < T_STRIKE:
            gap = lerp(110, 0, ((t - (T_STRIKE - 0.12)) / 0.12) ** 2)
        else:
            gap = -6 * ease_out((t - T_STRIKE) / 0.1)
        x, y = self.cue0
        y0 = y + R + 6 + gap
        path = skia.Path()
        path.moveTo(x - 3.5, y0)
        path.lineTo(x + 3.5, y0)
        path.lineTo(x + 7, y0 + 380)
        path.lineTo(x - 7, y0 + 380)
        path.close()
        c.drawPath(path, paint(th.ink, a * 0.85))
        c.drawRect(skia.Rect.MakeLTRB(x - 3.5, y0, x + 3.5, y0 + 10), paint(th.b, a))

    # ------------------------------------------------------------ hud
    def max_gap_cm(self, f):
        a_, b_ = self.runs
        fi = min(int(f), self.last_frame)
        alive = (fi < a_.death) & (fi < b_.death)
        d = np.linalg.norm(a_.pos[fi] - b_.pos[fi], axis=1)
        d = np.where(alive, d, 0)
        return float(d.max()) * 100

    def draw_hud(self, c, th, t, f, alpha):
        a = alpha * smooth((t - 1.3) / 0.5) * (1 - smooth((t - T_ZOOM[0]) / 0.4))
        if a <= 0:
            return
        y = 1765
        th.text(c, '时间', 90, y, 30, th.soft, alpha=a, align='left', spacing=0.15)
        th.text(c, f'{f / FPS:5.2f} s', 175, y, 34, th.ink, role='mono', alpha=a, align='left')
        gap = self.max_gap_cm(f)
        txt = f'{gap:6.2f} cm' if gap < 100 else f'{gap:6.1f} cm'
        th.text(c, txt, 990, y, 34, th.ink, role='mono', alpha=a, align='right')
        th.text(c, '最大偏差', 990 - 240, y, 30, th.soft, alpha=a, align='right', spacing=0.15)
        # legend
        ly = 1835
        c.drawCircle(398, ly, 10, paint(th.a, a))
        th.text(c, '第一次', 420, ly, 28, th.soft, alpha=a, align='left', spacing=0.15)
        c.drawCircle(588, ly, 11, paint(th.b, a, stroke=2.2))
        th.text(c, '第二次', 610, ly, 28, th.soft, alpha=a, align='left', spacing=0.15)

    # ------------------------------------------------------------ captions
    def caption(self, c, th, s, t, t0, t1, y=185, size=56):
        a = 255 * min(smooth((t - t0) / 0.6), 1 - smooth((t - (t1 - 0.6)) / 0.6))
        if a > 0:
            th.text(c, s, 540, y + 10 * (1 - ease_out((t - t0) / 0.9)), size, th.ink, role='title', alpha=a,
                    spacing=0.18)

    # ------------------------------------------------------------ aim lines + number
    def draw_aim(self, c, th, t):
        k = smooth((t - (T_ZOOM[0] + 0.5)) / 0.6)
        if k <= 0:
            return
        x, y = ZOOM_TO
        spread = math.radians(10) * ease_in_out((t - T_SPREAD[0]) / (T_SPREAD[1] - T_SPREAD[0]))
        length = 900 * ease_out((t - (T_ZOOM[0] + 0.5)) / 1.0)
        start = R * ZOOM + 16
        for rgb, ang in ((th.b, -spread / 2), (th.a, spread / 2)):
            dx, dy = math.sin(ang), -math.cos(ang)
            p = paint(rgb, 255 * k, stroke=2.4)
            c.drawLine(x + dx * start, y + dy * start, x + dx * (start + length), y + dy * (start + length), p)
            if th.glow:
                c.drawLine(x + dx * start, y + dy * start, x + dx * (start + length), y + dy * (start + length),
                           paint(rgb, 90 * k, stroke=10, blur=6, blend=skia.BlendMode.kPlus))
        if spread > 0.01:
            a = 255 * smooth((t - (T_SPREAD[0] + 0.3)) / 0.5)
            rad = 520
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeLTRB(x - rad, y - rad, x + rad, y + rad),
                       -90 - math.degrees(spread / 2), math.degrees(spread))
            c.drawPath(arc, paint(th.soft, a, stroke=1.2))
            lx = x + rad * math.sin(spread / 2) + 40
            th.text(c, '角度放大一万倍后', lx, y - rad + 10, 30, th.soft, alpha=a, align='left', spacing=0.2)
            th.text(c, '× 10 000', lx, y - rad + 60, 30, th.soft, role='mono', alpha=a, align='left')

    def draw_number(self, c, th, t):
        a = 255 * smooth((t - T_NUMBER) / 0.9)
        if a <= 0:
            return
        th.text(c, '0.001°', 540, 1480, 190, th.ink, role='title', alpha=a, spacing=0.02)
        a2 = 255 * smooth((t - (T_NUMBER + 0.8)) / 0.8)
        th.text(c, '两次出杆，全部的差别', 540, 1650, 40, th.soft, alpha=a2, spacing=0.35)

    # ------------------------------------------------------------ frame
    def draw(self, c, th, t):
        th.draw_background(c)
        f = self.sim_frame(t)
        scale, focus, target, zk = self.camera(t)
        c.save()
        c.translate(target[0], target[1])
        c.scale(scale, scale)
        c.translate(-focus[0], -focus[1])
        table_a = 255 * (1 - smooth((zk - 0.15) / 0.5))
        self.draw_table(c, th, t, table_a)
        self.draw_trails(c, th, f, 255)
        self.draw_connectors(c, th, f, 255 * (1 - smooth(zk / 0.3)))
        appear = ease_out((t - T_BALLS) / 0.6)
        if appear > 0:
            self.draw_balls(c, th, f, 255, appear)
        self.draw_cue(c, th, t, 255)
        c.restore()
        self.draw_hud(c, th, t, f, 255)
        self.caption(c, th, '同一杆，打两次', t, 0.6, 4.6)
        self.caption(c, th, '结果，完全不同', t, 5.0, 7.9)
        self.draw_aim(c, th, t)
        self.draw_number(c, th, t)
        out = smooth((t - (END - 0.6)) / 0.6)
        if out > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint(th.bg, 255 * out))
