---
name: vibe-knowledge-video
description: Make a 60-75 s landscape (1920x1080) bilingual Chinese/English knowledge video for Douyin / Xiaohongshu / Bilibili ("Vibe知识大赏" style) entirely with code - dark-tech motion graphics, no voice-over, no music (cut to the beat of a DJ track the user adds) - in the Rezelike/daimashipin repo. Use when the user asks to 做视频 / 做下一期 / 知识视频 / 科普视频 / 选题, to re-cut or re-time an episode, or to review Douyin data (播放量, 完播率, 收藏率) for these videos.
metadata:
  author: Rezelike
  version: "1.5"
---

# Vibe knowledge video

Repo: `https://github.com/Rezelike/daimashipin` (clone it if it is not in the workspace).
User defaults: landscape 16:9, **no voice-over**, **no music in the delivered file** (the user adds a
four-on-the-floor "动次打次" DJ track themselves, usually 《清明上河图》DJ版 — **128 BPM lines up with
it**, confirmed by the user 2026-10-19), Chinese + English text, dark-tech style, picture never shakes,
**no next-episode teaser: the CTA is the last screen and the video ends directly on the last bar**
(no end card, no fade), posts to 抖音 / 小红书 / B站, titles start with `Vibe知识大赏/`.
The user cannot see the sandbox: always report file paths / PR links, and put numbers in chat.

**Read `references/lessons.md` first** (real data from past episodes). Engine API: `references/engine.md`.
Latest worked example: `episodes/active_recall/episode.py` (experiment bars, dictation sheet, answer check,
A/B comment prompt, direct ending). Curve / sawtooth / timeline visuals: `episodes/forgetting_curve/`.

## Workflow (do not skip the two approval gates)

1. **Topic** — unless the user already chose, propose 3-5 topics in a table scored on:
   save-worthiness (will people 收藏 it to use later?), relevance to the viewer's own life,
   can it be *shown* with code visuals (curve, timer, chart, diagram), fact base solid.
   Recommend one. **Gate 1: user picks.**
2. **Script** — storyboard in chat: scene · bars · seconds · visual · on-screen CN / EN text.
   Structure (current): hook 4 bars → answer + overview 4 → 3-4 steps × 8 (example inside each step)
   → summary card 4 → CTA 4 (no teaser). The hook must carry the payoff (see Content rules): it is the
   only part most viewers see. Use **128 BPM** unless the user names a different song.
   Fact-check every claim (dates, numbers, quotes); state sources; label illustrations and
   "common practice" as such; add "不构成投资/医疗建议" where relevant. **Gate 2: user approves.**
3. **Environment** (~40 s, idempotent):
   `bash .kiro/skills/vibe-knowledge-video/scripts/setup_env.sh` then
   `/projects/sandbox/.videoenv/vpy -m engine.assets` (from repo root).
4. **Build** — `cp -r episodes/active_recall episodes/<slug>`, rename `slug`, set `bpm`, replace
   strings, give the hook an animated opener (`engine.openers`, see Content rules; demo:
   `out/openers_demo.mp4`), write 1-3 custom `visual=` functions for the key idea (the data shows the example is what
   viewers look for). Keep `music=False` unless the user asks for the engine's own score.
5. **Preview** — `$V episodes/<slug>/episode.py --preview` → view **only** `build/contact_sheet.png`.
   Fix everything the lint prints (hook too long, small text, missing glyphs, text off-screen or overflowing a card).
   Max 2 preview rounds.
6. **Render** — `$V episodes/<slug>/episode.py` (~1 min). Read the VERIFY block: duration, 1920x1080,
   30 fps, size < 95 MB, lint OK, `beatgrid ... OK`, `rhythm ... OK` and `shake ... stable`.
   View `build/mp4_sheet.png` once, then run `--cover` (it prints a lint; view the cover image only
   if you designed a new cover layout).
7. **Deliver** — new branch, commit `episodes/<slug>/episode.py` + `out/<slug>.mp4`, `_cover.png`,
   `_publish.txt`; open a PR with `gh api repos/Rezelike/daimashipin/pulls ...` (`gh pr create` does
   not work here). Put the comment question in `publish["pin"]` (pinned comment) and as the caption's
   first line; tell the user to copy-paste the title, not retype it (「主动回忆」 went out as 「主动会议」).
   In chat: the MP4 is silent on purpose, the BPM it is cut to, the cut times, how to
   align (song's first strong beat at 0:00), where to cut the song (video length), and that changing
   `bpm` + re-render takes ~1 min. Each episode branch is stacked on the previous one: say which single
   PR to merge (it contains all earlier ones) — skills only load from `main`.
8. **Data review** (when the user comes back with screenshots) — compare with the table in
   `references/lessons.md` (save %, 2 s bounce, 5 s retention, avg watch, completion, traffic sources),
   explain causes honestly (one video = weak evidence; name what changed), append a row, commit.

## Content rules (from the data)
- Topic must be **save-worthy and about the viewer** (Feynman: 2.39% saves → 11k plays; butterfly
  effect: 0.11% saves → 950 plays). Pure spectacle science keeps viewers but nobody saves it.
- **The first 2 seconds decide everything** (主动回忆: 48% gone at 2 s, 83% at 5 s, avg watch 5 s; every video so
  far stopped after one burst). Frame 0 must already show the hook (the engine does this): ≤ 10 characters,
  two big lines allowed (`hook("为什么你|[学了就忘]？", ...)`), ideally the surprising result itself or an action in
  motion (`hook(..., visual=fn)`). Best so far: butterfly effect opening on a billiards shot (2 s bounce 36%),
  Feynman's two-line question (39%). Worst: a concept title card, a 15-character one-line question (48%).
  Show the overview by ~0:04. No biography, no long intro, no section that only "sets up".
- **Never a text-only opening** (user, 2026-10-20: "开头多做几个动画，不要光是文字"). Every hook gets an animated
  visual: `engine.openers` — `race` (A looks better, then loses after a time skip: comparisons, experiments),
  `dissolve` (learned items dissolve while a counter drops: forgetting), `diverge` (two lines from one point
  end far apart: habits, compounding), `timer` (a clock races through an afternoon: focus) — or a custom one
  built the same way: moving on frame 0, events on beats, the reveal lands by beat 8, nothing shakes.
- Put a concrete example inside every step; end with a screenshot-able summary card + 收藏 prompt.
- CTA: a two-choice question with reply pills (`cta(..., options=[("扣 1 · …", DIM), ("扣 2 · …", VIOLET)])`)
  plus like / save / follow. No "下期" teaser (user, 2026-10-19). But the end is seen by only ~1% of viewers:
  the same question goes into the caption's first line and a pinned comment (`publish["pin"]`).
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
