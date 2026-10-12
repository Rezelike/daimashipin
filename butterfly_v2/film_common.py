"""Shared pieces for the scenes after the opening, matched to the opening's look.

Same caption, HUD and legend positions / sizes as opening.py, so the film reads as one piece.
"""
import skia

from theme import W, H, paint, smooth, ease_out


def caption(c, th, s, t, t0, t1, y=185, size=56, rgb=None, role='title', spacing=0.18):
    """Fade + slight rise in, fade out over the last 0.6 s (identical to Opening.caption)."""
    a = 255 * min(smooth((t - t0) / 0.6), 1 - smooth((t - (t1 - 0.6)) / 0.6))
    if a > 0:
        th.text(c, s, 540, y + 10 * (1 - ease_out((t - t0) / 0.9)), size, th.ink if rgb is None else rgb,
                role=role, alpha=a, spacing=spacing)


def hud(c, th, a, left_label, left_value, right_label, right_value):
    if a <= 0:
        return
    y = 1765
    th.text(c, left_label, 90, y, 30, th.soft, alpha=a, align='left', spacing=0.15)
    th.text(c, left_value, 175, y, 34, th.ink, role='mono', alpha=a, align='left')
    th.text(c, right_value, 990, y, 34, th.ink, role='mono', alpha=a, align='right')
    th.text(c, right_label, 990 - 240, y, 30, th.soft, alpha=a, align='right', spacing=0.15)


def legend(c, th, a, first='第一次', second='第二次'):
    if a <= 0:
        return
    ly = 1835
    c.drawCircle(398, ly, 10, paint(th.a, a))
    th.text(c, first, 420, ly, 28, th.soft, alpha=a, align='left', spacing=0.15)
    c.drawCircle(588, ly, 11, paint(th.b, a, stroke=2.2))
    th.text(c, second, 610, ly, 28, th.soft, alpha=a, align='left', spacing=0.15)


def dip(c, th, u, length, fade_in=0.5, fade_out=0.6):
    """Every scene comes up from, and goes back to, plain paper - the way the opening ends."""
    a = max(1 - smooth(u / fade_in), smooth((u - (length - fade_out)) / fade_out))
    if a > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), paint(th.bg, 255 * a))


def fmt_cm(x):
    return f'{x:6.2f} cm' if x < 100 else f'{x:6.1f} cm'
