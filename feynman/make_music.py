"""Original soundtrack for the Feynman video: upbeat piano + violin, 136 BPM, A minor.

Rendered from real instrument recordings (VSCO-2 CE, CC0). The arrangement follows
timeline.SCENES bar-by-bar, so musical phrases change exactly where the video cuts.

    python fetch_assets.py && python make_music.py   ->  build/music.wav
"""
import glob, os, re, sys
import numpy as np
import soundfile as sf
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import BEAT, BAR, TOTAL_BARS, DURATION

HERE = os.path.dirname(os.path.abspath(__file__))
VSCO = os.path.join(HERE, ".assets", "vsco")
BUILD = os.path.join(HERE, "build")
SR = 44100
rng = np.random.default_rng(7)

# --------------------------------------------------------------------------- samples
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def nm(s):
    """'A4' -> 69, 'G#5' -> 80"""
    m = re.fullmatch(r"([A-G])(#|b)?(-?\d)", s)
    return 12 * (int(m.group(3)) + 1) + NOTE[m.group(1)] + {"#": 1, "b": -1, None: 0}[m.group(2)]


def load(path):
    y, sr = sf.read(path, dtype="float32", always_2d=True)
    assert sr == SR, (path, sr)
    if y.shape[1] == 1:
        y = np.repeat(y, 2, 1)
    y = y[:, :2]
    # trim leading silence so note onsets are tight
    thr = 10 ** (-50 / 20)
    idx = np.argmax(np.abs(y).max(1) > thr)
    idx = max(0, idx - int(0.003 * SR))
    return np.ascontiguousarray(y[idx:])


class Bank:
    """layer -> midi -> [round-robin samples]"""

    def __init__(self):
        self.layers = {}

    def add(self, layer, midi, y):
        self.layers.setdefault(layer, {}).setdefault(midi, []).append(y)

    def pick(self, layer, midi):
        lay = self.layers[layer]
        keys = np.array(sorted(lay))
        k = int(keys[np.argmin(np.abs(keys - midi) + (keys < midi) * 0.1)])
        rr = lay[k]
        return rr[rng.integers(len(rr))], k


def build_banks():
    B = {}
    f = lambda pat: sorted(glob.glob(os.path.join(VSCO, pat)))
    # piano: file index -> key number (MappingChart: 000=21, 002=25, ... step 2 semitones per index)
    p = Bank()
    for path in f("Keys__Upright Piano__Player_dyn*_rr1_*.wav"):
        dyn, idx = re.search(r"dyn(\d)_rr1_(\d+)", path).groups()
        idx = int(idx)
        key = 21 + 2 * idx if idx < 44 else 108
        y = load(path)[: int(SR * 7)]
        p.add("mf" if dyn == "2" else "f", key, y)
    B["piano"] = p
    a = Bank()
    for path in f("Strings__Solo Violin__Arco Vib__*.wav"):
        n, dyn = re.search(r"ArcoVib_([A-G]#?\d)_([pf])", path).groups()
        a.add(dyn, nm(n), load(path)[: int(SR * 6)])
    B["vln"] = a
    s = Bank()   # spiccato files are named one octave low (C3 = middle C convention): +12
    for path in f("Strings__Solo Violin__spic__*.wav"):
        n, v = re.search(r"spic_([A-G]#?\d)_v(\d)", path).groups()
        s.add("v" + v, nm(n) + 12, load(path)[: int(SR * 1.2)])
    B["spic"] = s
    z = Bank()
    for path in f("Strings__Solo Violin__Pizz__*.wav"):
        m = re.search(r"Pizz_([A-G]#?\d)_([pf])", path)
        if not m:
            continue
        z.add(m.group(2), nm(m.group(1)), load(path)[: int(SR * 1.5)])
    B["pizz"] = z
    c = Bank()
    for path in f("Strings__Cello Section__spic__*.wav"):
        n, v = re.search(r"spic_([A-G]#?\d)_v(\d)", path).groups()
        c.add("v" + v, nm(n) + 12, load(path)[: int(SR * 1.2)])
    B["cello"] = c
    g = Bank()
    for path in f("VSCO 1 Percussion__drums__other__Bongos__*.wav"):
        g.add("hi" if "High" in path else "lo", 0, load(path)[: int(SR * 0.8)])
    B["bongo"] = g
    t = Bank()
    for path in f("Percussion__Timpani__Timpani3_Hit_v4_rr1_Sum.wav"):
        t.add("hit", 37, load(path)[: int(SR * 4)])   # measured pitch ~37.3
    B["timp"] = t
    return B


