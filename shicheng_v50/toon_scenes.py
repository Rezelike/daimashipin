# -*- coding: utf-8 -*-
"""卡通版场景：寝室、阳台、南门、校园路、大坡、岗亭、人工湖、宿舍楼门口、楼梯、大厅，和各种特效。"""
import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import render_hero_select as hero
import toon as T

W, H = 1280, 720
F = hero.F
INK = T.INK
clamp, ease_out, ease_back = hero.clamp, hero.ease_out, hero.ease_back


def nd(img):
    return ImageDraw.Draw(img, 'RGBA')


def mixc(a, b, u):
    return tuple(int(a[i] + (b[i] - a[i]) * u) for i in range(3))


def vgrad(w, h, stops):
    """stops = [(位置0..1, 颜色), ...]"""
    ys = np.linspace(0, 1, h)
    arr = np.zeros((h, 3), np.float32)
    for c in range(3):
        arr[:, c] = np.interp(ys, [s[0] for s in stops], [s[1][c] for s in stops])
    return Image.fromarray(np.repeat(arr[:, None, :], w, axis=1).astype(np.uint8), 'RGB')


def glow(img, x, y, r, color, a=0.5):
    r = max(2, int(r))
    s = r * 3
    m = Image.new('L', (2 * s, 2 * s), 0)
    ImageDraw.Draw(m).ellipse((s - r, s - r, s + r, s + r), fill=int(255 * a))
    m = m.filter(ImageFilter.GaussianBlur(r * 0.6))
    img.paste(Image.new(img.mode, m.size, tuple(color) + ((255,) if img.mode == 'RGBA' else ())), (int(x - s), int(y - s)), m)


def cone(img, x, y0, y1, w0, w1, color, a=0.25):
    """路灯往下打的一束光。"""
    h = int(y1 - y0)
    if h <= 2:
        return
    w = int(max(w0, w1) * 2 + 40)
    m = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(m)
    for k in range(12):
        f0 = k / 12
        yy0, yy1 = f0 * h, (k + 1) / 12 * h
        hw0, hw1 = w0 + (w1 - w0) * f0, w0 + (w1 - w0) * (k + 1) / 12
        md.polygon([(w / 2 - hw0, yy0), (w / 2 + hw0, yy0), (w / 2 + hw1, yy1), (w / 2 - hw1, yy1)], fill=int(255 * a * (1 - 0.7 * f0)))
    m = m.filter(ImageFilter.GaussianBlur(10))
    img.paste(Image.new(img.mode, m.size, tuple(color) + ((255,) if img.mode == 'RGBA' else ())), (int(x - w / 2), int(y0)), m)


def stars(d, seed, n, box, big=0.08):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if rng.random() < big:
            T.sparkle(d, x, y, rng.uniform(4, 8), (255, 250, 220), int(rng.uniform(150, 255)))
        else:
            r = float(rng.choice([0.8, 1.0, 1.3, 1.7]))
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(rng.uniform(90, 240))))


def milky(img, seed, box):
    rng = np.random.default_rng(seed)
    x0, y0, x1, y1 = box
    m = Image.new('L', img.size, 0)
    md = ImageDraw.Draw(m)
    for k in range(40):
        u = k / 39
        x = x0 + (x1 - x0) * u
        y = y1 + (y0 - y1) * u + rng.uniform(-30, 30)
        r = rng.uniform(40, 90)
        md.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=int(rng.uniform(30, 70)))
    m = m.filter(ImageFilter.GaussianBlur(30))
    img.paste(Image.new(img.mode, img.size, (170, 150, 230) + ((255,) if img.mode == 'RGBA' else ())), (0, 0), m)
    d = nd(img)
    for _ in range(160):
        u = rng.random()
        x = x0 + (x1 - x0) * u + rng.normal(0, 30)
        y = y1 + (y0 - y1) * u + rng.normal(0, 30)
        r = rng.uniform(0.6, 1.4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(rng.uniform(80, 200))))


def moon(img, x, y, r):
    glow(img, x, y, r * 2.8, (120, 140, 220), 0.4)
    glow(img, x, y, r * 1.6, (220, 220, 255), 0.35)
    d = nd(img)
    d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 244, 220, 255))
    for dx, dy, rr in ((-0.4, -0.3, 0.2), (0.25, 0.25, 0.16), (0.3, -0.35, 0.1), (-0.15, 0.4, 0.12)):
        d.ellipse((x + dx * r - rr * r, y + dy * r - rr * r, x + dx * r + rr * r, y + dy * r + rr * r), fill=(232, 226, 204, 255))


def cloud(d, x, y, s, col, a=60):
    for dx, dy, r in ((-0.6, 0.1, 0.4), (-0.2, -0.15, 0.5), (0.3, -0.05, 0.45), (0.7, 0.12, 0.35), (0.0, 0.2, 0.45)):
        d.ellipse((x + (dx - r) * s, y + (dy - r * 0.6) * s, x + (dx + r) * s, y + (dy + r * 0.6) * s), fill=tuple(col) + (a,))


WIN_LIT = [(255, 214, 140), (255, 232, 180), (255, 196, 120), (190, 220, 255), (255, 170, 150)]


def windows(d, rng, x0, y0, x1, y1, cols, rows, lit=0.5, dark=(34, 40, 66), people=0.15, frame=None, ww=None, wh=None):
    cw, chh = (x1 - x0) / cols, (y1 - y0) / rows
    ww = ww or cw * 0.62
    wh = wh or chh * 0.62
    spots = []
    for i in range(cols):
        for j in range(rows):
            cx, cy = x0 + (i + 0.5) * cw, y0 + (j + 0.5) * chh
            box = (cx - ww / 2, cy - wh / 2, cx + ww / 2, cy + wh / 2)
            if rng.random() < lit:
                col = WIN_LIT[int(rng.integers(0, len(WIN_LIT)))]
                d.rectangle(box, fill=col + (255,))
                if rng.random() < 0.5:
                    d.rectangle((box[0], box[1], box[0] + ww * 0.3, box[3]), fill=T.dk(col, 0.8) + (255,))
                if rng.random() < people:
                    px = cx + rng.uniform(-ww * 0.2, ww * 0.2)
                    d.ellipse((px - ww * 0.12, box[3] - wh * 0.75, px + ww * 0.12, box[3] - wh * 0.45), fill=T.dk(col, 0.45) + (255,))
                    d.rectangle((px - ww * 0.2, box[3] - wh * 0.45, px + ww * 0.2, box[3]), fill=T.dk(col, 0.45) + (255,))
                spots.append((cx, cy, True, box))
            else:
                d.rectangle(box, fill=tuple(dark) + (255,))
                spots.append((cx, cy, False, box))
            if frame:
                d.rectangle(box, outline=tuple(frame) + (255,), width=2)
                d.line(((cx, box[1]), (cx, box[3])), fill=tuple(frame) + (255,), width=2)
    return spots


