> **Re-graded 2026-10-16 after C2c was added to the gate: `GATE FAIL: C2c`, verdict EXCLUDED by C2c.** The skip is keyed to the absolute plaintext position, so every surviving doublet lands on one residue mod 5 (chi-square 300+); LP2's doublets are uniform mod 2..8. The PROCEED below is withdrawn. Lane S found this.

# Hypothesis gate: prime-totient keystream with collision skip (catalogue A2), four variants

Gated 2026-10-16 by a Haiku hypothesis-gate agent; this report file was assembled by the orchestrator from that agent's
gate outputs and hand-back (the agent did not write it), and the PASS variant was re-run by the orchestrator.

Hypothesis: Cicada's solved-page stream p = c - (prime_k - 1) mod 29 (the totient of the k-th prime, k advancing per
enciphered rune), keyed only by the start index k0 in the first 10,000 primes, plus a collision skip (if the output would
repeat the previous rune, advance k and re-encipher). Simulators: `totient_fskip_cipher.py` (literal F, F does not consume
a step, skip at every position), `totient_fskip_skip45_cipher.py` (skip only at plaintext positions i mod 5 != 0),
`totient_fskip_kwshift_cipher.py` (a 7-rune keyword added by prime index), `totient_fskip_skip45_nolitF_cipher.py`
(skip45 without the literal F).

## Verdicts
| run | final gate line | verdict |
|---|---|---|
| totient_fskip | GATE FAIL: C1 C2 C3 C6 | EXCLUDED by C1 C2 C3 C6 |
| totient_fskip_skip45 | GATE FAIL: C1 | EXCLUDED by C1 |
| totient_fskip_kwshift | GATE FAIL: C1 C2 C6 | EXCLUDED by C1 C2 C6 |
| totient_fskip_skip45_nolitF | GATE PASS | PROCEED (weak: C5 soft-fails on every seed; tiny key space) |

Why C1 fails: passing plaintext F through at its English rate (2.28%) puts rune 0 at 5.6% of the ciphertext; LP2 has
458 zeros (3.54%). This matches the community's independent result that LP2's body passes no F through
(`dl/aldegonde_clone/hypotheses/the-body-passes-nothing-through.md`, -8.9 sigma; `dl/leo/docs/FINDINGS.md` line 98). One
re-encipher per collision leaves 0.2-0.4% doublets, below the 0.4-1.0% band, which is why the base and kwshift runs also
fail C2 and C6.

## Prior coverage
Grep terms: totient, phi, prime, collision, skip, literal F, interrupt, pass-through. Files: REPORT.md, REPORT_ROUND2.md
(no hits), toolbox/CONSTRAINTS.md, dl/dukotah/liber-primus/LEDGER.json, the elimination ledger, dl/leo/docs/FINDINGS.md,
dl/aldegonde_clone/hypotheses/INDEX.md, dukotah campaign15 `P1-skip-beam_RESULT.md` (2,876 decodes, best -6.442; start
offsets 0, 100, ..., 1000 only), campaign18 `armada/rosetta_sweep.py` (start 0 only). All 10,000 starts with the
position-phase skip were never run.

## PROCEED design (totient_fskip_skip45_nolitF)
Key space: k0 in 0..9999 (13.3 bits), times 5 if the skip phase is free (50,000 keys): sweep it completely. Decode: a
two-branch beam over (position, k); branches differ only where c - prev equals the stream's step, so decoding is nearly
deterministic. Control: 1,600 runes of English at random k0 and phase, recovered at rank 1 in at least 18 of 20 plants.
Null: 200 within-page shuffles (increment shuffles) and 200 random-start copies; real best against the null max.
Candidates to `lp/verify_candidate.py` and the oracle. Caveat: dropping the literal F departs from the solved pages; a
pass on a 13-bit key is weak evidence for the cipher, and the family predicts no lag-5 echo.

## Full gate outputs (`gate_sim.py <run>_cipher.py --seeds 3`)

