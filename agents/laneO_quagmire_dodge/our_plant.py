# ABOUTME: Lane O control: plants a keyword key in the odometer + dodge family the sweep searches,
# ABOUTME: then asks the sweep's own score path for the planted key's rank over every schedule.
"""An independent planted control for the zero-offset dodge sweep.

The sweep searches the ODOMETER + dodge family (quagmire-odometer.md): a keyed alphabet K, a
one-zero schedule, the inner dial a advancing by one every word and the outer dial b when a
wraps, with the doublet dodge on top. The community selftest plants its own random K with
doublet_phase_test.encipher ("advance"), so passing it shows only that the port agrees with
the community's plant. This control is ours:

  keyword    a random word from the sweep's priority vocabulary, through one of the four alphabet
             rules of keyword_exhaustion.alphabets (the selftest uses a random K, not a keyword)
  schedule   a random one-zero schedule from dodge_priority_sweep.surviving_schedules, the
             sweep's own generator, bands off as the sweep runs
  dials      random start dials (a0, b0)
  register   matched_register over the LP's own word lengths, all 2,928 words, so the planted
             corpus has held-out text for adjudicate.py
  cipher     doublet_phase_test.encipher, the sweep's odometer model with the dodge on
  score      dodge_priority_sweep.score_key over EVERY schedule of that alphabet (keep = all,
             29 inner dials each, outer absorbed) on the first 400 words, as the sweep does

Pass = the planted schedule ranks 1. Reported: rank, score, z against the rest, recovered dial.

Not covered: quagmire_dodge.encipher, whose base steps by alpha_k composed with sigma each word
(a clock-dependent walk). That is a different variant from the odometer the scorer models, so
this control does not test it.

    python agents/laneO_quagmire_dodge/our_plant.py --nproc 8

Environment: source agents/laneO_quagmire_dodge/env.sh first.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PORT = Path(os.environ.get("DODGE_PORT", REPO / "dl" / "aldegonde_port"))
sys.path[:0] = [str(PORT / "src"), str(PORT / "experiments")]

import dodge_priority_sweep as dps  # noqa: E402
import doublet_phase_test as odo  # noqa: E402
from base_free_verifier import log_frequencies  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from keyword_exhaustion import alphabets as keyed_alphabets  # noqa: E402
from keyword_exhaustion import kw_runes  # noqa: E402
from pure_quagmire_restart import matched_register  # noqa: E402
from quagmire_runner import load_register  # noqa: E402
from quagmire_schedule_census import lp_words  # noqa: E402
from quagmire_ungated_sweep import priority_vocabulary  # noqa: E402

M = 29
SEED = 7301  # fixed; the community selftest uses 3301
OUT = REPO / "agents" / "laneO_quagmire_dodge" / "out"
_CORPUS = None
_LOGF = None


def _init(cipher, logf):
    global _CORPUS, _LOGF
    _CORPUS = dps.Corpus(cipher)
    _LOGF = logf


def _score_chunk(K, chunk):
    best = dps.score_key(K, chunk, _CORPUS, _LOGF, keep=len(chunk))
    return [(float(s), [int(x) for x in o], int(d)) for s, o, d in best]


def score_every_schedule(K, scheds, cipher, logf, nproc):
    """The sweep's score path (score_key) over every schedule, split across processes."""
    chunks = [c for c in np.array_split(scheds, max(1, nproc * 8)) if len(c)]
    t0 = time.time()
    with get_context("spawn").Pool(
        nproc, initializer=_init, initargs=(cipher, logf)
    ) as pool:
        parts = pool.starmap(_score_chunk, [(K, c) for c in chunks])
    rows = [row for part in parts for row in part]
    return rows, time.time() - t0


