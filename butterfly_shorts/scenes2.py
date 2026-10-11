"""Part 2 scenes (26-86 s): why it grows, coin, smoke & weather, contrast, butterfly, ending."""
import math

import numpy as np
import skia

import bumper
import scenes as s1
from common import *  # noqa: F403

# ================================================================ timeline
E_START, E_END = 26.0, 38.6        # why: bounces amplify the gap
F_START, F_END = 38.4, 49.6        # coin flip
G_START, G_END = 49.4, 60.6        # smoke -> weather forecast
H_START, H_END = 60.4, 70.6        # not everything is chaotic
I_START, I_END = 70.4, 79.6        # the butterfly
J_START, J_END = 79.4, 86.0        # ending
VIDEO_END = J_END


def pill_c(c, cx, y, text, rgb, size=40, fg=WHITE, alpha=255):
    f = font(size, 'Bold')
    w = f.measureText(text)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - w / 2 - 20, y - size * 0.8, w + 40, size * 1.5), 28, 28)
    c.drawRRect(rr, paint(rgb, alpha))
    c.drawString(text, cx - w / 2, y + size * 0.3, f, paint(fg, alpha))


def text_c(c, cx, y, text, size, rgb, weight='Bold', alpha=255):
    f = font(size, weight)
    c.drawString(text, cx - f.measureText(text) / 2, y + size * 0.36, f, paint(rgb, alpha))


def fade_in(t, t0, d=0.3):
    return clamp01((t - t0) / d)


def card(c, x, y, w, h, alpha=255, r=36):
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    c.drawRRect(rr.makeOffset(0, 10) if hasattr(rr, 'makeOffset') else rr, paint((0, 0, 0), alpha * 0.10, blur=16))
    c.drawRRect(rr, paint(WHITE, alpha))


PEG_COLORS = [(255, 196, 36), (58, 120, 232), (240, 72, 62), (146, 92, 206), (255, 140, 46),
              (36, 168, 96), (176, 62, 70), (46, 48, 56)]


def draw_arena(c, ox, oy, w, h, pegs, peg_r, alpha=255):
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(ox - 22, oy - 22, w + 44, h + 44), 34, 34)
    c.drawRRect(rr, paint(RAIL, alpha))
    c.drawRect(skia.Rect.MakeXYWH(ox, oy, w, h), paint(FELT, alpha))
    for k, (x, y) in enumerate(pegs):
        X, Y = ox + x, oy + y
        c.drawCircle(X + 5, Y + 8, peg_r, paint((0, 0, 0), alpha * 0.18, blur=6))
        c.drawCircle(X, Y, peg_r, paint(PEG_COLORS[k % len(PEG_COLORS)], alpha))
        c.drawCircle(X - peg_r * 0.35, Y - peg_r * 0.38, peg_r * 0.26, paint(WHITE, alpha * 0.7))


def draw_runner(c, ox, oy, pos, f, rgb, r, alpha, trail=70):
    f = min(f, len(pos) - 1)
    start = max(0, f - trail)
    if f > start:
        step = 6
        for j0 in range(start, f, step):
            j1 = min(j0 + step, f)
            path = skia.Path()
            path.moveTo(ox + pos[j0, 0], oy + pos[j0, 1])
            for j in range(j0 + 1, j1 + 1):
                path.lineTo(ox + pos[j, 0], oy + pos[j, 1])
            p = paint(rgb, alpha * 0.75 * (1 - (f - j1) / trail), stroke=r * 0.9)
            p.setStrokeCap(skia.Paint.kButt_Cap)
            c.drawPath(path, p)
    x, y = ox + pos[f, 0], oy + pos[f, 1]
    c.drawCircle(x + 2, y + 4, r, paint((0, 0, 0), alpha * 0.25, blur=3))
    c.drawCircle(x, y, r, paint(rgb, alpha))
    c.drawCircle(x, y, r, paint(WHITE, alpha, stroke=3))


# ================================================================ E: why it grows
E_LAUNCH = 28.0
E_PEGS = [(170, 330), (450, 250), (730, 330), (310, 560), (590, 560), (170, 790), (450, 870), (730, 790)]
E_BOX = (0, 0, 900, 1080)
E_ORIGIN = (90, 370)
E_PEG_R, E_BALL_R = 62, 18


