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


def spin(d=0.9, n=22):
    out = np.zeros(int(d * SR) + SR // 10)
    times = d * np.linspace(0, 1, n) ** 1.3
    tk = tick(3300)
    for tt in times:
        st = int(tt * SR)
        out[st: st + len(tk)] += tk
    return norm(out)


# ---------------- cue sheet (beat, sound, gain dB, pan -1..1) ----------------
def cues():
    c = []
    add = lambda b, s, g, p=0.0: c.append((b, s, g, p))
    # opening — clock ticks build to the first reveal
    for b in range(0, 5):
        add(b, tick(tock=b % 2 == 1), -21, 0.65)
    add(0.5, page_flip(), -17, -0.45)
    add(2.5, page_flip(), -18, -0.45)
    add(1.5, zz_puff(), -27, 0.45)
    for i in range(22):
        add(i * 0.12, type_click(), -33, 0.0)
    add(4.5, whoosh(0.38), -13, 0.0)
    add(4.5, riser(0.4), -14, 0.0)
    add(4.55, spin(0.5, 10), -26, 0.65)
    add(6.5, whoosh(0.42, bright=1.2), -12, 0.0)
    add(6.55, spin(0.65, 18), -25, 0.65)
    add(6.65, drop(), -11, -0.5)
    add(8.5, bell(1568), -8, 0.4)
    add(8.55, sparkle(), -21, 0.45)
    add(8.65, pop(500, 1300), -17, 0.5)
    add(9.5, bonk(), -16, -0.5)
    add(13.5, whoosh(0.5, up=False), -17, -0.6)
    # 先睡一觉
    add(14.6, whoosh(0.28), -18, 0.0)
    for i in range(12):
        add(15.2 + i * 0.22, type_click(), -33, 0.0)
    add(16.0, boing(), -14, 0.0)
    add(17.0, pop(360, 1050), -12, -0.4)
    add(18.8, stretch(), -16, 0.0)
    add(20.0, pop(420, 1250), -12, 0.0)
    add(23.0, page_flip(), -17, 0.0)
    add(24.0, pop(480, 1450), -12, 0.4)
    add(26.0, blip(1300), -19, 0.5)
    add(29.2, sparkle(0.5, 6), -24, -0.4)
    add(30.5, whoosh(0.5), -15, -0.2)
    # ① 什么时候
    add(31.8, blip(1800), -20, 0.0)
    add(32.0, whoosh(0.25), -20, 0.0)
    for i in range(10):
        add(32.2 + i * 0.24, type_click(), -34, -0.3)
    add(34.0, pop(420, 1200), -14, -0.6)
    add(35.0, blip(1600), -22, -0.2)
    for k in range(12):
        add(36 + k, tick(tock=k % 2 == 1), -17, -0.6)
    add(36.0, pop(380, 1100), -15, 0.5)
    for b in (28.5, 32.5, 36.5, 40.5, 44.5):
        add(b, page_flip(), -23, -0.4)
    add(48.0, bell(1318.5, 2.2), -6, -0.6)
    add(48.05, pop(380, 1100), -16, 0.5)
    add(48.2, blip(2100), -22, -0.3)
    add(50.2, thump(), -11, -0.4)
    add(50.6, whoosh(0.45, up=False), -18, -0.4)
    add(52.0, pop(380, 1100), -15, 0.5)
    add(52.3, zz_puff(), -22, -0.4)
    add(54.0, blip(1200), -21, 0.5)
    add(56.0, zz_puff(), -26, -0.4)
    add(60.0, zz_puff(), -26, -0.4)
    add(62.5, whoosh(0.6), -14, 0.0)
    # ② 睡多久
    add(64.0, whoosh(0.25), -20, 0.0)
    add(65.5, pop(400, 1150), -16, -0.5)
    for i, b in enumerate((65.0, 65.4, 65.8)):
        add(b, blip(1000 + i * 150), -24, 0.5)
    add(67.0, whirr(1.4, 14), -19, -0.1)
    add(70.0, bell(1046.5), -9, 0.0)
    add(70.05, pop(380, 1100), -17, 0.5)
    add(75.0, whirr(1.4, 18), -19, -0.1)
    add(78.0, bell(1318.5), -9, 0.0)
    add(78.05, pop(420, 1200), -17, 0.5)
    add(83.0, whirr(1.4, 22), -19, -0.1)
    add(86.0, bell(1568), -9, 0.0)
    add(86.05, pop(460, 1300), -17, 0.5)
    add(88.0, chime(1318.5), -9, -0.3)
    add(88.1, sparkle(), -20, -0.4)
    add(91.0, zz_puff(), -26, -0.4)
    add(95.0, whoosh(0.55, up=False), -15, -0.3)
    # ③ 醒来干嘛
    add(96.0, whoosh(0.25), -20, 0.0)
    add(98.0, alarm(1.32), -13, -0.3)
    add(100.4, boing(), -15, -0.4)
    add(101.0, thump(260, 120, 0.12), -13, -0.3)
    add(100.6, pop(380, 1100), -16, 0.5)
    add(102.0, pop(420, 1200), -14, -0.6)
    add(102.3, page_flip(), -19, -0.4)
    add(103.0, pop(380, 1100), -16, 0.5)
    for b in (104, 108.5, 113, 121.5, 124):
        add(b, scribble(), -27, -0.4)
    add(106.0, whoosh(0.25), -19, -0.6)
    for k in range(7):
        add(108 + k, page_flip(0.1), -15, -0.6)
    add(115.0, thump(180, 60, 0.3), -9, -0.6)
    add(116.0, riser(0.4), -14, -0.4)
    add(117.5, bell(1568), -8, -0.4)
    add(117.6, sparkle(), -21, -0.4)
    add(117.7, pop(380, 1100), -16, 0.5)
    add(119.0, blip(1200), -21, 0.5)
    add(121.0, pop(500, 1400), -17, -0.3)
    add(126.0, whoosh(0.6), -14, 0.2)
    # 照着做
    add(127.0, whoosh(0.25), -20, 0.0)
    add(130.0, pop(380, 1100), -13, 0.4)
    add(130.4, page_flip(), -18, -0.5)
    add(134.0, pop(420, 1200), -13, 0.4)
    add(135.0, zz_puff(), -21, -0.5)
    add(138.0, pop(460, 1300), -13, 0.4)
    add(138.1, bell(2093, 0.9), -16, -0.5)
    add(139.6, scribble(), -25, -0.5)
    add(142.0, warn_thud(), -10, 0.4)
    add(142.3, whoosh(0.18), -26, -0.5)
    add(143.2, whoosh(0.18), -26, -0.5)
    add(144.0, blip(1100), -21, 0.4)
    add(146.0, shutter(), -13, 0.4)
    add(149.5, pop(400, 1250), -12, -0.2)
    add(150.4, whoosh(0.2), -22, -0.3)
    add(152.0, thump(320, 160, 0.1), -14, -0.2)
    add(152.05, bell(1760, 1.4), -9, -0.2)
    add(152.1, sparkle(0.7, 12), -17, -0.2)
    add(153.0, pop(380, 1100), -18, -0.2)
    add(153.8, pop(520, 1500), -16, -0.4)
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
    target = 10 ** (-1.5 / 20)
    L, R = L * target, R * target
    pcm = (np.stack([L, R], axis=1) * 32767).astype(np.int16)
    with wave.open(str(out_path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f'wrote {out_path}: {n / SR:.3f} s, {len(cues())} cues, raw peak {peak:.2f}')


if __name__ == '__main__':
    out = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'build/sfx.wav')
    out.parent.mkdir(parents=True, exist_ok=True)
    mix(out)
