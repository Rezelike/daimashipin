"""Reusable engine for code-generated knowledge videos (dark-tech style, original piano + violin score).

    engine.core     drawing primitives: text (CJK fallback + readability lint), cards, icons, backgrounds
    engine.music    sample-based score engine (VSCO-2 CE, CC0) + auto arrangement by section role
    engine.render   Episode definition + CLI: preview sheet / frames / cover / full render / verify
    engine.figures  little people (seated, walking, props, crowds) + desk / door / clock furniture
    engine.sfx      synthesized sound effects (no music), levelled by loudness, cued on beats
    engine.assets   downloads CC0 samples + Lucide icons from GitHub (into REPO/.assets, gitignored)
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(REPO, "fonts")
ASSETS = os.path.join(REPO, ".assets")
OUT = os.path.join(REPO, "out")
