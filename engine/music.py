"""Original soundtrack engine: piano + violin lead, cello spiccato / pizzicato / bongos / timpani.

Rendered from real recordings (VSCO-2 CE, CC0), so it is royalty-free and never triggers
content-ID. Two ways to write a score:

1. auto_score(score, sections): give each section a ROLE and a bar count, the arrangement is
   generated (see ROLES). This is what Episode uses by default.
2. Call the pattern helpers yourself (ostinato, arp16, stabs, cello, spic, pizz, bongos, timp,
   melody) for full control.

Everything is in A minor; Score(transpose=n) shifts the whole piece by n semitones.
"""
import glob
import os
import re

import numpy as np
import soundfile as sf
from scipy import signal

from . import ASSETS

SR = 44100
VSCO = os.path.join(ASSETS, "vsco")
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def nm(s):
    """'A4' -> 69, 'G#5' -> 80"""
    m = re.fullmatch(r"([A-G])(#|b)?(-?\d)", s)
    return 12 * (int(m.group(3)) + 1) + NOTE[m.group(1)] + {"#": 1, "b": -1, None: 0}[m.group(2)]


# --------------------------------------------------------------------------- samples
def _load(path, max_s):
    y, sr = sf.read(path, dtype="float32", always_2d=True)
    assert sr == SR, (path, sr)
    if y.shape[1] == 1:
        y = np.repeat(y, 2, 1)
    y = y[:, :2]
    idx = np.argmax(np.abs(y).max(1) > 10 ** (-50 / 20))
    idx = max(0, idx - int(0.003 * SR))
    return np.ascontiguousarray(y[idx: idx + int(max_s * SR)])


class Bank:
    def __init__(self, rng):
        self.layers, self.rng = {}, rng

    def add(self, layer, midi, y):
        self.layers.setdefault(layer, {}).setdefault(midi, []).append(y)

    def pick(self, layer, midi):
        lay = self.layers[layer]
        keys = np.array(sorted(lay))
        k = int(keys[np.argmin(np.abs(keys - midi) + (keys < midi) * 0.1)])
        rr = lay[k]
        return rr[self.rng.integers(len(rr))], k


# Measured with pitch detection: VSCO filenames are off by an octave for these files.
PIZZ_FIX = {"Pizz_A4_f_RR1": 81, "Pizz_A6_f_RR1": 81, "Pizz_A6_f_RR2": 81,
            "Pizz_G3_f_RR1": 67, "Pizz_G3_f_RR2": 67, "Pizz_G3_p_RR1": 67}
PIZZ_SKIP = ("Pizz_C7_f",)


def build_banks(rng):
    if not glob.glob(os.path.join(VSCO, "*.wav")):
        raise SystemExit("No samples found. Run: python -m engine.assets")
    f = lambda pat: sorted(glob.glob(os.path.join(VSCO, pat)))
    B = {}
    p = Bank(rng)   # piano: file index -> key 21 + 2*idx (MappingChart.txt), idx 44 = key 108
    for path in f("Keys__Upright Piano__Player_dyn*_rr1_*.wav"):
        dyn, idx = re.search(r"dyn(\d)_rr1_(\d+)", path).groups()
        idx = int(idx)
        p.add("mf" if dyn == "2" else "f", 21 + 2 * idx if idx < 44 else 108, _load(path, 7))
    B["piano"] = p
    a = Bank(rng)
    for path in f("Strings__Solo Violin__Arco Vib__*.wav"):
        n, dyn = re.search(r"ArcoVib_([A-G]#?\d)_([pf])", path).groups()
        a.add(dyn, nm(n), _load(path, 6))
    B["vln"] = a
    s = Bank(rng)   # spiccato files are named one octave low -> +12 (measured)
    for path in f("Strings__Solo Violin__spic__*.wav"):
        n, v = re.search(r"spic_([A-G]#?\d)_v(\d)", path).groups()
        s.add("v" + v, nm(n) + 12, _load(path, 1.2))
    B["spic"] = s
    z = Bank(rng)
    for path in f("Strings__Solo Violin__Pizz__*.wav"):
        m = re.search(r"(Pizz_([A-G]#?\d)_([pf])(?:_RR\d)?)", path)
        if not m or any(k in path for k in PIZZ_SKIP):
            continue
        z.add(m.group(3), PIZZ_FIX.get(m.group(1), nm(m.group(2))), _load(path, 1.5))
    B["pizz"] = z
    c = Bank(rng)   # cello spiccato also named one octave low -> +12 (measured)
    for path in f("Strings__Cello Section__spic__*.wav"):
        n, v = re.search(r"spic_([A-G]#?\d)_v(\d)", path).groups()
        c.add("v" + v, nm(n) + 12, _load(path, 1.2))
    B["cello"] = c
    g = Bank(rng)
    for path in f("VSCO 1 Percussion__drums__other__Bongos__*.wav"):
        g.add("hi" if "High" in path else "lo", 0, _load(path, 0.8))
    B["bongo"] = g
    t = Bank(rng)
    for path in f("Percussion__Timpani__Timpani3_Hit_v4_rr1_Sum.wav"):
        t.add("hit", 37, _load(path, 4))      # measured pitch ~37.3
    B["timp"] = t
    return B


