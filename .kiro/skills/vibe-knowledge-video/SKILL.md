---
name: vibe-knowledge-video
description: Make a 60-75 s landscape (1920x1080) bilingual Chinese/English knowledge video for Douyin / Xiaohongshu / Bilibili ("Vibe知识大赏" style) entirely with code - dark-tech motion graphics, no voice-over, no music (cut to the beat of a DJ track the user adds) - in the Rezelike/daimashipin repo. Use when the user asks to 做视频 / 做下一期 / 知识视频 / 科普视频 / 选题, to re-cut or re-time an episode, or to review Douyin data (播放量, 完播率, 收藏率) for these videos.
metadata:
  author: Rezelike
  version: "1.1"
---

# Vibe knowledge video

Repo: `https://github.com/Rezelike/daimashipin` (clone it if it is not in the workspace).
User defaults: landscape 16:9, **no voice-over**, **no music in the delivered file** (the user adds a
four-on-the-floor "动次打次" DJ track themselves, e.g. 《清明上河图》DJ版), Chinese + English text,
dark-tech style, posts to 抖音 / 小红书 / B站, titles start with `Vibe知识大赏/`.
The user cannot see the sandbox: always report file paths / PR links, and put numbers in chat.

**Read `references/lessons.md` first** (real data from past episodes). Engine API: `references/engine.md`.
Latest worked example: `episodes/forgetting_curve/episode.py` (custom chart / sawtooth / timeline visuals).

## Workflow (do not skip the two approval gates)

1. **Topic** — unless the user already chose, propose 3-5 topics in a table scored on:
   save-worthiness (will people 收藏 it to use later?), relevance to the viewer's own life,
   can it be *shown* with code visuals (curve, timer, chart, diagram), fact base solid.
   Recommend one. **Gate 1: user picks.**
2. **Script** — storyboard in chat: scene · bars · seconds · visual · on-screen CN / EN text.
   Structure (proven): hook 4 bars → answer + overview 4 → 3-4 steps × 8 (example inside each step)
   → summary card 4 → CTA 4. Ask which song / BPM they will use (default **128 BPM** if unknown).
   Fact-check every claim (dates, numbers, quotes); state sources; label illustrations and
   "common practice" as such; add "不构成投资/医疗建议" where relevant. **Gate 2: user approves.**
3. **Environment** (~40 s, idempotent):
   `bash .kiro/skills/vibe-knowledge-video/scripts/setup_env.sh` then
   `/projects/sandbox/.videoenv/vpy -m engine.assets` (from repo root).
4. **Build** — `cp -r episodes/forgetting_curve episodes/<slug>`, rename `slug`, set `bpm`, replace
   strings, write 1-3 custom `visual=` functions for the key idea (the data shows the example is what
   viewers look for). Keep `music=False` unless the user asks for the engine's own score.
5. **Preview** — `$V episodes/<slug>/episode.py --preview` → view **only** `build/contact_sheet.png`.
   Fix everything the lint prints (small text, missing glyphs, text off-screen or overflowing a card).
   Max 2 preview rounds.
6. **Render** — `$V episodes/<slug>/episode.py` (~1 min). Read the VERIFY block: duration, 1920x1080,
   30 fps, size < 95 MB, lint OK, `beatgrid ... OK`, and `rhythm` must show the target BPM and
   "= scene cuts OK". View `build/mp4_sheet.png` once, then `--cover` (view once).
7. **Deliver** — new branch, commit `episodes/<slug>/episode.py` + `out/<slug>.mp4`, `_cover.png`,
   `_publish.txt`; open a PR with `gh api repos/Rezelike/daimashipin/pulls ...` (`gh pr create` does
   not work here). In chat: the MP4 is silent on purpose, the BPM it is cut to, the cut times, how to
   align (song's first strong beat at 0:00), and that changing `bpm` + re-render takes ~1 min.
8. **Data review** (when the user comes back with screenshots) — compare with the table in
   `references/lessons.md` (save %, 2 s bounce, 5 s retention, avg watch, completion, traffic sources),
   explain causes honestly (one video = weak evidence; name what changed), append a row, commit.

## Content rules (from the data)
- Topic must be **save-worthy and about the viewer** (Feynman: 2.39% saves → 11k plays; butterfly
  effect: 0.11% saves → 950 plays). Pure spectacle science keeps viewers but nobody saves it.
- Payoff within **10 s**: say the answer and show the full overview in the `answer` scene.
- Average viewer watches ~9-13 s: no biography, no long intro, no section that only "sets up".
- Put a concrete example inside every step; end with a screenshot-able summary card + 收藏 prompt.
- Hook = one relatable pain-point question + up to 3 short pain cards.
- One idea per screen; one highlighted `[keyword]` per line.

## Rhythm rules (the user's music is a four-on-the-floor DJ beat)
- Everything lives on the beat grid of `Episode(bpm=...)`: scenes are **4 or 8 bars** (DJ phrases),
  cuts land on bar downbeats, every element appears ON a beat (use integer `S.B` values), new
  content every 1-2 bars, data points / nodes land one per half bar.
- Engine defaults do the rest: hard "punch" cut (zoom 1.07→1 + white flash) on each downbeat,
  whole-frame kick on every beat (`bounce=0.010`, "动"), off-beat flicker in the background ("次").
- Unknown tempo → 128 BPM, say so, and offer to re-render once the user tells you the song's BPM.
- Verify by numbers, not by eye: VERIFY's `rhythm` line measures the pulse tempo and cut positions
  in the final file.

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
At most ~4 image views per episode: 1-2 contact sheets, 1 mp4 sheet, 1 cover. Never view single frames
unless debugging a specific bug. Prefer the lint and numeric checks.

## Sandbox gotchas
- Network: GitHub (+ PyPI, dnf mirrors) only. Pixabay / incompetech / archive.org / music BPM sites are
  blocked, so you can't look up a song's BPM: ask the user.
- `pip --user` fails (read-only) → the venv from `setup_env.sh`. skia needs libEGL/libGL → the script
  unpacks mesa rpms locally (`scripts/cpio_extract.py`, no `cpio` binary).
- `/tmp` is not shared between tool calls: keep files under `/projects/sandbox`.
- `read_file` on a freshly written PNG can fail with ENOENT: run `ls` on it, then read again.
- GitHub rejects files > 100 MB.
