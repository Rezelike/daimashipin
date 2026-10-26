"""One cover picture for Douyin.

Douyin's publish page keeps a single cover image and crops both the 3:4 竖封面 (profile grid) and the 4:3 横封面 from it
(user, 2026-10-26: "横版和竖版不能同时用，只能是一张图片"). This turns a finished 3:4 cover into one 4:3 picture:
the centred 3:4 crop is the cover pixel for pixel, the bands on both sides only continue its dark background
(edge colour of each row, smoothed vertically, fading to 35 %).

    python tools/one_cover.py IN.png OUT.png [--preview PREVIEW.png] [--shrink 0.94]

IN       the 3:4 cover (any size, scaled to 1080x1440)
--shrink scale the picture down, anchored at the top, so labels near the bottom clear the play count that Douyin draws
         in the profile grid (x 7-42 %, y 88.5-95 % of a tile); the freed edges are mirrored, the bottom strip fades a little
OUT      1920x1440
PREVIEW  the whole picture (= 横封面) with the 竖封面 crop marked in yellow, next to the 竖封面 itself
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

import numpy as np

W, H, OW = 1080, 1440, 1920
PAD = (OW - W) // 2  # 420 px on each side


def ffmpeg():
    if os.environ.get('FFMPEG'):
        return os.environ['FFMPEG']
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        exe = shutil.which('ffmpeg')
        if not exe:
            sys.exit('ffmpeg not found: set FFMPEG or pip install imageio-ffmpeg')
        return exe


def to_u8(a):
    return np.clip(a + 0.5, 0, 255).astype(np.uint8)


def read_cover(path):
    info = subprocess.run([ffmpeg(), '-hide_banner', '-i', path], capture_output=True, text=True).stderr
    m = re.search(r'Video: .*?(\d{2,5})x(\d{2,5})', info)
    if not m:
        sys.exit(f'cannot read {path}')
    w, h = int(m.group(1)), int(m.group(2))
    if abs(w / h - W / H) > 0.01:
        sys.exit(f'{path} is {w}x{h}, not 3:4')
    vf = [] if (w, h) == (W, H) else ['-vf', f'scale={W}:{H}:flags=lanczos']
    raw = subprocess.check_output([ffmpeg(), '-v', 'error', '-i', path, *vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32)


def resize(a, w, h):
    raw = subprocess.run([ffmpeg(), '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{a.shape[1]}x{a.shape[0]}',
                          '-i', '-', '-vf', f'scale={w}:{h}:flags=lanczos', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         input=to_u8(a).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3).astype(np.float32)


def write_png(a, path):
    h, w = a.shape[:2]
    subprocess.run([ffmpeg(), '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{w}x{h}', '-i', '-',
                    '-frames:v', '1', path], input=to_u8(a).tobytes(), check=True)


def shrink(a, f):
    """scale down to f, anchored at the top; mirror the freed side edges, mirror + fade the freed bottom strip"""
    cw = int(round(W * f / 2)) * 2
    ch = int(round(cw * H / W))
    x0 = (W - cw) // 2
    out = np.pad(resize(a, cw, ch), ((0, H - ch), (x0, W - cw - x0), (0, 0)), mode='reflect')
    k = np.arange(H - ch, dtype=np.float32) / max(1, H - ch - 1)
    out[ch:] *= (1 - 0.45 * k ** 1.5)[:, None, None]
    return out


def smooth_rows(a, sigma):
    r = int(3 * sigma)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    p = np.pad(a, ((r, r), (0, 0)), mode='reflect')
    return np.stack([np.convolve(p[:, c], k, mode='valid') for c in range(a.shape[1])], axis=1)


def side(cover, right):
    """H x PAD x 3 band that continues one side edge; column 0 touches the cover"""
    cols = cover[:, -24:] if right else cover[:, :24]
    edge = cover[:, -1] if right else cover[:, 0]
    soft = smooth_rows(np.median(cols, axis=1), 24)
    d = np.arange(1, PAD + 1, dtype=np.float32)
    t = np.clip(d / 48, 0, 1)
    t = t * t * (3 - 2 * t)                    # the edge column itself -> its smoothed colour within 48 px
    k = 0.35 + 0.65 * np.exp(-d / 220)         # then fade toward 35 % (vignette)
    band = edge[:, None] * (1 - t)[None, :, None] + soft[:, None] * t[None, :, None]
    return band * k[None, :, None]


def luma(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def preview(one, path):
    def half(a):
        return a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2, 3).mean(axis=(1, 3))
    full, crop = half(one), half(one[:, PAD:PAD + W])
    x0, x1, yel = PAD // 2, (PAD + W) // 2 - 1, np.array([247, 185, 62], np.float32)
    full[:, x0:x0 + 4] = yel
    full[:, x1 - 3:x1 + 1] = yel
    full[:4, x0:x1 + 1] = yel
    full[-4:, x0:x1 + 1] = yel
    gap = 28
    canvas = np.empty((full.shape[0], full.shape[1] + gap + crop.shape[1], 3), np.float32)
    canvas[:] = (5, 7, 13)
    canvas[:, :full.shape[1]] = full
    canvas[:, full.shape[1] + gap:] = crop
    write_png(canvas, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('src')
    ap.add_argument('out')
    ap.add_argument('--preview')
    ap.add_argument('--shrink', type=float, default=1.0)
    a = ap.parse_args()

    cover = read_cover(a.src)
    if a.shrink < 1:
        cover = shrink(cover, a.shrink)
    one = np.concatenate([side(cover, False)[:, ::-1], cover, side(cover, True)], axis=1)
    write_png(one, a.out)

    # checks
    Y, cY = luma(one), luma(cover)
    same = np.array_equal(to_u8(one[:, PAD:PAD + W]), to_u8(cover))
    seam = max(np.abs(Y[:, PAD - 1] - Y[:, PAD]).mean(), np.abs(Y[:, PAD + W - 1] - Y[:, PAD + W]).mean())
    inner = np.abs(np.diff(cY[:, :24], axis=1)).mean()
    side_max = max(Y[:, :PAD].max(), Y[:, PAD + W:].max())
    bright = np.nonzero((cY > 120).any(axis=0))[0]
    zone = cY[int(H * 0.86):int(H * 0.97), int(W * 0.05):int(W * 0.45)]
    print(f'wrote {a.out}: {OW}x{H}; 竖封面 = centre {W}x{H} at x {PAD}-{PAD + W - 1}, identical to the cover: {same}')
    print(f'  seam step {seam:.2f} (neighbour step inside the cover {inner:.2f}); side bands max luma {side_max:.1f}')
    if len(bright):
        print(f'  bright content in the 竖封面 x {bright.min()}-{bright.max()} (margins {bright.min()} / {W - 1 - bright.max()} px)')
    print(f'  play-count zone of the 竖封面: {int((zone > 120).sum())} bright px')
    if a.preview:
        preview(one, a.preview)
        print(f'wrote {a.preview}')


if __name__ == '__main__':
    main()
