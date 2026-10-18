# Gate: Quagmire-odometer dodge, "hold" variant (2026-10-17, orchestrator)

Cipher: `quagmire_odometer_dodge_hold_cipher.py`, the community's `doublet_phase_test.encipher` with variant `"hold"`
(on a would-be repeat the rune is re-emitted with the previous phase and the clock does not advance). It is the same as
lane O's gated family except for the preventer; the community's `dodge_aware_scorer` self-test plants both variants, but
the gate, the community sweep and lane O tiers A+B planted `"advance"` only. Found while merging the exhaustion census.

Command: `PYTHONUTF8=1 PYTHONPATH=dl/aldegonde_port/src python jobs/hypothesis-gate/tools/gate_sim.py
jobs/hypothesis-gate/runs/quagmire_odometer_dodge_hold_cipher.py --seeds 12`. Output: `2026-10-17-quagmire_odometer_dodge_hold_gate.txt`.

**Verdict: GATE PASS (marginal C3, 1 of 12 seeds).** Means over 12 random keys: doublets 90.0 +- 7.5 (LP2 86), cross-word
21.2 +- 4.5 (LP2 23), cross-word share 0.236, lag-5 within-word rate 5.8% (LP2 4.94%; soft C5 above its band on 3 seeds).
Every seed passes C1, C2, C2b, C2c and C6.

**Is it already covered?** Yes, at about the same power as `"advance"`. Lane O's sweep scorer (`score_key`, the MSVC
kernel, clock phase refitted per 18-rune window) recovers 18 of 20 planted `"hold"` keyword keys at rank 1 against 2,000
wrong schedules each (median z +22.8; misses ENLIGHTENMENT/R4 rank 22 and DUTY/R3 rank 79), and 18 of 20 plants score
above +0.75, against tiers A and B's best real scores of +0.706 and +0.720. The adjudicator scores through the same
kernel. See `agents/laneO_quagmire_dodge/RESULTS.md` section 11.
