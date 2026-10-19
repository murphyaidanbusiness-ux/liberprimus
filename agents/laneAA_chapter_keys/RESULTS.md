# Lane AA: the any-alphabet odometer dodge with a separate key for each part of the book (2026-10-18)

**Verdict: NULL (not detected) for any one key that covers about 6,000 or more consecutive runes; OPEN for keys on
single chapters.**
Lanes X, Y and Z assume one alphabet K and one schedule for the whole of LP2. LP1's sections each had their own key.
Here lane X's key-free attack runs on parts of LP2, each part free to have its own K, schedule, dials, variant and space
skip:

- **Windows of 6,000 runes** (stride 3,000; every span of 9,005+ runes holds one): 15 of 16 plants caught, LP2 null in
  all 4 windows (z -1.00 to +0.44).
- **Windows of 4,000 runes** (stride 2,000; every span of 6,003+ runes holds one): 19 of 24 plants caught, LP2 null in all
  6 windows (z -1.22 to +2.04). The one window above all 20 of its nulls fell to z +1.53 against 100 fresh nulls
  (7 of 100 as high), and windows shifted by 500 or 1,000 runes either way score z -0.61 to +0.71.
- **Single chapters: no power.** The largest chapter has 2,474 runes. At that length lane X catches 1 of 4 plants
  against 8 nulls (power curve) and 2 of 3 against 5 nulls on chapter 14 itself, by margins of only 0.007 and 0.038,
  and a new phase-free statistic built for short spans also fails (below). A key per chapter stays untested.

- Gates: jobs/hypothesis-gate/runs/2026-10-16-quagmire_odometer_dodge.md (GATE PASS, marginal C6) and
  jobs/hypothesis-gate/runs/2026-10-17-quagmire_odometer_dodge_hold.md (GATE PASS, marginal C3). A part of the book
  under its own key is the same cipher on a shorter text, so the fingerprint test is unchanged.

## Hypothesis

LP2 is the Quagmire-odometer dodge (`doublet_phase_test.encipher`, advance or hold, space skip 0-4) with any keyed
alphabet, but the book is cut into parts and every part has its own independent key. Per part: K any of 29!, any
one-zero schedule, any start dials, either variant, any space skip. Lane X's key-free attack needs no key, so the key
space per part is again about 8 x 10^39 and is never enumerated.

**Method:** lane X's pipeline unchanged (`agents/laneX_general_alphabet/pipeline.py`, dead-chain floor on,
`xlib.FLOOR = 1e-4`), run on each part alone. The part boundaries are unknown, so the test uses overlapping windows: a
window that lies inside one key's span sees one key, and windows of T runes at stride T/2 (cut on word boundaries) put
a whole window inside every span of about 1.5 T runes: 6,003 or more for T 4,000, 9,005 or more for T 6,000.

## 1. Single chapters (`run_laneAA.py probe`, `out/probe.jsonl`)

