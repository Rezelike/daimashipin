"""Little people + simple furniture for the dark-tech engine (ported from money_happiness/src/engine/folk.mjs).

User, 2026-10-23: "我还是想加几个小人，因为有人看着更舒服一点吧，不是干巴巴的塞一堆知识给你".
Everything is drawn by code (no real person). Figure coordinates: origin = centre between the feet, up is -y;
scale 1 is about 104 px tall (head top at -102). Chibi proportions: a standing figure's hands reach a desk top,
so "seated" = draw the figure, then draw a desk in front of it (desk() hides everything below its top).

    from engine import figures as F
    me = F.make(7, top="#3F6FA6")                       # seed or numpy Generator; any field can be pinned
    F.chair(c, x, floor, s)                             # optional backrest, drawn first
    F.draw(c, me, x, floor, s=2.2, mood=0.6, arm_r=F.ARM_WRITE, prop=dict(kind="pen"), t=S.t)
    F.desk(c, x, floor, 300, s)                         # in front: the figure now sits at the desk
    F.draw(c, me, x, floor, s=2.2, walk=S.t * 9)        # walking: legs and arms swing with the phase
    F.sprite(c, me, x, y, s=0.9, alpha=0.5)             # cached bitmap of one fixed pose (crowds)

mood: -1 sad, 0 neutral, 0.6 smile, 1 laugh.  look / look_y: eye direction (-1..1).
Arm angles (radians, 0 = straight down, pi = straight up): ARM_DOWN, ARM_WRITE (hand on the desk), ARM_OUT, ARM_UP.
Props held in one hand (side +1 right / -1 left): pen, phone (lit 0..1), note (sticky note), paper.
Keep motion smooth (no per-beat jitter): the user rejected anything that looks like shaking.
"""
import math
from functools import lru_cache

import numpy as np
import skia

from . import core as K
from .core import clamp, paint

SKINS = ["#F6D9BC", "#F1CBA4", "#E4B286", "#CF9568", "#AC7149", "#7F5136"]
HAIRS = ["#2B2422", "#3F2C22", "#6B4A30", "#B98C55", "#A9A6A1"]
TOPS = ["#3F6FA6", "#E09A46", "#4A9A8E", "#B65D72", "#7B6BB5", "#C9A04B", "#5E8F57", "#D27A57", "#6B7E9E",
        "#E4DCCB"]
PANTS = ["#26324C", "#2F2B3F", "#3A4258", "#22303F", "#4A3F37"]
STYLES = ["short", "short", "long", "bun", "curly", "bald"]

ARM_DOWN, ARM_WRITE, ARM_OUT, ARM_UP = 0.32, 1.07, 1.45, 2.45
SH_X, SH_Y, ARM_LEN = 12.5, -52.0, 25.0
DESK_TOP = 40.0                 # desk / table top height above the floor, in figure units
INK = "#262833"
WOOD, WOOD_D = "#6B4F3A", "#4A3628"


def shade(h, k):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % (min(255, round(r * k)), min(255, round(g * k)), min(255, round(b * k)))


def luma(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def make(seed=0, **over):
    """random look; pin any field: skin, hair, hair_style, top, pants, shoe"""
    r = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)

    def pick(arr):
        return arr[int(r.integers(len(arr)))]
    style = over.pop("hair_style", None) or pick(STYLES)
    hair = pick(["#A9A6A1", "#D9D5CD", "#3F2C22"]) if style == "bald" else pick(HAIRS)
    f = dict(skin=pick(SKINS), hair=hair, hair_style=style, top=pick(TOPS), pants=pick(PANTS), shoe="#141924",
             blink_at=float(r.uniform(0, 4)), id=int(r.integers(1 << 30)))
    f.update(over)
    return f


def hand_pos(side, theta):
    return side * (SH_X + ARM_LEN * math.sin(theta)), SH_Y + ARM_LEN * math.cos(theta)


# ----------------------------------------------------------------------------- tiny helpers (figure units)
def _rr(c, x, y, w, h, r, color, a=1.0):
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, paint(color, a))


def _circle(c, x, y, r, color, a=1.0):
    c.drawCircle(x, y, r, paint(color, a))


