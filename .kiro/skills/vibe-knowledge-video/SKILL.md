---
name: vibe-knowledge-video
description: Make a 60-75 s landscape (1920x1080) bilingual Chinese/English knowledge video for Douyin / Xiaohongshu / Bilibili ("Vibe知识大赏" style) entirely with code - dark-tech motion graphics, no voice-over, no music (cut to the beat of a DJ track the user adds) - in the Rezelike/daimashipin repo. Use when the user asks to 做视频 / 做下一期 / 知识视频 / 科普视频 / 选题, to re-cut or re-time an episode, or to review Douyin data (播放量, 完播率, 收藏率) for these videos.
metadata:
  author: Rezelike
  version: "2.1"
---

# Vibe knowledge video

Repo: `https://github.com/Rezelike/daimashipin` (clone it if it is not in the workspace).
User defaults: landscape 16:9, **no voice-over**, **sound effects but no music** (user, 2026-10-23:
"视频不要无声了，你给我加几个音效，但是不要配乐" → `Episode(sfx=[...])`, every effect on the beat of its visual
event; the user may still add a four-on-the-floor DJ track, usually 《清明上河图》DJ版 — **128 BPM lines up with
it**, confirmed by the user 2026-10-19), Chinese + English text, dark-tech style, picture never shakes,
**no call to action at the end: no 点赞 / 收藏 / 关注 / comment prompt** (user, 2026-10-26: "以后都不要在结尾加上收藏点赞关注啥的"):
the summary is the last screen and the video ends directly on its last bar (no end card, no fade, no next-episode
teaser), posts to 抖音 / 小红书 / B站, titles start with `Vibe知识大赏/` (≤ 30 characters in total),
**little people in every scene** (user, 2026-10-23: "有人看着更舒服一点"), **3:4 covers** (1080x1440, the profile grid)
**that the user generates with GPT** (2026-10-23: "封面还用gpt生成吧") **in the same look as the rest of the profile**
(2026-10-26: "我想尽量的保持一致性"; lessons 11): write a Chinese prompt (3:4 only) and tell
the user to upload one of their accepted covers (「总拖延？写下这一句」) as the **style** reference - not the flat code cover,
which makes GPT copy the flat infographic look. Then check what comes back (every Chinese character, numbers not swapped,
no stray text, seams, nothing where Douyin draws the play count: x 7-42 %, y 88.5-95 % of the tile), fix and resize it to
1080x1440, then deliver **one** picture: Douyin's publish page keeps a single cover image and crops both the 3:4 竖封面
and the 4:3 横封面 from it (user, 2026-10-26: "横版和竖版不能同时用"; lessons 12), so extend the cover to one 1920x1440
picture with `sleep_or_cram/tools/one_cover.py` (centre 1080x1440 = the cover pixel for pixel, the sides only continue
the background; never a separate 4:3 design) and tell the user to centre the 竖封面 box. Remind the user to tick Douyin's
AI declaration. The code cover stays as the fallback, in the same one-picture form.
The user cannot see the sandbox: always report file paths / PR links, and put numbers in chat.

**Read `references/lessons.md` first** (real data from past episodes). Engine API: `references/engine.md`.
**Best data so far: 睡还是背** (`sleep_or_cram/`, its own renderer; `sleep_or_cram/README.md` has the beat-by-beat timeline):
3.2万 plays, 2 s bounce 37.65%, 5 s 38.3%, avg watch 8 s. Follow its structure (lessons 13): two-stage reveal in the hook,
the figure acts through the answer, no STEP pages, the table builds while the figure acts, no save button.
Latest engine example: `episodes/if_then_plan/episode.py` (figures acting out each step: seated at desks, walking,
door, phone; crowds of sprites that light up for the result; fill-in summary template; 3:4 cover; its `cta` scene
and 「截图保存」 pill are the old ending - drop them, see Build). Experiment bars /
dictation sheet: `episodes/active_recall/`. Curve / sawtooth / timeline visuals: `episodes/forgetting_curve/`.

## Workflow (do not skip the two approval gates)

