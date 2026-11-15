"""Synthesize all SFX (no music) and mix them on the 128 BPM grid -> build/sfx.wav (48 kHz stereo).
Copied from bedtime_words/tools/audio.py; nap_length adds the water sounds and its own cue sheet."""
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


# ---------------- water sounds (nap_length) ----------------
def blub(f0=420, f1=1300, d=0.07):
    """One air bubble: a quick upward sine glide."""
    t = T(d)
    f = f0 * (f1 / f0) ** np.clip(t / (d * 0.7), 0, 1)
    return norm(np.sin(sweep_phase(f)) * env_ar(len(t), 0.002, d * 0.35))


def bubbles(d=0.9, n=7, lo=380, hi=900):
    """A short run of bubbles (the mattress sinking)."""
    out = np.zeros(int(d * SR) + SR // 10)
    for k in range(n):
        st = int(d * k / n * SR + (rng.uniform(0, 0.03) * SR if k else 0))   # the first one on the beat
        f0 = rng.uniform(lo, hi)
        b = blub(f0, f0 * rng.uniform(2.2, 3.0), rng.uniform(0.05, 0.08)) * rng.uniform(0.5, 1.0)
        out[st: st + len(b)] += b[: len(out) - st]
    return norm(out)


def splash(d=1.0, big=1.0):
    """Body into water: an impact thud, broadband spray, a hiss tail and a few droplets."""
    t = T(d)
    body = fft_band(rng.standard_normal(len(t)), lo=300, hi=7000) * env_ar(len(t), 0.003, 0.11 * big)
    tail = fft_band(rng.standard_normal(len(t)), lo=1500, hi=9000) * env_ar(len(t), 0.02, 0.26 * big) * 0.45
    thud = np.sin(sweep_phase(170 * (60 / 170) ** np.clip(t / 0.1, 0, 1))) * env_ar(len(t), 0.002, 0.07) * 0.9 * big
    out = body + tail + thud
    for _ in range(int(3 + 5 * big)):
        st = int(rng.uniform(0.08, d * 0.7) * SR)
        f0 = rng.uniform(700, 1300)
        dr = blub(f0, f0 * 2.1, 0.05) * rng.uniform(0.12, 0.3)
        out[st: st + len(dr)] += dr[: len(out) - st]
    return norm(out)


def swish(d=0.7):
    """A curtain pulled along its rod: rising filtered noise + the rings ticking."""
    t = T(d)
    n = rng.standard_normal(len(t))
    w = np.clip(t / d, 0, 1)
    y = (fft_band(n, lo=400, hi=2500) * (1 - w) + fft_band(n, lo=2500, hi=8000) * w * 0.7) * np.sin(np.pi * w) ** 1.2
    for k in range(4):
        st = int((0.06 + k * 0.12) * SR)
        tk = tick(3400 - k * 220) * 0.22
        y[st: st + len(tk)] += tk[: len(y) - st]
    return norm(y)


def buzz(d=1.5):
    """Phone on vibrate: a low buzz gated on and off."""
    t = T(d)
    car = fft_band(np.sign(np.sin(2 * np.pi * 170 * t)) * 0.6 + np.sin(2 * np.pi * 340 * t) * 0.4, hi=2200)
    gate = fft_band(((t % 0.31) < 0.21).astype(float), hi=60)
    env = (1 - np.exp(-t / 0.005)) * np.clip((d - t) / 0.05, 0, 1)
    return norm(car * gate * env)


def slosh(d=0.8):
    """Water moving around the mattress."""
    t = T(d)
    n = fft_band(rng.standard_normal(len(t)), lo=90, hi=1200)
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5 * (0.7 + 0.3 * np.sin(2 * np.pi * 5 * t))
    return norm(n * env)


def footstep():
    t = T(0.12)
    y = np.sin(sweep_phase(110 * (60 / 110) ** np.clip(t / 0.05, 0, 1))) * env_ar(len(t), 0.002, 0.03)
    sc = fft_band(rng.standard_normal(len(t)), lo=800, hi=4000) * env_ar(len(t), 0.004, 0.02) * 0.3
    return norm(y + sc)


def wobble(d=0.9):
    """Groggy: the "?" circling over his head, a slow vibrato glide down."""
    t = T(d)
    f = 620 + 140 * np.sin(2 * np.pi * 3.2 * t) - 160 * t / d
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.3
    ph = sweep_phase(f)
    return norm((np.sin(ph) + 0.3 * np.sin(2 * ph)) * e)


# ---------------- cue sheet (beat, sound, gain dB, pan -1..1) ----------------
HIT_DB = 0.0    # frame-0 hit
BED_DB = 12.0   # boost for the 0-2 s water sounds, so they are heard on a phone
DRIVE = 1.8     # soft clip before levelling (bedtime_words 1.3; this mix is sparser, its peaks needed more)


def cues():
    """One effect per visual event, on its beat (src/scene.js, src/sections.js).
    Pans: the mattress / pool on the left (-), the deck, boards and props on the right (+)."""
    c = []
    add = lambda b, s, g, p=0.0: c.append((b, s, g, p))
    # a whoosh peaks in its middle: start it half its length before the cut
    peak = lambda b, d: b - (d / 2) / BEAT

    # ---- opening: frame-0 hit, he sinks on the mattress (bubbles on every half beat), the marks light up
    add(0, hit(), HIT_DB, 0.0)
    add(0, slosh(1.2), -20 + BED_DB, -0.4)
    for k, b in enumerate((0.5, 1.0, 2.0, 2.5, 3.0, 3.5)):
        add(b, bubbles(0.3, 3, 380 + 30 * k, 700 + 40 * k), -24 + BED_DB, -0.35)
    add(1.5, pop(320, 980, 0.1), -14, -0.6)          # 10 分钟 mark + its board light up
    add(1.5, blip(1200), -22, 0.6)
    add(4.0, pop(300, 900, 0.12), -13, -0.6)         # 30 分钟 mark + its board
    add(4.0, blip(950), -22, 0.6)
    # reveal 1 (4.5): 醒来 5 分钟 — the three numbers roll in, the 30-minute one is the worst
    add(peak(4.5, 0.38), whoosh(0.38), -13, 0.3)
    for i, f0 in enumerate((420, 470, 380)):
        add(4.5 + i * 0.12, pop(f0, f0 * 2.8, 0.1), -15, 0.4 + i * 0.15)
    add(4.5, wobble(1.6), -22, -0.4)                 # the "?" start circling
    add(5.0, bonk(), -15, 0.75)                      # 比没睡还差
    for b in (5.5, 6.5, 7.5):
        add(b, bubbles(0.25, 2, 500, 900), -27, -0.4)  # rising slowly
    # reveal 2 (8.5): 醒来 35 分钟 — numbers roll again, he shakes his head
    add(peak(8.5, 0.42), whoosh(0.42, bright=1.2), -12, 0.3)
    for i in range(3):
        add(8.6 + i * 0.12, tick(2400 + 300 * i), -17, 0.4 + i * 0.15)
    add(8.5, whoosh(0.16), -24, -0.5)
    add(9.0, whoosh(0.16), -24, -0.5)
    add(10.5, bell(1568), -8, 0.5)                   # check on 睡 10 分钟
    add(10.55, sparkle(), -21, 0.5)
    add(11.5, pop(360, 900, 0.12), -18, 0.8)         # 缓过来了
    add(13.0, blip(1300), -24, 0.6)                  # source
    add(peak(15.5, 0.5), whoosh(0.5, up=False), -18, 0.5)
    # ---- 睡 10 分钟: the title flips to the answer, he stretches, the tags rise as bubbles, deep-sleep evidence
    add(peak(16.75, 0.4), whoosh(0.4), -15, 0.0)
    add(15.5, slosh(1.0), -24, -0.5)                 # the mattress drifts left
    for i in range(14):
        add(17.0 + i * 0.22, type_click(), -33, 0.0)
    add(18.0, stretch(), -16, -0.5)
    for k, b in enumerate((19.0, 21.5, 24.0)):
        add(b, blub(400 + 60 * k, 1300 + 120 * k, 0.08), -13, 0.2 + 0.2 * k)
        add(b + 0.02, pop(380 + 40 * k, 1100 + 100 * k), -16, 0.2 + 0.2 * k)
    add(26.5, pop(420, 1200), -14, -0.2)             # 睡 10 分钟：深睡不到 1 分钟
    add(27.5, pop(330, 950, 0.12), -14, -0.2)        # 睡 30 分钟：深睡约 11 分钟
    add(28.5, blip(1300), -24, -0.2)
    add(29.2, sparkle(0.5, 6), -24, 0.3)
    add(peak(30.5, 0.5), whoosh(0.5), -16, -0.2)
    # ---- ① 睡多久: lies down, the strip runs (falling asleep -> asleep 10 min), the phone buzzes, up at once
    add(peak(32.0, 0.25), whoosh(0.25), -20, 0.0)
    add(32.0, pop(380, 1100), -15, -0.7)             # header bubble
    for i in range(12):
        add(32.4 + i * 0.22, type_click(), -34, -0.3)
    add(33.0, slosh(0.8), -20, -0.4)                 # lies down
    add(34.0, pop(420, 1200), -15, 0.2)              # the strip appears
    for b in (35, 36, 37):
        add(b, tick(1900), -24, 0.0)                 # falling asleep
    add(38.0, chime(1046.5), -15, 0.0)               # 睡着
    add(38.0, zz_puff(), -24, -0.4)
    for b in (40, 42, 44):
        add(b, zz_puff(), -27, -0.4)
    for b in (39.0, 41.0, 43.0, 45.0):
        add(b, bubbles(0.25, 2, 450, 800), -28, -0.4)
    add(46.0, buzz(1.5), -12, 0.6)                   # 闹钟
    add(46.5, boing(), -14, -0.4)                    # up at once
    add(47.0, splash(0.6, 0.45), -15, -0.4)
    add(47.5, bell(1568, 1.2), -10, -0.4)            # check
    add(48.5, blip(1400), -21, 0.2)                  # note
    add(54.0, pop(400, 1150), -16, 0.5)              # Brooks: 7 tests
    add(54.0, whoosh(0.2), -24, -0.4)                # he points
    for k in range(5):
        add(54.5 + k * 0.5, pop(360 + 60 * k, 1000 + 160 * k, 0.09), -16, 0.5)
    add(57.0, chime(1318.5), -12, 0.5)               # 5 项
    add(57.5, blip(900), -22, 0.5)
    add(58.0, bonk(), -16, 0.5)                      # 0 项
    add(59.0, blip(1300), -24, 0.5)
    add(peak(63.0, 0.6), whoosh(0.6), -15, 0.0)
    # ---- ② 睡久了怎么办: sinks deep, wakes groggy, six surface bubbles pop (醒来 5 ... 30 分钟), the hard card
    add(peak(64.0, 0.25), whoosh(0.25), -20, 0.0)
    add(64.0, pop(380, 1100), -15, -0.7)
    for i in range(12):
        add(64.4 + i * 0.22, type_click(), -34, -0.3)
    add(65.0, slosh(0.8), -20, -0.3)
    add(66.0, drop(0.6), -14, -0.3)                  # down it goes
    for k in range(12):
        add(66.5 + k * 0.5, bubbles(0.25, 2, 420 - 15 * k, 820 - 25 * k), -25, -0.3)
    add(70.0, pop(330, 950, 0.12), -14, -0.8)        # the 30-60 zone lights up
    add(70.5, pop(380, 1100), -16, -0.8)
    add(72.5, wobble(1.8), -20, -0.3)                # awake but groggy
    for k in range(6):
        add(72.5 + 0.5 * k, blub(380 + 40 * k, 1100 + 90 * k, 0.08), -19, 0.05 * k)  # six bubbles rise to the surface
    for k in range(6):
        add(76 + 2 * k, blub(700 + 80 * k, 2200 + 180 * k, 0.05), -12, 0.1 + 0.08 * k)  # pop: +5 minutes
        add(76 + 2 * k, tick(2600), -24, 0.1 + 0.08 * k)
    add(76.0, pop(400, 1150), -18, 0.6)              # deck text
    add(78.0, blip(1300), -24, 0.6)
    add(86.0, chime(1318.5), -11, 0.5)               # 30 分钟内缓过来
    add(87.0, whoosh(0.16), -24, -0.3)
    add(87.45, whoosh(0.16), -24, -0.3)
    add(88.0, bell(1568), -9, 0.2)                   # 缓过来了
    add(90.0, pop(420, 1200), -15, -0.3)             # 难题 card
    add(91.5, bell(2093, 0.9), -14, -0.3)
    add(95.0, slosh(1.0), -22, -0.2)                 # drifts to the deck
    add(peak(95.0, 0.55), whoosh(0.55, up=False), -16, -0.2)
    # ---- ③ 醒来先干嘛: onto the deck, 醒了！, slow digits, curtain, splash, easy ones first
    add(peak(96.0, 0.25), whoosh(0.25), -20, 0.0)
    add(96.0, pop(380, 1100), -15, -0.7)
    for i in range(12):
        add(96.4 + i * 0.22, type_click(), -34, -0.3)
    add(97.0, slosh(0.6), -23, 0.0)
    for b in (98, 99, 100):
        add(b, footstep(), -16, 0.1 + 0.05 * (b - 98))
    add(101.0, pop(520, 1500), -13, 0.2)             # 醒了！
    add(101.05, blip(1800), -19, 0.2)
    add(102.0, pop(380, 1100), -16, 0.4)             # the task board
    for b in (104.0, 105.5, 107.0):
        add(b, scribble(0.35), -19, 0.4)             # one digit at a time
    add(105.0, warn_thud(), -13, 0.4)                # 做得很慢
    add(106.0, blip(1200), -22, 0.4)
    add(107.0, blip(1300), -25, 0.4)
    for b in (108, 109, 110):
        add(b, footstep(), -16, 0.45 + 0.05 * (b - 108))
    add(111.0, swish(0.75), -12, 0.75)               # the curtain
    add(112.5, chime(1567.98), -12, 0.75)            # 见光
    add(112.5, sparkle(0.6, 7), -22, 0.75)
    for b in (113, 114, 115, 116):
        add(b, footstep(), -16, 0.7 - 0.12 * (b - 113))
    add(117.0, slosh(0.4), -16, -0.1)                # scoops water
    add(117.5, splash(0.5, 0.35), -13, 0.1)          # face splash (洗把脸)
    add(117.0, page_flip(), -18, 0.3)                # the board turns over, header line 2 changes
    add(120.0, pop(450, 1300), -13, 0.4)             # easy 1 done
    add(121.0, pop(520, 1500), -13, 0.4)             # easy 2 done
    add(121.05, bell(2093, 0.8), -18, 0.4)
    add(122.5, whoosh(0.3), -22, 0.4)                # the hard card moves aside
    add(123.5, blip(1300), -21, 0.2)
    add(peak(126.0, 0.6), whoosh(0.6), -14, 0.0)
    # ---- 照着做: the three rows, acted on the mattress; he points; he jumps in
    add(126.5, slosh(1.2), -21, -0.4)
    add(127.0, pop(380, 1100), -15, -0.7)
    add(130.0, blub(420, 1300, 0.08), -12, 0.2)      # row 1
    add(130.02, pop(380, 1100), -15, 0.2)
    add(131.0, bubbles(0.3, 2, 500, 900), -24, -0.5)
    add(131.5, boing(), -16, -0.5)
    add(132.0, splash(0.5, 0.35), -17, -0.5)
    add(134.0, blub(460, 1400, 0.08), -12, 0.3)      # row 2
    add(134.02, pop(420, 1200), -15, 0.3)
    add(134.5, drop(0.45), -17, -0.5)
    add(135.0, bubbles(0.6, 4, 420, 800), -24, -0.5)
    add(136.5, wobble(1.4), -21, -0.5)
    for b in (137.5, 138.5, 139.5):
        add(b, bubbles(0.2, 2, 520, 900), -28, -0.5)
    add(140.5, blub(500, 1500, 0.08), -12, 0.4)      # row 3
    add(140.52, pop(460, 1300), -15, 0.4)
    add(141.0, splash(0.45, 0.3), -16, -0.5)         # face splash
    add(144.0, blip(1100), -22, 0.0)                 # 仅供参考
    add(144.5, blip(1300), -25, 0.5)
    add(146.0, whoosh(0.2), -22, -0.4)               # he points
    add(151.0, slosh(0.7), -21, -0.5)                # stands up on the mattress
    add(152.0, thump(160, 70, 0.2), -17, -0.5)       # crouch
    add(152.5, boing(), -14, -0.4)                   # jump
    add(152.6, whoosh(0.5), -20, -0.3)
    add(153.5, splash(1.1, 1.0), -7, -0.3)           # into the water
    for b in (155.0, 156.5, 158.0, 159.0):
        add(b, bubbles(0.4, 3, 400, 800), -24, -0.2)
    return c


def mix(out_path):
    n = int(DUR * SR)
    L = np.zeros(n + SR * 3)
    R = np.zeros(n + SR * 3)
    for b, s, g, p in cues():
        st = int(round(b * BEAT * SR))
        amp = 10 ** (g / 20)
        a = (p + 1) * np.pi / 4
        L[st: st + len(s)] += s * amp * np.cos(a)
        R[st: st + len(s)] += s * amp * np.sin(a)
    L, R = L[:n], R[:n]
    fade = np.ones(n)
    k = int(0.3 * SR)
    fade[-k:] = np.linspace(1, 0, k)
    L, R = L * fade, R * fade
    peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
    drive = DRIVE
    L, R = np.tanh(drive * L / peak) / np.tanh(drive), np.tanh(drive * R / peak) / np.tanh(drive)
    # level by loudness, not by peak: same integrated loudness as the previous episode
    gain = 10 ** ((TARGET_LUFS - lufs(L, R)) / 20)
    L, R = L * gain, R * gain
    pk = max(np.max(np.abs(L)), np.max(np.abs(R)))
    if pk > 10 ** (-1.5 / 20):
        raise SystemExit(f'sample peak {20 * np.log10(pk):.2f} dBFS > -1.5 dBFS at {TARGET_LUFS} LUFS: lower HIT_DB')
    peak = pk
    pcm = (np.stack([L, R], axis=1) * 32767).astype(np.int16)
    with wave.open(str(out_path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f'wrote {out_path}: {n / SR:.3f} s, {len(cues())} cues, {lufs(L, R):.1f} LUFS, sample peak {20 * np.log10(peak):.1f} dBFS')


if __name__ == '__main__':
    out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'build/sfx.wav')
    out.parent.mkdir(parents=True, exist_ok=True)
    mix(out)
