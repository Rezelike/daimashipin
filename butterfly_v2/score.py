"""Sound for the full film.

0-12.4 s is exactly the opening's score from music.py (same notes, same levels).
Later scenes keep the same instruments (Salamander piano, FluidR3 strings and cello),
the same key (A minor) and tempo (72 bpm), and the same reverb.

Pendulums (12.4-24.4 s): the melody is *played by the pendulums*. On every eighth note
each lower bob's height picks a note from the A-minor pentatonic scale - first break on
the left, second on the right. While the two runs coincide you hear one melody in
unison; when they separate, the melody splits into two.

The same idea runs through the film: the coin rings a note at every half turn, slowing to
a stop; the two forecast tracks play a note per day from their latitude; the two Lorenz runs
ring a bell each time they change wing. Each pair sounds together, then drifts apart.
The opening's arpeggio returns under the butterfly; the film ends on A minor.
"""
import numpy as np

import coin_scene as cs
import lorenz_scene as ls
import music
import pendulum_scene as ps
import weather_scene as ws
from music import SR, place, pan, piano, chord, lp, hp, reverb, write_wav, PIANO, STR, CELLO  # noqa: F401

BEAT = 60 / 72
EIGHTH = BEAT / 2
PENTA = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]       # A3 C4 D4 E4 G4 A4 C5 D5 E5 G5 A5
rng = np.random.default_rng(17)                           # separate from music.rng, so the opening stays identical


def buf(seconds):
    return np.zeros((int(round(seconds * SR)), 2))


# ============================================================== pendulums
def pendulum_music(sc):
    m = buf(ps.LEN)
    A1, A2, E3, A3, C4, E4, F3, G4 = 33, 45, 52, 57, 60, 64, 53, 67
    # raised and held: low drone, one high note
    place(m, 0.15, chord(CELLO, [A2, E3], ps.U_RELEASE + 1.2, attack=1.0, release=1.0, spread=0.3), 0.28)
    place(m, 0.55, pan(piano(76, 0.30), 0.12), 1.0)
    place(m, 1.05, pan(piano(69, 0.24), -0.1), 1.0)
    # released: the pendulums play
    t = ps.U_RELEASE
    while t < ps.U_DEV[0] + 0.2:
        s = ps.PendulumScene.sample(t)
        grow = (t - ps.U_RELEASE) / (ps.U_DEV[0] - ps.U_RELEASE)
        for k, run in enumerate(sc.runs):
            i = min(int(s), run.n - 1)
            h = -(run.p2[i, 1] - ps.PIVOT[1]) / ps.REACH            # -1 (bottom) .. 1 (top)
            note = PENTA[int(round((h + 1) / 2 * (len(PENTA) - 1)))]
            speed = min(1.0, run.v[i] / 1400)
            vel = 0.2 + 0.08 * speed + 0.06 * grow
            place(m, t, pan(piano(note, vel), -0.5 if k == 0 else 0.5), 0.75)
        t += EIGHTH
    # strings swell as the runs separate, then turn to F at 终点无关
    a_len = ps.U_SECOND - ps.U_RELEASE + 0.6
    place(m, ps.U_RELEASE, chord(STR, [A3, C4, E4], a_len, attack=a_len * 0.8, release=0.6, spread=0.8, seed=40),
          0.45)
    place(m, ps.U_RELEASE, chord(CELLO, [A2], a_len, attack=2.0, release=0.6, seed=41), 0.3)
    f_len = ps.LEN - ps.U_SECOND
    place(m, ps.U_SECOND, chord(STR, [F3, A3, C4, E4, G4], f_len, attack=0.5, release=f_len * 0.55, spread=0.9,
                                seed=42), 0.36)
    place(m, ps.U_SECOND, chord(CELLO, [41, 48], f_len, attack=0.4, release=f_len * 0.6, seed=43), 0.26)
    place(m, ps.U_SECOND + 0.02, pan(piano(A1 - 4, 0.40), -0.1), 1.0)      # deep F
    place(m, ps.U_SECOND + 0.02, pan(piano(41, 0.28), 0.1), 1.0)
    return m


