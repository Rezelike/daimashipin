"""Shared pieces for the scenes after the opening, matched to the opening's look.

Same caption, HUD and legend positions / sizes as opening.py, so the film reads as one piece.

Scenes draw their pictures in portrait design coordinates (1080 x 1920). In the wide (16:9)
format, `visual()` scales the picture into the middle of the frame, and captions, the
subtitle line, the HUD and the legend move to the wide layout below.
"""
import numpy as np
import skia

from theme import W, H, FORMAT, paint, smooth, ease_out, font

SAMPLING = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


class Layout:
    def __init__(self, wide):
        self.wide = wide
        if wide:
            # captions on top, picture in the middle (y ~200-945), one data row kept clear of the bottom edge
            self.cx = 960
            self.cap_y = {0: 92, 1: 160, 'title': 108}
            self.cap_k = 0.9
            self.sub_y, self.sub_k = 975, 0.94
            self.hud_y, self.hud_lx, self.hud_vx, self.hud_rx = 1030, 150, 235, 1770
            self.legend_cx, self.legend_y = 960, 1030
            self.vis = (960.0, 570.0)
        else:
            self.cx = 540
            self.cap_y = {0: 185, 1: 275, 'title': 200}
            self.cap_k = 1.0
            self.sub_y, self.sub_k = None, 1.0              # portrait: each scene gives its own y
            self.hud_y, self.hud_lx, self.hud_vx, self.hud_rx = 1765, 90, 175, 990
            self.legend_cx, self.legend_y = 540, 1835
            self.vis = None


LY = Layout(FORMAT == 'wide')


class visual:
    """with visual(c, focus, scale): draw the picture in portrait design coordinates.

    Portrait: nothing changes. Wide: the design point `focus` lands at the centre of the
    picture area, scaled by `scale`.
    """

    def __init__(self, c, focus, scale):
        self.c, self.focus, self.scale = c, focus, scale

    def __enter__(self):
        self.c.save()
        if LY.wide:
            self.c.translate(*LY.vis)
            self.c.scale(self.scale, self.scale)
            self.c.translate(-self.focus[0], -self.focus[1])
        return self.c

    def __exit__(self, *exc):
        self.c.restore()
        return False


def caption(c, th, s, t, t0, t1, line=0, size=56, rgb=None, role='title', spacing=0.18):
    """Fade + slight rise in, fade out over the last 0.6 s (identical to Opening.caption)."""
    a = 255 * min(smooth((t - t0) / 0.6), 1 - smooth((t - (t1 - 0.6)) / 0.6))
    if a > 0:
        y = LY.cap_y[line]
        th.text(c, s, LY.cx, y + 10 * (1 - ease_out((t - t0) / 0.9)), size * LY.cap_k,
                th.ink if rgb is None else rgb, role=role, alpha=a, spacing=spacing)


def sub(c, th, s, alpha, portrait_y, size=32, spacing=0.3):
    """The small grey explanatory line under the picture."""
    if alpha > 0:
        y = LY.sub_y if LY.wide else portrait_y
        th.text(c, s, LY.cx, y, size * LY.sub_k, th.soft, alpha=alpha, spacing=spacing)


def _is_mono(ch):
    return ord(ch) < 128 or ch == '°'


def value(c, th, s, x, y, size, alpha, align='left'):
    """HUD value: digits in the mono font, any Chinese unit in the body font."""
    if all(_is_mono(ch) for ch in s):
        th.text(c, s, x, y, size, th.ink, role='mono', alpha=alpha, align=align)
        return
    runs, cur = [], ''
    for ch in s:
        if cur and _is_mono(ch) != _is_mono(cur[-1]):
            runs.append(cur)
            cur = ''
        cur += ch
    runs.append(cur)
    fonts = [font('mono', 'Regular', size) if _is_mono(r[0]) else font(*th.body_font, size * 0.88) for r in runs]
    widths = [f.measureText(r) for f, r in zip(fonts, runs)]
    total = sum(widths)
    x0 = x - total if align == 'right' else (x - total / 2 if align == 'center' else x)
    p = paint(th.ink, alpha)
    for r, f, w in zip(runs, fonts, widths):
        c.drawString(r, x0, y + size * 0.36, f, p)
        x0 += w


