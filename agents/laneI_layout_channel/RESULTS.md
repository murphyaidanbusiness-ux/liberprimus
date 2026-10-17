# RESULTS: laneI_layout_channel

Hypothesis: the LP2 layout (word lengths, sentence lengths, line breaks, chapter marks, first/last runes) is a cover channel carrying a message independent of the rune values.

Verdict: **no layout channel found.** No encoding in the tested families produces a decode that beats a shuffle null once multiplicity is counted, and no decode contains a readable fragment. The same pipeline recovers planted 60-letter messages in 56/56 planted runs (7 encodings x 8 seeds) at z = 8 to 23 against a null max of 7.8. Data pin: sha256 matched (12,956 runes, 2,896 words).

## 1. Data actually used

- Word lengths: 2,896 (mean 4.47, max 14). Sentence units: 175 (174 `.` marks plus the final unit). Lines: **594 in the unsolved pages** (the "604" figure includes solved pages 55-57). Pages: 55. Chapter groups (`&` only): 17.
- Self-Reliance came from `dl/dukotah/.../keys/self_reliance.txt` (10,195 words). The laneH directory does not exist, so there was no coordination. LP1 text is the 5 solved pages in `SOLVED-PAGES.json` (1,887 letters, no word boundaries), so LP1 book code is letter-level only.
- Resources are in `core.py`. They are the dukotah quadgram table (A-Z) and a dictionary of 2,100 five-letter words plus hashed 7-grams, built from Emma, KJV, Moby Dick, Paradise Lost, Alice, Chesterton, Walden, Meditations, Nature, Imitation, Frankenstein and Self-Reliance (frequency >= 4).

## 2. What was tested

22 channels. Each is an integer or bit sequence. Real is compared with **200 shuffles per channel**. Length channels shuffle the sequence. Rune-value channels shuffle the layout (a permutation of word, line, sentence or page lengths over the unchanged rune stream). Bit channels shuffle the underlying lengths.

Channels:
- W: word lengths.
- SW, SR: sentence lengths in words and in runes.
- LR, LWd, LF, LT: runes per line, words per line, runes before the first break, runes after the last break.
- PGr, PGw: runes and words per page.
- CHw, CHr: words and runes per chapter group. There are 17 groups, so every decode is under 30 letters. These are untestable and listed for completeness.
- Rune streams: FW/LWr (first/last rune of each word), FL/LLr (of each line), FS/LS (of each sentence), FP/LP (of each page).
- Bit streams: BW (word boundary after rune i), BL (line break), BS (sentence mark per word).

Encodings (code in `enc.py`; `channels.py` holds the channel definitions):
1. **Raw**: length -> letter (A=1.. with all 26 Caesar shifts and both signs) and length -> rune index (29 shifts, both signs, transliterated). Forward and reversed.
2. **mod-k digits**, k = 3..10, grouped g = 2..8 where 25 <= k^g <= 1100, big and little endian, every offset. Each value goes through the mod-26 and mod-29 maps (+/- sign, all shifts), plus ASCII (and +32 SIXBIT) when 64 <= N <= 256.
3. **Base-N pairs and triples** of consecutive lengths, N in {10,12,14,15,16,26,29}, every offset, same maps plus ASCII.
4. **Bit streams**: parity and `len > c` at all useful cut-offs, then 5-bit A1Z26, 5-bit Baudot/ITA2 (stateful LTRS/FIGS), 7-bit ASCII and 8-bit ASCII. Every offset, MSB/LSB order, bit inversion, and forward or reversed direction. After the planted control exposed a flaw in the stateful Baudot decoder, a stateless Baudot family ("sl") was added for every channel.
5. **Morse**: three-class thresholds (t1, t2), four dot/dash/gap role assignments, both directions.
6. **Rune-value streams** (item 4): value and mod-29 increment, +/- 29 shifts, atbash, forward and reversed, parity and (>=14) bits, mod 3/4/5 digit groups.
7. **Book code** (SW, SR, LR, CHw, CHr): number -> letter or first/last letter of word n in Self-Reliance and LP1. Offsets -1..+2, mod and clip, cumulative pointer, pair (a+b, a*b, word a letter b).

Totals: 221,645 non-book cells, plus 6 x 42 book-code cells.

