# ABOUTME: Lane W measurement: plants odometer and clock-dependent keys, scores each against
# ABOUTME: 2,000 wrong keys with the dodge-aware score path, and writes out/measure.json.
"""Plant and score. Three tasks per planted index, run on four BelowNormal workers:

  odo      odometer key (doublet_phase_test.encipher, 'advance'), odometer score path
  clock    clock-dependent key (quagmire_dodge.encipher), clock word model in the same path
  literal  the same clock ciphertext scored by the UNMODIFIED odometer path (its own word
           model), planted dials (0,0), so it can see the key only if the walk is a shift

Each planted key is scored against N_WRONG wrong keys in four equal categories:
alphabet only, schedule only, sigma (clock) or dials (odometer), and everything.

    python -I -X utf8 agents/laneW_clock_dodge/measure.py [--planted 20] [--wrong 2000] [--kinds odo,clock,literal]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from multiprocessing import get_context
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clock_lib as L  # noqa: E402
import doublet_phase_test as odo  # noqa: E402
import quagmire_dodge as qd  # noqa: E402
from base_free_verifier import log_frequencies  # noqa: E402
from pure_quagmire_restart import matched_register  # noqa: E402
from pure_quagmire_restart import schedule as odo_schedule  # noqa: E402
from quagmire_runner import conj_shift  # noqa: E402

M = 29
OUT = Path(__file__).resolve().parent / "out"
G = {}


def _init():
    L.low_priority()
    G["lens"] = L.lp_lens(400)
    G["pools"] = L.register_pools()
    G["logf"] = log_frequencies()


def _wrong_odo(rng, K, offs, start, n):
    keys = []
    for j in range(n):
        cat = j % 4
        K2, offs2, start2 = K, offs, start
        if cat in (0, 3):
            K2 = rng.sample(range(M), M)
        if cat in (1, 3):
            offs2 = odo_schedule(rng)
        if cat in (2, 3):
            start2 = (rng.randrange(M), rng.randrange(M))
        keys.append((K2, offs2, start2, cat))
    return keys


def _wrong_clock(rng, K, offs, sigma, n):
    keys = []
    for j in range(n):
        cat = j % 4
        K2, offs2, sigma2 = K, offs, sigma
        if cat in (0, 3):
            K2 = rng.sample(range(M), M)
        if cat in (1, 3):
            offs2 = qd.schedule(rng, zeros=1)
        if cat in (2, 3):
            sigma2 = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
        keys.append((K2, offs2, sigma2, cat))
    return keys


def task_odo(idx, n_wrong):
    lens, pools, logf = G["lens"], G["pools"], G["logf"]
    rng = random.Random(7000 + idx)
    K = rng.sample(range(M), M)
    offs = odo_schedule(rng)
    start = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, lens, pools)
    cipher = odo.encipher(plain, K, offs, start, 0, "advance")
    st = L.Stream(cipher)
    t0 = time.time()
    true, v, _used = L.score_odo(st, K, offs, start, logf)
    wrong, cats = [], []
    for K2, offs2, start2, cat in _wrong_odo(rng, K, offs, start, n_wrong):
        s, _v, _p = L.score_odo(st, K2, offs2, start2, logf)
        wrong.append(s)
        cats.append(("alphabet", "schedule", "dials", "everything")[cat])
    wrong = np.asarray(wrong)
    res = L.summarise(true, wrong, cats)
    res["pi_identity_accuracy"] = float(np.mean(v == np.arange(M)))
    res["seconds_per_key"] = (time.time() - t0) / (n_wrong + 1)
    res.update(kind="odo", idx=idx, wrong_scores=wrong.tolist())
    return res


def _planted_clock(idx):
    rng = random.Random(9000 + idx)
    K = rng.sample(range(M), M)
    offs = qd.schedule(rng, zeros=1)
    alpha = qd.alphabets(K, offs)
    sigma = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
    base0 = rng.sample(range(M), M)
    plain = matched_register(rng, G["lens"], G["pools"])
    cipher, kappa, _bases, fires = L.clock_trace(plain, base0, alpha, sigma)
    return rng, dict(K=K, offs=offs, sigma=sigma, base0=base0, cipher=cipher, kappa=kappa, fires=fires)


def task_clock(idx, n_wrong):
    logf = G["logf"]
    rng, P = _planted_clock(idx)
    st = L.Stream(P["cipher"])
    t0 = time.time()
    true, v, used = L.score_clock(st, P["K"], P["offs"], P["sigma"], logf)
    fitted_phase = (used[st.win] + st.off) % 5
    phase_acc = float(np.mean(fitted_phase == P["kappa"]))
    pi_acc = float(np.mean(v == L.inverse(P["base0"])))
    wrong, cats = [], []
    for K2, offs2, sigma2, cat in _wrong_clock(rng, P["K"], P["offs"], P["sigma"], n_wrong):
        s, _v, _p = L.score_clock(st, K2, offs2, sigma2, logf)
        wrong.append(s)
        cats.append(("alphabet", "schedule", "sigma", "everything")[cat])
    wrong = np.asarray(wrong)
    res = L.summarise(true, wrong, cats)
    res["fires"] = P["fires"]
    res["phase_accuracy"] = phase_acc
    res["base0_accuracy"] = pi_acc
    res["seconds_per_key"] = (time.time() - t0) / (n_wrong + 1)
    res.update(kind="clock", idx=idx, wrong_scores=wrong.tolist())
    return res


def task_literal(idx, n_wrong):
    logf = G["logf"]
    rng, P = _planted_clock(idx)
    st = L.Stream(P["cipher"])
    start = (0, 0)
    true, _v, _p = L.score_odo(st, P["K"], P["offs"], start, logf)
    wrong, cats = [], []
    t0 = time.time()
    for K2, offs2, start2, cat in _wrong_odo(rng, P["K"], P["offs"], start, n_wrong):
        s, _v, _p = L.score_odo(st, K2, offs2, start2, logf)
        wrong.append(s)
        cats.append(("alphabet", "schedule", "dials", "everything")[cat])
    wrong = np.asarray(wrong)
    res = L.summarise(true, wrong, cats)
    res["seconds_per_key"] = (time.time() - t0) / (n_wrong + 1)
    res.update(kind="literal", idx=idx, wrong_scores=wrong.tolist())
    return res


def _run(task):
    kind, idx, n_wrong = task
    fn = {"odo": task_odo, "clock": task_clock, "literal": task_literal}[kind]
    out = fn(idx, n_wrong)
    print(f"{kind:<8}{idx:>3}  true {out['true']:+.4f}  best wrong {out['best_wrong']:+.4f} "
          f"({out['best_wrong_category']})  rank1 {out['rank1']}  z {out['z']:+.1f}", flush=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planted", type=int, default=20)
    ap.add_argument("--wrong", type=int, default=2000)
    ap.add_argument("--kinds", default="odo,clock,literal")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--out", default=str(OUT / "measure.json"))
    args = ap.parse_args()
    kinds = args.kinds.split(",")
    tasks = [(k, i, args.wrong) for k in kinds for i in range(args.planted)]
    t0 = time.time()
    ctx = get_context("spawn")
    with ctx.Pool(args.procs, initializer=_init) as pool:
        results = pool.map(_run, tasks, chunksize=1)
    wall = time.time() - t0
    summary = {}
    for kind in kinds:
        rs = [r for r in results if r["kind"] == kind]
        rank1 = sum(r["rank1"] for r in rs)
        summary[kind] = {
            "n": len(rs),
            "rank1": rank1,
            "median_z": float(np.median([r["z"] for r in rs])),
            "misses": [r["idx"] for r in rs if not r["rank1"]],
            "median_seconds_per_key": float(np.median([r["seconds_per_key"] for r in rs])),
            "wrong_per_planted": args.wrong,
        }
        if kind == "clock":
            summary[kind]["median_phase_accuracy"] = float(np.median([r["phase_accuracy"] for r in rs]))
            summary[kind]["median_base0_accuracy"] = float(np.median([r["base0_accuracy"] for r in rs]))
            summary[kind]["median_fires"] = float(np.median([r["fires"] for r in rs]))
        if kind == "odo":
            summary[kind]["median_pi_identity_accuracy"] = float(np.median([r["pi_identity_accuracy"] for r in rs]))
    OUT.mkdir(exist_ok=True)
    Path(args.out).write_text(json.dumps({"summary": summary, "wall_seconds": wall,
                                           "results": results}), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    print(f"wall {wall:.0f} s on {args.procs} procs")


if __name__ == "__main__":
    main()
