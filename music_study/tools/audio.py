"""Synthesize all SFX (no music) and mix them on the 128 BPM grid -> build/sfx.wav (48 kHz stereo).
music_study: the same effects as bedtime_words, a new cue list, and a faint "headphone leak" (hi-hats + a muffled
kick, no melody, no voice) from 0 to 2.11 s only (user, 2026-10-29: 耳机漏音「行」)."""
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
BEAT = 60 / 128
DUR = 75.0
rng = np.random.default_rng(128)


def T(d):
    return np.arange(int(d * SR)) / SR


def norm(x):
    m = np.max(np.abs(x))
    return x / m if m > 0 else x


def fft_band(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def sweep_phase(f):
    return 2 * np.pi * np.cumsum(f) / SR


def env_ar(n, a, r):
    t = np.arange(n) / SR
    return (1 - np.exp(-t / max(a, 1e-4))) * np.exp(-t / r)


# ---------------- SFX ----------------
def tick(f=2600, tock=False):
    t = T(0.05)
    f = f * (0.72 if tock else 1)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.007)
    n = fft_band(rng.standard_normal(len(t)), lo=2500) * np.exp(-t / 0.002)
    return norm(y + 0.6 * n)


def type_click():
    t = T(0.02)
    return norm(fft_band(rng.standard_normal(len(t)), lo=3000) * np.exp(-t / 0.0015) + 0.4 * np.sin(2 * np.pi * 4200 * t) * np.exp(-t / 0.003))


def pop(f0=380, f1=1150, d=0.11):
    t = T(d)
    f = f0 * (f1 / f0) ** np.clip(t / 0.035, 0, 1)
    return norm(np.sin(sweep_phase(f)) * env_ar(len(t), 0.002, 0.035))


def bonk():
    t = T(0.16)
    f = 420 * (180 / 420) ** np.clip(t / 0.08, 0, 1)
    return norm(np.sin(sweep_phase(f)) * env_ar(len(t), 0.002, 0.05))


def bell(f=1568, d=1.7, bright=1.0):
    t = T(d)
    parts = [(1, 1.0, 1.1), (2.0, 0.45 * bright, 0.6), (2.76, 0.32 * bright, 0.42), (5.4, 0.14 * bright, 0.22), (8.93, 0.07 * bright, 0.12)]
    y = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / dd) for r, a, dd in parts)
    y *= 1 - np.exp(-t / 0.0015)
    strike = fft_band(rng.standard_normal(len(t)), lo=3000) * np.exp(-t / 0.003) * 0.4
    return norm(y + strike)


def chime(f=1318.5):
    a, b = bell(f, 1.4), bell(f * 1.5, 1.6)
    out = np.zeros(len(b) + int(0.09 * SR))
    out[: len(a)] += a
    out[int(0.09 * SR): int(0.09 * SR) + len(b)] += b
    return norm(out)


def whoosh(d=0.42, up=True, bright=1.0):
    t = T(d)
    n = rng.standard_normal(len(t))
    lp, hp = fft_band(n, lo=200, hi=1200), fft_band(n, lo=1800, hi=9000 * bright)
    w = np.clip(t / d, 0, 1)
    if not up:
        w = 1 - w
    y = lp * (1 - w) + hp * w * 0.8
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.6
    return norm(y * env)


def riser(d=0.4):
    t = T(d)
    f = 240 * (820 / 240) ** (t / d)
    ph = sweep_phase(f)
    y = sum(np.sin(k * ph) / k for k in (1, 2, 3, 4))
    env = np.clip(t / d, 0, 1) ** 1.5 * np.exp(-np.maximum(0, t - d * 0.85) / 0.02)
    return norm(y * env + 0.25 * whoosh(d, True) * env)


def drop(d=0.5):
    t = T(d)
    f = 760 * (165 / 760) ** (t / d) * (1 + 0.03 * np.sin(2 * np.pi * 9 * t))
    ph = sweep_phase(f)
    y = np.sin(ph) + 0.3 * np.sin(2 * ph)
    return norm(y * env_ar(len(t), 0.004, 0.22))


def page_flip(d=0.16):
    t = T(d)
    n = fft_band(rng.standard_normal(len(t)), lo=1400, hi=7500)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 * (0.7 + 0.3 * np.sin(2 * np.pi * 34 * t))
    return norm(n * env)


