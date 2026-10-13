"""Procedural dark room with a warm window light beam (style ref: dim 3D room,
glowing window, dusty light shaft). Builds a static plate per shot."""
import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 2560, 1440
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_BLACK = os.path.join(HERE, "fonts", "NotoSerifSC-Black.otf")
FONT_BOLD = os.path.join(HERE, "fonts", "NotoSerifSC-Bold.otf")
FONT_SANS = os.path.join(HERE, "fonts", "NotoSansSC-Regular.otf")

# room (meters, camera at origin, +y down, +z forward)
RX, RY_TOP, RY_FLOOR, RZ_BACK, RZ_NEAR = 2.487, -1.3, 1.3, 6.0, 0.8
BASE_F = 1062.0
WARM = np.array([1.0, 0.80, 0.55], np.float32)
LIGHT_D = np.array([0.42, 0.62, -1.0])  # light direction (per unit -z)
WIN = (-1.92, -0.51, -0.85, 0.34)       # x0, x1, y0, y1 on back wall

_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)


def C(*rgb):
    return np.array(rgb, np.float32) / 255.0


def font(path, size):
    return ImageFont.truetype(path, max(4, int(size)))


def bigblur(img, sigma):
    if sigma < 0.3:
        return img
    if sigma <= 24:
        return cv2.GaussianBlur(img, (0, 0), sigma)
    f = sigma / 8.0
    h, w = img.shape[:2]
    sw, sh = max(2, int(w / f)), max(2, int(h / f))
    small = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), 8.0)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


