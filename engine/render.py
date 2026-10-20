"""Episode definition + CLI.

An episode file defines scene functions and an Episode, then calls run(EP):

    def sc_hook(c, S):            # S.t, S.B (local seconds / beats), S.dur, S.bars, S.gt, S.rng
        ...
    EP = Episode(slug="forgetting_curve", title="...", bpm=136, scenes=[
        Scene("hook", 4, sc_hook, role="intro", chapter="开场"),
        ...
    ])
    if __name__ == "__main__":
        run(EP)

CLI (run from the repo root):
    python episodes/<slug>/episode.py --preview [--times 1 5 9]  # ONE contact-sheet PNG + lint report
    python episodes/<slug>/episode.py --frame 12.5               # single PNG (debug only)
    python episodes/<slug>/episode.py --music                    # music only (build/music.wav)
    python episodes/<slug>/episode.py --cover                    # out/<slug>_cover.png
    python episodes/<slug>/episode.py                            # full: music + video + no-music copy + verify
"""
import argparse
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from multiprocessing import Pool
from typing import Callable, Optional

import numpy as np
import skia

from . import OUT, REPO
from . import core as K
from . import music as M

W, H, FPS = K.W, K.H, K.FPS


@dataclass
class Scene:
    sid: str
    bars: int
    fn: Callable
    role: str = "verse"       # music role, see engine.music.ROLE_DOC
    chapter: Optional[str] = None


@dataclass
class Episode:
    slug: str
    title: str
    scenes: list
    bpm: int = 128              # beat grid; with music=False use the BPM of the song the user will add
    music: bool = False         # False: silent video, user adds music in-app (default, user preference)
    transpose: int = 0          # (music=True) shift the whole score so episodes don't sound identical
    tail: float = 0.0           # seconds after the last bar; 0 = ends exactly on the last bar line (user preference)
    fade_out: float = 0.0       # fade to black over the last N seconds; 0 = end directly (user preference)
    # Stable picture by default (user: no shaking). The beat shows through elements appearing ON beats
    # and the background's brightness pulse - nothing moves the whole frame.
    cut: str = "hard"           # scene entry: "hard" (clean cut on the downbeat) | "slide" | "punch" (zoom-in, shakes)
    bounce: float = 0.0         # whole-frame zoom kick on every beat; looks like shaking -> keep 0
    flash: float = 0.0          # white flash on cuts (0..0.3)
    pulse: float = 0.6          # background brightness pulse on the beat (floor grid / particles), 0 = none
    progress_bar: bool = True
    glitch_cuts: bool = False   # RGB slice glitch on cuts (also reads as shaking)
    background: Callable = K.bg_dark_tech
    cover: Optional[Callable] = None     # cover(c) draws a 1920x1080 cover
    publish: dict = field(default_factory=dict)   # {"title":..., "desc":..., "tags": [...]}
    score: Optional[Callable] = None     # score(Score, sections) to override auto_score

    def __post_init__(self):
        self.beat = 60.0 / self.bpm
        self.bar = 4 * self.beat
        self.starts, b = {}, 0
        for s in self.scenes:
            self.starts[s.sid] = b
            b += s.bars
        self.total_bars = b
        self.duration = b * self.bar + self.tail
        assert len(self.starts) == len(self.scenes), "duplicate scene ids"
        if self.scenes[-1].role == "outro":
            assert self.scenes[-1].bars >= 3, "outro needs >= 3 bars (last 2 are the ringing end chord)"
        main = getattr(sys.modules.get("__main__"), "__file__", None)
        here = os.path.dirname(os.path.abspath(main)) if main else os.path.join(REPO, "episodes", self.slug)
        self.build = os.path.join(here, "build")

    def span(self, sid):
        b = self.starts[sid]
        n = next(s.bars for s in self.scenes if s.sid == sid)
        return b * self.bar, (b + n) * self.bar

    def scene_at(self, t):
        for s in self.scenes:
            s0, s1 = self.span(s.sid)
            if s0 <= t < s1:
                return s, s0, s1
        s = self.scenes[-1]
        return (s,) + self.span(s.sid)

    def chapters(self):
        out = []
        for s in self.scenes:
            lbl = s.chapter or s.sid
            s0, s1 = self.span(s.sid)
            if out and out[-1][0] == lbl:
                out[-1][2] = s1
            else:
                out.append([lbl, s0, s1])
        return out

    def timing_table(self):
        rows = []
        for s in self.scenes:
            s0, s1 = self.span(s.sid)
            rows.append(f"  {s.sid:12s} {s.bars:3d} bars  {s0:6.2f}s -> {s1:6.2f}s  ({s1 - s0:5.2f}s)  role={s.role}")
        rows.append(f"  total {self.total_bars} bars = {self.total_bars * self.bar:.1f}s (+{self.tail}s tail) @ {self.bpm} BPM")
        return "\n".join(rows)

    def cut_times(self):
        return [self.span(s.sid)[0] for s in self.scenes[1:]]


