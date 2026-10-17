# Hypothesis gate: Quagmire with a clock-dependent word step and the doublet dodge (`quagmire_dodge_clock`)

Gated 2026-10-17 by the hypothesis-gate job, under the orchestrator's brief. Simulator:
`jobs/hypothesis-gate/runs/quagmire_dodge_clock_cipher.py` (`encrypt(plain, words, rng)`). Outputs:
`2026-10-17-quagmire_dodge_clock_gate.txt` (3 seeds), `2026-10-17-quagmire_dodge_clock_gate12.txt` (12 seeds),
`2026-10-17-quagmire_dodge_clock_draws.txt` (300-key census). Family-mean table from `tools/family_means.py`.

**Verdict: PROCEED** (gate pass; C2 marginal on 1 of 12 seeds). Not run before: the community priced and parked a
sweep of this family and has no validated scorer for it (see Prior coverage). The planted-control and null design for
the attack lane is in "For PROCEED" below.

## The hypothesis

The community's own cipher `dl/aldegonde_port/experiments/quagmire_dodge.py`, `encipher(plain, base0, alpha, sigma)`:

- Letter step: alphabets `A_k = K . (add S_k) . K^-1` for the running sums S_k of a one-zero five-step schedule
  (`schedule(rng, zeros=1)`, 105,980 schedules).
- Dodge: within a word the base is fixed. Each emission uses `A_(clock mod 5)`. If it equals the previous rune, the clock
  advances one step and the rune is re-emitted. A would-be repeat survives only when the next offset is zero, so
  survivors are about 1/5 of would-be doublets.
- Word step (the clock dependence): at each word boundary the base becomes `base . (A_((clock-1) mod 5) . sigma)`.
  The per-word step is a keyed permutation whose identity depends on the clock phase at the boundary. The odometer
  variant instead shifts the base by an inner dial that advances one step per word, with an outer dial that carries
  when the inner one wraps.

## Simulator

`encrypt` groups the rune stream into words by word id (as the odometer simulator does) and draws every key from `rng`:
`K = rng.sample(range(29), 29)`, `offsets = schedule(rng, zeros=1)`, `alpha = alphabets(K, offsets)`,
`sigma = conj_shift(rng.sample(range(29), 29), rng.randrange(1, 29))`, `base0 = rng.sample(range(29), 29)`, then
`encipher(words, base0, alpha, sigma)`. This is the key form that `quagmire_dodge.fit()` and `dodge_scorer_check.py` use.

Key-draw check (PROOF line 7): seed 1000 and seed 1001 give different ciphertexts on the same plaintext (sha256 prefixes
`856ec00f63b1ca96` and `949be36c5320d58b`); seed 1000 reproduces (`856ec00f63b1ca96`).

## Gate output, 3 seeds (`gate_sim.py --seeds 3`, run after `source agents/laneO_quagmire_dodge/env.sh`)

```
cipher: Quagmire with clock-dependent word step and doublet dodge (community quagmire_dodge.encipher: base steps by alpha_k . sigma, one-zero schedule)
seed 0: doublets 91 (69 within, 22 cross), lag-5 112/1828
  C1 IoC                               1.0012     LP2 1.0      PASS
  C2 doublet rate                      0.00702    LP2 0.00664  PASS
  C2b conditional IoC                  1.0251     LP2 1.026    PASS
  C2c doublet positions mod 2..8       mod5 chi2 4.4 LP2 uniform  PASS
  C3 repeated words >=3                8          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0613     LP2 0.0494   FAIL(soft)
  C6 cross-word doublets (LP2-size)    22.0       LP2 23       PASS
seed 1: doublets 81 (64 within, 17 cross), lag-5 106/1828
  C1 IoC                               1.0005     LP2 1.0      PASS
  C2 doublet rate                      0.00625    LP2 0.00664  PASS
  C2b conditional IoC                  1.0299     LP2 1.026    PASS
  C2c doublet positions mod 2..8       mod5 chi2 4.0 LP2 uniform  PASS
  C3 repeated words >=3                7          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.058      LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    17.0       LP2 23       PASS
seed 2: doublets 115 (89 within, 26 cross), lag-5 92/1828
  C1 IoC                               0.9992     LP2 1.0      PASS
  C2 doublet rate                      0.00888    LP2 0.00664  PASS
  C2b conditional IoC                  1.0163     LP2 1.026    PASS
  C2c doublet positions mod 2..8       mod6 chi2 4.7 LP2 uniform  PASS
  C3 repeated words >=3                5          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0503     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    26.0       LP2 23       PASS
fails per constraint over 3 seeds: none
GATE PASS
```

