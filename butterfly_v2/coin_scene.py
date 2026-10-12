"""24.4-30.4 s: a coin in slow motion, drawn like a copperplate engraving, freezing on heads.

The numbers are real for a simple toss: 0.5 s in the air at 38 turns per second is exactly
19 turns, so it comes down heads. At 39 turns per second it would make 19.5 turns - tails.
"""
import math

import numpy as np
import skia

import film_common as fc
from theme import W, H, paint, font, clamp01, smooth, ease_out, ease_in_out, lerp

LEN = 6.0
SPIN = (38, 39)                 # turns per second: the one we see, and the one we only mention
FLIGHT = 0.5                    # seconds in the air
TAU = (0.40, FLIGHT)            # the slice of the flight shown in slow motion
U_PLAY = (0.25, 4.1)            # playback slows down to a freeze over this range
U_CAP1, U_CAP2 = 0.6, 2.4
U_NOTE = 4.35                   # the 38 / 39 note appears

CX, CY = 540, 930
R = 250
THICK = 26                      # rim thickness seen edge-on
WIDE_VIEW = ((540, 1035), 0.88)  # 16:9: design point at the picture centre, and scale
COPPER = (150, 96, 58)
COPPER_DARK = (96, 58, 36)


def tau_at(u):
    """Real time inside the toss shown at scene time u (slows smoothly to a stop)."""
    k = clamp01((u - U_PLAY[0]) / (U_PLAY[1] - U_PLAY[0]))
    k = 1 - (1 - k) ** 2.4
    return lerp(TAU[0], TAU[1], k)


def turns(u):
    return SPIN[0] * tau_at(u)


def mix(rgb1, rgb2, k):
    return tuple(int(round(a + (b - a) * k)) for a, b in zip(rgb1, rgb2))


