"""Score for the 12 s opening: real piano + string samples, plus restrained sound effects.

Structure (A minor, ~72 bpm):
  0.0-2.0  two soft piano notes over a low string drone
  2.0      the break; real collision times from the physics
  2.0-7.9  piano arpeggio Am(add9) -> Fmaj7 -> C/E -> G, strings swell as the runs diverge
  7.9-8.9  'tape rewind': the last seconds played backwards, speeding up
  8.9-9.7  near silence, a high string harmonic creeps in
  9.75     0.001° - everything stops; one ball click, one deep piano note
  10.7     angle spread: two high piano notes, strings return softly, fade
"""
import wave

import numpy as np
from scipy import signal

import opening as op
import samples

SR = samples.SR
DUR = op.END
N = int(DUR * SR)
rng = np.random.default_rng(3)


def tt(d):
    return np.arange(int(d * SR)) / SR


def place(buf, t0, x, gain=1.0):
    """buf: (N,2); x: mono or (n,2)."""
    i = int(round(t0 * SR))
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    if i < 0:
        x, i = x[-i:], 0
    x = x[: max(0, len(buf) - i)]
    buf[i:i + len(x)] += gain * x


def pan(x, p):
    """p in [-1, 1]; constant power."""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)


def repitch(x, ratio):
    if abs(ratio - 1) < 1e-6:
        return x
    n = int(len(x) / ratio)
    return np.interp(np.arange(n) * ratio, np.arange(len(x)), x)


def lp(x, f):
    return signal.sosfilt(signal.butter(2, f, 'lowpass', fs=SR, output='sos'), x)


def hp(x, f):
    return signal.sosfilt(signal.butter(2, f, 'highpass', fs=SR, output='sos'), x)


# ============================================================== instruments
PIANO = samples.piano()
STR = samples.strings()
CELLO = samples.cello()


def piano(m, vel=0.6, length=None, release=0.6):
    k, x = PIANO.nearest(m)
    x = repitch(x, 2 ** ((m - k) / 12))
    x = x / (np.max(np.abs(x)) + 1e-9)
    # soft notes are darker
    x = lp(x, 900 + 7000 * vel ** 1.6)
    if length is not None:
        n = min(len(x), int((length + release) * SR))
        x = x[:n].copy()
        r0 = int(length * SR)
        if r0 < n:
            x[r0:] *= np.linspace(1, 0, n - r0) ** 2
    return x * vel


def sustain(inst, m, d, attack=0.8, release=1.2, seed=0):
    """Arbitrarily long sustained note from a ~3 s sample (overlap-added grains)."""
    k, x = inst.nearest(m)
    x = repitch(x, 2 ** ((m - k) / 12))
    x = x / (np.max(np.abs(x)) + 1e-9)
    n = int(d * SR)
    out = np.zeros(n + SR)
    g = int(1.0 * SR)
    hop = g // 2
    win = np.sin(np.pi * np.arange(g) / g)        # equal-power: sin^2 + cos^2 = 1 at every overlap
    lo, hi = int(0.45 * SR), max(int(0.45 * SR) + 1, len(x) - g - int(0.2 * SR))
    r = np.random.default_rng(seed)
    out[:min(len(x), int(0.6 * SR))] += x[:int(0.6 * SR)] * np.linspace(1, 0, min(len(x), int(0.6 * SR)))
    ref = np.sqrt(np.mean(x[lo:hi + g] ** 2)) + 1e-9
    for s in range(0, n, hop):
        o = r.integers(lo, hi)
        grain = x[o:o + g]
        grain = grain * (ref / (np.sqrt(np.mean(grain ** 2)) + 1e-9)) ** 0.8   # even out bow swells
        out[s:s + g] += grain * win
    out = out[:n]
    t = np.arange(n) / SR
    env = np.minimum(1, t / attack) * np.clip((d - t) / release, 0, 1)
    return out * env ** 1.5


