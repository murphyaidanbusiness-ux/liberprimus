---
name: attack-lane
description: Runs one controlled attack on LP2 for a cipher family that passed the hypothesis gate, with a planted-key control, a size-matched null and oracle adjudication. Use when asked to attack, sweep, search or test a key model on LP2.
---

## Trigger
The orchestrator assigns a lane letter and a family whose hypothesis-gate report says `PROCEED`.

## Inputs
- The gate report (`jobs/hypothesis-gate/runs/...`) and its simulator `encrypt(plain, words, rng)`.
- `toolbox/CONSTRAINTS.md`; `toolbox/TECHNIQUES.md` for the method (hill climbing, beam search, crib drag, isomorphs ...).
- `toolbox/runes.py` (English runes for plants), `toolbox/nulls.py` (shuffles), `toolbox/score.py` (IoC, quadgrams).
- `docs/BRIEF_ROUND2.md` for this machine (16 cores, Python + numpy, MSVC at the path in `agents/laneO_quagmire_dodge/build_kernel.bat`).

## Steps
1. Write the decryptor and the search in `agents/lane<X>_<name>/`. Reuse the gate simulator as the encryptor.
2. Plant: encipher English from `toolbox/runes.english_stream` with a key drawn from the searched space; the search must return it at rank 1.
3. If the search is heuristic (annealing, beam, sampled starts), plant at least 20 keys and report `recovered k/n`; a miss rate is a power number, not a failure to hide.
4. Measure throughput on one core and state the full cost before a long run. Ask the orchestrator before anything over 2 hours.
5. Null: run the identical search on at least 20 shuffles from `toolbox/nulls.py`. Use `shuffle_increments` for chain-family models.
6. Real: run on LP2 (`lp/lpdata.unsolved()`, assert the SHA pin). Compare the best real score with the null max and give z.
7. Any best beating the null max clearly and reading as English goes to `python dl/dukotah/liber-primus/verify_solution.py --plaintext FILE` and `python lp/verify_candidate.py FILE`.
8. Write `RESULTS.md` from `tools/RESULTS_TEMPLATE.md`.
9. Run `python jobs/attack-lane/tools/check_results.py agents/lane<X>_<name>/RESULTS.md` and the reading lines of PROOF.md; fix every fail before returning.

## Rules
- Long jobs run at below-normal priority and leave memory for the owner's own work (check free RAM first).
- Do not claim a solve without the oracle passing. A clean null is the expected and useful result.
- Large intermediates end in `.bin` or `.npy` (git-ignored). Do not edit `lp/`, `toolbox/`, other lanes or `dl/`.
- Save any reusable helper to `tools/` here, or propose it for `toolbox/`, and link it.