def dorm_building(d, rng, x, base, w, h, body=(46, 52, 84), lit=0.5, label=None, roof=(36, 40, 66)):
    d.rectangle((x, base - h, x + w, base), fill=tuple(body) + (255,))
    d.rectangle((x - 6, base - h - 10, x + w + 6, base - h), fill=tuple(roof) + (255,))
    rows = max(2, int(h // 46))
    cols = max(2, int(w // 40))
    spots = windows(d, rng, x + 10, base - h + 12, x + w - 10, base - 30, cols, rows, lit, frame=T.dk(body, 0.7))
    for j in range(rows):
        y = base - h + 12 + (j + 1) * (h - 42) / rows - 4
        d.rectangle((x + 4, y, x + w - 4, y + 4), fill=T.lt(body, 0.12) + (255,))
    if label:
        d.rounded_rectangle((x + w / 2 - 46, base - h + 4, x + w / 2 + 46, base - h + 30), radius=6, fill=(230, 220, 190, 255))
        d.text((x + w / 2, base - h + 17), label, font=F('Black', 18), fill=(70, 50, 40, 255), anchor='mm')
    return spots


def tree(d, x, base, s, dark=(26, 58, 54), light=(46, 92, 76), trunk=(58, 42, 36)):
    d.polygon([(x - s * 0.07, base), (x + s * 0.07, base), (x + s * 0.04, base - s * 0.9), (x - s * 0.04, base - s * 0.9)], fill=trunk + (255,))
    for dx, dy, r in ((-0.34, -0.95, 0.4), (0.3, -1.0, 0.42), (0.0, -1.32, 0.45), (-0.05, -0.82, 0.36), (0.45, -0.75, 0.3), (-0.5, -0.72, 0.3)):
        d.ellipse((x + (dx - r) * s, base + (dy - r) * s, x + (dx + r) * s, base + (dy + r) * s), fill=dark + (255,))
    for dx, dy, r in ((-0.2, -1.32, 0.25), (0.25, -1.12, 0.22), (-0.45, -1.0, 0.18)):
        d.ellipse((x + (dx - r) * s, base + (dy - r) * s, x + (dx + r) * s, base + (dy + r) * s), fill=light + (255,))


def bush(d, x, base, s, dark=(28, 66, 56), light=(52, 104, 82)):
    for dx, r in ((-0.6, 0.45), (0.0, 0.6), (0.6, 0.45)):
        d.ellipse((x + (dx - r) * s, base - 2 * r * s, x + (dx + r) * s, base), fill=dark + (255,))
    for dx, r in ((-0.3, 0.22), (0.25, 0.25)):
        d.ellipse((x + (dx - r) * s, base - 1.1 * s - r * s, x + (dx + r) * s, base - 1.1 * s + r * s * 0.8), fill=light + (255,))


def willow(d, x, base, s):
    d.polygon([(x - s * 0.06, base), (x + s * 0.06, base), (x + s * 0.03, base - s), (x - s * 0.03, base - s)], fill=(44, 34, 30, 255))
    for k in range(18):
        a = -1.0 + k / 17 * 2.0
        x0 = x + a * s * 0.5
        y0 = base - s * (1.0 - 0.35 * abs(a))
        d.line(((x + a * s * 0.08, base - s * 1.05), (x0, y0), (x0 + a * s * 0.06, base - s * 0.2)), fill=(34, 74, 62, 255), width=int(s * 0.045))
        d.line(((x0, y0), (x0 + a * s * 0.05, base - s * 0.35)), fill=(56, 104, 82, 255), width=int(s * 0.02))


def lamp(img, x, base, hgt, on=True, r=70, cone_w=150, color=(255, 206, 130), style='round'):
    d = nd(img)
    d.rectangle((x - 4, base - hgt, x + 4, base), fill=(44, 48, 62, 255))
    d.rectangle((x - 10, base - 10, x + 10, base), fill=(36, 40, 52, 255))
    if style == 'round':
        d.rounded_rectangle((x - 16, base - hgt - 12, x + 16, base - hgt + 6), radius=6, fill=(62, 66, 82, 255))
    else:
        d.line(((x, base - hgt), (x + 26, base - hgt - 8)), fill=(44, 48, 62, 255), width=6)
    if on:
        lx = x if style == 'round' else x + 26
        cone(img, lx, base - hgt + 6, base + 10, 14, cone_w, color, 0.22)
        glow(img, lx, base - hgt, r, color, 0.5)
        nd(img).ellipse((lx - 9, base - hgt - 4, lx + 9, base - hgt + 10), fill=(255, 244, 210, 255))


def railing(d, x0, x1, y, h, col=(150, 158, 178), step=36):
    d.rectangle((x0, y, x1, y + 8), fill=tuple(col) + (255,))
    d.rectangle((x0, y + h, x1, y + h + 6), fill=T.dk(col, 0.85) + (255,))
    for x in range(int(x0), int(x1), step):
        d.rectangle((x, y + 8, x + 5, y + h), fill=T.dk(col, 0.8) + (255,))


def bench(d, x, y, s=1.0, col=(150, 100, 66)):
    for k in range(3):
        d.rounded_rectangle((x - 150 * s, y - 64 * s + k * 16 * s, x + 150 * s, y - 52 * s + k * 16 * s), radius=4, fill=T.dk(col, 0.9 - k * 0.05) + (255,))
    d.rounded_rectangle((x - 160 * s, y - 10 * s, x + 160 * s, y + 4 * s), radius=4, fill=col + (255,), outline=INK, width=2)
    for sx in (-1, 1):
        d.rectangle((x + sx * 135 * s - 6 * s, y, x + sx * 135 * s + 6 * s, y + 46 * s), fill=(50, 52, 60, 255))


def ebike(d, x, y, s=1.0, col=(80, 170, 220), box=(250, 210, 60)):
    for wx in (-48, 48):
        d.ellipse((x + (wx - 22) * s, y - 22 * s, x + (wx + 22) * s, y + 22 * s), fill=(30, 30, 36, 255))
        d.ellipse((x + (wx - 10) * s, y - 10 * s, x + (wx + 10) * s, y + 10 * s), fill=(120, 120, 130, 255))
    d.polygon([(x - 54 * s, y - 14 * s), (x + 40 * s, y - 14 * s), (x + 58 * s, y - 60 * s), (x + 44 * s, y - 64 * s), (x + 20 * s, y - 30 * s),
               (x - 40 * s, y - 34 * s)], fill=tuple(col) + (255,))
    d.rounded_rectangle((x - 66 * s, y - 86 * s, x - 18 * s, y - 36 * s), radius=6 * s, fill=tuple(box) + (255,), outline=INK, width=2)
    d.line(((x + 50 * s, y - 64 * s), (x + 34 * s, y - 70 * s)), fill=(30, 30, 36, 255), width=int(5 * s))


def bike(d, x, y, s=1.0, col=(220, 80, 80)):
    for wx in (-34, 34):
        d.ellipse((x + (wx - 22) * s, y - 22 * s, x + (wx + 22) * s, y + 22 * s), outline=(30, 30, 36, 255), width=int(4 * s))
    d.line(((x - 34 * s, y), (x - 6 * s, y - 30 * s), (x + 34 * s, y), (x + 10 * s, y - 30 * s), (x - 6 * s, y - 30 * s)), fill=tuple(col) + (255,),
           width=int(4 * s), joint='curve')
    d.line(((x + 10 * s, y - 30 * s), (x + 14 * s, y - 42 * s)), fill=(30, 30, 36, 255), width=int(4 * s))


def vending(img, x, base, s=1.0):
    d = nd(img)
    w, h = 110 * s, 220 * s
    d.rounded_rectangle((x - w / 2, base - h, x + w / 2, base), radius=8 * s, fill=(210, 60, 70, 255), outline=INK, width=3)
    d.rectangle((x - w / 2 + 10 * s, base - h + 14 * s, x + w / 2 - 10 * s, base - h + 130 * s), fill=(220, 240, 255, 255))
    rng = np.random.default_rng(5)
    for j in range(4):
        for i in range(4):
            cx = x - w / 2 + 22 * s + i * 22 * s
            cy = base - h + 30 * s + j * 28 * s
            col = [(80, 160, 230), (240, 200, 60), (90, 200, 120), (240, 120, 160)][int(rng.integers(0, 4))]
            d.rounded_rectangle((cx - 6 * s, cy - 10 * s, cx + 6 * s, cy + 10 * s), radius=3, fill=col + (255,))
    d.rectangle((x - w / 2 + 14 * s, base - 60 * s, x + w / 2 - 14 * s, base - 30 * s), fill=(40, 40, 46, 255))
    glow(img, x, base - h + 70 * s, 110 * s, (200, 230, 255), 0.4)


def notice_board(d, x, y, w, h, seed=3):
    d.rectangle((x, y, x + w, y + h), fill=(150, 110, 70, 255), outline=INK, width=3)
    d.rectangle((x + 8, y + 8, x + w - 8, y + h - 8), fill=(200, 170, 120, 255))
    rng = np.random.default_rng(seed)
    for _ in range(6):
        px, py = rng.uniform(x + 14, x + w - 60), rng.uniform(y + 14, y + h - 60)
        col = [(250, 250, 240), (255, 230, 120), (160, 220, 255), (255, 180, 190)][int(rng.integers(0, 4))]
        d.rectangle((px, py, px + 46, py + 40), fill=col + (255,))
        for k in range(3):
            d.line(((px + 6, py + 10 + k * 9), (px + 38, py + 10 + k * 9)), fill=(150, 150, 150, 255), width=2)
        d.ellipse((px + 20, py - 4, px + 26, py + 2), fill=(220, 40, 50, 255))


def poster(d, x, y, w, h, c1, c2, kind=0):
    d.rectangle((x, y, x + w, y + h), fill=tuple(c1) + (255,), outline=INK, width=3)
    if kind == 0:
        T.star(d, x + w / 2, y + h * 0.42, w * 0.3, tuple(c2) + (255,))
        d.rectangle((x + 10, y + h - 30, x + w - 10, y + h - 16), fill=tuple(c2) + (255,))
    elif kind == 1:
        d.ellipse((x + w * 0.25, y + h * 0.15, x + w * 0.75, y + h * 0.5), fill=tuple(c2) + (255,))
        d.polygon([(x + w * 0.15, y + h * 0.9), (x + w * 0.5, y + h * 0.45), (x + w * 0.85, y + h * 0.9)], fill=tuple(c2) + (255,))
    else:
        for k in range(4):
            d.line(((x + 10, y + 16 + k * h * 0.2), (x + w - 10, y + 6 + k * h * 0.2)), fill=tuple(c2) + (255,), width=6)


# ---------------------------------------------------------------- 特效
@lru_cache(maxsize=None)
def vignette_mask(strength=0.55):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    m = np.clip((d - 0.55) / 0.6, 0, 1) ** 1.4 * strength
    return Image.fromarray((m * 255).astype(np.uint8), 'L')


def vignette(img, strength=0.55, color=(0, 0, 0)):
    img.paste(Image.new('RGB', (W, H), color), (0, 0), vignette_mask(strength))
    return img


def radial_lines(img, cx, cy, color=(255, 255, 255), n=70, inner=260, a=200, seed=0, t=0.0):
    """漫画里的集中线。"""
    d = nd(img)
    rng = np.random.default_rng(seed + int(t * 12))
    R = 1500
    for _ in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        r0 = inner * rng.uniform(0.8, 1.3)
        w = rng.uniform(0.006, 0.02)
        p0 = (cx + math.cos(ang) * r0, cy + math.sin(ang) * r0 * 0.75)
        p1 = (cx + math.cos(ang - w) * R, cy + math.sin(ang - w) * R)
        p2 = (cx + math.cos(ang + w) * R, cy + math.sin(ang + w) * R)
        d.polygon([p0, p1, p2], fill=tuple(color) + (int(a * rng.uniform(0.5, 1.0)),))


def sunburst(img, cx, cy, c1, c2, n=18, rot=0.0):
    d = nd(img)
    for k in range(n):
        a0 = rot + k * 2 * math.pi / n
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + 1600 * math.cos(a0), cy + 1600 * math.sin(a0)), (cx + 1600 * math.cos(a1), cy + 1600 * math.sin(a1))],
                  fill=tuple(c2) + (255,))


def confetti(d, t, seed=1, n=60, box=(0, 0, W, H), speed=160):
    rng = np.random.default_rng(seed)
    cols = [(255, 90, 100), (255, 210, 60), (80, 200, 255), (130, 230, 140), (200, 140, 255), (255, 255, 255)]
    for _ in range(n):
        x0, y0 = rng.uniform(box[0], box[2]), rng.uniform(box[1] - 300, box[3])
        sp = rng.uniform(0.6, 1.4) * speed
        y = (y0 + t * sp - box[1]) % (box[3] - box[1] + 60) + box[1] - 30
        x = x0 + math.sin(t * rng.uniform(2, 5) + x0) * 20
        a = t * rng.uniform(3, 8)
        w, h = rng.uniform(6, 12), rng.uniform(3, 6)
        c, s = math.cos(a), math.sin(a)
        pts = [(x + c * dx - s * dy, y + s * dx + c * dy) for dx, dy in ((-w, -h), (w, -h), (w, h), (-w, h))]
        d.polygon(pts, fill=cols[int(rng.integers(0, len(cols)))] + (255,))


def speed_lines(d, t, seed=4, n=26, color=(255, 255, 255), dirx=-1, box=(0, 60, W, H - 60), a=(70, 170)):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        y = rng.uniform(box[1], box[3])
        x = (rng.uniform(0, W) + dirx * t * 2600) % (W + 300) - 150
        ln = rng.uniform(80, 280)
        d.line((x, y, x - dirx * ln, y), fill=tuple(color) + (int(rng.uniform(*a)),), width=int(rng.uniform(2, 6)))


def dust(d, x, y, age, n=6, seed=0, col=(220, 210, 200), spread=1.0):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        dx = rng.uniform(-40, 40) * spread - age * 60 * spread
        dy = -rng.uniform(0, 26) - age * 20
        r = (14 + age * 50) * rng.uniform(0.6, 1.2)
        a = int(170 * clamp(1 - age / 0.8))
        if a > 0:
            d.ellipse((x + dx - r, y + dy - r, x + dx + r, y + dy + r), fill=tuple(col) + (a,))


def fireflies(d, t, seed, n, box, col=(220, 255, 140)):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x0, y0 = rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3])
        ph = rng.uniform(0, 6.28)
        x = x0 + math.sin(t * 0.7 + ph) * 30
        y = y0 + math.cos(t * 0.9 + ph) * 18
        a = int(140 + 110 * math.sin(t * 3 + ph))
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=tuple(col) + (int(a * 0.3),))
        d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=tuple(col) + (a,))


