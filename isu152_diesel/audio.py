"""Sound for the ISU-152 diesel video. No music.

- Engine: one knock per cylinder firing, at the exact time it fires on screen (mech.bang_events). In slow motion
  that is one deep bang per beat; every x2 doubles the rate, and at the real 2000 rpm the 200 bangs a second merge
  into the engine roar. Left bank panned left, right bank right.
- In the four-stroke close-up (bars 4-6) only cylinder L1 is loud, with a sound per stroke: suck, squeeze (rise),
  bang, blow.
- Effects from engine/sfx.py on the beat: a hit on frame 0, whooshes peaking on the cuts, pops for captions,
  a chime when the real speed lands.
Levels are set by measured loudness (ITU-R BS.1770), then the mix goes to -18 LUFS integrated, true peak <= -1 dBTP.
"""
import numpy as np
import soundfile as sf
from scipy import signal

import mech as M
from engine import sfx as FX

SR = M.SR
B, BAR = M.BEAT, M.BAR
TARGET_LUFS = -18.0


def at(bar, beat):
    return bar * BAR + beat * B


# ----------------------------------------------------------------------------- loudness
def lufs_integrated(x):
    x = x if x.ndim == 2 else x[:, None]
    k = signal.lfilter(*FX._K2, signal.lfilter(*FX._K1, x, axis=0), axis=0)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    ms = np.array([np.mean(k[i:i + blk] ** 2, axis=0).sum() for i in range(0, len(k) - blk + 1, hop)])
    lv = -0.691 + 10 * np.log10(ms + 1e-12)
    g = ms[lv > -70]
    if not len(g):
        return -70.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    return float(-0.691 + 10 * np.log10(ms[(lv > -70) & (lv > rel)].mean()))


def _level(y, lufs):
    """scale a mono effect to a momentary loudness, soft-limited like engine/sfx.py does"""
    y = y / (np.max(np.abs(y)) + 1e-9)
    for _ in range(2):
        y = y * 10 ** ((lufs - FX.momentary_max(y)) / 20)
        y = FX.soft_limit(y, -2.5)
    return y


