"""Every picture of the ISU-152 diesel video, drawn as 360x640 pixel art (shown 3x = 1080x1920).

One scene per bar (mech.ROLES). Inside a bar, time is counted in beats (lb), and every caption, cut and label
starts on a whole beat. All motion in the tank shots repeats exactly k times per 26.25 s, so the last frame runs
straight into frame 0 when the video loops.
"""
import math
import numpy as np
from PIL import Image
import mech as M
import pix as X
from pix import Canvas, INK, WHITE, GREY, YELLOW, ORANGE, RED, CYAN

W, H = X.W, X.H
T = M.DUR
BORE = (26, 20, 40)
PANEL = (14, 11, 26)


def hsh(k, j=0):
    v = math.sin(k * 12.9898 + j * 78.233 + 0.123) * 43758.5453
    return v - math.floor(v)


def per(k, p):
    """speed (px/s) at which exactly k periods of length p pass in one loop"""
    return k * p / T


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


# =================================================================================================== captions / HUD
def box(c, x0, y0, x1, y1, edge=WHITE, fill=PANEL):
    c.rect(x0 - 1, y0 - 1, x1 + 1, y1 + 1, outline=INK)
    c.rect(x0, y0, x1, y1, fill=fill, outline=edge)


def title_box(c, cn_lines, en=None, y=56, cn_color=WHITE, en_color=YELLOW, sub=None, sub_color=YELLOW):
    """centred caption: Chinese lines at 2x, English (and an optional 1x Chinese sub line) at 1x"""
    rows = [(s, 2, cn_color) for s in cn_lines]
    if sub:
        rows.append((sub, 1, sub_color))
    if en:
        rows.append((en, 1, en_color))
    wmax = max(X.text_w(s, k) for s, k, _ in rows)
    hh = sum(16 * k for _, k, _ in rows)
    x0, x1 = 180 - wmax // 2 - 7, 180 + (wmax + 1) // 2 + 7
    box(c, x0, y, x1, y + hh + 8)
    yy = y + 4
    for s, k, col in rows:
        c.text(s, 180, yy, col, k, "c")
        yy += 16 * k
    return y + hh + 8


def label(c, cn, en, bx, by, anchor=None, color=YELLOW, align="l"):
    w = max(X.text_w(cn), X.text_w(en)) if en else X.text_w(cn)
    hh = 32 if en else 16
    x0 = bx if align == "l" else bx - w - 8
    x1, y1 = x0 + w + 8, by + hh + 4
    if anchor is not None:
        ax, ay = anchor
        sx = x0 if ax < x0 else (x1 if ax > x1 else ax)
        sy = by if ay < by else (y1 if ay > y1 else ay)
        c.line([(sx, sy), (ax, ay)], INK, 3)
        c.line([(sx, sy), (ax, ay)], color, 1)
        c.rect(ax - 1, ay - 1, ax + 1, ay + 1, fill=color, outline=INK)
    box(c, x0, by, x1, y1, edge=color)
    c.text(cn, x0 + 4, by + 2, color, 1)
    if en:
        c.text(en, x0 + 4, by + 17, WHITE, 1)
    return x0, by, x1, y1


def fmt_rpm(r):
    return f"{r:.1f}" if r < 99.95 else f"{r:,.0f}"


def fmt_kmh(v):
    return f"{v:.2f}" if v < 9.995 else (f"{v:.1f}" if v < 20 else f"{v:.0f}")


def fmt_factor(f):
    return "1/" + (f"{f:.0f}" if f >= 2.5 else f"{f:.1f}")


def hud(c, t, x2=False):
    rpm, kmh, fac = M.hud_numbers(t)
    real = fac < 1.02
    if real:
        tag, col = "实速 REAL SPEED", WHITE
    else:
        tag, col = "慢放 SLOW-MO " + fmt_factor(fac), YELLOW
    w = X.text_w(tag)
    box(c, 7, 7, 7 + w + 8, 24, edge=col)
    c.text(tag, 11, 8, col)
    if x2:
        c.text("×2", 7 + w + 14, 4, YELLOW, 2)
    s = fmt_rpm(rpm) + " RPM"
    k = fmt_kmh(kmh) + " km/h"
    w2 = max(X.text_w(s), X.text_w(k), 64)
    box(c, 352 - w2 - 8, 7, 352, 45, edge=WHITE)
    c.text(s, 348, 8, WHITE, 1, "r")
    frac = clamp(rpm / M.RPM_REAL)
    bx0, bx1 = 352 - w2 - 4, 348
    c.rect(bx0, 24, bx1, 27, fill=(36, 30, 56))
    fillx = bx0 + (bx1 - bx0) * frac
    if fillx > bx0 + 0.5:
        c.rect(bx0, 24, fillx, 27, fill=X.mix(X.GREEN, X.RED, frac ** 2))
    c.text(k, 348, 28, GREY, 1, "r")


# =================================================================================================== tank shots
HORIZON, GROUND, TX = 392, 432, 22
V_FAR, V_MID, V_ROAD, V_FG = per(2, 360), per(14, 240), per(48, 180), per(60, 180)
_CACHE = {}


def _sky():
    if "sky" in _CACHE:
        return _CACHE["sky"]
    a = np.zeros((H, W, 3), np.uint8)
    n = len(X.SKY)
    ys = [int(round(HORIZON * (k / n) ** 0.55)) for k in range(n + 1)]
    for k in range(n):
        a[ys[k]:ys[k + 1]] = X.SKY[k]
    for k in range(1, n):
        y = ys[k]
        lo = np.array(X.SKY[k], np.uint8)
        for x in range(W):
            if (x + y) % 2 == 0:
                a[y - 1, x] = lo
            if (x + 2 * (y % 2)) % 4 == 0:
                a[y - 2, x] = lo
    # sun halo (dithered) and the striped sun
    cxs, r = 180, 74
    for y in range(HORIZON - r - 14, HORIZON):
        for x in range(cxs - r - 14, cxs + r + 15):
            d = math.hypot(x - cxs, y - HORIZON)
            if r < d < r + 14 and (x + y) % 2 == 0:
                a[y, x] = X.mix(tuple(int(v) for v in a[y, x]), (255, 170, 120), 0.35 * (1 - (d - r) / 14))
    for y in range(HORIZON - r, HORIZON + 1):
        dy = HORIZON - y
        if dy < 44 and (dy % 7) < 1 + (44 - dy) // 13:
            continue
        hw = math.sqrt(max(0.0, r * r - dy * dy))
        a[y, int(cxs - hw):int(cxs + hw) + 1] = X.mix((255, 238, 150), (255, 92, 128), 1 - dy / r)
    for i in range(70):                                   # stars
        x, y = int(hsh(i, 1) * W), int(4 + hsh(i, 2) ** 1.4 * 230)
        col = X.mix((150, 130, 200), (255, 250, 255), hsh(i, 3))
        a[y, x] = col
        if hsh(i, 4) > 0.86 and 1 <= x < W - 1 and 1 <= y:
            a[y - 1, x] = a[y + 1, x] = a[y, x - 1] = a[y, x + 1] = X.mix(col, X.SKY[0], 0.5)
    # ground bands
    a[HORIZON:404] = (92, 44, 96)
    a[404:420] = (66, 34, 82)
    a[420:448] = (78, 50, 94)
    a[420] = a[447] = (52, 30, 70)
    for y in range(448, H):
        a[y] = X.mix((40, 24, 62), (14, 10, 28), (y - 448) / (H - 448))
    a[HORIZON, 110:250] = (255, 170, 120)
    _CACHE["sky"] = a
    return a


