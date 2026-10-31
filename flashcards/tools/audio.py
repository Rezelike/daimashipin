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


# ---------------- card sounds (this episode) ----------------
def flick():
    """One card leaving the pack: a 2 ms crack of bright noise."""
    t = T(0.012)
    return fft_band(rng.standard_normal(len(t)), lo=1500, hi=7000) * np.exp(-t / 0.0018)


def riffle(d=0.45, n=24):
    """The dealer's spring: a stream of card flicks, loudest in the middle of the arc."""
    out = np.zeros(int(d * SR) + SR // 20)
    for i in range(n):
        u = i / (n - 1)
        st = max(0, int((d * u + rng.uniform(-0.003, 0.003)) * SR))
        f = flick() * (0.35 + 0.65 * np.sin(np.pi * u) ** 0.7)
        out[st: st + len(f)] += f[: len(out) - st]
    out[: int(0.004 * SR)] += fft_band(rng.standard_normal(int(0.004 * SR)), lo=900, hi=5000) * 0.8   # sharp start
    return norm(out)


def deal_snap():
    """A card dealt off the deck: a snap, then a short swish."""
    t = T(0.09)
    sw = fft_band(rng.standard_normal(len(t)), lo=2000, hi=8000) * np.sin(np.pi * np.clip(t / 0.09, 0, 1)) ** 2
    k = int(0.004 * SR)
    sw[:k] += fft_band(rng.standard_normal(k), lo=1000, hi=6000) * np.exp(-np.arange(k) / SR / 0.0012) * 3
    return norm(sw)


def card_slide(d=0.28):
    """A card (or a stack) sliding over the felt."""
    t = T(d)
    n = fft_band(rng.standard_normal(len(t)), lo=400, hi=3500)
    return norm(n * np.clip(t / 0.006, 0, 1) * np.exp(-t / (d * 0.45)))


def card_flip():
    """Turning a card over: two quick flicks of air."""
    out = np.zeros(int(0.12 * SR))
    for st, lvl, lo, hi in ((0, 1.0, 1200, 6000), (int(0.03 * SR), 0.6, 2000, 8000)):
        t = T(0.035)
        b = fft_band(rng.standard_normal(len(t)), lo=lo, hi=hi) * np.exp(-t / 0.006) * lvl
        out[st: st + len(b)] += b
    return norm(out)


def tap_deck():
    """Squaring the deck on the table: two soft knocks."""
    out = np.zeros(int(0.22 * SR))
    for st, lvl in ((0, 1.0), (int(0.065 * SR), 0.65)):
        s = stack(240) * lvl
        out[st: st + len(s)] += s[: len(out) - st]
    return norm(out)


# ---------------- cue sheet (beat, sound, gain dB, pan -1..1) ----------------
HIT_DB = -2.0   # frame-0 hit
VOX_DB = -13.0  # the spoken answer (formant syllables, not a real voice)
DRIVE = 1.8     # soft clip before levelling (as read_aloud / music_study: a sparse mix)


def cues():
    """One effect per visual event, on its beat (src/scene.js, src/sections.js)."""
    c = []
    add = lambda b, s, g, p=0.0: c.append((b, s, g, p))
    small = lambda b, p=0.0: add(b, whoosh(0.22, bright=0.6), -24, p)            # he turns / gestures
    # ---- hook: frame-0 hit while the cards spring from hand to hand (springs start at 0.5 / 1.5 / 2.5)
    add(0, hit(), HIT_DB, 0.0)
    add(0, riffle(0.22, 12), -18, 0.15)                                           # the spring already in the air
    for b in (0.5, 1.5, 2.5):
        add(b, riffle(0.42), -15, 0.15)
    add(4.0, tap_deck(), -15, 0.1)                                                # deck squared
    # reveal 1 (4.5): the two estimate cards rise; small stacks 66 % > big 51 %
    add(4.5, whoosh(0.38), -13, 0.0)
    add(4.5, pop(330, 980), -16, -0.55)
    add(4.5, pop(420, 1250), -14, 0.55)
    add(5.0, blip(1500), -20, 0.55)                                               # the numbers have counted up
    small(5.0, 0.4)                                                               # opens his hand to the small stacks
    # reveal 2 (8.5): both cards turn over: big 65 %, small 34 %
    add(8.5, whoosh(0.42, bright=1.2), -12, 0.0)
    add(8.5, card_flip(), -11, 0.0)
    add(8.6, drop(0.45), -14, 0.55)
    add(9.0, pop(420, 1300), -14, -0.55)
    small(9.5, -0.2)                                                              # turns to the big deck
    add(10.5, bell(1568), -8, -0.6)                                               # ✓ 赢了
    add(10.55, sparkle(), -21, -0.6)
    add(11.5, pop(360, 1050), -16, 0.0)                                           # 63 of 70
    add(13.0, blip(1200), -22, 0.0)                                               # source
    small(14.5, 0.2)
    add(16.5, whoosh(0.5, up=False), -19, 0.0)                                    # line 2 starts to turn over
    add(17.0, card_flip(), -14, 0.0)                                              # line 2 turns over: the answer
    add(17.0, whoosh(0.3), -18, 0.0)
    for i in range(10):
        add(17.25 + i * 0.25, type_click(), -32, 0.0)
    # ---- 一大叠 (17-32): the four small stacks slide over and become one deck, a spring, ① ② ③, the evidence card
    for i, b in enumerate((17.5, 18, 18.5, 19)):
        add(b, card_slide(0.36), -17, 0.6 - 0.12 * i)
        add(b + 1, stack(200 + 30 * i), -14, 0.25)
    add(20.5, sparkle(0.45, 6), -22, 0.2)                                         # one big deck (turns yellow)
    add(20.5, riffle(0.42), -15, 0.2)
    small(21.5, -0.2)
    for i, b in enumerate((22, 23.5, 25)):
        add(b, deal_snap(), -16, -0.3)
        add(b + 1, pop(380 + 60 * i, 1150 + 120 * i), -13, -0.55)
    small(26.0, 0.2)
    add(26.5, whoosh(0.25), -21, 0.5)                                             # evidence card
    add(26.5, pop(340, 1000), -16, 0.5)
    add(27.0, spin(0.7, 20), -23, 0.5)                                            # 42 of 58 light up
    add(28.5, pop(420, 1250), -14, 0.5)
    add(29.0, blip(1200), -22, 0.5)
    for b in (30.5, 31.5, 32.5):
        add(b, step_snd(), -26, -0.2)                                             # walks behind the table
    add(31.0, whoosh(0.3), -22, -0.5)                                             # ① flies to the header
    # ---- ① 怎么叠 (32-64): deals the whole deck, the same card comes back after 19 others
    add(32.0, whoosh(0.4), -14, 0.0)                                              # cut to ①
    add(32.0, card_flip(), -18, -0.7)
    for i in range(12):
        add(33 + i * 0.25, type_click(), -33, -0.3)
    for i in range(21):
        add(34 + 0.5 * i, deal_snap(), -21 if 0 < i < 20 else -16, -0.3 + 0.9 * i / 20)
    add(35.0, pop(420, 1250), -15, -0.3)                                          # the marked card lands first ...
    add(45.0, chime(1318.5), -12, 0.6)                                            # ... and comes back after 19 others
    add(45.5, riser(0.45), -19, 0.2)                                              # the hop arrow
    add(46.5, pop(380, 1150), -15, 0.1)
    add(48.0, whoosh(0.3), -20, 0.2)                                              # row B: four small stacks
    add(48.0, spin(0.5, 16), -24, 0.2)
    for k in range(3):
        add(48.5 + 0.5 * k, blip(1300 + 200 * k), -22, -0.2 + 0.25 * k)
    add(50.0, pop(330, 980), -16, -0.4)
    add(51.0, blip(1100), -20, 0.3)                                               # 遍数、时间都一样
    add(52.0, pop(420, 1250), -13, 0.0)                                           # 49 %
    add(52.5, pop(330, 950), -16, 0.5)                                            # 36 %
    add(53.5, bell(1568), -8, 0.1)
    add(53.55, sparkle(), -22, 0.1)
    small(54.0, -0.2)                                                             # points
    add(54.5, blip(1200), -22, 0.3)                                               # source
    add(60.0, card_slide(0.6), -14, 0.2)                                          # the cards slide back to him
    add(60.0, whoosh(0.4, up=False), -21, 0.2)
    add(61.5, tap_deck(), -16, -0.5)
    # ---- ② 怎么排 (64-96): the same deck over four days (twice a day) vs a new small stack each day (8 times)
    add(64.0, whoosh(0.4), -14, 0.0)                                              # cut to ②
    add(64.0, card_flip(), -18, -0.7)
    for i in range(12):
        add(65 + i * 0.25, type_click(), -33, -0.3)
    add(65.0, pop(320, 950), -17, 0.5)                                            # the four small stacks
    add(65.5, pop(380, 1100), -16, -0.1)                                          # the day stand
    for k, d in enumerate((66, 70, 74, 78)):
        if k:
            add(d, card_flip(), -15, -0.1)                                        # 第 2 / 3 / 4 天
        add(d, stack(230 + 20 * k), -18, 0.3 + 0.12 * k)                          # today's small stack lifts
        add(d + 0.5, riffle(0.42), -16, -0.5)                                     # big deck, pass 1
        add(d + 2.0, riffle(0.42), -16, -0.5)                                     # big deck, pass 2
        for j in range(8):
            add(d + 0.5 * j, tick(2500 + 60 * j), -25, 0.3 + 0.12 * k)            # small stack: 8 passes today
    add(82.0, card_flip(), -14, -0.1)                                             # 第 5 天考试
    add(82.0, whoosh(0.3), -18, 0.0)
    add(83.0, pop(420, 1250), -13, -0.4)                                          # 54 %
    add(84.0, pop(330, 950), -16, 0.4)                                            # 21 %
    add(85.0, bell(1568), -8, -0.3)
    add(85.05, sparkle(), -22, -0.3)
    add(86.5, bonk(), -15, 0.6)                                                   # crammed the day before: 34 %
    add(88.0, blip(1200), -22, 0.0)                                               # source
    small(90.0, -0.2)                                                             # points
    add(95.5, whoosh(0.4, up=False), -21, 0.2)
    # ---- ③ 怎么翻 (96-128): says the answer, turns the card, puts it back under the deck; dropping cards loses
    add(96.0, whoosh(0.4), -14, 0.0)                                              # cut to ③
    add(96.0, card_flip(), -18, -0.7)
    for i in range(12):
        add(97 + i * 0.25, type_click(), -33, -0.3)
    for c3 in ((97.5, 100, 101.5, 103.5, (('i', 'b'), ('i', 't'), ('a', 't'))), (106, 107, 108, 109.5, (('i', 'k'),))):
        draw, say, flip, back, syl = c3
        add(draw, deal_snap(), -17, -0.2)                                         # draws the top card
        for j, (v, on) in enumerate(syl):
            add(say + 0.25 * j, voice(v, 132 - 6 * j, 0.15 if len(syl) > 1 else 0.24, on), VOX_DB, -0.3)
        add(flip, card_flip(), -12, -0.1)
        add(flip + 0.5, bell(1568 if draw < 100 else 1760), -9, -0.1)            # ✓ he had it right
        add(flip + 0.55, sparkle(0.45, 6), -23, -0.1)
        add(back, card_slide(0.3), -17, -0.4)                                     # back under the deck
        add(back + 1, tap_deck(), -17, -0.4)
    add(104.5, pop(360, 1050), -16, -0.2)                                         # 答对了也放回叠底
    add(112.0, pop(320, 950), -16, 0.4)                                           # tray + kept deck
    add(112.5, card_slide(0.36), -18, 0.3)                                        # a card dropped into the tray
    add(113.5, warn_thud(), -14, 0.2)                                             # ✗
    add(114.5, pop(300, 820), -17, 0.2)                                           # 21 %
    add(115.5, pop(420, 1250), -13, 0.6)                                          # 44 %
    add(116.5, bell(1568), -8, 0.6)
    add(116.55, sparkle(), -22, 0.6)
    add(117.5, blip(1200), -22, 0.3)                                              # source
    small(119.0, -0.2)                                                            # points
    add(126.0, tap_deck(), -17, -0.5)
    # ---- 照着做 (128-160): three cards dealt face up while he acts each one; fans the deck; ends on the last bar
    add(128.0, whoosh(0.4), -14, 0.0)                                             # cut to 照着做
    for i in range(10):
        add(129 + i * 0.25, type_click(), -33, -0.3)
    for i, b in enumerate((130, 134, 138)):
        add(b - 0.5, deal_snap(), -15, -0.2 + 0.3 * i)
        add(b, pop(380 + 50 * i, 1100 + 120 * i), -13, -0.1 + 0.3 * i)
    add(131.0, tap_deck(), -15, -0.5)                                             # 一大叠: squares the deck
    add(133.5, blip(1500), -23, 0.1)                                              # arrow
    add(134.5, riffle(0.42), -15, -0.5)                                           # 分几天: one pass
    add(137.5, blip(1700), -23, 0.3)                                              # arrow
    add(138.5, deal_snap(), -19, -0.4)                                            # lifts a card
    add(139.5, card_flip(), -13, -0.4)                                            # 说出答案再翻
    add(140.0, bell(1760), -10, -0.4)
    add(141.5, card_slide(0.3), -18, -0.5)
    add(142.0, warn_thud(), -13, 0.3)                                             # 背的时候更吃力
    add(144.0, blip(1100), -21, 0.3)                                              # 仅供参考
    add(147.5, riffle(0.32, 14), -16, -0.4)                                       # fans the deck
    add(150.0, whoosh(0.22, bright=0.7), -21, -0.3)                               # raises the fan at the summary
    add(151.0, chime(1318.5), -11, -0.3)
    add(151.05, sparkle(0.6, 8), -21, -0.3)
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
