# ABOUTME: Lane AA follow-up on the one window where LP2 beat all 20 nulls (T 4,000, window 3, runes 6,002-10,001):
# ABOUTME: 100 fresh nulls for that window and LP2 on windows shifted by -1,000 to +1,000 runes; out/followup.jsonl.
"""python -I -X utf8 agents/laneAA_chapter_keys/window_followup.py [--procs 4]

Stage 1 is deterministic, so a re-run with a new seed cannot move LP2's score; more nulls and shifted windows can say
whether the margin (0.0291 against a null max of 0.0270, z +2.04) is chance or local structure.
"""
import json
import random
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(HERE), str(REPO / "agents" / "laneY_section_reset")]
OUT = HERE / "out"
T = 4000
START = 6002                                    # rune offset of window 3
SHIFTS = (-1000, -500, 0, 500, 1000)


def span(words, s, n):
    starts_r = np.cumsum([0] + [len(w) for w in words])
    return int(np.searchsorted(starts_r, s)), int(np.searchsorted(starts_r, s + n))


def run(task):
    from run_laneAA import below_normal
    below_normal()
    import ylib as Y          # first: it puts lane X's directory on sys.path
    import xlib as X
    import pipeline as PL
    X.FLOOR = 1e-4
    kind, shift, idx = task
    words, _page, _chap = Y.lp2_words_meta()
    a, b = span(words, START + shift, T)
    if kind == "null":
        import nulls
        pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(62000 + idx))
        it = iter([x for p in pages for x in p])
        words = [[next(it) for _ in w] for w in words]
    t0 = time.time()
    rec = PL.attack(words[a:b], seed=idx, do_stage2=False)
    return {"kind": kind, "shift": shift, "idx": idx, "words": [a, b], "n_runes": rec["n_runes"],
            "s1_score": rec["s1_score"], "S": rec["S"], "kspace": rec["kspace"], "dead_chains": rec["dead_chains"],
            "seconds": time.time() - t0}


def main():
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    tasks = [("real", s, 0) for s in SHIFTS] + [("null", 0, i) for i in range(100)]
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    rows = []
    with get_context("spawn").Pool(procs) as pool, open(OUT / "followup.jsonl", "w", encoding="utf-8") as f:
        for rec in pool.imap_unordered(run, tasks):
            rows.append(rec)
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print("%-4s shift %+5d %3d runes %4d s1 %+.4f (%.0fs)" % (
                rec["kind"], rec["shift"], rec["idx"], rec["n_runes"], rec["s1_score"], rec["seconds"]), flush=True)
    nl = np.array([r["s1_score"] for r in rows if r["kind"] == "null"])
    for r in sorted((r for r in rows if r["kind"] == "real"), key=lambda r: r["shift"]):
        print("LP2 shift %+5d: %.4f  z %+.2f against %d nulls (mean %.4f sd %.4f max %.4f), %d as high" % (
            r["shift"], r["s1_score"], (r["s1_score"] - nl.mean()) / nl.std(ddof=1), len(nl), nl.mean(),
            nl.std(ddof=1), nl.max(), int((nl >= r["s1_score"]).sum())))
    print("wall %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