# --------------------------------------------------------------------------- score + patterns
class Score:
    def __init__(self, bpm=136, transpose=0):
        self.bpm, self.beat, self.transpose, self.ev = bpm, 60.0 / bpm, transpose, []

    def add(self, inst, beat, dur, midi, vel, **kw):
        self.ev.append((inst, beat, dur, midi, float(np.clip(vel, 0.05, 1.0)), kw))


CH = {"Am": (9, [9, 0, 4]), "F": (5, [5, 9, 0]), "C": (0, [0, 4, 7]), "G": (7, [7, 11, 2]),
      "Em": (4, [4, 7, 11]), "Dm": (2, [2, 5, 9]), "E": (4, [4, 8, 11])}


def tones(ch, lo, hi):
    return [m for m in range(lo, hi + 1) if m % 12 in CH[ch][1]]


def bass_root(ch, lo=40):
    return lo + ((CH[ch][0] - lo) % 12)


def triad(ch, center=71):
    cand = tones(ch, center - 9, center + 9)
    return min((cand[i:i + 3] for i in range(len(cand) - 2)), key=lambda w: abs(np.mean(w) - center))


def _b(b):
    return b * 4.0


def _lh(s, b, ch, v, lh):
    r = bass_root(ch)
    for off, d in {"1": [(0, 4)], "2": [(0, 2), (2, 2)], "332": [(0, 1.5), (1.5, 1.5), (3, 1)]}[lh]:
        for n in (r, r + 12):
            s.add("piano", _b(b) + off, d, n, v * 1.02, rel=0.2)


def ostinato(s, b, ch, v, lh="332", center=65):
    a, bb, c = triad(ch, center)
    for i, n in enumerate([a, bb, c, bb, a, bb, c, a + 12]):
        beat = _b(b) + i * 0.5
        s.add("piano", beat, _b(b) + (2 if i < 4 else 4) - beat, n, v * (1.0 if i in (0, 4) else 0.86), rel=0.18)
    _lh(s, b, ch, v, lh)


def arp16(s, b, ch, v, lo=57, hi=84, lh="332"):
    ts = tones(ch, lo, hi)[:6]
    seq = ts + ts[-2:0:-1]
    for i in range(16):
        s.add("piano", _b(b) + i * 0.25, 1.0, seq[i % len(seq)], v * (1.0 if i % 4 == 0 else 0.8), rel=0.15)
    _lh(s, b, ch, v * 1.03, lh)


def stabs(s, b, ch, v, rhythm=(0, 1.5, 3), length=0.45, center=72):
    tri, r = triad(ch, center), bass_root(ch)
    for k, off in enumerate(rhythm):
        acc = 1.0 if k == 0 else 0.9
        for n in tri + [tri[0] + 12, r, r + 12]:
            s.add("piano", _b(b) + off, length, n, v * acc, rel=0.07)


