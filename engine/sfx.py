"""Sound effects, no music - every sound is synthesized here with numpy, so there is nothing to license.

User, 2026-10-23: "视频不要无声了，你给我加几个音效，但是不要配乐".

    Episode(sfx=[(scene_id, beat, kind), (scene_id, beat, kind, {"pitch": 1.12, "pan": -0.4, "gain": -2}), ...])

Put every cue ON the beat of the visual event it belongs to: the picture is cut to Episode.bpm, so the effects land
on the beat too and still fit a DJ track the user may add on top.

kinds   hit (opening impact) · whoosh (peaks ON its cue: cuts, time skips) · pop / pop_big (something appears;
        pitch= steps a sequence up) · tick (clock) · chime (a result lands) · clock (ding-dong) · sparkle (save hint) ·
        buzz (phone) · thump (sit / stand / door shut) · step (footstep) · page (book, paper) · scribble (pencil, dur=) ·
        error (a cross) · huh (question marks) · swipe (strike-through) · rise (something grows, dur=) · door (opens)
options gain (dB on top of the kind's level) · pan (-1 left .. 1 right) · pitch · dur (seconds)

Levels are set by loudness, not by ear: each kind is scaled to a target momentary loudness (ITU-R BS.1770
K-weighting, 400 ms window), so a click and a bell feel balanced. You cannot hear the result - VERIFY measures
the final file (integrated loudness, true peak, onset offset of every transient cue from its beat).
"""
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000

# target momentary loudness of one event (LUFS, mono, before panning). Each effect is soft-limited to the
# ceiling on its own, so one big peak (the opening hit) cannot force the whole track down.
TARGET = dict(hit=-12, chime=-16, clock=-17, pop_big=-17, pop=-19, whoosh=-20, buzz=-19, error=-19, huh=-21,
              thump=-20, door=-21, sparkle=-21, page=-22, rise=-22, swipe=-23, tick=-25, step=-26, scribble=-28)
TRANSIENT = {"hit", "pop", "pop_big", "tick", "chime", "clock", "sparkle", "buzz", "thump", "step", "page", "error",
             "huh", "swipe", "door"}


# ----------------------------------------------------------------------------- building blocks
def _t(d):
    return np.arange(int(round(d * SR))) / SR


def _env(t, att, tau, hold=0.0):
    return np.clip(t / max(att, 1e-5), 0, 1) * np.exp(-np.maximum(0.0, t - att - hold) / tau)


def _filt(x, kind, f, order=2):
    wn = [f[0] / (SR / 2), min(0.99, f[1] / (SR / 2))] if kind == "band" else min(0.99, f / (SR / 2))
    b, a = signal.butter(order, wn, kind)
    return signal.lfilter(b, a, x)


def _chirp(f):
    return 2 * np.pi * np.cumsum(f) / SR


def _sweep(n, rng, fc, bw=1.2):
    """noise through a band (bw octaves wide) whose centre follows fc(t) in Hz"""
    x = rng.standard_normal(n + 1024)
    f, tt, Z = signal.stft(x, SR, nperseg=512, noverlap=448)
    lf = np.log2(np.maximum(f, 20.0))[:, None]
    m = np.exp(-0.5 * ((lf - np.log2(fc(tt))[None, :]) / (bw / 2)) ** 2)
    _, y = signal.istft(Z * m, SR, nperseg=512, noverlap=448)
    return y[:n]


def _bell(t, f, tau):
    parts = ((1.0, 1.0, 1.0), (2.0, 0.4, 0.55), (2.76, 0.28, 0.4), (5.4, 0.12, 0.2))
    y = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / (tau * d)) for m, a, d in parts)
    return y * np.clip(t / 0.0015, 0, 1)


def _later(y, d_s, z):
    d = int(d_s * SR)
    out = np.zeros(len(y))
    out[d:] = z[: len(y) - d]
    return y + out


# ----------------------------------------------------------------------------- the effects
def hit(rng):
    t = _t(0.7)
    y = np.sin(_chirp(48 + 120 * np.exp(-t / 0.035))) * _env(t, 0.001, 0.22)
    y += 0.55 * _filt(rng.standard_normal(len(t)), "band", (1200, 9000)) * _env(t, 0.0004, 0.018)
    y += 0.45 * _filt(rng.standard_normal(len(t)), "band", (120, 900)) * _env(t, 0.001, 0.07)
    return y


def whoosh(rng, dur=0.45, peak=0.32):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = _sweep(n, rng, lambda tt: 350 + 2600 * np.clip(tt / peak, 0, 1) ** 1.6, 1.4)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / 0.07))
    return y * env, peak                       # the cue time is the peak (the cut)


