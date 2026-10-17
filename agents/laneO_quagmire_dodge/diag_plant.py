# ABOUTME: Diagnostic for the failed odometer plant control: pinned-dial scores for three plants that
# ABOUTME: differ in keyword alphabet and schedule, on one register draw, to localise the miss.
import random, sys
from pathlib import Path
import numpy as np
REPO = Path(__file__).resolve().parents[2]
PORT = REPO / "dl" / "aldegonde_port"
sys.path[:0] = [str(PORT / "src"), str(PORT / "experiments")]
import dodge_priority_sweep as dps
import doublet_phase_test as odo
from base_free_verifier import log_frequencies
from dodge_score_kernel import score_dials
from ea_direction_test import PROSE_CACHE
from keyword_exhaustion import alphabets, kw_runes
from pure_quagmire_restart import matched_register
from quagmire_runner import load_register
from quagmire_schedule_census import lp_words
M = 29
logf = log_frequencies()
pools, _t, _f = load_register(PROSE_CACHE)
full_lens = [len(w) for w in lp_words()]
rng = random.Random(1)
plain = matched_register(rng, full_lens, pools)
Kkw = dict(alphabets(kw_runes("MOBIUS")))["R2 reversed"]
Krand = rng.sample(range(M), M)
sched_p = [25, 17, 14, 0, 2]
sched_s = [0, 7, 20, 8, 23]
def pinned_and_best(K, sched, start, label):
    cipher = odo.encipher(plain, K, sched, start, 0, "advance")[:400]
    logtab = dps.fast_log_table(K, sched, logf)
    true = float(score_dials(logtab, [(start[0], 0)], cipher)[0])
    grid = score_dials(logtab, [(t, 0) for t in range(M)], cipher)
    print(f"{label:<44} true dial {start[0]:>2}: {true:+.4f}   best dial {int(grid.argmax()):>2}: {grid.max():+.4f}")
pinned_and_best(Kkw, sched_p, (7, 8), "A keyword MOBIUS R2, planted schedule")
pinned_and_best(Krand, sched_p, (7, 8), "B random K, same planted schedule")
pinned_and_best(Kkw, sched_s, (21, 11), "C keyword MOBIUS R2, selftest schedule")
pinned_and_best(Krand, sched_s, (21, 11), "D random K, selftest schedule (community plant)")
