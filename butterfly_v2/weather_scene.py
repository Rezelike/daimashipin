"""30.4-42.4 s: a thread of incense smoke -> the camera pulls back -> a typhoon on the globe ->
two forecast tracks that agree for a week, then fork.

Smoke: a streakline in a simple flow that gets more turbulent with height (illustration).
Globe: orthographic view, coastlines from Natural Earth 110m (public domain).
Tracks: one base path; how far the two forecasts fork is driven by the gap between the two runs
of the Lorenz equations (lorenz.py: 0.506127 vs 0.506), so they agree until those runs part.
Distances in the HUD are great-circle distances between the two track heads on this globe.
"""
import json
import math
import os
import urllib.request

import numpy as np
import skia
from scipy.ndimage import uniform_filter1d

import film_common as fc
import lorenz as lz
from theme import W, H, FPS, paint, clamp01, smooth, ease_out, ease_in_out, lerp

LEN = 12.0
ROOT = os.path.dirname(os.path.abspath(__file__))
LAND_URL = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson'
LAND_PATH = os.path.join(ROOT, 'assets', 'geo', 'ne_110m_land.geojson')

# ---------------------------------------------------------------- timeline (seconds into the scene)
U_CAP1, U_CAP2 = 2.5, 9.6        # the second line lands as the two tracks fork (about day 9-10)
U_ZOOM = (3.0, 7.4)
U_SMOKE_OUT = (3.4, 5.3)
U_CLOUD_IN = (3.2, 5.4)
U_GLOBE_IN = (4.9, 6.9)
U_TRACK = (7.1, 11.1)
DAYS = 15

# ---------------------------------------------------------------- geometry
K0 = 16.0                       # camera zoom at the start (cloud blobs are 16x bigger)
TIP = np.array([540.0, 1480.0])  # incense tip, smoke frame
ANCHOR = np.array([540.0, 790.0])  # smoke-frame point that turns into the typhoon's eye
GC = np.array([540.0, 1000.0])
GR = 590.0
EARTH_KM = 6371.0
LAT0, LON0 = 24.0, 128.0
CYC = (16.0, 134.0)             # Philippine Sea
WIDE_VIEW = ((540, 1000), 0.58)  # 16:9: incense bowl to smoke top, and later the whole globe, fit the height


def project(lat, lon):
    """Orthographic projection -> (x, y, visible)."""
    p, l = np.radians(lat), np.radians(lon)
    p0, l0 = math.radians(LAT0), math.radians(LON0)
    cosc = math.sin(p0) * np.sin(p) + math.cos(p0) * np.cos(p) * np.cos(l - l0)
    x = np.cos(p) * np.sin(l - l0)
    y = math.cos(p0) * np.sin(p) - math.sin(p0) * np.cos(p) * np.cos(l - l0)
    return GC[0] + GR * x, GC[1] - GR * y, cosc > 0


def haversine_km(a, b):
    (la1, lo1), (la2, lo2) = np.radians(a), np.radians(b)
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * EARTH_KM * math.asin(math.sqrt(h))


def load_land():
    if not os.path.exists(LAND_PATH):
        os.makedirs(os.path.dirname(LAND_PATH), exist_ok=True)
        urllib.request.urlretrieve(LAND_URL, LAND_PATH + '.part')
        os.replace(LAND_PATH + '.part', LAND_PATH)
    rings = []
    for feat in json.load(open(LAND_PATH))['features']:
        g = feat['geometry']
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        for poly in polys:
            rings.append(np.array(poly[0]))
    return rings


def densify(ring, step=1.0):
    out = [ring[0]]
    for a, b in zip(ring[:-1], ring[1:]):
        n = max(1, int(np.ceil(np.max(np.abs(b - a)) / step)))
        for k in range(1, n + 1):
            out.append(a + (b - a) * k / n)
    return np.array(out)


def polyline_paths(xs, ys, vis):
    """Split a projected line wherever it goes behind the globe."""
    path = skia.Path()
    pen = False
    for x, y, v in zip(xs.tolist(), ys.tolist(), vis.tolist()):
        if v:
            if pen:
                path.lineTo(x, y)
            else:
                path.moveTo(x, y)
                pen = True
        else:
            pen = False
    return path


