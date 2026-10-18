# ABOUTME: Lane X runner: planted controls (random alphabets, both variants, space skips, shorter texts), the
# ABOUTME: LP2 increment-shuffle null and the real LP2 run, on BelowNormal workers; writes out/*.jsonl.
"""python -I -X utf8 agents/laneX_general_alphabet/run_lane.py [plants|null|real|all] [--procs 4]"""
import ctypes
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
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


def plant_tasks():
    tasks = []
    for i in range(20):                                   # full length, both variants, space skip 0
        tasks.append(("plant", i, "advance" if i % 2 == 0 else "hold", 0, 12956))
    for i in range(20, 24):                               # space skips 1-4
        tasks.append(("plant", i, "advance", i - 19, 12956))
    for i in range(24, 34):                               # shorter keyed spans: power vs length
        tasks.append(("plant", i, "advance" if i % 2 == 0 else "hold", 0, 6000 if i < 29 else 3000))
    return tasks


def run(task):
    import xlib as X
    import pipeline as PL
    kind, idx, variant, kspace, n = task
    if kind == "plant":
        rng = random.Random(77000 + idx)
        plain = X.english_words(n, 20000 + 14000 * idx)
        K = rng.sample(range(29), 29)
        offs = X.schedule(rng)
        dials = (rng.randrange(29), rng.randrange(29))
        words, ph = X.encipher_trace(plain, K, offs, dials, kspace, variant)
        truth = np.array([x for w in plain for x in w])
    else:
        words, truth = X.lp2_words(), None
        if kind == "null":
            import nulls
            pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(91000 + idx))
            flat = iter([x for p in pages for x in p])
            words = [[next(flat) for _ in w] for w in words]
    rec = PL.attack(words, seed=idx)
    out = {"kind": kind, "idx": idx, "variant": variant, "kspace_true": kspace, "n": n,
           "anchors": rec["anchors"], "s1_score": rec["s1_score"], "s1_untied": rec["s1_untied"], "S": rec["S"],
           "kspace": rec["kspace"], "s1_by_kspace": rec["s1_by_kspace"], "a0": rec["a0"], "ioc": rec["ioc"],
           "quad_full": rec["quad_full"], "seconds": rec["seconds"],
           "plain_head": list(map(int, rec["plain"][:400]))}
    if truth is not None:
        out["agree"] = float(np.mean(rec["plain"] == truth))
        out["phase_acc"] = X.phase_accuracy(rec["phase"], ph)
        out["S_true"] = list(map(int, X.running(offs)))
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    tasks = []
    if which in ("plants", "all"):
        tasks += plant_tasks()
    if which in ("null", "all"):
        tasks += [("null", i, "", 0, 12956) for i in range(20)]
    if which == "null2":                                  # 30 more nulls, seeds 20-49
        tasks += [("null", i, "", 0, 12956) for i in range(20, 50)]
    if which in ("real", "all"):
        tasks += [("real", 0, "", 0, 12956)]
    below_normal()
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(procs) as pool, open(OUT / ("%s.jsonl" % which), "w", encoding="utf-8") as f:
        for rec in pool.imap_unordered(run, tasks):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print("%-5s %2d %-7s ks %d n %5d  s1 %+.3f  quad %.3f  %s  (%.0fs)" % (
                rec["kind"], rec["idx"], rec["variant"], rec["kspace_true"], rec["n"], rec["s1_score"],
                rec["quad_full"], ("agree %.3f" % rec["agree"]) if "agree" in rec else "", rec["seconds"]), flush=True)
    print("wall %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
