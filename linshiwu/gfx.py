"""Drawing primitives + flat-style illustrations (skia).

Every illustration is drawn around the origin (roughly within +-250 units),
so callers place it with canvas.translate / canvas.scale.
"""
import math
import numpy as np
import skia

W, H = 1080, 1920

# ---------- palette ----------
BG = (244, 239, 230)
INK = (43, 43, 43)
GREY = (150, 145, 138)
LIGHT = (222, 215, 203)
CARD = (255, 253, 249)
PAPER = (250, 248, 242)
ORANGE = (232, 131, 58)
TEAL = (78, 156, 150)
MUSTARD = (226, 179, 60)
CORAL = (227, 110, 91)
BLUE = (86, 119, 184)
WOOD = (201, 139, 90)
WOOD_D = (168, 110, 66)
RED = (200, 58, 48)
GREEN = (84, 150, 88)
CARDBOARD = (212, 166, 106)
TAPE = (238, 222, 178)

LW = 7  # outline width in illustration units

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def prog(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)

def ease_out(x):
    x = clamp(x); return 1 - (1 - x) ** 3

def ease_in_out(x):
    x = clamp(x); return 3 * x * x - 2 * x * x * x

def back_out(x):
    x = clamp(x); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def lerp(a, b, x):
    return a + (b - a) * x

# ---------- paints ----------
def col(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(clamp(a, 0, 255)))

def fillp(rgb, a=255):
    return skia.Paint(Color=col(rgb, a), AntiAlias=True)

def strokep(rgb, w, a=255, dash=None):
    p = skia.Paint(Color=col(rgb, a), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                   StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap,
                   StrokeJoin=skia.Paint.kRound_Join)
    if dash:
        p.setPathEffect(skia.DashPathEffect.Make(dash, 0))
    return p

# ---------- paths ----------
def rrect(x, y, w, h, r):
    p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return p

def poly(pts, close=True):
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p

def circle(x, y, r):
    p = skia.Path(); p.addCircle(x, y, r); return p

def shape(c, path, fill, lw=LW, outline=INK):
    if fill is not None:
        c.drawPath(path, fillp(fill))
    if lw:
        c.drawPath(path, strokep(outline, lw))

def line(c, x1, y1, x2, y2, rgb=INK, w=LW, a=255, dash=None):
    c.drawLine(x1, y1, x2, y2, strokep(rgb, w, a, dash))

# ---------- layers / transforms ----------
class layer:
    """with layer(c, alpha, x, y, s, rot): draw at transformed position with opacity."""
    def __init__(self, c, alpha=1.0, x=0, y=0, s=1.0, rot=0.0):
        self.c, self.a, self.x, self.y, self.s, self.r = c, alpha, x, y, s, rot
    def __enter__(self):
        c = self.c; c.save()
        c.translate(self.x, self.y)
        if self.r: c.rotate(self.r)
        if self.s != 1: c.scale(self.s, self.s)
        self.layered = self.a < 0.999
        if self.layered:
            c.saveLayerAlpha(None, int(clamp(self.a) * 255))
        return c
    def __exit__(self, *a):
        if self.layered: self.c.restore()
        self.c.restore()

# ---------- text ----------
import os
# Noto Sans/Serif CJK .ttc files (Fedora/Amazon Linux, Debian/Ubuntu, Homebrew, or ./fonts)
_FONT_DIRS = [os.environ.get("CJK_FONT_DIR", ""), os.path.join(os.path.dirname(__file__), "fonts"),
              "/usr/share/fonts/google-noto-cjk/", "/usr/share/fonts/opentype/noto/",
              "/usr/share/fonts/noto-cjk/", os.path.expanduser("~/Library/Fonts/")]
_FD = next((d.rstrip("/") + "/" for d in _FONT_DIRS
            if d and os.path.exists(os.path.join(d, "NotoSerifCJK-Bold.ttc"))), _FONT_DIRS[2])
