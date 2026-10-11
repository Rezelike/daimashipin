"""
《60 秒看懂蝴蝶效应》—— 全部由代码生成的科普视频

画面中的每一条轨迹都是实时数值求解洛伦兹方程 (RK4) 得到的真实数据，不是手绘动画。
配音：gTTS（Google 中文语音），字幕/画面/音效按配音时长自动对齐。

用法:
    python make_video.py              # 渲染完整视频 -> out/butterfly.mp4 (+ .srt)
    python make_video.py --preview    # 只导出关键帧 PNG -> out/preview/
"""
import hashlib
import math
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
SR = 44100
TEMPO = 1.4  # 配音语速倍率
ROOT = Path(__file__).parent
FONT_DIR = ROOT.parent / "fonts"
OUT = ROOT / "out"
CACHE = ROOT / "tts_cache"
FF = imageio_ffmpeg.get_ffmpeg_exe()

# ============================================================ 字体 / 配色 / 工具
_fc = {}


def font(kind, size):
    if (kind, size) not in _fc:
        name = {"mono": "JetBrainsMono-Regular.ttf", "mono_b": "JetBrainsMono-Bold.ttf",
                "cn": "NotoSansSC-Regular.otf", "cn_b": "NotoSansSC-Bold.otf"}[kind]
        _fc[(kind, size)] = ImageFont.truetype(str(FONT_DIR / name), size)
    return _fc[(kind, size)]


C = dict(white=(236, 239, 244), text=(171, 178, 191), dim=(100, 108, 128), panel=(26, 30, 48),
         blue=(80, 170, 255), orange=(255, 150, 60), accent=(255, 209, 102),
         green=(102, 214, 140), red=(239, 83, 80), purple=(170, 120, 255))


def rgba(c, a=1.0):
    return (int(c[0]), int(c[1]), int(c[2]), int(max(0, min(1, a)) * 255))


def lerp_c(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def prog(t, s, d):
    return clamp((t - s) / d)


def text_c(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)


def tag(d, x, y, s, color, a=1.0, size=28, center=False):
    f = font("cn_b", size)
    w = d.textlength(s, font=f)
    if center:
        x -= (w + 32) / 2
    d.rounded_rectangle((x, y, x + w + 32, y + size + 22), 12, fill=rgba(color, 0.16 * a),
                        outline=rgba(color, a), width=2)
    d.text((x + 16, y + 7), s, font=f, fill=rgba(color, a))


def dashed(d, p0, p1, fill, width=2, dash=14, gap=10):
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    if L == 0:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    s = 0.0
    while s < L:
        e = min(L, s + dash)
        d.line((x0 + ux * s, y0 + uy * s, x0 + ux * e, y0 + uy * e), fill=fill, width=width)
        s += dash + gap


def make_bg():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    top, bot = np.array([8, 10, 20]), np.array([18, 20, 40])
    img = top + (bot - top) * (0.7 * y + 0.3 * x)[..., None]
    glow = np.exp(-(((x - 0.5) ** 2) / 0.12 + ((y - 0.45) ** 2) / 0.12))[..., None]
    img = img + glow * np.array([14, 10, 30])
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


BG = make_bg()


def new_layer():
    return Image.new("RGB", (W, H), (0, 0, 0))


def glow_onto(img, layer, blur=5):
    """把发光层叠加到画面上（缩小模糊再放大，速度快）"""
    small = layer.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur))
    halo = small.resize((W, H), Image.BILINEAR)
    return ImageChops.screen(img, ImageChops.add(layer, ImageChops.add(halo, halo)))


# ============================================================ 洛伦兹系统（真实数值计算）
SIG, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
DT = 0.005


def lorenz(s):
    x, y, z = s[..., 0], s[..., 1], s[..., 2]
    return np.stack([SIG * (y - x), x * (RHO - z) - y, x * y - BETA * z], -1)


def integrate(s0, n, every=1):
    s = np.array(s0, float)
    out = [s.copy()]
    for i in range(1, n + 1):
        k1 = lorenz(s)
        k2 = lorenz(s + DT / 2 * k1)
        k3 = lorenz(s + DT / 2 * k2)
        k4 = lorenz(s + DT * k3)
        s = s + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if i % every == 0:
            out.append(s.copy())
    return np.array(out)


