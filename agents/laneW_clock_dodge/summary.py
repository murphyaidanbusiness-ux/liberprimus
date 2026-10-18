# ABOUTME: Lane W final numbers: rank-1 and z under each tie and category rule, saved to out/summary.json.
"""python -I -X utf8 agents/laneW_clock_dodge/summary.py  (reads out/measure.json)"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diagnose as D  # noqa: E402
import measure  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"


def odo_block(res):
    rows = []
    for r in sorted((x for x in res if x["kind"] == "odo"), key=lambda x: x["idx"]):
        idx = r["idx"]
        rng = random.Random(7000 + idx)
        K = rng.sample(range(D.M), D.M)
        offs = D.odo_schedule(rng)
        start = (rng.randrange(D.M), rng.randrange(D.M))
        D.matched_register(rng, D.LENS, D.POOLS)
        wrong = measure._wrong_odo(rng, K, offs, start, 2000)
        equiv = np.asarray([(K2 == K) and (o2 == offs) and (s2[0] == start[0]) for K2, o2, s2, _c in wrong])
        cats = np.asarray([c for *_x, c in wrong])
        w = np.asarray(r["wrong_scores"])
        t = r["true"]
        keep_nondials = cats != 2
        keep_nonequiv = ~equiv
        rows.append(dict(
            idx=idx, true=t,
            strict=bool(t > w.max()),
            ties_win=bool(t >= w.max() - D.TOL),
            nondials_strict=bool(t > w[keep_nondials].max()),
            nonequiv_strict=bool(t > w[keep_nonequiv].max()),
            z_all=float((t - w.mean()) / w.std()),
            z_nonequiv=float((t - w[keep_nonequiv].mean()) / w[keep_nonequiv].std()),
            equivalent=int(equiv.sum()),
        ))
    return rows


def clock_block(res):
    rows = []
    for r in sorted((x for x in res if x["kind"] == "clock"), key=lambda x: x["idx"]):
        w = np.asarray(r["wrong_scores"])
        t = r["true"]
        rows.append(dict(idx=r["idx"], true=t, strict=bool(t > w.max()), z_all=float((t - w.mean()) / w.std()),
                         best_wrong=float(w.max()), phase_accuracy=r["phase_accuracy"],
                         base0_accuracy=r["base0_accuracy"], fires=r["fires"]))
    return rows


def main() -> None:
    data = json.loads((OUT / "measure.json").read_text(encoding="utf-8"))
    res = data["results"]
    od = odo_block(res)
    cl = clock_block(res)
    n = len(od)
    summary = {
        "odometer": {
            "n": n,
            "rank1_strict_ties_lose": sum(r["strict"] for r in od),
            "rank1_ties_count_as_wins": sum(r["ties_win"] for r in od),
            "rank1_dials_category_excluded": sum(r["nondials_strict"] for r in od),
            "rank1_equivalent_keys_removed": sum(r["nonequiv_strict"] for r in od),
            "median_z_all_2000": float(np.median([r["z_all"] for r in od])),
            "median_z_equivalents_removed": float(np.median([r["z_nonequiv"] for r in od])),
            "equivalent_keys_per_plant_median": float(np.median([r["equivalent"] for r in od])),
            "misses_equivalents_removed": [r["idx"] for r in od if not r["nonequiv_strict"]],
        },
        "clock": {
            "n": len(cl),
            "rank1_strict": sum(r["strict"] for r in cl),
            "median_z_all_2000": float(np.median([r["z_all"] for r in cl])),
            "median_phase_accuracy": float(np.median([r["phase_accuracy"] for r in cl])),
            "median_base0_accuracy": float(np.median([r["base0_accuracy"] for r in cl])),
            "median_fires_per_1802_runes": float(np.median([r["fires"] for r in cl])),
            "ties_in_sigma_category": int(sum(
                int(np.sum(np.abs(np.asarray(x["wrong_scores"]) - x["true"]) < D.TOL))
                for x in res if x["kind"] == "clock")),
        },
        "throughput_seconds_per_key_median": {
            k: float(np.median([r["seconds_per_key"] for r in res if r["kind"] == k])) for k in ("odo", "clock", "literal")
        },
        "wall_seconds": data["wall_seconds"],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