_TF = {}
_FONTS = {}
FACES = {
    "sans": "NotoSansCJK-Regular.ttc", "sans_m": "NotoSansCJK-Medium.ttc",
    "sans_b": "NotoSansCJK-Bold.ttc", "sans_k": "NotoSansCJK-Black.ttc",
    "serif": "NotoSerifCJK-Regular.ttc", "serif_b": "NotoSerifCJK-Bold.ttc",
    "serif_k": "NotoSerifCJK-Black.ttc",
}

def font(face, size, skew=0.0):
    k = (face, size, skew)
    if k not in _FONTS:
        if face not in _TF:
            _TF[face] = skia.Typeface.MakeFromFile(_FD + FACES[face], 2)  # index 2 = SC
        f = skia.Font(_TF[face], size)
        f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
        if skew: f.setSkewX(skew)
        _FONTS[k] = f
    return _FONTS[k]

def text_w(s, size, face="sans_b"):
    return font(face, size).measureText(s)

def text(c, s, x, y, size, rgb=INK, face="sans_b", align="center", a=255, skew=0.0, spacing=0):
    """y is the visual middle of the text line."""
    f = font(face, size, skew)
    base = y + size * 0.36
    if not spacing:
        w = f.measureText(s)
        x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
        c.drawString(s, x0, base, f, fillp(rgb, a))
        return w
    ws = [f.measureText(ch) for ch in s]
    w = sum(ws) + spacing * (len(s) - 1)
    x0 = x - w / 2 if align == "center" else x - w if align == "right" else x
    for ch, cw in zip(s, ws):
        c.drawString(ch, x0, base, f, fillp(rgb, a)); x0 += cw + spacing
    return w

def wrap(s, size, maxw, face="sans_b"):
    """Greedy wrap for CJK; prefers breaking after punctuation."""
    f = font(face, size)
    if f.measureText(s) <= maxw:
        return [s]
    lines, cur = [], ""
    for ch in s:
        if f.measureText(cur + ch) > maxw:
            # back off to the last punctuation in cur if it's reasonably far in
            cut = max(cur.rfind(p) for p in "，。、：；？！」")
            if cut >= len(cur) * 0.5:
                lines.append(cur[:cut + 1]); cur = cur[cut + 1:] + ch
            else:
                lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        if cur in "，。？！」" and lines:
            lines[-1] += cur
        else:
            lines.append(cur)
    return lines

def pill(c, s, x, y, size, bg, fg=(255, 255, 255), face="sans_b", pad=0.7, a=255):
    w = text_w(s, size, face) + size * pad * 2
    h = size * 1.75
    c.drawPath(rrect(x - w / 2, y - h / 2, w, h, h / 2), fillp(bg, a))
    text(c, s, x, y, size, fg, face, a=a)
    return w

# ---------- background ----------
def make_background():
    rng = np.random.default_rng(7)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    vign = 1 - 0.18 * np.clip(d * 1.6, 0, 1) ** 2
    noise = rng.normal(0, 4.0, (H, W))
    img = np.zeros((H, W, 4), np.uint8)
    for i in range(3):
        img[..., i] = np.clip(BG[i] * vign + noise, 0, 255)
    img[..., 3] = 255
    return skia.Image.fromarray(img, colorType=skia.kRGBA_8888_ColorType)

# =====================================================================
# Illustrations
# =====================================================================
def shirt(c, color):
    p = poly([(-60, -70), (-24, -82), (-12, -66), (12, -66), (24, -82), (60, -70), (98, -34),
              (72, -6), (56, -22), (56, 82), (-56, 82), (-56, -22), (-72, -6), (-98, -34)])
    shape(c, p, color)
    c.drawPath(poly([(-24, -82), (0, -58), (24, -82)], close=False), strokep(INK, 5))

def sock(c, color):
    p = skia.Path(); p.moveTo(-22, -70); p.lineTo(22, -70); p.lineTo(22, 20)
    p.quadTo(22, 50, 55, 52); p.quadTo(70, 70, 50, 82); p.lineTo(-5, 82)
    p.quadTo(-22, 82, -22, 60); p.close()
    shape(c, p, color)
    line(c, -22, -50, 22, -50, INK, 5)