# ================================================================ forecast tracks
def base_heading(d):
    """Compass heading (deg) of the base track: west-north-west, then recurving north-east."""
    return 298 + 100 * smooth((d - 1.6) / 5.6)


def base_speed(d):
    return 300 + 240 * smooth((d - 5.0) / 8.0)          # km per day


def build_tracks(dd=0.02):
    """Two tracks [(lat, lon) per step], forking by the smoothed gap between the Lorenz runs."""
    t0 = 0.5
    a, b = lz.runs(t0 + DAYS + 1.0)
    gap = np.linalg.norm(a - b, axis=1)
    env = np.maximum.accumulate(uniform_filter1d(gap, int(1.0 / lz.DT), mode='nearest'))
    fork = np.clip(env / 14.0, 0, 1) ** 0.75
    fork = uniform_filter1d(fork, int(1.6 / lz.DT), mode='nearest')    # no sudden kinks in the tracks
    days = np.arange(0, DAYS + 1e-9, dd)
    out, forks = [], []
    for sign in (1, -1):
        lat, lon = CYC
        pts = [(lat, lon)]
        for d in days[1:]:
            i = min(int((t0 + d) / lz.DT), len(fork) - 1)
            hdg = math.radians(base_heading(d) + sign * 26 * fork[i])
            km = base_speed(d) * dd
            lat += km * math.cos(hdg) / 111.2
            lon += km * math.sin(hdg) / (111.2 * math.cos(math.radians(lat)))
            pts.append((lat, lon))
        out.append(np.array(pts))
    forks = np.array([fork[min(int((t0 + d) / lz.DT), len(fork) - 1)] for d in days])
    return days, out, forks


# ================================================================ smoke
def flow(x, y, t, ph):
    """Straight near the tip; curling higher up, but held together around the centre line."""
    h = TIP[1] - y
    turb = np.clip((h - 230) / 520, 0, 1) ** 1.4
    vx = turb * (120 * np.sin(0.021 * y + 1.4 * t + ph) + 75 * np.sin(0.043 * y - 2.3 * t + 2 * ph)
                 + 40 * np.sin(0.011 * y + 0.6 * t)) - 0.9 * turb * (x - TIP[0])
    vy = -(160 - 50 * turb) + turb * 85 * np.sin(0.026 * (x - TIP[0]) + 1.8 * t + ph)
    return vx, vy


def simulate_smoke(n_frames, warm=6.0, strands=((-1.4, 0.0), (0.0, 2.1), (1.4, 4.2))):
    dt = 1.0 / FPS
    frames = [[] for _ in strands]
    state = [np.zeros((0, 3)) for _ in strands]          # x, y, age (oldest first)
    for fi in range(-int(warm * FPS), n_frames):
        t = fi * dt
        for k, (dx, ph) in enumerate(strands):
            # two particles per frame, so the thread stays smooth where it stretches
            p = np.vstack([state[k], [[TIP[0] + dx, TIP[1] - 1.4, dt / 2], [TIP[0] + dx, TIP[1], 0.0]]])
            for _ in range(3):
                vx, vy = flow(p[:, 0], p[:, 1], t, ph)
                p[:, 0] += vx * dt / 3
                p[:, 1] += vy * dt / 3
            p[:, 2] += dt
            p = p[(TIP[1] - p[:, 1] < 1220) & (p[:, 2] < 9.5)]
            state[k] = p
            if fi >= 0:
                frames[k].append(p.copy())
    return frames


