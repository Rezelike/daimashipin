"""
60 秒代码讲解视频生成器 —— 主题：《60 秒搞懂 防抖 Debounce》

纯代码出片：Pillow 逐帧绘制 + Pygments 语法高亮 + numpy 合成音效 + ffmpeg 编码。
用法:
    python make_video.py              # 渲染完整视频 -> out/debounce.mp4 (+ .srt)
    python make_video.py --preview    # 只导出若干关键帧 PNG -> out/preview/
"""
import math
import random
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pygments.lexers import JavascriptLexer
from pygments.token import Token

W, H, FPS = 1920, 1080, 30
ROOT = Path(__file__).parent
OUT = ROOT / "out"
FONT_DIR = ROOT / "fonts"

# ---------------------------------------------------------------- 字体 & 配色
_font_cache = {}


def font(kind, size):
    key = (kind, size)
    if key not in _font_cache:
        path = {
            "mono": "JetBrainsMono-Regular.ttf",
            "mono_b": "JetBrainsMono-Bold.ttf",
            "cn": "NotoSansSC-Regular.otf",
            "cn_b": "NotoSansSC-Bold.otf",
        }[kind]
        _font_cache[key] = ImageFont.truetype(str(FONT_DIR / path), size)
    return _font_cache[key]


C = dict(
    text=(171, 178, 191), dim=(92, 99, 112), white=(236, 239, 244),
    kw=(198, 120, 221), fn=(97, 175, 239), str=(152, 195, 121),
    num=(209, 154, 102), var=(224, 108, 117), op=(86, 182, 194),
    panel=(30, 34, 51), bar=(38, 43, 64), accent=(255, 209, 102),
    red=(239, 83, 80), green=(102, 214, 140), blue=(97, 175, 239),
)


def rgba(c, a=1.0):
    return (c[0], c[1], c[2], int(max(0, min(1, a)) * 255))


# ---------------------------------------------------------------- 动画工具
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def prog(t, start, dur):
    return clamp((t - start) / dur)


def make_background():
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    top, bottom = np.array([14, 17, 31]), np.array([24, 28, 52])
    img = top + (bottom - top) * (0.6 * y + 0.4 * x)[..., None]
    # 右上角一点光晕
    glow = np.exp(-(((x - 0.85) ** 2) / 0.05 + ((y - 0.1) ** 2) / 0.08))[..., None]
    img = img + glow * np.array([40, 30, 80])
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


BG = make_background()


def text_center(d, cx, y, s, f, fill):
    w = d.textlength(s, font=f)
    d.text((cx - w / 2, y), s, font=f, fill=fill)


def window(d, box, title, a=1.0):
    """Mac 风格编辑器窗口"""
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + 8, y0 + 14, x1 + 8, y1 + 14), 22, fill=(0, 0, 0, int(90 * a)))
    d.rounded_rectangle(box, 20, fill=rgba(C["panel"], a))
    d.rounded_rectangle((x0, y0, x1, y0 + 56), 20, fill=rgba(C["bar"], a))
    d.rectangle((x0, y0 + 36, x1, y0 + 56), fill=rgba(C["bar"], a))
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = x0 + 34 + i * 30
        d.ellipse((cx - 8, y0 + 20, cx + 8, y0 + 36), fill=rgba(col, a))
    text_center(d, (x0 + x1) / 2, y0 + 14, title, font("mono", 22), rgba(C["dim"], a))


def tag(d, x, y, s, color, a=1.0, size=26):
    f = font("cn_b", size)
    w = d.textlength(s, font=f)
    d.rounded_rectangle((x, y, x + w + 32, y + size + 22), 12, fill=rgba(color, 0.18 * a),
                        outline=rgba(color, a), width=2)
    d.text((x + 16, y + 7), s, font=f, fill=rgba(color, a))


# ---------------------------------------------------------------- 代码高亮
CODE = """function debounce(fn, delay = 300) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}

input.addEventListener('input', debounce(search, 300));"""


