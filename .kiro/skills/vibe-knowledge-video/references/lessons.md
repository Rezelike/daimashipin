# Data history & lessons (Douyin creator-center data)

Append a row after every episode (ask the user for 总览 + 流量分析 screenshots 24-48 h after posting).

| Episode | Posted | Length | Style / music on platform | Plays | Likes | Saves | Like % | Save % | 2s bounce | 5s retention | Avg watch | Completion | Recommend-feed share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 蝴蝶效应 Butterfly effect | 2026-10-12 | ~1:03 | beige minimal; AI-made piano+strings | 950 | 24 | 1 | 2.53% | 0.11% | 36.3% | **45.9%** | 13 s | **9.07%** | 98.1% |
| 临时物永久化理论 | 2026-10-14 | ~2:20 | 16:9, piano+strings | 527 | 11 | 4 | 2.27% | 0.76% | 48.0% | 18.8% | 5 s | 1.11% | 97.6% |
| 费曼学习法 Feynman (long) | 2026-10-17 | 3:51 | dark-tech; user replaced score with 《清明上河图》DJ版 | **1.1万** | 401 | 267 | **3.61%** | **2.39%** | 39.1% | 27.5% | 9 s | 0.39% | 99.1% |
| 艾宾浩斯遗忘曲线 Forgetting curve | (no data yet) | 1:16 | dark-tech, new short structure, silent, cut to 128 BPM for the user's DJ track | | | | | | | | | | |
| 主动回忆 Active recall | (no data yet) | 1:15 | same + stable picture, A/B comment prompt (扣1/扣2), no teaser, ends directly | | | | | | | | | | |

Extra facts:
- Feynman: cover CTR 14.29%, shares 16, comments 2, got 3793 platform "流量激励". Plays came in one burst the morning after posting, then stopped.
  Skip-rate peak ~2:00 (step 4), re-watch peak ~2:20 (worked example starts): viewers scrubbed forward looking for the example.
- Butterfly: like peaks at 0:00, ~0:30 and the end.
- All three: ~98-99% of traffic from 推荐页; 搜索 ≤ 0.2%; no music-page traffic visible.
- All titles started with "Vibe知识大赏/" (a popular tag for AI/code-made knowledge videos), so the tag alone doesn't explain differences.

## Conclusions (current best explanation, 3 data points only)
1. **Save-worthy topic is the #1 driver.** Feynman's save rate was ~20x butterfly's; that is what pushed it into bigger traffic pools.
   Practical, self-improvement, "use it on yourself" topics > pure science spectacle.
2. **Length / payoff timing capped the reach.** Avg watch 9 s on a 3:51 video, first real step at 0:56.
   -> 60-75 s, the core answer + overview must be on screen within 10 s, examples inside each step.
3. **Music did not measurably matter for reach** (no music-page traffic). User preference since 2026-10-17:
   deliver **silent** videos, the user adds a four-on-the-floor DJ track ("动次打次") and wants the picture cut to its beat.
   Feedback on the first beat-cut version: "画面不要一抖一抖的" -> no frame bounce / zoom cuts / glitch; rhythm only through
   timing (elements on beats, cuts on downbeats). Measured: still areas 29x more change on beats with the beat-zoom, 1.4x without.
   2026-10-19: user confirmed the 128 BPM cut lines up with 《清明上河图》DJ版; asked to drop the next-episode teaser
   and end directly (CTA is the last screen, no end card, no fade).
4. **The hook's 2 s bounce was similar across styles** (36-48%). Relatable pain-point questions are fine; don't over-invest there.
5. Keep: dark-tech style (best result so far), bilingual, summary card + "收藏" prompt at the end (protects the save rate).

## Open questions to test
- Does a 60-75 s cut of a save-worthy topic raise avg watch time above 13 s while keeping save rate > 2%?
- Feynman "互动趋势" (at which second people liked/saved) was not yet available; ask for it.
- Series effect (合集): does a learning-methods series raise 个人主页 traffic (currently ~0.4-1%)?
- Does the two-choice reply prompt (扣1 / 扣2, first used in 主动回忆) lift the comment rate above 0.11%?
