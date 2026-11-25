# -*- coding: utf-8 -*-
"""60 秒样片的声音：台词表、在线配音、音效和配乐合成、混音。"""
import math
import os
import subprocess
import sys
import time
import wave

import numpy as np

import render_hero_select as hero

SR = hero.SR
DUR = 60.0
TTS_DIR = hero.TTS_DIR
RNG = np.random.default_rng(2026)

V = dict(
    dacong=('zh-CN-YunxiNeural', '+0Hz'),
    afei=('zh-CN-YunxiaNeural', '+0Hz'),
    xiaok=('zh-CN-YunjianNeural', '-5Hz'),
    zhou=('zh-CN-YunyangNeural', '+0Hz'),
    xing=('zh-CN-XiaoxiaoNeural', '-4Hz'),
    suguan=('zh-CN-liaoning-XiaobeiNeural', '+0Hz'),
    narr=('zh-CN-YunjianNeural', '-15Hz'),
    rider=('zh-CN-YunyangNeural', '+6Hz'),
    roomA=('zh-CN-YunjianNeural', '+8Hz'),
    roomB=('zh-CN-YunyangNeural', '-14Hz'),
    roomC=('zh-CN-YunxiNeural', '+10Hz'),
    girl=('zh-CN-XiaoyiNeural', '+0Hz'),
)

# who=字幕里的名字；voices=[(声音键, 相对起点秒, 增益)]；start=开始时间；max_len=最长秒数
LINES = [
    dict(key='rider', who='外卖小哥', text='兄弟，炸鸡放南门了啊！', voices=[('rider', 0, 1.0)], start=0.55, max_len=1.55, rate=10, fx='phone'),
    dict(key='dacong1', who='大聪明', text='南门？？我住北区啊！', voices=[('dacong', 0, 1.0)], start=2.15, max_len=1.6, rate=12),
    dict(key='roomA1', who='室友A', text='大聪明，你填的南门？', voices=[('roomA', 0, 1.0)], start=4.95, max_len=1.65, rate=25),
    dict(key='roomB1', who='室友B', text='这把，拉完了。', voices=[('roomB', 0, 1.0)], start=6.65, max_len=0.95, rate=15),
    dict(key='narr', who='旁白', text='此时的他还不知道，这条帖子，将惊动全校。', voices=[('narr', 0, 1.0)], start=7.7, max_len=3.25, rate=18),
    dict(key='xing1', who='星星', text='报点：外卖架三层，红袋子。', voices=[('xing', 0, 1.0)], start=19.3, max_len=2.4, rate=15),
    dict(key='afei1', who='阿飞', text='看见了！', voices=[('afei', 0, 1.0)], start=21.85, max_len=0.8, rate=10),
    dict(key='afei2', who='阿飞', text='小K，坡顶，接！', show='小K！坡顶！接！', voices=[('afei', 0, 1.0)], start=24.2, max_len=1.7, rate=20),
    dict(key='xing2', who='星星', text='绕湖来不及了！', voices=[('xing', 0, 1.0)], start=30.3, max_len=1.25, rate=15),
    dict(key='zhou1', who='老周', text='交给我。', voices=[('zhou', 0, 1.0)], start=31.8, max_len=0.9, rate=0),
    dict(key='crowd', who='路人', text='空投！', voices=[('girl', 0, 0.8), ('roomC', 0.05, 0.7), ('xing', 0.09, 0.5), ('dacong', 0.13, 0.5)],
         start=35.55, max_len=0.7, rate=10),
    dict(key='xing3', who='星星', text='全校最大的显眼包。', voices=[('xing', 0, 1.0)], start=36.65, max_len=1.3, rate=12),
    dict(key='roomB2', who='室友B', text='这把，夯爆了！', voices=[('roomB', 0, 1.0)], start=44.0, max_len=1.0, rate=5),
    dict(key='suguan1', who='宿管阿姨', text='几个人吃啊？', show='……几个人吃啊？', voices=[('suguan', 0, 1.0)],
         start=45.75, max_len=1.05, rate=20),
    dict(key='dacong2', who='大聪明', text='说好的V你们50……', voices=[('dacong', 0, 1.0)], start=48.25, max_len=1.75, rate=20),
    dict(key='afei3', who='阿飞', text='那我们V你50，下周四再来！', show='……那我们V你50，下周四再来！', voices=[('afei', 0, 1.0)],
         start=50.65, max_len=2.25, rate=25),
    dict(key='all1', who='全员', text='包的！', voices=[('dacong', 0, 0.6), ('afei', 0.02, 0.6), ('xiaok', 0.04, 0.6), ('zhou', 0.03, 0.5),
                                                     ('xing', 0.05, 0.6), ('roomA', 0.06, 0.5)],
         start=52.95, max_len=0.5, rate=10),
    dict(key='suguan2', who='宿管阿姨', text='阿姨也V你50，鸡腿留一个。', voices=[('suguan', 0, 1.0)], start=53.4, max_len=2.2, rate=30),
    dict(key='room3', who='三个室友', text='二百五！', voices=[('roomA', 0, 0.7), ('roomB', 0.03, 0.7), ('roomC', 0.06, 0.7)],
         start=56.1, max_len=0.7, rate=10),
    dict(key='laugh', who='', text='哈哈哈哈哈哈！', voices=[('dacong', 0, 0.5), ('afei', 0.15, 0.5), ('xing', 0.3, 0.45), ('girl', 0.45, 0.4),
                                                       ('xiaok', 0.6, 0.4), ('suguan', 0.75, 0.45)],
         start=57.5, max_len=1.8, rate=0, subtitle=False),
]


