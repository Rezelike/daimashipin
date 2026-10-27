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
| 学累了，睡会儿还是接着学？ Nap or keep studying (`sleep_or_cram/`, own Canvas + numpy renderer, flat cartoon kids in every frame, sound effects, no music, 128 BPM, no on-screen save prompt, GPT cover) | 2026-10-26 18:09 | 1:15 | frame 0: 「学累了 / 睡会儿还是接着学？」 two lines + girl reading, boy napping, clock at 3 + a hit; 「30 分钟后」 tie at 2.11 s held 4 beats, 「一周后」 at 3.98 s, check 「还领先」 at 4.92 s | **7.2万** (27 h; 3.2万 at 24 h) | 1308 | 455 | 1.82% | 0.63% | 38.35% | 37.9% | 8 s | 1.54% | 99.5% |

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
- 睡还是背 / Nap or keep studying. Snapshot 1 (~24 h, 10-27 18:00): 3.2万 plays, likes 687 (2.14%), saves 220 (0.68%),
  shares 85, comments 8, follows +6; 2 s bounce 37.65%, 5 s 38.31%, avg watch 8 s, completion 1.52%.
  Snapshot 2 (~27.5 h, 10-27 21:32): **7.2万 plays** (Douyin: +1690.97% vs the account average), likes 1308 (1.82%, −29.8%),
  comments 22 (0.03%, +75.1%), shares 240 (0.33%, +223.5%: the most shared so far - a nap tip is easy to pass on), saves 455
  (0.63%, −29.4%), follows +15 / −1 (fans' share of plays 0.01%), 不感兴趣 0.04% (+712%, ~1 in 2,500 viewers; it rises when the
  feed pushes a video beyond the usual audience); completion 1.54% (+70.7%), avg watch 8 s (+45.8%), 2 s bounce 38.35% (−20.7%),
  5 s 37.9%, avg watch share 10.54%: the rates barely moved while the plays more than doubled. Implied account average: ~4,000
  plays, ~48% 2 s bounce, ~5.5 s avg watch, ~0.9% completion, ~2.6% likes, ~0.89% saves, ~0.10% shares.
  **The biggest wave came on the second evening:** posted 18:09; ~1,000-1,700 plays/h for the first hours, a few hundred per hour
  overnight, ~2,000/h at 09:00, ~5,500/h at 11:00, ~4,000/h at 14:00, then **~1.2万/h at 17:00-19:00** (the chart tops out at its
  1.2万 line), ~7,000/h at ~20:00 (snapshot 1's "drop to ~0" was the hour not yet counted). Every earlier video stopped after one
  burst within hours.
  平台扶持流量 1.5万 plays at 27 h = ~21% (snapshot 1's 1959 was counted only up to 10:00, so the "~6% / ~94% normal feed" computed
  from it was wrong); earlier videos ~31-37% (Feynman 3793 / 1.1万, 主动回忆 1882 / 6154, money 663 / 2172, if-then 4014 / 1.1万).
  Incentive text (真实生活分享计划) again: "很多用户都认为你分享的信息很实用 … 再投稿1篇同类作品，有机会继续获得流量激励".
  Douyin's diagnosis: "其中 完播率 和 2秒跳出率 数据表现很棒"; on completion: "你把学习累了该睡还是继续学的干货内容按逻辑分段排布，
  还设置了清晰的知识点看点". Retention curve: close to 「同类作品」 for ~10 s, slightly below after; the low point is still 0-2 s, and
  Douyin again suggests studying a hot talking-head opening (「韩国人每天必说的10句口头禅」).
  **Like timing (互动趋势, the first time we have it):** likes peak at 0:00-0:02 (~18-20% of all likes), then small bumps at ~0:06
  and ~0:08-0:11 (the 「还领先」 check at 4.9 s / 「优势没了」 at 5.4 s, the boy acting out the answer from 8 s, 「不止一个实验」 at
  12.4 s), ~1% from 0:13 on, and a rise at the very end (1:04+: the finished table, the thumbs-up). 「同类作品」 decays smoothly
  from ~16%. Likes follow the payoffs.
  Chapter clicks: 怎么睡 (0:14) 31.2%, 学还是睡 (0:00) 26.0%, 怎么做 (1:00) 21.6%, 先睡一会 (0:08) 21.2% (snapshot 1: 29.2 / 29.2 /
  21.2 / 20.4%). Three of the four names differ from the bar labels (睡还是学 / 先睡一觉 / 怎么睡 / 照着做) and 怎么睡 starts at 0:15
  in the video: user-typed or generated by Douyin - to confirm.
  **No spillover to the rest of the account:** 个人主页 0.3% of the plays; profile grid 10-26 09:52 -> 10-27 21:28: 主动回忆
  6547 -> 6580, 遗忘曲线 5931 -> 5941, 钱能买到快乐吗 2219 -> 2227 (+8 to +33). The account: 57 fans, 2521 likes; the bio
  「给世界一些惊喜」 does not say what the account gives. Suggested to the user 10-27: a 合集 of the learning-method videos, pin the
  hit, a bio that says what the videos are, the original MP4 also to 小红书 / B站, the next 同类 video within 1-2 days at ~18:00.
  **Comments (26 on the evening of 10-27; likes 1379, saves 480 by then):** the most liked is a joke (「我在梦里面也能学」 ♥41, 5
  replies), then nap-length advice from viewers: 「追求醒后马上好用…20分钟…背东西选60分钟，接受醒后半小时昏沉；90分钟只适合偶尔」
  (♥33, with sources), 「午睡30分钟就足够了，多了反而会进入深度睡眠起来会累」 (♥8, the first comment), 「眯10分钟最多不超过20分钟」
  (♥3); plus 「睡起来什么都忘了」 (♥7), 「睡到天黑有没有什么解决办法」, 「暴学一段时间就开始厌学，脑子不转了咋整」. Three viewers
  tagged @豆包 (「总结」 x2, 「@抖音求真 @豆包 是真的吗」): viewers ask the platform AI to summarise or fact-check, so every claim must
  hold up and the source must be easy to find. The author had liked 4 comments and replied to none. -> The question this audience
  asks most is nap length and waking up groggy (sleep inertia): the video said "30-60 min to remember" without mentioning the
  grogginess, the viewers' rule of thumb is "≤ 30 min". Drafted for the user 10-27: replies to the top comments + a pinned
  author comment with the source.
  Title as shown in the data: 「学累了，继续学还是睡一小会？ #学习 #学…」, not the prepared 「Vibe知识大赏/学累了，睡会儿还是接着学？
  1分钟学会午睡」: no prefix, other wording, hashtags (to confirm). The first video with no on-screen save prompt at all (no
  「建议先收藏」 at ~0:11, no end button; the prepared caption still ended with 建议收藏). Made with its own renderer: per the repo
  history the 36 texts < 34 px were not changed - no visible harm (weak evidence).
- All: ~98-99.5% of traffic from 推荐页; 搜索 ≤ 0.2%; no music-page traffic visible. All titles up to 如果…就… started with
  "Vibe知识大赏/" (睡还是背: see above).
  Douyin titles allow at most 30 characters (prefix included); the caption up to 1000.

## Conclusions (current best explanation, 7 data points)
1. **A save-worthy topic gets the first push.** Learning-method topics: Feynman 2.39% saves → 1.1万 plays, active recall 1.22% → 6154,
   if-then plan ~1.0% → 1.1万; money & happiness 0.55% → 2172; butterfly effect 0.11% → 950. Keep choosing practical
   "use it on yourself" topics.
   **睡还是背 (2026-10-26) qualifies this:** the lowest save rate of the learning-method videos (0.63% at 27 h) and still 7.2万
   plays at 27 h (~6.5x the best before, still ~7,000/h), ~79% from the normal feed (平台扶持 ~21% vs ~31-37% before). Douyin named
   the 2 s bounce, avg watch and completion as its strong points: retention carried this push more than saves. Practical topics stay (Douyin's incentive again said "信息很实用").
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
   without STEP pages; the table builds while he acts) -> at 27 h: 2 s bounce 38.35% (if-then 43.0%), 5 s 37.9% (28.1%), avg
   watch 8 s (5 s), completion 1.54% (0.63%), avg watch share 10.54% (6.88%): the best of the learning-method videos on every
   retention number, and the first video that did not stop after one burst (7.2万 at 27 h; the biggest wave came on the second
   evening). Likes bump on the reveals and on the finished table (互动趋势). Several things changed at once (topic, hook wording,
   the reveal held longer, acted-out answer, renderer and figures, no save prompt, title without the prefix, 18:09 slot). The
   2 s / 5 s numbers only depend on the feed title + the first seconds, so topic / hook / title are the candidates for the
   bounce; the acted-out middle can only explain the avg watch and completion. The low point is still 0-2 s (~38% gone).
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
   睡还是背 had none. Videos with that early pill: saves 2.39 / 1.22 / ~1.0%; 睡还是背 without any save prompt: 0.63% at 27 h (−29%
   vs the account average) - but a nap tip is also easy to remember without saving, so the two causes are not separable.
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
   **Changed 2026-10-27 (user: "不要你再用什么玩意儿扩成一张1920×1440的，直接让ChatGPT弄成一个横版竖版都能用的版本";
   "改成直接用 ChatGPT 出封面"):** no more extending a 3:4 GPT cover with `one_cover.py`. The prompt asks ChatGPT for one landscape
   4:3 picture with the whole design in the centre strip (at most half the width = the 竖封面 crop, margins on both sides,
   bottom-left empty) and only dark background on the sides (= the 横封面); the agent only checks the result. First used for
   背单词 (`bedtime_words/out/封面提示词.txt`, style reference 「学累了？先睡一觉」).
13. **The format to batch: 睡还是背 (best data so far; `sleep_or_cram/README.md` has the beat-by-beat timeline).** 75 s at 128 BPM.
   Frame 0 = a two-line question in the student's words with the figures already acting (one studies on, one naps) + a hit;
   reveal 1 at ~2 s (the tie), reveal 2 at ~4 s (4 beats after the first: 2 beats felt rushed to the user), the check at ~5 s.
   0:08 the hero acts out the answer while the 3 overview labels pop in. 0:15 / 0:30 / 0:45: three acted-out steps, no STEP
   pages; one prop changes its role (wall clock -> timer ring -> alarm clock, a calendar for the one-week delay). 1:00 the table
   builds while the hero acts; it ends on pointing + a thumbs-up, no save button, no CTA. The hero is on screen in every frame.
   Likes bump exactly on its payoffs (the ~5 s check, the 8-12 s answer, the finished table): keep a payoff at each of those points.
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
  Results vs targets (27 h): avg watch 8 s (> 5 s: met), 2 s bounce 38.35% (≤ 43%: met), 5 s 37.9% (≥ 28%: met), curve closer
  to 「同类作品」 (yes; slightly below after ~10 s), saves 0.63% (≥ 1%: missed).
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
- **Next: a batch in the 睡还是背 format** (conclusion 13), built by copying `sleep_or_cram/` (same kids, props, sound recipe,
  fonts read from `sleep_or_cram/assets/fonts/`). Order agreed 2026-10-27: the sequel 「背单词：睡前还是早上？」 first (user: "可以";
  slug `bedtime_words`), then 「睡醒更困？午睡多久不头昏」 (the comments' top question, backlog below), then 记忆宫殿 / 先看书还是先做题
  (prequestions) / 习惯 66 天, one per day at ~18:00 (睡还是背's slot, so the slot is not a confound).
  **背单词 built 2026-10-27** (`bedtime_words/`, PR #17): 「背单词 / 早上还是睡前？」, reveal 1 「都背到全对」 (16 vs 16) at 2.11 s,
  reveal 2 「12 小时后再考」 (7.5 vs 10, Mazza 2016) at 3.98 s; answer 「睡前背，早上复习」; conclusion 「早上默到全对」, not 「复习一遍」:
  Mazza's control group (learned before bed, slept, one pass in the morning) was no better than the wake group a week later.
  Fact-check found Gais 2006's students learned **German** words (not English). The boy "goes to bed" where he sits (blanket
  over the desk). New tools there: `tools/sheet.mjs` (numbered, timed preview tiles: point the user at 图 N + seconds) and
  `render.mjs --lint` (text off-screen / on top of each other).
  Targets: 2 s bounce ≤ 40%, 5 s ≥ 35%, avg watch ≥ 7 s, plays above the account average (~4,000); watch the save rate (no
  on-screen save prompt). One hit does not predict the next: judge each by its rates, not its plays.
  Still to confirm with the user: whether the posted title / chapter names were typed by hand.
- Second-day wave: does it repeat? (睡还是背 posted 18:09; the biggest wave came the next evening, ~1.2万/h at 17:00-19:00; every
  earlier video had one burst within hours.) Also ask for the profile grid in 3-5 days (long tail).
- Topic backlog: **背单词：睡前还是早上？** (proposed 2026-10-27 as the 睡还是背 sequel; same audience, sleep + memory): Mazza et al.
  2016, *Psychological Science* 27(10):1321-1330 - 40 French adults, 16 Swahili-French word pairs, learned until all were right,
  relearned 12 h later; sleep group (9 pm -> night's sleep -> 9 am) vs wake group (9 am -> 9 pm): at the relearning session ~10 vs
  ~7.5 of 16 recalled, ~3 vs ~6 rounds to get all 16 again; 1 week later ~15 vs ~11; still ahead at 6 months (numbers from the APS
  press release - check the paper's figures). Gais, Lucas & Born 2006, *Learning & Memory* 13:259-262: high-school students'
  vocabulary is kept better when sleep follows within a few hours of learning, independent of time of day. Keep the claim modest:
  a 2021 replication with realistic material (*Sleep* 44(3):zsaa210, Singapore, 52 students, facts about ants and crabs, 9 pm vs
  9 am, 12 h apart): the overnight boost held (d = 0.72), relearning was not faster (d = 0.10), and after 1 week the sleep group
  was only numerically ahead (d = 0.35, n.s.). Safe message: learn the hard words in the evening, sleep, review once in the morning.
  Hook in a viewer's own words: 睡还是背's comment 「睡起来什么都忘了」 (♥7) -> e.g. 「睡一觉|就忘光了？」.
  **睡醒更困？午睡多久不头昏** (the most-asked question under 睡还是背, 2026-10-27): Brooks & Lack 2006, *Sleep* 29(6):831-840 - after a
  short night, afternoon naps of 5 / 10 / 20 / 30 min: 5 min hardly helped; 10 min helped at once on every measure, partly for up to
  155 min; 20 min helped only from ~35 min after waking (up to 125 min); 30 min first made alertness and performance worse (sleep
  inertia), then helped up to 155 min -> 10 min was best overall. Leong et al. 2023, *Sleep* 46(4):zsad025 (habitual short
  sleepers): 10-60 min naps all lifted mood and alertness, only 30 min improved learning new material, the grogginess after 30-60
  min naps was gone within 30 min. Hilditch et al. 2016, *Sleep*: a 30-min night nap (~15 min of deep sleep) caused sleep inertia, a
  10-min one did not. Lovato & Lack 2010 review (PubMed 21075238): 5-15 min naps help almost at once for 1-3 h; > 30 min brings a
  short grogginess, then benefits for hours. -> "need to be sharp right away: 10-20 min; 30-60 min only if you can spare ~30 min to
  wake up"; it completes 睡还是背 (which said 10 min to wake up, 30-60 min to remember) without contradicting it.
  记忆宫殿 (recommended 2026-10-23; Dresler et al. 2017 *Neuron*: 40 days x 30 min, 26 → 62 of 72 words,
  48 after 4 months - the numbers so far from press coverage; Twomey & Kroneisen 2021 meta-analysis g = 0.65); 先猜答案再学
  (prequestion meta-analysis 2023: g = 0.54 for asked content, 0.04 for the rest); 同桌玩电脑 (Sana et al. 2013: -11% / -17%);
  交错练习 (deferred - user, 2026-10-23: "选题一的例子做过了"); 考前一晚睡好有用吗 (Okano et al. 2019, npj Science of Learning:
  the single night before a test did not matter, the month and week before did, sleep ≈ 25% of grade variance - correlational);
  一万小时定律 (Macnamara et al. 2014: deliberate practice explains 26% games, 21% music, 18% sports, 4% education, < 1% professions).
- Forgetting curve data (same structure, 15-character one-line hook): a ~48% 2 s bounce would strengthen conclusion 2.
- "互动趋势" (at which second people like): seen for 睡还是背 (likes follow the payoffs, see above); Feynman's still not seen.
- Series effect (合集): does a learning-methods series raise 个人主页 traffic (currently ~0.3-1%) and the older videos' plays?
  Suggested to the user 2026-10-27 while 睡还是背 still gets thousands of plays per hour; compare before / after if it was made.
