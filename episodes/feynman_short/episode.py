"""Example episode for the engine: Feynman Technique, short cut (~70 s) in the proven structure.

    python episodes/feynman_short/episode.py --preview   # contact sheet + lint
    python episodes/feynman_short/episode.py             # out/feynman_short.mp4 (+ _nomusic, verify)

Copy this folder to start a new episode: change the strings, keep the structure, add custom visuals.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from engine import core as K                         # noqa: E402
from engine import scenes as SC                      # noqa: E402
from engine.core import AMBER, BLUE, CYAN, DIM, GREEN, WHITE, ap, e_inout, lerp, rich, text  # noqa: E402
from engine.render import Episode, Scene, run        # noqa: E402


def snowball(c, S, x, y, w, h, a):
    """custom visual inside step 4's card: a snowball rolling downhill and growing"""
    B = S.B
    hx0, hy0, hx1, hy1 = x + 80, y + 80, x + 820, y + h - 50
    p0, p1, p2, p3 = (hx0, hy0), (hx0 + 300, hy0 + 30), (hx1 - 360, hy1 - 50), (hx1, hy1)

    def bez(u):
        return tuple((1 - u) ** 3 * p0[i] + 3 * (1 - u) ** 2 * u * p1[i] + 3 * (1 - u) * u ** 2 * p2[i] + u ** 3 * p3[i]
                     for i in range(2))

    hill = K.skia.Path()
    hill.moveTo(*p0)
    hill.cubicTo(*p1, *p2, *p3)
    c.drawPath(hill, K.paint(WHITE, 0.55 * a, stroke=4))
    u = e_inout((B - 9) / 10)
    r = lerp(12, 78, u ** 1.6)
    bx, by = bez(u)
    bx2, by2 = bez(min(1, u + 0.01))
    ang = math.atan2(by2 - by, bx2 - bx)
    cx, cy = bx + math.sin(ang) * r, by - math.cos(ang) * r
    c.drawCircle(cx, cy, r, K.paint("#DFF6FF", 0.95 * a))
    c.drawCircle(cx, cy, r + 10, K.paint(CYAN, 0.35 * a, blur=16))
    with K.at(c, cx, cy, 1.0, (u * 1400) % 360):
        K.icon(c, "snowflake", 0, 0, r * 1.2, BLUE, a * 0.8, glow=False, sw=1.5)
    k1, k2 = ap(B, 10) * a, ap(B, 13) * a
    rich(c, "复利就像[滚雪球]", x + 900, y + 120, 72, "black", WHITE, AMBER, k1, "l")
    text(c, "Compound interest is a snowball", x + 902, y + 190, 36, "monor", DIM, k1, "l")
    rich(c, "越大，粘上的雪[越多]", x + 900, y + 290, 60, "black", WHITE, AMBER, k2, "l")
    text(c, "Bigger ball, more snow each turn", x + 902, y + 352, 34, "monor", DIM, k2, "l")


EP = Episode(
    slug="feynman_short",
    title="费曼学习法（短版）",
    bpm=136,
    music=True,       # this one ships with the engine's original piano + violin score
    cut="slide",
    bounce=0.0,
    glitch_cuts=True,   # the style this one was rendered with
    tail=1.5,
    fade_out=1.2,
    scenes=[
        Scene("hook", 4, SC.hook("为什么你[学了就忘]？", "Why do you forget what you learn?", pains=[
            ("book-open", "书看了 3 遍", "合上全忘", "Read 3x, forgot all"),
            ("graduation-cap", "上课都听懂", "做题就懵", "Got it, then lost it"),
            ("bookmark", "收藏 100 篇", "一篇没看", "Saved 100, read 0"),
        ]), role="intro", chapter="痛点"),
        Scene("answer", 4, SC.answer("答案：诺贝尔奖得主费曼的方法", "[费曼学习法]", "THE FEYNMAN TECHNIQUE · 4 STEPS", [
            ("选概念", "Pick"), ("讲给孩子", "Teach"), ("找卡壳", "Find gaps"), ("简化", "Simplify"),
        ]), role="theme", chapter="答案"),
        Scene("step1", 6, SC.step(1, "选一个概念", "Pick a concept",
                                  [("白纸顶部写下[要学的概念]", "Write the concept at the top of a page")],
                                  example=("例子", "Example", [("学「复利」，先写下你[已经知道的]", "Write down what you already know")])),
              role="verse", chapter="4 步"),
        Scene("step2", 6, SC.step(2, "讲给 12 岁孩子听", "Teach it to a 12-year-old",
                                  [("[不用术语]，讲出来或写下来", "No jargon. Say it out loud or write it.")],
                                  example=("例子", "Example", [("复利 = 利息也会[再生利息]", "Interest earns interest, too"),
                                                              ("100 → 110 → 121 → 133.1", "10% a year, 3 years")])),
              role="verse", chapter="4 步"),
        Scene("step3", 6, SC.step(3, "找到卡壳点", "Find the gaps",
                                  [("讲不下去的地方 = [你没懂的地方]", "Where you get stuck = what you don't know")],
                                  example=("卡在这里", "Stuck here", [("为什么越往后[涨得越快]？", "Why does it grow faster and faster?"),
                                                                     ("回去翻书：因为[本金每年都在变大]", "Back to the book: the base keeps growing")])),
              role="tension", chapter="4 步"),
        Scene("step4", 6, SC.step(4, "简化 + 打比方", "Simplify & use an analogy",
                                  [("能不能[一句话]讲清楚？", "Can you say it in one sentence?")], visual=snowball),
              role="release", chapter="4 步"),
        Scene("summary", 4, SC.summary("费曼学习法 · 一图总结", "The whole method in one picture", [
            ("选一个概念，[写在纸上]", "Pick a concept, write it down"),
            ("讲给 12 岁孩子听", "Teach it to a kid"),
            ("卡壳了就[回去重学]", "Stuck? Go back to the source"),
            ("简化，[打个比方]", "Simplify with an analogy"),
        ]), role="recap", chapter="总结"),
        Scene("cta", 4, SC.cta("你想用它学[什么]？", "Tell me in the comments", "费曼学习法", "THE FEYNMAN TECHNIQUE",
                               end_card=True),
              role="outro", chapter="总结"),
    ],
    cover=SC.cover("学了就忘？", "费曼学习法", "THE FEYNMAN TECHNIQUE", "1 分钟学会 · 4 步", "诺贝尔奖得主的学习法 · 中英双语"),
    publish=dict(
        title="Vibe知识大赏/1分钟学会费曼学习法，学什么都更快",
        desc="学了就忘？诺贝尔奖得主费曼的 4 步学习法：选概念、讲给孩子听、找卡壳点、简化打比方。最后有一图总结，建议收藏。",
        tags=["Vibe知识大赏", "费曼学习法", "学习方法", "高效学习", "自我提升"],
    ),
)

if __name__ == "__main__":
    run(EP)
