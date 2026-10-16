"""费曼学习法 / The Feynman Technique — 1920x1080 dark-tech explainer, no voice-over.

    python fetch_assets.py          # CC0 samples + Lucide icons (GitHub only)
    python make_music.py            # build/music.wav  (original piano + violin, 136 BPM)
    python make_video.py            # ../out/feynman.mp4
    python make_video.py --preview  # build/contact_sheet.png (24 key frames in one image)
    python make_video.py --frame 63.5   # build/frame_63.50.png
    python make_video.py --cover    # ../out/feynman_cover.png
"""
import argparse, math, os, subprocess, sys
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from timeline import BPM, BEAT, BAR, FPS, W, H, SCENES, DURATION, bar_t  # noqa: E402

BUILD = os.path.join(HERE, "build")
OUT = os.path.join(REPO, "out")
ICONS = os.path.join(HERE, ".assets", "icons")
FONTS = os.path.join(REPO, "fonts")

# ----------------------------------------------------------------------------- palette
def rgb(h, a=255):
    h = h.lstrip("#")
    return skia.ColorSetARGB(a, int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


CYAN, BLUE, VIOLET, PINK = "#22D3EE", "#3B82F6", "#A855F7", "#F472B6"
AMBER, RED, GREEN, WHITE = "#FBBF24", "#F43F5E", "#34D399", "#F1F5F9"
DIM, DIMMER, PANEL, INK = "#94A3B8", "#475569", "#0B1224", "#020617"
STEP_COL = {1: CYAN, 2: VIOLET, 3: PINK, 4: AMBER}

# ----------------------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, k):
    return a + (b - a) * k


def e_out(k):
    k = clamp(k)
    return 1 - (1 - k) ** 3


def e_inout(k):
    k = clamp(k)
    return 4 * k ** 3 if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def e_back(k, s=1.9):
    k = clamp(k)
    return 1 + (s + 1) * (k - 1) ** 3 + s * (k - 1) ** 2


def ap(B, b0, dur=0.9):
    """appear progress (0..1, eased) for beat-time B starting at beat b0"""
    return e_out((B - b0) / dur)


# ----------------------------------------------------------------------------- fonts / text
FACE_FILES = {
    "black": "NotoSansSC-Black.otf", "bold": "NotoSansSC-Bold.otf", "reg": "NotoSansSC-Regular.otf",
    "mono": "JetBrainsMono-Bold.ttf", "monor": "JetBrainsMono-Regular.ttf",
}
_TF = {}
_MISSING = set()


def typeface(face):
    if face not in _TF:
        _TF[face] = skia.Typeface.MakeFromFile(os.path.join(FONTS, FACE_FILES[face]))
    return _TF[face]


@lru_cache(maxsize=512)
def font(face, size):
    f = skia.Font(typeface(face), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def check_glyphs(s, face):
    key = (s, face)
    if key in _MISSING:
        return
    g = font(face, 20).textToGlyphs(s)
    if 0 in list(g):
        _MISSING.add(key)
        bad = "".join(ch for ch in s if 0 in list(font(face, 20).textToGlyphs(ch)))
        print(f"[warn] missing glyphs in {face}: {bad!r} (in {s!r})", file=sys.stderr)


FALLBACK = {"mono": "bold", "monor": "reg"}


@lru_cache(maxsize=4096)
def runs(s, face):
    """split into (face, substring) runs; Latin mono fonts fall back to Noto Sans SC for CJK"""
    fb = FALLBACK.get(face)
    if not fb:
        return ((face, s),)
    f = font(face, 20)
    out = []
    for ch in s:
        fc = face if list(f.textToGlyphs(ch))[0] != 0 else fb
        if out and out[-1][0] == fc:
            out[-1][1] += ch
        else:
            out.append([fc, ch])
    return tuple((a, b) for a, b in out)


def measure(s, face, size, ls=0.0):
    return sum(font(fc, size).measureText(sub) for fc, sub in runs(s, face)) + ls * max(0, len(s) - 1)


def text(c, s, x, y, size, face="bold", color=WHITE, a=1.0, align="c", glow=None, gsig=None,
         ls=0.0, shader=None, stroke=None, glow_a=0.85):
    """Draw text vertically centred on y. Returns drawn width."""
    if not s or a <= 0.003:
        return measure(s, face, size, ls) if s else 0
    size = int(round(size))
    rs = runs(s, face)
    for fc, sub in rs:
        check_glyphs(sub, fc)
    f = font(face, size)
    w = measure(s, face, size, ls)
    x0 = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    m = f.getMetrics()
    base = y - (m.fAscent + m.fDescent) / 2

    def draw(p):
        xx = x0
        for fc, sub in rs:
            ff = font(fc, size)
            if ls:
                for ch in sub:
                    c.drawString(ch, xx, base, ff, p)
                    xx += ff.measureText(ch) + ls
            else:
                c.drawString(sub, xx, base, ff, p)
                xx += ff.measureText(sub)

    if glow:
        p = skia.Paint(AntiAlias=True, Color=rgb(glow))
        p.setAlphaf(clamp(a * glow_a))
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, gsig or size * 0.16))
        if stroke:
            p.setStyle(skia.Paint.kStroke_Style)
            p.setStrokeWidth(stroke)
        draw(p)
    p = skia.Paint(AntiAlias=True, Color=rgb(color))
    p.setAlphaf(clamp(a))
    if shader is not None:
        p.setShader(shader(x0, base + m.fAscent, w, m.fDescent - m.fAscent))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
    draw(p)
    return w


def grad_shader(c1, c2):
    def make(x, y, w, h):
        return skia.GradientShader.MakeLinear([(x, y), (x + w, y + h)], [rgb(c1), rgb(c2)])
    return make


def type_on(s, B, b0, cps_beats=8.0):
    """typewriter: characters revealed per beat"""
    n = int(max(0, (B - b0) * cps_beats))
    return s[:n], n < len(s)


def pair(c, cn, en, x, y, B, b0, cs=56, es=28, color=WHITE, ecol=DIM, align="c", gap=None,
         face="bold", glow=None, dy=26, a=1.0, en_face="monor"):
    """Chinese line + English line beneath, sliding up on appear."""
    k = ap(B, b0) * a
    if k <= 0:
        return
    off = (1 - ap(B, b0)) * dy
    gap = gap if gap is not None else cs * 0.62 + es * 0.62 + 6
    text(c, cn, x, y + off, cs, face, color, k, align, glow=glow)
    if en:
        text(c, en, x, y + gap + off, es, en_face, ecol, k * 0.95, align)


