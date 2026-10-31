"""Synthesize all SFX (no music) and mix them on the 128 BPM grid -> build/sfx.wav (48 kHz stereo)."""
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
TARGET_LUFS = -18.4  # same integrated loudness as the earlier episodes (plan: 混音 -18.4 LUFS)


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


# ---------------- this episode's own sounds ----------------
def step(bright=1.0):
    """A footstep on a gravel road: a soft low thump and a short crunch."""
    t = T(0.16)
    body = np.sin(sweep_phase(150 * (70 / 150) ** np.clip(t / 0.05, 0, 1))) * env_ar(len(t), 0.002, 0.035)
    crunch = fft_band(rng.standard_normal(len(t)), lo=900, hi=4200 * bright) * env_ar(len(t), 0.001, 0.018)
    return norm(body + 0.55 * crunch)


def flutter(d=0.45):
    """A flag cloth snapping in the wind."""
    t = T(d)
    n = fft_band(rng.standard_normal(len(t)), lo=250, hi=2600)
    env = np.sin(np.pi * t / d) ** 1.5 * (0.45 + 0.55 * np.abs(np.sin(2 * np.pi * 11 * t)))
    return norm(n * env)


def clink():
    """The hanging road sign: a small metal chain ping."""
    t = T(0.5)
    y = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / dd) for f, a, dd in ((3520, 1.0, 0.09), (5280, 0.5, 0.05), (2470, 0.4, 0.12)))
    return norm(y * (1 - np.exp(-t / 0.0008)))


def fill(n=7, d=0.42, f0=900, f1=1900):
    """A row of tiles filling left to right: quick rising blips over one beat."""
    out = np.zeros(int((d + 0.1) * SR))
    for k in range(n):
        f = f0 * (f1 / f0) ** (k / max(1, n - 1))
        t = T(0.05)
        s = np.sin(2 * np.pi * f * t) * env_ar(len(t), 0.001, 0.012)
        st = int(k * d / n * SR)
        out[st: st + len(s)] += s
    return norm(out)


def stumble():
    """Tripping into the gap: a scrape and a falling whoosh."""
    t = T(0.4)
    scrape = fft_band(rng.standard_normal(len(t)), lo=600, hi=3500) * env_ar(len(t), 0.004, 0.09)
    return norm(0.7 * scrape + 0.5 * whoosh(0.4, up=False))


# ---------------- cue sheet (beat, sound, gain dB, pan -1..1) ----------------
HIT_DB = -5.0   # frame-0 hit, the loudest sound (at 0 dB the AAC true peak went over 0 dBTP)
OPEN_DB = 8.0   # the 0-2 s footsteps: loud enough to hear on a phone under the hit


