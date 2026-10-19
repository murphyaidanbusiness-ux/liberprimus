# Lane Y: the any-alphabet odometer dodge with a key that restarts per chapter or per page (2026-10-18)

**Verdict: NULL.** Lane X's key-free detector, adapted so the key restarts at every segment, detects 20/20 planted
restart keys on LP2's layout (stage-1 score +0.107 to +0.311; 12/20 decrypted). LP2 scores 0.0178 with chapter
restarts (50 nulls 0.0162 +- 0.0022, max 0.0205; z +0.74) and 0.0174 with page restarts (50 nulls 0.0183 +- 0.0029,
max 0.0259; z -0.29). So LP2 is not this cipher with the same key restarted at each chapter or each page, for any alphabet.

- Gate: jobs/hypothesis-gate/runs/2026-10-16-quagmire_odometer_dodge.md (GATE PASS, marginal C6) and
  jobs/hypothesis-gate/runs/2026-10-17-quagmire_odometer_dodge_hold.md (GATE PASS, marginal C3)

## Hypothesis

Lane X (`agents/laneX_general_alphabet/RESULTS.md`) excluded the Quagmire-odometer dodge for every keyed alphabet under
ONE continuous key over pages 0-54, and said its detector is weak below about 6,000 runes of one key. Here the same key
(K, one-zero schedule, start dials, variant) restarts from its start setting at every segment, the way LP1's keyed pages
restarted their key. Two segmentations, tested separately: the 17 chapters (field `chap`, 9 to 2,474 runes) and the 55
pages (66 to 277 runes).

Key space as lane X: K any of 29! alphabets, any one-zero schedule, any start dials, both variants ("advance" and
"hold"), space skips 0-4; about 8 x 10^39 keys per segmentation (29! x 105,980 x 841 x 2 x 5). What is new: restarts. Lane X is blind to them: on 4
planted restart keys it scores +0.017 to +0.023, at its noise level, while lane Y scores +0.135 to +0.307
(`dev_check.py`, `logs/dev_check.log`).

**The adaptation** (`ylib.py`): with the same key restarted, each segment's word cycle is its word index inside the
segment and its outer dial restarts too, so the groups (local word cycle, phase) are the same fixed substitutions in
every segment and the evidence of all segments pools. The clock restarts, so the hidden drift may jump at a segment
start (uniform transition there); a doublet across a segment start is not an anchor. Stage 2 uses segment-local word
indices; otherwise it is lane X's pipeline.

## Control

Plants (`run_laneY.py`): English from `toolbox/runes.english_stream` (offsets 200000 + 20000 i) re-cut into LP2's exact
word lengths, enciphered segment by segment by `xlib.encipher_trace` (equal to the community encipher) with one random
key restarted at each segment; 10 per segmentation, advance and hold alternating.

| segmentation | plants | stage-1 score min / max | detected (above that segmentation's null max) | decrypted (>= 80% of runes) |
|---|---|---|---|---|
| chapter | 10 | 0.107 / 0.303 | 10/10 | 6/10 (two more at 70% and 73%; two failed at 6%) |
| page | 10 | 0.131 / 0.311 | 10/10 | 6/10 (two more at 74% and 75%; two failed at 7% and 10%) |

Recovered 20/20 at the detection level. Rank 1: the attack returns one solution per ciphertext, so "decrypted" means
that single answer is the planted plaintext (rank 1 of 1). The misses at stage 2 have stage 1 far above the null, as in
lane X; detection, not decryption, carries the exclusion.

## Null

50 shuffles per segmentation with `toolbox/nulls.shuffle_increments` (increments permuted within each page: keeps the
86 doublets, page lengths and word layout), each through the identical pipeline with that segmentation (`out/all.jsonl`).
- Chapter: stage-1 score mean 0.0162, sd 0.0022, max 0.0205.
- Page: mean 0.0183, sd 0.0029, max 0.0259.

## Real result

LP2 pages 0-54 (SHA pin asserted).
- Chapter restarts: stage-1 score 0.0178, z +0.74, 10 of 50 nulls as high; stage 2 quadgram -6.513 (noise).
- Page restarts: 0.0174, z -0.29, 31 of 50 nulls as high; quadgram -6.535.
The weakest chapter plant is 41 null sd above the chapter null mean; the weakest page plant 39.

## Verdict

NULL for the same key restarted at every chapter or every page, for every keyed alphabet, both variants, space skips 0-4.

Not covered:
- **Different start dials per segment** (K and schedule shared, dials changing between segments). The groups no longer
  line up across segments without a per-segment alignment search (29 x 29 offsets per segment); not built.
- **Independent keys per segment.** Each segment would then stand alone, and most are far below the ~6,000 runes the
  detector needs.
- As in lane X: word units other than the visible separators, the clock-dependent form, and the walk.

## Files

- `ylib.py`: segment-local observations, anchors and the restart HMM; stage 2 with local word indices.
- `run_laneY.py`: plants, 100 nulls and the real runs. `dev_check.py`: the lane X blindness check.
- `out/all.jsonl`; `logs/run_all.log`, `logs/dev_check.log`.

## Robustness: dead chains (2026-10-18)

Lane Y's verifier flagged RuntimeWarnings in the run logs. Cause: a Baum-Welch chain gets all-zero forward mass when a
doublet anchor demands a clock phase two or more drift steps from where its path sits; that chain then yields a
garbage grouping. `xlib.FLOOR` (default 0, as in the original runs) now adds a small floor to every drift transition,
and every fit reports whether its chain stayed finite. `agents/laneY_section_reset/floor_check.py`
(`out/floor_check.jsonl`, `logs/floor_check.log`):
- LP2 with the original setting (floor 0): **0 of 40 chains dead** for lane X, lane Y chapter and lane Y page, so the
  reported LP2 scores did not depend on a dead chain. The warnings came from some plant or null runs.
- With floor 1e-4: LP2 0.0211 (lane X), 0.0181 (chapters), 0.0182 (pages) against 20 nulls each at 0.0167 +- 0.0027
  (max 0.0219), 0.0173 +- 0.0031 (max 0.0239) and 0.0184 +- 0.0032 (max 0.0234): z +1.62, +0.24, -0.06. Planted keys
  4/4 detected in each test. The verdict is unchanged.

## Verification

Re-derived 2026-10-18 by verify-lane (claude-haiku-5-5, fresh code; `jobs/verify-lane/runs/2026-10-18-laneY.md`):
segment counts, the restart cipher (equal to the community encipher on 144/144 segments, groups a fixed substitution
shared across segments), every null and real number, and a fresh page-restart plant enciphered by the verifier's own code
(+0.292, 93.6% decrypted) all reproduce. It corrected the key-space size (now about 8 x 10^39) and flagged the dead-chain
warnings, resolved in the section above.
