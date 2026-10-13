"""Render the full video: per-frame camera drift, dust particles in the beam,
cross-fades, styled subtitles; encoded in parallel segments with ffmpeg."""
import os
import sys
import subprocess
import numpy as np
import cv2
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import room
from scenes import SCENES, FPS, XFADE, shot_of, timeline
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
OW, OH = 1920, 1080
BUILD = os.path.join(HERE, "build")
SEG = os.path.join(BUILD, "segments")

STARTS, DURS, TOTAL = timeline()
NFRAMES = int(round(TOTAL * FPS))

WHITE = (246, 242, 234)
GOLD_TOP = np.array([255, 226, 150], np.float32)
GOLD_BOT = np.array([222, 160, 70], np.float32)


def smooth(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def ease_io(x):
    x = np.clip(x, 0.0, 1.0)
    return 0.5 - 0.5 * np.cos(np.pi * x)


# ---------------------------------------------------------------- subtitles
def parse(markup):
    segs, gold, buf = [], False, ""
    for ch in markup:
        if ch == "[":
            if buf:
                segs.append((buf, gold))
            buf, gold = "", True
        elif ch == "]":
            if buf:
                segs.append((buf, gold))
            buf, gold = "", False
        else:
            buf += ch
    if buf:
        segs.append((buf, gold))
    return segs


def render_text_block(markup, size, font_path=room.FONT_BLACK, dot=True, track=0.02):
    """Returns (rgb float HxWx3 premultiplied, alpha HxW, x_offset_of_box, glyph_x_extent)."""
    if dot:
        markup = markup.rstrip("。")
    segs = parse(markup)
    fnt = ImageFont.truetype(font_path, size)
    chars = [(ch, g) for s, g in segs for ch in s]
    adv = [fnt.getlength(ch) + size * track for ch, _ in chars]
    tw = sum(adv) + (size * 0.45 if dot else 0)
    pad = int(size * 0.9)
    w, h = int(tw + 2 * pad), int(size * 1.6 + 2 * pad)
    base_y = pad + size * 0.8
    txt = Image.new("L", (w, h), 0)
    gold = Image.new("L", (w, h), 0)
    dt, dg = ImageDraw.Draw(txt), ImageDraw.Draw(gold)
    x = pad
    for (ch, g), a in zip(chars, adv):
        dt.text((x, base_y), ch, font=fnt, fill=255, anchor="ls")
        if g:
            dg.text((x, base_y), ch, font=fnt, fill=255, anchor="ls")
        x += a
    if dot:  # little ring after the sentence, like the reference
        r = size * 0.11
        cx, cy = x + size * 0.16, base_y - r
        dt.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        dt.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=0)
    a = np.asarray(txt, np.float32) / 255.0
    gm = np.asarray(gold, np.float32) / 255.0
    # vertical gold gradient
    yy = (np.arange(h, dtype=np.float32) - (base_y - size * 0.8)) / (size * 0.9)
    t = np.clip(yy, 0, 1)[:, None, None]
    goldcol = (GOLD_TOP * (1 - t) + GOLD_BOT * t) / 255.0
    col = np.ones((h, w, 3), np.float32) * (np.array(WHITE, np.float32) / 255.0)
    col = col * (1 - gm[..., None]) + goldcol * gm[..., None]
    # shadow + glows
    shadow = cv2.GaussianBlur(a, (0, 0), size * 0.12)
    shadow = np.roll(shadow, int(size * 0.04), axis=0)
    gglow = cv2.GaussianBlur(gm, (0, 0), size * 0.22)
    wglow = cv2.GaussianBlur(a, (0, 0), size * 0.35)
    alpha_sh = np.clip(shadow * 0.85 + wglow * 0.25, 0, 1)
    # composite: start with dark shadow layer, add warm glow, then the glyphs
    rgb = np.zeros((h, w, 3), np.float32)
    A = alpha_sh.copy()
    glow_col = np.array([1.0, 0.72, 0.35], np.float32)
    rgb = rgb + glow_col * (gglow * 0.75)[..., None]
    A = np.clip(A + gglow * 0.45, 0, 1)
    rgb = rgb * (1 - a[..., None]) + col * a[..., None]
    A = A * (1 - a) + a
    return rgb, A, pad, w


