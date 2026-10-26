"""Shared timeline: music and video are both locked to this bar grid,
so every scene cut lands exactly on a downbeat."""

BPM = 136
BEAT = 60.0 / BPM          # seconds per beat
BAR = 4 * BEAT             # 4/4
FPS = 30
W, H = 1920, 1080

# (scene id, start bar, length in bars)
SCENES = [
    ("hook",     0,   8),
    ("title",    8,   4),
    ("who",      12, 12),
    ("core",     24,  8),
    ("step1",    32, 12),
    ("step2",    44, 12),
    ("step3",    56, 12),
    ("step4",    68, 12),
    ("example",  80, 20),
    ("mistakes", 100, 12),
    ("recap",    112, 8),
    ("cta",      120, 10),   # last 2 bars = final chord ringing out
]
TOTAL_BARS = SCENES[-1][1] + SCENES[-1][2]
DURATION = TOTAL_BARS * BAR + 1.5   # small tail for reverb / fade


def bar_t(bar: float) -> float:
    return bar * BAR


def scene_span(sid):
    for s, b, n in SCENES:
        if s == sid:
            return bar_t(b), bar_t(b + n)
    raise KeyError(sid)