def colorize(code):
    """返回 [(char, color)]，标识符后面紧跟 '(' 的着色为函数"""
    toks = list(JavascriptLexer().get_tokens(code))
    out = []
    for i, (tt, v) in enumerate(toks):
        nxt = toks[i + 1][1] if i + 1 < len(toks) else ""
        if tt in Token.Keyword:
            col = C["kw"]
        elif tt in Token.Literal.String:
            col = C["str"]
        elif tt in Token.Literal.Number:
            col = C["num"]
        elif tt in Token.Operator or v == "=>":
            col = C["op"]
        elif tt in Token.Name:
            col = C["fn"] if nxt.startswith("(") else C["var"]
        else:
            col = C["text"]
        out += [(ch, col) for ch in v]
    if out and out[-1][0] == "\n" and not code.endswith("\n"):
        out.pop()
    return out


def draw_code(d, chars, n, x0, y0, f, lh, a=1.0):
    """绘制前 n 个字符（按颜色分段），返回光标所在 (行, 列)"""
    cw = f.getlength("M")
    line, col = 0, 0
    run, run_col, run_start = "", None, 0

    def flush():
        if run:
            d.text((x0 + run_start * cw, y0 + line * lh), run, font=f, fill=rgba(run_col, a))

    for ch, colr in chars[:n]:
        if ch == "\n":
            flush()
            run, run_col = "", None
            line, col = line + 1, 0
            continue
        if colr != run_col:
            flush()
            run, run_col, run_start = "", colr, col
        run += ch
        col += 1
    flush()
    return line, col


# ---------------------------------------------------------------- 场景基类
class Scene:
    dur = 5.0

    def captions(self):  # [(t0, t1, text)] 局部时间
        return []

    def sounds(self):  # [(t, kind)] 局部时间
        return []

    def draw(self, img, d, t):
        raise NotImplementedError


# ---------------------------------------------------------------- 1. 片头
class Title(Scene):
    dur = 4.0

    def captions(self):
        return [(0.6, 3.8, "一个高频面试题 + 实战技巧，60 秒讲清楚")]

    def sounds(self):
        return [(0.1, "whoosh"), (0.9, "ding")]

    def draw(self, img, d, t):
        p = ease_out(prog(t, 0.1, 0.8))
        tag(d, W / 2 - 90, 280 - 30 * (1 - p), "60 秒 · 代码", C["accent"], p, 30)
        p2 = ease_out(prog(t, 0.4, 0.8))
        f = font("cn_b", 120)
        text_center(d, W / 2, 380 + 40 * (1 - p2), "搞懂「防抖」", f, rgba(C["white"], p2))
        p3 = ease_out(prog(t, 0.8, 0.8))
        text_center(d, W / 2, 560 + 30 * (1 - p3), "Debounce", font("mono_b", 84), rgba(C["fn"], p3))
        p4 = ease_out(prog(t, 1.3, 0.8))
        w = 520 * p4
        d.rounded_rectangle((W / 2 - w / 2, 700, W / 2 + w / 2, 706), 3, fill=rgba(C["accent"], p4))
        text_center(d, W / 2, 735, "JavaScript  ·  9 行核心代码", font("cn", 34), rgba(C["text"], p4))


# ---------------------------------------------------------------- 输入框 + 请求列表（场景 2/4 共用）
def draw_input(d, x, y, w, s, caret_on, label=None):
    d.rounded_rectangle((x, y, x + w, y + 84), 16, fill=(16, 19, 33), outline=rgba(C["blue"], 0.9), width=3)
    d.text((x + 28, y + 16), "Q", font=font("mono_b", 40), fill=C["dim"])
    if s:
        d.text((x + 80, y + 14), s, font=font("mono", 44), fill=C["white"])
    else:
        d.text((x + 80, y + 18), "搜索...", font=font("cn", 36), fill=C["dim"])
    if caret_on:
        cx = x + 80 + d.textlength(s, font=font("mono", 44)) + 4
        d.rectangle((cx, y + 18, cx + 3, y + 66), fill=C["white"])
    if label:
        d.text((x, y - 50), label, font=font("cn", 28), fill=C["dim"])


