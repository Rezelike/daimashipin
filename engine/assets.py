"""Free assets, fetched from GitHub only (the sandbox can't reach most other hosts).

* Instrument samples: VSCO-2 Community Edition, CC0-1.0  https://github.com/sgossner/VSCO-2-CE
  (Upright Piano sampled by Simon Dalzell / Ivy Audio)
* Icons: Lucide, ISC  https://github.com/lucide-icons/lucide  (browse names at lucide.dev/icons)

    python -m engine.assets            # samples + default icons
    python -m engine.assets brain zap  # extra icons
Icons used in scenes are also downloaded on demand by engine.core.icon().
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from . import ASSETS

VSCO_DIR = os.path.join(ASSETS, "vsco")
ICON_DIR = os.path.join(ASSETS, "icons")
VSCO_REPO = "sgossner/VSCO-2-CE"
VSCO_PATTERNS = [
    r"^Keys/Upright Piano/Player_dyn[23]_rr1_\d+\.wav$",
    r"^Strings/Solo Violin/(Arco Vib|spic|Pizz)/.*\.wav$",
    r"^Strings/Cello Section/spic/.*\.wav$",
    r"^VSCO 1 Percussion/drums/other/Bongos/.*\.wav$",
    r"^Percussion/Timpani/Timpani3_Hit_v4_rr1_Sum\.wav$",
]
DEFAULT_ICONS = [
    "brain", "book-open", "notebook-pen", "baby", "message-circle", "search", "lightbulb", "repeat",
    "x", "check", "heart", "star", "bookmark", "user-plus", "trophy", "atom", "zap", "triangle-alert",
    "terminal", "sparkles", "pencil", "circle-question-mark", "snowflake", "trending-up", "quote",
    "target", "file-text", "rotate-cw", "eye", "list-checks", "graduation-cap", "badge-check",
    "clock", "calendar-days", "timer", "flame", "chart-line", "hourglass", "layers", "arrow-right",
]


def _get(url, out):
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return "cached"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = f"{out}.{os.getpid()}.part"
    r = subprocess.run(["curl", "-sL", "--fail", "--max-time", "300", "-o", tmp, url])
    if r.returncode != 0:
        if os.path.exists(tmp):
            os.remove(tmp)
        return f"FAIL {url}"
    os.replace(tmp, out)
    return "ok"


def icon_path(name, download=True):
    p = os.path.join(ICON_DIR, f"{name}.svg")
    if not os.path.exists(p) and download:
        res = _get(f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg", p)
        if res.startswith("FAIL"):
            raise FileNotFoundError(f"Lucide icon '{name}' not found (check the name on lucide.dev/icons)")
    return p


def fetch_vsco():
    tree = json.loads(subprocess.run(["gh", "api", f"repos/{VSCO_REPO}/git/trees/HEAD?recursive=1"],
                                     capture_output=True, text=True, check=True).stdout)["tree"]
    paths = [t["path"] for t in tree if t["type"] == "blob" and any(re.search(p, t["path"]) for p in VSCO_PATTERNS)]
    jobs = [(f"https://raw.githubusercontent.com/{VSCO_REPO}/master/" + urllib.parse.quote(p),
             os.path.join(VSCO_DIR, p.replace("/", "__"))) for p in paths]
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(lambda j: _get(*j), jobs))
    bad = [r for r in res if r.startswith("FAIL")]
    print(f"VSCO samples: {len(jobs)} files, {len(bad)} failed")
    return not bad


def fetch_icons(names):
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(lambda n: _get(
            f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{n}.svg",
            os.path.join(ICON_DIR, f"{n}.svg")), names))
    bad = [n for n, r in zip(names, res) if r.startswith("FAIL")]
    print(f"Lucide icons: {len(names)} requested, {len(bad)} not found {bad if bad else ''}")
    return not bad


if __name__ == "__main__":
    ok = fetch_vsco()
    ok &= fetch_icons(DEFAULT_ICONS + sys.argv[1:])
    sys.exit(0 if ok else 1)
