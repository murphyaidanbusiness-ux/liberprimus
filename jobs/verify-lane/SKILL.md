---
name: verify-lane
description: Independently re-derives a finished lane's headline numbers with fresh code and replays its control on fresh data. Use before any lane's result is reported, published or built on.
---

## Trigger
A lane hands back a RESULTS.md, or the orchestrator asks for a number to be checked.

## Inputs
- The lane's `agents/<lane>/RESULTS.md` and its output files (read them; do not import its code).
- `lp/lpdata.py`, `toolbox/` (fingerprint, nulls, score, runes).
- Worked examples: `data/fixture/laneQ_verify.py`, `lp/t7_lag5_lines.py`, `agents/laneO_quagmire_dodge/diag_alphabet_kind.py`.

## Steps
1. List the headline numbers in the lane's summary and verdict.
2. For each, write the shortest independent computation in `runs/<lane>_verify.py`, from the loader and the toolbox only.
3. Run it; record the lane's value and ours side by side.
4. Replay one control on fresh data: a new seed, a new plaintext, or the same key enciphered by your own code.
5. Where a number differs, find out why before reporting (definition, data slice, off-by-one, a bug on either side).
6. When the lane's verdict rests on a failed control, test whether the failure is the lane's code, the plant, or the method, by replaying the same key on fresh plaintext.
7. Write `runs/YYYY-MM-DD-<lane>.md` with the table, the replay and what it means for the verdict.
8. Run PROOF.md and fix every fail before returning.

## Rules
- Fresh code, same data. Sharing the lane's code would only repeat its bugs.
- A reproduced number is reported plainly; a difference is reported with both values, never smoothed over.
