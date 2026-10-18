# ABOUTME: Checks lane W's vectorised scorer against dodge_aware_scorer.score, the clock trace
# ABOUTME: against quagmire_dodge.encipher, and the clock word chain against the true bases.
"""Run before any measurement: python agents/laneW_clock_dodge/verify_port.py

1. das.score (the community's own, unmodified) equals clock_lib.score_odo on odometer keys.
2. clock_trace reproduces quagmire_dodge.encipher exactly.
3. The clock word maps equal the inverse of base0_inv[base_w] (the true bases of the trace).
4. Oracle: with the true phase of every rune, one assignment recovers base_0 (fraction of 29).
5. Timing per scored key, one core.
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I hides the script folder
import clock_lib as L  # noqa: E402
import dodge_aware_scorer as das
import doublet_phase_test as odo
import quagmire_dodge as qd
from base_free_verifier import log_frequencies
from pure_quagmire_restart import matched_register
from pure_quagmire_restart import schedule as odo_schedule
from quagmire_runner import conj_shift

M = 29


def main() -> int:
    ok = True
    logf = log_frequencies()
    lens = L.lp_lens(400)
    pools = L.register_pools()
    print(f"register: {len(lens)} words, {sum(lens)} runes; PROSE_CACHE via DODGE_PROSE")

    # 1. odometer: the vectorised copy against the community's own score
    worst = 0.0
    for seed in (11, 12, 13):
        rng = random.Random(seed)
        K = rng.sample(range(M), M)
        offs = odo_schedule(rng)
        start = (rng.randrange(M), rng.randrange(M))
        plain = matched_register(rng, lens, pools)
        cipher = odo.encipher(plain, K, offs, start, 0, "advance")
        st = L.Stream(cipher)
        ref = das.score(cipher, K, offs, start, logf)
        mine, _v, _p = L.score_odo(st, K, offs, start, logf)
        worst = max(worst, abs(ref - mine))
        print(f"1. odometer seed {seed}: das.score {ref:.12f}  vectorised {mine:.12f}  diff {abs(ref - mine):.2e}")
    ok &= worst < 1e-9
    print(f"1. worst difference {worst:.2e}  -> {'PASS' if worst < 1e-9 else 'FAIL'}")

    # 2 and 3. clock trace against the community encipher, and the chain against the bases
    rng = random.Random(21)
    K = rng.sample(range(M), M)
    offs = qd.schedule(rng, zeros=1)
    alpha = qd.alphabets(K, offs)
    sigma = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
    base0 = rng.sample(range(M), M)
    plain = matched_register(rng, lens, pools)
    ref = qd.encipher(plain, base0, alpha, sigma)
    cipher, kappa, bases, fires = L.clock_trace(plain, base0, alpha, sigma)
    same = ref == cipher
    ok &= same
    print(f"2. clock_trace equals quagmire_dodge.encipher on {sum(lens)} runes: {same} ({fires} clock skips)")

    base0_inv = L.inverse(base0)
    st = L.Stream(cipher)
    alpha_arr = np.asarray(alpha, dtype=np.int64)
    ph_true_end = kappa[st.end]  # the phase of each word's last emission, from the trace
    G_chain = L.clock_word_maps(alpha_arr, sigma, ph_true_end)
    G_base = np.array([L.inverse(base0_inv[np.asarray(b)]) for b in bases])
    chain_ok = np.array_equal(G_chain, G_base)
    ok &= chain_ok
    print(f"3. clock word maps equal inverse(base0_inv[base_w]) for all {len(bases)} words: {chain_ok}")

    # 4. oracle: exact phase for every rune, one assignment (no alternation, no windows)
    rows = np.arange(st.N)
    G = G_chain[st.owner]
    invA = L._inv_rows(alpha_arr)
    plain_idx = invA[kappa[:, None], G]
    mat = np.zeros((M, M))
    np.add.at(mat, st.c, logf[plain_idx])
    _tot, pi = das.assign(mat)
    acc = float(np.mean(pi == base0_inv[np.arange(M)]))
    oracle_ok = acc >= 0.9
    print(f"4. oracle (true phase per rune): assignment recovers base_0 at {acc:.2f} of symbols "
          f"({'PASS' if oracle_ok else 'FAIL'})")

    # 5. timing
    t0 = time.time()
    s_clock, _v, _p = L.score_clock(st, K, offs, sigma, logf)
    t_clock = time.time() - t0
    rng2 = random.Random(5)
    K2 = rng2.sample(range(M), M)
    offs2 = odo_schedule(rng2)
    start2 = (0, 0)
    cipher2 = odo.encipher(plain, K2, offs2, start2, 0, "advance")
    st2 = L.Stream(cipher2)
    t0 = time.time()
    _s, _v, _p = L.score_odo(st2, K2, offs2, start2, logf)
    t_odo = time.time() - t0
    print(f"5. timing one core: clock path {t_clock * 1000:.1f} ms/key, odometer path {t_odo * 1000:.1f} ms/key "
          f"({sum(lens)} runes)")
    print(f"\nverify_port: {'ALL PASS' if ok else 'FAILURE'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