def pop(rng, pitch=1.0, big=False):
    t = _t(0.16 if big else 0.12)
    f = 680 * pitch * (1 + 0.7 * np.exp(-t / 0.010))
    y = np.sin(_chirp(f)) * _env(t, 0.0015, 0.05 if big else 0.032)
    y += 0.35 * np.sin(_chirp(2 * f)) * _env(t, 0.001, 0.015)
    y += 0.25 * _filt(rng.standard_normal(len(t)), "high", 3000) * _env(t, 0.0003, 0.002)
    if big:
        y += 0.5 * np.sin(_chirp(220 * pitch * (1 + 0.5 * np.exp(-t / 0.02)))) * _env(t, 0.001, 0.06)
    return y


def pop_big(rng, pitch=1.0):
    return pop(rng, pitch, big=True)


def tick(rng):
    t = _t(0.05)
    y = np.sin(2 * np.pi * 2600 * t) * _env(t, 0.0003, 0.004)
    return y + 0.6 * _filt(rng.standard_normal(len(t)), "band", (2000, 8000)) * _env(t, 0.0002, 0.0015)


def chime(rng):
    t = _t(1.1)
    return _later(_bell(t, 1318.5, 0.35), 0.08, 0.85 * _bell(t, 1975.5, 0.45))


def clock(rng):
    t = _t(1.3)
    return _later(_bell(t, 1318.5, 0.4), 0.32, _bell(t, 1046.5, 0.5))


def sparkle(rng):
    t = _t(0.5)
    y = np.zeros(len(t))
    for i, f in enumerate((2637, 3136, 3520, 4186)):
        d = int(i * 0.035 * SR)
        tt = t[: len(t) - d]
        y[d:] += 0.8 ** i * np.sin(2 * np.pi * f * tt) * _env(tt, 0.001, 0.06)
    return y


def buzz(rng):
    t = _t(0.30)
    gate = np.convolve(((t % 0.15) < 0.10).astype(float), np.ones(144) / 144, "same")
    base = np.sin(2 * np.pi * 165 * t) + 0.45 * np.sign(np.sin(2 * np.pi * 165 * t))
    rattle = _filt(rng.standard_normal(len(t)), "band", (400, 2600)) * (0.5 + 0.5 * np.sin(2 * np.pi * 165 * t))
    return _filt(0.8 * base + 0.6 * rattle, "low", 3500) * gate


def thump(rng, pitch=1.0):
    t = _t(0.28)
    y = np.sin(_chirp(110 * pitch * (0.55 + 0.6 * np.exp(-t / 0.025)))) * _env(t, 0.001, 0.07)
    return y + 0.6 * _filt(rng.standard_normal(len(t)), "low", 800) * _env(t, 0.0005, 0.018)


def step(rng, pitch=1.0):
    t = _t(0.13)
    y = _filt(rng.standard_normal(len(t)), "band", (90, 1200)) * _env(t, 0.002, 0.022)
    return y + 0.6 * np.sin(2 * np.pi * 105 * pitch * t) * _env(t, 0.001, 0.035)


def page(rng):
    n = int(0.24 * SR)
    t = np.arange(n) / SR
    return _sweep(n, rng, lambda tt: 1800 + 3500 * np.clip(tt / 0.12, 0, 1), 1.2) * _env(t, 0.008, 0.06)


def scribble(rng, dur=2.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = _filt(rng.standard_normal(n), "band", (2500, 9500))
    env, pos = np.zeros(n), 0
    while pos < n:
        ln, gap = int(rng.uniform(0.06, 0.15) * SR), int(rng.uniform(0.02, 0.07) * SR)
        seg = np.sin(np.linspace(0, np.pi, ln)) ** 0.7 * rng.uniform(0.6, 1.0)
        m = max(0, min(ln, n - pos))
        env[pos: pos + m] = seg[:m]
        pos += ln + gap
    env *= 0.8 + 0.2 * np.sin(2 * np.pi * 31 * t)
    return x * env * np.clip(np.minimum(t, dur - t) / 0.03, 0, 1)


def error(rng):
    def tone(t, f):
        return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 3 * f * t)) * _env(t, 0.002, 0.05)
    return np.concatenate([tone(_t(0.09), 330), tone(_t(0.14), 233)])


def huh(rng):
    t = _t(0.22)
    f = 480 + 330 * np.clip(t / 0.16, 0, 1) ** 1.5
    y = np.sin(_chirp(f)) + 0.25 * np.sin(_chirp(2 * f))
    return y * np.clip(t / 0.01, 0, 1) * np.exp(-np.maximum(0, t - 0.12) / 0.04)


def swipe(rng):
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    return _sweep(n, rng, lambda tt: 1200 + 5000 * np.clip(tt / 0.1, 0, 1), 1.0) * _env(t, 0.004, 0.04)


def rise(rng, dur=0.94):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = _sweep(n, rng, lambda tt: 400 + 2200 * np.clip(tt / dur, 0, 1) ** 1.3, 1.2)
    y = y / (np.max(np.abs(y)) + 1e-9) + 0.5 * np.sin(_chirp(300 + 450 * (t / dur) ** 1.4))
    return y * (t / dur) ** 1.5 * np.clip((dur - t) / 0.03, 0, 1)