# --------------------------------------------------------------------------- score
CH = {
    "Am": (9, [9, 0, 4]), "F": (5, [5, 9, 0]), "C": (0, [0, 4, 7]), "G": (7, [7, 11, 2]),
    "Em": (4, [4, 7, 11]), "Dm": (2, [2, 5, 9]), "E": (4, [4, 8, 11]),
}
EV = []   # (inst, beat, dur_beats, midi, vel, extra)


def ev(inst, beat, dur, midi, vel, **kw):
    EV.append((inst, beat, dur, midi, float(np.clip(vel, 0.05, 1.0)), kw))


def tones(ch, lo, hi):
    pcs = CH[ch][1]
    return [m for m in range(lo, hi + 1) if m % 12 in pcs]


def bass_root(ch, lo=40):
    r = CH[ch][0]
    m = lo + ((r - lo) % 12)
    return m


def triad(ch, center=71):
    cand = tones(ch, center - 9, center + 9)
    best = min((cand[i:i + 3] for i in range(len(cand) - 2)),
               key=lambda w: abs(np.mean(w) - center))
    return best


def bar0(b):
    return b * 4.0


# ---- instrument patterns (one bar each)
def pno_ostinato(b, ch, v, lh="1", center=71):
    a, bb, c = triad(ch, center)
    pat = [a, bb, c, bb, a, bb, c, a + 12]
    for i, n in enumerate(pat):
        beat = bar0(b) + i * 0.5
        half_end = bar0(b) + (2 if i < 4 else 4)
        acc = 1.0 if i in (0, 4) else 0.86
        ev("piano", beat, half_end - beat, n, v * acc, rel=0.18)
    r = bass_root(ch)
    hits = {"1": [(0, 4)], "2": [(0, 2), (2, 2)], "332": [(0, 1.5), (1.5, 1.5), (3, 1)]}[lh]
    for off, d in hits:
        for n in (r, r + 12):
            ev("piano", bar0(b) + off, d, n, v * 1.02, rel=0.2)


def pno_arp16(b, ch, v, lo=60, hi=88, lh="1"):
    ts = tones(ch, lo, hi)[:6]
    seq = ts + ts[-2:0:-1]
    for i in range(16):
        n = seq[i % len(seq)]
        beat = bar0(b) + i * 0.25
        acc = 1.0 if i % 4 == 0 else 0.8
        ev("piano", beat, 1.0, n, v * acc, rel=0.15)
    r = bass_root(ch)
    for off, d in {"1": [(0, 4)], "332": [(0, 1.5), (1.5, 1.5), (3, 1)]}[lh]:
        for n in (r, r + 12):
            ev("piano", bar0(b) + off, d, n, v * 1.05, rel=0.2)


def pno_stabs(b, ch, v, rhythm=(0, 1.5, 3), length=0.45, center=72):
    tri = triad(ch, center)
    r = bass_root(ch)
    for k, off in enumerate(rhythm):
        acc = 1.0 if k == 0 else 0.9
        for n in tri + [tri[0] + 12]:
            ev("piano", bar0(b) + off, length, n, v * acc, rel=0.07)
        for n in (r, r + 12):
            ev("piano", bar0(b) + off, length, n, v * acc, rel=0.07)


def pno_block(b, ch, v, beats=4, notes=None):
    r = bass_root(ch, 36)
    ns = notes or ([r, r + 12] + triad(ch, 66) + triad(ch, 76))
    for n in ns:
        ev("piano", bar0(b), beats, n, v, rel=0.6)


def cello(b, ch, v, mode="8"):
    r = bass_root(ch, 40)
    if mode == "8":
        acc = [1, .62, .8, .62, .95, .62, .8, .7]
        for i in range(8):
            n = r + (12 if i == 7 else 0)
            ev("cello", bar0(b) + i * 0.5, 0.45, n, v * acc[i])
    elif mode == "4":
        for i in range(4):
            ev("cello", bar0(b) + i, 0.6, r, v * (1 if i % 2 == 0 else .75))
    elif mode == "332":
        for off in (0, 1.5, 3):
            ev("cello", bar0(b) + off, 0.6, r, v)
            ev("cello", bar0(b) + off + 0.5, 0.4, r, v * .6)