def leaves(d, t, seed, n, box, wind=1.0, col=(210, 160, 70)):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x0, y0 = rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3])
        sp = rng.uniform(40, 90)
        x = (x0 + t * sp * wind * 3) % (box[2] - box[0] + 80) + box[0] - 40
        y = (y0 + t * sp) % (box[3] - box[1] + 60) + box[1] - 30
        a = t * rng.uniform(2, 5) + x0
        r = rng.uniform(5, 9)
        d.ellipse((x - r, y - r * 0.5 * abs(math.cos(a)) - 1, x + r, y + r * 0.5 * abs(math.cos(a)) + 1), fill=tuple(col) + (230,))


def meteor(img, x, y, length, ang, a=1.0):
    m = Image.new('L', img.size, 0)
    md = ImageDraw.Draw(m)
    for k in range(10):
        u0, u1 = k / 10, (k + 1) / 10
        p0 = (x - math.cos(ang) * length * u0, y - math.sin(ang) * length * u0)
        p1 = (x - math.cos(ang) * length * u1, y - math.sin(ang) * length * u1)
        md.line((p0, p1), fill=int(255 * a * (1 - u0)), width=max(1, int(5 * (1 - u0))))
    img.paste(Image.new(img.mode, img.size, (255, 250, 220) + ((255,) if img.mode == 'RGBA' else ())), (0, 0), m)
    glow(img, x, y, 14, (255, 250, 220), 0.8 * a)


def puff(d, x, y, r, a, col=(235, 90, 60)):
    if a <= 0:
        return
    for k, (dx, dy, rr, aa) in enumerate(((0, 0, 1.0, 0.3), (-0.45, 0.2, 0.7, 0.32), (0.5, 0.15, 0.65, 0.32), (0.1, -0.35, 0.6, 0.34))):
        c = mixc(col, (230, 200, 200), 0.25 * k / 3)
        d.ellipse((x + dx * r - rr * r, y + dy * r - rr * r, x + dx * r + rr * r, y + dy * r + rr * r), fill=c + (int(a * aa),))


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


def grade(img, mul=(1.0, 1.0, 1.0), add=(0, 0, 0)):
    arr = np.asarray(img).astype(np.float32)
    arr = arr * np.array(mul, np.float32) + np.array(add, np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')


def caption(d, text, x, y, size, t, t0, color=(255, 230, 90), stroke=(20, 14, 10), weight='Black', anchor='mm', pop=True, shadow=True):
    u = (t - t0) / 0.22
    if u < 0:
        return
    sc = ease_back(u) if (pop and u < 1) else 1.0
    a = int(255 * clamp(u * 3))
    f = F(weight, size * max(0.3, sc))
    if shadow:
        d.text((x + size * 0.06, y + size * 0.08), text, font=f, fill=(0, 0, 0, int(a * 0.5)), anchor=anchor,
               stroke_width=max(2, int(size * 0.1)), stroke_fill=(0, 0, 0, int(a * 0.5)))
    d.text((x, y), text, font=f, fill=tuple(color) + (a,), anchor=anchor, stroke_width=max(2, int(size * 0.1)), stroke_fill=tuple(stroke) + (a,))


def bubble(d, x, y, text, size=30, t=None, t0=None, tail=(0, 40), fill=(255, 255, 255), col=INK):
    sc = 1.0
    if t is not None:
        u = (t - t0) / 0.2
        if u < 0:
            return
        sc = ease_back(u) if u < 1 else 1.0
    f = F('Black', max(8, int(size * sc)))
    w = f.getlength(text) + size * 1.2 * sc
    h = size * 1.7 * sc
    d.polygon([(x - 14 * sc, y + h / 2 - 4), (x + 14 * sc, y + h / 2 - 4), (x + tail[0], y + h / 2 + tail[1] * sc)], fill=tuple(fill) + (255,), outline=tuple(col) + (255,))
    d.rounded_rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), radius=h * 0.45, fill=tuple(fill) + (255,), outline=tuple(col) + (255,), width=3)
    d.polygon([(x - 12 * sc, y + h / 2 - 5), (x + 12 * sc, y + h / 2 - 5), (x + tail[0] * 0.8, y + h / 2 + tail[1] * sc * 0.8)], fill=tuple(fill) + (255,))
    d.text((x, y), text, font=f, fill=tuple(col) + (255,), anchor='mm')


def tag(d, x, y, text, color=(255, 255, 255), bg=(10, 14, 20), size=20, alpha=1.0):
    f = F('Bold', size)
    w = f.getlength(text) + 22
    A = int(230 * alpha)
    d.rounded_rectangle((x - w / 2, y - size - 10, x + w / 2, y + 6), radius=6, fill=tuple(bg) + (A,), outline=tuple(color) + (A,), width=2)
    d.polygon([(x - 8, y + 6), (x + 8, y + 6), (x, y + 16)], fill=tuple(bg) + (A,))
    d.text((x, y - size / 2 - 2), text, font=f, fill=tuple(color) + (int(255 * alpha),), anchor='mm')


