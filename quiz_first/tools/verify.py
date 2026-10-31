"""Numbers instead of eyes / ears for the finished MP4 (the agent can neither watch nor hear it).

    .venv/bin/python tools/verify.py out/先看书还是先做题_75s_1080p.mp4

- format:    duration, size, resolution, fps (from ffmpeg's stream info)
- loudness:  integrated loudness (BS.1770, same code as tools/audio.py) and true peak (4x oversampled) of the MP4's audio
- sfx:       every prominent cue (gain >= -16 dB) is found as an onset in the MP4 audio; offset from its beat (ms)
- rhythm:    share of picture events (frames where a lot starts changing) within 2 frames of the half-beat grid (>= 80 %)
- shake:     extra change on the beat in areas that are still just before and after it, in gray levels (< 1.0;
             the engine's stable videos measure 0.04-0.09, the rejected beat-zoom 7.4-8.0)
Same method as the checks in the Skill (references/engine.md); written for this episode's renderer.
"""
import re
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


def stream_info(mp4):
    err = subprocess.run([ffmpeg(), '-hide_banner', '-i', mp4], capture_output=True, text=True).stderr
    dur = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    vid = re.search(r'Video: (\w+).*?, (\d{3,5})x(\d{3,5}).*?, ([\d.]+) fps', err)
    aud = re.search(r'Audio: (\w+).*?, (\d+) Hz', err)
    secs = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3))
    return secs, vid.groups() if vid else None, aud.groups() if aud else None


def decode_audio(mp4, ch=1):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', mp4, '-f', 'f32le', '-ac', str(ch), '-ar', str(A.SR), '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return x if ch == 1 else x.reshape(-1, ch).T


def decode_gray(mp4):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', mp4, '-vf', f'scale={W}:{H},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W).astype(np.int16)


def true_peak(L, R):
    """4x oversampled peak (FFT interpolation) in dBTP."""
    pk = 0.0
    for x in (L, R):
        n = len(x)
        X = np.fft.rfft(x)
        Y = np.zeros(2 * n + 1, dtype=complex)
        Y[: len(X)] = X
        y = np.fft.irfft(Y, 4 * n) * 4
        pk = max(pk, np.max(np.abs(y)))
    return 20 * np.log10(pk)


def sfx_check(x):
    """Onset = first sample where the 2 ms envelope rises 4x above the median of the 20 ms before it, searched +-60 ms
    around a cue. Only prominent cues (>= -16 dB) with no other cue in the 80 ms before them."""
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
        c = int(round(t * A.SR))
        lo, hi = max(960, c - int(0.06 * A.SR)), min(len(x) - 1, c + int(0.06 * A.SR))
        for i in range(lo, hi, 24):
            if env[i] > 4 * np.median(env[i - 960:i - 96]) and env[i] > 1e-3:
                offs.append((i - c) / A.SR * 1000)
                break
    offs = np.array(offs)
    return len(offs), float(np.median(offs)), float(np.percentile(np.abs(offs), 90))


def picture_checks(f):
    d = np.abs(np.diff(f, axis=0))                     # d[i] = change from frame i to i+1
    changed = (d > 8).mean(axis=(1, 2))
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
    secs, vid, aud = stream_info(mp4)
    size = Path(mp4).stat().st_size / 1e6
    ok_fmt = abs(secs - 75) < 0.05 and vid and vid[1:3] == ('1920', '1080') and abs(float(vid[3]) - 30) < 0.01 and size < 95
    print(f'format  {secs:.3f} s, {size:.1f} MB, video {vid[0]} {vid[1]}x{vid[2]} {vid[3]} fps, audio {aud[0]} {aud[1]} Hz  {"OK" if ok_fmt else "CHECK"}')
    L, R = decode_audio(mp4, 2)
    lu, tp = A.lufs(L, R), true_peak(L, R)
    print(f'loud    {lu:.1f} LUFS (target {A.TARGET_LUFS}), true peak {tp:.1f} dBTP  {"OK" if abs(lu - A.TARGET_LUFS) < 0.6 and tp <= -1.0 else "CHECK"}')
    n, med, p90 = sfx_check((L + R) / 2)
    print(f'sfx     {n} prominent cues found in the MP4 audio; onset vs beat: median {med:+.1f} ms, 90 % within {p90:.1f} ms')
    nev, share, shake, shake_max = picture_checks(decode_gray(mp4))
    print(f'rhythm  {nev} picture events, {share * 100:.0f} % within 2 frames of the half-beat grid  {"OK" if share >= 0.8 else "CHECK"}')
    print(f'shake   extra change on the beat in still areas: mean {shake:.2f}, max {shake_max:.2f} gray levels  {"stable" if shake < 1.0 else "SHAKES"}')