class _S:
    pass


# ----------------------------------------------------------------------------- frame
def draw_progress(c, ep, t):
    a = K.clamp((t - 0.8) / 0.6)
    if ep.fade_out:
        a *= 1 - K.clamp((t - (ep.duration - ep.fade_out - 1.2)) / 1.2)
    if a <= 0:
        return
    chs = ep.chapters()
    total = chs[-1][2]
    x0, x1, y = 120, W - 120, 1046
    idx = max(i for i, ch in enumerate(chs) if t >= ch[1] - 1e-6)
    for i, (lbl, s0, s1) in enumerate(chs):
        sx = x0 + (x1 - x0) * s0 / total + 5
        ex = x0 + (x1 - x0) * s1 / total - 5
        c.drawRoundRect(skia.Rect.MakeLTRB(sx, y - 3, ex, y + 3), 3, 3, K.paint(K.DIMMER, 0.55 * a))
        k = K.clamp((t - s0) / (s1 - s0))
        if k > 0:
            fx = sx + (ex - sx) * k
            c.drawRoundRect(skia.Rect.MakeLTRB(sx, y - 3, fx, y + 3), 3, 3, K.paint(K.CYAN, a))
            if i == idx:
                c.drawCircle(fx, y, 7, K.paint(K.CYAN, a))
                c.drawCircle(fx, y, 14, K.paint(K.CYAN, 0.5 * a, blur=8))
        act = i == idx
        K.text(c, lbl, sx, y - 26, 26, "bold", K.WHITE if act else K.DIMMER, a * (1 if act else 0.75), "l", small=True)


