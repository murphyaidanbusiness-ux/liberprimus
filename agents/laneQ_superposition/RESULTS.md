# Lane Q (round two): all-shift keystream-reuse scan on LP2

Question: was any stretch of LP2 (pages 0-54, 12,956 runes) enciphered with a keystream that is also used elsewhere in LP2 at some relative shift (two-time pad)?

## Verdict

- No key reuse is detected at any unit type or stream (raw and increment D). Every real maximum lies inside its 200-null distribution (empirical p from 0.07 to 0.84).
- The scan has no power for the reuse the question is about. Page pairs overlap at most 277 runes, and at the null threshold a planted reuse of 277 runes is detected with probability 0.0000. Nothing is excluded at page-pair level or chapter-pair level.
- The only excluded range is whole-stream lag reuse: a single-lag reuse of at least about 3,200 to 4,700 runes (depending on the lag overlap and stream) is excluded at 90% power.
- Calibration issue: the normal z-statistic is badly miscalibrated for overlaps below about 250 (heavy tail; section 6). The null maximum is therefore set by short-overlap cells, which is the main reason page-length reuse is undetectable.

## 1. What is new versus the community

- dukotah armada, FOLLOWUP-TESTS.md section 4 (`dl/dukotah/liber-primus/analysis/armada/FOLLOWUP-TESTS.md`): tested aligned page pairs only (shift 0, 1,485 pairs), using IoC of differences. Top value IoC*N 1.292 (pages 29 and 54, n=76), dismissed as small-sample. No shift scan, no increment stream, no planted power.
- Leo, `dl/leo/tests5.py` and `dl/leo/docs/FINDINGS.md` fact 3 and line 91: section pairs and self-shifts with IoC of differences (max z 3.3) and kappa (z < 4.6). No page-level scan, no D stream, no unit-length power curve.
- Campaign XIV P1 (`dl/dukotah/liber-primus/analysis/campaign14/probes.py`, ledger row "Corpus-wide periodicity / key reuse"): raw-stream kappa for lags 1 to 6478, fixed expectation 1/29, 5-sigma threshold. Our raw-stream lag check reproduces it (max z 4.184 at lag 6002, no lag above 5).
- New here: (a) all unit pairs (55 pages, 17 chapter runs) at all shifts with overlap >= 60, and all self-lags of the whole stream (lags 1 to 12,896), on raw runes and on increments D; (b) a null that keeps the doublet deficit (within-page permutation of runes, or of increments with rebuild); (c) planted power curves by overlap length, for three cipher kinds including the chain model and skip-on-repeat; (d) a per-overlap-bin diagnostic showing the normal z is not calibrated at short overlaps.

## 2. Method

- Units: pages (55, lengths 66 to 277); chapters (17 contiguous runs of equal per-rune `chap`, lengths 9 to 2,474; 12 of 17 cross a page boundary); whole stream (12,956 runes, self-lags).
- Streams: raw runes; D = increments within each unit (c_i - c_{i-1} mod 29, first rune dropped).
- For an ordered pair (a, b) and shift t: M(t) = #{i: a_i = b_{i+t}}, n(t) = min(La, Lb - t) - max(0, -t) (>= 60), p0 = sum_c f^a_c f^b_c (empirical cross-marginals; self cells use sum_c f_c^2), z = (M - n p0)/sqrt(n p0 (1 - p0)).
- Computation: 29 one-hot indicator vectors per unit, rFFT, cross-spectrum summed over symbols, one inverse FFT per pair. Verified against direct computation on 300 random cells plus the argmax cell for each of the six (unit, stream) combinations: max |dM| = 0, max |dz| = 0 (`out/controls_log.txt`).
- Cells scanned: pages raw 532,565 / D 529,540; chapters raw 180,600 / D 180,375; stream raw 12,896 / D 12,895.
- Null: 200 shuffled corpora per (unit, stream), each through the identical pipeline. Raw: permute the runes within each page. D: permute the increments within each page and rebuild the runes from the page's first rune. Chapter and stream units are cut from the shuffled flat stream at the real chapter boundaries.
- Diagnostics: per-overlap-bin max z and count z > 4 (bins [60,100), [100,150), [150,250), [250,500), [500,1000), [1000,inf)); exact binomial tail of each reported cell (-log10 p under p0); longest run of consecutive matches.

## 3. Positive controls and power curve

Plaintext: English passages from Python's own documentation prose (`pydoc_data.topics`, 188,085 runes after `eng2runes` from `agents/laneN_cribdrag/common.py`). Deviation from the brief: the SOLVED-PAGES transliterations total 1,796 runes (five pages), too short for two disjoint 2,000-rune passages. Monogram IoC of the plaintext 1.836 (random 1.0). Plaintext coincidence rate q = 0.0633 (rune equal) and 0.0637 (mod 28), against 1/29 = 0.0345.

