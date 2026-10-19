# ABOUTME: Lane AA: lane X's key-free odometer-dodge attack run on each LP2 chapter alone, for a book whose chapters
# ABOUTME: each have their own independent key (K, schedule, dials, variant), as LP1's sections did; writes out/*.jsonl.
"""python -I -X utf8 agents/laneAA_chapter_keys/run_laneAA.py [probe|all] [--procs 4]

Lanes X, Y and Z assume one key (one alphabet K, one schedule) for the whole of LP2. LP1's sections each had their own
key. Here every chapter is attacked on its own with lane X's pipeline unchanged, so each chapter may have its own K,
schedule, start dials, variant and space skip. The price is power: a chapter has 9 to 2,474 runes against LP2's 12,956,
so only the chapters of 500 runes or more are tested, and the plants say how far down detection reaches.
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
CHAPTERS = (14, 7, 5, 9, 11, 8, 0, 2, 15)      # every chapter of 500 runes or more, largest first


def below_normal():
    if sys.platform == "win32":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


def chapter_words(words, chap, ch):
    return [w for w, c in zip(words, chap) if c == ch]


def run(task):
    below_normal()
    import ylib as Y          # first: it puts lane X's directory on sys.path
    import xlib as X
    import pipeline as PL
    X.FLOOR = 1e-4
    kind, ch, idx, variant = task
    words, _page, chap = Y.lp2_words_meta()
    truth = None
    if kind == "plant":
        rng = random.Random(77000 + 100 * ch + idx)
        lens = [len(w) for w in chapter_words(words, chap, ch)]
        flat = [x for w in X.english_words(sum(lens), 3000 * (10 * CHAPTERS.index(ch) + idx)) for x in w]
        it = iter(flat)
        plain = [[next(it) for _ in range(L)] for L in lens]
        K = rng.sample(range(29), 29)
        offs = X.schedule(rng)
        dials = (rng.randrange(29), rng.randrange(29))
        cw, _ph = X.encipher_trace(plain, K, offs, dials, rng.randrange(5), variant)
        truth = np.array(flat[:sum(lens)])
    else:
        if kind == "null":
            import nulls
            pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(99000 + 100 * ch + idx))
            it = iter([x for p in pages for x in p])
            words = [[next(it) for _ in w] for w in words]
        cw = chapter_words(words, chap, ch)
    t0 = time.time()
    rec = PL.attack(cw, seed=idx)
    out = {"kind": kind, "chap": ch, "idx": idx, "variant": variant, "n_runes": rec["n_runes"],
           "anchors": rec["anchors"], "s1_score": rec["s1_score"], "S": rec["S"], "kspace": rec["kspace"],
           "dead_chains": rec["dead_chains"], "quad_full": rec["quad_full"], "seconds": time.time() - t0,
           "plain_head": list(map(int, rec["plain"][:400]))}
    if truth is not None:
        out["agree"] = float(np.mean(rec["plain"] == truth))
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    tasks = []
    if which == "probe":
        for ch in (14, 8, 15):
            tasks += [("plant", ch, i, "advance" if i % 2 == 0 else "hold") for i in range(3)]
            tasks += [("null", ch, i, "") for i in range(5)]
    else:
        for ch in CHAPTERS:
            tasks += [("plant", ch, i, "advance" if i % 2 == 0 else "hold") for i in range(6)]
            tasks += [("null", ch, i, "") for i in range(20)]
            tasks += [("real", ch, 0, "")]
    below_normal()
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(procs) as pool, open(OUT / ("%s.jsonl" % which), "w", encoding="utf-8") as f:
        for rec in pool.imap_unordered(run, tasks):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print("%-5s ch %2d %2d %-7s runes %4d s1 %+.4f quad %.3f dead %d %s (%.0fs)" % (
                rec["kind"], rec["chap"], rec["idx"], rec["variant"], rec["n_runes"], rec["s1_score"],
                rec["quad_full"], rec["dead_chains"], ("agree %.3f" % rec["agree"]) if "agree" in rec else "",
                rec["seconds"]), flush=True)
    print("wall %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
