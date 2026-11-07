"""Numbers instead of eyes and ears for the finished MP4 (the agent can neither watch nor hear it).

    .venv/bin/python tools/verify.py out/单词卡分小叠背更好_75s_1080p.mp4

- file:      duration, size, fps, resolution, codecs (from ffmpeg's stream info)
- loudness:  integrated loudness (BS.1770, gated) and true peak (4x oversampled) of the decoded AAC
- sfx:       every prominent cue (gain >= -16 dB) is found as an onset in the decoded audio; offset from its beat (ms)
- cuts:      the biggest picture changes around each section start (8.0 / 15 / 30 / 45 / 60 s) sit on that bar line
- rhythm:    share of picture events (frames where a lot starts changing) within 2 frames of the half-beat grid (>= 80 %)
- shake:     extra change ON the beat in areas that are still just before and after it, in gray levels (< 1.0; the engine's
             stable videos measure 0.04-0.09, the rejected beat-zoom 7.4-8.0)
- figure:    frames in which the figure was not drawn (build/frame_check.json from render.mjs --all; should be 0)
Copied from read_aloud/tools/verify.py (PR #27); method of sfx / rhythm / shake as in music_study/tools/verify.py (PR #22);
the figure line as in nap_length/tools/verify.py (PR #26).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio as A  # noqa: E402

FPS, W, H = 30, 480, 270
BEAT = A.BEAT
SECTION_BEATS = (17, 32, 64, 96, 128)


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def file_info(mp4):
    err = subprocess.run([ffmpeg(), '-hide_banner', '-i', mp4], capture_output=True, text=True).stderr
    dur = re.search(r'Duration: (\d+):(\d+):([\d.]+)', err)
    secs = int(dur[1]) * 3600 + int(dur[2]) * 60 + float(dur[3])
    v = re.search(r'Video: (\w+).*?, (\d+)x(\d+).*?, ([\d.]+) fps', err)
    a = re.search(r'Audio: (\w+).*?, (\d+) Hz, (\w+)', err)
    return secs, Path(mp4).stat().st_size / 1e6, v[1], int(v[2]), int(v[3]), float(v[4]), a[1], int(a[2]), a[3]


def decode_audio(mp4, ch=2):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', mp4, '-f', 'f32le', '-ac', str(ch), '-ar', str(A.SR), '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return x.reshape(-1, ch).T if ch > 1 else x


def true_peak(x):
    """4x oversampling by FFT zero-padding (enough to catch inter-sample peaks of these effects)."""
    n = len(x)
    X = np.fft.rfft(x)
    Y = np.zeros(2 * n + 1, dtype=complex)
    Y[: len(X)] = X
    y = np.fft.irfft(Y, 4 * n) * 4
    return 20 * np.log10(np.max(np.abs(y)) + 1e-12)


def decode_gray(mp4):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-i', mp4, '-vf', f'scale={W}:{H},format=gray', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, H, W).astype(np.int16)


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
        found = None
        for i in range(lo, hi, 24):
            if env[i] > 4 * np.median(env[i - 960:i - 96]) and env[i] > 1e-3:
                found = i
                break
        if found is not None:
            offs.append((found - c) / A.SR * 1000)
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
    # section cuts: the frame with the most change within +-1 beat of each section start, distance from the bar line
    cuts = []
    for sb in SECTION_BEATS:
        c = sb * BEAT * FPS
        lo, hi = int(c - BEAT * FPS), int(c + BEAT * FPS)
        k = lo + int(np.argmax(changed[lo:hi]))
        cuts.append(((k + 1) - c) / FPS * 1000)
    return len(ev2), float(np.mean(on)), float(np.mean(extra)), float(np.max(extra)), cuts


if __name__ == '__main__':
    mp4 = sys.argv[1]
    secs, mb, vc, w, h, fps, ac, sr, layout = file_info(mp4)
    ok = abs(secs - 75) < 0.05 and (w, h) == (1920, 1080) and abs(fps - 30) < 0.01 and mb < 95
    print(f'file    {secs:.3f} s, {w}x{h}, {fps:g} fps, {vc} + {ac} {sr} Hz {layout}, {mb:.1f} MB  {"OK" if ok else "CHECK"}')
    L, R = decode_audio(mp4)
    lu = A.lufs(L, R)
    tp = max(true_peak(L), true_peak(R))
    print(f'lufs    {lu:.1f} LUFS integrated (target {A.TARGET_LUFS}), true peak {tp:.1f} dBTP  {"OK" if abs(lu - A.TARGET_LUFS) < 0.5 and tp <= -1 else "CHECK"}')
    n, med, p90 = sfx_check((L + R) / 2)
    print(f'sfx     {n} prominent cues found in the MP4 audio; onset vs beat: median {med:+.1f} ms, 90 % within {p90:.1f} ms')
    nev, share, shake, shake_max, cuts = picture_checks(decode_gray(mp4))
    print(f'cuts    biggest change near each section start (8 / 15 / 30 / 45 / 60 s), ms from the bar line: '
          + ', '.join(f'{c:+.0f}' for c in cuts))
    print(f'rhythm  {nev} picture events, {share * 100:.0f} % within 2 frames of the half-beat grid  {"OK" if share >= 0.8 else "CHECK"}')
    print(f'shake   extra change on the beat in still areas: mean {shake:.2f}, max {shake_max:.2f} gray levels  {"stable" if shake < 1.0 else "SHAKES"}')
    fc = Path(__file__).resolve().parent.parent / 'build/frame_check.json'
    if fc.exists():
        miss = json.loads(fc.read_text())['framesWithoutHero']
        print(f'figure  frames without the figure: {len(miss)}  {"OK" if not miss else "CHECK"}')
