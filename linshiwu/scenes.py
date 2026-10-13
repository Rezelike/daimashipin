"""Scene animators. Each draw(c, t, S) gets local time t (s) and scene timing S:
S.D = scene duration, S.L[i] / S.E[i] = start / end of narration line i (local).
SFX[id](S) returns a list of (local_time, kind) sound cues for that scene.
"""
import math
from gfx import *

CX = W / 2


def at(S, i, frac=0.0):
    """Time point inside line i (frac 0..1 of its duration)."""
    return S.L[i] + (S.E[i] - S.L[i]) * frac


# ---------------------------------------------------------------- shared bits
def viewfinder(c, t, a=1.0):
    m, ln = 64, 80
    p = strokep(INK, 6, 150 * a)
    for (x, y, sx, sy) in [(m, 230, 1, 1), (W - m, 230, -1, 1), (m, 1400, 1, -1), (W - m, 1400, -1, -1)]:
        c.drawLine(x, y, x + sx * ln, y, p); c.drawLine(x, y, x, y + sy * ln, p)
    if int(t * 1.6) % 2 == 0:
        c.drawCircle(m + 28, 300, 12, fillp(RED, 230 * a))
    text(c, "REC", m + 50, 300, 30, INK, "sans_b", "left", 200 * a)
    fr = int(t * 30) % 30
    text(c, f"00:0{int(t // 60)}:{int(t % 60):02d}:{fr:02d}", W - m - 20, 300, 28, INK, "sans_m", "right", 170 * a)


def law_header(c, t, tag, title, y=330):
    a = ease_out(prog(t, 0.0, 0.5))
    with layer(c, a, 0, (1 - a) * 30):
        pill(c, tag, CX, y, 34, ORANGE)
        text(c, title, CX, y + 110, 78, INK, "serif_k")


# ---------------------------------------------------------------- open
def draw_open(c, t, S):
    s = lerp(1.45, 1.62, t / S.D)
    with layer(c, 1, CX, 860, s):
        chair(c)
    viewfinder(c, t)
    a = ease_out(prog(t, S.E[1] - 0.2, 0.5))
    if a > 0:
        with layer(c, a, 0, (1 - a) * 20):
            pill(c, "观察对象 No.000 · 衣服椅", CX, 1330, 32, INK)


# ---------------------------------------------------------------- title
def draw_title(c, t, S):
    a0 = ease_out(prog(t, 0.0, 0.6))
    text(c, "OBSERVATION  REPORT  ·  VOL.01", CX, 600, 28, GREY, "sans_m", a=255 * a0, spacing=4)
    for row, (s, y) in enumerate([("临时物", 770), ("永久化理论", 950)]):
        sz = 150
        ws = [text_w(ch, sz, "serif_k") for ch in s]
        x = CX - sum(ws) / 2
        for k, ch in enumerate(s):
            p = ease_out(prog(t, 0.15 + row * 0.25 + k * 0.07, 0.5))
            text(c, ch, x + ws[k] / 2, y + (1 - p) * 40, sz, INK, "serif_k", a=255 * p)
            x += ws[k]
    u = ease_in_out(prog(t, 1.1, 0.8))
    if u > 0:
        c.drawPath(rrect(CX - 330, 1060, 660 * u, 14, 7), fillp(ORANGE))
    a = ease_out(prog(t, 1.5, 0.6))
    text(c, "一份关于「先这样吧」的观察报告", CX, 1150, 42, INK, "sans_m", a=255 * a)