## Gate output, 12 seeds (`gate_sim.py --seeds 12`)

Per-seed rows are in `2026-10-17-quagmire_dodge_clock_gate12.txt`. The decision lines:

```
seed 9: doublets 138 (113 within, 25 cross), lag-5 102/1828
  C2 doublet rate                      0.01065    LP2 0.00664  FAIL
  ...
fails per constraint over 12 seeds: {'C2': 1}
GATE PASS (marginal: C2)
```

C2 failed on 1 of 12 seeds (seed 9, rate 0.01065 above the band's 0.010). C5 failed softly on seeds 0, 3 and 4 (not
counted). No hard constraint failed on a majority of seeds, so the gate passes.

## Twelve-key family means beside LP2 (`tools/family_means.py`)

| statistic | clock-dependent dodge, 12 keys | odometer dodge, 12 keys (`2026-10-16-quagmire_odometer_dodge.md`) | LP2 |
|---|---|---|---|
| doublets | 90.9 +- 22.1 (65 to 138) | 87.4 (62 to 131) | 86 |
| within-word / cross-word doublets | 66.8 / 24.2 | not reported | 63 / 23 |
| cross-word doublets | 24.2 +- 6.0 (12 to 35) | 22.1 +- 6.2 (10 to 31) | 23 |
| cross-word share (pooled, sum cross / sum doublets) | 0.266 | 0.266 | 0.267 |
| cross-word share (mean of per-seed shares) | 0.283 +- 0.099 | not reported | 0.267 |
| within-word lag-5 rate | 0.0573 (sd 0.0031 over 12 keys) | 0.0572 | 0.0494 |
| doublet rate (C2 row) | 0.00702 mean | not reported | 0.00664 |
| C2c, doublet positions mod 2..8 | uniform on 12 of 12 (worst chi-square 17.5, mod 8; p = 0.001 value 24.3) | uniform on every seed | uniform |

LP2 sits 2.5 sd below the family's lag-5 mean. The odometer shows the same offset (0.0572). The soft C5 band
(0.039 to 0.060) admits both, but the family's echo runs high on average.

## Census: 300 random keys (`walk_draws.py --draws 300`, rng seeds 5000 to 5299)

| constraint | draws passing |
|---|---|
| C1 | 300 / 300 |
| C2 | 247 / 300 |
| C2b | 300 / 300 |
| C2c | 297 / 300 |
| C3 | 291 / 300 |
| C6 | 265 / 300 |
| all hard constraints | 211 / 300 (70%) |

The typical key passes. Doublet rate spans 0.0023 to 0.0168; cross-word doublets span 6 to 47. This is not a small
passing set, so there is no narrowing to do before a lane.

## What the hypothesis predicts for C4 and C5, and what the gate does not check

- C4 (layout): INFO only, as for every simulated cipher. The simulator uses English word lengths (z -5.69). The cipher
  copies the plaintext's word lengths, so LP2's layout (z +0.9) is a constraint on the register, not the cipher. An
  attack must use a register matched to LP2's word lengths, as lane O's sweep did.
- C5 (within-word lag-5): predicted about 0.057, above LP2's 0.0494 (see table). This model produces the echo at the
  same level as the odometer; it does not account for LP2's lower value.
- C3 is one-sided (it fails only on excess). The family's repeated-word counts are 3 to 9 (mean 6.6) against LP2's 16,
  and the odometer's 3-seed values were 5 to 12. The gate does not penalise this deficit. An attack should report it.

## Prior coverage

