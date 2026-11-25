"""Pixel-art canvas helpers: 360x640 art pixels, shown 3x (1080x1920). No anti-aliasing anywhere.

Text uses Fusion Pixel 12px (SIL OFL 1.1, assets/fonts/), drawn at its native 12 px and scaled by whole numbers,
so every glyph stays on the pixel grid: 1x = 36 px and 2x = 72 px in the final video.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, SCALE = 360, 640, 3
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "assets", "fonts", "fusion-pixel-12px-proportional-zh_hans.otf")
FONT = ImageFont.truetype(FONT_PATH, 12)
MARGIN = 6                       # text must stay this many art pixels inside the frame

# palette -------------------------------------------------------------------------------------------------------
INK = (18, 14, 30)
NIGHT = (24, 18, 46)
DEEP = (34, 24, 62)
PURPLE = (62, 36, 98)
WHITE = (244, 240, 250)
GREY = (150, 146, 170)
DIMTXT = (120, 112, 150)
YELLOW = (255, 214, 64)
ORANGE = (255, 150, 52)
RED = (232, 64, 52)
CYAN = (110, 220, 255)
GREEN = (96, 226, 120)
BLUE = (70, 150, 255)
SKY = [(30, 20, 58), (44, 26, 80), (70, 34, 104), (112, 44, 120), (160, 56, 124), (206, 76, 118),
       (238, 108, 104), (250, 148, 92), (255, 186, 98)]

TANK = dict(d=(40, 50, 30), m=(66, 82, 44), l=(96, 114, 60), h=(134, 152, 86))
ALU = dict(d=(104, 96, 104), m=(170, 160, 150), l=(214, 204, 190), h=(240, 232, 218))
HEAD = dict(d=(128, 34, 40), m=(204, 66, 52), l=(240, 110, 78), h=(255, 160, 110))
PISTON = dict(d=(82, 90, 118), m=(140, 150, 178), l=(196, 204, 226))
ROD = dict(d=(170, 120, 36), m=(240, 188, 64), l=(255, 230, 130))
STEEL = dict(d=(58, 54, 78), m=(108, 104, 132), l=(160, 156, 184))
AIR = [(90, 170, 255), (140, 210, 255)]
HOT = [(255, 120, 60), (255, 170, 80)]
FIRE = [(255, 250, 200), (255, 222, 90), (255, 150, 40), (232, 70, 30), (150, 40, 40)]
SMOKE = [(116, 106, 136), (88, 80, 108), (140, 132, 156)]
WATER = [(40, 110, 230), (70, 150, 255), (130, 196, 255)]

LINT = dict(missing=set(), edge=[], small=0)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def shade(c, k):
    """k < 0 darker, k > 0 lighter (towards white)"""
    return mix(c, (0, 0, 0), -k) if k < 0 else mix(c, (255, 255, 255), k)


class Canvas:
    def __init__(self, bg=NIGHT, size=(W, H), mode="RGB", img=None):
        if img is not None:
            self.img = img
        else:
            self.img = Image.new(mode, size, bg if bg is not None else (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.w, self.h = self.img.size

    # ---- shapes (all aliased) ---------------------------------------------------------------------------------
    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        x0, x1 = sorted((int(round(x0)), int(round(x1))))
        y0, y1 = sorted((int(round(y0)), int(round(y1))))
        self.d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

    def poly(self, pts, fill=None, outline=None, width=1):
        pts = [(int(round(x)), int(round(y))) for x, y in pts]
        if len(pts) >= 3:
            self.d.polygon(pts, fill=fill, outline=outline, width=width)

    def line(self, pts, fill, width=1):
        pts = [(int(round(x)), int(round(y))) for x, y in pts]
        self.d.line(pts, fill=fill, width=width)

    def thick(self, a, b, w, fill, outline=None):
        """a bar of width w (pixels) from a to b, as a polygon"""
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        n = max(1e-6, (dx * dx + dy * dy) ** 0.5)
        nx, ny = -dy / n * w / 2, dx / n * w / 2
        self.poly([(ax + nx, ay + ny), (bx + nx, by + ny), (bx - nx, by - ny), (ax - nx, ay - ny)], fill, outline)

    def circle(self, cx, cy, r, fill=None, outline=None, width=1):
        r = max(0.5, r)
        self.d.ellipse([int(round(cx - r)), int(round(cy - r)), int(round(cx + r)), int(round(cy + r))],
                       fill=fill, outline=outline, width=width)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=None, width=1):
        self.d.ellipse([int(round(cx - rx)), int(round(cy - ry)), int(round(cx + rx)), int(round(cy + ry))],
                       fill=fill, outline=outline, width=width)

    def px(self, x, y, c):
        self.d.point((int(round(x)), int(round(y))), fill=c)

    def dots(self, pts, c):
        if pts:
            self.d.point([(int(round(x)), int(round(y))) for x, y in pts], fill=c)

    # ---- text -------------------------------------------------------------------------------------------------
    def text(self, s, x, y, color=WHITE, scale=1, align="l", outline=INK, lint=True):
        """y = top of the 16 px line box (x scale). Returns (x0, y0, x1, y1)."""
        m = text_mask(s, scale)
        w, h = m.size
        x0 = int(round(x - (w / 2 if align == "c" else (w if align == "r" else 0))))
        y0 = int(round(y))
        if outline is not None:
            self.img.paste(outline, (x0, y0), _outline(s, scale))
        self.img.paste(color, (x0, y0), m)
        if lint:
            _lint(s, x0, y0, x0 + w, y0 + h, self.w, self.h)
        return x0, y0, x0 + w, y0 + h

    def blit(self, other, x=0, y=0):
        self.img.paste(other.img if isinstance(other, Canvas) else other, (int(x), int(y)))


_MASKS, _OUTS = {}, {}


def text_w(s, scale=1):
    return text_mask(s, scale).size[0]


def text_mask(s, scale=1):
    key = (s, scale)
    if key not in _MASKS:
        w = int(np.ceil(FONT.getlength(s))) + 2
        im = Image.new("L", (max(1, w), 16), 0)
        d = ImageDraw.Draw(im)
        d.fontmode = "1"
        d.text((1, 0), s, font=FONT, fill=255, anchor="la")
        a = np.array(im) > 127
        cols = np.nonzero(a.any(0))[0]
        if len(cols):
            a = a[:, max(0, cols[0] - 1): cols[-1] + 2]
        if scale > 1:
            a = np.repeat(np.repeat(a, scale, 0), scale, 1)
        _MASKS[key] = Image.fromarray((a * 255).astype(np.uint8), "L")
    return _MASKS[key]


def _outline(s, scale):
    key = (s, scale)
    if key not in _OUTS:
        a = np.array(text_mask(s, scale)) > 0
        k = max(1, scale)
        p = np.pad(a, k)
        o = np.zeros_like(p)
        for dy in range(-k, k + 1):
            for dx in range(-k, k + 1):
                o |= np.roll(np.roll(p, dy, 0), dx, 1)
        o = o[k:-k, k:-k]
        _OUTS[key] = Image.fromarray((o * 255).astype(np.uint8), "L")
    return _OUTS[key]


def _lint(s, x0, y0, x1, y1, w, h):
    cmap = _cmap()
    for ch in s:
        if ch != " " and ord(ch) not in cmap:
            LINT["missing"].add(ch)
    if x0 < MARGIN or y0 < MARGIN - 4 or x1 > w - MARGIN or y1 > h - MARGIN:
        LINT["edge"].append((s, x0, y0, x1, y1))


_CMAP = None


def _cmap():
    global _CMAP
    if _CMAP is None:
        try:
            from fontTools.ttLib import TTFont
            _CMAP = set(TTFont(FONT_PATH).getBestCmap())
        except Exception:                       # fontTools missing: skip the glyph check
            _CMAP = set(range(0x110000))
    return _CMAP


def upscale(img):
    a = np.asarray(img)
    return np.repeat(np.repeat(a, SCALE, 0), SCALE, 1)


def average(images):
    acc = np.zeros(np.asarray(images[0]).shape, np.float32)
    for im in images:
        acc += np.asarray(im, np.float32)
    return Image.fromarray(np.clip(acc / len(images) + 0.5, 0, 255).astype(np.uint8))