# ----------------------------------------------------------------------------- shapes
def paint(color, a=1.0, stroke=None, cap_round=True, shader=None, blur=None):
    p = skia.Paint(AntiAlias=True, Color=rgb(color))
    p.setAlphaf(clamp(a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap_round:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if shader is not None:
        p.setShader(shader)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def card(c, x, y, w, h, a=1.0, color=CYAN, r=22, fill=PANEL, fill_a=0.78, brackets=True, glow=True):
    if a <= 0.003:
        return
    rect = skia.Rect.MakeXYWH(x, y, w, h)
    if glow:
        c.drawRoundRect(rect, r, r, paint(color, 0.18 * a, blur=26))
    c.drawRoundRect(rect, r, r, paint(fill, fill_a * a))
    c.drawRoundRect(rect, r, r, paint(color, 0.45 * a, stroke=1.6))
    if brackets:
        L = 26
        p = paint(color, 0.95 * a, stroke=3.2)
        for (cx, cy, sx, sy) in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
            path = skia.Path()
            path.moveTo(cx + sx * 4, cy + sy * (L + 4))
            path.lineTo(cx + sx * 4, cy + sy * 4)
            path.lineTo(cx + sx * (L + 4), cy + sy * 4)
            c.drawPath(path, p)


def pill(c, cx, cy, w, h, color, a=1.0, fill_a=0.16):
    rect = skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h)
    c.drawRoundRect(rect, h / 2, h / 2, paint(color, fill_a * a))
    c.drawRoundRect(rect, h / 2, h / 2, paint(color, 0.85 * a, stroke=2))


def trim_path(c, path, p_prog, pnt):
    if p_prog <= 0:
        return
    if p_prog < 1:
        pe = skia.TrimPathEffect.Make(0, clamp(p_prog))
        if pe is None:      # skia returns null for degenerate (near-zero) trims
            return
        pnt.setPathEffect(pe)
    c.drawPath(path, pnt)


def glow_path(c, path, color, prog=1.0, width=4, a=1.0, glow=14):
    if prog <= 0 or a <= 0:
        return
    trim_path(c, path, prog, paint(color, 0.55 * a, stroke=width * 2.6, blur=glow))
    trim_path(c, path, prog, paint(color, a, stroke=width))


# ----------------------------------------------------------------------------- icons
@lru_cache(maxsize=256)
def icon_pic(name, color, sw):
    svg = open(os.path.join(ICONS, f"{name}.svg")).read()
    svg = svg.replace("currentColor", color).replace('stroke-width="2"', f'stroke-width="{sw}"')
    dom = skia.SVGDOM.MakeFromStream(skia.MemoryStream(svg.encode()))
    dom.setContainerSize(skia.Size(24, 24))
    rec = skia.PictureRecorder()
    cc = rec.beginRecording(skia.Rect(-4, -4, 28, 28))
    dom.render(cc)
    return rec.finishRecordingAsPicture()


def icon(c, name, cx, cy, size, color=CYAN, a=1.0, sw=2.0, glow=True, rot=0.0):
    if a <= 0.003:
        return
    pic = icon_pic(name, color, sw)
    c.save()
    c.translate(cx, cy)
    if rot:
        c.rotate(rot)
    s = size / 24
    c.scale(s, s)
    c.translate(-12, -12)
    p = skia.Paint()
    p.setAlphaf(clamp(a))
    if glow:
        sig = 9 / s
        p.setImageFilter(skia.ImageFilters.DropShadow(0, 0, sig, sig, rgb(color, 200)))
    c.drawPicture(pic, None, p)
    c.restore()


def badge_icon(c, name, cx, cy, r, color, a=1.0, B=0.0):
    """icon inside a glowing ring"""
    if a <= 0.003:
        return
    c.drawCircle(cx, cy, r, paint(color, 0.12 * a))
    c.drawCircle(cx, cy, r, paint(color, 0.8 * a, stroke=2.5))
    c.drawCircle(cx, cy, r + 9, paint(color, 0.25 * a, stroke=1.2))
    icon(c, name, cx, cy, r * 1.05, color, a)


# ----------------------------------------------------------------------------- background
class Static:
    bg = None
    overlay = None


def make_static():
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.drawPaint(paint(INK, shader=skia.GradientShader.MakeRadial(
        (W / 2, H * 0.42), 1250, [rgb("#0E1A3A"), rgb("#070D1F"), rgb("#02040A")], [0, 0.55, 1])))
    Static.bg = s.makeImageSnapshot()
    o = skia.Surface(W, H)
    c = o.getCanvas()
    c.clear(0)
    c.drawPaint(paint(INK, shader=skia.GradientShader.MakeRadial(
        (W / 2, H / 2), 1150, [rgb("#000000", 0), rgb("#000000", 0), rgb("#000000", 190)], [0, 0.62, 1])))
    sl = paint("#000000", 0.06)
    for y in range(0, H, 4):
        c.drawRect(skia.Rect.MakeXYWH(0, y, W, 1), sl)
    Static.overlay = o.makeImageSnapshot()


RNG = np.random.default_rng(11)
NP = 90
PX = RNG.uniform(0, W, NP)
PY = RNG.uniform(0, H, NP)
PS = RNG.uniform(0.8, 2.6, NP)
PV = RNG.uniform(6, 28, NP)
PPH = RNG.uniform(0, 6.28, NP)
PC = RNG.choice([CYAN, BLUE, VIOLET], NP)


def beat_pulse(t):
    ph = (t % BEAT) / BEAT
    down = int(t / BEAT) % 4 == 0
    return math.exp(-ph * 5) * (1.0 if down else 0.55)


def draw_background(c, t, energy=1.0):
    c.drawImage(Static.bg, 0, 0)
    pulse = beat_pulse(t) * energy
    # flat grid, slow drift
    g = paint("#1D3A6B", 0.22, stroke=1, cap_round=False)
    off = (t * 9) % 64
    for x in np.arange(-64 + off, W + 64, 64):
        c.drawLine(x, 0, x, 700, g)
    for y in np.arange(-64 + off * 0.5, 700, 64):
        c.drawLine(0, y, W, y, g)
    # perspective floor; one line passes per beat (locked to the music)
    hy, by, vx = 700, H, W / 2
    c.drawRect(skia.Rect.MakeXYWH(0, hy, W, H - hy), paint("#030712", 0.55))
    fl = paint(CYAN, 0.10 + 0.12 * pulse, stroke=1.3, cap_round=False)
    for k in range(-16, 17):
        c.drawLine(vx + k * 34, hy, vx + k * 260, by, fl)
    ph = (t / BEAT) % 1.0
    for i in range(1, 16):
        z = i - ph
        if z <= 0.05:
            continue
        y = hy + (by - hy) * (0.9 / z)
        if y > by:
            continue
        aa = clamp((y - hy) / (by - hy)) * (0.35 + 0.35 * pulse)
        c.drawLine(0, y, W, y, paint(CYAN, aa, stroke=1.4, cap_round=False))
    c.drawRect(skia.Rect.MakeXYWH(0, hy - 2, W, 4), paint(CYAN, 0.25 + 0.3 * pulse, blur=6))
    # horizon glow
    c.drawCircle(vx, hy, 520, paint(BLUE, 0.05 + 0.07 * pulse, blur=160))
    # particles
    ys = (PY - t * PV) % H
    tw = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(t * 2.2 + PPH))
    for i in range(NP):
        c.drawCircle(float(PX[i]), float(ys[i]), float(PS[i]), paint(PC[i], float(tw[i]) * 0.55))


def draw_overlay(c):
    c.drawImage(Static.overlay, 0, 0)


# ----------------------------------------------------------------------------- HUD
CHAPTERS = [  # label cn, label en, scenes
    ("开场", "INTRO", ["hook", "title"]),
    ("费曼", "WHO", ["who"]),
    ("核心", "CORE", ["core"]),
    ("四步法", "4 STEPS", ["step1", "step2", "step3", "step4"]),
    ("实战", "DEMO", ["example"]),
    ("误区", "MISTAKES", ["mistakes"]),
    ("总结", "RECAP", ["recap", "cta"]),
]
SC = {s: (bar_t(b), bar_t(b + n)) for s, b, n in SCENES}


def chapter_spans():
    out = []
    for cn, en, ss in CHAPTERS:
        out.append((cn, en, SC[ss[0]][0], SC[ss[-1]][1]))
    return out


