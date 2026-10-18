# ABOUTME: Lane X control on LP2's own word layout: English runes re-cut into LP2's exact word lengths, enciphered
# ABOUTME: with random-alphabet odometer-dodge keys, then attacked; checks the detector on the real layout.
import json
import random
import sys
from multiprocessing import get_context
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def run(idx):
    import xlib as X
    import pipeline as PL
    from run_lane import below_normal
    below_normal()
    lens = [len(w) for w in X.lp2_words()]
    rng = random.Random(55000 + idx)
    flat = [x for w in X.english_words(sum(lens), 60000 + 15000 * idx) for x in w]
    it = iter(flat)
    plain = [[next(it) for _ in range(L)] for L in lens]
    K = rng.sample(range(29), 29)
    offs = X.schedule(rng)
    words, ph = X.encipher_trace(plain, K, offs, (rng.randrange(29), rng.randrange(29)), 0,
                                 "advance" if idx % 2 == 0 else "hold")
    rec = PL.attack(words, seed=idx)
    truth = np.array([x for w in plain for x in w])
    return {"idx": idx, "variant": "advance" if idx % 2 == 0 else "hold", "anchors": rec["anchors"],
            "s1_score": rec["s1_score"], "quad_full": rec["quad_full"], "agree": float(np.mean(rec["plain"] == truth)),
            "phase_acc": X.phase_accuracy(rec["phase"], ph)}


if __name__ == "__main__":
    with get_context("spawn").Pool(4) as pool:
        res = pool.map(run, range(8))
    (HERE / "out" / "layout_plants.jsonl").write_text("".join(json.dumps(r) + "\n" for r in res), encoding="utf-8")
    for r in res:
        print("layout plant %d %-7s anchors %3d  s1 %+.3f  quad %.3f  agree %.3f  phase %.3f" % (
            r["idx"], r["variant"], r["anchors"], r["s1_score"], r["quad_full"], r["agree"], r["phase_acc"]))
