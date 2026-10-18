# Hypothesis gate: walk_dodge_random (2026-10-16)

## Hypothesis
Oosterhof's doublet-dodge walk, with every permutation free and drawn from rng. Walk rule as in the community's
`dl/aldegonde_clone/experiments/doublet_dodge_walk.py::encipher` and as restated in `agents/laneK_walk_search/RESULTS.md` section 0:
- `c = base[g^(clock mod 5)[p]]`; if `c` equals the previous cipher rune (across word boundaries too), `clock += 1` and recompute once; `clock += 1` after every rune.
- The clock is global and never resets at a word. After each word, `base := base o g^((clock-1) mod 5) o sigma`, with `(a o b)[x] = a[b[x]]`.
- Keys: g is an order-5 permutation with exactly 4 fixed points (five 5-cycles on the other 25 runes), sigma and base0 are uniform permutations of the 29 runes.

Note on the brief: "positions j and j+5 of a word use the same alphabet" holds exactly only while no skip falls between them, because the clock is global. I followed the community rule.

## Simulator
`jobs/hypothesis-gate/runs/walk_dodge_random_cipher.py`, defining `encrypt(plain, words, rng)`. Every key is drawn from `rng`; five rng seeds give five different ciphertexts of the same plaintext.

Why 4 fixed points: among order-5 permutations of 29 runes, the share with exactly f fixed points is 0.998349 for f = 4, 0.001651 for f = 9, and below 1e-7 for f >= 14 (count C(29,f) times the number of 5-cycle-only permutations of the other 29-f runes). A uniform draw therefore has 4 fixed points, which is the community's nominal form.

## Gate output (`gate_sim.py --seeds 3`)
```
cipher: walk_dodge_random: doublet-dodge walk, uniform order-5 g (4 fixed points), sigma and base0 from rng
seed 0: doublets 54 (41 within, 13 cross), lag-5 88/1828
  C1 IoC                               1.0003     LP2 1.0      PASS
  C2 doublet rate                      0.00417    LP2 0.00664  PASS
  C2b conditional IoC                  1.0221     LP2 1.026    PASS
  C3 repeated words >=3                9          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0481     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    13.0       LP2 23       PASS
seed 1: doublets 151 (126 within, 25 cross), lag-5 108/1828
  C1 IoC                               1.0003     LP2 1.0      PASS
  C2 doublet rate                      0.01166    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0169     LP2 1.026    PASS
  C3 repeated words >=3                5          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0591     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    25.0       LP2 23       PASS
seed 2: doublets 49 (40 within, 9 cross), lag-5 105/1828
  C1 IoC                               1.0201     LP2 1.0      FAIL
  C2 doublet rate                      0.00378    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0516     LP2 1.026    PASS
  C3 repeated words >=3                11         LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0574     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    9.0        LP2 23       FAIL
GATE FAIL: C1 C2 C6
```

Reading the seeds. Seed 0 passes every hard constraint. Seed 1 fails C2 high (doublet rate 0.0117, 126 within-word doublets). Seed 2 fails C1 (IoC 1.0201), C2 low (0.0038) and C6 (9 cross-word doublets against the band 12 to 35). The fixed-point set of g decides the doublet count: a within-word doublet survives only as a plaintext double on a fixed point of g. Checked on 20 keys: 920 of 920 surviving within-word doublets satisfy this.

## Key-draw census (not the gate; `tools/walk_draws.py --draws 300`, rng seeds 5000 to 5299)
| constraint | draws passing (of 300) |
| --- | --- |
| C1 IoC | 271 |
| C2 doublet rate | 138 |
| C2b conditional IoC | 295 |
| C3 repeated words | 272 |
| C6 cross-word doublets | 103 |
| all hard constraints | **43 (14%)** |

Doublet rate: median 0.0044, range 0 to 0.0232. Cross-word doublets: median 9.

## Verdict
**EXCLUDED by C1 C2 C6** (gate FAIL on seeds 1 and 2; C1 on seed 2, C2 on seeds 1 and 2, C6 on seed 2).