Scoring: for each cell, the decoded letter stream gets Qall (mean quadgram log10), Qwin (best 60-letter window), IoC, and dictionary-word hits (Hall/Hwin). Each cell's z is taken against its own 200 nulls. The family-wise statistic is the real maximum z over cells compared with the distribution of the same maximum over the 200 null replicates, so p = (1 + #{null max >= real max}) / 201. The minimum possible p is 0.005. Cells with fewer than 30 decoded letters (100 for IoC) are dropped, because degenerate tiny decodes produced fake z of about 14 in a first pass. ASCII cells also carry printable-fraction values in `out_*.pkl` (`prs`).

## 3. Planted-message control (`plant.py`, `plant_bk.py`, `plant_results.json`, `plant.log`)

A 60-letter message ("ALLTHINGSMUSTPASSTHETRUTHISHIDDENINPLAINSIGHTSEEKANDYEWILLFINDIT") was hidden at a random place in a synthetic 2,896-word layout. The layout was drawn i.i.d. from the real W marginal, and filler lengths were chosen to satisfy the parity or class of each hidden symbol. The full pipeline, including all ~20k cells and the filter, was run against the real W null.

| plant | seeds recovered at top cell | Qwin z of planted cell (min / median) | null max over 200 shuffles (max / p95) |
|---|---|---|---|
| length -> letter (1=A, via Caesar +25) | 8/8 | 19.9 / 19.9 | 7.8 / 6.3 |
| parity bits -> 5-bit Baudot (stateless family) | 8/8 | 17.3 / 17.6 | 7.8 / 6.3 |
| parity bits -> 7-bit ASCII, LSB first, offset 3 | 8/8 | 16.3 / 16.9 | 7.8 / 6.3 |
| (len > 4) bits -> 8-bit ASCII | 8/8 | 14.7 / 16.3 | 7.8 / 6.3 |
| base-15 pairs, mod 26 | 8/8 | 23.1 / 23.1 | 7.8 / 6.3 |
| mod-3 trits, 3 per letter | 8/8 | 17.1 / 17.1 | 7.8 / 6.3 |
| Morse (dot <=3, dash 4-6, gap >=7) | 8/8 | 8.2 / 8.3 | 7.8 / 6.3 |
| book code SW -> Self-Reliance letter index | 5/5 | 8.9 | 4.6 / 3.2 |
| book code SW -> LP1 letter index | 5/5 | 10.0 | 4.6 / 3.2 |

- Decoded plant, length -> letter: `ALLTHINGSMUSTPASSTHETRUTHISHIDDENINPLAINSIGHTSEEKANDYEWILLFI...`. The parity-Baudot plant gives the same text, surrounded by junk letters such as `LCJOGPLXOVVNLNKORVPO`.
- The first Baudot run lost the message in 4 of 5 seeds. A FIGS code (27) in the preceding random bits switched the stateful decoder off. This is why the stateless family exists.
- Morse is the weakest recovery, and the 60-letter window barely clears the null max (8.2 vs 7.8). A hidden Morse message shorter than about 60 letters would not be detected. Messages in all other families are detected well below 60 letters.
- Power limit: all window statistics assume a contiguous stretch of about 20 or more decoded letters. A keyed or arbitrary-substitution alphabet (beyond Caesar/atbash shifts) is not covered.

## 4. Encodings x channels (best Qwin z / family p, 200 nulls per cell family)

p is the empirical probability that the null max over that same family of cells reaches the real max (floor 0.005). "bits->A1Z26/Baudot*" is stateful Baudot plus A1Z26; "bits->Baudot(sl)" is stateless. "-" means the family does not apply or has too few letters.

