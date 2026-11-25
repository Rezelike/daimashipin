"""Timeline and V-2-IS engine mechanics.

Everything that moves is driven by one crank angle theta(t) (degrees), integrated from the engine speed omega(t).
The picture and the bang sounds both read theta, so every bang you hear is a cylinder firing on screen.

Beat grid: 128 BPM, 14 bars = 26.25 s. At the slowest slow-motion the crank turns 60 degrees per beat, so one of
the 12 cylinders fires on every beat (a V12 four-stroke fires every 720 / 12 = 60 degrees). Each later x2 doubles
the rate (2, 4, 8, 16 bangs per beat), which keeps every bang on the grid.
"""
import numpy as np

BPM = 128
BEAT = 60.0 / BPM                 # 0.46875 s
BAR = 4 * BEAT                    # 1.875 s
FPS = 30
NBARS = 14
DUR = NBARS * BAR                 # 26.25 s
NF = int(round(DUR * FPS))        # 788 frames
SR = 48000

RPM_REAL = 2000.0                 # V-2-IS: 520 hp at 2000 rpm
KMH_REAL = 35.0                   # ISU-152 top road speed (ru.wikipedia comparison table)
W_REAL = RPM_REAL * 6.0           # deg/s
W0 = 60.0 / BEAT                  # deg/s at the slowest slow-mo: 60 deg per beat
FACTOR0 = W_REAL / W0             # 93.75 -> shown as 1/94

ROLES = ["hook", "zoom", "slow", "stroke", "stroke", "stroke", "order", "cams", "fire", "volume",
         "floor", "real", "turns", "end"]
LADDER = {2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 7: 4, 8: 8, 9: 16, 10: 32}   # bar -> speed multiple of W0