Three chapters, 3 plants (English in the chapter's word layout, random key) and 5 nulls each:

| chapter | runes | null mean / max | plants | LP2 run |
|---|---|---|---|---|
| 14 | 2,474 | +0.0084 / +0.0271 | -0.012, +0.034, +0.065 (0 of 3 decrypted) | not run |
| 8 | 1,021 | -0.0392 / -0.0030 | -0.035, +0.006, +0.019 | not run |
| 15 | 534 | +0.0143 / +0.0415 | -0.071, -0.030, +0.007 | not run |

Plants and nulls overlap. With 29 free substitution tables, a chapter gives each table 18 to 85 runes, and the
Dirichlet cost of fitting a table eats the gain from English letter frequencies. So the full per-chapter sweep
(9 chapters of 500+ runes) was not run: it could only return noise.

## 2. Power curve (`power_curve.py`, `out/power.jsonl`)

Plants and nulls on the first N runes of LP2's word layout, full pipeline (all space skips, stage 2), 4 plants and
8 nulls per size:

| runes | null mean / sd / max | plants min / max | above the null max | decrypted (>= 80%) |
|---|---|---|---|---|
| 2,476 | 0.0046 / 0.0043 / 0.0126 | -0.046 / +0.017 | 1/4 | 0/4 |
| 4,001 | 0.0205 / 0.0069 / 0.0289 | +0.031 / +0.096 | 4/4 (the lowest by 0.002) | 0/4 |
| 6,002 | 0.0206 / 0.0037 / 0.0258 | +0.069 / +0.255 | 4/4 | 1/4 |
| 8,001 | 0.0163 / 0.0045 / 0.0225 | +0.067 / +0.260 | 4/4 | 1/4 |
| 12,956 | 0.0194 / 0.0028 / 0.0227 | +0.080 / +0.201 | 4/4 | 3/4 |

Detection starts near 4,000 runes and is solid from 6,000. Decryption needs the full book (lane X: 18 of 20). The lane
rests on detection, as lanes X, Y and Z do.

## 3. Windows (`run_windows.py 4000` and `6000`, `out/windows_4000.jsonl`, `out/windows_6000.jsonl`)

Each window: 4 plants (English in that window's word layout, a random key, variants alternating, random space skip)
and 20 nulls (the same window cut from `toolbox/nulls.shuffle_increments` of LP2, which keeps the 86 doublets and page
lengths), all through the identical pipeline.

T = 4,000, stride 2,000:

| window | runes (offsets) | null mean / sd / max | plants above max | plants min / max | LP2 | z | nulls as high |
|---|---|---|---|---|---|---|---|
| 0 | 0-4,001 | 0.0207 / 0.0033 / 0.0270 | 3/4 | +0.003 / +0.211 | 0.0166 | -1.22 | 17 of 20 |
| 1 | 2,008-6,002 | 0.0210 / 0.0054 / 0.0365 | 2/4 | -0.001 / +0.221 | 0.0224 | +0.27 | 6 of 20 |
| 2 | 4,001-8,001 | 0.0189 / 0.0048 / 0.0246 | 3/4 | +0.004 / +0.062 | 0.0242 | +1.11 | 2 of 20 |
| 3 | 6,002-10,001 | 0.0189 / 0.0050 / 0.0270 | 4/4 | +0.042 / +0.083 | 0.0291 | +2.04 | 0 of 20 |
| 4 | 8,001-12,006 | 0.0197 / 0.0043 / 0.0276 | 4/4 | +0.056 / +0.074 | 0.0183 | -0.32 | 13 of 20 |
| 5 | 8,952-12,956 | 0.0215 / 0.0059 / 0.0363 | 3/4 | +0.030 / +0.047 | 0.0185 | -0.50 | 14 of 20 |

T = 6,000, stride 3,000:

| window | runes (offsets) | null mean / sd / max | plants above max | plants min / max | LP2 | z | nulls as high |
|---|---|---|---|---|---|---|---|
| 0 | 0-6,002 | 0.0201 / 0.0033 / 0.0272 | 4/4 | +0.076 / +0.101 | 0.0216 | +0.44 | 5 of 20 |
| 1 | 3,000-9,000 | 0.0191 / 0.0030 / 0.0245 | 4/4 | +0.055 / +0.089 | 0.0170 | -0.70 | 13 of 20 |
| 2 | 6,002-12,006 | 0.0197 / 0.0050 / 0.0324 | 3/4 | +0.024 / +0.086 | 0.0172 | -0.50 | 14 of 20 |
| 3 | 6,954-12,956 | 0.0212 / 0.0032 / 0.0276 | 4/4 | +0.056 / +0.073 | 0.0181 | -1.00 | 17 of 20 |

No chain died in any run (0 dead chains). The six misses, each against its window's null max: T 4,000 window 0 plant 3
(hold, +0.0034 vs 0.0270), window 1 plants 1 and 2 (hold -0.0006, advance +0.0077, vs 0.0365), window 2 plant 0
(advance +0.0040 vs 0.0246), window 5 plant 1 (hold +0.0301 vs 0.0363); T 6,000 window 2 plant 3 (hold +0.0243 vs
0.0324). Four of the six are hold plants. Rank 1: the attack returns one answer per ciphertext, so "caught" means that
one answer scores above every null of its window.

**The window 3 margin, checked** (`window_followup.py`, `out/followup.jsonl`). Stage 1 is deterministic, so a new seed
cannot move LP2's score. 100 fresh nulls for the window (seeds 62000-62099): mean 0.0208, sd 0.0057, max 0.0360. LP2
on the window as re-cut (4,003 runes) scores 0.0295, z +1.53, 7 of 100 nulls as high. Shifted by -1,000, -500, +500 and
+1,000 runes: 0.0174, 0.0249, 0.0203, 0.0186 (z -0.61, +0.71, -0.09, -0.38). Chance: with six windows, one window above
20 nulls is expected about a quarter of the time. Not a lead (CLAUDE.md requires z >= 5 that survives held-out text).

## 4. A short-span statistic that does not work (`coincidence_probe.py`, `out/coincidence_probe.txt`)

To reach single chapters, the probe drops the tables, the schedule and the clock path. Two runes at the same clock
phase in words w and w+d use keys that differ by exactly d. So whenever their plaintext letters agree,
y_u = rho^d(y_t), where rho = K' add(1) K'^-1 is a 29-cycle (K' is K with the outer start dial folded in). The probe
counts those coincidences over pairs up to 24 runes apart and 1 to 4 words apart, and hill-climbs K' (30 restarts).

- The signal is real. The true rho gives coincidence rates of 0.048 to 0.057 against 1/29 = 0.034 for a random cycle.
- It is too small. On chapter 14 (about 8,500 pairs) the true rho carries 30 to 50 nats of evidence, and on chapter 8,
  9 to 21. Choosing among the 28! (10^29.5) cycles costs 68 nats. So the climb on a null finds cycles that score as high
  as the true one (rates 0.0555 to 0.0564 on chapter 14, against 0.0508 to 0.0562 for the true rho). The climb never
  found the true rho (0 of 6 plants). LP2's chapter 14 and chapter 8 scores sit among the plants and nulls.

A short-span attack therefore needs the per-rune English evidence (about 0.45 nats per rune: about 1,100 nats on
chapter 14), which means fitting K, the schedule and the clock path together. That search is not built.

## Verdict

NULL (not detected) for the odometer dodge with any keyed alphabet, both variants and space skips 0-4, when one key
covers 6,003 or more consecutive runes anywhere in LP2. Power per contained window: 19 of 24 for 4,000-rune windows
(Wilson 95% interval 0.60 to 0.91) and 15 of 16 for 6,000-rune windows (0.72 to 0.99), and a long key span contains
several windows. So a book in two parts with their own keys is not detected either, because the larger part has 6,478
runes or more. Together with lanes X, Y and Z: the odometer dodge is not detected for one continuous key, for keys
restarted per chapter or page, for a dial per line, sentence, page or chapter, or for any key over about 6,000 runes.

Not covered: a key per chapter, or any key used on fewer than about 6,000 runes (needs a joint K, schedule and path
search), different start dials per segment under one K, the clock-dependent form and the walk. One narrow piece of the
clock form is now closed by the gate: with sigma built from the same alphabet K (one keyword for everything) it repeats
words 52 to 69 times against LP2's 16, and fails C3 on 12 of 12 keys
(`jobs/hypothesis-gate/runs/2026-10-18-quagmire_dodge_clock_commuting.md`).

## Files

- `run_laneAA.py`: the single-chapter probe (`probe`); the full per-chapter design is in the code but was not run (no
  power).
- `power_curve.py`, `run_windows.py`, `window_followup.py`, `coincidence_probe.py`, `summarize.py` (prints the
  tables above).
- `out/`: `probe.jsonl`, `power.jsonl`, `windows_4000.jsonl`, `windows_6000.jsonl`, `followup.jsonl`,
  `coincidence_probe.txt`. `logs/`: run logs and the keep-awake logs.

## Verification

Re-derived 2026-10-18 by verify-lane (claude-haiku-5-5, fresh code; `jobs/verify-lane/runs/2026-10-18-laneAA.md`):
175 of 178 cell checks reproduce, including every table, the window offsets, the six misses, 0 dead chains in 439 runs,
exact stage-1 determinism on two windows, and the evidence arithmetic of section 4. Its own encipher matches the
community encipher and lane X's on 300 random cases (128,155 runes, 0 mismatches). A fresh plant on the 6,000-rune
window 1 was detected (+0.117 against the null max 0.0245) and not decrypted (6% of runes), in line with section 2.
Its three differences are fixed above: the containment spans are 6,003 and 9,005 runes, not 6,000 and 9,000 (windows
are cut on word boundaries); the true-rho rates span 0.048 to 0.057, not 0.051; and the single-chapter summary now gives
both the power-curve count (1 of 4) and the chapter 14 count (2 of 3). It also asked for "not detected" in place of
"excluded", with the power interval; done. The follow-up's 100 nulls were run on a 4,003-rune cut of window 3, not the
3,999-rune cut in the table (the shift scan around it covers the difference).
