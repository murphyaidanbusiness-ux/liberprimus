# ABOUTME: Robustness check for lanes X and Y: re-run LP2, nulls and plants with a small floor on the clock-drift
# ABOUTME: transitions (no chain can die) and count the chains that died without it; writes out/floor_check.jsonl.
"""python -I -X utf8 agents/laneY_section_reset/floor_check.py

Without a floor, a Baum-Welch chain gets all-zero forward mass (NaN) when an anchor demands a clock phase two or more
drift steps away from where its path sits, and that chain's grouping is then garbage. This re-runs, with FLOOR = 1e-4:
LP2 under lane X (one key) and lane Y (chapter and page restarts), 20 nulls and 4 plants for each, and LP2 again with
FLOOR = 0 to count the dead chains the original runs had.
"""
import json
import random
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
OUT = HERE / "out"


def run(task):
    from run_laneY import below_normal
    below_normal()
    import ylib as Y          # first: it puts lane X's directory on sys.path
    import xlib as X
    import pipeline as PL
    test, kind, idx, floor = task
    X.FLOOR = floor
    words, page, chap = Y.lp2_words_meta()
    segw = None if test == "X" else Y.seg_ids(chap if test == "Ychapter" else page)
    truth = None
    if kind == "plant":
        rng = random.Random(44000 + idx)
        lens = [len(w) for w in words]
        flat = [x for w in X.english_words(sum(lens), 400000 + 20000 * idx) for x in w]
        it = iter(flat)
        plain = [[next(it) for _ in range(L)] for L in lens]
        K = rng.sample(range(29), 29)
        offs = X.schedule(rng)
        dials = (rng.randrange(29), rng.randrange(29))
        variant = "advance" if idx % 2 == 0 else "hold"
        if segw is None:
            words, _ph = X.encipher_trace(plain, K, offs, dials, 0, variant)
        else:
            words, _ph = Y.encipher_segments(plain, segw, K, offs, dials, 0, variant)
        truth = np.array(flat[:sum(lens)])
    elif kind == "null":
        import nulls
        pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(97000 + idx))
        it = iter([x for p in pages for x in p])
        words = [[next(it) for _ in w] for w in words]
    t0 = time.time()
    rec = PL.attack(words, seed=idx) if segw is None else Y.attack(words, segw, seed=idx)
    out = {"test": test, "kind": kind, "idx": idx, "floor": floor, "s1_score": rec["s1_score"],
           "chains": rec["chains"], "dead_chains": rec["dead_chains"], "best_finite": rec["best_finite"],
           "quad_full": rec["quad_full"], "seconds": time.time() - t0}
    if truth is not None:
        out["agree"] = float(np.mean(rec["plain"] == truth))
    return out


if __name__ == "__main__":
    tasks = []
    for test in ("X", "Ychapter", "Ypage"):
        tasks += [(test, "real", 0, 0.0), (test, "real", 0, 1e-4)]
        tasks += [(test, "plant", i, 1e-4) for i in range(4)]
        tasks += [(test, "null", i, 1e-4) for i in range(20)]
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(4) as pool, open(OUT / "floor_check.jsonl", "w", encoding="utf-8") as f:
        for rec in pool.imap_unordered(run, tasks):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print("%-8s %-5s %2d floor %.0e  s1 %+.4f  dead %d/%d best_ok %s %s" % (
                rec["test"], rec["kind"], rec["idx"], rec["floor"], rec["s1_score"], rec["dead_chains"], rec["chains"],
                rec["best_finite"], ("agree %.3f" % rec["agree"]) if "agree" in rec else ""), flush=True)
    print("wall %.0f s" % (time.time() - t0))
