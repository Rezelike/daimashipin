"""Continuous piano + strings score, synthesized (no samples, no voice).
Key of C major, ~66.7 BPM, one through-composed piece spanning the whole video."""
import os
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scenes import timeline

SR = 44100
_, _, TOTAL = timeline()
BAR = 3.6
BEAT = BAR / 4
N = int((TOTAL + 0.0) * SR)
rng = np.random.default_rng(11)


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def nm(name):
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    acc = 1 if "#" in name else (-1 if "b" in name[1:] else 0)
    octv = int(name[-1])
    return 12 * (octv + 1) + names[name[0]] + acc


# chord: (bass, [voicing for arpeggio / pad])
CH = {
    "F":   ("F2", ["C3", "F3", "A3", "C4", "G4"]),
    "G":   ("G2", ["D3", "G3", "B3", "D4", "A4"]),
    "Em":  ("E2", ["B2", "E3", "G3", "B3", "D4"]),
    "Am":  ("A2", ["E3", "A3", "C4", "E4", "G4"]),
    "Dm":  ("D2", ["A2", "D3", "F3", "A3", "C4"]),
    "G7":  ("G2", ["D3", "G3", "B3", "F4", "D4"]),
    "C":   ("C3", ["G3", "C4", "E4", "G4", "D5"]),
    "Cs":  ("C3", ["G3", "C4", "D4", "G4", "E4"]),
}
PROG = ["F", "G", "Em", "Am", "Dm", "G7", "C", "Cs"]
BARS = [PROG[b % 8] for b in range(40)] + ["F", "C"]

MEL_A = [  # (bar, beat, dur_beats, note)
    (0, 0, 1.5, "A4"), (0, 1.5, 0.5, "G4"), (0, 2, 1, "A4"), (0, 3, 1, "C5"),
    (1, 0, 2, "B4"), (1, 2, 1, "G4"), (1, 3, 1, "D5"),
    (2, 0, 1.5, "E5"), (2, 1.5, 0.5, "D5"), (2, 2, 2, "B4"),
    (3, 0, 3, "C5"), (3, 3, 1, "A4"),
    (4, 0, 1.5, "D5"), (4, 1.5, 0.5, "C5"), (4, 2, 1, "A4"), (4, 3, 1, "F4"),
    (5, 0, 2, "G4"), (5, 2, 1, "B4"), (5, 3, 1, "D5"),
    (6, 0, 2, "E5"), (6, 2, 1, "D5"), (6, 3, 1, "C5"),
    (7, 0, 4, "C5"),
]
MEL_B = [
    (0, 0, 1, "C5"), (0, 1, 1, "A4"), (0, 2, 1, "C5"), (0, 3, 1, "F5"),
    (1, 0, 2, "D5"), (1, 2, 1, "B4"), (1, 3, 1, "G5"),
    (2, 0, 1.5, "G5"), (2, 1.5, 0.5, "E5"), (2, 2, 2, "B4"),
    (3, 0, 2, "A4"), (3, 2, 1, "C5"), (3, 3, 1, "E5"),
    (4, 0, 1.5, "F5"), (4, 1.5, 0.5, "E5"), (4, 2, 1, "D5"), (4, 3, 1, "A4"),
    (5, 0, 2, "B4"), (5, 2, 1, "D5"), (5, 3, 1, "F5"),
    (6, 0, 1, "E5"), (6, 1, 1, "G5"), (6, 2, 1, "E5"), (6, 3, 1, "D5"),
    (7, 0, 4, "C5"),
]


# ------------------------------------------------------------- instruments
def piano_note(midi, vel, length):
    f = mtof(midi)
    dur = length + 0.9
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    B = 0.00035
    bright = 0.55 + 0.45 * vel
    for h in range(1, 13):
        fh = f * h * np.sqrt(1 + B * h * h)
        if fh > 15000:
            break
        amp = (1.0 / h ** 1.15) * (bright ** (h - 1))
        dec = (0.55 + 0.32 * h) * (f / 262) ** 0.45
        env = np.exp(-t * dec) * 0.75 + np.exp(-t * dec * 6) * 0.25
        for det in (-0.6, 0.6):  # two strings per note -> gentle beating
            out += amp * env * np.sin(2 * np.pi * fh * (1 + det * 1e-3 * 0.8) * t + rng.random() * 6.28) * 0.5
    att = np.minimum(1, t / 0.004)
    rel = np.clip((dur - 0.9 + 0.35 - t) / 0.35, 0, 1) if length < 8 else 1
    rel = np.where(t < length, 1.0, np.clip(1 - (t - length) / 0.6, 0, 1) ** 2)
    hammer = rng.normal(0, 1, n) * np.exp(-t * 90) * 0.04 * vel
    return (out * att * rel + hammer) * vel


