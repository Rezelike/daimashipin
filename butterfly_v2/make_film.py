"""Render the full film (paper theme by default).

python make_film.py                         -> out/全片_纸张_有配乐.mp4, out/全片_纸张_无配乐.mp4
python make_film.py --stills 14 18 22       -> out/preview/全片_<t>s.png (full size)
python make_film.py --sheet 14 18 22 26     -> build/sheet.png (small contact sheet for quick checks)
python make_film.py --range 12 25           -> build/range.mp4 (silent, only that time range)
"""
import argparse
import os
import subprocess
import time

import imageio_ffmpeg
import skia

from film import Film
from theme import THEMES, W, H, FPS

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT, BUILD = os.path.join(ROOT, 'out'), os.path.join(ROOT, 'build')
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def encode(film, th, path, t_from, t_to):
    surface = skia.Surface(W, H)
    c = surface.getCanvas()
    proc = subprocess.Popen([FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba',
                             '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow',
                             '-crf', '16', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for i in range(int(round(t_from * FPS)), int(round(t_to * FPS))):
        film.draw(c, th, i / FPS)
        proc.stdin.write(surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise SystemExit('ffmpeg failed')


def sheet(film, th, times, path, cell_w=270):
    cell_h = cell_w * H // W
    cols = min(len(times), 6)
    rows = (len(times) + cols - 1) // cols
    big = skia.Surface(W, H)
    out = skia.Surface(cols * cell_w, rows * cell_h)
    oc = out.getCanvas()
    oc.clear(skia.ColorWHITE)
    for k, t in enumerate(times):
        film.draw(big.getCanvas(), th, t)
        x, y = (k % cols) * cell_w, (k // cols) * cell_h
        oc.drawImageRect(big.makeImageSnapshot(), skia.Rect.MakeXYWH(x, y, cell_w, cell_h),
                         skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    out.makeImageSnapshot().save(path, skia.kPNG)
    print('sheet', path, f'{cols * cell_w}x{rows * cell_h}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--theme', choices=list(THEMES), default='paper')
    ap.add_argument('--stills', nargs='*', type=float)
    ap.add_argument('--sheet', nargs='*', type=float)
    ap.add_argument('--sheet-out', default=os.path.join(BUILD, 'sheet.png'))
    ap.add_argument('--cell', type=int, default=270)
    ap.add_argument('--range', nargs=2, type=float)
    args = ap.parse_args()
    t0 = time.time()
    th = THEMES[args.theme]
    film = Film()
    os.makedirs(BUILD, exist_ok=True)
    if args.sheet is not None:
        sheet(film, th, args.sheet, args.sheet_out, args.cell)
        return
    if args.stills is not None:
        os.makedirs(f'{OUT}/preview', exist_ok=True)
        surface = skia.Surface(W, H)
        for ts in args.stills:
            film.draw(surface.getCanvas(), th, ts)
            surface.makeImageSnapshot().save(f'{OUT}/preview/全片_{ts:05.2f}s.png', skia.kPNG)
        print('stills done')
        return
    if args.range:
        encode(film, th, os.path.join(BUILD, 'range.mp4'), *args.range)
        print('wrote build/range.mp4', f'in {time.time() - t0:.0f}s')
        return

    import score
    os.makedirs(OUT, exist_ok=True)
    silent = os.path.join(BUILD, f'film_{th.name}_silent.mp4')
    encode(film, th, silent, 0, film.end)
    print(f'video encoded in {time.time() - t0:.0f}s', flush=True)
    for with_music, tag in ((True, '有配乐'), (False, '无配乐')):
        wav = score.build(film, os.path.join(BUILD, f'film_{tag}.wav'), with_music=with_music)
        path = os.path.join(OUT, f'全片_{th.label}_{tag}.mp4')
        subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac',
                        '-b:a', '256k', '-shortest', '-movflags', '+faststart', path], check=True)
        print('wrote', path, flush=True)
    print(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