def chair(c, clothes=True):
    # back legs
    for x in (-100, 100):
        shape(c, rrect(x - 11, -10, 22, 200, 8), WOOD_D)
    # backrest posts + rails
    for x in (-112, 112):
        shape(c, rrect(x - 13, -258, 26, 250, 10), WOOD)
    shape(c, rrect(-125, -272, 250, 50, 18), WOOD)
    shape(c, rrect(-105, -168, 210, 26, 10), WOOD)
    # seat
    shape(c, rrect(-150, -32, 300, 46, 14), WOOD)
    # front legs
    for x in (-130, 130):
        shape(c, rrect(x - 13, 10, 26, 205, 9), WOOD)
    if not clothes:
        return
    # shirt draped over backrest
    p = skia.Path(); p.moveTo(-95, -290); p.quadTo(-10, -305, 70, -288)
    p.lineTo(85, -150); p.quadTo(60, -120, 35, -150); p.lineTo(20, -230)
    p.quadTo(-30, -220, -60, -232); p.lineTo(-75, -120); p.quadTo(-100, -100, -112, -130); p.close()
    shape(c, p, TEAL)
    # pile on seat
    with layer(c, rot=-4):
        shape(c, rrect(-150, -84, 200, 58, 26), MUSTARD)
    with layer(c, x=40, y=-100, rot=7):
        shape(c, rrect(-90, -30, 180, 56, 26), CORAL)
    with layer(c, x=-40, y=-140, rot=-9):
        shape(c, rrect(-80, -26, 160, 48, 22), BLUE)
    with layer(c, x=10, y=-178, rot=4):
        shape(c, rrect(-55, -20, 110, 40, 18), PAPER)
    # sleeve hanging off the front
    p = skia.Path(); p.moveTo(95, -60); p.quadTo(150, -40, 150, 40)
    p.lineTo(118, 48); p.quadTo(115, -10, 70, -30); p.close()
    shape(c, p, CORAL)
    # sock dangling
    with layer(c, x=-120, y=40, s=0.55, rot=8):
        sock(c, BLUE)

INNER = [CORAL, TEAL, MUSTARD, BLUE, PAPER, ORANGE]

def bag(c, fill=PAPER, inner=2, bulge=0.0):
    """Plastic bag. inner = how many bags peek out of the top; bulge 0..1 = how stuffed."""
    b = 25 * bulge
    # handles
    for sx in (-1, 1):
        p = skia.Path(); p.moveTo(sx * 95, -60); p.cubicTo(sx * 105, -170, sx * 35, -170, sx * 40, -60)
        c.drawPath(p, strokep(INK, 22)); c.drawPath(p, strokep(fill, 10))
    # inner bags peeking out
    rng = np.random.default_rng(3)
    for i in range(inner):
        ang = (i - (inner - 1) / 2) * (110 / max(inner, 1))
        r = 34 + 4 * (i % 3)
        x = math.sin(math.radians(ang)) * 70; y = -78 - 14 * math.cos(math.radians(ang)) - rng.uniform(0, 12)
        p = skia.Path(); n = 9
        for k in range(n):
            a = 2 * math.pi * k / n; rr = r * (0.82 + 0.3 * ((k * 7 + i) % 3) / 2)
            pt = (x + math.cos(a) * rr, y + math.sin(a) * rr * 0.8)
            p.moveTo(*pt) if k == 0 else p.lineTo(*pt)
        p.close()
        shape(c, p, INNER[i % len(INNER)], 5)
    # body
    p = skia.Path(); p.moveTo(-112, -62); p.lineTo(112, -62)
    p.quadTo(140 + b, 40, 132 + b, 150); p.quadTo(0, 168 + b * 0.5, -132 - b, 150)
    p.quadTo(-140 - b, 40, -112, -62); p.close()
    shape(c, p, fill)
    for (x1, y1, x2, y2) in [(-60, -20, -40, 30), (30, 10, 70, 40), (-20, 80, 20, 100), (60, 90, 80, 120)]:
        line(c, x1, y1, x2, y2, GREY, 4)