def draw_requests(d, x, y, items, t, color, row_h=62):
    """items: [(appear_time, text)]"""
    for i, (t0, s) in enumerate(items):
        if t < t0:
            continue
        p = ease_out(prog(t, t0, 0.35))
        yy = y + i * row_h
        xx = x + 60 * (1 - p)
        d.rounded_rectangle((xx, yy, xx + 640, yy + row_h - 12), 10, fill=rgba(color, 0.12 * p),
                            outline=rgba(color, 0.7 * p), width=2)
        d.text((xx + 18, yy + 9), "GET", font=font("mono_b", 28), fill=rgba(color, p))
        d.text((xx + 90, yy + 9), f"/api/search?q={s}", font=font("mono", 28), fill=rgba(C["white"], p))


WORD = "debounce"


# ---------------------------------------------------------------- 2. 问题
class Problem(Scene):
    dur = 10.0
    key_t0, key_gap = 2.0, 0.42

    def keys(self):
        return [self.key_t0 + i * self.key_gap for i in range(len(WORD))]

    def captions(self):
        return [(0.3, 4.6, "场景：搜索框，用户每输入一个字就去请求接口"),
                (4.8, 9.8, "输入 8 个字母 = 发 8 次请求，前 7 次全是浪费")]

    def sounds(self):
        return [(0.0, "whoosh")] + [(k, "key") for k in self.keys()] + [(k + 0.05, "pop") for k in self.keys()]

    def draw(self, img, d, t):
        p = ease_out(prog(t, 0, 0.6))
        window(d, (160, 110 - 20 * (1 - p), 1760, 250 - 20 * (1 - p)), "search.js", p)
        chars = colorize("input.addEventListener('input', search);")
        draw_code(d, chars, len(chars), 220, 182 - 20 * (1 - p), font("mono", 36), 50, p)
        tag(d, 1530, 172 - 20 * (1 - p), "未优化", C["red"], p)

        keys = self.keys()
        n = sum(1 for k in keys if t >= k)
        caret = (t * 2) % 2 < 1.2
        draw_input(d, 160, 420, 760, WORD[:n], caret, "用户输入")
        d.text((1060, 320), "发出的网络请求", font=font("cn", 28), fill=C["dim"])
        draw_requests(d, 1060, 370, [(k, WORD[: i + 1]) for i, k in enumerate(keys)], t, C["red"])

        # 计数器
        f = font("cn_b", 96)
        col = C["red"] if n else C["dim"]
        bump = 1 + 0.12 * max(0, 1 - (t - keys[n - 1]) / 0.2) if n else 1
        fb = font("cn_b", int(96 * bump))
        d.text((160, 640), f"{n}", font=fb, fill=col)
        d.text((160 + d.textlength(str(n), font=fb) + 20, 676), "次请求", font=font("cn", 48), fill=C["text"])
        if t > 5.5:
            pp = ease_out(prog(t, 5.5, 0.5))
            d.text((160, 800), "服务器压力大 · 结果还会乱序闪烁", font=font("cn", 36), fill=rgba(C["accent"], pp))


# ---------------------------------------------------------------- 3. 写代码
SEGMENTS = [  # (起始行, 结束行(含), 讲解, 停顿秒数)
    (0, 0, "debounce 接收两个参数：原函数 fn，等待时间 delay", 1.6),
    (1, 1, "用闭包保存一个定时器 timer", 1.4),
    (2, 2, "返回一个新函数，用它代替原函数", 1.4),
    (3, 3, "关键 ①：每次触发，先取消上一次的计划", 2.2),
    (4, 6, "关键 ②：重新计时，安静 delay 毫秒后才真正执行", 2.6),
    (7, 8, "核心逻辑就这 9 行", 1.0),
    (9, 10, "用法：包一层，直接替换原来的监听函数", 2.4),
]
CPS = 24  # 打字速度：字符/秒


