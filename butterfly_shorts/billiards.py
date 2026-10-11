"""Simple but genuine 2D billiards physics (break shot).

Units: metres, seconds. Table playing surface of a 9-ft pool table.
The simulation is deterministic: the ONLY difference between two runs is the
cue angle we pass in, so any divergence on screen is real.
"""
import math
import numpy as np

TABLE_W = 1.78          # length (x)  - compact bar table, balls look bigger on a phone
TABLE_H = 0.89          # width (y)
R = 0.028575            # ball radius
POCKET_R = 0.058        # capture radius around pocket centre
E_BALL = 0.95           # ball-ball restitution
E_CUSH = 0.78           # cushion restitution
DECEL = 0.18            # constant rolling deceleration (m/s^2)
DRAG = 0.06             # extra proportional drag (1/s)

POCKETS = np.array([
    [0, 0], [TABLE_W / 2, -0.015], [TABLE_W, 0],
    [0, TABLE_H], [TABLE_W / 2, TABLE_H + 0.015], [TABLE_W, TABLE_H],
])

# Standard 8-ball-ish rack order (0 = cue ball)
RACK_ORDER = [1, 9, 2, 10, 8, 3, 11, 7, 14, 4, 5, 13, 15, 6, 12]


def initial_positions():
    pos = [[TABLE_W * 0.25, TABLE_H / 2]]  # cue ball on the head spot
    apex_x = TABLE_W * 0.72
    gap = 2 * R + 2e-5                     # an almost-touching rack
    k = 0
    for row in range(5):
        for j in range(row + 1):
            x = apex_x + row * gap * math.sqrt(3) / 2
            y = TABLE_H / 2 + (j - row / 2) * gap
            pos.append([x, y])
            k += 1
    return np.array(pos, dtype=float)


def simulate(angle_deg, speed=9.0, duration=7.0, fps=60, substeps=60):
    """Return (frames_pos [F,N,2], frames_alive [F,N], events) for a break.

    events: list of (time, kind, strength) with kind in {'cue','ball','cushion','pocket'}
    """
    pos = initial_positions()
    n = len(pos)
    vel = np.zeros_like(pos)
    a = math.radians(angle_deg)
    vel[0] = [speed * math.cos(a), speed * math.sin(a)]
    alive = np.ones(n, dtype=bool)
    dt = 1.0 / (fps * substeps)
    frames_pos, frames_alive, events = [], [], [(0.0, 'cue', 1.0)]
    t = 0.0
    for _f in range(int(duration * fps)):
        frames_pos.append(pos.copy())
        frames_alive.append(alive.copy())
        for _s in range(substeps):
            t += dt
            # friction
            sp = np.linalg.norm(vel, axis=1)
            moving = sp > 1e-9
            dec = np.minimum(sp, (DECEL + DRAG * sp) * dt)
            vel[moving] -= (vel[moving] / sp[moving, None]) * dec[moving, None]
            pos[alive] += vel[alive] * dt
            idx = np.nonzero(alive)[0]
            # ball-ball collisions
            p = pos[idx]
            d = p[:, None, :] - p[None, :, :]
            dist2 = (d ** 2).sum(-1)
            ii, jj = np.nonzero(np.triu(dist2 < (2 * R) ** 2, 1))
            for a_, b_ in zip(ii, jj):
                i, j = idx[a_], idx[b_]
                dv = pos[i] - pos[j]
                dist = math.hypot(*dv)
                if dist < 1e-12:
                    continue
                nrm = dv / dist
                rel = np.dot(vel[i] - vel[j], nrm)
                overlap = 2 * R - dist
                pos[i] += nrm * overlap / 2
                pos[j] -= nrm * overlap / 2
                if rel < 0:
                    imp = -(1 + E_BALL) * rel / 2
                    vel[i] += imp * nrm
                    vel[j] -= imp * nrm
                    if imp > 0.05:
                        events.append((t, 'ball', imp))
            # cushions
            for i in idx:
                for ax, hi in ((0, TABLE_W), (1, TABLE_H)):
                    if pos[i, ax] < R and vel[i, ax] < 0:
                        pos[i, ax] = R
                        if abs(vel[i, ax]) > 0.05:
                            events.append((t, 'cushion', abs(vel[i, ax])))
                        vel[i, ax] = -vel[i, ax] * E_CUSH
                    elif pos[i, ax] > hi - R and vel[i, ax] > 0:
                        pos[i, ax] = hi - R
                        if abs(vel[i, ax]) > 0.05:
                            events.append((t, 'cushion', abs(vel[i, ax])))
                        vel[i, ax] = -vel[i, ax] * E_CUSH
            # pockets
            for i in idx:
                if np.min(np.linalg.norm(POCKETS - pos[i], axis=1)) < POCKET_R:
                    alive[i] = False
                    vel[i] = 0
                    events.append((t, 'pocket', 1.0))
    return np.array(frames_pos), np.array(frames_alive), events


if __name__ == '__main__':
    import time
    t0 = time.time()
    pa, aa, ea = simulate(0.0)
    pb, ab, eb = simulate(0.001)
    print('sim time', time.time() - t0)
    for f in (30, 60, 120, 240, 419):
        dmax = np.max(np.linalg.norm(pa[f] - pb[f], axis=1))
        print(f'frame {f}: max ball separation {dmax*100:.2f} cm')
    print('pocketed A:', [i for i in range(16) if not aa[-1][i]])
    print('pocketed B:', [i for i in range(16) if not ab[-1][i]])
    print('final speed check', len(ea), len(eb))
