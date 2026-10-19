# ABOUTME: Lane AA main test: lane X's key-free attack on overlapping windows of LP2 (size T, stride T/2), so any one
# ABOUTME: key used over 1.5 T or more consecutive runes is caught by some window; plants, nulls, real; out/windows_T.jsonl.
"""python -I -X utf8 agents/laneAA_chapter_keys/run_windows.py T [--procs 4]

If LP2 has several independent keys (a key per part, as LP1's sections had), lane X on the whole book sees a mixture.
A window lying inside one key's span sees one key. Windows of T runes at stride T/2: every span of 1.5 T runes or more
contains a whole window. T comes from the power curve (`power_curve.py`). Each window has its own plants (English in
that window's word layout, random key) and its own nulls (the same window cut from increment-shuffled LP2).
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
N_PLANT, N_NULL = 4, 20


def windows(words, T):
    """(first word, end word) of each window: starts every T/2 runes on word boundaries, the last one flush with the end."""
    starts_r = np.cumsum([0] + [len(w) for w in words])        # rune offset of each word
    total = int(starts_r[-1])
    out, s = [], 0
    while True:
        a = int(np.searchsorted(starts_r, s))
        b = int(np.searchsorted(starts_r, s + T))
        if s + T >= total:
            b = len(words)
            a = int(np.searchsorted(starts_r, total - T, side="right")) - 1
            out.append((a, b))
            return out
        out.append((a, b))
        s += T // 2


def run(task):
    from run_laneAA import below_normal
    below_normal()
    import ylib as Y          # first: it puts lane X's directory on sys.path
    import xlib as X
    import pipeline as PL
    X.FLOOR = 1e-4
    kind, T, wi, idx = task
    words, _page, _chap = Y.lp2_words_meta()
    a, b = windows(words, T)[wi]
    truth = None
    variant = ""
    if kind == "plant":
        rng = random.Random(60000 + 1000 * wi + idx + T)
        lens = [len(w) for w in words[a:b]]
        flat = [x for w in X.english_words(sum(lens), 30000 * (N_PLANT * wi + idx)) for x in w]
        it = iter(flat)
        plain = [[next(it) for _ in range(L)] for L in lens]
        K = rng.sample(range(29), 29)
        offs = X.schedule(rng)
        dials = (rng.randrange(29), rng.randrange(29))
        variant = "advance" if idx % 2 == 0 else "hold"
        cw, _ph = X.encipher_trace(plain, K, offs, dials, rng.randrange(5), variant)
        truth = np.array(flat[:sum(lens)])
    else:
        if kind == "null":
            import nulls
            pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(61000 + 1000 * wi + idx + T))
            it = iter([x for p in pages for x in p])
            words = [[next(it) for _ in w] for w in words]
        cw = words[a:b]
    t0 = time.time()
    rec = PL.attack(cw, seed=idx)
    out = {"kind": kind, "T": T, "window": wi, "words": [a, b], "idx": idx, "variant": variant,
           "n_runes": rec["n_runes"], "anchors": rec["anchors"], "s1_score": rec["s1_score"], "S": rec["S"],
           "kspace": rec["kspace"], "dead_chains": rec["dead_chains"], "quad_full": rec["quad_full"],
           "seconds": time.time() - t0, "plain_head": list(map(int, rec["plain"][:400]))}
    if truth is not None:
        out["agree"] = float(np.mean(rec["plain"] == truth))
    return out


def main():
    T = int(sys.argv[1])
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    import ylib as Y
    words, _p, _c = Y.lp2_words_meta()
    W = windows(words, T)
    print("T %d: %d windows (words) %s" % (T, len(W), W), flush=True)
    tasks = []
    for wi in range(len(W)):
        tasks += [("plant", T, wi, i) for i in range(N_PLANT)]
        tasks += [("null", T, wi, i) for i in range(N_NULL)]
        tasks += [("real", T, wi, 0)]
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(procs) as pool, open(OUT / ("windows_%d.jsonl" % T), "w", encoding="utf-8") as f:
        for rec in pool.imap_unordered(run, tasks):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print("%-5s win %d %2d %-7s runes %5d s1 %+.4f quad %.3f dead %d %s (%.0fs)" % (
                rec["kind"], rec["window"], rec["idx"], rec["variant"], rec["n_runes"], rec["s1_score"],
                rec["quad_full"], rec["dead_chains"], ("agree %.3f" % rec["agree"]) if "agree" in rec else "",
                rec["seconds"]), flush=True)
    print("wall %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