print("求解洛伦兹方程 ...", flush=True)
A0 = integrate([1, 1, 1], 3000)[-1]          # 先跑一段，落到吸引子上
BGT = integrate(A0, 8000, every=2)           # 吸引子背景轮廓（40 个时间单位）
T_MAX = 30.0
NS = int(T_MAX / DT)
TIMES = np.arange(NS + 1) * DT
TA = integrate(A0, NS)                       # 轨迹 A
TB = integrate(A0 + [1e-5, 0, 0], NS)        # 轨迹 B：只差 0.00001
TC = integrate(A0 + [1.27e-4, 0, 0], NS)     # 洛伦兹故事：0.506127 vs 0.506
DIST = np.linalg.norm(TA - TB, axis=1)
T_SEP = float(TIMES[np.argmax(DIST > 5)])    # 两条轨迹“彻底分开”的时刻
_m = (DIST > 1e-4) & (DIST < 1) & (TIMES < T_SEP)
LAM = float(np.polyfit(TIMES[_m], np.log(DIST[_m]), 1)[0])  # 李雅普诺夫指数（实测）
LOG_D0 = float(np.polyfit(TIMES[_m], np.log(DIST[_m]), 1)[1])
DOUBLE = math.log(2) / LAM
PLUS10 = math.log(10) / LAM
_rng = np.random.default_rng(1)
_off = _rng.standard_normal((1000, 3))
_off = _off / np.linalg.norm(_off, axis=1, keepdims=True) * _rng.uniform(0, 1e-3, (1000, 1))
CLOUD_EVERY = 5
CLOUD_T = 22.0
CLOUD = integrate(A0 + _off, int(CLOUD_T / DT), every=CLOUD_EVERY)  # (帧, 1000, 3)
CLOUD_HUE = np.argsort(np.argsort(_off[:, 0])) / 999.0
print(f"  分离时刻 t={T_SEP:.2f}  λ={LAM:.3f}  误差翻倍时间={DOUBLE:.2f}", flush=True)


def proj(P, th, cx, cy, sc, tilt=0.32):
    x, y, z = P[..., 0], P[..., 1], P[..., 2] - 25
    X = x * np.cos(th) - y * np.sin(th)
    D = x * np.sin(th) + y * np.cos(th)
    Y = z * np.cos(tilt) - D * np.sin(tilt)
    return np.stack([cx + X * sc, cy - Y * sc], -1)


def polyline(d, pts, fill, width):
    if len(pts) >= 2:
        d.line(pts.ravel().tolist(), fill=fill, width=width, joint="curve")


def trail(d, pts, color, width=3, a=1.0, segs=20):
    n = len(pts)
    if n < 2:
        return
    edges = np.linspace(0, n - 1, segs + 1).astype(int)
    for k in range(segs):
        i0, i1 = edges[k], edges[k + 1]
        if i1 > i0:
            polyline(d, pts[i0:i1 + 1], rgba(color, a * ((k + 1) / segs) ** 1.6), width)


def dot(d, p, r, color, a=1.0):
    d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=rgba(color, a))


# ============================================================ 场景框架（按配音时长自动排时间）
class Scene:
    min_dur = 5.0
    lead, gap, tail = 0.4, 0.25, 0.5
    lines = []  # (字幕, 朗读文本 or None, 最早开始时间)

    def layout(self, durs):
        t, self.starts = self.lead, []
        for (disp, spoken, want), dd in zip(self.lines, durs):
            t = max(t, want)
            self.starts.append(t)
            t += dd + self.gap
        self.ends = [s + dd for s, dd in zip(self.starts, durs)]
        self.dur = max(self.min_dur, (self.ends[-1] if self.ends else 0) + self.tail)

    def captions(self):
        out = []
        for i, (disp, _, _) in enumerate(self.lines):
            nxt = self.starts[i + 1] if i + 1 < len(self.lines) else self.dur
            out.append((self.starts[i], min(nxt, self.ends[i] + 0.6), disp))
        return out

    def sounds(self):
        return [(0.0, "whoosh")]

    def draw(self, img, d, t):
        return img


def attractor_bg(d, th, cx, cy, sc, a=0.16, color=(140, 150, 200), n=None):
    pts = proj(BGT if n is None else BGT[:n], th, cx, cy, sc)
    polyline(d, pts, rgba(color, a), 1)


