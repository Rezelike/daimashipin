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
    Scene("hook",    4, SC.hook("为什么你[背了就忘]？", "Why ...?", pains=[(icon, line1, line2_red, en<=22ch), ...]), chapter="痛点"),
    Scene("answer",  4, SC.answer("lead", "[核心方法]", "EN TITLE", [(cn, en), ...2-4], colors=[...]),           chapter="答案"),
    Scene("step1",   8, SC.step(1, "标题", "Title", [(point_cn, en)], visual=my_chart, color=PINK),              chapter="3 步"),
    Scene("step2",   8, SC.step(2, "标题", "Title", [(point_cn, en)], example=("例子", "Example", [(cn, en), ...])), chapter="3 步"),
    Scene("step3",   8, SC.step(3, ...),                                                                         chapter="3 步"),
    Scene("summary", 4, SC.summary("一图总结", "EN", [(cn, en), ...]),                                           chapter="总结"),
    Scene("cta",     4, SC.cta("你会用它[做什么]？", "Tell me in the comments", "END TITLE", "EN", next_teaser=(cn, en)), chapter="总结"),
], cover=my_cover_fn, publish=dict(title=..., desc=..., tags=[...]))
if __name__ == "__main__":
    run(EP)
```
- Episode fields: `bpm` (beat grid = the song's BPM; 128: beat 0.469 s, bar 1.875 s, 40 bars = 75 s),
  `music` (False = silent file, default), `cut` ("punch" default | "slide"), `bounce` (frame kick per beat,
  0.010 default), `tail`, `progress_bar`, `glitch_cuts`, `cover`, `publish`; music only: `transpose`, `score`.
- Inside a scene function `fn(c, S)`: `S.B` = local beat (use it for all timing; put events on integers),
  `S.t` local seconds, `S.bars`, `S.rng` (per-frame RNG), `S.beat`; in a step `visual`, `S.vb` = beat
  the card appears (8 with one point line): time the visual's events from it (`S.vb + 2*i` = half bars).
- Factory beat plans: hook question 0, pain cards 4/6/8 · answer lead 0, headline 1, cards 4,5,6,(7),
  save hint after · step splash 0-4, header + point 4, card 8, example lines 10, 14 · summary rows
  2,4,6,8, hint after · cta question 0, icons 2,3,4, end card on the last 2 bars, teaser +2 beats.
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
$V episodes/<slug>/episode.py --cover        # out/<slug>_cover.png
$V episodes/<slug>/episode.py                # out/<slug>.mp4 (silent), out/<slug>_publish.txt + VERIFY
```
Full render of 75 s takes ~1 min on 8 cores. VERIFY includes `beatgrid` (cuts on bar lines) and
`rhythm` (pulse tempo + hardest frame changes measured from the final MP4).
Custom visual helpers worth copying from `episodes/forgetting_curve/episode.py`: `smooth()` (Catmull-Rom
through data points), `partial_path()` (curve that arrives at each point ON a beat), `burst()` (ring
explosion on a landing beat), `axes()` (0-100% grid). The long Feynman video (`feynman/`) is the reference for richer
custom visuals: terminal window, chat bubbles, live chart with counters, Feynman diagram, snowball.