def draw_hud(c, t, sid):
    a = clamp((t - 1.2) / 0.6)
    if t > DURATION - 2.2:
        a *= clamp((DURATION - 0.6 - t) / 1.6)
    if a <= 0:
        return
    # top-left brand
    c.drawRect(skia.Rect.MakeXYWH(64, 46, 14, 14), paint(CYAN, a))
    c.drawRect(skia.Rect.MakeXYWH(64, 46, 14, 14), paint(CYAN, 0.6 * a, blur=8))
    text(c, "FEYNMAN_TECHNIQUE", 92, 53, 19, "mono", CYAN, a * 0.95, "l", ls=1.5)
    text(c, "费曼学习法", 312, 53, 19, "bold", DIM, a * 0.9, "l")
    # top-right chapter + timecode
    spans = chapter_spans()
    idx = max(i for i, s in enumerate(spans) if t >= s[2] - 1e-6)
    cn, en = spans[idx][0], spans[idx][1]
    label = f"{idx + 1:02d}/{len(spans):02d}  {en}"
    w = text(c, label, W - 64, 53, 19, "mono", WHITE, a * 0.9, "r", ls=1.2)
    text(c, cn, W - 64 - w - 16, 53, 19, "bold", DIM, a * 0.9, "r")
    mm, ss = int(t // 60), t % 60
    dot_a = 0.4 + 0.6 * beat_pulse(t)
    c.drawCircle(W - 64 - 8, 86, 5, paint(RED, a * dot_a))
    text(c, f"T+{mm:02d}:{ss:05.2f}", W - 64 - 22, 86, 16, "monor", DIMMER, a, "r")
    # bottom chapter progress bar
    x0, x1, y = 160, W - 160, 1032
    total = spans[-1][3]
    for i, (cn, en, s0, s1) in enumerate(spans):
        sx = x0 + (x1 - x0) * s0 / total + 4
        ex = x0 + (x1 - x0) * s1 / total - 4
        c.drawRoundRect(skia.Rect.MakeLTRB(sx, y - 2.5, ex, y + 2.5), 3, 3, paint(DIMMER, 0.55 * a))
        k = clamp((t - s0) / (s1 - s0))
        if k > 0:
            fx = sx + (ex - sx) * k
            c.drawRoundRect(skia.Rect.MakeLTRB(sx, y - 2.5, fx, y + 2.5), 3, 3, paint(CYAN, a))
            if i == idx:
                c.drawCircle(fx, y, 6, paint(CYAN, a))
                c.drawCircle(fx, y, 12, paint(CYAN, 0.5 * a, blur=8))
        active = i == idx
        text(c, cn, sx, y - 20, 17, "bold", WHITE if active else DIMMER, a * (1 if active else 0.8), "l")


# ----------------------------------------------------------------------------- shared scene parts
def step_header(c, B, num, cn, en, color):
    """Big splash for 5 beats, then docks to the top-left."""
    k = e_inout((B - 5.0) / 1.2)
    # splash
    if k < 1:
        a = ap(B, 0, 0.7) * (1 - k)
        s = lerp(1.25, 1.0, e_back(B / 1.2))
        c.save()
        c.translate(W / 2, 470)
        c.scale(s, s)
        text(c, "STEP", 0, -190, 40, "mono", color, a, ls=14)
        text(c, f"{num:02d}", 0, -40, 230, "mono", color, a * 0.9, stroke=3.5, glow=color, gsig=22)
        pair(c, cn, en, 0, 140, B, 0.6, cs=84, es=34, face="black", glow=color, a=(1 - k))
        c.restore()
    if k > 0:
        a = k
        x = lerp(560, 160, k)
        text(c, f"{num:02d}", x, 168, 86, "mono", color, a, "l", stroke=2.2, glow=color, gsig=12)
        text(c, cn, x + 150, 150, 54, "black", WHITE, a, "l", glow=color, gsig=10, glow_a=0.5)
        text(c, en, x + 152, 204, 29, "monor", color, a, "l")
        c.drawRect(skia.Rect.MakeXYWH(160, 248, 1600 * e_out((B - 5.6) / 2.5), 2), paint(color, 0.5 * a))


def bullets(c, items, x, y, B, starts, color, gap=122, cs=46, es=27, icon_name="check"):
    for i, ((cn, en), b0) in enumerate(zip(items, starts)):
        k = ap(B, b0)
        if k <= 0:
            continue
        yy = y + i * gap
        badge_icon(c, icon_name, x + 26, yy + 14, 22, color, k)
        pair(c, cn, en, x + 72, yy, B, b0, cs=cs, es=es, align="l", gap=52)


def cross_mark(c, cx, cy, r, color, a):
    badge_icon(c, "x", cx, cy, r, color, a)


# ----------------------------------------------------------------------------- scenes
def sc_hook(c, t, T):
    B = t / BEAT
    # 0-6: slam title
    if B < 7:
        out = 1 - clamp((B - 5.6) / 1.0)
        s = lerp(1.5, 1.0, e_back(B / 1.1, 1.4))
        jit = (RNG_FRAME.uniform(-1, 1) * 14 if (B % 4 < 0.25 or B < 0.5) else 0)
        c.save()
        c.translate(W / 2, 430)
        c.scale(s, s)
        for dx, col in [(-6 + jit, RED), (6 - jit, CYAN)]:
            if B < 1.0 or B % 4 < 0.3:
                text(c, "为什么你", dx, -90, 132, "black", col, 0.6 * out)
                text(c, "学了就忘？", -dx, 70, 132, "black", col, 0.6 * out)
        text(c, "为什么你", 0, -90, 132, "black", WHITE, out, glow=CYAN, gsig=18, glow_a=0.45)
        text(c, "学了就忘？", 0, 70, 132, "black", WHITE, out, glow=PINK, gsig=18, glow_a=0.55)
        en, cur = type_on("Why do you forget what you learn?", B, 1.0, 14)
        text(c, en + ("_" if cur or int(B * 2) % 2 else " "), 0, 200, 38, "mono", CYAN, out)
        c.restore()
    # 6-18: three pain points
    if 6 <= B < 19.5:
        out = 1 - clamp((B - 18.4) / 1.0)
        items = [
            ("book-open", "书看了 3 遍", "合上全忘", "Read it 3 times → forgot it all"),
            ("graduation-cap", "上课都听懂", "做题就懵", "Got it in class → lost on the test"),
            ("bookmark", "收藏了 100 篇", "一篇没看", "Saved 100 posts → read none"),
        ]
        for i, (ic, l1, l2, en) in enumerate(items):
            b0 = 6.5 + i * 2
            k = ap(B, b0) * out
            if k <= 0:
                continue
            cx = 400 + i * 560
            y = 300 + (1 - ap(B, b0)) * 40
            card(c, cx - 250, y, 500, 400, k, [CYAN, VIOLET, PINK][i])
            badge_icon(c, ic, cx, y + 85, 40, [CYAN, VIOLET, PINK][i], k)
            text(c, l1, cx, y + 182, 46, "bold", WHITE, k)
            text(c, "↓", cx, y + 234, 34, "bold", DIM, k)
            kk = ap(B, b0 + 1.0) * out
            text(c, l2, cx, y + 290, 58, "black", RED, kk, glow=RED, gsig=12, glow_a=0.6)
            text(c, en, cx, y + 360, 22, "monor", DIM, k)
    # 18-25: not you, your method
    if 18.5 <= B < 26:
        out = 1 - clamp((B - 25.0) / 0.9)
        k1 = ap(B, 18.8) * out
        text(c, "不是你笨。", W / 2, 380, 104, "black", WHITE, k1)
        text(c, "It's not you.", W / 2, 470, 36, "mono", DIM, k1)
        k2 = ap(B, 21.0, 0.6) * out
        s = lerp(1.35, 1.0, e_back((B - 21.0) / 0.9))
        c.save()
        c.translate(W / 2, 640)
        c.scale(s, s)
        text(c, "是方法错了。", 0, 0, 124, "black", WHITE, k2, glow=CYAN, gsig=20, glow_a=0.75,
             shader=grad_shader(CYAN, VIOLET))
        c.restore()
        text(c, "It's your method.", W / 2, 750, 38, "mono", CYAN, k2)
    # 25-32: teaser
    if B >= 25.5:
        k = ap(B, 25.6)
        badge_icon(c, "trophy", W / 2, 330, 60, AMBER, k)
        pair(c, "诺贝尔奖得主的学习方法", "The learning method of a Nobel laureate", W / 2, 490, B, 26.0,
             cs=80, es=34, face="black", glow=AMBER)
        k2 = ap(B, 28.5)
        pill(c, W / 2, 650, 520, 70, CYAN, k2)
        text(c, "4 步 · 学什么都更快", W / 2, 650, 36, "bold", WHITE, k2)


def sc_title(c, t, T):
    B = t / BEAT
    # atom orbits behind the title
    cx, cy = W / 2, 420
    oa = ap(B, 0, 2)
    for i in range(3):
        c.save()
        c.translate(cx, cy)
        c.rotate(i * 60 + B * 6)
        rect = skia.Rect.MakeXYWH(-560, -150, 1120, 300)
        c.drawOval(rect, paint(BLUE, 0.28 * oa, stroke=1.6))
        ang = (B * 0.9 + i * 2.1)
        ex, ey = 560 * math.cos(ang), 150 * math.sin(ang)
        c.drawCircle(ex, ey, 7, paint(CYAN, oa))
        c.drawCircle(ex, ey, 16, paint(CYAN, 0.6 * oa, blur=10))
        c.restore()
    title = "费曼学习法"
    size = 176
    wtot = measure(title, "black", size)
    x = cx - wtot / 2
    for i, ch in enumerate(title):
        b0 = 0.2 + i * 0.35
        k = ap(B, b0, 0.6)
        s = lerp(1.6, 1.0, e_back((B - b0) / 0.8))
        wch = measure(ch, "black", size)
        c.save()
        c.translate(x + wch / 2, cy)
        c.scale(s, s)
        text(c, ch, 0, 0, size, "black", WHITE, k, glow=CYAN, gsig=26, glow_a=0.7,
             shader=grad_shader("#E0F7FF", "#B9A8FF"))
        c.restore()
        x += wch
    en, cur = type_on("THE FEYNMAN TECHNIQUE", B, 2.0, 10)
    text(c, en, cx, cy + 140, 46, "mono", CYAN, 1.0, ls=10)
    pair(c, "4 步，学什么都更快", "4 steps to learn anything faster", cx, cy + 250, B, 5.0, cs=50, es=28)
    k = ap(B, 8.5, 0.6)
    pulse = 0.75 + 0.25 * beat_pulse(t)
    pill(c, cx, 900, 470, 66, AMBER, k * pulse)
    icon(c, "star", cx - 180, 900, 30, AMBER, k)
    text(c, "建议先收藏 · Save this", cx + 18, 900, 30, "bold", WHITE, k)


def feynman_diagram(c, ox, oy, B, b0, s=1.0, a=1.0):
    p = lambda x, y: (ox + x * s, oy + y * s)
    V1, V2 = p(-120, 0), p(120, 0)
    legs = [(p(-330, -190), V1, False), (p(-330, 190), V1, True),
            (V2, p(330, -190), False), (V2, p(330, 190), True)]
    for i, (A_, B_, rev) in enumerate(legs):
        prog = clamp((B - b0 - (0 if i < 2 else 2.2)) / 1.6)
        path = skia.Path()
        path.moveTo(*A_)
        path.lineTo(*B_)
        glow_path(c, path, CYAN, e_inout(prog), 4, a)
        if prog > 0.6:
            mx, my = (A_[0] + B_[0]) / 2, (A_[1] + B_[1]) / 2
            ang = math.atan2(B_[1] - A_[1], B_[0] - A_[0]) + (math.pi if rev else 0)
            tri = skia.Path()
            L = 18 * s
            tri.moveTo(mx + L * math.cos(ang), my + L * math.sin(ang))
            tri.lineTo(mx + L * math.cos(ang + 2.5), my + L * math.sin(ang + 2.5))
            tri.lineTo(mx + L * math.cos(ang - 2.5), my + L * math.sin(ang - 2.5))
            tri.close()
            c.drawPath(tri, paint(CYAN, a * clamp((prog - 0.6) * 3)))
    # photon (wavy)
    prog = clamp((B - b0 - 1.2) / 1.4)
    path = skia.Path()
    n = 200
    for i in range(n + 1):
        u = i / n
        x = lerp(V1[0], V2[0], u)
        y = V1[1] + math.sin(u * math.pi * 2 * 5) * 16 * s
        (path.moveTo if i == 0 else path.lineTo)(x, y)
    glow_path(c, path, VIOLET, e_inout(prog), 3.4, a)
    for V in (V1, V2):
        k = clamp((B - b0 - 1.0) / 0.5) * a
        c.drawCircle(V[0], V[1], 9 * s, paint(WHITE, k))
        c.drawCircle(V[0], V[1], 20 * s, paint(CYAN, 0.6 * k, blur=10))
    la = clamp((B - b0 - 3.6) / 0.8) * a
    for lbl, (x, y) in [("e-", p(-360, -215)), ("e+", p(-360, 215)), ("e-", p(360, -215)),
                        ("e+", p(360, 215)), ("γ", p(0, -48))]:
        text(c, lbl, x, y, 30 * s, "mono", WHITE if lbl != "γ" else VIOLET, la)


def sc_who(c, t, T):
    B = t / BEAT
    # left: Feynman diagram card
    k = ap(B, 0)
    card(c, 130, 190, 760, 640, k, CYAN)
    feynman_diagram(c, 510, 470, B, 0.5, s=0.95, a=k)
    text(c, "费曼图 · FEYNMAN DIAGRAM", 510, 775, 22, "mono", DIM, ap(B, 4), ls=2)
    rx = 980
    if B < 24.5:
        out = 1 - clamp((B - 23.4) / 1.0)
        text(c, "WHO // 他是谁", rx, 230, 24, "mono", CYAN, ap(B, 1) * out, "l", ls=3)
        pair(c, "理查德·费曼", "Richard Feynman", rx, 310, B, 1.5, cs=86, es=36, face="black",
             align="l", glow=CYAN, a=out, gap=78)
        text(c, "1918 – 1988", rx, 445, 30, "mono", DIM, ap(B, 4) * out, "l", ls=2)
        k1 = ap(B, 6) * out
        badge_icon(c, "trophy", rx + 34, 548, 30, AMBER, k1)
        pair(c, "1965 年 诺贝尔物理学奖", "Nobel Prize in Physics, 1965", rx + 90, 535, B, 6,
             cs=46, es=26, align="l", gap=50, a=out)
        k2 = ap(B, 10) * out
        badge_icon(c, "sparkles", rx + 34, 688, 30, VIOLET, k2)
        pair(c, "外号「伟大的解释者」", "a.k.a. \u201cThe Great Explainer\u201d", rx + 90, 675, B, 10,
             cs=46, es=26, align="l", gap=50, a=out)
    else:
        kk = ap(B, 24.6)
        badge_icon(c, "notebook-pen", rx + 34, 262, 30, CYAN, kk)
        pair(c, "他有一本笔记本，标题是：", "He kept a notebook titled:", rx + 90, 250, B, 24.6, cs=40,
             es=24, align="l", gap=46)
        card(c, rx - 10, 360, 790, 250, ap(B, 27), PINK, r=16)
        cn, cur = type_on("《我不知道的事》", B, 27.5, 4)
        text(c, cn, rx + 385, 440, 66, "black", WHITE, ap(B, 27.5), glow=PINK, gsig=14, glow_a=0.6)
        en, cur2 = type_on("NOTEBOOK OF THINGS I DON'T KNOW ABOUT", B, 29.5, 16)
        text(c, en + ("_" if cur2 or int(B * 2) % 2 else ""), rx + 385, 540, 25, "mono", PINK, 1.0)
        k3 = ap(B, 36)
        text(c, "＊「费曼学习法」4 步，是后人从他的学习方式中总结出来的", rx, 680, 27, "reg", DIM, k3, "l")
        text(c, "*The 4-step method was later distilled from how he learned.", rx, 724, 23, "monor",
             DIMMER, k3, "l")


def sc_core(c, t, T):
    B = t / BEAT
    if B < 10.5:
        out = 1 - clamp((B - 9.6) / 0.9)
        k1, k2, k3 = ap(B, 0.2), ap(B, 1.2), ap(B, 2.4, 0.6)
        text(c, "听懂了", lerp(380, 560, k1), 430, 120, "black", DIM, k1 * out)
        text(c, "真懂了", lerp(1540, 1360, k2), 430, 120, "black", WHITE, k2 * out, glow=CYAN, gsig=18)
        s = lerp(2.2, 1.0, e_back((B - 2.4) / 0.8))
        c.save()
        c.translate(W / 2, 425)
        c.scale(s, s)
        text(c, "≠", 0, 0, 150, "black", PINK, k3 * out, glow=PINK, gsig=20)
        c.restore()
        text(c, "Familiar", 560, 560, 38, "mono", DIM, k1 * out)
        text(c, "≠", W / 2, 560, 38, "mono", PINK, k3 * out)
        text(c, "Understood", 1360, 560, 38, "mono", CYAN, k2 * out)
        pair(c, "你觉得懂了，往往只是「眼熟」", "Recognizing something is not the same as knowing it.",
             W / 2, 720, B, 4.5, cs=44, es=26, a=out)
    elif B < 25:
        out = 1 - clamp((B - 24.0) / 0.9)
        k = ap(B, 10.6) * out
        card(c, 210, 230, 1500, 540, k, VIOLET)
        icon(c, "quote", 300, 320, 64, VIOLET, k)
        pair(c, "如果我没法把它讲到大一新生都能听懂，", None, W / 2, 380, B, 11.2, cs=50, a=out)
        pair(c, "说明我们还没有真正理解它。", None, W / 2, 460, B, 12.4, cs=50, a=out, glow=VIOLET)
        text(c, "\u201cI couldn't reduce it to the freshman level.", W / 2, 565, 28, "monor", DIM,
             ap(B, 14) * out)
        text(c, "That means we really don't understand it.\u201d", W / 2, 607, 28, "monor", DIM,
             ap(B, 14.5) * out)
        text(c, "—— 理查德·费曼（据物理学家 David Goodstein 回忆）", W / 2, 700, 26, "reg", VIOLET,
             ap(B, 16) * out)
    else:
        k = ap(B, 25.2)
        s = lerp(1.3, 1.0, e_back((B - 25.2) / 0.9))
        c.save()
        c.translate(W / 2, 430)
        c.scale(s, s)
        text(c, "能讲清楚 = 真的懂", 0, 0, 110, "black", WHITE, k, glow=CYAN, gsig=20,
             shader=grad_shader("#FFFFFF", "#9BE7FF"))
        c.restore()
        text(c, "Explain it simply  =  Truly understand it", W / 2, 545, 36, "mono", CYAN, k)
        k2 = ap(B, 28)
        text(c, "下面 4 步，带你做到  ↓", W / 2, 690, 44, "bold", WHITE, k2)
        text(c, "Here's how, in 4 steps", W / 2, 745, 26, "monor", DIM, k2)


def sc_step1(c, t, T):
    B = t / BEAT
    col = STEP_COL[1]
    step_header(c, B, 1, "选一个概念", "Pick a concept", col)
    if B < 6:
        return
    # left: page
    k = ap(B, 6.5)
    card(c, 160, 300, 700, 640, k, col, r=18)
    text(c, "CONCEPT://", 200, 350, 22, "mono", col, k, "l", ls=2)
    s, cur = type_on("我要学：复利", B, 8.0, 3)
    text(c, s + ("▍" if cur or int(B * 2) % 2 else ""), 200, 420, 54, "black", WHITE, k, "l")
    c.drawRect(skia.Rect.MakeXYWH(200, 470, 620 * ap(B, 9.5, 2), 2), paint(col, 0.7 * k))
    rows = [0.92, 0.76, 0.85, 0.58, 0.8, 0.66]
    for i, wr in enumerate(rows):
        kk = clamp((B - 11 - i * 1.4) / 1.2)
        if kk <= 0:
            continue
        y = 530 + i * 62
        c.drawCircle(214, y, 6, paint(col, kk))
        path = skia.Path()
        path.moveTo(240, y)
        for j in range(1, 30):
            xx = 240 + j * (560 * wr) / 29
            path.lineTo(xx, y + math.sin(j * 1.7 + i) * 4)
        trim_path(c, path, kk, paint(DIM, 0.75, stroke=3))
    # right: instructions
    items = [("拿出一张白纸", "Grab a blank page"),
             ("在顶部写下要学的概念", "Write the concept at the top"),
             ("把你已经知道的，全部写下来", "Write down everything you already know")]
    bullets(c, items, 960, 340, B, [7.5, 10, 13], col)
    k2 = ap(B, 22)
    card(c, 960, 720, 800, 200, k2, AMBER, r=16, brackets=False)
    text(c, "TIP · 越具体越好", 1000, 765, 30, "bold", AMBER, k2, "l")
    text(c, "Be specific", 1300, 767, 22, "monor", DIM, k2, "l")
    cross_mark(c, 1022, 850, 20, RED, ap(B, 24))
    text(c, "经济学", 1060, 850, 40, "bold", DIM, ap(B, 24), "l")
    c.drawLine(1056, 852, 1056 + 124 * ap(B, 25, 0.6), 852, paint(RED, ap(B, 25), stroke=4))
    badge_icon(c, "check", 1290, 850, 20, GREEN, ap(B, 26))
    text(c, "复利", 1328, 850, 40, "black", WHITE, ap(B, 26), "l", glow=GREEN, gsig=8)
    text(c, "Economics  →  Compound interest", 1450, 852, 20, "monor", DIM, ap(B, 26), "l")


def bubble(c, x, y, w, h, color, a, left=True):
    rect = skia.Rect.MakeXYWH(x, y, w, h)
    c.drawRoundRect(rect, 26, 26, paint(color, 0.16 * a))
    c.drawRoundRect(rect, 26, 26, paint(color, 0.8 * a, stroke=2))
    tail = skia.Path()
    if left:
        tail.moveTo(x + 18, y + h - 4)
        tail.lineTo(x - 14, y + h + 16)
        tail.lineTo(x + 46, y + h - 2)
    else:
        tail.moveTo(x + w - 18, y + h - 4)
        tail.lineTo(x + w + 14, y + h + 16)
        tail.lineTo(x + w - 46, y + h - 2)
    c.drawPath(tail, paint(color, 0.8 * a, stroke=2))


def sc_step2(c, t, T):
    B = t / BEAT
    col = STEP_COL[2]
    step_header(c, B, 2, "讲给 12 岁的孩子听", "Teach it to a 12-year-old", col)
    if B < 6:
        return
    k = ap(B, 6.5)
    card(c, 160, 300, 860, 650, k, col, r=18)
    text(c, "CHAT://explain", 200, 345, 22, "mono", col, k, "l", ls=2)
    msgs = [  # (is_kid, cn, en, beat)
        (False, "它本质上是一种指数型增长机制。", "It's essentially an exponential growth mechanism.", 8),
        (True, "啥意思？听不懂……", "Huh? I don't get it...", 12),
        (False, "就像滚雪球，越滚越大。", "Like a snowball. It keeps getting bigger.", 17),
        (True, "哦！懂了！", "Oh! Got it!", 21),
    ]
    y = 390
    for kid, cn, en, b0 in msgs:
        kk = ap(B, b0, 0.6)
        if kk <= 0:
            break
        s = lerp(0.85, 1.0, e_back((B - b0) / 0.7))
        w = max(measure(cn, "bold", 36), measure(en, "monor", 22)) + 56
        h = 112
        x = 250 if kid else 980 - w
        c.save()
        c.translate(x + (0 if kid else w), y + h / 2)
        c.scale(s, s)
        c.translate(-(x + (0 if kid else w)), -(y + h / 2))
        bubble(c, x, y, w, h, VIOLET if kid else CYAN, kk, left=kid)
        text(c, cn, x + 28, y + 40, 36, "bold", WHITE, kk, "l")
        text(c, en, x + 28, y + 82, 22, "monor", DIM, kk, "l")
        c.restore()
        av = "baby" if kid else "graduation-cap"
        badge_icon(c, av, 205 if kid else 990, y + h / 2, 22, VIOLET if kid else CYAN, kk)
        y += h + 34
    items = [("不用术语", "No jargon"),
             ("用大白话、短句子", "Plain words, short sentences"),
             ("真的讲出来，或写下来", "Say it out loud, or write it down")]
    bullets(c, items, 1100, 340, B, [9, 13, 17], col)
    k2 = ap(B, 25)
    card(c, 1100, 720, 660, 200, k2, col, r=16, brackets=False)
    pair(c, "孩子一问「为什么」，", "When a kid asks \u201cwhy?\u201d,", 1140, 765, B, 25, cs=36, es=24, align="l",
         gap=40)
    pair(c, "你就知道哪里没懂。", "you find what you don't know.", 1140, 855, B, 26.5, cs=36, es=24,
         align="l", gap=40, glow=col)


def sc_step3(c, t, T):
    B = t / BEAT
    col = STEP_COL[3]
    step_header(c, B, 3, "找到卡壳点，回去重学", "Find the gaps. Go back to the source.", col)
    if B < 6:
        return
    k = ap(B, 6.5)
    # terminal window
    x, y, w, h = 160, 300, 900, 650
    card(c, x, y, w, h, k, col, r=16, brackets=False)
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, 52), 16, 16, paint("#111a33", 0.95 * k))
    for i, cc in enumerate([RED, AMBER, GREEN]):
        c.drawCircle(x + 30 + i * 26, y + 26, 7, paint(cc, k))
    text(c, "~/brain $ explain --to kid", x + w / 2, y + 26, 20, "monor", DIM, k)
    lines = [  # (beat, text, color, face)
        (8, "> explain(\"复利\")", WHITE, "mono"),
        (10, "  [1] 复利就是利滚利", GREEN, "bold"),
        (12, "  [2] 利息也会再生利息", GREEN, "bold"),
        (14.5, "  [3] 为什么越往后涨得越快？", RED, "bold"),
        (17, "  ERROR: gap detected  // 卡壳了", RED, "mono"),
        (21, "> open textbook --chapter 3", WHITE, "mono"),
        (24, "  [3] 因为本金每年都在变大", GREEN, "bold"),
        (27, "  OK: gap fixed  // 漏洞已补上", GREEN, "mono"),
    ]
    yy = y + 110
    for b0, s, cc, face in lines:
        kk = ap(B, b0, 0.4)
        if kk <= 0:
            break
        shown, cur = type_on(s, B, b0, 22)
        blink = (cc == RED and "ERROR" in s and int(B * 2) % 2 == 0)
        text(c, shown, x + 40, yy, 30 if face == "bold" else 27, face, cc, kk * (0.55 if blink else 1), "l",
             glow=cc if ("ERROR" in s or "OK" in s) else None, gsig=8)
        if s.startswith("  [") and cc != RED:
            pass
        yy += 62
    if B > 14.5 and B < 24:
        kk = ap(B, 14.8) * (1 - clamp((B - 23) / 1))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + 24, y + 110 + 3 * 62 - 30, 640, 60), 10, 10,
                        paint(RED, 0.9 * kk, stroke=2.5))
        badge_icon(c, "triangle-alert", x + 720, y + 110 + 3 * 62, 24, RED, kk)
    rx = 1140
    k1 = ap(B, 17.5)
    card(c, rx, 300, 620, 250, k1, col, r=16)
    text(c, "卡壳的地方", rx + 310, 375, 50, "black", WHITE, k1)
    text(c, "= 你真正不懂的地方", rx + 310, 445, 44, "black", col, k1, glow=col, gsig=12)
    text(c, "Where you get stuck = what you don't know", rx + 310, 507, 22, "monor", DIM, k1)
    bullets(c, [("回到课本 / 原始资料", "Go back to the book / source"),
                ("把漏洞补上，再讲一遍", "Fill the gap, then explain again")],
            rx, 640, B, [21, 26], col, gap=130, cs=40, icon_name="search")


