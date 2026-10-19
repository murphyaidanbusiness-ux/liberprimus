# ABOUTME: Lane Z: lane X's key-free odometer-dodge attack with the inner dial stepping once per LINE, SENTENCE, PAGE or
# ABOUTME: CHAPTER instead of once per word; plants, increment-shuffle nulls and LP2 per unit; writes out/all.jsonl.
"""python -I -X utf8 agents/laneZ_dial_units/run_laneZ.py [--procs 4]

Every word-keyed attack (lanes O, X, Y and the community's) assumes the dial steps per visible word. LP2's layout is not
the plaintext's layout (C4), and the lag-5 echo is sharper across line breaks, so here the dial steps per unit of the
book's own layout. Lane X's machinery works unchanged once the units are passed in place of words: a group is then
(unit index mod 29, clock phase). Fixed-length blocks are not tested: they make the key periodic, which C1 excludes.
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
sys.path[:0] = [str(HERE), str(REPO / "agents" / "laneX_general_alphabet")]
OUT = HERE / "out"
UNITS = ("line", "sent", "page", "chap")


def below_normal():
    if sys.platform == "win32":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


def lp2_unit_ids(unit):
    """LP2 runes (SHA-pinned) and, per rune, the id of its unit (global line, sentence, page or chapter id)."""
    sys.path.insert(0, str(REPO / "lp"))
    import lpdata
    U, _C, sha = lpdata.unsolved()
    assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    runes, ids = [], []
    for p in U:
        for k, x in enumerate(p["idx"]):
            runes.append(x)
            ids.append(p["page"] if unit == "page" else p[unit][k])
    return runes, ids


def cut(flat, ids):
    """Cut a rune stream into units at every change of unit id."""
    out, cur, prev = [], [], object()
    for x, u in zip(flat, ids):
        if u != prev and cur:
            out.append(cur)
            cur = []
        cur.append(x)
        prev = u
    out.append(cur)
    return out


def run(task):
    below_normal()
    import xlib as X
    import pipeline as PL
    X.FLOOR = 1e-4
    kind, unit, idx, variant = task
    runes, ids = lp2_unit_ids(unit)
    truth = None
    if kind == "plant":
        rng = random.Random(88000 + idx + 100 * UNITS.index(unit))
        flat = [x for w in X.english_words(len(runes), 600000 + 20000 * idx) for x in w][:len(runes)]
        K = rng.sample(range(29), 29)
        offs = X.schedule(rng)
        dials = (rng.randrange(29), rng.randrange(29))
        words, _ph = X.encipher_trace(cut(flat, ids), K, offs, dials, 0, variant)
        truth = np.array(flat)
    else:
        if kind == "null":
            import nulls
            pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(98000 + idx + 1000 * UNITS.index(unit)))
            runes = [x for p in pages for x in p]
        words = cut(runes, ids)
    t0 = time.time()
    rec = PL.attack(words, seed=idx)
    out = {"kind": kind, "unit": unit, "idx": idx, "variant": variant, "n_units": len(words),
           "anchors": rec["anchors"], "s1_score": rec["s1_score"], "S": rec["S"], "kspace": rec["kspace"],
           "dead_chains": rec["dead_chains"], "quad_full": rec["quad_full"], "seconds": time.time() - t0,
           "plain_head": list(map(int, rec["plain"][:400]))}
    if truth is not None:
        out["agree"] = float(np.mean(rec["plain"] == truth))
    return out


def main():
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 4
    tasks = []
    for unit in UNITS:
        tasks += [("plant", unit, i, "advance" if i % 2 == 0 else "hold") for i in range(6)]
        tasks += [("null", unit, i, "") for i in range(30)]
        tasks += [("real", unit, 0, "")]
    below_normal()
    OUT.mkdir(exist_ok=True)
    t0 = time.time()
    with get_context("spawn").Pool(procs) as pool, open(OUT / "all.jsonl", "w", encoding="utf-8") as f:
        for rec in pool.imap_unordered(run, tasks):
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print("%-5s %-4s %2d %-7s units %4d s1 %+.4f quad %.3f dead %d %s (%.0fs)" % (
                rec["kind"], rec["unit"], rec["idx"], rec["variant"], rec["n_units"], rec["s1_score"],
                rec["quad_full"], rec["dead_chains"], ("agree %.3f" % rec["agree"]) if "agree" in rec else "",
                rec["seconds"]), flush=True)
    print("wall %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