def spic(b, ch, v, sub=0.5, lo=69, hi=81, cresc=0.0):
    ts = tones(ch, lo, hi)
    hi_n, lo_n, mid = ts[-1], ts[0], ts[len(ts) // 2]
    pat = [hi_n, lo_n, hi_n, lo_n, mid, lo_n, hi_n, mid]
    steps = int(4 / sub)
    for i in range(steps):
        acc = 1.0 if (i * sub) % 1 == 0 else 0.78
        ev("spic", bar0(b) + i * sub, sub * 0.9, pat[i % 8], v * acc * (1 + cresc * i / steps))


def pizz(b, ch, v):
    ts = tones(ch, 64, 84)
    r = [t for t in ts if t % 12 == CH[ch][0]][0]
    third = [t for t in ts if t > r][0]
    fifth = [t for t in ts if t > third][0]
    for off, n, a in [(0, r, 1), (1, fifth, .8), (1.5, third, .75), (2.5, r + 12, .9), (3, fifth, .8)]:
        ev("pizz", bar0(b) + off, 0.5, n, v * a)


def bongos(b, v, busy=False):
    pat = [(0, "lo", 1), (1, "hi", .7), (1.5, "hi", .55), (2.5, "lo", .8), (3, "hi", .7), (3.5, "hi", .6)]
    if busy:
        pat += [(0.75, "hi", .4), (2.0, "hi", .5), (3.75, "hi", .45)]
    for off, which, a in pat:
        ev("bongo", bar0(b) + off, 0.3, 0, v * a, which=which)


def timp(b, v, midi=33, off=0.0):
    ev("timp", bar0(b) + off, 4, midi, v)


def melody(b, notes, v, transpose=0):
    beat = bar0(b)
    for n, d in notes:
        if n is not None:
            # slight swell on long notes, softer on short passing notes
            ev("vln", beat, d, nm(n) + transpose, v * (1.0 if d >= 1 else 0.88))
        beat += d


# ---- themes (pitch, beats)
M_A = [("A4", 2), ("C5", 1), ("E5", 1),  ("F5", 3), ("E5", 1),
       ("E5", 2), ("D5", 1), ("C5", 1),  ("D5", 3), ("B4", 1),
       ("A4", 1), ("C5", 1), ("E5", 1), ("A5", 1),  ("A5", 2), ("G5", 1), ("F5", 1),
       ("G5", 1), ("E5", 1), ("C5", 1), ("E5", 1),  ("D5", 4)]
M_B = [("C6", 1.5), ("A5", 1.5), ("F5", 1),  ("D6", 1.5), ("B5", 1.5), ("G5", 1),
       ("E6", 1.5), ("B5", 1.5), ("G5", 1),  ("A5", 3), ("E5", 1)]
M_B_END = M_B[:-2] + [("A5", 4)]
M_PRE = [("A4", 2), ("D5", 2),  ("C5", 2), ("F5", 2),  ("D5", 4),  ("B4", 2), ("D5", 1), ("G5", 1),
         ("F5", 4),  ("G5", 2), ("E5", 2),  ("A5", 2), ("C6", 2),  ("B5", 2), ("G#5", 2)]
M_C = [("A5", 4), ("E5", 4), ("G#5", 2), ("B5", 2), ("A5", 4)]
M_D = [("A5", 1.5), ("G5", 0.5), ("F5", 1), ("C5", 1),  ("D5", 1.5), ("E5", 0.5), ("F5", 1), ("G5", 1),
       ("E5", 2), ("G5", 1), ("C6", 1),  ("B5", 1), ("A5", 1), ("E5", 2)]
M_M = [("E5", 1), ("A5", 1), ("C6", 2),  ("B5", 2), ("G5", 2),  ("A5", 1), ("F5", 1), ("C6", 2),  ("B5", 2), ("D6", 2)]
M_END = [("A5", 1.5), ("G5", 0.5), ("F5", 1), ("C5", 1),  ("D5", 2), ("G5", 2),  ("E5", 4),  ("G5", 2), ("D5", 2)]


def compose():
    A = ["Am", "F", "C", "G"]
    Bp = ["F", "G", "Em", "Am"]
    PRE = ["Dm", "F", "G", "G", "Dm", "Em", "F", "E"]
    Cp = ["Dm", "Am", "E", "Am"]
    Dp = ["F", "G", "C", "Am"]
    Mp = ["Am", "Em", "F", "G"]

    # 0-8 intro / hook
    intro = ["Am", "Am", "F", "F", "C", "C", "G", "E"]
    timp(0, 0.9)
    for n in (33, 45):
        ev("piano", 0, 4, n, 0.9, rel=0.4)
    for i, ch in enumerate(intro):
        b = i
        if i < 7:
            pno_ostinato(b, ch, 0.52 + 0.03 * i, lh="1" if i < 4 else "332")
        else:
            pno_arp16(b, ch, 0.7, lh="332")
        if i >= 4:
            cello(b, ch, 0.55 + 0.05 * (i - 4))
            spic(b, ch, 0.5 + 0.04 * (i - 4), sub=0.5 if i < 7 else 0.25, cresc=0.4 if i == 7 else 0)

    # 8-12 title + 12-24 who  (theme A then lighter B verse)
    timp(8, 0.95)
    melody(8, M_A, 0.86)
    for i in range(8):
        ch = A[i % 4]
        pno_ostinato(8 + i, ch, 0.72, lh="332", center=64)
        cello(8 + i, ch, 0.72)
    for i in range(8):
        b, ch = 16 + i, Bp[i % 4]
        pno_arp16(b, ch, 0.5)
        pizz(b, ch, 0.62)
        bongos(b, 0.55)
        cello(b, ch, 0.5, "4")
    melody(20, M_B_END, 0.6)

    # 24-32 core: pre-chorus build
    for i, ch in enumerate(PRE):
        b = 24 + i
        pno_stabs(b, ch, 0.6 + 0.025 * i)
        cello(b, ch, 0.6 + 0.03 * i)
    melody(24, M_PRE, 0.72)
    spic(31, "E", 0.55, sub=0.25, lo=68, hi=83, cresc=0.5)

    # 32-44 step 1: theme A + interlude
    timp(32, 0.95)
    melody(32, M_A, 0.9)
    for i in range(12):
        b, ch = 32 + i, A[i % 4]
        pno_ostinato(b, ch, 0.74, lh="332", center=64 if i < 8 else 71)
        cello(b, ch, 0.74)
        if i >= 8:
            spic(b, ch, 0.58)
            bongos(b, 0.5)

    # 44-56 step 2: playful B section with pizzicato + bongos
    for i in range(12):
        b, ch = 44 + i, Bp[i % 4]
        pno_arp16(b, ch, 0.7, lo=57, hi=84, lh="1" if i < 4 else "332")
        pizz(b, ch, 0.62)
        bongos(b, 0.58, busy=i >= 8)
        cello(b, ch, 0.55, "4" if i < 8 else "8")
    melody(48, M_B, 0.78)
    melody(52, M_B_END, 0.82)

    # 56-68 step 3: tension (finding the gaps)
    for i in range(12):
        b, ch = 56 + i, Cp[i % 4]
        spic(b, ch, 0.6, sub=0.25, lo=67, hi=81)
        pno_stabs(b, ch, 0.68, center=69)
        cello(b, ch, 0.72)
        bongos(b, 0.5, busy=True)
    melody(60, M_C, 0.7)
    melody(64, M_C, 0.84, transpose=0)

    # 68-80 step 4: bright release
    timp(68, 0.9, midi=36)
    for i in range(12):
        b, ch = 68 + i, Dp[i % 4]
        pno_ostinato(b, ch, 0.74, lh="332", center=65)
        cello(b, ch, 0.72)
        if i >= 8:
            spic(b, ch, 0.55)
    melody(68, M_D, 0.84)
    melody(72, M_D, 0.88)
    melody(76, M_D, 0.92)

    # 80-100 worked example
    for i in range(8):
        b, ch = 80 + i, A[i % 4]
        pno_ostinato(b, ch, 0.6, lh="2")
        pizz(b, ch, 0.55)
        bongos(b, 0.48)
        cello(b, ch, 0.52, "4")
    for i, ch in enumerate(PRE):
        b = 88 + i
        if i < 4:
            pno_stabs(b, ch, 0.62 + 0.02 * i)
        else:
            pno_ostinato(b, ch, 0.66 + 0.02 * i, lh="332")
        cello(b, ch, 0.6 + 0.03 * i)
        spic(b, ch, 0.5 + 0.03 * i, sub=0.5 if i < 6 else 0.25, cresc=0.4 if i == 7 else 0)
    melody(88, M_PRE, 0.7)
    timp(96, 0.95)
    melody(96, M_A[:10], 0.92)
    for i in range(4):
        b, ch = 96 + i, A[i]
        pno_arp16(b, ch, 0.74, lh="332")
        cello(b, ch, 0.8)

    # 100-112 mistakes: rhythmic stabs
    for i in range(12):
        b, ch = 100 + i, Mp[i % 4]
        pno_stabs(b, ch, 0.66, rhythm=(0, 0.75, 1.5, 2.5, 3.25), length=0.3)
        cello(b, ch, 0.66)
        spic(b, ch, 0.52)
        bongos(b, 0.5, busy=i >= 4)
    melody(104, M_M, 0.72)
    melody(108, M_M, 0.82)

    # 112-120 recap: climax, theme an octave up
    timp(112, 1.0)
    timp(116, 0.85)
    melody(112, M_A, 0.95, transpose=12)
    for i in range(8):
        b, ch = 112 + i, A[i % 4]
        pno_arp16(b, ch, 0.8, lh="332")
        cello(b, ch, 0.85)
        bongos(b, 0.5, busy=True)

    # 120-130 CTA + ending on C major
    cta = ["F", "G", "C", "Am", "F", "G", "C", "G"]
    for i, ch in enumerate(cta):
        b = 120 + i
        pno_ostinato(b, ch, 0.72 - 0.012 * i, lh="332" if i < 6 else "2", center=65)
        cello(b, ch, 0.7 - 0.02 * i, "8" if i < 6 else "4")
    melody(120, M_D, 0.85)
    melody(124, M_END, 0.8)
    timp(128, 0.9, midi=36)
    pno_block(128, "C", 0.82, beats=8, notes=[36, 48, 60, 64, 67, 72, 76, 79, 84])
    ev("vln", bar0(128), 8, nm("C6"), 0.8)
    ev("cello", bar0(128), 0.6, 36, 0.9)


# --------------------------------------------------------------------------- render
INST = {  # gain, pan(-1..1), reverb send, release s
    # gains balanced from measured active RMS (piano ~-29 dB reference):
    # violin lead +2 dB, spiccato/pizz ~-6 dB, cello ~-4 dB, bongos ~-11 dB
    "piano": (0.62, -0.12, 0.20, 0.18),
    "vln":   (0.95, 0.18, 0.30, 0.16),
    "spic":  (1.30, 0.32, 0.22, 0.05),
    "pizz":  (2.40, 0.28, 0.25, 0.10),
    "cello": (0.85, -0.30, 0.16, 0.05),
    "bongo": (1.55, 0.10, 0.12, 0.05),
    "timp":  (0.95, 0.0, 0.22, 0.30),
}


def place(bus, start, y, ratio, length, rel, gain, pan, fade_in=0.002):
    if ratio != 1.0:
        n_out = int(min((length + rel) * SR, (len(y) - 2) / ratio))
        idx = np.arange(n_out) * ratio
        i0 = idx.astype(np.int64)
        fr = (idx - i0)[:, None].astype(np.float32)
        out = y[i0] * (1 - fr) + y[i0 + 1] * fr
    else:
        n_out = int(min((length + rel) * SR, len(y)))
        out = y[:n_out].copy()
    env = np.ones(n_out, np.float32)
    fi = int(fade_in * SR)
    if fi:
        env[:fi] = np.linspace(0, 1, fi)
    k = int(length * SR)
    if k < n_out:
        tail = n_out - k
        env[k:] *= np.cos(np.linspace(0, np.pi / 2, tail)) ** 2
    out *= env[:, None]
    th = (pan + 1) * np.pi / 4
    out[:, 0] *= gain * np.sqrt(2) * np.cos(th)
    out[:, 1] *= gain * np.sqrt(2) * np.sin(th)
    s = int(start * SR)
    if s < 0:
        out, s = out[-s:], 0
    e = min(len(bus), s + len(out))
    bus[s:e] += out[: e - s]


def make_ir(seconds=2.2, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), np.float32)
    for c in range(2):
        noise = r.standard_normal(n).astype(np.float32)
        b, a = signal.butter(1, 6500 / (SR / 2))
        noise = signal.lfilter(b, a, noise)
        ir[:, c] = noise * np.exp(-t * 6.9 / seconds)
    pre = int(0.018 * SR)
    ir = np.vstack([np.zeros((pre, 2), np.float32), ir])
    for d, g in [(0.011, .5), (0.019, .35), (0.027, .3), (0.041, .22)]:
        ir[int(d * SR), 0] += g
        ir[int((d + 0.004) * SR), 1] += g
    return ir / np.sqrt((ir ** 2).sum(0)).mean()