# ---------------------------------------------------------------- 背景
NIGHT = [(0.0, (16, 18, 46)), (0.55, (44, 36, 86)), (1.0, (86, 56, 110))]


@lru_cache(maxsize=None)
def bg_dorm():
    img = vgrad(W, H, [(0, (66, 70, 98)), (0.75, (52, 54, 78)), (1.0, (40, 40, 58))])
    d = nd(img)
    # 地板
    d.rectangle((0, 585, W, H), fill=(92, 72, 62, 255))
    for k in range(9):
        y = 585 + k * 16 + k * k * 1.2
        d.line(((0, y), (W, y)), fill=(76, 58, 50, 255), width=2)
    for x in range(-200, W + 200, 120):
        d.line(((640 + (x - 640) * 0.55, 585), (x, H)), fill=(80, 62, 54, 255), width=2)
    d.rectangle((0, 578, W, 590), fill=(120, 96, 84, 255))
    # 窗户
    wx0, wy0, wx1, wy1 = 470, 70, 810, 330
    sky = vgrad(wx1 - wx0, wy1 - wy0, [(0, (16, 18, 50)), (1.0, (70, 46, 100))])
    img.paste(sky, (wx0, wy0))
    d = nd(img)
    stars(d, 7, 40, (wx0, wy0, wx1, wy0 + 140))
    moon(img, 740, 120, 20)
    d = nd(img)
    rng = np.random.default_rng(3)
    for k, (bx, bw, bh) in enumerate(((480, 90, 120), (580, 70, 160), (660, 110, 100), (760, 60, 140))):
        dorm_building(d, rng, bx, wy1, bw, bh, body=(36, 40, 70), lit=0.45)
    tree(d, 520, wy1 + 10, 70)
    d.rectangle((wx0 - 12, wy0 - 12, wx1 + 12, wy1 + 12), outline=(226, 226, 232, 255), width=14)
    d.line(((640, wy0), (640, wy1)), fill=(226, 226, 232, 255), width=8)
    d.rectangle((wx0 - 30, wy1 + 12, wx1 + 30, wy1 + 28), fill=(210, 210, 216, 255))
    # 窗帘
    for s, x in ((-1, wx0 - 30), (1, wx1 + 30)):
        pts = [(x, wy0 - 30), (x - s * 70, wy0 - 30), (x - s * 52, wy1 + 60), (x + s * 4, wy1 + 60)]
        d.polygon(pts, fill=(70, 150, 160, 255), outline=INK)
        for k in range(1, 4):
            xx = x - s * 70 * k / 4
            d.line(((xx, wy0 - 28), (xx + s * 4, wy1 + 58)), fill=(52, 120, 130, 255), width=3)
    # 彩灯
    pts = []
    for k in range(15):
        x = wx0 - 40 + k * (wx1 - wx0 + 80) / 14
        y = wy0 - 34 + 16 * math.sin(k / 14 * math.pi)
        pts.append((x, y))
    d.line(pts, fill=(40, 40, 50, 255), width=2)
    bulbs = []
    for k, (x, y) in enumerate(pts):
        col = [(255, 200, 90), (255, 120, 150), (120, 220, 255), (170, 255, 140)][k % 4]
        bulbs.append((x, y + 8, col))
    for x, y, col in bulbs:
        glow(img, x, y, 16, col, 0.6)
    d = nd(img)
    for x, y, col in bulbs:
        d.ellipse((x - 5, y - 5, x + 5, y + 7), fill=col + (255,))
    # 墙上：日历、钟、海报
    d.rectangle((392, 96, 452, 176), fill=(250, 250, 246, 255), outline=INK, width=3)
    d.rectangle((392, 96, 452, 118), fill=(226, 58, 66, 255))
    d.text((422, 107), '11月', font=F('Bold', 14), fill=(255, 255, 255, 255), anchor='mm')
    for j in range(3):
        for i in range(4):
            d.rectangle((398 + i * 13, 124 + j * 15, 406 + i * 13, 132 + j * 15), fill=(180, 180, 186, 255))
    d.ellipse((396 + 2 * 13, 120 + 1 * 15, 412 + 2 * 13, 138 + 1 * 15), outline=(226, 40, 50, 255), width=3)
    d.text((422, 165), '周四', font=F('Black', 14), fill=(226, 40, 50, 255), anchor='mm')
    d.ellipse((870, 70, 950, 150), fill=(250, 250, 246, 255), outline=INK, width=4)
    for k in range(12):
        a = k * math.pi / 6
        d.line(((910 + 30 * math.cos(a), 110 + 30 * math.sin(a)), (910 + 34 * math.cos(a), 110 + 34 * math.sin(a))), fill=INK, width=2)
    d.line(((910, 110), (910 + 22 * math.cos(math.radians(-90 + 312)), 110 + 22 * math.sin(math.radians(-90 + 312)))), fill=INK, width=4)
    d.line(((910, 110), (910 + 16 * math.cos(math.radians(-90 + 326)), 110 + 16 * math.sin(math.radians(-90 + 326)))), fill=INK, width=5)
    poster(d, 980, 60, 90, 120, (40, 30, 80), (255, 200, 60), 0)
    poster(d, 1090, 76, 80, 104, (230, 90, 110), (255, 240, 220), 1)
    # 左边：上床下桌
    d.rectangle((20, 70, 440, 200), fill=(80, 84, 110, 255))
    d.rectangle((20, 168, 440, 200), fill=(150, 158, 176, 255), outline=INK, width=3)
    d.rounded_rectangle((40, 120, 420, 172), radius=16, fill=(160, 110, 200, 255), outline=INK, width=3)
    d.rounded_rectangle((330, 100, 410, 140), radius=14, fill=(250, 246, 236, 255), outline=INK, width=3)
    for x in (24, 434):
        d.rectangle((x - 4, 60, x + 6, 585), fill=(150, 158, 176, 255), outline=INK, width=2)
    for y in range(70, 170, 24):
        d.line(((20, y), (440, y)), fill=(150, 158, 176, 255), width=3)
    shelf_y = 250
    d.rectangle((40, shelf_y, 420, shelf_y + 10), fill=(150, 110, 80, 255), outline=INK, width=2)
    x = 50
    rng = np.random.default_rng(11)
    while x < 260:
        bw, bh = rng.uniform(12, 22), rng.uniform(40, 62)
        col = [(220, 90, 90), (90, 150, 220), (240, 200, 80), (120, 200, 140), (200, 140, 220)][int(rng.integers(0, 5))]
        d.rectangle((x, shelf_y - bh, x + bw, shelf_y), fill=col + (255,), outline=INK, width=2)
        x += bw + 2
    # 手办
    T.ocircle(d, (330, shelf_y - 44), 14, (250, 210, 180), 2)
    d.polygon([(316, shelf_y), (344, shelf_y), (338, shelf_y - 30), (322, shelf_y - 30)], fill=(90, 120, 220, 255), outline=INK)
    d.polygon([(318, shelf_y - 58), (330, shelf_y - 72), (342, shelf_y - 58)], fill=(255, 200, 60, 255))
    # 白板
    d.rectangle((60, 280, 300, 360), fill=(246, 248, 250, 255), outline=(150, 156, 170, 255), width=5)
    d.text((180, 306), '每晚十点·四排', font=F('Black', 22), fill=(40, 90, 200, 255), anchor='mm')
    d.text((180, 340), '炸鸡到了再开！', font=F('Bold', 18), fill=(220, 60, 70, 255), anchor='mm')
    for k, (sx, col) in enumerate(((320, (255, 230, 120)), (360, (160, 220, 255)), (330, (255, 180, 200)))):
        d.rectangle((sx, 290 + k * 26, sx + 34, 320 + k * 26), fill=col + (255,))
    # 桌子、显示器、台灯
    d.rectangle((30, 455, 430, 472), fill=(170, 130, 96, 255), outline=INK, width=3)
    d.rectangle((40, 472, 52, 585), fill=(120, 92, 70, 255))
    d.rectangle((410, 472, 422, 585), fill=(120, 92, 70, 255))
    d.rounded_rectangle((130, 350, 330, 450), radius=6, fill=(20, 22, 30, 255), outline=INK, width=3)
    scr = vgrad(186, 86, [(0, (60, 40, 120)), (1, (220, 90, 140))])
    img.paste(scr, (137, 357))
    d = nd(img)
    d.polygon([(150, 440), (200, 400), (240, 420), (300, 380), (323, 400), (323, 443), (150, 443)], fill=(40, 30, 70, 255))
    T.star(d, 270, 380, 12, (255, 230, 120, 255))
    d.rectangle((222, 450, 238, 456), fill=(30, 30, 36, 255))
    d.rounded_rectangle((150, 452, 310, 462), radius=3, fill=(30, 30, 36, 255))
    for k in range(10):
        d.rectangle((156 + k * 15, 454, 166 + k * 15, 459), fill=[(255, 80, 120), (255, 200, 60), (80, 220, 255), (140, 255, 120)][k % 4] + (255,))
    glow(img, 230, 400, 150, (150, 90, 220), 0.35)
    d = nd(img)
    d.line(((380, 455), (360, 400), (390, 380)), fill=(60, 60, 70, 255), width=5)
    d.polygon([(380, 372), (410, 372), (420, 392), (370, 392)], fill=(250, 210, 120, 255), outline=INK)
    glow(img, 395, 400, 90, (255, 200, 120), 0.45)
    cone(img, 395, 392, 455, 10, 60, (255, 210, 140), 0.25)
    d = nd(img)
    d.rounded_rectangle((60, 420, 110, 455), radius=6, fill=(255, 240, 220, 255), outline=INK, width=2)
    d.rectangle((60, 420, 110, 430), fill=(230, 70, 60, 255))
    # 右边：另一个上床下桌
    d.rectangle((840, 200, 1270, 300), fill=(84, 88, 114, 255))
    d.rectangle((840, 270, 1270, 300), fill=(150, 158, 176, 255), outline=INK, width=3)
    for x in (846, 1262):
        d.rectangle((x - 5, 190, x + 5, 585), fill=(150, 158, 176, 255), outline=INK, width=2)
    d.rectangle((840, 300, 940, 470), fill=(90, 130, 200, 255), outline=INK, width=2)
    for k in range(1, 4):
        d.line(((840 + k * 25, 300), (840 + k * 25, 470)), fill=(70, 106, 170, 255), width=3)
    d.rectangle((940, 520, 1260, 536), fill=(170, 130, 96, 255), outline=INK, width=3)
    d.rounded_rectangle((1040, 420, 1210, 516), radius=6, fill=(20, 22, 30, 255), outline=INK, width=3)
    scr = vgrad(156, 82, [(0, (30, 80, 150)), (1, (60, 200, 220))])
    img.paste(scr, (1047, 427))
    d = nd(img)
    for k in range(5):
        d.rectangle((1060 + k * 28, 490 - k * 10, 1076 + k * 28, 505), fill=(255, 255, 255, 140))
    glow(img, 1125, 470, 130, (80, 170, 255), 0.3)
    d = nd(img)
    d.rectangle((1220, 320, 1262, 520), fill=(230, 230, 220, 255), outline=INK, width=2)
    # 地上的东西
    T.ocircle(d, (520, 640), 30, (230, 120, 50), 3)
    d.arc((490, 610, 550, 670), 200, 340, fill=INK, width=3)
    d.line(((520, 610), (520, 670)), fill=INK, width=3)
    d.rounded_rectangle((900, 560, 960, 640), radius=8, fill=(90, 96, 110, 255), outline=INK, width=3)
    d.polygon([(912, 548), (948, 548), (944, 566), (916, 566)], fill=(250, 240, 220, 255), outline=INK)
    d.rectangle((914, 548, 946, 556), fill=(230, 70, 60, 255))
    for x, col in ((1000, (240, 120, 120)), (1040, (240, 120, 120))):
        d.ellipse((x - 22, 668, x + 22, 684), fill=col + (255,), outline=INK, width=2)
    d.polygon([(700, 640), (760, 630), (770, 660), (706, 668)], fill=(255, 200, 70, 255), outline=INK)
    d.text((736, 650), '薯片', font=F('Black', 14), fill=(200, 60, 40, 255), anchor='mm')
    return vignette(img, 0.5)