def cues():
    """One effect per visual event, on its beat (src/scene.js, src/sections.js). Footsteps on every heel strike."""
    c = []
    add = lambda b, s, g, p=0.0: c.append((b, s, g, p))
    walk = lambda beats, g, p: [add(b, step(), g, p) for b in beats]
    # ---- hook: frame-0 hit, he is already walking up toward the 21-day flag (heel strikes 0-4, feet together at 5)
    add(0, hit(), HIT_DB, 0.0)
    walk([1, 2, 3, 4], -20 + OPEN_DB, -0.1)   # the hit covers the heel strike on beat 0
    add(5, step(0.7), -16, 0.15)
    for i in range(16):
        add(0.14 + i * 0.14, type_click(), -33 + OPEN_DB, -0.3)
    # reveal 1 (4.5): 第 21 天：还没到顶 — the flag flashes, the caption pops, the bar is at ~2/3
    add(4.5, whoosh(0.32), -14, 0.0)
    add(4.5, flutter(), -17, 0.35)
    add(4.6, pop(380, 1100), -13, -0.4)
    add(5.0, tick(2200), -20, -0.4)
    add(6.0, boing(0.28), -19, 0.15)   # the shrug
    # reveal 2 (8.5): the camera pulls back, the fog lifts, 一般要 66 天
    add(8.5, whoosh(0.5, bright=1.2), -11, 0.2)
    add(8.5, riser(0.45), -16, 0.4)
    add(8.6, pop(420, 1250), -13, -0.4)
    add(9.0, bell(1318.5, 1.6), -12, 0.5)   # the 66 flag glows
    add(9.0, whoosh(0.18), -24, 0.0)        # he points up the road
    add(9.0, tick(2000), -22, -0.4)
    add(10.5, bell(1568), -9, -0.3)         # 最快 18 天
    add(10.5, sparkle(0.5, 6), -22, -0.3)
    add(11.5, pop(300, 700, 0.12), -14, 0.6)  # 最慢 ≈254 天（推算）
    add(11.5, whoosh(0.3), -23, 0.6)
    add(13.0, blip(1200), -22, -0.5)        # source
    add(15.5, whoosh(0.6), -16, 0.0)        # the camera closes in again
    # ---- the answer: he walks on (heel strikes 17-21, feet together at 22), the title flips, signpost boards pop
    add(16.75, whoosh(0.28), -18, 0.0)   # the title flips on beat 17
    walk([17, 18, 19, 20, 21], -21, 0.0)
    add(22, step(0.7), -22, 0.0)
    for i in range(12):
        add(17.4 + i * 0.22, type_click(), -33, 0.0)
    add(18.0, thump(200, 90, 0.14), -18, 0.3)  # the signpost
    for k, b in enumerate((19.0, 21.5, 25.0)):
        add(b, pop(360 + 60 * k, 1050 + 150 * k), -12, 0.3)
    add(22.0, whoosh(0.18), -24, 0.2)        # he points
    add(26.5, page_flip(), -16, -0.5)        # the 1960 card
    add(26.5, blip(1300), -20, -0.5)
    add(30.5, whoosh(0.5), -15, 0.0)
    # ---- ① 挑一件小事: he walks to the 早饭 sign (31-35), hangs the card on it
    walk([31, 32, 33, 34], -21, 0.0)
    add(35, step(0.7), -22, 0.0)
    add(31.5, pop(330, 900), -16, 0.2)       # the 早饭 plate
    add(31.8, whoosh(0.3, up=False), -17, -0.4)  # the hanging sign comes down
    add(32.0, clink(), -18, -0.4)
    for i in range(10):
        add(32.4 + i * 0.22, type_click(), -34, -0.3)
    add(36.0, pop(420, 1200), -13, 0.0)      # the card in his hand
    add(37.0, whoosh(0.2), -22, 0.1)         # arm up
    add(38.0, whoosh(0.25), -19, 0.2)        # onto the hook
    add(38.6, tick(1500, tock=True), -11, 0.25)
    add(42.0, pop(380, 1100), -14, 0.5)      # study example 1
    add(44.0, pop(440, 1300), -14, 0.65)     # study example 2
    add(45.0, blip(1500), -20, 0.6)
    add(46.0, blip(1100), -24, -0.5)         # source
    add(50.0, page_flip(0.2), -15, 0.2)      # 早饭 -> 7:30
    add(50.2, tick(2600), -18, 0.2)
    add(50.7, tick(2600, tock=True), -20, 0.2)
    add(50.5, pop(400, 1150), -15, -0.4)     # 定个钟点也行
    add(55.0, page_flip(0.2), -17, 0.2)      # back to 早饭
    add(58.5, whoosh(0.4, up=False), -20, 0.5)
    add(62.5, whoosh(0.6), -15, 0.0)
    # ---- ② 天天做: one step a day, every heel strike lights a slab (64-87, feet together at 88)
    walk(range(64, 88), -22, 0.0)
    add(88, step(0.7), -23, 0.0)
    add(64.0, whoosh(0.3, up=False), -17, -0.4)
    add(64.2, clink(), -18, -0.4)
    for i in range(10):
        add(64.4 + i * 0.22, type_click(), -34, -0.3)
    add(65.0, blip(1700), -20, -0.2)         # the bar is back
    add(72.0, pop(380, 1100), -14, 0.5)      # 研究里，做到的天数
    add(74.0, fill(7, 0.42, 1000, 2000), -17, 0.5)
    add(75.0, chime(1318.5), -9, 0.5)        # 88%
    add(78.0, fill(7, 0.42, 600, 1100), -19, 0.5)
    add(79.0, bonk(), -16, 0.5)              # 60-63%
    add(82.0, warn_thud(), -15, 0.4)         # 相关，不是因果
    add(83.0, blip(1100), -24, -0.5)
    add(95.0, whoosh(0.55, up=False), -16, 0.0)
    # ---- ③ 漏一天: the gap, the stumble (100), knees down (101), the tiny dip, up again, two more steps
    add(96.0, whoosh(0.3, up=False), -17, -0.4)
    add(96.2, clink(), -18, -0.4)
    add(96.0, thump(160, 70, 0.2), -18, 0.3)  # the gap opens in the road
    for i in range(10):
        add(96.4 + i * 0.22, type_click(), -34, -0.3)
    walk([97, 98, 99], -21, 0.0)
    add(100.0, stumble(), -12, 0.1)
    add(101.0, thump(120, 50, 0.3), -8, 0.1)  # knees on the road
    add(101.6, drop(0.35), -17, -0.2)        # bar −0.29
    add(102.0, pop(380, 1100), -14, 0.5)     # 漏一次，只掉 0.29 分
    add(104.0, fill(8, 0.42, 800, 1700), -18, 0.5)
    add(104.3, whoosh(0.3), -21, 0.0)        # getting up
    add(105.3, step(0.8), -19, 0.0)
    add(106.0, bonk(), -15, 0.6)             # the pink sliver
    walk([107], -21, 0.0)
    add(108, step(0.7), -22, 0.0)
    add(107.0, blip(1100), -24, -0.5)        # source
    add(110.0, whoosh(0.18), -24, 0.2)       # he points up at the scale
    add(112.0, chime(1046.5), -10, 0.5)      # 第二天接着做，照样往上涨
    add(112.05, sparkle(0.5, 6), -23, 0.5)
    add(126.5, whoosh(0.6), -15, 0.0)
    # ---- 照着做: the last steps to the top, three boards light up while he points, the sun clears the ridge
    walk([128, 129, 130], -21, 0.0)
    add(131, step(0.7), -22, 0.0)
    add(127.5, flutter(), -19, -0.5)         # the 66 flag
    add(128.0, whoosh(0.3, up=False), -17, -0.4)
    add(128.2, clink(), -18, -0.4)
    add(128.4, thump(200, 90, 0.14), -18, 0.3)  # the signpost
    for i in range(10):
        add(128.4 + i * 0.22, type_click(), -34, -0.3)
    for k, b in enumerate((130.0, 134.0, 138.0)):
        add(b, pop(380 + 50 * k, 1100 + 150 * k), -12, 0.35)
        add(b + 0.15, bell(1046.5 * 2 ** (k * 4 / 12), 0.9), -15, 0.35)
    add(130.5, chime(1568), -14, -0.3)       # 到顶
    add(130.5, whoosh(0.18), -24, 0.2)       # he points
    add(143.0, blip(1100), -22, -0.5)        # 仅供参考
    add(146.0, chime(1318.5), -8, 0.3)       # sunrise across the finished signpost
    add(146.0, sparkle(0.7, 10), -20, 0.4)
    add(146.0, whoosh(0.7, bright=0.8), -20, 0.4)
    add(150.0, whoosh(0.2), -22, 0.2)        # he points at it
    add(153.5, pop(520, 1500), -15, 0.2)     # hand up to the sun (a little hop)
    add(154.0, sparkle(0.5, 6), -22, 0.4)
    add(155.0, step(0.6), -24, 0.0)          # lands
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
    drive = 1.3
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