# ----------------------------------------------------------------------------- engine knocks
def _knock(rng, f):
    """one combustion knock for a firing rate of f bangs per second (shorter and lighter as f rises)"""
    dur = float(np.clip(1.25 / f, 0.018, 0.5))
    t = np.arange(int(dur * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(50 + 80 * np.exp(-t / 0.02)) / SR) * np.exp(-t / min(0.11, 0.42 / f))
    knock = FX._filt(rng.standard_normal(len(t)), "band", (450, 3400)) * np.exp(-t / min(0.035, 0.11 / f))
    click = FX._filt(rng.standard_normal(len(t)), "high", 2500) * np.exp(-t / 0.0011)
    y = body + 0.8 * knock / (np.abs(knock).max() + 1e-9) + 0.3 * click / (np.abs(click).max() + 1e-9)
    if f < 6:                                    # slow motion: a deep boom and a crackling tail
        boom = np.sin(2 * np.pi * np.cumsum(34 + 46 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.17)
        tail = FX._filt(rng.standard_normal(len(t)), "low", 1100) * np.exp(-t / 0.13)
        tail *= 0.55 + 0.45 * np.sin(2 * np.pi * 27 * t)
        y = y + 1.3 * boom + 0.55 * tail / (np.abs(tail).max() + 1e-9)
    y *= np.clip(t / 0.0006, 0, 1) * np.clip((dur - t) / 0.004, 0, 1)
    return y / (np.abs(y).max() + 1e-9)


def _rate_target(f):
    """loudness (LUFS, momentary) of a steady knock train at f bangs/s"""
    pts = [(2.13, -16.5), (4.27, -17.5), (8.53, -18.5), (17.1, -19.5), (34.1, -20.0), (68.3, -20.0), (200.0, -19.0)]
    lf = np.log([p[0] for p in pts])
    return float(np.interp(np.log(max(f, 2.13)), lf, [p[1] for p in pts]))


def _bucket(f):
    return float(2 ** (round(np.log2(max(f, 1.0)) * 2) / 2))


def engine_layer(n, rng):
    ev = M.bang_events(0.0, M.DUR)
    banks, gains = {}, {}
    for fb in sorted({_bucket(M.omega(t) / 60.0) for t, _ in ev}):
        variants = [_knock(rng, fb) for _ in range(6)]
        train = np.zeros(int(2.0 * SR) + len(variants[0]))
        for i in range(int(2.0 * fb)):
            s = int(i / fb * SR)
            v = variants[i % 6]
            train[s:s + len(v)] += v[:len(train) - s]
        gains[fb] = 10 ** ((_rate_target(fb) - FX.momentary_max(train[: int(2.0 * SR)])) / 20)
        banks[fb] = variants
    out = np.zeros((n, 2))
    for j, (t, cyl) in enumerate(ev):
        bi, lb = M.bar_beat(t)
        f = M.omega(t) / 60.0
        fb = _bucket(f)
        g = gains[fb] * 10 ** ((rng.uniform(-1.2, 1.2)) / 20)
        outside = bi == 0 or bi == 13 or (bi == 1 and lb < 1) or (bi == 12 and lb >= 2)
        if outside:
            g *= 10 ** (-3.5 / 20)
        if 3 <= bi <= 5:                         # close-up: only L1 is loud
            g *= 10 ** ((6.0 if cyl == "L1" else -13.0) / 20)
        v = banks[fb][j % 6] * g
        pan = -0.35 if cyl[0] == "L" else 0.35
        th = (pan + 1) * np.pi / 4
        s = int(round(t * SR))
        e = min(n, s + len(v))
        out[s:e, 0] += v[:e - s] * min(1.0, np.sqrt(2) * np.cos(th))
        out[s:e, 1] += v[:e - s] * min(1.0, np.sqrt(2) * np.sin(th))
    return out, len(ev)


# ----------------------------------------------------------------------------- four-stroke close-up sounds
def _suck(rng, dur=1.3):
    nn = int(dur * SR)
    t = np.arange(nn) / SR
    y = FX._sweep(nn, rng, lambda tt: 500 + 1900 * np.clip(tt / dur, 0, 1) ** 0.8, 1.3)
    return y * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5 * np.clip(t / 0.01, 0, 1)


def _blow(rng, dur=1.1):
    t = np.arange(int(dur * SR)) / SR
    y = FX._filt(rng.standard_normal(len(t)), "low", 1800) * np.exp(-t / 0.28) * np.clip(t / 0.004, 0, 1)
    return y * (0.65 + 0.35 * np.sin(2 * np.pi * 34 * t))


def custom_layer(n, rng):
    out = np.zeros((n, 2))
    items = [(at(3, 0), _suck(rng), -22.0, 0.0), (at(3, 9), _blow(rng), -21.0, -0.2)]
    for t0, y, lv, pan in items:
        y = _level(y, lv)
        s = int(round(t0 * SR))
        e = min(n, s + len(y))
        th = (pan + 1) * np.pi / 4
        out[s:e, 0] += y[:e - s] * min(1.0, np.sqrt(2) * np.cos(th))
        out[s:e, 1] += y[:e - s] * min(1.0, np.sqrt(2) * np.sin(th))
    return out


# ----------------------------------------------------------------------------- engine/sfx.py effects
def cues():
    c = [(0.0, "hit", {}), (at(0, 2), "pop", {"gain": -2}),
         (at(1, 1), "whoosh", {}), (at(1, 1), "pop", {"gain": -4}), (at(1, 2), "pop", {"pitch": 0.84}),
         (at(2, 1), "pop", {}), (at(2, 2), "pop", {"pitch": 1.12}), (at(2, 3), "pop", {"pitch": 1.26}),
         (at(3, 0), "whoosh", {"gain": -2}),
         (at(3, 0), "tick", {}), (at(3, 3), "tick", {}), (at(3, 6), "tick", {}), (at(3, 9), "tick", {}),
         (at(3, 1), "pop", {}), (at(3, 3), "rise", {"dur": 3 * B, "gain": -1}), (at(3, 4), "error", {"gain": -3}),
         (at(3, 6), "hit", {"gain": -3}), (at(3, 7), "pop", {"pitch": 1.12}), (at(3, 10), "pop", {"pitch": 0.9}),
         (at(6, 0), "whoosh", {"gain": -2})]
    for i, bar in enumerate((6, 7, 8, 9, 10)):
        c.append((at(bar, 0), "pop_big", {"pitch": 1.0 + 0.12 * i, "gain": -2}))
    c += [(at(7, 1), "pop", {}), (at(8, 1), "pop", {}), (at(9, 1), "pop", {}), (at(9, 2), "pop", {"pitch": 1.12}),
          (at(10, 2), "rise", {"dur": 2 * B, "gain": 1}),
          (at(11, 0), "chime", {"gain": -2}), (at(11, 2), "pop_big", {"pitch": 1.2}),
          (at(12, 0), "pop", {}), (at(12, 2), "whoosh", {"gain": -1}),
          (at(13, 0), "pop", {}), (at(13, 3), "pop", {"pitch": 1.12})]
    return c


def fx_layer(n, rng, cue_list):
    out = np.zeros((n, 2))
    for t0, kind, o in sorted(cue_list, key=lambda q: q[0]):
        args = {k: v for k, v in o.items() if k in ("pitch", "dur")}
        r = FX.KINDS[kind](rng, **args)
        y, off = r if isinstance(r, tuple) else (r, 0.0)
        y = _level(y, FX.TARGET[kind] + o.get("gain", 0.0))
        th = (o.get("pan", 0.0) + 1) * np.pi / 4
        s = int(round((t0 - off) * SR))
        s0, e = max(0, s), min(n, s + len(y))
        if e <= s0:
            continue
        out[s0:e, 0] += y[s0 - s:e - s] * min(1.0, np.sqrt(2) * np.cos(th))
        out[s0:e, 1] += y[s0 - s:e - s] * min(1.0, np.sqrt(2) * np.sin(th))
    return out


def build(path, seed=152):
    rng = np.random.default_rng(seed)
    n = int(round(M.NF / M.FPS * SR))
    eng, nb = engine_layer(n, rng)
    cl = cues()
    mix = eng + custom_layer(n, rng) + fx_layer(n, rng, cl)
    b, a = signal.butter(2, 30 / (SR / 2), "high")
    mix = signal.lfilter(b, a, mix, axis=0)
    for _ in range(3):
        mix *= 10 ** ((TARGET_LUFS - lufs_integrated(mix)) / 20)
        mix = FX.soft_limit(mix, -1.6)
    tp = FX.true_peak_db(mix)
    if tp > -1.1:
        mix *= 10 ** ((-1.1 - tp) / 20)
    sf.write(path, mix.astype(np.float32), SR, subtype="PCM_24")
    st = dict(bangs=nb, effects=len(cl), lufs=round(lufs_integrated(mix), 1), true_peak=round(FX.true_peak_db(mix), 1))
    return cl, st


def bang_onsets(x):
    """measured on the final file: start of each slow-motion bang (bar 3 and bars 7-8, 1-4 bangs per beat, plus the
    L1 bang in the close-up) vs the beat grid"""
    hop = SR // 1000
    m = len(x) // hop
    e = np.sqrt(np.mean(x[: m * hop].reshape(m, hop) ** 2, axis=1) + 1e-12)
    le = 20 * np.log10(e)
    rise = np.maximum(0, np.diff(le, prepend=le[0]))
    exp = [t for t, c in M.bang_events(at(2, 0) - 0.001, at(3, 0) - 0.01)]
    exp += [t for t, c in M.bang_events(at(3, 0), at(6, 0)) if c == "L1"]
    exp += [t for t, c in M.bang_events(at(6, 0) + 0.05, at(8, 0) - 0.01)]
    offs = []
    for t0 in exp:
        i0, i1 = max(0, int((t0 - 0.012) * 1000)), int((t0 + 0.02) * 1000)
        if i1 <= i0 or i1 >= len(rise):
            continue
        k = i0 + int(np.argmax(rise[i0:i1]))
        if rise[k] > 3.0:
            offs.append(abs(k / 1000 - t0) * 1000)
    offs = np.array(offs) if offs else np.array([np.nan])
    return dict(n=len(exp), found=int(np.sum(~np.isnan(offs))), med=float(np.nanmedian(offs)),
                worst=float(np.nanmax(offs)))