def _oval(c, cx, cy, rx, ry, color, a=1.0):
    c.drawOval(skia.Rect.MakeXYWH(cx - rx, cy - ry, 2 * rx, 2 * ry), paint(color, a))


def _line(c, x0, y0, x1, y1, color, width, a=1.0):
    c.drawLine(x0, y0, x1, y1, paint(color, a, stroke=width))


# ----------------------------------------------------------------------------- hair
def _hair_back(c, f):
    if f["hair_style"] == "long":
        _rr(c, -22.5, -97, 45, 46, 15, f["hair"])
    if f["hair_style"] == "bun":
        _circle(c, 0, -102, 8.5, f["hair"])


def _hair_front(c, f):
    st, col = f["hair_style"], f["hair"]
    p = skia.Path()
    if st in ("short", "bun"):
        p.moveTo(-21, -76)
        p.cubicTo(-23, -96, -10, -102.5, 1, -102)
        p.cubicTo(14, -101.5, 23, -94, 21, -76)
        if st == "short":
            p.quadTo(19, -86, 12, -88)
            p.quadTo(2, -84, -6, -89)
            p.quadTo(-15, -87, -21, -76)
        else:
            p.quadTo(17, -90, 0, -91)
            p.quadTo(-17, -90, -21, -76)
        p.close()
        c.drawPath(p, paint(col))
    elif st == "long":
        p.moveTo(-22, -66)
        p.cubicTo(-25, -98, -8, -103.5, 2, -102.5)
        p.cubicTo(16, -101.5, 25, -92, 22, -66)
        p.quadTo(19, -84, 7, -90)
        p.quadTo(-8, -86, -15, -87)
        p.quadTo(-20, -80, -22, -66)
        p.close()
        c.drawPath(p, paint(col))
    elif st == "curly":
        p.addArc(skia.Rect.MakeXYWH(-20.5, -102, 41, 26), 180, 180)
        p.close()
        c.drawPath(p, paint(col))
        for i in range(8):
            ang = math.pi * (1 + i / 7)
            _circle(c, math.cos(ang) * 19, -87 + math.sin(ang) * 14, 6.4, col)
    elif st == "bald":
        _oval(c, -18.6, -84, 3.6, 7, col)
        _oval(c, 18.6, -84, 3.6, 7, col)


# ----------------------------------------------------------------------------- face
def _face(c, f, mood, look, look_y, blink):
    m = clamp(mood, -1, 1)
    happy, sad = max(0.0, m), max(0.0, -m)
    ex, ey = look * 2, look_y * 1.5
    dark = luma(f["skin"]) < 0.5
    if m > 0.74:                                  # closed, smiling eyes  ^ ^
        for sx in (-7, 7):
            p = skia.Path()
            p.addArc(skia.Rect.MakeXYWH(sx + ex - 3.1, -76.4 + ey - 3.1, 6.2, 6.2), 201.6, 136.8)
            c.drawPath(p, paint(INK, 1, stroke=1.9))
    else:
        ry = 0.45 if blink else 2.9
        _oval(c, -7 + ex, -78 + ey, 2.3, ry, INK)
        _oval(c, 7 + ex, -78 + ey, 2.3, ry, INK)
    bx, lift = ex * 0.5, happy * 0.9
    bp = paint(shade("#6E6A66" if f["hair_style"] == "bald" else f["hair"], 0.85), 1, stroke=1.7)
    c.drawLine(-11 + bx, -85.6 + sad * 0.9 - lift, -4 + bx, -86.6 - sad * 2 - lift, bp)
    c.drawLine(4 + bx, -86.6 - sad * 2 - lift, 11 + bx, -85.6 + sad * 0.9 - lift, bp)
    blush = 0.12 + 0.26 * happy
    _circle(c, -12.5, -71.5, 3.4, "#EB786E", blush)
    _circle(c, 12.5, -71.5, 3.4, "#EB786E", blush)
    my, w = -69.5, 4 + 1.8 * happy
    if m > 0.62:
        op = 3.2 + 3 * (m - 0.62) / 0.38
        p = skia.Path()
        p.moveTo(-w - 0.5, my - 1.2)
        p.quadTo(0, my, w + 0.5, my - 1.2)
        p.quadTo(0, my + op * 1.9, -w - 0.5, my - 1.2)
        p.close()
        c.drawPath(p, paint("#4A1E1C" if dark else "#7A2F2C"))
    else:
        p = skia.Path()
        p.moveTo(-w, my - 2 * m)
        p.quadTo(0, my + 5 * m, w, my - 2 * m)
        c.drawPath(p, paint("#4E2622" if dark else "#8A463B", 1, stroke=1.8))


