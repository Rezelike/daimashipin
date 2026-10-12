"""Shared pieces for the scenes after the opening, matched to the opening's look.

Same caption, HUD and legend positions / sizes as opening.py, so the film reads as one piece.
"""
import numpy as np
import skia

from theme import W, H, paint, smooth, ease_out, font

SAMPLING = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def caption(c, th, s, t, t0, t1, y=185, size=56, rgb=None, role='title', spacing=0.18):
    """Fade + slight rise in, fade out over the last 0.6 s (identical to Opening.caption)."""
    a = 255 * min(smooth((t - t0) / 0.6), 1 - smooth((t - (t1 - 0.6)) / 0.6))
    if a > 0:
        th.text(c, s, 540, y + 10 * (1 - ease_out((t - t0) / 0.9)), size, th.ink if rgb is None else rgb,
                role=role, alpha=a, spacing=spacing)


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
    y = 1765
    if left_label:
        th.text(c, left_label, 90, y, 30, th.soft, alpha=a, align='left', spacing=0.15)
        # the opening puts the value at x=175 after a two-character label; keep the same gap for longer labels
        value(c, th, left_value, 175 + 30 * 1.15 * (len(left_label) - 2), y, 34, a)
    if right_label:
        value(c, th, right_value, 990, y, 34, a, align='right')
        th.text(c, right_label, 990 - 240, y, 30, th.soft, alpha=a, align='right', spacing=0.15)


def legend(c, th, a, first='第一次', second='第二次'):
    if a <= 0:
        return
    ly = 1835
    if (first, second) == ('第一次', '第二次'):          # exactly where the opening puts it
        x_dot, x1, x_ring, x2 = 398, 420, 588, 610
    else:
        f = font(*th.body_font, 28)
        w = [sum(f.measureText(ch) for ch in s) + 0.15 * 28 * (len(s) - 1) for s in (first, second)]
        x0 = 540 - (130 + w[0] + w[1]) / 2
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
    for x, y, r, a in zip(xs, ys, rs, alphas):
        if a < 0.004 or r < 0.3 or x + r < 0 or x - r > W or y + r < 0 or y - r > H:
            continue
        p.setAlphaf(float(min(a, 1.0)))
        c.drawImageRect(img, skia.Rect.MakeLTRB(x - r, y - r, x + r, y + r), SAMPLING, p)