def sc_step4(c, t, T):
    B = t / BEAT
    col = STEP_COL[4]
    step_header(c, B, 4, "简化 + 打比方", "Simplify & use analogies", col)
    if B < 6:
        return
    k = ap(B, 6.5)
    card(c, 160, 300, 860, 650, k, col, r=18)
    text(c, "COMPRESS://", 200, 345, 22, "mono", col, k, "l", ls=2)
    # many grey lines collapse into one bright line
    m = e_inout((B - 13) / 3)
    for i in range(7):
        kk = clamp((B - 7.5 - i * 0.5) / 1)
        if kk <= 0:
            continue
        y0 = 420 + i * 58
        y = lerp(y0, 640, m)
        wl = [700, 620, 680, 540, 660, 590, 450][i] * kk
        wl = lerp(wl, 640, m)
        aa = k * lerp(0.7, 0.0 if i else 1.0, m)
        c.drawRoundRect(skia.Rect.MakeXYWH(220, y - 8, wl, 16), 8, 8, paint(DIMMER, aa))
    if B > 15.5:
        kk = ap(B, 15.5)
        c.drawRoundRect(skia.Rect.MakeXYWH(220, 610, 640, 64), 32, 32, paint(col, 0.18 * kk))
        c.drawRoundRect(skia.Rect.MakeXYWH(220, 610, 640, 64), 32, 32, paint(col, kk, stroke=2.5))
        text(c, "一句话讲清楚", 540, 642, 40, "black", WHITE, kk, glow=col, gsig=10)
        icon(c, "lightbulb", 590, 470, 140 * e_back((B - 16) / 1), col, ap(B, 16), sw=1.6)
        text(c, "ONE SENTENCE", 540, 720, 24, "mono", col, kk, ls=4)
    items = [("能用一句话讲清楚吗？", "Can you say it in one sentence?"),
             ("用生活里的比喻", "Use everyday analogies"),
             ("讲不顺？回到第 1 步，再来一轮", "Still clunky? Back to step 1.")]
    bullets(c, items, 1100, 340, B, [9, 15, 21], col, icon_name="lightbulb")
    # loop
    k2 = ap(B, 26)
    if k2 > 0:
        cx, cy, r = 1430, 800, 92
        c.drawCircle(cx, cy, r, paint(col, 0.2 * k2, stroke=10))
        path = skia.Path()
        path.addArc(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), -90 + B * 40, 300)
        c.drawPath(path, paint(col, k2, stroke=6))
        icon(c, "repeat", cx, cy, 70, col, k2)
        text(c, "1 → 2 → 3 → 4 → 1", cx - 140, cy, 26, "mono", WHITE, k2, "r")
        text(c, "循环直到讲顺", cx + 130, cy - 18, 30, "bold", WHITE, k2, "l")
        text(c, "Loop until smooth", cx + 130, cy + 24, 23, "monor", DIM, k2, "l")


