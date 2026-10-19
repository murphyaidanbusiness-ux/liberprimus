# ABOUTME: Lane X end-to-end attack on one ciphertext: stage 1 (key-free schedule and clock path) for every space
# ABOUTME: skip, then stage 2 (an IoC alignment climb on the alphabet, then a substitution solve) on the best fit.
"""Attack one ciphertext (a list of rune words) for the Quagmire-odometer dodge with ANY keyed alphabet.

    from pipeline import attack;  rec = attack(words, seed)

Stage 1: anchor_counts -> shift_scan (advance and hold, top 4 each) -> fit_tied, for space skips 0-4. The best
tied DM score (nats per rune) is the family-wide statistic: about +0.24 to +0.33 on planted keys, about 0 on noise.
Stage 2: a0 from choose_a0, then a climb of K for the unigram IoC of the decrypt (it aligns the 29 tables; the
start dials then leave only a fixed substitution), then a quadgram substitution solve. English decrypts score about
-4.6 to -4.8 per quadgram; noise about -6.3.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage2 as S2  # noqa: E402
import xlib as X  # noqa: E402

M = 29


def stage1(words, kspaces=(0, 1, 2, 3, 4)):
    C, n_anchor = X.anchor_counts(words)
    starts = [s for v in ("advance", "hold") for _sc, s in X.shift_scan(C, v, top=4)[0]]
    fits = []
    for ks in kspaces:
        fits += X.fit_tied(words, starts, kspace=ks, iters=20)
    best = max(fits, key=lambda r: r["score"])
    return best, n_anchor, fits


def stage2(words, best, q, rng):
    """a0 from the S-pooled tables, then the IoC alignment climb and the substitution solve (stage2.solve_stage2)."""
    a0, _ = S2.choose_a0(words, best["phase"], best["S"])
    x, tau = S2.setup(words, best["phase"], best["S"], a0)
    r = S2.solve_stage2(x, tau, q, rng)
    return {"a0": a0, "ioc": r["ioc"], "quad_full": r["quad_full"], "plain": r["plain"]}


def attack(words, seed, do_stage2=True, kspaces=(0, 1, 2, 3, 4)):
    t0 = time.time()
    rng = np.random.default_rng(seed)
    best, n_anchor, fits = stage1(words, kspaces)
    by_ks = {}
    for f in fits:
        by_ks[f["kspace"]] = max(by_ks.get(f["kspace"], -9.0), f["score"])
    rec = {"chains": len(fits), "dead_chains": sum(not f["finite"] for f in fits), "best_finite": best["finite"],
           "n_runes": int(sum(len(w) for w in words)), "n_words": len(words), "anchors": int(n_anchor),
           "s1_score": best["score"], "s1_untied": best["untied"], "S": best["S"], "kspace": best["kspace"],
           "s1_by_kspace": by_ks, "phase": best["phase"], "t_stage1": time.time() - t0}
    if do_stage2:
        q = S2.quad_table()
        r2 = stage2(words, best, q, rng)
        rec.update({k: v for k, v in r2.items()})
    rec["seconds"] = time.time() - t0
    return rec