def remote(c, tape=True):
    shape(c, rrect(-72, -205, 144, 410, 46), (68, 73, 84))
    shape(c, circle(0, -150, 19), RED, 5)
    shape(c, circle(0, -70, 42), (110, 116, 128), 5)
    shape(c, circle(0, -70, 15), (68, 73, 84), 4)
    for r in range(3):
        for k in range(3):
            shape(c, circle(-40 + 40 * k, 20 + 40 * r, 12), (190, 194, 200), 4)
    # crack
    c.drawPath(poly([(-72, 80), (-30, 100), (-45, 120), (10, 140), (0, 160), (72, 170)], close=False),
               strokep((230, 230, 230), 4))
    if tape:
        for (y, rot) in [(95, -12), (150, 9)]:
            with layer(c, y=y, rot=rot):
                p = rrect(-112, -24, 224, 48, 4)
                c.drawPath(p, fillp(TAPE, 225)); c.drawPath(p, strokep(INK, 5))
                for k in range(-100, 101, 50):
                    line(c, k, -24, k + 10, 24, (215, 196, 150), 3)

WEDGE_POS = (185, 140)  # where the paper wedge sits, in table coordinates

def wedge(c, dx=0.0):
    p = poly([(160, 128), (210, 128), (205, 135), (212, 142), (204, 152), (158, 152), (163, 144), (157, 136)])
    with layer(c, x=dx):
        shape(c, p, PAPER, 4)

def table(c, wedge_dx=0.0, floor=True, tilt=0.0):
    """Table with a short right leg. wedge_dx=None -> no wedge. tilt (deg) rotates
    the table around the bottom of its left leg (the wobble)."""
    if floor:
        line(c, -330, 152, 330, 152, GREY, 5)
    c.save(); c.translate(-185, 152); c.rotate(tilt); c.translate(185, -152)
    shape(c, rrect(-200, -86, 30, 238, 8), WOOD_D)    # left leg (reaches floor)
    shape(c, rrect(170, -86, 30, 214, 8), WOOD_D)     # right leg (too short)
    shape(c, rrect(-215, -92, 430, 32, 8), WOOD)       # apron
    shape(c, rrect(-245, -128, 490, 40, 10), WOOD)     # top
    c.restore()
    if wedge_dx is not None:
        wedge(c, wedge_dx)

def box(c, label=True):
    shape(c, poly([(-160, -80), (-205, -150), (-40, -150), (0, -80)]), (190, 145, 90))
    shape(c, poly([(160, -80), (205, -150), (40, -150), (0, -80)]), (225, 182, 125))
    shape(c, rrect(-160, -82, 320, 225, 8), CARDBOARD)
    c.drawPath(rrect(-26, -82, 52, 225, 0), fillp(TAPE, 200))
    line(c, -26, -82, -26, 143, INK, 3); line(c, 26, -82, 26, 143, INK, 3)
    if label:
        with layer(c, x=95, y=60, rot=-6):
            shape(c, rrect(-55, -30, 110, 60, 4), PAPER, 4)
            text(c, "先放着", 0, 0, 28, INK, "sans_b")

def folder(c):
    shape(c, poly([(-150, -110), (-60, -110), (-38, -86), (150, -86), (150, 110), (-150, 110)]), (222, 165, 50))
    shape(c, rrect(-160, -55, 320, 170, 16), (245, 197, 82))
    text(c, "(3)", 0, 30, 54, (140, 95, 20), "sans_k")