class CodeScene(Scene):
    lead = 0.8
    x0, y0, lh = 330, 210, 60

    def __init__(self):
        self.chars = colorize(CODE)
        lines = CODE.split("\n")
        offs, acc = [], 0
        for ln in lines:
            offs.append(acc)
            acc += len(ln) + 1
        self.plan = []  # (t_start, t_typed, t_end, c0, c1, seg)
        t = self.lead
        for seg in SEGMENTS:
            a, b, _, hold = seg
            c0 = offs[a]
            c1 = min(len(self.chars), offs[b] + len(lines[b]) + 1)
            td = (c1 - c0) / CPS
            self.plan.append((t, t + td, t + td + hold, c0, c1, seg))
            t += td + hold
        self.dur = t + 0.6

    def typed(self, t):
        for ts, tt, te, c0, c1, _ in self.plan:
            if t < ts:
                return c0
            if t < tt:
                return c0 + int((t - ts) * CPS)
            if t < te:
                return c1
        return len(self.chars)

    def captions(self):
        return [(ts, te, seg[2]) for ts, tt, te, c0, c1, seg in self.plan]

    def sounds(self):
        ev = [(0.0, "whoosh")]
        for ts, tt, te, c0, c1, _ in self.plan:
            for i in range(c0, c1):
                if self.chars[i][0] not in " \n":
                    ev.append((ts + (i - c0) / CPS, "key"))
        return ev

    def draw(self, img, d, t):
        p = ease_out(prog(t, 0, 0.6))
        window(d, (220, 100 + 30 * (1 - p), 1700, 900 + 30 * (1 - p)), "debounce.js", p)
        f = font("mono", 37)
        n = self.typed(t)
        cur = None
        for ts, tt, te, c0, c1, seg in self.plan:
            if ts <= t < te:
                cur = (ts, tt, te, seg)
        # 停顿时高亮当前段落
        if cur and t >= cur[1]:
            a, b = cur[3][0], cur[3][1]
            if CODE.split("\n")[a] == "":
                a += 1
            hp = ease_out(prog(t, cur[1], 0.3))
            y_a, y_b = self.y0 + a * self.lh - 8, self.y0 + (b + 1) * self.lh - 6
            hl = C["accent"] if "关键" in cur[3][2] else C["blue"]
            d.rounded_rectangle((300, y_a, 1670, y_b), 10, fill=rgba(hl, 0.10 * hp),
                                outline=rgba(hl, 0.8 * hp), width=2)
        for i in range(len(CODE.split("\n"))):
            d.text((260, self.y0 + i * self.lh), f"{i + 1:>2}", font=font("mono", 26),
                   fill=rgba(C["dim"], p * 0.8))
        line, col = draw_code(d, self.chars, n, self.x0, self.y0, f, self.lh, p)
        typing = cur is not None and t < cur[1]
        if typing or (t * 2) % 2 < 1.1:
            cw = f.getlength("M")
            cx = self.x0 + col * cw
            cy = self.y0 + line * self.lh
            d.rectangle((cx, cy + 4, cx + 3, cy + 46), fill=rgba(C["accent"], p))


# ---------------------------------------------------------------- 4. 可视化
KEYS = [0.2, 0.4, 0.6, 1.5, 1.7, 1.9, 2.9, 3.1]  # 模拟时间（秒）
DELAY = 0.3
SIM_END = 3.8


def fires():
    out = []
    for i, k in enumerate(KEYS):
        nxt = KEYS[i + 1] if i + 1 < len(KEYS) else 1e9
        if nxt - k >= DELAY:
            out.append((k + DELAY, i))
    return out


