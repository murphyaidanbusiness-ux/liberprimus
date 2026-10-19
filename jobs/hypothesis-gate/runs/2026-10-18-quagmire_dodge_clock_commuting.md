# Hypothesis gate: Quagmire clock dodge with a commuting sigma (`quagmire_dodge_clock_commuting`)

Gated 2026-10-18 by the hypothesis-gate job (claude-haiku-5-5), under the orchestrator's brief. Simulator:
`jobs/hypothesis-gate/runs/quagmire_dodge_clock_commuting_cipher.py` (`encrypt(plain, words, rng)`).
Outputs in `jobs/hypothesis-gate/runs/`: `2026-10-18-quagmire_dodge_clock_commuting_gate.txt` (3 seeds),
`2026-10-18-quagmire_dodge_clock_commuting_gate12.txt` (12 seeds), `2026-10-18-quagmire_dodge_clock_commuting_draws.txt`
(300-key census), `2026-10-18-quagmire_dodge_clock_commuting_family.txt` (`tools/family_means.py` on the 12 seeds).
Mechanism check: `tools/commuting_check.py`.

**Verdict: EXCLUDED by C3.** C3 (repeated words, one-sided) fails on 3 of 3 seeds and 12 of 12 seeds, and 0 of 300
random keys pass it. C2 and C6 also failed, on one seed each of 12 (a minority that does not decide the gate).

## The hypothesis

The clock-dependent Quagmire dodge of `quagmire_dodge_clock` (gated PASS on 2026-10-17), with one change: sigma is built
from the same keyed alphabet K as the letter alphabets. `sigma = conj_shift(K, delta)` for a random delta in 1..28, so
sigma commutes with every `A_k = conj_shift(K, S_k)`. The word map then telescopes to
`base_w = base_0 . K . add(D_w) . K^-1`, with D_w summed over the earlier words (the tool confirms the count below).

Prediction under test (C3 one-sided): equal plaintext words repeat in the ciphertext far more often than LP2's 16.

## The simulator and the one change

`quagmire_dodge_clock_commuting_cipher.py` is a copy of `quagmire_dodge_clock_cipher.py`. The cipher line changes:

```
-    sigma = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
+    sigma = conj_shift(K, rng.randrange(1, M))
```

Draw order is K, offsets, delta, base0 (the independent permutation for sigma is no longer drawn, so the random
stream differs from the parent). NAME and DESCRIPTION were edited so that the gate output names the variant; no other
line changed. The encipher loop is the community's `quagmire_dodge.encipher`, unchanged.

Key-draw check (PROOF line 7), SHA-256 prefixes of the ciphertext on the English plaintext of `rn.english_stream(12956)`,
run as an inline Python call to `encrypt`: seed 1000 `b30a351908b29f65`; seed 1001 `1ab306325b92b2e3`; seed 1000 again
`b30a351908b29f65`. Different seeds give different ciphertexts, and a seed reproduces.

## Gate output, 3 seeds (`gate_sim.py --seeds 3`, after `source agents/laneO_quagmire_dodge/env.sh`)

```
cipher: Quagmire with clock-dependent word step, doublet dodge, and sigma commuting with the letter alphabets (sigma = conj_shift(K, delta), one keyword for everything)
seed 0: doublets 101 (81 within, 20 cross), lag-5 109/1828
  C1 IoC                               0.9994     LP2 1.0      PASS
  C2 doublet rate                      0.0078     LP2 0.00664  PASS
  C2b conditional IoC                  1.0482     LP2 1.026    PASS
  C2c doublet positions mod 2..8       mod7 chi2 13.6 LP2 uniform  PASS
  C3 repeated words >=3                55         LP2 16       FAIL
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0596     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    20.0       LP2 23       PASS
seed 1: doublets 87 (64 within, 23 cross), lag-5 102/1828
  C1 IoC                               0.9999     LP2 1.0      PASS
  C2 doublet rate                      0.00672    LP2 0.00664  PASS
  C2b conditional IoC                  1.0472     LP2 1.026    PASS
  C2c doublet positions mod 2..8       mod8 chi2 12.4 LP2 uniform  PASS
  C3 repeated words >=3                60         LP2 16       FAIL
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0558     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    23.0       LP2 23       PASS
seed 2: doublets 101 (74 within, 27 cross), lag-5 103/1828
  C1 IoC                               1.001      LP2 1.0      PASS
  C2 doublet rate                      0.0078     LP2 0.00664  PASS
  C2b conditional IoC                  1.062      LP2 1.026    PASS
  C2c doublet positions mod 2..8       mod7 chi2 4.0 LP2 uniform  PASS
  C3 repeated words >=3                54         LP2 16       FAIL
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0563     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    27.0       LP2 23       PASS
fails per constraint over 3 seeds: {'C3': 3}
GATE FAIL: C3
```

