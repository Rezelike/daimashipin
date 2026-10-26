# Engine reference (repo: Rezelike/daimashipin)

```
engine/core.py     primitives + readability lint      engine/scenes.py   structure scene factories
engine/music.py    score engine + auto arrangement    engine/render.py   Episode, Scene, run() CLI
engine/assets.py   fetch CC0 samples + Lucide icons   episodes/<slug>/episode.py   one file per video
```
Fonts are in `fonts/` (Noto Sans SC Black/Bold/Regular, JetBrains Mono). Assets go to `.assets/` (gitignored).

## Episode skeleton
```python
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from engine import core as K, scenes as SC
from engine.render import Episode, Scene, run

EP = Episode(slug="my_topic", title="...", bpm=128, music=False, scenes=[
    Scene("hook",    4, SC.hook("读 14 遍|输给[考 3 次]", "EN line", visual=my_opening), chapter="开头"),   # <= 10 chars, '|' = 2 lines
    Scene("answer",  4, SC.answer("lead", "[核心方法]", "EN TITLE", [(cn, en), ...2-4], colors=[...]),           chapter="答案"),
    Scene("step1",   8, SC.step(1, "标题", "Title", [(point_cn, en)], visual=my_chart, color=PINK),              chapter="3 步"),
    Scene("step2",   8, SC.step(2, "标题", "Title", [(point_cn, en)], example=("例子", "Example", [(cn, en), ...])), chapter="3 步"),
    Scene("step3",   8, SC.step(3, ...),                                                                         chapter="3 步"),
    Scene("summary", 8, my_summary,                                                                              chapter="照着做"),  # last screen, no CTA
], cover=my_cover_fn, publish=dict(title=..., desc=..., tags=[...]))
if __name__ == "__main__":
    run(EP)
```
- Episode fields: `bpm` (beat grid = the song's BPM; 128: beat 0.469 s, bar 1.875 s, 40 bars = 75 s),
  `tail` (0 = ends exactly on the last bar line, default) and `fade_out` (0 = no fade, default),
  `music` (False = silent file, default), `cut` ("hard" default | "slide" | "punch" = zoom-in, shakes),
  `bounce` (frame kick per beat, 0 default; >0 shakes - the user rejected it), `flash` (0), `pulse`
  (background brightness pulse, 0.6), `glitch_cuts` (False), `tail`, `progress_bar`, `cover`, `publish`;
  music only: `transpose`, `score`.
- A scene fn may declare `fn.static_region = (x0, y0, x1, y1)` + `fn.static_after = beats`: pixels there
  must stay still; VERIFY's `shake` line measures them (step headers and the summary title do this).
- Inside a scene function `fn(c, S)`: `S.B` = local beat (use it for all timing; put events on integers),
  `S.t` local seconds, `S.bars`, `S.rng` (per-frame RNG), `S.beat`; in a step `visual`, `S.vb` = beat
  the card appears (8 with one point line): time the visual's events from it (`S.vb + 2*i` = half bars).
- `hook(question, en, pains=(), accent=PINK, visual=None)`: the question is fully visible on frame 0 (no fade-in),
  one line (<= 124 px) or two lines split with '|' (<= 150 px); `visual(c, S)` draws under it from frame 0 (make it
  already move); pain cards are optional; questions > 10 characters are linted (HOOK TOO LONG).
- `publish=dict(title=..., desc=..., tags=[...], pin="置顶评论")`: `_publish.txt` also gets the pinned comment
  (optional; a comment question lives only there and in the caption, never on screen).
- The ending (user, 2026-10-26: "以后都不要在结尾加上收藏点赞关注啥的"): the 8-bar summary is the last screen - write it as
  your own scene (figures + the screenshot-able table, like `episodes/if_then_plan`'s `summary` without its 「截图保存」
  pill) or use `SC.summary(...)`, whose hint is off by default. No like / save / follow / comment prompt anywhere at
  the end: the lint reports such words in the last 8 bars (END CTA).
- Openers (`from engine import openers as OP`, pass as `hook(..., visual=OP.xxx(...))`; demo: `episodes/openers_demo`):
  `race(a, b, a_vals=(83, 40), b_vals=(71, 61), phases=("5 分钟后", "一周后"), flip=4, land=8, note=, source=)` ·
  `dissolve(words, keep=4, counter_label="还记得")` · `diverge(a_tag, b_tag, a_vals=(1, 37.8), b_vals=(1, 0.03),
  end_label=)` · `timer(t0="14:00", t1="18:00", distractions=[(icon, label)], result=("真正在学", "30 分钟"),
  focus_share=0.125)`. All draw in y 480-1000 under a two-line headline, move from frame 0, land by beat 8.
- Factory beat plans: hook question on frame 0, English typed from beat 1, optional pain cards 4/6/8 · answer lead 0, headline 1, cards 4,5,6,(7)
  · step splash 0-4, header + point 4, card 8, example lines 10, 14 · summary rows 2,4,6,8.
  `answer(save_hint=None)` and `summary(hint=None)` are the defaults; `SC.LEGACY_SAVE_HINT` / `SC.LEGACY_SUMMARY_HINT`
  only keep the posted episodes (主动回忆, 遗忘曲线, 费曼短版, 如果…就…) looking as posted.
- `cta(...)`: LEGACY, old episodes only (comment question, 扣 1 / 扣 2 pills, like / save / follow icons). Never in a
  new episode.
- `answer(..., colors=[...])` and `summary(..., colors=[...])` take per-step colours to match the steps.
- `[keyword]` in Chinese strings = accent colour + glow (`rich`, `pair`, scene factories).

## core primitives
| function | use |
|---|---|
| `text(c, s, x, y, size, face, color, a, align, glow=, ls=, shader=, stroke=, small=False)` | y is the vertical centre. faces: black / bold / reg / mono / monor (mono auto-falls back to CJK) |
| `rich(c, s, x, y, size, face, color, accent, a, align)` | `[bracket]` highlight |
| `pair(c, cn, en, x, y, B, b0, cs=72, es=36, ...)` | CN line + EN line, slides up at beat b0 |
| `ap(B, b0, dur)` / `window(B, b0, b1)` / `pop(B, b0)` | appear progress / visible window / pop scale |
| `with at(c, x, y, s, rot):` | transform block |
| `card`, `pill`, `bubble`, `badge(c, icon, cx, cy, r, color, a)`, `icon(c, name, cx, cy, size, color, a)` | Lucide names: lucide.dev/icons (auto-download) |
| `glow_path(c, path, color, prog)`, `trim_path`, `strike(c, x0, x1, y, prog)` | animated lines / charts |
| `type_on(s, B, b0, cps)`, `grad_shader(c1, c2)`, `beat_pulse(t, beat)` | |
| palette | CYAN BLUE VIOLET PINK AMBER RED GREEN WHITE DIM DIMMER PANEL |

Lint (run by `--preview`, `--lint` and the full render):
- text < 34 px while visible → enlarge it (`small=True` only for decoration)
- missing glyphs (✗, emoji) → draw them as Lucide icons (`x`, `check`)
- text crossing the 60 px screen margin, or starting inside a `card()` and running past its right edge
  → shorten / shrink it (`free=True` only for things meant to sit between cards, like arrows)
- END CTA: 点赞 / 收藏 / 关注 / 三连 / 转发 / 评论 / 扣 1 / 截图保存 visible in the last 8 bars (`K.END_CTA`, `K.END_BARS`)
  → remove the prompt (user, 2026-10-26); ignore only if the word is content, not a prompt

## Little people (`from engine import figures as F`)
Ported from the money-happiness video. Origin = feet centre, scale 1 ≈ 104 px tall, chibi proportions.
| function | use |
|---|---|
| `F.make(seed, top=, hair=, hair_style=, skin=, pants=)` / `F.crowd(n, seed)` | a look (pin any field) / n random looks |
| `F.draw(c, f, x, y, s, alpha, mood=, look=, look_y=, arm_l=, arm_r=, prop=, walk=, bob=, t=)` | one figure. mood -1 sad … 1 laugh; arms `ARM_DOWN / ARM_WRITE / ARM_OUT / ARM_UP` (radians); `prop=dict(kind="pen"/"phone"/"note"/"paper", side=±1, lit=)`; `walk=` phase (use `pi * (B - b0)`: one step per beat); `t=S.gt` for blinking |
| `F.sprite(c, f, x, y, s, alpha, **pose)` | cached bitmap of a fixed pose, for crowds of 10-40 |
| `F.chair` (draw first) → `F.draw` → `F.desk(c, x, floor, w, s)` (returns the desk-top y) | a seated figure: the desk hides everything below its top |
| `F.paper_on`, `F.book_on(opened=)`, `F.phone_on(lit=, buzz=)`, `F.bowl_on` | things lying on a desk top |
| `F.wall_clock(c, x, y, r, minutes)`, `F.door(c, x, floor, s, opened=)`, `F.floor_line(c, x0, x1, floor)` | room props |
Keep figure motion smooth (no per-beat jitter); start actions (stand, walk, open) on beats.
`Episode(cover_size=(1080, 1440))` renders `--cover` at 3:4 for the Douyin profile grid (the cover function draws
its own background; `K.bg_dark_tech` is 16:9 only). `extra_covers={"4x3": (fn, (1440, 1080))}` also writes
`out/<slug>_cover_4x3.png`: Douyin's publish page asks for a 竖封面 (3:4) and a 横封面 (4:3).

## Sound effects (`engine.sfx`, no music)
`Episode(sfx=[(scene_id, local_beat, kind), (scene_id, local_beat, kind, dict(pitch=, pan=, gain=, dur=)), ...])`.
Kinds: `hit whoosh pop pop_big tick chime clock sparkle buzz thump step page scribble error huh swipe rise door`
(`whoosh` peaks ON its cue; `scribble` / `rise` take `dur=` seconds). Levels: `sfx.TARGET` (momentary LUFS per kind),
`gain=` in dB on top; each effect is soft-limited, the mix is kept ≤ -1.5 dBTP (if-then-plan: -18.4 LUFS integrated).
`--sfx` re-makes only the effects and swaps them into the existing `out/<slug>.mp4` (video stream copied).

## Music roles (only with `music=True`; `engine.music.ROLE_DOC`)
intro (hook build, ends on dominant) · theme (main violin theme) · verse (light: arpeggio + pizzicato + bongos) ·
build (rising stabs) · tension (fast spiccato, minor) · release (bright major) · drive (rhythmic stabs, lists) ·
recap (climax, theme +8va) · outro (winds down, last 2 bars = ringing C-major chord, must be >= 3 bars).
`Episode(transpose=+2)` etc. changes key per episode; `Episode(score=fn)` to write the score by hand with
`ostinato / arp16 / stabs / cello / spic / pizz / bongos / timp / melody`.

## CLI (run from repo root, with the env wrapper)
```
V=/projects/sandbox/.videoenv/vpy
$V episodes/<slug>/episode.py --preview      # build/contact_sheet.png (1 image) + lint
$V episodes/<slug>/episode.py --frame 12.3   # single frame (debug)
$V episodes/<slug>/episode.py --music        # music only
$V episodes/<slug>/episode.py --cover        # out/<slug>_cover.png (Episode.cover_size, 3:4 for Douyin)
$V episodes/<slug>/episode.py --sfx          # only the sound effects, muxed into the existing mp4 (~10 s)
$V episodes/<slug>/episode.py                # out/<slug>.mp4 (sound effects if Episode.sfx, else silent) + VERIFY
```
Full render of 75 s takes ~1 min on 8 cores. VERIFY includes `beatgrid` (cuts on bar lines), `rhythm`
(share of visual events landing on a beat + strength of every cut) and `shake` (still areas on vs
between beats), all measured from the final MP4.
Custom visual helpers worth copying from `episodes/forgetting_curve/episode.py`: `smooth()` (Catmull-Rom
through data points), `partial_path()` (curve that arrives at each point ON a beat), `burst()` (ring
explosion on a landing beat), `axes()` (0-100% grid). The long Feynman video (`feynman/`) is the reference for richer
custom visuals: terminal window, chat bubbles, live chart with counters, Feynman diagram, snowball.