def saw_blep(freq_t):
    """Band-limited sawtooth with time-varying frequency."""
    dt = freq_t / SR
    ph = np.cumsum(dt) + rng.random()
    t = np.mod(ph, 1.0)
    y = 2 * t - 1
    m1 = t < dt
    x = t[m1] / dt[m1]
    y[m1] -= x + x - x * x - 1
    m2 = t > 1 - dt
    x = (t[m2] - 1) / dt[m2]
    y[m2] -= x * x + x + x + 1
    return y


def string_note(midi, start, length, att=0.8, rel=1.2, vib=0.0045, voices=5, spread=9.0):
    f = mtof(midi)
    dur = length + rel
    n = int(dur * SR)
    t = np.arange(n) / SR
    L = np.zeros(n)
    R = np.zeros(n)
    for v in range(voices):
        cents = (v - (voices - 1) / 2) / max(1, (voices - 1) / 2) * spread + rng.normal(0, 1.5)
        vr = 5.2 + rng.normal(0, 0.3)
        vdepth = vib * np.clip((t - 0.25) / 0.8, 0, 1)
        ft = f * 2 ** (cents / 1200) * (1 + vdepth * np.sin(2 * np.pi * vr * t + rng.random() * 6.28))
        s = saw_blep(ft)
        pan = 0.5 + 0.35 * ((v / max(1, voices - 1)) - 0.5) * 2
        L += s * (1 - pan)
        R += s * pan
    env = np.minimum(1, t / att) ** 1.5
    env *= np.where(t < length, 1.0, np.clip(1 - (t - length) / rel, 0, 1) ** 1.6)
    # slow bow-pressure swell
    env *= 0.9 + 0.1 * np.sin(2 * np.pi * t / max(1.5, length) - 1.2)
    return L * env / voices, R * env / voices


def add(buf, sig, start):
    i0 = int(start * SR)
    if i0 >= buf.shape[-1]:
        return
    i1 = min(buf.shape[-1], i0 + sig.shape[-1])
    buf[..., i0:i1] += sig[..., : i1 - i0]


def lowpass(x, fc, order=2):
    sos = butter(order, fc / (SR / 2), btype="low", output="sos")
    return sosfilt(sos, x, axis=-1)


def highpass(x, fc):
    sos = butter(2, fc / (SR / 2), btype="high", output="sos")
    return sosfilt(sos, x, axis=-1)


