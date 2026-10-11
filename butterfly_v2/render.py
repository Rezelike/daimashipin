"""Style preview: render the new 12 s opening in three themes.

python render.py                          -> out/开场_<纸张|纯白|深色>_<有配乐|无配乐>.mp4
python render.py --stills 3.0 6.5 11.5    -> out/preview/<theme>_<t>.png
python render.py --theme dark             -> one theme only
"""
import argparse
import os
import subprocess
import time

import imageio_ffmpeg
import skia

import music
from opening import Opening, END
from theme import THEMES, W, H, FPS

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT, BUILD = os.path.join(ROOT, 'out'), os.path.join(ROOT, 'build')
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def render_video(scene, th, wavs, paths):
    silent = os.path.join(BUILD, f'{th.name}_silent.mp4')
    surface = skia.Surface(W, H)
    c = surface.getCanvas()
    proc = subprocess.Popen([FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba',
                             '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow',
                             '-crf', '16', '-pix_fmt', 'yuv420p', silent], stdin=subprocess.PIPE)
    for i in range(int(END * FPS)):
        scene.draw(c, th, i / FPS)
        proc.stdin.write(surface.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    proc.stdin.close()
    if proc.wait():
        raise SystemExit('ffmpeg failed')
    for wav, path in zip(wavs, paths):
        subprocess.run([FFMPEG, '-y', '-loglevel', 'error', '-i', silent, '-i', wav, '-c:v', 'copy', '-c:a', 'aac',
                        '-b:a', '256k', '-shortest', '-movflags', '+faststart', path], check=True)
        print('wrote', path, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stills', nargs='*', type=float)
    ap.add_argument('--theme', choices=list(THEMES))
    args = ap.parse_args()
    t0 = time.time()
    scene = Opening()
    themes = [THEMES[args.theme]] if args.theme else list(THEMES.values())
    if args.stills is not None:
        os.makedirs(f'{OUT}/preview', exist_ok=True)
        surface = skia.Surface(W, H)
        for th in themes:
            for ts in args.stills:
                scene.draw(surface.getCanvas(), th, ts)
                surface.makeImageSnapshot().save(f'{OUT}/preview/{th.name}_{ts:05.2f}s.png', skia.kPNG)
        print('stills done')
        return
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    wavs = [music.build(scene, os.path.join(BUILD, 'with_music.wav'), with_music=True),
            music.build(scene, os.path.join(BUILD, 'sfx_only.wav'), with_music=False)]
    for th in themes:
        render_video(scene, th, wavs, [os.path.join(OUT, f'开场_{th.label}_有配乐.mp4'),
                                       os.path.join(OUT, f'开场_{th.label}_无配乐.mp4')])
    print(f'done in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