def render_frame(ep, c, surf, t, fi):
    rng = np.random.default_rng(fi * 7919 + 13)
    K.FRAME_CARDS.clear()
    sc, s0, s1 = ep.scene_at(t)
    lt = t - s0
    ep.background(c, t, ep.beat, ep.pulse)
    last = sc is ep.scenes[-1]
    if ep.cut == "hard":                # instant cut exactly on the downbeat; elements animate in on their beats
        a_in = a_out = 1.0
        zoom = 1.0
    elif ep.cut == "punch":
        a_in = K.e_out(lt / 0.06)
        a_out = 1.0 if last else 1 - K.clamp((lt - (s1 - s0 - 0.07)) / 0.07)
        zoom = K.lerp(1.07, 1.0, K.e_out(lt / (0.5 * ep.beat)))
    else:
        a_in = K.e_out(lt / 0.28)
        a_out = 1.0 if last else 1 - K.clamp((lt - (s1 - s0 - 0.22)) / 0.22)
        zoom = 1.0
    a = min(a_in, a_out)
    S = _S()
    S.t, S.B, S.dur, S.bars, S.gt, S.rng, S.beat = lt, lt / ep.beat, s1 - s0, sc.bars, t, rng, ep.beat
    c.saveLayerAlpha(None, int(255 * K.clamp(a)))
    if ep.cut == "punch":
        c.translate(W / 2, H / 2)
        c.scale(zoom, zoom)
        c.translate(-W / 2, -H / 2)
    else:
        c.translate(0, (1 - a_in) * 18)
    sc.fn(c, S)
    c.restore()
    if ep.progress_bar:
        draw_progress(c, ep, t)
    if ep.bounce:
        kz = 1 + ep.bounce * K.kick(t, ep.beat)
        if kz > 1.0005:
            snap = surf.makeImageSnapshot()
            c.clear(skia.ColorBLACK)
            c.drawImageRect(snap, skia.Rect.MakeXYWH(W / 2 * (1 - kz), H / 2 * (1 - kz), W * kz, H * kz),
                            skia.SamplingOptions(skia.FilterMode.kLinear))
    flash = 0.16 if ep.cut == "punch" else ep.flash
    if flash and lt < 0.5 * ep.beat and t > 0.02:
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), K.paint("#FFFFFF", flash * (1 - lt / (0.5 * ep.beat))))
    if ep.glitch_cuts and (0.05 < t and lt < 0.2 or t < 0.12):
        snap = surf.makeImageSnapshot()
        k = 1 - lt / 0.2 if t > 0.05 else 1 - t / 0.12
        for _ in range(7):
            y, h, dx = rng.uniform(0, H), rng.uniform(8, 60), rng.uniform(-60, 60) * k
            p = skia.Paint()
            p.setAlphaf(0.85 * k)
            c.drawImageRect(snap, skia.Rect.MakeXYWH(0, y, W, h), skia.Rect.MakeXYWH(dx, y, W, h),
                            skia.SamplingOptions(), p)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H), K.paint(K.CYAN, 0.10 * k))
    K.overlay(c)
    if ep.fade_out and t > ep.duration - ep.fade_out:
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, H),
                   K.paint("#000000", K.clamp((t - (ep.duration - ep.fade_out)) / (0.85 * ep.fade_out))))