def fmt_mm(g):
    if g >= 100:
        return f'{g / 10:.0f} 厘米'
    if g >= 10:
        return f'{g:.0f} 毫米'
    if g >= 1:
        return f'{g:.1f} 毫米'
    if g >= 0.01:
        return f'{g:.2f} 毫米'
    return f'{g:.4f} 毫米'


class SceneE:
    def __init__(self):
        dur = E_END - E_LAUNCH + 0.3
        args = ((450, 1040), E_PEGS, E_PEG_R, E_BALL_R, E_BOX, dur, FPS)
        self.pa, self.ba = bumper.simulate(args[0], -101, 330, *args[1:])
        self.pb, self.bb = bumper.simulate(args[0], -101 + s1.ANGLE_DIFF, 330, *args[1:])
        self.gap = np.linalg.norm(self.pa - self.pb, axis=1)
        self.report = bumper.gap_report(self.pa, self.pb, self.ba, FPS, max_gap=200)
        self.peg_hits = [(E_LAUNCH + t, i) for (t, k, i) in self.ba if k == 'peg']
        self.wall_hits = [E_LAUNCH + t for (t, k, i) in self.ba if k == 'wall']
        # moment the two balls visibly separate
        k = int(np.argmax(self.gap > 2 * E_BALL_R))
        self.t_apart = E_LAUNCH + k / FPS
        self.caps = [
            Caption('为什么会这样？', 26.15, 28.0, 210, size=84),
            Caption([('秘密就在「', INK), ('圆', CORAL), ('」上', INK)], 28.1, 30.6, 210, size=80),
            Caption('每撞一次，差距就放大好几倍', 30.7, 34.3, 210, size=64),
            Caption([('撞几次，就', INK), ('彻底分开', CORAL), ('了', INK)], 34.4, E_END, 210, size=78),
        ]

    def frame(self, t):
        return int(np.clip(round((t - E_LAUNCH) * FPS), 0, len(self.pa) - 1))

    def draw(self, c, t):
        ox, oy = E_ORIGIN
        a = 255 * ease_out_cubic((t - E_START) / 0.5)
        draw_arena(c, ox, oy, E_BOX[2], E_BOX[3], E_PEGS, E_PEG_R, a)
        f = self.frame(t)
        # "×N" bubbles at each peg bounce
        for (tb, g, fac) in self.report:
            tb += E_LAUNCH
            if fac is None or t < tb or t > tb + 1.6:
                continue
            idx = next(i for (th, i) in self.peg_hits if abs(th - tb) < 1e-6)
            px, py = ox + E_PEGS[idx][0], oy + E_PEGS[idx][1]
            k = (t - tb) / 1.6
            al = 255 * min(1, (1 - k) * 3)
            sc = ease_out_back(min(1, (t - tb) / 0.3))
            c.save()
            c.translate(px, py - E_PEG_R - 40 - 30 * k)
            c.scale(sc, sc)
            pill_c(c, 0, 0, f'×{fac:.0f}', CORAL, size=52, alpha=al)
            c.restore()
        if t >= E_LAUNCH - 0.6:
            al = 255 * fade_in(t, E_LAUNCH - 0.6)
            draw_runner(c, ox, oy, self.pb, f if t >= E_LAUNCH else 0, SKY, E_BALL_R, al)
            draw_runner(c, ox, oy, self.pa, f if t >= E_LAUNCH else 0, CORAL, E_BALL_R, al * 0.85)
        # live gap counter
        if t >= E_LAUNCH - 0.3:
            al = 255 * fade_in(t, E_LAUNCH - 0.3)
            g = float(self.gap[f]) if t >= E_LAUNCH else 0.0
            card(c, 170, 1530, 740, 150, al)
            text_c(c, 540, 1575, '两个球相差', 40, INK_SOFT, 'Medium', al)
            text_c(c, 540, 1638, fmt_mm(g) if g < 2000 else '很远', 64,
                   CORAL if g > 2 * E_BALL_R else INK, 'Black', al)
        draw_captions(c, self.caps, t)


