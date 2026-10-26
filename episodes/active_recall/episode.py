"""主动回忆 / Active recall — 75 s, silent (the user adds a four-on-the-floor DJ track), stable picture.

Beat grid: 128 BPM (beat 0.469 s, bar 1.875 s). Scenes are 4 or 8 bars, cuts on downbeats, every element
appears on a beat. No frame shaking. No next-episode teaser: the CTA is the last screen, no fade.

Facts (checked against the papers):
* Roediger & Karpicke (2006), Psychological Science 17(3):249-255, Experiment 2: 180 students, four learning periods.
  SSSS read the passage in all 4 periods (14.2 readings in total); STTT studied in 1 period (3.4 readings), then took
  3 free-recall tests. One week later: SSSS 40%, STTT 61%. Study periods were 5 min, tests 10 min, so the groups had
  the same number of rounds, NOT the same time. SSSS were the most confident (4.8 vs 4.0 on a 7-point scale).
* Karpicke & Roediger (2008), Science 319:966-968: 40 Swahili-English word pairs. One week later ~80% were recalled when
  pairs kept being tested, 33-36% when pairs were dropped from testing after the first correct recall.
* Dunlosky et al. (2013): practice testing / distributed practice rated "high utility", rereading / highlighting "low".
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import skia                                                    # noqa: E402

from engine import core as K                                   # noqa: E402
from engine import scenes as SC                                # noqa: E402
from engine.core import (AMBER, CYAN, DIM, DIMMER, GREEN, RED, VIOLET, WHITE, ap, at, badge, card,  # noqa: E402
                         e_out, icon, lerp, measure, paint, pill, rich, text)
from engine.render import Episode, Scene, run                  # noqa: E402

BPM = 128


# ----------------------------------------------------------------------------- helpers
def burst(c, x, y, B, b0, color, a=1.0, r0=12, r1=64):
    """ring that expands once when something lands on its beat"""
    k = (B - b0) / 1.0
    if 0 <= k <= 1:
        c.drawCircle(x, y, lerp(r0, r1, e_out(k)), paint(color, a * (1 - k), stroke=3))


def tile(c, cx, cy, w, h, label, color, k, B, b0):
    """one learning round: appears on its beat (gentle scale-in, no overshoot)"""
    if k <= 0:
        return
    with at(c, cx, cy, lerp(0.75, 1.0, e_out((B - b0) / 0.35))):
        rect = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
        c.drawRoundRect(rect, 12, 12, paint(color, 0.22 * k))
        c.drawRoundRect(rect, 12, 12, paint(color, 0.9 * k, stroke=2.5))
        text(c, label, 0, 0, 40, "black", WHITE, k, free=True)


def bar(c, cx, yb, bw, hmax, value, vmax, color, B, b0, b1, a, label, label_color, value_text, glow=False):
    """vertical bar that grows from beat b0 and lands ON beat b1"""
    u = e_out((B - b0) / (b1 - b0))
    if u <= 0 or a <= 0:
        return
    hgt = hmax * value / vmax * u
    rect = skia.Rect.MakeXYWH(cx - bw / 2, yb - hgt, bw, hgt)
    if glow:
        c.drawRoundRect(rect, 10, 10, paint(color, 0.35 * a, blur=18))
    c.drawRoundRect(rect, 10, 10, paint(color, 0.85 * a))
    text(c, value_text, cx, yb - hgt - 40, 56, "mono", WHITE, ap(B, b1, 0.3) * a,
         glow=color if glow else None, gsig=12)
    text(c, label, cx, yb + 40, 38, "bold", label_color, a)
    if glow:
        burst(c, cx, yb - hgt, B, b1, color, a)


# ----------------------------------------------------------------------------- step 1: the experiment
def experiment(c, S, x, y, w, h, a):
    B, vb = S.B, S.vb                                      # card appears on beat vb (= 8)
    text(c, "实验：两组都学 4 轮", 200, 530, 44, "bold", AMBER, a, "l")
    lanes = [("A 组 · 4 轮都在读", "读读读读", "共读[14]遍", vb + 1, 605),
             ("B 组 · 读 1 轮，再考 3 轮", "读考考考", "共读[3]遍", vb + 7, 755)]
    for lbl, rounds, cnt, b0, ly in lanes:                 # label, 4 rounds (one per beat), counter
        text(c, lbl, 200, ly, 40, "bold", WHITE, ap(B, b0, 0.4) * a, "l")
        for i, ch in enumerate(rounds):
            bb = b0 + 1 + i
            tile(c, 275 + i * 162, ly + 66, 150, 64, ch, CYAN if ch == "考" else DIM, ap(B, bb, 0.35) * a, B, bb)
        rich(c, cnt, 885, ly + 66, 44, "black", WHITE, AMBER, ap(B, b0 + 5, 0.4) * a, "l")
    kh = ap(B, vb + 12, 0.4) * a                           # beat 20: results
    text(c, "一周后还记得", 1465, 530, 44, "bold", WHITE, kh)
    c.drawLine(1240, 845, 1690, 845, paint(DIMMER, 0.8 * kh, stroke=2))
    bar(c, 1340, 845, 140, 225, 40, 70, DIM, B, vb + 13, vb + 14, kh, "A 重读", DIM, "40%")
    bar(c, 1590, 845, 140, 225, 61, 70, CYAN, B, vb + 15, vb + 16, kh, "B 考自己", CYAN, "61%", glow=True)
    rich(c, "可是 A 组反而觉得自己[记得最牢]", 200, 885, 44, "black", WHITE, AMBER, ap(B, vb + 18, 0.5) * a, "l")
    text(c, "数据：Roediger & Karpicke 2006 · 实验 2 · 1 周后测试", 200, 942, 34, "reg", DIM, a, "l")


# ----------------------------------------------------------------------------- steps 2-3: the dictation sheet
WORDS = [("环境", "environment", "environment"),          # (prompt, what was written, correct answer)
         ("机会", "oppotunity", "opportunity"),
         ("必要的", "necessary", "necessary"),
         ("影响", "influence", "influence"),
         ("解释", "", "explain")]
ROW_Y = [608 + 66 * i for i in range(len(WORDS))]


def sheet(c, a, title, title_en, ic, col):
    card(c, 190, 495, 850, 425, a, col, r=16, fill="#0F1A33", fill_a=0.92, brackets=False, glow=False)
    icon(c, ic, 232, 542, 36, col, a)
    text(c, title, 266, 542, 40, "bold", WHITE, a, "l")
    text(c, title_en, 266 + measure(title, "bold", 40) + 20, 544, 34, "monor", DIM, a, "l")
    for i, (cn, _, _) in enumerate(WORDS):
        yy = ROW_Y[i]
        text(c, cn, 230, yy, 44, "black", WHITE, a, "l")
        c.drawLine(480, yy + 28, 930, yy + 28, paint(DIMMER, 0.8 * a, stroke=2))


def dictation(c, S, x, y, w, h, a):
    B, vb = S.B, S.vb
    sheet(c, a, "合上书默写", "No peeking", "eye-off", VIOLET)
    for i, (cn, wr, _) in enumerate(WORDS):                # one row every half bar: beats 10, 12, 14, 16, 18
        bt = vb + 2 + 2 * i
        if B < bt:
            continue
        yy = ROW_Y[i]
        if wr:
            shown, cur = K.type_on(wr, B, bt, 14)
            text(c, shown + ("_" if cur else ""), 500, yy, 44, "mono", WHITE, a, "l")
        else:
            k5 = ap(B, bt, 0.4) * a
            text(c, "?", 500, yy, 44, "mono", DIM, k5, "l")
            text(c, "想不起来，先空着", 560, yy, 36, "bold", DIM, k5, "l")
    text(c, "这些都算「考自己」", 1100, 542, 44, "bold", AMBER, ap(B, vb + 13, 0.4) * a, "l")   # beat 21
    chips = [("pencil", "空白纸默写", "Blank-page recall"),
             ("layers", "问答卡：正面问，背面答", "Flashcards"),
             ("mic", "讲给别人听", "Explain it (Feynman)")]
    for j, (ic, cn, en) in enumerate(chips):               # beats 22, 24, 26
        b0 = vb + 14 + 2 * j
        kj = ap(B, b0, 0.4) * a
        if kj <= 0:
            continue
        with at(c, 1420, 632 + j * 120, lerp(0.85, 1.0, e_out((B - b0) / 0.4))):
            card(c, -320, -52, 640, 104, kj, VIOLET, r=20, brackets=False, glow=False)
            badge(c, ic, -268, 0, 26, VIOLET, kj)
            text(c, cn, -222, -16, 44, "black", WHITE, kj, "l")
            text(c, en, -220, 28, 34, "monor", DIM, kj, "l")


def checking(c, S, x, y, w, h, a):
    B, vb = S.B, S.vb
    sheet(c, a, "打开书，对答案", "Check", "book-open", GREEN)
    for i, (cn, wr, right) in enumerate(WORDS):            # one check every half bar: beats 10 ... 18
        yy = ROW_Y[i]
        bt = vb + 2 + 2 * i
        kc = ap(B, bt, 0.3) * a
        mark = lerp(0.6, 1.0, e_out((B - bt) / 0.3))
        if wr == right:
            text(c, wr, 500, yy, 44, "mono", WHITE, a, "l")
            if kc > 0:
                with at(c, 985, yy, mark):
                    badge(c, "check", 0, 0, 22, GREEN, kc)
            continue
        fix = ap(B, bt + 1, 0.4)                           # the correction lands one beat after the red mark
        old = wr or "?"
        text(c, old, 500, yy, 44, "mono", RED if kc > 0 else (WHITE if wr else DIM), a * (1 - fix), "l")
        if kc > 0:
            K.strike(c, 494, 506 + measure(old, "mono", 44), yy + 2, e_out((B - bt) / 0.4), RED, a * (1 - fix), 5)
            with at(c, 985, yy, mark):
                badge(c, "x", 0, 0, 22, RED, kc)
        if fix > 0:
            text(c, right, 500, yy, 44, "mono", GREEN, a * fix, "l", glow=GREEN, gsig=8, glow_a=0.5)
    kh = ap(B, vb + 12, 0.4) * a                           # beat 20: why re-test the right ones
    text(c, "一周后，单词还记得", 1415, 542, 44, "bold", WHITE, kh)
    c.drawLine(1150, 838, 1690, 838, paint(DIMMER, 0.8 * kh, stroke=2))
    bar(c, 1275, 838, 140, 230, 35, 100, DIM, B, vb + 13, vb + 14, kh, "考对就不再考", DIM, "约35%")
    bar(c, 1560, 838, 140, 230, 80, 100, GREEN, B, vb + 15, vb + 16, kh, "对的也继续考", GREEN, "约80%", glow=True)
    kp = ap(B, vb + 18, 0.5) * a                           # beat 26
    if kp > 0:
        s = "下次复习：第 1、3、7 天"
        pill(c, 1415, 940, measure(s, "bold", 36) + 80, 56, AMBER, kp)
        text(c, s, 1415, 940, 36, "bold", WHITE, kp)
    text(c, "数据：Karpicke & Roediger 2008 · 背 40 个外语单词", 200, 942, 34, "reg", DIM, a, "l")


# ----------------------------------------------------------------------------- episode
EP = Episode(
    slug="active_recall",
    title="主动回忆",
    bpm=BPM,
    music=False,
    tail=0.0,          # ends exactly on the last bar line ...
    fade_out=0.0,      # ... with no fade: the user asked to end directly
    scenes=[
        Scene("hook", 4, SC.hook("复习了好几遍，为什么[一考就忘]？", "You reviewed it. Why is it gone on the test?", pains=[
            ("highlighter", "重点划满一本", "合上一片空白", "Highlighted all → blank"),
            ("repeat", "重读了 3 遍", "一考就卡壳", "Reread 3x, still stuck"),
            ("badge-check", "感觉都会了", "一做题就错", "Felt sure, still wrong"),
        ]), chapter="痛点"),
        Scene("answer", 4, SC.answer("问题是：你只在「看」，没在「想」", "[主动回忆]", "ACTIVE RECALL · TEST YOURSELF",
                                     [("合上书", "Close the book"), ("写出来", "Recall"), ("对答案", "Check")],
                                     colors=[CYAN, VIOLET, GREEN], save_hint=SC.LEGACY_SAVE_HINT),   # posted look
              chapter="答案"),
        Scene("step1", 8, SC.step(1, "合上书，别重读", "Close the book. Don't reread.",
                                  [("重读只是[眼熟]，回忆才[记得住]", "Rereading feels familiar. Recalling makes it stick.")],
                                  visual=experiment, color=CYAN), chapter="3 步"),
        Scene("step2", 8, SC.step(2, "把记得的写出来", "Write down what you remember",
                                  [("能写多少写多少，[先别翻书]", "Write all you can before you peek")],
                                  visual=dictation, color=VIOLET), chapter="3 步"),
        Scene("step3", 8, SC.step(3, "对答案", "Check your answers",
                                  [("错的马上改，对的[下次还考]", "Fix mistakes now. Test the right ones again.")],
                                  visual=checking, color=GREEN), chapter="3 步"),
        Scene("summary", 4, SC.summary("主动回忆 · 一图总结", "Active recall in one picture", [
            ("别重读，[合上书]回忆", "Don't reread. Close the book and recall"),
            ("[写出来]：默写、问答卡、讲出来", "Write it, use flashcards, or explain it"),
            ("[对答案]，错的马上改", "Check, and fix mistakes right away"),
            ("对的也再考：第 [1、3、7] 天", "Re-test on day 1, 3 and 7"),
        ], colors=[CYAN, VIOLET, GREEN, AMBER], hint=SC.LEGACY_SUMMARY_HINT), chapter="总结"),
        Scene("cta", 4, SC.cta("你平时是[重读]，还是[考自己]？", "Reread, or test yourself? Tell me below.",
                               options=[("扣 1 · 重读", DIM), ("扣 2 · 考自己", VIOLET)], end_card=False),
              chapter="总结"),
    ],
    cover=SC.cover("读 14 遍，不如考 3 次？", "主动回忆", "ACTIVE RECALL", "1 分钟学会 · 附总结卡", "合上书考自己 · 中英双语"),
    publish=dict(
        title="Vibe知识大赏/读14遍不如考3次？1分钟学会主动回忆",
        desc="复习好几遍还是一考就忘？问题是你只在「看」，没在「想」。"
             "实验里两组都学 4 轮：一直重读的一组读了约 14 遍，一周后只记得 40%；"
             "读 1 轮、考 3 轮的一组只读了约 3 遍，却记得 61%。"
             "心理学综述也把「重读」「划重点」评为低效，「自测」评为高效。最后有一张总结卡，建议收藏。",
        tags=["Vibe知识大赏", "主动回忆", "学习方法", "记忆方法", "高效学习", "背单词"],
    ),
)

if __name__ == "__main__":
    run(EP)
