"""Build the ISU-152 diesel video (1080x1920, 30 fps, 26.25 s, sound effects only, cut to 128 BPM).

    V=/projects/sandbox/.videoenv/vpy                       # bash .kiro/skills/vibe-knowledge-video/scripts/setup_env.sh
    $V isu152_diesel/render.py --preview                    # build/preview.png (24 numbered frames) + text lint
    $V isu152_diesel/render.py --stills 0,8.44              # single frames -> build/stills/
    $V isu152_diesel/render.py --audio                      # sound only, swapped into the existing MP4
    $V isu152_diesel/render.py                              # out/ISU-152柴油机_26s_1080x1920.mp4 + VERIFY
"""
import argparse
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, REPO)
import mech as M          # noqa: E402
import art as A           # noqa: E402
import pix as X           # noqa: E402

BUILD = os.path.join(HERE, "build")
OUT = os.path.join(HERE, "out")
MP4 = os.path.join(OUT, "ISU-152柴油机_26s_1080x1920.mp4")
PREVIEW_T = [0.0, 1.2, 2.1, 2.6, 3.4, 3.9, 5.2, 6.2, 7.3, 8.0, 8.5, 9.6, 10.7, 11.9, 13.6, 15.6, 17.4, 18.2,
             19.4, 21.3, 22.0, 23.0, 23.9, 25.3]


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def sheet(times, ims, path, cols=8, scale=1.0):
    tw, th = int(X.W * scale), int(X.H * scale)
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (cols * tw, rows * (th + 16)), (0, 0, 0))
    d = ImageDraw.Draw(sh)
    for i, (t, im) in enumerate(zip(times, ims)):
        x, y = (i % cols) * tw, (i // cols) * (th + 16)
        sh.paste(im.resize((tw, th), Image.NEAREST), (x, y + 16))
        bi, lb = M.bar_beat(t)
        d.text((x + 4, y + 2), f"#{i + 1}  {t:.2f}s  bar {bi + 1} beat {lb:.1f}  {M.ROLES[bi]}", fill=(255, 255, 255))
    sh.save(path)


def lint(step=3):
    X.LINT["edge"].clear()
    X.LINT["missing"].clear()
    for fi in range(0, M.NF, step):
        A.frame(fi / M.FPS, fi)
    edges = sorted({e[0] for e in X.LINT["edge"]})
    print(f"lint      text off the {X.MARGIN}-px safe margin: {edges if edges else 'none'}; "
          f"missing glyphs: {sorted(X.LINT['missing']) if X.LINT['missing'] else 'none'}; "
          f"smallest text 12 art px = 36 px in the video")
    return not edges and not X.LINT["missing"]


def _frame_bytes(fi):
    return np.asarray(A.frame(fi / M.FPS, fi), np.uint8).tobytes()


def render_video(path):
    cmd = [ffmpeg(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{X.W}x{X.H}",
           "-r", str(M.FPS), "-i", "-", "-vf", f"scale={X.W * X.SCALE}:{X.H * X.SCALE}:flags=neighbor",
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-tune", "animation", "-g", "60",
           "-pix_fmt", "yuv420p", path]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count() or 4) as pool:
        for b in pool.imap(_frame_bytes, range(M.NF), chunksize=6):
            pr.stdin.write(b)
    pr.stdin.close()
    if pr.wait() != 0:
        raise SystemExit("ffmpeg failed")


def mux(video, wav, out):
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", out], check=True)


def mp4_sheet(path, out_png, n=12):
    tmp = os.path.join(BUILD, "_mp4frames")
    os.makedirs(tmp, exist_ok=True)
    ims, ts = [], []
    for i in range(n):
        t = 0.2 + (M.DUR - 0.6) * i / (n - 1)
        f = os.path.join(tmp, f"{i:02d}.png")
        subprocess.run([ffmpeg(), "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
                        "-vf", "scale=360:640:flags=neighbor", f], check=True)
        ims.append(Image.open(f).convert("RGB"))
        ts.append(t)
    sheet(ts, ims, out_png, cols=6)


def verify(path, cues):
    from engine.render import probe
    from engine import sfx as FX
    import audio as AU
    p = probe(path)
    size = os.path.getsize(path) / 1e6
    print("VERIFY")
    print(f"file      {path}  {size:.1f} MB (limit 95)")
    print(f"duration  {p['duration']} (target {M.NF / M.FPS:.3f} s = {M.NBARS} bars at {M.BPM} BPM)")
    print(f"video     {p['video']}")
    print(f"audio     {p['audio']}")
    print(f"loudness  {p['lufs']} LUFS integrated (target -18), true peak {p['true_peak']} dBTP (limit -1)")
    raw = subprocess.run([ffmpeg(), "-v", "error", "-i", path, "-vf", "scale=90:160,format=gray", "-f", "rawvideo",
                          "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 160, 90).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))
    med = float(np.median(d)) + 1e-6
    cut_s = [M.BAR + M.BEAT, 3 * M.BAR, 6 * M.BAR, 12 * M.BAR + 2 * M.BEAT]
    rows = []
    for ct in cut_s:
        i = int(np.ceil(ct * M.FPS - 1e-6))
        win = d[max(0, i - 4): i + 3]
        rows.append(f"{ct:.3f}s x{d[i - 1] / med:.0f} (peak at frame {max(0, i - 4) + int(np.argmax(win)) + 1}, "
                    f"cut frame {i})")
    print("cuts      " + " | ".join(rows))
    loop = float(np.abs(fr[-1] - fr[0]).mean())
    print(f"loop      last frame vs frame 0: {loop:.2f} gray levels (an ordinary frame step here: {np.median(d[:50]):.2f})")
    a = subprocess.run([ffmpeg(), "-v", "error", "-i", path, "-map", "0:a", "-ac", "1", "-ar", str(FX.SR), "-f",
                        "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(a, np.float32)
    offs, active = FX.onset_offsets(x, cues)
    aa = np.abs(offs) * 1000
    print(f"sfx       {len(cues)} cues; transients start {np.median(aa):.0f} ms (median) / {aa.max():.0f} ms (worst) "
          f"from their beats ({len(aa)} checked); sound on {active * 100:.0f}% of the time; no music")
    bo = AU.bang_onsets(x)
    print(f"bangs     slow-motion bangs (bars 3-10) found in the file: {bo['found']}/{bo['n']}, median "
          f"{bo['med']:.1f} ms / worst {bo['worst']:.1f} ms from the beat grid")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--stills", default="")
    ap.add_argument("--audio", action="store_true")
    args = ap.parse_args()
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    if args.preview:
        ims = [A.frame(t) for t in PREVIEW_T]
        sheet(PREVIEW_T, ims, os.path.join(BUILD, "preview.png"))
        print("preview  ", os.path.join(BUILD, "preview.png"))
        lint()
        return
    if args.stills:
        d = os.path.join(BUILD, "stills")
        os.makedirs(d, exist_ok=True)
        for s in args.stills.split(","):
            t = float(s)
            A.frame(t).resize((X.W * X.SCALE, X.H * X.SCALE), Image.NEAREST).save(os.path.join(d, f"{t:06.2f}.png"))
        print("stills   ", d)
        return
    import audio as AU
    wav = os.path.join(BUILD, "audio.wav")
    t0 = time.time()
    cues, st = AU.build(wav)
    print(f"audio     {wav}: {st}  ({time.time() - t0:.0f} s)")
    if args.audio:
        tmp = os.path.join(BUILD, "video_only.mp4")
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", MP4, "-map", "0:v", "-c", "copy", tmp], check=True)
        mux(tmp, wav, MP4)
        verify(MP4, cues)
        return
    ok = lint()
    vid = os.path.join(BUILD, "video_only.mp4")
    t0 = time.time()
    render_video(vid)
    print(f"video     {M.NF} frames in {time.time() - t0:.0f} s")
    mux(vid, wav, MP4)
    A.frame(0.0).resize((X.W * X.SCALE, X.H * X.SCALE), Image.NEAREST).save(os.path.join(OUT, "第0帧.png"))
    mp4_sheet(MP4, os.path.join(OUT, "分镜预览.png"))
    verify(MP4, cues)
    print("lint OK" if ok else "lint: see above")


if __name__ == "__main__":
    main()