def chord(inst, notes, d, attack=1.0, release=1.5, spread=0.6, seed=0):
    out = np.zeros((int(d * SR), 2))
    for j, m in enumerate(notes):
        p = (j / max(1, len(notes) - 1) - 0.5) * 2 * spread
        out += pan(sustain(inst, m, d, attack, release, seed + j), p)
    return out / len(notes) ** 0.5


# ============================================================== sfx (quiet, realistic)
def click(strength, bright=1.0):
    d = 0.06
    t = tt(d)
    f0 = rng.uniform(2700, 3300)
    x = (np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * f0 * 1.48 * t)) * np.exp(-t * 170)
    x += 0.4 * hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 420) * bright
    return x * min(1.0, 0.2 + strength * 0.3)


def cue_strike():
    t = tt(0.2)
    x = (np.sin(2 * np.pi * 1850 * t) + 0.6 * np.sin(2 * np.pi * 2750 * t)) * np.exp(-t * 85)
    x += 0.7 * np.sin(2 * np.pi * 230 * t) * np.exp(-t * 35)
    x += 0.4 * hp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 260)
    return x


def cushion(strength):
    t = tt(0.1)
    return (np.sin(2 * np.pi * 140 * t) * np.exp(-t * 50) +
            0.3 * lp(rng.standard_normal(len(t)), 800) * np.exp(-t * 70)) * min(1, 0.15 + strength * 0.2)


def pocket():
    t = tt(0.4)
    x = np.sin(2 * np.pi * (100 + 50 * np.exp(-t * 20)) * t) * np.exp(-t * 11)
    for k in range(3):
        cl = click(0.5)
        o = int((0.07 + 0.06 * k) * SR)
        x[o:o + len(cl)] += 0.35 * cl * 0.6 ** k
    return x * 0.6