1. **Topic** — unless the user already chose, propose 3-5 topics in a table scored on:
   save-worthiness (will people 收藏 it to use later?), relevance to the viewer's own life,
   can it be *shown* with code visuals (curve, timer, chart, diagram), fact base solid.
   Recommend one. **Gate 1: user picks.**
2. **Script** — storyboard in chat: scene · bars · seconds · visual · on-screen CN / EN text.
   Structure (current): hook 4 bars → answer + overview 4 → 3 steps × 8 (example inside each step)
   → summary 8 (screenshot-able, acted out by the figures; the last screen, no CTA after it) = 40 bars, 75 s at
   128 BPM. The hook must carry the payoff (see Content rules): it is the
   only part most viewers see. Use **128 BPM** unless the user names a different song.
   Fact-check every claim (dates, numbers, quotes); state sources; label illustrations and
   "common practice" as such; add "不构成投资/医疗建议" where relevant. **Gate 2: user approves.**
3. **Environment** (~40 s, idempotent):
   `bash .kiro/skills/vibe-knowledge-video/scripts/setup_env.sh` then
   `/projects/sandbox/.videoenv/vpy -m engine.assets` (from repo root).
4. **Build** — `cp -r episodes/if_then_plan episodes/<slug>`, rename `slug`, set `bpm`, replace
   strings, remove the old ending (its `cta` scene with the like / save / follow icons, the `("cta", …)` sfx cues and
   the 「截图保存」 pill; make `summary` the 8-bar last screen), give the hook an animated opener (`engine.openers`, or
   figures acting it out; see Content rules; demo: `out/openers_demo.mp4`), write 1-3 custom `visual=` functions for the key idea (the data shows the example is what
   viewers look for). Keep `music=False` unless the user asks for the engine's own score. Write the `sfx=` cue list
   last, one cue per visual event, on the same local beat (copy the one in `episodes/if_then_plan/`): hit on frame 0,
   whoosh on every cut, pops for things appearing, chime when the result lands, room sounds for what the figures do.
5. **Preview** — `$V episodes/<slug>/episode.py --preview` → view **only** `build/contact_sheet.png`.
   Fix everything the lint prints (hook too long, small text, missing glyphs, text off-screen or overflowing a card,
   END CTA = a like / save / follow / comment prompt in the last 8 bars).
   Max 2 preview rounds.
6. **Render** — `$V episodes/<slug>/episode.py` (~1 min). Read the VERIFY block: duration, 1920x1080,
   30 fps, size < 95 MB, lint OK, `beatgrid ... OK`, `rhythm ... OK` and `shake ... stable`; with sound effects also
   `lufs` (about -18), `true_peak` (≤ -1 dBTP) and the `sfx` line (transients within a few ms of their beats).
   You cannot hear: say so, and judge the sound only by these numbers. Re-level or swap effects without re-rendering
   the picture: `$V episodes/<slug>/episode.py --sfx` (~10 s).
   View `build/mp4_sheet.png` once, then run `--cover` (3:4, 1080x1440 with `cover_size`; it prints a lint;
   view the cover image only if you designed a new cover layout; keep its bottom-left empty for the play count;
   the publish page keeps ONE cover image for both the 竖封面 and the 横封面, so skip `extra_covers` and extend the 3:4
   cover with `sleep_or_cram/tools/one_cover.py`).
7. **Deliver** — new branch (ask the user first), commit `episodes/<slug>/episode.py` + `out/<slug>.mp4`, `_cover.png`,
   `_publish.txt`; open a PR with `gh api repos/Rezelike/daimashipin/pulls ...` (`gh pr create` does
   not work here). A comment question is optional and goes only into the caption / `publish["pin"]`, never on
   screen (asked in the caption: 2 comments per 1.1万 plays, lessons 4); tell the user to copy-paste the title, not
   retype it (「主动回忆」 went out as 「主动会议」).
   In chat: the MP4 has sound effects and no music, the BPM it is cut to, the cut times, how to
   align a song if the user adds one (a strong beat at 0:00, song volume low enough not to cover the effects),
   and that changing `bpm` + re-render takes ~1 min. Branch off `main` (everything up to 睡还是背 is merged since
   2026-10-26), not off another episode branch, so each PR merges on its own — skills only load from `main`.