# ---------------------------------------------------------------- 配音
def tts(tag, voice, pitch, text, rate, max_len):
    os.makedirs(TTS_DIR, exist_ok=True)
    x = None
    for _ in range(7):
        sign = '+' if rate >= 0 else '-'
        mp3 = os.path.join(TTS_DIR, f's60_{tag}_r{rate}.mp3')
        if not os.path.exists(mp3) or os.path.getsize(mp3) == 0:
            # 在线配音偶尔不出声，隔一会儿重试几次
            for attempt in range(4):
                r = subprocess.run([sys.executable, '-m', 'edge_tts', '--voice', voice, f'--rate={sign}{abs(rate)}%',
                                    f'--pitch={pitch}', '--text', text, '--write-media', mp3], capture_output=True)
                if r.returncode == 0 and os.path.getsize(mp3) > 0:
                    break
                time.sleep(1.5 * (attempt + 1))
            else:
                raise RuntimeError(f'配音失败：{voice} {text}')
        x = hero.trim(hero.decode(mp3))
        length = len(x) / SR
        if length <= max_len or rate >= 40:
            break
        rate = min(40, int(math.ceil(((1 + rate / 100) * length / max_len - 1) * 100)) + 1)
    return hero.norm(x), rate


def phone_fx(x):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    spec[(f < 350) | (f > 3200)] = 0
    y = np.fft.irfft(spec, len(x))
    y = np.tanh(3 * y / max(1e-6, np.abs(y).max()))
    y += 0.012 * RNG.standard_normal(len(y))
    return hero.norm(y, 0.9)


def build_voices():
    """生成全部台词，返回 {key: (波形, 时长)}。"""
    out = {}
    for ln in LINES:
        mix = None
        for i, (vk, off, gain) in enumerate(ln['voices']):
            voice, pitch = V[vk]
            x, rate = tts(f"{ln['key']}_{i}_{vk}", voice, pitch, ln['text'], ln['rate'], ln['max_len'] - off)
            if ln.get('fx') == 'phone':
                x = phone_fx(x)
            pad = np.zeros(int(off * SR) + len(x))
            pad[int(off * SR):] += gain * x
            if mix is None:
                mix = pad
            else:
                n = max(len(mix), len(pad))
                mix = np.pad(mix, (0, n - len(mix))) + np.pad(pad, (0, n - len(pad)))
            print(f"  配音 {ln['key']}/{vk}: {len(x) / SR:.2f}s（语速 {rate:+d}%）")
        mix = hero.norm(mix, 0.95)
        out[ln['key']] = (mix, len(mix) / SR)
    return out