# ================================================================ F: coin flip
F_FLICK = 40.6
F_SLOW = 7.2                       # slow motion factor
F_T = 0.5                          # real flight time (s)
F_LAND = F_FLICK + F_T * F_SLOW    # 44.2
F_SPIN = (2 * math.pi * 38, 2 * math.pi * 39)   # rev/s -> 19 vs 19.5 turns
COIN_X = (300, 780)
PAD_Y = 1380
COIN_R = 120
RISE = 640                         # pixels for the 0.31 m rise
GOLD, GOLD_DARK, GOLD_EDGE = (255, 200, 72), (232, 160, 40), (196, 128, 30)
SILVER, SILVER_DARK = (205, 214, 226), (150, 162, 180)


def draw_coin(c, x, y, ang, r=COIN_R, alpha=255, face_scale=None):
    """Side view of a coin flipping about the horizontal axis. ang=0 -> heads up (seen flat)."""
    sy = math.cos(ang) if face_scale is None else face_scale
    h = max(abs(sy), 0.06) * r
    heads = math.cos(ang) >= 0
    body, dark, mark = (GOLD, GOLD_DARK, '正') if heads else (SILVER, SILVER_DARK, '反')
    edge = skia.Rect.MakeLTRB(x - r, y - h + 9, x + r, y + h + 9)
    c.drawOval(edge, paint(GOLD_EDGE if heads else SILVER_DARK, alpha))
    rect = skia.Rect.MakeLTRB(x - r, y - h, x + r, y + h)
    c.drawOval(rect, paint(body, alpha))
    inner = skia.Rect.MakeLTRB(x - r * 0.8, y - h * 0.8, x + r * 0.8, y + h * 0.8)
    c.drawOval(inner, paint(dark, alpha, stroke=5))
    if abs(sy) > 0.2:
        c.save()
        c.translate(x, y)
        c.scale(1, abs(sy))
        f = font(r * 0.95, 'Black')
        c.drawString(mark, -f.measureText(mark) / 2, r * 0.33, f, paint(dark, alpha))
        c.restore()


def draw_pad(c, x, y, alpha=255):
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 150, y + 14, 300, 70), 35, 35)
    c.drawRRect(rr.makeOffset(0, 8) if hasattr(rr, 'makeOffset') else rr, paint((0, 0, 0), alpha * 0.12, blur=10))
    c.drawRRect(rr, paint((255, 214, 186), alpha))
    c.drawRRect(rr, paint((236, 176, 140), alpha, stroke=4))


class SceneF:
    def __init__(self):
        self.caps = [
            Caption('再来抛两次硬币', 38.6, F_FLICK + 0.1, 210, size=82),
            Caption('同样的手法，同样的高度', F_FLICK + 0.2, F_LAND, 210, size=68),
            Caption([('一个', INK), ('正面', GOLD_EDGE), ('，一个', INK), ('反面', SILVER_DARK)],
                    F_LAND + 0.4, 46.9, 210, size=80),
            Caption('硬币不是"随机"的', 47.0, F_END, 210, size=82),
            Caption('只是转速差了约 3%，结果就反了', 47.5, F_END, 330, size=50, color=INK_SOFT,
                    weight='Medium'),
        ]

    def coin_state(self, k, t):
        """(y, angle, landed) for coin k at video time t."""
        if t < F_FLICK:
            return PAD_Y, 0.0, False
        tr = min((t - F_FLICK) / F_SLOW, F_T)
        g = 2 * RISE / (F_T / 2) ** 2 / 2       # so that peak = RISE at T/2
        v0 = g * F_T / 2
        y = PAD_Y - (v0 * tr - 0.5 * g * tr * tr)
        return y, F_SPIN[k] * tr, tr >= F_T

    def draw(self, c, t):
        a = 255 * ease_out_cubic((t - F_START) / 0.4)
        for k, x in enumerate(COIN_X):
            draw_pad(c, x, PAD_Y + 20, a)
        reveal = ease_out_back((t - F_LAND - 0.15) / 0.5)
        for k, x in enumerate(COIN_X):
            y, ang, landed = self.coin_state(k, t)
            if t < F_FLICK:
                draw_coin(c, x, y, 0.0, alpha=a, face_scale=0.18)
            elif not landed:
                draw_coin(c, x, y, ang, alpha=a)
            else:
                # lands flat, then flips up towards the camera to reveal its face
                fs = lerp(0.18, 1.0, clamp01(reveal))
                yy = lerp(PAD_Y, 900, ease_out_cubic((t - F_LAND - 0.15) / 0.5))
                draw_coin(c, x, yy, ang, r=COIN_R * lerp(1, 1.25, clamp01(reveal)), alpha=a,
                          face_scale=fs * (1 if math.cos(ang) >= 0 else -1))
                if t > F_LAND + 0.5:
                    al = 255 * fade_in(t, F_LAND + 0.5)
                    heads = math.cos(ang) >= 0
                    pill_c(c, x, 1150, '正面' if heads else '反面', GOLD_EDGE if heads else SILVER_DARK,
                           size=50, alpha=al)
            # labels
            pill_c(c, x, 1560, f'第 {k + 1} 枚', (CORAL, SKY)[k], size=38, alpha=a)
        if F_FLICK < t < F_LAND:
            al = 255 * min(fade_in(t, F_FLICK + 0.3), clamp01((F_LAND - t) / 0.3))
            pill_c(c, 540, 1700, '▶ 慢动作', INK_SOFT, size=34, alpha=al)
        draw_captions(c, self.caps, t)