def pendulum_sfx(sc):
    """Very quiet air for each swing: low-passed noise following the lower bob's speed."""
    s = buf(ps.LEN)
    n = len(s)
    u = np.arange(n) / SR
    for k, run in enumerate(sc.runs):
        idx = np.clip(((u - ps.U_RELEASE) * ps.RATE).astype(int), 0, run.n - 1)
        env = np.where(u > ps.U_RELEASE, (run.v[idx] / 1800) ** 2, 0)
        env *= 1 - np.clip((u - ps.U_DEV[0]) / 0.8, 0, 1)
        noise = lp(hp(rng.standard_normal(n), 120), 700)
        place(s, 0, pan(noise * env, -0.4 if k == 0 else 0.4), 0.05)
    return s


# ============================================================== coin
def coin_events():
    """(u, kind) for every half turn (a face square to the camera) and every edge-on moment."""
    us = np.linspace(0, cs.U_PLAY[1], 24000)
    n = np.array([cs.turns(u) for u in us])
    faces, edges = [], []
    for arr, out in ((np.floor(n * 2 + 1e-7), faces), (np.floor(n * 2 + 0.5), edges)):
        idx = np.nonzero(np.diff(arr) > 0)[0] + 1
        out.extend((float(us[i]), int(arr[i])) for i in idx)
    if not faces or faces[-1][0] < cs.U_PLAY[1] - 0.05:
        faces.append((cs.U_PLAY[1], int(round(n[-1] * 2))))
    return faces, edges


def coin_ring():
    """A coin landing on its face: a few inharmonic metal partials."""
    t = np.arange(int(1.8 * SR)) / SR
    x = np.zeros_like(t)
    for ratio, amp, dec in ((1.0, 1.0, 2.6), (2.32, 0.55, 3.6), (4.25, 0.3, 5.0), (6.63, 0.18, 7.0)):
        f = 2350 * ratio
        x += amp * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t * dec)
        x += 0.4 * amp * np.sin(2 * np.pi * (f + 3.1) * t) * np.exp(-t * dec)       # slight beating
    x += 0.3 * hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 90)
    return x / np.max(np.abs(x))


def coin_music(sc):
    m = buf(cs.LEN)
    A2, E3, A3, C4, E4 = 45, 52, 57, 60, 64
    end = cs.U_PLAY[1]
    place(m, 0, chord(STR, [A3, C4, E4], end + 0.2, attack=1.0, release=0.5, spread=0.8, seed=50), 0.30)
    place(m, 0, chord(CELLO, [A2, E3], end + 0.2, attack=1.0, release=0.5, spread=0.3, seed=51), 0.22)
    faces, _ = coin_events()
    for u, half in faces:                       # the coin plays a music box that winds down
        heads = half % 2 == 0
        place(m, u, pan(piano(81 if heads else 76, 0.22 + 0.04 * (u / end)), 0.2 if heads else -0.2), 0.8)
    place(m, end + 0.02, pan(piano(33, 0.40), -0.1), 1.0)
    place(m, end + 0.02, pan(piano(45, 0.30), 0.1), 1.0)
    place(m, cs.U_NOTE + 0.05, pan(piano(72, 0.26), -0.4), 1.0)                 # 38 turns
    place(m, cs.U_NOTE + 0.50, pan(piano(71, 0.24), 0.4), 1.0)                  # 39 turns
    tail = cs.LEN - cs.U_NOTE
    place(m, cs.U_NOTE, chord(STR, [53, A3, C4], tail + 0.3, attack=0.8, release=1.0, spread=0.8, seed=52), 0.24)
    return m


def coin_sfx(sc):
    s = buf(cs.LEN)
    _, edges = coin_events()
    for u, _ in edges:                          # air past the rim each time it turns edge-on
        t = np.arange(int(0.22 * SR)) / SR
        x = lp(hp(rng.standard_normal(len(t)), 300), 1600) * np.sin(np.pi * t / t[-1]) ** 2
        place(s, u - 0.11, pan(x, 0), 0.05)
    place(s, cs.U_PLAY[1], pan(coin_ring(), 0.05), 0.22)
    return s


