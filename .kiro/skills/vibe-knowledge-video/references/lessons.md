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
| 「如果…就…」计划 If-then plan (`if_then_plan`, dark-tech + figures in every scene, sound effects, no music, 128 BPM, GPT cover without people) | 2026-10-23 ~15:00 | 1:15 | frame 0: 「同一份作业 / 差一句话」 two lines + two seated figures already writing + a hit; time skip on beat 4, crowds light up, 71% vs 32% lands on beat 8 (3.75 s) | **1.1万** | 289 | 111 | ~2.6% | ~1.0% | 43.0% | **28.1%** | 5 s | 0.63% | (not shown) |

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
- If-then plan (data at ~19 h): comments 2, shares 13, follows +4 (fans' share of plays 0.13%), **4014 流量激励 (the most so far)**.
  One burst again: posted ~15:00, peak ~4,300 plays/h around 17:00, ~0 from 18:30. Douyin: "播放量较往期上涨415.9% … 2秒跳出率和
  吸粉率数据表现很棒". 内容吸引力 vs 往期: completion 0.63% (−54%), avg watch 5 s (−7%), 2 s bounce 42.97% (−13.9%),
  5 s 完播率 28.06% (+38.6%), avg watch share 6.88% (+7.1%). The retention curve stays BELOW Douyin's 「同类作品」 curve for the
  whole video, and Douyin still marks the low point at 0-2 s. Same afternoon slot as the money video: 2172 → 1.1万 plays.
  Several things changed at once vs 主动回忆 (opening, figures, sound effects, cover, chapter names), so no single cause is proven;
  the 2 s / 5 s metrics only depend on the first seconds (opening + frame-0 sound), the cover does not show in the feed.
- Profile grid 2026-10-26 09:52 (play counts only): 费曼 1.3万 (was 1.1万), 如果…就… 1.1万, 主动回忆 6547 (6154),
  遗忘曲线 5931 (5860), 钱能买到快乐吗 2219 (2172), 蝴蝶效应 960 (950), 临时物 540 (527): after the burst the long tail
  adds 1-18 %, the most for Feynman.
- All: ~98-99% of traffic from 推荐页; 搜索 ≤ 0.2%; no music-page traffic visible. All titles start with "Vibe知识大赏/".
  Douyin titles allow at most 30 characters (prefix included); the caption up to 1000.

## Conclusions (current best explanation, 6 data points)
1. **A save-worthy topic gets the first push.** Learning-method topics: Feynman 2.39% saves → 1.1万 plays, active recall 1.22% → 6154,
   if-then plan ~1.0% → 1.1万; money & happiness 0.55% → 2172; butterfly effect 0.11% → 950. Keep choosing practical
   "use it on yourself" topics.
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
   **Tested 2026-10-23 (if-then plan): it worked.** Two-line hook + figures moving on frame 0 + a hit, the result landing on
   beat 8 -> 2 s bounce 43.0% (主动回忆 48.3%, money 50.7%), 5 s retention 28.1% (主动回忆 16.9%) - best of the dark-tech videos.
   **The next bottleneck is 0:05-0:20:** avg watch is still 5 s and the curve stays under 「同类作品」. After the hook landed,
   the video went to text: an answer card at 0:07.5 and a "STEP 01" splash at 0:15 / 0:30 / 0:45 (sections that only set up).
   -> after the hook, no text-only screen: the figures keep acting through the answer, steps open on the action
   (`SC.step(..., splash_beats=0)`), and the hook opens a second question before it closes (two-stage reveal).
3. **Viewers want the method, not the pain point** (chapter clicks 三步 44.9% vs 痛点 2.6%). Pain cards are optional, never in the first 2 s.
4. **End-of-video CTAs reach ~1% of viewers** (completion 0.4-0.6% on the dark-tech videos): 扣1/扣2 at 1:07 got 0 comments, so it
   was never really tested. Put the comment question in the caption's first line + a pinned comment. Follows are tiny (+2 per 6k plays).
   If-then plan: caption-first-line question + (planned) pinned comment -> 2 comments on 1.1万 plays (0.02%): no effect.
   Comments are not this account's lever; don't spend screen time on comment prompts.
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
10. **Covers (user, 2026-10-23):** made by the user with GPT from our prompt; **no people on the cover** ("封面不要小人会不会好一点":
   the profile's best covers - brain, curve, books - had none). A cover is read in half a second, so it must say
   (a) the topic in plain words ("总拖延？"), (b) what to do ("写下这一句" + the sentence itself), (c) the proof with its
   label ("按时完成率 32% → 71%"). The first GPT cover (「同一份作业 / 差一句话」 + two sticky notes + bare 32% / 71%) was
   rejected: "这完全不知道这张封面在说什么" - a riddle headline works in the video (answered 4 s later), never on a cover.
11. **Covers match the profile grid (user, 2026-10-26: "我想尽量的保持一致性"; accepted: 「学累了？/先睡一觉」).** The grid's
   covers share a near-black background (only 主动回忆 is blue), two title lines of the same height filling the width
   (「总拖延？」 and 「写下这一句」 measure the same in the grid) and one group of realistic 3D objects with cinematic light in
   the lower half (paper + sticky note, gold coins, books + brain). The first GPT cover for 睡还是背 followed the flat code
   layout (HUD panel, flat bars, pill, bright navy grid floor; the 9-character first line half the height of 「先睡一觉」)
   and did not fit. Accepted: the user's 「总拖延」 cover uploaded as the style reference + the same words; the chart as
   objects (frosted-gray pillar on an open textbook, glowing gold pillar on a pillow), the glowing 「只休息」 dashed line kept.
   Douyin draws the play count at x 7-42 %, y 88.5-95 % of a grid tile (measured on the user's profile screenshot); GPT put
   the bottom labels down to 90 %, so the 3:4 picture was scaled to 94 % at the top and the edges extended (labels now end
   at 85 %). GPT covers are AI-generated content: the user must tick Douyin's AI declaration (《人工智能生成合成内容标识办法》
   Art. 10, in force since 2025-09-01); the PNGs pasted into chat carry no AI metadata, so the platform may not label them itself.

## Open questions to test
- If-then plan (2026-10-23) results vs its targets: 2 s bounce 43.0% (target < 40%: missed, but -5 points), 5 s retention 28.1%
  (target > 27%: met), saves ~1.0% (target ≥ 1%: met).
- **Next episode = 午睡还是接着背 (user's pick 2026-10-24, topic 3; Cousins et al. 2019, *Sleep* 42(1):zsy207):** one change -
  no text-only screen after the hook (figures act through the answer, steps without the "STEP" splash, two-stage reveal in the
  hook: "30 分钟后" tie -> "一周后" nap still ahead). Keep: learning-method topic, 75 s, 128 BPM, figures, sound effects.
  Target: avg watch > 5 s and the curve closer to 「同类作品」, 2 s bounce ≤ 43%, 5 s retention ≥ 28%, saves ≥ 1%.
  Built 2026-10-25 in `sleep_or_cram/` on branch `sleep-or-cram` (PR #12) with its own Canvas + numpy renderer, because the
  Skill was not on `main`: the engine's lint and cover rules were not applied automatically (the frame-0 hit and -18.4 LUFS
  were added afterwards; 36 texts are below 34 px - the user decides before posting). Not posted yet.
  User edits before posting (2026-10-26): "前面「睡还是背」章节感觉有点快了" -> the 30-minute tie is now held 4 beats instead
  of 2: 「一周后」 at 3.98 s (was 3.05), the check at 4.92 s (was 3.98), chapter 2 at 8.0 s (was 7.0); the 先睡一觉 section
  gave up the 2 beats, so everything from 15 s on is unchanged. Reveals 2 beats (0.94 s) apart felt rushed to the user.
  "「收藏这张表」的元素去掉吧" -> no save button in the summary section; the boy points at the table, then a thumbs-up.
- Topic backlog: 记忆宫殿 (recommended 2026-10-23; Dresler et al. 2017 *Neuron*: 40 days x 30 min, 26 → 62 of 72 words,
  48 after 4 months - the numbers so far from press coverage; Twomey & Kroneisen 2021 meta-analysis g = 0.65); 先猜答案再学
  (prequestion meta-analysis 2023: g = 0.54 for asked content, 0.04 for the rest); 同桌玩电脑 (Sana et al. 2013: -11% / -17%);
  交错练习 (deferred - user, 2026-10-23: "选题一的例子做过了"); 考前一晚睡好有用吗 (Okano et al. 2019, npj Science of Learning:
  the single night before a test did not matter, the month and week before did, sleep ≈ 25% of grade variance - correlational);
  一万小时定律 (Macnamara et al. 2014: deliberate practice explains 26% games, 21% music, 18% sports, 4% education, < 1% professions).
- Forgetting curve data (same structure, 15-character one-line hook): a ~48% 2 s bounce would strengthen conclusion 2.
- Feynman "互动趋势" (at which second people liked / saved): still not seen.
- Series effect (合集): does a learning-methods series raise 个人主页 traffic (currently ~0.4-1%)?
