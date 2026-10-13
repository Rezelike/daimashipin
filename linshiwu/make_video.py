"""Build the video.

  python3 make_video.py tts                # synthesize narration + timeline.json
  python3 make_video.py preview law1@0.6   # render still frames (scene@fraction or seconds)
  python3 make_video.py all                # tts + audio + render + mux + srt + cover
"""
import hashlib, json, math, os, subprocess, sys
from multiprocessing import Pool

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
OUT = os.path.join(HERE, "out")
TTS_DIR = os.environ.get("TTS_MODEL_DIR", "/opt/tts/kokoro-multi-lang-v1_0").rstrip("/") + "/"
os.makedirs(BUILD, exist_ok=True); os.makedirs(OUT, exist_ok=True)
FPS = 30
SR = 24000

import content

# ======================================================================= TTS
def tts_engine():
    import sherpa_onnx
    d = TTS_DIR
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=d + "model.onnx", voices=d + "voices.bin", tokens=d + "tokens.txt",
                data_dir=d + "espeak-ng-data", dict_dir=d + "dict",
                lexicon=d + "lexicon-us-en.txt," + d + "lexicon-zh.txt"),
            num_threads=8),
        rule_fsts=d + "date-zh.fst," + d + "phone-zh.fst," + d + "number-zh.fst")
    return sherpa_onnx.OfflineTts(cfg)


def trim(x, thr=0.01, pad=0.05):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pad * SR)); b = min(len(x), idx[-1] + int(pad * SR))
    return x[a:b]


def lines_of(scene):
    for ln in scene["lines"]:
        yield (ln, ln) if isinstance(ln, str) else ln