class Subtitle:
    def __init__(self, markup, size=66, y=0.84, dot=True, font_path=room.FONT_BLACK, track=0.02):
        self.rgb, self.a, self.pad, self.w = render_text_block(markup, size, font_path, dot, track)
        h, w = self.a.shape
        self.x0 = int(OW / 2 - w / 2)
        self.y0 = int(OH * y - h / 2)
        self.size = size
        self.xs = np.arange(w, dtype=np.float32)

    def draw(self, frame, alpha, reveal=1.0, rise=0.0):
        if alpha <= 0.002:
            return
        h, w = self.a.shape
        # left-to-right soft reveal
        if reveal < 1.0:
            soft = self.size * 2.0
            edge = self.pad + reveal * (w - 2 * self.pad + soft) - soft * 0.5
            m = np.clip((edge - self.xs) / soft + 0.5, 0, 1)[None, :]
        else:
            m = 1.0
        a = self.a * m * alpha
        y0 = self.y0 + int(rise)
        x0 = self.x0
        ys0, ys1 = max(0, y0), min(OH, y0 + h)
        xs0, xs1 = max(0, x0), min(OW, x0 + w)
        sa = a[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0, None]
        sc = self.rgb[ys0 - y0:ys1 - y0, xs0 - x0:xs1 - x0]
        region = frame[ys0:ys1, xs0:xs1]
        region[:] = region * (1 - sa) + sc * sa


