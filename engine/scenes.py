"""Scene factories for the proven short structure (60-75 s):

    hook (4 bars)  -> answer (4)  -> step x N (8 each, example inside the step)  -> summary (4)  -> cta (4)

Timing is on the beat grid (S.B = local beat): every element appears exactly ON a beat, new content
every 1-2 bars, so the cut works with a four-on-the-floor ("动次打次") track at Episode.bpm.
Use scene lengths of 4 or 8 bars (DJ phrases are 4/8/16 bars).

Each factory returns fn(c, S). Content strings support [keyword] highlighting.
Sizes follow the phone-feed readability rules (headline >= 96, main >= 64, English >= 36).
For special visuals (charts, diagrams) pass visual=fn(c, S, x, y, w, h, a) to step(), or write
your own scene function with the primitives in engine.core.
"""
import math

import skia

from . import core as K
from .core import (AMBER, CYAN, DIM, DIMMER, GREEN, PINK, RED, VIOLET, WHITE, W, ap, at, badge, card, e_back,
                   e_inout, icon, lerp, measure, pill, pop, rich, text)

STEP_COLORS = [CYAN, VIOLET, PINK, AMBER, GREEN]


def _typed(c, s, B, b0, x, y, size, color, a=1.0, cps=14):
    shown, cur = K.type_on(s, B, b0, cps)
    text(c, shown + ("_" if cur or int(B * 2) % 2 else " "), x, y, size, "mono", color, a)


# ----------------------------------------------------------------------------- hook
def hook(question, en, pains=(), accent=PINK):
    """question: '为什么你[背了就忘]？'
    pains: [(icon, line1, line2_red, en)] up to 3 cards under the question; keep en <= 22 chars"""
    def fn(c, S):
        B = S.B
        qs = min(124, 1600 * 100 / max(1, K.rich_width(question, 100)))
        qw = K.rich_width(question, qs)
        s = pop(B, 0, 0.5, max(1.0, min(1.25, 1780 / max(1, qw * 1.07))), 0.8)   # one smooth zoom-in, no jitter
        with at(c, W / 2, 300, s):
            rich(c, question, 0, 0, qs, "black", WHITE, accent, ap(B, 0, 0.3))
        _typed(c, en, B, 1.0, W / 2, 425, 42, CYAN, cps=16)
        n = len(pains)
        if n:
            cw, gap = 540, 30
            x0 = W / 2 - (n * cw + (n - 1) * gap) / 2
            for i, (ic, l1, l2, pen) in enumerate(pains):
                b0 = 4 + i * 2          # beats 4, 6, 8
                k = ap(B, b0, 0.5)
                if k <= 0:
                    continue
                x, y = x0 + i * (cw + gap), 520 + (1 - k) * 40
                col = STEP_COLORS[i % 3]
                card(c, x, y, cw, 380, k, col)
                badge(c, ic, x + cw / 2, y + 72, 38, col, k)
                text(c, l1, x + cw / 2, y + 168, 52, "bold", WHITE, k)
                text(c, l2, x + cw / 2, y + 250, 68, "black", RED, ap(B, b0 + 1, 0.4), glow=RED, gsig=12, glow_a=0.6)
                text(c, pen, x + cw / 2, y + 328, 36, "monor", DIM, k)
    return fn


# ----------------------------------------------------------------------------- answer (payoff within 10 s)
def answer(lead, headline, en, steps, save_hint=("建议先收藏", "Save this"), accent=CYAN, colors=None):
    """lead: '答案：'  headline: '用[费曼学习法]'  steps: [(cn, en)] 2-4 items shown as an overview row
    colors: per-step colours (match the step scenes)"""
    def fn(c, S):
        B = S.B
        text(c, lead, W / 2, 190, 60, "bold", DIM, ap(B, 0, 0.4))
        with at(c, W / 2, 330, pop(B, 1, 0.6, 1.3)):
            rich(c, headline, 0, 0, 120, "black", WHITE, accent, ap(B, 1, 0.3))
        text(c, en, W / 2, 445, 40, "mono", accent, ap(B, 2, 0.5))
        n = len(steps)
        gap = 36
        cw = min(440, (1680 - (n - 1) * gap) / n)
        x0 = W / 2 - (n * cw + (n - 1) * gap) / 2
        for i, (cn, sen) in enumerate(steps):
            b0 = 4 + i                  # one card per beat
            k = ap(B, b0, 0.4)
            if k <= 0:
                continue
            col = (colors or STEP_COLORS)[i % len(colors or STEP_COLORS)]
            x = x0 + i * (cw + gap)
            with at(c, x + cw / 2, 680, pop(B, b0, 0.7, 0.7)):
                card(c, -cw / 2, -120, cw, 240, k, col, brackets=False)
                text(c, f"{i + 1:02d}", 0, -62, 64, "mono", col, k, glow=col, gsig=10)
                text(c, cn, 0, 22, 56, "black", WHITE, k)
                text(c, sen, 0, 82, 36, "monor", DIM, k)
            if i < n - 1 and k > 0.5:
                text(c, "→", x + cw + gap / 2, 680, 44, "bold", DIMMER, k, free=True)
        if save_hint:
            k = ap(B, 4 + n + 1, 0.5)
            pulse = 0.75 + 0.25 * K.beat_pulse(S.t, S.beat)
            pill(c, W / 2, 925, 520, 76, AMBER, k * pulse)
            icon(c, "star", W / 2 - 200, 925, 36, AMBER, k)
            text(c, f"{save_hint[0]} · {save_hint[1]}", W / 2 + 22, 925, 38, "bold", WHITE, k)
    return fn


