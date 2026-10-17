# ABOUTME: Diagnostic: true-dial score of the sweep's own scorer on planted keyword alphabets versus
# ABOUTME: random alphabets, same register, schedule and start dial, to see whether the miss is systematic.
import random, sys
from pathlib import Path
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
from quagmire_ungated_sweep import priority_vocabulary
M = 29
logf = log_frequencies()
pools, _t, _f = load_register(PROSE_CACHE)
full_lens = [len(w) for w in lp_words()]
rng = random.Random(5)
plain = matched_register(rng, full_lens, pools)
sched, start = [25, 17, 14, 0, 2], (7, 8)
def true_dial_score(K):
    cipher = odo.encipher(plain, K, sched, start, 0, "advance")[:400]
    lt = dps.fast_log_table(K, sched, logf)
    return float(score_dials(lt, [(start[0], 0)], cipher)[0])
vocab = sorted({w for w in priority_vocabulary() if kw_runes(w)})
kw = []
for word in rng.sample(vocab, 12):
    rules = list(alphabets(kw_runes(word)))
    rule, K = rules[rng.randrange(len(rules))]
    kw.append((word, rule, true_dial_score(K)))
rnd = [true_dial_score(rng.sample(range(M), M)) for _ in range(12)]
for word, rule, s in kw:
    print(f"keyword {word:<16} {rule:<14} true-dial score {s:+.4f}")
print(f"keyword alphabets: mean {sum(s for *_, s in kw)/len(kw):+.4f}  min {min(s for *_, s in kw):+.4f}  max {max(s for *_, s in kw):+.4f}")
print(f"random alphabets:  mean {sum(rnd)/len(rnd):+.4f}  min {min(rnd):+.4f}  max {max(rnd):+.4f}")