def hud(c, th, a, left_label, left_value, right_label, right_value):
    if a <= 0:
        return
    y = LY.hud_y
    if left_label:
        th.text(c, left_label, LY.hud_lx, y, 30, th.soft, alpha=a, align='left', spacing=0.15)
        # the opening puts the value 85 px after a two-character label; keep the same gap for longer labels
        value(c, th, left_value, LY.hud_vx + 30 * 1.15 * (len(left_label) - 2), y, 34, a)
    if right_label:
        value(c, th, right_value, LY.hud_rx, y, 34, a, align='right')
        th.text(c, right_label, LY.hud_rx - 240, y, 30, th.soft, alpha=a, align='right', spacing=0.15)


def legend(c, th, a, first='第一次', second='第二次'):
    if a <= 0:
        return
    ly = LY.legend_y
    if (first, second) == ('第一次', '第二次'):          # exactly where the opening puts it
        dx = LY.legend_cx - 540
        x_dot, x1, x_ring, x2 = 398 + dx, 420 + dx, 588 + dx, 610 + dx
    else:
        f = font(*th.body_font, 28)
        w = [sum(f.measureText(ch) for ch in s) + 0.15 * 28 * (len(s) - 1) for s in (first, second)]
        x0 = LY.legend_cx - (130 + w[0] + w[1]) / 2
        x_dot, x1 = x0 + 10, x0 + 32
        x_ring = x1 + w[0] + 76
        x2 = x_ring + 22
    c.drawCircle(x_dot, ly, 10, paint(th.a, a))
    th.text(c, first, x1, ly, 28, th.soft, alpha=a, align='left', spacing=0.15)
    c.drawCircle(x_ring, ly, 11, paint(th.b, a, stroke=2.2))
    th.text(c, second, x2, ly, 28, th.soft, alpha=a, align='left', spacing=0.15)


def dip(c, th, u, length, fade_in=0.5, fade_out=0.6):
    """Every scene comes up from, and goes back to, plain paper - the way the opening ends."""
    a = max(1 - smooth(u / fade_in), smooth((u - (length - fade_out)) / fade_out))
    if a > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(th.bg, 255 * a))


def fmt_cm(x):
    return f'{x:6.2f} cm' if x < 100 else f'{x:6.1f} cm'


# ---------------------------------------------------------------- soft ink blobs (smoke, clouds)
_sprites = {}


def blob(rgb, size=128):
    """A soft round ink blot, drawn many times with drawImageRect - much faster than blurred circles."""
    if rgb not in _sprites:
        yy, xx = np.mgrid[0:size, 0:size]
        r = np.hypot(xx - size / 2 + 0.5, yy - size / 2 + 0.5) / (size / 2)
        a = np.clip(1 - r * r, 0, 1) ** 2
        rgba = np.zeros((size, size, 4), np.uint8)
        rgba[..., :3] = rgb
        rgba[..., 3] = (a * 255).astype(np.uint8)
        img = skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
        _sprites[rgb] = img.withDefaultMipmaps()
    return _sprites[rgb]


def draw_blobs(c, img, xs, ys, rs, alphas, blend=skia.BlendMode.kMultiply):
    p = skia.Paint(AntiAlias=True)
    if blend is not None:
        p.setBlendMode(blend)
    b = c.getLocalClipBounds()                    # visible area in the current (local) coordinates
    x0, y0, x1, y1 = b.left(), b.top(), b.right(), b.bottom()
    for x, y, r, a in zip(xs, ys, rs, alphas):
        if a < 0.004 or r < 0.3 or x + r < x0 or x - r > x1 or y + r < y0 or y - r > y1:
            continue
        p.setAlphaf(float(min(a, 1.0)))
        c.drawImageRect(img, skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), SAMPLING, p)
