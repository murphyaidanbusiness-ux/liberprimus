# Lane X: the Quagmire-odometer dodge with ANY keyed alphabet (2026-10-18)

**Verdict: NULL.** A key-free detector that every full-length planted key lights up (24/24, stage-1 score +0.109 to
+0.318, of which 18 also decrypt to readable English) gives LP2 +0.0201, against 50 size-matched nulls at 0.0158 +-
0.0029 (max 0.0218; z +1.46, empirical p 0.06). So LP2 pages 0-54 are not this cipher under one continuous key, for any
of the 29! alphabets, any one-zero schedule, any start dials, both dodge variants and space skips 0-4.

- Gate: jobs/hypothesis-gate/runs/2026-10-16-quagmire_odometer_dodge.md (GATE PASS, marginal C6) and
  jobs/hypothesis-gate/runs/2026-10-17-quagmire_odometer_dodge_hold.md (GATE PASS, marginal C3)

## Hypothesis

The community's Quagmire-odometer dodge (`doublet_phase_test.encipher`, lane O's family):
c = K[pos[p] + a_w + S[phase]] + b_w (mod 29), with the inner dial a_w rising one per word, the outer dial b_w rising
one each time a_w wraps, S the running sum of a five-step schedule with exactly one zero offset, and the clock
advancing one per rune plus a drift at every dodged repeat (+1 "advance", -1 "hold") and an optional fixed number of
steps per word space (space skip 0-4).

Key space: K any permutation (29! = 8.8e30), schedule any one-zero five-step schedule summing to 0, dials (a0, b0) any
of 841, two variants, five space skips: about 10^37 keys. Lane O and tiers A+B searched only keyword-built alphabets
(188 alphabets from 47 words); the community sweep the same kind. This lane needs no assumption about K.

**Why a key-free attack exists.** Fix a word cycle r = w mod 29 and a phase k: every rune in that group is enciphered by
the same permutation, and inside the group the outer dial rises by exactly one per 29-word cycle, so subtracting
floor(w/29) leaves a fixed substitution. So the 145 groups are each a monoalphabetic substitution of English, and the
schedule ties them into 29 shift tables, whatever K is. The only unknown that decides the grouping is the clock drift.
Every surviving doublet pins the clock: under this family a doublet survives only where the dodge re-emits with the
alphabet it would have used anyway, i.e. at one fixed clock phase (checked: 86 of 86 anchors at one phase in a plant).

**The attack** (`xlib.py`, `stage2.py`, `pipeline.py`):
1. Stage 1a: counts from the runes just after each doublet (phase known) give every schedule tie its likelihood
   (`shift_scan`, 2 x 29^3 candidates). Stage 1b: a five-state hidden Markov model over the clock drift with the
   groups tied by the top candidates, fitted by Baum-Welch, for each space skip 0-4 (`fit_tied`). Statistic: the
   Dirichlet-multinomial log marginal likelihood of the fitted grouping, minus the uniform model, per rune (it has no
   fitted parameters, so noise cannot win by overfitting the tables).
2. Stage 2: the start inner dial from the tied tables (`choose_a0`); a climb of K for the unigram IoC of the decrypt,
   which aligns the 29 tables and leaves the start dials as one fixed substitution; a quadgram solve of that
   substitution (`solve_stage2`). The quadgram model is trained on Poe, Plato and Emerson, not on the plants' source.

Cost: about 35 s per ciphertext on one core (stage 1 about 25 s for five space skips; stage 2 about 1 s).

## Control