# ============================================================== reverb
def reverb(x, seconds=2.6, mix=0.32, predelay=0.02):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 6.9 / seconds)
        ir = lp(ir, 5500)
        ir[: int(predelay * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, ch] = signal.fftconvolve(x[:, ch], ir)[: len(x)]
    return x * (1 - mix) + out * mix * 2.2


# ============================================================== build
def video_time_of_sim(t_sim):
    return op.T_STRIKE + t_sim


def build_sfx(scene):
    s = np.zeros((N, 2))
    place(s, op.T_STRIKE - 0.004, pan(cue_strike(), 0.0), 0.75)
    last = {}
    for k, run in enumerate(scene.runs):
        for (t, kind, strength) in run.events[1:]:
            tv = video_time_of_sim(t)
            if tv > op.T_REWIND[0] - 0.05:
                continue
            key = (k, kind)
            if tv - last.get(key, -1) < (0.015 if kind == 'ball' else 0.035):
                continue
            last[key] = tv
            p = -0.35 if k == 0 else 0.35          # first break slightly left, second slightly right
            g = 0.5 if k == 0 else 0.42
            if kind == 'ball':
                place(s, tv, pan(click(strength), p), g)
            elif kind == 'cushion':
                place(s, tv, pan(cushion(strength), p), g)
            elif kind == 'pocket':
                place(s, tv, pan(pocket(), p), g)
    # the single click at 0.001°
    place(s, op.T_NUMBER, pan(click(1.2, bright=0.6), 0), 0.8)
    return s


def build_music():
    m = np.zeros((N, 2))
    A2, E3, A3, C4, E4, A4, B4, E5 = 45, 52, 57, 60, 64, 69, 71, 76
    # ---- 0-2 s: drone + two notes
    place(m, 0.0, chord(CELLO, [A2, E3], 2.6, attack=1.2, release=0.8, spread=0.3), 0.32)
    place(m, 0.35, pan(piano(E5, 0.32), 0.15), 1.0)
    place(m, 1.15, pan(piano(A4, 0.28), -0.1), 1.0)
    # ---- 2.0-7.9: arpeggio over a progression, strings swelling
    beat = 60 / 72
    eighth = beat / 2
    prog = [  # (bass, arpeggio)
        (33, [57, 64, 71, 72]),        # Am(add9)
        (29, [53, 57, 64, 72]),        # Fmaj7
        (28, [55, 60, 64, 67]),        # C/E
        (31, [55, 59, 62, 71]),        # G
    ]
    bar = 4 * beat
    t0 = op.T_STRIKE
    for b, (bass, arp) in enumerate(prog * 2):
        tb = t0 + b * bar * 0.5          # two chords per bar - keeps it moving
        if tb > op.T_REWIND[0] - 0.2:
            break
        place(m, tb, pan(piano(bass + 12, 0.42, length=bar * 0.5, release=0.8), -0.25), 1.0)
        for j in range(4):
            tn = tb + j * eighth
            if tn < op.T_REWIND[0] - 0.1:
                vel = 0.26 + 0.05 * (j == 0) + 0.12 * (tn - t0) / (op.T_REWIND[0] - t0)
                place(m, tn, pan(piano(arp[j] + 12 * (j == 3 and b % 2 == 1), vel), 0.1 + 0.08 * j), 1.0)
    swell = op.T_REWIND[0] - t0 + 0.4
    strings = chord(STR, [A3, C4, E4, A4], swell, attack=swell * 0.85, release=0.35, spread=0.8, seed=10)
    place(m, t0, strings, 0.55)
    place(m, t0, chord(CELLO, [A2, E3], swell, attack=2.5, release=0.35, seed=20), 0.35)
    # ---- 7.9-8.9: rewind - reverse the last ~4 s, accelerating
    i0, i1 = int((op.T_REWIND[0] - 4.0) * SR), int(op.T_REWIND[0] * SR)
    seg = m[i0:i1][::-1]
    n_out = int((op.T_REWIND[1] - op.T_REWIND[0]) * SR)
    u = np.linspace(0, 1, n_out)
    pos = (u ** 1.6) * (len(seg) - 1)                     # speeds up, like a tape spinning back
    rew = np.stack([np.interp(pos, np.arange(len(seg)), seg[:, ch]) for ch in range(2)], 1)
    rew = np.stack([lp(rew[:, ch], 3500) for ch in range(2)], 1)
    rew *= (np.sin(np.pi * u) ** 0.7)[:, None]
    m[i1:] = 0                                            # hard stop of the forward music
    place(m, op.T_REWIND[0], rew, 0.55)
    # ---- 8.9-9.7: high harmonic
    place(m, 8.85, chord(STR, [E5 + 12], 0.9, attack=0.7, release=0.15, spread=0), 0.18)
    # ---- 9.75: silence, then one deep note
    place(m, op.T_NUMBER + 0.05, pan(piano(A2 - 12, 0.5), -0.1), 1.0)
    place(m, op.T_NUMBER + 0.05, pan(piano(A2, 0.35), 0.1), 1.0)
    # ---- 10.7: spread
    place(m, op.T_SPREAD[0] + 0.05, pan(piano(E5 + 12, 0.3), 0.35), 1.0)
    place(m, op.T_SPREAD[0] + 0.55, pan(piano(B4 + 12, 0.26), 0.45), 1.0)
    place(m, op.T_SPREAD[0], chord(STR, [A3, E4, B4], op.END - op.T_SPREAD[0], attack=1.0, release=1.0,
                                   spread=0.9, seed=30), 0.4)
    return m


def master(x, target_peak=0.89):
    x = x - np.mean(x, axis=0)
    peak = np.max(np.abs(x)) + 1e-9
    x = np.tanh(x / peak * 1.1) / np.tanh(1.1)
    fade = np.ones(len(x))
    k = int((DUR - 0.5) * SR)
    fade[k:] = np.linspace(1, 0, len(x) - k)
    return x * fade[:, None] * target_peak


def write_wav(path, x):
    data = (np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def build(scene, path, with_music=True):
    sfx = build_sfx(scene)
    mix = sfx * 0.9
    if with_music:
        mus = build_music()
        mix = mix + mus / (np.max(np.abs(mus)) + 1e-9) * 0.8
    mix = reverb(mix, seconds=2.8, mix=0.3)
    write_wav(path, master(mix))
    print('audio written', path, flush=True)
    return path