Plant: passages P1 and P2 (disjoint segments), one keystream K. Unit u uses K from offset 0, unit v uses K from offset s, s uniform in [1, L-60], so overlap n = L - s. Kinds: `add` c = p + k mod 29; `chain` c_i = c_{i-1} + 1 + ((p_i + k_i) mod 28) mod 29; `skip` additive with skip-on-repeat. Each plant is placed in a background of page-shuffled real runes cut into L-blocks (51, 25, 12, 6 blocks for L = 250, 500, 1000, 2000). 20 plants per cell. Threshold T = max over 200 null backgrounds of the global max z. Detection = planted cell z > T (`det_cell`).

Analytic expectation for a planted cell: E[z] = sqrt(n) * c, with c_raw = (q - 1/29)/sqrt((1/29)(28/29)) = 0.1580 and c_D = 0.1509 (for chain). Planted means match this (e.g. L=2000 raw add, mean overlap about 950: predicted 4.9, observed 4.66).

| L (runes) | stream | kind | planted z mean | detect (cell > T) | T (block null max) |
|---|---|---|---|---|---|
| 250 | raw | add | 2.17 | 0/20 | 7.44 |
| 250 | raw | chain | 0.01 | 0/20 | 7.44 |
| 250 | raw | skip | 0.22 | 0/20 | 7.44 |
| 250 | D | add | 0.70 | 0/20 | 7.89 |
| 250 | D | chain | 2.09 | 0/20 | 7.89 |
| 250 | D | skip | -0.18 | 0/20 | 7.89 |
| 500 | raw | add | 2.67 | 0/20 | 7.13 |
| 500 | D | chain | 2.91 | 0/20 | 7.66 |
| 1000 | raw | add | 3.50 | 0/20 | 6.70 |
| 1000 | D | chain | 3.01 | 0/20 | 6.49 |
| 2000 | raw | add | 4.66 | 4/20 | 6.09 |
| 2000 | D | chain | 4.47 | 1/20 | 6.59 |

The other kind/stream combinations (chain on raw, add on D, skip everywhere) are not detected at any L (z means between -0.35 and 0.91; full table in `out/controls.json`).

Whole-stream plants (two planted segments of length L in the 12,956-rune stream, self-lag scan): 0/20 detected for every L in {250, 500, 1000, 2000}, stream and kind. Planted lag z means range from -0.32 to 1.99 across all L, streams and kinds (largest at L=2000, raw add), against null maxima over lags of 5.0 to 6.1. Expected: local reuse is diluted by about sqrt(N/n) in the whole-stream lag scan.

Real page lengths (two real pages of 66 to 277 runes replaced by planted units of their own lengths, 20 plants per kind and stream, threshold 8.6 raw / 8.2 D): 0/20 detected for all six kind/stream combinations (planted z means 0.21 to 1.62).

Answer to the brief's question: page-length reuse (overlap about 60 to 277) is undetectable at this sample size by this scan. At L=2000 only the raw additive kind is detected at 20%.

## 4. Null

Real-run nulls (200 per unit and stream, `out/real.json`):

| unit | stream | null max z mean | sd | max of 200 (= T) | null n(z>4) mean | sd |
|---|---|---|---|---|---|---|
| pages | raw | 6.162 | 0.412 | 7.526 | 230.0 | 15.1 |
| pages | D | 6.119 | 0.407 | 7.874 | 220.6 | 14.8 |
| chapters | raw | 5.557 | 0.430 | 7.348 | 48.1 | 7.3 |
| chapters | D | 5.595 | 0.436 | 7.653 | 45.7 | 7.5 |
| stream | raw | 4.068 | 0.318 | 4.904 | 0.71 | 0.81 |
| stream | D | 4.113 | 0.346 | 5.182 | 0.84 | 0.96 |

Overlap-bin diagnostic (pages raw null): null n(z>4) per bin: [60,100) 87.7, [100,150) 65.7, [150,250) 71.0, [250,500) 5.6; a normal tail would give about 3 to 5 per bin. The short-overlap tail is the dominant source of the null maximum.

## 5. Real results

| unit | stream | real max z | null mean +- sd | z vs null | empirical p (max) | real n(z>4) | null n(z>4) | empirical p (n4) |
|---|---|---|---|---|---|---|---|---|
| pages | raw | 6.861 | 6.162 +- 0.412 | +1.70 | 0.065 | 253 | 230.0 +- 15.1 | 0.070 |
| pages | D | 6.058 | 6.119 +- 0.407 | -0.15 | 0.527 | 208 | 220.6 +- 14.8 | 0.816 |
| chapters | raw | 5.156 | 5.557 +- 0.430 | -0.93 | 0.811 | 54 | 48.1 +- 7.3 | 0.239 |
| chapters | D | 5.335 | 5.595 +- 0.436 | -0.60 | 0.711 | 42 | 45.7 +- 7.5 | 0.706 |
| stream | raw | 4.184 | 4.068 +- 0.318 | +0.36 | 0.323 | 1 | 0.71 +- 0.81 | 0.517 |
| stream | D | 3.803 | 4.113 +- 0.346 | -0.90 | 0.836 | 0 | 0.84 +- 0.96 | 1.000 |

Stream lags 1 to 6478 (the campaign XIV range): raw max z 4.184 (n(z>4) = 1); D max z 3.615 (n(z>4) = 0).