# ================================================================ G: smoke -> weather
G_EMIT_X, G_EMIT_Y = 540, 1480
G_WEATHER = 56.0


class SceneG:
    def __init__(self):
        rng = np.random.default_rng(11)
        dt = 1 / FPS
        n_frames = int((G_END - G_START + 0.2) * FPS)
        warm = int(4.0 * FPS)                     # pre-roll so smoke is already rising
        parts = []                                # [x, y, vx, vy, age, seed]
        self.frames = []
        for fi in range(-warm, n_frames):
            tt = G_START + fi * dt
            for _ in range(2):
                parts.append([G_EMIT_X + rng.normal(0, 0.6), G_EMIT_Y, 0.0, -150.0, 0.0,
                              rng.uniform(0, 2 * math.pi)])
            alive = []
            for p in parts:
                h = G_EMIT_Y - p[1]
                turb = clamp01((h - 230) / 520) ** 1.4
                ph = p[5]
                ax = turb * 700 * (math.sin(0.016 * p[1] + 1.7 * tt + 0.35 * ph)
                                   + 0.7 * math.sin(0.037 * p[1] - 2.6 * tt + ph))
                ay = turb * 260 * math.sin(0.022 * p[0] + 2.0 * tt + ph)
                p[2] += (ax - 1.6 * p[2]) * dt
                p[3] += (ay - 1.0 * (p[3] + 150 * (1 - 0.4 * turb))) * dt
                p[0] += p[2] * dt
                p[1] += p[3] * dt
                p[4] += dt
                if p[4] < 7.0 and p[1] > 380:
                    alive.append(p)
            parts = alive
            if fi >= 0:
                self.frames.append(np.array([[p[0], p[1], p[4], G_EMIT_Y - p[1]] for p in parts]))
        self.caps = [
            Caption('点一根香，看它的烟', 49.6, 51.8, 210, size=78),
            Caption([('近处：', INK), ('笔直一条线', SKY)], 51.9, 53.9, 210, size=78),
            Caption([('远处：', INK), ('乱成一团', CORAL)], 54.0, G_WEATHER, 210, size=78),
            Caption('天气，也是这样', G_WEATHER + 0.15, 58.1, 210, size=82),
            Caption([('所以天气预报，最多准', INK), ('两周左右', CORAL)], 58.2, G_END, 210, size=62),
        ]

    def draw_smoke(self, c, t, alpha):
        f = int(np.clip(round((t - G_START) * FPS), 0, len(self.frames) - 1))
        pts = self.frames[f]
        for x, y, age, h in pts:
            k = clamp01(h / 1000)
            r = 5 + 34 * k
            a = alpha * (0.55 - 0.45 * k) * min(1, age / 0.2)
            c.drawCircle(x, y, r, paint((150, 158, 172), a * 255 * 0.55, blur=2 + r * 0.45))

    def draw_incense(self, c, alpha):
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(440, 1690, 200, 70), 30, 30), paint(RAIL, alpha))
        c.drawRect(skia.Rect.MakeLTRB(G_EMIT_X - 5, G_EMIT_Y + 6, G_EMIT_X + 5, 1700), paint((176, 96, 72), alpha))
        c.drawCircle(G_EMIT_X, G_EMIT_Y + 6, 9, paint((255, 120, 60), alpha * 0.6, blur=6))
        c.drawCircle(G_EMIT_X, G_EMIT_Y + 6, 5, paint((255, 90, 40), alpha))

    def draw_bracket(self, c, y0, y1, text, rgb, alpha):
        x = 880
        p = paint(rgb, alpha, stroke=6)
        c.drawLine(x, y0, x, y1, p)
        c.drawLine(x - 20, y0, x, y0, p)
        c.drawLine(x - 20, y1, x, y1, p)
        f = font(40, 'Bold')
        for i, ch in enumerate(text):
            c.drawString(ch, x + 22, (y0 + y1) / 2 - (len(text) - 1) * 24 + i * 48 + 14, f, paint(rgb, alpha))

    def draw_weather(self, c, t):
        cards = [('今天', 'sun', 1.0), ('明天', 'partly', 1.0), ('3 天后', 'rain', 0.95),
                 ('1 周后', 'cloud', 0.55), ('2 周后', '?', 1.0), ('1 个月后', '?', 1.0)]
        for k, (label, icon, clarity) in enumerate(cards):
            t0 = G_WEATHER + 0.25 + 0.28 * k
            if t < t0:
                continue
            s = ease_out_back((t - t0) / 0.4)
            col_, row = k % 3, k // 3
            cx, cy = 200 + col_ * 340, 760 + row * 470
            c.save()
            c.translate(cx, cy)
            c.scale(s, s)
            card(c, -150, -190, 300, 380)
            self.draw_icon(c, 0, -30, icon, clarity, t)
            text_c(c, 0, 125, label, 46, INK if clarity > 0.9 else INK_SOFT, 'Bold')
            c.restore()

    def draw_icon(self, c, x, y, icon, clarity, t):
        a = 255 * clarity
        blur = None if clarity > 0.9 else 4
        sun, cloud, rain = (255, 190, 50), (190, 202, 220), SKY
        if icon in ('sun', 'partly'):
            sx, sy = (x, y) if icon == 'sun' else (x - 30, y - 25)
            for i in range(8):
                ang = i * math.pi / 4 + t * 0.6
                c.drawLine(sx + 62 * math.cos(ang), sy + 62 * math.sin(ang), sx + 84 * math.cos(ang),
                           sy + 84 * math.sin(ang), paint(sun, a, stroke=9))
            c.drawCircle(sx, sy, 46, paint(sun, a))
        if icon in ('partly', 'rain', 'cloud'):
            cx, cy = (x + 15, y + 15) if icon == 'partly' else (x, y - 10)
            wob = 0 if clarity > 0.9 else 8 * math.sin(t * 5)
            for dx, dy, r in ((-40, 10, 38), (0, -16, 50), (42, 8, 40)):
                c.drawCircle(cx + dx + wob, cy + dy, r, paint(cloud, a, blur=blur))
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - 78 + wob, cy + 4, 156, 46), 23, 23),
                        paint(cloud, a, blur=blur))
            if icon == 'rain':
                for i in range(3):
                    yy = cy + 70 + ((t * 120 + i * 23) % 40)
                    c.drawLine(cx - 40 + i * 40, yy, cx - 50 + i * 40, yy + 22, paint(rain, a, stroke=8))
        if icon == '?':
            wob = 6 * math.sin(t * 4 + x)
            f = font(170, 'Black')
            c.drawString('?', x - f.measureText('?') / 2 + wob, y + 60, f, paint((200, 204, 214)))

    def draw(self, c, t):
        a_sm = 1 - ease_in_out((t - G_WEATHER) / 0.6)
        if a_sm > 0:
            a_in = ease_out_cubic((t - G_START) / 0.5)
            al = a_sm * a_in
            c.saveLayerAlpha(None, int(255 * al))
            self.draw_smoke(c, t, 1.0)
            self.draw_incense(c, 255)
            if t > 51.9:
                self.draw_bracket(c, 1250, 1460, '看得清', SKY, 255 * fade_in(t, 51.9))
            if t > 54.0:
                self.draw_bracket(c, 520, 1150, '乱成一团', CORAL, 255 * fade_in(t, 54.0))
            c.restore()
        if t > G_WEATHER:
            self.draw_weather(c, t)
        draw_captions(c, self.caps, t)