def notice(c, date=True):
    shape(c, rrect(-170, -230, 340, 460, 6), (243, 231, 196), 6)
    text(c, "临时通知", 0, -158, 50, INK, "sans_k")
    line(c, -120, -110, 120, -110, INK, 4)
    for i, w in enumerate([240, 220, 240, 180, 230, 140]):
        c.drawPath(rrect(-120, -75 + i * 38, w, 12, 6), fillp(GREY, 160))
    if date:
        text(c, "2019.03.02", 120, 180, 26, GREY, "sans_m", align="right")
    for (x, r) in [(-150, -35), (150, 35)]:
        with layer(c, x=x, y=-225, rot=r):
            c.drawPath(rrect(-45, -16, 90, 32, 2), fillp(TAPE, 220))

def stamp(c, s, rgb=RED, size=64):
    w = text_w(s, size, "sans_k") + size * 0.8
    h = size * 1.6
    c.drawPath(rrect(-w / 2, -h / 2, w, h, 14), strokep(rgb, 8))
    c.drawPath(rrect(-w / 2 + 10, -h / 2 + 10, w - 20, h - 20, 8), strokep(rgb, 3))
    text(c, s, 0, 0, size, rgb, "sans_k", spacing=size * 0.1)

def lamp(c):
    shape(c, rrect(-110, 150, 220, 36, 18), (70, 75, 84))
    c.drawPath(poly([(-40, 155), (40, -40), (-60, -170)], close=False), strokep(INK, 20))
    c.drawPath(poly([(-40, 155), (40, -40), (-60, -170)], close=False), strokep((120, 126, 138), 10))
    shape(c, circle(40, -40, 16), (120, 126, 138), 5)
    with layer(c, x=-60, y=-170, rot=-28):
        shape(c, poly([(-60, -50), (60, -50), (110, 60), (-110, 60)]), TEAL)
        c.drawPath(circle(0, 75, 26), fillp((255, 226, 140)))
        c.drawPath(circle(0, 75, 26), strokep(INK, 5))

def wardrobe(c):
    shape(c, rrect(-105, -170, 210, 330, 10), WOOD)
    line(c, 0, -160, 0, 150, INK, 5)
    shape(c, circle(-16, 0, 8), MUSTARD, 4); shape(c, circle(16, 0, 8), MUSTARD, 4)
    for x in (-85, 85):
        shape(c, rrect(x - 10, 158, 20, 22, 4), WOOD_D, 5)

def basket(c):
    shape(c, poly([(-110, -70), (110, -70), (85, 110), (-85, 110)]), (214, 190, 140))
    for y in (-30, 10, 50, 85):
        line(c, -100 + (y + 70) * 0.13, y, 100 - (y + 70) * 0.13, y, (160, 135, 90), 4)
    shape(c, rrect(-122, -88, 244, 30, 12), (190, 164, 112))
    # a shirt corner sticking out
    with layer(c, x=40, y=-100, s=0.45, rot=20):
        shirt(c, MUSTARD)

def check_badge(c, s, rgb=GREEN, size=40):
    w = text_w(s, size) + size * 2.6
    h = size * 1.9
    c.drawPath(rrect(-w / 2, -h / 2, w, h, h / 2), fillp(rgb))
    x0 = -w / 2 + size * 1.0
    c.drawPath(poly([(x0 - 14, 0), (x0 - 2, 13), (x0 + 18, -14)], close=False), strokep((255, 255, 255), 8))
    text(c, s, x0 + size * 0.75, 0, size, (255, 255, 255), "sans_b", align="left")

def arrow(c, x1, y1, x2, y2, rgb=INK, w=6, head=22, a=255, bend=0.0):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    cx, cy = mx - dy * bend, my + dx * bend
    p = skia.Path(); p.moveTo(x1, y1); p.quadTo(cx, cy, x2, y2)
    c.drawPath(p, strokep(rgb, w, a))
    ang = math.atan2(y2 - cy, x2 - cx)
    for s in (-1, 1):
        a2 = ang + math.pi + s * 0.5
        c.drawLine(x2, y2, x2 + math.cos(a2) * head, y2 + math.sin(a2) * head, strokep(rgb, w, a))
