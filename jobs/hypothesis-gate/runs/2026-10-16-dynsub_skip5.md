> **Re-graded 2026-10-16 after C2c was added to the gate: `GATE FAIL: C2c`, verdict EXCLUDED by C2c.** The skip is keyed to the absolute plaintext position, so every surviving doublet lands on one residue mod 5 (chi-square 300+); LP2's doublets are uniform mod 2..8. The PROCEED below is withdrawn. Lane S found this.

# Hypothesis gate: dynsub_skip5 (Chaocipher-29 dynamic substitution, skip-on-repeat at 4 of every 5 positions)

Date: 2026-10-16. Model: claude-haiku-5-5. Job: hypothesis-gate. Catalogue entry: A1 in `toolbox/TECHNIQUES.md`,
gated as its own hypothesis because the skip fires at 4 of every 5 letter positions (the "1/5" mechanism of
`toolbox/CONSTRAINTS.md` and the dodge family).

## Hypothesis

The same keyed wheels and Chaocipher-29 step as [dynsub_skip](2026-10-16-dynsub_skip.md). The difference is the skip
rule: it fires only when the letter position i (0-based in the plaintext) is not 0 mod 5. At positions 0 mod 5 a repeat
is emitted as it is, so repeats survive at one position in five, as in `jobs/hypothesis-gate/data/fixture/otp_dodge5.py`.
The phase is the global letter position. A per-word phase reset is a different hypothesis and is not gated here.

Simulator: [dynsub_skip5_cipher.py](dynsub_skip5_cipher.py), defines `encrypt(plain, words, rng)`. Key form: two
`rng.shuffle` calls on `range(29)`.

## Gate output

Command: `python jobs/hypothesis-gate/tools/gate_sim.py jobs/hypothesis-gate/runs/dynsub_skip5_cipher.py --seeds 3`

```
cipher: dynsub_skip5: Chaocipher-29 dynamic substitution, skip-on-repeat at 4 of every 5 letter positions (the 1/5 mechanism)
seed 0: doublets 76 (63 within, 13 cross), lag-5 54/1828
  C1 IoC                               0.9998     LP2 1.0      PASS
  C2 doublet rate                      0.00587    LP2 0.00664  PASS
  C2b conditional IoC                  1.0214     LP2 1.026    PASS
  C3 repeated words >=3                10         LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0295     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    13.0       LP2 23       PASS
seed 1: doublets 92 (63 within, 29 cross), lag-5 51/1828
  C1 IoC                               0.9993     LP2 1.0      PASS
  C2 doublet rate                      0.0071     LP2 0.00664  PASS
  C2b conditional IoC                  1.0266     LP2 1.026    PASS
  C3 repeated words >=3                8          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0279     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    29.0       LP2 23       PASS
seed 2: doublets 83 (65 within, 18 cross), lag-5 52/1828
  C1 IoC                               0.9998     LP2 1.0      PASS
  C2 doublet rate                      0.00641    LP2 0.00664  PASS
  C2b conditional IoC                  1.0253     LP2 1.026    PASS
  C3 repeated words >=3                6          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0284     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    18.0       LP2 23       PASS
GATE PASS
```

Reading: C1, C2, C2b, C3 and C6 pass on every seed. C2 lands at 0.59-0.71% against LP2's 0.66%. C6 is 13-29 against a
band of 12-35, so seed 0 sits near the lower edge. C5 fails softly on all three seeds: the simulated within-word lag-5
rate is 2.8-3.0%, below chance and below LP2's 4.94%. The hypothesis predicts no period-5 echo, because the wheels never
return to the same state at lag 5. So the LP2 echo is a real tension for this model, and the gate does not decide on it.
C4 is layout and is INFO only.

## Prior coverage

Terms searched: chaocipher, dynamic substitution, skip-on-repeat / skip on repeat, dodge, evolving or progressive
alphabet, period-5, Byrne, Mellen, Lasry, nadir / zenith, key-skip, anti-repeat, lapse, reroll.

Files searched: `REPORT.md`, `REPORT_ROUND2.md`, `dl/dukotah/liber-primus/LEDGER.json`,
`dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, `dl/leo/docs/FINDINGS.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`,
and repo-wide and `dl/` greps for chaocipher and nadir/zenith.

Closest tested relatives, none of them this hypothesis:
- Battery 11, `dl/aldegonde_clone/docs/lp_structure_findings.md` section 5 (`lp_battery11.py`): "S2 reroll, 19% lapse"
  is an additive i.i.d. key with a reroll that fires 81% of the time. It gives 0.70% doublets and passes every column
  of that table. That is the same firing rate on an additive base, so the mechanism is covered there. The wheel base is not.
- Oosterhof's doublet-dodge walk, `dl/aldegonde_clone/hypotheses/doublet-dodge-walk.md` (lane J row "c walk +
  doublet-dodge", `agents/laneJ_lag5_echo/RESULTS.md`; lane K, `agents/laneK_walk_search/RESULTS.md`). Its alphabet
  advances by a clock permutation g^(j mod 5) and a per-word base, not by a Chaocipher step driven by the data. It does
  produce the lag-5 echo, which this model does not. Lane K excludes fixed alphabet sets. Neither tests data-driven wheels.
- Dukotah LEDGER and ELIMINATION-LEDGER: soft anti-repeat on seed-derived keystreams (about 83%), closed for those
  families. Leo FINDINGS: key-skip Vigenere gives 0.4-0.7% doublets but is periodic (C1).

No record runs Chaocipher wheels with a 1-in-5 skip, so the hypothesis is not already tested. The lane should be read
against the battery-11 and doublet-dodge rows, since the mechanism alone is covered on additive bases.

## Verdict

PROCEED

Key space: two 29-permutations, (29!)^2 = 7.8e61, about 2^205.6. The skip adds no key bits: its phase is the letter
position, and the wheel state is fixed by the two permutations.

## Planted-control and null design for the attack-lane job

- Positive control: 50 plants of `dynsub_skip5` on the English stream (`rn.english_stream(12956)`, with a fresh
  random (L, R) key from rng per plant). Run the lane's solver unchanged. A plant counts as recovered if the planted
  key or at least 95% of its runes come back at rank 1. Require at least 80% recovery across at least 20 plants, list
  every miss, and replay each miss on fresh plaintext before blaming the scorer.
- Null: 50 draws of `nulls.shuffle_increments(pages, rng)` on LP2 pages 0-54 (`toolbox/nulls.py`). Those keep the doublet
  deficit, which this model produces. Do not use `shuffle_runes` as the primary null, because it removes the deficit and
  would make the baseline too easy. The real-LP2 best score counts only if it exceeds the maximum over the 50 nulls.
- Report the lag-5 echo of any decoded plaintext. The model predicts none, so any fit to the 4.94% echo would need to be
  explained.

## Checks

- [`tools/dynsub_checks.py`](../tools/dynsub_checks.py): wheels stay permutations; seeds differ; the same seed reproduces; discards on seed 1000 are
  326; doublet rate on seed 1000 is 0.00587.
- Reference: `PHASE = 1` (plain Chaocipher-29) gives 3.3-3.6% doublets, which fails C2 without the skip.
