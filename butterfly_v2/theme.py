"""Three visual themes: paper, white, dark. Plus fonts and small drawing helpers."""
import os

import numpy as np
import skia

W, H, FPS = 1080, 1920, 60
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_FONTS = os.path.join(os.path.dirname(HERE), 'fonts')
CJK = '/usr/share/fonts/google-noto-cjk/'

_tf = {}


def _typeface(kind, weight):
    key = (kind, weight)
    if key in _tf:
        return _tf[key]
    tf = None
    if kind == 'serif':
        p = f'{CJK}NotoSerifCJK-{weight}.ttc'
        if os.path.exists(p):
            tf = skia.Typeface.MakeFromFile(p, 2)          # index 2 = Simplified Chinese
    elif kind == 'sans':
        p = f'{CJK}NotoSansSC-{weight}.otf'
        if os.path.exists(p):
            tf = skia.Typeface.MakeFromFile(p)
    elif kind == 'mono':
        tf = skia.Typeface.MakeFromFile(os.path.join(REPO_FONTS, 'JetBrainsMono-Regular.ttf'))
    if tf is None:  # fall back to the Noto Sans SC shipped in the repo
        tf = skia.Typeface.MakeFromFile(os.path.join(REPO_FONTS, 'NotoSansSC-Regular.otf'))
    _tf[key] = tf
    return tf


def font(kind, weight, size):
    f = skia.Font(_typeface(kind, weight), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def col(rgb, a=255):
    return skia.ColorSetARGB(int(max(0, min(255, a))), *rgb)


def paint(rgb, a=255, stroke=None, blur=None, blend=None):
    p = skia.Paint(AntiAlias=True, Color=col(rgb, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend is not None:
        p.setBlendMode(blend)
    return p


def clamp01(x):
    return max(0.0, min(1.0, x))


def smooth(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    """Quintic-ish, slower at both ends than smoothstep - feels more 'camera'."""
    x = clamp01(x)
    return x * x * x * (x * (6 * x - 15) + 10)


def lerp(a, b, t):
    return a + (b - a) * t


class Theme:
    def __init__(self, name, label, bg, ink, soft, hair, a, b, pocket, surface, title_font, body_font,
                 glow=False, texture=None, vignette=0.0):
        self.name, self.label = name, label
        self.bg, self.ink, self.soft, self.hair = bg, ink, soft, hair
        self.a, self.b, self.pocket, self.surface = a, b, pocket, surface
        self.title_font, self.body_font = title_font, body_font   # (kind, weight)
        self.glow = glow
        self.vignette = vignette
        self._bg_img = self._make_background(texture)

    # ------------------------------------------------------------ background
    def _make_background(self, texture):
        rng = np.random.default_rng(1)
        img = np.ones((H, W, 3)) * np.array(self.bg, dtype=float)
        if texture == 'paper':
            # fine grain + soft mottling + faint fibres
            grain = rng.normal(0, 1, (H, W))
            low = rng.normal(0, 1, (H // 24 + 2, W // 24 + 2))
            low = np.kron(low, np.ones((24, 24)))[:H, :W]
            from scipy.ndimage import gaussian_filter
            low = gaussian_filter(low, 18)
            shade = 1 + 0.018 * grain + 0.05 * low / (np.abs(low).max() + 1e-9)
            fib = np.zeros((H, W))
            for _ in range(900):
                x, y = rng.integers(0, W), rng.integers(0, H)
                ln, ang = rng.integers(8, 40), rng.uniform(0, np.pi)
                for s in range(ln):
                    xx, yy = int(x + s * np.cos(ang)), int(y + s * np.sin(ang))
                    if 0 <= xx < W and 0 <= yy < H:
                        fib[yy, xx] += 1
            fib = gaussian_filter(fib, 0.6)
            shade -= 0.05 * fib
            img *= shade[..., None]
        elif texture == 'dark':
            yy, xx = np.mgrid[0:H, 0:W]
            r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
            img += (np.array([22, 26, 36]) * np.clip(1 - r * 1.6, 0, 1)[..., None])
            img += rng.normal(0, 1.2, (H, W))[..., None]           # dither against banding
        if self.vignette:
            yy, xx = np.mgrid[0:H, 0:W]
            r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
            img *= (1 - self.vignette * np.clip(r - 0.55, 0, 1) ** 1.6)[..., None]
        rgba = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
        return skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType)

    def draw_background(self, c):
        c.drawImage(self._bg_img, 0, 0)

    # ------------------------------------------------------------ text
    def text(self, c, s, x, y, size, rgb=None, role='body', alpha=255, align='center', spacing=0.0):
        kind, weight = self.title_font if role == 'title' else (('mono', 'Regular') if role == 'mono'
                                                                 else self.body_font)
        f = font(kind, weight, size)
        rgb = self.ink if rgb is None else rgb
        widths = [f.measureText(ch) for ch in s]
        total = sum(widths) + spacing * size * (len(s) - 1)
        x0 = x - total / 2 if align == 'center' else (x - total if align == 'right' else x)
        p = paint(rgb, alpha)
        for ch, w in zip(s, widths):
            c.drawString(ch, x0, y + size * 0.36, f, p)
            x0 += w + spacing * size
        return total


THEMES = {
    'paper': Theme('paper', '纸张', bg=(241, 235, 222), ink=(46, 42, 37), soft=(128, 118, 104), hair=(46, 42, 37),
                   a=(184, 62, 42), b=(40, 72, 122), pocket=(46, 42, 37), surface=None,
                   title_font=('serif', 'Light'), body_font=('serif', 'Regular'), texture='paper', vignette=0.25),
    'white': Theme('white', '纯白', bg=(255, 255, 255), ink=(29, 29, 31), soft=(134, 134, 139), hair=(29, 29, 31),
                   a=(235, 77, 61), b=(0, 113, 227), pocket=(29, 29, 31), surface=(245, 245, 247),
                   title_font=('sans', 'Thin'), body_font=('sans', 'Light')),
    'dark': Theme('dark', '深色', bg=(10, 12, 17), ink=(238, 238, 242), soft=(128, 134, 148), hair=(238, 238, 242),
                  a=(255, 112, 92), b=(86, 170, 255), pocket=(0, 0, 0), surface=None,
                  title_font=('sans', 'Thin'), body_font=('sans', 'Light'), glow=True, texture='dark', vignette=0.35),
}