# ================================================================ H: contrast
H_GO = 63.2
H_STONE_ANG = (50.0, 52.0)
H_DIFF = 2.0
H_G = 1500.0
H_RANGE = 760.0
H_SLOW = 2.0
STONE_PANEL = (60, 360, 960, 640)       # x, y, w, h
BUMP_PANEL = (60, 1070, 960, 640)
H_PEGS = [(170, 170), (450, 120), (730, 170), (310, 340), (590, 340), (170, 500), (730, 500)]
H_BOX = (0, 0, 880, 560)
H_PEG_R, H_BALL_R = 48, 16


class SceneH:
    def __init__(self):
        self.v = math.sqrt(H_RANGE * H_G / math.sin(2 * math.radians(H_STONE_ANG[0])))
        dur = H_END - H_GO + 0.3
        self.pa, self.ba = bumper.simulate((440, 540), -95, 420, H_PEGS, H_PEG_R, H_BALL_R, H_BOX, dur, FPS)
        self.pb, self.bb = bumper.simulate((440, 540), -95 + H_DIFF, 420, H_PEGS, H_PEG_R, H_BALL_R, H_BOX, dur, FPS)
        self.peg_hits = [H_GO + t for (t, k, i) in self.ba if k == 'peg']
        self.land_t = [H_GO + H_SLOW * 2 * self.v * math.sin(math.radians(a)) / H_G for a in H_STONE_ANG]
        self.caps = [
            Caption('但，不是所有事都这样', 60.55, 62.9, 210, size=78),
            Caption([('两边起点都只差 ', INK), ('2°', CORAL)], 63.0, 66.6, 210, size=76),
            Caption([('关键看：差距会不会被', INK), ('放大', CORAL)], 66.7, H_END, 210, size=64),
        ]

    def stone_pos(self, k, t):
        a = math.radians(H_STONE_ANG[k])
        tr = max(0.0, (t - H_GO) / H_SLOW)
        T = 2 * self.v * math.sin(a) / H_G
        tr = min(tr, T)
        return self.v * math.cos(a) * tr, self.v * math.sin(a) * tr - 0.5 * H_G * tr * tr

    def draw(self, c, t):
        a = 255 * ease_out_cubic((t - 61.3) / 0.5)
        if a <= 0:
            draw_captions(c, self.caps, t)
            return
        # ---- stone panel
        x, y, w, h = STONE_PANEL
        card(c, x, y, w, h, a)
        pill_c(c, x + 150, y + 60, '扔石头', INK, size=40, alpha=a)
        gx, gy = x + 90, y + h - 90
        c.drawLine(x + 40, gy, x + w - 40, gy, paint(FELT_DARK, a, stroke=6))
        for k, rgb in ((1, SKY), (0, CORAL)):
            pts = []
            steps = 60
            for j in range(steps + 1):
                tt = H_GO + (min(t, self.land_t[k]) - H_GO) * j / steps
                px, py = self.stone_pos(k, tt)
                pts.append((gx + px, gy - py))
            if t > H_GO:
                path = skia.Path()
                path.moveTo(*pts[0])
                for p in pts[1:]:
                    path.lineTo(*p)
                pp = paint(rgb, a * 0.8, stroke=5)
                pp.setPathEffect(skia.DashPathEffect.Make([16, 12], 0))
                c.drawPath(path, pp)
            sx, sy = pts[-1] if t > H_GO else (gx, gy)
            c.drawCircle(sx, sy - 16, 18, paint(rgb, a))
            if t >= self.land_t[k]:
                c.drawLine(sx, gy, sx, gy - 70, paint(rgb, a, stroke=5))
                c.drawPath(self.flag(sx, gy - 70), paint(rgb, a))
        if t > max(self.land_t) + 0.2:
            al = 255 * fade_in(t, max(self.land_t) + 0.2)
            text_c(c, x + w / 2, y + 150, '落点只差一点点', 50, INK, 'Bold', al)
        # ---- bumper panel
        x, y, w, h = BUMP_PANEL
        card(c, x, y, w, h, a)
        pill_c(c, x + 150, y + 60, '撞圆球', INK, size=40, alpha=a)
        ox, oy = x + 40, y + 110
        c.save()
        c.translate(ox, oy)
        c.scale(1, (h - 140) / H_BOX[3])
        c.translate(-ox, -oy)
        draw_arena(c, ox, oy, H_BOX[2], H_BOX[3], H_PEGS, H_PEG_R, a)
        f = int(np.clip(round((t - H_GO) * FPS), 0, len(self.pa) - 1))
        draw_runner(c, ox, oy, self.pb, f, SKY, H_BALL_R, a, trail=60)
        draw_runner(c, ox, oy, self.pa, f, CORAL, H_BALL_R, a * 0.85, trail=60)
        c.restore()
        if t > 66.2:
            al = 255 * fade_in(t, 66.2)
            pill_c(c, x + w - 210, y + 60, '越撞差得越远', CORAL, size=40, alpha=al)
        draw_captions(c, self.caps, t)

    @staticmethod
    def flag(x, y):
        p = skia.Path()
        p.moveTo(x, y)
        p.lineTo(x + 44, y + 14)
        p.lineTo(x, y + 28)
        p.close()
        return p


