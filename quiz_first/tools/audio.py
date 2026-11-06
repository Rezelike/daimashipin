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
TARGET_LUFS = -18.4  # same integrated loudness as the previous episodes


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


def buzz_wrong(d=0.34, f=150):
    """Game-show 'wrong' buzzer: a low square-ish tone with a fast wobble."""
    t = T(d)
    ph = sweep_phase(f * (1 + 0.025 * np.sin(2 * np.pi * 31 * t)))
    y = np.sign(np.sin(ph)) * 0.6 + np.sin(2 * ph) * 0.3 + np.sin(3 * ph) * 0.2
    y = fft_band(y, lo=90, hi=2600)
    env = (1 - np.exp(-t / 0.004)) * np.clip((d - t) / 0.03, 0, 1)
    return norm(y * env)


def slap():
    """Hand on the buzzer dome: a short thump + a plastic click."""
    t = T(0.14)
    f = 210 * (90 / 210) ** np.clip(t / 0.05, 0, 1)
    y = np.sin(sweep_phase(f)) * env_ar(len(t), 0.001, 0.035)
    c = fft_band(rng.standard_normal(len(t)), lo=1800, hi=8000) * np.exp(-t / 0.004) * 0.7
    return norm(y + c)


def step(bright=1.0):
    """One footstep on the stage floor."""
    t = T(0.12)
    y = np.sin(sweep_phase(110 * (60 / 110) ** np.clip(t / 0.05, 0, 1))) * env_ar(len(t), 0.001, 0.03)
    n = fft_band(rng.standard_normal(len(t)), lo=500, hi=3500 * bright) * np.exp(-t / 0.012) * 0.6
    return norm(y + n)


def squeak(d=0.9):
    """A fat highlighter drawn round a word: rubbing noise with a wobbling pitched edge."""
    t = T(d)
    n = fft_band(rng.standard_normal(len(t)), lo=1200, hi=5200)
    tone = np.sin(sweep_phase(2300 + 500 * np.sin(2 * np.pi * 2.2 * t))) * 0.35
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.8 * (0.65 + 0.35 * np.abs(np.sin(2 * np.pi * 4.4 * t)))
    return norm((n + tone) * env)


# ---------------- cue sheet (beat, sound, gain dB, pan -1..1) ----------------
HIT_DB = 0.0    # frame-0 hit