class Visualize(Scene):
    lead, speed = 1.2, 0.5  # 0.5 倍速慢放
    dur = 1.2 + SIM_END / 0.5 + 2.6

    def real(self, s):
        return self.lead + s / self.speed

    def captions(self):
        return [(0.2, self.real(1.5), "加上防抖后慢放：每次按键都会重置 300ms 计时器"),
                (self.real(1.5), self.real(SIM_END), "只有停顿超过 300ms，计时器走完，才发请求"),
                (self.real(SIM_END), self.dur - 0.1, "同样 8 次输入，请求从 8 次降到 3 次")]

    def sounds(self):
        ev = [(0.0, "whoosh")]
        ev += [(self.real(k), "key") for k in KEYS]
        ev += [(self.real(f), "ding") for f, _ in fires()]
        return ev

    def draw(self, img, d, t):
        p = ease_out(prog(t, 0, 0.6))
        s = clamp((t - self.lead) * self.speed, 0, SIM_END)
        n = sum(1 for k in KEYS if s >= k)
        tag(d, 160, 90, "已加防抖 · 300ms", C["green"], p)
        draw_input(d, 160, 220, 760, WORD[:n], (t * 2) % 2 < 1.2, "用户输入")
        d.text((1060, 160), "发出的网络请求", font=font("cn", 28), fill=C["dim"])
        reqs = [(self.real(f), WORD[: i + 1]) for f, i in fires()]
        draw_requests(d, 1060, 210, reqs, t, C["green"])

        # 时间轴
        X0, X1 = 400, 1740
        sx = lambda v: X0 + (X1 - X0) * v / SIM_END
        tracks = [("按键", 590), ("计时器", 700), ("search()", 810)]
        for name, y in tracks:
            d.text((160, y - 22), name, font=font("cn_b", 32) if name != "search()" else font("mono_b", 30),
                   fill=rgba(C["text"], p))
            d.line((X0, y, X1, y), fill=rgba(C["dim"], 0.6 * p), width=2)
        for v in range(0, 4):
            x = sx(v)
            d.line((x, 900, x, 912), fill=rgba(C["dim"], p), width=2)
            text_center(d, x, 918, f"{v}s", font("mono", 22), rgba(C["dim"], p))

        for i, k in enumerate(KEYS):
            if s < k:
                continue
            # 按键点
            pp = ease_out((s - k) / 0.08)
            x = sx(k)
            r = 12 * pp
            d.ellipse((x - r, 590 - r, x + r, 590 + r), fill=C["blue"])
            text_center(d, x, 545, WORD[i], font("mono_b", 26), C["white"])
            # 计时器条
            nxt = KEYS[i + 1] if i + 1 < len(KEYS) else 1e9
            end = min(k + DELAY, nxt, s)
            done = nxt - k >= DELAY and s >= k + DELAY
            cut = nxt < k + DELAY and s >= nxt
            col = C["green"] if done else ((110, 116, 135) if cut else C["accent"])
            d.rounded_rectangle((x, 686, max(x + 4, sx(end)), 714), 6, fill=col)
            if cut:
                d.line((sx(end), 676, sx(end), 724), fill=C["red"], width=4)
        for f_t, i in fires():
            if s >= f_t:
                pp = ease_out((s - f_t) / 0.15)
                x = sx(f_t)
                r = 16 * pp
                d.ellipse((x - r, 810 - r, x + r, 810 + r), fill=C["green"])
                d.line((x, 714, x, 794), fill=rgba(C["green"], 0.6), width=2)
                # 光环
                ring = (s - f_t) / 0.4
                if ring < 1:
                    rr = 16 + 30 * ring
                    d.ellipse((x - rr, 810 - rr, x + rr, 810 + rr), outline=rgba(C["green"], 1 - ring), width=3)
        # 播放头
        if t > self.lead - 0.2:
            x = sx(s)
            d.line((x, 520, x, 880), fill=rgba(C["white"], 0.5), width=2)
        # 结果对比
        if t > self.real(SIM_END):
            pp = ease_out(prog(t, self.real(SIM_END), 0.5))
            d.text((1060, 420), "8", font=font("cn_b", 64), fill=rgba(C["red"], pp))
            d.text((1110, 440), "次输入  →", font=font("cn", 36), fill=rgba(C["text"], pp))
            d.text((1310, 420), "3", font=font("cn_b", 64), fill=rgba(C["green"], pp))
            d.text((1360, 440), "次请求", font=font("cn", 36), fill=rgba(C["text"], pp))