# ================================================================ I: the butterfly
class SceneI:
    def __init__(self):
        rng = np.random.default_rng(5)
        self.swirls = []
        for k in range(160):
            while True:
                x, y = rng.uniform(70, 1010), rng.uniform(430, 1800)
                if not (300 < x < 780 and 650 < y < 1150):
                    break
            self.swirls.append((x, y, rng.uniform(16, 34), rng.uniform(0, 6.28), rng.choice([-1, 1]),
                                (CORAL, SKY, (255, 196, 36), (146, 92, 206), FELT)[k % 5]))
        self.t_pop = [73.3 + 2.3 * (k / 160) ** 0.55 for k in range(160)]
        self.caps = [
            Caption('一只蝴蝶，能掀起一场风暴吗？', 70.6, 73.1, 210, size=64),
            Caption('其实，不是它一只', 73.25, 75.7, 210, size=80),
            Caption('风、鸟、车、炊烟……到处都是微小的扰动', 73.6, 75.7, 320, size=42, color=INK_SOFT,
                    weight='Medium'),
            Caption('无数微小的差别', 75.85, I_END, 210, size=84),
            Caption([('让未来', INK), ('算不准', CORAL)], 76.35, I_END, 330, size=84),
        ]

    def draw(self, c, t):
        for (x, y, r, ph, d, rgb), t0 in zip(self.swirls, self.t_pop):
            if t < t0:
                continue
            s = ease_out_back((t - t0) / 0.35)
            path = skia.Path()
            for j in range(40):
                u = j / 39
                ang = ph + d * (t * 3 + u * 9)
                rr = r * s * u
                px, py = x + rr * math.cos(ang), y + rr * math.sin(ang)
                path.moveTo(px, py) if j == 0 else path.lineTo(px, py)
            c.drawPath(path, paint(rgb, 170, stroke=5))
        bs = ease_out_back((t - I_START) / 0.6)
        draw_butterfly_s(c, 540, 900 - 16 * math.sin(t * 2.4), t, 0.85 * bs)
        draw_captions(c, self.caps, t)


