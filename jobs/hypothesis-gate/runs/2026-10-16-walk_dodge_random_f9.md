# Hypothesis gate: walk_dodge_random_f9 (variant, 2026-10-16)

## Why this is gated
Variant of `walk_dodge_random` (see `2026-10-16-walk_dodge_random.md`), gated as its own hypothesis because the C2 band admits one fixed-point count among order-5 steps. The within-word doublet rate is about 0.0262 x f/29 (0.0262 is the English within-word doublet rate on this stream, 339 of 12,955 pairs). That gives about 0.0036 for f = 4, 0.0081 for f = 9 and 0.0127 for f = 14, so f = 9 is the only count whose expected rate falls in [0.004, 0.010]. This is an approximation for a uniform fixed set; the census below is the measured check.

## Hypothesis
The same walk rule as `walk_dodge_random`. The only change is g: an order-5 permutation with 9 fixed points (four 5-cycles on 20 runes), drawn uniformly from rng. sigma and base0 are uniform permutations.

## Simulator
`jobs/hypothesis-gate/runs/walk_dodge_random_f9_cipher.py`, defining `encrypt(plain, words, rng)`. Every key is drawn from rng; five rng seeds give five different ciphertexts for one plaintext.

## Gate output (`gate_sim.py --seeds 3`)
```
cipher: walk_dodge_random_f9: doublet-dodge walk, uniform order-5 g with 9 fixed points, sigma and base0 from rng
seed 0: doublets 67 (53 within, 14 cross), lag-5 91/1828
  C1 IoC                               1.0144     LP2 1.0      FAIL
  C2 doublet rate                      0.00517    LP2 0.00664  PASS
  C2b conditional IoC                  1.0481     LP2 1.026    PASS
  C3 repeated words >=3                8          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0498     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    14.0       LP2 23       PASS
seed 1: doublets 255 (196 within, 59 cross), lag-5 112/1828
  C1 IoC                               1.0006     LP2 1.0      PASS
  C2 doublet rate                      0.01968    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0079     LP2 1.026    PASS
  C3 repeated words >=3                14         LP2 16       FAIL
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0613     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    59.0       LP2 23       FAIL
seed 2: doublets 131 (120 within, 11 cross), lag-5 104/1828
  C1 IoC                               1.0204     LP2 1.0      FAIL
  C2 doublet rate                      0.01011    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0359     LP2 1.026    PASS
  C3 repeated words >=3                15         LP2 16       FAIL
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0569     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    11.0       LP2 23       FAIL
GATE FAIL: C1 C2 C3 C6
```

Reading the seeds. Seed 0 fails C1 (IoC 1.0144). Seed 1 fails C2 (0.0197, too high), C3 (14 repeated words against the null band) and C6 (59). Seed 2 fails C1 (1.0204), C2 (0.01011, just above 0.010), C3 (15) and C6 (11).

## Key-draw census (not the gate; `tools/walk_draws.py --draws 300`, rng seeds 5000 to 5299)
| constraint | draws passing (of 300) |
| --- | --- |
| C1 IoC | 237 |
| C2 doublet rate | 124 |
| C2b conditional IoC | 283 |
| C3 repeated words | 267 |
| C6 cross-word doublets | 159 |
| all hard constraints | **57 (19%)** |

Doublet rate: median 0.0101, range 0.0012 to 0.0246. Cross-word doublets: median 27. The typical f = 9 key sits right at the top of the C2 band.

## Verdict
**EXCLUDED by C1 C2 C3 C6** (gate FAIL; C1 on seeds 0 and 2, C2 on seeds 1 and 2, C3 on seeds 1 and 2, C6 on seeds 1 and 2).

As for the parent family, this excludes the typical key. 19% of keys pass every hard constraint on English, which is not zero. The three-seed gate reads a typical key, so the FAIL does not show that no key with 9 fixed points reproduces LP2.

## Predictions for the non-deciding constraints
- C4: the plaintext's own word lengths, -5.69 on every draw (LP2 +0.9). Same as the parent (INFO).
- C5: within-word lag-5 rate 0.0498, 0.0613 and 0.0569 on the three seeds (seed 1 fails the soft band at 0.0613). Not discriminating.

## Prior coverage
Grep terms: `Oosterhof`, `dodge`, `doublet`, `skip`, `clock`, `walk`, `order-5`, `fixed point`, `power`.
Files searched: `REPORT.md`, `REPORT_ROUND2.md`, `toolbox/CONSTRAINTS.md`, `dl/dukotah/liber-primus/LEDGER.json`, `dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`, `dl/leo/docs/FINDINGS.md`, `agents/laneJ_lag5_echo/RESULTS.md`, `agents/laneK_walk_search/RESULTS.md`, `agents/laneL_keyword_walk/RESULTS.md`.
Hits: the walk family is covered by lanes J, K and L (see the parent report). Lane L's step set also includes 119,284 powers of keyed permutations, which carry one to five 5-cycles and so include nine-fixed-point steps (keyword-derived, null on real page 0; `agents/laneL_keyword_walk/RESULTS.md`, step enumeration). Lane L did not run a uniform random nine-fixed-point g.

## PROOF (`jobs/hypothesis-gate/PROOF.md`)
- [pass] Names the hypothesis and links `runs/walk_dodge_random_f9_cipher.py`; the simulator defines `encrypt(plain, words, rng)`.
- [pass] The full `gate_sim.py --seeds 3` output is pasted above, including the final GATE line.
- [pass] Verdict: `EXCLUDED by C1 C2 C3 C6`.
- [pass] No PROCEED after a gate FAIL; every failed id is named.
- [pass] Prior-coverage line lists the grep terms and the files searched.
- [n/a] PROCEED design: not required.
- [pass] Every key is drawn from rng; five seeds give five different ciphertexts.