def sc_example(c, t, T):
    B = t / BEAT
    # splash
    if B < 6:
        out = 1 - clamp((B - 5) / 1)
        k = ap(B, 0, 0.6) * out
        text(c, "LIVE DEMO", W / 2, 330, 42, "mono", AMBER, k, ls=16)
        s = lerp(1.3, 1, e_back(B / 1))
        c.save()
        c.translate(W / 2, 470)
        c.scale(s, s)
        text(c, "实战：用费曼法学「复利」", 0, 0, 96, "black", WHITE, k, glow=AMBER, gsig=18)
        c.restore()
        text(c, "Let's try it: Compound Interest", W / 2, 590, 38, "mono", DIM, k)
        return
    # docked title + step tracker
    k = ap(B, 5.6)
    text(c, "实战 · 复利", 160, 160, 48, "black", WHITE, k, "l", glow=AMBER, gsig=10, glow_a=0.5)
    text(c, "DEMO // Compound Interest", 160, 208, 22, "mono", AMBER, k, "l", ls=2)
    stages = [(6, 1, "定义"), (20, 2, "讲给孩子"), (36, 3, "找卡壳"), (60, 4, "打比方")]
    cur = max(i for i, s in enumerate(stages) if B >= s[0])
    for i, (b0, n, lbl) in enumerate(stages):
        x = 1010 + i * 190
        act = i == cur
        cc = STEP_COL[n]
        pill(c, x, 180, 172, 54, cc if i <= cur else DIMMER, k * (1 if act else 0.55), fill_a=0.25 if act else 0.06)
        text(c, f"{n:02d} {lbl}", x, 180, 24, "bold", WHITE if i <= cur else DIM, k)
    c.drawRect(skia.Rect.MakeXYWH(160, 248, 1600, 2), paint(AMBER, 0.4 * k))

    def stage_alpha(b0, b1):
        return ap(B, b0 + 0.3) * (1 - clamp((B - (b1 - 0.9)) / 0.8))

    # 01 textbook definition
    a = stage_alpha(6, 20)
    if a > 0:
        card(c, 260, 330, 1400, 520, a, CYAN)
        badge_icon(c, "book-open", 340, 410, 34, CYAN, a)
        text(c, "课本定义", 400, 400, 40, "bold", CYAN, a, "l")
        text(c, "Textbook", 400, 447, 25, "monor", DIM, a, "l")
        pair(c, "复利：把前一期的利息并入本金，", None, 330, 540, B, 7.5, cs=52, align="l", a=a)
        pair(c, "再计算下一期利息的计息方式。", None, 330, 615, B, 8.5, cs=52, align="l", a=a)
        text(c, "Interest earned on the principal plus all accumulated interest.", 330, 690, 25,
             "monor", DIM, ap(B, 9.5) * a, "l")
        kk = ap(B, 12) * a
        for pre, word, y in [("复利：把前一期的利息并入", "本金", 572), ("再计算下一期利息的", "计息方式", 647)]:
            x0 = 330 + measure(pre, "bold", 52)
            x1 = x0 + measure(word, "bold", 52)
            c.drawLine(x0, y, x0 + (x1 - x0) * ap(B, 12, 1.2), y, paint(RED, kk, stroke=5))
        pill(c, 1330, 770, 440, 64, RED, ap(B, 14) * a)
        icon(c, "triangle-alert", 1150, 770, 30, RED, ap(B, 14) * a)
        text(c, "术语太多 · Too much jargon", 1350, 770, 28, "bold", WHITE, ap(B, 14) * a)
    # 02 explain to a kid
    a = stage_alpha(20, 36)
    if a > 0:
        card(c, 260, 330, 1400, 520, a, VIOLET)
        badge_icon(c, "baby", 340, 410, 34, VIOLET, a)
        text(c, "讲给孩子", 400, 400, 40, "bold", VIOLET, a, "l")
        text(c, "To a 12-year-old", 400, 447, 25, "monor", DIM, a, "l")
        pair(c, "你存了 100 块，银行每年多给你 10%。", "You save \u00a5100. The bank adds 10% every year.",
             330, 540, B, 21.5, cs=50, es=25, align="l", a=a)
        pair(c, "第二年，连那 10 块钱也开始帮你赚钱。", "Next year, that extra \u00a510 starts earning too.",
             330, 680, B, 25, cs=50, es=25, align="l", a=a, glow=VIOLET)
        kk = ap(B, 28) * a
        for i, (lbl, v) in enumerate([("第1年", "100 → 110"), ("第2年", "110 → 121"), ("第3年", "121 → 133.1")]):
            x = 1180 + 0 * i
            text(c, f"{lbl}  {v}", 1630, 390 + i * 42, 24, "mono", WHITE if i < 2 else AMBER,
                 ap(B, 28 + i * 1.2) * a, "r")
    # 03 stuck -> chart
    a = stage_alpha(36, 60)
    if a > 0:
        pair(c, "卡壳：为什么越往后涨得越快？", "Stuck: why does it grow faster and faster?", 160, 330, B, 36.5,
             cs=46, es=24, align="l", a=a, color=WHITE, glow=PINK, gap=50)
        cx0, cy0, cw, ch = 220, 450, 1000, 450
        card(c, cx0 - 60, cy0 - 40, cw + 120, ch + 110, a, PINK, r=16, brackets=False)
        ax = paint(DIMMER, 0.9 * a, stroke=2)
        c.drawLine(cx0, cy0 + ch, cx0 + cw, cy0 + ch, ax)
        c.drawLine(cx0, cy0, cx0, cy0 + ch, ax)
        ymax = 180000
        for v in (50000, 100000, 150000):
            y = cy0 + ch - ch * v / ymax
            c.drawLine(cx0, y, cx0 + cw, y, paint(DIMMER, 0.3 * a, stroke=1))
            text(c, f"{v // 1000}k", cx0 - 14, y, 18, "monor", DIM, a, "r")
        for yr in (0, 10, 20, 30):
            text(c, f"{yr}", cx0 + cw * yr / 30, cy0 + ch + 24, 18, "monor", DIM, a)
        text(c, "年 years", cx0 + cw, cy0 + ch + 52, 18, "reg", DIM, a, "r")
        prog = e_inout((B - 39) / 12)
        n = int(prog * 300)
        for kind, colr, f in [("simple", CYAN, lambda y: 10000 * (1 + 0.1 * y)),
                              ("comp", PINK, lambda y: 10000 * 1.1 ** y)]:
            path = skia.Path()
            for i in range(max(2, n + 1)):
                yr = 30 * i / 300
                px, py = cx0 + cw * yr / 30, cy0 + ch - ch * f(yr) / ymax
                (path.moveTo if i == 0 else path.lineTo)(px, py)
            if prog > 0:
                glow_path(c, path, colr, 1.0, 4, a)
                yr = 30 * prog
                px, py = cx0 + cw * yr / 30, cy0 + ch - ch * f(yr) / ymax
                c.drawCircle(px, py, 8, paint(colr, a))
        yr = 30 * prog
        sv, cv = 10000 * (1 + 0.1 * yr), 10000 * 1.1 ** yr
        rx = 1340
        kk = ap(B, 39) * a
        text(c, "本金 \u00a510,000 · 年化 10%", rx, 470, 28, "bold", WHITE, kk, "l")
        text(c, f"第 {int(round(yr)):>2d} 年 / year", rx, 512, 22, "mono", DIM, kk, "l")
        text(c, "单利 Simple", rx, 580, 26, "bold", CYAN, kk, "l")
        text(c, f"\u00a5{sv:,.0f}", rx, 628, 46, "mono", CYAN, kk, "l")
        text(c, "复利 Compound", rx, 700, 26, "bold", PINK, kk, "l")
        text(c, f"\u00a5{cv:,.0f}", rx, 752, 56, "mono", PINK, kk, "l", glow=PINK, gsig=10)
        k3 = ap(B, 52) * a
        pill(c, 1520, 860, 470, 66, GREEN, k3)
        text(c, "因为「本金」每年都在变大", 1520, 852, 28, "bold", WHITE, k3)
        text(c, "The base grows every year", 1520, 883, 18, "monor", DIM, k3)
        text(c, "*仅为演示复利原理，不构成投资建议 · Illustration only, not financial advice", 160, 962,
             18, "reg", DIMMER, a, "l")
    # 04 analogy: snowball
    a = stage_alpha(60, 81)
    if a > 0:
        card(c, 160, 300, 1600, 620, a, AMBER)
        hx0, hy0, hx1, hy1 = 220, 420, 1000, 860
        hill = skia.Path()
        hill.moveTo(hx0, hy0)
        hill.cubicTo(hx0 + 320, hy0 + 40, hx1 - 380, hy1 - 60, hx1, hy1)
        c.drawPath(hill, paint(WHITE, 0.55 * a, stroke=4))
        u = e_inout((B - 61) / 12)
        # point along the cubic
        def bez(u):
            p0, p1, p2, p3 = (hx0, hy0), (hx0 + 320, hy0 + 40), (hx1 - 380, hy1 - 60), (hx1, hy1)
            x = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u ** 2 * p2[0] + u ** 3 * p3[0]
            y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u ** 2 * p2[1] + u ** 3 * p3[1]
            return x, y
        r = lerp(14, 92, u ** 1.6)
        bx, by = bez(u)
        bx2, by2 = bez(min(1, u + 0.01))
        ang = math.atan2(by2 - by, bx2 - bx)
        nx, ny = -math.sin(ang), math.cos(ang)
        cx, cy = bx - nx * r, by - ny * r
        for j in range(14):
            uu = u - j * 0.02
            if uu <= 0:
                break
            px, py = bez(uu)
            c.drawCircle(px + RNG_FRAME.uniform(-6, 6), py - 6 + RNG_FRAME.uniform(-4, 4), 3,
                         paint(WHITE, 0.4 * a * (1 - j / 14)))
        c.drawCircle(cx, cy, r, paint("#DFF6FF", 0.95 * a))
        c.drawCircle(cx, cy, r + 10, paint(CYAN, 0.35 * a, blur=16))
        rot = (u * 1400) % 360
        c.save()
        c.translate(cx, cy)
        c.rotate(rot)
        icon(c, "snowflake", 0, 0, r * 1.2, BLUE, a * 0.8, glow=False, sw=1.5)
        c.restore()
        rx = 1080
        pair(c, "复利，就像滚雪球：", "Compound interest is like a snowball:", rx, 450, B, 62, cs=52, es=24,
             align="l", a=a, face="black")
        pair(c, "雪球越大，", None, rx, 580, B, 65, cs=58, align="l", a=a, glow=AMBER)
        pair(c, "每滚一圈粘上的雪就越多。", None, rx, 665, B, 66.5, cs=46, align="l", a=a, glow=AMBER)
        text(c, "The bigger it gets, the more snow it picks up each turn.", rx, 747, 23, "monor", DIM,
             ap(B, 67) * a, "l")
        k4 = ap(B, 71) * a
        pill(c, rx + 290, 845, 580, 66, GREEN, k4)
        badge_icon(c, "badge-check", rx + 40, 845, 22, GREEN, k4)
        text(c, "一个比喻，讲清复利 · Got it!", rx + 310, 845, 30, "bold", WHITE, k4)