def _surface():
    arr = np.zeros((H, W, 4), np.uint8)
    return arr, skia.Surface(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


_EP = None


def _chunk(job):
    idx, f0, f1, path = job
    arr, surf = _surface()
    c = surf.getCanvas()
    pr = subprocess.Popen([ffmpeg(), "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-tune", "animation", "-maxrate", "4000k", "-bufsize", "8000k", "-g", "60",
                           "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        c.save()
        c.clear(skia.ColorBLACK)
        render_frame(_EP, c, surf, fi / FPS, fi)
        c.restore()
        pr.stdin.write(arr.tobytes())
    pr.stdin.close()
    pr.wait()
    return idx, f1 - f0, K.LINT["small"], K.LINT["missing"], K.LINT["edge"]


def contact_sheet(ep, times, path, cols=6, scale=0.25):
    tw, th = int(W * scale), int(H * scale)
    rows = math.ceil(len(times) / cols)
    sheet = skia.Surface(cols * tw, rows * (th + 30))
    sc = sheet.getCanvas()
    sc.clear(skia.ColorBLACK)
    arr, surf = _surface()
    c = surf.getCanvas()
    for i, t in enumerate(times):
        c.clear(skia.ColorBLACK)
        render_frame(ep, c, surf, t, int(t * FPS))
        x, y = (i % cols) * tw, (i // cols) * (th + 30)
        sc.drawImageRect(surf.makeImageSnapshot(), skia.Rect.MakeXYWH(x, y, tw, th),
                         skia.SamplingOptions(skia.FilterMode.kLinear))
        K.text(sc, f"{t:6.2f}s  {ep.scene_at(t)[0].sid}", x + 8, y + th + 15, 18, "mono", "#FFFFFF", 1, "l", small=True)
    sheet.makeImageSnapshot().save(path)


def default_times(ep, n=24):
    """2 samples per scene (40% and 85% through), capped at n"""
    ts = []
    for s in ep.scenes:
        s0, s1 = ep.span(s.sid)
        ts += [s0 + (s1 - s0) * 0.45, s0 + (s1 - s0) * 0.9]
    if len(ts) > n:
        ts = [ts[round(i * (len(ts) - 1) / (n - 1))] for i in range(n)]
    return ts


def lint_pass(ep, step_beats=1.0):
    """render ~1 frame per beat off-screen, collect small-text / missing-glyph warnings"""
    arr, surf = _surface()
    c = surf.getCanvas()
    t = 0.0
    while t < ep.duration:
        c.clear(skia.ColorBLACK)
        render_frame(ep, c, surf, t, int(t * FPS))
        t += ep.beat * step_beats
    return K.lint_report()


def make_music(ep):
    s = M.Score(ep.bpm, ep.transpose)
    sections = [(sc.role, ep.starts[sc.sid], sc.bars) for sc in ep.scenes]
    (ep.score or M.auto_score)(s, sections)
    out = os.path.join(ep.build, "music.wav")
    n, levels = M.render_wav(s, ep.duration, out)
    print(f"music: {n} notes -> {out}")
    return out


def probe(path):
    r = subprocess.run([ffmpeg(), "-hide_banner", "-i", path, "-map", "0:a", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    err = r.stderr
    dur = re.search(r"Duration: (\S+),", err)
    v = re.search(r"Video: (.+)", err)
    a = re.search(r"Audio: (.+)", err)
    summ = err[err.rfind("Summary:"):]
    I = re.search(r"I:\s+(-?[\d.]+) LUFS", summ)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ)
    return dict(duration=dur and dur.group(1), video=v and v.group(1).strip(), audio=a and a.group(1).strip(),
                lufs=I and float(I.group(1)), true_peak=tp and float(tp.group(1)))


def mp4_sheet(path, out_png, duration, n=12):
    tmp = os.path.join(os.path.dirname(out_png), "_mp4frames")
    os.makedirs(tmp, exist_ok=True)
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    for i in range(n):
        t = 0.6 + (duration - 1.8) * i / (n - 1)
        subprocess.run([ffmpeg(), "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
                        "-vf", "scale=480:270", os.path.join(tmp, f"{i:02d}.png")], check=True)
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-framerate", "1", "-i", os.path.join(tmp, "%02d.png"),
                    "-vf", "tile=4x3", "-frames:v", "1", out_png], check=True)


def rhythm_check(path, ep):
    """Measured on the FINAL file:
    - events: frames where the picture changes noticeably (local peaks of frame difference); share that land
      within 1.5 frames of a beat of ep.bpm, vs the best of other tempos (chance level ~10-30%)
    - cuts: change at each scene cut relative to the median frame change
    - shake: regions declared still by the scene factories (docked step headers, summary title): how much more
      they change ON the beat than between beats (1 = perfectly still; a beat-zoom gives ~30)"""
    from scipy.ndimage import uniform_filter
    raw = subprocess.run([ffmpeg(), "-v", "error", "-i", path, "-vf", "scale=192:108,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 108, 192).astype(np.float32)     # 1 cell = 10x10 px
    end = int(ep.span(ep.scenes[-1].sid)[0] * FPS)             # skip the end card + fade-out
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))                # d[i] = change from frame i to i+1
    dd = d[:end]
    thr = np.median(dd) * 3
    ev = np.array([i + 1 for i in range(3, len(dd) - 3) if dd[i] > thr and dd[i] == dd[i - 3:i + 4].max()])

    def on_grid(bpm):
        bf = 60 / bpm * FPS
        return float(np.mean(np.abs(((ev / bf + 0.5) % 1.0) - 0.5) * bf <= 1.5)) if len(ev) else 0.0

    frac = on_grid(ep.bpm)
    other = max(on_grid(b) for b in range(90, 181) if abs(b - ep.bpm) >= 6 and abs(b - ep.bpm / 2) >= 3
                and abs(b - ep.bpm * 2) >= 6)
    med = float(np.median(dd)) + 1e-6
    cut_ratio = [float(d[max(0, int(round(ct * FPS)) - 2): int(round(ct * FPS)) + 1].max() / med) for ct in ep.cut_times()]
    tt = np.arange(1, len(fr)) / FPS
    ph = (tt / ep.beat) % 1.0
    on_sum, off_sum = [], []
    for sc_ in ep.scenes:
        reg = getattr(sc_.fn, "static_region", None)
        if not reg:
            continue
        s0, s1 = ep.span(sc_.sid)
        m = (tt > s0 + sc_.fn.static_after * ep.beat) & (tt < s1 - 3.5 / FPS)
        x0, y0, x1, y1 = (int(v / 10) for v in reg)
        sub = fr[:, y0:y1, x0:x1]
        hp = sub - uniform_filter(sub, size=(1, 5, 5), mode="nearest")   # edges only: ignore the smooth glow pulse
        rd = np.abs(np.diff(hp, axis=0)).mean((1, 2))
        on_sum += list(rd[m & (ph < 0.15)])
        off_sum += list(rd[m & (ph > 0.35) & (ph < 0.9)])
    shake = None
    if on_sum and off_sum:      # judged in absolute gray levels: a ratio of two tiny numbers is meaningless
        on, off = float(np.mean(on_sum)), float(np.mean(off_sum))
        shake = dict(excess=on - off, ratio=on / max(0.02, off))
    return dict(events=len(ev), on_beat=frac, other=other, cut_min=min(cut_ratio) if cut_ratio else None, shake=shake)


def write_publish(ep):
    if not ep.publish:
        return None
    p = os.path.join(OUT, f"{ep.slug}_publish.txt")
    pub = ep.publish
    with open(p, "w") as f:
        f.write(f"标题：{pub.get('title', ep.title)}\n\n")
        if pub.get("desc"):
            f.write(f"简介：\n{pub['desc']}\n\n")
        if pub.get("tags"):
            f.write("话题：" + " ".join("#" + t.lstrip("#") for t in pub["tags"]) + "\n")
        if pub.get("pin"):
            f.write(f"\n置顶评论（发布后马上自己发一条，然后置顶）：{pub['pin']}\n")
        f.write("\n标题请直接复制，不要手打（同音字：回忆 → 会议）。\n")
        if not ep.music:
            f.write(f"\n配乐：视频本身无配乐，请自己加。画面按 {ep.bpm} BPM 的节拍剪辑：文字和图形都在拍点上出现，切镜头都在小节的第一拍；画面不抖动。\n")
            f.write("对齐方法：把歌的一个重拍（「动」）对齐到视频第 0 秒；歌的 BPM 不同的话，告诉 Kiro 改 bpm 重新渲染（约 1 分钟）。\n")
            f.write("切镜头时间点（秒）：" + "、".join(f"{t:.2f}" for t in ep.cut_times()) + "\n")
    return p


def run(ep):
    global _EP
    _EP = ep
    p = argparse.ArgumentParser()
    p.add_argument("--preview", action="store_true")
    p.add_argument("--times", type=float, nargs="*")
    p.add_argument("--frame", type=float, nargs="*")
    p.add_argument("--music", action="store_true")
    p.add_argument("--cover", action="store_true")
    p.add_argument("--lint", action="store_true")
    p.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    args = p.parse_args()
    os.makedirs(ep.build, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    print(f"{ep.slug}: {ep.title}\n{ep.timing_table()}")
    if args.frame:
        arr, surf = _surface()
        for t in args.frame:
            surf.getCanvas().clear(skia.ColorBLACK)
            render_frame(ep, surf.getCanvas(), surf, t, int(t * FPS))
            out = os.path.join(ep.build, f"frame_{t:07.2f}.png")
            surf.makeImageSnapshot().save(out)
            print(out)
        print(K.lint_report())
        return
    if args.preview:
        out = os.path.join(ep.build, "contact_sheet.png")
        contact_sheet(ep, args.times or default_times(ep), out)
        print(f"PREVIEW (view this ONE image): {out}")
        print(lint_pass(ep))
        return
    if args.lint:
        print(lint_pass(ep, 0.5))
        return
    if args.music:
        make_music(ep)
        return
    if args.cover:
        if not ep.cover:
            raise SystemExit("episode has no cover() function")
        for v in K.LINT.values():
            v.clear()
        arr, surf = _surface()
        c = surf.getCanvas()
        ep.cover(c)
        K.overlay(c)
        out = os.path.join(OUT, f"{ep.slug}_cover.png")
        surf.makeImageSnapshot().save(out)
        print(out)
        print("cover " + K.lint_report())
        return

    music = make_music(ep) if ep.music else None
    total = int(round(ep.duration * FPS))
    n = args.workers * 3
    bounds = [round(i * total / n) for i in range(n + 1)]
    jobs = [(i, bounds[i], bounds[i + 1], os.path.join(ep.build, f"seg_{i:03d}.mp4")) for i in range(n)]
    small, missing, edge, done = set(), set(), set(), 0
    with Pool(args.workers) as pool:
        for idx, cnt, sm, ms, ed in pool.imap_unordered(_chunk, jobs):
            done += cnt
            small |= sm
            missing |= ms
            edge |= ed
    print(f"video: {done}/{total} frames rendered")
    lst = os.path.join(ep.build, "segments.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{j[3]}'\n" for j in jobs)
    out = os.path.join(OUT, f"{ep.slug}.mp4")
    silent = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a",
              "-c:v", "copy", "-c:a", "aac", "-b:a", "64k", "-shortest", "-movflags", "+faststart"]
    out_nm = None
    if music:
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", music,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out],
                       check=True)
        # silent-audio copy, for choosing music inside the Douyin / Xiaohongshu app
        out_nm = os.path.join(OUT, f"{ep.slug}_nomusic.mp4")
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst] + silent + [out_nm],
                       check=True)
    else:   # user adds their own music: one silent video (a silent AAC track keeps editors / apps happy)
        subprocess.run([ffmpeg(), "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst] + silent + [out],
                       check=True)
    for j in jobs:
        os.remove(j[3])
    pub = write_publish(ep)
    # ---- verification
    info = probe(out)
    sheet = os.path.join(ep.build, "mp4_sheet.png")
    mp4_sheet(out, sheet, ep.duration)
    print("\n==== VERIFY ====")
    print(f"file      {out}  ({os.path.getsize(out) / 1e6:.1f} MB){'' if music else '  [silent: user adds music]'}")
    if out_nm:
        print(f"no-music  {out_nm}  ({os.path.getsize(out_nm) / 1e6:.1f} MB)")
    for k, v in info.items():
        if k in ("lufs", "true_peak") and not music:
            continue
        print(f"{k:9s} {v}")
    bad = [round(t / ep.bar, 3) for t in ep.cut_times() if abs(t / ep.bar - round(t / ep.bar)) > 1e-6]
    print(f"beatgrid  {ep.bpm} BPM, bar {ep.bar:.4f}s, cuts on bar lines: {'OK' if not bad else bad}; "
          f"cut times: {', '.join(f'{t:.2f}' for t in ep.cut_times())}")
    r = rhythm_check(out, ep)
    shake = r["shake"]
    ok = r["on_beat"] >= 0.8 and r["on_beat"] > r["other"] + 0.3 and (r["cut_min"] or 99) > 4
    print(f"rhythm    {r['events']} visual events, {r['on_beat'] * 100:.0f}% land on a {ep.bpm} BPM beat (±1.5 frames; "
          f"best other tempo {r['other'] * 100:.0f}%); weakest scene cut {r['cut_min']:.0f}x the median frame change"
          f" -> {'OK' if ok else 'CHECK'}")
    if shake is None:
        print("shake     (no static regions declared by the scenes; settings: "
              f"bounce={ep.bounce}, cut={ep.cut}, glitch_cuts={ep.glitch_cuts})")
    else:
        print(f"shake     still edges change {shake['excess']:.2f} gray levels more on the beat than between beats "
              f"({'stable, no shaking' if shake['excess'] < 1.0 else 'SHAKING: the frame moves on the beat'}; "
              f"limit 1.0, the rejected beat-zoom measured 7.4); bounce={ep.bounce}, cut={ep.cut}, glitch_cuts={ep.glitch_cuts}")
    print(K.lint_report({"small": small, "missing": missing, "edge": edge, "hook": K.LINT["hook"]}))
    if pub:
        print(f"publish   {pub}")
    print(f"MP4 SHEET (12 frames decoded from the final file; view this ONE image): {sheet}")
    if os.path.getsize(out) > 95e6:
        print("[warn] > 95 MB: GitHub rejects files over 100 MB; raise -crf or shorten")
