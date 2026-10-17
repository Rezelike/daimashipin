"""艾宾浩斯遗忘曲线 / The Ebbinghaus forgetting curve — 75 s, no music (user adds a four-on-the-floor DJ track).

Beat grid: 128 BPM (1 beat = 0.469 s, 1 bar = 1.875 s). Every scene is 4 or 8 bars, every element lands
on a beat, the frame kicks on each beat. If the chosen song has another tempo, change BPM and re-render.

Facts:
* Ebbinghaus (1885), Über das Gedächtnis: one subject (himself), nonsense syllables, savings method.
  Savings: 20 min 58.2%, 1 h 44.2%, 9 h 35.8%, 1 d 33.7%, 2 d 27.8%, 6 d 25.4%, 31 d 21.1%.
* Replicated: Murre & Dros (2015), PLOS ONE 10(7): e0120644.
* Step 2's curve is an illustration (labelled), the 1/3/7/15/30-day schedule is common practice (labelled).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import skia                                                    # noqa: E402

from engine import core as K                                   # noqa: E402
from engine import scenes as SC                                # noqa: E402
from engine.core import (AMBER, CYAN, DIM, DIMMER, PINK, VIOLET, WHITE, W, ap, at, badge, e_back,  # noqa: E402
                         e_inout, e_out, lerp, paint, pill, rich, text)
from engine.render import Episode, Scene, run                  # noqa: E402

BPM = 128

# ----------------------------------------------------------------------------- helpers
def _seg_point(p0, p1, p2, p3, u):
    return tuple((1 - u) ** 3 * p0[i] + 3 * (1 - u) ** 2 * u * p1[i] + 3 * (1 - u) * u ** 2 * p2[i] + u ** 3 * p3[i]
                 for i in range(2))


def _split(p0, p1, p2, p3, u):
    """first part [0,u] of a cubic bezier (de Casteljau)"""
    l = lambda a, b: (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    a, b, c = l(p0, p1), l(p1, p2), l(p2, p3)
    d, e = l(a, b), l(b, c)
    return p0, a, d, l(d, e)


def smooth(pts):
    """Catmull-Rom through pts -> list of cubic segments (p0, c1, c2, p1)"""
    segs = []
    for i in range(len(pts) - 1):
        p0 = pts[max(0, i - 1)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        segs.append((p1, c1, c2, p2))
    return segs


def partial_path(segs, lands, B):
    """path drawn up to beat B; segment i travels from lands[i] to lands[i+1] (eased, arrives ON the beat)"""
    path = skia.Path()
    path.moveTo(*segs[0][0])
    head = segs[0][0]
    for i, sg in enumerate(segs):
        u = e_inout((B - lands[i]) / (lands[i + 1] - lands[i]))
        if u <= 0:
            break
        q = sg if u >= 1 else _split(*sg, u)
        path.cubicTo(*q[1], *q[2], *q[3])
        head = q[3]
        if u < 1:
            break
    return path, head


def burst(c, x, y, B, b0, color, a=1.0, r0=10, r1=46):
    """ring that explodes on the beat a point lands"""
    k = (B - b0) / 1.0
    if 0 <= k <= 1:
        c.drawCircle(x, y, lerp(r0, r1, e_out(k)), paint(color, a * (1 - k), stroke=3))


def axes(c, X0, X1, YT, YB, a, ylabels=True):
    for v in (0, 25, 50, 75, 100):
        y = YB - (YB - YT) * v / 100
        c.drawLine(X0, y, X1, y, paint(DIMMER, (0.6 if v == 0 else 0.28) * a, stroke=2 if v == 0 else 1))
        if ylabels:
            text(c, f"{v}%", X0 - 18, y, 34, "monor", DIM, a, "r")
    c.drawLine(X0, YT - 10, X0, YB, paint(DIMMER, 0.6 * a, stroke=2))


# ----------------------------------------------------------------------------- step 1: the real curve
EBB = [("刚学完", 100.0), ("20分钟", 58.2), ("1小时", 44.2), ("9小时", 35.8), ("1天", 33.7),
       ("2天", 27.8), ("6天", 25.4), ("31天", 21.1)]


def forgetting_curve(c, S, x, y, w, h, a):
    B, vb = S.B, S.vb
    X0, X1, YT, YB = 300, 1380, 540, 850
    xs = [X0 + (X1 - X0) * i / (len(EBB) - 1) for i in range(len(EBB))]
    pts = [(xs[i], YB - (YB - YT) * v / 100) for i, (_, v) in enumerate(EBB)]
    lands = [vb + 2 * i for i in range(len(EBB))]           # beats 8, 10, ... 22: one point per half bar
    axes(c, X0, X1, YT, YB, a)
    for i, (lbl, v) in enumerate(EBB):
        text(c, lbl, xs[i], 892, 34, "bold", WHITE if B >= lands[i] else DIMMER, a)
    text(c, "数据：艾宾浩斯 1885 · 无意义音节 · 按重学时节省的时间计算", X0, 940, 34, "reg", DIM, a, "l")
    segs = smooth(pts)
    path, head = partial_path(segs, lands, B)
    if B > lands[0]:
        K.glow_path(c, path, PINK, 1.0, 5, a)
    n = sum(1 for lb in lands if B >= lb)
    for i in range(n):
        px, py = pts[i]
        c.drawCircle(px, py, 9, paint(WHITE, a))
        c.drawCircle(px, py, 18, paint(PINK, 0.5 * a, blur=8))
        burst(c, px, py, B, lands[i], PINK, a)
        if i:
            text(c, f"{EBB[i][1]:.0f}%", px, py - 38, 34, "mono", WHITE, a)
    if 0 < n < len(EBB) and B < lands[-1]:
        c.drawCircle(head[0], head[1], 7, paint(PINK, a))
    # 1 day = about 1/3  (lands on the bar-5 downbeat)
    k1 = ap(B, lands[4], 0.4) * a
    if k1 > 0:
        px, py = pts[4]
        c.drawCircle(px, py, 30 * e_back((B - lands[4]) / 0.6), paint(AMBER, k1, stroke=4))
    # steepest part annotation
    k2 = ap(B, vb + 16, 0.5) * a
    if k2 > 0:
        br = skia.Path()
        br.moveTo(pts[0][0] + 16, pts[0][1] - 8)
        br.cubicTo(pts[1][0] + 40, pts[1][1] - 60, pts[2][0] + 30, pts[2][1] - 70, pts[2][0] + 70, pts[2][1] - 70)
        K.glow_path(c, br, PINK, e_out((B - vb - 16) / 0.8), 3, k2, glow=8)
        text(c, "最初 1 小时，忘得最快", pts[2][0] + 90, pts[2][1] - 72, 44, "black", PINK, k2, "l",
             glow=PINK, gsig=8, glow_a=0.5)
    # live counter panel
    cx = 1590
    i = max(0, n - 1)
    text(c, "还剩", cx, 580, 44, "bold", DIM, a)
    if n:
        s = lerp(1.25, 1.0, e_out((B - lands[i]) / 0.5))
        with at(c, cx, 680, s):
            text(c, f"{EBB[i][1]:.0f}%", 0, 0, 120, "mono", PINK if i else WHITE, a, glow=PINK, gsig=14)
        text(c, EBB[i][0] if i == 0 else f"{EBB[i][0]}后", cx, 790, 44, "bold", WHITE, a)
    if k1 > 0 and n >= 5:
        pill(c, cx, 870, 260, 70, AMBER, k1)
        text(c, "1 天 ≈ 1/3", cx, 870, 38, "black", WHITE, k1)


# ----------------------------------------------------------------------------- step 2: spaced repetition (illustration)
REVIEWS = [1, 3, 7, 15]
STAB = [0.81, 2.5, 7.8, 24.3, 67.0]     # chosen so troughs rise 29% -> 45% -> 60% -> 72% -> 80% (illustration)


def spaced(c, S, x, y, w, h, a):
    B, vb = S.B, S.vb
    X0, X1, YT, YB = 300, 1380, 560, 850
    X = lambda d: X0 + (X1 - X0) * math.sqrt(d / 30)
    Y = lambda v: YB - (YB - YT) * v / 100
    axes(c, X0, X1, YT, YB, a)
    text(c, "示意图 · Illustration", 1740, 510, 34, "bold", DIM, a, "r")
    for d, lbl in [(0, "学完"), (1, "第1天"), (3, "第3天"), (7, "第7天"), (15, "第15天"), (30, "第30天")]:
        text(c, lbl, X(d), 892, 34, "bold", WHITE if (d == 0 or B >= vb + 4 + 2 * (REVIEWS.index(d) + 1 if d in REVIEWS else 6)) else DIMMER, a)

    def curve(f, d0, d1, prog):
        path = skia.Path()
        n = 60
        for j in range(n + 1):
            d = d0 + (d1 - d0) * (j / n) * prog
            (path.moveTo if j == 0 else path.lineTo)(X(d), Y(f(d)))
        return path

    # grey: no review (draws during bar 3)
    pg = e_inout((B - vb) / 4)
    if pg > 0:
        no_rev = lambda d: 21 + 79 * math.exp(-d / 0.45)
        c.drawPath(curve(no_rev, 0, 30, pg), paint(DIM, 0.85 * a, stroke=4))
        if pg >= 1:
            text(c, "不复习", X(30) - 10, Y(21) + 34, 36, "bold", DIM, a, "r")
    # cyan: review on days 1, 3, 7, 15; each review lands ON a beat (vb+6, +8, +10, +12)
    edges = [0] + REVIEWS + [30]
    starts = [vb + 4 + 2 * k for k in range(5)]                  # segment k drawn from starts[k]
    ends = [vb + 6 + 2 * k for k in range(4)] + [vb + 16]
    troughs = []
    for k in range(5):
        d0, d1 = edges[k], edges[k + 1]
        u = e_inout((B - starts[k]) / (ends[k] - starts[k]))
        if u <= 0:
            break
        f = lambda d, d0=d0, s=STAB[k]: 100 * math.exp(-(d - d0) / s)
        K.glow_path(c, curve(f, d0, d1, u), CYAN, 1.0, 5, a)
        if u >= 1 and k < 4:
            tv = f(d1)
            troughs.append((X(d1), Y(tv)))
            c.drawLine(X(d1), Y(tv), X(d1), Y(100), paint(CYAN, a, stroke=5))
            c.drawCircle(X(d1), Y(100), 9, paint(WHITE, a))
            burst(c, X(d1), Y(100), B, ends[k], CYAN, a)
            text(c, f"复习{k + 1}", X(d1), Y(100) - 34, 34, "bold", CYAN, a)
    # rising troughs = forgetting less every time
    k3 = ap(B, vb + 18, 0.5) * a
    if k3 > 0 and len(troughs) == 4:
        tp = skia.Path()
        tp.moveTo(*troughs[0])
        for p in troughs[1:]:
            tp.lineTo(*p)
        prog = e_out((B - vb - 18) / 1.0)
        if prog < 1:
            K.trim_path(c, tp, prog, paint(AMBER, k3, stroke=4))
        else:
            pe = paint(AMBER, k3, stroke=4)
            pe.setPathEffect(skia.DashPathEffect.Make([18, 12], -B * 20))
            c.drawPath(tp, pe)
        text(c, "每次都忘得更少", troughs[1][0] + 60, 740, 40, "black", AMBER, k3, "l",
             glow=AMBER, gsig=8, glow_a=0.5)
    # legend
    kl = ap(B, vb + 16, 0.5) * a
    if kl > 0:
        c.drawLine(1450, 640, 1510, 640, paint(DIM, kl, stroke=5))
        text(c, "不复习", 1530, 640, 40, "bold", DIM, kl, "l")
        c.drawLine(1450, 740, 1510, 740, paint(CYAN, kl, stroke=5))
        text(c, "复习 4 次", 1530, 740, 40, "bold", CYAN, kl, "l")


# ----------------------------------------------------------------------------- step 3: the schedule
NODES = [("当天", "睡前"), ("第 1 天", None), ("第 3 天", None), ("第 7 天", None), ("第 15 天", None), ("第 30 天", None)]
GAPS = [1, 2, 4, 8, 15]


def schedule(c, S, x, y, w, h, a):
    B, vb = S.B, S.vb
    ny = 700
    xs = [330 + i * (1260 / 5) for i in range(6)]
    lands = [vb + 2 * i for i in range(6)]                     # one node per half bar: beats 8 ... 18
    text(c, "常用间隔 · 可按难度调整", 200, 510, 34, "bold", DIM, a, "l")
    c.drawLine(xs[0], ny, xs[-1], ny, paint(DIMMER, 0.6 * a, stroke=3))
    for i in range(5):
        u = e_inout((B - lands[i]) / (lands[i + 1] - lands[i]))
        if u <= 0:
            continue
        hgt = 40 + 110 * math.log2(GAPS[i]) / math.log2(15)
        x0, x1 = xs[i], xs[i + 1]
        arc = skia.Path()
        arc.moveTo(x0, ny - 30)
        arc.cubicTo(x0 + 20, ny - 30 - hgt * 1.3, x1 - 20, ny - 30 - hgt * 1.3, x1, ny - 30)
        K.glow_path(c, arc, AMBER, u, 4, a, glow=10)
        if u >= 1:
            text(c, f"+{GAPS[i]} 天", (x0 + x1) / 2, ny - 30 - hgt - 26, 36, "mono", AMBER, a)
    for i, (lbl, sub) in enumerate(NODES):
        on = B >= lands[i]
        if on:
            s = lerp(1.35, 1.0, e_back((B - lands[i]) / 0.6))
            with at(c, xs[i], ny, s):
                badge(c, "check", 0, 0, 26, AMBER, a)
            burst(c, xs[i], ny, B, lands[i], AMBER, a, 26, 70)
        else:
            c.drawCircle(xs[i], ny, 12, paint(DIMMER, a))
        text(c, lbl, xs[i], ny + 72, 44, "black", WHITE if on else DIMMER, a)
        if sub:
            text(c, sub, xs[i], ny + 118, 36, "bold", DIM if on else DIMMER, a)
    kt = ap(B, vb + 12, 0.5) * a
    if kt > 0:
        tw = K.rich_width("复习 = 合上书[回忆一遍]，不是重看", 50)
        badge(c, "brain", W / 2 - tw / 2 - 50, 885, 26, VIOLET, kt)
        rich(c, "复习 = 合上书[回忆一遍]，不是重看", W / 2 + 10, 885, 50, "black", WHITE, VIOLET, kt)
        text(c, "Recall with the book closed, don't just reread", W / 2 + 10, 935, 36, "monor", DIM, kt)


# ----------------------------------------------------------------------------- cover
def cover(c):
    K.bg_dark_tech(c, 3.3, 60 / BPM)
    path = skia.Path()
    X0, X1, YT, YB = 160, 1760, 120, 760
    pts = [(X0 + (X1 - X0) * i / 7, YB - (YB - YT) * v / 100) for i, (_, v) in enumerate(EBB)]
    path.moveTo(*pts[0])
    for sg in smooth(pts):
        path.cubicTo(*sg[1], *sg[2], *sg[3])
    K.glow_path(c, path, PINK, 1.0, 8, 0.55, glow=22)
    text(c, "背了就忘？", W / 2, 210, 100, "black", PINK, 1, glow=PINK, gsig=16)
    text(c, "遗忘曲线", W / 2, 440, 230, "black", WHITE, 1, glow=CYAN, gsig=30,
         shader=K.grad_shader("#E0F7FF", "#B9A8FF"))
    text(c, "THE EBBINGHAUS FORGETTING CURVE", W / 2, 610, 48, "mono", CYAN, 1, ls=6)
    pill(c, W / 2, 760, 900, 110, AMBER, 1, fill_a=0.22)
    text(c, "1 分钟看懂 · 附复习时间表", W / 2, 760, 60, "black", WHITE, 1)
    text(c, "1 天后只剩约 1/3 · 中英双语", W / 2, 900, 40, "bold", DIM, 1)


# ----------------------------------------------------------------------------- episode
EP = Episode(
    slug="forgetting_curve",
    title="艾宾浩斯遗忘曲线",
    bpm=BPM,
    music=False,
    scenes=[
        Scene("hook", 4, SC.hook("为什么你背的单词，[总是记不住]？", "Why do you keep forgetting what you learn?", pains=[
            ("book-open", "昨晚背 50 个单词", "今早剩 20 个", "50 words → 20 overnight"),
            ("graduation-cap", "考前通宵复习", "考完全忘光", "Cram, test, forget"),
            ("bookmark", "刚看完一本书", "一周后讲不出", "A week later: blank"),
        ]), chapter="痛点"),
        Scene("answer", 4, SC.answer("不是你记性差，是遗忘有规律", "[艾宾浩斯遗忘曲线]", "THE EBBINGHAUS FORGETTING CURVE",
                                     [("忘得多快", "How fast"), ("复习的作用", "Why review"), ("复习时间表", "When to review")],
                                     colors=[PINK, CYAN, AMBER]), chapter="答案"),
        Scene("step1", 8, SC.step(1, "遗忘有多快", "How fast we forget",
                                  [("1 天后，只剩约 [1/3]", "After 1 day, only about 1/3 is left")],
                                  visual=forgetting_curve, color=PINK), chapter="3 步"),
        Scene("step2", 8, SC.step(2, "复习一次，曲线变平", "Each review flattens the curve",
                                  [("每复习一次，[忘得更慢]", "Every review slows down forgetting")],
                                  visual=spaced, color=CYAN), chapter="3 步"),
        Scene("step3", 8, SC.step(3, "什么时候复习", "When to review",
                                  [("间隔[越来越长]地复习", "Review at growing intervals")],
                                  visual=schedule, color=AMBER), chapter="3 步"),
        Scene("summary", 4, SC.summary("遗忘曲线 · 复习时间表", "Forgetting curve · review schedule", [
            ("学完当天，睡前[回忆一遍]", "Same day: recall once before bed"),
            ("第 1、3、7 天，[各回忆一次]", "Day 1, 3, 7: recall again"),
            ("第 15、30 天，[再巩固一次]", "Day 15, 30: lock it in"),
            ("先理解再记，[忘得更慢]", "Understand first, forget slower"),
        ]), chapter="总结"),
        Scene("cta", 4, SC.cta("你最想记住的是[什么]？", "What do you most want to remember?", "艾宾浩斯遗忘曲线",
                               "THE FORGETTING CURVE", next_teaser=("主动回忆：合上书考自己", "Next: active recall, test yourself")),
              chapter="总结"),
    ],
    cover=cover,
    publish=dict(
        title="Vibe知识大赏/背了就忘？1分钟看懂艾宾浩斯遗忘曲线",
        desc="背了就忘，不是你记性差。艾宾浩斯 1885 年的实验发现：遗忘先快后慢，1 天后只剩约 1/3。"
             "复习一次，曲线就变平一点。最后有一张复习时间表，建议收藏。",
        tags=["Vibe知识大赏", "艾宾浩斯遗忘曲线", "记忆方法", "学习方法", "高效学习"],
    ),
)

if __name__ == "__main__":
    run(EP)