# ============================================================== weather
def weather_music(sc):
    m = buf(ws.LEN)
    A2, E3, A3, C4, E4, G4 = 45, 52, 57, 60, 64, 67
    # smoke: almost nothing - a drone and three notes
    place(m, 0, chord(CELLO, [A2, E3], ws.U_ZOOM[0] + 2.2, attack=1.2, release=1.4, spread=0.3, seed=60), 0.22)
    for u, note, vel in ((0.45, 76, 0.26), (1.45, 72, 0.24), (2.45, 69, 0.24)):
        place(m, u, pan(piano(note, vel), 0.1), 1.0)
    # pulling back: strings swell, Am -> F
    z0, z1 = ws.U_ZOOM
    place(m, z0 - 0.3, chord(STR, [A3, C4, E4, G4], 2.6, attack=1.8, release=0.8, spread=0.8, seed=61), 0.42)
    place(m, z0 + 2.0, chord(STR, [53, A3, C4, E4], z1 - z0, attack=0.8, release=1.0, spread=0.9, seed=62), 0.42)
    place(m, z0 + 2.0, chord(CELLO, [41, 48], z1 - z0, attack=0.8, release=1.0, seed=63), 0.28)
    place(m, z0 + 2.02, pan(piano(29, 0.36), -0.1), 1.0)
    # the forecast: each track plays a note per day, from its latitude. Same notes while they agree.
    t0, t1 = ws.U_TRACK
    lo, hi = 14.0, 64.0
    for d in range(ws.DAYS + 1):
        u = t0 + (t1 - t0) * d / ws.DAYS
        for k in range(2):
            lat = sc.day_lat[k][d]
            note = PENTA[int(round(np.clip((lat - lo) / (hi - lo), 0, 1) * (len(PENTA) - 1)))]
            place(m, u, pan(piano(note, 0.2 + 0.08 * d / ws.DAYS), -0.5 if k == 0 else 0.5), 0.75)
    place(m, t0 - 0.2, chord(STR, [A3, C4, E4], ws.U_CAP2 - t0 + 0.6, attack=1.0, release=0.6, spread=0.8,
                             seed=64), 0.3)
    # 超过两周: G, which the next scene resolves to A minor
    g_len = ws.LEN - ws.U_CAP2 + 0.4
    place(m, ws.U_CAP2, chord(STR, [55, 59, 62, 67], g_len, attack=0.6, release=1.2, spread=0.9, seed=65), 0.4)
    place(m, ws.U_CAP2, chord(CELLO, [43, 50], g_len, attack=0.6, release=1.2, seed=66), 0.3)
    place(m, ws.U_CAP2 + 0.02, pan(piano(31, 0.38), -0.1), 1.0)
    return m


def weather_sfx(sc):
    """Wind that rises as the camera pulls back into the sky, circling slowly once the typhoon shows."""
    s = buf(ws.LEN)
    n = len(s)
    u = np.arange(n) / SR
    z0, z1 = ws.U_ZOOM
    env = np.clip((u - z0) / 1.5, 0, 1) ** 1.5 * (1 - 0.6 * np.clip((u - z1) / 3.0, 0, 1))
    env *= 1 - np.clip((u - (ws.LEN - 1.0)) / 1.0, 0, 1)
    noise = lp(hp(rng.standard_normal(n), 90), 900)
    sweep = 0.5 + 0.5 * np.sin(2 * np.pi * 0.18 * u)
    place(s, 0, np.stack([noise * env * sweep, noise * env * (1 - sweep)], 1), 0.06)
    return s


# ============================================================== lorenz
LZ_PROG = [  # (bass, arpeggio) - the opening's progression
    (33, [57, 64, 71, 72]),        # Am(add9)
    (29, [53, 57, 64, 72]),        # Fmaj7
    (28, [55, 60, 64, 67]),        # C/E
    (31, [55, 59, 62, 71]),        # G
]