def block(s, b, notes, v, beats=8):
    for n in notes:
        s.add("piano", _b(b), beats, n, v, rel=0.6)


def cello(s, b, ch, v, mode="8"):
    r = bass_root(ch, 40)
    if mode == "8":
        for i, acc in enumerate([1, .62, .8, .62, .95, .62, .8, .7]):
            s.add("cello", _b(b) + i * 0.5, 0.45, r + (12 if i == 7 else 0), v * acc)
    elif mode == "4":
        for i in range(4):
            s.add("cello", _b(b) + i, 0.6, r, v * (1 if i % 2 == 0 else .75))


def spic(s, b, ch, v, sub=0.5, lo=69, hi=81, cresc=0.0):
    ts = tones(ch, lo, hi)
    hi_n, lo_n, mid = ts[-1], ts[0], ts[len(ts) // 2]
    pat = [hi_n, lo_n, hi_n, lo_n, mid, lo_n, hi_n, mid]
    steps = int(4 / sub)
    for i in range(steps):
        acc = 1.0 if (i * sub) % 1 == 0 else 0.78
        s.add("spic", _b(b) + i * sub, sub * 0.9, pat[i % 8], v * acc * (1 + cresc * i / steps))


def pizz(s, b, ch, v):
    ts = tones(ch, 64, 84)
    r = [t for t in ts if t % 12 == CH[ch][0]][0]
    third = [t for t in ts if t > r][0]
    fifth = [t for t in ts if t > third][0]
    for off, n, a in [(0, r, 1), (1, fifth, .8), (1.5, third, .75), (2.5, r + 12, .9), (3, fifth, .8)]:
        s.add("pizz", _b(b) + off, 0.5, n, v * a)


def bongos(s, b, v, busy=False):
    pat = [(0, "lo", 1), (1, "hi", .7), (1.5, "hi", .55), (2.5, "lo", .8), (3, "hi", .7), (3.5, "hi", .6)]
    if busy:
        pat += [(0.75, "hi", .4), (2.0, "hi", .5), (3.75, "hi", .45)]
    for off, which, a in pat:
        s.add("bongo", _b(b) + off, 0.3, 0, v * a, which=which)


def timp(s, b, v, midi=33):
    s.add("timp", _b(b), 4, midi, v)


def melody(s, b, notes, v, transpose=0, end_bar=None):
    beat, end = _b(b), (_b(end_bar) if end_bar is not None else 1e9)
    for n, d in notes:
        if beat >= end:
            break
        if n is not None:
            s.add("vln", beat, min(d, end - beat), nm(n) + transpose, v * (1.0 if d >= 1 else 0.88))
        beat += d


def mel_bars(notes):
    return sum(d for _, d in notes) / 4


# 8-bar / 4-bar themes (pitch, beats)
M_A = [("A4", 2), ("C5", 1), ("E5", 1), ("F5", 3), ("E5", 1), ("E5", 2), ("D5", 1), ("C5", 1), ("D5", 3), ("B4", 1),
       ("A4", 1), ("C5", 1), ("E5", 1), ("A5", 1), ("A5", 2), ("G5", 1), ("F5", 1), ("G5", 1), ("E5", 1), ("C5", 1),
       ("E5", 1), ("D5", 4)]
M_B = [("C6", 1.5), ("A5", 1.5), ("F5", 1), ("D6", 1.5), ("B5", 1.5), ("G5", 1), ("E6", 1.5), ("B5", 1.5), ("G5", 1),
       ("A5", 3), ("E5", 1)]
M_PRE = [("A4", 2), ("D5", 2), ("C5", 2), ("F5", 2), ("D5", 4), ("B4", 2), ("D5", 1), ("G5", 1), ("F5", 4),
         ("G5", 2), ("E5", 2), ("A5", 2), ("C6", 2), ("B5", 2), ("G#5", 2)]
M_C = [("A5", 4), ("E5", 4), ("G#5", 2), ("B5", 2), ("A5", 4)]
M_D = [("A5", 1.5), ("G5", 0.5), ("F5", 1), ("C5", 1), ("D5", 1.5), ("E5", 0.5), ("F5", 1), ("G5", 1),
       ("E5", 2), ("G5", 1), ("C6", 1), ("B5", 1), ("A5", 1), ("E5", 2)]
M_M = [("E5", 1), ("A5", 1), ("C6", 2), ("B5", 2), ("G5", 2), ("A5", 1), ("F5", 1), ("C6", 2), ("B5", 2), ("D6", 2)]
M_END = [("A5", 1.5), ("G5", 0.5), ("F5", 1), ("C5", 1), ("D5", 2), ("G5", 2), ("E5", 4), ("G5", 2), ("D5", 2)]


# --------------------------------------------------------------------------- roles
def _acc_intro(s, b, ch, i, n, fill):
    half = n // 2
    if i == n - 1:
        arp16(s, b, ch, 0.7)
    else:
        ostinato(s, b, ch, 0.52 + 0.2 * i / max(1, n), lh="1" if i < half else "332", center=71)
    if i >= half:
        cello(s, b, ch, 0.55 + 0.15 * (i - half) / max(1, n - half))
        if not fill:
            spic(s, b, ch, 0.5)


def _acc_theme(s, b, ch, i, n, fill):
    ostinato(s, b, ch, 0.74, center=64)
    cello(s, b, ch, 0.74)
    if i >= 8 and not fill:
        spic(s, b, ch, 0.56)


def _acc_verse(s, b, ch, i, n, fill):
    arp16(s, b, ch, 0.7, lh="1" if i < 2 else "332")
    pizz(s, b, ch, 0.62)
    bongos(s, b, 0.56, busy=i >= 4)
    cello(s, b, ch, 0.55, "4")


def _acc_build(s, b, ch, i, n, fill):
    stabs(s, b, ch, 0.6 + 0.12 * i / max(1, n))
    cello(s, b, ch, 0.6 + 0.2 * i / max(1, n))


def _acc_tension(s, b, ch, i, n, fill):
    if not fill:
        spic(s, b, ch, 0.6, sub=0.25, lo=67, hi=81)
    stabs(s, b, ch, 0.68, center=69)
    cello(s, b, ch, 0.72)
    bongos(s, b, 0.5, busy=True)


def _acc_release(s, b, ch, i, n, fill):
    ostinato(s, b, ch, 0.74, center=65)
    cello(s, b, ch, 0.72)
    if i >= n // 2 and not fill:
        spic(s, b, ch, 0.55)


def _acc_drive(s, b, ch, i, n, fill):
    stabs(s, b, ch, 0.66, rhythm=(0, 0.75, 1.5, 2.5, 3.25), length=0.3)
    cello(s, b, ch, 0.66)
    if not fill:
        spic(s, b, ch, 0.52)
    bongos(s, b, 0.5, busy=i >= 2)


def _acc_recap(s, b, ch, i, n, fill):
    arp16(s, b, ch, 0.8)
    cello(s, b, ch, 0.85)
    bongos(s, b, 0.5, busy=True)


def _acc_outro(s, b, ch, i, n, fill):
    if i < n - 2:
        ostinato(s, b, ch, 0.72 - 0.15 * i / max(1, n), center=65)
        cello(s, b, ch, 0.7, "8" if i < n - 3 else "4")
    elif i == n - 2:
        block(s, b, [36, 48, 60, 64, 67, 72, 76, 79, 84], 0.82, beats=8)
        s.add("vln", _b(b), 8, nm("C6"), 0.8)
        s.add("cello", _b(b), 0.6, 36, 0.9)
        timp(s, b, 0.9, midi=36)


A_PROG, B_PROG, PRE_PROG = ["Am", "F", "C", "G"], ["F", "G", "Em", "Am"], ["Dm", "F", "G", "G", "Dm", "Em", "F", "E"]
ROLES = {
    # role: progression, accompaniment, melody, melody velocity, melody start offset (bars), timpani hit
    "intro":   dict(prog=A_PROG, acc=_acc_intro, mel=None, last="E", hit=33),
    "theme":   dict(prog=A_PROG, acc=_acc_theme, mel=M_A, vel=0.9, hit=33),
    "verse":   dict(prog=B_PROG, acc=_acc_verse, mel=M_B, vel=0.76, off=2),
    "build":   dict(prog=PRE_PROG, acc=_acc_build, mel=M_PRE, vel=0.72, last="E"),
    "tension": dict(prog=["Dm", "Am", "E", "Am"], acc=_acc_tension, mel=M_C, vel=0.8, off=2),
    "release": dict(prog=["F", "G", "C", "Am"], acc=_acc_release, mel=M_D, vel=0.88, hit=36),
    "drive":   dict(prog=["Am", "Em", "F", "G"], acc=_acc_drive, mel=M_M, vel=0.8, off=2),
    "recap":   dict(prog=A_PROG, acc=_acc_recap, mel=M_A, vel=0.95, mel_tr=12, hit=33),
    "outro":   dict(prog=["F", "G", "C", "G"], acc=_acc_outro, mel=M_END, vel=0.8),
}
ROLE_DOC = {
    "intro": "hook: builds up, ends on the dominant",
    "theme": "main violin theme, full band (good for the core answer / title)",
    "verse": "light & playful: piano arpeggio + pizzicato + bongos (explanations, examples)",
    "build": "rising stabs (before a reveal)",
    "tension": "fast spiccato, minor (problems, mistakes, 'getting stuck')",
    "release": "bright major (solutions, the 'aha')",
    "drive": "rhythmic stabs (lists, quick tips)",
    "recap": "climax: theme an octave up (summary card)",
    "outro": "winds down; LAST 2 BARS are a ringing C-major chord (CTA / end card)",
}


def auto_score(s, sections):
    """sections: [(role, start_bar, bars)] in order."""
    for k, (role, b0, n) in enumerate(sections):
        R = ROLES[role]
        nxt = sections[k + 1][0] if k + 1 < len(sections) else None
        if R.get("hit") is not None:
            timp(s, b0, 0.95, midi=R["hit"])
        for i in range(n):
            ch = R["prog"][i % len(R["prog"])]
            fill = i == n - 1 and nxt in ("theme", "recap", "release") and role != "outro"
            if i == n - 1 and R.get("last"):
                ch = R["last"]
            R["acc"](s, b0 + i, ch, i, n, fill)
            if fill:
                spic(s, b0 + i, ch, 0.6, sub=0.25, lo=68, hi=83, cresc=0.5)
        if R["mel"]:
            off = R.get("off", 0) if n >= 4 + R.get("off", 0) else 0
            end = b0 + (n - 2 if role == "outro" else n)
            mb = b0 + off
            while mb < end:
                melody(s, mb, R["mel"], R["vel"], R.get("mel_tr", 0), end_bar=end)
                mb += mel_bars(R["mel"])


# --------------------------------------------------------------------------- render
INST = {  # gain (balanced from measured active RMS), pan, reverb send, release s
    "piano": (0.62, -0.12, 0.20, 0.18), "vln": (0.95, 0.18, 0.30, 0.16), "spic": (1.30, 0.32, 0.22, 0.05),
    "pizz": (2.40, 0.28, 0.25, 0.10), "cello": (0.85, -0.30, 0.16, 0.05), "bongo": (1.55, 0.10, 0.12, 0.05),
    "timp": (0.95, 0.0, 0.22, 0.30),
}


def _place(bus, start, y, ratio, length, rel, gain, pan):
    if ratio != 1.0:
        n_out = int(min((length + rel) * SR, (len(y) - 2) / ratio))
        idx = np.arange(n_out) * ratio
        i0 = idx.astype(np.int64)
        fr = (idx - i0)[:, None].astype(np.float32)
        out = y[i0] * (1 - fr) + y[i0 + 1] * fr
    else:
        n_out = int(min((length + rel) * SR, len(y)))
        out = y[:n_out].copy()
    if n_out <= 0:
        return
    env = np.ones(n_out, np.float32)
    fi = min(n_out, int(0.002 * SR))
    env[:fi] = np.linspace(0, 1, fi)
    k = int(length * SR)
    if k < n_out:
        env[k:] *= np.cos(np.linspace(0, np.pi / 2, n_out - k)) ** 2
    out = out * env[:, None]
    th = (pan + 1) * np.pi / 4
    out[:, 0] *= gain * np.sqrt(2) * np.cos(th)
    out[:, 1] *= gain * np.sqrt(2) * np.sin(th)
    s = int(start * SR)
    if s < 0:
        out, s = out[-s:], 0
    e = min(len(bus), s + len(out))
    if e > s:
        bus[s:e] += out[: e - s]


def _ir(seconds=2.2, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), np.float32)
    b, a = signal.butter(1, 6500 / (SR / 2))
    for c in range(2):
        ir[:, c] = signal.lfilter(b, a, r.standard_normal(n).astype(np.float32)) * np.exp(-t * 6.9 / seconds)
    ir = np.vstack([np.zeros((int(0.018 * SR), 2), np.float32), ir])
    for d, g in [(0.011, .5), (0.019, .35), (0.027, .3), (0.041, .22)]:
        ir[int(d * SR), 0] += g
        ir[int((d + 0.004) * SR), 1] += g
    return ir / np.sqrt((ir ** 2).sum(0)).mean()