def sc_mistakes(c, t, T):
    B = t / BEAT
    k = ap(B, 0)
    badge_icon(c, "triangle-alert", 200, 168, 34, RED, k)
    text(c, "3 个常见误区", 260, 150, 54, "black", WHITE, k, "l", glow=RED, gsig=10, glow_a=0.5)
    text(c, "3 common mistakes", 262, 202, 26, "monor", RED, k, "l")
    c.drawRect(skia.Rect.MakeXYWH(160, 248, 1600 * ap(B, 0.5, 3), 2), paint(RED, 0.5 * k))
    rows = [
        ("只在脑子里过一遍", "Just thinking it through", "写下来，或说出来", "Write it down or say it"),
        ("用术语糊弄自己", "Hiding behind jargon", "换成大白话", "Use plain words"),
        ("讲一遍就结束", "One pass and done", "反复循环，直到讲顺", "Loop until it flows"),
    ]
    for i, (w_cn, w_en, r_cn, r_en) in enumerate(rows):
        b0 = 3 + i * 12
        y = 330 + i * 225
        ka = ap(B, b0)
        if ka <= 0:
            continue
        card(c, 160, y - 20, 1600, 180, ka, DIMMER, r=18, brackets=False, glow=False)
        text(c, f"0{i + 1}", 220, y + 70, 54, "mono", DIMMER, ka, "l")
        cross_mark(c, 360, y + 70, 30, RED, ka)
        pair(c, w_cn, w_en, 420, y + 48, B, b0, cs=46, es=24, align="l", color=DIM, gap=52)
        ks = ap(B, b0 + 3, 0.7)
        if ks > 0:
            wcn = measure(w_cn, "bold", 46)
            c.drawLine(416, y + 50, 416 + (wcn + 8) * ks, y + 50, paint(RED, ka, stroke=5))
        kr = ap(B, b0 + 4)
        if kr > 0:
            ax = lerp(1000, 1040, kr)
            text(c, "→", ax, y + 66, 60, "bold", GREEN, kr)
            badge_icon(c, "check", 1140, y + 70, 30, GREEN, kr)
            pair(c, r_cn, r_en, 1195, y + 48, B, b0 + 4, cs=46, es=24, align="l", color=WHITE,
                 glow=GREEN, gap=52)