| channel | raw len->letter/rune | mod-k grouped | base-N pairs/triples | bits->ASCII | bits->A1Z26/Baudot* | bits->Baudot(sl) | Morse | rune value | rune increments | book code SR | book code LP1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W | 3.3 / 0.637 | 4.8 / 0.736 | 5.4 / 0.119 | 3.6 / 0.517 | 3.4 / 0.811 | 2.8 / 0.920 | 4.3 / 0.010 | - | - | - | - |
| SW | 3.0 / 0.587 | 5.3 / 0.114 | 4.6 / 0.214 | - | -0.2 / 0.652 | - | 2.6 / 0.274 | - | - | 1.4 / 0.836 | 1.6 / 0.423 |
| SR | 2.3 / 0.980 | 5.8 / 0.010 | 4.0 / 0.627 | - | 0.5 / 0.617 | - | 1.3 / 0.995 | - | - | 1.6 / 0.786 | 0.9 / 0.915 |
| LR | 3.2 / 0.547 | 6.0 / 0.015 | 4.2 / 0.622 | 3.1 / 0.418 | 2.8 / 0.881 | 4.1 / 0.090 | 2.7 / 0.224 | - | - | 1.6 / 0.761 | 1.7 / 0.473 |
| LWd | 3.4 / 0.383 | 4.5 / 0.667 | 4.0 / 0.761 | 3.0 / 0.423 | 4.9 / 0.104 | 5.5 / 0.015 | 4.0 / 0.005 | - | - | - | - |
| LF | 3.9 / 0.209 | 5.6 / 0.040 | 4.7 / 0.229 | 2.3 / 0.886 | 3.9 / 0.453 | 3.5 / 0.433 | 2.8 / 0.363 | - | - | - | - |
| LT | 2.8 / 0.741 | 5.2 / 0.109 | 4.3 / 0.557 | 4.0 / 0.109 | 2.9 / 0.930 | 3.6 / 0.448 | 2.5 / 0.483 | - | - | - | - |
| PGr | 2.6 / 0.731 | 3.2 / 0.856 | 3.2 / 0.741 | - | - | - | - | - | - | - | - |
| PGw | 3.2 / 0.284 | 3.0 / 0.940 | 3.5 / 0.428 | - | - | - | - | - | - | - | - |
| FW | - | 4.6 / 0.393 | - | 4.6 / 0.025 | 2.7 / 0.667 | 2.5 / 0.667 | - | 3.4 / 0.562 | 3.4 / 0.552 | - | - |
| LWr | - | 3.9 / 0.960 | - | 2.7 / 0.846 | 3.4 / 0.289 | 3.0 / 0.368 | - | 3.1 / 0.751 | 4.4 / 0.114 | - | - |
| FL | - | 4.6 / 0.144 | - | 3.9 / 0.134 | 3.0 / 0.562 | 1.5 / 1.000 | - | 4.2 / 0.104 | 4.6 / 0.035 | - | - |
| LLr | - | 4.3 / 0.463 | - | 2.9 / 0.552 | 3.2 / 0.463 | 2.4 / 0.642 | - | 3.2 / 0.537 | 3.0 / 0.647 | - | - |
| FS | - | 4.4 / 0.294 | - | - | - | - | - | 3.0 / 0.527 | 6.8 / 0.005 | - | - |
| LS | - | 5.0 / 0.055 | - | - | - | - | - | 3.6 / 0.189 | 2.9 / 0.592 | - | - |
| FP | - | 3.0 / 0.418 | - | - | - | - | - | 3.5 / 0.184 | 3.1 / 0.512 | - | - |
| LP | - | 3.0 / 0.448 | - | - | - | - | - | 3.4 / 0.184 | 2.7 / 0.761 | - | - |
| BW | - | - | - | 2.5 / 0.766 | 3.5 / 0.224 | 2.1 / 0.701 | - | - | - | - | - |
| BL | - | - | - | 1.2 / 0.896 | 2.9 / 0.159 | 1.1 / 0.856 | - | - | - | - | - |
| BS | - | - | - | 2.5 / 0.184 | 3.6 / 0.129 | 1.7 / 0.811 | - | - | - | - | - |

Counts of independent tests: the table has 102 filled cells, and about 5 would be expected below 0.05 by chance. Observed below 0.05: W-Morse 0.010, SR-mod 0.010, LR-mod 0.015, LF-mod 0.040, LWd-Morse 0.005, LWd-Baudot(sl) 0.015, FW-ASCII 0.025, FL-incr 0.035, FS-incr 0.005. These are 9 against 5 expected, and many are strongly correlated (same decode, Qall/Qwin).

## 5. The nominal hits, examined

- **FS (first rune of each sentence), increments, A26 +15**: Qwin z 6.8, p = 0.005 in the family test. Cell-specific p = 0.0003 on 3,000 fresh shuffles, but that cell was picked from 4,140 cells in 8 channels. Source of the excess: the 174 increments have a skewed value distribution (IoC29 = 1.118, z = +2.7). Even with the order shuffled the quadgram score stays high (z 4.4). The text is `FNOPFPQQBNQRNNZRRSBRAISHVAYCUSALLPRQ...`, with no dictionary word. Chance.
- **SR (sentence runes) mod-4 groups of 5, A26 +0** (p = 0.010): 35 letters, `PODOFUSAZWFRENEYNZJUDHEYTHSYISOFCLL`. Short-string chance; no 5+ letter word.
- **W-Morse (p = 0.010) and LWd-Morse (p = 0.005)**: the decodes are strings of E, I, S, H, T (`EIUIATSHIEIESSRIEEISBIIN...`, IoC 6.8). They score on letter-frequency skew, not on words. Zero five-letter dictionary words.
- **LWd gt6 -> Baudot(sl)** (p = 0.015): about 118 letters with a score of -8.55, which is near the random floor. Not meaningful.
- **Dictionary words overall**: positions that begin a 5-letter or hashed 7-letter dictionary word, summed over all 221,645 cells with >= 30 letters, are 57,240 real against 57,287 +/- 232 for the null (z = -0.2). No channel has more word-hit cells than null (table in `analyze_all.txt`).
- **Raw IoC of first/last rune streams** (`rune_ioc.json`, 300 layout shuffles): FW 0.998 (z -0.7), LWr 1.002 (z +0.8), LLr 0.998, FS 1.044 (z +1.2), LS 0.998, FP, LP null. The best quadgram over 58 rune maps is within 2.4 sd of null everywhere. The one exception is FL, covered next.