# ----------------------------------------------------------------------------- props
def _prop(c, f, hand, side, pr):
    kind = pr.get("kind")
    hx, hy = hand
    if kind == "pen":
        _line(c, hx, hy + 1, hx + side * 4, hy - 13, "#E2E8F0", 2.6)
        _line(c, hx + side * 3.2, hy - 10, hx + side * 4, hy - 13, "#F59E0B", 2.6)
    elif kind == "phone":
        lit = pr.get("lit", 0.0)
        cx, cy = hx, hy - 8
        if lit > 0:
            c.drawRoundRect(skia.Rect.MakeXYWH(cx - 7, cy - 10.5, 14, 21), 4, 4, paint("#6EE7C8", 0.7 * lit, blur=5))
        c.drawRoundRect(skia.Rect.MakeXYWH(cx - 5, cy - 8.5, 10, 17), 2.6, 2.6, paint("#1A2133"))
        c.drawRoundRect(skia.Rect.MakeXYWH(cx - 3.6, cy - 6.8, 7.2, 13.2), 1.4, 1.4,
                        paint("#96F0D2" if lit > 0 else "#33405E", 0.35 + 0.65 * lit if lit > 0 else 1.0))
    elif kind == "note":
        with K.at(c, hx + side * 2, hy - 15, 1.0, -8 * side):
            c.drawRect(skia.Rect.MakeXYWH(-13, -13, 26, 26), paint("#000000", 0.25, blur=3))
            c.drawRect(skia.Rect.MakeXYWH(-13, -13, 26, 26), paint("#FDE68A"))
            for i, wl in enumerate(pr.get("lines", (18, 14, 16))):
                _line(c, -9, -5 + i * 6, -9 + wl, -5 + i * 6, "#B45309", 1.6)
    elif kind == "paper":
        with K.at(c, hx + side * 3, hy - 16, 1.0, 6 * side):
            c.drawRect(skia.Rect.MakeXYWH(-11, -14, 22, 28), paint("#F8FAFC"))
            for i in range(4):
                _line(c, -7, -8 + i * 6, 6 - (i == 3) * 5, -8 + i * 6, "#94A3B8", 1.4)
    if kind:
        _circle(c, hx, hy, 4.3, f["skin"])