def line_windows(voices):
    """[(start, end, line)]，用来画字幕、对口型、TT头像说话光圈。"""
    return [(ln['start'], ln['start'] + voices[ln['key']][1], ln) for ln in LINES]


# ---------------------------------------------------------------- 音效
def T(d):
    return np.arange(int(SR * d)) / SR


def env_ar(t, a, r, d):
    return np.minimum(1, t / max(a, 1e-4)) * np.clip((d - t) / max(r, 1e-4), 0, 1)


def lowpass(x, k):
    k = max(1, int(k))
    return np.convolve(x, np.ones(k) / k, mode='same')


def sfx_buzz():
    parts = []
    for _ in range(2):
        t = T(0.2)
        x = 0.6 * np.sign(np.sin(2 * np.pi * 165 * t)) + 0.3 * np.sin(2 * np.pi * 330 * t)
        parts += [x * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t)) * env_ar(t, 0.01, 0.02, 0.2), np.zeros(int(SR * 0.08))]
    return hero.norm(lowpass(np.concatenate(parts), 6))


def sfx_dong():
    t = T(1.4)
    f = 48 + 60 * np.exp(-t / 0.06)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    hit = lowpass(RNG.standard_normal(len(t)) * np.exp(-t / 0.02), 30)
    return hero.norm(boom + 0.6 * hit + 0.15 * np.sin(2 * np.pi * 110 * t) * np.exp(-t / 0.6))


def sfx_tap():
    t = T(0.03)
    return hero.norm(np.diff(RNG.standard_normal(len(t)), prepend=0) * np.exp(-t / 0.004))


def sfx_steps(d, rate=7.0):
    y = np.zeros(int(SR * d))
    t1 = T(0.09)
    thump = np.sin(2 * np.pi * 70 * t1) * np.exp(-t1 / 0.03) + 0.3 * lowpass(RNG.standard_normal(len(t1)), 8) * np.exp(-t1 / 0.01)
    k = 0.0
    while k < d:
        hero.place(y, thump, k, 0.8)
        k += 1 / rate
    return hero.norm(y)


def sfx_wind(d):
    t = T(d)
    x = lowpass(RNG.standard_normal(len(t)), 40) * (0.4 + 0.6 * np.sin(np.pi * t / d) ** 2)
    return hero.norm(x)


def sfx_pop():
    t = T(0.12)
    x = np.sin(2 * np.pi * np.cumsum(600 + 900 * t / 0.12) / SR) * np.exp(-t / 0.04)
    return hero.norm(x)


def sfx_choir(d=1.8):
    t = T(d)
    y = np.zeros(len(t))
    for f0 in (220.0, 261.63, 329.63, 440.0):
        for det in (-0.003, 0.0, 0.003):
            f = f0 * (1 + det) * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t + f0))
            ph = 2 * np.pi * np.cumsum(f) / SR
            for k in range(1, 22):
                fk = f0 * k
                a = (np.exp(-((fk - 800) / 160) ** 2) + 0.7 * np.exp(-((fk - 1150) / 220) ** 2)
                     + 0.3 * np.exp(-((fk - 2900) / 320) ** 2) + 0.05) / k ** 0.6
                y += a * np.sin(k * ph)
    return hero.norm(y * env_ar(t, 0.35, 0.5, d))


def sfx_roll(d):
    t = T(d)
    x = lowpass(RNG.standard_normal(len(t)), 25) * (0.7 + 0.3 * np.sin(2 * np.pi * 18 * t))
    clicks = (RNG.random(len(t)) < 0.0015) * RNG.standard_normal(len(t)) * 3
    return hero.norm(x + clicks)


def sfx_screech(d=0.6):
    t = T(d)
    tone = np.sin(2 * np.pi * np.cumsum(3000 - 900 * t / d) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 37 * t))
    noise = hero.svf_bandpass(RNG.standard_normal(len(t)), np.full(len(t), 3500.0), 3.0)
    sparks = (RNG.random(len(t)) < 0.004) * RNG.standard_normal(len(t)) * 4
    return hero.norm((0.6 * tone + noise + sparks) * env_ar(t, 0.02, 0.2, d))