# ------------------------------------------------------------ 1. 片头
class Title(Scene):
    min_dur = 5.5
    lines = [("巴西的一只蝴蝶扇扇翅膀，会引起德州的一场龙卷风吗？", None, 0.6)]

    def sounds(self):
        return [(0.2, "whoosh"), (1.0, "ding")]

    def draw(self, img, d, t):
        layer = new_layer()
        ld = ImageDraw.Draw(layer, "RGBA")
        n = int(len(BGT) * ease_in_out(prog(t, 0, self.dur - 0.5)))
        if n > 2:
            pts = proj(BGT[:n], 0.5 + 0.06 * t, W / 2, 500, 15)
            polyline(ld, pts, rgba(C["purple"], 0.22), 1)
            dot(ld, pts[-1], 6, C["white"])
        img = glow_onto(img, layer)
        d = ImageDraw.Draw(img, "RGBA")
        p = ease_out(prog(t, 0.2, 0.8))
        tag(d, W / 2, 250 - 20 * (1 - p), "混沌理论 · 60 秒", C["accent"], p, 30, center=True)
        p2 = ease_out(prog(t, 0.5, 0.9))
        text_c(d, W / 2, 360 + 40 * (1 - p2), "蝴蝶效应", font("cn_b", 150), rgba(C["white"], p2))
        p3 = ease_out(prog(t, 0.9, 0.9))
        text_c(d, W / 2, 570 + 30 * (1 - p3), "The Butterfly Effect", font("mono_b", 60), rgba(C["blue"], p3))
        p4 = ease_out(prog(t, 1.4, 0.9))
        text_c(d, W / 2, 690, "Edward Lorenz · 1972", font("mono", 32), rgba(C["text"], p4))
        return img


# ------------------------------------------------------------ 2. 洛伦兹的故事
class Story(Scene):
    min_dur = 10.0
    lines = [("1961 年，洛伦兹做天气模拟时，把 0.506127 偷懒输成了 0.506",
              "一九六一年，洛伦兹做天气模拟时，把零点五零六一二七，偷懒输成了零点五零六。", 0.4),
             ("结果：两次预报一开始几乎一样，后来完全不同", "结果两次预报，一开始几乎一样，后来完全不同。", 0)]
    PX0, PX1, PY, PS, PT = 200, 1720, 700, 10, 25.0

    def layout(self, durs):
        super().layout(durs)
        self.strike = self.ends[0] - 1.3
        self.plot0 = self.starts[1] - 0.3
        self.plot1 = self.dur - 0.6
        k = int(self.PT / DT)
        self.sep_i = int(np.argmax(np.abs(TA[:k, 0] - TC[:k, 0]) > 3))

    def sounds(self):
        return [(0.0, "whoosh"), (self.strike, "pop")]

    def draw(self, img, d, t):
        p = ease_out(prog(t, 0.1, 0.6))
        text_c(d, W / 2, 110, "1961 · 洛伦兹的天气模拟", font("cn", 36), rgba(C["dim"], p))
        f = font("mono_b", 100)
        if t > 0.6:
            pa = ease_out(prog(t, 0.6, 0.5))
            w_all, w_head = d.textlength("0.506127", font=f), d.textlength("0.506", font=f)
            x, y = W / 2 - w_all / 2 - 160, 170
            d.text((x, y), "0.506", font=f, fill=rgba(C["white"], pa))
            sp = prog(t, self.strike, 0.4)
            col = lerp_c(C["white"], C["red"], sp)
            d.text((x + w_head, y), "127", font=f, fill=rgba(col, pa * (1 - 0.6 * sp)))
            if sp > 0:
                d.line((x + w_head - 6, y + 72, x + w_head + (w_all - w_head + 12) * sp, y + 72),
                       fill=rgba(C["red"], 1), width=7)
            pn = ease_out(prog(t, self.strike + 0.3, 0.5))
            d.text((x + w_all + 50, y + 34), "← 只差 0.000127", font=font("cn_b", 44), fill=rgba(C["accent"], pn))
        if t > self.plot0 - 0.4:
            pp = ease_out(prog(t, self.plot0 - 0.4, 0.4))
            d.line((self.PX0, self.PY, self.PX1, self.PY), fill=rgba(C["dim"], 0.6 * pp), width=2)
            d.text((self.PX0, 440), "模拟出的天气变量 x(t)", font=font("cn", 28), fill=rgba(C["dim"], pp))
            d.line((self.PX0 + 380, 458, self.PX0 + 420, 458), fill=rgba(C["blue"], pp), width=4)
            d.text((self.PX0 + 430, 440), "0.506127", font=font("mono", 26), fill=rgba(C["blue"], pp))
            d.line((self.PX0 + 600, 458, self.PX0 + 640, 458), fill=rgba(C["orange"], pp), width=4)
            d.text((self.PX0 + 650, 440), "0.506", font=font("mono", 26), fill=rgba(C["orange"], pp))
            k = int(self.PT / DT * ease_in_out(prog(t, self.plot0, self.plot1 - self.plot0)))
            if k > 2:
                xs = self.PX0 + (self.PX1 - self.PX0) * TIMES[:k:4] / self.PT
                for traj, col, wd in ((TC, C["orange"], 5), (TA, C["blue"], 3)):
                    pts = np.stack([xs, self.PY - traj[:k:4, 0] * self.PS], -1)
                    polyline(d, pts, rgba(col), wd)
            if k > self.sep_i:
                xs = self.PX0 + (self.PX1 - self.PX0) * TIMES[self.sep_i] / self.PT
                ps = ease_out((k - self.sep_i) / 300)
                dashed(d, (xs, 480), (xs, 920), rgba(C["accent"], ps), 3)
                d.text((xs + 14, 486), "从这里分道扬镳", font=font("cn_b", 30), fill=rgba(C["accent"], ps))
        return img


