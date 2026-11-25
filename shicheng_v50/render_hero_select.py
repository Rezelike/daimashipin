#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《事成V你50》11～19秒 选英雄卡 预览视频

用代码生成的粗剪预览：
- 人物是代码画的占位剪影，正式版换成AI定妆图；
- 台词是在线AI配音（edge-tts），正式版换成真人或你选的配音；
- 叮、嗖、锁定、乌鸦叫和背景节奏都是代码合成的。

运行（在仓库根目录）：
    pip install numpy pillow imageio-ffmpeg edge-tts
    python shicheng_v50/render_hero_select.py
配音要联网，生成后缓存在 shicheng_v50/.assets/（已被 .gitignore 忽略）。
字体用仓库 fonts/ 里的 Noto Sans SC 和 JetBrains Mono。
"""
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FONT_DIR = os.path.join(REPO, 'fonts')      # 仓库自带的字体
CACHE = os.path.join(HERE, '.assets')       # 配音缓存和混音文件
TTS_DIR = os.path.join(CACHE, 'tts')
OUT_DIR = HERE
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FONT_FILES = {
    'Black': 'NotoSansSC-Black.otf',
    'Bold': 'NotoSansSC-Bold.otf',
    'Medium': 'NotoSansSC-Regular.otf',     # 仓库里没有 Medium 字重，用 Regular
    'Num': 'JetBrainsMono-Bold.ttf',        # 倒计时数字用等宽字体，跳秒时不晃
}

W, H, FPS, SR = 1280, 720, 30, 44100
FILM_OFFSET = 11.0          # 这一段在成片里从第11秒开始
PLACEHOLDER_TAG = '定妆图占位'   # 人物左上角的小标签，设成空字符串就不画
WATERMARK = '预览版｜人物为占位图'
CW, CH, SS = 560, 660, 2    # 人物画布尺寸，SS=2 倍画再缩小，边缘更平滑
CHAR_X, CHAR_Y = 60, H - CH + 40

# 每张卡：时长加起来正好8秒。lead=台词从卡片开始后0.2秒进来
CARDS = [
    dict(key='afei', name='阿飞', club='田径队', role='决斗', skill='百米11秒', loc='南门操场',
         color=(255, 70, 85), dur=1.8, line='V我50，真的假的？',
         voice='zh-CN-YunxiaNeural', pitch='+0Hz', rate=12, ini='飞'),
    dict(key='xiaok', name='小K', club='轮滑社', role='先锋', skill='下坡不踩刹车', loc='大坡顶',
         color=(255, 186, 30), dur=1.8, line='下坡？我的主场。',
         voice='zh-CN-YunjianNeural', pitch='-5Hz', rate=14, ini='K'),
    dict(key='laozhou', name='老周', club='航模社', role='控场', skill='呼叫空投', loc='人工湖',
         color=(64, 150, 255), dur=1.4, line='50块，够买俩桨。',
         voice='zh-CN-YunyangNeural', pitch='+0Hz', rate=18, ini='周'),
    dict(key='xingxing', name='星星', club='天文社', role='哨卫', skill='全图视野', loc='9号楼阳台',
         color=(172, 112, 255), dur=1.8, line='钱不要，鸡翅留一个。',
         voice='zh-CN-XiaoxiaoNeural', pitch='-4Hz', rate=12, ini='星'),
    dict(key='dacongming', name='大聪明', club='501寝室', role='？？？', skill='填错地址', loc='8号楼501',
         color=(150, 150, 160), dur=1.2, line=None, voice=None, ini='聪'),
]
STARTS = []
_acc = 0.0
for _c in CARDS:
    STARTS.append(round(_acc, 3))
    _acc += _c['dur']
DUR = round(_acc, 3)
assert abs(DUR - 8.0) < 1e-6, DUR
VOICE_LEAD = 0.15
S5 = STARTS[4]
CROW_SFX_T = S5 + 0.55      # 乌鸦叫开始
BGM_STOP_T = S5 + 0.45      # 背景节奏在乌鸦出来前掐掉，空气突然安静


# ---------------------------------------------------------------- 小工具
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    s = 1.9
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


@lru_cache(maxsize=None)
def F(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONT_FILES[weight]), max(6, int(size)))


def P(*pts):
    return [(x * SS, y * SS) for x, y in pts]


# ---------------------------------------------------------------- 配音
def decode(path):
    raw = subprocess.run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-i', path,
                          '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def trim(x, thr_db=-40):
    win = int(SR * 0.01)
    n = len(x) // win
    env = np.abs(x[:n * win]).reshape(n, win).max(axis=1)
    idx = np.where(env > 10 ** (thr_db / 20))[0]
    a = max(0, idx[0] * win - int(SR * 0.02))
    b = min(len(x), (idx[-1] + 1) * win + int(SR * 0.04))
    y = x[a:b].copy()
    fade = int(SR * 0.01)
    y[:fade] *= np.linspace(0, 1, fade)
    y[-fade:] *= np.linspace(1, 0, fade)
    return y


def tts_fit(c, max_len):
    """生成配音；太长就把语速调快，直到塞进这张卡的时间里。"""
    os.makedirs(TTS_DIR, exist_ok=True)
    rate = c['rate']
    for _ in range(6):
        mp3 = os.path.join(TTS_DIR, f"{c['key']}_r{rate}.mp3")
        if not os.path.exists(mp3):
            subprocess.run([sys.executable, '-m', 'edge_tts', '--voice', c['voice'], f'--rate=+{rate}%', f"--pitch={c['pitch']}",
                            '--text', c['line'], '--write-media', mp3], check=True, capture_output=True)
        x = trim(decode(mp3))
        length = len(x) / SR
        if length <= max_len or rate >= 40:
            return x / max(1e-6, np.abs(x).max()), rate
        rate = min(40, int(math.ceil(((1 + rate / 100) * length / max_len - 1) * 100)) + 1)
    return x / max(1e-6, np.abs(x).max()), rate


# ---------------------------------------------------------------- 音效合成
def svf_bandpass(x, freqs, q):
    low = band = 0.0
    damp = 1.0 / q
    out = np.empty_like(x)
    for i in range(len(x)):
        f = 2 * math.sin(math.pi * min(freqs[i], SR / 6) / SR)
        high = x[i] - low - damp * band
        band += f * high
        low += f * band
        out[i] = band
    return out


def norm(x, peak=1.0):
    return peak * x / max(1e-9, np.abs(x).max())


def sfx_ding():
    t = np.arange(int(SR * 0.6)) / SR
    x = (np.sin(2 * np.pi * 1568 * t) + 0.35 * np.sin(2 * np.pi * 3136 * t)
         + 0.25 * np.sin(2 * np.pi * 2349 * t)) * np.exp(-t / 0.16)
    x *= np.minimum(1, t / 0.004)
    return norm(x)


def sfx_whoosh(d=0.28):
    n = int(SR * d)
    t = np.arange(n) / SR
    noise = np.random.default_rng(1).standard_normal(n)
    y = svf_bandpass(noise, 300 + 3200 * (t / d) ** 1.5, q=1.3)
    return norm(y * np.sin(np.pi * t / d) ** 2)


def sfx_lock():
    n = int(SR * 0.5)
    t = np.arange(n) / SR
    f = 55 + 140 * np.exp(-t / 0.03)
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    click = np.diff(np.random.default_rng(2).standard_normal(n) * np.exp(-t / 0.004), prepend=0)
    fz = 700 + 1300 * np.minimum(1, t / 0.06)
    zap = 0.5 * np.sin(2 * np.pi * np.cumsum(fz) / SR) * np.exp(-t / 0.05)
    shim = 0.25 * (np.sin(2 * np.pi * 1760 * t) + 0.7 * np.sin(2 * np.pi * 2637 * t)) \
        * np.exp(-t / 0.22) * np.minimum(1, t / 0.01)
    return norm(0.9 * thump + 0.25 * click + zap + shim)


def sfx_crow():
    parts = []
    for k, (f0, f1, d) in enumerate([(560, 430, 0.26), (540, 405, 0.30)]):
        n = int(SR * d)
        t = np.arange(n) / SR
        ph = 2 * np.pi * np.cumsum(f0 + (f1 - f0) * t / d) / SR
        x = sum(np.sin(h * ph) / h ** 0.8 for h in range(1, 14))
        x = x * (1 + 0.5 * np.sin(2 * np.pi * 35 * t))
        x = x + 0.35 * np.random.default_rng(3 + k).standard_normal(n)
        x = 0.7 * svf_bandpass(x, np.full(n, 1300.0), 1.6) + 0.3 * svf_bandpass(x, np.full(n, 2600.0), 2.0)
        env = np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08)
        parts += [x * env, np.zeros(int(SR * 0.09))]
    return norm(np.concatenate(parts))


def kick():
    t = np.arange(int(SR * 0.35)) / SR
    f = 45 + 110 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    return norm(x)


def hat():
    n = int(SR * 0.06)
    t = np.arange(n) / SR
    x = np.random.default_rng(7).standard_normal(n)
    x = np.diff(np.diff(x, prepend=0), prepend=0) * np.exp(-t / 0.012)
    return norm(x)


def place(buf, x, t, gain=1.0):
    i = int(round(t * SR))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += gain * x[:j - i]


def make_bgm(total, stop):
    n = int(SR * total)
    y = np.zeros(n)
    beat = 0.5                        # 120 BPM
    k, h = kick(), hat()
    for i in range(int(total / beat) + 2):
        place(y, k, i * beat, 0.55)
        place(y, h, i * beat + beat / 2, 0.16)
        place(y, h, i * beat + beat * 0.75, 0.08)
    t = np.arange(n) / SR
    pump = 1 - 0.7 * np.exp(-(t % beat) / 0.09)
    y += (0.16 * np.sin(2 * np.pi * 55 * t) + 0.04 * np.sin(2 * np.pi * 110 * t)) * pump
    pad = np.zeros(n)
    for f in (220.0, 221.1, 329.63, 328.3):
        for hh in range(1, 6):
            pad += np.sin(2 * np.pi * f * hh * t + hh) / hh
    y += 0.012 * pad
    i, fl = int(stop * SR), int(0.04 * SR)
    y[i:i + fl] *= np.linspace(1, 0, fl)
    y[i + fl:] = 0
    return y


def build_audio(voices):
    n = int(SR * DUR)
    sfx = np.zeros(n)
    vox = np.zeros(n)
    ding, whoosh, lock, crow = sfx_ding(), sfx_whoosh(), sfx_lock(), sfx_crow()
    duck = np.ones(n)
    for k, c in enumerate(CARDS):
        s = STARTS[k]
        place(sfx, ding, s, 0.30)
        place(sfx, whoosh, s + 0.17, 0.18)
        if k < 4:
            place(vox, voices[k], s + VOICE_LEAD, 0.9)
            a, b = int((s + VOICE_LEAD) * SR), int((s + VOICE_LEAD) * SR + len(voices[k]))
            duck[a:b] = 0.5
            place(sfx, lock, s + c['dur'] - 0.3, 0.5)
    place(sfx, crow, CROW_SFX_T, 0.5)
    ker = np.ones(int(SR * 0.06)) / int(SR * 0.06)
    duck = np.convolve(duck, ker, mode='same')
    mixed = make_bgm(DUR, BGM_STOP_T) * 0.6 * duck + sfx + vox
    peak = np.abs(mixed).max()
    if peak > 0.9:
        mixed *= 0.9 / peak
    pcm = (np.clip(mixed, -1, 1) * 32767).astype(np.int16)
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, 'mix.wav')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
    return path


# ---------------------------------------------------------------- 画面素材
def make_bg(color):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base = np.array([14, 20, 28], np.float32)
    col = np.array(color, np.float32)
    g = (np.clip(0.62 - xx / W * 0.62, 0, 1) ** 1.3)[..., None]
    arr = base * (1 - g) + col * 0.55 * g
    arr *= (1 - 0.35 * (yy / H))[..., None]
    d = np.sqrt(((xx - W * 0.35) / (W * 0.8)) ** 2 + ((yy - H * 0.45) / (H * 0.75)) ** 2)
    arr *= np.clip(1.25 - d * 0.75, 0.35, 1.0)[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGB')


def make_stripes(color):
    tex = Image.new('RGBA', (W + 500, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(tex)
    slant = int(H * 0.42)
    for x in range(-slant, W + 500, 38):
        d.line([(x, H), (x + slant, 0)], fill=(255, 255, 255, 13), width=2)
    for x, wdt, a in [(140, 90, 34), (520, 46, 24), (980, 120, 20)]:
        d.polygon([(x, H), (x + wdt, H), (x + wdt + slant, 0), (x + slant, 0)], fill=tuple(color) + (a,))
    return tex


def make_bigname(name):
    size = min(400, int(860 / max(1, len(name))))
    layer = Image.new('RGBA', (W + 200, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((40, 400), name, font=F('Black', size), fill=(0, 0, 0, 0),
           stroke_width=3, stroke_fill=(255, 255, 255, 46), anchor='ls')
    return layer


def make_band(top=True):
    hgt = 130 if top else 140
    a = np.linspace(185, 0, hgt) if top else np.linspace(0, 160, hgt)
    band = Image.new('RGBA', (W, hgt), (5, 8, 12, 255))
    band.putalpha(Image.fromarray(np.repeat(a.astype(np.uint8)[:, None], W, axis=1), 'L'))
    return band


# ---- 人物占位剪影（正式版换成AI定妆图）
def body_mask(shoulder_w, arms):
    m = Image.new('L', (CW * SS, CH * SS), 0)
    d = ImageDraw.Draw(m)
    cx = 280
    d.ellipse([(cx - 62) * SS, 103 * SS, (cx + 62) * SS, 247 * SS], fill=255)
    d.rectangle([(cx - 26) * SS, 230 * SS, (cx + 26) * SS, 290 * SS], fill=255)
    hw = shoulder_w / 2
    d.polygon(P((cx - hw + 50, 278), (cx + hw - 50, 278), (cx + hw, 335), (cx + hw - 18, 660),
                (cx - hw + 18, 660), (cx - hw, 335)), fill=255)
    for sx in (cx - hw + 46, cx + hw - 46):
        d.ellipse([(sx - 48) * SS, 278 * SS, (sx + 48) * SS, 374 * SS], fill=255)
    for pts, wdt in arms:
        d.line(P(*pts), fill=255, width=int(wdt * SS), joint='curve')
        for (x, y) in pts:
            r = wdt / 2
            d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=255)
    return m


def props_afei(d, ctx):
    d.rounded_rectangle([218 * SS, 380 * SS, 342 * SS, 470 * SS], radius=10 * SS,
                        fill=(246, 246, 246, 255), outline=(30, 30, 30, 255), width=3 * SS)
    for x, y in [(231, 393), (329, 393)]:
        d.ellipse([(x - 4) * SS, (y - 4) * SS, (x + 4) * SS, (y + 4) * SS], fill=(150, 150, 150, 255))
    d.text((280 * SS, 430 * SS), '50', font=F('Black', 62 * SS), fill=(20, 20, 20, 255), anchor='mm')


def props_xiaok(d, ctx):
    helmet = (34, 34, 42, 255)
    d.polygon(P((198, 270), (362, 270), (332, 302), (228, 302)), fill=(60, 60, 72, 255))
    d.pieslice([206 * SS, 90 * SS, 354 * SS, 238 * SS], 180, 360, fill=helmet)
    d.rectangle([206 * SS, 158 * SS, 354 * SS, 172 * SS], fill=helmet)
    d.line(P((212, 165), (348, 165)), fill=(255, 200, 60, 255), width=5 * SS)
    for x in (255, 280, 305):
        d.line(P((x, 104), (x, 134)), fill=(78, 78, 90, 255), width=4 * SS)
    d.line(P((222, 170), (262, 244)), fill=(25, 25, 25, 255), width=4 * SS)
    d.line(P((338, 170), (298, 244)), fill=(25, 25, 25, 255), width=4 * SS)


def props_laozhou(d, ctx):
    strap = (25, 25, 32, 255)
    d.line(P((214, 286), (204, 660)), fill=strap, width=16 * SS)
    d.line(P((346, 286), (356, 660)), fill=strap, width=16 * SS)
    for x0 in (232, 286):
        d.rounded_rectangle([x0 * SS, 166 * SS, (x0 + 42) * SS, 196 * SS], radius=6 * SS,
                            outline=(12, 12, 12, 255), width=5 * SS)
    d.line(P((274, 178), (286, 178)), fill=(12, 12, 12, 255), width=4 * SS)
    d.line(P((240, 173), (254, 173)), fill=(255, 255, 255, 210), width=3 * SS)
    d.line(P((340, 442), (330, 395)), fill=(205, 205, 215, 255), width=3 * SS)
    d.line(P((410, 442), (420, 395)), fill=(205, 205, 215, 255), width=3 * SS)
    d.rounded_rectangle([330 * SS, 440 * SS, 420 * SS, 500 * SS], radius=10 * SS,
                        fill=(40, 40, 48, 255), outline=(205, 205, 215, 255), width=2 * SS)
    for x in (352, 398):
        d.ellipse([(x - 10) * SS, 460 * SS, (x + 10) * SS, 480 * SS], fill=(95, 95, 105, 255))


def props_xingxing(d, ctx):
    hair = (44, 28, 70, 255)
    d.ellipse([204 * SS, 90 * SS, 356 * SS, 252 * SS], fill=hair)
    d.rectangle([204 * SS, 170 * SS, 356 * SS, 318 * SS], fill=hair)
    d.ellipse([204 * SS, 286 * SS, 262 * SS, 342 * SS], fill=hair)
    d.ellipse([298 * SS, 286 * SS, 356 * SS, 342 * SS], fill=hair)
    d.ellipse([232 * SS, 128 * SS, 328 * SS, 246 * SS], fill=ctx['face'] + (255,))
    d.chord([222 * SS, 98 * SS, 338 * SS, 204 * SS], 180, 360, fill=hair)
    d.rounded_rectangle([220 * SS, 248 * SS, 340 * SS, 292 * SS], radius=16 * SS, fill=(222, 48, 60, 255))
    d.polygon(P((300, 280), (330, 282), (342, 384), (312, 388)), fill=(198, 38, 50, 255))
    leg = (200, 200, 212, 255)
    for x2 in (432, 470, 506):
        d.line(P((470, 472), (x2, 660)), fill=leg, width=6 * SS)
    d.line(P((392, 500), (546, 396)), fill=(232, 232, 240, 255), width=34 * SS)
    d.line(P((538, 401), (552, 392)), fill=(120, 120, 132, 255), width=42 * SS)
    d.line(P((394, 500), (380, 509)), fill=(80, 80, 92, 255), width=20 * SS)


def props_dacongming(d, ctx):
    hair = (38, 38, 44, 255)
    d.polygon(P((210, 156), (220, 94), (240, 126), (252, 74), (270, 118), (286, 68), (300, 116), (318, 80),
                (326, 124), (348, 100), (352, 160), (330, 122), (280, 108), (232, 124)), fill=hair)
    d.arc([214 * SS, 222 * SS, 346 * SS, 332 * SS], 0, 180, fill=(25, 25, 30, 255), width=12 * SS)
    for x in (222, 338):
        d.ellipse([(x - 24) * SS, 262 * SS, (x + 24) * SS, 312 * SS], fill=(30, 30, 36, 255),
                  outline=(255, 150, 60, 255), width=3 * SS)
    drop = (120, 200, 255, 255)
    d.polygon(P((374, 118), (362, 146), (386, 146)), fill=drop)
    d.ellipse([361 * SS, 134 * SS, 387 * SS, 160 * SS], fill=drop)


CHAR_SPEC = {
    'afei': dict(shoulder=400, arms=[([(122, 320), (42, 470), (132, 575)], 58),
                                     ([(438, 320), (518, 470), (428, 575)], 58)], props=props_afei),
    'xiaok': dict(shoulder=330, arms=[([(136, 330), (106, 500), (120, 640)], 46),
                                      ([(424, 330), (454, 500), (440, 640)], 46)], props=props_xiaok),
    'laozhou': dict(shoulder=320, arms=[([(140, 330), (95, 270), (228, 198)], 42),
                                        ([(420, 330), (450, 470), (372, 470)], 44)], props=props_laozhou),
    'xingxing': dict(shoulder=300, arms=[([(150, 330), (130, 500), (140, 650)], 40),
                                         ([(410, 330), (455, 410), (458, 445)], 40)], props=props_xingxing),
    'dacongming': dict(shoulder=330, arms=[([(140, 330), (80, 240), (205, 142)], 44),
                                           ([(420, 330), (445, 500), (430, 645)], 44)],
                       props=props_dacongming, plaid=True),
}


def make_character(c):
    spec = CHAR_SPEC[c['key']]
    mask_big = body_mask(spec['shoulder'], spec['arms'])
    mask = mask_big.resize((CW, CH), Image.LANCZOS)
    col = np.array(c['color'], np.float32)
    t = np.linspace(0, 1, CH)[:, None, None]
    top = np.clip(col * 0.55 + 255 * 0.25, 0, 255)
    grad = np.repeat(top * (1 - t) + col * 0.25 * t, CW, axis=1)
    face = tuple(int(v) for v in grad[190, 0])
    body = Image.fromarray(grad.astype(np.uint8), 'RGB').convert('RGBA')
    body.putalpha(mask)
    glow = Image.new('RGBA', (CW, CH), tuple(c['color']) + (0,))
    glow.putalpha(mask.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.85)))
    edge = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    rim = Image.new('RGBA', (CW, CH), (255, 255, 255, 0))
    rim.putalpha(edge.point(lambda v: int(min(255, v * 1.2) * 0.55)))
    out = Image.alpha_composite(Image.new('RGBA', (CW, CH), (0, 0, 0, 0)), glow)
    out = Image.alpha_composite(out, body)
    if spec.get('plaid'):
        pl = Image.new('RGBA', (CW * SS, CH * SS), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pl)
        for x in range(0, CW, 40):
            pd.line([(x * SS, 290 * SS), (x * SS, CH * SS)], fill=(255, 255, 255, 60), width=4 * SS)
        for y in range(300, CH, 40):
            pd.line([(0, y * SS), (CW * SS, y * SS)], fill=(255, 255, 255, 60), width=4 * SS)
        pl = pl.resize((CW, CH), Image.LANCZOS)
        a = np.array(pl.getchannel('A'), np.float32) * (np.array(mask, np.float32) / 255)
        pl.putalpha(Image.fromarray(a.astype(np.uint8), 'L'))
        out = Image.alpha_composite(out, pl)
    out = Image.alpha_composite(out, rim)
    props = Image.new('RGBA', (CW * SS, CH * SS), (0, 0, 0, 0))
    spec['props'](ImageDraw.Draw(props), {'face': face})
    return Image.alpha_composite(out, props.resize((CW, CH), Image.LANCZOS))


# ---------------------------------------------------------------- 每一帧
AVATARS = [('聪', (150, 150, 160), None)] + [(c['ini'], c['color'], k) for k, c in enumerate(CARDS[:4])]


def card_at(t):
    k = 0
    for i, s in enumerate(STARTS):
        if t >= s - 1e-9:
            k = i
    return k, STARTS[k]


def speaking(card_k, t, vlen):
    a = STARTS[card_k] + VOICE_LEAD
    return a <= t < a + vlen[card_k]


def draw_topbar(d, t, vlen):
    d.rounded_rectangle((30, 22, 42, 44), radius=6, fill=(255, 255, 255, 235))
    d.arc((25, 30, 47, 52), 0, 180, fill=(255, 255, 255, 235), width=2)
    d.line((36, 52, 36, 57), fill=(255, 255, 255, 235), width=2)
    d.text((56, 38), 'TT语音 · 组队中', font=F('Bold', 24), fill=(255, 255, 255, 240), anchor='lm')
    secs = int(480 - ((FILM_OFFSET + t) - 4) * (50 / 15))
    mm, ss = divmod(max(0, secs), 60)
    d.rounded_rectangle((506, 15, 774, 61), radius=23, fill=(200, 34, 50, 235))
    d.text((530, 38), '门禁倒计时', font=F('Medium', 19), fill=(255, 255, 255, 235), anchor='lm')
    d.text((754, 39), f'{mm:02d}:{ss:02d}', font=F('Num', 32), fill=(255, 255, 255, 255), anchor='rm')
    d.rounded_rectangle((884, 14, 1258, 62), radius=24, fill=(8, 12, 18, 215), outline=(255, 255, 255, 45), width=1)
    for i in range(6):
        cx, cy, r = 912 + i * 57, 38, 18
        if i == 5:   # 第6个：神秘人，全片灰着（其实是宿管阿姨）
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(62, 62, 70, 255))
            d.text((cx, cy), '?', font=F('Bold', 20), fill=(150, 150, 158, 255), anchor='mm')
            continue
        ini, col, k = AVATARS[i]
        tj = -1.0 if k is None else STARTS[k]
        if t < tj:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, 55), width=2)
            d.text((cx, cy - 1), '+', font=F('Medium', 20), fill=(255, 255, 255, 70), anchor='mm')
            continue
        sc = ease_back((t - tj) / 0.28) if tj >= 0 else 1.0
        if k is not None and speaking(k, t, vlen):
            ph = (t * 4) % 1
            d.ellipse((cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5), outline=(60, 235, 140, 255), width=3)
            r2 = r + 5 + 10 * ph
            d.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=(60, 235, 140, int(160 * (1 - ph))), width=2)
        rr = max(1.0, r * sc)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=tuple(col) + (255,))
        d.text((cx, cy), ini, font=F('Bold', 18 * sc), fill=(255, 255, 255, 255), anchor='mm')


def draw_textblock(d, c, lt, k):
    x0, col = 700, tuple(c['color'])
    fast = k == 4
    t_club, t_name = (0.36, 0.42) if fast else (0.42, 0.48)
    t_rows = [0.50, 0.58, 0.66] if fast else [0.62, 0.74, 0.86]
    a = clamp((lt - t_club) / 0.12)
    if a > 0:
        f = F('Bold', 24)
        w = f.getlength(c['club'])
        dx = int(30 * (1 - ease_out(a)))
        d.rounded_rectangle((x0 + dx, 170, x0 + dx + w + 28, 208), radius=6, fill=col + (int(235 * a),))
        d.text((x0 + dx + 14, 189), c['club'], font=f, fill=(255, 255, 255, int(255 * a)), anchor='lm')
    a = clamp((lt - t_name) / 0.14)
    if a > 0:
        sc = 1.25 - 0.25 * ease_out(a)
        d.text((x0, 335), c['name'], font=F('Black', 124 * sc), fill=(255, 255, 255, int(255 * a)), anchor='ls')
        bw = int(96 * ease_out((lt - t_name - 0.05) / 0.15))
        if bw > 0:
            d.rectangle((x0, 352, x0 + bw, 360), fill=col + (255,))
    for i, (lab, val) in enumerate([('定位', c['role']), ('技能', c['skill']), ('位置', c['loc'])]):
        a = clamp((lt - t_rows[i]) / 0.14)
        if a <= 0:
            continue
        yc, dx, A = 410 + i * 58, int(40 * (1 - ease_out(a))), int(255 * a)
        d.rectangle((x0 + dx, yc - 20, x0 + dx + 68, yc + 20), outline=col + (A,), width=2)
        d.text((x0 + dx + 34, yc), lab, font=F('Medium', 22), fill=col + (A,), anchor='mm')
        vcol = (200, 200, 205, A) if (fast and lab == '定位') else (255, 255, 255, A)
        d.text((x0 + dx + 90, yc), val, font=F('Bold', 34), fill=vcol, anchor='lm')


def lock_time(k):
    return CARDS[k]['dur'] - (0.35 if k == 4 else 0.3)


def draw_lock(d, c, lt, k):
    col = tuple(c['color'])
    lt0 = lock_time(k)
    appear = clamp((lt - 0.3) / 0.15)
    if appear <= 0:
        return
    cx, cy, bw, bh = 850, 612, 300, 70
    locked = lt >= lt0
    sc = 1 + 0.12 * math.sin(math.pi * clamp((lt - lt0) / 0.2)) if (locked and k < 4) else 1.0
    w2, h2, chf = bw * sc / 2, bh * sc / 2, 16 * sc
    poly = [(cx - w2 + chf, cy - h2), (cx + w2, cy - h2), (cx + w2, cy + h2 - chf),
            (cx + w2 - chf, cy + h2), (cx - w2, cy + h2), (cx - w2, cy - h2 + chf)]
    if not locked:
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * 3 * lt)
        d.polygon(poly, fill=(16, 22, 30, int(230 * appear)), outline=col + (int((150 + 100 * pulse) * appear),), width=3)
        d.text((cx, cy), '锁  定', font=F('Black', 34), fill=(255, 255, 255, int(255 * appear)), anchor='mm')
    elif k < 4:
        d.polygon(poly, fill=col + (255,), outline=(255, 255, 255, 255), width=3)
        d.text((cx, cy), '已锁定', font=F('Black', 34 * sc), fill=(255, 255, 255, 255), anchor='mm')
        p = (lt - lt0) / 0.35
        if p < 1:
            r = 40 + 280 * ease_out(p)
            d.ellipse((cx - r, cy - r * 0.55, cx + r, cy + r * 0.55), outline=col + (int(220 * (1 - p)),), width=4)
    else:   # 大聪明：锁定失败，按钮变灰
        d.polygon(poly, fill=(62, 62, 68, 255), outline=(105, 105, 112, 255), width=3)
        d.text((cx, cy), '锁  定', font=F('Black', 34), fill=(135, 135, 140, 255), anchor='mm')


def draw_crow(d, t):
    t0, dur, S = S5 + 0.5, 0.72, 1.7
    p = (t - t0) / dur
    if not 0 <= p <= 1:
        return
    x = 1420 - 1640 * p
    y = 265 - 95 * p + 20 * math.sin(p * math.pi * 3)
    flap = math.sin(2 * math.pi * 9 * (t - t0))

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
    for tc in (CROW_SFX_T, CROW_SFX_T + 0.35):
        u = (t - tc) / 0.28
        if 0 <= u <= 1:
            sc = ease_back(u / 0.4) if u < 0.4 else 1.0
            d.text((x + 16 * S, y - 60 * S), '嘎！', font=F('Black', 48 * sc), fill=(255, 255, 255, 255),
                   anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0, 255))


def draw_subtitle(d, t, vlen):
    for k, c in enumerate(CARDS[:4]):
        a0 = STARTS[k] + VOICE_LEAD
        a1 = min(STARTS[k] + c['dur'], a0 + vlen[k] + 0.15)
        if a0 <= t < a1:
            d.text((640, 698), f"{c['name']}：{c['line']}", font=F('Bold', 32), fill=(255, 255, 255, 255),
                   anchor='ms', stroke_width=4, stroke_fill=(0, 0, 0, 220))
    if CROW_SFX_T <= t < S5 + 1.2:
        d.text((640, 698), '（一只乌鸦飞过）', font=F('Medium', 28), fill=(215, 215, 220, 255),
               anchor='ms', stroke_width=4, stroke_fill=(0, 0, 0, 220))


WHITE = Image.new('RGB', (W, H), (255, 255, 255))


def render_frame(t, A, vlen):
    k, s = card_at(t)
    c, lt = CARDS[k], t - s
    frame = A['bg'][k].copy()
    off = int(60 * lt) + 60
    strip = A['stripes'][k].crop((off, 0, off + W, H))
    frame.paste(strip, (0, 0), strip)
    bn = A['bigname'][k]
    frame.paste(bn, (-int(30 * lt), 0), bn)
    alpha = clamp((lt - 0.2) / 0.12)
    if alpha > 0:
        p = ease_out((lt - 0.2) / 0.3)
        sc = 0.92 + 0.08 * p
        ch = A['char'][k]
        if sc < 0.999:
            ch = ch.resize((int(CW * sc), int(CH * sc)), Image.BILINEAR)
        if alpha < 1:
            ch = ch.copy()
            ch.putalpha(ch.getchannel('A').point(lambda v: int(v * alpha)))
        x = int(CHAR_X + (CW - ch.width) / 2 - 340 * (1 - p))
        y = int(CHAR_Y + (CH - ch.height))
        frame.paste(ch, (x, y), ch)
    frame.paste(A['top'], (0, 0), A['top'])
    frame.paste(A['bottom'], (0, H - A['bottom'].height), A['bottom'])
    d = ImageDraw.Draw(frame, 'RGBA')
    if alpha > 0 and PLACEHOLDER_TAG:
        tag = PLACEHOLDER_TAG
        tw = F('Medium', 16).getlength(tag)
        d.rounded_rectangle((40, 112, 40 + tw + 24, 142), radius=8, fill=(0, 0, 0, 140), outline=(255, 255, 255, 90))
        d.text((52, 127), tag, font=F('Medium', 16), fill=(255, 255, 255, int(210 * alpha)), anchor='lm')
    draw_topbar(d, t, vlen)
    draw_textblock(d, c, lt, k)
    draw_lock(d, c, lt, k)
    if k == 4:
        draw_crow(d, t)
    draw_subtitle(d, t, vlen)
    if WATERMARK:
        d.text((20, 708), WATERMARK, font=F('Medium', 15), fill=(255, 255, 255, 120), anchor='ls')
    fa = 0.9 * (1 - lt / 0.2) ** 2 if lt < 0.2 else 0.0
    if k < 4 and 0 <= lt - lock_time(k) < 0.1:
        fa = max(fa, 0.5 * (1 - (lt - lock_time(k)) / 0.1))
    if fa > 0:
        frame = Image.blend(frame, WHITE, fa)
    if k == 4 and lt >= lock_time(4):
        u = lt - lock_time(4)
        dx = int(12 * math.sin(2 * math.pi * 16 * u) * math.exp(-u / 0.3))
        dy = int(4 * math.sin(2 * math.pi * 21 * u) * math.exp(-u / 0.3))
        shaken = Image.new('RGB', (W, H), (0, 0, 0))
        shaken.paste(frame, (dx, dy))
        frame = shaken
    return frame


# ---------------------------------------------------------------- 主流程
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    voices, vlen = [], []
    for k, c in enumerate(CARDS[:4]):
        x, rate = tts_fit(c, c['dur'] - VOICE_LEAD - 0.02)
        voices.append(x)
        vlen.append(len(x) / SR)
        print(f"配音 {c['name']}: {len(x) / SR:.2f}s（语速 +{rate}%）")
    wav = build_audio(voices)

    A = {
        'bg': [make_bg(c['color']) for c in CARDS],
        'stripes': [make_stripes(c['color']) for c in CARDS],
        'bigname': [make_bigname(c['name']) for c in CARDS],
        'char': [make_character(c) for c in CARDS],
        'top': make_band(True),
        'bottom': make_band(False),
    }

    mp4 = os.path.join(OUT_DIR, 'hero_select_11-19s.mp4')
    proc = subprocess.Popen([FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                             '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
                             '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                             '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', mp4],
                            stdin=subprocess.PIPE)
    sheet_times = [(0.35, '阿飞滑入'), (1.15, '字弹出+配音'), (1.62, '锁定'),
                   (2.75, '小K'), (4.55, '老周'), (6.00, '星星'),
                   (6.65, '星星锁定'), (7.45, '乌鸦飞过'), (7.85, '大聪明锁定失败')]
    sheet_frames = {int(round(t * FPS)): (t, label) for t, label in sheet_times}
    kept = []
    n_frames = int(round(DUR * FPS))
    for i in range(n_frames):
        t = i / FPS
        fr = render_frame(t, A, vlen)
        proc.stdin.write(fr.tobytes())
        if i in sheet_frames:
            kept.append((sheet_frames[i], fr.copy()))
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit('ffmpeg 编码失败')

    tw, th, lab_h = 426, 240, 34
    sheet = Image.new('RGB', (tw * 3, (th + lab_h) * 3), (12, 12, 16))
    sd = ImageDraw.Draw(sheet)
    for idx, ((t, label), fr) in enumerate(kept):
        col, row = idx % 3, idx // 3
        x, y = col * tw, row * (th + lab_h)
        sd.text((x + 10, y + lab_h // 2), f'{FILM_OFFSET + t:.1f}秒  {label}', font=F('Bold', 18),
                fill=(255, 255, 255), anchor='lm')
        sheet.paste(fr.resize((tw, th), Image.LANCZOS), (x, y + lab_h))
    sheet.save(os.path.join(OUT_DIR, 'hero_select_11-19s_keyframes.png'))

    gif = os.path.join(OUT_DIR, 'hero_select_11-19s_silent.gif')
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', mp4, '-vf',
                    'fps=12,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];'
                    '[b][p]paletteuse=dither=bayer:bayer_scale=4', gif], check=True)
    print('完成：', mp4)


if __name__ == '__main__':
    main()