def sfx_prop(d, ramp=0.0):
    t = T(d)
    f = 150 + 40 * np.minimum(1, t / max(ramp, 1e-3)) if ramp else np.full(len(t), 190.0)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph) / k for k in range(1, 9)) * (0.7 + 0.3 * np.sin(2 * np.pi * 31 * t))
    x += 0.4 * lowpass(RNG.standard_normal(len(t)), 6)
    return hero.norm(x * env_ar(t, 0.15, 0.3, d))


def sfx_beeps(d=4.2):
    y = np.zeros(int(SR * d))
    tb = T(0.06)
    beep = np.sin(2 * np.pi * 1250 * tb) * env_ar(tb, 0.004, 0.02, 0.06)
    k, gap = 0.0, 0.55
    while k < d - 0.06:
        hero.place(y, beep, k, 1.0)
        k += gap
        gap = max(0.07, gap * 0.82)
    return hero.norm(y)


def sfx_heart(d, period=0.8):
    y = np.zeros(int(SR * d))
    t1 = T(0.16)
    lub = np.sin(2 * np.pi * 52 * t1) * np.exp(-t1 / 0.05)
    k = 0.0
    while k < d:
        hero.place(y, lub, k, 1.0)
        hero.place(y, lub, k + 0.18, 0.6)
        k += period
        period *= 1.08
    return hero.norm(y)


def sfx_click():
    y = np.zeros(int(SR * 0.16))
    t1 = T(0.04)
    c = np.diff(RNG.standard_normal(len(t1)), prepend=0) * np.exp(-t1 / 0.003) + 0.6 * np.sin(2 * np.pi * 1900 * t1) * np.exp(-t1 / 0.012)
    hero.place(y, c, 0.0, 1.0)
    hero.place(y, c, 0.07, 0.8)
    return hero.norm(y)


def sfx_fanfare():
    y = np.zeros(int(SR * 1.6))
    for i, f in enumerate((392.0, 523.25, 659.25, 783.99)):
        t = T(0.9 if i == 3 else 0.22)
        x = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 10)) * env_ar(t, 0.01, 0.15, len(t) / SR)
        hero.place(y, x, i * 0.11, 0.8)
    t = T(1.2)
    chord = sum(np.sin(2 * np.pi * f * t) for f in (523.25, 659.25, 783.99, 1046.5)) * env_ar(t, 0.05, 0.6, 1.2)
    hero.place(y, chord, 0.44, 0.5)
    cym = lowpass(np.diff(RNG.standard_normal(int(SR * 1.2)), prepend=0), 2) * np.exp(-T(1.2) / 0.35)
    hero.place(y, cym, 0.44, 0.35)
    return hero.norm(y)


def sfx_slap():
    t = T(0.12)
    x = np.diff(RNG.standard_normal(len(t)), prepend=0) * np.exp(-t / 0.012) + 0.5 * np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.03)
    return hero.norm(x)


def sfx_slurp():
    t = T(0.45)
    x = hero.svf_bandpass(RNG.standard_normal(len(t)), 700 + 1800 * t / 0.45, 4.0) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t))
    return hero.norm(x * env_ar(t, 0.05, 0.1, 0.45))


def sfx_coin():
    y = np.zeros(int(SR * 0.6))
    for i, f in enumerate((1318.5, 1760.0)):
        t = T(0.45)
        hero.place(y, (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t / 0.12), i * 0.08, 1.0)
    return hero.norm(y)


def sfx_thud():
    t = T(0.5)
    f = 40 + 70 * np.exp(-t / 0.04)
    return hero.norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.15) + 0.3 * lowpass(RNG.standard_normal(len(t)), 12) * np.exp(-t / 0.03))


def sfx_swell(d=1.0):
    t = T(d)
    return hero.norm(lowpass(RNG.standard_normal(len(t)), 60) * (t / d) ** 2 * env_ar(t, 0.01, 0.05, d))


def sfx_lockon():
    y = np.zeros(int(SR * 0.3))
    t1 = T(0.05)
    b = np.sin(2 * np.pi * 1650 * t1) * env_ar(t1, 0.003, 0.01, 0.05)
    hero.place(y, b, 0, 1)
    hero.place(y, b, 0.09, 1)
    return hero.norm(y)