### totient_fskip
```
cipher: totient_fskip
seed 0: doublets 22 (20 within, 2 cross), lag-5 66/1828
  C1 IoC                               1.0155     LP2 1.0      FAIL
  C2 doublet rate                      0.0017     LP2 0.00664  FAIL
  C2b conditional IoC                  1.0514     LP2 1.026    PASS
  C3 repeated words >=3                15         LP2 16       FAIL
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0361     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    2.0        LP2 23       FAIL
seed 1: doublets 19 (18 within, 1 cross), lag-5 53/1828
  C1 IoC                               1.0133     LP2 1.0      FAIL
  C2 doublet rate                      0.00147    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0508     LP2 1.026    PASS
  C3 repeated words >=3                5          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.029      LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    1.0        LP2 23       FAIL
seed 2: doublets 22 (18 within, 4 cross), lag-5 58/1828
  C1 IoC                               1.0141     LP2 1.0      FAIL
  C2 doublet rate                      0.0017     LP2 0.00664  FAIL
  C2b conditional IoC                  1.0455     LP2 1.026    PASS
  C3 repeated words >=3                10         LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0317     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    4.0        LP2 23       FAIL
GATE FAIL: C1 C2 C3 C6
```

### totient_fskip_skip45
```
cipher: totient_fskip_skip45
seed 0: doublets 115 (90 within, 25 cross), lag-5 72/1828
  C1 IoC                               1.0136     LP2 1.0      FAIL
  C2 doublet rate                      0.00888    LP2 0.00664  PASS
  C2b conditional IoC                  1.0431     LP2 1.026    PASS
  C3 repeated words >=3                6          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0394     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    25.0       LP2 23       PASS
seed 1: doublets 108 (80 within, 28 cross), lag-5 58/1828
  C1 IoC                               1.0111     LP2 1.0      FAIL
  C2 doublet rate                      0.00834    LP2 0.00664  PASS
  C2b conditional IoC                  1.0372     LP2 1.026    PASS
  C3 repeated words >=3                12         LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0317     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    28.0       LP2 23       PASS
seed 2: doublets 105 (83 within, 22 cross), lag-5 70/1828
  C1 IoC                               1.0131     LP2 1.0      FAIL
  C2 doublet rate                      0.0081     LP2 0.00664  PASS
  C2b conditional IoC                  1.0351     LP2 1.026    PASS
  C3 repeated words >=3                3          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0383     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    22.0       LP2 23       PASS
GATE FAIL: C1
```

### totient_fskip_kwshift
```
cipher: totient_fskip_kwshift
seed 0: doublets 27 (23 within, 4 cross), lag-5 59/1828
  C1 IoC                               1.0139     LP2 1.0      FAIL
  C2 doublet rate                      0.00208    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0421     LP2 1.026    PASS
  C3 repeated words >=3                10         LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0323     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    4.0        LP2 23       FAIL
seed 1: doublets 49 (41 within, 8 cross), lag-5 53/1828
  C1 IoC                               1.0143     LP2 1.0      FAIL
  C2 doublet rate                      0.00378    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0442     LP2 1.026    PASS
  C3 repeated words >=3                5          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.029      LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    8.0        LP2 23       FAIL
seed 2: doublets 47 (38 within, 9 cross), lag-5 53/1828
  C1 IoC                               1.0158     LP2 1.0      FAIL
  C2 doublet rate                      0.00363    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0436     LP2 1.026    PASS
  C3 repeated words >=3                7          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.029      LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    9.0        LP2 23       FAIL
GATE FAIL: C1 C2 C6
```

### totient_fskip_skip45_nolitF
```
cipher: totient_fskip_skip45_nolitF
seed 0: doublets 78 (57 within, 21 cross), lag-5 61/1828
  C1 IoC                               1.0002     LP2 1.0      PASS
  C2 doublet rate                      0.00602    LP2 0.00664  PASS
  C2b conditional IoC                  1.0336     LP2 1.026    PASS
  C3 repeated words >=3                7          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0334     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    21.0       LP2 23       PASS
seed 1: doublets 87 (69 within, 18 cross), lag-5 57/1828
  C1 IoC                               1.0008     LP2 1.0      PASS
  C2 doublet rate                      0.00672    LP2 0.00664  PASS
  C2b conditional IoC                  1.0297     LP2 1.026    PASS
  C3 repeated words >=3                9          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0312     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    18.0       LP2 23       PASS
seed 2: doublets 96 (76 within, 20 cross), lag-5 67/1828
  C1 IoC                               1.0015     LP2 1.0      PASS
  C2 doublet rate                      0.00741    LP2 0.00664  PASS
  C2b conditional IoC                  1.034      LP2 1.026    PASS
  C3 repeated words >=3                8          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0367     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    20.0       LP2 23       PASS
GATE PASS
```