def render():
    banks = build_banks()
    compose()
    n = int(DURATION * SR) + SR
    buses = {k: np.zeros((n, 2), np.float32) for k in INST}
    for inst, beat, dur, midi, vel, kw in EV:
        gain, pan, _, rel = INST[inst]
        rel = kw.get("rel", rel)
        t = beat * BEAT
        if not (inst == "timp" or beat % 4 == 0):
            t += rng.normal(0, 0.005)
        vel = vel * (1 + rng.normal(0, 0.03))
        length = dur * BEAT
        if inst == "piano":
            y, k = banks["piano"].pick("mf" if vel < 0.64 else "f", midi)
            g = gain * vel ** 1.5
        elif inst == "vln":
            y, k = banks["vln"].pick("p" if vel < 0.7 else "f", midi)
            length += 0.03          # legato overlap
            g = gain * vel ** 1.2
        elif inst in ("spic", "cello"):
            y, k = banks[inst].pick("v1" if vel < 0.6 else "v2", midi)
            g = gain * vel ** 1.3
        elif inst == "pizz":
            y, k = banks["pizz"].pick("p" if vel < 0.6 else "f", midi)
            g = gain * vel ** 1.3
        elif inst == "bongo":
            y, k = banks["bongo"].pick(kw["which"], 0)
            midi, g = 0, gain * vel ** 1.3
        elif inst == "timp":
            y, k = banks["timp"].pick("hit", midi)
            g = gain * vel ** 1.2
        ratio = 2 ** ((midi - k) / 12)
        place(buses[inst], t, y, ratio, length, rel, g, pan)

    ir = make_ir()
    dry = sum(buses.values())
    send = sum(buses[k] * INST[k][2] for k in INST)
    wet = np.stack([signal.oaconvolve(send[:, c], ir[:, c])[:n] for c in range(2)], 1)
    mix = dry + wet * 0.55
    b, a = signal.butter(2, 32 / (SR / 2), "high")
    mix = signal.lfilter(b, a, mix, axis=0).astype(np.float32)

    # gentle bus compression (RMS, 2.5:1 above -20 dBFS)
    mono = (mix ** 2).mean(1)
    att, relc = np.exp(-1 / (0.01 * SR)), np.exp(-1 / (0.15 * SR))
    env = signal.lfilter([1 - relc], [1, -relc], mono)
    env = np.sqrt(np.maximum(env, 1e-12))
    lvl = 20 * np.log10(env + 1e-9)
    over = np.maximum(lvl - (-20), 0)
    gain_db = -over * (1 - 1 / 2.5)
    mix *= (10 ** (gain_db / 20))[:, None].astype(np.float32)

    # fade out the tail, peak-normalize to -1 dBFS
    end = int(DURATION * SR)
    fade = int(1.2 * SR)
    mix = mix[:end]
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    mix *= 10 ** (-1 / 20) / np.abs(mix).max()

    os.makedirs(BUILD, exist_ok=True)
    out = os.path.join(BUILD, "music.wav")
    sf.write(out, mix, SR, subtype="PCM_24")
    print(f"{len(EV)} notes -> {out}  ({len(mix) / SR:.1f}s)")
    for k, v in buses.items():
        print(f"  bus {k:6s} rms={20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-9):6.1f} dB")


if __name__ == "__main__":
    render()