def bar_beat(t):
    bi = int(min(NBARS - 1, max(0, t // BAR)))
    return bi, (t - bi * BAR) / BEAT


def omega(t):
    """engine speed in deg/s (scalar or array)"""
    t = np.asarray(t, float)
    bi = np.clip((t // BAR).astype(int), 0, NBARS - 1)
    lb = (t - bi * BAR) / BEAT
    w = np.full(t.shape, W_REAL)
    u = np.clip((lb - 2) / 2, 0, 1)                      # bar 1: real speed, then slow down over beats 2-4
    w = np.where(bi == 1, np.exp(np.log(W_REAL) * (1 - u) + np.log(W0) * u), w)
    for b, k in LADDER.items():
        if b != 10:
            w = np.where(bi == b, W0 * k, w)
    w = np.where(bi == 10, np.exp(np.log(W0 * 32) * (1 - u) + np.log(W_REAL) * u), w)   # floor it: beats 2-4
    return w if w.ndim else float(w)


_TG = np.arange(int(round(DUR * SR)) + 2) / SR
_W = omega(_TG)
_TH = np.concatenate([[0.0], np.cumsum((_W[1:] + _W[:-1]) * 0.5 / SR)])
_i2 = int(round(2 * BAR * SR))
_TH += (120.0 - _TH[_i2]) % 720.0     # bar 2 starts at theta = 120 (L5 fires); bar 3 starts at 360 (L1 intake)


def theta(t):
    return np.interp(t, _TG, _TH)


# ----------------------------------------------------------------------------- firing order (T-34-85 manual)
ORDER = ["L1", "R6", "L5", "R2", "L3", "R4", "L6", "R1", "L2", "R5", "L4", "R3"]   # fires at 0, 60, ... 660 deg
FIRE = {c: 60.0 * i for i, c in enumerate(ORDER)}
PIN_PHASE = {1: 0.0, 6: 0.0, 2: 240.0, 5: 240.0, 3: 120.0, 4: 120.0}               # crank throw of pin n


def psi(th, cyl):
    """position in the 720-degree cycle: 0 = fires (TDC), 0-180 power, 180-360 exhaust, 360-540 intake, 540-720
    compression"""
    return (th - FIRE[cyl]) % 720.0


def stroke_of(ps):
    return ("power", "exhaust", "intake", "compression")[int(ps // 180) % 4]


def bang_events(t0, t1):
    """[(time, cylinder)] for every firing between t0 and t1"""
    i0, i1 = int(max(0, np.floor(t0 * SR))), int(min(len(_TG) - 1, np.ceil(t1 * SR)))
    th = _TH[i0:i1 + 1]
    k = np.floor(th / 60.0)
    idx = np.nonzero(np.diff(k) > 0)[0]
    out = []
    for i in idx:
        for m in range(int(k[i]) + 1, int(k[i + 1]) + 1):
            target = m * 60.0
            a, b = th[i], th[i + 1]
            frac = (target - a) / (b - a) if b > a else 0.0
            tt = (i0 + i + frac) / SR
            if t0 <= tt < t1:
                out.append((tt, ORDER[m % 12]))
    return out


# ----------------------------------------------------------------------------- crank, master + articulated rods
# Real V-2: bore 150 mm, stroke 180 mm (master-rod bank) / 186.7 mm (articulated bank), 60 degree V.
# Rod lengths and the knuckle position are illustrative values chosen so the strokes come out at 180 / 186.7 mm.
R_CRANK, L_MASTER, E_KNUCKLE, KAPPA, L_ART = 90.0, 315.0, 50.0, 73.0, 265.0
H_CROWN = 100.0                     # piston pin to crown
DECK = 508.0                        # crank centre to cylinder-head face along the bank axis
SQ3 = np.sqrt(3.0) / 2
AX = {"L": np.array([-0.5, SQ3]), "R": np.array([0.5, SQ3])}     # bank axes in the (y, z) end view
INWARD = {"L": np.array([SQ3, 0.5]), "R": np.array([-SQ3, 0.5])}  # unit normals pointing into the V


def _perp(a):
    return np.array([a[1], -a[0]])


def pair(th, n):
    """crank pin P, knuckle pin K and piston pins QL / QR of cylinder pair n, plus each piston's distance from the
    crank centre along its bank axis (mm)"""
    eta = np.radians(-30.0 + th + PIN_PHASE[n])
    P = R_CRANK * np.array([np.sin(eta), np.cos(eta)])
    aL, aR = AX["L"], AX["R"]
    sL = P @ aL + np.sqrt(L_MASTER ** 2 - (P @ _perp(aL)) ** 2)
    QL = sL * aL
    m = (QL - P) / L_MASTER
    c, s = np.cos(np.radians(-KAPPA)), np.sin(np.radians(-KAPPA))
    K = P + E_KNUCKLE * np.array([c * m[0] - s * m[1], s * m[0] + c * m[1]])
    sR = K @ aR + np.sqrt(L_ART ** 2 - (K @ _perp(aR)) ** 2)
    return dict(P=P, K=K, QL=QL, QR=sR * aR, sL=sL, sR=sR)


def crown(th, cyl):
    """distance of the piston crown from the crank centre along its bank axis (mm); TDC = 505"""
    p = pair(th, int(cyl[1]))
    return (p["sL"] if cyl[0] == "L" else p["sR"]) + H_CROWN


def valve_lift(ps, kind):
    """0..1; intake open 340-580 deg, exhaust open 140-380 deg of the cycle (generic timing, overlap at 360)"""
    a, b = (340.0, 580.0) if kind == "in" else (140.0, 380.0)
    if a <= ps <= b:
        return float(np.sin(np.pi * (ps - a) / (b - a)))
    return 0.0


def cam_angle(ps, kind):
    """lobe angle of this cylinder's cam (deg), 0 = nose pointing at the valve"""
    return ((ps - (460.0 if kind == "in" else 260.0)) / 2.0) % 360.0


def hud_numbers(t):
    w = omega(t)
    return w / 6.0, KMH_REAL * w / W_REAL, W_REAL / w      # rpm, km/h, slow-motion factor
