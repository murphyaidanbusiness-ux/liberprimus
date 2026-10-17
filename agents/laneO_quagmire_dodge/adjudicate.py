# ABOUTME: Held-out test for sweep candidates: scores each (keyed alphabet, schedule, dial) on the LP words
# ABOUTME: the sweep never scored, against 200 random keys from the sweep's own generator.
"""Does a candidate survive text it was not fitted to?

The sweep scores only the first SCORE_WORDS=400 words. A candidate is held out on the rest:
the words after the first 400 are cut into consecutive 400-word chunks (a remainder shorter
than 400 is dropped), so for the real corpus there are six chunks.

Dial convention. The candidate's recovered inner dial a0 is the odometer's inner shift at word
0 of the scored corpus, and the inner shift rises by one per word. So chunk m, starting at
global word g, is scored at the pinned inner dial (a0 + g) mod 29 with outer dial 0. The outer
dial is absorbed by the free bijection (dodge_score_kernel asserts it), and the kernel
re-fits the clock phase in every 18-rune window, so the chunk needs nothing else. The
best-dial variant instead takes the best of the 29 inner dials per chunk, as the sweep does.

Null. 200 random keys: K from the sweep's vocabulary alphabets, schedule from
surviving_schedules (the sweep's generator), random inner dial, scored on the same chunks.
Reported: the null mean, sd and max of the chunk-mean. A candidate is compared by z against the
null mean/sd and by its margin over the null max.

    python agents/laneO_quagmire_dodge/adjudicate.py --candidates FILE [--corpus lp|PLANTED.json]

--corpus lp scores the real LP corpus; a planted_corpus.json from our_plant.py scores that
planted cipher instead (the validation run). Environment: source agents/laneO_quagmire_dodge/env.sh.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
PORT = Path(os.environ.get("DODGE_PORT", REPO / "dl" / "aldegonde_port"))
sys.path[:0] = [str(PORT / "src"), str(PORT / "experiments")]

import dodge_priority_sweep as dps  # noqa: E402
from base_free_verifier import log_frequencies  # noqa: E402
from dodge_score_kernel import score_dials  # noqa: E402
from quagmire_schedule_census import lp_words  # noqa: E402

M = 29
SCORE_WORDS = dps.SCORE_WORDS  # 400: the words the sweep scored
CHUNK = 400
NULLS = 200
OUT = REPO / "agents" / "laneO_quagmire_dodge" / "out"


def load_corpus(spec: str) -> list[list[int]]:
    if spec == "lp":
        return lp_words()
    return json.loads(Path(spec).read_text(encoding="utf-8"))["words"]


def chunks_of(words):
    """(global start word, chunk) for each full CHUNK-word block after the first SCORE_WORDS."""
    held = words[SCORE_WORDS:]
    return [
        (SCORE_WORDS + m * CHUNK, held[m * CHUNK : (m + 1) * CHUNK])
        for m in range(len(held) // CHUNK)
    ]


def key_scores(K, sched, a0, chunks, logf) -> dict:
    logtab = dps.fast_log_table(K, sched, logf)
    pinned = [
        float(score_dials(logtab, [((a0 + g) % M, 0)], chunk)[0]) for g, chunk in chunks
    ]
    dials = [(t, 0) for t in range(M)]
    best = [float(score_dials(logtab, dials, chunk).max()) for _g, chunk in chunks]
    return {
        "pinned": pinned,
        "pinned_mean": float(np.mean(pinned)),
        "best_dial": best,
        "best_dial_mean": float(np.mean(best)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates", required=True)
    ap.add_argument("--corpus", default="lp")
    ap.add_argument("--nulls", type=int, default=NULLS)
    ap.add_argument("--seed", type=int, default=9301)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    words = load_corpus(args.corpus)
    chunks = chunks_of(words)
    lens400 = [len(w) for w in words[:SCORE_WORDS]]
    _w, keys = dps._prepare(lens400)  # tables, bands, and the sweep's keyed alphabets
    tables, bands = dps._W["tables"], dps._W["bands"]
    logf = log_frequencies()
    print(
        f"corpus {args.corpus}: {len(words)} words; held out {len(words) - SCORE_WORDS} words; "
        f"{len(chunks)} chunks of {CHUNK} starting at words {[g for g, _ in chunks]}"
    )

    rng = random.Random(args.seed)
    nulls = []
    for _ in range(args.nulls):
        _name, K = keys[rng.randrange(len(keys))]
        scheds = dps.surviving_schedules(K, tables, bands)
        sched = [int(x) for x in scheds[rng.randrange(len(scheds))]]
        a0 = rng.randrange(M)
        nulls.append(key_scores(K, sched, a0, chunks, logf))
    null_p = np.array([n["pinned_mean"] for n in nulls])
    null_b = np.array([n["best_dial_mean"] for n in nulls])
    stats = {
        "n": len(nulls),
        "pinned": {"mean": float(null_p.mean()), "sd": float(null_p.std(ddof=1)), "max": float(null_p.max())},
        "best_dial": {"mean": float(null_b.mean()), "sd": float(null_b.std(ddof=1)), "max": float(null_b.max())},
    }
    print(
        f"null ({len(nulls)} random keys): pinned chunk-mean mean {stats['pinned']['mean']:+.4f} "
        f"sd {stats['pinned']['sd']:.4f} max {stats['pinned']['max']:+.4f}"
    )
    print(
        f"null best-dial chunk-mean mean {stats['best_dial']['mean']:+.4f} "
        f"sd {stats['best_dial']['sd']:.4f} max {stats['best_dial']['max']:+.4f}"
    )

    cands = []
    for line in Path(args.candidates).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        s = key_scores(rec["K"], rec["sched"], rec["dial"], chunks, logf)
        s.update(
            {
                "keyword": rec.get("keyword"),
                "first400_score": rec.get("score"),
                "sched": rec["sched"],
                "dial": rec["dial"],
                "z_pinned": (s["pinned_mean"] - stats["pinned"]["mean"]) / stats["pinned"]["sd"],
                "margin_pinned_over_null_max": s["pinned_mean"] - stats["pinned"]["max"],
                "z_best_dial": (s["best_dial_mean"] - stats["best_dial"]["mean"]) / stats["best_dial"]["sd"],
                "margin_best_dial_over_null_max": s["best_dial_mean"] - stats["best_dial"]["max"],
            }
        )
        cands.append(s)
        print(
            f"{str(rec.get('keyword')):<16} sched {rec['sched']} dial {rec['dial']:>2}  "
            f"held-out pinned mean {s['pinned_mean']:+.4f} (z {s['z_pinned']:+.1f}, "
            f"margin {s['margin_pinned_over_null_max']:+.4f})  best-dial mean "
            f"{s['best_dial_mean']:+.4f} (z {s['z_best_dial']:+.1f})  first-400 score {rec.get('score')}"
        )

    out = Path(args.out) if args.out else OUT / f"adjudicate_{Path(args.candidates).stem}_{Path(args.corpus).stem}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "candidates": args.candidates,
                "corpus": args.corpus,
                "chunk_starts": [g for g, _ in chunks],
                "chunk_words": CHUNK,
                "null": stats,
                "null_seed": args.seed,
                "candidate_results": cands,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"written to {out}")


if __name__ == "__main__":
    main()