# ----------------------------------------------------------------------------- figure
def draw(c, f, x=0.0, y=0.0, s=1.0, alpha=1.0, mood=0.3, look=0.0, look_y=0.0, arm_l=ARM_DOWN, arm_r=ARM_DOWN,
         t=None, blink=None, bob=0.0, prop=None, walk=None, lean=0.0, legs=True):
    """one figure; feet centre at (x, y). walk: phase in radians (legs + arms swing); lean: degrees"""
    if alpha <= 0.003 or s <= 0:
        return
    if blink is None:
        blink = t is not None and (t + f["blink_at"]) % 4.2 < 0.12
    skin_d, top_d = shade(f["skin"], 0.86), shade(f["top"], 0.8)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if alpha < 0.999:
        c.saveLayerAlpha(skia.Rect.MakeLTRB(-60, -120, 60, 10), int(255 * clamp(alpha)))
    _oval(c, 0, 0, 19, 3.6, "#000000", 0.32)
    swing = 0.38 * math.sin(walk) if walk is not None else 0.0
    if walk is not None:
        bob += -1.6 * abs(math.cos(walk))
    if legs:
        for side, ang in ((-1, swing), (1, -swing)):
            c.save()
            c.translate(side * 5.75, -25)
            c.rotate(math.degrees(ang))
            _rr(c, -4.25, 0, 8.5, 24, 4, f["pants"])
            _oval(c, side * 0.25, 22.6, 6.8, 3.2, f["shoe"])
            c.restore()
    c.translate(0, bob)
    if lean:
        c.rotate(lean)
    al = arm_l + (0.35 * math.sin(walk) if walk is not None else 0.0)
    ar = arm_r - (0.35 * math.sin(walk) if walk is not None else 0.0)
    hl, hr = hand_pos(-1, al), hand_pos(1, ar)
    pside = (prop or {}).get("side", 1) if prop else 0
    for side, hd in ((-1, hl), (1, hr)):
        _line(c, side * SH_X, SH_Y, hd[0], hd[1], top_d, 8)
    if pside != -1:
        _circle(c, hl[0], hl[1], 4.3, f["skin"])
    if pside != 1:
        _circle(c, hr[0], hr[1], 4.3, f["skin"])
    torso = skia.Rect.MakeXYWH(-16, -58, 32, 37)
    c.drawRoundRect(torso, 11, 11, paint(f["top"]))
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(torso, 11, 11), skia.ClipOp.kIntersect, True)
    c.drawRect(skia.Rect.MakeXYWH(7, -60, 12, 42), paint("#000000", 0.12))
    c.restore()
    neck = skia.Path()
    neck.addArc(skia.Rect.MakeXYWH(-5.5, -63.5, 11, 11), 0, 180)
    neck.close()
    c.drawPath(neck, paint(skin_d))
    _rr(c, -4.5, -64, 9, 8, 3, skin_d)
    _hair_back(c, f)
    if f["hair_style"] != "long":
        for sx in (-19.5, 19.5):
            _circle(c, sx, -78, 4, f["skin"])
            _circle(c, sx, -78, 2, skin_d)
    _circle(c, 0, -79, 20.5, f["skin"])
    _hair_front(c, f)
    _face(c, f, mood, look, look_y, blink)
    if prop:
        _prop(c, f, hl if pside == -1 else hr, pside, prop)
    if alpha < 0.999:
        c.restore()
    c.restore()


# ----------------------------------------------------------------------------- sprites (crowds)
_SPR = {}
_SPR_W, _SPR_H, _SPR_OX, _SPR_OY, _SPR_K = 90, 134, 45, 124, 3     # baked at 3x for crisp downscaling


def sprite(c, f, x, y, s=1.0, alpha=1.0, **pose):
    """cached bitmap of one fixed pose (mood, look, arm_l, arm_r, prop ...) - for crowds of 10-40 figures"""
    if alpha <= 0.003 or s <= 0:
        return
    key = (f["id"], f["skin"], f["top"], repr(sorted(pose.items())))
    img = _SPR.get(key)
    if img is None:
        surf = skia.Surface(_SPR_W * _SPR_K, _SPR_H * _SPR_K)
        cc = surf.getCanvas()
        cc.clear(skia.ColorTRANSPARENT)
        cc.scale(_SPR_K, _SPR_K)
        draw(cc, f, _SPR_OX, _SPR_OY, 1.0, blink=False, **pose)
        img = _SPR[key] = surf.makeImageSnapshot()
    p = skia.Paint(AntiAlias=True)
    p.setAlphaf(clamp(alpha))
    c.drawImageRect(img, skia.Rect.MakeXYWH(x - _SPR_OX * s, y - _SPR_OY * s, _SPR_W * s, _SPR_H * s),
                    skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)


def crowd(n, seed=1, **over):
    r = np.random.default_rng(seed)
    return [make(r, **over) for _ in range(n)]


# ----------------------------------------------------------------------------- furniture (screen coords)
def chair(c, x, floor, s, a=1.0, color="#334155"):
    """backrest behind a seated figure - draw it BEFORE the figure"""
    _rrs(c, x - 20 * s, floor - 66 * s, 40 * s, 30 * s, 8 * s, color, a)


def _rrs(c, x, y, w, h, r, color, a=1.0, stroke=None):
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, paint(color, a, stroke=stroke))


