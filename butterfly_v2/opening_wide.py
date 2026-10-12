"""The 12.4 s opening laid out for 16:9.

Same simulation, timeline, colours and sound as opening.py. The only change is the framing:
the table lies on its side (the break travels to the right), and the captions, HUD, the
"x 10 000" label and 0.001° move to the wide layout. Everything inside the table is drawn
by the unchanged Opening methods, through one rotation.
"""
import math

import skia

import film_common as fc
from opening import Opening, CX, CY, R, ZOOM, T_BALLS, T_ZOOM, T_SPREAD, T_NUMBER, END
from theme import W, H, FPS, paint, smooth, ease_out, ease_in_out, lerp

S_W = 0.95                      # table size on screen (outer frame ~1350 x 710 px)
CENTER = fc.LY.vis              # table centre on screen
BALL_AT = (470.0, 470.0)        # where the cue ball sits on screen after the push-in
NUMBER_AT = (960, 795)


def to_screen(x, y):
    """Portrait design point -> wide screen (rotated 90° clockwise: 'up' becomes 'right')."""
    return CENTER[0] - S_W * (y - CY), CENTER[1] + S_W * (x - CX)


def to_design(X, Y):
    return CX + (Y - CENTER[1]) / S_W, CY - (X - CENTER[0]) / S_W


ZOOM_TO_W = to_design(*BALL_AT)


class OpeningWide(Opening):
    def camera(self, t):
        k = ease_in_out((t - T_ZOOM[0]) / (T_ZOOM[1] - T_ZOOM[0]))
        scale = lerp(1.0, ZOOM, k)
        fx, fy = self.cue0
        tx, ty = lerp(fx, ZOOM_TO_W[0], k), lerp(fy, ZOOM_TO_W[1], k)
        return scale, (fx, fy), (tx, ty), k

    @staticmethod
    def rotate_into_frame(c):
        c.translate(*CENTER)
        c.rotate(90)
        c.scale(S_W, S_W)
        c.translate(-CX, -CY)

    # ------------------------------------------------------------ aim lines (in design space) + labels (on screen)
    @staticmethod
    def aim_state(t):
        k = smooth((t - (T_ZOOM[0] + 0.5)) / 0.6)
        spread = math.radians(10) * ease_in_out((t - T_SPREAD[0]) / (T_SPREAD[1] - T_SPREAD[0]))
        return k, spread

    def draw_aim_lines(self, c, th, t):
        k, spread = self.aim_state(t)
        if k <= 0:
            return
        x, y = ZOOM_TO_W
        length = 900 * ease_out((t - (T_ZOOM[0] + 0.5)) / 1.0)
        start = R * ZOOM + 16
        for rgb, ang in ((th.b, -spread / 2), (th.a, spread / 2)):
            dx, dy = math.sin(ang), -math.cos(ang)
            p = paint(rgb, 255 * k, stroke=2.4 / S_W)
            c.drawLine(x + dx * start, y + dy * start, x + dx * (start + length), y + dy * (start + length), p)
        if spread > 0.01:
            a = 255 * smooth((t - (T_SPREAD[0] + 0.3)) / 0.5)
            rad = 520
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeLTRB(x - rad, y - rad, x + rad, y + rad),
                       -90 - math.degrees(spread / 2), math.degrees(spread))
            c.drawPath(arc, paint(th.soft, a, stroke=1.2 / S_W))

    def draw_aim_label(self, c, th, t):
        k, spread = self.aim_state(t)
        if k <= 0 or spread <= 0.01:
            return
        a = 255 * smooth((t - (T_SPREAD[0] + 0.3)) / 0.5)
        rad = 520 * S_W
        # just below the lower (red) line, where it crosses the arc
        ex = BALL_AT[0] + rad * math.cos(spread / 2)
        ey = BALL_AT[1] + rad * math.sin(spread / 2)
        th.text(c, '角度放大一万倍后', ex - 6, ey + 58, 30, th.soft, alpha=a, align='left', spacing=0.2)
        th.text(c, '× 10 000', ex - 6, ey + 104, 30, th.soft, role='mono', alpha=a, align='left')

    def draw_number(self, c, th, t):
        a = 255 * smooth((t - T_NUMBER) / 0.9)
        if a <= 0:
            return
        th.text(c, '0.001°', NUMBER_AT[0], NUMBER_AT[1], 170, th.ink, role='title', alpha=a, spacing=0.02)
        a2 = 255 * smooth((t - (T_NUMBER + 0.8)) / 0.8)
        th.text(c, '两次出杆，全部的差别', NUMBER_AT[0], NUMBER_AT[1] + 140, 38, th.soft, alpha=a2, spacing=0.35)

    # ------------------------------------------------------------ hud + captions
    def draw_hud(self, c, th, t, f, alpha):
        a = alpha * smooth((t - 1.3) / 0.5) * (1 - smooth((t - T_ZOOM[0]) / 0.4))
        if a <= 0:
            return
        gap = self.max_gap_cm(f)
        fc.hud(c, th, a, '时间', f'{f / FPS:5.2f} s', '最大偏差', fc.fmt_cm(gap))
        fc.legend(c, th, a)

    def caption(self, c, th, s, t, t0, t1, y=185, size=56):
        fc.caption(c, th, s, t, t0, t1, line=0, size=size)

    # ------------------------------------------------------------ frame
    def draw(self, c, th, t):
        th.draw_background(c)
        f = self.sim_frame(t)
        scale, focus, target, zk = self.camera(t)
        c.save()
        self.rotate_into_frame(c)
        c.save()
        c.translate(target[0], target[1])
        c.scale(scale, scale)
        c.translate(-focus[0], -focus[1])
        table_a = 255 * (1 - smooth((zk - 0.15) / 0.5))
        self.draw_table(c, th, t, table_a)
        self.draw_trails(c, th, f, 255)
        self.draw_connectors(c, th, f, 255 * (1 - smooth(zk / 0.3)))
        appear = ease_out((t - T_BALLS) / 0.6)
        if appear > 0:
            self.draw_balls(c, th, f, 255, appear)
        self.draw_cue(c, th, t, 255)
        c.restore()
        self.draw_aim_lines(c, th, t)
        c.restore()
        self.draw_hud(c, th, t, f, 255)
        self.caption(c, th, '同一杆，打两次', t, 0.6, 4.6)
        self.caption(c, th, '结果，完全不同', t, 5.0, 7.9)
        self.draw_aim_label(c, th, t)
        self.draw_number(c, th, t)
        out = smooth((t - (END - 0.6)) / 0.6)
        if out > 0:
            c.drawRect(skia.Rect.MakeWH(W, H), paint(th.bg, 255 * out))
