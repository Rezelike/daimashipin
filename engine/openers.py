"""Animated openers: visuals for hook(question, en, visual=...) so the opening is never text-only.

Why: the butterfly-effect video opened on a billiards shot already in motion and had the best 2 s bounce (36%);
text-only openings lost ~48% of viewers within 2 s (see the skill's references/lessons.md).
User, 2026-10-20: "开头多做几个动画，不要光是文字".

Every opener:
- already shows the animation on frame 0, and something moves from the very first frame
- puts its events ON beats (integer S.B) and lands the reveal by beat 8 (3.75 s at 128 BPM)
- never moves the whole frame and never pulses / jitters (the user rejected shaking)
- draws under the hook's headline (y 480-1000)

    from engine import openers as OP
    SC.hook("读 14 遍|输给[考 3 次]", "14 rereads lose to 3 self-tests",
            visual=OP.race("一直重读", "合上书考", a_vals=(83, 40), b_vals=(71, 61)))

race      A vs B: the one that looks better at first loses after a time skip     (comparisons, experiments)
dissolve  learned words dissolve into particles while a counter counts down       (forgetting, memory)
diverge   two lines leave one point together and end far apart, values compound    (habits, 1%, compounding)
timer     a clock races through an afternoon while distractions pop up            (focus, procrastination)
"""
import math

import numpy as np
import skia

from . import core as K
from .core import (AMBER, CYAN, DIM, DIMMER, GREEN, PINK, RED, VIOLET, WHITE, W, ap, at, badge, clamp,
                   e_inout, e_out, lerp, measure, paint, pill, text)

PANEL2 = "#0F1A33"


def _burst(c, x, y, B, b0, color, r0=14, r1=84, width=3.0):
    """one expanding ring when something lands on beat b0"""
    k = (B - b0) / 1.0
    if 0 <= k <= 1:
        c.drawCircle(x, y, lerp(r0, r1, e_out(k)), paint(color, 1 - k, stroke=width))


# ----------------------------------------------------------------------------- race
def race(a, b, a_vals=(83, 40), b_vals=(71, 61), phases=("5 分钟后", "一周后"), colors=(DIM, CYAN), unit="%",
         flip=4, land=8, note=None, source=None):
    """Two lanes grow from frame 0 and A looks better; on beat `flip` the phase label jumps (time skip), A falls
    back, B overtakes and lands on beat `land` with a burst and a check.
    a, b: lane labels (<= 5 字); a_vals / b_vals: (phase-1 value, phase-2 value);
    note: takeaway shown 2 beats after landing; source: small data-source line."""
    vmax = max(a_vals + b_vals) * 1.18
    X0, X1 = 600, 1560
    lanes = [(a, a_vals, colors[0], 655), (b, b_vals, colors[1], 835)]
    win = 0 if a_vals[1] > b_vals[1] else 1
    pw = max(measure(p, "bold", 40) for p in phases) + 130

    def value(vals, B):
        if B < flip:
            return lerp(vals[0] * 0.3, vals[0], e_out(B / flip))
        return lerp(vals[0], vals[1], e_inout((B - flip) / (land - flip)))

    def fn(c, S):
        B = S.B
        p2 = B >= flip
        col = AMBER if p2 else DIM
        with at(c, W / 2, 548, lerp(1.12, 1.0, e_out((B - flip) / 0.4)) if p2 else 1.0):
            pill(c, 0, 0, pw, 72, col, 1.0, fill_a=0.22)
            K.icon(c, "calendar-days" if p2 else "timer", -pw / 2 + 44, 0, 34, col)
            text(c, phases[1] if p2 else phases[0], 22, 0, 40, "bold", WHITE)
        done = B >= land
        for i, (name, vals, colr, y) in enumerate(lanes):
            v = value(vals, B)
            text(c, name, X0 - 36, y, 48, "black", WHITE, 1.0, "r")
            c.drawRoundRect(skia.Rect.MakeXYWH(X0, y - 34, X1 - X0, 68), 34, 34, paint(DIMMER, 0.35))
            wbar = max(68.0, (X1 - X0) * v / vmax)
            rect = skia.Rect.MakeXYWH(X0, y - 34, wbar, 68)
            if done and i == win:
                c.drawRoundRect(rect, 34, 34, paint(colr, 0.45 * ap(B, land, 0.4), blur=18))
            c.drawRoundRect(rect, 34, 34, paint(colr, 0.9))
            num = f"{v:.0f}{unit}"
            num_col = WHITE if not done else (colr if i == win else RED)
            text(c, num, X0 + wbar + 24, y, 56, "mono", num_col, 1.0, "l")
            if i == win:
                _burst(c, X0 + wbar, y, B, land, colr)
                if done:
                    bx = X0 + wbar + 24 + measure(num, "mono", 56) + 52
                    with at(c, bx, y, lerp(0.6, 1.0, e_out((B - land) / 0.4))):
                        badge(c, "check", 0, 0, 26, colr, 1.0)
        if note:
            text(c, note, W / 2, 925, 44, "black", AMBER, ap(B, land + 2, 0.5))
        if source:
            text(c, source, W / 2, 978, 34, "reg", DIM, 1.0)
    return fn