def do_tts():
    eng = None
    tdir = os.path.join(BUILD, "tts"); os.makedirs(tdir, exist_ok=True)
    t = 0.0
    timeline = []
    for sc in content.SCENES:
        start = t; t += sc["pre"]
        L, E, subs, wavs = [], [], [], []
        for sub, say in lines_of(sc):
            key = hashlib.md5(f"{say}|{content.VOICE_SID}|{content.VOICE_SPEED}".encode()).hexdigest()[:12]
            path = os.path.join(tdir, key + ".wav")
            if not os.path.exists(path):
                eng = eng or tts_engine()
                a = eng.generate(say, sid=content.VOICE_SID, speed=content.VOICE_SPEED)
                assert a.sample_rate == SR, a.sample_rate
                sf.write(path, trim(np.array(a.samples, np.float32)), SR)
            dur = sf.info(path).duration
            L.append(t); E.append(t + dur); subs.append(sub); wavs.append(path)
            t += dur + content.LINE_GAP
        t += sc["post"] - content.LINE_GAP
        timeline.append(dict(id=sc["id"], chapter=sc["chapter"], start=start, end=t,
                             L=L, E=E, subs=subs, wavs=wavs))
    json.dump(timeline, open(os.path.join(BUILD, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    print(f"timeline: {t:.1f}s, {sum(len(s['L']) for s in timeline)} lines")
    return timeline


def load_timeline():
    return json.load(open(os.path.join(BUILD, "timeline.json")))


class SceneT:
    def __init__(self, s):
        self.id = s["id"]; self.D = s["end"] - s["start"]
        self.L = [x - s["start"] for x in s["L"]]; self.E = [x - s["start"] for x in s["E"]]


# ===================================================================== AUDIO
def env_ar(n, att, rel):
    e = np.ones(n, np.float32)
    a, r = min(int(att * SR), n), min(int(rel * SR), n)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def smooth(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def music(total):
    n = int(total * SR); out = np.zeros(n, np.float32)
    beat = 60 / 72; bar = beat * 4
    chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
    nb = int(total / bar) + 1
    rng = np.random.default_rng(1)
    for b in range(nb):
        ch = chords[b % 4]; t0 = b * bar
        # pad
        dur = bar + 1.5; i0 = int(t0 * SR); m = min(int(dur * SR), n - i0)
        if m <= 0: break
        tt = np.arange(m) / SR; e = env_ar(m, 1.0, 1.4)
        for note in ch:
            f = midi(note)
            out[i0:i0 + m] += 0.035 * e * (np.sin(2 * np.pi * f * tt) + np.sin(2 * np.pi * f * 1.004 * tt)
                                           + 0.25 * np.sin(4 * np.pi * f * tt))
        # bass
        f = midi(ch[0] - 12); mb = min(int(bar * SR), n - i0); tb = np.arange(mb) / SR
        out[i0:i0 + mb] += 0.09 * np.sin(2 * np.pi * f * tb) * np.exp(-tb * 0.8) * env_ar(mb, 0.02, 0.4)
        # soft plucks (arpeggio, one note per beat, sometimes skipped)
        for k in range(4):
            if rng.random() < 0.25: continue
            note = ch[[0, 2, 1, 3][k]] + 12 + (12 if k == 3 and rng.random() < 0.5 else 0)
            i1 = int((t0 + k * beat) * SR); mp = min(int(2.0 * SR), n - i1)
            if mp <= 0: continue
            tp = np.arange(mp) / SR; f = midi(note)
            out[i1:i1 + mp] += 0.07 * (np.sin(2 * np.pi * f * tp) * np.exp(-tp * 3.0)
                                       + 0.3 * np.sin(4 * np.pi * f * tp) * np.exp(-tp * 6)) * env_ar(mp, 0.004, 0.05)
    return out


def sfx(kind):
    rng = np.random.default_rng(abs(hash(kind)) % 1000)
    def T(d): return np.arange(int(d * SR)) / SR
    if kind == "pop":
        t = T(0.12); f = np.linspace(520, 1100, len(t))
        return 0.22 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)
    if kind == "thud":
        t = T(0.35); nz = smooth(rng.normal(0, 1, len(t)), 30)
        return 0.55 * np.sin(2 * np.pi * 75 * t) * np.exp(-t * 14) + 0.5 * nz * np.exp(-t * 35)
    if kind == "chime":
        t = T(2.0)
        return 0.06 * sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in [(1318.5, 2.5), (1760, 3), (2637, 4)])
    if kind == "tick":
        t = T(0.05); return 0.15 * np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 90)
    if kind in ("whoosh", "swipe"):
        d = 0.5 if kind == "whoosh" else 0.3; t = T(d)
        nz = smooth(rng.normal(0, 1, len(t)), 6) - smooth(rng.normal(0, 1, len(t)), 60)
        return (0.18 if kind == "whoosh" else 0.12) * nz * np.hanning(len(t))
    raise ValueError(kind)


def do_audio(tl):
    import scenes
    total = tl[-1]["end"]; n = int(total * SR) + SR
    voice = np.zeros(n, np.float32); fx = np.zeros(n, np.float32)
    for s in tl:
        for t0, w in zip(s["L"], s["wavs"]):
            x, _ = sf.read(w, dtype="float32"); i = int(t0 * SR)
            voice[i:i + len(x)] += x[: n - i]
        S = SceneT(s)
        cues = scenes.SFX[s["id"]](S)
        if s["id"] not in ("open", "title"):
            cues = cues + [(0.0, "whoosh")]
        for (tl_, kind) in cues:
            x = sfx(kind).astype(np.float32); i = int((s["start"] + tl_) * SR)
            if 0 <= i < n:
                fx[i:i + len(x)] += x[: n - i]
    voice *= 0.85 / (np.abs(voice).max() + 1e-9)
    mus = music(n / SR)
    # duck music under narration
    venv = smooth(np.abs(voice), int(0.25 * SR))
    duck = 1 - 0.55 * np.clip(venv / (venv.max() * 0.25), 0, 1)
    fade = np.ones(n, np.float32); fi, fo = int(1.5 * SR), int(3 * SR)
    fade[:fi] = np.linspace(0, 1, fi); fade[-fo:] = np.linspace(1, 0, fo)
    mix = voice + 0.55 * mus * duck * fade + 0.8 * fx
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    path = os.path.join(BUILD, "mix.wav")
    sf.write(path, np.stack([mix, mix], 1), SR)
    print("audio:", path, f"{n / SR:.1f}s")
    return path


# ===================================================================== RENDER
NO_SUB = {("core", 2), ("end", 0), ("end", 1), ("end", 2)}
NO_BRAND = {"open", "title", "end", "turn"}
_BG = None
SUB_MAX = 17  # chars per subtitle chunk (one screen line at 50px)


def sub_chunks(s, l0, l1):
    """Split a narration line into one-line subtitle chunks timed by character share."""
    clauses, cur = [], ""
    for ch in s:
        cur += ch
        if ch in "，。？！：；":
            clauses.append(cur); cur = ""
    if cur:
        clauses.append(cur)
    chunks, cur = [], ""
    for cl in clauses:
        if cur and len(cur) + len(cl) > SUB_MAX:
            chunks.append(cur); cur = cl
        else:
            cur += cl
        if cur.endswith(("。", "？", "！")):
            chunks.append(cur); cur = ""
    if cur:
        chunks.append(cur)
    total = sum(len(c) for c in chunks); out = []; t = l0
    for c in chunks:
        d = (l1 - l0) * len(c) / total
        txt = c.rstrip("，。；：")
        out.append((txt, t, t + d)); t += d
    return out


def render_frame(c, T, tl):
    import skia, gfx, scenes
    global _BG
    if _BG is None:
        _BG = gfx.make_background()
    c.drawImage(_BG, 0, 0)
    sc = next((s for s in tl if s["start"] <= T < s["end"]), tl[-1])
    S = SceneT(sc); t = T - sc["start"]
    a = gfx.ease_out(gfx.prog(t, 0, 0.35)) * (1 - gfx.ease_in_out(gfx.prog(t, S.D - 0.3, 0.3)))
    if sc["id"] == "open": a = 1 - gfx.ease_in_out(gfx.prog(t, S.D - 0.3, 0.3))
    if sc["id"] == "end": a = gfx.ease_out(gfx.prog(t, 0, 0.35))
    dx, dy = scenes.shake(t, S) if sc["id"] == "law3" else (0, 0)
    with gfx.layer(c, a, dx, dy):
        scenes.DRAW[sc["id"]](c, t, S)
    if sc["id"] not in NO_BRAND:
        gfx.text(c, content.TITLE, gfx.W / 2, 150, 30, gfx.GREY, "serif_b", spacing=6)
        gfx.line(c, 280, 150, 360, 150, gfx.GREY, 3); gfx.line(c, 720, 150, 800, 150, gfx.GREY, 3)
    # subtitles
    for i, (l0, l1) in enumerate(zip(S.L, S.E)):
        if (sc["id"], i) in NO_SUB:
            continue
        nxt = S.L[i + 1] if i + 1 < len(S.L) else S.D
        chunks = sub_chunks(sc["subs"][i], l0, l1)
        for j, (txt, c0, c1) in enumerate(chunks):
            last = j == len(chunks) - 1
            hide = min(l1 + 0.3, nxt) if last else c1
            if not (c0 <= t < hide):
                continue
            sa = (gfx.prog(t, c0, 0.1) if j == 0 else 1) * (1 - gfx.prog(t, hide - 0.1, 0.1) if last else 1)
            lines = gfx.wrap(txt, 50, 900) if gfx.text_w(txt, 50) <= 900 else [txt[:len(txt) // 2], txt[len(txt) // 2:]]
            y0 = 1560 - (len(lines) - 1) * 36
            for k, ln in enumerate(lines):
                y = y0 + k * 72
                w = gfx.text_w(ln, 50)
                c.drawPath(gfx.rrect(540 - w / 2 - 24, y - 38, w + 48, 76, 14), gfx.fillp((255, 253, 249), 200 * sa))
                gfx.text(c, ln, 540, y, 50, gfx.INK, "sans_b", a=255 * sa)
    # global fade from / to black
    total = tl[-1]["end"]
    k = max(1 - gfx.prog(T, 0, 1.0), gfx.prog(T, total - 1.0, 1.0))
    if k > 0:
        c.drawRect(skia.Rect.MakeWH(gfx.W, gfx.H), gfx.fillp((0, 0, 0), 255 * k))


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def render_chunk(args):
    import skia, gfx
    idx, f0, f1, tl = args
    arr = np.zeros((gfx.H, gfx.W, 4), np.uint8)
    surf = skia.Surface(arr); c = surf.getCanvas()
    path = os.path.join(BUILD, f"part{idx:02d}.mp4")
    p = subprocess.Popen([ffmpeg(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                          "-s", f"{gfx.W}x{gfx.H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                          "-threads", "2", path], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        c.save(); render_frame(c, f / FPS, tl); c.restore()
        p.stdin.write(arr.tobytes())
    p.stdin.close(); p.wait()
    return path


def do_render(tl, audio, name="linshiwu_9x16.mp4", workers=8):
    total = tl[-1]["end"]; nf = int(math.ceil(total * FPS))
    step = int(math.ceil(nf / workers))
    jobs = [(i, i * step, min(nf, (i + 1) * step), tl) for i in range(workers) if i * step < nf]
    with Pool(len(jobs)) as pool:
        parts = pool.map(render_chunk, jobs)
    lst = os.path.join(BUILD, "parts.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    out = os.path.join(OUT, name)
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    print("video:", out)
    return out


def preview(tl, specs):
    import skia, gfx
    arr = np.zeros((gfx.H, gfx.W, 4), np.uint8)
    surf = skia.Surface(arr); c = surf.getCanvas()
    pdir = os.path.join(OUT, "preview"); os.makedirs(pdir, exist_ok=True)
    from PIL import Image
    outs = []
    for sp in specs:
        if "@" in sp:
            sid, fr = sp.split("@"); s = next(x for x in tl if x["id"] == sid)
            T = s["start"] + (s["end"] - s["start"]) * float(fr)
        else:
            T = float(sp)
        c.save(); render_frame(c, T, tl); c.restore()
        path = os.path.join(pdir, f"{sp.replace('@', '_').replace('.', '')}.png")
        Image.fromarray(arr.copy()).convert("RGB").resize((540, 960)).save(path)
        outs.append(path)
    print("\n".join(outs))


def do_srt(tl):
    def ts(x):
        h, r = divmod(x, 3600); m, s = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    k = 0; out = []
    for s in tl:
        for l0, l1, sub in zip(s["L"], s["E"], s["subs"]):
            for txt, c0, c1 in sub_chunks(sub, l0, l1):
                k += 1; out.append(f"{k}\n{ts(c0)} --> {ts(c1)}\n{txt}\n")
    path = os.path.join(OUT, "linshiwu.srt")
    open(path, "w").write("\n".join(out)); print("srt:", path)


def do_cover():
    import skia, gfx
    from PIL import Image
    arr = np.zeros((gfx.H, gfx.W, 4), np.uint8)
    surf = skia.Surface(arr); c = surf.getCanvas()
    c.drawImage(gfx.make_background(), 0, 0)
    with gfx.layer(c, 1, 540, 1260, 1.55):
        gfx.chair(c)
    gfx.text(c, "OBSERVATION  REPORT  ·  VOL.01", 540, 300, 28, gfx.GREY, "sans_m", spacing=4)
    gfx.text(c, "临时物", 540, 450, 160, gfx.INK, "serif_k")
    gfx.text(c, "永久化理论", 540, 630, 160, gfx.INK, "serif_k")
    c.drawPath(gfx.rrect(200, 740, 680, 14, 7), gfx.fillp(gfx.ORANGE))
    gfx.pill(c, "为什么这把椅子永远堆满衣服？", 540, 840, 42, gfx.INK)
    path = os.path.join(OUT, "linshiwu_cover.png")
    Image.fromarray(arr.copy()).convert("RGB").save(path); print("cover:", path)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "tts":
        do_tts()
    elif cmd == "preview":
        preview(load_timeline(), sys.argv[2:])
    elif cmd == "audio":
        do_audio(load_timeline())
    elif cmd == "cover":
        do_cover()
    elif cmd == "all":
        tl = do_tts(); a = do_audio(tl); do_render(tl, a); do_srt(tl); do_cover()