# ------------------------------------------------------------ 3. 方程
EQS = ["dx/dt = σ(y − x)", "dy/dt = x(ρ − z) − y", "dz/dt = xy − βz"]
EQ_LABELS = ["x：对流的强弱", "y：上升、下沉气流的温差", "z：垂直方向的温度分布"]


class Equations(Scene):
    min_dur = 7.5
    lines = [("他把大气对流简化成 3 个方程", "他把大气对流，简化成三个方程，", 0.4),
             ("没有任何随机性：起点相同，结果就永远相同", "没有任何随机性，起点相同，结果就永远相同。", 0)]

    def draw(self, img, d, t):
        f = font("mono_b", 66)
        cw = f.getlength("M")
        for i, eq in enumerate(EQS):
            p = ease_out(prog(t, 0.4 + i * 0.5, 0.6))
            x, y = 300 + 40 * (1 - p), 200 + i * 150
            for j, ch in enumerate(eq):
                col = C["accent"] if ch in "σρβ" else (C["blue"] if ch in "xyz" else C["white"])
                d.text((x + j * cw, y), ch, font=f, fill=rgba(col, p))
            d.text((1200, y + 18), EQ_LABELS[i], font=font("cn", 36), fill=rgba(C["text"], p))
        p = ease_out(prog(t, 2.0, 0.6))
        d.text((300, 680), "σ = 10     ρ = 28     β = 8/3", font=font("mono", 44), fill=rgba(C["accent"], p))
        if len(self.starts) > 1:
            p = ease_out(prog(t, self.starts[1], 0.5))
            tag(d, W / 2, 800, "100% 确定 · 没有一丝随机", C["green"], p, 36, center=True)
        return img


# ------------------------------------------------------------ 4. 两条轨迹
V4 = 1.5     # 模拟速度：时间单位 / 秒
S4_0 = 1.2   # 第几秒开始运动


def sim4(t):
    return clamp((t - S4_0) * V4, 0, T_MAX)


