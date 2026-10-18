# ABOUTME: Lane W follow-up: tie and invariance checks on out/measure.json, a true-key decrypt
# ABOUTME: of one clock plant through the scorer's own word maps, oracle-path scores, accuracies.
"""python -I -X utf8 agents/laneW_clock_dodge/diagnose.py  (needs DODGE_PROSE set)"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clock_lib as L  # noqa: E402
import dodge_aware_scorer as das  # noqa: E402
import doublet_phase_test as odo  # noqa: E402
import measure  # noqa: E402  (generator code only; nothing runs at import)
import quagmire_dodge as qd  # noqa: E402
from base_free_verifier import log_frequencies  # noqa: E402
from pure_quagmire_restart import matched_register  # noqa: E402
from pure_quagmire_restart import schedule as odo_schedule  # noqa: E402
from quagmire_runner import conj_shift  # noqa: E402

M = 29
OUT = Path(__file__).resolve().parent / "out"
TOL = 1e-9
LENS = L.lp_lens(400)
POOLS = L.register_pools()
LOGF = log_frequencies()


def _cats(kind, n):
    base = ("alphabet", "schedule", "dials" if kind != "clock" else "sigma", "everything")
    return np.asarray([base[j % 4] for j in range(n)])


def tie_rows(results, kind, excluded):
    rows = []
    for r in sorted((x for x in results if x["kind"] == kind), key=lambda x: x["idx"]):
        w = np.asarray(r["wrong_scores"])
        cats = _cats(kind, len(w))
        t = r["true"]
        tie = np.abs(w - t) < TOL
        keep = cats != excluded
        rows.append(dict(
            idx=r["idx"], true=t, best_wrong=float(w.max()), best_cat=r["best_wrong_category"],
            ties=int(tie.sum()), ties_in_excluded=int((tie & ~keep).sum()),
            strict=bool(t > w.max()), ties_win=bool(t >= w.max() - TOL),
            excl_strict=bool(t > w[keep].max()), excl_ties_win=bool(t >= w[keep].max() - TOL),
        ))
    return rows


def summary(rows, label):
    n = len(rows)
    return (f"{label:<40} strict {sum(r['strict'] for r in rows):>2}/{n}  ties-win {sum(r['ties_win'] for r in rows):>2}/{n}"
            f"  excl-category strict {sum(r['excl_strict'] for r in rows):>2}/{n}"
            f"  excl-category ties-win {sum(r['excl_ties_win'] for r in rows):>2}/{n}")


def odo_equivalence(idx, scores_by_idx):
    """Regenerate plant idx and its wrong keys as measure.py did. A wrong key is EQUIVALENT to the
    plant if it keeps K and the schedule and changes only the outer dial b (same inner dial a)."""
    rng = random.Random(7000 + idx)
    K = rng.sample(range(M), M)
    offs = odo_schedule(rng)
    start = (rng.randrange(M), rng.randrange(M))
    matched_register(rng, LENS, POOLS)
    wrong = measure._wrong_odo(rng, K, offs, start, 2000)
    equiv = np.asarray([(K2 == K) and (offs2 == offs) and (s2[0] == start[0]) for K2, offs2, s2, _c in wrong])
    s = np.asarray(scores_by_idx[idx]["wrong_scores"])
    tie = np.abs(s - scores_by_idx[idx]["true"]) < TOL
    rest = ~equiv
    return dict(idx=idx, ties=int(tie.sum()), equivalent=int(equiv.sum()),
                ties_equal_equivalent=bool(np.array_equal(tie, equiv)),
                rank1_excluding_equivalent=bool(scores_by_idx[idx]["true"] > s[rest].max()),
                best_nonequivalent=float(s[rest].max()))


def start_invariance(idx, deltas):
    rng = random.Random(7000 + idx)
    K = rng.sample(range(M), M)
    offs = odo_schedule(rng)
    start = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, LENS, POOLS)
    cipher = odo.encipher(plain, K, offs, start, 0, "advance")
    st = L.Stream(cipher)
    base, v0, _ = L.score_odo(st, K, offs, start, LOGF)
    out = []
    for da, db in deltas:
        s2 = ((start[0] + da) % M, (start[1] + db) % M)
        s, v, _ = L.score_odo(st, K, offs, s2, LOGF)
        out.append((da, db, s - base, bool(np.array_equal(v, v0))))
    return start, base, out


def clock_plant(idx):
    rng = random.Random(9000 + idx)
    K = rng.sample(range(M), M)
    offs = qd.schedule(rng, zeros=1)
    alpha = np.asarray(qd.alphabets(K, offs), dtype=np.int64)
    sigma = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
    base0 = rng.sample(range(M), M)
    plain = matched_register(rng, LENS, POOLS)
    cipher, kappa, bases, fires = L.clock_trace(plain, base0, alpha.tolist(), sigma)
    return dict(K=K, offs=offs, alpha=alpha, sigma=sigma, base0=base0, plain=plain,
                cipher=cipher, kappa=kappa, bases=bases, fires=fires)


def clock_decrypt_check(P):
    """True K, schedule, sigma, base_0 and the TRUE phase of every rune, decrypt via the scorer's maps."""
    st = L.Stream(P["cipher"])
    alpha, kappa, sigma = P["alpha"], P["kappa"], P["sigma"]
    G = L.clock_word_maps(alpha, sigma, kappa[st.end])[st.owner]
    invA = L._inv_rows(alpha)
    y = L.inverse(P["base0"])[st.c]  # y = base_0^-1(c), the scorer's assigned image
    tinv = G[np.arange(st.N), y]  # T_w^-1(y) = A_k(p)
    p = invA[kappa, tinv]
    flat_plain = [r for word in P["plain"] for r in word]
    return p.tolist() == flat_plain, st.N, int(np.sum(p != np.asarray(flat_plain)))