8. **Data review** (when the user comes back with screenshots) — compare with the table in
   `references/lessons.md` (save %, 2 s bounce, 5 s retention, avg watch, completion, traffic sources),
   explain causes honestly (one video = weak evidence; name what changed), append a row, commit.

## Content rules (from the data)
- Topic must be **save-worthy and about the viewer** (Feynman: 2.39% saves → 11k plays; butterfly
  effect: 0.11% saves → 950 plays). Pure spectacle science keeps viewers but nobody saves it. But saves are not the
  only lever: 睡还是背 had 0.68% saves and got 3.2万 plays on its retention (2 s / 5 s / avg watch).
- **The first 2 seconds decide everything** (主动回忆: 48% gone at 2 s, 83% at 5 s, avg watch 5 s; every video before
  睡还是背 stopped after one burst; 睡还是背 got a second, bigger wave the next day). Frame 0 must already show the hook
  (the engine does this): ≤ 10 characters (睡还是背's 11 + ？ in two lines still did best: natural wording first),
  two big lines allowed (`hook("为什么你|[学了就忘]？", ...)`), ideally the surprising result itself or an action in
  motion (`hook(..., visual=fn)`). Best so far: butterfly effect opening on a billiards shot (2 s bounce 36%),
  睡还是背's two-line question with the figures already acting + a two-stage reveal (37.65%; 5 s 38.3%),
  Feynman's two-line question (39%). Worst: a concept title card, a 15-character one-line question (48%).
  Show the overview by ~0:04. No biography, no long intro, no section that only "sets up".
- **Never a text-only opening** (user, 2026-10-20: "开头多做几个动画，不要光是文字"). Every hook gets an animated
  visual: `engine.openers` — `race` (A looks better, then loses after a time skip: comparisons, experiments),
  `dissolve` (learned items dissolve while a counter drops: forgetting), `diverge` (two lines from one point
  end far apart: habits, compounding), `timer` (a clock races through an afternoon: focus) — or a custom one
  built the same way: moving on frame 0, events on beats, the reveal lands by beat 8, nothing shakes.
- **Little people in every scene** (user, 2026-10-23): `engine.figures` — seat them at desks (draw the figure,
  then `F.desk()` in front), walk them (`walk=` phase, one step per beat), give them props (pen, phone, note,
  paper), show results as crowds of sprites lighting up (real counts from the paper). Each step acts out one
  everyday scene; the text says the rule, the figure shows it.
- Put a concrete example inside every step; end on a screenshot-able summary (the last screen), with no prompt on it.
- Chapter labels are what Douyin lists as chapters: name them by payoff ("3 个写法", "照着填"), never "片头 / 结尾".
- Hook wording (user, 2026-10-26: 「学累了 / 睡还是背？」 "感觉怪怪的" -> 「学累了 / 睡会儿还是接着学？」): say it the way a
  student would ask it; no bare one-character verb that can be misread (「背」 needs an object: 背书 / 背单词); reuse the
  words the video uses later (接着学); never give the option that wins the name of the study's control condition
  (「休息」 was this study's losing rest group, the 「只休息」 line).
- Titles: ≤ 30 characters including `Vibe知识大赏/`; no number that needs background knowledge (「7.5 万美元」).
- Cover prompts (GPT, no people): the topic in plain words + what to do + the proof with its label; never a riddle
  (rejected: 「同一份作业 / 差一句话」 with bare 32% / 71%; accepted: 「总拖延？ / 写下这一句」 + the sentence + 按时完成率).
  Same look as the profile grid: near-black background, two equally huge title lines (pain? / action: 「学累了？/先睡一觉」),
  the proof as realistic 3D objects with cinematic light; no flat chart, HUD panel, frame or pill. Keep any baseline the
  claim depends on (the 「只休息」 dashed line: nap and cram did not differ from each other).
- **No CTA at the end** (user, 2026-10-26: "以后都不要在结尾加上收藏点赞关注啥的"): no like / save / follow icons, no
  收藏 button, no 「建议先收藏」 / 「截图保存」 pill, no comment question or 扣 1 / 扣 2 pills, no "下期" teaser (2026-10-19).
  The factory hints are off by default; `SC.cta` and `SC.LEGACY_*` exist only so the old episodes keep their look;
  the lint reports these words in the last 8 bars (END CTA). Model ending: 睡还是背 (the boy points at the finished
  table, then a thumbs-up). End prompts reached ~1% of viewers anyway (completion 0.4-0.6%).
- Pain points are the least-wanted part (Douyin chapter clicks: 痛点 2.6% vs 三步 44.9%): pain cards are
  optional and never in the first 2 s.
- One idea per screen; one highlighted `[keyword]` per line.

## Rhythm rules (the user's music is a four-on-the-floor DJ beat)
- **The picture must never shake** (user feedback, 2026-10-17: "画面不要一抖一抖的"). Nothing moves the
  whole frame on the beat: keep the defaults `bounce=0`, `cut="hard"`, `glitch_cuts=False`; no per-beat
  scale pulsing of text / icons, no jitter, no repeated pops on the same element.
- The beat is shown only by **when** things happen: scenes are **4 or 8 bars** (DJ phrases), clean cuts
  exactly on bar downbeats, every element appears ON a beat (integer `S.B`), new content every 1-2 bars,
  data points / nodes land one per half bar; plus a soft background brightness pulse (`pulse=0.6`).
- Unknown tempo → 128 BPM, say so, and offer to re-render once the user tells you the song's BPM.
- Verify by numbers, not by eye: VERIFY `rhythm` (share of visual events on the beat, should be ≥ 80%)
  and `shake` (extra edge change in still areas on the beat, in gray levels: must be < 1.0; stable videos
  measure 0.04-0.09, the rejected beat-zoom measured 7.4-8.0).

## Visual / readability rules (enforced by the lint)
Landscape video sits in ~1/3 of a phone screen in the feed:
headline ≥ 96 px, main line ≥ 64 px, English / secondary ≥ 36 px, nothing visible < 34 px
(except progress-bar labels / credits with `small=True`). No tiny corner HUD text.
Noto Sans SC lacks ✗ and emoji: use Lucide icons (`x`, `check`, ...).

## Sound effects (default since 2026-10-23)
`engine.sfx` synthesizes every effect with numpy (nothing to license) and levels each one by loudness
(BS.1770 momentary), not by ear; one effect per visual event, on its beat, never a melody or a bed (no music).
Typical: `hit` on frame 0 (Douyin's own advice: open with a short punchy sound), `whoosh` peaking on each cut,
`pop` (pitch steps up through a list), `chime` when the result lands, `tick` / `clock`, `buzz`, `step`, `door`,
`page`, `scribble` for what the figures do. Start walks on half beats so the footsteps fall on the beats.

## Optional: original score
`Episode(music=True, bpm=136, cut="slide", bounce=0)` renders the engine's piano + violin score
(VSCO-2 CE samples, CC0) and also writes a `_nomusic` copy (see `episodes/feynman_short`).
You cannot hear: verify music by numbers (tempo, per-section RMS, peaks) and say so.

## Image budget (user has a hard limit on image views)
At most ~4 image views per episode (主动回忆 needed only 2): 1-2 contact sheets, 1 mp4 sheet, cover only if
its layout is new. Never view single frames unless debugging a specific bug. Prefer the lint and numeric checks.

## Sandbox gotchas
- Network: GitHub (+ PyPI, dnf mirrors) only. Pixabay / incompetech / archive.org / music BPM sites are
  blocked, so you can't look up a song's BPM: ask the user.
- `pip --user` fails (read-only) → the venv from `setup_env.sh`. skia needs libEGL/libGL → the script
  unpacks mesa rpms locally (`scripts/cpio_extract.py`, no `cpio` binary).
- `/tmp` is not shared between tool calls: keep files under `/projects/sandbox`.
- `read_file` on a freshly written PNG can fail with ENOENT: run `ls` on it, then read again.
- GitHub rejects files > 100 MB.