class TwoPaths(Scene):
    lines = [("那如果两个起点只差 0.00001 呢？", "那如果，两个起点只差十万分之一呢？", 0.3),
             ("一开始，两条轨迹完全重合", "一开始，两条轨迹完全重合，", S4_0 + 1.5),
             ("但误差悄悄放大……最后分道扬镳", "但误差悄悄放大，最后分道扬镳。", S4_0 + (T_SEP - 3.5) / V4)]
    min_dur = S4_0 + (T_SEP + 4.5) / V4
    CX, CY, SC = 700, 500, 15

    def melody_times(self):
        out, t = [], S4_0
        while t < self.dur - 0.5:
            out.append(t)
            t += 0.25
        return out

    def draw(self, img, d, t):
        s = sim4(t)
        i = int(s / DT)
        th = 0.4 + 0.12 * t
        layer = new_layer()
        ld = ImageDraw.Draw(layer, "RGBA")
        attractor_bg(ld, th, self.CX, self.CY, self.SC, 0.22)
        i0 = max(0, i - int(1.3 / DT))
        pa = proj(TA[i0:i + 1:2], th, self.CX, self.CY, self.SC)
        pb = proj(TB[i0:i + 1:2], th, self.CX, self.CY, self.SC)
        trail(ld, pb, C["orange"], 7)
        trail(ld, pa, C["blue"], 3)
        dot(ld, pb[-1], 12, C["orange"])
        dot(ld, pa[-1], 7, C["blue"])
        dot(ld, pa[-1], 3, C["white"])
        img = glow_onto(img, layer)
        d = ImageDraw.Draw(img, "RGBA")

        # 信息面板
        p = ease_out(prog(t, 0.2, 0.6))
        X = 1330
        d.rounded_rectangle((X, 150, 1800, 820), 24, fill=rgba(C["panel"], 0.85 * p),
                            outline=rgba(C["dim"], 0.5 * p), width=2)
        dot(d, (X + 50, 222), 10, C["blue"], p)
        d.text((X + 75, 200), "起点 A", font=font("cn_b", 34), fill=rgba(C["white"], p))
        dot(d, (X + 260, 222), 12, C["orange"], p)
        d.text((X + 285, 200), "起点 B", font=font("cn_b", 34), fill=rgba(C["white"], p))
        d.text((X + 40, 270), "初始相差  0.00001", font=font("cn", 32), fill=rgba(C["text"], p))
        dist = float(DIST[i])
        u = clamp((math.log10(max(dist, 1e-6)) + 5) / 6)
        col = lerp_c(C["green"], C["red"], u)
        d.text((X + 40, 360), "当前距离", font=font("cn", 30), fill=rgba(C["dim"], p))
        s_d = f"{dist:.6f}" if dist < 0.1 else (f"{dist:.3f}" if dist < 10 else f"{dist:.1f}")
        d.text((X + 40, 400), s_d, font=font("mono_b", 76), fill=rgba(col, p))
        amp = dist / 1e-5
        d.text((X + 40, 520), "误差被放大了", font=font("cn", 30), fill=rgba(C["dim"], p))
        d.text((X + 40, 560), f"{amp:,.0f} 倍", font=font("cn_b", 60), fill=rgba(col, p))
        # 进度条（对数）
        d.rounded_rectangle((X + 40, 670, X + 430, 690), 10, fill=rgba(C["dim"], 0.3 * p))
        d.rounded_rectangle((X + 40, 670, X + 40 + 390 * max(u, 0.03), 690), 10, fill=rgba(col, p))
        d.text((X + 40, 720), "t = %.1f" % s, font=font("mono", 28), fill=rgba(C["dim"], p))
        d.text((X + 40, 770), "戴耳机：左耳 A · 右耳 B", font=font("cn", 24), fill=rgba(C["dim"], p))
        return img


# ------------------------------------------------------------ 5. 对数坐标
class LogPlot(Scene):
    min_dur = 9.0
    lines = [("对数坐标下，距离几乎是一条直线：误差在指数增长", "对数坐标下，距离几乎是直线，误差在指数增长。", 0.4),
             ("测量精度提高 10 倍，也只能多预测一小会儿", "测量精度提高十倍，也只能多预测一小会儿。", 0)]
    X0, X1, Y0, Y1 = 330, 1680, 150, 830
    LMIN, LMAX = -6, 2

    def __init__(self):
        self.TM = T_SEP + 5

    def sx(self, t):
        return self.X0 + (self.X1 - self.X0) * t / self.TM

    def sy(self, lg):
        return self.Y1 - (self.Y1 - self.Y0) * (lg - self.LMIN) / (self.LMAX - self.LMIN)

    def draw(self, img, d, t):
        p = ease_out(prog(t, 0, 0.5))
        for lg, lab in [(-5, "0.00001"), (-3, "0.001"), (-1, "0.1"), (1, "10")]:
            y = self.sy(lg)
            d.line((self.X0, y, self.X1, y), fill=rgba(C["dim"], 0.25 * p), width=1)
            d.text((self.X0 - 20 - d.textlength(lab, font=font("mono", 26)), y - 16), lab,
                   font=font("mono", 26), fill=rgba(C["dim"], p))
        d.line((self.X0, self.Y1, self.X1, self.Y1), fill=rgba(C["dim"], p), width=2)
        d.line((self.X0, self.Y0, self.X0, self.Y1), fill=rgba(C["dim"], p), width=2)
        d.text((self.X1 - 120, self.Y1 + 14), "时间 →", font=font("cn", 28), fill=rgba(C["dim"], p))
        d.text((self.X0 + 10, self.Y0 - 50), "A、B 两点距离（对数坐标）", font=font("cn", 28), fill=rgba(C["dim"], p))
        # 实测曲线
        k = int(self.TM / DT * ease_in_out(prog(t, 0.5, self.starts[0] + 3.0)))
        k = min(k, len(DIST) - 1)
        if k > 2:
            tt = TIMES[:k:3]
            pts = np.stack([self.sx(tt), self.sy(np.log10(np.maximum(DIST[:k:3], 1e-7)))], -1)
            polyline(d, pts, rgba(C["red"]), 3)
        # 拟合直线
        pf = ease_out(prog(t, self.starts[0] + 2.0, 0.8))
        if pf > 0:
            te = T_SEP * pf
            f0 = (self.sx(0), self.sy(LOG_D0 / math.log(10)))
            f1 = (self.sx(te), self.sy((LOG_D0 + LAM * te) / math.log(10)))
            dashed(d, f0, f1, rgba(C["accent"], 0.9), 3)
            tag(d, self.X0 + 40, self.Y0 + 10, f"指数增长：误差每 {DOUBLE:.2f} 个时间单位翻一倍", C["accent"], pf, 32)
        if k > int(T_SEP / DT):
            pq = ease_out((k - T_SEP / DT) / 400)
            d.text((self.sx(T_SEP) + 60, self.sy(-0.4)), "饱和：两者已毫无关系", font=font("cn_b", 30),
                   fill=rgba(C["red"], pq))
        if len(self.starts) > 1:
            pz = ease_out(prog(t, self.starts[1], 0.6))
            tag(d, self.X0 + 40, self.Y0 + 90, f"初始误差缩小 10 倍  →  可预测时间只多 {PLUS10:.1f}",
                C["blue"], pz, 32)
        return img


