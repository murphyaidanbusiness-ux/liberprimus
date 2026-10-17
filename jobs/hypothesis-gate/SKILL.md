---
name: hypothesis-gate
description: Decides whether a proposed LP2 cipher hypothesis is worth an attack lane, by simulating it on English and grading the result against the LP2 fingerprint. Use before spending compute on any new cipher family or key model.
---

## Trigger
A new cipher or key-source idea, from a survey, the gap audit, the community, or the orchestrator.

## Inputs
- The hypothesis, in words, from the orchestrator.
- `toolbox/CONSTRAINTS.md` (the fingerprint and the quick exclusions), `toolbox/fingerprint.py`.
- `tools/gate_sim.py` and the fixture ciphers in `data/fixture/` as examples of the simulator format.
- Prior coverage: `REPORT.md`, `REPORT_ROUND2.md`, and the ledgers listed in `toolbox/CONSTRAINTS.md`.

## Steps
1. Check the quick exclusions in `toolbox/CONSTRAINTS.md`. If one applies, still simulate it, because the gate output is the evidence.
2. Write the cipher as `runs/<hypothesis>_cipher.py` with `encrypt(plain, words, rng)`, following `data/fixture/otp_dodge5.py`. Use a random key from `rng` of the hypothesis's real size and form.
3. Run `python jobs/hypothesis-gate/tools/gate_sim.py runs/<hypothesis>_cipher.py --seeds 3`.
4. Grep for prior coverage (family name, synonyms, key source) in the reports and ledgers; record the terms and hits.
5. Write `runs/YYYY-MM-DD-<hypothesis>.md`: the hypothesis, the simulator link, the full gate output, prior coverage, the verdict.
6. Verdict: `EXCLUDED by <ids>` on any hard fail; `ALREADY TESTED by <lane/ledger>` if covered; otherwise `PROCEED` with the key space and a planted-control and null design.
7. Run PROOF.md and fix every fail before returning.

## Rules
- A gate fail is a result, not a reason to tweak the simulator until it passes. If a variant of the hypothesis might pass, gate the variant as its own hypothesis and say so.
- `GATE PASS (marginal: ...)` means a minority of random keys failed; report it and, for a PROCEED, rerun with `--seeds 12` to show LP2 sits inside the family's spread.
- C4 (layout) and C5 (the lag-5 echo) are reported but do not decide the gate. Say what the hypothesis predicts for them.
- Simulate on at least LP2's length (12,956 runes); the bands are scaled to that size.
- When keys vary a lot within a family, or the key space is small, run `tools/walk_draws.py <cipher> --draws 300` (or `--census` to grade every key) and report the fraction of keys that pass; a small passing set is an attack target, not an exclusion.
- Save any helper you write to `tools/` and link it here.
