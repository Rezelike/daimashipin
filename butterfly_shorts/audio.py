"""Synthesise original background music + sound effects for Part 1.

Everything is generated from scratch with numpy (no samples, no copyright issues).
Ball-collision sounds are placed at the exact times the physics engine reports.

Outputs build/part1_full.wav (music + sfx) and build/part1_sfx.wav (sfx only).
"""
import os
import wave

import numpy as np
from scipy import signal

import scenes as sc

SR = 44100
DUR = sc.D_END
N = int(DUR * SR)
ROOT = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)


def tt(d):
    return np.arange(int(d * SR)) / SR


def place(buf, t0, x, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    if i < 0:
        x = x[-i:]
        i = 0
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += gain * x


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos')
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'lowpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, 'highpass', fs=SR, output='sos'), x)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# ============================================================== instruments
def pluck(freq, d=0.6, bright=1.0):
    t = tt(d)
    env = np.exp(-t * 5.5) * np.minimum(1, t / 0.004)
    x = (np.sin(2 * np.pi * freq * t) + 0.45 * bright * np.sin(4 * np.pi * freq * t) * np.exp(-t * 9)
         + 0.2 * bright * np.sin(6 * np.pi * freq * t) * np.exp(-t * 14))
    return x * env


def marimba(freq, d=0.5):
    t = tt(d)
    env = np.exp(-t * 7) * np.minimum(1, t / 0.002)
    return (np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * freq * 3.99 * t) * np.exp(-t * 25)) * env


def pad(freqs, d, attack=0.6, release=0.8):
    t = tt(d)
    x = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.12):
            ff = f * 2 ** (det / 12)
            for h in range(1, 6):
                x += np.sin(2 * np.pi * ff * h * t + rng.uniform(0, 6.28)) / h ** 1.6
    x = lp(x, 1800)
    env = np.minimum(1, t / attack) * np.minimum(1, (d - t) / release).clip(0)
    return x * env / (len(freqs) * 4)


def bass(freq, d=0.5):
    t = tt(d)
    env = np.exp(-t * 3.5) * np.minimum(1, t / 0.006)
    return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * env


def kick(d=0.35):
    t = tt(d)
    f = 48 + 90 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat(d=0.06):
    t = tt(d)
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * 70)


def clap(d=0.2):
    t = tt(d)
    return bp(rng.standard_normal(len(t)), 900, 3500) * np.exp(-t * 22)


def shaker(d=0.08):
    t = tt(d)
    return bp(rng.standard_normal(len(t)), 4000, 9000) * np.sin(np.pi * t / d) ** 2


# ============================================================== sfx
def ball_click(strength):
    d = 0.05
    t = tt(d)
    f0 = rng.uniform(2600, 3400)
    x = (np.sin(2 * np.pi * f0 * t) + 0.6 * np.sin(2 * np.pi * f0 * 1.52 * t)) * np.exp(-t * 160)
    x += 0.35 * hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 400)
    return x * min(1.0, 0.25 + strength * 0.35)


def cushion_thud(strength):
    t = tt(0.12)
    x = np.sin(2 * np.pi * 150 * t) * np.exp(-t * 45) + 0.4 * lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 60)
    return x * min(1.0, 0.2 + strength * 0.25)


def pocket_drop():
    t = tt(0.45)
    x = np.sin(2 * np.pi * (110 + 60 * np.exp(-t * 20)) * t) * np.exp(-t * 12)
    for k in range(3):  # rattle in the pocket
        cl = ball_click(0.6)
        off = int((0.08 + 0.07 * k) * SR)
        x[off:off + len(cl)] += 0.3 * cl * (0.7 ** k)
    return x


def cue_hit():
    t = tt(0.15)
    x = (np.sin(2 * np.pi * 1700 * t) + 0.7 * np.sin(2 * np.pi * 2600 * t)) * np.exp(-t * 90)
    x += 0.8 * np.sin(2 * np.pi * 220 * t) * np.exp(-t * 40)
    x += 0.5 * bp(rng.standard_normal(len(t)), 1500, 8000) * np.exp(-t * 200)
    return x


