"""Numbers instead of eyes/ears for the finished MP4 (the agent can neither watch nor hear it).

    .venv/bin/python tools/verify.py out/记忆宫殿真的有用吗_75s_1080p.mp4

(copied from music_study/tools/verify.py on the music-study branch, PR #22; added the lufs / true-peak line)

- sfx:    every prominent cue (gain >= -16 dB) is found as an onset in the decoded MP4 audio; offset from its beat (ms)
- rhythm: share of picture events (frames where a lot starts changing) within 2 frames of the half-beat grid (>= 80 %)
- lufs:   integrated loudness of the MP4's stereo audio (BS.1770, as audio.py) and its true peak (4x oversampled)
- shake:  extra change on the beat in areas that are still just before and after it, in gray levels (< 1.0;
          the engine's stable videos measure 0.04-0.09, the rejected beat-zoom 7.4-8.0)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio as A  # noqa: E402

FPS, W, H = 30, 480, 270
BEAT = A.BEAT


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode_audio(mp4):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', mp4, '-f', 'f32le', '-ac', '1', '-ar', str(A.SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def decode_gray(mp4):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', mp4, '-vf', f'scale={W}:{H},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W).astype(np.int16)


def decode_stereo(mp4):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', mp4, '-f', 'f32le', '-ac', '2', '-ar', str(A.SR), '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64).reshape(-1, 2)
    return x[:, 0], x[:, 1]


def true_peak(x, k=4):
    """Peak of the k-times oversampled signal (FFT interpolation, in 10 s blocks with overlap), dBTP."""
    best, n, blk, pad = 0.0, len(x), A.SR * 10, 4800
    for st in range(0, n, blk):
        a, b = max(0, st - pad), min(n, st + blk + pad)
        seg = x[a:b]
        X = np.fft.rfft(seg)
        up = np.fft.irfft(np.concatenate([X, np.zeros(len(seg) * (k - 1) // 2 + 1)]), len(seg) * k) * k
        best = max(best, np.max(np.abs(up)))
    return 20 * np.log10(best + 1e-12)


def sfx_check(x):
    """Onset = first sample where the 2 ms envelope rises 12 dB above the 20 ms before it, searched +-60 ms around a cue.
    Only prominent cues (>= -16 dB) with no other cue in the 80 ms before them (else the onset belongs to that one)."""
    env = np.sqrt(np.convolve(x * x, np.ones(96) / 96, mode='same')) + 1e-9
    offs = []
    allc = A.cues()
    starts = sorted(b * BEAT for b, *_ in allc)
    for b, s, g, p in allc:
        if g < -16 or b < 0:
            continue
        t = b * BEAT
        if any(t - 0.08 < u < t - 1e-6 for u in starts):
            continue
        c = int(round(b * BEAT * A.SR))
        lo, hi = max(960, c - int(0.06 * A.SR)), min(len(x) - 1, c + int(0.06 * A.SR))
        found = None
        for i in range(lo, hi, 24):
            if env[i] > 4 * np.median(env[i - 960:i - 96]) and env[i] > 1e-3:
                found = i
                break
        if found is not None:
            offs.append((found - c) / A.SR * 1000)
    offs = np.array(offs)
    return len(offs), np.median(offs), np.percentile(np.abs(offs), 90)


def picture_checks(f):
    d = np.abs(np.diff(f, axis=0))                     # d[i] = change from frame i to i+1
    changed = (d > 8).mean(axis=(1, 2))
    # rhythm: where a burst of change STARTS (rising edge above the threshold); the peak of a growing element lags
    # its start by a few frames, the start is what has to be on the beat
    base = np.array([np.median(changed[max(0, i - 6):i]) if i > 0 else 0 for i in range(len(changed))])
    flux = np.maximum(0, changed - base)
    thr = max(0.002, np.percentile(flux, 85))
    ev = [i for i in range(1, len(flux)) if flux[i] > thr and flux[i - 1] <= thr]
    ev2 = []
    for i in ev:
        if not ev2 or i - ev2[-1] >= 4:
            ev2.append(i)
    grid = BEAT / 2
    on = [abs(((i + 1) / FPS) / grid - round(((i + 1) / FPS) / grid)) * grid * FPS <= 2.0 for i in ev2]
    # shake: still areas around each beat
    extra = []
    for k in range(1, int(75 / BEAT)):
        b = int(round(k * BEAT * FPS)) - 1
        if b < 4 or b + 4 >= len(d):
            continue
        still = (d[b - 3] < 2) & (d[b + 3] < 2) & (d[b - 2] < 2)
        if still.mean() < 0.2:
            continue
        extra.append(d[b][still].mean() - d[b - 2][still].mean())
    return len(ev2), float(np.mean(on)), float(np.mean(extra)), float(np.max(extra))


if __name__ == '__main__':
    mp4 = sys.argv[1]
    L, R = decode_stereo(mp4)
    print(f'lufs    {A.lufs(L, R):.1f} LUFS integrated, true peak {max(true_peak(L), true_peak(R)):.1f} dBTP')
    n, med, p90 = sfx_check(decode_audio(mp4))
    print(f'sfx     {n} prominent cues found in the MP4 audio; onset vs beat: median {med:+.1f} ms, 90 % within {p90:.1f} ms')
    nev, share, shake, shake_max = picture_checks(decode_gray(mp4))
    print(f'rhythm  {nev} picture events, {share * 100:.0f} % within 2 frames of the half-beat grid  {"OK" if share >= 0.8 else "CHECK"}')
    print(f'shake   extra change on the beat in still areas: mean {shake:.2f}, max {shake_max:.2f} gray levels  {"stable" if shake < 1.0 else "SHAKES"}')
