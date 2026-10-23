"""「如果…就…」计划 / If-then plans (implementation intentions) - 75 s, silent, 128 BPM, little people in every scene.

User, 2026-10-23: "我还是想加几个小人，因为有人看着更舒服一点吧" -> engine.figures (ported from money_happiness).
Opening per lessons.md: frame 0 shows the full two-line hook with the figures already moving; the result lands on
beat 8 (3.75 s). Beat grid 128 BPM (beat 0.469 s, bar 1.875 s), cuts on downbeats, no shaking, ends on the last bar.

Facts (checked against the papers; the user supplied the 1997 PDF):
* Gollwitzer & Brandstaetter (1997), JPSP 73(1):186-199.
  Study 2: 86 University of Munich students (volunteers) got the same goal: write a report on how they spent
  Christmas Eve during the 2 holidays after it. Half also formed implementation intentions on when and where to
  start (examples in the paper: "right after breakfast the next morning", "in a quiet corner in the living room").
  Of the 36 returned reports that could be matched to a condition, 71% (12 of 17) vs 32% (6 of 19) were written
  within the 2 days; mean writing time 2.3 vs 7.7 days after Christmas Eve (Table 1).
  Study 1 (correlational, 111 female students): difficult projects completed 62% with vs 22% without implementation
  intentions; easy projects 84% vs 78% (n.s.) -> "use it on what is hard to start".
* Gollwitzer & Sheeran (2006), Advances in Experimental Social Psychology 38:69-119: 94 independent tests,
  medium-to-large effect on goal attainment, d = .65.
* Duckworth, Grant, Loew, Oettingen & Gollwitzer (2011), Educational Psychology 31(1):17-26: 66 high-school students
  preparing for a high-stakes exam; a 30-minute written exercise (mental contrasting + implementation intentions)
  vs a placebo writing exercise: more than 60% more practice questions completed.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import numpy as np                                             # noqa: E402
import skia                                                    # noqa: E402

from engine import core as K                                   # noqa: E402
from engine import figures as F                                # noqa: E402
from engine import scenes as SC                                # noqa: E402
from engine.core import (AMBER, CYAN, DIM, DIMMER, GREEN, PINK, RED, VIOLET, WHITE, W, ap, at, badge, card,  # noqa: E402
                         clamp, e_inout, e_out, icon, lerp, measure, paint, pill, pop, rich, text)
from engine.render import Episode, Scene, run                  # noqa: E402

BPM = 128
ME = F.make(7, hair_style="short", hair="#2B2422", top="#3F6FA6", skin="#F1CBA4", pants="#26324C")
PAL = F.make(12, hair_style="long", hair="#3F2C22", top="#B65D72", skin="#F6D9BC")
SRC_1997 = "Gollwitzer & Brandstätter 1997"


# ----------------------------------------------------------------------------- helpers
def burst(c, x, y, B, b0, color, a=1.0, r0=12, r1=64):
    """ring that expands once when something lands on its beat"""
    k = (B - b0) / 1.0
    if 0 <= k <= 1:
        c.drawCircle(x, y, lerp(r0, r1, e_out(k)), paint(color, a * (1 - k), stroke=3))


def prog(B, b0, b1):
    return e_inout((B - b0) / (b1 - b0))


def walk(B, b0, b1, x0, x1):
    """x + walk phase between beats b0..b1; one step per beat, so the leg swing is fastest exactly on the beats"""
    if B <= b0:
        return x0, None
    if B >= b1:
        return x1, None
    u = (B - b0) / (b1 - b0)
    return lerp(x0, x1, 0.5 - 0.5 * math.cos(math.pi * u)), math.pi * (B - b0)


def writing(t, on=True):
    return 0.06 * math.sin(t * 12) if on else 0.0


def mark_line(c, ok, s, x, y, B, b0, a, accent, size=48, strike_b=None):
    """check / cross badge + text, appears on beat b0; strike_b: red strike-through landing on that beat"""
    k = ap(B, b0, 0.4) * a
    if k <= 0:
        return
    with at(c, x + 26, y, lerp(0.7, 1.0, e_out((B - b0) / 0.35))):
        badge(c, "check" if ok else "x", 0, 0, 22, GREEN if ok else RED, k)
    w = rich(c, s, x + 70, y, size, "black", WHITE if ok else DIM, accent, k, "l")
    if strike_b is not None and B >= strike_b:
        K.strike(c, x + 64, x + 76 + w, y + 2, e_out((B - strike_b) / 0.4), RED, k, 5)


def think(c, x, y, w, h, color, a, tail_to):
    """thought bubble; three small circles lead to tail_to (the head)"""
    if a <= 0.003:
        return
    rect = skia.Rect.MakeXYWH(x, y, w, h)
    c.drawRoundRect(rect, h / 2, h / 2, paint("#0F1A33", 0.95 * a))
    c.drawRoundRect(rect, h / 2, h / 2, paint(color, 0.9 * a, stroke=2.5))
    tx, ty = tail_to
    for i, r in enumerate((10, 7, 4.5)):
        k = (i + 1) / 4
        cx, cy = lerp(x + 46, tx, k), lerp(y + h, ty, k)
        c.drawCircle(cx, cy, r, paint("#0F1A33", 0.95 * a))
        c.drawCircle(cx, cy, r, paint(color, 0.9 * a, stroke=2))


def note_on(c, x, ty, s, a=1.0, written=1.0):
    """sticky note lying on a desk; its lines get written as `written` goes 0 -> 1"""
    w, h = 24 * s, 7 * s
    p = skia.Path()
    p.moveTo(x - w / 2 + 2 * s, ty - h)
    p.lineTo(x + w / 2 + 2 * s, ty - h)
    p.lineTo(x + w / 2, ty)
    p.lineTo(x - w / 2, ty)
    p.close()
    c.drawPath(p, paint("#FDE68A", a))
    n = 3
    for i in range(n):
        frac = clamp(written * n - i)
        if frac <= 0:
            break
        yy = ty - h + (i + 1) * h / (n + 1)
        x0 = x - w / 2 + 4 * s + (1 - (i + 1) / (n + 1)) * 2 * s
        c.drawLine(x0, yy, x0 + (w - 10 * s) * frac, yy, paint("#B45309", a, stroke=1.3 * s))


def stack(c, cx, base, w, hgt, color, a):
    """stack of practice sheets"""
    if hgt <= 1 or a <= 0:
        return
    rect = skia.Rect.MakeXYWH(cx - w / 2, base - hgt, w, hgt)
    c.drawRect(rect, paint("#E2E8F0", 0.92 * a))
    for yy in np.arange(base - hgt + 8, base, 8):
        c.drawLine(cx - w / 2, float(yy), cx + w / 2, float(yy), paint("#94A3B8", 0.7 * a, stroke=1.2))
    c.drawRect(rect, paint(color, 0.9 * a, stroke=2.5))


# ----------------------------------------------------------------------------- hook: same assignment, one sentence apart
L_X, R_X = 560, 1360
HOOK_FLOOR, HOOK_S = 960, 2.9
CROWD_L = F.crowd(19, seed=21)          # Study 2: 19 matched reports without a plan, 6 written in the 2 days
CROWD_R = F.crowd(17, seed=22)          # 17 with a plan, 12 written in the 2 days
LIT_L = [1, 14, 8, 4, 17, 11]                           # 2 per beat on beats 5, 6, 7
LIT_R = [0, 10, 4, 15, 7, 12, 3, 16, 1, 8, 14, 11]       # 4 per beat on beats 5, 6, 7


def crowd_pos(n, cx, i):
    back = (n + 1) // 2
    if i < back:
        return cx + (i - (back - 1) / 2) * 62, 745
    j, front = i - back, n - back
    return cx + (j - (front - 1) / 2) * 62, 850


def draw_crowd(c, crowd, cx, order, per, B, ka):
    lit = 0
    for i, f in enumerate(crowd):                       # back row first
        x, y = crowd_pos(len(crowd), cx, i)
        lb = 5 + order.index(i) // per if i in order else None
        k = ap(B, lb, 0.35) if lb is not None else 0.0
        if lb is not None and B >= lb:
            lit += 1
        if k < 1:
            F.sprite(c, f, x, y, 0.95, ka * 0.42 * (1 - k), mood=0.0)
        if k > 0:
            F.sprite(c, f, x, y, 0.95, ka * k, mood=0.85, arm_r=F.ARM_UP, prop=dict(kind="paper"))
    return lit


def hook_visual(c, S):
    B, t = S.B, S.gt
    flip, land = 4, 8
    p2 = B >= flip
    ov = ap(B, 9, 0.5)                                   # beat 9: the overview replaces the time pill
    if ov < 1:
        lbl = "2 天假期过完" if p2 else "放假前"
        col = AMBER if p2 else DIM
        pw = measure("2 天假期过完", "bold", 40) + 130
        with at(c, W / 2, 548, lerp(1.12, 1.0, e_out((B - flip) / 0.4)) if p2 else 1.0):
            pill(c, 0, 0, pw, 72, col, 1 - ov, fill_a=0.22)
            icon(c, "calendar-days" if p2 else "timer", -pw / 2 + 44, 0, 34, col, 1 - ov)
            text(c, lbl, 22, 0, 40, "bold", WHITE, 1 - ov)
    if ov > 0:
        s_ = "差的就是这一句：如果……，就……"
        pw = measure(s_, "black", 44) + 100
        with at(c, W / 2, 548, lerp(0.9, 1.0, e_out((B - 9) / 0.4))):
            pill(c, 0, 0, pw, 80, AMBER, ov, fill_a=0.22)
            text(c, s_, 0, 0, 44, "black", WHITE, ov)
    text(c, "只定目标", L_X, 615, 40, "bold", DIM, ap(B, 1, 0.4))
    text(c, "+ 写下何时、在哪", R_X, 615, 40, "bold", AMBER, ap(B, 2, 0.4))
    ka = 1 - clamp((B - flip) / 0.6)                     # phase A: the two desks, moving from frame 0
    if ka > 0:
        F.chair(c, L_X, HOOK_FLOOR, HOOK_S, ka)
        F.draw(c, PAL, L_X, HOOK_FLOOR, HOOK_S, ka, mood=0.0, look_y=0.6, arm_l=F.ARM_WRITE, arm_r=F.ARM_WRITE, t=t)
        ty = F.desk(c, L_X, HOOK_FLOOR, 440, HOOK_S, ka)
        F.paper_on(c, L_X, ty, HOOK_S, ka, written=0.0)
        F.chair(c, R_X, HOOK_FLOOR, HOOK_S, ka)
        F.draw(c, ME, R_X, HOOK_FLOOR, HOOK_S, ka, mood=0.6, look=0.4, look_y=0.7, arm_l=F.ARM_WRITE,
               arm_r=F.ARM_WRITE + writing(t), prop=dict(kind="pen"), t=t)
        ty = F.desk(c, R_X, HOOK_FLOOR, 440, HOOK_S, ka)
        F.paper_on(c, R_X - 50, ty, HOOK_S, ka, written=0.0)
        note_on(c, R_X + 48, ty, HOOK_S, ka, written=clamp(0.15 + B / 3.6))
    kb = clamp((B - flip) / 0.6)                         # phase B: who wrote the report within the 2 days
    if kb > 0:
        nl = draw_crowd(c, CROWD_L, L_X, LIT_L, 2, B, kb)
        nr = draw_crowd(c, CROWD_R, R_X, LIT_R, 4, B, kb)
        done = B >= land
        for cx, lit, n, win in ((L_X, nl, 19, False), (R_X, nr, 17, True)):
            num = f"{round(100 * lit / n)}%"
            col = (GREEN if win else RED) if done else WHITE
            nw = measure(num, "mono", 76)
            cnt = f"{lit}/{n} 人"
            cw = measure(cnt, "bold", 40)
            x0 = cx - (nw + 24 + cw) / 2
            text(c, num, x0, 910, 76, "mono", col, kb, "l", glow=GREEN if (done and win) else None, gsig=12)
            text(c, cnt, x0 + nw + 24, 916, 40, "bold", DIM, kb, "l")
            if win:
                burst(c, x0 + nw / 2, 910, B, land, GREEN, 1.0, 20, 120)
        text(c, f"数据：{SRC_1997} · 实验 2 · 按寄回报告的人算", W / 2, 990, 34, "reg", DIM, ap(B, land, 0.5))


# ----------------------------------------------------------------------------- answer
_answer = SC.answer("心理学叫「执行意图」", "如果[时机]，我就[动作]", "IMPLEMENTATION INTENTION · IF-THEN PLAN",
                    [("写清时间地点", "When & where"), ("写具体动作", "One concrete action"),
                     ("干扰也写一句", "Beat distractions")], colors=[CYAN, VIOLET, PINK])


def answer(c, S):
    _answer(c, S)
    F.draw(c, ME, 200, 520, 2.3, ap(S.B, 0, 0.4), mood=0.8, look=0.5, arm_r=F.ARM_UP, prop=dict(kind="note"), t=S.gt)


# ----------------------------------------------------------------------------- step 1: "if" = a moment you will hit
FL = 935                                                 # floor line inside the step cards
RX = 1060                                                # text column inside the step cards


def step1_vis(c, S, x, y, w, h, a):
    B, vb, t = S.B, S.vb, S.gt                           # card on beat vb (= 8)
    s_, TX, DX = 2.4, 430, 860
    F.floor_line(c, 170, 1010, FL, a)
    F.wall_clock(c, 290, 585, 58, 19 * 60 + 44 + 16 * e_out((B - vb) / 4), a)   # 20:00 on beat 12
    burst(c, 290, 585, B, vb + 4, CYAN, a, 58, 110)
    stand, sit = prog(B, vb + 5, vb + 5.6), prog(B, vb + 8, vb + 8.6)          # stand 13, sit 16
    xw, ph = walk(B, vb + 5.6, vb + 8, TX, DX)
    bob = 5 * (1 - stand) + 5 * sit
    if B < vb + 5:                                        # eating: hand to mouth every 2 beats
        arm_r = lerp(F.ARM_WRITE, 2.6, 0.5 - 0.5 * math.cos(math.pi * (B - vb)))
        look, look_y, mood, prop = (-0.9, -0.5, 0.3, None) if B >= vb + 4 else (0.0, 0.4, 0.5, None)
    elif ph is not None or B < vb + 8:
        arm_r, look, look_y, mood, prop = F.ARM_DOWN, 1.0, 0.0, 0.5, None
    else:
        on = B >= vb + 10
        arm_r, look, look_y, mood = F.ARM_WRITE + writing(t, on), 0.3, 0.7, 0.7
        prop = dict(kind="pen") if on else None
    F.chair(c, TX, FL, s_, a)
    F.chair(c, DX, FL, s_, a)
    F.draw(c, ME, xw, FL, s_, a, mood=mood, look=look, look_y=look_y, arm_l=F.ARM_WRITE if ph is None else F.ARM_DOWN,
           arm_r=arm_r, prop=prop, walk=ph, bob=bob, t=t)
    ty = F.desk(c, TX, FL, 290, s_, a, top="#9A3412", front="#7C2D12", edge="#C2410C")
    F.bowl_on(c, TX + 40, ty, s_, a)
    ty = F.desk(c, DX, FL, 270, s_, a)
    F.book_on(c, DX - 20, ty, s_, a, opened=prog(B, vb + 9, vb + 10))
    mark_line(c, False, "今晚找时间背单词", RX, 560, B, vb + 1, a, CYAN, 46, strike_b=vb + 3)
    mark_line(c, True, "如果[晚上 8 点吃完饭]，", RX, 655, B, vb + 4, a, CYAN, 50)
    rich(c, "我就[背 20 个单词]", RX + 70, 725, 50, "black", WHITE, CYAN, ap(B, vb + 10, 0.4) * a, "l")
    kq = ap(B, vb + 14, 0.5) * a
    text(c, "实验里的例子：", RX, 830, 38, "bold", AMBER, kq, "l")
    text(c, "「第二天吃完早饭，客厅安静的角落」", RX, 882, 38, "bold", WHITE, kq, "l")
    text(c, f"{SRC_1997} · 实验 2", RX, 938, 34, "reg", DIM, kq, "l")


# ----------------------------------------------------------------------------- step 2: "then" = one concrete action
def step2_vis(c, S, x, y, w, h, a):
    B, vb, t = S.B, S.vb, S.gt
    s_, DX = 2.5, 520
    F.floor_line(c, 170, 1010, FL, a)
    confused = clamp((B - (vb + 1)) / 0.5) * (1 - clamp((B - (vb + 5)) / 0.5))
    happy = clamp((B - (vb + 6)) / 0.5)
    on = B >= vb + 7
    F.chair(c, DX, FL, s_, a)
    F.draw(c, ME, DX, FL, s_, a, mood=0.3 - 0.6 * confused + 0.45 * happy, look=0.6 * confused,
           look_y=0.6 - 1.4 * confused, arm_l=F.ARM_WRITE, arm_r=F.ARM_WRITE + writing(t, on),
           prop=dict(kind="pen") if on else None, bob=5, t=t)
    ty = F.desk(c, DX, FL, 330, s_, a)
    F.book_on(c, DX + 40, ty, s_, a, opened=prog(B, vb + 6, vb + 7))             # opens on beat 14
    head = (565, 690)
    k1 = ap(B, vb + 1, 0.4) * a * (1 - clamp((B - (vb + 5)) / 0.5))              # "好好学习" 9 -> crossed 12 -> gone 13
    crossed = B >= vb + 4
    think(c, 610, 500, 330, 100, RED if crossed else DIM, k1, head)
    text(c, "好好学习", 775, 550, 52, "black", DIM, k1 * 0.75, glow=DIM, gsig=10, glow_a=0.9)
    if crossed and k1 > 0:
        with at(c, 935, 505, lerp(0.6, 1.0, e_out((B - vb - 4) / 0.35))):
            badge(c, "x", 0, 0, 24, RED, k1)
    kq = ap(B, vb + 2, 0.3) * a * (1 - clamp((B - (vb + 5)) / 0.5))
    for qx, qy in ((425, 680), (640, 650)):
        text(c, "?", qx, qy, 56, "black", AMBER, kq)
    k2 = ap(B, vb + 5, 0.4) * a                                                   # beat 13
    with at(c, 820, 550, lerp(0.85, 1.0, e_out((B - vb - 5) / 0.4))):
        think(c, -230, -50, 460, 100, VIOLET, k2, (head[0] - 820, head[1] - 550))
        text(c, "打开练习册第 32 页", 0, 0, 40, "black", WHITE, k2)
    rx = 1110
    mark_line(c, False, "就好好学习", rx, 560, B, vb + 1, a, VIOLET, 50, strike_b=vb + 4)
    mark_line(c, True, "就[打开练习册第 32 页]", rx, 650, B, vb + 5, a, VIOLET, 50)
    ke = ap(B, vb + 12, 0.5) * a                                                  # beat 20: not a one-off
    rich(c, "[94] 组实验汇总：效果中到大", rx, 790, 44, "black", WHITE, VIOLET, ke, "l")
    fill = e_out((B - vb - 12) / 2)
    for i in range(94):
        col_, row = divmod(i, 2)
        k = ke * (1.0 if i / 94 < fill else 0.25)
        c.drawCircle(rx + 6 + col_ * 13, 852 + row * 20, 5, paint(VIOLET if i / 94 < fill else DIMMER, k))
    text(c, "d = 0.65 · Gollwitzer & Sheeran 2006", rx, 935, 34, "reg", DIM, ke, "l")


# ----------------------------------------------------------------------------- step 3: one more line for the distraction
def step3_vis(c, S, x, y, w, h, a):
    B, vb, t = S.B, S.vb, S.gt
    s_, DX, DOOR = 2.4, 430, 900
    F.floor_line(c, 170, 1010, FL, a)
    door_k = prog(B, vb + 7, vb + 7.6) * (1 - prog(B, vb + 9, vb + 9.6))          # opens 15, closes 17
    F.door(c, DOOR, FL, s_, door_k, a)
    stand, sit = prog(B, vb + 4, vb + 4.5), prog(B, vb + 12, vb + 12.5)          # stand 12, sit 20
    at_door = DOOR - 90
    if B < vb + 9.5:
        xw, ph = walk(B, vb + 4.5, vb + 7, DX, at_door)
    else:
        xw, ph = walk(B, vb + 9.5, vb + 12, at_door, DX)
    holding = vb + 4 <= B < vb + 8
    reach = prog(B, vb + 3, vb + 4) if B < vb + 4.5 else (prog(B, vb + 7.5, vb + 8) * (1 - prog(B, vb + 8.5, vb + 9)))
    on = B >= vb + 13
    if B >= vb + 12:
        look, look_y, mood = 0.3, 0.7, 0.75
    elif B >= vb + 9.5:
        look, look_y, mood = -1.0, 0.0, 0.6
    elif B >= vb + 2:
        look, look_y, mood = 1.0, 0.2, 0.15
    else:
        look, look_y, mood = 0.0, 0.6, 0.4
    arm_r = (F.ARM_WRITE + writing(t, on)) if B >= vb + 12.5 else lerp(F.ARM_DOWN if ph is not None else F.ARM_WRITE,
                                                                       F.ARM_OUT, reach)
    F.chair(c, DX, FL, s_, a)
    prop = dict(kind="phone", lit=1.0) if holding else (dict(kind="pen") if on else None)
    F.draw(c, ME, xw, FL, s_, a, mood=mood, look=look, look_y=look_y, arm_l=F.ARM_WRITE if ph is None else F.ARM_DOWN,
           arm_r=arm_r, prop=prop, walk=ph, bob=5 * (1 - stand) + 5 * sit, t=t)
    ty = F.desk(c, DX, FL, 300, s_, a)
    F.book_on(c, DX - 40, ty, s_, a, opened=1.0)
    if B < vb + 4:                                        # phone on the desk buzzes on beats 9, 10, 11
        buzz = (B - vb - 1) % 1.0 if vb + 1 <= B < vb + 4 else 0.0
        F.phone_on(c, DX + 100, ty, s_, a, lit=1.0 if B >= vb + 1 else 0.0, buzz=buzz)
    if vb + 8 <= B < vb + 8.6:                            # beat 16: the phone goes out through the door
        u = e_out((B - vb - 8) / 0.6)
        hx, hy = F.hand_pos(1, F.ARM_OUT)
        px, py = lerp(at_door + hx * s_, DOOR + 10, u), lerp(FL + (hy - 8) * s_, FL - 140, u)
        with at(c, px, py, lerp(1.0, 0.5, u)):
            c.drawRoundRect(skia.Rect.MakeXYWH(-10, -17, 20, 34), 5, 5, paint("#96F0D2", a * (1 - u)))
    ke = ap(B, vb + 13, 0.5) * a                                                  # beat 21: the evidence
    text(c, "66 名美国高中生备考", RX, 545, 44, "bold", AMBER, ke, "l")
    text(c, "Duckworth 等 2011", RX, 595, 34, "reg", DIM, ke, "l")
    g = e_out((B - vb - 14) / 2)                                                  # stacks grow 22 -> land 24
    stack(c, 1210, 840, 170, 120 * g, DIM, ke)
    stack(c, 1530, 840, 170, 192 * g, PINK, ke)
    text(c, "对照组", 1210, 880, 36, "bold", DIM, ke)
    text(c, "写下障碍 + 如果…就…", 1530, 880, 36, "bold", PINK, ke)
    kl = ap(B, vb + 16, 0.4) * a
    text(c, "+60%", 1530, 615, 56, "mono", PINK, kl, glow=PINK, gsig=12)
    burst(c, 1530, 648, B, vb + 16, PINK, a, 20, 110)
    rich(c, "多做了[六成以上]的练习题", 1390, 940, 44, "black", WHITE, PINK, ap(B, vb + 17, 0.5) * a)


# ----------------------------------------------------------------------------- summary: fill in the template
def blank(c, x, y, w, hint, color, a):
    c.drawLine(x, y + 34, x + w, y + 34, paint(color, 0.95 * a, stroke=3))
    text(c, hint, x + w / 2, y, 36, "bold", DIM, a)


SUM_CX = 860


def summary(c, S):
    B = S.B
    k = ap(B, 0)
    text(c, "一图总结 · 照着填", W / 2, 140, 80, "black", WHITE, k, glow=CYAN, gsig=14, glow_a=0.5)
    text(c, "Fill in the blanks", W / 2, 222, 36, "monor", CYAN, k)
    rows = [(2, CYAN, [("t", "如果"), ("b", "什么时候 · 在哪", 380), ("t", "，我就"), ("b", "一个具体动作", 330)],
             "If (when & where), then I will (one action)"),
            (4, PINK, [("t", "如果"), ("b", "最常打断你的事", 380), ("t", "，我就"), ("b", "怎么应对", 330)],
             "If (my biggest distraction), then I will (...)"),
            (6, AMBER, [("r", "先用在[最难开始]的那件事上")], "Start with the task you put off most")]
    for i, (b0, col, parts, en) in enumerate(rows):
        kk = ap(B, b0, 0.4)
        if kk <= 0:
            continue
        y = 290 + i * 184
        with at(c, SUM_CX, y + 85, pop(B, b0, 0.6, 0.85)):
            card(c, -650, -85, 1300, 170, kk, col, r=18, brackets=False)
            text(c, f"{i + 1:02d}", -575, 0, 64, "mono", col, kk, glow=col, gsig=8)
            xx = -480
            for part in parts:
                if part[0] == "t":
                    xx += text(c, part[1], xx, -16, 60, "black", WHITE, kk, "l")
                elif part[0] == "r":
                    xx += rich(c, part[1], xx, -16, 60, "black", WHITE, col, kk, "l")
                else:
                    blank(c, xx + 12, -16, part[2], part[1], col, kk)
                    xx += part[2] + 24
            text(c, en, -478, 46, 34, "monor", DIM, kk, "l")
    kh = ap(B, 8, 0.5)
    pill(c, SUM_CX, 955, 460, 70, AMBER, kh * (0.8 + 0.2 * K.beat_pulse(S.t, S.beat)))
    text(c, "截图保存 · Screenshot", SUM_CX, 955, 36, "bold", WHITE, kh)
    F.draw(c, ME, 1690, 880, 2.6, ap(B, 0, 0.4), mood=0.8, look=-1.0, arm_l=F.ARM_OUT, t=S.gt)


summary.static_region = (460, 95, 1460, 245)
summary.static_after = 1.5


# ----------------------------------------------------------------------------- cta
_cta = SC.cta("评论区写下你的[如果…就…]", "Write yours in the comments", options=None, end_card=False)


def cta(c, S):
    _cta(c, S)
    F.draw(c, ME, 220, 930, 3.0, ap(S.B, 0, 0.4), mood=0.9, look=0.4, arm_r=2.25 + 0.35 * math.sin(math.pi * S.B),
           t=S.gt)


# ----------------------------------------------------------------------------- 3:4 cover (Douyin profile grid)
def cover(c):
    CW, CH = 1080, 1440
    c.drawPaint(paint("#020617", shader=skia.GradientShader.MakeRadial(
        (CW / 2, CH * 0.42), 1150, [K.rgb("#13224A"), K.rgb("#070D1F"), K.rgb("#02040A")], [0, 0.55, 1])))
    g = paint("#1D3A6B", 0.22, stroke=1, cap_round=False)
    for gx in range(0, CW + 1, 60):
        c.drawLine(gx, 0, gx, 1060, g)
    for gy in range(0, 1061, 60):
        c.drawLine(0, gy, CW, gy, g)
    c.drawRect(skia.Rect.MakeXYWH(0, 1060, CW, CH - 1060), paint("#030712", 0.7))
    for k in range(-10, 11):
        c.drawLine(CW / 2 + k * 30, 1060, CW / 2 + k * 200, CH, paint(CYAN, 0.12, stroke=1.3, cap_round=False))
    c.drawRect(skia.Rect.MakeXYWH(0, 1058, CW, 4), paint(CYAN, 0.45, blur=6))
    text(c, "同一份作业", CW / 2, 190, 120, "black", WHITE, 1, glow=CYAN, gsig=18, glow_a=0.35)
    rich(c, "差[一句话]", CW / 2, 385, 210, "black", WHITE, AMBER, 1)
    for cx, lbl, col, num, ncol, who, mood, pl in ((290, "只定目标", DIM, "32%", DIM, PAL, -0.3, False),
                                                   (790, "+ 写下何时、在哪", AMBER, "71%", GREEN, ME, 0.85, True)):
        text(c, lbl, cx, 560, 46, "bold", col, 1)
        text(c, num, cx, 675, 128, "mono", ncol, 1, glow=GREEN if pl else None, gsig=18)
        F.chair(c, cx, 1060, 2.7)
        F.draw(c, who, cx, 1060, 2.7, 1.0, mood=mood, look_y=0.6, arm_l=F.ARM_WRITE,
               arm_r=F.ARM_WRITE, prop=dict(kind="pen") if pl else None, blink=False)
        ty = F.desk(c, cx, 1060, 400, 2.7)
        F.paper_on(c, cx - (55 if pl else 0), ty, 2.7, written=0.0)
        if pl:
            note_on(c, cx + 60, ty, 2.7, written=1.0)
    s_ = "1 分钟学会「如果…就…」"
    pw = measure(s_, "black", 54) + 120
    pill(c, CW / 2, 1190, pw, 104, AMBER, 1, fill_a=0.22)
    text(c, s_, CW / 2, 1190, 54, "black", WHITE, 1)


# ----------------------------------------------------------------------------- episode
EP = Episode(
    slug="if_then_plan",
    title="如果…就…计划",
    bpm=BPM,
    music=False,
    tail=0.0,
    fade_out=0.0,
    scenes=[
        Scene("hook", 4, SC.hook("同一份作业|差[一句话]", "Same assignment. One sentence apart.", accent=AMBER,
                                 visual=hook_visual), chapter="差一句话"),
        Scene("answer", 4, answer, chapter="如果…就…"),
        Scene("step1", 8, SC.step(1, "如果：写一个时机", "IF: a moment you can't miss",
                                  [("写一个[一定会遇到]的时间或地点", "A time or place you're sure to hit")],
                                  visual=step1_vis, color=CYAN), chapter="3 个写法"),
        Scene("step2", 8, SC.step(2, "就：写一个具体动作", "THEN: one concrete action",
                                  [("写一个[到点就能开始]的动作", "An action you can start the moment it comes")],
                                  visual=step2_vis, color=VIOLET), chapter="3 个写法"),
        Scene("step3", 8, SC.step(3, "干扰也写一句", "Plan for your biggest distraction",
                                  [("[如果想刷手机]，我就把它放到门外", "If I want my phone, it goes outside the door")],
                                  visual=step3_vis, color=PINK), chapter="3 个写法"),
        Scene("summary", 4, summary, chapter="照着填"),
        Scene("cta", 4, cta, chapter="照着填"),
    ],
    cover=cover,
    cover_size=(1080, 1440),
    publish=dict(
        title="Vibe知识大赏/拖延的人，少写了一句话",
        desc="你的「如果…就…」是什么？写在评论区。"
             "同一份作业，差一句话：实验里，大学生要在圣诞假期写一份报告，其中一半人事先写下了「什么时候、在哪写」。"
             "寄回报告的人里，写了的 71% 按时写完，没写的只有 32%。"
             "把 94 组实验汇总起来，这个方法的效果中到大。"
             "3 个写法：「如果」后面写一个一定会遇到的时机，「就」后面写一个具体动作，再给最常打断你的事也写一句。"
             "最后有一张照着填的模板，建议收藏。",
        tags=["Vibe知识大赏", "拖延症", "执行意图", "学习方法", "自律", "高效学习"],
        pin="评论区写下你的「如果…就…」，比如：如果晚上 8 点吃完饭，我就背 20 个单词。你的呢？",
    ),
)

if __name__ == "__main__":
    run(EP)