def whoosh(d=0.45, up=True):
    t = tt(d)
    n = rng.standard_normal(len(t))
    lo = np.linspace(300, 2500, len(t)) if up else np.linspace(2500, 300, len(t))
    out = np.zeros_like(n)
    for k in range(0, len(t), 2205):  # piecewise band-pass sweep
        seg = slice(k, k + 2205)
        out[seg] = bp(n[seg], lo[k], lo[k] * 2.2)
    return out * np.sin(np.pi * t / d) ** 2


def pop():
    t = tt(0.12)
    f = 380 + 700 * (1 - np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)


def blip(freq=1200):
    t = tt(0.08)
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 55)


def bell(freq, d=1.6):
    t = tt(d)
    x = np.zeros_like(t)
    for ratio, amp, dec in ((1, 1, 2.2), (2.76, 0.4, 4), (5.4, 0.2, 7), (8.93, 0.1, 10)):
        x += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t * dec)
    return x * np.minimum(1, t / 0.002)


def riser(d):
    t = tt(d)
    f = 200 * 2 ** (3 * t / d)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    nz = hp(rng.standard_normal(len(t)), 2000) * 0.5
    return (tone + nz) * (t / d) ** 2


def impact():
    return kick(0.6) * 1.2 + 0.5 * lp(rng.standard_normal(int(0.6 * SR)), 400) * np.exp(-tt(0.6) * 8)


# ============================================================== build
def build_sfx():
    s = np.zeros(N)
    A, B, C = sc.SceneA(), sc.SceneB(), sc.SceneC()
    D = sc.SceneD()
    # caption pops
    for scene, gain in ((A, 0.25), (B, 0.25), (C, 0.0), (D, 0.22)):
        for cap in scene.caps:
            place(s, cap.t_in, blip(1100), gain)
    # cue: draw-back swish + strike
    place(s, 1.3, whoosh(0.5, up=False), 0.12)
    place(s, sc.T_STRIKE - 0.005, cue_hit(), 0.9)
    # physics events from BOTH tables, merged & capped
    last = {}
    for sim in A.sims:
        for (t, kind, strength) in sim.events[1:]:
            tg = sc.T_STRIKE + t
            if tg > sc.A_END:
                continue
            key = kind
            if tg - last.get(key, -1) < (0.012 if kind == 'ball' else 0.03):
                continue
            last[key] = tg
            if kind == 'ball':
                place(s, tg, ball_click(strength), 0.55)
            elif kind == 'cushion':
                place(s, tg, cushion_thud(strength), 0.45)
            elif kind == 'pocket':
                place(s, tg, pocket_drop(), 0.5)
    # question mark sting
    place(s, 4.2, pop(), 0.35)
    # transitions
    place(s, sc.B_START - 0.15, whoosh(0.45), 0.35)
    place(s, 8.6, impact(), 0.55)
    place(s, 8.6, bell(midi(88), 1.0), 0.18)
    place(s, sc.C_START - 0.1, whoosh(0.4), 0.3)
    for k, n in enumerate((84, 88, 91, 96)):
        place(s, 11.25 + 0.07 * k, bell(midi(n)), 0.16)
    place(s, sc.D_START - 0.1, whoosh(0.45), 0.3)
    place(s, 15.0, pop(), 0.2)                     # pendulums merge
    place(s, sc.P_RELEASE, blip(700), 0.35)        # release
    place(s, D.t_split - 1.6, riser(1.6), 0.22)
    place(s, D.t_split, impact(), 0.5)
    place(s, D.t_split + 2.1, pop(), 0.3)
    return s


CHORDS = [  # C  Am  F  G  (bright I-vi-IV-V)
    (48, [60, 64, 67, 72]), (45, [57, 60, 64, 69]), (41, [53, 57, 60, 65]), (43, [55, 59, 62, 67]),
]
BPM = 108
BEAT = 60 / BPM


