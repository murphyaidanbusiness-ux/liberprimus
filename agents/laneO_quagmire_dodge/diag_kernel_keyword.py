# ABOUTME: Diagnostic: is the MOBIUS R2 keyword alphabet a valid permutation, and do the C kernel and the
# ABOUTME: Python reference agree on it (the random-K parity test is the only one run so far)?
import random, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
PORT = REPO / "dl" / "aldegonde_port"
sys.path[:0] = [str(PORT / "src"), str(PORT / "experiments")]
import dodge_priority_sweep as dps
import doublet_phase_test as odo
from base_free_verifier import log_frequencies
from dodge_aware_scorer import score
from dodge_score_kernel import score_dials, log_table
from ea_direction_test import PROSE_CACHE
from keyword_exhaustion import alphabets, kw_runes
from pure_quagmire_restart import matched_register
from quagmire_runner import load_register
from quagmire_schedule_census import lp_words
M = 29
logf = log_frequencies()
seq = kw_runes("MOBIUS")
K = dict(alphabets(seq))["R2 reversed"]
print("kw_runes(MOBIUS) =", seq)
print("K length", len(K), "is permutation of 0..28:", sorted(K) == list(range(M)))
pools, _t, _f = load_register(PROSE_CACHE)
full_lens = [len(w) for w in lp_words()]
plain = matched_register(random.Random(1), full_lens, pools)
sched, start = [25, 17, 14, 0, 2], (7, 8)
cipher = odo.encipher(plain, K, sched, start, 0, "advance")[:400]
flat = float(sum(logf) / M)
py = score(cipher, K, sched, (7, 0), logf) - flat
lt = dps.fast_log_table(K, sched, logf)
ref = log_table(K, sched, logf)
print("fast_log_table == reference log_table:", bool((lt == ref).all()))
kern = float(score_dials(lt, [(7, 0)], cipher)[0])
print(f"Python reference at dial 7: {py:+.5f}   C kernel at dial 7: {kern:+.5f}   diff {abs(py-kern):.2e}")