# ---------------------------------------------------------------- 5. 总结
class Summary(Scene):
    dur = 8.0

    def captions(self):
        return [(0.3, 4.2, "记住一句话：连续触发，只执行最后一次"),
                (4.3, 7.9, "下期讲它的兄弟：节流 Throttle，关注不迷路")]

    def sounds(self):
        return [(0.0, "whoosh"), (0.5, "ding")] + [(1.6 + i * 0.35, "pop") for i in range(3)]

    def draw(self, img, d, t):
        p = ease_out(prog(t, 0.1, 0.7))
        text_center(d, W / 2, 150 + 30 * (1 - p), "防抖 = 等它停下来，再执行", font("cn_b", 80), rgba(C["white"], p))
        cards = [("搜索联想", "输入停顿后再请求"), ("窗口 resize", "拖完再重新布局"), ("表单校验", "输完再提示错误")]
        for i, (h, sub) in enumerate(cards):
            pp = ease_out(prog(t, 1.6 + i * 0.35, 0.6))
            x = 260 + i * 480
            y = 380 + 50 * (1 - pp)
            d.rounded_rectangle((x, y, x + 420, y + 260), 24, fill=rgba(C["panel"], pp),
                                outline=rgba(C["blue"], 0.6 * pp), width=2)
            text_center(d, x + 210, y + 60, h, font("cn_b", 48), rgba(C["fn"], pp))
            text_center(d, x + 210, y + 150, sub, font("cn", 32), rgba(C["text"], pp))
        pn = ease_out(prog(t, 4.3, 0.6))
        tag(d, W / 2 - 200, 760, "下期预告：节流 Throttle", C["accent"], pn, 34)


# ---------------------------------------------------------------- 时间线 & 字幕
SCENES = [Title(), Problem(), CodeScene(), Visualize(), Summary()]
STARTS = []
_acc = 0.0
for sc in SCENES:
    STARTS.append(_acc)
    _acc += sc.dur
TOTAL = _acc
FADE = 0.35

CAPTIONS = sorted((s + a, s + b, txt) for s, sc in zip(STARTS, SCENES) for a, b, txt in sc.captions())


def draw_caption(d, t):
    for t0, t1, txt in CAPTIONS:
        if t0 <= t < t1:
            a = min(prog(t, t0, 0.2), 1 - prog(t, t1 - 0.2, 0.2))
            f = font("cn_b", 44)
            w = d.textlength(txt, font=f)
            y = 975
            d.rounded_rectangle((W / 2 - w / 2 - 30, y - 12, W / 2 + w / 2 + 30, y + 66), 14,
                                fill=(0, 0, 0, int(150 * a)))
            text_center(d, W / 2, y, txt, f, rgba(C["white"], a))


def render_frame(t):
    img = BG.copy()
    d = ImageDraw.Draw(img, "RGBA")
    for s, sc in zip(STARTS, SCENES):
        if s <= t < s + sc.dur:
            sc.draw(img, d, t - s)
            local = t - s
            fade = min(prog(local, 0, FADE), 1 - prog(local, sc.dur - FADE, FADE))
            if fade < 1:
                img = Image.blend(BG, img, ease_in_out(fade))
                d = ImageDraw.Draw(img, "RGBA")
            break
    # 进度条
    d.rectangle((0, H - 6, W * t / TOTAL, H), fill=rgba(C["accent"], 0.9))
    draw_caption(d, t)
    return img


