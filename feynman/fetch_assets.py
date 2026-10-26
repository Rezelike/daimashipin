"""Download the free assets used by the Feynman video (not committed to git).

* Instrument samples: VSCO-2 Community Edition (CC0-1.0)
  https://github.com/sgossner/VSCO-2-CE  (Upright Piano by Simon Dalzell / Ivy Audio)
* Icons: Lucide (ISC license)  https://github.com/lucide-icons/lucide
"""
import json, os, re, subprocess, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, ".assets")
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

ICONS = [
    "brain", "book-open", "notebook-pen", "baby", "message-circle", "search",
    "lightbulb", "repeat", "x", "check", "heart", "star", "bookmark", "user-plus",
    "trophy", "atom", "zap", "triangle-alert", "terminal", "sparkles", "pencil",
    "circle-question-mark", "snowflake", "trending-up", "quote", "target", "file-text",
    "message-square-text", "rotate-cw", "eye", "mic", "list-checks", "graduation-cap",
    "drum", "scan-search", "badge-check", "messages-square", "piggy-bank",
]


def _get(url, out):
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return "cached"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run(["curl", "-sL", "--fail", "--max-time", "300", "-o", out, url])
    return "ok" if r.returncode == 0 else f"FAIL {url}"


def fetch_vsco():
    tree = json.loads(subprocess.run(
        ["gh", "api", f"repos/{VSCO_REPO}/git/trees/HEAD?recursive=1"],
        capture_output=True, text=True, check=True).stdout)["tree"]
    paths = [t["path"] for t in tree if t["type"] == "blob"
             and any(re.search(p, t["path"]) for p in VSCO_PATTERNS)]
    jobs = [(f"https://raw.githubusercontent.com/{VSCO_REPO}/master/" + urllib.parse.quote(p),
             os.path.join(VSCO_DIR, p.replace("/", "__"))) for p in paths]
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(lambda j: _get(*j), jobs))
    bad = [r for r in res if r.startswith("FAIL")]
    print(f"VSCO samples: {len(jobs)} files, {len(bad)} failed")
    for b in bad:
        print(" ", b)


def fetch_icons():
    jobs = [(f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{n}.svg",
             os.path.join(ICON_DIR, f"{n}.svg")) for n in ICONS]
    with ThreadPoolExecutor(12) as ex:
        res = list(ex.map(lambda j: _get(*j), jobs))
    bad = [r for r in res if r.startswith("FAIL")]
    print(f"Lucide icons: {len(jobs)} files, {len(bad)} failed")
    for b in bad:
        print(" ", b)


if __name__ == "__main__":
    fetch_vsco()
    fetch_icons()
