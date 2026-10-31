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


# ---------------- voice-like sounds (formant synthesis; no real speech, no music) ----------------
VOWELS = {'a': (730, 1150, 2500), 'o': (520, 880, 2450), 'e': (480, 1800, 2550), 'i': (300, 2250, 3000),
          'u': (340, 760, 2350), 'v': (300, 1750, 2300)}


def _formant_gain(f, fmts, bws=(90, 110, 160), amps=(1.0, 0.55, 0.25)):
    return sum(a * np.exp(-((f - F) ** 2) / (2 * bw ** 2)) for F, bw, a in zip(fmts, bws, amps))


def voice(vowel='a', f0=128, d=0.17, onset='t'):
    """One spoken syllable: glottal harmonics shaped by the vowel's formants, a short consonant burst first."""
    t = T(d)
    fmts = VOWELS[vowel]
    f = f0 * (1.06 - 0.12 * t / d) * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t))
    ph = sweep_phase(f)
    y = np.zeros(len(t))
    for h in range(1, 40):
        fh = h * f0
        if fh > 5000:
            break
        y += _formant_gain(fh, fmts) / h ** 0.6 * np.sin(h * ph)
    env = np.clip(t / 0.018, 0, 1) * np.clip((d - t) / 0.06, 0, 1) ** 1.5
    y = y * env
    lo, hi = {'t': (2500, 7000), 's': (4000, 9000), 'b': (150, 1200), 'k': (1500, 4000)}[onset]
    burst = fft_band(rng.standard_normal(int(0.03 * SR)), lo=lo, hi=hi) * np.exp(-np.arange(int(0.03 * SR)) / SR / 0.006)
    out = np.zeros(len(t) + len(burst) // 2)
    out[: len(burst)] += norm(burst) * 0.35
    out[len(burst) // 3: len(burst) // 3 + len(y)] += norm(y)
    return norm(out)


def whisper(vowel='a', d=0.2):
    """The same syllable whispered: noise through the vowel's formants, no pitch."""
    n = rng.standard_normal(int(d * SR))
    X = np.fft.rfft(n)
    fr = np.fft.rfftfreq(len(n), 1 / SR)
    X *= _formant_gain(fr, VOWELS[vowel], bws=(160, 200, 260)) + 0.08 * (fr > 3000)
    y = np.fft.irfft(X, len(n))
    t = T(d)
    env = np.clip(t / 0.03, 0, 1) * np.clip((d - t) / 0.08, 0, 1)
    return norm(y * env)


def lip():
    """Lips moving with no voice: a tiny soft click."""
    t = T(0.03)
    return norm(fft_band(rng.standard_normal(len(t)), lo=300, hi=2500) * np.exp(-t / 0.004))


def hum_on(d=0.35):
    """The light pen switching on: a short rising electric hum."""
    t = T(d)
    f = 180 * (360 / 180) ** np.clip(t / 0.15, 0, 1)
    ph = sweep_phase(f)
    y = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sign(np.sin(3 * ph)) * 0.3
    return norm(fft_band(y, hi=3000) * env_ar(len(t), 0.01, 0.12))


def marker(d=0.7):
    """A glowing marker drawing a loop: a bright squeaky swish that follows the loop."""
    t = T(d)
    n = fft_band(rng.standard_normal(len(t)), lo=2200, hi=6500)
    sq = np.sin(sweep_phase(2400 + 500 * np.sin(2 * np.pi * 2.2 * t))) * 0.25
    env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 0.8 * (0.75 + 0.25 * np.sin(2 * np.pi * 9 * t))
    return norm((n + sq) * env)


def scan(d=0.33, up=True):
    """The recognition test sweeping up a column: quick rising blips."""
    out = np.zeros(int(d * SR) + SR // 8)
    for k in range(6):
        b = blip(900 + k * 160 if up else 1700 - k * 160)
        st = int(k * d / 6 * SR)
        out[st: st + len(b)] += b * (0.5 + 0.1 * k)
    return norm(out)


def step_snd():
    t = T(0.09)
    y = fft_band(rng.standard_normal(len(t)), lo=90, hi=900) * np.exp(-t / 0.018)
    return norm(y + 0.5 * np.sin(2 * np.pi * 85 * t) * np.exp(-t / 0.03))


def stack(f0=210):
    """A block landing on the pile: a short wooden thunk."""
    t = T(0.16)
    y = np.sin(sweep_phase(f0 * (1 + 0.6 * np.exp(-t / 0.01)))) * env_ar(len(t), 0.001, 0.045)
    c = fft_band(rng.standard_normal(len(t)), lo=600, hi=4000) * np.exp(-t / 0.004) * 0.4
    return norm(y + c)


# ---------------- cue sheet (beat, sound, gain dB, pan -1..1) ----------------
HIT_DB = -2.0   # frame-0 hit (2 dB under the old 0 dB: this mix is sparser, the hit set the peak)
VOX_DB = -13.0  # spoken syllables
DRIVE = 1.8     # soft clip before levelling (bedtime_words 1.3; music_study 1.8 for its sparser mix)
# syllables of the line he says in ② (速度是路程与时间之比) and of the opening's English words
LINE2_V = ['u', 'u', 'i', 'u', 'e', 'v', 'i', 'a', 'i', 'i']
HOOK_V = [('a', 't'), ('a', 'k'), ('e', 't'), ('o', 'b'), ('i', 'k'), ('a', 'b')]


def cues():
    """One effect per visual event, on its beat (src/scene.js, src/sections.js)."""
    c = []
    add = lambda b, s, g, p=0.0: c.append((b, s, g, p))
    # ---- opening: frame 0 hit; he paces and reads one list, half the words aloud (they fly into 念出声 as solid
    # blocks), half silently (dashed boxes into 默读)
    add(0, hit(), HIT_DB, 0.0)
    for i, b in enumerate((0, 1, 2, 3)):
        v, on = HOOK_V[i]
        add(b, voice(v, 128 + 6 * (i % 2), 0.17, on), VOX_DB + 2, 0.15)       # says the word: it fills solid and flies
        add(b + 0.5, pop(330 + 50 * i, 980 + 110 * i, 0.09), -17, -0.55)      # lands in 念出声
        add(b + 1, page_flip(0.07), -27, -0.7)                                 # a silent word lands in 默读
    # reveal 1 (4.5): one list, half aloud -> 60 % vs 76 % recognised
    add(4.5, whoosh(0.38), -13, -0.3)
    add(4.5, scan(0.33), -17, -0.5)
    add(5.0, pop(420, 1250), -14, -0.45)
    add(5.0, pop(360, 1050), -17, -0.65)
    add(6.5, whoosh(0.22, bright=0.6), -24, 0.2)                              # he turns to the right
    # he reads the next list almost all aloud (3 of 4 words here); the right pair builds
    add(6.5, pop(300, 900, 0.08), -19, 0.6)
    for i, b in enumerate((6.5, 7.0, 8.0)):
        v, on = HOOK_V[2 + i]
        add(b, voice(v, 130 + 5 * i, 0.15, on), VOX_DB, 0.25)
    add(8.0, page_flip(0.07), -27, 0.6)                                       # the one silent word lands
    # reveal 2 (8.5): almost all aloud -> 63 % vs 65 %, the difference is gone
    add(8.5, whoosh(0.42, bright=1.2), -12, 0.4)
    add(8.5, scan(0.33), -18, 0.55)
    add(8.6, drop(0.45), -14, 0.5)
    add(9.0, pop(380, 1000), -17, 0.6)
    add(10.0, whoosh(0.22, bright=0.6), -24, -0.1)                            # turns back to the left
    add(10.5, bell(1568), -8, -0.45)                                          # ✓ 挑着念
    add(10.55, sparkle(), -21, -0.45)
    add(11.5, bonk(), -15, 0.45)                                              # 全念：差不多 + shrug
    add(13.0, blip(1200), -22, 0.0)                                           # source
    for b in (14.5, 15.5, 16.5):
        add(b, step_snd(), -24, -0.1)
    add(16.0, whoosh(0.5, up=False), -17, 0.0)
    add(17.0, whoosh(0.3), -17, 0.0)                                          # the second line flips to the answer
    for i in range(10):
        add(17.25 + i * 0.25, type_click(), -32, 0.0)
    # ---- 挑着念 (17-32): the floating page, ① ② ③, the evidence card
    add(17.5, riser(0.45), -18, -0.2)
    add(18.5, sparkle(0.45, 6), -23, -0.2)
    for i, b in enumerate((19, 21, 23)):
        add(b, pop(380 + 60 * i, 1150 + 120 * i), -13, 0.4)
        add(b, whoosh(0.2), -25, 0.4)
    add(26.5, whoosh(0.25), -21, 0.5)
    for i, b in enumerate((26.5, 27.0, 27.5, 28.0)):
        add(b, pop(520 - 50 * i, 1400 - 150 * i, 0.09), -15 - i, 0.55)      # 77 > 74 > 69 > 65
    add(28.5, blip(1200), -22, 0.5)
    # ---- ① 念哪些 (32-64): the notes page, a silent read-through, three loops with the light pen
    add(32.0, whoosh(0.4), -14, 0.2)                                          # cut to ①
    for b in (31.5, 32.5):
        add(b, step_snd(), -24, -0.4)
    for i in range(12):
        add(33 + i * 0.25, type_click(), -33, -0.2)
    for b in (34, 35, 36, 37, 38, 39):
        add(b, tick(1900), -24, 0.2)                                          # the dashed box moves down a row
    add(41.5, hum_on(), -17, -0.3)                                            # light pen on
    for b in (42, 46, 50):
        add(b, marker(0.7), -16, 0.25)
        add(b + 1.5, pop(420, 1250), -14, 0.35)                               # 定义 / 公式 / 单词
    add(53.0, whoosh(0.4, up=False, bright=0.6), -20, 0.3)                    # the other rows dim
    add(53.5, tick(1500), -20, -0.3)                                          # pen off
    add(54.0, blip(1100), -21, 0.2)
    add(56.0, whoosh(0.22, bright=0.7), -22, -0.2)                            # he points at the loops
    for b in (63, 64):
        add(b, step_snd(), -24, -0.5)
    # ---- ② 怎么念 (64-96): the circled line said aloud, whispered, mouthed, read silently
    add(64.0, whoosh(0.4), -14, 0.0)                                          # cut to ②
    for i in range(12):
        add(65 + i * 0.25, type_click(), -33, -0.2)
    for b in (65.5, 71.5, 77.5, 83.5):
        add(b, blip(1300), -24, 0.0)                                          # row label
    for i in range(10):
        v = LINE2_V[i]
        on = 's' if i in (0, 2, 6, 8) else 't' if i in (1, 3, 9) else 'k'
        add(66 + 0.5 * i, voice(v, 132 - 2 * i, 0.15, on), VOX_DB, -0.1)
        add(72 + 0.5 * i, whisper(v, 0.17), VOX_DB - 9, -0.1)
        add(78 + 0.5 * i, lip(), -30, -0.1)
    add(84.0, page_flip(0.25), -22, 0.3)                                      # the dashed row
    for i, b in enumerate((87, 87.5, 88, 88.5)):
        add(b, pop(520 - 60 * i, 1450 - 160 * i), -14 - i, 0.45)              # 66 > 57 > better > 43
    add(89.0, whoosh(0.22, bright=0.7), -22, -0.2)                            # points
    add(89.5, chime(1318.5), -10, 0.1)                                        # 正常出声最好
    add(90.5, blip(1100), -22, 0.2)
    # ---- ③ 念了有什么用 (96-128): spoken blocks pile up on 记住原话, bounce off 读懂意思
    add(96.0, whoosh(0.4), -14, 0.0)                                          # cut to ③
    for i in range(12):
        add(97 + i * 0.25, type_click(), -33, -0.2)
    add(96.0, pop(320, 950), -17, 0.4)                                        # the two trays
    add(96.5, page_flip(), -20, -0.5)                                         # picks up the sheet
    for i, b in enumerate((99, 100, 101, 102, 103)):
        add(b, voice(LINE2_V[i * 2], 130, 0.16, 't' if i % 2 else 's'), VOX_DB, -0.3)
        add(b + 1, stack(220 + 25 * i), -13, 0.1)
    for b in (104.5, 105.5):
        add(b, voice('e', 136, 0.16, 'k'), VOX_DB, -0.3)
        add(b + 1, boing(0.28), -15, 0.6)                                     # bounces off 读懂意思
    add(106.5, bell(1568), -8, 0.1)                                           # ✓ 记忆题 81 % vs 74 %
    add(106.55, sparkle(0.5, 7), -22, 0.1)
    add(108.0, bonk(), -14, 0.6)                                              # ≈ 差不多
    add(109.0, whoosh(0.2, bright=0.6), -25, -0.4)                            # shrug
    add(110.0, blip(1100), -22, 0.0)
    add(113.5, boing(0.3), -18, 0.6)                                          # ? over 读懂意思
    add(115.0, warn_thud(), -12, 0.6)                                         # 要读懂：另想办法
    add(120.0, whoosh(0.22, bright=0.7), -22, -0.3)                           # points
    # ---- 照着做 (128-160): the track builds while he acts each clip; no CTA, ends on the last bar
    add(128.0, whoosh(0.4), -14, 0.0)                                         # cut to 照着做
    for i in range(10):
        add(129 + i * 0.25, type_click(), -33, -0.2)
    add(130.0, pop(380, 1100), -13, 0.0)
    add(130.0, tick(1900), -24, -0.5)                                         # his dashed box
    add(133.5, blip(1500), -22, 0.1)                                          # arrow
    add(134.0, pop(420, 1200), -13, 0.2)
    add(134.0, hum_on(0.3), -19, -0.5)
    add(134.5, marker(0.7), -16, 0.2)
    add(137.5, blip(1700), -22, 0.3)                                          # arrow
    add(138.0, pop(460, 1300), -13, 0.4)
    for i, b in enumerate((138, 139, 140)):
        add(b, voice(['u', 'i', 'a'][i], 130, 0.16, 's'), VOX_DB, -0.4)
    add(142.0, warn_thud(), -10, 0.3)                                         # 读懂另想办法
    add(142.25, whoosh(0.18), -27, -0.5)
    add(143.0, whoosh(0.18), -27, -0.5)
    add(144.0, blip(1100), -21, 0.3)
    add(150.0, whoosh(0.22, bright=0.7), -21, -0.3)                           # points at the track
    add(153.5, riser(0.3), -17, -0.4)                                         # jump
    add(155.0, thump(160, 60, 0.3), -11, -0.4)                                # lands
    add(155.05, sparkle(0.6, 8), -22, -0.4)
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
