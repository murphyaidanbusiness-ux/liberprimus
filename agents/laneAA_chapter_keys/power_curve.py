# ABOUTME: Lane AA power curve: how many runes of one key lane X's key-free attack needs, from plants and nulls on
# ABOUTME: prefixes of LP2's word layout (2,474 to 12,956 runes); records score, phase accuracy, decryption; out/power.jsonl.
"""python -I -X utf8 agents/laneAA_chapter_keys/power_curve.py [--procs 4]

The per-chapter probe (`run_laneAA.py probe`) found no power on single chapters. This measures where the power starts,
which bounds every hypothesis with several independent keys (a key per chapter, per part, per half).
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
SIZES = (2474, 4000, 6000, 8000, 12956)


def prefix_count(words, n):
    """Number of leading LP2 words that hold at least n runes (all of them for the full size)."""
    s = 0
    for k, w in enumerate(words):
        if s >= n:
            return k
        s += len(w)
    return len(words)


def run(task):
    from run_laneAA import below_normal
    below_normal()
    import ylib as Y          # first: it puts lane X's directory on sys.path
    import xlib as X
    import pipeline as PL
    X.FLOOR = 1e-4
    kind, size, idx = task
    words, _page, _chap = Y.lp2_words_meta()
    k = prefix_count(words, size)
    truth = ph = None
    variant = ""
    if kind == "plant":
        rng = random.Random(55000 + 10 * SIZES.index(size) + idx)
        lens = [len(w) for w in words[:k]]
        flat = [x for w in X.english_words(sum(lens), 20000 * (5 * SIZES.index(size) + idx)) for x in w]
        it = iter(flat)
        plain = [[next(it) for _ in range(L)] for L in lens]
        K = rng.sample(range(29), 29)
        offs = X.schedule(rng)
        dials = (rng.randrange(29), rng.randrange(29))
        variant = "advance" if idx % 2 == 0 else "hold"
        cw, ph = X.encipher_trace(plain, K, offs, dials, rng.randrange(5), variant)
        truth = np.array(flat[:sum(lens)])
    else:
        import nulls
        pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(56000 + 100 * SIZES.index(size) + idx))
        it = iter([x for p in pages for x in p])
        cw = [[next(it) for _ in w] for w in words][:k]
    t0 = time.time()
    rec = PL.attack(cw, seed=idx)
    out = {"kind": kind, "size": size, "idx": idx, "variant": variant, "n_runes": rec["n_runes"],
           "anchors": rec["anchors"], "s1_score": rec["s1_score"], "dead_chains": rec["dead_chains"],
           "quad_full": rec["quad_full"], "seconds": time.time() - t0}
    if truth is not None:
        out["agree"] = float(np.mean(rec["plain"] == truth))
        out["phase_acc"] = X.phase_accuracy(rec["phase"], np.array(ph))
    return out


def main():
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    tasks = [(kind, size, i) for size in SIZES for kind, n in (("plant", 4), ("null", 8)) for i in range(n)]
    tasks.sort(key=lambda t: -t[1])              # largest first, so the pool ends on short tasks
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(procs) as pool, open(OUT / "power.jsonl", "w", encoding="utf-8") as f:
        for rec in pool.imap_unordered(run, tasks):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print("%-5s size %5d %d %-7s runes %5d s1 %+.4f quad %.3f %s (%.0fs)" % (
                rec["kind"], rec["size"], rec["idx"], rec["variant"], rec["n_runes"], rec["s1_score"],
                rec["quad_full"], ("phase %.2f agree %.3f" % (rec["phase_acc"], rec["agree"])) if "agree" in rec
                else "", rec["seconds"]), flush=True)
    print("wall %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