@lru_cache(maxsize=None)
def bg_dorm_blur(k=8):
    return Image.eval(bg_dorm().filter(ImageFilter.GaussianBlur(k)), lambda v: int(v * 0.72))


@lru_cache(maxsize=None)
def bg_campus():
    """惊动全校：俯瞰校园，返回 (图, 窗户位置)。"""
    img = vgrad(W, H, NIGHT)
    d = nd(img)
    stars(d, 21, 160, (0, 0, W, 300))
    milky(img, 22, (0, 40, W, 300))
    moon(img, 1110, 110, 40)
    d = nd(img)
    rng = np.random.default_rng(23)
    spots = []
    for k, (x, w, h) in enumerate(((20, 180, 210), (230, 150, 260), (410, 200, 200), (640, 170, 300), (840, 210, 230), (1080, 180, 260))):
        spots += dorm_building(d, rng, x, 560, w, h, body=(40, 46, 82), lit=0.12, label=f'{[3, 5, 6, 8, 7, 9][k]}号楼')
    d.rectangle((0, 560, W, H), fill=(30, 50, 50, 255))
    for x in range(0, W, 110):
        tree(d, x + 30, 600, 70, (22, 50, 46), (40, 80, 66))
    for x in (120, 520, 900):
        lamp(img, x, 690, 150, r=50, cone_w=90)
    return img, spots


@lru_cache(maxsize=None)
def bg_balcony():
    img = vgrad(W, H, [(0, (12, 14, 40)), (0.6, (48, 36, 92)), (1, (96, 60, 120))])
    milky(img, 31, (100, 30, 1200, 330))
    d = nd(img)
    stars(d, 32, 180, (0, 0, W, 420))
    moon(img, 1110, 110, 46)
    d = nd(img)
    for x, y, s in ((200, 150, 120), (700, 90, 160), (980, 220, 110)):
        cloud(d, x, y, s, (150, 130, 200), 40)
    rng = np.random.default_rng(33)
    for x, w, h in ((-20, 200, 160), (200, 160, 210), (380, 220, 150), (640, 160, 230), (820, 240, 170), (1080, 220, 200)):
        dorm_building(d, rng, x, 560, w, h, body=(34, 38, 72), lit=0.38)
    d.rectangle((0, 548, W, 600), fill=(24, 44, 46, 255))
    for x in range(0, W, 90):
        tree(d, x + 20, 580, 60, (20, 44, 42), (36, 70, 60))
    for x in range(60, W, 240):
        glow(img, x, 566, 22, (255, 206, 130), 0.7)
    d = nd(img)
    # 阳台
    d.rectangle((0, 640, W, H), fill=(60, 62, 80, 255))
    d.rectangle((0, 512, W, 528), fill=(196, 204, 220, 255), outline=INK, width=2)
    d.rectangle((0, 528, W, 640), fill=(140, 170, 210, 70))
    for x in range(0, W, 160):
        d.rectangle((x, 528, x + 8, 640), fill=(170, 178, 196, 255))
    d.rectangle((0, 632, W, 644), fill=(160, 168, 186, 255))
    pts = [(x, 520 + 10 * math.sin(x / 60)) for x in range(0, W + 40, 40)]
    for k, (x, y) in enumerate(pts):
        col = [(255, 220, 120), (255, 170, 200), (160, 220, 255)][k % 3]
        glow(img, x, y, 12, col, 0.6)
    d = nd(img)
    for k, (x, y) in enumerate(pts):
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=[(255, 220, 120), (255, 170, 200), (160, 220, 255)][k % 3] + (255,))
    # 晾衣杆
    d.line(((0, 40), (W, 40)), fill=(180, 186, 200, 255), width=6)
    for x, col, kind in ((120, (240, 150, 170), 0), (260, (140, 190, 240), 1), (1040, (250, 240, 220), 0), (1180, (180, 230, 190), 1)):
        d.line(((x, 40), (x, 56)), fill=(200, 200, 210, 255), width=2)
        if kind == 0:
            T.opoly(d, [(x - 48, 58), (x + 48, 58), (x + 64, 88), (x + 40, 96), (x + 38, 150), (x - 38, 150), (x - 40, 96), (x - 64, 88)], col, 2)
        else:
            T.opoly(d, [(x - 40, 58), (x + 40, 58), (x + 36, 140), (x + 6, 140), (x, 100), (x - 6, 140), (x - 36, 140)], col, 2)
    # 花盆
    for x, s in ((60, 1.0), (1220, 1.2)):
        d.polygon([(x - 30 * s, 600), (x + 30 * s, 600), (x + 22 * s, 640), (x - 22 * s, 640)], fill=(190, 110, 80, 255), outline=INK)
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.4
            d.ellipse((x + math.cos(a) * 26 * s - 12 * s, 600 + math.sin(a) * 34 * s - 18 * s, x + math.cos(a) * 26 * s + 12 * s,
                       600 + math.sin(a) * 34 * s + 18 * s), fill=(70, 160, 100, 255), outline=INK)
    return vignette(img, 0.45)