def _far_tile():
    if "far" in _CACHE:
        return _CACHE["far"]
    im = Canvas(None, (360, 34), mode="RGBA")
    for x in range(360):
        h = 13 + 5 * math.sin(2 * math.pi * 2 * x / 360 + 1.3) + 3 * math.sin(2 * math.pi * 5 * x / 360 + 0.4) \
            + 1.5 * math.sin(2 * math.pi * 13 * x / 360)
        top = int(round(33 - h))
        im.rect(x, top, x, 33, fill=(84, 38, 96, 255))
        im.px(x, top, (150, 70, 124, 255))
    _CACHE["far"] = im.img
    return im.img


def _pine(c, x, base, h, col, rim):
    tiers = 3
    for k in range(tiers):
        yb = base - k * h / (tiers + 0.6)
        yt = yb - h / 1.7
        hw = (h / 3.2) * (1 - k / (tiers + 1))
        c.poly([(x - hw, yb), (x + hw, yb), (x, yt)], col)
        c.line([(x, yt), (x + hw, yb)], rim)
    c.rect(x - 1, base, x, base + 3, fill=col)


def _mid_tile():
    if "mid" in _CACHE:
        return _CACHE["mid"]
    P, Hh = 240, 84
    c = Canvas(None, (P, Hh), mode="RGBA")
    col, rim = (44, 22, 60, 255), (116, 48, 108, 255)
    base = Hh - 6
    for shift in (-P, 0, P):
        for x, h in ((14, 44), (28, 60), (40, 36), (104, 52), (120, 66), (134, 40), (176, 30), (204, 56), (222, 42)):
            _pine(c, x + shift, base, h, col, rim)
        for px in (70, 190):
            x = px + shift
            c.rect(x, base - 60, x + 1, base + 2, fill=col)
            c.rect(x - 6, base - 56, x + 7, base - 55, fill=col)
        for x0 in (70, 190):
            for side in (-6, 7):
                pts = []
                for i in range(25):
                    u = i / 24
                    pts.append((x0 + shift + side + u * 120, base - 55 + 10 * 4 * u * (1 - u)))
                c.line(pts, (36, 18, 50, 255))
    c.rect(0, base, P - 1, Hh - 1, fill=(60, 30, 76, 255))
    for i in range(30):
        x = int(hsh(i, 7) * P)
        c.rect(x, base - 2, x + 3, base, fill=(52, 26, 68, 255))
    _CACHE["mid"] = c.img
    return c.img


def _tank_sprite():
    """the static body: 330 x 112, ground line at row 104, rear of the track at column 4"""
    if "tank" in _CACHE:
        return _CACHE["tank"]
    c = Canvas(None, (330, 112), mode="RGBA")
    G, O = 104, 4
    TK = X.TANK

    def p(x, y):
        return (O + x, G - y)

    def poly(pts, fill, outline=INK):
        c.poly([p(*q) for q in pts], fill, outline)

    poly([(8, 6), (226, 6), (234, 30), (6, 30)], TK["d"])                       # lower hull behind the track
    poly([(2, 31), (232, 31), (234, 35), (2, 35)], TK["l"])                      # fender
    poly([(4, 35), (4, 45), (12, 52), (110, 52), (110, 35)], TK["m"])            # engine deck (side)
    c.line([p(12, 52), p(110, 52)], TK["h"])
    c.line([p(4, 45), p(12, 52)], TK["h"])
    for x in range(18, 106, 6):                                                  # louvres
        c.line([p(x, 39), p(x + 2, 48)], TK["d"])
    for x0 in (14, 54):                                                          # external fuel tanks
        poly([(x0, 35), (x0 + 34, 35), (x0 + 34, 46), (x0, 46)], TK["l"])
        c.line([p(x0 + 1, 45), p(x0 + 33, 45)], TK["h"])
        for xs in (x0 + 8, x0 + 26):
            c.line([p(xs, 35), p(xs, 46)], TK["d"])
    poly([(108, 35), (108, 83), (196, 83), (226, 43), (234, 35)], TK["m"])      # casemate side
    poly([(110, 76), (110, 82), (195, 82), (200, 76)], TK["l"], None)
    c.line([p(108, 83), p(196, 83)], TK["h"])
    c.line([p(196, 83), p(226, 43)], TK["h"])
    poly([(118, 40), (186, 40), (186, 70), (118, 70)], TK["m"], None)
    c.line([p(118, 70), p(186, 70)], TK["d"])
    c.line([p(150, 40), p(150, 70)], TK["d"])
    poly([(200, 31), (220, 31), (220, 37), (200, 37)], TK["d"])                  # tool box
    poly([(128, 83), (128, 88), (146, 88), (146, 83)], TK["m"])                  # commander's cupola
    c.rect(*p(131, 90), *p(134, 88), fill=TK["d"], outline=INK)
    c.rect(*p(141, 90), *p(144, 88), fill=TK["d"], outline=INK)
    poly([(162, 83), (162, 86), (176, 86), (176, 83)], TK["l"])                  # hatch
    c.rect(*p(182, 87), *p(188, 83), fill=TK["d"], outline=INK)                 # vent dome
    # the commander, out of the hatch to his chest
    c.rect(*p(133, 95), *p(141, 88), fill=(54, 60, 46), outline=INK)            # padded jacket
    c.rect(*p(134, 102), *p(140, 96), fill=(226, 176, 136), outline=INK)        # face
    c.rect(*p(133, 103), *p(141, 99), fill=(48, 36, 30), outline=INK)           # tanker's helmet
    c.line([p(134, 101), p(134, 97)], (48, 36, 30))
    c.line([p(136, 101), p(139, 101)], (190, 196, 210))                          # goggles on the helmet
    c.line([p(141, 92), p(147, 90)], (54, 60, 46), 2)                            # arm on the rim
    # the gun: mantlet, barrel, muzzle brake
    c.ellipse(*p(214, 58), 12, 12, fill=TK["m"], outline=INK)
    c.ellipse(*p(213, 60), 6, 4, fill=TK["l"])
    poly([(224, 55), (304, 56), (304, 61), (224, 62)], TK["m"])
    c.line([p(224, 61), p(304, 60)], TK["h"])
    poly([(302, 54), (316, 54), (316, 63), (302, 63)], TK["d"])
    for xs in (306, 310, 313):
        c.line([p(xs, 55), p(xs, 62)], INK)
    c.rect(*p(225, 49), *p(228, 46), fill=(255, 226, 150), outline=INK)         # headlight
    c.rect(*p(-2, 46), *p(4, 43), fill=(46, 42, 50), outline=INK)               # exhaust pipes
    c.rect(*p(-2, 40), *p(4, 37), fill=(46, 42, 50), outline=INK)
    _CACHE["tank"] = c.img
    return c.img