def door(rng):
    t = _t(0.45)
    click = _filt(rng.standard_normal(len(t)), "band", (1500, 7000)) * _env(t, 0.0003, 0.006)
    sw = _sweep(len(t), rng, lambda tt: 250 + 700 * np.clip(tt / 0.35, 0, 1), 1.3)
    sw = sw / (np.max(np.abs(sw)) + 1e-9) * np.sin(np.pi * np.clip(t / 0.42, 0, 1)) ** 1.5
    return 0.7 * click / (np.max(np.abs(click)) + 1e-9) + 0.6 * sw


KINDS = dict(hit=hit, whoosh=whoosh, pop=pop, pop_big=pop_big, tick=tick, chime=chime, clock=clock, sparkle=sparkle,
             buzz=buzz, thump=thump, step=step, page=page, scribble=scribble, error=error, huh=huh, swipe=swipe,
             rise=rise, door=door)


# ----------------------------------------------------------------------------- loudness (ITU-R BS.1770, 48 kHz)
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def momentary_max(y):
    """loudest 400 ms window of a mono signal, in LUFS"""
    k = signal.lfilter(*_K2, signal.lfilter(*_K1, np.concatenate([y, np.zeros(int(0.4 * SR))])))
    w = int(0.4 * SR)
    ms = np.convolve(k * k, np.ones(w) / w, "valid")
    return -0.691 + 10 * np.log10(max(float(ms.max()), 1e-12))


def soft_limit(y, ceiling_db):
    """linear below 60% of the ceiling, then a tanh knee that never exceeds it"""
    c = 10 ** (ceiling_db / 20)
    k = 0.6 * c
    a = np.abs(y)
    over = a > k
    out = y.copy()
    out[over] = np.sign(y[over]) * (k + (c - k) * np.tanh((a[over] - k) / (c - k)))
    return out


def true_peak_db(x):
    up = signal.resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(max(float(np.max(np.abs(up))), 1e-12))


# ----------------------------------------------------------------------------- mix
def render(cues, duration, path, seed=5, ceiling_db=-1.5):
    """cues: [(t_seconds, kind, opts)] -> stereo 48 kHz WAV of exactly `duration` seconds. Returns stats."""
    rng = np.random.default_rng(seed)
    n = int(round(duration * SR))
    mix = np.zeros((n, 2))
    used = {}
    for t0, kind, o in sorted(cues, key=lambda c: c[0]):
        if kind not in KINDS:
            raise ValueError(f"unknown sfx kind {kind!r}; choose from {sorted(KINDS)}")
        args = {k: v for k, v in o.items() if k in ("pitch", "dur")}
        out = KINDS[kind](rng, **args)
        y, off = out if isinstance(out, tuple) else (out, 0.0)
        y = y / (np.max(np.abs(y)) + 1e-9)
        for _ in range(2):                                       # level -> limit -> re-level (limiting costs loudness)
            y *= 10 ** ((TARGET[kind] + o.get("gain", 0.0) - momentary_max(y)) / 20)
            y = soft_limit(y, ceiling_db - 1.0)
        th = (o.get("pan", 0.0) + 1) * np.pi / 4
        gl, gr = min(1.0, np.sqrt(2) * np.cos(th)), min(1.0, np.sqrt(2) * np.sin(th))   # balance law: never louder
        start = int(round((t0 - off) * SR))
        s0, s1 = max(0, start), min(n, start + len(y))
        if s1 <= s0:
            continue
        seg = y[s0 - start: s1 - start]
        mix[s0:s1, 0] += seg * gl
        mix[s0:s1, 1] += seg * gr
        used[kind] = used.get(kind, 0) + 1
    b, a = signal.butter(2, 30 / (SR / 2), "high")               # no DC / sub rumble
    mix = soft_limit(signal.lfilter(b, a, mix, axis=0), ceiling_db - 0.5)   # bus: only overlaps reach the knee
    tp = true_peak_db(mix)
    trim = min(0.0, ceiling_db - tp)                             # only ever turn down
    mix *= 10 ** (trim / 20)
    sf.write(path, mix.astype(np.float32), SR, subtype="PCM_24")
    return dict(events=sum(used.values()), kinds=used, true_peak_db=tp + trim, trim_db=trim)


def onset_offsets(x, cues, sr=SR):
    """for every transient cue: time of the steepest level rise within -30..+40 ms of the cue, minus the cue (s)"""
    hop = sr // 500                                              # 2 ms
    m = len(x) // hop
    e = np.sqrt(np.mean(x[: m * hop].reshape(m, hop) ** 2, axis=1) + 1e-12)
    le = 20 * np.log10(e)
    rise_ = np.maximum(0, np.diff(le, prepend=le[0]))
    offs = []
    for t0, kind, _ in cues:
        if kind not in TRANSIENT:
            continue
        i0, i1 = max(0, int((t0 - 0.03) * 500)), int((t0 + 0.04) * 500)
        if i1 <= i0 or i0 >= len(rise_):
            continue
        offs.append((int(np.argmax(rise_[i0:i1])) + i0) / 500 - t0)
    return np.array(offs), float(np.mean(le > -50))