# ---------------------------------------------------------------- 音效合成
SR = 44100


def synth(kind, rng):
    if kind == "key":  # 机械键盘咔哒
        n = int(SR * 0.04)
        env = np.exp(-np.linspace(0, 1, n) * 60)
        noise = rng.standard_normal(n)
        noise = np.diff(noise, prepend=0)  # 高通一下更“脆”
        tone = np.sin(2 * np.pi * rng.uniform(1800, 2600) * np.arange(n) / SR)
        return (0.5 * noise + 0.5 * tone) * env * rng.uniform(0.12, 0.2)
    if kind == "pop":
        n = int(SR * 0.08)
        tt = np.arange(n) / SR
        f = 900 - 500 * tt / tt[-1]
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40) * 0.25
    if kind == "ding":
        n = int(SR * 0.6)
        tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * 1320 * tt) + 0.5 * np.sin(2 * np.pi * 1980 * tt)
        return s * np.exp(-tt * 7) * 0.22
    if kind == "whoosh":
        n = int(SR * 0.45)
        tt = np.linspace(0, 1, n)
        noise = rng.standard_normal(n)
        k = 200
        noise = np.convolve(noise, np.ones(k) / k, mode="same") * 8  # 低通
        return noise * np.sin(np.pi * tt) ** 2 * 0.18
    raise ValueError(kind)


def build_audio(path):
    rng = np.random.default_rng(7)
    total = int(SR * (TOTAL + 0.5))
    buf = np.zeros(total)
    # 背景 pad：Am - F - C - G，柔和低音量
    tt = np.arange(total) / SR
    chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [130.8, 196, 261.6], [196, 246.9, 293.7]]
    bar = 4.0
    pad = np.zeros(total)
    for ci in range(int(TOTAL / bar) + 1):
        s0, s1 = int(ci * bar * SR), min(total, int((ci + 1) * bar * SR))
        seg_t = tt[s0:s1] - ci * bar
        env = np.minimum(1, seg_t / 0.8) * np.minimum(1, (bar - seg_t) / 0.8)
        for fr in chords[ci % 4]:
            pad[s0:s1] += np.sin(2 * np.pi * fr * tt[s0:s1]) * env
    buf += pad * 0.025
    for s, sc in zip(STARTS, SCENES):
        for lt, kind in sc.sounds():
            snd = synth(kind, rng)
            i = int((s + lt) * SR)
            j = min(total, i + len(snd))
            buf[i:j] += snd[: j - i]
    fade = int(SR * 1.0)
    buf[-fade:] *= np.linspace(1, 0, fade)
    buf = np.clip(buf, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
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


# ---------------------------------------------------------------- 主流程
def main():
    OUT.mkdir(exist_ok=True)
    print(f"总时长 {TOTAL:.1f}s，场景：" + ", ".join(f"{type(s).__name__}={s.dur:.1f}s" for s in SCENES))
    if "--preview" in sys.argv:
        pdir = OUT / "preview"
        pdir.mkdir(exist_ok=True)
        times = [2.5] + [s + sc.dur * f for s, sc in zip(STARTS[1:], SCENES[1:]) for f in (0.55, 0.9)]
        for i, t in enumerate(times):
            render_frame(t).save(pdir / f"frame_{i:02}_{t:05.1f}s.png")
        print("preview ->", pdir)
        return

    wav, mp4 = OUT / "audio.wav", OUT / "debounce.mp4"
    build_audio(wav)
    write_srt(OUT / "debounce.srt")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(mp4)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(TOTAL * FPS)
    for i in range(nframes):
        proc.stdin.write(render_frame(i / FPS).tobytes())
        if i % (FPS * 5) == 0:
            print(f"  {i / FPS:5.1f}s / {TOTAL:.1f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("done ->", mp4)


if __name__ == "__main__":
    main()