def _track(c, t, ox, gy):
    """track, wheels and moving track links (smeared over 3 sub-positions so they do not strobe)"""
    def p(x, y):
        return (ox + x, gy - y)
    col = (46, 42, 50)
    c.circle(*p(14, 15), 16, fill=col, outline=INK)
    c.circle(*p(214, 14), 14, fill=col, outline=INK)
    c.poly([p(14, 31), p(214, 28), p(214, 0), p(14, 0)], col)
    c.line([p(14, 31), p(214, 28)], INK)
    c.line([p(20, 0), p(208, 0)], INK)
    s = V_ROAD * t
    for k_off in (0.0, -3.7, -7.3):
        for k in range(34):
            x = 16 + ((k * 6 + s + k_off) % 198)
            c.rect(*p(x, 30), *p(x + 1, 29), fill=(120, 112, 130, 90))
        for k in range(30):
            x = 24 + ((k * 6 - s - k_off) % 180)
            c.rect(*p(x, 2), *p(x + 1, 1), fill=(120, 112, 130, 90))
    TK = X.TANK
    c.circle(*p(14, 15), 12, fill=TK["d"], outline=INK)
    c.circle(*p(14, 15), 9, outline=(70, 80, 50))
    c.circle(*p(14, 15), 4, fill=TK["l"], outline=INK)
    c.circle(*p(214, 14), 10, fill=TK["m"], outline=INK)
    c.circle(*p(214, 14), 4, fill=TK["l"], outline=INK)
    for k in range(6):
        x = 36 + 30 * k
        c.circle(*p(x, 10), 10, fill=(30, 28, 34), outline=INK)
        c.circle(*p(x, 10), 8, fill=TK["m"])
        c.circle(*p(x, 10), 6, outline=TK["d"])
        c.circle(*p(x, 10), 3, fill=TK["l"], outline=INK)


def _smoke(c, t, ox, gy):
    dt, life = M.BEAT / 4, 0.9
    K = int(round(T / dt))
    k1 = math.floor(t / dt)
    for k in range(k1 - int(life / dt) - 1, k1 + 1):
        a = t - k * dt
        if a < 0 or a > life:
            continue
        kk = k % K
        u = a / life
        x = ox - 2 - V_ROAD * a * 0.9 - 10 * a * hsh(kk, 1)
        y = gy - 44 + 2 * hsh(kk, 2) - 14 * a - 18 * a * a * hsh(kk, 3)
        r = 2 + 7 * u
        al = int(170 * (1 - u) ** 1.2)
        if x + 3 * r < 0:
            continue
        c.ellipse(x, y, r * 2.2, r, fill=X.mix((60, 52, 78), (150, 120, 160), u) + (al,))


def tank_scene(t):
    a = _sky().copy()
    img = Image.fromarray(a)
    c = Canvas(img=img)
    far, mid = _far_tile(), _mid_tile()
    off = -int(round(V_FAR * t)) % 360
    for x in (off - 360, off):
        img.paste(far, (x, HORIZON - 31), far)
    off = -int(round(V_MID * t)) % 240
    for x in (off - 240, off, off + 240):
        img.paste(mid, (x, 408 - 84 + 6), mid)
    s = V_ROAD * t
    for k in range(12):                                     # road: ruts and pebbles
        for m in range(-1, 3):
            x = (k * 15 + int(hsh(k) * 9) - s) % 180 + m * 180
            if -4 < x < W + 4:
                c.rect(x, 423 + int(hsh(k, 1) * 22), x + 1, 423 + int(hsh(k, 1) * 22), fill=(116, 84, 124))
    for k in range(6):
        for m in range(-1, 3):
            x = (k * 30 - s) % 180 + m * 180
            c.rect(x, 428, x + 11, 428, fill=(60, 36, 76))
            c.rect(x + 9, 441, x + 22, 441, fill=(60, 36, 76))
    sf = V_FG * t
    for k in range(9):                                      # foreground tufts and stones
        for m in range(-1, 3):
            x = (k * 20 + int(hsh(k, 5) * 12) - sf) % 180 + m * 180
            if -6 < x < W + 6:
                y = 452 + int(hsh(k, 6) * 6)
                c.line([(x, y), (x + 2, y - 5), (x + 3, y), (x + 5, y - 4), (x + 6, y)], (64, 36, 86))
            x2 = (k * 20 + int(hsh(k, 8) * 15) - sf * 1.3) % 180 + m * 180
            if -6 < x2 < W + 6 and k % 3 == 0:
                c.rect(x2, 492 + int(hsh(k, 9) * 30), x2 + 4, 493 + int(hsh(k, 9) * 30), fill=(28, 18, 44))
    _smoke(c, t, TX, GROUND)
    _track(c, t, TX, GROUND)
    body = _tank_sprite()
    img.paste(body, (TX - 4, GROUND - 104), body)
    return c


def zoomed(c, z, cx, cy):
    if z <= 1.001:
        return c
    w, h = W / z, H / z
    x0 = clamp(cx - w / 2, 0, W - w)
    y0 = clamp(cy - h / 2, 0, H - h)
    im = c.img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.NEAREST)
    return Canvas(img=im)


ZOOM_AT = (TX + 64, GROUND - 42)