def summarise(rows, planted_sched):
    rows = sorted(rows, key=lambda r: -r[0])
    pos = next(i for i, (_s, o, _d) in enumerate(rows) if o == planted_sched)
    truth = rows[pos]
    others = np.array([s for s, o, _d in rows if o != planted_sched])
    z = (truth[0] - others.mean()) / others.std()
    print(f"schedules scored: {len(rows):,}")
    print(
        f"planted schedule ranks {pos + 1} of {len(rows):,}; score {truth[0]:+.4f} vs "
        f"rest mean {others.mean():+.4f} sd {others.std():.4f}; z = {z:+.2f}; "
        f"best other {others.max():+.4f}"
    )
    return {
        "rank": pos + 1,
        "of": len(rows),
        "score": truth[0],
        "z": float(z),
        "best_other": float(others.max()),
        "recovered_dial": truth[2],
        "top5": [{"score": round(s, 5), "sched": o, "dial": d} for s, o, d in rows[:5]],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nproc", type=int, default=8)
    args = ap.parse_args()

    rng = random.Random(SEED)
    lens400 = dps._lens()
    _words, _keys = dps._prepare(lens400)  # fills dps._W: tables, bands, log table, corpus
    tables, bands = dps._W["tables"], dps._W["bands"]
    logf = log_frequencies()

    vocab = sorted({w for w in priority_vocabulary() if kw_runes(w)})
    word = rng.choice(vocab)
    rules = list(keyed_alphabets(kw_runes(word)))
    rule, K = rules[rng.randrange(len(rules))]
    scheds = dps.surviving_schedules(K, tables, bands)
    sched = [int(x) for x in scheds[rng.randrange(len(scheds))]]
    assert sum(sched) % M == 0 and sched.count(0) == 1, "planted schedule must be one-zero"
    start = (rng.randrange(M), rng.randrange(M))
    print(f"planted keyword {word!r}, rule {rule}, schedule {sched}, start dials {start}")
    print(f"surviving schedules for this alphabet: {len(scheds):,}")

    pools, _t, _f = load_register(PROSE_CACHE)
    full_lens = [len(w) for w in lp_words()]
    plain = matched_register(rng, full_lens, pools)
    cipher = odo.encipher(plain, K, sched, start, 0, "advance")
    print(f"odometer + dodge cipher: {len(cipher)} words, {sum(map(len, cipher))} runes")

    rows, dt = score_every_schedule(K, scheds, cipher[:400], logf, args.nproc)
    print(f"scored on the first 400 words in {dt:.1f}s on {args.nproc} workers")
    res = summarise(rows, sched)
    print(
        f"recovered inner dial {res['recovered_dial']}, planted start dial {start[0]} "
        "(the outer dial is absorbed by the free bijection, so it is not scored)"
    )
    verdict = "PASS" if res["rank"] == 1 else "FAIL"
    print(f"\nplant control: {verdict} (planted rank {res['rank']})")

    OUT.mkdir(parents=True, exist_ok=True)
    result = {
        "seed": SEED,
        "keyword": word,
        "rule": rule,
        "K": [int(x) for x in K],
        "schedule": sched,
        "start_dials": list(start),
        "cipher": "doublet_phase_test.encipher, odometer, dodge 'advance'",
        "register": "matched_register, all 2928 LP word lengths",
        "scored": res,
        "seconds": round(dt, 1),
        "verdict": verdict,
    }
    (OUT / "our_plant_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (OUT / "planted_corpus.json").write_text(
        json.dumps(
            {
                "keyword": word,
                "rule": rule,
                "K": [int(x) for x in K],
                "schedule": sched,
                "start_dials": list(start),
                "words": cipher,
            }
        ),
        encoding="utf-8",
    )
    cand = {
        "score": res["score"],
        "keyword": word,
        "K": [int(x) for x in K],
        "sched": sched,
        "dial": res["recovered_dial"],
    }
    (OUT / "planted_candidate.jsonl").write_text(json.dumps(cand) + "\n", encoding="utf-8")
    print(f"written to {OUT}")


if __name__ == "__main__":
    main()
