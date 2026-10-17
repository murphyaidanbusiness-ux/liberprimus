# Hypothesis gate: Quagmire-odometer with the doublet dodge (lane O's family)

Gated 2026-10-16 by the orchestrator. Simulator: `quagmire_odometer_dodge_cipher.py` (random keyed alphabet, random
one-zero five-step schedule, random odometer dials, enciphered by the community's own `doublet_phase_test.encipher`
with `"advance"`, from the audited port in `dl/aldegonde_port`). Gate output for 3 seeds:
`2026-10-16-quagmire_odometer_dodge_gate.txt`.

**Verdict: PROCEED (gate pass, marginal C6 on 1 of 3 seeds).** The validated sweep is `agents/laneO_quagmire_dodge/`
(launch-ready, ~382 core-hours, ~89% power for a key from Cicada's vocabulary).

## Twelve-key spread (`gate_sim.py --seeds 12`, orchestrator)
| statistic | family over 12 random keys | LP2 |
|---|---|---|
| doublets | 87.4 mean (62 to 131) | 86 |
| cross-word doublets | 22.1 +- 6.2 (10 to 31) | 23 |
| cross-word share | 0.266 | 0.267 |
| within-word lag-5 rate | 0.0572 mean | 0.0494 |
| C2c (doublet positions mod 2..8) | uniform on every seed | uniform |

This is the only family simulated in round two that reproduces the lag-5 echo: every other family (dynamic substitution,
totient stream, the 1/5 toy) put lag 5 at or below chance (2.8-3.5%). It also passes C2c, because its exempt phase rides
on a clock that advances at each dodge, so surviving doublets do not pile up on one absolute residue. Under the old
"fail on any seed" rule, single keys failed C2 (131 doublets), C3 or C6; that rule was replaced by a majority rule (see
CHANGELOG), since each seed is a fresh key from the family.

Prior coverage: never swept (`dl/aldegonde_clone/hypotheses/quagmire-dodge.md` lines 244-282 and 373; lane O).