Plants: English from `toolbox/runes.english_stream` (Moby-Dick, not the scorer's training texts), enciphered by
`xlib.encipher_trace`, which equals the community `doublet_phase_test.encipher` exactly for both variants (asserted),
with K a random permutation, a random one-zero schedule and random start dials (`run_lane.py`, `layout_plants.py`).

| plants | n | stage-1 score min / median / max | detected (above null max 0.0218) | plaintext recovered (>= 80% of runes) | phase accuracy median |
|---|---|---|---|---|---|
| 12,956 runes, space skip 0, advance | 10 | 0.204 / 0.239 / 0.318 | 10/10 | 10/10 | 0.891 |
| 12,956 runes, space skip 0, hold | 10 | 0.153 / 0.253 / 0.312 | 10/10 | 8/10 | 0.901 |
| 12,956 runes, space skips 1-4 | 4 | 0.109 / 0.121 / 0.203 | 4/4 | 0/4 (skip 1: 69%) | 0.672 |
| LP2's own word lengths (English re-cut), skip 0 | 8 | 0.125 / 0.213 / 0.272 | 8/8 | 6/8 | 0.860 |
| 6,000 runes | 5 | 0.043 / 0.108 / 0.203 | not calibrated (null is full length) | 1/5 | 0.641 |
| 3,000 runes | 5 | -0.028 / 0.038 / 0.198 | not calibrated | 1/5 | 0.325 |

**Recovered 24/24 at the detection level and 18/20 decrypted** for full-length plants with space skip 0 (plus 6/8 on
LP2's layout). The two hold misses (plants 5 and 9) and the space-skip plants are stage-2 failures with stage 1 still
far above the null: the schedule was right and the clock path was 67-89% right, which is enough to detect and not
always enough for the IoC climb. Recovered plaintext reads as English (plant 3, hold, 95.2% of runes right:
`FTFEUTMOSTINTERESTBECAUSETHEREWERECERTAINENGRAFTEDCLERICALPECULIARITIESABOUTHIMIMPUTABLETOTHAT`), with the residual
errors where the clock path is wrong.

Rank 1: the attack returns one solution per ciphertext, not a ranked list, so "recovered" means that single answer is
the planted plaintext (rank 1 of 1); detection means the stage-1 score clears the null max.

## Null

50 shuffles with `toolbox/nulls.shuffle_increments` (increments permuted within each page, runes rebuilt: keeps LP2's 86
doublets, page lengths and word layout), each through the identical pipeline (`out/all.jsonl`, `out/null2.jsonl`).
Stage-1 score: mean 0.0158, sd 0.0029, max 0.0218. Stage-2 quadgram score: mean -6.528, sd 0.008, max -6.513.

## Real result

LP2 pages 0-54 (`lp/lpdata.unsolved()`, SHA pin asserted): stage-1 score **0.0201**, z +1.46 against the null; 2 of 50
nulls score as high (empirical p 0.06); null max 0.0218. The weakest full-length plant (+0.109) is 32 null sd above the
null mean. Stage 2 on the best fit: quadgram -6.519 (null max -6.513), first 120 runes
`TRDDEAHILEOEPOIOXTIAIAEDTFGAEEOAECGMNLEAEATHAEOEOTSUNPSEADYPERBUMSONMIAJLLIAAPCBEADGLDEBEOLDOEAESTULOPAUSBRUXJNGWANORBGLPPBEAWSJFEOSUUJUAOECG`
(noise). Best stage-1 fit: schedule [0, 1, 10, 9, 0], space skip 1, by space skip 0.016 / 0.020 / 0.013 / 0.012 / 0.015.

## Verdict

NULL. The Quagmire-odometer dodge is excluded for LP2 as one continuous key over pages 0-54, for every keyed alphabet,
not just keyword ones, at full detection power (24/24 full-length plants, 8/8 on LP2's layout), for both variants and
space skips 0-4. This supersedes tier C of lane O for continuous keys (tier C would only add more keyword alphabets).

What it does not exclude:
- **A key that restarts per section or page.** Detection needs a long single-key span: at 6,000 runes stage-1 scores fall
  to 0.04-0.20 and recovery to 1/5; at 3,000 the detector is weak. Lane O's keyword sweep, which scores the first 400
  words, remains the only test for short keyed spans, and only for keyword alphabets.
- **Word units other than LP2's separators.** The dial steps per word; if the visible separators are not the
  encipherer's units (C4 says the layout is not the plaintext's layout), every word-keyed model, this one and lane O's
  included, is mis-specified.
- **The clock-dependent variant** (lane W, word maps cumulative) and Oosterhof's walk: their groups are not fixed
  substitutions, so this detector does not apply.

## Files

- `xlib.py`: the traced cipher (equal to the community encipher), LP2 and English loaders, the stage-1 detector.
- `stage2.py`: quadgram model, a0 choice, the IoC alignment climb, the substitution solve (and the abandoned
  approaches: the (A, b0) grid climb, the two-alphabet climb, the Caesar-blind difference model, kept for the record).
- `pipeline.py`: the end-to-end attack. `run_lane.py`: plants, nulls and the real run. `layout_plants.py`: plants on
  LP2's word lengths.
- `out/all.jsonl` (34 plants, 20 nulls, real), `out/null2.jsonl` (30 more nulls), `out/layout_plants.jsonl`;
  `logs/run_all.log`, `logs/run_null2.log`, `logs/layout_plants.log`.

## Verification

Re-derived 2026-10-18 by verify-lane (claude-haiku-5-5, fresh code; `jobs/verify-lane/runs/2026-10-18-laneX.md`):
the traced cipher equals the community encipher on 6 fresh plants and every (word cycle, phase) group is a fixed
substitution; every doublet sits at one phase on 10/10 plants; the nulls keep 86 doublets and the page lengths; the null
mean, sd and max, the real score, z +1.46 and 2 of 50 all reproduce; a fresh plant enciphered by the verifier's own code
is detected (+0.259) and decrypted (91.1% of runes). One expectation differed, not a lane number: the untied 145-group
DM statistic with alpha 1 has a no-signal floor near -0.10 per rune (LP2 zero-drift -0.0985, nulls -0.1014 +- 0.0024),
so only the null comparison, not the sign of a raw score, carries meaning.