def cues():
    """One effect per visual event, on its beat (src/scene.js, src/sections.js). Left = negative pan."""
    c = []
    add = lambda b, s, g, p=0.0: c.append((b, s, g, p))
    # ---- opening: he thinks in front of the question card, the options light up one per beat
    add(0, hit(), HIT_DB, 0.0)
    for k, b in enumerate((0.5, 1.5, 2.5, 3.5)):
        add(b, pop(320 + 50 * k, 950 + 110 * k, 0.09), -15, -0.55)
    for b in (1, 2, 3, 4):
        add(b, tick(2600, tock=b % 2 == 0), -21, 0.0)
    add(3.5, whoosh(0.3, bright=0.7), -21, -0.1)          # arm up
    # reveal 1 (4.5): three slaps, three wrong buzzes; the scoreboards count up to 31% / 57%
    for k, b in enumerate((4.5, 5.5, 6.5)):
        add(b, slap(), -12, 0.0)
        add(b, buzz_wrong(0.32, 150 - 8 * k), -9, 0.05)
    add(4.5, blip(1500), -20, 0.45)                         # marquee flips
    add(4.55, spin(0.4, 12), -25, 0.45)                     # the numbers roll
    add(7.0, drop(0.45), -17, 0.0)                          # he slumps
    # reveal 2 (8.5): the hour counter rolls to 48, the same questions again, two dings
    add(8.5, slap(), -12, 0.0)
    add(8.5, bell(1568, 1.0), -10, 0.05)
    add(8.5, whirr(1.0, 18), -19, 0.45)
    add(9.5, slap(), -12, 0.0)
    add(9.5, bell(2093, 1.0), -11, 0.05)
    add(8.65, riser(0.5), -19, 0.4)
    add(10.5, boing(), -17, 0.0)                            # he jumps
    add(10.5, chime(1318.5), -9, 0.35)                      # check: 反超
    add(10.55, sparkle(), -22, 0.35)
    add(11.5, bonk(), -15, 0.6)                             # 57% -> 53%
    add(13.0, blip(1200), -22, -0.6)                        # source
    add(15.5, whoosh(0.5, up=False), -17, 0.3)
    # ---- 先猜再读 (17): the card flies into his hand, the answer line, pocket, walk to the page, tags pop
    add(16.5, whoosh(0.3), -16, -0.5)
    add(17.0, pop(380, 1150), -13, 0.0)
    for i in range(14):
        add(17.2 + i * 0.2, type_click(), -32, 0.0)
    add(18.0, page_flip(0.2), -18, 0.6)
    add(19.0, pop(500, 300, 0.1), -17, -0.1)               # into the pocket
    for k, b in enumerate((19.0, 21.5, 24.0)):
        add(b, pop(360 + 60 * k, 1050 + 150 * k), -12, -0.5)
    for b in (20, 21, 22, 23):
        add(b, step(), -20, 0.1)
    add(26.5, blip(1300), -19, -0.2)
    add(27.0, tick(2400), -20, -0.2)
    add(27.5, tick(1700), -20, -0.2)
    add(29.0, sparkle(0.5, 6), -24, -0.6)
    add(30.5, whoosh(0.5), -15, 0.0)
    add(31.5, thump(150, 60, 0.3), -14, 0.0)                # the round screen comes down
    # ---- ① 挑 5 道重点题: five cards out of the question bank, the rest back in
    add(32.0, pop(300, 900), -16, -0.3)
    for k, P in enumerate((36, 38, 40, 42, 44)):
        add(P - 0.5, page_flip(0.1), -19, -0.3)
        add(P, pop(360 + 45 * k, 1050 + 120 * k), -12, 0.1 + 0.15 * k)
    add(46.0, thump(), -11, -0.2)                           # lid shut
    add(48.0, chime(1318.5), -9, 0.3)                       # 问到的：记得更牢
    add(48.05, sparkle(), -21, 0.3)
    add(49.0, whoosh(0.2), -23, 0.1)
    add(50.0, bonk(), -15, -0.1)                            # 没问到的：不会多记住
    add(52.0, pop(420, 1200), -17, 0.0)
    add(54.0, blip(1200), -22, -0.6)
    add(60.0, whoosh(0.4, up=False), -16, 0.2)
    add(60.5, page_flip(0.16), -18, -0.2)
    for b in (62.5, 63.5):
        add(b, step(), -20, 0.0)
    # ---- ② 先猜，不翻书: write 红色？, wrong, shrug, keep guessing; one week later 55% vs 45%
    add(64.0, blip(1800), -19, 0.0)
    add(64.5, whoosh(0.3), -16, 0.3)
    add(64.6, pop(380, 1100), -14, 0.3)
    add(65.5, pop(600, 1400, 0.06), -21, -0.1)
    for b in (66.0, 67.0):
        add(b, scribble(0.9), -15, 0.1)
    add(69.0, buzz_wrong(0.36, 142), -9, 0.3)
    add(69.0, thump(240, 110, 0.12), -14, 0.3)              # the 错 stamp
    add(70.0, whoosh(0.25, bright=0.6), -21, 0.0)           # shrug
    for k, b in enumerate((72, 74, 76, 78)):
        add(b, page_flip(0.16), -16, 0.3)
        add(b + 0.5, scribble(0.8), -18, 0.1)
        add(b + 1.5, buzz_wrong(0.2, 160 + 6 * k), -15, 0.3)
    add(80.0, page_flip(0.16), -17, 0.3)
    add(80.5, whoosh(0.4, up=False, bright=0.7), -19, -0.3)
    add(82.0, whoosh(0.3), -16, 0.4)
    add(82.0, whirr(1.1, 16), -19, 0.4)
    add(82.5, spin(0.4, 12), -24, 0.2)
    add(83.0, spin(0.4, 12), -24, 0.6)
    add(83.5, blip(1300), -21, 0.2)
    add(84.0, blip(1100), -21, 0.6)
    add(86.0, chime(1318.5), -9, 0.2)
    add(86.05, sparkle(), -21, 0.2)
    add(88.0, pop(420, 1200), -17, 0.3)
    add(88.5, whoosh(0.2), -23, 0.2)
    add(90.0, blip(1200), -22, -0.6)
    add(94.5, whoosh(0.5, up=False), -16, 0.0)
    # ---- ③ 带着题读，找到就圈: walk the page, turn, circle 黑色, fix the guess; 84% vs 54%
    add(96.0, blip(1800), -19, 0.0)
    add(96.0, page_flip(0.24), -17, 0.4)
    add(96.5, pop(520, 1300, 0.08), -19, -0.1)
    for b in (99, 100, 101, 102, 103):
        add(b, step(), -20, -0.2 + 0.1 * (b - 99))
    add(103.5, whoosh(0.2, bright=0.7), -22, 0.6)          # he turns round
    add(104.0, squeak(0.75), -14, 0.4)
    add(105.5, chime(1568), -9, 0.4)                        # found it
    add(105.55, sparkle(), -21, 0.4)
    add(107.0, scribble(0.5), -16, -0.5)                    # strike 红色？
    add(108.0, pop(420, 1250), -13, -0.5)                   # 黑色 ✓
    add(108.05, bell(2093, 0.8), -17, -0.5)
    add(110.0, whoosh(0.3), -16, -0.5)
    add(110.5, spin(0.4, 12), -24, -0.7)
    add(111.0, spin(0.4, 12), -24, -0.4)
    add(112.0, blip(1300), -21, -0.7)
    add(114.0, chime(1318.5), -10, -0.7)
    add(114.05, sparkle(), -22, -0.7)
    add(115.0, whoosh(0.2), -23, 0.4)
    add(116.0, pop(420, 1200), -17, -0.5)
    add(118.0, blip(1200), -22, -0.6)
    add(126.5, whoosh(0.5, up=False), -15, 0.0)
    add(127.5, thump(150, 60, 0.3), -13, 0.0)               # the big screen comes down
    # ---- 照着做: three panels flip while he acts each step, pink note, 通关, point, two jumps
    add(128.0, blip(1800), -19, 0.2)
    add(129.5, page_flip(0.16), -18, -0.5)
    for k, b in enumerate((130, 134, 138)):
        add(b, page_flip(0.12), -16, 0.3)
        add(b, pop(380 + 60 * k, 1100 + 150 * k), -12, 0.3)
    add(133.0, scribble(0.9), -18, -0.5)
    add(137.5, squeak(0.9), -17, -0.5)
    add(142.0, warn_thud(), -10, 0.3)
    add(142.3, whoosh(0.18), -26, -0.5)
    add(143.2, whoosh(0.18), -26, -0.5)
    add(144.0, blip(1100), -21, 0.3)
    add(146.0, chime(1568), -7, 0.0)                        # 通关
    add(146.05, sparkle(0.8, 14), -18, 0.0)
    add(146.0, thump(120, 50, 0.3), -15, 0.0)
    add(149.5, whoosh(0.2), -21, -0.3)
    add(154.0, boing(), -14, -0.5)
    add(155.0, step(0.6), -16, -0.5)
    add(156.0, boing(), -15, -0.5)
    add(157.0, step(0.6), -16, -0.5)
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