class Canvas:
    def __init__(self, k=1.0, target=None):
        self.k = k
        self.F = BASE_F * k
        if target is None:
            self.p0 = np.array([0.0, (720 - 530) / BASE_F])
        else:
            self.p0 = np.array([target[0] / target[2], target[1] / target[2]])
        self.A = np.zeros((H, W, 3), np.float32)   # albedo
        self.E = np.zeros((H, W, 3), np.float32)   # emissive
        self.S = np.zeros((H, W), np.float32)      # shadow (blocks patch light)
        self.L = np.zeros((H, W, 3), np.float32)   # extra local light

    # ---------- projection ----------
    def P(self, x, y, z):
        return (W / 2 + self.F * (x / z - self.p0[0]),
                H / 2 + self.F * (y / z - self.p0[1]))

    def PP(self, pts3):
        return [self.P(*p) for p in pts3]

    def px(self, meters, z):
        return self.F * meters / z

    # ---------- raster helpers ----------
    def _mask(self, pts, blur=0.0):
        pts = np.asarray(pts, np.float64)
        pad = int(blur * 3) + 2
        bx0, by0 = pts[:, 0].min(), pts[:, 1].min()
        bx1, by1 = pts[:, 0].max(), pts[:, 1].max()
        x0, y0 = max(0, int(np.floor(bx0)) - pad), max(0, int(np.floor(by0)) - pad)
        x1, y1 = min(W, int(np.ceil(bx1)) + pad), min(H, int(np.ceil(by1)) + pad)
        if x1 - x0 < 1 or y1 - y0 < 1:
            return None
        ss = 3
        img = Image.new("L", ((x1 - x0) * ss, (y1 - y0) * ss), 0)
        ImageDraw.Draw(img).polygon([((px - x0) * ss, (py - y0) * ss) for px, py in pts], fill=255)
        m = np.asarray(img.reduce(ss), np.float32) / 255.0
        if blur > 0.3:
            m = cv2.GaussianBlur(m, (0, 0), blur)
        return x0, y0, x1, y1, m, (bx0, by0, bx1, by1)

    def _color_field(self, color, grad, region, bb):
        x0, y0, x1, y1 = region
        if grad is None:
            return np.broadcast_to(np.asarray(color, np.float32), (y1 - y0, x1 - x0, 3))
        c0, c1, mode = grad
        c0, c1 = np.asarray(c0, np.float32), np.asarray(c1, np.float32)
        if mode == "v":
            t = (_YY[y0:y1, x0:x1] - bb[1]) / max(1e-3, bb[3] - bb[1])
        else:
            t = (_XX[y0:y1, x0:x1] - bb[0]) / max(1e-3, bb[2] - bb[0])
        t = np.clip(t, 0, 1)[..., None]
        return c0 * (1 - t) + c1 * t

    def apply(self, region, m, col, layer):
        x0, y0, x1, y1 = region
        if layer == "A":
            a = self.A[y0:y1, x0:x1]
            a[:] = a * (1 - m[..., None]) + col * m[..., None]
        elif layer == "E":
            self.E[y0:y1, x0:x1] += col * m[..., None]
        elif layer == "L":
            self.L[y0:y1, x0:x1] += col * m[..., None]
        elif layer == "S":
            s = self.S[y0:y1, x0:x1]
            np.maximum(s, m, out=s)
        elif layer == "AE":  # opaque surface that also glows
            a = self.A[y0:y1, x0:x1]
            a[:] = a * (1 - m[..., None])
            e = self.E[y0:y1, x0:x1]
            e[:] = e * (1 - m[..., None]) + col * m[..., None]

    def poly(self, pts, color=(0, 0, 0), layer="A", alpha=1.0, blur=0.0, grad=None):
        r = self._mask(pts, blur)
        if r is None:
            return
        x0, y0, x1, y1, m, bb = r
        col = self._color_field(color, grad, (x0, y0, x1, y1), bb)
        self.apply((x0, y0, x1, y1), m * alpha, col, layer)

    def poly3(self, pts3, color, **kw):
        self.poly(self.PP(pts3), color, **kw)

    def ellipse_pts(self, cx, cy, rx, ry, rot=0.0, n=72, a0=0, a1=2 * np.pi):
        t = np.linspace(a0, a1, n)
        x, y = rx * np.cos(t), ry * np.sin(t)
        c, s = np.cos(rot), np.sin(rot)
        return list(zip(cx + x * c - y * s, cy + x * s + y * c))

    def ellipse(self, cx, cy, rx, ry, color, rot=0.0, **kw):
        self.poly(self.ellipse_pts(cx, cy, rx, ry, rot), color, **kw)

    def line3(self, a, b, width_m, color, **kw):
        pa, pb = np.array(self.P(*a)), np.array(self.P(*b))
        za = a[2]
        wpx = max(0.8, self.px(width_m, za))
        d = pb - pa
        n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9) * wpx / 2
        self.poly([pa + n, pb + n, pb - n, pa - n], color, **kw)

    def rgba_image(self, img, x0, y0, layer="A", alpha=1.0, emissive_gain=1.0):
        """Composite a PIL RGBA image with top-left at (x0, y0)."""
        arr = np.asarray(img, np.float32) / 255.0
        h, w = arr.shape[:2]
        x0, y0 = int(round(x0)), int(round(y0))
        cx0, cy0 = max(0, x0), max(0, y0)
        cx1, cy1 = min(W, x0 + w), min(H, y0 + h)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        sub = arr[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        m = sub[..., 3] * alpha
        self.apply((cx0, cy0, cx1, cy1), m, sub[..., :3] * emissive_gain, layer)

    # ---------- 3D primitives ----------
    def box(self, x0, x1, y0, y1, z0, z1, top, front, side, bottom=None, alpha=1.0):
        """Axis aligned box; y0 = top (smaller y = higher)."""
        if y0 > 0:
            self.poly3([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], top, alpha=alpha)
        if y1 < 0:
            self.poly3([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
                       bottom if bottom is not None else side, alpha=alpha)
        if x0 > 0:
            self.poly3([(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], side, alpha=alpha)
        if x1 < 0:
            self.poly3([(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)], side, alpha=alpha)
        self.poly3([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], front, alpha=alpha)

    def floor_shadow(self, pts3, blur_m=0.03):
        """Project 3D points along the light direction onto the floor -> shadow."""
        out = []
        for (x, y, z) in pts3:
            t = (RY_FLOOR - y) / LIGHT_D[1]
            out.append((x + LIGHT_D[0] * t, RY_FLOOR, max(0.3, z + LIGHT_D[2] * t)))
        pts = np.array(self.PP(out))
        hull = cv2.convexHull(pts.astype(np.float32)).reshape(-1, 2)
        self.poly(hull, 0, layer="S", blur=self.px(blur_m, 3.0))


# =====================================================================
#   scene content
# =====================================================================

def draw_room(c):
    F = c
    zb, zn = RZ_BACK, RZ_NEAR
    # ceiling, side walls, floor
    c.poly3([(-RX, RY_TOP, zn), (RX, RY_TOP, zn), (RX, RY_TOP, zb), (-RX, RY_TOP, zb)], C(66, 66, 72),
            grad=(C(40, 40, 46), C(80, 80, 88), "v"))
    c.poly3([(-RX, RY_TOP, zn), (-RX, RY_TOP, zb), (-RX, RY_FLOOR, zb), (-RX, RY_FLOOR, zn)], 0,
            grad=(C(62, 62, 70), C(96, 96, 104), "h"))
    c.poly3([(RX, RY_TOP, zn), (RX, RY_TOP, zb), (RX, RY_FLOOR, zb), (RX, RY_FLOOR, zn)], 0,
            grad=(C(96, 96, 104), C(62, 62, 70), "h"))
    c.poly3([(-RX, RY_FLOOR, zn), (RX, RY_FLOOR, zn), (RX, RY_FLOOR, zb), (-RX, RY_FLOOR, zb)], 0,
            grad=(C(108, 100, 92), C(84, 78, 72), "v"))
    # floor planks
    for i in range(1, 14):
        x = -RX + i * (2 * RX / 14)
        c.line3((x, RY_FLOOR, zb), (x, RY_FLOOR, zn), 0.006, C(60, 55, 50), alpha=0.55)
    # back wall
    c.poly3([(-RX, RY_TOP, zb), (RX, RY_TOP, zb), (RX, RY_FLOOR, zb), (-RX, RY_FLOOR, zb)], 0,
            grad=(C(112, 112, 120), C(124, 122, 126), "v"))
    # baseboards
    c.poly3([(-RX, 1.22, zb), (RX, 1.22, zb), (RX, RY_FLOOR, zb), (-RX, RY_FLOOR, zb)], C(80, 78, 80))
    c.poly3([(-RX, 1.22, zn), (-RX, 1.22, zb), (-RX, RY_FLOOR, zb), (-RX, RY_FLOOR, zn)], C(70, 68, 72))
    c.poly3([(RX, 1.22, zn), (RX, 1.22, zb), (RX, RY_FLOOR, zb), (RX, RY_FLOOR, zn)], C(70, 68, 72))
    # crisp corner edges (subtle highlight like the reference)
    edge = C(150, 150, 158)
    for a, b in [((-RX, RY_TOP, zb), (RX, RY_TOP, zb)), ((-RX, RY_FLOOR, zb), (RX, RY_FLOOR, zb)),
                 ((-RX, RY_TOP, zb), (-RX, RY_FLOOR, zb)), ((RX, RY_TOP, zb), (RX, RY_FLOOR, zb)),
                 ((-RX, RY_TOP, zb), (-RX, RY_TOP, zn)), ((RX, RY_TOP, zb), (RX, RY_TOP, zn)),
                 ((-RX, RY_FLOOR, zb), (-RX, RY_FLOOR, zn)), ((RX, RY_FLOOR, zb), (RX, RY_FLOOR, zn))]:
        c.line3(a, b, 0.008, edge, alpha=0.35)

    # window (recessed) - jamb + sill + glowing panes
    x0, x1, y0, y1 = WIN
    d = 0.22
    c.poly3([(x0, y0, zb), (x0, y0, zb + d), (x0, y1, zb + d), (x0, y1, zb)], C(150, 140, 125))
    c.poly3([(x0, y1, zb), (x1, y1, zb), (x1, y1, zb + d), (x0, y1, zb + d)], C(170, 160, 140))
    c.poly3([(x0, y0, zb), (x1, y0, zb), (x1, y0, zb + d), (x0, y0, zb + d)], C(120, 115, 110))
    zp = zb + d
    c.poly3([(x0, y0, zp), (x1, y0, zp), (x1, y1, zp), (x0, y1, zp)], 0, layer="AE",
            grad=(np.array([3.3, 3.0, 2.4], np.float32), np.array([2.9, 2.5, 1.8], np.float32), "v"))
    # mullions (dark silhouettes against the light)
    fr = np.array([0.55, 0.45, 0.32], np.float32)
    mw = 0.035
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    for (a0, a1, b0, b1) in [(xm - mw, xm + mw, y0, y1), (x0, x1, ym - mw, ym + mw),
                             (x0, x0 + mw * 1.5, y0, y1), (x1 - mw * 1.5, x1, y0, y1),
                             (x0, x1, y0, y0 + mw * 1.5), (x0, x1, y1 - mw * 1.5, y1)]:
        c.poly3([(a0, b0, zp - 0.01), (a1, b0, zp - 0.01), (a1, b1, zp - 0.01), (a0, b1, zp - 0.01)],
                fr, layer="AE")


def draw_picture(c):
    z = RZ_BACK - 0.005
    x0, x1, y0, y1 = 0.85, 1.5, -0.75, -0.25
    c.poly3([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], C(60, 58, 60))
    b = 0.05
    c.poly3([(x0 + b, y0 + b, z), (x1 - b, y0 + b, z), (x1 - b, y1 - b, z), (x0 + b, y1 - b, z)], C(22, 22, 26))
    cx, cy = c.P((x0 + x1) / 2, (y0 + y1) / 2, z)
    r = c.px(0.06, z)
    c.ellipse(cx - r * 0.9, cy, r, r, C(150, 60, 50), alpha=0.7, blur=r * 0.6)
    c.ellipse(cx + r * 0.9, cy, r, r, C(60, 130, 80), alpha=0.6, blur=r * 0.6)


def draw_sticky(c):
    z = RZ_BACK - 0.004
    x0, x1, y0, y1 = 0.10, 0.32, -0.12, 0.10
    p = c.PP([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])
    # slight shadow
    off = c.px(0.006, z)
    c.poly([(q[0] + off, q[1] + off) for q in p], C(20, 20, 20), alpha=0.5, blur=off * 2)
    curl = c.px(0.035, z)
    body = [p[0], p[1], p[2], (p[2][0] - curl, p[2][1]), (p[2][0], p[2][1] - curl)]
    body = [p[0], p[1], (p[2][0], p[2][1] - curl), (p[2][0] - curl, p[2][1]), p[3]]
    c.poly(body, 0, grad=(C(246, 214, 92), C(226, 186, 70), "v"))
    c.poly([(p[2][0], p[2][1] - curl), (p[2][0] - curl, p[2][1]), (p[2][0] - curl, p[2][1] - curl)],
           C(255, 236, 140))
    w = int(p[1][0] - p[0][0])
    if w > 30:
        img = Image.new("RGBA", (w, w), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        fnt = font(FONT_BOLD, w * 0.2)
        d.multiline_text((w / 2, w * 0.47), "等有空\n再弄", font=fnt, fill=(40, 50, 110, 235),
                         anchor="mm", align="center", spacing=w * 0.05)
        img = img.rotate(-4, resample=Image.BICUBIC)
        c.rgba_image(img, p[0][0], p[0][1])


def draw_notice(c):
    z = RZ_BACK - 0.004
    x0, x1, y0, y1 = 1.75, 2.25, -0.58, 0.12
    p = c.PP([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])
    off = c.px(0.008, z)
    c.poly([(q[0] + off, q[1] + off) for q in p], C(20, 20, 20), alpha=0.45, blur=off * 2)
    c.poly(p, 0, grad=(C(232, 228, 214), C(212, 200, 172), "v"))
    gx, gy = c.P(2.0, -0.25, z)
    c.ellipse(gx, gy, c.px(0.5, z), c.px(0.6, z), WARM * 0.45, layer="L", blur=c.px(0.2, z))
    w, h = int(p[1][0] - p[0][0]), int(p[3][1] - p[0][1])
    if w > 40:
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((w / 2, h * 0.12), "临时通知", font=font(FONT_BLACK, w * 0.15), fill=(30, 30, 34, 240), anchor="mm")
        fs = font(FONT_SANS, w * 0.052)
        lines = ["因近期调整，自即日起：", "1. 会议室暂停对外预约；", "2. 打印请至三楼；",
                 "3. 具体恢复时间另行通知。", "", "特此通知。"]
        for i, t in enumerate(lines):
            d.text((w * 0.1, h * 0.25 + i * h * 0.075), t, font=fs, fill=(55, 55, 60, 225))
        d.text((w * 0.9, h * 0.84), "行政部", font=fs, fill=(55, 55, 60, 225), anchor="rm")
        d.text((w * 0.9, h * 0.9), "2019年3月", font=fs, fill=(55, 55, 60, 225), anchor="rm")
        c.rgba_image(img, p[0][0], p[0][1])
    # tape pieces (one peeling)
    tw = c.px(0.07, z)
    tape = C(235, 225, 190)
    for (q, ang) in [(p[0], -0.6), (p[1], 0.6)]:
        c.ellipse(q[0], q[1], tw, tw * 0.28, tape, rot=ang, alpha=0.6)


def draw_cabinet(c, bags=0):
    x0, x1, yt, yb, z0, z1 = -2.45, -1.55, 0.45, 1.3, 5.45, 6.0
    wood_f, wood_t, wood_s = C(120, 100, 80), C(150, 128, 104), C(96, 80, 64)
    c.box(x0, x1, yt, yb, z0, z1, wood_t, wood_f, wood_s)
    # drawer seams and knobs (lower drawers)
    for yy in [0.76, 1.03]:
        c.line3((x0 + 0.02, yy, z0 - 0.001), (x1 - 0.02, yy, z0 - 0.001), 0.006, C(50, 40, 32))
    for yy in [0.9, 1.16]:
        kx, ky = c.P((x0 + x1) / 2, yy, z0 - 0.002)
        r = c.px(0.018, z0)
        c.ellipse(kx, ky, r, r, C(200, 190, 170))
    # pulled-out top drawer
    dz0 = 5.05
    c.box(x0 + 0.04, x1 - 0.04, 0.50, 0.74, dz0, z0, C(40, 30, 24), C(128, 106, 84), C(100, 84, 66))
    ins = 0.025
    c.poly3([(x0 + 0.04 + ins, 0.50, dz0 + ins), (x1 - 0.04 - ins, 0.50, dz0 + ins),
             (x1 - 0.04 - ins, 0.50, z0), (x0 + 0.04 + ins, 0.50, z0)], C(25, 20, 18))
    kx, ky = c.P((x0 + x1) / 2, 0.62, dz0 - 0.002)
    r = c.px(0.018, dz0)
    c.ellipse(kx, ky, r * 1.4, r * 0.8, C(200, 190, 170))
    if bags >= 1:
        kx, ky = c.P((x0 + x1) / 2, 0.62, dz0 - 0.01)
        hang_bag(c, kx, ky, dz0 - 0.01, 0.34, seed=1)
    if bags >= 2:
        fx, fy = c.P(-1.28, RY_FLOOR, 4.9)
        hang_bag(c, fx, fy - c.px(0.46, 4.9), 4.9, 0.32, seed=2, handles_up=True)


def hang_bag(c, ax, ay, z, size_m, seed=1, handles_up=False):
    """A white plastic bag stuffed with other plastic bags, hung from (ax, ay)."""
    S = int(c.px(size_m, z))
    if S < 10:
        return
    rng = np.random.default_rng(seed)
    Wd, Hd = int(S * 1.2), int(S * 1.45)
    img = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = Wd / 2
    top = S * 0.38
    # handles (two loops tied into a knot at the hook)
    lw = max(2, int(S * 0.045))
    d.line([(cx - S * 0.18, top + S * 0.05), (cx - S * 0.05, S * 0.06), (cx, S * 0.03)], fill=(232, 232, 226, 245), width=lw)
    d.line([(cx + S * 0.18, top + S * 0.05), (cx + S * 0.05, S * 0.06), (cx, S * 0.03)], fill=(222, 222, 216, 245), width=lw)
    d.ellipse([cx - S * 0.06, S * 0.0, cx + S * 0.06, S * 0.09], fill=(214, 214, 208, 255))
    # bulging body
    body = []
    for t in np.linspace(0, 2 * np.pi, 90):
        r = 1 + 0.035 * np.sin(t * 7 + seed) + 0.02 * np.sin(t * 13)
        x = cx + np.cos(t) * S * 0.5 * r
        y = top + S * 0.55 + np.sin(t) * S * 0.52 * r * (0.85 if np.sin(t) < 0 else 1.0)
        body.append((x, y))
    d.polygon(body, fill=(236, 236, 230, 245))
    # other bags showing through / poking out of the opening (blended layers)
    def over(fn):
        nonlocal img, d
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        fn(ImageDraw.Draw(lay))
        img = Image.alpha_composite(img, lay)
        d = ImageDraw.Draw(img)
    for (ox, oy, rw, rh, col) in [(-0.2, 0.45, 0.22, 0.16, (220, 120, 105, 70)), (0.18, 0.62, 0.24, 0.18, (150, 175, 215, 60)),
                                  (0.0, 0.8, 0.28, 0.16, (250, 250, 248, 110)), (-0.12, 0.98, 0.2, 0.12, (200, 200, 196, 70))]:
        over(lambda dd: dd.ellipse([cx + (ox - rw) * S, top + (oy - rh) * S, cx + (ox + rw) * S, top + (oy + rh) * S], fill=col))
    over(lambda dd: dd.polygon([(cx - S * 0.22, top + S * 0.08), (cx - S * 0.3, top - S * 0.08), (cx - S * 0.12, top + S * 0.02)],
                               fill=(210, 90, 80, 235)))
    over(lambda dd: dd.polygon([(cx + S * 0.08, top + S * 0.06), (cx + S * 0.2, top - S * 0.1), (cx + S * 0.26, top + S * 0.06)],
                               fill=(244, 244, 240, 245)))
    # crinkle lines + rim
    for _ in range(14):
        x = cx + rng.uniform(-0.38, 0.38) * S
        y = top + rng.uniform(0.15, 0.95) * S
        d.line([(x, y), (x + rng.uniform(-0.08, 0.08) * S, y + rng.uniform(0.06, 0.16) * S)],
               fill=(170, 170, 170, 255), width=max(1, int(S * 0.008)))
    d.arc([cx - S * 0.36, top - S * 0.05, cx + S * 0.36, top + S * 0.18], 180, 360, fill=(250, 250, 248, 200),
          width=max(1, int(S * 0.02)))
    c.rgba_image(img, ax - Wd / 2, ay - S * 0.03)
    c.rgba_image(img, ax - Wd / 2, ay - S * 0.03, layer="E", alpha=0.10)


def draw_door(c):
    x = RX - 0.002
    z0, z1, yt = 4.95, 5.85, -0.75
    c.poly3([(x, yt - 0.06, z0 - 0.06), (x, yt - 0.06, z1 + 0.06), (x, RY_FLOOR, z1 + 0.06), (x, RY_FLOOR, z0 - 0.06)],
            C(130, 125, 120))
    c.poly3([(x, yt, z0), (x, yt, z1), (x, RY_FLOOR, z1), (x, RY_FLOOR, z0)], 0,
            grad=(C(92, 74, 60), C(70, 56, 46), "h"))
    kx, ky = c.P(x, 0.25, z0 + 0.1)
    r = c.px(0.025, z0)
    c.ellipse(kx, ky, r * 0.6, r, C(210, 190, 150))


def draw_box(c):
    x0, x1, yt, yb, z0, z1 = 0.95, 1.55, 0.84, 1.3, 4.40, 4.95
    c.floor_shadow([(x0, yt, z0), (x1, yt, z0), (x1, yt, z1), (x0, yt, z1)])
    card_t, card_f, card_s = C(196, 152, 104), C(170, 128, 86), C(140, 104, 70)
    c.box(x0, x1, yt, yb, z0, z1, card_t, card_f, card_s)
    xm = (x0 + x1) / 2
    # flap seam + tape strip on top, running down the front
    tw = 0.05
    c.poly3([(xm - tw, yt, z0), (xm + tw, yt, z0), (xm + tw, yt, z1), (xm - tw, yt, z1)], C(214, 186, 140))
    c.line3((xm, yt - 0.001, z0), (xm, yt - 0.001, z1), 0.004, C(110, 80, 50), alpha=0.6)
    c.poly3([(xm - tw, yt, z0), (xm + tw, yt, z0), (xm + tw, yt + 0.14, z0), (xm - tw, yt + 0.14, z0)],
            C(200, 170, 124))
    # marker label on the front face
    p = c.PP([(x0, yt, z0), (x1, yt, z0), (x1, yb, z0), (x0, yb, z0)])
    w, h = int(p[1][0] - p[0][0]), int(p[3][1] - p[0][1])
    if w > 40:
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((w * 0.5, h * 0.55), "先放着", font=font(FONT_BLACK, w * 0.2), fill=(28, 22, 20, 220), anchor="mm")
        d.text((w * 0.5, h * 0.8), "过两天拆", font=font(FONT_BOLD, w * 0.09), fill=(28, 22, 20, 200), anchor="mm")
        img = img.rotate(2, resample=Image.BICUBIC)
        c.rgba_image(img, p[0][0], p[0][1])
    # dust on top
    cx, cy = c.P(xm, yt, (z0 + z1) / 2)
    c.ellipse(cx, cy, c.px(0.25, 4.5), c.px(0.08, 4.5), C(220, 210, 190), alpha=0.18, blur=c.px(0.05, 4.5))


def draw_chair(c):
    x0, x1, z0, z1 = 1.25, 1.75, 3.0, 3.45
    ys, th, yback = 0.85, 0.045, 0.30
    wood_t, wood_f, wood_s = C(110, 80, 58), C(92, 66, 48), C(70, 50, 36)
    lw = 0.04
    c.floor_shadow([(x0, ys, z0), (x1, ys, z0), (x1, ys, z1), (x0, ys, z1), (x0, yback, z1), (x1, yback, z1)])
    # back legs + backrest posts (go up to yback)
    for xx in (x0, x1 - lw):
        c.box(xx, xx + lw, yback, RY_FLOOR, z1 - lw, z1, wood_t, wood_f, wood_s)
    c.box(x0, x1, yback, yback + 0.07, z1 - lw, z1, wood_t, wood_f, wood_s)
    for i in range(3):
        xx = x0 + 0.12 + i * 0.12
        c.box(xx, xx + 0.03, yback + 0.07, ys, z1 - lw * 0.8, z1 - lw * 0.2, wood_t, wood_f, wood_s)
    # seat
    c.box(x0, x1, ys, ys + th, z0, z1, wood_t, wood_f, wood_s)
    # front legs
    for xx in (x0, x1 - lw):
        c.box(xx, xx + lw, ys + th, RY_FLOOR, z0, z0 + lw, wood_t, wood_f, wood_s)
    # pile of clothes
    zc = 3.2
    def B(x, y, z, rx, ry, col, rot=0.0, a=1.0):
        px, py = c.P(x, y, z)
        c.ellipse(px, py, c.px(rx, z), c.px(ry, z), col, rot=rot, alpha=a)
    denim, rust, gray, cream, green, navy = (C(64, 82, 115), C(150, 78, 58), C(128, 128, 134),
                                             C(198, 186, 160), C(64, 92, 76), C(40, 44, 64))
    # draped over backrest
    c.poly3([(x0 + 0.02, yback + 0.02, z1 - 0.01), (x1 - 0.08, yback - 0.01, z1 - 0.01),
             (x1 - 0.05, yback + 0.42, z1 - 0.05), (x0 + 0.1, yback + 0.36, z1 - 0.05)], gray)
    c.poly3([(x1 - 0.12, yback + 0.03, z1 - 0.02), (x1 + 0.03, yback + 0.05, z1 - 0.02),
             (x1 + 0.06, yback + 0.62, z1 - 0.03), (x1 - 0.03, yback + 0.6, z1 - 0.03)], rust)
    B(1.42, yback + 0.03, z1 - 0.02, 0.17, 0.05, gray)
    # heap on the seat
    B(1.50, ys - 0.06, zc, 0.27, 0.09, navy)
    B(1.40, ys - 0.12, zc - 0.02, 0.17, 0.08, denim, 0.2)
    B(1.60, ys - 0.13, zc - 0.05, 0.16, 0.07, cream, -0.25)
    B(1.48, ys - 0.20, zc, 0.15, 0.065, green, 0.1)
    B(1.56, ys - 0.25, zc - 0.03, 0.10, 0.05, rust, -0.4)
    B(1.44, ys - 0.27, zc - 0.02, 0.08, 0.04, cream, 0.5)
    # sleeve / trouser leg hanging from the front edge
    c.poly3([(1.30, ys - 0.05, z0 - 0.01), (1.40, ys - 0.06, z0 - 0.01), (1.38, ys + 0.38, z0 - 0.03),
             (1.31, ys + 0.37, z0 - 0.03)], denim)
    c.poly3([(1.58, ys - 0.07, z0 - 0.02), (1.66, ys - 0.07, z0 - 0.02), (1.70, ys + 0.22, z0 - 0.04),
             (1.63, ys + 0.24, z0 - 0.04)], cream)
    # a t-shirt that slipped onto the floor


def draw_table(c, flower=False):
    x0, x1, z0, z1 = -0.62, 0.62, 2.60, 3.20
    yt, th = 0.55, 0.04
    wood_t, wood_f, wood_s = C(104, 78, 58), C(80, 58, 42), C(64, 46, 34)
    lw, ins = 0.05, 0.04
    c.floor_shadow([(x0, yt, z0), (x1, yt, z0), (x1, yt, z1), (x0, yt, z1)])
    # back legs
    for xx in (x0 + ins, x1 - ins - lw):
        c.box(xx, xx + lw, yt + th, RY_FLOOR, z1 - ins - lw, z1 - ins, wood_t, wood_f, wood_s)
    # front-left leg
    c.box(x0 + ins, x0 + ins + lw, yt + th, RY_FLOOR, z0 + ins, z0 + ins + lw, wood_t, wood_f, wood_s)
    # folded paper under the front-right leg
    lx0 = x1 - ins - lw
    layers = [(0.000, C(214, 210, 198)), (0.006, C(236, 233, 222)), (0.012, C(206, 202, 190)),
              (0.018, C(240, 238, 228)), (0.024, C(220, 216, 204))]
    for i, (dy, col) in enumerate(layers):
        ox = 0.006 * ((i % 2) * 2 - 1)
        c.box(lx0 - 0.045 + ox, lx0 + lw + 0.04 + ox, RY_FLOOR - dy - 0.006, RY_FLOOR - dy,
              z0 + ins - 0.05, z0 + ins + lw + 0.04, col, col * 0.86, col * 0.78)
    paper_top = RY_FLOOR - layers[-1][0] - 0.006
    c.box(lx0, lx0 + lw, yt + th, paper_top, z0 + ins, z0 + ins + lw, wood_t, wood_f, wood_s)
    # apron + top
    c.box(x0 + ins, x1 - ins, yt + th, yt + th + 0.06, z0 + ins, z0 + ins + 0.01, wood_t, wood_f * 0.9, wood_s)
    c.box(x0, x1, yt, yt + th, z0, z1, wood_t, wood_f, wood_s)
    # wood grain on top
    for i in range(6):
        zz = z0 + 0.05 + i * 0.1
        c.line3((x0 + 0.03, yt - 0.0005, zz), (x1 - 0.03, yt - 0.0005, zz), 0.0015, C(70, 52, 38), alpha=0.4)

    # ---- remote control with tape ----
    rx0, rx1, rz0, rz1, rh = -0.48, -0.08, 2.70, 2.80, 0.03
    ry0 = yt - rh
    c.box(rx0, rx1, ry0, yt, rz0, rz1, C(42, 42, 46), C(26, 26, 28), C(20, 20, 22))
    # buttons
    for i in range(6):
        for j in range(2):
            bx = rx0 + 0.05 + i * 0.035
            bz = rz0 + 0.03 + j * 0.04
            px, py = c.P(bx, ry0 - 0.001, bz)
            r = c.px(0.008, bz)
            col = C(190, 60, 50) if (i == 0 and j == 0) else C(110, 110, 116)
            c.ellipse(px, py, r, r * 0.45, col)
    # broken back-cover gap
    c.line3((rx1 - 0.09, ry0 - 0.001, rz0), (rx1 - 0.085, ry0 - 0.001, rz1), 0.002, C(5, 5, 5))
    # tape strips (wrap top + front)
    tape = C(232, 214, 168)
    for (tx, tw) in [(-0.165, 0.045), (-0.135, 0.04)]:
        c.poly3([(tx, ry0 - 0.0015, rz0 - 0.002), (tx + tw, ry0 - 0.0015, rz0 - 0.002),
                 (tx + tw + 0.004, ry0 - 0.0015, rz1 + 0.002), (tx + 0.004, ry0 - 0.0015, rz1 + 0.002)],
                tape, alpha=0.78)
        c.poly3([(tx, ry0 - 0.0015, rz0 - 0.002), (tx + tw, ry0 - 0.0015, rz0 - 0.002),
                 (tx + tw, yt, rz0 - 0.002), (tx, yt, rz0 - 0.002)], tape * 0.82, alpha=0.78)
    c.line3((-0.15, ry0 - 0.002, rz0 + 0.01), (-0.14, ry0 - 0.002, rz1 - 0.01), 0.0015, C(255, 245, 220), alpha=0.6)

    # ---- phone propped up, screen glowing ----
    pz = 3.05
    px0, px1, py0, py1 = 0.07, 0.215, 0.29, 0.545
    c.poly3([(px0 + 0.015, py1, pz + 0.01), (px1 - 0.015, py1, pz + 0.01), (px1, yt, pz + 0.07), (px0, yt, pz + 0.07)],
            C(30, 30, 30))  # stand
    p = c.PP([(px0, py0, pz), (px1, py0, pz), (px1, py1, pz), (px0, py1, pz)])
    c.poly(p, C(14, 14, 16))
    w, h = int(p[1][0] - p[0][0]), int(p[3][1] - p[0][1])
    if w > 12:
        b = max(1, int(w * 0.05))
        scr = phone_screen(w - 2 * b, h - 2 * b)
        c.rgba_image(scr, p[0][0] + b, p[0][1] + b, layer="AE", emissive_gain=0.9)
    gx, gy = c.P((px0 + px1) / 2, yt, pz - 0.1)
    c.ellipse(gx, gy, c.px(0.35, pz), c.px(0.12, pz), np.array([0.25, 0.30, 0.42], np.float32), layer="L",
              blur=c.px(0.08, pz))

    if flower:
        draw_cup_flower(c, 0.38, 2.92, yt)


def phone_screen(w, h):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    arr = np.zeros((h, w, 3), np.float32)
    t = np.linspace(0, 1, h)[:, None]
    arr[:] = (np.array([24, 32, 58]) * (1 - t) + np.array([52, 38, 70]) * t)[:, None, :][:, 0, None, :]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    fs = font(FONT_SANS, w * 0.072)
    d.text((w * 0.08, h * 0.035), "10:24", font=font(FONT_SANS, w * 0.07), fill=(230, 230, 240, 255))
    names = ["照片备份", "新建文件夹", "未命名", "临时", "新建文件夹(2)", "下载", "文档", "新建文件夹(3)", "备用"]
    cols, rows = 3, 3
    cw, ch = w / cols, h * 0.24
    for i, n in enumerate(names):
        cx = cw * (i % cols + 0.5)
        cy = h * 0.2 + ch * (i // cols)
        iw, ih = cw * 0.55, cw * 0.42
        hl = (n == "新建文件夹(3)")
        if hl:
            d.rounded_rectangle([cx - cw * 0.46, cy - ih * 0.7, cx + cw * 0.46, cy + ih * 1.25],
                                radius=cw * 0.08, fill=(255, 220, 140, 60), outline=(255, 214, 120, 255),
                                width=max(1, int(w * 0.008)))
        d.rounded_rectangle([cx - iw / 2, cy - ih / 2 - ih * 0.12, cx - iw * 0.05, cy - ih / 2 + ih * 0.1],
                            radius=ih * 0.08, fill=(240, 186, 80, 255))
        d.rounded_rectangle([cx - iw / 2, cy - ih / 2, cx + iw / 2, cy + ih / 2], radius=ih * 0.1,
                            fill=(252, 204, 98, 255))
        fnt = fs if len(n) <= 5 else font(FONT_SANS, w * 0.058)
        d.text((cx, cy + ih * 0.85), n, font=fnt, fill=(255, 240, 200, 255) if hl else (225, 228, 238, 255),
               anchor="mm")
    return img


def draw_cup_flower(c, x, z, yt):
    # paper cup (frustum) with a little flower: the "temporary" pot
    h, rt, rb = 0.11, 0.05, 0.037
    top = yt - h
    pt = np.array(c.P(x, top, z)); pb = np.array(c.P(x, yt, z))
    rtp, rbp = c.px(rt, z), c.px(rb, z)
    et, eb = rtp * 0.28, rbp * 0.28
    body = c.ellipse_pts(pb[0], pb[1], rbp, eb, 0, 30, 0, np.pi) + c.ellipse_pts(pt[0], pt[1], rtp, et, 0, 30, np.pi, 0)
    c.poly(body, 0, grad=(C(236, 232, 222), C(200, 196, 186), "h"))
    band = c.ellipse_pts(pb[0], pb[1] - (pb[1] - pt[1]) * 0.45, (rbp + rtp) / 2, eb, 0, 30, 0, np.pi) + \
        c.ellipse_pts(pt[0], pt[1] + (pb[1] - pt[1]) * 0.35, rtp * 0.97, et, 0, 30, np.pi, 0)
    c.poly(band, C(150, 70, 60), alpha=0.8)
    c.ellipse(pt[0], pt[1], rtp, et, C(60, 46, 36))
    c.ellipse(pt[0], pt[1], rtp * 0.9, et * 0.8, C(72, 54, 40))
    # stem + leaves
    sh = 0.17
    c.line3((x, top, z), (x + 0.004, top - sh, z), 0.004, C(70, 140, 70))
    lx, ly = c.P(x, top - 0.06, z)
    c.ellipse(lx - c.px(0.025, z), ly, c.px(0.028, z), c.px(0.009, z), C(80, 155, 80), rot=-0.5)
    c.ellipse(lx + c.px(0.022, z), ly - c.px(0.03, z), c.px(0.024, z), c.px(0.008, z), C(80, 155, 80), rot=0.6)
    fx, fy = c.P(x + 0.004, top - sh, z)
    r = c.px(0.016, z)
    pink = C(250, 140, 120)
    for i in range(5):
        a = i * 2 * np.pi / 5 - np.pi / 2
        c.ellipse(fx + np.cos(a) * r * 0.9, fy + np.sin(a) * r * 0.9, r * 0.8, r * 0.8, pink)
    c.ellipse(fx, fy, r * 0.55, r * 0.55, C(255, 210, 120))
    c.ellipse(fx, fy, r * 3.2, r * 3.2, np.array([0.5, 0.18, 0.12], np.float32), layer="E", blur=r * 1.5)


def draw_tag(c):
    x, z, ytop = -0.12, 4.0, -0.32
    gx, gy = c.P(x, ytop + 0.22, z)
    c.ellipse(gx, gy, c.px(0.3, z), c.px(0.4, z), WARM * 0.9, layer="L", blur=c.px(0.1, z))
    c.line3((x, RY_TOP, z), (x, ytop, z), 0.004, C(170, 160, 140), alpha=0.9)
    w_m, h_m = 0.30, 0.46
    wpx, hpx = int(c.px(w_m, z)), int(c.px(h_m, z))
    if wpx < 8:
        return
    pad = int(wpx * 0.25)
    img = Image.new("RGBA", (wpx + 2 * pad, hpx + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cut = wpx * 0.28
    shape = [(pad + cut, pad), (pad + wpx - cut, pad), (pad + wpx, pad + cut), (pad + wpx, pad + hpx),
             (pad, pad + hpx), (pad, pad + cut)]
    d.polygon(shape, fill=(196, 160, 108, 255))
    d.polygon([(pad + wpx * 0.06, pad + hpx * 0.97), (pad + wpx * 0.94, pad + hpx * 0.97),
               (pad + wpx * 0.94, pad + hpx * 0.93), (pad + wpx * 0.06, pad + hpx * 0.93)], fill=(170, 136, 90, 255))
    hr = wpx * 0.07
    d.ellipse([pad + wpx / 2 - hr * 1.6, pad + cut * 0.55 - hr * 1.6, pad + wpx / 2 + hr * 1.6, pad + cut * 0.55 + hr * 1.6],
              fill=(226, 206, 160, 255))
    d.ellipse([pad + wpx / 2 - hr, pad + cut * 0.55 - hr, pad + wpx / 2 + hr, pad + cut * 0.55 + hr], fill=(0, 0, 0, 0))
    d.text((pad + wpx / 2, pad + hpx * 0.42), "临", font=font(FONT_BLACK, wpx * 0.5), fill=(60, 36, 24, 245), anchor="mm")
    d.text((pad + wpx / 2, pad + hpx * 0.72), "时", font=font(FONT_BLACK, wpx * 0.5), fill=(60, 36, 24, 245), anchor="mm")
    img = img.rotate(-6, resample=Image.BICUBIC, center=(pad + wpx / 2, pad + cut * 0.55))
    ax, ay = c.P(x, ytop, z)
    c.rgba_image(img, ax - pad - wpx / 2, ay - pad - cut * 0.55 + c.px(0.0, z))


# =====================================================================

def build(shot):
    k = shot.get("k", 1.0)
    c = Canvas(k, shot.get("target"))
    draw_room(c)
    draw_picture(c)
    draw_sticky(c)
    draw_notice(c)
    draw_door(c)
    draw_cabinet(c, bags=shot.get("bags", 1))
    draw_box(c)
    if shot.get("tag"):
        draw_tag(c)
    draw_chair(c)
    draw_table(c, flower=shot.get("flower", False))
    return light(c)


def light(c):
    F = c.F
    zb = RZ_BACK
    x0, x1, y0, y1 = WIN
    # --- beam volume & floor patch ---
    win3 = [(x0, y0, zb + 0.2), (x1, y0, zb + 0.2), (x1, y1, zb + 0.2), (x0, y1, zb + 0.2)]
    patch3 = []
    for (x, y, z) in win3:
        t = (RY_FLOOR - y) / LIGHT_D[1]
        zz = z + LIGHT_D[2] * t
        if zz < 0.35:  # clip to a near plane in the air
            t = (z - 0.35) / -LIGHT_D[2]
            patch3.append((x + LIGHT_D[0] * t, y + LIGHT_D[1] * t, 0.35))
        else:
            patch3.append((x + LIGHT_D[0] * t, RY_FLOOR, zz))
    floor_pts = []
    for (x, y, z) in patch3:
        floor_pts.append((x, RY_FLOOR, z) if y >= RY_FLOOR - 1e-6 else None)
    # floor patch = region of floor lit: quad between floor hits of bottom & top window edge
    def floor_hit(x, y, z):
        t = (RY_FLOOR - y) / LIGHT_D[1]
        return (x + LIGHT_D[0] * t, RY_FLOOR, max(0.35, z + LIGHT_D[2] * t))
    fp = [floor_hit(*win3[3]), floor_hit(*win3[2]), floor_hit(*win3[1]), floor_hit(*win3[0])]
    patch = np.zeros((H, W), np.float32)
    r = c._mask(c.PP(fp), blur=0.012 * F)
    if r:
        patch[r[1]:r[3], r[0]:r[2]] = r[4]
    patch *= (1.0 - 0.88 * c.S)
    patch = cv2.GaussianBlur(patch, (0, 0), max(1.0, 0.004 * F))
    # beam hull in screen space
    sp = np.array(c.PP(win3) + c.PP(patch3), np.float32)
    hull = cv2.convexHull(sp).reshape(-1, 2)
    beam = np.zeros((H, W), np.float32)
    r = c._mask(hull, blur=0.02 * F)
    if r:
        beam[r[1]:r[3], r[0]:r[2]] = r[4]
    wc = np.array(c.P((x0 + x1) / 2, (y0 + y1) / 2, zb))
    dist = np.sqrt((_XX - wc[0]) ** 2 + (_YY - wc[1]) ** 2)
    sig = F * 1.15 / zb
    glow = np.exp(-(dist ** 2) / (2 * sig ** 2))
    falloff = np.exp(-dist / (F * 0.55))
    # soft streaks in the beam (god rays)
    ang = np.arctan2(_YY - wc[1], _XX - wc[0])
    streak = 0.88 + 0.12 * np.sin(ang * 23.0) * np.sin(ang * 7.0 + 1.3)
    beam_d = beam * (0.25 + 0.75 * falloff)

    amb = np.array([0.20, 0.205, 0.24], np.float32)
    Lm = amb + glow[..., None] * WARM * 0.55
    Lm = Lm + patch[..., None] * WARM * 1.7
    Lm = Lm + bigblur(patch, 0.10 * F)[..., None] * WARM * 0.30
    Lm = Lm + beam_d[..., None] * WARM * 0.55
    Lm = Lm + c.L
    img = c.A * Lm + c.E
    out = 1.0 - np.exp(-img * 1.15)
    bright = np.maximum(out - 0.62, 0)
    out = out + bigblur(bright, 0.012 * F) * 0.55 + bigblur(bright, 0.06 * F) * 0.45
    out = cv2.GaussianBlur(out, (0, 0), 0.55)
    haze = (beam_d * streak)[..., None] * WARM * 0.26
    # dark version (lights off) for title fade-in
    dark_img = c.A * (amb * 0.55)
    dark = 1.0 - np.exp(-dark_img * 1.15)
    return dict(base=out.astype(np.float32), haze=haze.astype(np.float32),
                density=beam_d.astype(np.float32), dark=dark.astype(np.float32), F=F)


if __name__ == "__main__":
    import sys, time
    sys.path.insert(0, HERE)
    from scenes import shot_of
    names = sys.argv[1:] or ["wide"]
    os.makedirs(os.path.join(HERE, "build", "preview"), exist_ok=True)
    for n in names:
        t = time.time()
        s = build(shot_of(n))
        img = np.clip(s["base"] + s["haze"], 0, 1)
        im = Image.fromarray((img * 255).astype(np.uint8)).resize((1280, 720), Image.LANCZOS)
        im.save(os.path.join(HERE, "build", "preview", f"{n}.jpg"), quality=88)
        print(n, f"{time.time() - t:.1f}s")