Grep terms: `quagmire.dodge` (matches both spellings), `dodge`, `clock-depend`, `alpha.*sigma`, `word.step`,
`dodge.*sweep` and `sweep.*dodge`, `sigma`, and `sweep` inside `doublet-dodge-walk.md`.
Files searched: `REPORT.md`, `REPORT_ROUND2.md`, `toolbox/CONSTRAINTS.md` (read in full), `dl/dukotah/liber-primus/LEDGER.json`,
`dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, `dl/leo/docs/FINDINGS.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`,
`dl/aldegonde_clone/hypotheses/quagmire-dodge.md`, `dl/aldegonde_clone/hypotheses/doublet-dodge-walk.md`,
`agents/laneO_quagmire_dodge/RESULTS.md`, `dl/aldegonde_port/experiments/quagmire_dodge.py`.

Findings:

1. **Not run.** `quagmire-dodge.md` around line 373 reads "It has NOT been run. Michel's call, 2026-09-21: the sweep stays
   parked." No ledger, `REPORT.md` or `REPORT_ROUND2.md` entry reports a run of `quagmire_dodge.encipher` on LP2. The
   only hits are `INDEX.md` lines 84, 95 and 156, which are the community's own notes on this hypothesis.
2. **Priced once, on a scorer that cannot see it.** The first plan (`quagmire-dodge.md` lines 214 to 236) prices this
   family at 30 core-hours over 3301's vocabulary (4.92e9 keys), using `walk_score_kernel` (sigma-based). `dodge_scorer_check.py`
   plants this encipher's true key and finds it does not separate: 0.493 against 0.619 for the best of 2,000 wrong sigmas
   (`quagmire-dodge.md` lines 244 to 265). That result is the community's own; I did not re-run it.
3. **The replacement scorer is validated only on the odometer.** `dodge_aware_scorer.py` (the 'z = 12 to 20' result)
   imports `doublet_phase_test.encipher` and nothing from `quagmire_dodge`. Its `word_shifts` gives each word an
   odometer shift, not this encipher's per-word permutation.
4. **Lane O covers the odometer, not this family.** `agents/laneO_quagmire_dodge/RESULTS.md` section 4c says
   "Not covered by this control: `quagmire_dodge.encipher`". Lane O's tiers A and B (577.8 million keys, 47 words,
   both null) search `doublet_phase_test.encipher` with dials.
5. **The later-priced sweep is the odometer.** The unbanded sweep priced at 218 core-hours in `quagmire-dodge.md`, and the
   3.9e9-key sweep in `REPORT_ROUND2.md` (row O), share one count: 1,264 alphabets x 105,980 schedules x 29 dials =
   3.885e9. That is the odometer family, which lane O ran. `doublet-dodge-walk.md` has no sweep of this family.

So this encipher was priced once on a scorer that cannot see it, and the sweep that was later run is the odometer. The
replacement scorer is unvalidated on this model. It is not `ALREADY TESTED`, but it is not untested in the sense of
having a working scorer either.

## For PROCEED

**Key space.** The raw parameter tuple is K (29!, about 10^30.9), the schedule (105,980 one-zero schedules), sigma
(a 29-cycle, of which there are 28!, about 10^29.5) and base0 (29!, about 10^30.9): about 10^96.4 in total. A walk
scorer solves base0 by assignment, so base0 is not enumerated. The community's vocabulary reduction is 1,264 alphabets
(316 words, 4 rules) times 105,980 schedules times 369 seam-band sigma disks: 4.94e10 keys. The 369 is the community's
seam-band reduction, which is an assumption, not a measured bound. At lane O's measured 3,000 keys/s/core (REPORT_ROUND2),
4.94e10 keys is about 4,600 core-hours. The community's 30 core-hours assumed the walk kernel's 45,000 keys/s/core,
and that kernel cannot see the key, so the figures are not comparable. Its d1/d4/d6 rate bands keep only 9% of true keys (`quagmire-dodge.md` around line 373).

**Scorer, and whether the odometer scorer adapts.** The attack lane needs a dodge-aware scorer for this encipher, not
lane O's. The lane O / community scorer (`dodge_aware_scorer.py`, `dodge_score_kernel`) assumes the odometer step:
`build()` maps each word to an (inner, outer) shift from `word_shifts`. Adaptation is possible but not a drop-in:

- Keep `letter_maps`, `assign`, `refit_phases` and the phase-fitting loop. The fire condition
  `base^-1(c_j) = R(base^-1(c_(j-1)))` with `R = A_(k+d) . A_k^-1` still holds.
- Replace `word_shifts` with the per-word permutation chain: `base_w = base_(w-1) . compose(A_phase, sigma)`, with the
  phase at each boundary taken from the fitted clock (after the fires). `quagmire_runner.word_products` computes a
  similar chain, but it takes the phase as `(word length - 1) mod 5`, which is the clock only when no dodge fired, so
  it cannot be used as is.
- Make sigma a key input (29-cycles), so the key search enumerates sigma or a band of it.
- Validate before any sweep: plant true keys of `quagmire_dodge.encipher` (not the odometer), then check separation.
  Until that passes, the scorer is unvalidated for this model.

**Planted control.** At least 100 plants of `quagmire_dodge.encipher`, each with a random vocabulary keyword, a random
one-zero schedule, a random sigma from the seam band and a random base0, enciphered over a matched register (400 words,
the lane O sweep's text length). Require the planted key at rank 1 among the sweep's scored keys in most plants. List
every miss. The port-community-code PROOF requires at least 20 plants with misses listed (CHANGELOG 2026-10-16).

**Null.** Two nulls, as lane O's adjudicator does: (a) 200 random keys drawn from the same generator (K from the
keyword family, one-zero schedule, seam-band sigma, base0 solved), scored on the same chunks; (b) a held-out
adjudication on the remaining LP2 words (six 400-word chunks, pinned best dial replaced by best base0). A candidate must
sit above the null max on all held-out chunks.

**Oracle.** Any candidate goes to `dl/dukotah/liber-primus/verify_solution.py --plaintext` and `lp/verify_candidate.py`.
No solve is claimed without the oracle.

## Fixes made this run

- `jobs/hypothesis-gate/tools/walk_draws.py`: its `HARD` tuple and report rows omitted C2c, which `gate_sim.py` counts as
  hard since 2026-10-16. Both now use the same set. Logged in `CHANGELOG.md` (2026-10-17, hypothesis-gate).
- New: `jobs/hypothesis-gate/tools/family_means.py`, which prints the 12-key table from any saved gate output.

## Not done

- Did not re-run `dodge_scorer_check.py` (its result is cited from `quagmire-dodge.md`).
- Did not write or validate a clock-variant scorer; that is the attack lane's job.
- Did not edit lane O's `RESULTS.md` (its section 4c still states the variant is not covered), nor commit anything.

## PROOF (`jobs/hypothesis-gate/PROOF.md`), line by line

Output:
1. PASS. The report names `quagmire_dodge_clock`, links `runs/quagmire_dodge_clock_cipher.py`, and the simulator defines `encrypt(plain, words, rng)`.
2. PASS. The full `gate_sim.py --seeds 3` output, including `GATE PASS`, is pasted above.
3. PASS. Verdict: `PROCEED`.
4. PASS. Not applicable: no gate FAIL. The 12-seed marginal (C2) is reported, not ignored.
5. PASS. The grep terms and files searched are listed under Prior coverage.
6. PASS. For PROCEED: the key space and the planted-control and null design are given above.
7. PASS. Every key is drawn from `rng`; seeds 1000 and 1001 differ, and seed 1000 reproduces.

Fixture:
8. PASS. `otp_dodge5.py` gives `GATE PASS`; `vigenere7.py` gives `GATE FAIL: C1 C2 C2b C2c C3 C6`; `norepeat.py` gives `GATE FAIL: C2 C6`. All three match `data/fixture/expected.md`.

Tools:
9. PASS. `dynsub_checks.py` runs clean (wheels stay permutations; seeds differ; seeds reproduce).
10. PASS after fix. `walk_draws.py` now counts C2c as hard; its 300-draw census ran (211/300).
11. PASS. `family_means.py` runs on the 12-seed output.