# ----------------------------------------------------------------------------- step
def step(num, cn, en, points, example=None, visual=None, color=None, splash_beats=4):
    """
    Beat plan: splash bar 1 (beats 0-4) -> header docks + point 1 on beat 4 -> one more point per bar
               -> card on the next bar line (S.vb = that beat) -> example lines every bar.
    points:  [(cn, en)]  1-2 key lines, [keyword] highlight, 64 px
    example: (label_cn, label_en, [(cn, en), ...])  text example card (lines 54 px)
    visual:  fn(c, S, x, y, w, h, a) custom drawing inside the card; time it from S.vb (card beat)
    """
    col = color or STEP_COLORS[(num - 1) % len(STEP_COLORS)]

    def fn(c, S):
        B = S.B
        k = e_inout((B - splash_beats) / 0.5)
        if k < 1:
            a = ap(B, 0, 0.3) * (1 - k)
            with at(c, W / 2, 440, lerp(1.25, 1.0, e_back(B / 0.7))):
                text(c, "STEP", 0, -200, 44, "mono", col, a, ls=14)
                text(c, f"{num:02d}", 0, -50, 220, "mono", col, a * 0.9, stroke=3.5, glow=col, gsig=22)
                text(c, cn, 0, 130, 96, "black", WHITE, a, glow=col, gsig=14, glow_a=0.6)
                text(c, en, 0, 225, 42, "monor", col, a)
        if k > 0:
            x = lerp(520, 140, k)
            text(c, f"{num:02d}", x, 150, 96, "mono", col, k, "l", stroke=2.4, glow=col, gsig=12)
            text(c, cn, x + 160, 128, 66, "black", WHITE, k, "l", glow=col, gsig=10, glow_a=0.5)
            text(c, en, x + 162, 192, 36, "monor", col, k, "l")
            c.drawRect(skia.Rect.MakeXYWH(140, 240, 1640 * ap(B, splash_beats, 1.0), 3), K.paint(col, 0.5 * k))
        b = splash_beats
        for i, (pcn, pen) in enumerate(points):
            kk = ap(B, b, 0.5)
            if kk > 0:
                y = 330 + i * 130 + (1 - kk) * 26
                badge(c, "check", 172, y, 26, col, kk)
                rich(c, pcn, 222, y, 64, "black", WHITE, col, kk, "l")
                text(c, pen, 224, y + 58, 36, "monor", DIM, kk * 0.95, "l")
            b += 4
        if example or visual:
            ky = 330 + len(points) * 130 + 10
            kh = 1000 - ky - 30 if visual else min(1000 - ky - 30, 150 + len(example[2]) * 118)
            ka = ap(B, b, 0.5)
            S.vb = b
            card(c, 140, ky, 1640, kh, ka, col, r=20)
            if visual:
                visual(c, S, 140, ky, 1640, kh, ka)
            else:
                lab, lab_en, lines = example
                badge(c, "lightbulb", 200, ky + 62, 28, AMBER, ka)
                text(c, lab, 248, ky + 50, 40, "bold", AMBER, ka, "l")
                text(c, lab_en, 250 + measure(lab, "bold", 40) + 18, ky + 52, 34, "monor", DIM, ka, "l")
                yy = ky + 140
                for j, (lcn, len_) in enumerate(lines):
                    kj = ap(B, b + 2 + j * 4, 0.5)
                    if kj > 0:
                        rich(c, lcn, 200, yy, 54, "black", WHITE, AMBER, kj, "l")
                        if len_:
                            text(c, len_, 202, yy + 52, 34, "monor", DIM, kj, "l")
                    yy += 118
    fn.static_region = (140, 100, 700, 220)     # docked header: must not move once docked (shake check)
    fn.static_after = splash_beats + 1.5
    return fn