# ================================================================ scene
class WeatherScene:
    LEN = LEN

    def __init__(self):
        self.cyc = np.array(project(*CYC)[:2], dtype=float)
        self.smoke = simulate_smoke(int((U_SMOKE_OUT[1] + 0.1) * FPS))
        self.build_globe()
        self.build_cyclone()
        self.days, tracks, self.forks = build_tracks()
        self.tracks_ll = tracks
        self.tracks_xy = []
        for tr in tracks:
            x, y, _ = project(tr[:, 0], tr[:, 1])
            self.tracks_xy.append(np.stack([x, y], 1))
        self.km = np.array([haversine_km(a, b) for a, b in zip(*tracks)])
        # latitude of each head, used by the score
        self.day_lat = [[tr[int(round(d / (self.days[1] - self.days[0])))][0] for d in range(DAYS + 1)]
                        for tr in tracks]

    # ------------------------------------------------------------ static globe paths (world = final screen)
    def build_globe(self):
        rings = [densify(r) for r in load_land()]
        self.coast = skia.Path()
        self.land = skia.Path()
        for r in rings:
            x, y, v = project(r[:, 1], r[:, 0])
            if not v.any():
                continue
            self.coast.addPath(polyline_paths(x, y, v))
            # fill: push hidden points onto the limb so the shape closes cleanly
            dx, dy = x - GC[0], y - GC[1]
            rr = np.hypot(dx, dy) + 1e-9
            x2 = np.where(v, x, GC[0] + dx / rr * GR)
            y2 = np.where(v, y, GC[1] + dy / rr * GR)
            pts = [skia.Point(a, b) for a, b in zip(x2.tolist(), y2.tolist())]
            self.land.addPoly(pts, True)
        self.grat = skia.Path()
        for lat in range(-75, 90, 15):
            lon = np.arange(-180, 181, 2.0)
            self.grat.addPath(polyline_paths(*project(np.full_like(lon, lat), lon)))
        for lon in range(-180, 180, 15):
            lat = np.arange(-80, 81, 2.0)
            self.grat.addPath(polyline_paths(*project(lat, np.full_like(lat, lon))))
        disc = skia.Path()
        disc.addCircle(GC[0], GC[1], GR)
        self.disc = disc

    def draw_globe(self, c, th, a, k):
        if a <= 0:
            return
        mul = skia.BlendMode.kMultiply
        c.drawPath(self.disc, paint(th.ink, a * 0.035, blend=mul))
        c.save()
        c.clipPath(self.disc, doAntiAlias=True)
        c.drawPath(self.grat, paint(th.hair, a * 0.16, stroke=1.0 / k))
        c.drawPath(self.land, paint(th.ink, a * 0.06, blend=mul))
        # engraved hatching on land
        c.save()
        c.clipPath(self.land, doAntiAlias=True)
        hp = paint(th.ink, a * 0.22, stroke=0.9 / k, blend=mul)
        x0, y0 = GC[0] - GR, GC[1] - GR
        for s in np.arange(0, 4 * GR, 7.0):
            c.drawLine(x0 + s, y0, x0 + s - 2 * GR, y0 + 2 * GR, hp)
        c.restore()
        c.drawPath(self.coast, paint(th.ink, a * 0.55, stroke=1.2 / k))
        c.restore()
        c.drawCircle(GC[0], GC[1], GR, paint(th.ink, a * 0.85, stroke=2.0 / k))
        c.drawCircle(GC[0], GC[1], GR + 20, paint(th.hair, a * 0.3, stroke=1.0 / k))

    # ------------------------------------------------------------ typhoon (soft ink blobs around the eye)
    def build_cyclone(self):
        rng = np.random.default_rng(21)
        r, th_, size, alpha = [], [], [], []

        def add(rr, tt, ss, aa):
            r.append(rr), th_.append(tt), size.append(ss), alpha.append(aa)

        for _ in range(170):                                   # eyewall
            add(abs(rng.normal(11, 2.4)), rng.uniform(0, 2 * math.pi), rng.uniform(4, 7), rng.uniform(0.16, 0.28))
        for arm in range(3):                                   # spiral bands
            for _ in range(230):
                s = rng.uniform(0, 1) ** 0.85
                rr = 14 + 96 * s
                tt = arm * 2 * math.pi / 3 + 1.9 * math.log(rr / 14) + rng.normal(0, 0.15 + 0.12 * s)
                add(rr + rng.normal(0, 2.5), tt, lerp(6, 15, s) * rng.uniform(0.7, 1.2),
                    lerp(0.24, 0.07, s) * rng.uniform(0.6, 1.0))
        for _ in range(140):                                   # loose cloud around it
            rr = rng.uniform(25, 135)
            add(rr, rng.uniform(0, 2 * math.pi), rng.uniform(5, 13), rng.uniform(0.03, 0.08))
        self.cr, self.ct = np.array(r), np.array(th_)
        self.cs, self.ca = np.array(size), np.array(alpha)

    def draw_cyclone(self, c, th, u, a, k, target):
        if a <= 0:
            return
        omega = -0.45 * np.sqrt(14 / np.maximum(self.cr, 8))     # counter-clockwise, faster near the eye
        ang = self.ct + omega * u
        # screen positions directly (cheaper culling than going through the canvas matrix)
        xs = target[0] + k * self.cr * np.cos(ang)
        ys = target[1] + k * self.cr * np.sin(ang)
        fc.draw_blobs(c, fc.blob(th.ink), xs, ys, k * self.cs, self.ca * a / 255)

    # ------------------------------------------------------------ smoke frame
    def draw_smoke(self, c, th, u, a):
        if a <= 0:
            return
        f = min(int(u * FPS), len(self.smoke[0]) - 1)
        mul = skia.BlendMode.kMultiply
        img = fc.blob(th.ink)
        for k, frames in enumerate(self.smoke):
            p = frames[f]
            if len(p) < 3:
                continue
            h = TIP[1] - p[:, 1]
            # soft wash where it has gone turbulent, spreading and thinning as it rises
            # sample by arc length, so places where the thread bunches up don't turn into dark spots
            arc = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(p[:, :2], axis=0).T))])
            _, first = np.unique((arc / 16).astype(int), return_index=True)
            sel = first[h[first] > 300]
            kk = np.clip((h[sel] - 300) / 900, 0, 1)
            top = 1 - np.clip((h[sel] - 1000) / 220, 0, 1)
            fc.draw_blobs(c, img, p[sel, 0], p[sel, 1], 6 + 38 * kk, a / 255 * 0.06 * (0.4 + kk) * top, blend=mul)
            # the thread itself, newest (at the tip) to oldest; it dissolves into the wash higher up
            pts = p[::-1]
            hh = h[::-1]
            lst = pts[:, :2].tolist()
            for j0 in range(0, len(pts) - 1, 12):
                j1 = min(j0 + 12, len(pts) - 1)
                hm = float(hh[j0:j1 + 1].mean())
                q = clamp01(hm / 1050)
                fade = (1 - q) ** 1.3
                if fade < 0.02:
                    continue
                path = skia.Path.Polygon([skia.Point(*xy) for xy in lst[j0:j1 + 1]], False)
                c.drawPath(path, paint(th.ink, a * 0.6 * fade, stroke=1.2 + 1.4 * q, blend=mul))
        # incense stick and holder
        c.drawLine(TIP[0], TIP[1] + 4, TIP[0], 1712, paint((112, 82, 62), a, stroke=3.2))
        bowl = skia.Path()
        bowl.addArc(skia.Rect.MakeLTRB(462, 1680, 618, 1764), 0, 180)
        c.drawPath(bowl, paint(th.ink, a * 0.85, stroke=1.6))
        c.drawLine(462, 1722, 618, 1722, paint(th.ink, a * 0.85, stroke=1.6))
        c.drawCircle(TIP[0], TIP[1], 4.0, paint(th.a, a))
        c.drawCircle(TIP[0], TIP[1], 9, paint(th.a, a * 0.18, blur=5))

    # ------------------------------------------------------------ tracks
    def track_day(self, u):
        return DAYS * clamp01((u - U_TRACK[0]) / (U_TRACK[1] - U_TRACK[0]))

    def draw_tracks(self, c, th, u, k):
        d = self.track_day(u)
        if d <= 0:
            return
        n = int(d / (self.days[1] - self.days[0]))
        mul = None if th.glow else skia.BlendMode.kMultiply
        for kk in (1, 0):
            rgb = th.a if kk == 0 else th.b
            xy = self.tracks_xy[kk][:n + 1]
            if len(xy) >= 2:
                path = skia.Path.Polygon([skia.Point(*q) for q in xy.tolist()], False)
                c.drawPath(path, paint(rgb, 220, stroke=(2.6 if kk == 0 else 2.0) / k, blend=mul))
            step = int(round(1 / (self.days[1] - self.days[0])))
            for di in range(1, int(d) + 1):
                x, y = self.tracks_xy[kk][di * step]
                if kk == 0:
                    c.drawCircle(x, y, 3.6 / k, paint(rgb, 230))
                else:
                    c.drawCircle(x, y, 5.2 / k, paint(rgb, 230, stroke=1.4 / k))
        for kk in (0, 1):
            x, y = self.tracks_xy[kk][n]
            if kk == 0:
                c.drawCircle(x, y, 7.5 / k, paint(th.a, 240))
            else:
                c.drawCircle(x, y, 10 / k, paint(th.b, 255, stroke=1.8 / k))

    # ------------------------------------------------------------ frame
    def camera(self, u):
        e = ease_in_out((u - U_ZOOM[0]) / (U_ZOOM[1] - U_ZOOM[0]))
        k = math.exp(math.log(K0) * (1 - e))
        target = ANCHOR + (self.cyc - ANCHOR) * e
        return k, target, e

    def draw(self, c, th, u):
        th.draw_background(c)
        k, target, e = self.camera(u)
        # smoke, shrinking towards the anchor as the camera pulls back
        a_smoke = 255 * smooth(u / 0.4) * (1 - smooth((u - U_SMOKE_OUT[0]) / (U_SMOKE_OUT[1] - U_SMOKE_OUT[0])))
        a_globe = 255 * smooth((u - U_GLOBE_IN[0]) / (U_GLOBE_IN[1] - U_GLOBE_IN[0]))
        a_cloud = 255 * smooth((u - U_CLOUD_IN[0]) / (U_CLOUD_IN[1] - U_CLOUD_IN[0]))
        with fc.visual(c, *WIDE_VIEW):
            if a_smoke > 0:
                s = k / K0
                c.save()
                c.translate(target[0], target[1])
                c.scale(s, s)
                c.translate(-ANCHOR[0], -ANCHOR[1])
                self.draw_smoke(c, th, u, a_smoke)
                c.restore()
            # globe + typhoon + tracks, in world coordinates
            c.save()
            c.translate(target[0], target[1])
            c.scale(k, k)
            c.translate(-self.cyc[0], -self.cyc[1])
            self.draw_globe(c, th, a_globe, k)
            c.restore()
            self.draw_cyclone(c, th, u, a_cloud, k, target)
            c.save()
            c.translate(target[0], target[1])
            c.scale(k, k)
            c.translate(-self.cyc[0], -self.cyc[1])
            self.draw_tracks(c, th, u, k)
            c.restore()
        # text
        fc.caption(c, th, '天气也是如此。', u, U_CAP1, LEN + 1, line=0)
        fc.caption(c, th, '超过两周，没人算得准。', u, U_CAP2, LEN + 1, line=1)
        a_t = 255 * smooth((u - (U_TRACK[0] - 0.2)) / 0.5)
        fc.sub(c, th, '两次计算，初始数据只差 0.000127', a_t, 1668)
        d = self.track_day(u)
        i = min(int(d / (self.days[1] - self.days[0])), len(self.km) - 1)
        fc.hud(c, th, a_t, '预报', f'第 {int(d):2d} 天', '两条路径相距', f'{self.km[i]:5.0f} km')
        fc.legend(c, th, a_t, '第一次计算', '第二次计算')
        fc.dip(c, th, u, LEN)


if __name__ == '__main__':
    sc = WeatherScene()
    step = int(round(1 / (sc.days[1] - sc.days[0])))
    print('cyclone at', sc.cyc)
    for d in range(0, DAYS + 1):
        a, b = sc.tracks_ll[0][d * step], sc.tracks_ll[1][d * step]
        print(f'day {d:2d}: A {a[0]:5.1f}N {a[1]:6.1f}E  B {b[0]:5.1f}N {b[1]:6.1f}E  apart {sc.km[d * step]:6.0f} km'
              f'  fork {sc.forks[d * step]:.2f}')