# ------------------------------------------------------------ 6. 一千个起点
V6, S6_0 = 2.0, 0.6


class Cloud(Scene):
    min_dur = 10.0
    lines = [("1000 个几乎相同的起点，很快散布到整只“蝴蝶”上", "一千个几乎相同的起点，很快散布到整只蝴蝶上。", 0.4),
             ("所以，天气预报很难超过两周", "所以，天气预报很难超过两周。", 5.5)]
    CX, CY, SC = 860, 500, 15

    def draw(self, img, d, t):
        s = clamp((t - S6_0) * V6, 0, CLOUD_T)
        fi = min(int(s / (DT * CLOUD_EVERY)), len(CLOUD) - 1)
        th = 1.0 + 0.1 * t
        layer = new_layer()
        ld = ImageDraw.Draw(layer, "RGBA")
        attractor_bg(ld, th, self.CX, self.CY, self.SC, 0.2)
        pts = proj(CLOUD[fi], th, self.CX, self.CY, self.SC)
        for (x, y), h in zip(pts, CLOUD_HUE):
            col = tuple(int(v) for v in lerp_c(C["blue"], C["orange"], h))
            ld.ellipse((x - 2.6, y - 2.6, x + 2.6, y + 2.6), fill=col)
        img = glow_onto(img, layer, 4)
        d = ImageDraw.Draw(img, "RGBA")
        p = ease_out(prog(t, 0.2, 0.6))
        spread = float(np.mean(np.std(CLOUD[fi], axis=0)))
        d.text((120, 150), "1000 个起点", font=font("cn_b", 44), fill=rgba(C["white"], p))
        d.text((120, 215), "初始差距 < 0.001", font=font("cn", 32), fill=rgba(C["text"], p))
        d.text((120, 300), "散布范围", font=font("cn", 30), fill=rgba(C["dim"], p))
        s_sp = f"{spread:.5f}" if spread < 0.1 else f"{spread:.1f}"
        u = clamp((math.log10(max(spread, 1e-5)) + 4) / 5)
        d.text((120, 340), s_sp, font=font("mono_b", 64), fill=rgba(lerp_c(C["green"], C["red"], u), p))
        d.text((120, 440), "t = %.1f" % s, font=font("mono", 28), fill=rgba(C["dim"], p))
        if len(self.starts) > 1:
            pz = ease_out(prog(t, self.starts[1], 0.6))
            tag(d, 1460, 170, "短期：能预测", C["green"], pz, 32)
            tag(d, 1460, 250, "长期：不可能", C["red"], ease_out(prog(t, self.starts[1] + 0.5, 0.6)), 32)
        return img


