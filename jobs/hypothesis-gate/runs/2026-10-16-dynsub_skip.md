# Hypothesis gate: dynsub_skip (Chaocipher-29 dynamic substitution, strict skip-on-repeat)

Date: 2026-10-16. Model: claude-haiku-5-5. Job: hypothesis-gate. Catalogue entry: A1 in `toolbox/TECHNIQUES.md`
(`jobs/technique-survey/runs/2026-10-16-computational-ai.md`, "Dynamic substitution with skip-on-repeat").

## Hypothesis

Two keyed 29-rune wheels: a cipher wheel L and a plain wheel R, each a random permutation of 0..28 drawn from `rng`.
Encipher plain rune p: k = R.index(p), c = L[k]. If c equals the previous output rune, the would-be output is
discarded, the wheels take one extra step at that k, and p is re-enciphered; this repeats until the output differs
(strict skip). After each emitted rune both wheels step once. The wheel step is Byrne's Chaocipher adapted to 29
symbols with nadir 14: L rotates so the cipher rune is at index 0 and the rune at index 1 moves to the nadir; R
rotates so the plain rune is at index 0, rotates one more place, and the rune at index 2 moves to the nadir.

Simulator: [dynsub_skip_cipher.py](dynsub_skip_cipher.py), defines `encrypt(plain, words, rng)`. Key form: two
`rng.shuffle` calls on `range(29)`. The skip loop has a guard (`MAX_DISCARDS`); it never fired.

Its sibling with the skip at 4 of 5 positions is gated separately in `2026-10-16-dynsub_skip5.md`.

## Gate output

Command: `python jobs/hypothesis-gate/tools/gate_sim.py jobs/hypothesis-gate/runs/dynsub_skip_cipher.py --seeds 3`

```
cipher: dynsub_skip: Chaocipher-29 dynamic substitution, strict skip-on-repeat
seed 0: doublets 0 (0 within, 0 cross), lag-5 57/1828
  C1 IoC                               0.9997     LP2 1.0      PASS
  C2 doublet rate                      0.0        LP2 0.00664  FAIL
  C2b conditional IoC                  1.0353     LP2 1.026    PASS
  C3 repeated words >=3                4          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0312     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    0.0        LP2 23       FAIL
seed 1: doublets 0 (0 within, 0 cross), lag-5 80/1828
  C1 IoC                               0.9993     LP2 1.0      PASS
  C2 doublet rate                      0.0        LP2 0.00664  FAIL
  C2b conditional IoC                  1.0284     LP2 1.026    PASS
  C3 repeated words >=3                7          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0438     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    0.0        LP2 23       FAIL
seed 2: doublets 0 (0 within, 0 cross), lag-5 60/1828
  C1 IoC                               1.0003     LP2 1.0      PASS
  C2 doublet rate                      0.0        LP2 0.00664  FAIL
  C2b conditional IoC                  1.0414     LP2 1.026    PASS
  C3 repeated words >=3                7          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0328     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    0.0        LP2 23       FAIL
GATE FAIL: C2 C6
```

Reading: a strict skip gives exactly 0 adjacent repeats on every seed, against LP2's 86. C6 fails because there are no
cross-word doublets either (LP2 23). The discards on seed 1000 number 456, about 3.5% of positions, which is the plain
Chaocipher doublet rate that the skip removes. C5 is soft and does not decide the gate.

## Prior coverage

Terms searched: chaocipher, dynamic substitution, skip-on-repeat / skip on repeat, dodge, evolving or progressive
alphabet, Byrne, Mellen, Lasry, nadir / zenith, key-skip, anti-repeat.

Files searched: `REPORT.md`, `REPORT_ROUND2.md`, `dl/dukotah/liber-primus/LEDGER.json`,
`dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, `dl/leo/docs/FINDINGS.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`,
and repo-wide and `dl/` greps for chaocipher and nadir/zenith (the Chaocipher wheel signature).

Hits:
- `dl/aldegonde_clone/experiments/lp_battery11.py` and `dl/aldegonde_clone/docs/lp_structure_findings.md` section 5:
  plain Chaocipher-29 gives 3.53% doublets (excluded by C2). "S1 skip key letter on collision" on an additive random key
  gives 0.20%, and the write-up says strict skips "over-suppress to near zero". That is the strict rule on an additive
  base, not on wheels.
- `research/s3/sim2.py`, `research/scout3_norepeat_generators.md`: plain Chaocipher-29 gives 3.45% doublets on flat
  plaintext.
- No run anywhere combines Chaocipher wheels with a skip. `TECHNIQUES.md` A1 agrees that the skip variant is untested.

## Verdict

EXCLUDED by C2 C6

The strict rule is excluded on the wheel base, as the battery's strict-skip row already suggested on the additive base.
The variant with the skip at 4 of 5 positions is gated separately.

## Checks

- [`tools/dynsub_checks.py`](../tools/dynsub_checks.py): every wheel step leaves two permutations of 0..28; two seeds give different ciphertexts on
  the same plaintext; the same seed reproduces.
- The reference row `PHASE = 1` (skip never fires) gives plain Chaocipher-29 at 3.3-3.6% doublets on the English stream.