def clock_oracle_score(P):
    """Scorer's own assignment, with the TRUE phase of every rune and the true word maps."""
    st = L.Stream(P["cipher"])
    alpha, kappa, sigma = P["alpha"], P["kappa"], P["sigma"]
    G = L.clock_word_maps(alpha, sigma, kappa[st.end])[st.owner]
    invA = L._inv_rows(alpha)
    plain_idx = invA[kappa[:, None], G]
    mat = np.zeros((M, M))
    np.add.at(mat, st.c, LOGF[plain_idx])
    total, v = das.assign(mat)
    return total / st.N, v


def main() -> None:
    data = json.loads((OUT / "measure.json").read_text(encoding="utf-8"))
    res = data["results"]
    odo_by = {r["idx"]: r for r in res if r["kind"] == "odo"}
    clk_by = {r["idx"]: r for r in res if r["kind"] == "clock"}

    print("== 1. ties with the true key in the measurement\n")
    odo_rows = tie_rows(res, "odo", "dials")
    clk_rows = tie_rows(res, "clock", "sigma")
    lit_rows = tie_rows(res, "literal", "dials")
    print(f"{'plant':>8}{'true':>12}{'best wrong':>13}{'best cat':>13}{'ties':>6}{'ties in dials':>15}")
    for r in odo_rows:
        print(f"{'odo ' + str(r['idx']):>8}{r['true']:>12.6f}{r['best_wrong']:>13.6f}{r['best_cat']:>13}"
              f"{r['ties']:>6}{r['ties_in_excluded']:>15}")
    print()
    print(summary(odo_rows, "odometer (dials category excluded)"))
    print(summary(clk_rows, "clock (sigma category excluded)"))
    print(summary(lit_rows, "literal clock on odometer path (dials excl.)"))

    print("\n== 1a. are the odometer ties exactly the keys with the same inner dial a?")
    for idx in range(20):
        e = odo_equivalence(idx, odo_by)
        print(f"  plant {idx:>2}: ties {e['ties']:>2}  equivalent (same K, schedule, a) {e['equivalent']:>2}  "
              f"ties = equivalent: {e['ties_equal_equivalent']}  rank-1 without equivalents: "
              f"{e['rank1_excluding_equivalent']} (best other {e['best_nonequivalent']:+.6f})")

    print("\n== 1b. start-dial invariance on odometer plants (score minus true; * = assignment changed)")
    for idx in range(5):
        start, base, out = start_invariance(idx, [(1, 0), (0, 1), (2, 0), (0, 5), (7, 3), (13, 11)])
        diffs = " ".join(f"{d:+.2e}{'' if same else '*'}" for _a, _b, d, same in out)
        print(f"  plant {idx} start {start} score {base:+.6f}: {diffs}")

    print("\n== 1c. clock sigma category: ties with the true key")
    print(f"  ties in the sigma category, all 20 plants: {sum(r['ties_in_excluded'] for r in clk_rows)}"
          f"  (any tie at all: {sum(r['ties'] for r in clk_rows)})")

    print("\n== 2. true-key decrypt of clock plants with the TRUE phase of every rune")
    for idx in range(3):
        P = clock_plant(idx)
        ok, n, bad = clock_decrypt_check(P)
        print(f"  plant {idx}: runes {n}, plaintext recovered exactly: {ok}, mismatches {bad}")

    print("\n== 3. clock accuracies from measure.json")
    cl = list(clk_by.values())
    pa = np.array([r["phase_accuracy"] for r in cl])
    ba = np.array([r["base0_accuracy"] for r in cl])
    print(f"  phase_accuracy  median {np.median(pa):.4f}  IQR {np.percentile(pa, 25):.4f}-{np.percentile(pa, 75):.4f}"
          f"  range {pa.min():.4f}-{pa.max():.4f}   (chance 0.2)")
    print(f"  base0_accuracy  median {np.median(ba):.4f}  IQR {np.percentile(ba, 25):.4f}-{np.percentile(ba, 75):.4f}"
          f"  range {ba.min():.4f}-{ba.max():.4f}   (chance 1/29 = {1 / 29:.4f})")
    oi = np.array([r["pi_identity_accuracy"] for r in odo_by.values()])
    print(f"  odometer identity accuracy median {np.median(oi):.4f}, range {oi.min():.4f}-{oi.max():.4f}")

    print("\n== 4. oracle path: the planted clock key scored with its TRUE phases vs the best of 2,000 wrong")
    wins = 0
    for idx in range(20):
        P = clock_plant(idx)
        oracle, v = clock_oracle_score(P)
        best = max(clk_by[idx]["wrong_scores"])
        wins += oracle > best
        print(f"  plant {idx:>2}: oracle {oracle:+.4f}  best wrong (fitted path) {best:+.4f}  "
              f"oracle beats all: {oracle > best}  base_0 recovered {float(np.mean(v == L.inverse(P['base0']))):.2f}")
    print(f"  oracle beats the best wrong key on {wins}/20 plants")


if __name__ == "__main__":
    main()