Top cells (full top 20 in `out/real.json`). Format: units, shift t, overlap n, matches M, z, -log10 exact binomial p, longest run of consecutive matches.

- Pages raw: p10 vs p14, t=60, n=77, M=14, z=6.861, -log10 p=6.21, run 2. p37 vs p43, t=153, n=121, M=16, z=6.049, -log10 p=5.51, run 2. p08 vs p13, t=212, n=60, M=10, z=5.685, run 2. p07 vs p39, t=-127, n=81, M=12, z=5.512, run 2.
- Pages D: p12 vs p44, t=-59, n=201, M=23, z=6.058, -log10 p=6.02, run 2. p10 vs p21, t=80, n=192, M=22, z=5.902, run 2. p29 vs p53, t=-198, n=78, M=12, z=5.848, run 1.
- Chapters raw: chap03 vs chap10, t=-172, n=91, M=12, z=5.156, run 2. chap07 vs chap10, t=-1701, n=91, M=12, z=5.147.
- Chapters D: chap05 vs chap13, t=-345, n=120, M=15, z=5.335, run 1. chap05 vs chap08, t=788, n=232, M=22, z=4.922, run 4.
- Stream raw: lag 6002, n=6954, M=304, z=4.184, -log10 p=4.50, run 4. Stream D: lag 7550, n=5405, M=243, z=3.803, run 3.

The most extreme real cell (pages raw, p10/p14, t=60) lies in the most heavy-tailed bin ([60,100): real bin max 6.861 vs null 5.965 +- 0.436, empirical p 0.050). Its matches are scattered (longest run 2), so it is not a copied passage. After the global maximum over all cells it is not significant (empirical p 0.065). Every other top cell has longest run at most 4, consistent with scattered coincidences.

## 6. Verdict per unit type and stream

Exclusion thresholds use the real-run null maxima (T) and the normal model with unit sd, so power(n) = Phi(c sqrt(n) - T); 90% power requires n90 = ((T + 1.2816)/c)^2.

- Pages, raw: no reuse detected (emp p 0.065). Not excluded for any overlap: n90 = 3,108, but page overlap is at most 277 (power at 277 = 0.0000; at 60 = 0.0000). Page-pair reuse is undetectable and unexcluded.
- Pages, D: no reuse detected (emp p 0.527). n90 = 3,679; not excluded for any overlap at most 277.
- Chapters, raw: no reuse detected (emp p 0.811). n90 = 2,984; the largest achievable chapter-pair overlap is 1,894 (second-longest chapter), power 0.32. Not excluded.
- Chapters, D: no reuse detected (emp p 0.711). n90 = 3,503; power at 1,894 = 0.14. Not excluded.
- Whole stream, raw: no lag reuse detected (emp p 0.323). Single-lag reuse of m runes is excluded at 90% power when m >= m90: 3,157 runes (lag overlap 6,500) to 4,289 runes (lag overlap 12,000). Full-lag reuse (m = n) is trivially excluded (z about 16).
- Whole stream, D: no lag reuse detected (emp p 0.836). m90 = 3,452 (overlap 6,500) to 4,691 (overlap 12,000).

Stated plainly: a shift scan of LP2 with this statistic excludes only single-lag reuse of about 3,200 to 4,700 runes or more. Shorter reuse, including reuse between any two pages or any two chapters, is not excluded. The verdict is "no reuse detected" for every unit type and stream, and "not excluded" for page-length and chapter-length reuse.

## 7. Caveats

- The brief's z is normal-approximated. Per-bin diagnostics show it is miscalibrated below overlap about 250 (about 20x heavier tail at z > 4). Thresholds therefore come from the nulls (protocol), not from the normal tail. The null maximum of the global max is itself heavy-tailed: across control seeds the 200-sample stream maxima ranged 5.0 to 6.1, while the real-run nulls gave 4.9 and 5.2.
- Planted plaintext is Python documentation prose, not Liber Primus solved text (deviation, see section 3).
- No chapter-level planted control was run (17 units, 15 usable).
- Skip-on-repeat breaks alignment after the first skip, so its low detection is partly by design.
- The whole-stream lag scan is diluted for local reuse by roughly sqrt(N/n).
- Campaign XIV's kappa used a fixed expectation of 1/29 over lags 1 to 6478 on raw runes. Our z uses cross-marginals and includes D and lags up to 12,896; the two agree on raw lags 1 to 6478 (no peak above 5).

## Files

- `agents/laneQ_superposition/shiftscan.py`: FFT scan, brute-force check, null constructions, ciphers, English source (`scan`, `cell_brute`, `cell_detail`, `null_pages`, `enc_additive`, `enc_chain`, `enc_skip`, `english_runes`).
- `agents/laneQ_superposition/run_controls.py`: planted controls and power curves (sections 0 to 4). Output `out/controls.json`, log `out/controls_log.txt`.
- `agents/laneQ_superposition/run_real.py`: real scan and 200 nulls. Output `out/real.json`, log `out/real_log.txt`.
