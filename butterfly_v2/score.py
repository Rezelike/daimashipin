"""Sound for the full film.

0-12.4 s is exactly the opening's score from music.py (same notes, same levels).
Later scenes keep the same instruments (Salamander piano, FluidR3 strings and cello),
the same key (A minor) and tempo (72 bpm), and the same reverb.

Pendulums (12.4-24.4 s): the melody is *played by the pendulums*. On every eighth note
each lower bob's height picks a note from the A-minor pentatonic scale - first break on
the left, second on the right. While the two runs coincide you hear one melody in
unison; when they separate, the melody splits into two.
"""
import numpy as np

import music
import pendulum_scene as ps
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


SCENE_AUDIO = {
    'PendulumScene': (pendulum_music, pendulum_sfx),
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
    write_wav(path, master(total))
    print('audio written', path, flush=True)
    return path