def thump(f0=130, f1=55, d=0.25):
    t = T(d)
    f = f0 * (f1 / f0) ** np.clip(t / 0.12, 0, 1)
    y = np.sin(sweep_phase(f)) * env_ar(len(t), 0.002, 0.09)
    c = fft_band(rng.standard_normal(len(t)), hi=2500) * np.exp(-t / 0.006) * 0.5
    return norm(y + c)


def boing(d=0.32):
    t = T(d)
    f = (320 + 380 * (1 - np.exp(-t / 0.05))) * (1 + 0.08 * np.sin(2 * np.pi * 14 * t) * np.exp(-t / 0.12))
    return norm(np.sin(sweep_phase(f)) * env_ar(len(t), 0.003, 0.11))


def stretch(d=0.62):
    t = T(d)
    f = 210 * (520 / 210) ** (t / d) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))
    ph = sweep_phase(f)
    y = np.sin(ph) + np.sin(3 * ph) / 9 + np.sin(5 * ph) / 25
    env = np.sin(np.pi * t / d) ** 1.2
    air = fft_band(rng.standard_normal(len(t)), lo=300, hi=2500) * env * 0.25
    return norm(y * env * 0.8 + air)


def alarm(d=2.6):
    t = T(d)
    car = np.sin(2 * np.pi * 2350 * t) + 0.6 * np.sin(2 * np.pi * 3170 * t) + 0.3 * np.sin(2 * np.pi * 4710 * t)
    strikes = (np.sin(2 * np.pi * 23 * t) > 0).astype(float)
    strikes = fft_band(strikes, hi=400)
    env = (1 - np.exp(-t / 0.01)) * np.clip((d - t) / 0.06, 0, 1)
    return norm(car * (0.35 + 0.65 * strikes) * env)


def sparkle(d=0.6, n=9):
    out = np.zeros(int(d * SR))
    for _ in range(n):
        f = rng.uniform(2800, 7200)
        st = int(rng.uniform(0, d * 0.6) * SR)
        t = T(0.16)
        s = np.sin(2 * np.pi * f * t) * env_ar(len(t), 0.001, 0.04)
        out[st: st + len(s)] += s[: len(out) - st]
    return norm(out)


def blip(f=1500):
    t = T(0.12)
    a = np.sin(2 * np.pi * f * t) * env_ar(len(t), 0.001, 0.018)
    b = np.zeros_like(a)
    k = int(0.05 * SR)
    b[k:] = (np.sin(2 * np.pi * f * 1.5 * t) * env_ar(len(t), 0.001, 0.02))[: len(t) - k]
    return norm(a + b)


def zz_puff(d=0.7):
    t = T(d)
    n = fft_band(rng.standard_normal(len(t)), lo=120, hi=900)
    env = np.sin(np.pi * t / d) ** 2
    return norm(n * env)


def scribble(d=0.55):
    t = T(d)
    n = fft_band(rng.standard_normal(len(t)), lo=1500, hi=4500)
    env = np.abs(np.sin(2 * np.pi * 7 * t)) ** 2 * np.sin(np.pi * t / d)
    return norm(n * env)


def warn_thud():
    t = T(0.45)
    y = (np.sin(2 * np.pi * 72 * t) + 0.5 * np.sin(2 * np.pi * 144 * t)) * env_ar(len(t), 0.003, 0.16)
    buzz = np.sign(np.sin(2 * np.pi * 110 * t)) * env_ar(len(t), 0.003, 0.07) * 0.18
    return norm(y + fft_band(buzz, hi=1600))


def shutter():
    """Camera shutter: two short filtered clicks."""
    out = np.zeros(int(0.2 * SR))
    for st, lvl in ((0, 1.0), (int(0.07 * SR), 0.7)):
        t = T(0.05)
        c = fft_band(rng.standard_normal(len(t)), lo=900, hi=7000) * np.exp(-t / 0.008) * lvl
        out[st: st + len(c)] += c
    return norm(out)


