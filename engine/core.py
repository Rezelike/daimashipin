"""Drawing primitives for 1920x1080 dark-tech knowledge videos (skia).

Readability rules are enforced by a lint: any text drawn smaller than MIN_TEXT px (and visible)
is recorded unless small=True is passed. Landscape videos are shown at ~1/3 screen height in the
phone feed, so: headline >= 96, main line >= 64, English / secondary >= 36.
"""
import math
import os
import sys
from contextlib import contextmanager
from functools import lru_cache

import numpy as np
import skia

from . import FONTS
from .assets import icon_path

W, H, FPS = 1920, 1080, 30
MIN_TEXT = 34

# ----------------------------------------------------------------------------- palette
CYAN, BLUE, VIOLET, PINK = "#22D3EE", "#3B82F6", "#A855F7", "#F472B6"
AMBER, RED, GREEN, WHITE = "#FBBF24", "#F43F5E", "#34D399", "#F1F5F9"
DIM, DIMMER, PANEL, INK = "#94A3B8", "#475569", "#0B1224", "#020617"
ACCENTS = [CYAN, VIOLET, PINK, AMBER, GREEN, BLUE]


def rgb(h, a=255):
    h = h.lstrip("#")
    return skia.ColorSetARGB(a, int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


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
    """appear progress 0..1 (eased) at local beat B for an element starting at beat b0"""
    return e_out((B - b0) / dur)


def window(B, b0, b1, fade_in=0.9, fade_out=0.8):
    """visible between beats b0..b1 with fades (for swapping content inside one scene)"""
    return e_out((B - b0) / fade_in) * (1 - clamp((B - (b1 - fade_out)) / fade_out))


def pop(B, b0, dur=0.8, frm=0.6, s=1.9):
    """scale for a pop-in: frm -> 1 with overshoot"""
    return lerp(frm, 1.0, e_back((B - b0) / dur, s))


@contextmanager
def at(c, x, y, s=1.0, rot=0.0):
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    if s != 1.0:
        c.scale(s, s)
    try:
        yield
    finally:
        c.restore()


# ----------------------------------------------------------------------------- fonts / text
FACE_FILES = {
    "black": "NotoSansSC-Black.otf", "bold": "NotoSansSC-Bold.otf", "reg": "NotoSansSC-Regular.otf",
    "mono": "JetBrainsMono-Bold.ttf", "monor": "JetBrainsMono-Regular.ttf",
}
FALLBACK = {"mono": "bold", "monor": "reg"}
LINT = {"small": set(), "missing": set(), "edge": set()}
SAFE = 60   # px margin; text crossing it is reported
FRAME_CARDS = []   # card rects drawn in the current frame (device coords), for the overflow lint
_TF = {}


def typeface(face):
    if face not in _TF:
        _TF[face] = skia.Typeface.MakeFromFile(os.path.join(FONTS, FACE_FILES[face]))
    return _TF[face]


@lru_cache(maxsize=1024)
def font(face, size):
    f = skia.Font(typeface(face), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


@lru_cache(maxsize=8192)
def runs(s, face):
    """(face, substring) runs: Latin mono faces fall back to Noto Sans SC for CJK / missing glyphs."""
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


def measure(s, face="bold", size=48, ls=0.0):
    size = int(round(size))
    return sum(font(fc, size).measureText(sub) for fc, sub in runs(s, face)) + ls * max(0, len(s) - 1)


def _lint(s, face, size, a, small):
    if a > 0.5 and size < MIN_TEXT and not small and s.strip():
        LINT["small"].add((int(size), s[:40]))
    for fc, sub in runs(s, face):
        g = list(font(fc, 20).textToGlyphs(sub))
        if 0 in g:
            LINT["missing"].add((fc, "".join(ch for ch in sub if list(font(fc, 20).textToGlyphs(ch))[0] == 0)))


def text(c, s, x, y, size, face="bold", color=WHITE, a=1.0, align="c", glow=None, gsig=None,
         ls=0.0, shader=None, stroke=None, glow_a=0.85, small=False, free=False):
    """Draw text vertically centred on y. align: 'l' | 'c' | 'r'. Returns width.
    small=True: allow < MIN_TEXT (decoration only). free=True: skip the card-overflow lint."""
    size = int(round(size))
    if not s or a <= 0.003:
        return measure(s, face, size, ls) if s else 0
    _lint(s, face, size, a, small)
    rs = runs(s, face)
    w = measure(s, face, size, ls)
    x0 = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    if a > 0.5 and not small:
        mx = c.getTotalMatrix()
        l, r = mx.mapXY(x0, y).x(), mx.mapXY(x0 + w, y).x()
        yy = mx.mapXY(x0, y).y()
        if c.getBaseLayerSize().width() == W and (l < SAFE - 1 or r > W - SAFE + 1):
            LINT["edge"].add((int(l), int(r), s[:40]))
        for cl, ct, cr, cb in ([] if free else FRAME_CARDS):
            if cl <= l <= cr and ct <= yy <= cb and r > cr - 8:
                LINT["edge"].add((int(l), int(r), "overflows its card: " + s[:40]))
                break
    m = font(face, size).getMetrics()
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


def _segments(s):
    """'房间不打扫，就会[落满灰]。' -> [('房间不打扫，就会', False), ('落满灰', True), ('。', False)]"""
    out, cur, acc = [], "", False
    for ch in s:
        if ch == "[" and not acc:
            if cur:
                out.append((cur, False))
            cur, acc = "", True
        elif ch == "]" and acc:
            out.append((cur, True))
            cur, acc = "", False
        else:
            cur += ch
    if cur:
        out.append((cur, acc))
    return out


def rich_width(s, size, face="black"):
    return sum(measure(seg, face, size) for seg, _ in _segments(s))


def rich(c, s, x, y, size, face="black", color=WHITE, accent=AMBER, a=1.0, align="c", glow_accent=True,
         small=False):
    """Text with [bracketed] keywords drawn in the accent colour (with glow)."""
    segs = _segments(s)
    w = sum(measure(seg, face, size) for seg, _ in segs)
    xx = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    for seg, hl in segs:
        xx += text(c, seg, xx, y, size, face, accent if hl else color, a, "l",
                   glow=accent if (hl and glow_accent) else None, gsig=size * 0.14, glow_a=0.7, small=small)
    return w


def pair(c, cn, en, x, y, B, b0, cs=72, es=36, color=WHITE, ecol=DIM, accent=AMBER, align="c",
         face="black", en_face="monor", a=1.0, dy=28, gap=None):
    """Chinese line ([keyword] highlight supported) + English line, sliding up when it appears."""
    k = ap(B, b0) * a
    if k <= 0:
        return
    off = (1 - ap(B, b0)) * dy
    gap = gap if gap is not None else cs * 0.62 + es * 0.62 + 8
    rich(c, cn, x, y + off, cs, face, color, accent, k, align)
    if en:
        text(c, en, x, y + gap + off, es, en_face, ecol, k * 0.95, align)


def type_on(s, B, b0, chars_per_beat=8.0):
    n = int(max(0, (B - b0) * chars_per_beat))
    return s[:n], n < len(s)


def grad_shader(c1, c2):
    def make(x, y, w, h):
        return skia.GradientShader.MakeLinear([(x, y), (x + w, y + h)], [rgb(c1), rgb(c2)])
    return make


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


def card(c, x, y, w, h, a=1.0, color=CYAN, r=22, fill=PANEL, fill_a=0.8, brackets=True, glow=True):
    if a <= 0.003:
        return
    rect = skia.Rect.MakeXYWH(x, y, w, h)
    dr = c.getTotalMatrix().mapRect(rect)
    FRAME_CARDS.append((dr.left(), dr.top(), dr.right(), dr.bottom()))
    if glow:
        c.drawRoundRect(rect, r, r, paint(color, 0.18 * a, blur=26))
    c.drawRoundRect(rect, r, r, paint(fill, fill_a * a))
    c.drawRoundRect(rect, r, r, paint(color, 0.5 * a, stroke=2))
    if brackets:
        L = 30
        p = paint(color, 0.95 * a, stroke=3.5)
        for (cx, cy, sx, sy) in [(x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)]:
            path = skia.Path()
            path.moveTo(cx + sx * 4, cy + sy * (L + 4))
            path.lineTo(cx + sx * 4, cy + sy * 4)
            path.lineTo(cx + sx * (L + 4), cy + sy * 4)
            c.drawPath(path, p)


def pill(c, cx, cy, w, h, color, a=1.0, fill_a=0.18):
    if a <= 0.003:
        return
    rect = skia.Rect.MakeXYWH(cx - w / 2, cy - h / 2, w, h)
    c.drawRoundRect(rect, h / 2, h / 2, paint(color, fill_a * a))
    c.drawRoundRect(rect, h / 2, h / 2, paint(color, 0.9 * a, stroke=2.5))


def trim_path(c, path, prog, pnt):
    if prog <= 0:
        return
    if prog < 1:
        pe = skia.TrimPathEffect.Make(0, clamp(prog))
        if pe is None:          # skia returns null for degenerate trims
            return
        pnt.setPathEffect(pe)
    c.drawPath(path, pnt)


def glow_path(c, path, color, prog=1.0, width=4, a=1.0, glow=14):
    if prog <= 0 or a <= 0:
        return
    trim_path(c, path, prog, paint(color, 0.55 * a, stroke=width * 2.6, blur=glow))
    trim_path(c, path, prog, paint(color, a, stroke=width))


def strike(c, x0, x1, y, prog, color=RED, a=1.0, width=6):
    if prog > 0:
        c.drawLine(x0, y, x0 + (x1 - x0) * clamp(prog), y, paint(color, a, stroke=width))


def bubble(c, x, y, w, h, color, a, left=True):
    rect = skia.Rect.MakeXYWH(x, y, w, h)
    c.drawRoundRect(rect, 28, 28, paint(color, 0.16 * a))
    c.drawRoundRect(rect, 28, 28, paint(color, 0.85 * a, stroke=2.5))
    tail = skia.Path()
    if left:
        tail.moveTo(x + 20, y + h - 4)
        tail.lineTo(x - 16, y + h + 18)
        tail.lineTo(x + 50, y + h - 2)
    else:
        tail.moveTo(x + w - 20, y + h - 4)
        tail.lineTo(x + w + 16, y + h + 18)
        tail.lineTo(x + w - 50, y + h - 2)
    c.drawPath(tail, paint(color, 0.85 * a, stroke=2.5))


# ----------------------------------------------------------------------------- icons (Lucide)
@lru_cache(maxsize=512)
def _icon_pic(name, color, sw):
    svg = open(icon_path(name)).read()
    svg = svg.replace("currentColor", color).replace('stroke-width="2"', f'stroke-width="{sw}"')
    dom = skia.SVGDOM.MakeFromStream(skia.MemoryStream(svg.encode()))
    dom.setContainerSize(skia.Size(24, 24))
    rec = skia.PictureRecorder()
    cc = rec.beginRecording(skia.Rect(-4, -4, 28, 28))
    dom.render(cc)
    return rec.finishRecordingAsPicture()


def icon(c, name, cx, cy, size, color=CYAN, a=1.0, sw=2.0, glow=True, rot=0.0):
    """Lucide icon by name (lucide.dev/icons), downloaded on first use."""
    if a <= 0.003:
        return
    pic = _icon_pic(name, color, sw)
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


def badge(c, name, cx, cy, r, color, a=1.0):
    """icon inside a glowing ring"""
    if a <= 0.003:
        return
    c.drawCircle(cx, cy, r, paint(color, 0.12 * a))
    c.drawCircle(cx, cy, r, paint(color, 0.85 * a, stroke=2.5))
    c.drawCircle(cx, cy, r + 10, paint(color, 0.25 * a, stroke=1.2))
    icon(c, name, cx, cy, r * 1.05, color, a)


# ----------------------------------------------------------------------------- background
class _Static:
    bg = None
    overlay = None


def make_static():
    if _Static.bg is not None:
        return
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.drawPaint(paint(INK, shader=skia.GradientShader.MakeRadial(
        (W / 2, H * 0.42), 1250, [rgb("#0E1A3A"), rgb("#070D1F"), rgb("#02040A")], [0, 0.55, 1])))
    _Static.bg = s.makeImageSnapshot()
    o = skia.Surface(W, H)
    c = o.getCanvas()
    c.clear(0)
    c.drawPaint(paint(INK, shader=skia.GradientShader.MakeRadial(
        (W / 2, H / 2), 1150, [rgb("#000000", 0), rgb("#000000", 0), rgb("#000000", 190)], [0, 0.62, 1])))
    sl = paint("#000000", 0.05)
    for y in range(0, H, 4):
        c.drawRect(skia.Rect.MakeXYWH(0, y, W, 1), sl)
    _Static.overlay = o.makeImageSnapshot()


_R = np.random.default_rng(11)
_NP = 90
_PX, _PY = _R.uniform(0, W, _NP), _R.uniform(0, H, _NP)
_PS, _PV, _PPH = _R.uniform(0.8, 2.6, _NP), _R.uniform(6, 28, _NP), _R.uniform(0, 6.28, _NP)
_PC = _R.choice([CYAN, BLUE, VIOLET], _NP)


def beat_pulse(t, beat):
    ph = (t % beat) / beat
    down = int(t / beat) % 4 == 0
    return math.exp(-ph * 5) * (1.0 if down else 0.55)


def kick(t, beat, decay=7.0):
    """'动': sharp hit on every beat (four-on-the-floor), strongest on the bar's downbeat"""
    ph = (t % beat) / beat
    return math.exp(-ph * decay) * (1.0 if int(t / beat) % 4 == 0 else 0.6)


def hat(t, beat, decay=9.0):
    """'次': off-beat hi-hat tick, halfway between beats"""
    return math.exp(-(((t / beat) + 0.5) % 1.0) * decay)


def bg_dark_tech(c, t, beat, energy=1.0):
    """grid + perspective floor scrolling one line per beat + drifting particles"""
    make_static()
    c.drawImage(_Static.bg, 0, 0)
    pulse = beat_pulse(t, beat) * energy
    g = paint("#1D3A6B", 0.22, stroke=1, cap_round=False)
    off = (t * 9) % 64
    for x in np.arange(-64 + off, W + 64, 64):
        c.drawLine(float(x), 0, float(x), 700, g)
    for y in np.arange(-64 + off * 0.5, 700, 64):
        c.drawLine(0, float(y), W, float(y), g)
    hy, by, vx = 700, H, W / 2
    c.drawRect(skia.Rect.MakeXYWH(0, hy, W, H - hy), paint("#030712", 0.55))
    fl = paint(CYAN, 0.12 + 0.12 * pulse, stroke=1.3, cap_round=False)
    for k in range(-16, 17):
        c.drawLine(vx + k * 34, hy, vx + k * 260, by, fl)
    ph = (t / beat) % 1.0
    for i in range(1, 16):
        z = i - ph
        if z <= 0.05:
            continue
        y = hy + (by - hy) * (0.9 / z)
        if y > by:
            continue
        aa = clamp((y - hy) / (by - hy)) * (0.42 + 0.35 * pulse)
        c.drawLine(0, y, W, y, paint(CYAN, aa, stroke=1.4, cap_round=False))
    hh = hat(t, beat) * energy
    c.drawRect(skia.Rect.MakeXYWH(0, hy - 2, W, 4), paint(CYAN, 0.25 + 0.3 * pulse + 0.15 * hh, blur=6))
    c.drawCircle(vx, hy, 520, paint(BLUE, 0.05 + 0.07 * pulse, blur=160))
    ys = (_PY - t * _PV) % H
    tw = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(t * 2.2 + _PPH)) + 0.45 * hh
    for i in range(_NP):
        c.drawCircle(float(_PX[i]), float(ys[i]), float(_PS[i]), paint(_PC[i], float(tw[i]) * 0.55))


def overlay(c):
    make_static()
    c.drawImage(_Static.overlay, 0, 0)


def lint_report(lint=None):
    lint = lint or LINT
    lines = []
    if lint["missing"]:
        lines.append("MISSING GLYPHS (will render as boxes): " + ", ".join(f"{f}:{s!r}" for f, s in sorted(lint["missing"])))
    if lint.get("edge"):
        lines.append(f"OUT OF SAFE AREA (text crosses the {SAFE}px screen margin; also check it fits its card):")
        for l, r, s in sorted(lint["edge"])[:30]:
            lines.append(f"   x {l}..{r}  {s!r}")
    if lint["small"]:
        lines.append(f"SMALL TEXT (< {MIN_TEXT}px, unreadable in the phone feed; enlarge or pass small=True):")
        for size, s in sorted(lint["small"])[:30]:
            lines.append(f"   {size:3d}px  {s!r}")
    return "\n".join(lines) if lines else "lint: OK (no small text, no missing glyphs, all text inside the safe area)"


def warn(msg):
    print(f"[warn] {msg}", file=sys.stderr)
