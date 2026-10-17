"""Lane V shared helpers: LP2 loader with word, page and section ids; English runes laid out as LP2 words.

Run from the repository root with `python -I -X utf8 agents/laneV_lag5_mechanisms/<script>.py`.
Process priority is lowered by `lower_priority()` (BELOW_NORMAL, 0x4000) before any work.
"""
import ctypes
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "lp"))
sys.path.insert(0, os.path.join(ROOT, "toolbox"))
import lpdata  # noqa: E402
import runes as rn  # noqa: E402

LP_SHA = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
M = 29
# Lane J's nine page-group sections (agents/laneJ_lag5_echo/core.py, lp_relikd), mapped onto LP2 pages 0-54.
GROUPS = [(0, 2), (3, 7), (8, 14), (15, 22), (23, 26), (27, 32), (33, 39), (40, 53), (54, 55)]
ENGLISH = os.path.join(ROOT, "dl", "dukotah", "liber-primus", "data", "keys", "armada18", "melville_moby_dick.txt")


def lower_priority():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def load_lp2():
    """Returns C (runes 0..28), wid (word id per rune), page (0..54 per rune), sec (section 0..8 per rune)."""
    U, C, sha = lpdata.unsolved()
    assert sha == LP_SHA, sha
    C = np.array(C, dtype=np.int64)
    word = np.array([w for p in U for w in p["word"]])
    _, wid = np.unique(word, return_inverse=True)
    page = np.array([p["page"] for p in U for _ in p["idx"]], dtype=np.int64)
    gid = np.zeros(55, dtype=np.int64)
    for g, (a, b) in enumerate(GROUPS):
        gid[a:b + 1] = g
    sec = gid[page]
    return C, wid, page, sec


_ENG = None


def english_runes():
    """All English runes of the gate's text (Moby-Dick, after the 20,000-character header, as runes.english_stream)."""
    global _ENG
    if _ENG is None:
        text = open(ENGLISH, encoding="utf-8", errors="replace").read()[20000:]
        R = []
        for word in re.findall(r"[A-Za-z]+", text):
            R.extend(rn.eng2runes(word))
        _ENG = np.array(R, dtype=np.int64)
    return _ENG


def english_segment(n, start):
    """n English runes starting at rune index `start` (wrapping), used as plaintext for LP2-shaped streams."""
    E = english_runes()
    idx = (np.arange(n) + start) % len(E)
    return E[idx]


def lag_profile(C, wid, K=10):
    """Within- and cross-word coincidence counts at lags 1..K: returns (mw, nw, mx, nx), each of length K."""
    mw, nw, mx, nx = (np.zeros(K, dtype=np.int64) for _ in range(4))
    for k in range(1, K + 1):
        same = wid[:-k] == wid[k:]
        eq = C[:-k] == C[k:]
        mw[k - 1] = int((eq & same).sum())
        nw[k - 1] = int(same.sum())
        mx[k - 1] = int((eq & ~same).sum())
        nx[k - 1] = int((~same).sum())
    return mw, nw, mx, nx
