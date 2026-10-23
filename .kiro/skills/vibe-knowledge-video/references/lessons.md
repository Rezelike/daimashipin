# Data history & lessons (Douyin creator-center data)

Append a row after every episode (ask the user for 总览 + 流量分析 screenshots 24-48 h after posting).

| Episode | Posted | Length | Opening (first 2 s) | Plays | Likes | Saves | Like % | Save % | 2s bounce | 5s retention | Avg watch | Completion | Recommend-feed share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 蝴蝶效应 Butterfly effect (`butterfly_v2`, paper style, 16:9, piano + strings) | 2026-10-12 | 1:00 | billiards shot already in motion, 「同一杆，打两次」 | 950 | 24 | 1 | 2.53% | 0.11% | **36.3%** | **45.9%** | **13 s** | **9.07%** | 98.1% |
| 临时物永久化理论 (`linshiwu_16x9`, dark 3D room, piano + strings) | 2026-10-14 | 2:33 | 6.4 s title card 「临时物永久化理论」 | 527 | 11 | 4 | 2.27% | 0.76% | 48.0% | 18.8% | 5 s | 1.11% | 97.6% |
| 费曼学习法 Feynman (long, dark-tech, 《清明上河图》DJ版) | 2026-10-17 | 3:51 | 「为什么你 / 学了就忘？」 two lines, 132 px | **1.1万** | 401 | 267 | **3.61%** | **2.39%** | 39.1% | 27.5% | 9 s | 0.39% | 99.1% |
| 艾宾浩斯遗忘曲线 Forgetting curve (silent, 128 BPM cut) | ? | 1:16 | 「为什么你背的单词，总是记不住？」 one line, 15 chars | 5860 (profile grid, 10-21; no details) | | | | | | | | | |
| 主动回忆 Active recall (silent, 128 BPM cut, user's DJ track) | 2026-10-19 23:11 | 1:15 | 「复习了好几遍，为什么一考就忘？」 one line, 15 chars, 107 px + typed English + pain cards from 1.9 s | 6154 | 207 | 75 | 3.36% | 1.22% | 48.3% | 16.9% | 5 s | 0.58% | 99.0% |
| 钱能买到快乐吗 Money & happiness (`money_happiness/` Node engine on the `money-happiness` branch, navy-gold, flat figures, 3 PNAS papers, silent, NOT beat-cut) | 2026-10-22 14:52 | 2:03 | 2.6 s title card 「钱能买到快乐吗？」 fading in from black, then two scholars | 2172 | 38 | 12 | 1.75% | 0.55% | 50.7% | — | — | 1.36% | 98.9% |

Extra facts:
- Feynman: cover CTR 14.29%, shares 16, comments 2, got 3793 platform "流量激励". Plays came in one burst the morning after posting, then stopped.
  Skip-rate peak ~2:00 (step 4), re-watch peak ~2:20 (worked example starts): viewers scrubbed forward looking for the example.
- Active recall: comments 0, shares 4, follows +2 (fans' share of plays 0.18%), 1882 流量激励, plays +574% vs the account's
  recent average. ~5,000 plays in the first 1-2 hours after posting, then almost nothing (same one-burst pattern as Feynman).
  Douyin marked the retention low point at 0-2 s and suggested studying "热门同类作者视频开头" (example shown: a talking-head video).
  Douyin showed chapters named after the progress-bar labels: chapter click rate 三步 (0:14) 44.9% (1st), 痛点 (0:00) 2.6% (last).
  The posted title had a typo (「主动会议」 instead of 「主动回忆」), the user retyped it.
  Douyin's 比往期 implies the account's recent average is ~50% 2 s bounce and ~20% 5 s retention: most videos lose half the viewers in 2 s.
- Butterfly: like peaks at 0:00, ~0:30 and the end.
- Money & happiness (data at ~21 h): comments 1, shares 2, follows 0 (fans' share of plays 0.23%), 663 流量激励 from the
  「真实生活分享计划」 (Douyin: users found the info practical; "再投稿 1 篇同类作品" may earn more). One burst: ~736 plays in the
  first hour after posting, ~0 from 18:00 on. Douyin's 比往期 (plays -35%, likes -41%, saves -47%) implies the account's recent
  average is ~3,360 plays, ~3.0% likes, ~1.0% saves. Douyin's own suggestions: (1) the opening "缓慢露出'钱能'两个字" is
  low-information -> show the cover question on frame 0 with a punchy sound; (2) add everyday-life detail (put $100K into
  terms viewers know). Chapter clicks: 研究1 (0:13) 31.8%, 片头 (0:00) 22.7%, 研究3 (1:05) 20.5%, 研究2 (0:38) 15.9%,
  结尾 (1:46) 9.1% - the chapter holding the answer got the fewest clicks because "结尾" says nothing.
  Confounds: posted 14:52 (others ~23:00), 2:03 long, not a learning method. The 总览 page no longer shows 5 s retention / avg watch.
  The first title draft used 「7.5 万美元」: Chinese viewers don't know that number, so the posted title had no number.
- All: ~98-99% of traffic from 推荐页; 搜索 ≤ 0.2%; no music-page traffic visible. All titles start with "Vibe知识大赏/".
  Douyin titles allow at most 30 characters (prefix included); the caption up to 1000.

## Conclusions (current best explanation, 5 data points)
1. **A save-worthy topic gets the first push.** Learning-method topics: Feynman 2.39% saves → 1.1万 plays, active recall 1.22% → 6154;
   money & happiness 0.55% → 2172; butterfly effect 0.11% → 950. Keep choosing practical "use it on yourself" topics.
2. **The opening (first 2 s) is the bottleneck, and it caps every video at one burst.** Active recall: 48% gone at 2 s, 83% at 5 s,
   avg watch 5 s, so the answer at 0:07.5 reached ~12% of viewers. Shortening to 75 s with the answer inside 10 s did NOT raise
   avg watch (the 3:51 Feynman had 9 s).
   Held best: a concrete action already in motion + a ≤ 6-character line (butterfly, billiards: 36%), then a two-line ≤ 9-character
   question about the viewer (Feynman: 39%). Lost: a 6.4 s concept title card (临时物: 48%) and a 15-character one-line question +
   English + cards (主动回忆: 48%).
   Money & happiness: a title card fading in from black lost 50.7% in 2 s - and Douyin's own diagnosis said the same.
   -> frame 0 = the full hook; ≤ 10 characters (two lines OK); show the surprising result or an action in motion; overview by ~0:04.
   User, 2026-10-20: "开头多做几个动画，不要光是文字" -> `engine/openers.py` (race / dissolve / diverge / timer), demo
   `out/openers_demo.mp4`: all four move from frame 0, 96% of visual events on the beat, shake 0.09 (limit 1.0).
3. **Viewers want the method, not the pain point** (chapter clicks 三步 44.9% vs 痛点 2.6%). Pain cards are optional, never in the first 2 s.
4. **End-of-video CTAs reach ~1% of viewers** (completion 0.4-0.6% on the dark-tech videos): 扣1/扣2 at 1:07 got 0 comments, so it
   was never really tested. Put the comment question in the caption's first line + a pinned comment. Follows are tiny (+2 per 6k plays).
5. **Music did not measurably matter for reach** (no music-page traffic). User preference since 2026-10-17:
   deliver **silent** videos, the user adds a four-on-the-floor DJ track ("动次打次") and wants the picture cut to its beat.
   Feedback on the first beat-cut version: "画面不要一抖一抖的" -> no frame bounce / zoom cuts / glitch; rhythm only through
   timing (elements on beats, cuts on downbeats). Measured: still areas 29x more change on beats with the beat-zoom, 1.4x without.
   2026-10-19: user confirmed the 128 BPM cut lines up with 《清明上河图》DJ版; asked to drop the next-episode teaser
   and end directly (CTA is the last screen, no end card, no fade).
   2026-10-23: "视频不要无声了，你给我加几个音效，但是不要配乐" -> deliver with sound effects (`engine/sfx.py`), still no
   music. if_then_plan: 75 effects on the beat grid, -18.4 LUFS, true peak -1.7 dBTP; Douyin had advised the money video
   to open with "短促有力的音效", so frame 0 gets a `hit`.
6. Keep: dark-tech style (the user's choice; both learning-method videos got the first push with it), bilingual,
   summary card + 收藏 prompt (the save rate is what triggers the push).
7. **Douyin shows the progress-bar labels as chapter names**: name chapters by what they give ("3 个写法", "照着填"), never
   "片头 / 结尾" (money: 结尾 9.1% of chapter clicks although it held the answer).
8. **Titles and covers:** no number that needs background knowledge (「7.5 万美元」 confused the user's audience);
   self-explaining comparisons are fine (「读14遍不如考3次」). The profile grid is 3:4 and crops 16:9 covers: make covers
   1080x1440 (`Episode(cover_size=(1080, 1440))`) and keep the bottom-left empty (Douyin puts the play count there).
9. **User, 2026-10-23: little people in every scene** ("有人看着更舒服一点，不是干巴巴的塞一堆知识给你") -> `engine/figures.py`
   (ported from the money video): each step acts out one everyday scene. Douyin's own advice on the money video pointed the
   same way (everyday-life detail).

## Open questions to test
- **Next episode = 「如果…就…」计划 (`if_then_plan`, 2026-10-23):** changes vs 主动回忆: frame-0 hook with figures already
  moving and the result landing on beat 8 (Gollwitzer & Brandstätter 1997, Study 2: 71% vs 32%), figures in every scene,
  payoff chapter names, 3:4 cover. Same: learning-method topic, 75 s, 128 BPM, silent, dark-tech. Post ~23:00 again.
  Target: 2 s bounce < 40%, 5 s retention > 27%, saves ≥ 1%.
- Topic backlog: 交错练习 (deferred - user, 2026-10-23: "选题一的例子做过了"); 考前一晚睡好有用吗 (Okano et al. 2019,
  npj Science of Learning: the single night before a test did not matter, the month and week before did, sleep ≈ 25% of
  grade variance - correlational); 一万小时定律 (Macnamara et al. 2014: deliberate practice explains 26% games, 21% music,
  18% sports, 4% education, < 1% professions).
- Forgetting curve data (same structure, 15-character one-line hook): a ~48% 2 s bounce would strengthen conclusion 2.
- Does a caption question + pinned comment lift comments above 0.11%?
- Feynman "互动趋势" (at which second people liked / saved): still not seen.
- Series effect (合集): does a learning-methods series raise 个人主页 traffic (currently ~0.4-1%)?