# ----------------------------------------------------------------------------- dissolve
def dissolve(words, keep=4, start=0, counter_label="还记得", color=VIOLET, seed=3):
    """Word chips are on screen at frame 0; from beat `start` one chip per beat dissolves into particles until
    `keep` remain (they light up), while a big counter counts down on the beats.
    words: up to 12, each <= 11 letters."""
    words = list(words)[:12]
    n, cols = len(words), 4
    rows = math.ceil(n / cols)
    cw, ch, gx, gy = 300, 88, 26, 30
    gx0, gy0 = 160, (560 if rows >= 3 else 640)
    order = list(np.random.default_rng(seed).permutation(n))
    gone = [int(i) for i in order[:max(0, n - keep)]]
    beat_of = {idx: start + j for j, idx in enumerate(gone)}
    end_beat = start + len(gone)
    parts = {}
    for idx in gone:
        r = np.random.default_rng(seed * 100 + idx)
        parts[idx] = (r.uniform(0, 1, (26, 2)), r.uniform(-150, 150, 26), r.uniform(-320, -90, 26),
                      r.uniform(2.0, 4.5, 26))

    def fn(c, S):
        B = S.B
        left = n
        for i, wd in enumerate(words):
            rr, cc = divmod(i, cols)
            x, y = gx0 + cc * (cw + gx), gy0 + rr * (ch + gy)
            b0 = beat_of.get(i)
            a = 1.0
            if b0 is not None and B >= b0:
                a = 1 - clamp((B - b0) / 0.6)
                if B >= b0 + 1:                       # the counter drops on the next beat
                    left -= 1
                u, vx, vy, sz = parts[i]
                tt = (B - b0) * S.beat                # seconds since this chip started to dissolve
                if tt < 1.6:
                    fade = 1 - tt / 1.6
                    for j in range(len(vx)):
                        px = x + u[j, 0] * cw + vx[j] * tt
                        py = y + u[j, 1] * ch + vy[j] * tt + 130 * tt * tt
                        c.drawCircle(float(px), float(py), float(sz[j]),
                                     paint(WHITE if j % 3 == 0 else color, 0.9 * fade))
            if a <= 0.003:
                continue
            rect = skia.Rect.MakeXYWH(x, y, cw, ch)
            survivor = b0 is None
            lit = survivor and B >= end_beat
            if lit:
                c.drawRoundRect(rect, 18, 18, paint(AMBER, 0.35 * ap(B, end_beat, 0.4), blur=16))
            c.drawRoundRect(rect, 18, 18, paint(PANEL2, 0.92 * a))
            c.drawRoundRect(rect, 18, 18, paint(AMBER if lit else (color if survivor else DIM), 0.85 * a, stroke=2.5))
            text(c, wd, x + cw / 2, y + ch / 2, 40, "mono", WHITE, a)
        cx = 1650
        text(c, counter_label, cx, 600, 44, "bold", DIM)
        text(c, f"{left}", cx, 715, 140, "mono", AMBER if left <= keep else WHITE, 1.0, glow=color, gsig=14)
        text(c, f"/ {n}", cx, 825, 48, "mono", DIM)
    return fn


