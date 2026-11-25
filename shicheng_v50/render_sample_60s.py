#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《事成V你50》60 秒样片（动态分镜）

在仓库根目录运行：
    pip install numpy pillow imageio-ffmpeg edge-tts
    python shicheng_v50/render_sample_60s.py              # 出 sample_60s.mp4 和关键帧拼图
    python shicheng_v50/render_sample_60s.py --preview    # 只出关键帧拼图，快速检查画面

人物、场景和界面都是代码画的占位；台词用 edge-tts 在线配音（要联网，缓存在 .assets/）；
音效和配乐由代码合成。11～19 秒直接用 render_hero_select.py 的选英雄卡。
"""
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render_hero_select as hero  # noqa: E402
import sample_audio as SA  # noqa: E402
import sample_figures as SF  # noqa: E402
import sample_scenes as SC  # noqa: E402
from sample_scenes import nd, W, H, F, clamp, ease_out, ease_back, caption, tag  # noqa: E402

FPS = 30
DUR = 60.0
WIN = []
SR = hero.SR


def seg(t, a, b):
    return clamp((t - a) / (b - a))


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


CD_KEYS = [(4.0, 480), (19.0, 430), (23.0, 330), (27.0, 190), (30.0, 100), (33.0, 60), (38.0, 5), (43.2, 0)]


def countdown(t):
    if t <= CD_KEYS[0][0]:
        return CD_KEYS[0][1]
    for (t0, v0), (t1, v1) in zip(CD_KEYS, CD_KEYS[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return 0


def stand_y(ground, h):
    return ground - 0.465 * h


def drone(d, x, y, s=1.0, t=0.0, bag=True, rope=60):
    if bag:
        d.line((x, y + 8 * s, x, y + rope * s), fill=(200, 200, 210, 255), width=max(1, int(2 * s)))
        SF.draw_bag(d, x, y + (rope + 18) * s, 46 * s)
    for sx in (-1, 1):
        d.line((x, y, x + sx * 46 * s, y - 10 * s), fill=(30, 30, 36, 255), width=int(6 * s))
        rx = x + sx * 46 * s
        a = int(90 + 60 * math.sin(t * 60 + sx))
        d.ellipse((rx - 30 * s, y - 16 * s, rx + 30 * s, y - 6 * s), fill=(160, 170, 190, a))
    d.rounded_rectangle((x - 22 * s, y - 10 * s, x + 22 * s, y + 10 * s), radius=6 * s, fill=(26, 26, 32, 255))
    d.ellipse((x - 4 * s, y - 3 * s, x + 4 * s, y + 5 * s), fill=(255, 60, 60, 255) if int(t * 4) % 2 else (60, 255, 120, 255))


def puff(d, x, y, r, a, col=(235, 90, 60)):
    if a <= 0:
        return
    for k, (dx, dy, rr, aa) in enumerate(((0, 0, 1.0, 0.28), (-0.45, 0.2, 0.7, 0.3), (0.5, 0.15, 0.65, 0.3), (0.1, -0.35, 0.6, 0.32))):
        c = SC.mixc(col, (200, 190, 190), 0.25 * k / 3)
        d.ellipse((x + dx * r - rr * r, y + dy * r - rr * r, x + dx * r + rr * r, y + dy * r + rr * r), fill=c + (int(a * aa),))


def crow(d, x, y, t, S=1.6, caw=False):
    flap = math.sin(2 * math.pi * 9 * t)

    def q(*pts):
        return [(x + dx * S, y + dy * S) for dx, dy in pts]

    body = (18, 18, 22, 255)
    wy = -46 * flap
    d.polygon(q((-12, -6), (22, -4), (30, wy - 6), (-2, wy)), fill=body)
    d.ellipse([*q((-34, -14))[0], *q((30, 14))[0]], fill=body)
    d.ellipse([*q((-50, -20))[0], *q((-22, 6))[0]], fill=body)
    d.polygon(q((-50, -9), (-72, -3), (-50, 1)), fill=(45, 45, 45, 255))
    d.polygon(q((26, -6), (62, -16), (62, 12), (26, 8)), fill=body)
    d.polygon(q((-16, -4), (16, -2), (6, wy * 1.2 + 4), (-30, wy * 1.1)), fill=body)
    d.ellipse([*q((-44, -14))[0], *q((-38, -8))[0]], fill=(235, 235, 235, 255))
    if caw:
        d.text((x + 16 * S, y - 60 * S), '嘎！', font=F('Black', 46), fill=(255, 255, 255, 255), anchor='mm',
               stroke_width=5, stroke_fill=(0, 0, 0, 255))


def bucket(d, x, y, s=1.0):
    for k in range(5):
        a = -0.9 + k * 0.45
        d.ellipse((x + a * 50 * s - 22 * s, y - 70 * s - 18 * s * (1 - abs(a)), x + a * 50 * s + 22 * s, y - 34 * s),
                  fill=(196, 120, 50, 255))
    d.polygon([(x - 70 * s, y - 50 * s), (x + 70 * s, y - 50 * s), (x + 52 * s, y + 60 * s), (x - 52 * s, y + 60 * s)],
              fill=(250, 250, 246, 255), outline=(200, 200, 196, 255))
    d.rectangle((x - 66 * s, y - 50 * s, x + 66 * s, y - 34 * s), fill=(235, 235, 230, 255))


# ================================================================ 镜头
def s_black(t):
    img = Image.new('RGB', (W, H), (0, 0, 0))
    d = nd(img)
    a = clamp(t / 0.25)
    d.text((640, 300), '周四 22:52', font=F('Bold', 66), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    jx = 5 * math.sin(2 * math.pi * 30 * t) if t < 0.6 else 0
    x, y = 640 + jx, 450
    d.rounded_rectangle((x - 30, y - 54, x + 30, y + 54), radius=10, outline=(255, 255, 255, 220), width=4)
    if t < 0.6:
        for s in (-1, 1):
            for k in (1, 2):
                xx = x + s * (40 + k * 14)
                d.line((xx, y - 22 + k * 4, xx, y + 22 - k * 4), fill=(255, 255, 255, 200), width=3)
    else:
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=(60, 200, 110, 255))
        d.text((640, 540), '通话中 00:0' + str(int(t - 0.6)), font=F('Medium', 22), fill=(180, 180, 190, 255), anchor='mm')
    return img


def sit_pose(reach=(0.24, -0.2)):
    return dict(view='side', lean=8, arms=({'ik': reach, 'rel': 'P', 'bend': 1}, {'ik': (reach[0] + 0.03, reach[1] + 0.01), 'rel': 'P', 'bend': 1}),
                legs=((85, 88), (92, 92)))


def lying_roomB(img, x_head, y_head, h, view='side', expr='deadpan', tk=0.0):
    pose = dict(view=view, bust=False, rot=90, arms=((0, 0), (0, 0)), legs=((0, 0), (0, 0)))
    off = 0.39 * h
    SF.put(img, 'roomB', pose, x_head - off, y_head, h, facing=-1, expr=expr, talk=tk, glow=False)
    d = nd(img)
    d.rounded_rectangle((x_head - off - 0.9 * h, y_head - 0.07 * h, x_head - 0.06 * h, y_head + 0.09 * h), radius=0.05 * h,
                        fill=(88, 108, 160, 255), outline=(60, 76, 120, 255), width=3)


def s_dorm_call(t):
    lt = t - 1.4
    img = SC.bg_dorm().copy()
    SF.put(img, 'roomA', sit_pose(), 430, 520, 340, facing=-1, expr='neutral')
    lying_roomB(img, 1186, 296, 300, expr='deadpan')
    SF.put(img, 'roomC', SF.stand('front'), 1010, stand_y(712, 390), 390, expr='neutral')
    shocked = t >= 2.05
    pose = dict(view='front', arms=((8, 4), {'ik': (0.07, 0.0), 'rel': 'Hc', 'bend': 1}), legs=((3, 0), (3, 0)))
    SF.put(img, 'dacong', pose, 640, stand_y(780, 610), 610, expr='shock' if shocked else 'neutral',
           talk=talk('大聪明', t), hold='phone', sweat=shocked)
    return SC.zoom(img, 1.0 + 0.1 * smooth(lt / 2.6), 640, 300)


def s_turn(t, who, t0):
    lt = t - t0
    if who == 'roomB':
        img = SC.bg_dorm_blur().copy()
        d = nd(img)
        d.rectangle((0, 470, W, H), fill=(70, 80, 110, 255))
        d.ellipse((560, 330, 900, 450), fill=(232, 232, 238, 255))
        lying_roomB(img, 720, 380, 1000, view='side' if lt < 0.07 else 'front', expr='deadpan')
    else:
        img = SC.bg_dorm_blur().copy()
        view = 'side' if lt < 0.07 else 'front'
        expr = {'roomA': 'question', 'roomC': 'shock'}[who] if view == 'front' else 'neutral'
        SF.put(img, who, dict(view=view, bust=True, arms=((12, 6), (12, 6))), 640, 840, 1150, facing=1, expr=expr)
    s = 1.0 + 0.14 * (1 - ease_out(lt / 0.15))
    return SC.shake(SC.zoom(img, s, 640, 330), 8 * math.sin(lt * 90) * (1 - clamp(lt / 0.15)), 0)


def s_roomA(t):
    lt = t - 4.9
    img = SC.bg_dorm_blur().copy()
    SF.put(img, 'roomA', dict(view='front', bust=True, arms=((12, 6), (12, 6))), 640, 860, 1100, expr='question', talk=talk('室友A', t))
    return SC.zoom(img, 1.0 + 0.05 * smooth(lt / 1.7), 640, 340)


def s_roomB(t):
    lt = t - 6.6
    img = SC.bg_dorm_blur().copy()
    d = nd(img)
    d.rectangle((0, 450, W, H), fill=(70, 80, 110, 255))
    d.ellipse((620, 320, 960, 440), fill=(232, 232, 238, 255))
    lying_roomB(img, 780, 370, 900, view='side', expr='deadpan', tk=talk('室友B', t))
    return SC.zoom(img, 1.0 + 0.06 * smooth(lt / 0.85), 760, 360)


POST = '急！南门炸鸡运回北区8号楼'


def s_phone(t):
    lt = t - 7.45
    img = SC.bg_dorm_blur().copy()
    sx0, sy0, sx1, sy1 = SC.phone_frame(img, 460, 30, 360, 660)
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
    d.text((sx0 + 20, sy0 + 130), POST[:n] + ('|' if int(t * 4) % 2 and n < len(POST) else ''), font=F('Bold', 22),
           fill=(20, 20, 26, 255), anchor='lm')
    chips = [('#门禁前', 9.1), ('#事成V你50', 9.3), ('#找搭子', 9.45)]
    x = sx0 + 20
    for txt, tc in chips:
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
    for r in range(4):
        for c in range(10 if r < 3 else 5):
            kw = (sx1 - sx0 - 22) / 10
            kx = sx0 + 6 + c * (kw + 1) + (kw * 2.5 if r == 3 else 0) * (c == 0)
            if r == 3:
                kx = sx0 + 6 + c * (kw * 2 + 2)
                kw2 = kw * 2
            else:
                kw2 = kw
            ky = ky0 + 10 + r * 48
            on = (r * 10 + c) == hot
            d.rounded_rectangle((kx, ky, kx + kw2 - 2, ky + 40), radius=5, fill=(170, 176, 190, 255) if on else (255, 255, 255, 255))
    if 10.2 <= t < 10.7:
        p = (t - 10.2) / 0.5
        r = 20 + 120 * ease_out(p)
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(230, 40, 70, int(220 * (1 - p))), width=5)
    if t >= 10.35:
        a = clamp((t - 10.35) / 0.15)
        d.rounded_rectangle((540, 330, 740, 390), radius=14, fill=(20, 20, 26, int(220 * a)))
        d.text((640, 360), '✓ 发布成功', font=F('Bold', 22), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    if 9.75 <= t < 10.35:
        p = smooth((t - 9.75) / 0.42)
        fx, fy = lerp(900, (bx0 + bx1) / 2 + 10, p), lerp(760, (by0 + by1) / 2 + 14, p)
        if pressed:
            fy += 4
        d.line((fx, fy, fx + 260, fy + 330), fill=(238, 206, 176, 255), width=56)
        d.ellipse((fx - 28, fy - 28, fx + 28, fy + 28), fill=(238, 206, 176, 255))
        d.ellipse((fx - 18, fy - 22, fx + 10, fy + 2), fill=(250, 226, 206, 255))
    z = 1.0 + 0.9 * smooth((t - 9.6) / 0.3) * (1 - smooth((t - 10.45) / 0.3))
    img = SC.zoom(img, z, (bx0 + bx1) / 2, (by0 + by1) / 2 + 60)
    if t >= 10.75:
        img = Image.blend(img, Image.new('RGB', (W, H), (255, 255, 255)), smooth((t - 10.75) / 0.25))
    return img


def s_balcony(t):
    lt = t - 19.0
    img = SC.bg_balcony().copy()
    lean = lerp(5, 55, smooth((lt - 0.15) / 0.6))
    pose = dict(view='side', lean=lean, head=-lean * 0.35, arms=({'ik': (0.2, -0.3), 'rel': 'P', 'bend': -1},
                                                               {'ik': (0.24, -0.33), 'rel': 'P', 'bend': -1}), legs=((-6, 4), (6, 4)))
    h = 380
    J = SF.joints(SF.FIGS['xingxing'], dict(pose, lean=55, head=-55 * 0.35), -1)
    floor, s = 700, 1.5
    eye_x, eye_y = 700 + 94 * s, floor - 112 * s
    px_, py_ = eye_x + 14 - J['Hc'][0] * h, eye_y - 6 - J['Hc'][1] * h
    d = nd(img)
    d.rectangle((0, 660, W, H), fill=(36, 36, 48, 255))
    SC.telescope(d, 700, floor, aim=-1, s=s)
    SF.put(img, 'xingxing', pose, px_, py_, h, facing=-1, expr='determined', talk=talk('星星', t))
    return SC.zoom(img, 1.0 + 0.08 * smooth(lt / 1.6), 760, 420)


def s_pov(t):
    lt = t - 20.6
    world, pos = SC.bg_gate_world()
    bxw, byw = pos['bag']
    z = lerp(1.0, 1.9, smooth((lt - 0.35) / 1.3))
    cx = lerp(820, bxw + 40, smooth((lt - 0.2) / 1.3)) + 6 * math.sin(lt * 13)
    cy = lerp(470, byw - 10, smooth((lt - 0.2) / 1.3)) + 4 * math.sin(lt * 17)
    k = 0.8 * z
    crop = world.crop((int(cx - 640 / k), int(cy - 360 / k), int(cx + 640 / k), int(cy + 360 / k))).resize((W, H), Image.BILINEAR)
    d = nd(crop)

    def scr(p):
        return ((p[0] - cx) * k + 640, (p[1] - cy) * k + 360)

    if lt >= 0.25:
        gx, gy = scr(pos['guard'])
        tag(d, gx, gy - 40, '保安大爷｜中立｜别惹', color=(255, 255, 255), size=20, alpha=clamp((lt - 0.25) / 0.15))
    if lt >= 0.4:
        qx, qy = scr(pos['couple'])
        tag(d, qx, qy - 60, '情侣｜无害｜别打扰', color=(255, 170, 200), size=20, alpha=clamp((lt - 0.4) / 0.15))
    if lt >= 0.4:
        bx, by = scr((bxw, byw))
        u = clamp((lt - 0.4) / 0.25)
        r = lerp(140, 40, ease_out(u)) * k / 0.8 / 1.5
        red = (255, 60, 60, 255)
        for sx in (-1, 1):
            for sy in (-1, 1):
                x0, y0 = bx + sx * r, by + sy * r * 0.85
                d.line((x0, y0, x0 - sx * r * 0.35, y0), fill=red, width=4)
                d.line((x0, y0, x0, y0 - sy * r * 0.35), fill=red, width=4)
        if u >= 1:
            tag(d, bx, by - r - 6, '大红·炸鸡桶', color=(255, 200, 80), bg=(120, 20, 20), size=24)
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).ellipse((640 - 330, 360 - 330, 640 + 330, 360 + 330), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(6))
    out = Image.new('RGB', (W, H), (0, 0, 0))
    out.paste(crop, (0, 0), m)
    d = nd(out)
    d.ellipse((310, 30, 970, 690), outline=(40, 40, 46, 255), width=10)
    d.line((640, 60, 640, 300), fill=(255, 255, 255, 50), width=1)
    d.line((640, 420, 640, 660), fill=(255, 255, 255, 50), width=1)
    d.line((340, 360, 580, 360), fill=(255, 255, 255, 50), width=1)
    d.line((700, 360, 940, 360), fill=(255, 255, 255, 50), width=1)
    return out


def street(offset):
    far = SC.bg_street_far()
    near = SC.bg_street_near()
    o1 = int(offset * 0.3) % (far.width - W)
    img = far.crop((o1, 0, o1 + W, H))
    o2 = int(offset) % (near.width - W)
    nr = near.crop((o2, 0, o2 + W, H))
    img.paste(nr, (0, 0), nr)
    return img, o2


def s_afei_run(t):
    lt = t - 23.0
    run_t = max(0.0, lt - 0.45)
    offset = 0.5 * 1700 * run_t ** 2
    img, o2 = street(offset)
    d = nd(img)
    bag_world = (560, 528)
    if lt < 0.3:
        SF.draw_bag(d, bag_world[0] - o2, bag_world[1], 50)
        pose = dict(view='side', arms=((-5, 10), {'ik': (0.24, -0.33), 'rel': 'P', 'bend': -1}), legs=((-3, 3), (4, 3)))
        SF.put(img, 'afei', pose, 700, stand_y(650, 440), 440, facing=-1, expr='determined')
    elif lt < 0.45:
        pose = dict(view='side', lean=30, arms=((-40, 30), (40, 80)), legs=((-20, 30), (30, 50)))
        SF.put(img, 'afei', pose, 640, stand_y(650, 440) + 20, 440, facing=1, expr='yell', hold='bag')
    else:
        ph = 2 * math.pi * 3.3 * run_t
        pose = SF.run(ph, lean=20, arms=((-60 * math.sin(ph), 85), (50, 85)))
        pose['head'] = -12 + 8 * math.sin(lt * 80)
        y = stand_y(650, 440) + 10 + SF.run_bob(ph, 440)
        SC.speed_lines(d, lt, n=int(10 + 30 * clamp(run_t)))
        SF.put(img, 'afei', pose, 600, y, 440, facing=1, expr='yell', hold='bag', talk=talk('阿飞', t))
    return img


def s_couple(t):
    lt = t - 24.5
    img = SC.bg_road().copy()
    passed = t >= 24.88
    wind = clamp((t - 24.78) / 0.12) * (1 - clamp((t - 25.5) / 0.8)) if t >= 24.78 else 0.0
    sit = dict(view='front', arms=((10, 4), (10, 4)), legs=((2, 0), (2, 0)), legscale=(0.35, 1.0))
    SF.put(img, 'girl', sit, 580, 515, 330, expr='shock' if passed else 'happy', wind=wind)
    boy = dict(view='front', arms=((10, 4), {'ik': (0.05, 0.15), 'rel': 'N', 'bend': 1}), legs=((2, 0), (2, 0)), legscale=(0.35, 1.0))
    lid_off = t >= 24.92
    img2, (bx, by) = SF.fig_layer('boy', boy, 340, expr='shock' if passed else 'happy', hold=None)
    img.paste(img2, (int(700 - bx), int(515 - by)), img2)
    J = SF.joints(SF.FIGS['boy'], boy, 1)
    cupx, cupy = 700 + J['W1'][0] * 340, 515 + J['W1'][1] * 340
    d = nd(img)
    SF.HOLD['cup'](d, (cupx, cupy), 340, dict(lid_off=lid_off))
    if lid_off:
        u = (t - 24.92) / 0.9
        lx, ly = cupx + 380 * u, cupy - 20 - 520 * u + 600 * u * u
        a = t * 20
        d.ellipse((lx - 12, ly - 5 + 3 * math.sin(a), lx + 12, ly + 5 - 3 * math.sin(a)), fill=(250, 250, 250, 255))
    if wind > 0:
        rng = np.random.default_rng(int(t * 30))
        for _ in range(16):
            y = rng.uniform(300, 600)
            x = (rng.uniform(0, W) + lt * 1500) % W
            d.line((x, y, x + 60, y - 4), fill=(255, 255, 255, int(120 * wind)), width=2)
    if 24.6 <= t < 24.95:
        u = (t - 24.6) / 0.35
        x = lerp(-250, 1500, u)
        for g in range(3):
            SF.put(img, 'afei', SF.run(t * 30 + g), x - g * 70, stand_y(760, 520), 520, facing=1, expr='yell', hold='bag',
                   glow=(g == 0))
        d = nd(img)
        SC.speed_lines(d, t, n=30)
    return img


def s_to_slope(t):
    lt = t - 26.3
    img = SC.bg_slope_top().copy()
    SF.put(img, 'xiaok', dict(view='side', lean=10, arms=((-10, 20), {'ik': (0.3, -0.25), 'rel': 'P', 'bend': -1}),
                              legs=((-8, 10), (10, 10))), 900, stand_y(600, 380) - 10, 380, facing=-1, expr='determined')
    ph = 2 * math.pi * 3.3 * lt
    x = lerp(120, 560, lt / 0.7)
    SF.put(img, 'afei', SF.run(ph, lean=20), x, stand_y(600, 380) + SF.run_bob(ph, 380), 380, facing=1, expr='yell', hold='bag',
           talk=talk('阿飞', t))
    return img


def s_handoff(t):
    lt = t - 27.0
    img = SC.bg_slope_top().copy()
    h = 400
    u = smooth((lt - 0.3) / 0.6)
    meet = (640, stand_y(600, h) - 0.12 * h)
    a_hand = (meet[0] - 0.04 * h - 520) / h
    SF.put(img, 'afei', dict(view='side', lean=8, arms=((-15, 15), {'ik': (a_hand + 0.04, -0.12), 'rel': 'P', 'bend': -1}),
                             legs=((-10, 8), (12, 8))), 520, stand_y(600, h), h, facing=1, expr='determined')
    SF.put(img, 'xiaok', dict(view='side', lean=8, arms=((-15, 15), {'ik': (0.24, -0.12), 'rel': 'P', 'bend': -1}),
                              legs=((-10, 8), (12, 8))), 760, stand_y(600, h), h, facing=-1, expr='determined')
    d = nd(img)
    bx = lerp(meet[0] - 40, meet[0] + 30, u)
    SF.draw_bag(d, bx, meet[1] + 26, 0.13 * h)
    d.line((0, 250, W, 262), fill=(255, 230, 190, 40), width=10)
    s = 1.04 + 0.08 * smooth(lt / 1.2)
    return SC.zoom(img, s, lerp(600, 680, lt / 1.2), 380)


def slope_y(x):
    return 305 + 0.2656 * x


def sparks(d, x, y, t, n=26, seed=0, spread=1.0, color=(255, 220, 120)):
    rng = np.random.default_rng(seed + int(t * 30))
    for _ in range(n):
        a = rng.uniform(math.pi * 0.9, math.pi * 1.4)
        ln = rng.uniform(10, 50) * spread
        x1, y1 = x + math.cos(a) * ln, y + math.sin(a) * ln * 0.6 - rng.uniform(0, 20)
        d.line((x, y, x1, y1), fill=tuple(color) + (int(rng.uniform(150, 255)),), width=2)


def s_skate(t):
    lt = t - 28.2
    img = SC.bg_slope_down().copy()
    x = lerp(-120, 1380, lt / 1.1)
    h = 330
    drift = 0.55 <= lt < 0.95
    if drift:
        pose = dict(view='side', lean=-12, rot=12, arms=((-60, 20), (70, 80)), legs=((10, 50), (45, 10)))
    else:
        pose = dict(view='side', lean=35, rot=15, head=-20, arms=((-30, 20), (60, 80)), legs=((-20, 30), (40, 70)))
    y = slope_y(x) - 0.34 * h
    for g in range(3):
        SF.put(img, 'xiaok', pose, x - g * 45, y - g * 12, h, facing=1, expr='determined', hold='bag', glow=(g == 0))
    d = nd(img)
    if drift:
        sparks(d, x + 20, slope_y(x) - 6, t, n=40, spread=1.4)
        caption(d, '小K 漂移 +1', x + 40, y - 190, 40, t, 28.2 + 0.55, color=(255, 200, 60))
    return img


def s_guard(t):
    lt = t - 29.3
    img = SC.bg_booth().copy()
    if 0.02 <= lt < 0.16:
        d = nd(img)
        x = lerp(80, 1200, (lt - 0.02) / 0.14)
        d.line((x - 260, 300, x, 300), fill=(255, 190, 40, 200), width=26)
    if lt < 0.18:
        view, f = 'side', -1
    elif lt < 0.36:
        view, f = 'front', 1
    else:
        view, f = 'side', 1
    pose = dict(view=view, bust=True, arms=((10, 5), {'ik': (0.0, 0.1), 'rel': 'Hc', 'bend': 1}))
    SF.put(img, 'guard', pose, 640, 840, 1250, facing=f, expr='deadpan', hold='thermos')
    return img


def lake_frame(t, w=W, ox=0):
    img = SC.bg_lake(w).copy()
    SC.water(img, 360, H, t, moon_x=int(w * 0.22))
    if img.width != W:
        img = img.crop((int(ox), 0, int(ox) + W, H))
    return img


def shore(img):
    d = nd(img)
    d.polygon([(0, 600), (W, 580), (W, H), (0, H)], fill=(70, 66, 62, 255))
    d.line((0, 600, W, 580), fill=(110, 104, 96, 255), width=6)
    SC.willow(d, 90, 600, 260)
    SC.willow(d, 1210, 585, 240)


def s_brake(t):
    lt = t - 30.0
    img = lake_frame(t)
    shore(img)
    h = 360
    d = nd(img)
    if lt < 0.38:
        x = lerp(-120, 600, ease_out(lt / 0.38))
        pose = dict(view='side', lean=35, head=-20, arms=((-30, 20), (60, 80)), legs=((-20, 30), (40, 70)))
        SF.put(img, 'xiaok', pose, x, 600 - 0.36 * h, h, facing=1, expr='determined', hold='bag')
    elif lt < 0.8:
        x = 600 + 40 * ease_out((lt - 0.38) / 0.42)
        pose = dict(view='side', lean=-22, arms=((150, 20), (120, 30)), legs=((-10, 40), (38, 5)))
        SF.put(img, 'xiaok', pose, x, 600 - 0.42 * h, h, facing=1, expr='shock', hold={'bag': 'W0'})
        sparks(nd(img), x + 70, 596, t, n=36, spread=1.3)
    else:
        pose = dict(view='side', lean=18, head=25, arms=((4, 4), (8, 6)), legs=((-3, 3), (4, 3)))
        SF.put(img, 'xiaok', pose, 640, stand_y(600, h), h, facing=1, expr='sad', hold='bag')
    return img


def s_drone_up(t):
    lt = t - 31.5
    img = lake_frame(t)
    shore(img)
    rise = smooth((lt - 0.6) / 0.9)
    tilt = 140 * rise
    h = 560
    glint = 0.3 <= lt < 0.5
    if lt < 0.55:
        arm1 = {'ik': (0.0, 0.0), 'rel': 'Hc', 'bend': 1}
        pose = dict(view='front', arms=((8, 4), arm1))
        hold = None
    else:
        pose = dict(view='front', arms=((8, 4), {'ik': (0.05, -0.18), 'rel': 'P', 'bend': 1}))
        hold = 'remote'
    layer = img.copy()
    SF.put(layer, 'laozhou', pose, 470, stand_y(760, h), h, expr='determined', talk=talk('老周', t), glint=glint, hold=hold)
    d = nd(layer)
    dy = lerp(640, 300, rise)
    drone(d, 860, dy, s=1.4, t=t, rope=60)
    out = Image.new('RGB', (W, H))
    out.paste(layer, (0, int(tilt)))
    top = SC.bg_lake().crop((0, 0, W, int(tilt) + 1))
    out.paste(top, (0, 0))
    return out


def s_airdrop(t):
    lt = t - 33.0
    ox = 320 * smooth(lt / 2.4)
    img = lake_frame(t, w=1800, ox=ox)
    d = nd(img)
    path_x = lambda tt: lerp(-160, 1700, (tt - 33.0) / 2.4)  # noqa: E731
    path_y = lambda tt: 250 + 24 * math.sin((tt - 33.0) * 2.2)  # noqa: E731
    for k in range(40):
        te = 33.0 + k * 0.07
        if te > t:
            break
        age = t - te
        x, y = path_x(te) - ox + 8 * math.sin(k * 1.7), path_y(te) + 75 - age * 18
        puff(d, x, y, 12 + age * 34, int(255 * clamp(1 - age / 2.0)))
    drone(d, path_x(t) - ox, path_y(t), s=1.2, t=t, rope=55)
    return img


def s_crowd(t):
    lt = t - 35.4
    img = lake_frame(t)
    d = nd(img)
    d.rectangle((0, 470, W, H), fill=(66, 62, 58, 255))
    d.rectangle((0, 466, W, 476), fill=(110, 104, 96, 255))
    for k in range(9):
        puff(d, 320 + k * 110, 150 + 10 * math.sin(k * 1.3) - k * 4, 26 + k * 5, 200 - k * 12)
    look = lt >= 0.12
    run = lt >= 0.4
    for i in range(6):
        h = 230 + (i % 3) * 20
        base_x = 120 + i * 190
        col = SF.CROWD_COLORS[i % len(SF.CROWD_COLORS)]
        if run:
            rt = lt - 0.4
            ph = 2 * math.pi * 3.2 * rt + i
            x = base_x + 900 * rt
            pose = SF.run(ph, lean=16)
            pose['head'] = -25
            SF.put(img, 'boy', pose, x, stand_y(680, h) + SF.run_bob(ph, h), h, facing=1, expr='shock', color=col, glow=False)
        else:
            pose = SF.stand('side')
            pose['head'] = -30 if look else 0
            SF.put(img, 'boy', pose, base_x, stand_y(680, h), h, facing=1 if i % 2 else -1, expr='shock' if look else 'neutral',
                   color=col, glow=False)
            if look:
                caption(nd(img), '！', base_x, stand_y(680, h) - 0.6 * h, 44, t, 35.52, color=(255, 230, 60))
    return img


def s_facepalm(t):
    lt = t - 36.5
    img = SC.bg_balcony().copy()
    d = nd(img)
    d.rectangle((0, 660, W, H), fill=(36, 36, 48, 255))
    SC.telescope(d, 330, 720, aim=-1, s=1.6)
    up = smooth((lt - 0.1) / 0.3)
    arm = {'ik': (lerp(0.12, 0.03, up), lerp(0.25, -0.05, up)), 'rel': 'Hc', 'bend': 1}
    SF.put(img, 'xingxing', dict(view='front', arms=((6, 3), arm)), 700, stand_y(790, 640) + 4 * math.sin(lt * 5), 640,
           expr='deadpan', talk=talk('星星', t))
    return SC.zoom(img, 1.0 + 0.05 * smooth(lt / 1.5), 700, 330)


def s_door_close(t):
    lt = t - 38.0
    img = SC.bg_door().copy()
    d = nd(img)
    w = lerp(30, 170, smooth(lt / 1.0))
    d.rectangle((470, 262, 640, 640), fill=(200, 220, 230, 120), outline=(90, 96, 110, 255), width=6)
    d.rectangle((810 - w, 262, 810, 640), fill=(200, 220, 230, 140), outline=(90, 96, 110, 255), width=6)
    edge = (810 - w, 460)
    h = 470
    J = SF.joints(SF.FIGS['suguan'], dict(view='side', arms=((-5, 10), (70, 10))), -1)
    SF.put(img, 'suguan', dict(view='side', arms=((-5, 10), {'ik': ((900 - edge[0]) / h - 0.02, (edge[1] - stand_y(650, h)) / h), 'rel': 'P', 'bend': 1}),
                               legs=((-3, 3), (4, 3))), 900, stand_y(650, h), h, facing=-1, expr='deadpan')
    return img


def s_stairs(t):
    lt = t - 39.0
    img = SC.bg_stairs().copy()
    h = 400
    x = lerp(180, 860, lt / 1.0)
    ph = 2 * math.pi * 2.0 * lt
    y = 330 + 0.2857 * x - 0.43 * h + SF.run_bob(ph, h)
    SF.put(img, 'dacong', SF.run(ph, lean=10), x, y, h, facing=1, expr='yell', sweat=True)
    if lt >= 0.3:
        u = (lt - 0.3) / 0.7
        sx, sy = x - 120 - 180 * u, y + 0.4 * h - 300 * u + 330 * u * u
        d = nd(img)
        a = lt * 14
        pts = [(sx + 26 * math.cos(a + k * math.pi / 2), sy + 11 * math.sin(a + k * math.pi / 2)) for k in range(4)]
        d.polygon(pts, fill=(250, 250, 250, 255), outline=(120, 140, 200, 255))
    return img


def s_fall(t):
    lt = t - 40.0
    img = SC.vgrad(W, H, (10, 14, 36), (40, 34, 70))
    d = nd(img)
    SC.stars(d, 81, 120, (0, 0, W, 500))
    d.rectangle((0, 600, W, H), fill=(52, 52, 64, 255))
    d.rectangle((420, 560, 860, H), fill=(255, 226, 170, 255))
    by = lerp(-80, 330, lt / 1.0)
    for k in range(7):
        puff(d, 640 + 8 * math.sin(k * 1.9), by - 70 - k * 34, 16 + k * 6, 230 - k * 28)
    SF.draw_bag(d, 640, by, 90)
    up = smooth(lt / 0.5)
    arm0 = {'ik': (-lerp(0.12, 0.3, up), lerp(0.1, -0.15, up)), 'rel': 'N', 'bend': -1}
    arm1 = {'ik': (lerp(0.12, 0.3, up), lerp(0.1, -0.15, up)), 'rel': 'N', 'bend': 1}
    SF.put(img, 'dacong', dict(view='front', bust=True, arms=(arm0, arm1)), 640, 880, 900, expr='shock', sweat=True)
    return img


def s_dive(t):
    lt = t - 41.0
    img = SC.bg_door().filter(ImageFilter.GaussianBlur(5))
    h = 420
    x = lerp(220, 760, lt / 1.0)
    rot = lerp(70, 88, lt)
    pose = dict(view='side', rot=rot, arms=({'ik': (0.06, -0.72), 'rel': 'P', 'bend': 1}, {'ik': (0.1, -0.74), 'rel': 'P', 'bend': 1}),
                legs=((-12, 10), (5, 25)))
    caught = lt >= 0.45
    SF.put(img, 'dacong', pose, x, 420, h, facing=1, expr='determined', hold='bag' if caught else None)
    d = nd(img)
    if not caught:
        J = SF.joints(SF.FIGS['dacong'], pose, 1)
        hx, hy = x + J['W1'][0] * h, 420 + J['W1'][1] * h
        bx = lerp(hx + 140, hx, lt / 0.45)
        by = lerp(hy - 220, hy + 20, lt / 0.45)
        SF.draw_bag(d, bx, by, 0.13 * h)
    SC.speed_lines(d, lt * 0.3, n=14)
    caption(d, '接住泼天的富贵', 640, 150, 66, t, 41.35, color=(255, 214, 80))
    return img


PANELS = [('8号楼', 'dacong', 'bag'), ('3号楼', 'afei', None), ('6号楼', 'xiaok', None), ('7号楼', 'laozhou', 'remote')]


def panel(t, label, key, hold):
    pw, ph = 634, 354
    img = SC.vgrad(pw, ph, (16, 20, 40), (30, 30, 50))
    d = nd(img)
    SC.stars(d, hash(label) % 100, 30, (0, 0, 330, 140))
    door_x = 360
    d.rectangle((door_x, 0, pw, ph), fill=(255, 226, 170, 255))
    d.rectangle((door_x, 300, pw, ph), fill=(200, 170, 120, 255))
    d.rectangle((0, 300, door_x, ph), fill=(60, 62, 74, 255))
    d.rectangle((door_x - 14, 40, door_x, 300), fill=(90, 96, 110, 255))
    d.rounded_rectangle((door_x - 130, 50, door_x - 26, 84), radius=6, fill=(220, 210, 180, 255))
    d.text((door_x - 78, 67), label, font=F('Black', 22), fill=(60, 40, 30, 255), anchor='mm')
    close = smooth((t - 42.0) / 1.2)
    w = lerp(170, 8, close)
    d.polygon([(door_x, 40), (door_x + w, 70 - 30 * close), (door_x + w, 300 - 10 * close), (door_x, 300)],
              fill=(160, 190, 210, 200), outline=(80, 90, 110, 255))
    u = clamp((t - 42.15) / 1.0)
    x = lerp(-140, 520, u)
    pose = dict(view='side', rot=82, arms=({'ik': (0.06, -0.72), 'rel': 'P', 'bend': 1}, {'ik': (0.1, -0.74), 'rel': 'P', 'bend': 1}),
                legs=((-12, 10), (5, 25)))
    SF.put(img, key, pose, x, 250, 230, facing=1, expr='determined', hold=hold, glow=False)
    if t >= 43.2:
        caption(nd(img), '咔哒', door_x + 20, 150, 40, t, 43.2, color=(255, 255, 255))
    return img


def s_four(t):
    img = Image.new('RGB', (W, H), (0, 0, 0))
    for i, (label, key, hold) in enumerate(PANELS):
        p = panel(t, label, key, hold)
        img.paste(p, (4 + (i % 2) * 638, 4 + (i // 2) * 358))
    caption(nd(img), '同一秒，四栋楼', 640, 360, 52, t, 42.05, color=(255, 255, 255))
    return img


def s_victory(t):
    lt = t - 43.6
    img = SC.bg_victory(t)
    d = nd(img)
    s = ease_back(clamp(lt / 0.3))
    bucket(d, 640, 290, 1.3 * s)
    caption(d, '大吉大利，今晚吃鸡', 640, 500, 84, t, 43.75, color=(255, 214, 80), stroke=(90, 40, 0))
    rng = np.random.default_rng(int(t * 10))
    for _ in range(30):
        x, y = rng.uniform(100, 1180), rng.uniform(60, 640)
        r = rng.uniform(2, 5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 240, 160, int(rng.uniform(80, 220))))
    return img


def s_gaze(t):
    lt = t - 45.0
    img = SC.bg_lobby().copy()
    h = 420
    pose = dict(view='side', rot=90, arms=({'ik': (0.1, -0.2), 'rel': 'P', 'bend': 1}, {'ik': (0.12, -0.18), 'rel': 'P', 'bend': 1}),
                legs=((-3, 3), (3, 3)))
    SF.put(img, 'dacong', pose, 360, 610, h, facing=1, expr='determined', hold='bag', sweat=True)
    sip = smooth((t - 45.1) / 0.2) * (1 - smooth((t - 45.55) / 0.25))
    arm1 = {'ik': (lerp(0.12, 0.04, sip), lerp(-0.2, -0.36, sip)), 'rel': 'P', 'bend': 1}
    SF.put(img, 'suguan', dict(view='side', head=22, arms=((-5, 10), arm1), legs=((-3, 3), (4, 3))), 860, stand_y(700, 520), 520,
           facing=-1, expr='squint', hold='thermos', talk=talk('宿管阿姨', t))
    d = nd(img)
    if t >= 45.1:
        a = clamp((t - 45.1) / 0.2)
        d.rounded_rectangle((250, 70, 1030, 126), radius=12, fill=(70, 30, 120, int(225 * a)), outline=(200, 160, 255, int(255 * a)), width=3)
        d.text((640, 98), '宿管阿姨 使用了【凝视】，全场被硬控2秒', font=F('Bold', 28), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return SC.zoom(img, 1.0 + 0.06 * smooth(lt / 1.8), 640, 420)


def s_eat(t):
    lt = t - 46.8
    img = SC.bg_dorm().copy()
    d = nd(img)
    cheer = 0.5 + 0.5 * math.sin(lt * 9)
    up = dict(view='front', arms=((150 + 10 * cheer, 10), (150 + 10 * cheer, 10)))
    SF.put(img, 'roomA', up, 330, stand_y(800, 560), 560, expr='happy')
    SF.put(img, 'roomB', up, 1000, stand_y(800, 560), 560, expr='happy')
    reach = smooth((t - 47.4) / 0.3) * (1 - smooth((t - 47.8) / 0.15))
    c_arm = {'ik': (lerp(-0.25, -0.5, reach), lerp(0.05, -0.02, reach)), 'rel': 'N', 'bend': -1}
    SF.put(img, 'roomC', dict(view='front', arms=(c_arm, (150, 10))), 1180, stand_y(820, 560), 560, expr='happy')
    d = nd(img)
    d.rectangle((380, 520, 960, 560), fill=(110, 84, 62, 255))
    d.rectangle((380, 560, 960, H), fill=(80, 60, 46, 255))
    bucket(d, 560, 470, 0.9)
    d.rectangle((820, 452, 920, 514), fill=(250, 250, 246, 255), outline=(200, 200, 196, 255), width=2)
    d.rectangle((830, 440, 910, 472), fill=(255, 230, 90, 255))
    d.text((870, 456), '星星的', font=F('Black', 20), fill=(80, 60, 20, 255), anchor='mm')
    slap = smooth((t - 47.7) / 0.08) * (1 - smooth((t - 47.95) / 0.2))
    put_wing = smooth((t - 46.9) / 0.4)
    arm1 = {'ik': (lerp(0.1, 0.32, put_wing) + 0.12 * slap, lerp(0.15, 0.1, put_wing) - 0.05 * slap), 'rel': 'N', 'bend': 1}
    SF.put(img, 'dacong', dict(view='front', arms=((150, 10), arm1)), 700, stand_y(820, 580), 580,
           expr='determined' if slap > 0.1 else 'happy', hold='wing' if t < 47.25 else None)
    if 47.75 <= t < 48.05:
        caption(nd(img), '啪！', 1010, 330, 60, t, 47.75, color=(255, 255, 255))
    return img


def s_wallet(t):
    img = SC.bg_dorm_blur().copy()
    sx0, sy0, sx1, sy1 = SC.phone_frame(img, 460, 30, 360, 660)
    d = nd(img)
    d.text(((sx0 + sx1) / 2, sy0 + 70), '钱包 · 转账', font=F('Bold', 22), fill=(20, 20, 26, 255), anchor='mm')
    d.text((sx0 + 24, sy0 + 130), '转给：TT语音组队的 4 位搭子', font=F('Medium', 18), fill=(90, 90, 100, 255), anchor='lm')
    d.text((sx0 + 24, sy0 + 170), '每人 ¥50', font=F('Bold', 22), fill=(20, 20, 26, 255), anchor='lm')
    d.text((sx0 + 24, sy0 + 250), '¥ 200.00', font=F('Black', 54), fill=(20, 20, 26, 255), anchor='lm')
    d.rounded_rectangle((sx0 + 24, sy1 - 120, sx1 - 24, sy1 - 64), radius=14, fill=(60, 180, 100, 255))
    d.text(((sx0 + sx1) / 2, sy1 - 92), '确认转账', font=F('Bold', 24), fill=(255, 255, 255, 255), anchor='mm')
    d.text(((sx0 + sx1) / 2, sy1 - 30), '示意界面', font=F('Medium', 14), fill=(150, 150, 160, 255), anchor='mm')
    if t >= 49.7:
        u = ease_back(clamp((t - 49.7) / 0.25))
        cx, cy = (sx0 + sx1) / 2, 370
        d.rectangle((sx0, sy0, sx1, sy1), fill=(0, 0, 0, 120))
        d.rounded_rectangle((cx - 150 * u, cy - 110 * u, cx + 150 * u, cy + 110 * u), radius=18, fill=(255, 255, 255, 255))
        d.text((cx, cy - 60 * u), '余额不足', font=F('Black', 30 * u), fill=(220, 40, 50, 255), anchor='mm')
        d.text((cx, cy - 10 * u), '零钱', font=F('Medium', 20 * u), fill=(90, 90, 100, 255), anchor='mm')
        d.text((cx, cy + 50 * u), '¥ 3.50', font=F('Black', 56 * u), fill=(20, 20, 26, 255), anchor='mm')
    if t >= 50.05:
        caption(d, '空气突然安静', 640, 120, 54, t, 50.05, color=(255, 255, 255), stroke=(0, 0, 0))
        p = (t - 50.05) / 0.6
        crow(d, lerp(1380, -150, p), 230 - 60 * p, t, caw=(t < 50.4))
    z = 1.0 + 0.25 * smooth((t - 49.6) / 0.2)
    return SC.zoom(img, z, 640, 380)


SEATS = [('大聪明', '聪', (150, 150, 160)), ('阿飞', '飞', (255, 70, 85)), ('小K', 'K', (255, 186, 30)),
         ('老周', '周', (64, 150, 255)), ('星星', '星', (172, 112, 255))]


def seat_xy(i):
    return 400 + (i % 3) * 240, 250 + (i // 3) * 230


def tt_panel(t, mystery=0.0, balance=None):
    img = SC.bg_dorm_blur().copy()
    d = nd(img)
    d.rounded_rectangle((230, 100, 1050, 620), radius=28, fill=(10, 14, 22, 235), outline=(255, 255, 255, 50), width=2)
    SC.title(d, 'TT语音 · 组队中')
    d.text((640, 140), '南门炸鸡运输队', font=F('Bold', 28), fill=(255, 255, 255, 255), anchor='mm')
    talking = set()
    for s, e, ln in WIN:
        if s <= t < e:
            if ln['who'] == '全员':
                talking |= {0, 1, 2, 3, 4}
            for i, (name, _, _) in enumerate(SEATS):
                if ln['who'] == name:
                    talking.add(i)
            if ln['who'] == '宿管阿姨':
                talking.add(5)
    for i in range(6):
        cx, cy = seat_xy(i)
        r = 56
        if i == 5:
            flip = abs(math.cos(math.pi * clamp((t - 53.25) / 0.3))) if 53.25 <= t < 53.55 else 1.0
            lit = t >= 53.4
            col = (196, 72, 64) if lit else (62, 62, 70)
            name = '8号楼·宿管阿姨' if lit else '神秘人'
            ini = '宿' if lit else '?'
            if 5 in talking:
                ph = (t * 4) % 1
                d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), outline=(60, 235, 140, 255), width=4)
            d.ellipse((cx - r * flip, cy - r, cx + r * flip, cy + r), fill=col + (255,))
            d.text((cx, cy), ini, font=F('Black', max(8, int(44 * flip))), fill=(255, 255, 255, 255) if lit else (150, 150, 158, 255), anchor='mm')
            d.text((cx, cy + r + 30), name, font=F('Bold', 22), fill=(255, 255, 255, 255) if lit else (150, 150, 158, 255), anchor='mm')
            continue
        name, ini, col = SEATS[i]
        if i in talking:
            ph = (t * 4) % 1
            d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), outline=(60, 235, 140, 255), width=4)
            r2 = r + 8 + 14 * ph
            d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=(60, 235, 140, int(160 * (1 - ph))), width=3)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(col) + (255,))
        d.text((cx, cy), ini, font=F('Black', 44), fill=(255, 255, 255, 255), anchor='mm')
        d.text((cx, cy + r + 30), name, font=F('Bold', 22), fill=(255, 255, 255, 255), anchor='mm')
    if balance is not None:
        cx, cy = seat_xy(0)
        d.rounded_rectangle((cx - 90, cy - r - 52, cx + 90, cy - r - 16), radius=10, fill=(255, 214, 80, 255))
        d.text((cx, cy - r - 34), f'余额 ¥{balance:.2f}', font=F('Bold', 20), fill=(60, 40, 0, 255), anchor='mm')
    return img, d


def coin_toast(d, t, t0, src, dst):
    u = (t - t0) / 0.45
    if not 0 <= u <= 1:
        return
    x = lerp(src[0], dst[0], ease_out(u))
    y = lerp(src[1], dst[1], ease_out(u)) - 60 * math.sin(math.pi * u)
    d.rounded_rectangle((x - 58, y - 20, x + 58, y + 20), radius=10, fill=(255, 214, 80, 255))
    d.text((x, y), '收款 +50', font=F('Bold', 20), fill=(60, 40, 0, 255), anchor='mm')


def s_vme(t):
    n_in = sum(1 for k in range(4) if t >= 53.05 + k * 0.12 + 0.45)
    img, d = tt_panel(t, balance=3.5 + 50 * n_in)
    for k in range(4):
        coin_toast(d, t, 53.05 + k * 0.12, seat_xy(k + 1), seat_xy(0))
    return img


def s_mystery(t):
    n_in = 4 + (1 if t >= 55.45 + 0.45 else 0)
    img, d = tt_panel(t, balance=3.5 + 50 * n_in)
    coin_toast(d, t, 55.45, seat_xy(5), seat_xy(0))
    return img


def s_250(t):
    lt = t - 55.6
    if lt < 0.35:
        img = SC.bg_victory(t)
        d = nd(img)
        caption(d, '收款合计：250元', 640, 360, 96, t, 55.6, color=(255, 214, 80), stroke=(90, 40, 0))
        return img
    img = SC.bg_dorm_blur().copy()
    turned = lt >= 0.45
    for i, key in enumerate(('roomA', 'roomB', 'roomC')):
        tk = talk('三个室友', t)
        pose = dict(view='side' if turned else 'front', bust=True, arms=((10, 5), (10, 5)))
        SF.put(img, key, pose, 330 + i * 310, 820, 900, facing=1, expr='deadpan', talk=tk)
    d = nd(img)
    d.rounded_rectangle((440, 70, 840, 130), radius=14, fill=(255, 214, 80, 240))
    d.text((640, 100), '收款合计：250元', font=F('Black', 34), fill=(60, 40, 0, 255), anchor='mm')
    return img


def s_end(t):
    lt = t - 57.4
    img = SC.vgrad(W, H, (16, 18, 30), (6, 6, 12))
    strip = hero.make_stripes((255, 120, 80))
    off = int(40 * lt) + 60
    st = strip.crop((off, 0, off + W, H))
    img.paste(st, (0, 0), st)
    d = nd(img)
    caption(d, '一个人很难吃鸡，一群人就行。', 640, 270, 56, t, 57.5, color=(255, 255, 255), stroke=(0, 0, 0), pop=False)
    caption(d, '在TT语音，永远有人并肩相伴。', 640, 360, 44, t, 58.1, color=(255, 214, 80), stroke=(0, 0, 0), pop=False)
    if t >= 58.6:
        a = clamp((t - 58.6) / 0.3)
        d.rounded_rectangle((570, 430, 710, 530), radius=24, fill=(255, 255, 255, int(235 * a)))
        d.text((640, 480), 'TT', font=F('Black', 56), fill=(30, 30, 40, int(255 * a)), anchor='mm')
        d.text((640, 560), '（这里放TT语音Logo）', font=F('Medium', 18), fill=(170, 170, 180, int(255 * a)), anchor='mm')
    return img


SHOTS = [
    (0.0, 1.4, s_black), (1.4, 4.0, s_dorm_call),
    (4.0, 4.3, lambda t: s_turn(t, 'roomA', 4.0)), (4.3, 4.6, lambda t: s_turn(t, 'roomB', 4.3)),
    (4.6, 4.9, lambda t: s_turn(t, 'roomC', 4.6)), (4.9, 6.6, s_roomA), (6.6, 7.45, s_roomB), (7.45, 11.0, s_phone),
    (11.0, 19.0, None),
    (19.0, 20.6, s_balcony), (20.6, 23.0, s_pov), (23.0, 24.5, s_afei_run), (24.5, 26.3, s_couple), (26.3, 27.0, s_to_slope),
    (27.0, 28.2, s_handoff), (28.2, 29.3, s_skate), (29.3, 30.0, s_guard), (30.0, 31.5, s_brake), (31.5, 33.0, s_drone_up),
    (33.0, 35.4, s_airdrop), (35.4, 36.5, s_crowd), (36.5, 38.0, s_facepalm), (38.0, 39.0, s_door_close), (39.0, 40.0, s_stairs),
    (40.0, 41.0, s_fall), (41.0, 42.0, s_dive), (42.0, 43.6, s_four), (43.6, 45.0, s_victory), (45.0, 46.8, s_gaze),
    (46.8, 48.2, s_eat), (48.2, 50.6, s_wallet), (50.6, 53.1, s_vme), (53.1, 55.6, s_mystery), (55.6, 57.4, s_250),
    (57.4, 60.01, s_end),
]

SPEAKER_AV = {'大聪明': 0, '阿飞': 1, '小K': 2, '老周': 3, '星星': 4}


def overlays(img, t):
    d = nd(img)
    if 38.0 <= t < 43.4:
        p = 0.5 + 0.5 * math.sin(2 * math.pi * 2.2 * t)
        for k in range(6):
            a = int((40 + 50 * p) * (1 - k / 6))
            d.rectangle((k * 12, k * 12, W - k * 12, H - k * 12), outline=(220, 20, 30, a), width=12)
    if 4.0 <= t < 7.45 or 19.0 <= t < 43.6:
        SC.countdown_pill(d, countdown(t), t, urgent=(38.0 <= t < 43.6))
    if 4.0 <= t < 7.45:
        caption(d, '距离门禁：8分钟｜距离南门：3公里', 640, 104, 30, t, 4.0, color=(255, 255, 255), stroke=(0, 0, 0))
    if 19.0 <= t < 43.6:
        SC.title(d)
        talking = {SPEAKER_AV[ln['who']] for s, e, ln in WIN if s <= t < e and ln['who'] in SPEAKER_AV}
        SC.ttbar(d, talking, t)
    SC.killfeed(d, t, 24.7, [('阿飞', (255, 90, 100)), ('运送了', (255, 255, 255)), ('炸鸡桶', (255, 214, 80)), ('800米', (255, 255, 255))])
    SC.killfeed(d, t, 33.2, [('老周', (100, 170, 255)), ('呼叫了', (255, 255, 255)), ('空投', (255, 214, 80))])
    cur = None
    for s, e, ln in WIN:
        if s <= t < e + 0.12 and ln.get('subtitle', True):
            cur = ln
    if cur is not None:
        txt = cur.get('show', cur['text'])
        if cur['who'] == '旁白':
            SC.subtitle(d, f'（旁白）{txt}', color=(200, 220, 255))
        else:
            SC.subtitle(d, f"{cur['who']}：{txt}")
    SC.watermark(d)
    return img


def render(t, HA, hvlen):
    if 11.0 <= t < 19.0:
        return hero.render_frame(t - 11.0, HA, hvlen)
    for t0, t1, fn in SHOTS:
        if t0 <= t < t1 and fn is not None:
            img = fn(t)
            break
    else:
        img = Image.new('RGB', (W, H))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    return overlays(img, t)


SHEET = [0.5, 2.6, 4.1, 5.5, 7.0, 8.8, 10.25, 14.0, 19.9, 21.5, 23.9, 24.75, 25.6, 26.7, 27.6, 28.9, 29.6, 30.6, 32.6, 34.2,
         35.9, 37.2, 38.5, 39.5, 40.6, 41.6, 43.25, 44.3, 46.2, 47.8, 50.2, 52.0, 54.2, 56.4, 59.0]


def sheet(frames, path):
    cols = 5
    tw, th, lab = 320, 180, 26
    rows = math.ceil(len(frames) / cols)
    out = Image.new('RGB', (cols * tw, rows * (th + lab)), (12, 12, 16))
    d = ImageDraw.Draw(out)
    for i, (t, fr) in enumerate(frames):
        x, y = (i % cols) * tw, (i // cols) * (th + lab)
        d.text((x + 8, y + lab // 2), f'{t:.1f}秒', font=F('Bold', 16), fill=(255, 255, 255), anchor='lm')
        out.paste(fr.resize((tw, th), Image.LANCZOS), (x, y + lab))
    out.save(path)


def main():
    preview = '--preview' in sys.argv
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
        'char': [hero.make_character(c) for c in hero.CARDS],
        'top': hero.make_band(True),
        'bottom': hero.make_band(False),
    }
    sheet_path = os.path.join(HERE, 'sample_60s_keyframes.png')
    if preview:
        only = [float(a) for a in sys.argv[2:]] or SHEET
        sheet([(t, render(t, HA, hvlen)) for t in only], sheet_path)
        print('预览：', sheet_path)
        return
    wav = SA.build_mix(voices, hero.build_audio(hv), os.path.join(hero.CACHE, 'mix60.wav'))
    mp4 = os.path.join(HERE, 'sample_60s.mp4')
    proc = subprocess.Popen([hero.FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                             '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', mp4],
                            stdin=subprocess.PIPE)
    keep = {int(round(t * FPS)): t for t in SHEET}
    kept = []
    for i in range(int(DUR * FPS)):
        t = i / FPS
        fr = render(t, HA, hvlen)
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