def build_music(t_split):
    m = np.zeros(N)
    bar = 4 * BEAT
    # 0-2 s : suspense - soft pad + ticking
    place(m, 0.0, pad([midi(60), midi(67)], 2.3, attack=0.4, release=0.4), 0.5)
    for k in range(8):
        place(m, k * BEAT / 2, marimba(midi(79), 0.15), 0.08)
    # helper to play a groove section
    def groove(t0, t1, level, drums=True, arp=True, bass_on=True, pad_on=True, density=2):
        nbars = int(np.ceil((t1 - t0) / bar))
        for b in range(nbars):
            root, notes = CHORDS[b % 4]
            tb = t0 + b * bar
            if pad_on:
                place(m, tb, pad([midi(n) for n in notes[:3]], bar + 0.3, attack=0.25, release=0.3), 0.45 * level)
            for beat in range(4):
                tbeat = tb + beat * BEAT
                if tbeat >= t1:
                    break
                if bass_on and beat in (0, 2):
                    place(m, tbeat, bass(midi(root), BEAT * 1.8), 0.32 * level)
                if drums:
                    if beat in (0, 2):
                        place(m, tbeat, kick(), 0.45 * level)
                    if beat in (1, 3):
                        place(m, tbeat, clap(), 0.16 * level)
                    for h in range(2):
                        place(m, tbeat + h * BEAT / 2, hat(), 0.07 * level)
                if arp:
                    for k in range(density):
                        tn = tbeat + k * BEAT / density
                        if tn < t1:
                            n = notes[(beat * density + k) % 4] + 12
                            place(m, tn, pluck(midi(n), 0.5), 0.12 * level)
    # 2-8 s : the break - light groove (no kick, so ball clicks stay audible)
    groove(sc.T_STRIKE, sc.A_END - 0.3, 0.75, drums=False, density=2)
    for k in range(int((sc.A_END - 0.3 - sc.T_STRIKE) / (BEAT / 2))):
        place(m, sc.T_STRIKE + k * BEAT / 2, shaker(), 0.05)
    # 8-11 s : reveal - only a held pad (space for the "0.001°" moment)
    place(m, 8.6, pad([midi(57), midi(64), midi(71)], 2.8, attack=0.2, release=0.9), 0.55)
    # 11.2-14 s : title - full groove burst
    groove(11.25, sc.C_END, 1.0, drums=True, density=4)
    # 14-split : pendulum calm - gentle arp only
    groove(sc.D_START + 0.2, t_split, 0.7, drums=False, bass_on=False, density=2)
    # split -> end : full groove, fade out at the end
    groove(t_split, sc.D_END, 1.0, drums=True, density=4)
    fade = np.ones(N)
    k0 = int((sc.D_END - 1.2) * SR)
    fade[k0:] = np.linspace(1, 0, N - k0) ** 1.5
    return m * fade


def master(x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 1.25
    x = np.tanh(x) / np.tanh(1.25)
    return x * 0.89  # ~ -1 dBFS


def write_wav(path, x):
    st = np.stack([x, x], 1)
    data = (np.clip(st, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def build(out_dir):
    """Write the two soundtracks into out_dir and return (full_wav, sfx_wav)."""
    sfx = build_sfx()
    music = build_music(sc.SceneD().t_split)
    sfx_n = sfx / np.max(np.abs(sfx))
    music_n = music / np.max(np.abs(music))
    full, only_sfx = os.path.join(out_dir, 'part1_full.wav'), os.path.join(out_dir, 'part1_sfx.wav')
    write_wav(full, master(0.62 * music_n + 0.8 * sfx_n))
    write_wav(only_sfx, master(sfx_n) * 0.85)
    print('audio written')
    return full, only_sfx


if __name__ == '__main__':
    os.makedirs(f'{ROOT}/build', exist_ok=True)
    build(f'{ROOT}/build')
