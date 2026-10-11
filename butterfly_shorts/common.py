"""Shared drawing helpers: palette, fonts, easing, captions."""
import skia

W, H = 1080, 1920
FPS = 60

# ---- bright palette -------------------------------------------------------
BG = (251, 247, 240)
BG_DOT = (238, 230, 218)
INK = (47, 53, 66)
INK_SOFT = (120, 126, 140)
CORAL = (255, 107, 107)
SKY = (77, 171, 247)
FELT = (76, 195, 138)
FELT_DARK = (56, 160, 110)
RAIL = (232, 168, 108)
RAIL_DARK = (196, 128, 74)
POCKET = (60, 64, 72)
WHITE = (255, 255, 255)

import os

SYSTEM_FONT_DIR = '/usr/share/fonts/google-noto-cjk/'
REPO_FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
# Repo only ships Regular + Bold; heavier/lighter weights fall back to the closest one.
REPO_FALLBACK = {'Black': 'Bold', 'Bold': 'Bold', 'Medium': 'Regular', 'Regular': 'Regular'}
_tf_cache = {}


def typeface(weight='Bold'):
    if weight not in _tf_cache:
        path = os.path.join(SYSTEM_FONT_DIR, f'NotoSansSC-{weight}.otf')
        if not os.path.exists(path):
            path = os.path.join(REPO_FONT_DIR, f'NotoSansSC-{REPO_FALLBACK[weight]}.otf')
        _tf_cache[weight] = skia.Typeface.MakeFromFile(path)
    return _tf_cache[weight]


def font(size, weight='Bold'):
    f = skia.Font(typeface(weight), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def col(rgb, a=255):
    return skia.ColorSetARGB(int(max(0, min(255, a))), *rgb)


def paint(rgb, a=255, stroke=None, cap=None, blur=None):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(cap or skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


# ---- easing ---------------------------------------------------------------
def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out_cubic(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x, s=1.7):
    x = clamp01(x)
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def lerp(a, b, t):
    return a + (b - a) * t


# ---- background -----------------------------------------------------------
def draw_background(c):
    c.clear(col(BG))
    p = paint(BG_DOT)
    for y in range(30, H, 60):
        for x in range(30, W, 60):
            c.drawCircle(x, y, 3, p)


# ---- captions -------------------------------------------------------------
class Caption:
    """A line of (optionally multi-coloured) text that pops in and fades out.

    segments: str or list of (text, rgb)
    """

    def __init__(self, segments, t_in, t_out, y, size=72, color=INK, weight='Bold',
                 pop=True, fade=0.25):
        if isinstance(segments, str):
            segments = [(segments, color)]
        self.segments = segments
        self.t_in, self.t_out, self.y, self.size = t_in, t_out, y, size
        self.weight, self.pop, self.fade = weight, pop, fade

    def draw(self, c, t):
        if t < self.t_in or t > self.t_out:
            return
        a_in = clamp01((t - self.t_in) / 0.22)
        a_out = clamp01((self.t_out - t) / self.fade)
        alpha = min(a_in, a_out)
        scale = ease_out_back((t - self.t_in) / 0.35) * 0.25 + 0.75 if self.pop else 1.0
        rise = (1 - ease_out_cubic((t - self.t_in) / 0.35)) * 24
        f = font(self.size, self.weight)
        widths = [f.measureText(s) for s, _ in self.segments]
        total = sum(widths)
        c.save()
        c.translate(W / 2, self.y + rise)
        c.scale(scale, scale)
        x = -total / 2
        base = self.size * 0.36
        for (s, rgb), w in zip(self.segments, widths):
            c.drawString(s, x, base, f, paint(rgb, 255 * alpha))
            x += w
        c.restore()


def draw_captions(c, caps, t):
    for cap in caps:
        cap.draw(c, t)