class CoinScene:
    LEN = LEN

    def __init__(self):
        self._face = {}

    # ------------------------------------------------------------ the engraved faces (drawn flat, R = 1 unit)
    def draw_face(self, c, th, heads, light):
        """Engraving in a unit-radius frame centred at 0. light: -1..1, where the glint band sits."""
        base = mix(th.bg, COPPER, 0.16)
        c.drawCircle(0, 0, R, paint(base))
        clip = skia.Path()
        clip.addCircle(0, 0, R - 2)
        c.save()
        c.clipPath(clip, doAntiAlias=True)
        # hatching: parallel lines, heavier on the lower right (shadow), thin where the light catches
        n = 64
        for i in range(n + 1):
            y = -R + 2 * R * i / n
            half = math.sqrt(max(0.0, R * R - y * y))
            if half < 2:
                continue
            for x0 in np.linspace(-half, half, 9)[:-1]:
                x1 = x0 + 2 * half / 8
                xm = (x0 + x1) / 2
                shade = 0.5 + 0.5 * (0.6 * y / R + 0.4 * xm / R)
                glint = math.exp(-((y / R - light) / 0.22) ** 2)
                w = 0.35 + 1.5 * shade * (1 - 0.85 * glint)
                c.drawLine(x0, y, x1, y, paint(COPPER_DARK, 150 * (1 - 0.7 * glint), stroke=w))
        c.restore()
        # rims and milled edge
        c.drawCircle(0, 0, R, paint(th.ink, 235, stroke=3.0))
        c.drawCircle(0, 0, R * 0.9, paint(th.ink, 200, stroke=1.4))
        c.drawCircle(0, 0, R * 0.865, paint(th.ink, 140, stroke=0.9))
        for j in range(120):
            a = 2 * math.pi * j / 120
            ca, sa = math.cos(a), math.sin(a)
            c.drawLine(R * 0.905 * ca, R * 0.905 * sa, R * 0.985 * ca, R * 0.985 * sa, paint(th.ink, 150, stroke=1.1))
        if heads:
            # a large engraved "壹", with a ring of dots like the table diamonds
            f = font(*th.title_font, R * 0.95)
            wdt = f.measureText('壹')
            c.drawString('壹', -wdt / 2, R * 0.33, f, paint(th.ink, 225))
            for j in range(12):
                a = 2 * math.pi * j / 12 - math.pi / 2
                c.drawCircle(R * 0.77 * math.cos(a), R * 0.77 * math.sin(a), 3.2, paint(th.ink, 190))
        else:
            # tails: an engraved rosette
            for j in range(8):
                a = 2 * math.pi * j / 8
                petal = skia.Path()
                petal.moveTo(0, 0)
                ca, sa = math.cos(a), math.sin(a)
                cb, sb = math.cos(a + 0.42), math.sin(a + 0.42)
                cd, sd = math.cos(a - 0.42), math.sin(a - 0.42)
                petal.cubicTo(R * 0.45 * cb, R * 0.45 * sb, R * 0.62 * ca, R * 0.62 * sa, R * 0.66 * ca, R * 0.66 * sa)
                petal.cubicTo(R * 0.62 * ca, R * 0.62 * sa, R * 0.45 * cd, R * 0.45 * sd, 0, 0)
                c.drawPath(petal, paint(th.ink, 210, stroke=1.6))
            c.drawCircle(0, 0, R * 0.12, paint(th.ink, 210, stroke=1.6))
            c.drawCircle(0, 0, R * 0.7, paint(th.ink, 120, stroke=1.0))

    # ------------------------------------------------------------ the coin in 3D (spinning about the horizontal axis)
    def draw_coin(self, c, th, x, y, ang, alpha):
        cy_ = math.cos(ang)
        sy_ = math.sin(ang)
        heads = cy_ >= 0
        h = max(abs(cy_), 0.012)
        off = THICK * sy_ * (1 if heads else -1)
        c.saveLayerAlpha(None, int(alpha))
        # rim band: between the visible face and the hidden one
        rim = skia.Path()
        rim.addOval(skia.Rect.MakeLTRB(x - R, y - R * h, x + R, y + R * h))
        rim.addOval(skia.Rect.MakeLTRB(x - R, y + off - R * h, x + R, y + off + R * h))
        rim.addRect(skia.Rect.MakeLTRB(x - R, min(y, y + off), x + R, max(y, y + off)))
        c.drawPath(rim, paint(mix(th.bg, COPPER, 0.35)))
        c.save()
        c.clipPath(rim, doAntiAlias=True)
        for j in range(-60, 61):                        # reeding on the edge
            xx = x + R * math.sin(j / 60 * math.pi / 2)
            c.drawLine(xx, y - R * h - abs(off), xx, y + R * h + abs(off), paint(COPPER_DARK, 120, stroke=1.0))
        c.restore()
        c.drawPath(rim, paint(th.ink, 220, stroke=2.0))
        # the face we can see
        c.save()
        c.translate(x, y)
        c.scale(1, h)
        if not heads:
            c.scale(1, -1)                              # the back face is seen upside down
        light = math.sin(ang * 1.0 + 0.6) * 0.9
        self.draw_face(c, th, heads, light)
        c.restore()
        c.restore()

    def draw_shadow(self, c, th, x, y_coin, alpha):
        lift = (1300 - y_coin) / 500
        r = R * (1.05 + 0.25 * lift)
        img = fc.blob(th.ink)
        p = skia.Paint(AntiAlias=True)
        p.setAlphaf(float(alpha / 255 * 0.10 / (1 + 0.6 * lift)))
        p.setBlendMode(skia.BlendMode.kMultiply)
        c.drawImageRect(img, skia.Rect.MakeLTRB(x - r, 1395 - r * 0.16, x + r, 1395 + r * 0.16), fc.SAMPLING, p)

    def draw_note(self, c, th, u):
        a = 255 * smooth((u - U_NOTE) / 0.6)
        if a <= 0:
            return
        if fc.LY.wide:                                  # to the right of the coin
            (y1, y2), x, x_face = (410, 474), 1270, 1725
        else:                                           # under the coin
            (y1, y2), x, x_face = (1505, 1570), 300, 780
        for k, (y, spin, face) in enumerate(((y1, SPIN[0], '正面'), (y2, SPIN[1], '反面'))):
            ak = a * smooth((u - U_NOTE - 0.45 * k) / 0.6)
            if ak <= 0:
                continue
            if k == 0:
                c.drawCircle(x, y, 10, paint(th.a, ak))
            else:
                c.drawCircle(x, y, 11, paint(th.b, ak, stroke=2.2))
            th.text(c, f'每秒 {spin} 圈，翻 {spin * FLIGHT:g} 圈', x + 28, y, 32, th.soft, alpha=ak, align='left',
                    spacing=0.12)
            th.text(c, face, x_face, y, 34, th.a if k == 0 else th.b, alpha=ak, align='left', spacing=0.2)

    # ------------------------------------------------------------ frame
    def draw(self, c, th, u):
        th.draw_background(c)
        n = turns(u)
        ang = 2 * math.pi * n
        k = clamp01((u - U_PLAY[0]) / (U_PLAY[1] - U_PLAY[0]))
        y = CY - 50 * math.sin(math.pi * (0.35 + 0.65 * (1 - (1 - k) ** 2.4)))      # near the top of the arc
        appear = ease_out((u - 0.05) / 0.6)
        z = lerp(0.94, 1.0, ease_out(u / 2.0)) * lerp(1.0, 1.035, ease_in_out((u - U_PLAY[1]) / 1.6))
        with fc.visual(c, *WIDE_VIEW):
            c.save()
            c.translate(CX, CY)
            c.scale(z, z)
            c.translate(-CX, -CY)
            self.draw_shadow(c, th, CX, y, 255 * appear)
            self.draw_coin(c, th, CX, y, ang, 255 * appear)
            c.restore()
        # slow motion marker, then the freeze
        a_slow = 255 * smooth((u - 0.5) / 0.5) * (1 - smooth((u - (U_PLAY[1] - 0.4)) / 0.4))
        fc.sub(c, th, '慢动作', a_slow, 1440, size=30, spacing=0.5)
        fc.caption(c, th, '你以为的随机，', u, U_CAP1, LEN + 1, line=0)
        fc.caption(c, th, '只是算不清。', u, U_CAP2, LEN + 1, line=1)
        a_hud = 255 * smooth((u - 0.6) / 0.5)
        fc.hud(c, th, a_hud, '时间', f'{tau_at(u):5.3f} s', '已翻', f'{n:5.2f} 圈')
        self.draw_note(c, th, u)
        fc.dip(c, th, u, LEN)


if __name__ == '__main__':
    for u in (0, 1, 2, 3, 4, 4.1, 5):
        print(f'u={u}: tau={tau_at(u):.3f}s turns={turns(u):.3f}')