# ------------------------------------------------------------ 7. 总结
class Summary(Scene):
    min_dur = 7.5
    lines = [("确定的规则，也能产生无法预测的结果——这就是混沌", "确定的规则，也能产生无法预测的结果，这就是混沌。", 0.5)]

    def sounds(self):
        return [(0.0, "whoosh"), (0.4, "ding")] + [(1.4 + i * 0.35, "pop") for i in range(3)]

    def draw(self, img, d, t):
        layer = new_layer()
        ld = ImageDraw.Draw(layer, "RGBA")
        attractor_bg(ld, 2.0 + 0.1 * t, W / 2, 520, 15, 0.25, C["purple"])
        img = glow_onto(img, layer)
        d = ImageDraw.Draw(img, "RGBA")
        p = ease_out(prog(t, 0.1, 0.7))
        text_c(d, W / 2, 150 + 30 * (1 - p), "蝴蝶效应 = 对初始条件的敏感依赖", font("cn_b", 76), rgba(C["white"], p))
        cards = [("确定 ≠ 可预测", "规则里没有随机性"),
                 ("误差指数放大", f"每 {DOUBLE:.1f} 个时间单位翻倍"),
                 ("无处不在", "天气 · 三体运动 · 种群数量")]
        for i, (h, sub) in enumerate(cards):
            pp = ease_out(prog(t, 1.4 + i * 0.35, 0.6))
            x, y = 230 + i * 500, 380 + 50 * (1 - pp)
            d.rounded_rectangle((x, y, x + 460, y + 250), 24, fill=rgba(C["panel"], 0.9 * pp),
                                outline=rgba(C["blue"], 0.6 * pp), width=2)
            text_c(d, x + 230, y + 60, h, font("cn_b", 50), rgba(C["accent"], pp))
            text_c(d, x + 230, y + 150, sub, font("cn", 32), rgba(C["text"], pp))
        pn = ease_out(prog(t, self.dur - 3.5, 0.6))
        tag(d, W / 2, 760, "下期预告：三体问题为什么没有通解？", C["purple"], pn, 34, center=True)
        return img


SCENES = [Title(), Story(), Equations(), TwoPaths(), LogPlot(), Cloud(), Summary()]


# ============================================================ 配音
def tts(text):
    """gTTS 合成 → 去首尾静音 → 加速，返回 float32 单声道 SR 采样"""
    CACHE.mkdir(exist_ok=True)
    mp3 = CACHE / (hashlib.md5(text.encode()).hexdigest()[:16] + ".mp3")
    if not mp3.exists():
        from gtts import gTTS
        gTTS(text, lang="zh-CN").save(str(mp3))
    af = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          f"atempo={TEMPO}")
    raw = subprocess.run([FF, "-loglevel", "error", "-i", str(mp3), "-af", af, "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    return a / (np.abs(a).max() + 1e-9) * 0.85


print("生成配音 ...", flush=True)
VOICE = []
for sc in SCENES:
    clips = [tts(sp or disp) for disp, sp, _ in sc.lines]
    VOICE.append(clips)
    sc.layout([len(c) / SR for c in clips])

STARTS, _acc = [], 0.0
for sc in SCENES:
    STARTS.append(_acc)
    _acc += sc.dur
TOTAL = _acc
FADE = 0.35
CAPTIONS = [(s + a, s + b, txt) for s, sc in zip(STARTS, SCENES) for a, b, txt in sc.captions()]


# ============================================================ 渲染
def draw_caption(d, t):
    for t0, t1, txt in CAPTIONS:
        if t0 <= t < t1:
            a = min(prog(t, t0, 0.15), 1 - prog(t, t1 - 0.15, 0.15))
            f = font("cn_b", 44)
            w = d.textlength(txt, font=f)
            d.rounded_rectangle((W / 2 - w / 2 - 30, 963, W / 2 + w / 2 + 30, 1041), 14, fill=(0, 0, 0, int(160 * a)))
            text_c(d, W / 2, 975, txt, f, rgba(C["white"], a))


def render_frame(t):
    img = BG.copy()
    for s, sc in zip(STARTS, SCENES):
        if s <= t < s + sc.dur:
            local = t - s
            img = sc.draw(img, ImageDraw.Draw(img, "RGBA"), local)
            fade = min(prog(local, 0, FADE), 1 - prog(local, sc.dur - FADE, FADE))
            if fade < 1:
                img = Image.blend(BG, img, ease_in_out(fade))
            break
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, H - 6, W * t / TOTAL, H), fill=rgba(C["accent"], 0.9))
    draw_caption(d, t)
    return img