def draw_butterfly_s(c, x, y, t, scale):
    if scale > 0:
        s1.draw_butterfly(c, x, y, t, scale=scale)


# ================================================================ J: ending
class SceneJ:
    def __init__(self, scene_a):
        self.A = scene_a
        self.caps = [
            Caption('规律是确定的', 79.75, VIDEO_END + 1, 800, size=104, weight='Black'),
            Caption([('未来，却', INK), ('算不准', CORAL)], 80.75, VIDEO_END + 1, 960, size=104, weight='Black'),
            Caption([('你还见过哪些「', INK_SOFT), ('蝴蝶效应', INK), ('」？', INK_SOFT)], 82.6, VIDEO_END + 1, 1240,
                    size=56, weight='Bold'),
            Caption('评论区聊聊', 83.1, VIDEO_END + 1, 1340, size=46, color=INK_SOFT, weight='Medium'),
        ]

    def draw(self, c, t):
        # the two finished tables from the opening, faded into the background
        for cy, sim in zip(s1.TABLE_CY, self.A.sims):
            s1.draw_table(c, cy)
            s1.draw_balls(c, cy, sim, s1.A_END)
        veil = 0.9 * ease_out_cubic((t - J_START) / 0.8)
        c.drawRect(skia.Rect.MakeWH(W, H), paint(BG, 255 * veil))
        draw_captions(c, self.caps, t)
