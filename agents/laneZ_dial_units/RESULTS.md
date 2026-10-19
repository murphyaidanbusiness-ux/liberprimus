# Lane Z: the any-alphabet odometer dodge with the dial stepping per line, sentence, page or chapter (2026-10-18)

**Verdict: NULL.** With the inner dial stepping once per unit of LP2's own layout instead of once per word, lane X's
key-free detector catches 24/24 planted keys (6 per unit, stage-1 score +0.105 to +0.332) and decrypts 15. LP2 sits
inside 30 nulls for every unit: lines 0.0185 (z +0.67), sentences 0.0203 (z +0.79), pages 0.0195 (z +0.76), chapters
0.0241 (z -0.44).

- Gate: jobs/hypothesis-gate/runs/2026-10-16-quagmire_odometer_dodge.md (GATE PASS, marginal C6) and
  jobs/hypothesis-gate/runs/2026-10-17-quagmire_odometer_dodge_hold.md (GATE PASS, marginal C3)

## Hypothesis

Every word-keyed attack so far (lanes O, X and Y and the community's sweep) assumes the odometer's inner dial steps once
per visible word. LP2's layout is not the plaintext's layout (C4: word lengths have English marginals but no English
sequence), and the lag-5 echo is sharper across line breaks (C5, post hoc). So the dial may step per unit of the book's
own layout instead. Four units, each tested separately: the 594 lines (field `line`, 3 to 26 runes), the 175 sentences
(`sent`, 3 to 375), the 55 pages (66 to 277) and the 17 chapters (`chap`, 9 to 2,474), all with global ids.

Key space per unit as lane X: K any of 29! alphabets, any one-zero schedule, any start dials, both variants and space
skips 0-4: about 8 x 10^39 keys. Fixed-length blocks are not tested: a dial stepping every L runes makes the key periodic
(period 29L), which C1 excludes for every L up to 51.

**Method:** lane X's pipeline unchanged (`agents/laneX_general_alphabet/pipeline.py`), with the units passed in place
of words, so a group is (unit index mod 29, clock phase). The dead-chain floor is on (`xlib.FLOOR = 1e-4`).

## Control

Plants (`run_laneZ.py`): English from `toolbox/runes.english_stream` (offsets 600000 + 20000 i), cut into LP2's units,
enciphered by `xlib.encipher_trace` (equal to the community encipher) with the dial stepping per unit; random K,
schedule and dials; 6 per unit, advance and hold alternating.

| dial steps per | plants | stage-1 score min / max | detected (above that unit's null max) | decrypted (>= 80% of runes) |
|---|---|---|---|---|
| line | 6 | 0.105 / 0.222 | 6/6 | 4/6 (one at 70%, one failed at 6%) |
| sentence | 6 | 0.137 / 0.291 | 6/6 | 4/6 (two failed at 13% and 19%) |
| page | 6 | 0.118 / 0.291 | 6/6 | 4/6 (two failed at 5% and 7%) |
| chapter | 6 | 0.284 / 0.332 | 6/6 | 3/6 (three failed at 8%, 21% and 35%) |

Recovered 24/24 at the detection level. Rank 1: the attack returns one solution per ciphertext, so "decrypted" means
that single answer is the planted plaintext (rank 1 of 1). The weakest plant per unit is 34 to 86 null sd above its
null mean. Detection, not decryption, carries the exclusion.

## Null

30 shuffles per unit with `toolbox/nulls.shuffle_increments` (increments permuted within each page: keeps the 86
doublets and page lengths), cut into the same units, each through the identical pipeline (`out/all.jsonl`).

| unit | null mean | sd | max |
|---|---|---|---|
| line | 0.0171 | 0.0022 | 0.0200 |
| sentence | 0.0182 | 0.0026 | 0.0254 |
| page | 0.0172 | 0.0030 | 0.0267 |
| chapter | 0.0254 | 0.0030 | 0.0321 |

## Real result

LP2 pages 0-54 (SHA pin asserted), stage-1 score and z against its unit's nulls:
- Lines: 0.0185, z +0.67, 11 of 30 nulls as high; stage 2 quadgram -6.531 (noise).
- Sentences: 0.0203, z +0.79, 3 of 30; -6.538.
- Pages: 0.0195, z +0.76, 5 of 30; -6.523.
- Chapters: 0.0241, z -0.44, 20 of 30; -6.519.

No chain died in any run (0 dead chains in 148 runs).

## Verdict

NULL for a dial stepping per line, per sentence, per page or per chapter, for every keyed alphabet, both variants and
space skips 0-4, with one continuous key. Together with lanes X and Y: the odometer dodge is excluded with the dial per
word, line, sentence, page or chapter, and with a key that restarts per chapter or page.

Not covered: a dial stepping on units the book does not mark (true plaintext words hidden by a re-laid layout), different
start dials per segment, independent keys per segment, the clock-dependent form and the walk.

## Files

- `run_laneZ.py`: units, plants, nulls and the real runs. `out/all.jsonl`; `logs/run_all.log`.

## Verification

Re-derived 2026-10-18 by verify-lane (claude-haiku-5-5, fresh code; `jobs/verify-lane/runs/2026-10-18-laneZ.md`): the
four unit cuts and all 36 null, real and plant numbers reproduce, and the verifier's own encipher matches the community
encipher. Its fresh line-unit plant was detected (+0.125 against the line null max 0.0200) but not decrypted (5% of
runes; clock-phase accuracy 0.46). That is within lane Z's stage-2 rate (15 of 24 plants decrypted, plus this one: 15 of
25), and the exclusion rests on detection (25 of 25 including the replay).