def hook_text(c, leader=False):
    yb = title_box(c, ["ISU-152 的柴油机", "是怎么工作的？"], "HOW DOES THE ISU-152'S DIESEL WORK?",
                   en_color=WHITE)
    y = yb + 8
    s1, s2 = "12 缸 · 每秒 200 次做功", "12 CYLINDERS · 200 BANGS A SECOND"
    w = max(X.text_w(s1), X.text_w(s2))
    box(c, 180 - w // 2 - 6, y, 180 + w // 2 + 6, y + 36, edge=YELLOW, fill=(40, 20, 30))
    c.text(s1, 180, y + 2, YELLOW, 1, "c")
    c.text(s2, 180, y + 18, WHITE, 1, "c")
    if leader:
        label(c, "V-2-IS 柴油机", "V-12 DIESEL · 38.9 L", 14, 250, anchor=(TX + 66, GROUND - 46))


# =================================================================================================== engine backdrop
def engine_bg():
    if "ebg" not in _CACHE:
        a = np.zeros((H, W, 3), np.uint8)
        for y in range(H):
            a[y] = X.mix((20, 15, 42), (44, 28, 74), y / 470) if y < 470 else X.mix((22, 14, 40), (10, 8, 22),
                                                                                    (y - 470) / 170)
        c = Canvas(img=Image.fromarray(a))
        k = 0
        while True:
            y = 470 + int(3 * k ** 1.55)
            if y >= H:
                break
            c.line([(0, y), (W, y)], (56, 32, 92))
            k += 1
        for xb in range(-400, 761, 40):
            x_top = 180 + (xb - 180) * (470 - 430) / (H - 430)
            c.line([(x_top, 470), (xb, H)], (56, 32, 92))
        c.line([(0, 470), (W, 470)], (120, 60, 140))
        for i in range(40):
            x, y = int(hsh(i, 11) * W), int(10 + hsh(i, 12) * 150)
            c.px(x, y, X.mix((80, 70, 130), (200, 190, 240), hsh(i, 13)))
        _CACHE["ebg"] = c.img
    return Canvas(img=_CACHE["ebg"].copy())


# =================================================================================================== overview (3/4 view)
_AL, _PH = math.radians(20.0), math.radians(30.0)
_R = (math.cos(_AL), math.sin(_AL), 0.0)
_U = (-math.sin(_AL) * math.sin(_PH), math.cos(_AL) * math.sin(_PH), math.cos(_PH))
_D = (math.sin(_AL) * math.cos(_PH), -math.cos(_AL) * math.cos(_PH), math.sin(_PH))
OSC, OCX, OCY = 0.205, 170.0, 367.0
PITCH, XB0, XB1 = 175.0, -540.0, 540.0


def P3(x, y, z):
    return (OCX + OSC * (x * _R[0] + y * _R[1] + z * _R[2]), OCY - OSC * (x * _U[0] + y * _U[1] + z * _U[2]))


def depth(x, y, z):
    return x * _D[0] + y * _D[1] + z * _D[2]


def cx_of(n):
    return (3.5 - n) * PITCH            # cylinder 1 at the front (screen right)


def bpt(b, x, w, l=0.0):
    a, nn = M.AX[b], M.INWARD[b]
    return P3(x, w * a[0] + l * nn[0], w * a[1] + l * nn[1])


def bquad(b, x0, x1, w0, w1, l=0.0):
    return [bpt(b, x0, w0, l), bpt(b, x1, w0, l), bpt(b, x1, w1, l), bpt(b, x0, w1, l)]


def _lerp(p, q, u):
    return (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)


def _in_quad(q, u, v):
    """point at (u, v) in 0..1 inside quad q (corners 0-1 along x, 0-3 along w)"""
    a = _lerp(q[0], q[1], u)
    b = _lerp(q[3], q[2], u)
    return _lerp(a, b, v)


def gas_color(ps, hot=False):
    st = M.stroke_of(ps)
    if st == "intake":
        return (46, 84, 170)
    if st == "compression":
        return X.mix((46, 84, 170), (170, 70, 50), ((ps - 540) / 180) ** 1.4)
    if st == "power":
        if ps < 24:
            return X.FIRE[0]
        if ps < 100:
            return X.mix(X.FIRE[1] if hot else X.FIRE[2], X.FIRE[3], (ps - 24) / 76)
        return X.mix(X.FIRE[3], (70, 40, 56), (ps - 100) / 80)
    return X.mix((104, 92, 120), (40, 32, 56), (ps - 180) / 180)


def _gas_overview(c, q, ps, seed, fi, hot):
    c.poly(q, gas_color(ps, hot))
    st = M.stroke_of(ps)
    if st == "intake" or st == "compression":
        p = ((ps - 360) % 360) / 360
        col = X.mix(X.AIR[1], X.HOT[1], max(0.0, (ps - 540) / 180) if st == "compression" else 0.0)
        for i in range(7):
            if st == "intake" and i > 7 * p * 2:
                continue
            c.px(*_in_quad(q, 0.15 + 0.7 * hsh(seed * 7 + i, 1), 0.1 + 0.8 * hsh(seed * 7 + i, 2)), col)
    elif st == "power" and ps < 110:
        for i in range(10):
            u, v = hsh(seed * 31 + i, fi), hsh(seed * 17 + i, fi + 3)
            c.px(*_in_quad(q, 0.1 + 0.8 * u, 0.1 + 0.85 * v), X.FIRE[i % 3])
    elif st == "exhaust":
        for i in range(5):
            c.px(*_in_quad(q, 0.2 + 0.6 * hsh(seed * 5 + i, 4), clamp(0.2 + 0.7 * hsh(seed * 5 + i, 5) +
                                                                       (ps - 180) / 400)), X.SMOKE[2])


def _burst(c, x, y, r, col=YELLOW):
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        c.line([(x + math.cos(a) * r * 0.45, y + math.sin(a) * r * 0.45),
                (x + math.cos(a) * r, y + math.sin(a) * r)], col, 1)


def _bank_back(c, b, th, fx, fi):
    c.poly(bquad(b, XB0, XB1, 228, 508), X.ALU["m"], INK)
    c.line([bpt(b, XB0, 506), bpt(b, XB1, 506)], X.ALU["l"])
    c.line([bpt(b, XB0, 231), bpt(b, XB1, 231)], X.ALU["d"])
    for n in range(6, 0, -1):
        cx = cx_of(n)
        cyl = f"{b}{n}"
        ps = M.psi(th, cyl)
        cw = M.crown(th, cyl)
        if fx.get("water"):
            for s in (-1, 1):
                q = bquad(b, cx + s * 80, cx + s * 87, 250, 490)
                c.poly(q, X.WATER[0])
                ph = (fi * 0.08 + n * 0.17 + (s + 1) * 0.3) % 1.0
                for k in range(3):
                    c.px(*_in_quad(q, 0.5, (ph + k / 3) % 1.0), X.WATER[2])
        c.poly(bquad(b, cx - 76, cx + 76, 228, 508), BORE)
        c.line([bpt(b, cx + 74, 230), bpt(b, cx + 74, 506)], (44, 36, 64))
        _gas_overview(c, bquad(b, cx - 75, cx + 75, cw, 507), ps, n + (6 if b == "R" else 0), fi, fx.get("hot"))


def _bank_front(c, b, th, fx, fi):
    pist = X.PISTON
    for n in range(6, 0, -1):
        cx = cx_of(n)
        cw = M.crown(th, f"{b}{n}")
        c.poly(bquad(b, cx - 74, cx + 74, cw - 118, cw), pist["m"], INK)
        c.line([bpt(b, cx - 73, cw - 2), bpt(b, cx + 73, cw - 2)], pist["l"])
        for dw in (16, 28):
            c.line([bpt(b, cx - 73, cw - dw), bpt(b, cx + 73, cw - dw)], pist["d"])
    hd = X.HEAD
    side = 1.0 if b == "L" else -1.0
    top = [bpt(b, XB0 - 12, 652), bpt(b, XB1 + 12, 652), bpt(b, XB1 + 12, 652, side * 115),
           bpt(b, XB0 - 12, 652, side * 115)]
    c.poly(top, hd["l"], INK)
    c.poly(bquad(b, XB0 - 12, XB1 + 12, 508, 652), hd["m"], INK)
    c.line([bpt(b, XB0 - 11, 650), bpt(b, XB1 + 11, 650)], hd["h"])
    xr = fx.get("xray")
    for loff in (side * 32, side * 86):                   # two cam covers per head
        a, e = bpt(b, XB0, 676, loff), bpt(b, XB1, 676, loff)
        if xr:
            c.thick(a, e, 8, hd["m"] + (70,), None)
            c.line([a, e], X.STEEL["l"], 2)
        else:
            c.thick(a, e, 8, hd["m"], INK)
            c.line([bpt(b, XB0, 684, loff), bpt(b, XB1, 684, loff)], hd["h"])
    for n in range(6, 0, -1):
        cx = cx_of(n)
        ps = M.psi(th, f"{b}{n}")
        for dx, kind in ((-38, "ex"), (38, "in")):
            lift = M.valve_lift(ps, kind) * (1.6 if xr else 1.0)
            c.poly(bquad(b, cx + dx - 14, cx + dx + 14, 504 - lift * 16, 512 - lift * 16), X.STEEL["l"], INK)
            c.line([bpt(b, cx + dx, 512 - lift * 16), bpt(b, cx + dx, 600)], X.STEEL["m"])
        c.poly(bquad(b, cx - 5, cx + 5, 498, 590), X.STEEL["m"])
        if xr:
            for loff, kind in ((side * 32, "in"), (side * 86, "ex")):
                ang = math.radians(M.cam_angle(ps, kind))
                a, nn = M.AX[b], M.INWARD[b]
                vy, vz = -a[0] * math.cos(ang) + nn[0] * math.sin(ang), -a[1] * math.cos(ang) + nn[1] * math.sin(ang)
                base = (676 * a[0] + loff * nn[0], 676 * a[1] + loff * nn[1])
                for dxx in (-38, 38):
                    p0 = P3(cx + dxx, *base)
                    p1 = P3(cx + dxx, base[0] + 34 * vy, base[1] + 34 * vz)
                    c.line([p0, p1], YELLOW, 2)
        if ps < 26 and not fx.get("no_burst"):
            x, y = bpt(b, cx, 560)
            _burst(c, x, y, 9 if b == "L" else 7)


def _rods(c, b, th, pins):
    for n in range(6, 0, -1):
        p = pins[n]
        top = bpt(b, cx_of(n), p["sL"] if b == "L" else p["sR"])
        y, z = p["P"] if b == "L" else p["K"]
        bot = P3(cx_of(n), y, z)
        c.thick(bot, top, 5, X.ROD["m"], INK)
        c.circle(*bot, 3, X.ROD["l"], INK)


def _crank(c, th, pins):
    st = X.STEEL
    c.thick(P3(-575, 0, 0), P3(575, 0, 0), 6, st["m"], INK)
    els = []
    for n in range(1, 7):
        y, z = pins[n]["P"]
        cx = cx_of(n)
        for s in (-1, 1):
            xw = cx + s * 52
            els.append((depth(xw, -y, -z), "cw", xw, y, z))
            els.append((depth(xw, y * 0.5, z * 0.5) + 0.1, "web", xw, y, z))
        els.append((depth(cx, y, z) + 0.2, "pin", cx, y, z))
    for _, kind, x, y, z in sorted(els):
        if kind == "cw":
            c.thick(P3(x, 0, 0), P3(x, -1.35 * y, -1.35 * z), 10, st["d"], INK)
        elif kind == "web":
            c.thick(P3(x, 0, 0), P3(x, y, z), 7, st["m"], INK)
        else:
            c.thick(P3(x - 52, y, z), P3(x + 52, y, z), 7, st["l"], INK)


def _disc(xc, r, n=30, ang0=0.0):
    return [P3(xc, r * math.sin(a + ang0), r * math.cos(a + ang0)) for a in np.linspace(0, 2 * math.pi, n,
                                                                                         endpoint=False)]


def _flywheel(c, th):
    st = X.STEEL
    c.poly(_disc(-660, 255), st["d"], INK)
    c.poly(_disc(-620, 255), st["m"], INK)
    for k in range(6):
        a = math.radians(th + k * 60)
        c.circle(*P3(-620, 165 * math.sin(a), 165 * math.cos(a)), 2.5, st["d"], INK)
    c.poly(_disc(-620, 70), st["l"], INK)


def _case_back(c):
    c.poly([P3(XB0 - 20, 210, -235), P3(XB1 + 20, 210, -235), P3(XB1 + 20, 210, 170), P3(XB0 - 20, 210, 170)],
           (34, 26, 54))


def _case_front(c):
    al = X.ALU
    c.poly([P3(XB0 - 20, -225, -245), P3(XB1 + 20, -225, -245), P3(XB1 + 20, -225, -75), P3(XB0 - 20, -225, -75)],
           al["m"], INK)
    c.line([P3(XB0 - 20, -225, -80), P3(XB1 + 20, -225, -80)], al["l"])
    c.poly([P3(XB1 + 20, -225, -245), P3(XB1 + 20, 210, -245), P3(XB1 + 20, 210, -75), P3(XB1 + 20, -225, -75)],
           al["d"], INK)


def _front_cover(c, th):
    al = X.ALU
    x0, x1, y0, y1, z0, z1 = 560, 630, -175, 175, -230, 240
    c.poly([P3(x0, y0, z0), P3(x1, y0, z0), P3(x1, y0, z1), P3(x0, y0, z1)], al["m"], INK)
    c.poly([P3(x1, y0, z0), P3(x1, y1, z0), P3(x1, y1, z1), P3(x1, y0, z1)], al["d"], INK)
    c.poly([P3(x0, y0, z1), P3(x1, y0, z1), P3(x1, y1, z1), P3(x0, y1, z1)], al["l"], INK)
    c.poly(_disc(640, 95), X.STEEL["m"], INK)
    for k in range(4):
        a = math.radians(-th + k * 90)
        c.line([P3(642, 0, 0), P3(642, 80 * math.sin(a), 80 * math.cos(a))], X.STEEL["l"])


def overview(c, th, fx=None, fi=0):
    fx = fx or {}
    pins = {n: M.pair(th, n) for n in range(1, 7)}
    c.ellipse(OCX + 6, OCY + 62, 160, 13, fill=(8, 6, 18, 170))
    _flywheel(c, th)
    _case_back(c)
    _bank_back(c, "R", th, fx, fi)
    _rods(c, "R", th, pins)
    _bank_front(c, "R", th, fx, fi)
    _crank(c, th, pins)
    _case_front(c)
    _bank_back(c, "L", th, fx, fi)
    _rods(c, "L", th, pins)
    _bank_front(c, "L", th, fx, fi)
    _front_cover(c, th)
    if fx.get("vol"):
        b, n = fx["vol"][0], int(fx["vol"][1])
        q = bquad(b, cx_of(n) - 76, cx_of(n) + 76, 325, 505)
        c.poly(q, (110, 220, 255, 110), CYAN, 1)
    return pins


def overview_blurred(t, fx, fi):
    """the overview with motion blur: average of sub-frame crank angles across a 0.6-frame shutter"""
    th = M.theta(t)
    dth = M.omega(t) / M.FPS * 0.6
    n = int(min(10, max(1, math.ceil(dth / 14.0))))
    if n == 1:
        c = engine_bg()
        overview(c, th, fx, fi)
        return c
    ims = []
    for i in range(n):
        c = engine_bg()
        overview(c, th + dth * (i / (n - 1) - 0.5), dict(fx, no_burst=True), fi)
        ims.append(c.img)
    return Canvas(img=X.average(ims))


# =================================================================================================== detail (end view)
SD, DCX, DCY = 0.36, 180.0, 458.0


def DPt(y, z):
    return (DCX + y * SD, DCY - z * SD)


def dpt(b, w, l=0.0):
    a, nn = M.AX[b], M.INWARD[b]
    return DPt(w * a[0] + l * nn[0], w * a[1] + l * nn[1])


def dquad(b, w0, w1, l0, l1):
    return [dpt(b, w0, l0), dpt(b, w0, l1), dpt(b, w1, l1), dpt(b, w1, l0)]


def _path(pts, u):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    s = u * sum(seg)
    for i, L in enumerate(seg):
        if s <= L or i == len(seg) - 1:
            return _lerp(pts[i], pts[i + 1], clamp(s / max(L, 1e-6)))
        s -= L
    return pts[-1]


def _pipe(c, pts, w, fill):
    for i in range(len(pts) - 1):
        c.thick(pts[i], pts[i + 1], w + 2, INK)
    for p in pts:
        c.circle(*p, (w + 2) / 2, INK)
    for i in range(len(pts) - 1):
        c.thick(pts[i], pts[i + 1], w, fill)
    for p in pts:
        c.circle(*p, w / 2, fill)


def _cam(c, b, l, ang_deg, col):
    a, nn = M.AX[b], M.INWARD[b]
    cy_, cz_ = 698 * a[0] + l * nn[0], 698 * a[1] + l * nn[1]
    lobe = math.radians(ang_deg)
    pts = []
    for k in range(28):
        ph = 2 * math.pi * k / 28
        r = 17 + 11 * max(0.0, math.cos(ph - lobe)) ** 3
        vy = -a[0] * math.cos(ph) + nn[0] * math.sin(ph)
        vz = -a[1] * math.cos(ph) + nn[1] * math.sin(ph)
        pts.append(DPt(cy_ + r * vy, cz_ + r * vz))
    c.poly(pts, col, INK)
    c.circle(*DPt(cy_, cz_), 2, X.STEEL["d"])


def _spark_plug(c, x, y):
    c.rect(x - 2, y - 14, x + 2, y - 4, fill=(236, 232, 240), outline=INK)
    c.rect(x - 4, y - 4, x + 4, y + 1, fill=(150, 150, 170), outline=INK)
    c.rect(x - 1, y + 2, x + 1, y + 6, fill=(120, 120, 140), outline=INK)
    c.line([(x - 9, y - 12), (x + 9, y + 6)], INK, 4)
    c.line([(x + 9, y - 12), (x - 9, y + 6)], INK, 4)
    c.line([(x - 9, y - 12), (x + 9, y + 6)], RED, 2)
    c.line([(x + 9, y - 12), (x - 9, y + 6)], RED, 2)


INTAKE_PATH = [(0.0, 760.0), (0.0, 600.0), None]   # completed in _air_paths


def _air_paths():
    inn = [DPt(0, 770), DPt(0, 600), dpt("L", 606, 128), dpt("L", 566, 56), dpt("L", 512, 40), dpt("L", 470, 20)]
    out = [dpt("L", 470, -20), dpt("L", 512, -40), dpt("L", 566, -56), dpt("L", 606, -128), dpt("L", 596, -200)]
    return inn, out


def detail(c, th, lb3, t, fi):
    al, st, hd, pist, rod = X.ALU, X.STEEL, X.HEAD, X.PISTON, X.ROD
    p1 = M.pair(th, 1)
    psL, psR = M.psi(th, "L1"), M.psi(th, "R1")
    cwL, cwR = p1["sL"] + M.H_CROWN, p1["sR"] + M.H_CROWN
    case = [(-216, 124), (0, 249), (216, 124), (300, 40), (290, -120), (200, -210), (-200, -210), (-290, -120),
            (-300, 40)]
    c.poly([DPt(*q) for q in case], al["d"], INK)
    c.line([DPt(-296, 36), DPt(-286, -118), DPt(-198, -206)], al["m"])
    c.circle(*DPt(0, 0), 178 * SD, BORE)
    for b in ("R", "L"):
        c.poly(dquad(b, 215, 508, -125, 125), al["m"], INK)
        c.line([dpt(b, 506, -124), dpt(b, 506, 124)], al["l"])
        for s in (-1, 1):
            c.poly(dquad(b, 240, 496, s * 90, s * 112), X.WATER[0])
            for k in range(3):
                ph = (t * 0.6 + k / 3 + (s + 1) * 0.25) % 1.0
                c.px(*dpt(b, 240 + 256 * ph, s * 101), X.WATER[2])
        c.poly(dquad(b, 150, 508, -86, 86), st["d"])
        c.poly(dquad(b, 150, 508, -76, 76), BORE)
    # the focus cylinder L1: what is in the chamber
    gas = dquad("L", cwL, 507, -75, 75)
    inn, out = _air_paths()
    stg = M.stroke_of(psL)
    c.poly(gas, gas_color(psL, True))
    if stg in ("intake", "compression"):
        p = (psL - 360) / 180 if stg == "intake" else 1.0
        hot = 0.0 if stg == "intake" else ((psL - 540) / 180) ** 1.2
        for i in range(40):
            if i >= 40 * min(1.0, p * 1.2):
                continue
            col = X.mix(X.AIR[i % 2], X.HOT[i % 2], hot)
            x, y = _in_quad(gas, 0.06 + 0.88 * hsh(i, 1), 0.06 + 0.88 * hsh(i, 2))
            c.rect(x, y, x + 1, y + 1, fill=col)
    elif stg == "power":
        if psL < 110:
            for i in range(70):
                u, v = hsh(i, fi * 3 + 1), hsh(i, fi * 3 + 2)
                x, y = _in_quad(gas, 0.04 + 0.92 * u, 0.04 + 0.92 * v)
                c.rect(x, y, x + 1, y + 1, fill=X.FIRE[int(hsh(i, fi + 5) * 3)])
        else:
            for i in range(14):
                x, y = _in_quad(gas, 0.1 + 0.8 * hsh(i, 21), 0.1 + 0.8 * hsh(i, 22))
                c.rect(x, y, x + 1, y + 1, fill=X.SMOKE[1])
    else:
        p = (psL - 180) / 180
        for i in range(30):
            if i >= 30 * (1 - p * 0.85):
                continue
            x, y = _in_quad(gas, 0.1 + 0.8 * hsh(i, 23), clamp(0.1 + 0.8 * hsh(i, 24)))
            c.rect(x, y, x + 1, y + 1, fill=X.SMOKE[i % 3])
    c.poly(dquad("R", cwR, 507, -75, 75), (32, 26, 46))
    # crank, rods, pistons
    P, K = p1["P"], p1["K"]
    eta = math.atan2(P[0], P[1])
    cw_pts = [DPt(0, 0)] + [DPt(160 * math.sin(eta + math.pi + d), 160 * math.cos(eta + math.pi + d))
                            for d in np.linspace(-1.1, 1.1, 12)]
    c.poly(cw_pts, st["d"], INK)
    c.thick(DPt(0, 0), DPt(*P), 82 * SD, st["m"], INK)
    c.circle(*DPt(0, 0), 52 * SD, st["l"], INK)
    c.circle(*DPt(0, 0), 20 * SD, st["d"])
    QL, QR = p1["QL"], p1["QR"]
    c.thick(DPt(*K), DPt(*QR), 30 * SD, rod["m"], INK)
    c.circle(*DPt(*QR), 20 * SD, rod["l"], INK)
    c.thick(DPt(*P), DPt(*QL), 40 * SD, rod["m"], INK)
    c.circle(*DPt(*P), 62 * SD, rod["m"], INK)
    c.circle(*DPt(*K), 22 * SD, rod["m"], INK)
    c.circle(*DPt(*P), 38 * SD, st["l"], INK)
    c.circle(*DPt(*K), 12 * SD, st["l"], INK)
    c.circle(*DPt(*QL), 20 * SD, rod["l"], INK)
    for b, cw in (("R", cwR), ("L", cwL)):
        c.poly(dquad(b, cw - 125, cw, -74, 74), pist["m"], INK)
        c.line([dpt(b, cw - 2, -72), dpt(b, cw - 2, 72)], pist["l"])
        c.poly(dquad(b, cw - 13, cw, -30, 30), BORE if b == "R" else gas_color(psL, True))
        for dw in (18, 30, 42):
            c.line([dpt(b, cw - dw, -73), dpt(b, cw - dw, 73)], pist["d"])
        c.circle(*dpt(b, cw - M.H_CROWN, 0), 20 * SD, st["l"], INK)
    # heads: ports, valves, injector, cams
    for b, ps in (("R", psR), ("L", psL)):
        c.poly(dquad(b, 508, 662, -132, 132), hd["m"], INK)
        c.line([dpt(b, 660, -131), dpt(b, 660, 131)], hd["h"])
        _pipe(c, [dpt(b, 512, 40), dpt(b, 566, 56), dpt(b, 606, 128)], 24 * SD, BORE)
        _pipe(c, [dpt(b, 512, -40), dpt(b, 566, -56), dpt(b, 606, -128)], 24 * SD, BORE)
        for l, kind in ((40, "in"), (-40, "ex")):
            lift = M.valve_lift(ps, kind)
            dw = lift * 16
            c.thick(dpt(b, 508 - dw, l), dpt(b, 662, l), 8 * SD, st["l"], INK)
            c.poly(dquad(b, 497 - dw, 508 - dw, l - 25, l + 25), st["l"], INK)
            c.poly(dquad(b, 656, 670, l - 14, l + 14), st["m"], INK)
            for k in range(4):
                c.line([dpt(b, 610 + k * 11, l - 10), dpt(b, 616 + k * 11, l + 10)], st["m"])
        c.poly(dquad(b, 492, 655, -8, 8), st["m"], INK)
        c.poly(dquad(b, 628, 655, -12, 12), st["l"], INK)
        c.poly(dquad(b, 662, 744, -106, 106), hd["d"], INK)
        c.poly(dquad(b, 668, 738, -98, 98), (30, 20, 36))
        _cam(c, b, 40, M.cam_angle(ps, "in"), st["l"])
        _cam(c, b, -40, M.cam_angle(ps, "ex"), st["l"])
    # air in, exhaust out, fuel pump
    man = [(-167, 552), (-207, 619), (207, 619), (167, 552)]
    c.poly([DPt(*q) for q in man], al["l"], INK)
    c.poly([DPt(-36, 619), DPt(36, 619), DPt(36, 780), DPt(-36, 780)], al["l"], INK)
    c.poly([DPt(-24, 610), DPt(24, 610), DPt(24, 781), DPt(-24, 781)], BORE)
    for b in ("L", "R"):
        _pipe(c, [dpt(b, 606, -128), dpt(b, 600, -168), dpt(b, 560, -205)], 30 * SD, (70, 64, 88))
    c.poly([DPt(-52, 380), DPt(52, 380), DPt(52, 452), DPt(-52, 452)], st["m"], INK)
    c.text("NK-1", 180, DPt(0, 446)[1], WHITE, 1, "c", lint=False)
    inj_on = psL > 708 or psL < 10
    for b in ("L", "R"):
        col = YELLOW if (b == "L" and inj_on) else (150, 110, 40)
        c.line([DPt(-30 if b == "L" else 30, 452), dpt(b, 560, 150), dpt(b, 640, 132), dpt(b, 640, 9)], INK, 3)
        c.line([DPt(-30 if b == "L" else 30, 452), dpt(b, 560, 150), dpt(b, 640, 132), dpt(b, 640, 9)], col, 1)
    lin, lex = M.valve_lift(psL, "in"), M.valve_lift(psL, "ex")
    if lin > 0.05:
        for i in range(12):
            u = (t * 1.6 + i / 12) % 1.0
            x, y = _path(inn, u)
            c.rect(x, y, x + 1, y + 1, fill=X.AIR[i % 2])
    if lex > 0.05:
        for i in range(10):
            u = (t * 1.3 + i / 10) % 1.0
            x, y = _path(out, u)
            c.rect(x - 1, y - 1, x + 1, y + 1, fill=X.SMOKE[i % 3])
    if inj_on:
        tip = dpt("L", 490, 0)
        for l in (-64, -32, 0, 32, 64):
            c.line([tip, dpt("L", max(cwL + 6, 470), l)], X.FIRE[1])
    if 0 <= psL < 30:
        x, y = _in_quad(gas, 0.5, 0.5)
        _burst(c, x, y, 26, YELLOW)
    c.text("L1", dpt("L", 300, -170)[0], dpt("L", 300, -170)[1] - 6, YELLOW, 1, "c")
    c.text("R1", dpt("R", 300, -170)[0], dpt("R", 300, -170)[1] - 6, X.DIMTXT, 1, "c")
    return dict(P=DPt(*P), inj=dpt("L", 640, 0), vin=dpt("L", 497 - lin * 16, 40), vex=dpt("L", 497 - lex * 16, -40),
                chamber=_in_quad(gas, 0.5, 0.5))


TABS = [("吸气", "SUCK"), ("压缩", "SQUEEZE"), ("做功", "BANG"), ("排气", "BLOW")]


def tabs(c, k, y=114):
    for i, (cn, en) in enumerate(TABS):
        x0 = 10 + i * 86
        on = i == k
        box(c, x0, y, x0 + 82, y + 18, edge=YELLOW if on else (80, 72, 110), fill=YELLOW if on else PANEL)
        s = f"{cn} {en}"
        c.text(s, x0 + 41, y + 2, INK if on else GREY, 1, "c", outline=None if on else INK)


# =================================================================================================== bar by bar
def _x2(lb):
    return lb < 2.0


def frame(t, fi=None):
    fi = int(round(t * M.FPS)) if fi is None else fi
    bi, lb = M.bar_beat(t)
    role = M.ROLES[bi]
    th = M.theta(t)

    if role == "hook":
        c = tank_scene(t)
        hook_text(c, leader=lb >= 2)
        hud(c, t)
        return c.img

    if role == "zoom":
        if lb < 1:
            c = zoomed(tank_scene(t), 1 + 4 * lb ** 2, *ZOOM_AT)
            hook_text(c)
            hud(c, t)
            return c.img
        c = overview_blurred(t, {}, fi)
        if lb < 2:
            title_box(c, ["快得看不清"], "TOO FAST TO SEE")
        else:
            title_box(c, ["放慢看看"], "LET'S SLOW IT DOWN")
        hud(c, t)
        return c.img

    if role == "slow":
        c = engine_bg()
        overview(c, th, {}, fi)
        title_box(c, ["12 个活塞推 1 根曲轴"], "12 PISTONS TURN ONE CRANKSHAFT")
        if lb < 0.75:
            x, y = bpt("L", cx_of(5), 560)
            c.text("砰！", x + 2, y - 52, YELLOW, 2, "c")
            c.text("BANG!", x + 2, y - 20, WHITE, 1, "c")
        if lb >= 1:
            label(c, "活塞", "PISTON", 10, 160, anchor=bpt("L", cx_of(2), M.crown(th, "L2") - 60))
        if lb >= 2:
            label(c, "曲轴", "CRANKSHAFT", 236, 470, anchor=P3(500, 0, 0))
        if lb >= 3:
            label(c, "两排 · 夹角 60°", "TWO BANKS, 60° V", 200, 160, anchor=bpt("R", cx_of(1), 640))
        hud(c, t)
        return c.img

    if role == "stroke":
        lb3 = (t - 3 * M.BAR) / M.BEAT
        k = int(min(3, lb3 // 3))
        c = engine_bg()
        a = detail(c, th, lb3, t, fi)
        heads = [(["① 只吸空气"], "1 SUCK: AIR ONLY", None),
                 (["② 压到约 1/15"], "2 SQUEEZE: ~15:1, 500°C+", "空气热到 500°C 以上"),
                 (["③ 喷柴油，自己着火"], "3 BANG! FUEL LIGHTS ITSELF", None),
                 (["④ 废气排出去"], "4 BLOW: EXHAUST OUT", None)]
        cn, en, sub = heads[k]
        yb = title_box(c, cn, en, sub=sub)
        tabs(c, k, y=yb + 6)
        ly = yb + 32
        if k == 0 and lb3 >= 1:
            label(c, "进气门", "INTAKE VALVE", 10, ly, anchor=a["vin"])
        if k == 1 and lb3 >= 4:
            _spark_plug(c, 300, ly + 22)
            label(c, "没有火花塞", "NO SPARK PLUG", 284, ly, anchor=None, align="r")
        if k == 2:
            if lb3 < 6.8:
                x, y = a["chamber"]
                c.text("砰！", x, y - 46, YELLOW, 2, "c")
            label(c, "喷油器", "INJECTOR", 10, ly, anchor=a["inj"])
            if lb3 >= 7:
                label(c, "推着曲轴转", "PUSHES THE CRANK", 350, 500, anchor=a["P"], align="r")
        if k == 3 and lb3 >= 10:
            label(c, "排气门", "EXHAUST VALVE", 10, ly, anchor=a["vex"])
        hud(c, t)
        return c.img

    if role in ("order", "cams", "fire", "volume", "floor", "real", "turns"):
        if role == "turns" and lb >= 2:
            z = 1 + 4 * (1 - (lb - 2) / 2) ** 2
            c = zoomed(tank_scene(t), z, *ZOOM_AT)
            title_box(c, ["曲轴每秒转 33 圈"], "33 TURNS EVERY SECOND")
            hud(c, t)
            return c.img
        fx = {"order": {}, "cams": {"xray": True}, "fire": {"water": True, "hot": True},
              "volume": {"vol": "L2"}, "floor": {}, "real": {}, "turns": {}}[role]
        c = overview_blurred(t, fx, fi)
        x2 = role in ("order", "cams", "fire", "volume", "floor") and _x2(lb)
        if role == "order":
            title_box(c, ["每转 60° 就有一缸做功"], "A BANG EVERY 60° OF TURN")
            firing_strip(c, th)
        elif role == "cams":
            title_box(c, ["每排 2 根凸轮轴"], "2 CAMSHAFTS PER BANK", sub="一共 48 个气门 · 48 VALVES")
            if lb >= 1:
                label(c, "凸轮轴", "CAMSHAFT", 236, 470, anchor=bpt("L", cx_of(1), 676, 86))
        elif role == "fire":
            title_box(c, ["燃烧 1700–1900°C"], "FIRE: 1,700–1,900°C", sub="比岩浆（约 1200°C）还烫")
            if lb >= 1:
                label(c, "冷却水", "WATER JACKET", 10, 470, anchor=bpt("L", cx_of(5), 380))
                label(c, "靠水冷", "WATER-COOLED", 350, 470, anchor=None, align="r")
        elif role == "volume":
            title_box(c, ["1 个缸 = 3.2 升"], "ONE CYLINDER = 3.2 L")
            q = bquad("L", cx_of(2) - 76, cx_of(2) + 76, 325, 505)
            label(c, "3.2 L", None, 300, 230, anchor=_in_quad(q, 1.0, 0.5), color=CYAN)
            if lb >= 1:
                car_engines(c, lb)
        elif role == "floor":
            c.text("全速！", 180, 84, YELLOW, 3, "c")
            c.text("FLOOR IT!", 180, 136, WHITE, 2, "c")
        elif role == "real":
            title_box(c, ["12 缸，一声轰鸣"], "12 CYLINDERS. ONE ROAR.")
            if lb >= 2:
                y = 474
                s1, s2 = "每秒 200 次做功", "200 BANGS A SECOND"
                w = max(X.text_w(s1, 2), X.text_w(s2))
                box(c, 180 - w // 2 - 7, y, 180 + w // 2 + 7, y + 52, edge=YELLOW, fill=(40, 20, 30))
                c.text(s1, 180, y + 3, YELLOW, 2, "c")
                c.text(s2, 180, y + 35, WHITE, 1, "c")
        elif role == "turns":
            title_box(c, ["曲轴每秒转 33 圈"], "33 TURNS EVERY SECOND")
        hud(c, t, x2=x2)
        return c.img

    # end: back on the road, then the opening frame again (seamless loop)
    c = tank_scene(t)
    if lb < 3:
        title_box(c, ["520 马力", "推着 46 吨跑"], "520 HP MOVES 46 TONNES")
    else:
        hook_text(c)
    hud(c, t)
    return c.img


def firing_strip(c, th):
    y = 470
    c.text("工作顺序 FIRING ORDER", 180, y, WHITE, 1, "c")
    last = int((th % 720) // 60)
    for i, cyl in enumerate(M.ORDER):
        x0 = 13 + i * 28
        on = i == last
        done = (last - i) % 12 in (1, 2)
        box(c, x0, y + 18, x0 + 25, y + 36, edge=YELLOW if on else (80, 72, 110),
            fill=YELLOW if on else ((60, 40, 30) if done else PANEL))
        c.text(cyl, x0 + 13, y + 19, INK if on else (WHITE if done else GREY), 1, "c", outline=None if on else INK)
    c.text("L = 左排  R = 右排", 180, y + 40, GREY, 1, "c")


def _car_engine(c, x, y):
    c.rect(x - 18, y - 8, x + 18, y + 8, fill=X.ALU["m"], outline=INK)
    for k in range(4):
        c.rect(x - 16 + k * 9, y - 13, x - 10 + k * 9, y - 8, fill=X.HEAD["m"], outline=INK)
    c.rect(x - 22, y - 2, x - 18, y + 4, fill=X.STEEL["m"], outline=INK)


def car_engines(c, lb):
    y = 486
    _car_engine(c, 96, y)
    c.text("1.6 L", 96, y + 12, WHITE, 1, "c")
    if lb >= 2:
        c.text("+", 180, y - 12, YELLOW, 2, "c")
        _car_engine(c, 264, y)
        c.text("1.6 L", 264, y + 12, WHITE, 1, "c")
        c.text("= 2 台家用车发动机  2 CAR ENGINES", 180, y + 30, CYAN, 1, "c")