## 6. Line structure (item 3; `lines.py`, `lines2.py`, `fl_check.py`, `lines_out.json`)

- Runes per line: mean 21.8, sd 2.6 (range 3-26). Dropping page-final and short lines (532 of 594 kept): mean 22.1, sd 1.7, range 16-26. **Lines do not hold a fixed rune count.**
- Glyph-width model: fit total width = sum of w_rune x count + w_dash x dashes + w_dot x dots = const (31 parameters). The residual sd is 0.0505 against 0.0721 +/- 0.0005 for the same fit with runes shuffled across lines (z = -43). The fitted widths are plausible and span a 4.6x range: EA 1.79, X 1.39, M 1.31, U 1.25 at the wide end, I 0.38, A 0.68, R 0.73 at the narrow end. The `-` separator costs about 0.25 of a rune and the `.` about 1.04. So the breaks are largely a typographic fill of variable-width glyphs. About half of the line-length variance is explained, and the remainder is not shown to be free choice or noise.
- **First rune of each line** has IoC 1.090 (z = +7.0, chi2 81 on 28 df). This is explained: with widths fitted *excluding* first runes, the enrichment of each rune as line-first correlates with its width at r = 0.70 (null 0.00 +/- 0.20, z = 3.6), and chi2 drops from 78.7 to 40.9. Greedy filling sends wide glyphs to the next line. It is not an acrostic.
- Break position vs rune: chi2 24.1 on 28 df (independent). Mid-word fraction 70.8%.
- Line-length autocorrelation is weakly positive (lag 1 z = +4.7, lag 2 +3.0, lag 3 +3.2; kept lines +3.8/+2.2/+2.8). It is unexplained but small (r about 0.19) and is not message-like. The runes-per-line, words-per-line, runes-before-first-break and runes-after-last-break symbol streams (LR, LWd, LF, LT) decode to null in every family above.

## 7. Verdict by item

1. **Word lengths** (W, 20,385 cells): null in every encoding. Best Qwin z 5.4, p = 0.12 (base-N). The parity/threshold bit decodes, Morse, mod-k and pair/triple families are null. The Morse hit is E/I-run frequency skew.
2. **Sentence lengths and chapter marks** (SW, SR, CHw, CHr): null. Book code into Self-Reliance (word, letter, cumulative, pair) and into LP1 letters gives p >= 0.4. Chapter groups only have 17 values, so they are untestable beyond a handful of letters.
3. **Line structure**: null. Breaks follow a variable-glyph-width fill, with no residual channel detectable.
4. **First/last runes** (words, lines, sentences, pages): null. The FL IoC anomaly is the typographic width effect.

## 8. What this does not cover

- Messages shorter than about 20 decoded letters, or a Morse message shorter than about 60 letters.
- Keyed or substitution alphabets beyond Caesar/atbash, and a layout stream used as a *key* for the runes (not a plaintext carrier).
- LP1 book code at word level, other books, and the Hall/Hwin dictionary statistic as the primary selector (it is a sparse rare-event count and was used only as a cross-check).
- Cover-channel schemes that code lengths with a pmf-aware (arithmetic/Huffman) coder. Scout lead 5 is only partly addressed: the parity, threshold and base-N bit routes are tested, and the pmf coder is not.

## Files

Code: `core.py`, `enc.py`, `channels.py`, `run.py`, `run_bdt.py`, `booksc.py`, `plant.py`, `plant_bk.py`, `lines.py`, `lines2.py`, `fl_check.py`, `rune_ioc.py`, `analyze.py`, `table.py`.
Raw results: `out_*.pkl`, `summary.json`, `family_table.json`, `analyze_all.txt`, `plant_results.json`, `plant_bk.json`, `lines_out.json`, `rune_ioc.json`.