def telescope(d, x, base, aim=-1, s=1.0, tube=1.0):
    top = (x, base - 150 * s)
    for dx in (-48, 0, 44):
        d.line((top, (x + dx * s, base)), fill=INK, width=int(8 * s))
        d.line((top, (x + dx * s, base)), fill=(210, 210, 222, 255), width=int(5 * s))
    x0, y0 = x - aim * 70 * s * tube, base - 122 * s
    x1, y1 = x + aim * 120 * s * tube, base - 122 * s - 74 * s * tube
    d.line(((x0, y0), (x1, y1)), fill=INK, width=int(36 * s))
    d.line(((x0, y0), (x1, y1)), fill=(240, 240, 248, 255), width=int(30 * s))
    d.line(((x1, y1), (x1 + aim * 16 * s, y1 - 9 * s)), fill=(90, 96, 140, 255), width=int(40 * s))
    d.line(((x0, y0), (x0 - aim * 18 * s, y0 + 9 * s)), fill=(70, 70, 84, 255), width=int(16 * s))
    d.line(((x0 + aim * 30 * s, y0 - 18 * s), (x1 - aim * 30 * s, y1 + 14 * s)), fill=(120, 150, 230, 255), width=int(6 * s))
    return (x0 - aim * 24 * s * tube, y0 + 10 * s)