def sfx_zoom():
    t = T(0.5)
    x = np.sin(2 * np.pi * np.cumsum(300 + 700 * t / 0.5) / SR) * 0.4 + 0.3 * lowpass(RNG.standard_normal(len(t)), 10)
    return hero.norm(x * env_ar(t, 0.05, 0.1, 0.5))


# ---------------------------------------------------------------- 配乐
def pad(freqs, d, bright=1.6, attack=0.8, release=0.8):
    t = T(d)
    y = np.zeros(len(t))
    for f0 in freqs:
        for det in (-0.003, 0.003):
            for k in range(1, 8):
                y += np.sin(2 * np.pi * f0 * (1 + det) * k * t + k) / k ** bright
    return hero.norm(y * env_ar(t, attack, release, d))


def marimba(f, d=0.35):
    t = T(d)
    return (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t / 0.03)) * np.exp(-t / 0.12)


def snare():
    t = T(0.18)
    return hero.norm(0.6 * RNG.standard_normal(len(t)) * np.exp(-t / 0.05) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04))


def music_heist(d, bpm=128):
    y = np.zeros(int(SR * d))
    beat = 60 / bpm
    k, h, s = hero.kick(), hero.hat(), snare()
    bass_notes = [55.0, 55.0, 65.41, 55.0, 49.0, 49.0, 58.27, 49.0]
    i = 0
    while i * beat < d:
        tb = i * beat
        hero.place(y, k, tb, 0.6)
        if i % 2 == 1:
            hero.place(y, s, tb, 0.35)
        for q in range(4):
            hero.place(y, h, tb + q * beat / 4, 0.12 if q % 2 else 0.07)
        f = bass_notes[i % len(bass_notes)]
        tt = T(beat * 0.9)
        bass = sum(np.sin(2 * np.pi * f * m * tt) / m ** 1.3 for m in range(1, 6)) * np.exp(-tt / 0.25)
        hero.place(y, bass, tb, 0.35)
        i += 1
    return hero.norm(y)


