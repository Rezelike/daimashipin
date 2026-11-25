# -*- coding: utf-8 -*-
"""60 秒样片的场景背景和界面叠加（倒计时、TT 悬浮条、字幕、花字、击杀播报）。"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import render_hero_select as hero
import sample_figures as SF

W, H = hero.W, hero.H
F = hero.F
clamp, ease_out, ease_back = hero.clamp, hero.ease_out, hero.ease_back


def nd(img):
    return ImageDraw.Draw(img, 'RGBA')


def mixc(c1, c2, u):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * u) for i in range(3))


def vgrad(w, h, c1, c2, power=1.0):
    t = (np.linspace(0, 1, h) ** power)[:, None, None]
    arr = np.array(c1, np.float32) * (1 - t) + np.array(c2, np.float32) * t
    return Image.fromarray(np.repeat(arr, w, axis=1).astype(np.uint8), 'RGB')


def glow(img, x, y, r, color, a=0.55):
    r = max(2, int(r))
    s = r * 3
    m = Image.new('L', (2 * s, 2 * s), 0)
    ImageDraw.Draw(m).ellipse((s - r, s - r, s + r, s + r), fill=int(255 * a))
    m = m.filter(ImageFilter.GaussianBlur(r * 0.55))
    img.paste(Image.new('RGB', m.size, color), (int(x - s), int(y - s)), m)


def stars(d, seed, n, box):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = float(rng.choice([0.8, 1.0, 1.2, 1.6, 2.0]))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(rng.uniform(80, 230))))


def moon(img, x, y, r):
    glow(img, x, y, r * 2.4, (110, 130, 200), 0.35)
    d = nd(img)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(246, 240, 214, 255))
    d.ellipse((x - r * 0.45, y - r * 0.35, x - r * 0.12, y - r * 0.02), fill=(228, 222, 198, 255))
    d.ellipse((x + r * 0.1, y + r * 0.2, x + r * 0.42, y + r * 0.5), fill=(232, 226, 202, 255))


def building(d, rng, x, base, w, h, body, lit):
    d.rectangle((x, base - h, x + w, base), fill=tuple(body) + (255,))
    for i in range(max(1, int((w - 10) // 22))):
        for j in range(max(1, int((h - 12) // 26))):
            wx, wy = x + 8 + i * 22, base - h + 10 + j * 26
            if wx + 10 > x + w - 4 or wy + 12 > base - 4:
                continue
            if rng.random() < lit:
                col = [(255, 214, 140), (255, 236, 190), (170, 210, 255)][int(rng.integers(0, 3))]
                d.rectangle((wx, wy, wx + 10, wy + 12), fill=col + (220,))
            else:
                d.rectangle((wx, wy, wx + 10, wy + 12), fill=(36, 42, 66, 255))


def skyline(d, seed, x0, x1, base, hmin, hmax, body=(22, 26, 48), lit=0.35):
    rng = np.random.default_rng(seed)
    x = x0
    while x < x1:
        w = int(rng.uniform(70, 160))
        building(d, rng, x, base, w, int(rng.uniform(hmin, hmax)), body, lit)
        x += w + int(rng.uniform(10, 40))


def tree(d, x, base, s, col=(18, 36, 40)):
    d.rectangle((x - s * 0.06, base - s * 0.9, x + s * 0.06, base), fill=(30, 24, 22, 255))
    for dx, dy, r in [(-0.3, -1.0, 0.38), (0.25, -1.05, 0.4), (0, -1.35, 0.42), (-0.05, -0.85, 0.35)]:
        d.ellipse((x + (dx - r) * s, base + (dy - r) * s, x + (dx + r) * s, base + (dy + r) * s), fill=tuple(col) + (255,))


def willow(d, x, base, s):
    d.rectangle((x - s * 0.05, base - s, x + s * 0.05, base), fill=(30, 26, 24, 255))
    for k in range(14):
        a = -1.0 + k / 13 * 2.0
        x0 = x + a * s * 0.45
        d.line((x + a * s * 0.1, base - s * 1.05, x0, base - s * (0.95 - 0.5 * (1 - abs(a)))), fill=(24, 48, 44, 255), width=int(s * 0.05))
        d.line((x0, base - s * (0.95 - 0.5 * (1 - abs(a))), x0 + a * s * 0.05, base - s * 0.25), fill=(30, 58, 52, 255), width=int(s * 0.035))


def lamp(img, x, base, hgt, on=True, r=60):
    d = nd(img)
    d.rectangle((x - 3, base - hgt, x + 3, base), fill=(40, 44, 56, 255))
    d.rounded_rectangle((x - 14, base - hgt - 10, x + 14, base - hgt + 4), radius=4, fill=(60, 64, 78, 255))
    if on:
        glow(img, x, base - hgt, r, (255, 200, 120), 0.45)
        nd(img).ellipse((x - 8, base - hgt - 4, x + 8, base - hgt + 8), fill=(255, 236, 190, 255))


def water(img, y0, y1, t, moon_x=None, seed=9):
    d = nd(img)
    for y in range(y0, y1, 6):
        k = (y - y0) / max(1, y1 - y0)
        d.rectangle((0, y, img.width, y + 6), fill=mixc((22, 30, 58), (10, 14, 30), k) + (255,))
    rng = np.random.default_rng(seed)
    for _ in range(int(img.width / 9)):
        y = rng.uniform(y0 + 4, y1)
        x = (rng.uniform(0, img.width) + t * 30 * (1 + (y - y0) / 200)) % img.width
        ln = rng.uniform(20, 70) * (0.6 + (y - y0) / max(1, y1 - y0))
        d.line((x, y, x + ln, y), fill=(140, 160, 210, int(rng.uniform(25, 70))), width=2)
    if moon_x is not None:
        for j in range(26):
            y = y0 + 6 + j * (y1 - y0 - 6) / 26
            w = 26 + 5 * math.sin(t * 3 + j)
            d.line((moon_x - w, y, moon_x + w, y), fill=(240, 230, 190, max(0, 120 - j * 4)), width=3)


def zoom(img, s, cx=W / 2, cy=H / 2):
    if abs(s - 1) < 1e-3:
        return img
    w, h = W / s, H / s
    x0 = min(max(cx - w / 2, 0), W - w) if s > 1 else cx - w / 2
    y0 = min(max(cy - h / 2, 0), H - h) if s > 1 else cy - h / 2
    return img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)


def shake(img, dx, dy):
    if not dx and not dy:
        return img
    out = Image.new('RGB', img.size, (0, 0, 0))
    out.paste(img, (int(dx), int(dy)))
    return out


def speed_lines(d, t, seed=4, n=22, color=(255, 255, 255), dirx=-1):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        y = rng.uniform(60, H - 60)
        x = (rng.uniform(0, W) + dirx * t * 2600) % (W + 300) - 150
        ln = rng.uniform(80, 260)
        d.line((x, y, x - dirx * ln, y), fill=tuple(color) + (int(rng.uniform(60, 160)),), width=int(rng.uniform(2, 5)))


# ---------------------------------------------------------------- 背景
@lru_cache(maxsize=None)
def bg_dorm():
    img = vgrad(W, H, (40, 48, 68), (24, 28, 40))
    d = nd(img)
    d.polygon([(0, 560), (W, 560), (W, H), (0, H)], fill=(30, 32, 42, 255))
    for i in range(-8, 18):
        d.line([(640 + i * 60, 560), (640 + i * 200, H)], fill=(255, 255, 255, 10), width=2)
    d.rectangle((500, 110, 780, 330), fill=(14, 20, 44, 255))
    stars(d, 1, 40, (505, 115, 775, 250))
    skyline(d, 2, 500, 780, 330, 40, 110, lit=0.4)
    moon(img, 720, 160, 18)
    d = nd(img)
    d.rectangle((500, 110, 780, 330), outline=(80, 88, 108, 255), width=8)
    d.line((640, 110, 640, 330), fill=(80, 88, 108, 255), width=6)
    d.rounded_rectangle((110, 60, 330, 118), radius=10, fill=(200, 205, 212, 255))
    for k in range(5):
        d.line((130, 92 + k * 4, 310, 92 + k * 4), fill=(160, 165, 172, 255), width=1)
    d.rectangle((360, 150, 470, 230), fill=(228, 230, 234, 255), outline=(120, 120, 130, 255), width=3)
    d.rectangle((40, 160, 110, 260), fill=(150, 70, 80, 255))
    d.rectangle((800, 140, 850, 210), fill=(70, 110, 150, 255))
    d.rectangle((30, 455, 440, 476), fill=(96, 74, 56, 255))
    for x in (40, 420):
        d.rectangle((x, 476, x + 12, 560), fill=(70, 54, 42, 255))
    d.rounded_rectangle((110, 300, 330, 432), radius=8, fill=(18, 22, 30, 255))
    d.rectangle((122, 312, 318, 420), fill=(60, 120, 200, 255))
    for k in range(6):
        d.rectangle((135 + k * 30, 380 - k * 9, 155 + k * 30, 410), fill=(120, 200, 255, 160))
    d.rectangle((210, 432, 230, 455), fill=(30, 30, 36, 255))
    glow(img, 220, 365, 120, (80, 140, 230), 0.35)
    d = nd(img)
    for x in (860, 1236):
        d.rectangle((x, 120, x + 10, H), fill=(140, 148, 160, 255))
    d.rectangle((860, 340, 1246, 360), fill=(150, 158, 170, 255))
    d.rounded_rectangle((872, 300, 1234, 342), radius=10, fill=(88, 108, 160, 255))
    d.rounded_rectangle((1150, 286, 1226, 316), radius=10, fill=(230, 230, 236, 255))
    d.line((872, 262, 1100, 262), fill=(140, 148, 160, 255), width=6)
    for y in range(380, H, 50):
        d.line((876, y, 912, y), fill=(140, 148, 160, 255), width=5)
    d.line((876, 360, 876, H), fill=(140, 148, 160, 255), width=5)
    d.line((912, 360, 912, H), fill=(140, 148, 160, 255), width=5)
    d.rectangle((930, 520, 1236, 540), fill=(96, 74, 56, 255))
    d.rounded_rectangle((990, 410, 1170, 512), radius=8, fill=(18, 22, 30, 255))
    d.rectangle((1000, 420, 1160, 502), fill=(60, 120, 200, 255))
    glow(img, 1080, 460, 110, (80, 140, 230), 0.3)
    glow(img, 420, 420, 90, (255, 200, 120), 0.25)
    return img


@lru_cache(maxsize=None)
def bg_dorm_blur():
    return Image.eval(bg_dorm().filter(ImageFilter.GaussianBlur(7)), lambda v: int(v * 0.7))


@lru_cache(maxsize=None)
def bg_balcony():
    img = vgrad(W, H, (10, 14, 34), (48, 36, 78), 1.2)
    d = nd(img)
    stars(d, 3, 140, (0, 0, W, 380))
    moon(img, 1080, 120, 46)
    d = nd(img)
    skyline(d, 4, -40, W + 40, 560, 60, 190, body=(24, 26, 50), lit=0.3)
    for x in range(30, W, 160):
        tree(d, x, 562, 70, (14, 28, 34))
    for x in range(80, W, 230):
        glow(img, x, 548, 16, (255, 200, 120), 0.6)
    d = nd(img)
    d.rectangle((0, 640, W, H), fill=(32, 32, 44, 255))
    d.rectangle((0, 518, W, 530), fill=(160, 168, 186, 255))
    for x in range(0, W, 42):
        d.rectangle((x, 530, x + 5, 640), fill=(120, 128, 146, 255))
    d.rectangle((0, 636, W, 646), fill=(130, 138, 156, 255))
    d.line((0, 58, W, 58), fill=(160, 168, 186, 255), width=5)
    for x, col in [(160, (220, 120, 140)), (330, (120, 170, 230)), (1000, (240, 230, 220))]:
        d.line((x, 58, x, 72), fill=(200, 200, 210, 255), width=2)
        d.polygon([(x - 50, 72), (x + 50, 72), (x + 66, 100), (x + 42, 108), (x + 40, 170), (x - 40, 170), (x - 42, 108), (x - 66, 100)],
                  fill=col + (255,))
    return img


def telescope(d, x, base, aim=-1, s=1.0):
    """三脚架天文望远镜，aim=-1 朝左。返回目镜位置。"""
    top = (x, base - 150 * s)
    for dx in (-48, 0, 44):
        d.line((top, (x + dx * s, base)), fill=(210, 210, 222, 255), width=int(5 * s))
    x0, y0 = x - aim * 70 * s, base - 122 * s
    x1, y1 = x + aim * 120 * s, base - 196 * s
    d.line(((x0, y0), (x1, y1)), fill=(236, 236, 244, 255), width=int(30 * s))
    d.line(((x1, y1), (x1 + aim * 16 * s, y1 - 9 * s)), fill=(120, 120, 134, 255), width=int(38 * s))
    d.line(((x0, y0), (x0 - aim * 18 * s, y0 + 9 * s)), fill=(80, 80, 92, 255), width=int(16 * s))
    return (x0 - aim * 24 * s, y0 + 10 * s)


@lru_cache(maxsize=None)
def bg_gate_world():
    """望远镜看到的南门（1600×900 的大图）和里面几个目标的位置。"""
    w, h = 1600, 900
    img = vgrad(w, h, (16, 20, 40), (44, 44, 62))
    d = nd(img)
    stars(d, 5, 60, (0, 0, w, 300))
    skyline(d, 6, -20, w, 520, 90, 220, body=(26, 28, 52), lit=0.25)
    d.rectangle((0, 560, w, h), fill=(44, 46, 56, 255))
    d.rectangle((0, 600, w, 612), fill=(70, 72, 84, 255))
    for x in range(220, 1390, 26):
        d.rectangle((x, 380, x + 6, 560), fill=(70, 74, 90, 255))
    d.rectangle((220, 380, 1390, 390), fill=(80, 84, 100, 255))
    for x in (170, 1390):
        d.rectangle((x, 300, x + 60, 600), fill=(110, 104, 110, 255))
    rng = np.random.default_rng(8)
    sx0, sx1 = 500, 920
    for k, y in enumerate((430, 490, 550)):
        d.rectangle((sx0, y, sx1, y + 8), fill=(170, 176, 190, 255))
    for x in (sx0, sx1 - 8):
        d.rectangle((x, 410, x + 8, 600), fill=(170, 176, 190, 255))
    red_pos = None
    palette = [(90, 140, 210), (230, 200, 90), (240, 240, 236), (170, 120, 80), (110, 190, 140), (200, 130, 190)]
    for k, y in enumerate((430, 490, 550)):
        x = sx0 + 16
        while x < sx1 - 50:
            bw = int(rng.uniform(34, 52))
            bh = int(rng.uniform(30, 44))
            if k == 2 and red_pos is None and x > 700:
                SF.draw_bag(d, x + 24, y - 22, 50)
                red_pos = (x + 24, y - 22)
                x += 64
                continue
            d.rounded_rectangle((x, y - bh, x + bw, y), radius=5, fill=palette[int(rng.integers(0, len(palette)))] + (255,))
            x += bw + int(rng.uniform(6, 14))
    d.rectangle((1010, 420, 1170, 600), fill=(150, 150, 160, 255))
    d.polygon([(995, 420), (1185, 420), (1150, 390), (1030, 390)], fill=(120, 60, 60, 255))
    d.rectangle((1030, 450, 1150, 520), fill=(255, 220, 150, 255))
    SF.put(img, 'guard', dict(view='front', bust=True, arms=((8, 4), {'ik': (0.0, 0.12), 'rel': 'Hc', 'bend': 1})), 1090, 540, 160,
           expr='deadpan', hold='thermos', glow=False)
    nd(img).rectangle((1030, 518, 1150, 600), fill=(150, 150, 160, 255))
    d = nd(img)
    d.rectangle((1230, 560, 1420, 572), fill=(120, 84, 60, 255))
    d.rectangle((1230, 520, 1420, 530), fill=(120, 84, 60, 255))
    for x in (1240, 1405):
        d.rectangle((x, 572, x + 8, 610), fill=(70, 54, 42, 255))
    SF.put(img, 'girl', dict(view='front', arms=((10, 4), (10, 4)), legs=((2, 0), (2, 0)), legscale=(0.35, 1.0)), 1290, 560, 150,
           expr='happy', glow=False)
    SF.put(img, 'boy', dict(view='front', arms=((10, 4), {'ik': (0.05, 0.15), 'rel': 'N', 'bend': 1}), legs=((2, 0), (2, 0)),
                            legscale=(0.35, 1.0)), 1360, 560, 155, expr='happy', hold='cup', glow=False)
    for x in (110, 1500):
        lamp(img, x, 610, 260)
    return img, dict(bag=red_pos, guard=(1090, 470), couple=(1325, 470))


@lru_cache(maxsize=None)
def bg_street_far():
    img = vgrad(3600, H, (14, 18, 38), (46, 40, 70))
    d = nd(img)
    stars(d, 11, 160, (0, 0, 3600, 300))
    skyline(d, 12, -40, 3640, 520, 80, 230, body=(26, 28, 52), lit=0.3)
    return img


@lru_cache(maxsize=None)
def bg_street_near():
    img = Image.new('RGBA', (4200, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 560, 4200, H), fill=(44, 46, 56, 255))
    d.rectangle((0, 600, 4200, 610), fill=(70, 72, 84, 255))
    for x in range(0, 4200, 320):
        d.rectangle((x, 640, x + 160, 650), fill=(200, 200, 160, 120))
    for x in range(160, 900, 26):
        d.rectangle((x, 380, x + 6, 560), fill=(70, 74, 90, 255))
    d.rectangle((160, 380, 900, 390), fill=(80, 84, 100, 255))
    rng = np.random.default_rng(13)
    palette = [(90, 140, 210), (230, 200, 90), (240, 240, 236), (170, 120, 80), (110, 190, 140)]
    for y in (430, 490, 550):
        d.rectangle((300, y, 720, y + 8), fill=(170, 176, 190, 255))
        x = 316
        while x < 680:
            bw = int(rng.uniform(34, 52))
            bh = int(rng.uniform(30, 44))
            d.rounded_rectangle((x, y - bh, x + bw, y), radius=5, fill=palette[int(rng.integers(0, len(palette)))] + (255,))
            x += bw + 10
    for x in (300, 712):
        d.rectangle((x, 410, x + 8, 600), fill=(170, 176, 190, 255))
    for x in range(1100, 4200, 380):
        tree(d, x, 600, 150, (16, 34, 38))
    return img


@lru_cache(maxsize=None)
def bg_road():
    img = vgrad(W, H, (14, 18, 38), (46, 40, 70))
    d = nd(img)
    stars(d, 21, 90, (0, 0, W, 300))
    for x in (160, 470, 1150):
        glow(img, x, 300, 70, (220, 230, 255), 0.25)
    d = nd(img)
    skyline(d, 22, -40, W + 40, 470, 60, 150, body=(28, 30, 54), lit=0.25)
    for x in (80, 300, 980, 1200):
        tree(d, x, 560, 180, (16, 34, 38))
    d.rectangle((0, 560, W, H), fill=(44, 46, 56, 255))
    d.rectangle((0, 592, W, 600), fill=(70, 72, 84, 255))
    for x in (60, 1220):
        lamp(img, x, 590, 300)
    d = nd(img)
    d.rectangle((470, 470, 810, 482), fill=(130, 90, 64, 255))
    d.rectangle((470, 520, 810, 534), fill=(130, 90, 64, 255))
    for x in (486, 790):
        d.rectangle((x, 534, x + 10, 590), fill=(70, 54, 42, 255))
    return img


@lru_cache(maxsize=None)
def bg_slope_top():
    img = vgrad(W, H, (12, 16, 36), (52, 40, 78), 1.1)
    d = nd(img)
    stars(d, 31, 120, (0, 0, W, 330))
    skyline(d, 32, -40, W + 40, 520, 50, 140, body=(24, 26, 50), lit=0.25)
    glow(img, 640, 250, 260, (255, 210, 150), 0.42)
    d = nd(img)
    d.rectangle((0, 560, W, H), fill=(40, 42, 54, 255))
    d.polygon([(900, 560), (W, 560), (W, 600)], fill=(30, 32, 42, 255))
    for x in (120, 1160):
        tree(d, x, 560, 170, (14, 28, 34))
    lamp(img, 640, 562, 320, r=120)
    return img


@lru_cache(maxsize=None)
def bg_slope_down():
    img = vgrad(W, H, (12, 16, 36), (52, 40, 78), 1.1)
    d = nd(img)
    stars(d, 41, 100, (0, 0, W, 260))
    skyline(d, 42, -40, W + 40, 360, 40, 120, body=(24, 26, 50), lit=0.25)
    d.polygon([(0, 260), (W, 600), (W, H), (0, H)], fill=(20, 40, 36, 255))
    d.polygon([(0, 250), (W, 590), (W, 700), (0, 360)], fill=(48, 50, 62, 255))
    d.line((0, 305, W, 645), fill=(220, 220, 180, 90), width=4)
    for k in range(6):
        x = 60 + k * 230
        y = 250 + (590 - 250) * x / W
        lamp(img, x, y, 170, r=50)
    return img


@lru_cache(maxsize=None)
def bg_booth():
    img = vgrad(W, H, (70, 56, 40), (40, 32, 26))
    d = nd(img)
    d.rectangle((0, 0, W, H), outline=(210, 205, 196, 255), width=60)
    d.rectangle((60, 60, W - 60, H - 60), fill=(16, 20, 38, 255))
    stars(d, 51, 40, (60, 60, W - 60, 300))
    lamp(img, 1050, 640, 420)
    d = nd(img)
    d.rectangle((60, 560, W - 60, H - 60), fill=(150, 120, 80, 255))
    d.rectangle((0, 600, W, H), fill=(120, 96, 66, 255))
    return img


@lru_cache(maxsize=None)
def bg_lake(w=W):
    img = vgrad(w, H, (10, 14, 36), (40, 40, 80), 1.1)
    d = nd(img)
    stars(d, 61, int(150 * w / W), (0, 0, w, 300))
    moon(img, int(w * 0.22), 130, 52)
    d = nd(img)
    skyline(d, 62, -40, w + 40, 360, 50, 150, body=(26, 28, 54), lit=0.4)
    return img


@lru_cache(maxsize=None)
def bg_door():
    img = vgrad(W, H, (34, 38, 56), (26, 28, 40))
    d = nd(img)
    rng = np.random.default_rng(71)
    for x in range(60, W, 140):
        for y in (40, 140):
            lit = rng.random() < 0.5
            d.rectangle((x, y, x + 80, y + 64), fill=((255, 216, 150) if lit else (40, 46, 70)) + (255,))
    d.rectangle((420, 200, 860, 250), fill=(70, 74, 92, 255))
    d.rounded_rectangle((560, 208, 720, 242), radius=6, fill=(220, 210, 180, 255))
    d.text((640, 225), '8号楼', font=F('Black', 26), fill=(60, 40, 30, 255), anchor='mm')
    d.rectangle((450, 250, 830, 640), fill=(60, 60, 72, 255))
    d.rectangle((470, 262, 810, 640), fill=(255, 226, 170, 255))
    glow(img, 640, 450, 200, (255, 220, 160), 0.35)
    d = nd(img)
    d.rectangle((880, 360, 1060, 520), fill=(255, 220, 150, 255), outline=(90, 90, 104, 255), width=8)
    d.rectangle((0, 640, W, H), fill=(70, 72, 84, 255))
    for k, y in enumerate((640, 666, 692)):
        d.rectangle((400 - k * 30, y, 880 + k * 30, y + 26), fill=(96, 98, 110, 255), outline=(60, 62, 74, 255))
    lamp(img, 220, 640, 420)
    return img


@lru_cache(maxsize=None)
def bg_stairs():
    img = vgrad(W, H, (210, 214, 206), (180, 184, 176))
    d = nd(img)
    d.polygon([(0, 420), (W, 640), (W, H), (0, H)], fill=(110, 150, 120, 255))
    steps = 14
    for k in range(steps):
        x0 = k * W / steps
        y0 = 330 + k * 26
        d.rectangle((x0, y0, x0 + W / steps + 2, H), fill=(150, 150, 150, 255))
        d.line((x0, y0, x0 + W / steps, y0), fill=(110, 110, 110, 255), width=4)
    d.line((0, 190, W, 410), fill=(90, 90, 100, 255), width=8)
    for k in range(0, steps, 2):
        x = k * W / steps + 20
        d.line((x, 190 + 220 * x / W, x, 330 + k * 26), fill=(90, 90, 100, 255), width=4)
    glow(img, 300, 60, 80, (255, 255, 230), 0.6)
    return img


@lru_cache(maxsize=None)
def bg_lobby():
    img = vgrad(W, H, (214, 210, 196), (190, 184, 170))
    d = nd(img)
    d.rectangle((0, 380, W, H), fill=(176, 170, 156, 255))
    for i in range(-10, 22):
        d.line((640 + i * 70, 380, 640 + i * 260, H), fill=(140, 134, 122, 255), width=2)
    for y in (420, 480, 560, 660):
        d.line((0, y, W, y), fill=(140, 134, 122, 255), width=2)
    d.rectangle((860, 120, 1120, 300), fill=(255, 226, 170, 255), outline=(120, 110, 100, 255), width=10)
    d.rectangle((160, 120, 420, 300), fill=(238, 238, 230, 255), outline=(150, 140, 120, 255), width=6)
    for k in range(4):
        d.rectangle((180 + k * 60, 140, 228 + k * 60, 200), fill=(250, 250, 250, 255), outline=(200, 200, 200, 255))
    return img


def bg_victory(t):
    img = vgrad(W, H, (40, 24, 8), (10, 6, 2))
    d = nd(img)
    for k in range(18):
        a = t * 0.4 + k * math.pi / 9
        d.polygon([(640, 330), (640 + 1200 * math.cos(a - 0.06), 330 + 1200 * math.sin(a - 0.06)),
                   (640 + 1200 * math.cos(a + 0.06), 330 + 1200 * math.sin(a + 0.06))], fill=(255, 200, 90, 26))
    glow(img, 640, 330, 220, (255, 200, 100), 0.4)
    return img


# ---------------------------------------------------------------- 界面叠加
def caption(d, text, x, y, size, t, t0, color=(255, 230, 90), stroke=(20, 14, 10), weight='Black', anchor='mm', pop=True):
    """综艺花字：弹出来，再停住。"""
    u = (t - t0) / 0.22
    if u < 0:
        return
    sc = ease_back(u) if (pop and u < 1) else 1.0
    a = int(255 * clamp(u * 3))
    d.text((x, y), text, font=F(weight, size * max(0.3, sc)), fill=tuple(color) + (a,), anchor=anchor,
           stroke_width=max(2, int(size * 0.09)), stroke_fill=tuple(stroke) + (a,))


def tag(d, x, y, text, color=(255, 255, 255), bg=(10, 14, 20), size=20, alpha=1.0):
    """游戏里的头顶标签：带小三角的圆角条。"""
    f = F('Bold', size)
    w = f.getlength(text) + 22
    A = int(230 * alpha)
    d.rounded_rectangle((x - w / 2, y - size - 10, x + w / 2, y + 6), radius=6, fill=tuple(bg) + (A,),
                        outline=tuple(color) + (A,), width=2)
    d.polygon([(x - 8, y + 6), (x + 8, y + 6), (x, y + 16)], fill=tuple(bg) + (A,))
    d.text((x, y - size / 2 - 2), text, font=f, fill=tuple(color) + (int(255 * alpha),), anchor='mm')


def killfeed(d, t, t0, parts, y=86, life=2.2):
    """右上角的播报：parts = [(文字, 颜色), ...]。"""
    if not (t0 <= t < t0 + life):
        return
    u = (t - t0) / 0.2
    f = F('Bold', 22)
    total = sum(f.getlength(s) for s, _ in parts) + 14 * (len(parts) - 1) + 30
    a = clamp(min(u, (t0 + life - t) / 0.25))
    x1 = 1258
    x0 = x1 - total + (1 - ease_out(u)) * 120
    d.rounded_rectangle((x0, y, x1, y + 38), radius=6, fill=(8, 12, 18, int(200 * a)))
    d.rectangle((x1 - 5, y, x1, y + 38), fill=(255, 70, 85, int(255 * a)))
    x = x0 + 15
    for s, col in parts:
        d.text((x, y + 19), s, font=f, fill=tuple(col) + (int(255 * a),), anchor='lm')
        x += f.getlength(s) + 14


def subtitle(d, text, color=(255, 255, 255), size=32):
    d.text((640, 698), text, font=F('Bold', size), fill=tuple(color) + (255,), anchor='ms', stroke_width=4, stroke_fill=(0, 0, 0, 220))


def title(d, text='TT语音 · 组队中'):
    d.rounded_rectangle((30, 22, 42, 44), radius=6, fill=(255, 255, 255, 235))
    d.arc((25, 30, 47, 52), 0, 180, fill=(255, 255, 255, 235), width=2)
    d.line((36, 52, 36, 57), fill=(255, 255, 255, 235), width=2)
    d.text((56, 38), text, font=F('Bold', 24), fill=(255, 255, 255, 240), anchor='lm',
           stroke_width=2, stroke_fill=(0, 0, 0, 120))


def countdown_pill(d, secs, t, urgent=False):
    mm, ss = divmod(max(0, int(secs)), 60)
    if urgent:
        p = 0.5 + 0.5 * math.sin(2 * math.pi * 2.2 * t)
        d.rounded_rectangle((466, 10, 814, 74), radius=32, fill=mixc((190, 30, 46), (255, 80, 90), p) + (245,))
        d.text((496, 42), '门禁倒计时', font=F('Medium', 24), fill=(255, 255, 255, 240), anchor='lm')
        d.text((794, 43), f'{mm:02d}:{ss:02d}', font=F('Num', 44), fill=(255, 255, 255, 255), anchor='rm')
    else:
        d.rounded_rectangle((506, 15, 774, 61), radius=23, fill=(200, 34, 50, 235))
        d.text((530, 38), '门禁倒计时', font=F('Medium', 19), fill=(255, 255, 255, 235), anchor='lm')
        d.text((754, 39), f'{mm:02d}:{ss:02d}', font=F('Num', 32), fill=(255, 255, 255, 255), anchor='rm')


AVATARS = [('聪', (150, 150, 160)), ('飞', (255, 70, 85)), ('K', (255, 186, 30)), ('周', (64, 150, 255)), ('星', (172, 112, 255))]


def ttbar(d, talking=(), t=0.0):
    d.rounded_rectangle((884, 14, 1258, 62), radius=24, fill=(8, 12, 18, 215), outline=(255, 255, 255, 45), width=1)
    for i in range(6):
        cx, cy, r = 912 + i * 57, 38, 18
        if i == 5:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(62, 62, 70, 255))
            d.text((cx, cy), '?', font=F('Bold', 20), fill=(150, 150, 158, 255), anchor='mm')
            continue
        ini, col = AVATARS[i]
        if i in talking:
            ph = (t * 4) % 1
            d.ellipse((cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5), outline=(60, 235, 140, 255), width=3)
            r2 = r + 5 + 10 * ph
            d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=(60, 235, 140, int(160 * (1 - ph))), width=2)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(col) + (255,))
        d.text((cx, cy), ini, font=F('Bold', 18), fill=(255, 255, 255, 255), anchor='mm')


def watermark(d):
    d.text((20, 708), '样片｜人物、场景和界面都是占位', font=F('Medium', 15), fill=(255, 255, 255, 120), anchor='ls')


def phone_frame(img, x, y, w, h, screen=(246, 246, 250)):
    d = nd(img)
    d.rounded_rectangle((x, y, x + w, y + h), radius=40, fill=(16, 16, 20, 255), outline=(96, 98, 110, 255), width=4)
    sx0, sy0, sx1, sy1 = x + 14, y + 14, x + w - 14, y + h - 14
    d.rounded_rectangle((sx0, sy0, sx1, sy1), radius=30, fill=tuple(screen) + (255,))
    d.rounded_rectangle((x + w / 2 - 46, y + 20, x + w / 2 + 46, y + 36), radius=8, fill=(16, 16, 20, 255))
    return (sx0, sy0, sx1, sy1)
