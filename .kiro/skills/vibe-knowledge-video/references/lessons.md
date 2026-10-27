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
| 学累了，睡会儿还是接着学？ Nap or keep studying (`sleep_or_cram/`, own Canvas + numpy renderer, flat cartoon kids in every frame, sound effects, no music, 128 BPM, no on-screen save prompt, GPT cover) | 2026-10-26 18:09 | 1:15 | frame 0: 「学累了 / 睡会儿还是接着学？」 two lines + girl reading, boy napping, clock at 3 + a hit; 「30 分钟后」 tie at 2.11 s held 4 beats, 「一周后」 at 3.98 s, check 「还领先」 at 4.92 s | **3.2万** | 687 | 220 | 2.14% | 0.68% | 37.65% | 38.31% | 8 s | 1.52% | 99.5% |

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
- 睡还是背 / Nap or keep studying (data at ~24 h; screenshots 2026-10-27 17:59-18:00): comments 8 (0.02%), shares 85 (0.26%,
  +155% vs the account average - the most shared so far: a nap tip is easy to pass on), follows +6 (fans' share of plays 0.03%),
  不感兴趣 0.04% (+839%, ~1 in 2,500 viewers; it rises when the feed pushes a video beyond the usual audience). Highest absolute
  numbers so far except saves (220 vs Feynman's 267): likes 687, shares 85, comments 8, follows +6.
  **Not one burst:** ~1,000-1,700 plays/h right after posting at 18:09, a few hundred per hour overnight, then a bigger wave the
  next day: ~2,000/h at 09:00, ~4,700/h at 11:00, ~3,300/h at 14:00, the top hour ~5,076/h around 16:00; the last point (~17:00)
  drops to ~0, probably the hour not yet counted. The first video whose plays rose again after the first wave.
  流量激励 1959 (真实生活分享计划, counted up to 10-27 10:00; Douyin again: "很多用户都认为你分享的信息很实用 … 再投稿1篇同类作品，
  有机会继续获得流量激励") = ~6% of the plays; it was ~31-37% for the earlier ones (Feynman 3793 / 1.1万, 主动回忆 1882 / 6154,
  money 663 / 2172, if-then 4014 / 1.1万): ~94% of this video's plays came from the normal recommendation feed.
  Douyin: "播放量较往期上涨703.12% … 其中 平均播放时长 和 2秒跳出率 数据表现很棒". 比往期: completion 1.52% (+69.3%), avg watch
  8 s (+47.0%), 2 s bounce 37.65% (−22.2%), 5 s 完播率 38.31% (+70.4%), avg watch share 10.61% (+59.4%), likes 2.14% (−17.8%),
  comments 0.02% (+42.2%), shares 0.26% (+155.1%), saves 0.68% (−23.5%) -> the account average Douyin compares with is now
  ~4,000 plays, ~48% 2 s bounce, ~22.5% 5 s, ~5.4 s avg watch, ~0.9% completion, ~2.6% likes, ~0.89% saves, ~0.10% shares.
  Retention curve: close to 「同类作品」 for the first ~10 s, slightly below after; Douyin still marks the low point at 0-2 s and
  again suggests "推荐学习以下热门同类作者视频开头" (a talking-head example).
  Chapter clicks (names as Douyin lists them): 学还是睡 (0:00) 29.2%, 怎么睡 (0:14) 29.2%, 怎么做 (1:00) 21.2%, 先睡一会 (0:08)
  20.4% - evenly spread. Three of the four names differ from the video's bar labels (睡还是学 / 先睡一觉 / 怎么睡 / 照着做) and 怎么睡
  starts at 0:15 in the video: typed by the user at upload or generated by Douyin - to confirm.
  Title as shown in the data: 「学累了，继续学还是睡一小会？ #学习 #学…」, not the prepared
  「Vibe知识大赏/学累了，睡会儿还是接着学？1分钟学会午睡」: no prefix, other wording, hashtags in the title (to confirm).
  The first video with no on-screen save prompt at all (no 「建议先收藏」 at ~0:11, no end button; the prepared caption still
  ended with 建议收藏). Made with its own renderer: per the repo history the 36 texts < 34 px were not changed - no visible harm
  (weak evidence).
- All: ~98-99.5% of traffic from 推荐页; 搜索 ≤ 0.2%; no music-page traffic visible. All titles up to 如果…就… started with
  "Vibe知识大赏/" (睡还是背: see above).
  Douyin titles allow at most 30 characters (prefix included); the caption up to 1000.

## Conclusions (current best explanation, 7 data points)
1. **A save-worthy topic gets the first push.** Learning-method topics: Feynman 2.39% saves → 1.1万 plays, active recall 1.22% → 6154,
   if-then plan ~1.0% → 1.1万; money & happiness 0.55% → 2172; butterfly effect 0.11% → 950. Keep choosing practical
   "use it on yourself" topics.
   **睡还是背 (2026-10-26) qualifies this:** the lowest save rate of the learning-method videos (0.68%) and still 3.2万 plays,
   ~3x the best before, ~94% from the normal feed. Douyin named avg watch and the 2 s bounce as its strong points: retention
   carried this push more than saves. Practical topics stay (Douyin's incentive again said "信息很实用").
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
   **Tested 2026-10-26 (睡还是背): it worked again.** The hook in the student's own words, the figures already acting on frame 0 +
   a hit, a two-stage reveal (30 分钟后: a tie, held 4 beats -> 一周后: only the nap still ahead -> check at 4.9 s), then no
   text-only screen (the boy wakes, stretches, picks up the book while the overview labels pop in; the steps are acted out
   without STEP pages; the table builds while he acts) -> 2 s bounce 37.65% (if-then 43.0%), 5 s 38.31% (28.1%), avg watch 8 s
   (5 s), completion 1.52% (0.63%), avg watch share 10.61% (6.88%): the best of the learning-method videos on every retention
   number, and the first video that did not stop after one burst (3.2万). Several things changed at once (topic, hook wording,
   the reveal held longer, acted-out answer, renderer and figures, no save prompt, title without the prefix, 18:09 slot). The
   2 s / 5 s numbers only depend on the feed title + the first seconds, so topic / hook / title are the candidates for the
   bounce; the acted-out middle can only explain the avg watch and completion. The low point is still 0-2 s (37.65% gone).
3. **Viewers want the method, not the pain point** (chapter clicks 三步 44.9% vs 痛点 2.6%). Pain cards are optional, never in the first 2 s.
4. **End-of-video CTAs reach ~1% of viewers** (completion 0.4-0.6% on the dark-tech videos): 扣1/扣2 at 1:07 got 0 comments, so it
   was never really tested. Put the comment question in the caption's first line + a pinned comment. Follows are tiny (+2 per 6k plays).
   If-then plan: caption-first-line question + (planned) pinned comment -> 2 comments on 1.1万 plays (0.02%): no effect.
   Comments are not this account's lever; don't spend screen time on comment prompts.
   **User, 2026-10-26: "以后都不要在结尾加上收藏点赞关注啥的"** (after removing 睡还是背's 「收藏这张表」 button): from now on
   no like / save / follow icons, save button, 「建议先收藏」 / 「截图保存」 pill or comment question in any video; the
   screenshot-able summary is the last screen. Engine: the factory hints are off by default, `SC.cta` is legacy, the lint
   reports such words in the last 8 bars (END CTA); the four engine episodes posted before keep their look (`SC.LEGACY_*`).
   Skill 2.0 also turned off the 「建议先收藏」 pill on the answer page (~0:11 - not the end; seen by ~1/4 of viewers) because
   睡还是背 had none. Videos with that early pill: saves 2.39 / 1.22 / ~1.0%; 睡还是背 without any save prompt: 0.68% (−23% vs
   the account average) - but a nap tip is also easy to remember without saving, so the two causes are not separable.
5. **Music did not measurably matter for reach** (no music-page traffic). User preference since 2026-10-17:
   deliver **silent** videos, the user adds a four-on-the-floor DJ track ("动次打次") and wants the picture cut to its beat.
   Feedback on the first beat-cut version: "画面不要一抖一抖的" -> no frame bounce / zoom cuts / glitch; rhythm only through
   timing (elements on beats, cuts on downbeats). Measured: still areas 29x more change on beats with the beat-zoom, 1.4x without.
   2026-10-19: user confirmed the 128 BPM cut lines up with 《清明上河图》DJ版; asked to drop the next-episode teaser
   and end directly (no end card, no fade; since 2026-10-26 no CTA either - see 4).
   2026-10-23: "视频不要无声了，你给我加几个音效，但是不要配乐" -> deliver with sound effects (`engine/sfx.py`), still no
   music. if_then_plan: 75 effects on the beat grid, -18.4 LUFS, true peak -1.7 dBTP; Douyin had advised the money video
   to open with "短促有力的音效", so frame 0 gets a `hit`.
6. Keep: dark-tech style (the user's choice; both learning-method videos got the first push with it), bilingual,
   a screenshot-able summary (the save rate is what triggers the push) - without an on-screen 收藏 prompt (see 4).
7. **Douyin shows the progress-bar labels as chapter names**: name chapters by what they give ("3 个写法", "照着填"), never
   "片头 / 结尾" (money: 结尾 9.1% of chapter clicks although it held the answer). 睡还是背: Douyin listed 学还是睡 / 先睡一会 /
   怎么睡 / 怎么做 while the bar said 睡还是学 / 先睡一觉 / 怎么睡 / 照着做 - the names are not always copied from the bar
   (user-typed or generated by Douyin, to confirm); clicks were evenly spread (20-29%).
8. **Titles and covers:** no number that needs background knowledge (「7.5 万美元」 confused the user's audience);
   self-explaining comparisons are fine (「读14遍不如考3次」). The profile grid is 3:4 and crops 16:9 covers: make covers
   1080x1440 (`Episode(cover_size=(1080, 1440))`) and keep the bottom-left empty (Douyin puts the play count there).
9. **User, 2026-10-23: little people in every scene** ("有人看着更舒服一点，不是干巴巴的塞一堆知识给你") -> `engine/figures.py`
   (ported from the money video): each step acts out one everyday scene. Douyin's own advice on the money video pointed the
   same way (everyday-life detail).
   Gestures (user, 2026-10-26: "最后这个感觉像是在比中指一样（笑）"): a raised arm with one digit sticking up from a round
   fist reads as a middle finger. Point sideways at the thing (arm at most ~30° above horizontal, index finger along the
   forearm, thumb tucked on top); draw 👍 as a square fist with finger creases and the thumb rising from a top corner, never centred.
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
12. **One cover picture for both shapes (user, 2026-10-26: "封面只能保留一个版本，横版和竖版不能同时用，只能是一张图片给他弄成横版和竖版").**
   Douyin's publish page keeps a single cover image and crops the 3:4 竖封面 (profile grid) and the 4:3 横封面 from it, so a
   separate 4:3 design (the accepted GPT 横封面 for 睡还是背) cannot be used. Delivered `封面_横竖通用.png` (1920x1440): the
   centre 1080x1440 is the accepted 3:4 cover pixel for pixel, the 420 px on each side continue its near-black background
   (edge colour of each row, smoothed, fading to 35 %; seam step 0.02 vs 0.32 between neighbouring columns inside the cover).
   The 3:4 crop wins because the profile grid shows it; in the 4:3 view the design fills the middle 56 % of the width.
   Keep >= 80 px between the design and the sides of the 3:4 crop so a slightly off-centre crop box does not cut the
   title (睡还是背: 85 / 92 px). Tool: `sleep_or_cram/tools/one_cover.py IN OUT --preview P [--shrink 0.94]`.
   Still unknown: whether Douyin centres the crop boxes by default or the user drags them - ask after the first upload.
13. **The format to batch: 睡还是背 (best data so far; `sleep_or_cram/README.md` has the beat-by-beat timeline).** 75 s at 128 BPM.
   Frame 0 = a two-line question in the student's words with the figures already acting (one studies on, one naps) + a hit;
   reveal 1 at ~2 s (the tie), reveal 2 at ~4 s (4 beats after the first: 2 beats felt rushed to the user), the check at ~5 s.
   0:08 the hero acts out the answer while the 3 overview labels pop in. 0:15 / 0:30 / 0:45: three acted-out steps, no STEP
   pages; one prop changes its role (wall clock -> timer ring -> alarm clock, a calendar for the one-week delay). 1:00 the table
   builds while the hero acts; it ends on pointing + a thumbs-up, no save button, no CTA. The hero is on screen in every frame.
   Change nothing structural inside the next batch, so its data tests this format and not a new mix.

## Open questions to test
- If-then plan (2026-10-23) results vs its targets: 2 s bounce 43.0% (target < 40%: missed, but -5 points), 5 s retention 28.1%
  (target > 27%: met), saves ~1.0% (target ≥ 1%: met).
- **Next episode = 午睡还是接着背 (user's pick 2026-10-24, topic 3; Cousins et al. 2019, *Sleep* 42(1):zsy207):** one change -
  no text-only screen after the hook (figures act through the answer, steps without the "STEP" splash, two-stage reveal in the
  hook: "30 分钟后" tie -> "一周后" nap still ahead). Keep: learning-method topic, 75 s, 128 BPM, figures, sound effects.
  Target: avg watch > 5 s and the curve closer to 「同类作品」, 2 s bounce ≤ 43%, 5 s retention ≥ 28%, saves ≥ 1%.
  Built 2026-10-25 in `sleep_or_cram/` on branch `sleep-or-cram` (PR #12) with its own Canvas + numpy renderer, because the
  Skill was not on `main`: the engine's lint and cover rules were not applied automatically (the frame-0 hit and -18.4 LUFS
  were added afterwards; 36 texts are below 34 px - the user decides before posting). Posted 2026-10-26 18:09 (data above).
  Results vs targets: avg watch 8 s (> 5 s: met), 2 s bounce 37.65% (≤ 43%: met), 5 s 38.31% (≥ 28%: met), curve closer to
  「同类作品」 (yes; slightly below after ~10 s), saves 0.68% (≥ 1%: missed).
  User edits before posting (2026-10-26): "前面「睡还是背」章节感觉有点快了" -> the 30-minute tie is now held 4 beats instead
  of 2: 「一周后」 at 3.98 s (was 3.05), the check at 4.92 s (was 3.98), chapter 2 at 8.0 s (was 7.0); the 先睡一觉 section
  gave up the 2 beats, so everything from 15 s on is unchanged. Reveals 2 beats (0.94 s) apart felt rushed to the user.
  "「收藏这张表」的元素去掉吧" -> no save button in the summary section; the boy points at the table, then a thumbs-up.
  "开头的文字「学累了睡还是背」感觉怪怪的" -> hook 「学累了 / 睡会儿还是接着学？」 (11 characters, one over the ≤ 10 rule;
  picked by the user from 睡会儿还是接着学 / 睡还是接着学 (9) / 先睡还是接着学 (10)). The user's own idea 「先休息一会还是继续学」
  was not used: 「休息」 is this study's losing rest group (the 「只休息」 line), so viewers would map the napping boy to 「休息」
  and then watch 「只休息」 lose. Chapter 1 renamed 睡还是学, English line "Tired? Nap, or keep studying?", title
  「Vibe知识大赏/学累了，睡会儿还是接着学？1分钟学会午睡」 (29); the girl's plate stays 「接着背 1 小时」 (what the cram group
  did, and the words on the cover).
- **Next: a batch in the 睡还是背 format** (conclusion 13). Targets: 2 s bounce ≤ 40%, 5 s ≥ 35%, avg watch ≥ 7 s, plays above the
  account average (~4,000). Post at the same time of day as 睡还是背 (~18:00) so the slot is not a confound; watch the save rate
  (no on-screen save prompt). Asked the user 2026-10-27: the renderer / figures for the batch (copy `sleep_or_cram/` vs the
  engine), whether the ~0:11 save pill stays off, and whether the posted title / chapter names were typed by hand.
- Second-day wave: does it repeat? (睡还是背 posted 18:09, the main wave came 09:00-17:00 the next day; every earlier video had one
  burst within hours.) Also ask for the profile grid in 3-5 days (long tail).
- Topic backlog: 记忆宫殿 (recommended 2026-10-23; Dresler et al. 2017 *Neuron*: 40 days x 30 min, 26 → 62 of 72 words,
  48 after 4 months - the numbers so far from press coverage; Twomey & Kroneisen 2021 meta-analysis g = 0.65); 先猜答案再学
  (prequestion meta-analysis 2023: g = 0.54 for asked content, 0.04 for the rest); 同桌玩电脑 (Sana et al. 2013: -11% / -17%);
  交错练习 (deferred - user, 2026-10-23: "选题一的例子做过了"); 考前一晚睡好有用吗 (Okano et al. 2019, npj Science of Learning:
  the single night before a test did not matter, the month and week before did, sleep ≈ 25% of grade variance - correlational);
  一万小时定律 (Macnamara et al. 2014: deliberate practice explains 26% games, 21% music, 18% sports, 4% education, < 1% professions).
- Forgetting curve data (same structure, 15-character one-line hook): a ~48% 2 s bounce would strengthen conclusion 2.
- Feynman "互动趋势" (at which second people liked / saved): still not seen.
- Series effect (合集): does a learning-methods series raise 个人主页 traffic (currently ~0.4-1%)?