def music_playful(d, bpm=140):
    y = np.zeros(int(SR * d))
    beat = 60 / bpm
    mel = [523.25, 659.25, 783.99, 659.25, 587.33, 698.46, 880.0, 698.46, 659.25, 783.99, 1046.5, 783.99, 587.33, 493.88, 392.0, 493.88]
    bass = [130.81, 130.81, 174.61, 174.61, 164.81, 164.81, 98.0, 98.0]
    i = 0
    while i * beat / 2 < d:
        hero.place(y, marimba(mel[i % len(mel)]), i * beat / 2, 0.5)
        if i % 2 == 0:
            hero.place(y, marimba(bass[(i // 2) % len(bass)], 0.5), i * beat / 2, 0.5)
            hero.place(y, hero.kick(), i * beat / 2, 0.25 if (i // 2) % 2 == 0 else 0.0)
        i += 1
    return hero.norm(y)


def fade_cut(x, d_in=0.03, d_out=0.04):
    n_in, n_out = int(SR * d_in), int(SR * d_out)
    if n_in:
        x[:n_in] *= np.linspace(0, 1, n_in)
    if n_out:
        x[-n_out:] *= np.linspace(1, 0, n_out)
    return x


# ---------------------------------------------------------------- 混音
def build_mix(voices, hero_wav, out_path):
    n = int(SR * DUR)
    vox, sfx, mus = np.zeros(n), np.zeros(n), np.zeros(n)
    P = hero.place

    for ln in LINES:
        P(vox, voices[ln['key']][0], ln['start'], 0.95)

    # 0–11 秒
    P(sfx, sfx_buzz(), 0.05, 0.55)
    for tt in (4.0, 4.3, 4.6):
        P(sfx, sfx_dong(), tt, 0.7)
    for i in range(14):
        P(sfx, sfx_tap(), 7.55 + i * 0.12, 0.25)
    P(sfx, sfx_dong(), 10.2, 0.8)
    P(mus, fade_cut(pad([55.0, 82.41, 110.0], 3.5, 1.4, 0.6, 0.6)), 4.0, 0.25)
    P(mus, fade_cut(pad([146.83, 174.61, 220.0, 293.66], 3.8, 1.2, 1.0, 0.8)), 7.3, 0.35)

    # 11–19 秒：选英雄卡自带的混音
    with wave.open(hero_wav) as w:
        hx = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2)[:, 0].astype(np.float32) / 32768
    P(sfx, hx, 11.0, 1.0)

    # 19–38 秒：接力
    P(sfx, hero.sfx_whoosh(), 19.0, 0.3)
    P(sfx, sfx_zoom(), 20.55, 0.35)
    P(sfx, sfx_lockon(), 21.0, 0.5)
    P(sfx, sfx_steps(1.6, 9), 23.3, 0.35)
    P(sfx, sfx_wind(1.6), 23.4, 0.35)
    P(sfx, hero.sfx_whoosh(0.4), 24.65, 0.6)
    P(sfx, sfx_wind(1.0), 24.75, 0.5)
    P(sfx, sfx_pop(), 24.95, 0.5)
    P(sfx, hero.sfx_ding(), 24.7, 0.2)
    P(sfx, sfx_steps(0.7, 9), 26.3, 0.35)
    P(sfx, sfx_choir(1.8), 27.0, 0.55)
    P(sfx, sfx_roll(1.1), 28.2, 0.35)
    P(sfx, sfx_screech(0.5), 28.75, 0.35)
    P(sfx, hero.sfx_ding(), 28.8, 0.2)
    P(sfx, sfx_roll(0.5), 30.0, 0.3)
    P(sfx, sfx_screech(0.6), 30.35, 0.45)
    P(sfx, sfx_prop(1.5, ramp=0.6), 31.95, 0.3)
    P(sfx, sfx_prop(2.5), 33.0, 0.3)
    P(sfx, hero.sfx_ding(), 33.2, 0.2)
    P(sfx, sfx_steps(1.0, 6), 35.6, 0.4)
    P(mus, fade_cut(music_heist(8.0)), 19.0, 0.5)
    P(mus, fade_cut(music_heist(9.8)), 28.2, 0.55)

    # 38–45 秒：门禁前一秒
    P(sfx, sfx_beeps(4.2), 38.0, 0.45)
    P(sfx, sfx_heart(4.5), 38.0, 0.6)
    P(sfx, hero.sfx_whoosh(0.5), 39.2, 0.4)
    P(sfx, sfx_swell(1.0), 40.0, 0.4)
    P(sfx, sfx_thud(), 41.5, 0.6)
    for k in range(4):
        P(sfx, sfx_click(), 43.15 + k * 0.03, 0.5)
    P(sfx, sfx_fanfare(), 43.6, 0.6)

    # 45–60 秒
    P(sfx, sfx_slurp(), 45.25, 0.4)
    P(sfx, sfx_slap(), 47.75, 0.6)
    P(mus, fade_cut(music_playful(3.2)), 46.8, 0.4)
    P(sfx, sfx_dong(), 49.7, 0.5)
    P(sfx, hero.sfx_crow(), 50.05, 0.5)
    for k in range(4):
        P(sfx, sfx_coin(), 53.05 + k * 0.12, 0.35)
    P(mus, fade_cut(music_playful(2.6)), 52.95, 0.35)
    P(sfx, sfx_coin(), 55.45, 0.4)
    P(sfx, sfx_dong(), 55.6, 0.8)
    P(mus, fade_cut(pad([261.63, 329.63, 392.0, 523.25], 2.6, 1.4, 0.4, 1.0)), 57.4, 0.35)

    # 台词出现时，配乐压低
    duck = np.ones(n)
    for ln in LINES:
        a = int(ln['start'] * SR)
        b = a + len(voices[ln['key']][0])
        duck[a:b] = 0.45
    duck = np.convolve(duck, np.ones(int(SR * 0.08)) / int(SR * 0.08), mode='same')
    mixed = vox + sfx + mus * duck
    peak = np.abs(mixed).max()
    if peak > 0.92:
        mixed *= 0.92 / peak
    pcm = (np.clip(mixed, -1, 1) * 32767).astype(np.int16)
    with wave.open(out_path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.repeat(pcm[:, None], 2, axis=1).tobytes())
    return out_path
