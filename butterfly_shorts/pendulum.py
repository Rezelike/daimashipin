"""Double pendulum (equal masses, equal arm lengths), RK4 integration."""
import math
import numpy as np

G = 9.81
L = 1.0


def deriv(s):
    t1, t2, w1, w2 = s
    d = t1 - t2
    den = 3 - math.cos(2 * d)
    a1 = (-3 * G * math.sin(t1) - G * math.sin(t1 - 2 * t2)
          - 2 * math.sin(d) * (w2 * w2 * L + w1 * w1 * L * math.cos(d))) / (L * den)
    a2 = (2 * math.sin(d) * (2 * w1 * w1 * L + 2 * G * math.cos(t1)
          + w2 * w2 * L * math.cos(d))) / (L * den)
    return np.array([w1, w2, a1, a2])


def simulate(t1_deg, t2_deg, duration, fps=60, substeps=40):
    s = np.array([math.radians(t1_deg), math.radians(t2_deg), 0.0, 0.0])
    h = 1.0 / (fps * substeps)
    out = []
    for _ in range(int(duration * fps)):
        out.append(s.copy())
        for _ in range(substeps):
            k1 = deriv(s)
            k2 = deriv(s + h / 2 * k1)
            k3 = deriv(s + h / 2 * k2)
            k4 = deriv(s + h * k3)
            s = s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return np.array(out)


def bob_positions(states):
    t1, t2 = states[:, 0], states[:, 1]
    x1, y1 = L * np.sin(t1), L * np.cos(t1)
    x2, y2 = x1 + L * np.sin(t2), y1 + L * np.cos(t2)
    return np.stack([x1, y1], 1), np.stack([x2, y2], 1)


if __name__ == '__main__':
    for a0 in (120, 135, 150):
        A = simulate(a0, a0, 14)
        B = simulate(a0 + 0.001, a0, 14)
        _, pa = bob_positions(A)
        _, pb = bob_positions(B)
        d = np.linalg.norm(pa - pb, axis=1)
        first = next((i / 60 for i, v in enumerate(d) if v > 0.05), None)
        print(a0, 'visible split at t =', first, 's; sep@each 2s', [round(float(d[i]), 2) for i in range(0, 840, 120)])
