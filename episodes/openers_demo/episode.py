"""开场动画样片 / opener demo: four animated openings, 4 bars each (128 BPM, silent, 30 s).

    python episodes/openers_demo/episode.py   ->  out/openers_demo.mp4

Numbers used:
* race: Roediger & Karpicke (2006), Experiment 2 - final test after 5 min: rereading 83%, testing 71%;
  after 1 week: 40% vs 61%
* dissolve: 12 words, about 1/3 left (Ebbinghaus: roughly a third after one day)
* diverge: 1.01^365 = 37.8, 0.99^365 = 0.03 (arithmetic)
* timer: illustration (labelled on screen)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from engine import openers as OP                      # noqa: E402
from engine import scenes as SC                       # noqa: E402
from engine.render import Episode, Scene, run         # noqa: E402

WORDS = ["environment", "opportunity", "necessary", "influence", "explain", "language",
         "remember", "knowledge", "practice", "decision", "interest", "attention"]

EP = Episode(
    slug="openers_demo",
    title="开场动画样片",
    bpm=128,
    music=False,
    scenes=[
        Scene("race", 4, SC.hook("读 14 遍|输给[考 3 次]", "14 rereads lose to 3 self-tests",
                                 visual=OP.race("一直重读", "合上书考", a_vals=(83, 40), b_vals=(71, 61),
                                                note="读得少，反而记得多",
                                                source="数据：Roediger & Karpicke 2006")),
              chapter="① 对比反转"),
        Scene("dissolve", 4, SC.hook("背了 12 个|剩下[4 个]", "12 words learned, 4 left a day later",
                                     visual=OP.dissolve(WORDS, keep=4)),
              chapter="② 消散"),
        Scene("diverge", 4, SC.hook("每天 1%|一年差[多少]？", "1% a day: how big is the gap?",
                                    visual=OP.diverge("每天 +1%", "每天 -1%", a_vals=(1.0, 1.01 ** 365),
                                                      b_vals=(1.0, 0.99 ** 365), end_label="一年后")),
              chapter="③ 分叉"),
        Scene("timer", 4, SC.hook("坐一下午|只学[半小时]？", "A whole afternoon, 30 minutes of study?",
                                  visual=OP.timer()),
              chapter="④ 计时"),
    ],
)

if __name__ == "__main__":
    run(EP)
