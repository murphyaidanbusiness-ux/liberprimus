# Orchestrator diagnostic for lane O: does the sweep's scorer recover planted keys whose alphabet is
# keyword-built (the only kind the sweep searches) as well as it recovers random alphabets (the kind
# the community selftest plants)?
"""For each seed: plant an odometer + dodge key (doublet_phase_test.encipher, 'advance') on a register
matched to the LP's first 400 word lengths, then score the planted schedule and 4,000 random wrong
one-zero schedules under the planted alphabet with the sweep's own score path (score_key, 29 inner
dials each, outer dial absorbed). Report the planted key's rank and z per alphabet kind.

    source agents/laneO_quagmire_dodge/env.sh && python agents/laneO_quagmire_dodge/diag_alphabet_kind.py
"""

from __future__ import annotations

import json
import os
import random
import sys
from multiprocessing import get_context
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PORT = Path(os.environ.get("DODGE_PORT", REPO / "dl" / "aldegonde_port"))
sys.path[:0] = [str(PORT / "src"), str(PORT / "experiments")]

M = 29
WRONG = int(os.environ.get("DIAG_WRONG", "4000"))
SEEDS = range(int(os.environ.get("DIAG_SEED0", "0")), int(os.environ.get("DIAG_SEED1", "10")))


def run(job):
    kind, seed = job
    import dodge_priority_sweep as dps
    from doublet_phase_test import encipher
    from base_free_verifier import log_frequencies
    from ea_direction_test import PROSE_CACHE
    from keyword_exhaustion import alphabets, kw_runes
    from pure_quagmire_restart import matched_register, schedule
    from quagmire_runner import load_register
    from quagmire_ungated_sweep import priority_vocabulary

    rng = random.Random(1000 * (kind == "keyword") + seed)
    lens = dps._lens()
    pools, _t, _f = load_register(PROSE_CACHE)
    logf = log_frequencies()
    if kind == "random":
        K, label = rng.sample(range(M), M), "random"
    else:
        vocab = sorted({w for w in priority_vocabulary() if kw_runes(w)})
        word = rng.choice(vocab)
        rules = list(alphabets(kw_runes(word)))
        rule, K = rules[rng.randrange(len(rules))]
        K, label = [int(x) for x in K], "%s/%s" % (word, rule)
    offsets = schedule(rng)
    dials = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, lens, pools)
    cipher = encipher(plain, K, offsets, dials, 0, "advance")
    corpus = dps.Corpus(cipher)
    wrong = set()
    while len(wrong) < WRONG:
        s = tuple(schedule(rng))
        if list(s) != offsets:
            wrong.add(s)
    scheds = np.array([offsets] + sorted(wrong), dtype=np.int8)
    best = dps.score_key(K, scheds, corpus, logf, keep=len(scheds))
    ranked = sorted(best, key=lambda t: -t[0])
    pos = next(i for i, (_s, o, _d) in enumerate(ranked) if list(o) == offsets)
    others = np.array([s for s, o, _d in ranked if list(o) != offsets])
    truth = ranked[pos]
    # how far is the planted alphabet from "keyword then the rest in order"? count ascending runs
    runs = 1 + sum(1 for i in range(1, M) if K[i] != (K[i - 1] + 1) % M)
    return {"kind": kind, "seed": seed, "alphabet": label, "runs": runs, "offsets": offsets,
            "dials": list(dials), "rank": pos + 1, "of": len(ranked), "score": round(truth[0], 4),
            "wrong_mean": round(float(others.mean()), 4), "wrong_sd": round(float(others.std()), 4),
            "wrong_max": round(float(others.max()), 4),
            "z": round(float((truth[0] - others.mean()) / others.std()), 2),
            "dial_recovered": int(truth[2]), "dial_planted": dials[0]}


if __name__ == "__main__":
    jobs = [(k, s) for k in os.environ.get("DIAG_KINDS", "random,keyword").split(",") for s in SEEDS]
    with get_context("spawn").Pool(min(14, len(jobs))) as pool:
        res = pool.map(run, jobs)
    out = REPO / "agents" / "laneO_quagmire_dodge" / "out" / os.environ.get("DIAG_OUT", "diag_alphabet_kind.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(r) + "\n" for r in res), encoding="utf-8")
    for r in res:
        print("%-8s seed %d  %-28s runs %2d  rank %4d/%d  score %+.4f  wrong %+.4f±%.4f max %+.4f  z %+6.2f  dial %2d/%2d" % (
            r["kind"], r["seed"], r["alphabet"][:28], r["runs"], r["rank"], r["of"], r["score"], r["wrong_mean"],
            r["wrong_sd"], r["wrong_max"], r["z"], r["dial_recovered"], r["dial_planted"]))
    for k in os.environ.get("DIAG_KINDS", "random,keyword").split(","):
        rs = [r for r in res if r["kind"] == k]
        print("%s: rank-1 in %d/%d, median z %+.2f" % (k, sum(r["rank"] == 1 for r in rs), len(rs),
                                                      float(np.median([r["z"] for r in rs]))))