def sc_recap(c, t, T):
    B = t / BEAT
    k = ap(B, 0)
    text(c, "一图看懂费曼学习法", W / 2, 160, 58, "black", WHITE, k, glow=CYAN, gsig=12, glow_a=0.5)
    text(c, "The whole method in one picture", W / 2, 215, 26, "monor", CYAN, k)
    cx, cy = W / 2, 600
    nodes = [  # angle, num, cn, en
        (-90, 1, "选一个概念", "Pick a concept"),
        (0, 2, "讲给孩子听", "Teach a kid"),
        (90, 3, "找卡壳点", "Find the gaps"),
        (180, 4, "简化 + 比喻", "Simplify"),
    ]
    rx, ry = 520, 255
    ring = skia.Path()
    ring.addOval(skia.Rect.MakeXYWH(cx - rx, cy - ry, 2 * rx, 2 * ry))
    prog = e_inout((B - 1) / 6)
    c.drawPath(ring, paint(DIMMER, 0.5 * k, stroke=3))
    pnt = paint(CYAN, 0.9 * k, stroke=4)
    pnt.setPathEffect(skia.DashPathEffect.Make([26, 22], -B * 30))
    if prog >= 1:
        c.drawPath(ring, pnt)
    else:
        trim_path(c, ring, prog, paint(CYAN, 0.9 * k, stroke=4))
    badge_icon(c, "brain", cx, cy - 10, 62, CYAN, ap(B, 2), B)
    text(c, "真懂", cx, cy + 92, 40, "black", WHITE, ap(B, 2.5))
    for i, (ang, n, cn, en) in enumerate(nodes):
        b0 = 3 + i * 2.5
        kk = ap(B, b0, 0.6)
        if kk <= 0:
            continue
        a = math.radians(ang)
        nx, ny = cx + rx * math.cos(a), cy + ry * math.sin(a)
        col = STEP_COL[n]
        s = lerp(0.6, 1, e_back((B - b0) / 0.8))
        bw, bh = 330, 120
        c.save()
        c.translate(nx, ny)
        c.scale(s, s)
        card(c, -bw / 2, -bh / 2, bw, bh, kk, col, r=18, brackets=False)
        text(c, f"{n:02d}", -bw / 2 + 48, 0, 44, "mono", col, kk, glow=col, gsig=8)
        text(c, cn, -bw / 2 + 95, -16, 34, "bold", WHITE, kk, "l")
        text(c, en, -bw / 2 + 97, 27, 21, "monor", DIM, kk, "l")
        c.restore()
    k2 = ap(B, 14)
    pulse = 0.8 + 0.2 * beat_pulse(t)
    pill(c, 1600, 945, 300, 60, AMBER, k2 * pulse)
    text(c, "截图保存 · Screenshot", 1600, 945, 24, "bold", WHITE, k2)


def sc_cta(c, t, T):
    B = t / BEAT
    end_a = 1 - clamp((B - 34) / 3)
    if B < 33:
        out = 1 - clamp((B - 32) / 1)
        k = ap(B, 0.2)
        text(c, "今天就挑一个概念，试一试", W / 2, 260, 78, "black", WHITE, k * out, glow=CYAN, gsig=14,
             glow_a=0.55)
        text(c, "Pick one concept and try it today.", W / 2, 345, 32, "mono", CYAN, k * out)
        k2 = ap(B, 6)
        card(c, 360, 430, 1200, 170, k2 * out, VIOLET, r=20)
        badge_icon(c, "message-circle", 470, 515, 38, VIOLET, k2 * out)
        text(c, "评论区告诉我：你想用它学什么？", 540, 495, 46, "bold", WHITE, k2 * out, "l")
        text(c, "Tell me in the comments: what will you learn with it?", 542, 554, 26, "monor", DIM,
             k2 * out, "l")
        for i, (ic, cn, en, col) in enumerate([("heart", "点赞", "LIKE", PINK), ("star", "收藏", "SAVE", AMBER),
                                                 ("user-plus", "关注", "FOLLOW", CYAN)]):
            b0 = 12 + i * 2
            kk = ap(B, b0, 0.5) * out
            if kk <= 0:
                continue
            x = W / 2 + (i - 1) * 380
            s = lerp(0.4, 1, e_back((B - b0) / 0.7, 2.4)) * (1 + 0.06 * beat_pulse(t))
            c.save()
            c.translate(x, 790)
            c.scale(s, s)
            c.drawCircle(0, -10, 78, paint(col, 0.14 * kk))
            c.drawCircle(0, -10, 78, paint(col, 0.9 * kk, stroke=3))
            c.drawCircle(0, -10, 92, paint(col, 0.35 * kk, blur=18))
            icon(c, ic, 0, -10, 70, col, kk, sw=2.2)
            text(c, cn, 0, 112, 40, "black", WHITE, kk)
            text(c, en, 0, 156, 20, "mono", col, kk, ls=4)
            c.restore()
    else:
        k = ap(B, 33.2) * end_a
        text(c, "费曼学习法", W / 2, 440, 130, "black", WHITE, k, glow=CYAN, gsig=24,
             shader=grad_shader("#E0F7FF", "#B9A8FF"))
        text(c, "THE FEYNMAN TECHNIQUE", W / 2, 560, 38, "mono", CYAN, k, ls=10)
        text(c, "选概念 → 讲给孩子 → 找卡壳 → 简化", W / 2, 650, 32, "bold", DIM, k)
        text(c, "Music: original score made with VSCO 2 CE samples (CC0)  ·  Icons: Lucide (ISC)", W / 2,
             930, 17, "monor", DIMMER, k)


