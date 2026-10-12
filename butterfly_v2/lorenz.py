"""The Lorenz system (sigma=10, rho=28, beta=8/3), RK4.

Two runs, as in Lorenz's 1961 story: he restarted a weather run from a printout and typed
0.506 instead of 0.506127. Here that is the starting x of the two runs; y and z are identical.
"""
import numpy as np

SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0
DT = 0.002
STARTS = ((0.506127, 1.0, 20.0), (0.506, 1.0, 20.0))
_cache = {}


def simulate(start, t_end, dt=DT):
    n = int(round(t_end / dt)) + 1
    out = np.empty((n, 3))
    x, y, z = start

    def f(x, y, z):
        return SIGMA * (y - x), x * (RHO - z) - y, x * y - BETA * z

    for i in range(n):
        out[i] = (x, y, z)
        k1 = f(x, y, z)
        k2 = f(x + dt / 2 * k1[0], y + dt / 2 * k1[1], z + dt / 2 * k1[2])
        k3 = f(x + dt / 2 * k2[0], y + dt / 2 * k2[1], z + dt / 2 * k2[2])
        k4 = f(x + dt * k3[0], y + dt * k3[1], z + dt * k3[2])
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        z += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
    return out


def runs(t_end=30.0):
    """The two runs (first = 0.506127, second = 0.506), sampled every DT."""
    if t_end not in _cache:
        _cache[t_end] = [simulate(s, t_end) for s in STARTS]
    return _cache[t_end]


if __name__ == '__main__':
    a, b = runs()
    d = np.linalg.norm(a - b, axis=1)
    for thr in (0.01, 0.1, 0.5, 2, 10):
        i = int(np.argmax(d > thr))
        print(f'gap > {thr:5}: t = {i * DT:5.2f}')
