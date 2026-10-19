# ABOUTME: Lane Y runner: planted restart-per-chapter and restart-per-page keys on LP2's layout, 50 increment-shuffle
# ABOUTME: nulls under each segmentation, and the real LP2 run; BelowNormal workers; writes out/*.jsonl.
"""python -I -X utf8 agents/laneY_section_reset/run_laneY.py [plants|null|real|all] [--procs 4]"""
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


def below_normal():
    if sys.platform == "win32":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


def run(task):
    import ylib as Y
    import xlib as X
    kind, seg_kind, idx, variant = task
    words, page, chap = Y.lp2_words_meta()
    segw = Y.seg_ids(chap if seg_kind == "chapter" else page)
    truth = ph = None
    if kind == "plant":
        rng = random.Random(66000 + idx)
        lens = [len(w) for w in words]
        flat = [x for w in X.english_words(sum(lens), 200000 + 20000 * idx) for x in w]
        it = iter(flat)
        plain = [[next(it) for _ in range(L)] for L in lens]
        K = rng.sample(range(29), 29)
        offs = X.schedule(rng)
        dials = (rng.randrange(29), rng.randrange(29))
        words, ph = Y.encipher_segments(plain, segw, K, offs, dials, 0, variant)
        truth = np.array(flat[:sum(lens)])
    elif kind == "null":
        import nulls
        pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(93000 + idx))
        it = iter([x for p in pages for x in p])
        words = [[next(it) for _ in w] for w in words]
    t0 = time.time()
    rec = Y.attack(words, segw, seed=idx)
    out = {"kind": kind, "seg": seg_kind, "idx": idx, "variant": variant, "anchors": rec["anchors"],
           "s1_score": rec["s1_score"], "S": rec["S"], "kspace": rec["kspace"], "quad_full": rec["quad_full"],
           "ioc": rec["ioc"], "seconds": time.time() - t0, "plain_head": list(map(int, rec["plain"][:400]))}
    if truth is not None:
        out["agree"] = float(np.mean(rec["plain"] == truth))
        out["phase_acc"] = X.phase_accuracy(rec["phase"], ph)
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    tasks = []
    if which in ("plants", "all"):
        tasks += [("plant", seg, i, "advance" if i % 2 == 0 else "hold") for seg in ("chapter", "page") for i in range(10)]
    if which in ("null", "all"):
        tasks += [("null", seg, i, "") for seg in ("chapter", "page") for i in range(50)]
    if which in ("real", "all"):
        tasks += [("real", seg, 0, "") for seg in ("chapter", "page")]
    below_normal()
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(procs) as pool, open(OUT / ("%s.jsonl" % which), "w", encoding="utf-8") as f:
        for rec in pool.imap_unordered(run, tasks):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print("%-5s %-7s %2d %-7s s1 %+.3f quad %.3f %s (%.0fs)" % (
                rec["kind"], rec["seg"], rec["idx"], rec["variant"], rec["s1_score"], rec["quad_full"],
                ("agree %.3f" % rec["agree"]) if "agree" in rec else "", rec["seconds"]), flush=True)
    print("wall %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