SCENE_FN = {
    "hook": sc_hook, "title": sc_title, "who": sc_who, "core": sc_core, "step1": sc_step1,
    "step2": sc_step2, "step3": sc_step3, "step4": sc_step4, "example": sc_example,
    "mistakes": sc_mistakes, "recap": sc_recap, "cta": sc_cta,
}
RNG_FRAME = np.random.default_rng(0)


# ----------------------------------------------------------------------------- frame
def scene_at(t):
    for sid, b, n in SCENES:
        s0, s1 = bar_t(b), bar_t(b + n)
        if s0 <= t < s1:
            return sid, s0, s1
    sid, b, n = SCENES[-1]
    return sid, bar_t(b), bar_t(b + n)


def render_frame(c, surf, t, fi):
    global RNG_FRAME
    RNG_FRAME = np.random.default_rng(fi * 7919 + 13)
    sid, s0, s1 = scene_at(t)
    lt = t - s0
    draw_background(c, t)
    # scene enter / exit
    a_in = e_out(lt / 0.28)
    a_out = 1 - clamp((lt - (s1 - s0 - 0.22)) / 0.22) if sid != "cta" else 1
    a = min(a_in, a_out)
    c.saveLayerAlpha(None, int(255 * clamp(a)))
    dy = (1 - a_in) * 18
    c.translate(0, dy)
    SCENE_FN[sid](c, lt, s1 - s0)
    c.restore()
    draw_hud(c, t, sid)
    # glitch flash on every cut (and the hook slam)
    if lt < 0.2 and t > 0.05 or t < 0.12:
        snap = surf.makeImageSnapshot()
        k = 1 - lt / 0.2 if t > 0.05 else 1 - t / 0.12
        for _ in range(7):
            y = RNG_FRAME.uniform(0, H)
            h = RNG_FRAME.uniform(8, 60)
            dx = RNG_FRAME.uniform(-60, 60) * k
            src = skia.Rect.MakeXYWH(0, y, W, h)
            dst = skia.Rect.MakeXYWH(dx, y, W, h)
            p = skia.Paint()
            p.setAlphaf(0.85 * k)
            c.drawImageRect(snap, src, dst, skia.SamplingOptions(), p)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), paint(CYAN, 0.10 * k))
        yy = H * (lt / 0.2 if t > 0.05 else t / 0.12)
        c.drawRect(skia.Rect.MakeXYWH(0, yy - 3, W, 6), paint(WHITE, 0.7 * k, blur=4))
    draw_overlay(c)
    # global fade-out at the very end
    if t > DURATION - 1.2:
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), paint("#000000", clamp((t - (DURATION - 1.2)) / 1.0)))


def new_surface():
    arr = np.zeros((H, W, 4), np.uint8)
    surf = skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    return arr, surf


def ffmpeg_exe():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def render_chunk(args):
    idx, f0, f1, path = args
    make_static()
    arr, surf = new_surface()
    c = surf.getCanvas()
    cmd = [ffmpeg_exe(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-tune", "animation", "-maxrate", "3500k", "-bufsize", "7000k", "-g", "60",
           "-pix_fmt", "yuv420p", path]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        c.save()
        c.clear(skia.ColorBLACK)
        render_frame(c, surf, fi / FPS, fi)
        c.restore()
        pr.stdin.write(arr.tobytes())
    pr.stdin.close()
    pr.wait()
    return idx, f1 - f0


def render_png(t, path, scale=1.0):
    make_static()
    arr, surf = new_surface()
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    render_frame(c, surf, t, int(t * FPS))
    img = surf.makeImageSnapshot()
    if scale != 1.0:
        img = img.resize(int(W * scale), int(H * scale))
    img.save(path)
    return img


def contact_sheet(times, path, cols=6, scale=0.25):
    tw, th = int(W * scale), int(H * scale)
    rows = math.ceil(len(times) / cols)
    sheet = skia.Surface(cols * tw, rows * (th + 26))
    sc = sheet.getCanvas()
    sc.clear(skia.ColorBLACK)
    make_static()
    arr, surf = new_surface()
    c = surf.getCanvas()
    for i, t in enumerate(times):
        c.clear(skia.ColorBLACK)
        render_frame(c, surf, t, int(t * FPS))
        img = surf.makeImageSnapshot()
        x, y = (i % cols) * tw, (i // cols) * (th + 26)
        sc.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw, th), skia.SamplingOptions(skia.FilterMode.kLinear))
        text(sc, f"{t:6.2f}s  {scene_at(t)[0]}", x + 8, y + th + 13, 16, "mono", "#FFFFFF", 1, "l")
    sheet.makeImageSnapshot().save(path)


def cover(path):
    make_static()
    arr, surf = new_surface()
    c = surf.getCanvas()
    draw_background(c, 3.3)
    t = 0
    for i in range(3):
        c.save()
        c.translate(W / 2, 470)
        c.rotate(i * 60 + 20)
        c.drawOval(skia.Rect.MakeXYWH(-640, -170, 1280, 340), paint(BLUE, 0.3, stroke=2))
        c.restore()
    text(c, "学了就忘？", W / 2, 230, 92, "black", PINK, 1, glow=PINK, gsig=16)
    text(c, "费曼学习法", W / 2, 450, 230, "black", WHITE, 1, glow=CYAN, gsig=30,
         shader=grad_shader("#E0F7FF", "#B9A8FF"))
    text(c, "THE FEYNMAN TECHNIQUE", W / 2, 610, 52, "mono", CYAN, 1, ls=12)
    pill(c, W / 2, 760, 860, 110, AMBER, 1, fill_a=0.22)
    text(c, "4 步，学什么都更快", W / 2, 760, 62, "black", WHITE, 1)
    text(c, "诺贝尔奖得主的学习法 · 中英双语", W / 2, 900, 38, "bold", DIM, 1)
    draw_overlay(c)
    surf.makeImageSnapshot().save(path)


def main():
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--preview", action="store_true")
    ap_.add_argument("--frame", type=float, nargs="*")
    ap_.add_argument("--times", type=float, nargs="*")
    ap_.add_argument("--cover", action="store_true")
    ap_.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    args = ap_.parse_args()
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if args.frame:
        for t in args.frame:
            p = os.path.join(BUILD, f"frame_{t:06.2f}.png")
            render_png(t, p)
            print(p)
        return
    if args.preview:
        times = args.times or [1.0, 6.0, 9.5, 13.0, 18.0, 25.0, 33.0, 40.0, 48.0, 53.0, 62.0, 75.0,
                               95.0, 105.0, 120.0, 132.0, 147.0, 160.0, 172.0, 182.0, 195.0, 205.0,
                               215.0, 227.0]
        p = os.path.join(BUILD, "contact_sheet.png")
        contact_sheet(times, p)
        print(p)
        return
    if args.cover:
        p = os.path.join(OUT, "feynman_cover.png")
        cover(p)
        print(p)
        return
    music = os.path.join(BUILD, "music.wav")
    assert os.path.exists(music), "run make_music.py first"
    total = int(round(DURATION * FPS))
    n = args.workers * 3
    bounds = [round(i * total / n) for i in range(n + 1)]
    jobs = [(i, bounds[i], bounds[i + 1], os.path.join(BUILD, f"seg_{i:03d}.mp4")) for i in range(n)]
    done = 0
    with Pool(args.workers) as pool:
        for idx, cnt in pool.imap_unordered(render_chunk, jobs):
            done += cnt
            print(f"  segment {idx:3d} done  ({done}/{total} frames)", flush=True)
    lst = os.path.join(BUILD, "segments.txt")
    with open(lst, "w") as f:
        for j in jobs:
            f.write(f"file '{j[3]}'\n")
    out = os.path.join(OUT, "feynman.mp4")
    subprocess.run([ffmpeg_exe(), "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", music,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    for j in jobs:
        os.remove(j[3])
    print(out, f"{os.path.getsize(out) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