@lru_cache(maxsize=None)
def bg_gate():
    """望远镜里看到的南门（1800×1000），返回 (图, 目标位置)。"""
    w, h = 1800, 1000
    img = vgrad(w, h, [(0, (18, 20, 50)), (0.55, (52, 42, 90)), (1, (60, 58, 76))])
    d = nd(img)
    stars(d, 41, 90, (0, 0, w, 300))
    rng = np.random.default_rng(42)
    for x, bw, bh in ((-20, 260, 200), (260, 200, 260), (1260, 240, 220), (1520, 300, 250)):
        dorm_building(d, rng, x, 560, bw, bh, body=(34, 38, 70), lit=0.35)
    d.rectangle((0, 560, w, h), fill=(66, 68, 80, 255))
    for x in range(0, w, 80):
        d.line(((x, 560), (x - 40, h)), fill=(58, 60, 72, 255), width=2)
    d.rectangle((0, 640, w, 660), fill=(90, 92, 104, 255))
    # 校门
    d.rectangle((560, 300, 620, 640), fill=(180, 170, 160, 255), outline=INK, width=3)
    d.rectangle((1180, 300, 1240, 640), fill=(180, 170, 160, 255), outline=INK, width=3)
    d.rectangle((540, 260, 1260, 312), fill=(150, 60, 56, 255), outline=INK, width=3)
    d.text((900, 286), '南  门', font=F('Black', 40), fill=(255, 220, 140, 255), anchor='mm')
    glow(img, 900, 286, 120, (255, 200, 120), 0.3)
    d = nd(img)
    for x in range(640, 1180, 30):
        d.rectangle((x, 420, x + 6, 600), fill=(90, 94, 110, 255))
    d.rectangle((620, 420, 1180, 428), fill=(100, 104, 120, 255))
    # 外卖架
    sx0, sx1 = 680, 1100
    for y in (470, 530, 590):
        d.rectangle((sx0, y, sx1, y + 8), fill=(200, 206, 220, 255), outline=INK, width=2)
    for x in (sx0, sx1 - 8):
        d.rectangle((x, 440, x + 8, 640), fill=(200, 206, 220, 255), outline=INK, width=2)
    pal = [(90, 150, 220), (240, 200, 80), (246, 246, 240), (170, 120, 80), (120, 200, 140), (210, 140, 200), (250, 150, 80)]
    red = None
    for k, y in enumerate((470, 530, 590)):
        x = sx0 + 18
        while x < sx1 - 52:
            if k == 2 and red is None and x > 860:
                T.draw_bag(d, x + 26, y - 26, 54, 2)
                red = (x + 26, y - 26)
                x += 68
                continue
            bw, bh = rng.uniform(34, 52), rng.uniform(30, 44)
            col = pal[int(rng.integers(0, len(pal)))]
            d.rounded_rectangle((x, y - bh, x + bw, y), radius=5, fill=col + (255,), outline=INK, width=2)
            d.arc((x + bw * 0.25, y - bh - 10, x + bw * 0.75, y - bh + 8), 180, 360, fill=INK, width=2)
            x += bw + rng.uniform(5, 12)
    # 保安亭
    d.rectangle((1290, 430, 1470, 640), fill=(170, 168, 176, 255), outline=INK, width=3)
    d.polygon([(1270, 432), (1490, 432), (1450, 396), (1310, 396)], fill=(140, 60, 60, 255), outline=INK)
    d.rectangle((1310, 460, 1450, 540), fill=(255, 220, 150, 255), outline=INK, width=3)
    glow(img, 1380, 500, 90, (255, 210, 140), 0.35)
    T.put(img, 'guard', dict(view='front', bust=True, arms=((8, 6), {'ik': (0.0, 0.14), 'rel': 'Hc', 'bend': 1})), 1380, 590, 150,
          expr='deadpan', hold='thermos')
    d = nd(img)
    d.rectangle((1310, 540, 1450, 640), fill=(170, 168, 176, 255), outline=INK, width=3)
    # 电动车和小哥
    ebike(d, 420, 640, 1.2)
    T.put_on(img, 'rider', T.stand('side'), 330, 650, 160, facing=-1, expr='happy')
    d = nd(img)
    for x in range(150, 300, 40):
        bike(d, x, 640, 0.9, [(220, 80, 80), (80, 160, 220), (240, 200, 60)][(x // 40) % 3])
    # 长椅和情侣
    bench(d, 1640, 640, 0.6)
    sitp = dict(view='front', arms=((10, 6), (10, 6)), legs=((2, 0), (2, 0)))
    T.put(img, 'girl', sitp, 1610, 610, 140, expr='love')
    T.put(img, 'boy', dict(view='front', arms=((10, 6), {'ik': (0.06, 0.16), 'rel': 'N', 'bend': 1})), 1670, 610, 145, expr='love', hold='cup')
    d = nd(img)
    bench(d, 1640, 640, 0.6)
    # 猫
    d.ellipse((1150, 620, 1190, 646), fill=(240, 160, 80, 255), outline=INK, width=2)
    d.ellipse((1180, 606, 1206, 630), fill=(240, 160, 80, 255), outline=INK, width=2)
    d.polygon([(1184, 610), (1188, 598), (1194, 610)], fill=(240, 160, 80, 255), outline=INK)
    d.polygon([(1196, 610), (1202, 598), (1206, 612)], fill=(240, 160, 80, 255), outline=INK)
    d.line(((1150, 630), (1130, 612)), fill=(240, 160, 80, 255), width=6)
    for x in (120, 520, 1560):
        lamp(img, x, 660, 300, r=70, cone_w=130)
    return img, dict(bag=red, guard=(1380, 470), couple=(1640, 520), rider=(360, 560), cat=(1180, 600))


@lru_cache(maxsize=None)
def street_layers():
    far = vgrad(3800, H, NIGHT)
    d = nd(far)
    stars(d, 51, 200, (0, 0, 3800, 280))
    rng = np.random.default_rng(52)
    x = -20
    while x < 3800:
        bw = rng.uniform(140, 240)
        dorm_building(d, rng, x, 520, bw, rng.uniform(150, 260), body=(36, 40, 74), lit=0.35)
        x += bw + rng.uniform(20, 60)
    mid = Image.new('RGBA', (4400, H), (0, 0, 0, 0))
    d = nd(mid)
    for x in range(0, 4400, 260):
        tree(d, x + 60, 590, 150, (24, 56, 52), (44, 90, 74))
    for x in range(130, 4400, 520):
        lamp(mid, x, 600, 280, r=60, cone_w=120)
    d = nd(mid)
    for x in range(400, 4400, 1100):
        notice_board(d, x, 450, 160, 110, seed=x)
    d.rectangle((0, 590, 4400, H), fill=(70, 72, 86, 255))
    d.rectangle((0, 590, 4400, 604), fill=(110, 112, 126, 255))
    for x in range(0, 4400, 80):
        d.line(((x, 604), (x - 30, H)), fill=(62, 64, 78, 255), width=2)
    near = Image.new('RGBA', (5200, H), (0, 0, 0, 0))
    d = nd(near)
    for x in range(0, 5200, 330):
        bush(d, x + 80, H + 10, 70)
    return far, mid, near


@lru_cache(maxsize=None)
def bg_bench():
    img = vgrad(W, H, NIGHT)
    d = nd(img)
    stars(d, 61, 120, (0, 0, W, 280))
    rng = np.random.default_rng(62)
    for x, bw, bh in ((-30, 240, 200), (260, 200, 250), (900, 220, 220), (1120, 220, 260)):
        dorm_building(d, rng, x, 520, bw, bh, body=(36, 40, 74), lit=0.35)
    for x in (40, 1180):
        tree(d, x, 600, 230)
    tree(d, 300, 590, 170)
    tree(d, 960, 590, 180)
    d.rectangle((0, 590, W, H), fill=(70, 72, 86, 255))
    d.rectangle((0, 590, W, 602), fill=(110, 112, 126, 255))
    lamp(img, 640, 600, 360, r=90, cone_w=240)
    vending(img, 1060, 600, 0.9)
    d = nd(img)
    for x in (180, 1180):
        bush(d, x, 620, 60)
    return img


@lru_cache(maxsize=None)
def bg_slope_top():
    img = vgrad(W, H, [(0, (14, 16, 44)), (0.6, (60, 44, 96)), (1, (120, 70, 110))])
    d = nd(img)
    stars(d, 71, 140, (0, 0, W, 300))
    milky(img, 72, (0, 60, W, 260))
    rng = np.random.default_rng(73)
    d = nd(img)
    for x, bw, bh in ((-20, 200, 120), (200, 160, 160), (380, 220, 110), (900, 180, 150), (1100, 200, 120)):
        dorm_building(d, rng, x, 470, bw, bh, body=(34, 38, 70), lit=0.4)
    glow(img, 640, 240, 300, (255, 210, 150), 0.35)
    d = nd(img)
    d.rectangle((0, 560, W, H), fill=(64, 66, 82, 255))
    d.rectangle((0, 556, W, 566), fill=(110, 112, 126, 255))
    for x in (120, 1170):
        tree(d, x, 566, 220)
    lamp(img, 640, 566, 380, r=140, cone_w=260)
    return img


def god_rays(img, cx, cy, t, col=(255, 230, 180), a=0.18, n=9):
    m = Image.new('L', (W, H), 0)
    md = ImageDraw.Draw(m)
    for k in range(n):
        ang = math.pi / 2 + (k - n / 2) * 0.16 + 0.03 * math.sin(t + k)
        wdt = 0.04 + 0.02 * math.sin(k * 2.3)
        md.polygon([(cx, cy), (cx + 1400 * math.cos(ang - wdt), cy + 1400 * math.sin(ang - wdt)),
                    (cx + 1400 * math.cos(ang + wdt), cy + 1400 * math.sin(ang + wdt))], fill=int(255 * a))
    m = m.filter(ImageFilter.GaussianBlur(14))
    img.paste(Image.new('RGB', (W, H), col), (0, 0), m)


@lru_cache(maxsize=None)
def bg_slope_down():
    img = vgrad(W, H, [(0, (14, 16, 44)), (0.6, (60, 44, 96)), (1, (100, 60, 100))])
    d = nd(img)
    stars(d, 81, 120, (0, 0, W, 240))
    rng = np.random.default_rng(82)
    for x, bw, bh in ((-20, 220, 140), (240, 180, 180), (460, 240, 120), (760, 200, 170), (1000, 260, 130)):
        dorm_building(d, rng, x, 330, bw, bh, body=(34, 38, 70), lit=0.45)
    d.polygon([(0, 250), (W, 590), (W, H), (0, H)], fill=(26, 52, 46, 255))
    d.polygon([(0, 240), (W, 580), (W, 690), (0, 350)], fill=(70, 72, 86, 255))
    d.line(((0, 295), (W, 635)), fill=(230, 220, 170, 120), width=5)
    for k in range(8):
        x = k * 180
        y = 240 + (580 - 240) * x / W
        tree(d, x + 40, y - 6, 90, (22, 50, 46), (40, 80, 66))
    for k in range(6):
        x = 70 + k * 230
        y = 240 + (580 - 240) * x / W
        lamp(img, x, y, 170, r=50, cone_w=70)
    d = nd(img)
    d.rectangle((1150, 520, 1250, 600), fill=(170, 168, 176, 255), outline=INK, width=3)
    d.polygon([(1140, 522), (1260, 522), (1240, 500), (1160, 500)], fill=(140, 60, 60, 255), outline=INK)
    d.rectangle((1166, 536, 1234, 576), fill=(255, 220, 150, 255), outline=INK, width=2)
    return img


@lru_cache(maxsize=None)
def bg_booth():
    img = vgrad(W, H, [(0, (120, 98, 72)), (1, (80, 64, 50))])
    d = nd(img)
    out = vgrad(W - 160, 440, [(0, (16, 18, 46)), (1, (50, 40, 86))])
    img.paste(out, (80, 70))
    d = nd(img)
    stars(d, 91, 50, (80, 70, W - 80, 260))
    rng = np.random.default_rng(92)
    for x, bw, bh in ((100, 200, 150), (340, 160, 190), (860, 220, 160)):
        dorm_building(d, rng, x, 420, bw, bh, body=(34, 38, 70), lit=0.4)
    d.rectangle((80, 420, W - 80, 510), fill=(64, 66, 82, 255))
    lamp(img, 1000, 470, 300, r=70, cone_w=110)
    d = nd(img)
    d.rectangle((60, 50, W - 60, 530), outline=(226, 220, 206, 255), width=26)
    d.line(((640, 50), (640, 530)), fill=(226, 220, 206, 255), width=16)
    d.rectangle((0, 530, W, H), fill=(150, 116, 84, 255), outline=INK, width=3)
    d.rectangle((0, 530, W, 548), fill=(176, 140, 104, 255))
    d.rounded_rectangle((900, 470, 1040, 540), radius=8, fill=(60, 60, 70, 255), outline=INK, width=3)
    d.ellipse((920, 486, 960, 526), fill=(30, 30, 36, 255))
    d.line(((1000, 470), (1030, 420)), fill=INK, width=4)
    d.rectangle((150, 480, 260, 540), fill=(240, 240, 232, 255), outline=INK, width=3)
    d.text((205, 510), '值班表', font=F('Bold', 18), fill=(60, 60, 70, 255), anchor='mm')
    return img


@lru_cache(maxsize=None)
def bg_lake(w=W):
    img = vgrad(w, H, [(0, (12, 14, 42)), (0.5, (46, 38, 92)), (1, (30, 30, 70))])
    d = nd(img)
    stars(d, 101, int(170 * w / W), (0, 0, w, 300))
    milky(img, 102, (0, 40, w, 260))
    moon(img, int(w * 0.24), 120, 52)
    d = nd(img)
    for x, y, s in ((w * 0.5, 160, 150), (w * 0.8, 110, 120)):
        cloud(d, x, y, s, (150, 130, 200), 40)
    rng = np.random.default_rng(103)
    x = -20
    while x < w:
        bw = rng.uniform(150, 240)
        dorm_building(d, rng, x, 360, bw, rng.uniform(100, 170), body=(34, 38, 70), lit=0.45)
        x += bw + rng.uniform(30, 90)
    for x in range(0, w, 140):
        tree(d, x + 30, 372, 60, (20, 44, 42), (36, 70, 60))
    # 石拱桥和亭子
    bx = w * 0.62
    d.rectangle((bx - 220, 330, bx + 220, 346), fill=(120, 116, 130, 255))
    d.chord((bx - 160, 300, bx + 160, 420), 180, 360, fill=(30, 30, 60, 255))
    for k in range(9):
        lx = bx - 200 + k * 50
        d.line(((lx, 330), (lx, 316)), fill=(150, 146, 160, 255), width=4)
        glow(img, lx, 312, 10, (255, 200, 120), 0.7)
    d = nd(img)
    px_ = w * 0.86
    d.polygon([(px_ - 70, 318), (px_ + 70, 318), (px_ + 40, 290), (px_ - 40, 290)], fill=(150, 56, 56, 255), outline=INK)
    d.polygon([(px_ - 20, 290), (px_ + 20, 290), (px_, 270)], fill=(150, 56, 56, 255))
    for k in (-50, 50):
        d.rectangle((px_ + k - 4, 318, px_ + k + 4, 360), fill=(150, 56, 56, 255))
    # 水面和倒影
    top = img.crop((0, 0, w, 372)).transpose(Image.FLIP_TOP_BOTTOM).resize((w, H - 372))
    refl = Image.eval(top.filter(ImageFilter.GaussianBlur(3)), lambda v: int(v * 0.55))
    img.paste(refl, (0, 372))
    d = nd(img)
    d.rectangle((0, 372, w, H), fill=(20, 30, 70, 90))
    for k in range(14):
        lx, ly = rng.uniform(0, w), rng.uniform(470, 700)
        d.ellipse((lx - 26, ly - 8, lx + 26, ly + 8), fill=(40, 100, 70, 255))
        d.polygon([(lx, ly), (lx + 26, ly - 3), (lx + 26, ly + 3)], fill=(20, 30, 70, 255))
    return img


def ripples(img, t, y0=380, seed=104):
    d = nd(img)
    rng = np.random.default_rng(seed)
    for _ in range(int(img.width / 8)):
        y = rng.uniform(y0 + 6, H)
        x = (rng.uniform(0, img.width) + t * 30 * (1 + (y - y0) / 200)) % img.width
        ln = rng.uniform(20, 80) * (0.5 + (y - y0) / 300)
        d.line((x, y, x + ln, y), fill=(170, 180, 230, int(rng.uniform(30, 80))), width=2)


@lru_cache(maxsize=None)
def bg_shore():
    img = bg_lake().copy()
    d = nd(img)
    d.polygon([(0, 590), (W, 570), (W, H), (0, H)], fill=(90, 84, 80, 255))
    d.rectangle((0, 580, W, 592), fill=(130, 124, 116, 255))
    for x in range(0, W, 46):
        d.rectangle((x, 552, x + 6, 588), fill=(150, 144, 136, 255))
    d.line(((0, 556), (W, 540)), fill=(160, 154, 146, 255), width=6)
    willow(d, 90, 600, 270)
    willow(d, 1200, 585, 250)
    return img


@lru_cache(maxsize=None)
def bg_door():
    img = vgrad(W, H, [(0, (14, 16, 44)), (1, (50, 40, 80))])
    d = nd(img)
    stars(d, 111, 40, (0, 0, W, 60))
    d.rectangle((60, 0, 1220, 640), fill=(196, 160, 130, 255), outline=INK, width=3)
    rng = np.random.default_rng(112)
    for x0 in (90, 830):
        windows(d, rng, x0, 20, x0 + 360, 230, 4, 2, lit=0.6, frame=(120, 100, 90), people=0.4)
    d.rectangle((60, 238, 1220, 252), fill=(170, 136, 110, 255))
    d.rectangle((420, 150, 860, 230), fill=(120, 60, 56, 255), outline=INK, width=3)
    d.text((640, 190), '8 号 楼', font=F('Black', 44), fill=(255, 220, 150, 255), anchor='mm')
    glow(img, 640, 190, 160, (255, 200, 120), 0.25)
    d = nd(img)
    d.rectangle((440, 260, 840, 640), fill=(60, 58, 70, 255), outline=INK, width=4)
    lob = vgrad(360, 360, [(0, (255, 236, 196)), (1, (230, 200, 150))])
    img.paste(lob, (460, 278))
    d = nd(img)
    d.rectangle((560, 300, 720, 380), fill=(240, 236, 226, 255), outline=(150, 140, 120, 255), width=3)
    d.ellipse((610, 306, 670, 366), fill=(250, 250, 246, 255), outline=INK, width=3)
    d.line(((640, 336), (640, 312)), fill=INK, width=4)
    d.line(((640, 336), (658, 326)), fill=INK, width=4)
    d.text((640, 392), '门禁 23:00', font=F('Black', 20), fill=(200, 40, 50, 255), anchor='mm')
    glow(img, 640, 450, 230, (255, 226, 170), 0.35)
    d = nd(img)
    d.rectangle((880, 330, 1060, 500), fill=(255, 220, 150, 255), outline=INK, width=6)
    d.rectangle((880, 300, 1060, 330), fill=(150, 60, 56, 255), outline=INK, width=3)
    d.text((970, 315), '值班室', font=F('Black', 18), fill=(255, 230, 180, 255), anchor='mm')
    notice_board(d, 150, 330, 220, 160, 9)
    d.rectangle((0, 640, W, H), fill=(80, 82, 96, 255))
    for k, y in enumerate((640, 664, 688)):
        d.rectangle((400 - k * 34, y, 880 + k * 34, y + 24), fill=(110, 112, 126, 255), outline=INK, width=2)
    lamp(img, 260, 640, 440, r=80, cone_w=140)
    for x in (1110, 1180):
        bike(nd(img), x, 690, 1.0, (80, 160, 220))
    return img


@lru_cache(maxsize=None)
def bg_stairs():
    img = vgrad(W, H, [(0, (228, 230, 222)), (1, (200, 204, 196))])
    d = nd(img)
    d.polygon([(0, 430), (W, 650), (W, H), (0, H)], fill=(110, 160, 130, 255))
    steps = 14
    for k in range(steps):
        x0 = k * W / steps
        y0 = 330 + k * 26
        d.rectangle((x0, y0, x0 + W / steps + 2, H), fill=(168, 168, 172, 255))
        d.line((x0, y0, x0 + W / steps, y0), fill=(120, 120, 128, 255), width=5)
    d.line((0, 190, W, 410), fill=INK, width=10)
    d.line((0, 190, W, 410), fill=(200, 120, 60), width=6)
    for k in range(0, steps, 2):
        x = k * W / steps + 20
        d.line((x, 190 + 220 * x / W, x, 330 + k * 26), fill=(90, 90, 100, 255), width=4)
    d.rectangle((900, 60, 1040, 200), fill=(30, 36, 70, 255), outline=(240, 240, 240, 255), width=10)
    stars(d, 121, 12, (910, 70, 1030, 190))
    d.rectangle((150, 110, 240, 200), fill=(230, 50, 50, 255), outline=INK, width=3)
    d.text((195, 155), '消防栓', font=F('Black', 18), fill=(255, 255, 255, 255), anchor='mm')
    d.rectangle((420, 80, 600, 150), fill=(250, 250, 240, 255), outline=INK, width=3)
    d.text((510, 115), '轻声慢行', font=F('Black', 26), fill=(60, 120, 90, 255), anchor='mm')
    glow(img, 320, 40, 90, (255, 255, 230), 0.7)
    return img


@lru_cache(maxsize=None)
def bg_lobby():
    img = vgrad(W, H, [(0, (232, 222, 200)), (1, (206, 196, 176))])
    d = nd(img)
    d.rectangle((0, 400, W, H), fill=(190, 182, 164, 255))
    for i in range(-10, 22):
        d.line((640 + i * 70, 400, 640 + i * 260, H), fill=(160, 152, 136, 255), width=2)
    for y in (440, 500, 580, 680):
        d.line((0, y, W, y), fill=(160, 152, 136, 255), width=2)
    d.rectangle((860, 120, 1140, 320), fill=(255, 226, 170, 255), outline=(120, 100, 90, 255), width=12)
    d.rectangle((860, 90, 1140, 120), fill=(150, 60, 56, 255), outline=INK, width=3)
    d.text((1000, 105), '宿管值班室', font=F('Black', 18), fill=(255, 230, 180, 255), anchor='mm')
    d.rounded_rectangle((900, 200, 1000, 280), radius=6, fill=(40, 40, 50, 255))
    d.rectangle((908, 208, 992, 262), fill=(120, 190, 230, 255))
    for k in range(4):
        for j in range(3):
            d.rectangle((150 + k * 62, 130 + j * 56, 204 + k * 62, 178 + j * 56), fill=(210, 214, 222, 255), outline=INK, width=2)
            d.rectangle((168 + k * 62, 150 + j * 56, 186 + k * 62, 156 + j * 56), fill=(90, 90, 100, 255))
    d.ellipse((560, 70, 660, 170), fill=(250, 250, 246, 255), outline=INK, width=5)
    d.line(((610, 120), (610, 82)), fill=INK, width=5)
    d.line(((610, 120), (610, 92)), fill=(220, 40, 50), width=3)
    d.rectangle((560, 190, 660, 230), fill=(250, 250, 240, 255), outline=INK, width=2)
    d.text((610, 210), '23:00', font=F('Black', 22), fill=(220, 40, 50, 255), anchor='mm')
    d.polygon([(1180, 400), (1240, 400), (1230, 360), (1190, 360)], fill=(190, 110, 80, 255), outline=INK)
    for k in range(6):
        a = -math.pi / 2 + (k - 2.5) * 0.35
        d.ellipse((1210 + math.cos(a) * 40 - 16, 340 + math.sin(a) * 60 - 26, 1210 + math.cos(a) * 40 + 16, 340 + math.sin(a) * 60 + 26),
                  fill=(70, 160, 100, 255), outline=INK)
    return img


def bg_victory(t):
    img = Image.new('RGB', (W, H), (60, 30, 6))
    sunburst(img, 640, 330, (60, 30, 6), (120, 64, 14), 18, t * 0.4)
    glow(img, 640, 330, 260, (255, 210, 110), 0.5)
    return img


@lru_cache(maxsize=None)
def bg_end():
    img = vgrad(W, H, [(0, (12, 14, 42)), (0.6, (52, 40, 96)), (1, (110, 66, 110))])
    d = nd(img)
    stars(d, 131, 160, (0, 0, W, 300))
    milky(img, 132, (0, 40, W, 280))
    d = nd(img)
    rng = np.random.default_rng(133)
    dorm_building(d, rng, 180, 600, 920, 330, body=(70, 64, 100), lit=0.7, label='8号楼')
    d.rectangle((0, 600, W, H), fill=(80, 82, 96, 255))
    for x in (60, 1220):
        tree(d, x, 610, 200)
    for x in (300, 980):
        lamp(img, x, 610, 300, r=80, cone_w=140)
    return img