# ----------------------------------------------------------------------------- summary (screenshot card)
def summary(title, en, items, accent=CYAN, hint=("截图保存", "Screenshot")):
    """items: [(cn, en)] 2-4 rows"""
    def fn(c, S):
        B = S.B
        k = ap(B, 0)
        text(c, title, W / 2, 140, 80, "black", WHITE, k, glow=accent, gsig=14, glow_a=0.5)
        text(c, en, W / 2, 222, 36, "monor", accent, k)
        n = len(items)
        rh = min(170, (620 - 14 * (n - 1)) / n)
        for i, (cn, ien) in enumerate(items):
            b0 = 2 + i * 2              # every half bar
            kk = ap(B, b0, 0.4)
            if kk <= 0:
                continue
            col = STEP_COLORS[i % len(STEP_COLORS)]
            y = 290 + i * (rh + 14)
            with at(c, W / 2, y + rh / 2, pop(B, b0, 0.6, 0.85)):
                card(c, -720, -rh / 2, 1440, rh, kk, col, r=18, brackets=False)
                text(c, f"{i + 1:02d}", -640, 0, 64, "mono", col, kk, glow=col, gsig=8)
                rich(c, cn, -540, -18, 60, "black", WHITE, col, kk, "l")
                text(c, ien, -538, 40, 34, "monor", DIM, kk, "l")
        if hint:
            kh = ap(B, 2 + n * 2, 0.5)
            pill(c, W / 2, 955, 460, 70, AMBER, kh * (0.8 + 0.2 * K.beat_pulse(S.t, S.beat)))
            text(c, f"{hint[0]} · {hint[1]}", W / 2, 955, 36, "bold", WHITE, kh)
    fn.static_region = (460, 95, 1460, 245)     # title
    fn.static_after = 1.5
    return fn


# ----------------------------------------------------------------------------- cta / end card
def cta(question, q_en, end_title, end_en, next_teaser=None):
    """question: comment prompt. Last 2 bars: end title (+ optional next-episode teaser (cn, en))."""
    def fn(c, S):
        B = S.B
        end_b = (S.bars - 2) * 4
        out = 1 - K.clamp((B - end_b) / 0.8)
        if out > 0:
            k = ap(B, 0, 0.4) * out
            qw = K.rich_width(question, 72)
            badge(c, "message-circle", W / 2 - qw / 2 - 70, 220, 44, VIOLET, k)
            rich(c, question, W / 2 + 10, 220, 72, "black", WHITE, VIOLET, k)
            text(c, q_en, W / 2, 300, 38, "monor", DIM, k)
            for i, (ic, cn, ien, col) in enumerate([("heart", "点赞", "LIKE", PINK), ("star", "收藏", "SAVE", AMBER),
                                                     ("user-plus", "关注", "FOLLOW", CYAN)]):
                b0 = 2 + i                  # beats 2, 3, 4
                kk = ap(B, b0, 0.4) * out
                if kk <= 0:
                    continue
                with at(c, W / 2 + (i - 1) * 400, 600, pop(B, b0, 0.7, 0.4, 2.4)):
                    c.drawCircle(0, -20, 90, K.paint(col, 0.14 * kk))
                    c.drawCircle(0, -20, 90, K.paint(col, 0.9 * kk, stroke=3))
                    c.drawCircle(0, -20, 104, K.paint(col, 0.35 * kk, blur=18))
                    icon(c, ic, 0, -20, 80, col, kk, sw=2.2)
                    text(c, cn, 0, 125, 52, "black", WHITE, kk)
                    text(c, ien, 0, 182, 34, "mono", col, kk, ls=4)
        k = ap(B, end_b, 0.5) * (1 - K.clamp((B - (S.bars * 4 + 2)) / 2))
        if k > 0:
            text(c, end_title, W / 2, 400, 130, "black", WHITE, k, glow=CYAN, gsig=24,
                 shader=K.grad_shader("#E0F7FF", "#B9A8FF"))
            text(c, end_en, W / 2, 520, 40, "mono", CYAN, k, ls=8)
            if next_teaser:
                kt = ap(B, end_b + 2, 0.5) * (1 - K.clamp((B - (S.bars * 4 + 2)) / 2))
                tw = measure(next_teaser[0], "bold", 46)
                pw = max(900, tw + 260)
                pill(c, W / 2, 680, pw, 96, AMBER, kt)
                text(c, "下期", W / 2 - pw / 2 + 50, 680, 42, "black", AMBER, kt, "l")
                text(c, next_teaser[0], W / 2 - pw / 2 + 160, 680, 46, "bold", WHITE, kt, "l")
                text(c, next_teaser[1], W / 2, 775, 36, "monor", DIM, kt)
    return fn


# ----------------------------------------------------------------------------- cover
def cover(kicker, title, en, pill_text, sub, accent=PINK):
    def fn(c):
        K.bg_dark_tech(c, 3.3, 60 / 136)
        for i in range(3):
            with at(c, W / 2, 470, 1.0, i * 60 + 20):
                c.drawOval(skia.Rect.MakeXYWH(-640, -170, 1280, 340), K.paint(K.BLUE, 0.3, stroke=2))
        text(c, kicker, W / 2, 230, 96, "black", accent, 1, glow=accent, gsig=16)
        tsize = min(230, 1700 / max(1, len(title)))
        text(c, title, W / 2, 450, tsize, "black", WHITE, 1, glow=CYAN, gsig=30,
             shader=K.grad_shader("#E0F7FF", "#B9A8FF"))
        text(c, en, W / 2, 610, 52, "mono", CYAN, 1, ls=10)
        pw = max(700, measure(pill_text, "black", 62) + 160)
        pill(c, W / 2, 760, pw, 110, AMBER, 1, fill_a=0.22)
        text(c, pill_text, W / 2, 760, 62, "black", WHITE, 1)
        text(c, sub, W / 2, 900, 40, "bold", DIM, 1)
    return fn