def render_wav(score, duration, out_path, seed=7):
    rng = np.random.default_rng(seed)
    banks = build_banks(rng)
    n = int(duration * SR) + SR
    buses = {k: np.zeros((n, 2), np.float32) for k in INST}
    for inst, beat, dur, midi, vel, kw in score.ev:
        gain, pan, _, rel = INST[inst]
        rel = kw.get("rel", rel)
        t = beat * score.beat + (0 if (inst == "timp" or beat % 4 == 0) else rng.normal(0, 0.005))
        vel *= 1 + rng.normal(0, 0.03)
        length = dur * score.beat
        if inst not in ("bongo",):
            midi = midi + score.transpose
        if inst == "piano":
            y, k = banks["piano"].pick("mf" if vel < 0.64 else "f", midi)
            g = gain * vel ** 1.5
        elif inst == "vln":
            y, k = banks["vln"].pick("p" if vel < 0.7 else "f", midi)
            length += 0.03
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
        else:
            y, k = banks["timp"].pick("hit", midi)
            g = gain * vel ** 1.2
        _place(buses[inst], t, y, 2 ** ((midi - k) / 12), length, rel, g, pan)
    ir = _ir()
    dry = sum(buses.values())
    send = sum(buses[k] * INST[k][2] for k in INST)
    wet = np.stack([signal.oaconvolve(send[:, c], ir[:, c])[:n] for c in range(2)], 1)
    mix = dry + wet * 0.55
    b, a = signal.butter(2, 32 / (SR / 2), "high")
    mix = signal.lfilter(b, a, mix, axis=0).astype(np.float32)
    mono = (mix ** 2).mean(1)
    relc = np.exp(-1 / (0.15 * SR))
    env = np.sqrt(np.maximum(signal.lfilter([1 - relc], [1, -relc], mono), 1e-12))
    over = np.maximum(20 * np.log10(env + 1e-9) + 20, 0)
    mix *= (10 ** (-over * 0.6 / 20))[:, None].astype(np.float32)
    end, fade = int(duration * SR), int(1.2 * SR)
    mix = mix[:end]
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    mix *= 10 ** (-1 / 20) / max(1e-9, np.abs(mix).max())
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sf.write(out_path, mix, SR, subtype="PCM_24")
    levels = {k: 20 * np.log10(np.sqrt((v ** 2).mean()) + 1e-9) for k, v in buses.items()}
    return len(score.ev), levels