# ---------------------------------------------------------------- specimens
SPECS = [
    (chair, 0.34, 18, "No.000", "衣服椅", "Sella vestimentorum"),
    (lambda c: bag(c, inner=3), 0.5, 10, "No.001", "袋中袋", "Saccus saccorum"),
    (remote, 0.44, 0, "No.002", "胶带遥控器", "Telecontrolum adhaesivum"),
    (table, 0.5, -10, "No.003", "垫脚纸", "Charta stabilis"),
    (box, 0.52, 10, "No.004", "待拆纸箱", "Arca perpetua"),
    (folder, 0.62, -5, "No.005", "新建文件夹(3)", "Directorium novum III"),
]
CW, CH = 450, 320
CARD_POS = [(70 + (i % 2) * 490, 330 + (i // 2) * 350) for i in range(6)]


def card_times(S):
    return [S.L[0] + 0.5] + [S.L[i] + 0.1 for i in range(1, 6)]


def draw_specimens(c, t, S):
    a = ease_out(prog(t, 0, 0.5))
    text(c, "居所常见物种图鉴", CX, 250, 44, INK, "serif_k", a=255 * a)
    ts = card_times(S)
    for i, (fn, sc, oy, no, name, latin) in enumerate(SPECS):
        p = prog(t, ts[i], 0.45)
        if p <= 0:
            continue
        x, y = CARD_POS[i]
        k = back_out(p)
        with layer(c, clamp(p * 2), x + CW / 2, y + CH / 2, 0.6 + 0.4 * k):
            active = (i == 0 and t < S.L[1]) or (0 < i < 6 and S.L[i] <= t < S.L[min(i + 1, 6)])
            c.drawPath(rrect(-CW / 2 + 8, -CH / 2 + 10, CW, CH, 22), fillp(INK, 28))
            c.drawPath(rrect(-CW / 2, -CH / 2, CW, CH, 22), fillp(CARD))
            c.drawPath(rrect(-CW / 2, -CH / 2, CW, CH, 22), strokep(ORANGE if active else INK, 7 if active else 4))
            text(c, no, -CW / 2 + 24, -CH / 2 + 32, 22, GREY, "sans_b", "left")
            with layer(c, 1, 0, -28 + oy, sc):
                fn(c)
            text(c, name, 0, CH / 2 - 68, 32, INK, "sans_b")
            text(c, latin, 0, CH / 2 - 30, 21, GREY, "serif", skew=-0.22)
            # stamps
            ps = prog(t, at(S, 6, 0.6) + i * 0.12, 0.2)
            pp = prog(t, S.L[7] + 0.55 + i * 0.1, 0.2)
            if ps > 0:
                with layer(c, ps * (1 - 0.6 * clamp(pp * 2)), CW / 2 - 85, -CH / 2 + 52, 2.2 - 1.2 * ps, -14):
                    stamp(c, "临时", RED, 30)
                    if pp > 0:
                        line(c, -60, 0, -60 + 120 * ease_out(pp), 0, RED, 6)
            if pp > 0:
                with layer(c, pp, CW / 2 - 95, -CH / 2 + 118, 2.2 - 1.2 * pp, -10):
                    stamp(c, "永久", INK, 34)


# ---------------------------------------------------------------- core
def draw_core(c, t, S):
    # dictionary entry card
    a = ease_out(prog(t, 0, 0.6)) * (1 - ease_in_out(prog(t, S.L[2] - 0.2, 0.4)))
    if a > 0:
        with layer(c, a, 0, (1 - ease_out(prog(t, 0, 0.6))) * 40):
            c.drawPath(rrect(98, 548, 900, 600, 30), fillp(INK, 25))
            c.drawPath(rrect(90, 540, 900, 600, 30), fillp(CARD))
            c.drawPath(rrect(90, 540, 900, 600, 30), strokep(INK, 4))
            text(c, "临时物永久化", CX, 680, 96, INK, "serif_k")
            text(c, "lín shí wù yǒng jiǔ huà", CX, 790, 34, GREY, "sans_m", spacing=2)
            pill(c, "名词", 210, 880, 30, ORANGE)
            d = "一件事物被标记为“临时”之后，被替换的概率持续下降，直至趋近于零的现象。"
            for k, ln in enumerate(wrap(d, 40, 760, "sans_m")):
                text(c, ln, 270, 880 + k * 64, 40, INK, "sans_m", "left")
            text(c, "—— 见：先这样吧、过两天再说", 950, 1080, 30, GREY, "sans_m", "right")
    # the big proposition, revealed char by char
    rows = [("没有什么，", 700), ("比临时方案更持久。", 860)]
    hi = {(1, 1), (1, 2), (1, 6), (1, 7)}
    n_total = sum(len(r[0]) for r in rows)
    t0, t1 = S.L[2], S.L[2] + (S.E[2] - S.L[2]) * 0.85
    q = ease_out(prog(t, t0 - 0.3, 0.5))
    if q > 0:
        text(c, "“", 150, 560, 220, ORANGE, "serif_k", a=200 * q)
    idx = 0
    for r, (s, y) in enumerate(rows):
        sz = 104
        ws = [text_w(ch, sz, "serif_k") for ch in s]
        x = CX - sum(ws) / 2
        for k, ch in enumerate(s):
            p = ease_out(prog(t, t0 + (t1 - t0) * idx / n_total, 0.35))
            if p > 0:
                rgb = ORANGE if (r, k) in hi else INK
                text(c, ch, x + ws[k] / 2, y + (1 - p) * 30, sz, rgb, "serif_k", a=255 * p)
            x += ws[k]; idx += 1
    u = ease_in_out(prog(t, S.E[2] + 0.1, 0.6))
    if u > 0:
        c.drawPath(rrect(CX - 300, 960, 600 * u, 10, 5), fillp(INK))


# ---------------------------------------------------------------- law 1
X0, X1, YT, YB = 150, 950, 560, 1010
U0 = 0.52

def motive(u):
    if u < U0:
        return 0.12 + 0.78 * (u / U0) ** 1.6
    return 0.05 + 0.85 * math.exp(-(u - U0) * 30)

def chart_pt(u, v):
    return X0 + (X1 - X0) * u, YB - (YB - YT) * v

def draw_law1(c, t, S):
    law_header(c, t, "第一定律", "够用即终点")
    ax = ease_out(prog(t, 0.4, 0.6))
    if ax > 0:
        line(c, X0, YB, X0 + (X1 - X0 + 30) * ax, YB, INK, 5)
        line(c, X0, YB, X0, YB - (YB - YT + 40) * ax, INK, 5)
        text(c, "改变的动力", X0 + 20, YT - 40, 32, INK, "sans_b", "left", 255 * ax)
        text(c, "时间", X1 + 20, YB + 45, 32, INK, "sans_b", "right", 255 * ax)
    u = 0.0
    if t > S.L[1]:
        u = U0 * ease_in_out(prog(t, S.L[1], (S.E[1] - S.L[1]) * 0.9))
    if t > S.L[2]:
        u = U0 + (1 - U0) * ease_in_out(prog(t, at(S, 2, 0.25), (S.E[2] - S.L[2]) * 0.6))
    if u > 0:
        p = skia.Path(); n = 140
        for k in range(n + 1):
            uu = u * k / n
            x, y = chart_pt(uu, motive(uu))
            p.moveTo(x, y) if k == 0 else p.lineTo(x, y)
        c.drawPath(p, strokep(ORANGE, 10))
        x, y = chart_pt(u, motive(u))
        c.drawCircle(x, y, 15, fillp(ORANGE)); c.drawCircle(x, y, 15, strokep(INK, 4))
    a = ease_out(prog(t, at(S, 1, 0.45), 0.4))
    if a > 0:
        with layer(c, a):
            x, y = chart_pt(0.3, motive(0.3))
            pill(c, "不能用", x - 20, y - 70, 30, RED)
    a = ease_out(prog(t, at(S, 2, 0.2), 0.4))
    if a > 0:
        x, _ = chart_pt(U0, 0)
        line(c, x, YB, x, YT - 10, INK, 4, 200 * a, dash=[16, 12])
        with layer(c, a, x, YT - 10, 0.8, -8):
            c.drawPath(rrect(-80, -22, 160, 44, 4), fillp(TAPE, 235)); c.drawPath(rrect(-80, -22, 160, 44, 4), strokep(INK, 4))
            text(c, "临时方案", 0, 0, 30, INK, "sans_b")
    a = ease_out(prog(t, at(S, 2, 0.6), 0.4))
    if a > 0:
        x, y = chart_pt(0.79, 0.2)
        with layer(c, a):
            pill(c, "能用，但不完美", x, y, 30, GREY)
    # remote + "修遥控器这件事" crossed out
    a = ease_out(prog(t, S.L[3], 0.5))
    if a > 0:
        with layer(c, a, 330, 1215, 0.52 * (0.8 + 0.2 * a), -14):
            remote(c)
        with layer(c, a):
            text(c, "「修遥控器」", 730, 1170, 46, INK, "serif_k")
            text(c, "这件事", 730, 1245, 46, INK, "serif_k")
            k = ease_in_out(prog(t, at(S, 3, 0.62), 0.5))
            if k > 0:
                line(c, 580, 1210, 580 + 300 * k, 1205, RED, 10)


# ---------------------------------------------------------------- law 2
ORBIT = [(0, 250, shirt, CORAL, 0.38), (1.3, 360, sock, BLUE, 0.5), (2.2, 250, shirt, MUSTARD, 0.38),
         (3.3, 360, shirt, TEAL, 0.34), (4.3, 250, sock, CORAL, 0.5), (5.3, 360, shirt, BLUE, 0.38)]
FLOAT = [(250, 640, shirt, CORAL, 0.5, -12), (830, 650, shirt, MUSTARD, 0.5, 15),
         (200, 1060, sock, BLUE, 0.6, 20), (870, 1060, shirt, TEAL, 0.5, -8)]

def draw_law2(c, t, S):
    law_header(c, t, "第二定律", "习惯的吸引力")
    cy = 900
    aA = ease_out(prog(t, S.L[1], 0.5)) * (1 - ease_in_out(prog(t, S.L[2] - 0.2, 0.4)))
    aB = ease_out(prog(t, S.L[2] + 0.1, 0.5)) * (1 - ease_in_out(prog(t, S.L[3] - 0.2, 0.4)))
    aC = ease_out(prog(t, S.L[3] + 0.1, 0.5))
    if t < S.L[1] + 0.1:  # intro: just the chair
        with layer(c, ease_out(prog(t, 0.3, 0.5)), CX, cy, 0.62):
            chair(c)
    if aA > 0:
        with layer(c, aA):
            for r in (250, 360):
                c.drawCircle(CX, cy, r, strokep(GREY, 4, 180, dash=[14, 14]))
            with layer(c, 1, CX, cy, 0.62):
                chair(c)
            for k, (a0, r, fn, colr, sc) in enumerate(ORBIT):
                pa = ease_out(prog(t, S.L[1] + 0.3 + k * 0.25, 0.5))
                ang = a0 + (t - S.L[1]) * (0.5 if r == 250 else -0.32)
                rr = r + (1 - pa) * 250
                with layer(c, pa, CX + math.cos(ang) * rr, cy + math.sin(ang) * rr, sc, math.degrees(ang) * 0.3):
                    fn(c, colr)
            text(c, "越久，越重", CX, cy + 440, 34, GREY, "sans_b", a=255 * ease_out(prog(t, at(S, 1, 0.6), 0.4)))
    if aB > 0:
        with layer(c, aB):
            items = [(200, wardrobe, 0.62, "衣柜"), (CX, chair, 0.48, "中转站"), (880, basket, 0.72, "洗衣篮")]
            for k, (x, fn, sc, lab) in enumerate(items):
                pk = back_out(prog(t, S.L[2] + 0.2 + k * 0.3, 0.45))
                with layer(c, clamp(pk), x, cy, sc * (0.7 + 0.3 * pk)):
                    fn(c)
                if lab == "中转站":
                    pill(c, lab, x, cy + 230, 34, ORANGE)
                else:
                    text(c, lab, x, cy + 230, 36, INK, "sans_b", a=255 * clamp(pk))
            ar = ease_in_out(prog(t, at(S, 2, 0.45), 0.5))
            if ar > 0:
                arrow(c, 280, cy - 170, 280 + (430 - 280) * ar, cy - 170 - 20 * ar, INK, 6, bend=-0.25 * ar)
            ar2 = ease_in_out(prog(t, at(S, 2, 0.6), 0.5))
            if ar2 > 0:
                arrow(c, 650, cy - 170, 650 + (800 - 650) * ar2, cy - 170 + 20 * ar2, INK, 6, bend=-0.25 * ar2)
            sa = ease_out(prog(t, at(S, 2, 0.75), 0.4))
            if sa > 0:
                with layer(c, sa, CX, cy - 300, 0.9 + 0.1 * sa):
                    check_badge(c, "运行稳定", GREEN, 32)
    if aC > 0:
        with layer(c, aC):
            fly = ease_out(prog(t, at(S, 3, 0.3), 0.7))
            with layer(c, 1, CX, cy + 40, 0.82):
                chair(c, clothes=fly < 0.05)
            for k, (fx, fy, fn, colr, sc, rot) in enumerate(FLOAT):
                if fly <= 0.05:
                    continue
                bob = math.sin(t * 2.2 + k) * 12 * fly
                x, y = lerp(CX, fx, fly), lerp(cy - 60, fy, fly) + bob
                with layer(c, 1, x, y, sc, rot * fly + math.sin(t * 1.7 + k) * 6):
                    fn(c, colr)
                qa = ease_out(prog(t, at(S, 3, 0.62) + k * 0.12, 0.35))
                if qa > 0:
                    text(c, "?", x + 70, y - 70, 80, ORANGE, "sans_k", a=255 * qa)


# ---------------------------------------------------------------- law 3
BUBBLES = [("难看", 290, 620, 0.42), ("不顺手", 800, 700, 0.6), ("该换了", 330, 860, 0.78)]

def draw_law3(c, t, S):
    law_header(c, t, "第三定律", "标签豁免")
    a = ease_out(prog(t, S.L[1], 0.5))
    if a > 0:
        dim = 1 - 0.45 * ease_in_out(prog(t, S.L[2], 0.6))
        with layer(c, a * dim):
            c.drawPath(rrect(140, 540, 800, 400, 26), strokep(GREY, 4, 220, dash=[14, 12]))
            pill(c, "正式物品", CX, 540, 28, INK)
            with layer(c, 1, CX, 750, 0.58):
                lamp(c)
            for (s, x, y, f) in BUBBLES:
                pb = back_out(prog(t, at(S, 1, f), 0.35))
                if pb > 0:
                    with layer(c, clamp(pb), x, y, pb):
                        w = text_w(s, 36) + 50
                        c.drawPath(rrect(-w / 2, -36, w, 72, 20), fillp(RED))
                        c.drawPath(poly([(-14, 30), (14, 30), (-4, 54)]), fillp(RED))
                        text(c, s, 0, 0, 36, (255, 255, 255))
    a = ease_out(prog(t, S.L[2], 0.5))
    if a > 0:
        with layer(c, a, 0, (1 - a) * 40):
            c.drawPath(rrect(140, 990, 800, 400, 26), strokep(GREY, 4, 220, dash=[14, 12]))
            pill(c, "临时物品", CX, 990, 28, ORANGE)
            with layer(c, 1, CX - 120, 1200, 0.68, -3):
                notice(c)
            ps = prog(t, at(S, 2, 0.62), 0.2)
            if ps > 0:
                with layer(c, clamp(ps * 1.5), CX + 20, 1250, 2.6 - 1.6 * ease_out(ps), -14):
                    stamp(c, "免检", RED, 66)
    a = ease_out(prog(t, at(S, 3, 0.1), 0.5))
    if a > 0:
        text(c, "从未被看待  →  从未被否定", CX, 1430, 36, GREY, "sans_b", a=255 * a)


def shake(t, S):
    """Screen shake offset for stamp impacts (law3)."""
    t0 = at(S, 2, 0.62) + 0.2
    if t0 <= t < t0 + 0.3:
        k = (1 - (t - t0) / 0.3)
        return math.sin(t * 90) * 10 * k, math.cos(t * 70) * 8 * k
    return 0, 0


# ---------------------------------------------------------------- breed
def bag_layout(n):
    if n == 1:
        return [(CX, 880, 0.95)]
    if n == 2:
        return [(310, 880, 0.75), (770, 880, 0.75)]
    if n == 4:
        return [(310, 720, 0.55), (770, 720, 0.55), (310, 1060, 0.55), (770, 1060, 0.55)]
    xs = [170, 410, 670, 910]
    return [(xs[i % 4], 760 + (i // 4) * 300, 0.4) for i in range(8)]


def breed_stages(S):
    return [(0, 1), (at(S, 2, 0.55), 2), (S.E[2] + 0.6, 4), (S.E[2] + 1.3, 8)]


def draw_breed(c, t, S):
    law_header(c, t, "推论", "临时物会繁殖")
    stages = breed_stages(S)
    cur, prev, tp = 1, 1, 0.0
    for (ts, n) in stages:
        if t >= ts:
            prev, cur, tp = cur, n, ts
    k = ease_in_out(prog(t, tp, 0.45))
    L1, L0 = bag_layout(cur), bag_layout(prev)
    stuffed = ease_in_out(prog(t, S.L[1], S.E[1] - S.L[1]))
    a0 = ease_out(prog(t, 0.3, 0.5))
    for i in range(cur):
        x1, y1, s1 = L1[i]
        if i < prev:
            x0, y0, s0 = L0[i]; ap = 1
        else:
            par = L0[i % prev]
            x0, y0, s0 = par[0], par[1], 0.05
            ap = clamp(k * 3)
        x, y, s = lerp(x0, x1, k), lerp(y0, y1, k), lerp(s0, s1, k if i < prev else back_out(k))
        inner, bulge = (2 + int(4 * stuffed), stuffed) if i == 0 else (1 + i % 3, 0.2)
        jig = math.sin(t * 25) * 2.5 * stuffed * (1 - prog(t, S.E[1], 0.3)) if i == 0 else 0
        with layer(c, a0 * ap, x, y, s, jig):
            bag(c, PAPER, inner, bulge)
    a = ease_out(prog(t, S.L[1], 0.4))
    if a > 0:
        text(c, "种群数量", CX - 40, 1340, 40, INK, "sans_b", "right", 255 * a)
        pk = back_out(prog(t, tp, 0.3)) if tp > 0 else 1
        with layer(c, a, CX + 60, 1340, 0.6 + 0.4 * pk):
            text(c, str(cur), 0, 0, 72, ORANGE, "sans_k")


# ---------------------------------------------------------------- turn
def draw_turn(c, t, S):
    warm = ease_in_out(prog(t, 0, 1.2))
    c.drawRect(skia.Rect.MakeWH(W, H), fillp((255, 196, 130), 34 * warm))
    wedge_in = ease_out(prog(t, S.L[1] + 0.2, 0.7))
    z = ease_in_out(prog(t, S.L[2], 1.4))
    s = lerp(1.3, 3.3, z)
    fx, fy = lerp(0, WEDGE_POS[0], z), lerp(0, WEDGE_POS[1], z)
    cy = 860
    wob = (1 - wedge_in) * 3.7 * (0.5 + 0.5 * math.sin(t * 8))
    a = ease_out(prog(t, 0.0, 0.6))
    with layer(c, a, CX - s * fx, cy - s * fy, s):
        table(c, wedge_dx=None, tilt=wob)
        if wedge_in > 0:
            wedge(c, (1 - wedge_in) * 260)
    if t < S.L[1] + 0.6:
        wa = ease_out(prog(t, 0.6, 0.4)) * (1 - prog(t, S.L[1] + 0.2, 0.4))
        if wa > 0:
            text(c, "晃", CX + 360, cy - 260 + math.sin(t * 8) * 8, 72, RED, "sans_k", a=255 * wa)
    ba = back_out(prog(t, S.L[1] + 1.0, 0.45)) * (1 - prog(t, S.L[2], 0.4))
    if ba > 0:
        with layer(c, clamp(ba), CX, 520, ba):
            check_badge(c, "问题已解决", GREEN, 40)
    sa = ease_out(prog(t, S.L[2] + 1.2, 0.5))
    if sa > 0:
        c.drawCircle(CX, cy, 140 + 12 * math.sin(t * 3), strokep(ORANGE, 8, 255 * sa))
        with layer(c, sa, 0, (1 - sa) * 20):
            pill(c, "最懂这张桌子的", CX, cy + 230, 36, ORANGE)
            text(c, "一张纸", CX, cy + 330, 60, INK, "serif_k")


# ---------------------------------------------------------------- end
def draw_end(c, t, S):
    fade_chair = 1 - 0.85 * ease_in_out(prog(t, S.L[2] - 0.2, 0.6))
    s = lerp(1.25, 0.95, ease_in_out(t / S.D))
    with layer(c, fade_chair, CX, 1030, s):
        chair(c)
    viewfinder(c, t + 100, fade_chair)
    a = ease_out(prog(t, S.L[0], 0.6)) * (1 - prog(t, S.L[1] - 0.2, 0.35))
    if a > 0:
        text(c, "生活，从来不是", CX, 430, 76, INK, "serif_k", a=255 * a)
        text(c, "按计划搭起来的", CX, 540, 76, INK, "serif_k", a=255 * a)
    a = ease_out(prog(t, S.L[1], 0.6)) * (1 - prog(t, S.L[2] - 0.2, 0.35))
    if a > 0:
        text(c, "而是由一个又一个", CX, 390, 64, INK, "serif_k", a=255 * a)
        text(c, "「先这样吧」", CX, 520, 110, ORANGE, "serif_k", a=255 * ease_out(prog(t, at(S, 1, 0.3), 0.5)))
        text(c, "攒起来的", CX, 640, 64, INK, "serif_k", a=255 * ease_out(prog(t, at(S, 1, 0.7), 0.5)))
    a = ease_out(prog(t, S.L[2], 0.6))
    if a > 0:
        with layer(c, a, 0, (1 - a) * 30):
            text(c, "你家里的", CX, 700, 72, INK, "serif_k")
            text(c, "「先这样吧」", CX, 850, 120, ORANGE, "serif_k")
            text(c, "是什么？", CX, 1000, 72, INK, "serif_k")
        pa = back_out(prog(t, S.E[2] + 0.2, 0.4))
        if pa > 0:
            with layer(c, clamp(pa), CX, 1180, pa):
                pill(c, "评论区告诉我 ↓", 0, 0, 38, INK)


DRAW = dict(open=draw_open, title=draw_title, specimens=draw_specimens, core=draw_core,
            law1=draw_law1, law2=draw_law2, law3=draw_law3, breed=draw_breed, turn=draw_turn, end=draw_end)

SFX = dict(
    open=lambda S: [(S.E[1] - 0.2, "pop")],
    title=lambda S: [(0.15, "chime")],
    specimens=lambda S: [(x, "pop") for x in card_times(S)]
        + [(at(S, 6, 0.6) + i * 0.12 + 0.15, "thud") for i in range(6)]
        + [(S.L[7] + 0.55 + i * 0.1 + 0.15, "thud") for i in range(6)],
    core=lambda S: [(S.L[2] - 0.2, "chime")],
    law1=lambda S: [(0.05, "pop"), (at(S, 2, 0.2), "tick"), (at(S, 3, 0.62), "swipe")],
    law2=lambda S: [(0.05, "pop")] + [(S.L[2] + 0.2 + k * 0.3, "pop") for k in range(3)]
        + [(at(S, 2, 0.75), "chime"), (at(S, 3, 0.3), "whoosh")],
    law3=lambda S: [(0.05, "pop")] + [(at(S, 1, f), "pop") for (_, _, _, f) in BUBBLES]
        + [(at(S, 2, 0.62) + 0.2, "thud")],
    breed=lambda S: [(0.05, "pop")] + [(ts, "pop") for ts, _ in breed_stages(S)[1:]],
    turn=lambda S: [(S.L[1] + 0.2, "whoosh"), (S.L[1] + 1.0, "chime")],
    end=lambda S: [(S.E[2] + 0.2, "pop")],
)