This verdict excludes the typical key, not the whole family. 43 of 300 random keys (14%) pass every hard constraint on English. A three-seed gate on a family where about 14% of keys pass fails almost always: if draws are independent, all three pass with probability about 0.14^3, or 0.003. The FAIL therefore says that a random member does not reproduce LP2's fingerprint; it does not show that no key in the family does. Whether to spend an attack lane on the passing keys is a decision for the orchestrator, not something this gate can make.

## Predictions for the constraints that do not decide the gate
- C4 (layout): the walk copies the plaintext's word lengths, so C4 is the plaintext's own value: -5.69 on every draw, against LP2's +0.9. The hypothesis predicts English word-length layout, which LP2 does not show (INFO). Note that `toolbox/CONSTRAINTS.md` quotes English z of +7 to +15; this stream gives -5.69, and I did not resolve the difference.
- C5 (within-word lag-5 echo, soft): a within-word lag-5 equality survives only when no skip falls between the two positions, and then it equals the plaintext's own lag-5 equality. Measured 0.048, 0.059 and 0.057 on the three seeds (soft band 0.039 to 0.060). The walk reproduces LP2's echo level, so C5 does not discriminate here.

## Prior coverage
Grep terms: `Oosterhof`, `dodge`, `doublet`, `skip`, `clock`, `walk`, `order-5`, `fixed point`.
Files searched: `REPORT.md`, `REPORT_ROUND2.md`, `toolbox/CONSTRAINTS.md`, `dl/dukotah/liber-primus/LEDGER.json`, `dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`, `dl/leo/docs/FINDINGS.md`, `agents/laneJ_lag5_echo/RESULTS.md`, `agents/laneK_walk_search/RESULTS.md`, `agents/laneL_keyword_walk/RESULTS.md`.
Hits:
- Lane K (`agents/laneK_walk_search/RESULTS.md`): the free-key walk. Global search is infeasible (0 of 63 annealing runs recovered it with one permutation unknown). `REPORT.md` "What the constraints leave" calls this the one consistent shape and prices its key at about 180 to 280 bits.
- Lane L (`agents/laneL_keyword_walk/RESULTS.md`): keyword-built alphabets, 1.13M order-5 steps, three clock variants, null on the real page 0. REPORT.md ("What the constraints leave") records that lane L derived the same fixed-point consequence for within-word doublets.
- Lane J (`agents/laneJ_lag5_echo/RESULTS.md`): the doublet-dodge walk fits the doublet and echo profile, which it calls fitting, not prediction.
- `dl/aldegonde_clone/hypotheses/INDEX.md`: `one-parameter-fits-both-suppressions.md` and `seam-to-d1w-ratio-is-a-constraint.md` test this same walk.
- `LEDGER.json` and `ELIMINATION-LEDGER.md`: no entry on the dodge walk under these terms.

The walk family is covered by lanes J, K and L. The EXCLUDED verdict takes precedence over ALREADY TESTED in the protocol.

## Key space (context for any future PROCEED)
Free keys: about 283 bits (g 79.7, sigma 101.8, base0 101.8), per lane K's pricing. Not an attack design, since this hypothesis is EXCLUDED.

## PROOF (`jobs/hypothesis-gate/PROOF.md`)
- [pass] Names the hypothesis and links `runs/walk_dodge_random_cipher.py`; the simulator defines `encrypt(plain, words, rng)`.
- [pass] The full `gate_sim.py --seeds 3` output is pasted above, including the final GATE line.
- [pass] Verdict is exactly one of the three allowed forms: `EXCLUDED by C1 C2 C6`.
- [pass] No PROCEED follows a gate FAIL, and the failed ids (C1, C2, C6) are named in the verdict.
- [pass] The prior-coverage line lists the grep terms and the files searched.
- [n/a] PROCEED design: not required, since the verdict is EXCLUDED.
- [pass] Every key is drawn from rng: five rng seeds give five different ciphertexts for one plaintext.

Fixture check (`gate_sim.py <file> --seeds 2` on each `data/fixture/*.py`, against `data/fixture/expected.md`):
- `norepeat.py`: `GATE FAIL: C2 C6` (matches)
- `otp_dodge5.py`: `GATE PASS` (matches)
- `vigenere7.py`: `GATE FAIL: C1 C2 C2b C3 C6` (matches)

Helper saved and linked: `jobs/hypothesis-gate/tools/walk_draws.py` (key-draw census; the gate's bands are unchanged).