# ----------------------------------------------------------------------------- diverge
def diverge(a_tag, b_tag, a_vals=(1.0, 37.8), b_vals=(1.0, 0.03), fmt=("{:.1f}", "{:.2f}"), end_label=None,
            land=8, colors=(CYAN, PINK)):
    """Two lines leave the same point together from frame 0 and drift apart slowly, then fast (compounding);
    the values next to the dots change geometrically and land on beat `land` with a burst.
    a_tag / b_tag: labels at the start (e.g. '每天 +1%'); end_label: shown above the scene when they land."""
    SX, SY, EX = 260, 760, 1480
    ya, yb = 590, 930

    def ys(p):
        k = p ** 2.2
        return SY - 8 - (SY - 8 - ya) * k, SY + 8 + (yb - SY - 8) * k

    def fn(c, S):
        B = S.B
        u = clamp(B / land)
        p = 0.03 + 0.97 * u                       # constant speed: moving from the first frame
        done = B >= land
        for which, colr in ((0, colors[0]), (1, colors[1])):
            path = skia.Path()
            for j in range(81):
                pp = p * j / 80
                (path.moveTo if j == 0 else path.lineTo)(SX + (EX - SX) * pp, ys(pp)[which])
            K.glow_path(c, path, colr, 1.0, 5, 1.0)
            x, y = SX + (EX - SX) * p, ys(p)[which]
            c.drawCircle(x, y, 13, paint(WHITE, 1.0))
            c.drawCircle(x, y, 26, paint(colr, 0.55, blur=10))
            v0, v1 = (a_vals, b_vals)[which]
            v = v1 if done else v0 * (v1 / v0) ** u
            dy = -30 if which == 0 else 30
            text(c, fmt[which].format(v), x + 30, y + dy, 72 if done else 52, "mono", colr if done else WHITE, 1.0,
                 "l", glow=colr if done else None, gsig=10)
            _burst(c, x, y, B, land, colr)
        text(c, a_tag, SX - 10, SY - 110, 40, "bold", colors[0], 1.0, "l")
        text(c, b_tag, SX - 10, SY + 110, 40, "bold", colors[1], 1.0, "l")
        if end_label:
            text(c, end_label, W / 2, 525, 44, "black", AMBER, ap(B, land, 0.4))
    return fn


# ----------------------------------------------------------------------------- timer
def timer(t0="14:00", t1="18:00", distractions=(("smartphone", "刷手机"), ("message-circle", "回消息"),
          ("tv", "看视频"), ("coffee", "吃零食")), result=("真正在学", "30 分钟"), focus_share=30 / 240,
          color=AMBER, land=8, note="示意 · Illustration"):
    """A clock races through an afternoon from frame 0 while a distraction pops up on beats 1-4; on beat `land`
    the result lands and the ring shows how small the focused part was (green slice = focus_share)."""
    h0, m0 = map(int, t0.split(":"))
    h1, m1 = map(int, t1.split(":"))
    M0, M1 = h0 * 60 + m0, h1 * 60 + m1
    CX, CY, R = 520, 770, 190
    rect = skia.Rect.MakeXYWH(CX - R, CY - R, 2 * R, 2 * R)

    def fn(c, S):
        B = S.B
        done = B >= land
        prog = 1.0 if done else e_out(B / land)    # fast at first: time flies from the first frame
        c.drawCircle(CX, CY, R, paint(DIMMER, 0.45, stroke=22))
        arc = skia.Path()
        arc.addArc(rect, -90, 359.9 * prog)
        c.drawPath(arc, paint(DIM if done else color, 0.5 if done else 0.9, stroke=22, cap_round=False))
        if done:
            kf = ap(B, land, 0.5)
            fa = skia.Path()
            fa.addArc(rect, -90, 360 * focus_share * kf)
            c.drawPath(fa, paint(GREEN, 0.5, stroke=40, cap_round=False, blur=12))
            c.drawPath(fa, paint(GREEN, 1.0, stroke=26, cap_round=False))
            ang_f = math.radians(-90 + 360 * focus_share)
            _burst(c, CX + R * math.cos(ang_f), CY + R * math.sin(ang_f), B, land, GREEN)
        ang = math.radians(-90 + 360 * prog)
        c.drawLine(CX, CY, CX + R * 0.72 * math.cos(ang), CY + R * 0.72 * math.sin(ang), paint(WHITE, 0.9, stroke=6))
        c.drawCircle(CX, CY, 10, paint(WHITE, 1.0))
        mins = M0 + (M1 - M0) * prog
        text(c, f"{int(mins // 60):02d}:{int(mins % 60):02d}", CX, CY + 72, 60, "mono", WHITE, 1.0)
        for i, (ic, lbl) in enumerate(distractions[:4]):
            b0 = 1 + i
            k = ap(B, b0, 0.35)
            if k <= 0:
                continue
            x, y = 1040 + (i % 2) * 380, 620 + (i // 2) * 150
            with at(c, x, y, lerp(0.6, 1.0, e_out((B - b0) / 0.35))):
                badge(c, ic, -100, 0, 34, RED, k)
                text(c, lbl, -50, 0, 48, "black", WHITE, k, "l")
        if done:
            kr = ap(B, land, 0.4)
            label = f"{result[0]}  {result[1]}"
            pw = measure(label, "black", 48) + 100
            pill(c, 1230, 955, pw, 84, GREEN, kr, fill_a=0.22)
            text(c, label, 1230, 955, 48, "black", WHITE, kr)
        if note:
            text(c, note, 120, 545, 36, "bold", DIM, 1.0, "l")
    return fn