C3 detail (the gate's null is the cipher's own shuffle with the same word lengths): seed 0 shuffle null 5.8 +- 3.0,
z +16.4; seed 1 6.8 +- 2.8, z +19.1; seed 2 8.0 +- 2.7, z +17.1. The band is z <= 3.

## Gate output, 12 seeds (`gate_sim.py --seeds 12`)

Decision lines:

```
fails per constraint over 12 seeds: {'C3': 12, 'C6': 1, 'C2': 1}
GATE FAIL: C3
```

- C2 failed on seed 9 only (doublet rate 0.01112, above the band's 0.010).
- C6 failed on seed 5 only (5 cross-word doublets, below the band's 12).
- C3 failed on all 12 seeds. Repeated-word counts by seed: 55, 60, 54, 63, 58, 54, 64, 56, 69, 52, 54, 68
  (mean 58.9, range 52 to 69).

Family means (`tools/family_means.py`, 12 seeds): doublets 85.3 +- 25.2 (LP2 86); cross-word doublets 21.8 +- 8.4 (LP2 23);
within-word lag-5 rate 0.0567 (LP2 0.0494); doublet rate 0.00659 (LP2 0.00664); C2c uniform on 12 of 12 seeds.
Most statistics sit near LP2. Within-word lag-5 is high (0.0567 against 0.0494, the soft band's edge, as in the
parent family). C3 is the statistic that fails.

## Per-constraint pass shares (`tools/walk_draws.py --draws 300`, rng seeds 5000 to 5299)

| constraint | draws passing |
|---|---|
| C1 | 300 / 300 |
| C2 | 247 / 300 |
| C2b | 298 / 300 |
| C2c | 299 / 300 |
| C3 | **0 / 300** |
| C6 | 263 / 300 |
| all hard constraints | **0 / 300** |

Doublet rate spans 0.0028 to 0.0180 and cross-word doublets 7 to 54 across draws. The family fails C3 on every draw.
Nothing passes, so there is no small passing set to attack. This is an exclusion of the family, not a narrowing.

## C3 against LP2

LP2 has 16 repeated words of at least 3 runes. The simulated family has 52 to 69 (3.3 to 4.3 times LP2). The earlier
independent-sigma clock form (`2026-10-17-quagmire_dodge_clock.md`) had 3 to 9 (mean 6.6 over 12 seeds), which passes.
Making sigma commute with the letter alphabets raises the repeat count about nine times.

**Prediction check.** The direction the brief predicted holds: equal plaintext words repeat far more often in the
ciphertext, and C3 is the constraint that fails on excess.

## Mechanism (`tools/commuting_check.py`, seeds 1000 to 1002)

The script replays the simulator's draws and the encipher loop, records the base at each word, and checks the replay
against `encrypt`.

- The replay matches `encrypt` on all three seeds.
- Distinct base maps over the word sequence: **29** on every seed. This is the telescoping claim: every word map is
  `base_0` composed with a power of one 29-cycle.
- Distinct (base, clock phase at word start) states: **145** on every seed (29 x 5), all visited.
- Equal plaintext words of at least 3 runes: 2,201 words, 9,291 equal pairs. Pairs that start in the same state:
  65, 66 and 61 on seeds 0, 1 and 2. A uniform state draw predicts 9,291 / 145 = 64.1. The measured collision rate is
  the 1-in-145 rate the telescoping implies.
- Ciphertext repeated word types (at least 3 runes): 55, 60 and 54.

So the excess is structural: a small state count makes equal plaintext words collide, and the gate's C3 counts them.

## Prior coverage

Grep terms (case-insensitive, over the files below): `quagmire.dodge`, `clock.depend`, `commut`, `one keyword`,
`keyword for everything`, `telescop`, `quagmire_dodge`, `sigma`, `base.count`, `base-count`, `normalis|normaliz`,
`centrali`, `walk`.

Files searched: `REPORT.md`, `REPORT_ROUND2.md`, `toolbox/CONSTRAINTS.md`, `research/EXHAUSTED.md`,
`agents/laneO_quagmire_dodge/RESULTS.md`, `dl/dukotah/liber-primus/LEDGER.json`,
`dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, `dl/leo/docs/FINDINGS.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`,
`quagmire-dodge.md`, `doublet-dodge-walk.md`, `sigma-power-step.md`, `per-word-related-alphabets.md`,
`length-clocked-walk.md`, and the code `dl/aldegonde_port/experiments/quagmire_dodge.py` and `base_count_floor.py`.

Hits:

1. **This exact variant: not run.** No ledger, report or lane run reports a sigma that commutes with the letter
   alphabets in the clock form. The gate and sweep records cover the independent-sigma clock form (`REPORT_ROUND2.md`
   lines 92 to 94 and 130, gate PASS 2026-10-17) and the odometer (`agents/laneO_quagmire_dodge/RESULTS.md` lines 159 to 160,
   which says `quagmire_dodge.encipher` is not covered).
2. **Clock form parked and unsearched.** `research/EXHAUSTED.md` line 82 (AL-27 clock-form Quagmire dodge, "never searched",
   the dodge-aware scorer blind to it, lane W 0/20). `dl/aldegonde_clone/hypotheses/quagmire-dodge.md` (lines 73, 144,
   297, and the "NOT been run" note near line 373) and `INDEX.md` line 156 are the community's own records of the parked sweep.
3. **Commuting steps in a related walk leak.** `per-word-related-alphabets.md` (section "Why the walk must be free") says the
   centralizer of its step `g` (steps commuting with `g`) "leaves periodic IoC 1.52 and a delta chi2 of 218". That is a
   different walk (a 5-cycle `g` with word-to-word permutations), so it is related, not this result.
4. **The C3 mechanism is on record.** `toolbox/CONSTRAINTS.md` quick exclusions: a fixed alphabet set with a small per-word
   phase is excluded by C3 (5 alphabets would force at least 482 repeated words). This family has 145 states, not 5, so
   the same mechanism applies at a smaller scale, and the measured excess matches it.
5. **Community base-count argument (walk only, see the next section).** `sigma-power-step.md` lines 106 to 190 and
   `dl/aldegonde_port/experiments/base_count_floor.py` (header read; not run).

No hit for `telescop` or `one keyword` in any ledger. The only `telescop` hit is `sigma-power-step.md` line 114, about
the walk.

## Does the community base-count argument cover this case?

**It covers the walk, not the Quagmire clock form by name.** The community's argument (`sigma-power-step.md` and
`base_count_floor.py`, read, not run) bounds the base count of the length-clocked walk, `base_w = base_0 . g^e . sigma^w`,
where `g` is a 5-cycle letter step. A commuting normaliser then visits at most 5 . ord(sigma) <= 500 bases. Its numbers
(N >~ 600 from the identity census, the commuting p = 0.0034 on 2,839 generic-English length-4+ pairs) are computed for
that walk. The note first calls the commuting case "marginal, not excluded" (the census bound alone), then sharpens it
to "excluded" at p = 0.0034 (about 2.9 sigma) on the conservative register, with p near 1e-7 on the same-author register.

This family is a different parametrisation. Its word step is `A_phase . sigma`, and every `A_k` and sigma are powers of
one 29-cycle, so its base count is at most 29 (times 5 phases = 145 states), not 500. The same mechanism applies: fewer
states make equal plaintext words collide more often. The community's own pressure figure gives 2,839 / 145 = about 20 forced
length-4+ repeats, against 0 observed in LP2. That is arithmetic on the note's figures, not a run. The gate measures the
same excess directly (C3 52 to 69 against 16, and 65 of 9,291 pairs sharing a state against 64 expected).

So: the walk argument does not transfer as written, the mechanism does, and the clock form was never priced by the
community. This gate is the first measurement of this family's C3.

## Gaps

- The gate's C1 is the IoC only. The periodic-IoC leakage that `per-word-related-alphabets.md` reports for a centralizer
  walk is not tested by the gate. C1 passes here (IoC 0.9994 to 1.001). The family is excluded by C3 regardless.
- Lane O's odometer tiers and the clock-variant scorer are not involved. Nothing here touches LP2.

## Verdict

**EXCLUDED by C3** (C2 and C6 also failed, on one seed each of 12; minority, not decisive). Not PROCEED (a gate fail is
never followed by PROCEED). Not ALREADY TESTED (the community's walk argument does not cover this family by name, and
no run exists). No variant is gated here. The nearest variant that passes is the independent-sigma clock form, already
gated PASS on 2026-10-17. No key space or attack design is given, since the family is excluded.

## Lead check

Nothing here is a lead on LP2. The gate runs the simulator on English and grades against the LP2 fingerprint bands, and it
decrypts nothing. No LEAD.md, no email, no notification.

## PROOF (`jobs/hypothesis-gate/PROOF.md`), line by line

Output:
1. PASS. The report names `quagmire_dodge_clock_commuting`, links `runs/quagmire_dodge_clock_commuting_cipher.py`, and that file defines `encrypt(plain, words, rng)`.
2. PASS. The full `gate_sim.py --seeds 3` output, including `GATE FAIL: C3`, is pasted above.
3. PASS. Verdict: `EXCLUDED by C3`.
4. PASS. The gate failed, and PROCEED is not written. Every failed constraint id is named in the verdict (C3; C2 and C6 as minority fails).
5. PASS. The grep terms and files searched are listed under Prior coverage.
6. PASS (not applicable). The verdict is EXCLUDED, so no key space or attack design is required.
7. PASS. Seeds 1000 and 1001 give different ciphertexts (`b30a351908b29f65` and `1ab306325b92b2e3`), and seed 1000 reproduces.

Fixture:
8. PASS. `gate_sim.py --seeds 2` on the three fixtures gives `otp_dodge5.py` GATE PASS; `vigenere7.py` GATE FAIL: C1 C2 C2b C2c C3 C6; `norepeat.py` GATE FAIL: C2 C6. All three match `data/fixture/expected.md`.

Other tools run: `walk_draws.py --draws 300` (above, runs without error), `family_means.py` on the 12-seed output (above),
`dynsub_checks.py` (dynsub_skip and dynsub_skip5 wheels stay permutations, seeds differ and reproduce; reference doublet
rates 0.033 to 0.036), and `commuting_check.py` (above, all three checks pass).

## Files

- New: `jobs/hypothesis-gate/runs/quagmire_dodge_clock_commuting_cipher.py` (simulator)
- New: `jobs/hypothesis-gate/tools/commuting_check.py` (mechanism check: 29 maps, 145 states, replay matches)
- New: this report, and the four outputs listed at the top
- CHANGELOG.md: one dated entry

## Not done

- Did not run `base_count_floor.py` (read only; it downloads Gutenberg texts). Its numbers are cited from the note.
- Did not change the gate's logic, its bands, or any ledger. Did not edit SKILL.md; the helper is linked from this report.
- Did not commit or push (not asked).
- No variant of the cipher was gated beyond the one specified.
