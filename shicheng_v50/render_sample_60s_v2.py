#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《事成V你50》60 秒样片 v2：卡通角色、丰富场景、夸张表情

在仓库根目录运行：
    pip install numpy pillow imageio-ffmpeg edge-tts
    python shicheng_v50/render_sample_60s_v2.py              # 出 sample_60s_v2.mp4 和关键帧拼图
    python shicheng_v50/render_sample_60s_v2.py --preview    # 只出关键帧拼图
    python shicheng_v50/render_sample_60s_v2.py --preview 2.6 14.0    # 只看这几秒

时间线、台词和配音跟 v1（render_sample_60s.py）一样；人物换成 toon.py 的卡通角色，场景换成 toon_scenes.py。
"""
import math
import os
import subprocess
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_hero_select as hero  # noqa: E402
import render_sample_60s as V1  # noqa: E402
import sample_audio as SA  # noqa: E402
import sample_scenes as SC1  # noqa: E402
import toon as T  # noqa: E402
import toon_scenes as S  # noqa: E402
from toon_scenes import nd, W, H, F, clamp, ease_out, ease_back, caption, tag, bubble  # noqa: E402

FPS, DUR, SR = 30, 60.0, hero.SR
WIN = []
WHO_KEY = {'外卖小哥': 'rider', '大聪明': 'dacong', '室友A': 'roomA', '室友B': 'roomB', '阿飞': 'afei', '小K': 'xiaok',
           '老周': 'laozhou', '星星': 'xingxing', '宿管阿姨': 'suguan'}
ALL = set(WHO_KEY.values())
INK = T.INK


def lerp(a, b, u):
    return a + (b - a) * u


def smooth(u):
    u = clamp(u)
    return u * u * (3 - 2 * u)


def talk(who, t):
    for s, e, ln in WIN:
        if ln['who'] == who and s <= t < e:
            return 0.5 + 0.5 * math.sin(2 * math.pi * 7.5 * (t - s))
    return 0.0


def speaking(who, t):
    return any(ln['who'] == who and s <= t < e for s, e, ln in WIN)


CD_KEYS = [(4.0, 480), (19.0, 430), (23.0, 330), (27.0, 190), (30.0, 100), (33.0, 60), (38.0, 5), (43.2, 0)]


def countdown(t):
    if t <= CD_KEYS[0][0]:
        return CD_KEYS[0][1]
    for (t0, v0), (t1, v1) in zip(CD_KEYS, CD_KEYS[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return 0


def ghost(frame, key, pose, x, y, h, alpha, **kw):
    img, (px, py), _ = T.render(key, pose, h, **kw)
    img.putalpha(img.getchannel('A').point(lambda v: int(v * alpha)))
    frame.paste(img, (int(x - px), int(y - py)), img)


def chair(d, x, seat_y, f, s=1.0):
    bx = x - f * 58 * s
    T.opoly(d, [(bx - 26 * s, seat_y - 200 * s), (bx + 26 * s, seat_y - 200 * s), (bx + 32 * s, seat_y), (bx - 32 * s, seat_y)], (46, 46, 60), 3)
    d.rectangle((bx - 18 * s, seat_y - 180 * s, bx + 18 * s, seat_y - 120 * s), fill=(220, 60, 80, 255))
    d.rounded_rectangle((x - 72 * s, seat_y - 4 * s, x + 72 * s, seat_y + 20 * s), radius=8, fill=(46, 46, 60, 255), outline=INK, width=3)
    d.rectangle((x - 7 * s, seat_y + 20 * s, x + 7 * s, seat_y + 84 * s), fill=(70, 70, 80, 255))
    d.line(((x - 52 * s, seat_y + 90 * s), (x + 52 * s, seat_y + 90 * s)), fill=(70, 70, 80, 255), width=int(8 * s))


def drone(d, x, y, s=1.0, t=0.0, bag=True, rope=60, alpha=255):
    if bag:
        d.line((x, y + 8 * s, x, y + rope * s), fill=(220, 220, 230, alpha), width=max(1, int(3 * s)))
        T.draw_bag(d, x, y + (rope + 20) * s, 52 * s, max(1, 2 * s))
    for sx in (-1, 1):
        d.line((x, y, x + sx * 50 * s, y - 10 * s), fill=INK, width=int(9 * s))
        d.line((x, y, x + sx * 50 * s, y - 10 * s), fill=(60, 64, 78, alpha), width=int(5 * s))
        rx = x + sx * 50 * s
        a = int(110 + 70 * math.sin(t * 60 + sx))
        d.ellipse((rx - 34 * s, y - 18 * s, rx + 34 * s, y - 6 * s), fill=(190, 200, 220, a))
    d.rounded_rectangle((x - 24 * s, y - 11 * s, x + 24 * s, y + 11 * s), radius=7 * s, fill=(40, 42, 52, alpha), outline=INK, width=max(1, int(2 * s)))
    d.ellipse((x - 5 * s, y - 4 * s, x + 5 * s, y + 6 * s), fill=(255, 70, 70, 255) if int(t * 4) % 2 else (70, 255, 130, 255))


def flipflop(d, x, y, a, s=1.0):
    pts = [(x + 26 * s * math.cos(a + k * math.pi / 2), y + 11 * s * math.sin(a + k * math.pi / 2)) for k in range(4)]
    T.opoly(d, pts, (60, 160, 230), 2)
    d.line((pts[0], pts[2]), fill=(250, 250, 250), width=3)


def impact(d, x, y, r, col=(255, 240, 120)):
    pts = []
    for k in range(16):
        a = k * math.pi / 8
        rr = r if k % 2 == 0 else r * 0.5
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    T.opoly(d, pts, col, 3)


# ================================================================ 0～11 秒
def s_black(t):
    img = Image.new('RGB', (W, H), (8, 8, 14))
    d = nd(img)
    a = clamp(t / 0.25)
    d.text((640, 96), '周四 22:52', font=F('Black', 60), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    buzz = t < 0.6
    jx = 6 * math.sin(2 * math.pi * 28 * t) if buzz else 0
    sx0, sy0, sx1, sy1 = SC1.phone_frame(img, 500 + jx, 150, 280, 540, screen=(28, 32, 48))
    cx = (sx0 + sx1) / 2
    d = nd(img)
    if buzz:
        for k in range(2):
            ph = (t * 2 + k / 2) % 1
            r = 70 + 40 * ph
            d.ellipse((cx - r, sy0 + 150 - r, cx + r, sy0 + 150 + r), outline=(120, 220, 160, int(200 * (1 - ph))), width=3)
    icon = T.head_icon('rider', 140, 'happy' if buzz else 'smile', talk=talk('外卖小哥', t), t=t, bg=(250, 214, 90))
    img.paste(icon, (int(cx - 70), int(sy0 + 80)), icon)
    d = nd(img)
    d.text((cx, sy0 + 260), '外卖小哥', font=F('Black', 30), fill=(255, 255, 255, 255), anchor='mm')
    if buzz:
        d.text((cx, sy0 + 300), '来电…', font=F('Medium', 20), fill=(180, 186, 200, 255), anchor='mm')
        for bx, col in ((cx - 70, (230, 60, 70)), (cx + 70, (60, 200, 110))):
            d.ellipse((bx - 32, sy1 - 110, bx + 32, sy1 - 46), fill=col + (255,))
        for x in (420, 860):
            caption(d, '嗡', x, 360 + 10 * math.sin(t * 40), 46, t, 0.05, color=(255, 255, 255), stroke=(40, 40, 60))
    else:
        d.text((cx, sy0 + 300), f'通话中 00:0{int(t - 0.6)}', font=F('Medium', 20), fill=(160, 230, 180, 255), anchor='mm')
        d.ellipse((cx - 32, sy1 - 110, cx + 32, sy1 - 46), fill=(230, 60, 70, 255))
        for k in range(5):
            hgt = 10 + 26 * abs(math.sin(t * 9 + k)) * (1 if talk('外卖小哥', t) else 0.2)
            d.rounded_rectangle((cx - 50 + k * 22, sy0 + 380 - hgt, cx - 38 + k * 22, sy0 + 380 + hgt), radius=5, fill=(120, 220, 160, 255))
    return img


@lru_cache(maxsize=None)
def gate_inset_base():
    world, _ = S.bg_gate()
    return world.crop((560, 330, 1200, 730))


def rider_inset(img, t):
    a_in = ease_out(clamp((t - 1.4) / 0.2))
    a_out = ease_out(clamp((t - 2.05) / 0.2))
    if a_out >= 1:
        return
    panel = gate_inset_base().copy()
    T.put_on(panel, 'rider', dict(view='front', arms=((8, 6), {'ik': (0.2, -0.16), 'rel': 'N', 'bend': 1}), hands=('fist', 'thumb')),
             120, 390, 250, expr='happy', talk=talk('外卖小哥', t), t=t)
    panel = panel.resize((400, 250), Image.LANCZOS)
    x = int(40 - 470 * (1 - a_in) - 470 * a_out)
    d = nd(img)
    d.rounded_rectangle((x - 6, 84, x + 406, 340), radius=18, fill=(255, 214, 90, 255), outline=INK, width=4)
    img.paste(panel, (x, 90))
    d = nd(img)
    d.rounded_rectangle((x + 10, 300, x + 150, 332), radius=10, fill=(20, 20, 26, 230))
    d.text((x + 80, 316), '南门·外卖架', font=F('Bold', 18), fill=(255, 230, 140, 255), anchor='mm')


def s_dorm_call(t):
    img = S.bg_dorm().copy()
    shocked = t >= 2.05
    if shocked:
        S.radial_lines(img, 640, 300, (255, 255, 255), n=90, inner=320, a=120, seed=2, t=t)
    d = nd(img)
    chair(d, 384, 515, -1, 1.0)
    T.put(img, 'roomA', dict(view='side', lean=6, head=8 if not shocked else -14,
                             arms=({'ik': (0.3, -0.1), 'rel': 'P', 'bend': 1}, {'ik': (0.33, -0.09), 'rel': 'P', 'bend': 1}),
                             legs=((80, 85), (86, 88))), 384, 505, 300, facing=-1, expr='focus' if not shocked else 'shock', t=t)
    d = nd(img)
    d.rounded_rectangle((860, 236, 1250, 268), radius=10, fill=(120, 170, 220, 255), outline=INK, width=3)
    d.rounded_rectangle((1150, 210, 1240, 248), radius=14, fill=(250, 246, 236, 255), outline=INK, width=3)
    T.put(img, 'roomB', dict(view='side', rot=90, arms=((10, 20), {'ik': (0.14, -0.22), 'rel': 'N', 'bend': 1}), legs=((5, 5), (8, 10))),
          1010, 244, 250, facing=-1, expr='deadpan' if not shocked else 'shock', t=t, hold='phone')
    d = nd(img)
    T.opoly(d, [(868, 224), (1072, 212), (1086, 266), (866, 266)], (250, 170, 90), 3)
    for k in range(4):
        d.line(((900 + k * 45, 222), (906 + k * 45, 262)), fill=(230, 140, 70, 255), width=3)
    T.put_on(img, 'roomC', dict(view='front', arms=((8, 6), {'ik': (0.1, 0.08), 'rel': 'Hc', 'bend': 1})), 1120, 712, 470,
             expr='neutral' if not shocked else 'shock', t=t, shadow=True)
    jump = -30 * math.sin(math.pi * clamp((t - 2.05) / 0.25)) if shocked else 0
    e = 'smile' if not shocked else ('shock' if t < 2.15 else 'scream')
    T.put_on(img, 'dacong', dict(view='front', arms=((8, 6), {'ik': (0.13, 0.02), 'rel': 'Hc', 'bend': 1}), hands=('fist', 'open')),
             640, 718 + jump, 540, expr=e, talk=talk('大聪明', t), hold='phone', t=t, shadow=True)
    if t < 2.3:
        rider_inset(img, t)
    if 2.05 <= t < 2.12:
        img = Image.blend(img, Image.new('RGB', (W, H), (255, 255, 255)), 0.6)
    s = 1.0 + 0.12 * ease_out(clamp((t - 2.05) / 0.15)) if shocked else 1.0 + 0.03 * smooth((t - 1.4) / 0.65)
    return S.zoom(img, s, 640, 330)


def s_turn(t, who, t0):
    lt = t - t0
    img = S.bg_dorm_blur().copy()
    col = {'roomA': (120, 200, 255), 'roomB': (190, 160, 255), 'roomC': (255, 200, 120)}[who]
    S.radial_lines(img, 640, 330, col, n=80, inner=300, a=150, seed=hash(who) % 50, t=t)
    turned = lt >= 0.07
    d = nd(img)
    if who == 'roomB':
        d.rectangle((0, 470, W, H), fill=(120, 170, 220, 255))
        d.ellipse((560, 320, 980, 470), fill=(250, 246, 236, 255), outline=INK, width=4)
        T.put(img, 'roomB', dict(view='front' if turned else 'side', bust=True, rot=90, arms=((10, 6), (10, 6))), 330, 400, 900, facing=-1,
              expr='dead' if turned else 'deadpan', t=t)
        d = nd(img)
        T.opoly(d, [(-20, 430), (440, 410), (470, 740), (-20, 740)], (250, 170, 90), 4)
    elif who == 'roomC':
        c = dict(T.CH['roomC'], acc=('towel',))
        T.put(img, c, dict(view='front' if turned else 'side', bust=True, arms=((12, 6), (12, 6))), 640, 860, 1150, facing=1,
              expr='shock' if turned else 'neutral', t=t)
        d = nd(img)
        u = clamp(lt / 0.3)
        bx, by = 700 + 40 * u, 520 + 260 * u * u
        a = u * 5
        d.line(((bx - 60 * math.cos(a), by - 60 * math.sin(a)), (bx + 60 * math.cos(a), by + 60 * math.sin(a))), fill=INK, width=14)
        d.line(((bx - 60 * math.cos(a), by - 60 * math.sin(a)), (bx + 60 * math.cos(a), by + 60 * math.sin(a))), fill=(90, 170, 255), width=8)
    else:
        T.put(img, 'roomA', dict(view='front' if turned else 'side', bust=True, arms=((12, 6), (12, 6))), 640, 860, 1150, facing=1,
              expr='judge' if turned else 'neutral', glint=turned, t=t)
    s = 1.0 + 0.16 * (1 - ease_out(lt / 0.15))
    return S.shake(S.zoom(img, s, 640, 330), 10 * math.sin(lt * 90) * (1 - clamp(lt / 0.15)), 0)


def s_roomA(t):
    lt = t - 4.9
    img = S.bg_dorm_blur().copy()
    d = nd(img)
    S.radial_lines(img, 640, 330, (120, 200, 255), n=50, inner=380, a=70, seed=5, t=0)
    push = lt < 0.4
    arm1 = {'ik': (0.0, 0.03), 'rel': 'Hc', 'bend': 1} if push else (12, 6)
    e = dict(eyes='half', brows='sly', mouth='flat', fx=('question',))
    T.put(img, 'roomA', dict(view='front', bust=True, arms=((12, 6), arm1)), 640, 870, 1100, expr=e, talk=talk('室友A', t), glint=push,
          t=t)
    return S.zoom(img, 1.0 + 0.04 * smooth(lt / 1.7), 640, 340)


def s_roomB(t):
    lt = t - 6.6
    img = S.bg_dorm_blur().copy()
    d = nd(img)
    d.rectangle((0, 470, W, H), fill=(120, 170, 220, 255))
    d.ellipse((600, 320, 1020, 470), fill=(250, 246, 236, 255), outline=INK, width=4)
    e = dict(eyes='dot', brows='flat', mouth='flat', fx=('soul', 'gloom'))
    T.put(img, 'roomB', dict(view='front', bust=True, rot=90, arms=((10, 6), (10, 6))), 340, 400, 1000, facing=-1, expr=e,
          talk=talk('室友B', t), t=t)
    d = nd(img)
    T.opoly(d, [(-20, 430), (480, 410), (510, 740), (-20, 740)], (250, 170, 90), 4)
    if lt > 0.3:
        caption(d, '拉', 1060, 210, 120, t, 6.9, color=(180, 160, 255), stroke=(40, 30, 80))
    return S.zoom(img, 1.0 + 0.05 * smooth(lt / 0.85), 760, 360)


POST = '急！南门炸鸡运回北区8号楼'


def phone_post(img, t, px0=720):
    sx0, sy0, sx1, sy1 = SC1.phone_frame(img, px0, 30, 360, 660)
    d = nd(img)
    d.text((sx0 + 26, sy0 + 22), '22:53', font=F('Bold', 18), fill=(20, 20, 26, 255), anchor='lm')
    d.rectangle((sx0, sy0 + 44, sx1, sy0 + 96), fill=(255, 255, 255, 255))
    d.text((sx0 + 20, sy0 + 70), '‹', font=F('Bold', 30), fill=(40, 40, 48, 255), anchor='lm')
    d.text(((sx0 + sx1) / 2, sy0 + 70), '发布找搭子', font=F('Bold', 22), fill=(20, 20, 26, 255), anchor='mm')
    pressed = 10.2 <= t < 10.32
    bx0, by0, bx1, by1 = sx1 - 82, sy0 + 56, sx1 - 14, sy0 + 86
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=15, fill=(150, 20, 40, 255) if pressed else (230, 40, 70, 255))
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), '发布', font=F('Bold', 18), fill=(255, 255, 255, 255), anchor='mm')
    n = int(clamp((t - 7.55) / 1.5) * len(POST))
    d.text((sx0 + 20, sy0 + 130), POST[:n] + ('|' if int(t * 4) % 2 and n < len(POST) else ''), font=F('Bold', 21), fill=(20, 20, 26, 255),
           anchor='lm')
    x = sx0 + 20
    for txt, tc in (('#门禁前', 9.1), ('#事成V你50', 9.3), ('#找搭子', 9.45)):
        f = F('Bold', 19)
        w = f.getlength(txt) + 24
        if t >= tc:
            sc = ease_back((t - tc) / 0.2)
            cx, cy = x + w / 2, sy0 + 180
            d.rounded_rectangle((cx - w / 2 * sc, cy - 17 * sc, cx + w / 2 * sc, cy + 17 * sc), radius=17 * sc, fill=(255, 228, 232, 255))
            d.text((cx, cy), txt, font=F('Bold', 19 * sc), fill=(220, 30, 60, 255), anchor='mm')
        x += w + 10
    d.text((sx0 + 20, sy0 + 230), '示意界面，正式版用TT语音真实录屏', font=F('Medium', 15), fill=(150, 150, 160, 255), anchor='lm')
    ky0 = sy1 - 210
    d.rectangle((sx0, ky0, sx1, sy1), fill=(214, 216, 222, 255))
    hot = int(t * 9) % 30 if 7.55 <= t < 9.05 else -1
    kw = (sx1 - sx0 - 22) / 10
    for r in range(4):
        for c in range(10 if r < 3 else 5):
            kx = sx0 + 6 + c * (kw + 1) if r < 3 else sx0 + 6 + c * (kw * 2 + 2)
            kw2 = kw if r < 3 else kw * 2
            ky = ky0 + 10 + r * 48
            d.rounded_rectangle((kx, ky, kx + kw2 - 2, ky + 40), radius=5, fill=(170, 176, 190, 255) if (r * 10 + c) == hot else (255, 255, 255, 255))
    if 10.2 <= t < 10.7:
        p = (t - 10.2) / 0.5
        r = 20 + 120 * ease_out(p)
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(230, 40, 70, int(220 * (1 - p))), width=5)
    if t >= 10.3:
        a = clamp((t - 10.3) / 0.1)
        d.rounded_rectangle((sx0 + 60, 330, sx1 - 60, 390), radius=14, fill=(20, 20, 26, int(220 * a)))
        d.text(((sx0 + sx1) / 2, 360), '发布成功', font=F('Bold', 22), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    if 9.75 <= t < 10.35:
        p = smooth((t - 9.75) / 0.42)
        fx, fy = lerp(1180, (bx0 + bx1) / 2 + 10, p), lerp(760, (by0 + by1) / 2 + 14, p)
        if pressed:
            fy += 4
        d.line((fx, fy, fx + 260, fy + 330), fill=INK, width=64)
        d.line((fx, fy, fx + 260, fy + 330), fill=(246, 214, 186, 255), width=56)
        d.ellipse((fx - 32, fy - 32, fx + 32, fy + 32), fill=INK)
        d.ellipse((fx - 28, fy - 28, fx + 28, fy + 28), fill=(246, 214, 186, 255))
        d.ellipse((fx - 18, fy - 22, fx + 10, fy + 2), fill=(252, 232, 214, 255))
    return (bx0 + bx1) / 2, (by0 + by1) / 2


def s_phone(t):
    img = S.bg_dorm_blur().copy()
    if t >= 9.6:
        S.radial_lines(img, 330, 420, (255, 140, 60), n=70, inner=260, a=110, seed=9, t=t)
        S.glow(img, 330, 420, 260, (255, 120, 40), 0.25)
    e = 'nervous' if t < 8.6 else ('determined' if t < 9.6 else 'fired')
    jit = 0.012 * math.sin(t * 42) if 7.55 <= t < 9.05 else 0.0
    pose = dict(view='front', bust=True, arms=({'ik': (-0.05 + jit, 0.1), 'rel': 'N', 'bend': -1}, {'ik': (0.07 - jit, 0.1), 'rel': 'N', 'bend': 1}))
    T.put(img, 'dacong', pose, 330, 860, 900, expr=e, t=t, hold='phone')
    bx, by = phone_post(img, t)
    z = 1.0 + 0.9 * smooth((t - 9.6) / 0.3) * (1 - smooth((t - 10.25) / 0.1))
    return S.zoom(img, z, bx, by + 60)


def s_campus(t):
    lt = t - 10.35
    base, spots = S.bg_campus()
    img = base.copy()
    d = nd(img)
    src = (725, 420)
    R = 1500 * ease_out(clamp(lt / 0.6))
    for k in range(3):
        rr = R - k * 60
        if rr > 0:
            d.ellipse((src[0] - rr, src[1] - rr * 0.55, src[0] + rr, src[1] + rr * 0.55), outline=(255, 220, 120, int(200 * (1 - k * 0.3) * (1 - lt / 0.7))),
                      width=6 - k * 2)
    rng = np.random.default_rng(7)
    for (x, y, lit, box) in spots:
        dist = math.hypot(x - src[0], (y - src[1]) / 0.55)
        if dist < R and not lit:
            d.rectangle(box, fill=(255, 226, 150, 255))
            if rng.random() < 0.2:
                d.rounded_rectangle((x - 5, y - 26, x + 5, y - 12), radius=2, fill=(120, 200, 255, 255))
    caption(d, '全校：？？？', 640, 120, 60, t, 10.55, color=(255, 255, 255), stroke=(40, 30, 80))
    if lt < 0.12:
        img = Image.blend(img, Image.new('RGB', (W, H), (255, 255, 255)), 0.8 * (1 - lt / 0.12))
    return img


# ================================================================ 11～19 秒：选英雄卡
CARD_SPEC = [
    dict(key='afei', pose=dict(view='front', arms=((95, 95), (95, 95)), legs=((6, 0), (6, 0))), expr='fired'),
    dict(key='xiaok', pose=dict(view='front', arms=((12, 8), {'ik': (0.26, -0.24), 'rel': 'P', 'bend': 1}), hands=('fist', 'point')), expr='cool'),
    dict(key='laozhou', pose=dict(view='front', arms=({'ik': (-0.12, -0.04), 'rel': 'P', 'bend': -1}, {'ik': (0.03, 0.03), 'rel': 'Hc', 'bend': 1})),
         expr='cool', hold={'remote': 'W0'}),
    dict(key='xingxing', pose=dict(view='front', arms=((8, 6), {'ik': (0.17, -0.16), 'rel': 'N', 'bend': 1}), hands=('fist', 'point')), expr='smile'),
    dict(key='dacong', pose=dict(view='front', arms=((8, 6), {'ik': (0.06, -0.11), 'rel': 'Hc', 'bend': 1}), hands=('fist', 'open')), expr='nervous'),
]


def toon_card(k, lt, hvlen, t):
    spec = CARD_SPEC[k]
    img = Image.new('RGBA', (hero.CW, hero.CH), (0, 0, 0, 0))
    tk = 0.0
    a0 = hero.VOICE_LEAD
    if k < 4 and a0 <= lt < a0 + hvlen[k]:
        tk = 0.5 + 0.5 * math.sin(2 * math.pi * 7.5 * (lt - a0))
    expr = spec['expr']
    if k == 4 and lt >= hero.lock_time(4):
        expr = 'dead'
    glint = k == 2 and 0.35 <= lt < 0.95
    T.put(img, spec['key'], spec['pose'], 280, 520, 720, expr=expr, talk=tk, t=t, glint=glint, hold=spec.get('hold'))
    return img


@lru_cache(maxsize=None)
def icon(key, size, expr='smile'):
    return T.head_icon(key, size, expr)


ICON_KEYS = ['dacong', 'afei', 'xiaok', 'laozhou', 'xingxing']


def hero_frame(t, HA, hvlen):
    lt = t - 11.0
    k, s0 = hero.card_at(lt)
    HA['char'][k] = toon_card(k, lt - s0, hvlen, t)
    fr = hero.render_frame(lt, HA, hvlen)
    for i in range(5):
        cx, cy = 912 + i * 57, 38
        tj = -1.0 if i == 0 else hero.STARTS[i - 1]
        if lt < tj:
            continue
        sc = ease_back((lt - tj) / 0.28) if tj >= 0 else 1.0
        size = max(4, int(36 * sc))
        ic = icon(ICON_KEYS[i], 36).resize((size, size), Image.LANCZOS) if size != 36 else icon(ICON_KEYS[i], 36)
        fr.paste(ic, (int(cx - size / 2), int(cy - size / 2)), ic)
    return fr


# ================================================================ 19～38 秒：接力
def s_balcony(t):
    lt = t - 19.0
    img = S.bg_balcony().copy()
    if 0.1 <= lt < 0.8:
        u = (lt - 0.1) / 0.7
        S.meteor(img, lerp(260, 980, u), lerp(70, 250, u), 220, math.atan2(180, 720), a=1 - abs(u - 0.5) * 1.2)
    lean = lerp(8, 52, smooth((lt - 0.1) / 0.5))
    pose = dict(view='side', lean=lean, head=-lean * 0.4,
                arms=({'ik': (0.22, -0.32), 'rel': 'P', 'bend': -1}, {'ik': (0.26, -0.35), 'rel': 'P', 'bend': -1}), legs=((-6, 4), (8, 5)))
    h = 400
    J = T.joints(T.CH['xingxing'], dict(pose, lean=52, head=-52 * 0.4), -1)
    floor = 705
    fy = max(J['A0'][1], J['A1'][1]) + 0.045
    py = floor - fy * h
    ex = 820 + J['Hc'][0] * h - 0.05 * h
    ey = py + J['Hc'][1] * h + 0.02 * h
    s = (floor - ey) / 112
    tube = 1.4 / s
    d = nd(img)
    S.telescope(d, ex - 94 * s * tube, floor, aim=-1, s=s, tube=tube)
    T.put(img, 'xingxing', pose, 820, py, h, facing=-1, expr='focus', talk=talk('星星', t), t=t, wind=0.25 + 0.08 * math.sin(t * 2))
    return S.zoom(img, 1.0 + 0.08 * smooth(lt / 1.6), 760, 420)


def s_pov(t):
    lt = t - 20.6
    base, pos = S.bg_gate()
    world = base
    if t >= 21.6:
        world = base.copy()
        u = clamp((t - 21.6) / 1.4)
        x = lerp(180, 640, u)
        ph = 2 * math.pi * 3.2 * (t - 21.6)
        T.put_on(world, 'afei', T.run(ph), x, 655, 200, facing=1, expr='fired', t=t)
        S.dust(nd(world), x - 30, 650, (t * 2) % 0.8, n=5, seed=int(t * 6))
    bxw, byw = pos['bag']
    z = lerp(1.0, 1.85, smooth((lt - 0.35) / 1.3))
    k = 0.72 * z
    cx = lerp(900, bxw + 10, smooth((lt - 0.2) / 1.3)) + 6 * math.sin(lt * 13)
    cy = lerp(520, byw - 20, smooth((lt - 0.2) / 1.3)) + 4 * math.sin(lt * 17)
    crop = world.crop((int(cx - 640 / k), int(cy - 360 / k), int(cx + 640 / k), int(cy + 360 / k))).resize((W, H), Image.BILINEAR)
    d = nd(crop)

    def scr(p):
        return ((p[0] - cx) * k + 640, (p[1] - cy) * k + 360)

    for key, txt, col, t0 in (('guard', '保安大爷｜中立｜别惹', (255, 255, 255), 0.2), ('couple', '情侣｜无害｜别打扰', (255, 170, 200), 0.35),
                              ('cat', '流浪猫｜中立｜可撸', (255, 210, 140), 0.5), ('rider', '外卖小哥｜已撤离', (180, 230, 255), 0.6)):
        if lt >= t0:
            x, y = scr(pos[key])
            if -100 < x < W + 100:
                tag(d, x, y - 30, txt, color=col, size=18, alpha=clamp((lt - t0) / 0.15))
    if t >= 21.6:
        u = clamp((t - 21.6) / 1.4)
        x, y = scr((lerp(180, 640, u), 610))
        tag(d, x, y - 60, '阿飞｜决斗', color=(255, 120, 130), bg=(60, 10, 20), size=20)
    if lt >= 0.4:
        bx, by = scr((bxw, byw))
        u = clamp((lt - 0.4) / 0.25)
        r = lerp(140, 44, ease_out(u)) * k / 0.72 / 1.4
        for sx in (-1, 1):
            for sy in (-1, 1):
                x0, y0 = bx + sx * r, by + sy * r * 0.85
                d.line((x0, y0, x0 - sx * r * 0.35, y0), fill=(255, 60, 60, 255), width=4)
                d.line((x0, y0, x0, y0 - sy * r * 0.35), fill=(255, 60, 60, 255), width=4)
        if u >= 1:
            tag(d, bx, by - r - 6, '大红·炸鸡桶', color=(255, 200, 80), bg=(120, 20, 20), size=24)
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).ellipse((640 - 330, 360 - 330, 640 + 330, 360 + 330), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(6))
    out = Image.new('RGB', (W, H), (0, 0, 0))
    out.paste(crop, (0, 0), m)
    d = nd(out)
    d.ellipse((310, 30, 970, 690), outline=(40, 40, 46, 255), width=10)
    for a, b in (((640, 60), (640, 300)), ((640, 420), (640, 660)), ((340, 360), (580, 360)), ((700, 360), (940, 360))):
        d.line((a, b), fill=(255, 255, 255, 60), width=1)
    return out


def street(offset):
    far, mid, near = S.street_layers()
    o1 = int(offset * 0.25) % (far.width - W)
    img = far.crop((o1, 0, o1 + W, H)).convert('RGB')
    o2 = int(offset * 0.7) % (mid.width - W)
    m = mid.crop((o2, 0, o2 + W, H))
    img.paste(m, (0, 0), m)
    return img, int(offset) % (near.width - W)


def mini_rack(d, x, base):
    for y in (base - 120, base - 60):
        d.rectangle((x, y, x + 260, y + 8), fill=(200, 206, 220, 255), outline=INK, width=2)
    for xx in (x, x + 252):
        d.rectangle((xx, base - 150, xx + 8, base), fill=(200, 206, 220, 255), outline=INK, width=2)
    rng = np.random.default_rng(3)
    for y in (base - 120, base - 60):
        xx = x + 14
        while xx < x + 230:
            bw, bh = rng.uniform(30, 46), rng.uniform(26, 40)
            d.rounded_rectangle((xx, y - bh, xx + bw, y), radius=5, fill=[(90, 150, 220), (240, 200, 80), (246, 246, 240), (120, 200, 140)][int(rng.integers(0, 4))] + (255,),
                                outline=INK, width=2)
            xx += bw + 8


def s_afei_run(t):
    lt = t - 23.0
    rt = max(0.0, lt - 0.38)
    offset = 0.5 * 2200 * rt ** 2
    img, o3 = street(offset)
    d = nd(img)
    mini_rack(d, 260 - offset * 0.7, 600)
    ground = 668
    h = 420
    if lt < 0.38:
        pose = dict(view='side', lean=58, head=-40, arms=({'ik': (0.3, 0.26), 'rel': 'P', 'bend': 1}, {'ik': (0.28, 0.22), 'rel': 'P', 'bend': 1}),
                    legs=((-35, 110), (75, 100)))
        T.put_on(img, 'afei', pose, 640, ground, h, facing=1, expr='fired', t=t, hold='bag', shadow=True)
        if lt > 0.15:
            caption(nd(img), '预备——', 640, 150, 50, t, 23.15, color=(255, 255, 255), stroke=(120, 20, 30))
    else:
        ph = 2 * math.pi * 3.6 * rt
        pose = T.run(ph, lean=24, amp=1.15)
        y = ground + T.bob(ph, h)
        S.speed_lines(d, lt, n=int(12 + 40 * clamp(rt / 0.6)))
        for g, a in ((2, 0.18), (1, 0.32)):
            ghost(img, 'afei', T.run(ph - g * 0.5, 24, 1.15), 600 - g * 90, y - (0.44 + 0.045) * h + 0.04 * h, h, a, facing=1, expr='fired', t=t)
        P = T.put_on(img, 'afei', pose, 600, y, h, facing=1, expr='fired', t=t, hold='bag', talk=talk('阿飞', t))
        d = nd(img)
        for k in range(3):
            S.dust(d, 520 - k * 60, ground - 6, ((t * 3) + k * 0.25) % 0.8, n=5, seed=k + int(t * 4))
    near = S.street_layers()[2].crop((o3, 0, o3 + W, H))
    img.paste(near, (0, 0), near)
    return img


def s_couple(t):
    lt = t - 24.5
    img = S.bg_bench().copy()
    d = nd(img)
    seat_y = 572
    for k in range(3):
        d.rounded_rectangle((470, seat_y - 76 + k * 16, 810, seat_y - 64 + k * 16), radius=4, fill=(140, 94, 62, 255), outline=INK, width=2)
    passed = t >= 24.86
    wind = clamp((t - 24.8) / 0.1) * (1 - clamp((t - 25.5) / 0.8)) if t >= 24.8 else 0.0
    if t < 24.86:
        e_g = e_b = 'love'
    elif t < 25.4:
        e_g = e_b = 'shock'
    else:
        e_g = e_b = 'confused'
    sit = dict(view='front', thigh_k=0.25, arms=((10, 6), (14, 6)), legs=((3, 0), (3, 0)))
    look_g = (0.8, 0) if t >= 25.5 else None
    look_b = (-0.8, 0) if t >= 25.5 else None
    T.put(img, 'girl', sit, 575, seat_y - 6, 300, expr=e_g, t=t, wind=wind, look=look_g)
    boy = dict(view='front', thigh_k=0.25, arms=((10, 6), {'ik': (0.07, 0.13), 'rel': 'N', 'bend': 1}), legs=((3, 0), (3, 0)))
    lid_off = t >= 24.9
    T.put(img, 'boy', boy, 705, seat_y - 6, 300, expr=e_b, t=t, hold='cup', hold_ctx=dict(lid_off=lid_off), look=look_b)
    d = nd(img)
    d.rounded_rectangle((460, seat_y - 10, 820, seat_y + 6), radius=4, fill=(160, 110, 74, 255), outline=INK, width=3)
    for sx in (-1, 1):
        d.rectangle((640 + sx * 150 - 7, seat_y + 6, 640 + sx * 150 + 7, seat_y + 56), fill=(50, 52, 60, 255))
    if lid_off:
        u = (t - 24.9) / 0.9
        lx, ly = 760 + 420 * u, 480 - 480 * u + 560 * u * u
        a = t * 22
        d.ellipse((lx - 16, ly - 6 + 4 * math.sin(a), lx + 16, ly + 6 - 4 * math.sin(a)), fill=(250, 250, 250, 255), outline=INK)
    if wind > 0:
        S.leaves(d, t, 5, 26, (0, 250, W, 650), wind=6.0)
        S.speed_lines(d, t, seed=8, n=int(20 * wind), dirx=-1, box=(0, 300, W, 600), a=(50, 120))
    if 24.6 <= t < 24.95:
        u = (t - 24.6) / 0.35
        x = lerp(-260, 1540, u)
        for g in range(3):
            ghost(img, 'afei', T.run(t * 30 + g, 26, 1.2), x - g * 80, 650 - 0.485 * 520 + 0.04 * 520, 520, 0.9 - g * 0.3, facing=1, expr='fired', t=t)
        S.speed_lines(nd(img), t, n=36)
    if passed and t < 25.4:
        caption(nd(img), '？！', 640, 230, 70, t, 24.95, color=(255, 255, 255), stroke=(40, 30, 80))
    return img


def s_to_slope(t):
    lt = t - 26.3
    img = S.bg_slope_top().copy()
    T.put_on(img, 'xiaok', dict(view='side', lean=8, arms=((-10, 20), {'ik': (0.3, -0.24), 'rel': 'P', 'bend': -1}), legs=((-8, 10), (10, 10)),
                                hands=('fist', 'open')), 930, 600, 380, facing=-1, expr='cool', t=t)
    ph = 2 * math.pi * 3.4 * lt
    x = lerp(100, 600, lt / 0.7)
    T.put_on(img, 'afei', T.run(ph, 22, 1.1), x, 600 + T.bob(ph, 380), 380, facing=1, expr='fired', hold='bag', t=t, talk=talk('阿飞', t))
    S.dust(nd(img), x - 50, 596, (t * 3) % 0.8, n=5, seed=int(t * 5))
    return img


def s_handoff(t):
    lt = t - 27.0
    img = S.bg_slope_top().copy()
    S.god_rays(img, 640, 186, t, (255, 230, 170), 0.2)
    h = 420
    u = smooth((lt - 0.3) / 0.6)
    PA = T.put_on(img, 'afei', dict(view='side', lean=10, arms=((-15, 15), {'ik': (0.3, -0.16), 'rel': 'P', 'bend': -1}), legs=((-12, 10), (14, 10))),
                  510, 606, h, facing=1, expr='fired' if u < 0.6 else 'happy', t=t)
    PK = T.put_on(img, 'xiaok', dict(view='side', lean=10, arms=((-15, 15), {'ik': (0.3, -0.16), 'rel': 'P', 'bend': -1}), legs=((-12, 10), (14, 10)),
                                     hands=('fist', 'open')), 770, 606, h, facing=-1, expr='cool' if u < 0.6 else 'determined', t=t)
    d = nd(img)
    a, b = PA['W1'], PK['W1']
    T.draw_bag(d, lerp(a[0], b[0], u), lerp(a[1], b[1], u) + 26, 0.15 * h, 2)
    rng = np.random.default_rng(4)
    for _ in range(30):
        x, y = rng.uniform(300, 980), rng.uniform(200, 560)
        tw = 0.5 + 0.5 * math.sin(t * 6 + x)
        T.sparkle(d, x, y - lt * 20, 5 + 6 * tw, (255, 236, 170), int(200 * tw))
    S.glow(img, lerp(a[0], b[0], u), lerp(a[1], b[1], u) + 20, 80, (255, 230, 150), 0.35)
    return S.zoom(img, 1.04 + 0.1 * smooth(lt / 1.2), lerp(600, 680, lt / 1.2), 400)


def s_skate(t):
    lt = t - 28.2
    img = S.bg_slope_down().copy()
    d = nd(img)
    x = lerp(-140, 1400, lt / 1.1)
    h = 330
    drift = 0.55 <= lt < 0.95
    if drift:
        pose = dict(view='side', lean=-14, rot=15, arms=((-70, 20), (80, 70)), legs=((12, 50), (50, 10)))
    else:
        pose = dict(view='side', lean=36, rot=15, head=-22, arms=((-35, 20), (65, 80)), legs=((-22, 34), (40, 74)))
    gy = 300 + 0.2656 * x
    S.speed_lines(d, lt, n=30, box=(0, 100, W, 600))
    for g, a in ((2, 0.2), (1, 0.38)):
        ghost(img, 'xiaok', pose, x - g * 60, gy - 0.39 * h - g * 16, h, a, facing=1, expr='cool', t=t)
    T.put(img, 'xiaok', pose, x, gy - 0.39 * h, h, facing=1, expr='cool', hold='bag', t=t)
    if drift:
        d = nd(img)
        rng = np.random.default_rng(int(t * 30))
        for _ in range(40):
            a = rng.uniform(math.pi * 0.85, math.pi * 1.45)
            ln = rng.uniform(14, 70)
            x0, y0 = x + 20, gy - 4
            d.line((x0, y0, x0 + math.cos(a) * ln, y0 + math.sin(a) * ln * 0.6 - rng.uniform(0, 26)), fill=(255, 220, 110, int(rng.uniform(150, 255))), width=3)
        caption(d, '小K 漂移 +1', x + 60, gy - 0.95 * h, 44, t, 28.75, color=(255, 200, 60))
    return img


def s_guard(t):
    lt = t - 29.3
    img = S.bg_booth().copy()
    d = nd(img)
    if 0.02 <= lt < 0.18:
        x = lerp(60, 1260, (lt - 0.02) / 0.16)
        d.line((x - 300, 300, x, 300), fill=(255, 196, 40, 220), width=30)
        S.speed_lines(d, t, n=10, box=(80, 200, W - 80, 420))
    if lt < 0.18:
        look, e = (-0.9, 0), 'deadpan'
    elif lt < 0.36:
        look, e = (0, 0), 'deadpan'
    else:
        look, e = (0.9, 0), 'confused'
    sip = lt < 0.5
    arm1 = {'ik': (0.04, 0.1), 'rel': 'Hc', 'bend': 1} if sip else {'ik': (0.12, 0.3), 'rel': 'N', 'bend': 1}
    T.put(img, 'guard', dict(view='front', bust=True, arms=((10, 5), arm1)), 640, 910, 1000, expr=e, look=look, t=t, hold='thermos')
    return img


def s_brake(t):
    lt = t - 30.0
    img = S.bg_shore().copy()
    S.ripples(img, t, 380)
    h = 360
    ground = 640
    if lt < 0.38:
        x = lerp(-140, 600, ease_out(lt / 0.38))
        pose = dict(view='side', lean=36, head=-22, arms=((-35, 20), (65, 80)), legs=((-22, 34), (40, 74)))
        T.put_on(img, 'xiaok', pose, x, ground, h, facing=1, expr='cool', hold='bag', t=t)
    elif lt < 0.85:
        x = 600 + 46 * ease_out((lt - 0.38) / 0.47)
        w = math.sin((lt - 0.38) * 40)
        pose = dict(view='side', lean=-20 + 8 * w, arms=((150 + 40 * w, 30), (120 - 40 * w, 30)), legs=((-12, 40), (38, 6)), hands=('open', 'open'))
        T.put_on(img, 'xiaok', pose, x, ground, h, facing=1, expr='panic', hold={'bag': 'W0'}, t=t)
        d = nd(img)
        rng = np.random.default_rng(int(t * 30))
        for _ in range(36):
            a = rng.uniform(math.pi * 0.9, math.pi * 1.4)
            ln = rng.uniform(14, 60)
            d.line((x + 70, ground - 4, x + 70 + math.cos(a) * ln, ground - 4 + math.sin(a) * ln * 0.6 - rng.uniform(0, 20)),
                   fill=(255, 220, 110, int(rng.uniform(150, 255))), width=3)
        S.dust(d, x + 40, ground - 10, (lt - 0.38) * 1.2, n=8, seed=3)
    else:
        tilt = 6 * math.sin((lt - 0.85) * 9)
        pose = dict(view='side', lean=18 + tilt, head=25, arms=((40, 10), (60, 6)), legs=((-3, 3), (4, 3)))
        T.put_on(img, 'xiaok', pose, 646, ground, h, facing=1, expr='nervous', hold='bag', t=t)
        caption(nd(img), '……', 760, 300, 60, t, 30.9, color=(255, 255, 255), stroke=(30, 30, 60))
    return img


def s_drone_up(t):
    lt = t - 31.5
    base = S.bg_shore().copy()
    S.ripples(base, t, 380)
    rise = smooth((lt - 0.65) / 0.85)
    tilt = 150 * rise
    h = 600
    glint = 0.28 <= lt < 0.55
    if lt < 0.6:
        arm1 = {'ik': (0.0, 0.03), 'rel': 'Hc', 'bend': 1}
        hold = None
    else:
        arm1 = {'ik': (0.08, -0.2), 'rel': 'P', 'bend': 1}
        hold = 'remote'
    if glint:
        S.radial_lines(base, 470, 300, (150, 200, 255), n=60, inner=260, a=120, seed=11, t=0)
    T.put_on(base, 'laozhou', dict(view='front', arms=((8, 6), arm1)), 470, 800, h, expr='cool', talk=talk('老周', t), glint=glint, hold=hold, t=t)
    d = nd(base)
    if glint:
        T.sparkle(d, 520, 230, 40, (255, 255, 255))
    dy = lerp(650, 300, rise)
    drone(d, 880, dy, s=1.5, t=t, rope=64)
    out = Image.new('RGB', (W, H))
    out.paste(base, (0, int(tilt)))
    out.paste(S.bg_lake().crop((0, 0, W, int(tilt) + 1)), (0, 0))
    return out


def s_airdrop(t):
    lt = t - 33.0
    ox = 320 * smooth(lt / 2.4)
    world = S.bg_lake(1800).copy()
    S.ripples(world, t, 380, seed=7)
    d = nd(world)
    for i, xw in enumerate((1060, 1116, 1172)):
        T.put_on(world, T.crowd_char(i + 2), dict(view='front', arms=((8, 6), {'ik': (0.2, -0.3), 'rel': 'N', 'bend': 1}), hands=('fist', 'point')),
                 xw, 336, 60, expr='shock', t=t)
    d = nd(world)

    def path(tt):
        return lerp(-160, 1700, (tt - 33.0) / 2.4), 230 + 26 * math.sin((tt - 33.0) * 2.2)

    for k in range(44):
        te = 33.0 + k * 0.06
        if te > t:
            break
        age = t - te
        px, py = path(te)
        S.puff(d, px + 8 * math.sin(k * 1.7), py + 80 - age * 16, 12 + age * 34, int(255 * clamp(1 - age / 2.0)))
    x, y = path(t)
    drone(d, x, 2 * 372 - y - 60, s=1.0, t=t, rope=-50, alpha=70, bag=False)
    drone(d, x, y, s=1.25, t=t, rope=56)
    return world.crop((int(ox), 0, int(ox) + W, H))


def s_crowd(t):
    lt = t - 35.4
    img = S.bg_shore().copy()
    S.ripples(img, t, 380)
    d = nd(img)
    for k in range(9):
        S.puff(d, 300 + k * 110, 140 + 10 * math.sin(k * 1.3) - k * 4, 26 + k * 5, 200 - k * 12)
    look = lt >= 0.12
    run = lt >= 0.4
    for i in range(6):
        h = 230 + (i % 3) * 22
        bx = 110 + i * 200
        c = T.crowd_char(i)
        if run:
            rt = lt - 0.4
            ph = 2 * math.pi * 3.3 * rt + i
            x = bx + 950 * rt
            pose = T.run(ph, 18)
            pose['head'] = -28
            T.put_on(img, c, pose, x, 690 + T.bob(ph, h), h, facing=1, expr='love' if i % 2 else 'excited', t=t + i)
        else:
            pose = T.stand('side')
            pose['head'] = -32 if look else 0
            T.put_on(img, c, pose, bx, 690, h, facing=1 if i % 2 else -1, expr=dict(eyes='shock', brows='high', mouth='O', fx=('exclaim',)) if look else 'neutral',
                     t=t + i)
    return img


def s_facepalm(t):
    lt = t - 36.5
    img = S.bg_balcony().copy()
    d = nd(img)
    for k in range(16):
        S.puff(d, 100 + k * 70, 300 - k * 6 + 6 * math.sin(k), 14 + k * 1.5, 120)
    S.telescope(d, 300, 720, aim=-1, s=1.6)
    up = smooth((lt - 0.08) / 0.3)
    arm = {'ik': (lerp(0.15, 0.04, up), lerp(0.3, 0.0, up)), 'rel': 'Hc', 'bend': 1}
    e = dict(eyes='half', brows='worried', mouth='flat', fx=('gloom',))
    T.put_on(img, 'xingxing', dict(view='front', arms=((6, 4), arm), hands=('fist', 'open')), 720, 820 + 4 * math.sin(lt * 5), 660, expr=e,
             talk=talk('星星', t), t=t, wind=0.15)
    return S.zoom(img, 1.0 + 0.05 * smooth(lt / 1.5), 720, 330)


def s_door_close(t):
    lt = t - 38.0
    img = S.bg_door().copy()
    d = nd(img)
    w = lerp(20, 170, smooth(lt / 1.0))
    d.rectangle((470, 278, 640, 640), fill=(200, 226, 240, 110), outline=(90, 96, 110, 255), width=6)
    d.rectangle((810 - w, 278, 810, 640), fill=(200, 226, 240, 140), outline=(90, 96, 110, 255), width=6)
    edge = (810 - w, 470)
    h = 470
    J = T.joints(T.CH['suguan'], dict(view='side'), -1)
    gy = 652
    py = gy - (max(J['A0'][1], J['A1'][1]) + 0.045) * h
    arm = {'ik': ((900 - edge[0]) / h, (edge[1] - py) / h), 'rel': 'P', 'bend': 1}
    T.put(img, 'suguan', dict(view='side', arms=((-5, 10), arm), legs=((-4, 3), (5, 3)), hands=('fist', 'open')), 900, py, h, facing=-1,
          expr='stern', glint=int(t * 3) % 2 == 0, t=t)
    return img


def s_stairs(t):
    lt = t - 39.0
    img = S.bg_stairs().copy()
    h = 400
    x = lerp(160, 880, lt / 1.0)
    ph = 2 * math.pi * 2.2 * lt
    y = 330 + 0.2857 * x - 0.43 * h + T.bob(ph, h)
    T.put(img, 'dacong', T.run(ph, 12), x, y, h, facing=1, expr='cry', t=t)
    d = nd(img)
    for k in range(3):
        T.drop(d, x - 60 - k * 40, y - 0.45 * h + 10 * k, 8)
    if lt >= 0.3:
        u = (lt - 0.3) / 0.7
        flipflop(d, x - 120 - 200 * u, y + 0.4 * h - 300 * u + 340 * u * u, lt * 14, 1.3)
    return img


def s_fall(t):
    lt = t - 40.0
    img = S.vgrad(W, H, [(0, (12, 14, 42)), (1, (60, 44, 96))])
    d = nd(img)
    S.stars(d, 81, 120, (0, 0, W, 500))
    d.rectangle((0, 600, W, H), fill=(80, 82, 96, 255))
    d.rectangle((420, 560, 860, H), fill=(255, 226, 170, 255))
    by = lerp(-80, 330, lt / 1.0)
    for k in range(7):
        S.puff(d, 640 + 8 * math.sin(k * 1.9), by - 70 - k * 34, 16 + k * 6, 230 - k * 28)
    S.glow(img, 640, by, 120, (255, 220, 130), 0.4)
    d = nd(img)
    T.draw_bag(d, 640, by, 100, 3)
    up = smooth(lt / 0.5)
    a0 = {'ik': (-lerp(0.12, 0.3, up), lerp(0.1, -0.16, up)), 'rel': 'N', 'bend': -1}
    a1 = {'ik': (lerp(0.12, 0.3, up), lerp(0.1, -0.16, up)), 'rel': 'N', 'bend': 1}
    T.put(img, 'dacong', dict(view='front', bust=True, arms=(a0, a1), hands=('open', 'open')), 640, 900, 900, expr='excited', look=(0, -1), t=t)
    return img


def s_dive(t):
    lt = t - 41.0
    img = S.bg_door().filter(ImageFilter.GaussianBlur(5))
    S.sunburst(img, 640, 380, (0, 0, 0), (255, 200, 90), 20, t * 0.6)
    img = Image.blend(S.bg_door().filter(ImageFilter.GaussianBlur(5)), img, 0.35)
    S.glow(img, 640, 380, 300, (255, 220, 140), 0.35)
    h = 430
    x = lerp(240, 760, lt / 1.0)
    rot = lerp(70, 86, lt)
    pose = dict(view='side', rot=rot, arms=({'ik': (0.06, -0.72), 'rel': 'P', 'bend': 1}, {'ik': (0.1, -0.74), 'rel': 'P', 'bend': 1}),
                legs=((-12, 10), (5, 25)), hands=('open', 'open'))
    caught = lt >= 0.45
    P = T.put(img, 'dacong', pose, x, 430, h, facing=1, expr='determined', hold='bag' if caught else None, t=t)
    d = nd(img)
    if not caught:
        hx, hy = P['W1']
        u2 = lt / 0.45
        T.draw_bag(d, lerp(hx + 150, hx, u2), lerp(hy - 240, hy + 30, u2), 0.15 * h, 2)
    else:
        impact(d, P['W1'][0] + 30, P['W1'][1], 60 * (1 - clamp((lt - 0.45) / 0.3)) + 1)
    S.speed_lines(d, lt * 0.3, n=16)
    caption(d, '接住泼天的富贵', 640, 140, 70, t, 41.35, color=(255, 214, 80))
    return img


@lru_cache(maxsize=None)
def panel_bg(label):
    img = S.bg_door().resize((634, 354), Image.LANCZOS)
    d = nd(img)
    d.rectangle((210, 75, 425, 112), fill=(120, 60, 56, 255), outline=INK, width=2)
    d.text((317, 93), label, font=F('Black', 24), fill=(255, 220, 150, 255), anchor='mm')
    return img


PANELS = [('8 号 楼', 'dacong', 'bag', 'determined'), ('3 号 楼', 'afei', None, 'fired'), ('6 号 楼', 'xiaok', None, 'cool'),
          ('7 号 楼', 'laozhou', 'remote', 'cool')]


def panel(t, label, key, hold, expr):
    img = panel_bg(label).copy()
    d = nd(img)
    close = smooth((t - 42.0) / 1.2)
    w = lerp(84, 4, close)
    d.rectangle((317 - w, 138, 317 + w, 318), fill=(255, 236, 196, 255))
    d.rectangle((228, 138, 317 - w, 318), fill=(200, 226, 240, 170), outline=(90, 96, 110, 255), width=3)
    d.rectangle((317 + w, 138, 405, 318), fill=(200, 226, 240, 170), outline=(90, 96, 110, 255), width=3)
    u = clamp((t - 42.15) / 1.0)
    x = lerp(-140, 330, u)
    pose = dict(view='side', rot=82, arms=({'ik': (0.06, -0.72), 'rel': 'P', 'bend': 1}, {'ik': (0.1, -0.74), 'rel': 'P', 'bend': 1}),
                legs=((-12, 10), (5, 25)), hands=('open', 'open'))
    T.put(img, key, pose, x, 268, 190, facing=1, expr=expr, hold=hold, t=t, glint=(key == 'laozhou'))
    if t >= 43.2:
        caption(nd(img), '咔哒', 317, 120, 40, t, 43.2, color=(255, 255, 255))
    return img


def s_four(t):
    img = Image.new('RGB', (W, H), (0, 0, 0))
    for i, (label, key, hold, e) in enumerate(PANELS):
        img.paste(panel(t, label, key, hold, e), (4 + (i % 2) * 638, 4 + (i // 2) * 358))
    caption(nd(img), '同一秒，四栋楼', 640, 360, 52, t, 42.05, color=(255, 255, 255))
    return img


def s_victory(t):
    lt = t - 43.6
    img = S.bg_victory(t)
    d = nd(img)
    s = ease_back(clamp(lt / 0.3))
    T.draw_bucket(d, 640, 300, 1.5 * s, 3)
    for i, (key, x, y) in enumerate((('dacong', 640, 520), ('afei', 300, 230), ('xiaok', 980, 230), ('laozhou', 240, 470), ('xingxing', 1040, 470))):
        t0 = 43.7 + i * 0.08
        if t >= t0:
            sc = ease_back(clamp((t - t0) / 0.25))
            size = int(150 * sc) if i else int(170 * sc)
            if size > 8:
                ic = T.head_icon(key, size, 'laugh' if i != 2 else 'happy', t=t)
                img.paste(ic, (int(x - size / 2), int(y - size / 2 + 6 * math.sin(t * 6 + i))), ic)
    d = nd(img)
    caption(d, '大吉大利，今晚吃鸡', 640, 640, 80, t, 43.75, color=(255, 214, 80), stroke=(90, 40, 0))
    S.confetti(d, t, seed=3, n=80)
    return img


def s_gaze(t):
    lt = t - 45.0
    img = S.bg_lobby().copy()
    img = Image.blend(img, Image.new('RGB', (W, H), (40, 20, 70)), 0.45 * smooth(lt / 0.3))
    S.radial_lines(img, 900, 300, (60, 30, 100), n=60, inner=240, a=160, seed=13, t=0)
    S.glow(img, 900, 300, 260, (120, 60, 200), 0.3)
    hug = {'ik': (0.12, 0.05), 'rel': 'N', 'bend': 1}
    T.put(img, 'dacong', dict(view='front', rot=90, arms=(hug, {'ik': (0.1, 0.07), 'rel': 'N', 'bend': -1}), legs=((5, 5), (8, 10))),
          260, 600, 420, expr='nervous', t=t, hold={'bag': 'W1'})
    sip = smooth((t - 45.1) / 0.2) * (1 - smooth((t - 45.55) / 0.25))
    arm1 = {'ik': (lerp(0.14, 0.05, sip), lerp(-0.18, -0.36, sip)), 'rel': 'P', 'bend': 1}
    e = 'stern' if t < 46.45 else 'sly'
    T.put_on(img, 'suguan', dict(view='side', head=22, arms=((-5, 10), arm1), legs=((-4, 3), (5, 3))), 880, 712, 540, facing=-1, expr=e,
             hold='thermos', talk=talk('宿管阿姨', t), glint=t < 46.45, t=t)
    d = nd(img)
    if t >= 45.1:
        a = clamp((t - 45.1) / 0.2)
        d.rounded_rectangle((250, 50, 1030, 108), radius=12, fill=(70, 30, 120, int(225 * a)), outline=(200, 160, 255, int(255 * a)), width=3)
        d.text((640, 79), '宿管阿姨 使用了【凝视】，全场被硬控2秒', font=F('Bold', 28), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return S.zoom(img, 1.0 + 0.06 * smooth(lt / 1.8), 640, 420)


def s_eat(t):
    lt = t - 46.8
    img = S.bg_dorm().copy()
    d = nd(img)
    cheer = 0.5 + 0.5 * math.sin(lt * 9)
    up = dict(view='front', arms=((150 + 12 * cheer, 10), (150 + 12 * cheer, 10)), hands=('open', 'open'))
    T.put_on(img, 'roomA', up, 300, 790, 520, expr='laugh', t=t)
    T.put_on(img, 'roomB', dict(view='front', arms=((8, 6), {'ik': (0.05, 0.06), 'rel': 'Hc', 'bend': 1})), 1000, 790, 520, expr='drool', t=t)
    slapped = t >= 47.75
    reach = smooth((t - 47.35) / 0.3) * (1 - smooth((t - 47.8) / 0.15))
    c_arm = {'ik': (lerp(-0.22, -0.46, reach), lerp(0.08, 0.02, reach)), 'rel': 'N', 'bend': -1}
    T.put_on(img, 'roomC', dict(view='front', arms=(c_arm, (20, 10))), 1170, 800, 520, expr='cry' if slapped else 'excited', t=t)
    slap = smooth((t - 47.68) / 0.07) * (1 - smooth((t - 47.95) / 0.2))
    put_wing = smooth((t - 46.9) / 0.4)
    arm1 = {'ik': (lerp(0.1, 0.32, put_wing) + 0.12 * slap, lerp(0.15, 0.08, put_wing) - 0.05 * slap), 'rel': 'N', 'bend': 1}
    T.put_on(img, 'dacong', dict(view='front', arms=((150, 10), arm1), hands=('open', 'open')), 680, 800, 560,
             expr='smug' if slap > 0.1 or slapped else 'happy', hold='wing' if t < 47.25 else None, t=t)
    d = nd(img)
    d.rectangle((330, 560, 990, 584), fill=(176, 136, 100, 255), outline=INK, width=3)
    d.rectangle((330, 584, 990, H), fill=(140, 104, 76, 255), outline=INK, width=3)
    T.draw_bucket(d, 540, 500, 1.0, 3)
    T.opoly(d, [(820, 470), (930, 470), (930, 540), (820, 540)], (250, 250, 246), 3)
    d.rectangle((830, 452, 920, 486), fill=(255, 230, 90, 255), outline=INK, width=2)
    d.text((875, 469), '星星的', font=F('Black', 20), fill=(80, 60, 20, 255), anchor='mm')
    if 47.75 <= t < 48.1:
        impact(d, 1000, 420, 60, (255, 255, 255))
        caption(d, '啪！', 1000, 340, 70, t, 47.75, color=(255, 80, 80), stroke=(255, 255, 255))
    S.confetti(d, t, seed=9, n=30, box=(0, 0, W, 500), speed=120)
    return img


def wallet(img, t):
    sx0, sy0, sx1, sy1 = SC1.phone_frame(img, 720, 30, 360, 660)
    d = nd(img)
    cx = (sx0 + sx1) / 2
    d.text((cx, sy0 + 70), '钱包 · 转账', font=F('Bold', 22), fill=(20, 20, 26, 255), anchor='mm')
    d.text((sx0 + 24, sy0 + 130), '转给：TT语音组队的 4 位搭子', font=F('Medium', 18), fill=(90, 90, 100, 255), anchor='lm')
    d.text((sx0 + 24, sy0 + 170), '每人 ¥50', font=F('Bold', 22), fill=(20, 20, 26, 255), anchor='lm')
    d.text((sx0 + 24, sy0 + 250), '¥ 200.00', font=F('Black', 54), fill=(20, 20, 26, 255), anchor='lm')
    d.rounded_rectangle((sx0 + 24, sy1 - 120, sx1 - 24, sy1 - 64), radius=14, fill=(60, 180, 100, 255))
    d.text((cx, sy1 - 92), '确认转账', font=F('Bold', 24), fill=(255, 255, 255, 255), anchor='mm')
    d.text((cx, sy1 - 30), '示意界面', font=F('Medium', 14), fill=(150, 150, 160, 255), anchor='mm')
    if t >= 49.7:
        u = ease_back(clamp((t - 49.7) / 0.25))
        cy = 370
        d.rectangle((sx0, sy0, sx1, sy1), fill=(0, 0, 0, 120))
        d.rounded_rectangle((cx - 150 * u, cy - 110 * u, cx + 150 * u, cy + 110 * u), radius=18, fill=(255, 255, 255, 255))
        d.text((cx, cy - 60 * u), '余额不足', font=F('Black', max(8, int(30 * u))), fill=(220, 40, 50, 255), anchor='mm')
        d.text((cx, cy - 10 * u), '零钱', font=F('Medium', max(8, int(20 * u))), fill=(90, 90, 100, 255), anchor='mm')
        d.text((cx, cy + 50 * u), '¥ 3.50', font=F('Black', max(8, int(56 * u))), fill=(20, 20, 26, 255), anchor='mm')


def s_wallet(t):
    img = S.bg_dorm_blur().copy()
    stone = smooth((t - 50.05) / 0.3)
    e = 'smile' if t < 49.7 else ('shock' if t < 50.05 else 'dead')
    pose = dict(view='front', bust=True, arms=({'ik': (-0.05, 0.1), 'rel': 'N', 'bend': -1}, {'ik': (0.07, 0.1), 'rel': 'N', 'bend': 1}))
    T.put(img, 'dacong', pose, 330, 860, 900, expr=e, talk=talk('大聪明', t), t=t, hold='phone', stone=stone)
    wallet(img, t)
    if t >= 50.05:
        img = S.grade(img, (0.75, 0.75, 0.8), (10, 10, 14))
        d = nd(img)
        caption(d, '空气突然安静', 640, 110, 58, t, 50.05, color=(255, 255, 255), stroke=(0, 0, 0))
        p = (t - 50.05) / 0.6
        V1.crow(d, lerp(1380, -150, p), 230 - 60 * p, t, caw=(t < 50.4))
    z = 1.0 + 0.22 * smooth((t - 49.6) / 0.2)
    return S.zoom(img, z, 640, 380)


SEATS = [('大聪明', 'dacong'), ('阿飞', 'afei'), ('小K', 'xiaok'), ('老周', 'laozhou'), ('星星', 'xingxing')]


def seat_xy(i):
    return 400 + (i % 3) * 240, 255 + (i // 3) * 230


def tt_panel(t, balance):
    img = S.bg_dorm_blur().copy()
    d = nd(img)
    d.rounded_rectangle((230, 100, 1050, 625), radius=28, fill=(10, 14, 22, 235), outline=(255, 255, 255, 50), width=2)
    SC1.title(d, 'TT语音 · 组队中')
    d.text((640, 140), '南门炸鸡运输队', font=F('Bold', 28), fill=(255, 255, 255, 255), anchor='mm')
    all_talk = speaking('全员', t)
    coin_in = t >= 53.5
    for i in range(6):
        cx, cy = seat_xy(i)
        r = 58
        if i == 5:
            lit = t >= 53.4
            flip = abs(math.cos(math.pi * clamp((t - 53.25) / 0.3))) if 53.25 <= t < 53.55 else 1.0
            if speaking('宿管阿姨', t):
                ph = (t * 4) % 1
                d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), outline=(60, 235, 140, 255), width=4)
                r2 = r + 8 + 14 * ph
                d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=(60, 235, 140, int(160 * (1 - ph))), width=3)
            if lit:
                ic = T.head_icon('suguan', 2 * r, 'wink', talk=talk('宿管阿姨', t), t=t, bg=(250, 200, 190))
            else:
                ic = Image.new('RGBA', (2 * r, 2 * r), (0, 0, 0, 0))
                ImageDraw.Draw(ic).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=(62, 62, 70, 255))
                ImageDraw.Draw(ic).text((r, r), '?', font=F('Black', 50), fill=(150, 150, 158, 255), anchor='mm')
            w = max(2, int(2 * r * flip))
            ic = ic.resize((w, 2 * r))
            img.paste(ic, (int(cx - w / 2), int(cy - r)), ic)
            d = nd(img)
            d.text((cx, cy + r + 28), '8号楼·宿管阿姨' if lit else '神秘人', font=F('Bold', 22), fill=(255, 255, 255, 255) if lit else (150, 150, 158, 255),
                   anchor='mm')
            continue
        name, key = SEATS[i]
        tk = talk(name, t)
        if speaking(name, t) or all_talk:
            ph = (t * 4) % 1
            d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), outline=(60, 235, 140, 255), width=4)
            r2 = r + 8 + 14 * ph
            d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=(60, 235, 140, int(160 * (1 - ph))), width=3)
        if i == 0:
            e = 'moved' if coin_in else ('dead' if t < 53.4 else 'shock')
        elif all_talk:
            e = 'happy'
        else:
            e = {'afei': 'laugh', 'xiaok': 'cool', 'laozhou': 'smile', 'xingxing': 'smile'}[key]
        ic = T.head_icon(key, 2 * r, e, talk=tk + (0.6 if all_talk else 0), t=t)
        img.paste(ic, (int(cx - r), int(cy - r)), ic)
        d = nd(img)
        d.text((cx, cy + r + 28), name, font=F('Bold', 22), fill=(255, 255, 255, 255), anchor='mm')
    cx, cy = seat_xy(0)
    d.rounded_rectangle((cx - 96, cy - 58 - 52, cx + 96, cy - 58 - 14), radius=10, fill=(255, 214, 80, 255), outline=INK, width=2)
    d.text((cx, cy - 58 - 33), f'余额 ¥{balance:.2f}', font=F('Bold', 20), fill=(60, 40, 0, 255), anchor='mm')
    return img, d


def coin_toast(d, t, t0, src, dst):
    u = (t - t0) / 0.45
    if not 0 <= u <= 1:
        return
    x = lerp(src[0], dst[0], ease_out(u))
    y = lerp(src[1], dst[1], ease_out(u)) - 60 * math.sin(math.pi * u)
    d.rounded_rectangle((x - 60, y - 21, x + 60, y + 21), radius=10, fill=(255, 214, 80, 255), outline=INK, width=2)
    d.text((x, y), '收款 +50', font=F('Bold', 20), fill=(60, 40, 0, 255), anchor='mm')


def s_vme(t):
    n_in = sum(1 for k in range(4) if t >= 53.05 + k * 0.12 + 0.45)
    img, d = tt_panel(t, 3.5 + 50 * n_in)
    for k in range(4):
        coin_toast(d, t, 53.05 + k * 0.12, seat_xy(k + 1), seat_xy(0))
    return img


def s_mystery(t):
    n_in = 4 + (1 if t >= 55.45 + 0.45 else 0)
    img, d = tt_panel(t, 3.5 + 50 * n_in)
    for k in range(4):
        coin_toast(d, t, 53.05 + k * 0.12, seat_xy(k + 1), seat_xy(0))
    coin_toast(d, t, 55.45, seat_xy(5), seat_xy(0))
    return img


def s_250(t):
    lt = t - 55.6
    if lt < 0.35:
        img = S.bg_victory(t)
        d = nd(img)
        s = 1.6 - 0.6 * ease_out(clamp(lt / 0.12))
        caption(d, '收款合计：250元', 640, 360, int(96 * s), t, 55.6, color=(255, 214, 80), stroke=(90, 40, 0), pop=False)
        return img
    img = S.bg_dorm_blur().copy()
    S.radial_lines(img, 980, 380, (255, 255, 255), n=60, inner=300, a=110, seed=17, t=0)
    shout = t >= 56.05
    for i, key in enumerate(('roomA', 'roomB', 'roomC')):
        e = 'scream' if shout else 'judge'
        T.put(img, key, dict(view='front', bust=True, arms=((10, 5), (10, 5))), 200 + i * 230, 820, 760, expr=e, look=(0.9, 0), t=t,
              talk=talk('三个室友', t))
    T.put(img, 'dacong', dict(view='front', bust=True, arms=((10, 5), (10, 5))), 1010, 900, 980, expr='cry' if shout else 'moved', t=t)
    d = nd(img)
    d.rounded_rectangle((440, 40, 840, 100), radius=14, fill=(255, 214, 80, 240), outline=INK, width=3)
    d.text((640, 70), '收款合计：250元', font=F('Black', 34), fill=(60, 40, 0, 255), anchor='mm')
    if shout:
        caption(d, '250', 1010, 230 - 20 * clamp((t - 56.05) / 0.5), 80, t, 56.05, color=(255, 90, 90), stroke=(255, 255, 255))
    return img


END_CAST = [
    # (key, x, ground, h, pose, expr, extra)
    ('guard', 140, 630, 210, dict(view='front', arms=((8, 6), {'ik': (0.12, -0.1), 'rel': 'N', 'bend': 1}), hands=('fist', 'thumb')), 'happy', {}),
    ('girl', 1090, 630, 200, dict(view='front', arms=((150, 10), (20, 8)), hands=('open', 'fist')), 'happy', {}),
    ('boy', 1190, 630, 210, dict(view='front', arms=((20, 8), {'ik': (0.08, 0.12), 'rel': 'N', 'bend': 1})), 'happy', dict(hold='cup')),
    ('roomA', 230, 720, 300, dict(view='front', arms=((150, 10), (150, 10)), hands=('open', 'open')), 'laugh', {}),
    ('xiaok', 370, 720, 300, dict(view='front', arms=((8, 6), {'ik': (0.16, -0.12), 'rel': 'N', 'bend': 1}), hands=('fist', 'thumb')), 'cool', {}),
    ('afei', 500, 720, 310, dict(view='front', arms=((95, 95), (95, 95))), 'fired', {}),
    ('xingxing', 790, 720, 300, dict(view='front', arms=((8, 6), {'ik': (0.06, 0.08), 'rel': 'Hc', 'bend': 1})), 'happy', dict(hold='wing')),
    ('laozhou', 920, 720, 300, dict(view='front', arms=((8, 6), {'ik': (0.03, 0.03), 'rel': 'Hc', 'bend': 1})), 'smile', dict(glint=True)),
    ('suguan', 1050, 720, 300, dict(view='front', arms=((8, 6), {'ik': (0.1, -0.1), 'rel': 'N', 'bend': 1})), 'wink', dict(hold='wing')),
    ('roomB', 1170, 720, 290, dict(view='front', arms=((8, 6), {'ik': (0.05, 0.06), 'rel': 'Hc', 'bend': 1})), 'drool', {}),
    ('roomC', 90, 720, 290, dict(view='front', arms=((150, 10), (20, 10)), hands=('open', 'fist')), 'laugh', {}),
]


def s_end(t):
    lt = t - 57.4
    img = S.bg_end().copy()
    d = nd(img)
    for k in range(3):
        tt = (t * 0.8 + k * 0.33) % 1
        fx, fy = 260 + k * 380, 120 + 40 * k
        if tt < 0.7:
            r = 90 * ease_out(tt / 0.7)
            for j in range(14):
                a = j * math.pi / 7
                col = [(255, 120, 140), (255, 220, 100), (140, 220, 255)][k]
                d.line(((fx + math.cos(a) * r * 0.6, fy + math.sin(a) * r * 0.6), (fx + math.cos(a) * r, fy + math.sin(a) * r)),
                       fill=col + (int(255 * (1 - tt / 0.7)),), width=3)
    for key, x, g, h, pose, e, extra in END_CAST:
        T.put_on(img, key, pose, x, g + 4 * math.sin(t * 7 + x), h, expr=e, t=t, shadow=True, **extra)
    P = T.put_on(img, 'dacong', dict(view='front', arms=((160, 12), (160, 12)), hands=('open', 'open')), 645, 720 + 6 * math.sin(t * 7), 330,
                 expr='laugh', t=t, shadow=True)
    d = nd(img)
    T.draw_bucket(d, (P['W0'][0] + P['W1'][0]) / 2, min(P['W0'][1], P['W1'][1]) - 40, 0.9, 3)
    S.confetti(d, t, seed=21, n=70, box=(0, 0, W, 460), speed=140)
    a = clamp((t - 57.5) / 0.3)
    d.rounded_rectangle((250, 22, 1030, 180), radius=24, fill=(10, 12, 24, int(170 * a)))
    caption(d, '一个人很难吃鸡，一群人就行。', 640, 72, 50, t, 57.5, color=(255, 255, 255), stroke=(0, 0, 0), pop=False)
    caption(d, '在TT语音，永远有人并肩相伴。', 640, 140, 40, t, 58.0, color=(255, 214, 80), stroke=(0, 0, 0), pop=False)
    if t >= 58.6:
        a = clamp((t - 58.6) / 0.3)
        d.rounded_rectangle((1120, 30, 1250, 120), radius=20, fill=(255, 255, 255, int(235 * a)), outline=INK, width=3)
        d.text((1185, 66), 'TT', font=F('Black', 44), fill=(30, 30, 40, int(255 * a)), anchor='mm')
        d.text((1185, 104), 'Logo位置', font=F('Medium', 14), fill=(120, 120, 130, int(255 * a)), anchor='mm')
    return img


SHOTS = [
    (0.0, 1.4, s_black, {'rider'}), (1.4, 4.0, s_dorm_call, {'dacong', 'roomA', 'roomB', 'roomC', 'rider'}),
    (4.0, 4.3, lambda t: s_turn(t, 'roomA', 4.0), {'roomA'}), (4.3, 4.6, lambda t: s_turn(t, 'roomB', 4.3), {'roomB'}),
    (4.6, 4.9, lambda t: s_turn(t, 'roomC', 4.6), {'roomC'}), (4.9, 6.6, s_roomA, {'roomA'}), (6.6, 7.45, s_roomB, {'roomB'}),
    (7.45, 10.35, s_phone, {'dacong'}), (10.35, 11.0, s_campus, set()), (11.0, 19.0, None, ALL),
    (19.0, 20.6, s_balcony, {'xingxing'}), (20.6, 23.0, s_pov, set()), (23.0, 24.5, s_afei_run, {'afei'}), (24.5, 26.3, s_couple, set()),
    (26.3, 27.0, s_to_slope, {'afei', 'xiaok'}), (27.0, 28.2, s_handoff, {'afei', 'xiaok'}), (28.2, 29.3, s_skate, {'xiaok'}),
    (29.3, 30.0, s_guard, set()), (30.0, 31.5, s_brake, {'xiaok'}), (31.5, 33.0, s_drone_up, {'laozhou'}), (33.0, 35.4, s_airdrop, set()),
    (35.4, 36.5, s_crowd, set()), (36.5, 38.0, s_facepalm, {'xingxing'}), (38.0, 39.0, s_door_close, {'suguan'}),
    (39.0, 40.0, s_stairs, {'dacong'}), (40.0, 41.0, s_fall, {'dacong'}), (41.0, 42.0, s_dive, {'dacong'}), (42.0, 43.6, s_four, ALL),
    (43.6, 45.0, s_victory, ALL - {'roomB'}), (45.0, 46.8, s_gaze, {'dacong', 'suguan'}), (46.8, 48.2, s_eat, {'dacong', 'roomA', 'roomB', 'roomC'}),
    (48.2, 50.6, s_wallet, {'dacong'}), (50.6, 53.1, s_vme, ALL), (53.1, 55.6, s_mystery, ALL),
    (55.6, 57.4, s_250, {'roomA', 'roomB', 'roomC', 'dacong'}), (57.4, 60.01, s_end, ALL),
]


def ttbar(img, t):
    d = nd(img)
    d.rounded_rectangle((884, 14, 1258, 62), radius=24, fill=(8, 12, 18, 215), outline=(255, 255, 255, 45), width=1)
    for i in range(6):
        cx, cy, r = 912 + i * 57, 38, 18
        if i == 5:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(62, 62, 70, 255))
            d.text((cx, cy), '?', font=F('Bold', 20), fill=(150, 150, 158, 255), anchor='mm')
            continue
        name, key = SEATS[i]
        if speaking(name, t):
            ph = (t * 4) % 1
            d.ellipse((cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5), outline=(60, 235, 140, 255), width=3)
            r2 = r + 5 + 10 * ph
            d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=(60, 235, 140, int(160 * (1 - ph))), width=2)
            ic = T.head_icon(key, 36, 'smile', talk=talk(name, t), t=t)
        else:
            ic = icon(key, 36)
        img.paste(ic, (cx - 18, cy - 18), ic)
        d = nd(img)


def voice_inset(img, t, onscreen):
    for s, e, ln in WIN:
        key = WHO_KEY.get(ln['who'])
        if key and s <= t < e + 0.1 and key not in onscreen:
            a = clamp((t - s) / 0.12)
            r = 52
            cx, cy = 86, 560
            d = nd(img)
            ph = (t * 3) % 1
            d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(10, 12, 20, int(200 * a)), outline=(60, 235, 140, int(255 * a)), width=4)
            rr = r + 8 + 16 * ph
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(60, 235, 140, int(150 * (1 - ph) * a)), width=3)
            ic = T.head_icon(key, 2 * r, 'smile', talk=talk(ln['who'], t), t=t)
            if a < 1:
                ic.putalpha(ic.getchannel('A').point(lambda v: int(v * a)))
            img.paste(ic, (cx - r, cy - r), ic)
            d = nd(img)
            d.rounded_rectangle((cx - 50, cy + r + 8, cx + 50, cy + r + 36), radius=10, fill=(10, 12, 20, int(220 * a)))
            d.text((cx, cy + r + 22), ln['who'], font=F('Bold', 18), fill=(255, 255, 255, int(255 * a)), anchor='mm')
            break


def overlays(img, t, onscreen):
    d = nd(img)
    if 38.0 <= t < 43.4:
        p = 0.5 + 0.5 * math.sin(2 * math.pi * 2.2 * t)
        for k in range(6):
            a = int((40 + 50 * p) * (1 - k / 6))
            d.rectangle((k * 12, k * 12, W - k * 12, H - k * 12), outline=(220, 20, 30, a), width=12)
    if 4.0 <= t < 7.45 or 19.0 <= t < 43.6:
        SC1.countdown_pill(d, countdown(t), t, urgent=(38.0 <= t < 43.6))
    if 4.0 <= t < 7.45:
        caption(d, '距离门禁：8分钟｜距离南门：3公里', 640, 104, 30, t, 4.0, color=(255, 255, 255), stroke=(0, 0, 0))
    if 19.0 <= t < 43.6:
        SC1.title(d)
        ttbar(img, t)
        d = nd(img)
    SC1.killfeed(d, t, 24.7, [('阿飞', (255, 90, 100)), ('运送了', (255, 255, 255)), ('炸鸡桶', (255, 214, 80)), ('800米', (255, 255, 255))])
    SC1.killfeed(d, t, 33.2, [('老周', (100, 170, 255)), ('呼叫了', (255, 255, 255)), ('空投', (255, 214, 80))])
    voice_inset(img, t, onscreen)
    d = nd(img)
    cur = None
    for s, e, ln in WIN:
        if s <= t < e + 0.12 and ln.get('subtitle', True):
            cur = ln
    if cur is not None:
        txt = cur.get('show', cur['text'])
        if cur['who'] == '旁白':
            SC1.subtitle(d, f'（旁白）{txt}', color=(200, 220, 255))
        else:
            SC1.subtitle(d, f"{cur['who']}：{txt}")
    d.text((20, 708), '样片｜代码生成', font=F('Medium', 15), fill=(255, 255, 255, 120), anchor='ls')
    return img


def render(t, HA, hvlen):
    if 11.0 <= t < 19.0:
        return hero_frame(t, HA, hvlen)
    for t0, t1, fn, onscreen in SHOTS:
        if t0 <= t < t1 and fn is not None:
            img = fn(t)
            break
    else:
        img, onscreen = Image.new('RGB', (W, H)), set()
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return overlays(img, t, onscreen)


SHEET = [0.5, 1.8, 2.6, 4.15, 4.45, 5.6, 7.0, 8.8, 10.0, 10.6, 11.6, 14.0, 16.5, 18.5, 19.6, 21.2, 22.5, 23.2, 23.9, 24.75,
         25.7, 26.7, 27.6, 28.9, 29.7, 30.6, 31.9, 32.7, 34.3, 35.9, 37.2, 38.5, 39.5, 40.6, 41.6, 43.25, 44.3, 46.2, 47.8, 49.0,
         50.3, 51.5, 54.2, 56.4, 59.0]


def sheet(frames, path):
    cols = 5
    tw, th, lab = 320, 180, 24
    rows = math.ceil(len(frames) / cols)
    out = Image.new('RGB', (cols * tw, rows * (th + lab)), (12, 12, 16))
    d = ImageDraw.Draw(out)
    for i, (t, fr) in enumerate(frames):
        x, y = (i % cols) * tw, (i // cols) * (th + lab)
        d.text((x + 8, y + lab // 2), f'{t:.1f}秒', font=F('Bold', 16), fill=(255, 255, 255), anchor='lm')
        out.paste(fr.resize((tw, th), Image.LANCZOS), (x, y + lab))
    out.save(path)


def sfx_chime():
    tt = np.arange(int(SR * 0.7)) / SR
    x = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) for f, d in ((2093, 0.25), (2637, 0.2), (3136, 0.15)))
    return hero.norm(x * np.minimum(1, tt / 0.003))


def sfx_crack():
    n = int(SR * 0.45)
    rng = np.random.default_rng(31)
    y = np.zeros(n)
    for k in range(9):
        i = int(rng.uniform(0, 0.3) * SR)
        tt = np.arange(int(SR * 0.05)) / SR
        burst = rng.standard_normal(len(tt)) * np.exp(-tt / 0.006)
        y[i:i + len(tt)] += burst[:max(0, min(len(tt), n - i))]
    return hero.norm(np.diff(y, prepend=0))


def sfx_low(d=1.6):
    tt = np.arange(int(SR * d)) / SR
    x = (np.sin(2 * np.pi * 55 * tt) + 0.5 * np.sin(2 * np.pi * 58.3 * tt) + 0.3 * np.sin(2 * np.pi * 110 * tt))
    return hero.norm(x * np.minimum(1, tt / 0.3) * np.clip((d - tt) / 0.4, 0, 1))


def extra_sfx():
    pop, whoosh = SA.sfx_pop(), hero.sfx_whoosh(0.3)
    ex = [(whoosh, 1.42, 0.3), (whoosh, 2.05, 0.3), (SA.sfx_dong(), 2.05, 0.7), (sfx_chime(), 4.05, 0.3), (sfx_chime(), 4.92, 0.25),
          (hero.sfx_whoosh(0.5), 10.3, 0.4), (sfx_chime(), 19.15, 0.3), (SA.sfx_thud(), 23.38, 0.55), (hero.sfx_whoosh(0.4), 23.4, 0.5),
          (pop, 25.45, 0.3), (pop, 29.7, 0.3), (sfx_chime(), 31.78, 0.4), (sfx_low(1.7), 45.05, 0.4), (sfx_chime(), 45.1, 0.3),
          (sfx_crack(), 50.1, 0.55), (whoosh, 53.25, 0.35), (sfx_chime(), 53.45, 0.3)]
    for k in range(8):
        ex.append((pop, 10.45 + k * 0.06, 0.15))
    for k in range(5):
        ex.append((pop, 43.7 + k * 0.08, 0.25))
    for k in range(3):
        ex.append((pop, 57.5 + k * 0.33, 0.2))
    return ex


def main():
    preview = '--preview' in sys.argv
    hero.PLACEHOLDER_TAG = ''
    hero.WATERMARK = '样片｜代码生成'
    voices = SA.build_voices()
    WIN[:] = SA.line_windows(voices)
    hv, hvlen = [], []
    for c in hero.CARDS[:4]:
        x, _ = hero.tts_fit(c, c['dur'] - hero.VOICE_LEAD - 0.02)
        hv.append(x)
        hvlen.append(len(x) / SR)
    HA = {
        'bg': [hero.make_bg(c['color']) for c in hero.CARDS],
        'stripes': [hero.make_stripes(c['color']) for c in hero.CARDS],
        'bigname': [hero.make_bigname(c['name']) for c in hero.CARDS],
        'char': [None] * len(hero.CARDS),
        'top': hero.make_band(True),
        'bottom': hero.make_band(False),
    }
    sheet_path = os.path.join(HERE, 'sample_60s_v2_keyframes.png')
    if preview:
        only = [float(a) for a in sys.argv[2:]] or SHEET
        sheet([(t, render(t, HA, hvlen)) for t in only], sheet_path)
        print('预览：', sheet_path)
        return
    wav = SA.build_mix(voices, hero.build_audio(hv), os.path.join(hero.CACHE, 'mix60_v2.wav'), extra=extra_sfx())
    mp4 = os.path.join(HERE, 'sample_60s_v2.mp4')
    proc = subprocess.Popen([hero.FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                             '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', mp4],
                            stdin=subprocess.PIPE)
    keep = {int(round(t * FPS)): t for t in SHEET}
    kept = []
    for i in range(int(DUR * FPS)):
        t = i / FPS
        fr = render(t, HA, hvlen)
        assert fr.size == (W, H), (t, fr.size)
        proc.stdin.write(fr.tobytes())
        if i in keep:
            kept.append((keep[i], fr))
        if i % 150 == 0:
            print(f'  {t:5.1f}s', flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit('ffmpeg 编码失败')
    sheet(kept, sheet_path)
    print('完成：', mp4)


if __name__ == '__main__':
    main()