def desk(c, x, floor, w, s, a=1.0, top="#8B6A4F", front="#5B4433", edge="#A8876A"):
    """desk centred on x, top at DESK_TOP units above the floor; covers anything behind it below the top"""
    ty = floor - DESK_TOP * s
    _rrs(c, x - w / 2, ty, w, 6 * s, 3 * s, top, a)
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 6 * s, ty + 6 * s, w - 12 * s, floor - ty - 6 * s), paint(front, a))
    c.drawLine(x - w / 2, ty + 0.5, x + w / 2, ty + 0.5, paint(edge, 0.9 * a, stroke=1.5))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 6 * s, ty + 6 * s, w - 12 * s, 3 * s), paint("#000000", 0.25 * a))
    return ty


def floor_line(c, x0, x1, floor, a=1.0, color="#22D3EE"):
    c.drawLine(x0, floor, x1, floor, paint(color, 0.35 * a, stroke=2))
    c.drawRect(skia.Rect.MakeLTRB(x0, floor, x1, floor + 6), paint(color, 0.08 * a, blur=6))


def paper_on(c, x, ty, s, a=1.0, lines=4, written=1.0):
    """sheet lying on a desk top at ty (slight perspective)"""
    w, h = 34 * s, 8 * s
    p = skia.Path()
    p.moveTo(x - w / 2 + 3 * s, ty - h)
    p.lineTo(x + w / 2 + 3 * s, ty - h)
    p.lineTo(x + w / 2, ty)
    p.lineTo(x - w / 2, ty)
    p.close()
    c.drawPath(p, paint("#F1F5F9", a))
    n = int(lines * clamp(written) + 0.999)
    for i in range(n):
        yy = ty - h + (i + 1) * h / (lines + 1)
        frac = 1.0 if i < n - 1 else (lines * clamp(written)) - (n - 1)
        c.drawLine(x - w / 2 + 6 * s, yy, x - w / 2 + 6 * s + (w - 14 * s) * frac, yy, paint("#64748B", a, stroke=1.2 * s))


def book_on(c, x, ty, s, a=1.0, opened=0.0, color="#7C3AED"):
    """book on a desk: closed (cover) -> open (two pages) as opened goes 0 -> 1"""
    w, h = 30 * s, 6 * s
    k = clamp(opened)
    if k < 0.5:
        ww = w * (1 - 0.4 * k)
        _rrs(c, x - ww / 2, ty - h, ww, h, 2 * s, color, a)
        c.drawLine(x - ww / 2 + 2 * s, ty - h * 0.5, x + ww / 2 - 2 * s, ty - h * 0.5, paint("#C4B5FD", 0.7 * a, stroke=1.2 * s))
    else:
        u = (k - 0.5) / 0.5
        for side in (-1, 1):
            p = skia.Path()
            p.moveTo(x, ty - h * 0.6)
            p.quadTo(x + side * w * 0.3 * u, ty - h * (0.6 + 0.6 * u), x + side * w * 0.55 * u, ty - h * 0.9)
            p.lineTo(x + side * w * 0.55 * u, ty)
            p.lineTo(x, ty)
            p.close()
            c.drawPath(p, paint("#F8FAFC", a))
            c.drawPath(p, paint("#CBD5E1", a, stroke=1.0 * s))
        c.drawLine(x, ty - h * 0.6, x, ty, paint("#94A3B8", a, stroke=1.2 * s))


def phone_on(c, x, ty, s, a=1.0, lit=0.0, buzz=0.0):
    """phone lying on a desk; buzz 0..1 draws vibration rings (keep it smooth, the whole frame never moves)"""
    w, h = 16 * s, 4 * s
    if lit > 0:
        c.drawRoundRect(skia.Rect.MakeXYWH(x - w / 2 - 3 * s, ty - h - 3 * s, w + 6 * s, h + 3 * s), 3 * s, 3 * s,
                        paint("#6EE7C8", 0.55 * lit * a, blur=8))
    _rrs(c, x - w / 2, ty - h, w, h, 1.5 * s, "#1A2133", a)
    _rrs(c, x - w / 2 + 1.5 * s, ty - h + 1 * s, w - 3 * s, h - 1.8 * s, 1 * s, "#96F0D2" if lit > 0 else "#33405E",
         a * (0.4 + 0.6 * lit) if lit > 0 else a)
    if buzz > 0:
        for i in range(2):
            rr_ = (10 + 7 * i + 6 * buzz) * s
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(x - rr_, ty - h / 2 - rr_, 2 * rr_, 2 * rr_), 200, 50)
            c.drawPath(arc, paint("#6EE7C8", a * (1 - buzz) * (0.9 - 0.3 * i), stroke=1.6 * s))
            arc = skia.Path()
            arc.addArc(skia.Rect.MakeXYWH(x - rr_, ty - h / 2 - rr_, 2 * rr_, 2 * rr_), 290, 50)
            c.drawPath(arc, paint("#6EE7C8", a * (1 - buzz) * (0.9 - 0.3 * i), stroke=1.6 * s))