# ---------------------------------------------------------------- scenes
class SceneRT:
    def __init__(self, idx):
        name, dur, text, label = SCENES[idx]
        self.idx, self.name, self.dur, self.label = idx, name, DURS[idx], label
        self.shot = shot_of(name)
        plate = room.build(self.shot)
        self.base, self.haze, self.dark = plate["base"], plate["haze"], plate["dark"]
        self.F = plate["F"]
        self.title = self.shot.get("title", False)
        self.ending = (name == "ending")
        rng = np.random.default_rng(100 + idx)
        # dust particles sampled from beam density
        dens = plate["density"]
        small = cv2.resize(dens, (room.W // 8, room.H // 8), interpolation=cv2.INTER_AREA)
        p = small.ravel() / small.sum()
        n = 420
        pick = rng.choice(p.size, n, p=p)
        py, px = np.divmod(pick, small.shape[1])
        self.px = (px + rng.random(n)) * 8
        self.py = (py + rng.random(n)) * 8
        self.dens = dens
        self.pvx = rng.normal(0.0, 4.0, n) * (self.F / 1062) ** 0.5
        self.pvy = rng.normal(-3.0, 3.0, n) * (self.F / 1062) ** 0.5
        self.pph = rng.random(n) * 2 * np.pi
        self.pfreq = rng.uniform(0.3, 1.2, n)
        kz = (self.F / 1062.0) ** 0.35
        self.psize = rng.choice([1.0, 1.4, 2.0, 3.2], n, p=[0.45, 0.3, 0.17, 0.08]) * kz
        self.pbright = rng.uniform(0.25, 1.0, n)
        self.wph = rng.random(n) * 2 * np.pi
        if self.title:
            self.sub = Subtitle(text, size=118, y=0.80, dot=False, track=0.12)
            self.sub2 = Subtitle("没有什么，比临时方案更持久", size=34, y=0.895, dot=False,
                                 font_path=room.FONT_BOLD, track=0.35)
        else:
            self.sub = Subtitle(text, size=64, y=0.845)
            self.sub2 = None
        seed = 7 + idx
        r2 = np.random.default_rng(seed)
        self.drift = r2.uniform(0, 2 * np.pi, 4)
        self.zoom0, self.zoom1 = 1.0, 1.0 + (0.075 if not self.title else 0.05)

    def particles(self, img, t):
        x = self.px + self.pvx * t + 6.0 * np.sin(t * 0.4 + self.wph)
        y = self.py + self.pvy * t + 4.0 * np.cos(t * 0.33 + self.wph)
        x = np.mod(x, room.W)
        y = np.mod(y, room.H)
        xi, yi = x.astype(int), y.astype(int)
        d = self.dens[np.clip(yi, 0, room.H - 1), np.clip(xi, 0, room.W - 1)]
        tw = 0.55 + 0.45 * np.sin(t * self.pfreq * 2 * np.pi * 0.35 + self.pph)
        b = d * tw * self.pbright * 1.25
        col = np.array([1.0, 0.88, 0.68], np.float32)
        for i in np.nonzero(b > 0.03)[0]:
            s = self.psize[i]
            r = int(np.ceil(s * 2.5))
            cx, cy = x[i], y[i]
            x0, y0 = int(cx) - r, int(cy) - r
            x1, y1 = x0 + 2 * r + 1, y0 + 2 * r + 1
            if x0 < 0 or y0 < 0 or x1 > room.W or y1 > room.H:
                continue
            gx = np.arange(x0, x1) - cx
            gy = np.arange(y0, y1) - cy
            g = np.exp(-(gy[:, None] ** 2 + gx[None, :] ** 2) / (2 * (s * 0.7) ** 2)) * b[i]
            img[y0:y1, x0:x1] += g[..., None] * col

    def frame(self, t):
        """t = local time in seconds (can be slightly negative / beyond dur)."""
        u = np.clip(t / self.dur, -0.2, 1.2)
        flick = 1.0 + 0.06 * np.sin(t * 1.3 + self.drift[0]) + 0.04 * np.sin(t * 2.9 + self.drift[1])
        img = self.base + self.haze * (flick - 1.0 + 1.0)
        if self.title:
            lit = smooth((t - 0.6) / 3.2)
            img = self.dark * (1 - lit) + img * lit
        else:
            img = img.copy()
        if not self.title or t > 0.6:
            self.particles(img, t + 3.0)
        # camera: slow push + subtle handheld drift
        z = self.zoom0 + (self.zoom1 - self.zoom0) * ease_io(u)
        if self.ending:
            z = 1.0 + 0.10 * ease_io(u)
        dx = 7.0 * np.sin(t * 0.21 + self.drift[2]) + 3.0 * np.sin(t * 0.53 + self.drift[3])
        dy = 5.0 * np.sin(t * 0.17 + self.drift[3]) + 2.0 * np.sin(t * 0.47 + self.drift[2])
        s = (OW / room.W) * z
        cx, cy = room.W / 2 + dx, room.H / 2 + dy
        M = np.array([[s, 0, OW / 2 - s * cx], [0, s, OH / 2 - s * cy]], np.float32)
        out = cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return out

    def subtitle_alpha(self, t):
        if self.title:
            a_in = smooth((t - 2.2) / 1.2)
            a_out = 1 - smooth((t - (self.dur - 1.2)) / 0.7)
            return a_in * a_out, smooth((t - 2.2) / 1.6)
        a_in = smooth((t - 0.35) / 0.5)
        a_out = 1 - smooth((t - (self.dur - 1.0)) / 0.45)
        return a_in * a_out, smooth((t - 0.3) / 0.9)


# ---------------------------------------------------------------- composition
_cache = {}


def scene(i):
    if i not in _cache:
        if len(_cache) >= 3:
            _cache.pop(max(_cache, key=lambda k: abs(k - i)))
        _cache[i] = SceneRT(i)
    return _cache[i]


_VIGNETTE = None
_GRAIN = None
_LABELS = {}


def vignette():
    global _VIGNETTE
    if _VIGNETTE is None:
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        r = np.sqrt(((xx - OW / 2) / (OW / 2)) ** 2 + ((yy - OH / 2) / (OH / 2)) ** 2)
        _VIGNETTE = (1.0 - 0.42 * smooth((r - 0.45) / 0.95))[..., None].astype(np.float32)
    return _VIGNETTE


def grain(fi):
    global _GRAIN
    if _GRAIN is None:
        rng = np.random.default_rng(3)
        _GRAIN = [cv2.GaussianBlur(rng.normal(0, 1, (OH, OW)).astype(np.float32), (0, 0), 0.7)[..., None]
                  for _ in range(6)]
    return _GRAIN[fi % len(_GRAIN)]


def label_sub(text):
    if text not in _LABELS:
        _LABELS[text] = Subtitle(text, size=30, y=0.085, dot=False, font_path=room.FONT_BOLD, track=0.3)
    return _LABELS[text]


def draw_label(frame, t, i):
    lab = SCENES[i][3]
    if not lab:
        return
    st, du = STARTS[i], DURS[i]
    prev_same = i > 0 and SCENES[i - 1][3] == lab
    next_same = i + 1 < len(SCENES) and SCENES[i + 1][3] == lab
    lt = t - st
    a_in = 1.0 if prev_same else smooth((lt - 0.3) / 0.8)
    a_out = 1.0 if next_same else 1 - smooth((lt - (du - 0.9)) / 0.5)
    a = a_in * a_out * 0.85
    if a <= 0.002:
        return
    sub = label_sub(lab)
    sub.draw(frame, a)
    # thin decorative lines either side
    h, w = sub.a.shape
    yc = int(OH * 0.085)
    half = (w - 2 * sub.pad) / 2
    for sgn in (-1, 1):
        x_in = OW / 2 + sgn * (half + 22)
        x_out = OW / 2 + sgn * (half + 22 + 70)
        xa, xb = int(min(x_in, x_out)), int(max(x_in, x_out))
        frame[yc:yc + 2, xa:xb] = frame[yc:yc + 2, xa:xb] * (1 - a * 0.6) + np.array([0.85, 0.78, 0.62]) * a * 0.6


def scene_index(t):
    i = 0
    while i + 1 < len(STARTS) and t >= STARTS[i + 1]:
        i += 1
    return i


def render_frame(fi):
    t = fi / FPS
    i = scene_index(t)
    lt = t - STARTS[i]
    A = scene(i)
    img = A.frame(lt)
    # cross-fade with neighbours
    if i + 1 < len(SCENES) and t > STARTS[i + 1] - XFADE / 2:
        w = smooth((t - (STARTS[i + 1] - XFADE / 2)) / XFADE)
        img = img * (1 - w) + scene(i + 1).frame(t - STARTS[i + 1]) * w
    elif i > 0 and t < STARTS[i] + XFADE / 2:
        w = smooth((t - (STARTS[i] - XFADE / 2)) / XFADE)
        img = scene(i - 1).frame(t - STARTS[i - 1]) * (1 - w) + img * w
    img = img * vignette()
    # subtitles of current (and fading neighbour) scenes
    for j in {max(0, i - 1), i, min(len(SCENES) - 1, i + 1)}:
        S = scene(j) if j in _cache or j == i else None
        if S is None:
            continue
        a, rev = S.subtitle_alpha(t - STARTS[j])
        if a > 0:
            S.sub.draw(img, a, reveal=rev, rise=(1 - rev) * 10)
            if S.sub2 is not None:
                a2, r2 = S.subtitle_alpha(t - STARTS[j] - 0.9)
                S.sub2.draw(img, a2 * 0.8, reveal=r2)
    draw_label(img, t, i)
    # global fades
    g = smooth(t / 1.6) * (1 - smooth((t - (TOTAL - 3.0)) / 2.8))
    img = img * g
    img = img + grain(fi) * 0.012
    return np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)


def render_segment(args):
    si, f0, f1 = args
    path = os.path.join(SEG, f"seg_{si:02d}.mp4")
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
           "-pix_fmt", "yuv420p", "-x264-params", "keyint=60", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        p.stdin.write(render_frame(fi).tobytes())
    p.stdin.close()
    p.wait()
    return path


def main():
    os.makedirs(SEG, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "still":
        os.makedirs(os.path.join(BUILD, "stills"), exist_ok=True)
        for tt in map(float, sys.argv[2:]):
            fr = render_frame(int(tt * FPS))
            Image.fromarray(fr).resize((1280, 720), Image.LANCZOS).save(
                os.path.join(BUILD, "stills", f"t{tt:06.2f}.jpg"), quality=88)
        return
    nseg = 32
    bounds = np.linspace(0, NFRAMES, nseg + 1).astype(int)
    jobs = [(i, bounds[i], bounds[i + 1]) for i in range(nseg)]
    with Pool(8) as pool:
        paths = []
        for p in pool.imap(render_segment, jobs):
            paths.append(p)
            print("done", os.path.basename(p), flush=True)
    with open(os.path.join(SEG, "list.txt"), "w") as f:
        for p in paths:
            f.write(f"file '{p}'\n")
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(SEG, "list.txt"), "-c", "copy", os.path.join(BUILD, "video_noaudio.mp4")], check=True)
    print("frames", NFRAMES, "duration", TOTAL)
    music = os.path.join(BUILD, "music.wav")
    if os.path.exists(music):
        out_dir = os.path.join(HERE, "out")
        os.makedirs(out_dir, exist_ok=True)
        final = os.path.join(out_dir, "linshiwu_16x9.mp4")
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", os.path.join(BUILD, "video_noaudio.mp4"),
                        "-i", music, "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-tune", "film",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                        "-movflags", "+faststart", final], check=True)
        print("wrote", final)
    else:
        print("build/music.wav not found - run `python music.py` first to add the soundtrack")


if __name__ == "__main__":
    main()
