"""Build the full butterfly-effect short video (~86 s).

python render.py                      -> out/蝴蝶效应_有配乐.mp4 + out/蝴蝶效应_无配乐.mp4
python render.py --stills 1.9 7.5 ... -> PNG previews in out/preview/
"""
import os
import subprocess
import sys
import time

import imageio_ffmpeg
import skia

import audio
from common import W, H, FPS
from video import Video, END

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'out')
BUILD = os.path.join(ROOT, 'build')
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def render_stills(part, times):
    os.makedirs(f'{OUT}/preview', exist_ok=True)
    surface = skia.Surface(W, H)
    for ts in times:
        part.draw(surface.getCanvas(), ts)
        surface.makeImageSnapshot().save(f'{OUT}/preview/frame_{ts:05.2f}s.png', skia.kPNG)
    print('stills written to', f'{OUT}/preview')


def render_silent(part, path):
    surface = skia.Surface(W, H)
    c = surface.getCanvas()
    proc = subprocess.Popen([
        FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}',
        '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
        '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    n = int(END * FPS)
    for i in range(n):
        part.draw(c, i / FPS)
        proc.stdin.write(surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
        if i % 300 == 0:
            print(f'  frame {i}/{n}', flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit('ffmpeg failed')


def mux(video, wav, out):
    subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', video, '-i', wav, '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out)


def main():
    t0 = time.time()
    part = Video()
    print(f'physics simulated in {time.time() - t0:.1f}s', flush=True)
    if len(sys.argv) > 1 and sys.argv[1] == '--stills':
        render_stills(part, [float(x) for x in sys.argv[2:]])
        return
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    full_wav, sfx_wav = audio.build(BUILD, part)
    silent = os.path.join(BUILD, 'silent.mp4')
    print('rendering frames ...', flush=True)
    render_silent(part, silent)
    mux(silent, full_wav, os.path.join(OUT, '蝴蝶效应_有配乐.mp4'))
    mux(silent, sfx_wav, os.path.join(OUT, '蝴蝶效应_无配乐.mp4'))
    print(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