# ============================================================ 音频
def synth(kind, rng, freq=440.0):
    if kind == "pluck":
        n = int(SR * 0.5)
        tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * freq * tt) + 0.3 * np.sin(2 * np.pi * 2 * freq * tt)
        return s * np.exp(-tt * 7) * np.minimum(1, tt / 0.004)
    if kind == "pop":
        n = int(SR * 0.08)
        tt = np.arange(n) / SR
        f = 900 - 500 * tt / tt[-1]
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40) * 0.25
    if kind == "ding":
        n = int(SR * 0.8)
        tt = np.arange(n) / SR
        return (np.sin(2 * np.pi * 1320 * tt) + 0.5 * np.sin(2 * np.pi * 1980 * tt)) * np.exp(-tt * 6) * 0.18
    if kind == "whoosh":
        n = int(SR * 0.5)
        noise = np.convolve(rng.standard_normal(n), np.ones(200) / 200, mode="same") * 8
        return noise * np.sin(np.pi * np.linspace(0, 1, n)) ** 2 * 0.15
    raise ValueError(kind)


PENTA = [0, 3, 5, 7, 10, 12, 15, 17, 19, 22, 24, 27]


def note_freq(x):
    deg = int(np.clip(round((x + 17) / 34 * (len(PENTA) - 1)), 0, len(PENTA) - 1))
    return 220 * 2 ** (PENTA[deg] / 12)


def mix(buf, snd, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(snd))
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    buf[i:j, 0] += snd[: j - i] * gain * l * 1.414
    buf[i:j, 1] += snd[: j - i] * gain * r * 1.414


def build_audio(path):
    rng = np.random.default_rng(3)
    n = int(SR * (TOTAL + 0.5))
    voice = np.zeros((n, 2))
    music = np.zeros((n, 2))
    # 背景铺底和弦 Am - F - C - G
    tt = np.arange(n) / SR
    chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [130.8, 196, 261.6], [196, 246.9, 293.7]]
    bar = 4.0
    for ci in range(int(TOTAL / bar) + 1):
        s0, s1 = int(ci * bar * SR), min(n, int((ci + 1) * bar * SR))
        if s0 >= n:
            break
        st = tt[s0:s1] - ci * bar
        env = np.minimum(1, st / 1.0) * np.minimum(1, (bar - st) / 1.0)
        for fr in chords[ci % 4]:
            music[s0:s1] += (np.sin(2 * np.pi * fr * tt[s0:s1]) * env * 0.022)[:, None]
    for s, sc, clips in zip(STARTS, SCENES, VOICE):
        for lt, clip in zip(sc.starts, clips):
            mix(voice, clip, s + lt, 0.9)
        for lt, kind in sc.sounds():
            mix(music, synth(kind, rng), s + lt)
        if isinstance(sc, TwoPaths):  # 两条轨迹 → 左右声道两段旋律
            for lt in sc.melody_times():
                i = int(sim4(lt) / DT)
                mix(music, synth("pluck", rng, note_freq(TA[i, 0])), s + lt, 0.09, -0.85)
                mix(music, synth("pluck", rng, note_freq(TB[i, 0])), s + lt, 0.09, 0.85)
    # 人声出现时压低背景音乐
    env = np.abs(voice).max(axis=1)
    k = int(SR * 0.3)
    env = np.convolve(env > 0.02, np.ones(k) / k, mode="same")
    music *= (1 - 0.55 * np.clip(env * 3, 0, 1))[:, None]
    buf = voice + music
    fade = int(SR * 1.0)
    buf[-fade:] *= np.linspace(1, 0, fade)[:, None]
    buf = np.clip(buf, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((buf * 32767).astype(np.int16).tobytes())


def write_srt(path):
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, txt) in enumerate(CAPTIONS, 1):
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")


def main():
    OUT.mkdir(exist_ok=True)
    print(f"总时长 {TOTAL:.1f}s：" + ", ".join(f"{type(s).__name__}={s.dur:.1f}" for s in SCENES))
    if "--preview" in sys.argv:
        pdir = OUT / "preview"
        pdir.mkdir(exist_ok=True)
        for old in pdir.glob("*.png"):
            old.unlink()
        for k, (s, sc) in enumerate(zip(STARTS, SCENES)):
            for f in (0.5, 0.92):
                t = s + sc.dur * f
                render_frame(t).save(pdir / f"{k}_{type(sc).__name__}_{t:05.1f}s.png")
        print("preview ->", pdir)
        return
    wav, mp4 = OUT / "audio.wav", OUT / "butterfly.mp4"
    build_audio(wav)
    write_srt(OUT / "butterfly.srt")
    cmd = [FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(mp4)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(TOTAL * FPS)
    for i in range(nf):
        proc.stdin.write(render_frame(i / FPS).tobytes())
        if i % (FPS * 10) == 0:
            print(f"  {i / FPS:5.1f}s / {TOTAL:.1f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    wav.unlink()
    print("done ->", mp4)


if __name__ == "__main__":
    main()