def lorenz_music(sc):
    m = buf(ls.LEN)
    A1, A2, E3, A3, C4, E4, A4, C5, E5 = 33, 45, 52, 57, 60, 64, 69, 72, 76
    arp_end = ls.U_DRAW[1]
    # G -> A minor: the resolution of the last scene
    place(m, 0.05, pan(piano(A1, 0.42), -0.1), 1.0)
    place(m, 0.05, pan(piano(A2, 0.30), 0.1), 1.0)
    place(m, 0.0, chord(CELLO, [A2, E3], arp_end + 0.6, attack=1.5, release=1.0, spread=0.3, seed=70), 0.28)
    # the opening's arpeggio comes back while the butterfly is drawn
    half_bar = 2 * BEAT
    b = 0
    while True:
        tb = 0.6 + b * half_bar
        if tb > arp_end - 0.3:
            break
        bass, arp = LZ_PROG[b % 4]
        grow = min(1.0, tb / 8.5) * (1 - 0.6 * max(0.0, (tb - 9.0) / 2.0))
        place(m, tb, pan(piano(bass + 12, 0.34 + 0.1 * grow, length=half_bar, release=0.8), -0.25), 1.0)
        for j in range(4):
            tn = tb + j * EIGHTH
            if tn < arp_end - 0.15:
                vel = 0.22 + 0.04 * (j == 0) + 0.12 * grow
                place(m, tn, pan(piano(arp[j] + 12 * (j == 3 and b % 2 == 1), vel), 0.1 + 0.08 * j), 1.0)
        # strings follow the harmony
        place(m, tb, chord(STR, [n for n in arp[:3]], half_bar + 0.4, attack=0.6, release=0.6, spread=0.8,
                           seed=80 + b), 0.18 + 0.2 * grow)
        b += 1
    # 蝴蝶效应: everything lands together
    place(m, ls.U_TITLE, pan(piano(21, 0.5), -0.1), 1.0)
    place(m, ls.U_TITLE, pan(piano(A1, 0.45), 0.1), 1.0)
    place(m, ls.U_TITLE, chord(STR, [A3, E4, A4, C5], 3.0, attack=0.25, release=2.2, spread=0.9, seed=90), 0.4)
    # each run rings a bell whenever it changes wing - together at first, then out of step
    for k, events in enumerate(sc.switch_u):
        for u, sign in events:
            if u < arp_end:
                place(m, u, pan(piano(88 if sign > 0 else 81, 0.17), -0.55 if k == 0 else 0.55), 0.7)
    # 世界遵守规则，却拒绝被预测。
    e1, e2 = ls.U_END1, ls.U_END2
    place(m, arp_end - 0.4, chord(STR, [53, A3, C4, E4], e2 - arp_end + 1.6, attack=1.2, release=1.2, spread=0.9,
                                  seed=91), 0.36)
    place(m, arp_end - 0.4, chord(CELLO, [41, 48], e2 - arp_end + 1.6, attack=1.2, release=1.2, seed=92), 0.26)
    place(m, e1 + 0.05, pan(piano(E5, 0.26), 0.2), 1.0)
    place(m, e1 + 0.85, pan(piano(C5, 0.24), 0.1), 1.0)
    place(m, e2 + 0.05, pan(piano(A4, 0.26), -0.05), 1.0)
    place(m, e2 + 0.05, pan(piano(E4, 0.2), -0.2), 1.0)
    final = ls.LEN - e2
    place(m, e2, chord(STR, [A3, C4, E4], final, attack=1.6, release=final * 0.6, spread=0.9, seed=93), 0.32)
    place(m, e2, chord(CELLO, [A2], final, attack=1.6, release=final * 0.6, seed=94), 0.24)
    place(m, 15.0, pan(piano(A1, 0.36), -0.1), 1.0)
    place(m, 15.0, pan(piano(A2, 0.26), 0.1), 1.0)
    place(m, 16.2, pan(piano(81, 0.18), 0.3), 1.0)
    return m


def lorenz_sfx(sc):
    return buf(ls.LEN)


SCENE_AUDIO = {
    'PendulumScene': (pendulum_music, pendulum_sfx),
    'CoinScene': (coin_music, coin_sfx),
    'WeatherScene': (weather_music, weather_sfx),
    'LorenzScene': (lorenz_music, lorenz_sfx),
}


# ============================================================== mix
def master(x, target_peak=0.89, fade=0.8):
    x = x - np.mean(x, axis=0)
    peak = np.max(np.abs(x)) + 1e-9
    x = np.tanh(x / peak * 1.1) / np.tanh(1.1)
    k = len(x) - int(fade * SR)
    x[k:] *= np.linspace(1, 0, len(x) - k)[:, None]
    return x * target_peak


def build(film, path, with_music=True):
    total = buf(film.end + 0.05)
    # ---- opening: same as music.build, minus its own master/fade
    place(total, 0, music.build_sfx(film.opening) * 0.9)
    ref = 1.0
    mus = buf(film.end + 0.05)
    if with_music:
        om = music.build_music()
        ref = np.max(np.abs(om)) + 1e-9
        place(mus, 0, om)
    # ---- later scenes, on the same level reference as the opening
    for t0, scene in film.parts:
        mus_fn, sfx_fn = SCENE_AUDIO[type(scene).__name__]
        place(total, t0, sfx_fn(scene) * 0.9)
        if with_music:
            place(mus, t0, mus_fn(scene))
    if with_music:
        total += mus / ref * 0.8
    total = reverb(total, seconds=2.8, mix=0.3)
    write_wav(path, master(total, fade=1.2))
    print('audio written', path, flush=True)
    return path
