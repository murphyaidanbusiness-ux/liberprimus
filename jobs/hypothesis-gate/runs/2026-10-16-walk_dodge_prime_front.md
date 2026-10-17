# Hypothesis gate: walk_dodge_prime_front (variant, 2026-10-16)

## Why this is gated
Variant of `walk_dodge_prime` (see `2026-10-16-walk_dodge_prime.md`). The prime-seeded family must place the one residue that the ladder never produces. The ladder has no residue 28 (phi stream) or 0 (prime stream), because the only prime congruent to 0 mod 29 is 29 itself. The parent places the missing residue LAST, so it becomes a fixed point of g. The hypothesis leaves this placement open, so the FIRST placement is gated as its own hypothesis.

## Hypothesis
Walk rule as in `walk_dodge_random`. Keys come from the prime/totient ladder at offset k0 (0 to 9,999) and stream choice (phi or prime). The same first-appearance orderings are used, with the missing residue placed FIRST in each ordering. g: five 5-cycles on the first 25 ordering runes, the last 4 fixed.

## Simulator
`jobs/hypothesis-gate/runs/walk_dodge_prime_front_cipher.py`, defining `encrypt(plain, words, rng)`. The key (k0, stream) is drawn from rng; five rng seeds give five different ciphertexts for one plaintext.

## Gate output (`gate_sim.py --seeds 3`)
```
cipher: walk_dodge_prime_front: as walk_dodge_prime, but the residue the ladder never produces is placed FIRST (not last)
seed 0: doublets 38 (27 within, 11 cross), lag-5 96/1828
  C1 IoC                               1.0219     LP2 1.0      FAIL
  C2 doublet rate                      0.00293    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0574     LP2 1.026    PASS
  C3 repeated words >=3                11         LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0525     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    11.0       LP2 23       FAIL
seed 1: doublets 15 (15 within, 0 cross), lag-5 118/1828
  C1 IoC                               0.9993     LP2 1.0      PASS
  C2 doublet rate                      0.00116    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0387     LP2 1.026    PASS
  C3 repeated words >=3                5          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0646     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    0.0        LP2 23       FAIL
seed 2: doublets 16 (1 within, 15 cross), lag-5 102/1828
  C1 IoC                               0.9996     LP2 1.0      PASS
  C2 doublet rate                      0.00124    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0298     LP2 1.026    PASS
  C3 repeated words >=3                10         LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0558     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    15.0       LP2 23       PASS
GATE FAIL: C1 C2 C6
```

Reading the seeds. Seed 0 (phi, k0 7028 in the gate draw sequence) fails C1 (1.0219), C2 (0.00293) and C6 (11). Seed 1 fails C2 (0.00116), C6 (0) and C5 soft (0.0646). Seed 2 fails C2 (0.00124) and passes C1 and C6. Gate draws: seeds 1000 to 1002.

## Key-draw census (not the gate; `tools/walk_draws.py --draws 300`, rng seeds 5000 to 5299)
| constraint | draws passing (of 300) |
| --- | --- |
| C1 IoC | 273 |
| C2 doublet rate | 133 |
| C2b conditional IoC | 298 |
| C3 repeated words | 268 |
| C6 cross-word doublets | 93 |
| all hard constraints | **42 (14%)** |

Doublet rate: median 0.0042, range 0 to 0.0185. This matches the uniform random family (`2026-10-16-walk_dodge_random.md`: 43 of 300), so the front placement behaves like random keys.

## Verdict
**EXCLUDED by C1 C2 C6** (gate FAIL; C1 on seed 0, C2 on seeds 0, 1 and 2, C6 on seeds 0 and 1).

The FRONT placement removes the forced fixed point. The family then behaves like the uniform random family: 14% of keys pass every hard constraint, and the three-seed gate reads a typical key. As with the others, this does not show that no key in the family passes.

## Predictions for the non-deciding constraints
- C4: plaintext word lengths, -5.69 on every draw (LP2 +0.9); INFO.
- C5: 0.0525, 0.0646 (soft fail) and 0.0558 on the three seeds. Not discriminating.

## Prior coverage
Grep terms: `Oosterhof`, `dodge`, `doublet`, `skip`, `clock`, `walk`, `totient`, `prime`, `phi`.
Files searched: `REPORT.md`, `REPORT_ROUND2.md`, `toolbox/CONSTRAINTS.md`, `dl/dukotah/liber-primus/LEDGER.json`, `dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`, `dl/leo/docs/FINDINGS.md`, `agents/laneK_walk_search/RESULTS.md`, `agents/laneL_keyword_walk/RESULTS.md`, `agents/laneC_gematria_structure/RESULTS.md`.
Hits: the walk family is covered by lanes J, K and L (see the parent report). Lane L's keyword grids use rune order, which equals prime-value order because the Gematria primes increase with the index (`agents/laneL_keyword_walk/RESULTS.md`, alphabet enumeration). That is not the successive-primes-mod-29 ordering used here. The ladder as a keystream and as a seed generator was tested elsewhere (`dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, Round 22 X4 and Round 26 C; lane C), but not as walk permutations.

## PROOF (`jobs/hypothesis-gate/PROOF.md`)
- [pass] Names the hypothesis and links `runs/walk_dodge_prime_front_cipher.py`; the simulator defines `encrypt(plain, words, rng)`.
- [pass] The full `gate_sim.py --seeds 3` output is pasted above, including the final GATE line.
- [pass] Verdict: `EXCLUDED by C1 C2 C6`.
- [pass] No PROCEED after a gate FAIL; every failed id is named.
- [pass] Prior-coverage line lists the grep terms and the files searched.
- [n/a] PROCEED design: not required.
- [pass] Every key is drawn from rng; five seeds give five different ciphertexts.