# ------------------------------------------------------------- arrangement
def build():
    pad = np.zeros((2, N + SR * 6))
    cello = np.zeros((2, N + SR * 6))
    viol = np.zeros((2, N + SR * 6))
    pno = np.zeros((2, N + SR * 6))

    def piano(midi, start, vel, length):
        s = piano_note(midi, vel, length)
        pan = np.clip(0.5 + (midi - 60) / 60.0, 0.15, 0.85)
        add(pno, np.vstack([s * (1 - pan) * 1.4, s * pan * 1.4]), start + rng.normal(0, 0.006))

    nb = len(BARS)
    for b, ch in enumerate(BARS):
        t0 = b * BAR
        bass, voic = CH[ch]
        cyc = b // 8
        final = (b == nb - 1)
        # ---------- piano left-hand arpeggio (always present = continuity)
        dyn = {0: 0.42, 1: 0.48, 2: 0.46, 3: 0.40, 4: 0.55}.get(cyc, 0.4)
        if b < 2:
            dyn *= 0.75 + 0.125 * b
        if final:
            piano(nm(bass), t0, 0.55, 6.0)
            piano(nm(bass) - 12, t0, 0.35, 6.0)
            for k, v in enumerate(voic):
                piano(nm(v), t0 + 0.09 * k, 0.38, 6.0)
            piano(nm("C5"), t0 + 0.6, 0.42, 6.0)
            piano(nm("E5"), t0 + 1.2, 0.30, 5.5)
            piano(nm("G5"), t0 + 1.8, 0.25, 5.0)
        else:
            pattern = [bass, voic[0], voic[1], voic[2], voic[3], voic[2], voic[1], voic[4]]
            for k, nn in enumerate(pattern):
                ln = BAR - k * BEAT / 2 + 0.15  # sustain pedal until bar end
                v = dyn * (1.0 if k == 0 else 0.62 + 0.12 * (k % 2 == 0)) * rng.uniform(0.92, 1.06)
                piano(nm(nn), t0 + k * BEAT / 2, v, ln)
            if cyc == 4 or b in (38, 39):
                piano(nm(bass) - 12, t0, dyn * 0.6, BAR)
        # ---------- string pad from bar 4 (soft), swell in cycle 4
        if b >= 4:
            lvl = {0: 0.5, 1: 0.7, 2: 0.85, 3: 0.6, 4: 1.0}.get(cyc, 0.7)
            if final:
                lvl = 0.75
            ln = BAR + 0.25 if not final else 5.0
            for v in voic[:4]:
                l, r = string_note(nm(v), t0, ln, att=1.1 if b == 4 else 0.7, rel=1.6, vib=0.003, voices=4, spread=7)
                add(pad, np.vstack([l, r]) * lvl * 0.5, t0)
        # ---------- cello bass line (cycles 2, 4 and the ending)
        if cyc in (2, 4) or b >= 40:
            l, r = string_note(nm(bass), t0, BAR + 0.1 if b < nb - 1 else 5.0, att=0.5, rel=1.4, vib=0.004, voices=3, spread=5)
            add(cello, np.vstack([l * 0.8, r * 1.0]) * (0.9 if cyc == 4 else 0.7), t0)

    # ---------- melodies
    def play_mel(mel, bar0, inst, vel=0.5, octave=0):
        for (bb, beat, d, note) in mel:
            st = (bar0 + bb) * BAR + beat * BEAT
            m = nm(note) + octave
            if inst == "piano":
                piano(m, st, vel * rng.uniform(0.92, 1.05), d * BEAT + 0.35)
            else:
                l, r = string_note(m, st, d * BEAT + 0.05, att=0.22, rel=0.7, vib=0.006, voices=3, spread=6)
                add(viol, np.vstack([l * 1.0, r * 0.75]) * vel, st)

    play_mel(MEL_A, 8, "piano", 0.62)                 # theme on piano
    play_mel(MEL_A, 16, "strings", 0.62)               # violins take the theme
    play_mel(MEL_B, 24, "piano", 0.55)                 # quiet variation
    play_mel(MEL_B, 32, "strings", 0.70)               # full swell
    play_mel(MEL_B, 32, "strings", 0.34, octave=-12)   # violas double an octave below
    play_mel(MEL_B, 32, "piano", 0.40, octave=12)      # piano sparkle above

    # ---------- tone shaping
    pad = lowpass(highpass(pad, 120), 2200)
    cello = lowpass(cello, 900)
    viol = lowpass(highpass(viol, 200), 3800)
    pno = lowpass(pno, 9000)

    mix = pno * 0.55 + pad * 0.32 + cello * 0.42 + viol * 0.36
    mix = mix[:, : N + SR * 4]

    # ---------- reverb (synthetic stereo hall)
    ir_len = int(3.4 * SR)
    t = np.arange(ir_len) / SR
    irs = []
    for ch in range(2):
        noise = rng.normal(0, 1, ir_len)
        noise = lowpass(noise, 6000)
        ir = noise * np.exp(-t * 2.1)
        ir[: int(0.012 * SR)] = 0
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    wet = np.vstack([fftconvolve(mix[0], irs[0])[: mix.shape[1]], fftconvolve(mix[1], irs[1])[: mix.shape[1]]])
    wet = lowpass(wet, 5000)
    out = mix * 0.78 + wet * 0.55
    out = out[:, :N]

    # ---------- master: fades, gentle limiting, normalize
    tt = np.arange(N) / SR
    fade = np.clip(tt / 1.2, 0, 1) * np.clip((TOTAL - tt) / 4.5, 0, 1) ** 1.5
    out *= fade
    out /= np.max(np.abs(out)) + 1e-9
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out *= 0.89
    return out


def write_wav(path, x):
    x16 = (np.clip(x, -1, 1) * 32767).astype(np.int16).T.copy()
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(x16.tobytes())


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    x = build()
    write_wav(os.path.join(HERE, "build", "music.wav"), x)
    print("music seconds", x.shape[1] / SR, "peak", np.abs(x).max())
