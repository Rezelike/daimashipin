"""A ball bouncing between round posts (exact, event-driven, no friction).

Used to show WHY tiny differences grow: every bounce off a round surface
multiplies the angle error. Units are pixels (we treat 1 px = 1 mm on screen).
"""
import math
import numpy as np


def _hit_circle(p, v, c, rad):
    """Time until point p moving with v hits circle (c, rad) from outside, or None."""
    d = p - c
    b = np.dot(d, v)
    if b >= 0:
        return None
    a = np.dot(v, v)
    disc = b * b - a * (np.dot(d, d) - rad * rad)
    if disc < 0:
        return None
    t = (-b - math.sqrt(disc)) / a
    return t if t > 1e-12 else None


def simulate(start, angle_deg, speed, pegs, peg_r, ball_r, box, duration, fps):
    """box = (x0, y0, x1, y1). Returns (positions[F,2], bounces[(t, kind, idx)])."""
    p = np.array(start, dtype=float)
    a = math.radians(angle_deg)
    v = np.array([math.cos(a), math.sin(a)]) * speed
    pegs = np.asarray(pegs, dtype=float)
    x0, y0, x1, y1 = box
    t, frames, bounces = 0.0, [], []
    n_frames = int(duration * fps)
    next_frame = 0
    while next_frame < n_frames:
        # earliest event
        best, kind, idx = math.inf, None, None
        for i, c in enumerate(pegs):
            h = _hit_circle(p, v, c, peg_r + ball_r)
            if h is not None and h < best:
                best, kind, idx = h, 'peg', i
        for ax, lo, hi in ((0, x0 + ball_r, x1 - ball_r), (1, y0 + ball_r, y1 - ball_r)):
            if v[ax] < 0:
                h = (lo - p[ax]) / v[ax]
            elif v[ax] > 0:
                h = (hi - p[ax]) / v[ax]
            else:
                continue
            if 1e-12 < h < best:
                best, kind, idx = h, 'wall', ax
        # emit frames until that event
        while next_frame < n_frames and next_frame / fps <= t + best:
            frames.append(p + v * (next_frame / fps - t))
            next_frame += 1
        p = p + v * best
        t += best
        if kind == 'peg':
            nrm = p - pegs[idx]
            nrm /= np.linalg.norm(nrm)
            v = v - 2 * np.dot(v, nrm) * nrm
        else:
            v[idx] = -v[idx]
        bounces.append((t, kind, idx))
    return np.array(frames), bounces


def gap_report(pa, pb, bounces_a, fps, max_gap=60.0):
    """For each peg bounce of run A: (t, gap_after_mm, factor_vs_previous)."""
    gap = np.linalg.norm(pa - pb, axis=1)
    out, prev = [], None
    for (t, kind, _i) in bounces_a:
        if kind != 'peg':
            continue
        f = min(int(t * fps) + 6, len(gap) - 1)  # a few frames after the bounce
        g = float(gap[f])
        out.append((t, g, None if prev is None else g / prev))
        prev = g
        if g > max_gap:
            break
    return out


if __name__ == '__main__':
    pegs = [(260, 330), (540, 250), (820, 330), (400, 560), (680, 560), (260, 790), (540, 870), (820, 790)]
    box = (0, 0, 1080 - 180, 1080)
    pegs = [(x - 90, y) for x, y in pegs]
    for ang in (-78, -72, -66, -101, -108):
        A, ba = simulate((450, 1040), ang, 330, pegs, 62, 18, box, 10, 60)
        B, bb = simulate((450, 1040), ang + 0.001, 330, pegs, 62, 18, box, 10, 60)
        rep = gap_report(A, B, ba, 60)
        print(ang, [(round(t, 2), round(g, 4), None if f is None else round(f, 1)) for t, g, f in rep])