def whirr(d=1.4, n=16):
    """Accelerating then decelerating ticks (timer / clock spinning)."""
    out = np.zeros(int(d * SR) + SR // 10)
    u = np.linspace(0, 1, n)
    times = d * (0.5 - 0.5 * np.cos(np.pi * u))
    tk = tick(3000)
    for i, tt in enumerate(times):
        st = int(tt * SR)
        out[st: st + len(tk)] += tk * (0.55 + 0.45 * np.sin(np.pi * i / (n - 1)))
    return norm(out)


def hit(d=0.7):
    """Punchy hit for frame 0 (same recipe as engine/sfx.py on the if-then-plan branch).
    Own RNG, so every other effect keeps exactly the same noise."""
    r = np.random.default_rng(7)
    t = T(d)

    def env(att, tau):
        return np.clip(t / att, 0, 1) * np.exp(-np.maximum(0.0, t - att) / tau)

    y = np.sin(sweep_phase(48 + 120 * np.exp(-t / 0.035))) * env(0.001, 0.22)
    y += 0.55 * fft_band(r.standard_normal(len(t)), lo=1200, hi=9000) * env(0.0004, 0.018)
    y += 0.45 * fft_band(r.standard_normal(len(t)), lo=120, hi=900) * env(0.001, 0.07)
    return norm(y)


# ---------------- loudness (ITU-R BS.1770-4) ----------------
TARGET_LUFS = -18.4  # same integrated loudness as the previous episode (if_then_plan)


def _k_weight(x):
    """K-weighting at 48 kHz, applied in the frequency domain (loudness only needs the power)."""
    z = np.exp(-1j * 2 * np.pi * np.fft.rfftfreq(len(x), 1 / SR) / SR)

    def bq(b, a):
        return (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)

    h = bq((1.53512485958697, -2.69169618940638, 1.19839281085285), (1.0, -1.69065929318241, 0.73248077421585))
    h = h * bq((1.0, -2.0, 1.0), (1.0, -1.99004745483398, 0.99007225036621))
    return np.fft.irfft(np.fft.rfft(x) * h, len(x))


def lufs(L, R):
    """Integrated loudness: 400 ms blocks, 75 % overlap, absolute gate -70 LUFS, relative gate -10 LU."""
    p = _k_weight(L) ** 2 + _k_weight(R) ** 2
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    cs = np.concatenate([[0.0], np.cumsum(p)])
    st = np.arange(0, len(p) - blk + 1, hop)
    ms = (cs[st + blk] - cs[st]) / blk
    lk = -0.691 + 10 * np.log10(np.maximum(ms, 1e-15))
    rel = -0.691 + 10 * np.log10(ms[lk > -70].mean()) - 10
    return -0.691 + 10 * np.log10(ms[(lk > -70) & (lk > rel)].mean())


def spin(d=0.9, n=22):
    out = np.zeros(int(d * SR) + SR // 10)
    times = d * np.linspace(0, 1, n) ** 1.3
    tk = tick(3300)
    for tt in times:
        st = int(tt * SR)
        out[st: st + len(tk)] += tk
    return norm(out)


def chirp(n=2):
    """A bird outside the morning window: quick rising sine sweeps."""
    out = np.zeros(int(0.34 * SR))
    for k in range(n):
        t = T(0.07)
        s = np.sin(sweep_phase(2900 + 1500 * (t / 0.07) ** 0.7)) * np.sin(np.pi * t / 0.07) ** 2
        st = int(k * 0.11 * SR)
        out[st: st + len(s)] += s
    return norm(out)


def bubble(f0=300, f1=720, d=0.13):
    """A lyric bubble leaving his ear cup: a soft rising bloop."""
    t = T(d)
    f = f0 + (f1 - f0) * (1 - np.exp(-t / 0.02))
    return norm(np.sin(sweep_phase(f)) * env_ar(len(t), 0.004, 0.035))


def stamp():
    """The 「正确率其实差不多」 stamp: a low thud plus a short slap."""
    t = T(0.3)
    y = np.sin(sweep_phase(160 * (60 / 160) ** np.clip(t / 0.08, 0, 1))) * env_ar(len(t), 0.002, 0.08)
    slap = fft_band(rng.standard_normal(len(t)), lo=500, hi=5000) * np.exp(-t / 0.01)
    return norm(y + 0.8 * slap)


def tick_run(n=5, d=0.75, f0=2600, f1=1500):
    """A knob or slider moving: n ticks over d beats, pitch from f0 to f1."""
    out = np.zeros(int(d * BEAT * SR) + SR // 10)
    for k in range(n):
        tk = tick(f0 + (f1 - f0) * k / max(1, n - 1))
        st = int(k * d / max(1, n - 1) * BEAT * SR)
        out[st: st + len(tk)] += tk
    return norm(out)


def leak(beats=4.5):
    """Music leaking from the boy's headphones in the hook (0-2.11 s): closed hi-hats on every half beat (the offbeats
    louder), a muffled kick on every beat, band-limited like sound escaping from ear cups. No melody, no voice.
    It stops dead on beat 4.5 (reveal 1), when the music is switched off for the dictation."""
    r = np.random.default_rng(11)
    n = int(round(beats * BEAT * SR))
    out = np.zeros(n + SR // 4)
    th = T(0.08)
    hat = fft_band(r.standard_normal(len(th)), lo=6500, hi=12000) * np.exp(-th / 0.012)
    tk = T(0.16)
    kick = np.sin(sweep_phase(120 * (60 / 120) ** np.clip(tk / 0.05, 0, 1))) * env_ar(len(tk), 0.002, 0.05)
    kick += 0.5 * fft_band(r.standard_normal(len(tk)), lo=800, hi=3000) * np.exp(-tk / 0.004)
    for k in range(int(beats * 2)):
        st = int(round(k * 0.5 * BEAT * SR))
        out[st: st + len(hat)] += hat * (1.0 if k % 2 else 0.55)
        if k % 2 == 0:
            out[st: st + len(kick)] += kick * 0.8
    out = fft_band(out, lo=120, hi=9000)[:n]
    m = int(0.006 * SR)
    out[-m:] *= np.linspace(1, 0, m)
    return norm(out)


# ---------------- cue sheet (beat, sound, gain dB, pan -1..1) ----------------
HIT_DB = -1.5   # frame-0 hit (the leak's first kick lands on it too)
BED_DB = 8.0    # boost for the 0-2 s pages and typing (bedtime_words used 15; here the leak fills the hook)
LEAK_LU = -20.0  # the headphone leak sits about 20 LU below the integrated loudness of the whole mix
LEAK_PAN = 0.45  # it comes from the boy (right half of the frame)
DRIVE = 1.8      # soft clip after peak normalisation (bedtime_words: 1.3; this mix is sparser, 1.8 keeps the true peak under -1 dBTP)


def cues():
    """One effect per visual event, on its beat (src/scene.js, src/sections.js). Hers on the left, his on the right."""
    c = []
    add = lambda b, s, g, p=0.0: c.append((b, s, g, p))
    # ---- hook: hit on frame 0; words land in their heads (hers on the half beats, his on the beats), lyric bubbles
    # leave his ear cup on the half beats, one knocks his word away (2.5); typing of the English line; page turns
    add(0, hit(), HIT_DB, 0.0)
    for k, b in enumerate((0.5, 1.5, 2.5, 3.5)):
        add(b, pop(300 + 45 * k, 900 + 110 * k, 0.09), -16, -0.5)
    for k, b in enumerate((1.0, 2.0, 4.0)):
        add(b, pop(330 + 50 * k, 980 + 120 * k, 0.09), -16, 0.5)
    for b in (-0.5 + 1, 1.5, 2.5, 3.5):
        add(b, bubble(), -21 + 6, 0.35)
    add(2.5, bonk(), -13, 0.6)
    for b in (0.5, 2.5):
        add(b, page_flip(), -18 + BED_DB, 0.0)
    for i in range(16):
        add(i * 0.1625, type_click(), -34 + BED_DB, 0.0)
    # reveal 1 (4.5): 默写 — the music stops, bubbles pop, the two sheets drop, both write; counts complete on 5.5 / 6.0
    add(4.5, whoosh(0.38), -13, 0.0)
    add(4.5, blip(1700), -17, 0.5)
    add(4.5, pop(520, 1500, 0.07), -22, 0.4)
    add(4.5, page_flip(0.2), -18, 0.0)
    add(5.0, scribble(0.25), -21, -0.5)
    add(5.0, scribble(0.47), -21, 0.5)
    add(5.5, pop(380, 1100), -14, -0.5)
    add(6.0, pop(360, 1000), -14, 0.5)
    add(6.5, bonk(), -16, 0.5)            # 少记 1 个
    # reveal 2 (8.5): he switches to instrumental music; his sheet turns over and fills to 7.9; the check at 10.5
    add(8.5, whoosh(0.42, bright=1.2), -12, 0.0)
    add(8.5, blip(1900), -16, 0.5)        # finger on the phone
    add(8.5, sparkle(0.5, 6), -24, 0.5)   # notes start
    add(8.5, page_flip(0.2), -17, 0.5)
    add(9.0, scribble(0.47), -21, 0.5)
    add(10.0, pop(400, 1150), -14, 0.5)
    add(10.5, bell(1568), -8, 0.0)
    add(10.55, sparkle(), -21, 0.0)
    add(11.5, bonk(), -17, 0.7)           # 带词的歌：少记 1 个
    add(13.0, blip(1200), -22, -0.4)
    add(15.5, whoosh(0.5, up=False), -17, -0.6)
    # ---- 关掉歌词: the answer; he turns the volume down; the playlist; 65 studies
    add(16.5, whoosh(0.28), -18, 0.0)
    for i in range(12):
        add(17.0 + i * 0.22, type_click(), -33, 0.0)
    add(18.0, blip(1900), -18, 0.3)
    add(18.5, tick_run(3, 0.5, 2400, 1400), -22, 0.3)
    add(19.0, pop(360, 1050), -12, 0.3)
    add(21.5, pop(420, 1250), -12, 0.4)
    add(25.0, pop(480, 1450), -12, 0.4)
    for b in (20.5, 22.5, 24.5, 28.5):
        add(b, page_flip(), -24, 0.0)
    for k in range(4):
        add(26.5 + k * 0.5, pop(400 + 40 * k, 1150 + 100 * k, 0.08), -18, -0.6)
    add(28.5, warn_thud(), -16, -0.6)
    add(29.2, sparkle(0.5, 6), -24, 0.4)
    add(30.5, whoosh(0.5), -15, 0.0)
    # ---- ① 别听带词的歌
    add(31.8, blip(1800), -20, 0.0)
    add(32.0, whoosh(0.25), -20, 0.0)
    for i in range(10):
        add(32.5 + i * 0.24, type_click(), -34, -0.3)
    add(33.5, pop(380, 1100), -15, 0.3)
    for k in range(6):
        add(34.0 + k * 0.5, tick(2300 + 60 * k), -19, 0.2)     # 床前明月光，
    for k in range(4):
        add(37.0 + k * 0.5, tick(2300 + 60 * k), -19, 0.2)     # 疑是地上
    add(38.0, bubble(), -15, -0.3)
    add(39.5, pop(520, 1500, 0.07), -18, 0.3)
    add(39.5, bonk(), -12, 0.3)               # ……啦啦？
    add(40.0, blip(1300), -22, 0.0)
    add(43.0, whoosh(0.4, up=False), -18, 0.3)
    add(44.0, blip(1900), -18, -0.4)          # he picks his favourite song
    for k, b in enumerate((44, 45, 46)):
        add(b, pop(380 + 50 * k, 1100 + 130 * k), -13, -0.3 + 0.3 * k)
    add(48.0, bell(1318.5, 1.6), -10, -0.3)   # 安静 ✓
    add(48.5, blip(1000), -18, 0.3)           # =
    add(49.0, bonk(), -17, 0.3)
    add(55.5, whoosh(0.4, up=False), -18, 0.0)
    add(56.0, pop(400, 1150), -15, -0.3)
    add(56.5, pop(440, 1250), -15, 0.4)
    add(57.5, bonk(), -16, -0.3)
    add(58.0, bonk(), -16, 0.4)
    add(59.5, whoosh(0.35, up=False), -19, 0.0)
    add(60.0, whoosh(0.5, up=False, bright=0.6), -15, -0.4)   # headphones come off
    add(60.5, pop(520, 1500, 0.07), -18, 0.3)
    add(61.0, blip(1100), -20, 0.3)
    add(61.0, thump(170, 80, 0.18), -18, -0.4)
    add(62.5, whoosh(0.6), -14, 0.0)
    # ---- ② 想听就换纯音乐
    add(63.8, blip(1800), -20, 0.0)
    add(64.0, whoosh(0.25), -20, 0.0)
    for i in range(10):
        add(64.5 + i * 0.24, type_click(), -34, -0.3)
    add(65.0, whoosh(0.4, up=True, bright=0.6), -17, -0.4)    # headphones on
    add(65.8, thump(190, 90, 0.15), -20, -0.4)
    add(66.0, sparkle(0.5, 6), -23, -0.3)
    for k in range(3):
        add(66 + k * 0.5, pop(380 + 50 * k, 1100 + 120 * k, 0.09), -15, -0.2 + 0.3 * k)
    add(69.5, whoosh(0.4, up=False), -18, 0.0)
    add(70.0, blip(1300), -21, 0.0)
    add(70.0, pop(380, 1100), -16, 0.0)
    add(70.5, tick_run(4, 0.75, 2000, 1500), -20, -0.1)
    add(71.0, tick_run(5, 0.75, 2000, 2800), -20, 0.2)
    add(72.0, blip(1600), -21, 0.2)
    add(73.0, stamp(), -9, 0.0)
    add(76.0, whoosh(0.4, up=False), -17, 0.0)
    add(77.0, pop(380, 1100), -16, 0.0)
    for k in range(4):
        add(77.5 + k * 0.5, blip(1000 + 150 * k), -24, 0.3)
    add(80.0, blip(1900), -19, -0.4)
    for k, b in enumerate((80, 81, 82)):
        add(b, pop(420 + 50 * k, 1250 + 120 * k), -13, 0.3)
    add(84.5, riser(0.7), -17, 0.3)
    add(86.0, warn_thud(), -10, 0.3)          # 快 · 大声 ✗
    add(86.05, bonk(), -16, 0.3)
    add(86.5, blip(1300), -22, 0.0)
    add(87.5, whoosh(0.35, up=False), -19, 0.0)
    add(88.0, pop(380, 1100), -16, 0.0)
    add(88.5, tick_run(5, 1.0, 2400, 1200), -19, 0.2)   # the volume goes down
    add(90.0, blip(1200), -22, 0.0)
    add(95.0, whoosh(0.55, up=False), -15, -0.3)
    # ---- ③ 算题影响不明显
    add(95.8, blip(1800), -20, 0.0)
    add(96.0, whoosh(0.25), -20, 0.0)
    for i in range(10):
        add(96.5 + i * 0.24, type_click(), -34, -0.3)
    add(97.0, pop(380, 1100), -15, 0.3)
    for k, b in enumerate((98, 100, 102)):
        add(b, pop(420 + 40 * k, 1200 + 100 * k, 0.09), -15, 0.3)
        add(b + 0.5, scribble(0.3), -20, -0.4)
        add(b + 1, blip(1500 + 150 * k), -19, 0.4)
    add(104.0, pop(380, 1100), -16, 0.3)
    for k in range(3):
        add(104.5 + k * 0.5, blip(1700 + 200 * k), -18, 0.3)
    add(106.5, bell(1318.5, 1.2), -12, 0.5)
    add(108.5, whoosh(0.35, up=False), -19, 0.0)
    add(109.0, blip(1300), -21, 0.0)
    add(109.5, pop(400, 1150, 0.08), -18, 0.3)
    for b in (110, 111, 112):
        add(b, page_flip(0.12), -19, 0.3)
        add(b, bonk(), -16, 0.3)
    add(113.0, page_flip(0.12), -19, 0.5)
    add(113.0, chime(1318.5), -14, 0.5)
    add(114.0, blip(1200), -22, 0.0)
    add(119.5, whoosh(0.35, up=False), -19, 0.0)
    add(120.0, pop(380, 1100), -15, 0.3)
    add(120.0, whoosh(0.5, up=False, bright=0.6), -15, -0.4)  # headphones off
    add(121.0, thump(170, 80, 0.18), -18, -0.4)
    add(126.0, whoosh(0.6), -14, 0.2)
    # ---- 照着做: the mixer is set channel by channel while he acts each row
    add(127.0, whoosh(0.25), -20, 0.0)
    for i in range(8):
        add(127.5 + i * 0.24, type_click(), -34, -0.3)
    add(130.0, whoosh(0.22, up=False, bright=0.5), -17, 0.0)  # fader 1 all the way down
    add(130.0, pop(380, 1100), -13, -0.1)
    add(130.4, page_flip(), -19, -0.5)
    add(130.8, thump(200, 90, 0.12), -17, -0.1)
    add(134.0, whoosh(0.22, up=False, bright=0.5), -17, 0.2)  # fader 2 down a little
    add(134.0, pop(420, 1200), -13, 0.2)
    add(134.1, whoosh(0.4, up=True, bright=0.6), -19, -0.5)   # headphones on
    add(134.6, sparkle(0.5, 6), -24, -0.5)
    add(138.0, pop(460, 1300), -13, 0.5)
    add(138.1, bell(2093, 0.9), -16, 0.5)                     # green light
    add(138.5, scribble(0.5), -22, -0.5)
    add(142.0, warn_thud(), -10, 0.0)
    add(142.3, whoosh(0.18), -26, -0.5)
    add(143.2, whoosh(0.18), -26, -0.5)
    add(144.0, blip(1100), -21, 0.2)
    add(146.0, shutter(), -13, 0.2)
    add(150.0, whoosh(0.2), -22, -0.3)   # he points at the mixer
    add(153.8, pop(520, 1500), -16, -0.4)  # thumbs-up
    return c


def bus(cue_list, n):
    L = np.zeros(n + SR * 3)
    R = np.zeros(n + SR * 3)
    for b, s, g, p in cue_list:
        st = int(round(b * BEAT * SR))
        amp = 10 ** (g / 20)
        a = (p + 1) * np.pi / 4
        L[st: st + len(s)] += s * amp * np.cos(a)
        R[st: st + len(s)] += s * amp * np.sin(a)
    return L[:n], R[:n]


def process(L, R):
    """End fade, soft clip (tanh) after peak normalisation, then level to TARGET_LUFS. Returns the signal and the
    small-signal gain of the chain (to measure quiet parts such as the leak on the same scale)."""
    n = len(L)
    fade = np.ones(n)
    k = int(0.3 * SR)
    fade[-k:] = np.linspace(1, 0, k)
    L, R = L * fade, R * fade
    peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
    drive = DRIVE
    L, R = np.tanh(drive * L / peak) / np.tanh(drive), np.tanh(drive * R / peak) / np.tanh(drive)
    gain = 10 ** ((TARGET_LUFS - lufs(L, R)) / 20)
    return L * gain, R * gain, gain * drive / (peak * np.tanh(drive))


def mix(out_path):
    n = int(DUR * SR)
    cl = cues()
    L0, R0 = bus(cl, n)
    lk = leak()
    a = (LEAK_PAN + 1) * np.pi / 4
    lead = np.zeros(n)
    lead[: len(lk)] = lk
    # set the leak so that, after the same gain chain, it sits LEAK_LU below the final integrated loudness
    level = 10 ** (-30 / 20)
    for _ in range(3):
        L, R, g = process(L0 + lead * level * np.cos(a), R0 + lead * level * np.sin(a))
        leak_lufs = lufs(lead * level * np.cos(a) * g, lead * level * np.sin(a) * g)
        level *= 10 ** ((TARGET_LUFS + LEAK_LU - leak_lufs) / 20)
    L, R, g = process(L0 + lead * level * np.cos(a), R0 + lead * level * np.sin(a))
    leak_lufs = lufs(lead * level * np.cos(a) * g, lead * level * np.sin(a) * g)
    pk = max(np.max(np.abs(L)), np.max(np.abs(R)))
    if pk > 10 ** (-1.5 / 20):
        raise SystemExit(f'sample peak {20 * np.log10(pk):.2f} dBFS > -1.5 dBFS at {TARGET_LUFS} LUFS: lower HIT_DB')
    pcm = (np.stack([L, R], axis=1) * 32767).astype(np.int16)
    with wave.open(str(out_path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    total = lufs(L, R)
    print(f'wrote {out_path}: {n / SR:.3f} s, {len(cl)} cues + headphone leak 0-{len(lk) / SR:.3f} s, '
          f'{total:.1f} LUFS, sample peak {20 * np.log10(pk):.1f} dBFS, leak {leak_lufs:.1f} LUFS ({leak_lufs - total:+.1f} LU)')


if __name__ == '__main__':
    out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'build/sfx.wav')
    out.parent.mkdir(parents=True, exist_ok=True)
    mix(out)