def bowl_on(c, x, ty, s, a=1.0):
    p = skia.Path()
    p.moveTo(x - 12 * s, ty - 9 * s)
    p.quadTo(x - 11 * s, ty, x, ty)
    p.quadTo(x + 11 * s, ty, x + 12 * s, ty - 9 * s)
    p.close()
    c.drawPath(p, paint("#E2E8F0", a))
    _oval_s(c, x, ty - 9 * s, 12 * s, 2.4 * s, "#F8FAFC", a)
    c.drawLine(x + 4 * s, ty - 16 * s, x + 14 * s, ty - 7 * s, paint("#B45309", a, stroke=1.4 * s))
    c.drawLine(x + 7 * s, ty - 17 * s, x + 16 * s, ty - 8 * s, paint("#B45309", a, stroke=1.4 * s))


def _oval_s(c, cx, cy, rx, ry, color, a=1.0):
    c.drawOval(skia.Rect.MakeXYWH(cx - rx, cy - ry, 2 * rx, 2 * ry), paint(color, a))


def wall_clock(c, x, y, r, minutes, a=1.0, color="#22D3EE"):
    """analog clock; minutes since 00:00 (e.g. 19*60+50)"""
    c.drawCircle(x, y, r, paint("#0F1A33", 0.95 * a))
    c.drawCircle(x, y, r, paint(color, 0.9 * a, stroke=3))
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        r0 = r * (0.78 if i % 3 == 0 else 0.86)
        c.drawLine(x + r0 * math.cos(ang), y + r0 * math.sin(ang), x + r * 0.92 * math.cos(ang),
                   y + r * 0.92 * math.sin(ang), paint("#CBD5E1", 0.8 * a, stroke=2.5 if i % 3 == 0 else 1.5))
    hh = math.radians((minutes / 60.0 % 12) * 30 - 90)
    mm = math.radians((minutes % 60) * 6 - 90)
    c.drawLine(x, y, x + r * 0.5 * math.cos(hh), y + r * 0.5 * math.sin(hh), paint("#F1F5F9", a, stroke=5))
    c.drawLine(x, y, x + r * 0.75 * math.cos(mm), y + r * 0.75 * math.sin(mm), paint("#F1F5F9", a, stroke=3))
    c.drawCircle(x, y, 5, paint(color, a))


def door(c, x, floor, s, opened=0.0, a=1.0, color="#94A3B8"):
    """door centred on x standing on the floor; opened 0 -> 1 swings the panel open (dark gap)"""
    w, h = 46 * s, 112 * s
    k = clamp(opened)
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2, floor - h, w, h), paint("#020617", a))
    if k > 0:
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2, floor - h, w, h), paint("#1E293B", 0.6 * a * k))
    pw = w * (1 - 0.82 * k)
    _rrs(c, x + w / 2 - pw, floor - h, pw, h, 3 * s, "#475569", a)
    _rrs(c, x + w / 2 - pw, floor - h, pw, h, 3 * s, color, 0.9 * a, stroke=2)
    if pw > 14 * s:
        c.drawCircle(x + w / 2 - pw + 7 * s, floor - h * 0.48, 2.6 * s, paint("#FBBF24", a))
    frame = skia.Rect.MakeXYWH(x - w / 2 - 4 * s, floor - h - 4 * s, w + 8 * s, h + 4 * s)
    c.drawRect(frame, paint(color, a, stroke=2.5))
