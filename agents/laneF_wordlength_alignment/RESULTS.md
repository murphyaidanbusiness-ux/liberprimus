# RESULTS: laneF_wordlength_alignment

Hypothesis tested: the unsolved plaintext is a known published text, possibly with short function words merged into a neighbour or dropped, or with a different digraph convention. If so, its word-length sequence should align with a window of that text.

Data pin: sha256 matched. Target: 2,896 word lengths (in runes), in book order, max length 14. Sections are Leo's 9 page ranges (0-2, 3-7, 8-14, 15-22, 23-26, 27-32, 33-39, 40-53, 54), with 158/255/383/437/224/326/378/719/16 words. Section s8 (16 words) is too short to carry signal and is reported but not used in sums. All code and raw outputs are in this directory.

## Verdict in plain words

1. **No known-text alignment.** 149 texts (15.7M words) were tested under 42 transliteration and function-word models, with exhaustive Smith-Waterman alignment (no seeding shortcut) and a k-mer index. No section aligns with any text beyond the shuffled-target null. On the same pipeline, a planted 300-word passage is found at the exact offset with z = 344-354. Even under a deliberately wrong model (planted with THE/OF merged, searched with THE/OF dropped, merged into the preceding word, left unmodified, or spelled letter by letter), detection holds at z = 12-200. The library is therefore excluded as the plaintext source under every model tried, including texts the earlier campaigns did not cover (Walden, Meditations, Imitation of Christ, Golden Bough, Leviathan, Siddhartha, Ulysses, Shakespeare and about 30 others fetched here).
2. **The one cell above its own null is a chance island.** Model base_mP2 in section s6 aligns 18 cipher words (1979-1996) with the Imitation of Christ: "HE LOVETH FOR HIS BELOVED FOR JESUS WILL BE LOVED ALONE ABOVE ALL THINGS+THE LOVE+OF CREATED THINGS IS". It scores 15 against 215 shuffles (mean 11.6, max 14). The 15 words on either side do not align, whereas a true source aligns across the whole section; even mismatched plants score 68-437. Pooled over 10,320 shuffle maxima, the per-cell tail probability is about 0.001-0.003, and 378 (variant, section) cells were tested. In the family-wise replicate test the real maximum ranks 2nd of 24 by z (p ≈ 0.08) and 9th of 24 by score excess. Its implied chain key has IoC 1.13 over 63 runes, which looks random. Verdict: chance.
3. **New finding, and the likely reason any alignment approach fails: the ORDER of the unsolved word lengths has no English serial structure.**
   - Model-free test (bigram independence chi-square on the 7x7 length table, permutation null):
     - unsolved book, z = -0.06 (p = 0.49);
     - Cicada's own solved LP1 pages, measured on their true rune word lengths (695 words), z = +4.0 (p = 0.0015).
   - Markov-1 log-likelihood gain over the unigram model, against 1,000 permutations:
     - unsolved book, z = -0.6 to -1.7 under all 9 English models;
     - held-out English windows of the same size (40 windows), z = +6.7 to +8.8 (sd 1.4-1.8; minimum 2.0-4.8);
     - LP1 solved pages, z = +3.1 to +4.3, which matches held-out English windows of the same size (+3.6 to +4.4).
   - Random +1-rune insertions (F-interrupter-like, 3.5-7% of runes) barely weaken the English signal (z ≥ 3.3).

   So the unsolved word lengths look like a random permutation of an English-like length distribution. English prose with THE/OF removed is excluded at about 5 sd (unsolved -1.0 against +6.7 ± 1.4 for held-out drop-THE/OF/TO English).

   This also re-reads Lane E's bigram evidence: the 2.2% adjacent 2-2 rate is exactly the independence value (0.155² = 2.4%), so it does not specifically support "THE/OF absent". Lane E's "sentence marks placed independently of word length" fits the same picture. Plausible readings:
   - the word separators are not the plaintext word boundaries in plaintext order (word-level transposition, or a separator layout drawn independently);
   - the plaintext is not running prose (a word list or salad);
   - the separators are themselves keyed.

   Under any of these readings, word-length cribs and known-text skeleton matching cannot work.

## Prior work (ledger check)

dukotah ELIMINATION-LEDGER "SKELETON" and Round 10 L4-skeleton tested contiguous exact or ±1-slack matching of the whole sequence and of 120/400-word windows against 224 texts / 22.6M words. Both were null; there was no merge, drop or digraph model and no gapped alignment. Campaign XVIII tested per-page longest exact runs against 11 texts. Several of those texts are not on disk (Gutenberg is proxy-blocked), so this lane cannot re-cover their corpus. New in this lane: function-word merge/drop models, digraph variants, gapped local alignment per section, k-mer diagonal statistics with 200 shuffles, an in-run positive control in every run, and the serial-structure test (finding 3).

## 1. Library (build_lib.py, build_lib.log)

149 texts and 15,736,008 words (149,391 types) after content-hash de-duplication. Some duplicates survive because their headers differ: Moby Dick ×2-3, KJV ×2, Mabinogion and Agrippa ×2.

| source | count |
|---|---|
| dukotah data/keys (Self-Reliance, solved LP plaintext, rune poem) and armada18/armada19 | 97 files: occult, philosophy, scripture, myth, fiction, Cicada 2012-13 puzzle texts, koans, LP1 forward/reversed |
| analysis/bookcipher/books (Agrippa, Blake, KJV, Mabinogion, Milton) | 5 |
| armada20 (Gospel of Thomas, Marriage of Heaven and Hell) | 2 |
| NLTK Gutenberg sample (lane E cache; bryant, burgess and edgeworth held out) | 15 |
| fetched via raw.githubusercontent.com/GITenberg | 37 |

The 37 fetched texts are: Walden, Meditations (Aurelius), Marriage of Heaven and Hell, Leaves of Grass, Siddhartha, Nature, Art of War, The Prince, Beyond Good and Evil, Apology, Phaedo, Consolation of Philosophy, Spinoza's Ethics, Enchiridion, Leviathan, Locke, Golden Bough, Hume's Enquiry, Imitation of Christ, Shakespeare (complete), Ulysses, Through the Looking-Glass, Rime of the Ancient Mariner, Bacon's Essays, Anthem, Frankenstein, Egyptian Book of the Dead, Carlyle's Heroes, Emerson's Conduct of Life, Thoreau's A Week, Walking, Orthodoxy, Paradise Lost, Republic, Symposium, Timaeus and Nietzsche's Dawn of Day.

Fetch failures (GITenberg name guesses that returned 404; about 8 minutes spent): Zarathustra, Kybalion, Dhammapada, Songs of Innocence, Confessions, Varieties of Religious Experience, Montaigne, Koran, Book of Mormon, Origin of Species, Gulliver, Apocrypha, Divine Comedy, Pilgrim's Progress (already in the library), Gibran's Prophet and Madman, Book of Enoch, Yoga Sutras, Sartor Resartus, Representative Men. Gutenberg, archive.org and the pglaf mirrors are unreachable. Gödel, Escher, Bach and the Book of Thoth are not openly available. The 224-text L4 corpus is not on disk.

Held-out English, used only as a null: three NLTK children's texts (230k words) plus the UD English Web Treebank (176k words).

Transliteration (core.rlen): K→C, V→U, Q→C, Z→S; greedy ING→one rune, then TH NG EA EO OE AE IA, IO→IA. Non-letters are dropped, words split at whitespace, hyphens and punctuation, apostrophes removed, lengths clipped at 15.

**42 variants (core.variant_list):**
- **Digraph variants (11):**
  - base;
  - ing2 (ING = I+NG);
  - one variant per digraph dropped: noTH, noNG, noEA, noEO, noOE, noAE, noIA;
  - letters (no digraphs);
  - THonly.
- **Function-word models on base (27):** each stop set below is (a) merged with the FOLLOWING word (mF), (b) merged with the PRECEDING word (mP), or (c) dropped. Stop sets are the first 1, 2, 3, 4, 6, 9, 13, 20 and 26 of THE, OF, TO, A, AN, AND, IN, IS, IT, OR, BE, AS, AT, BY, HE, WE, SO, NO, ON, IF, MY, UP, DO, ME, US, I. Runs of stop words chain into one merged word.
- **Letter-by-letter and TH-only with THE/OF dropped or merged-following (4).**

## 2. Positive control (task item 4; posctrl.py, posctrl.log)

300 consecutive words of a library text, Cicada-transliterated, with THE/OF merged into the following word, then searched against the whole library.

| source | searched in variant | found text | SW score | 2nd-best text | shuffle max (31) | z | alignment start vs true start |
|---|---|---|---|---|---|---|---|
| Emerson Essays II | base_mF2 (correct model) | correct | 300 | 11 | 13 | 344 | 32207 = 32207 |
| | base_drop2 | correct | 187 | 11 | 13 | 197 | +1 |
| | base_mP2 | correct | 130 | 10 | 13 | 141 | +21 |
| | base (unmodified) | correct | 117 | 11 | 14 | 118 | (different stream) |
| | letters | correct | 38 | 11 | 16 | 24 | |
| Agrippa III | base_mF2 | correct | 300 | 10 | 13 | 354 | 25036 = 25036 |
| | base_drop2 / mP2 / base / letters | correct | 158 / 95 / 69 / 20 | 10 / 10 / 10 / 11 | 13 / 12 / 13 / 13 | 202 / 119 / 95 / 12 | exact, exact, ... |

The k-mer index on the same plants:
- diagonal-band hits: 293-296 against a null maximum of 6-31 (z 76-411), and the band identifies the correct text;
- longest exact run: 300 against a null maximum of 12-13 (z ≈ 400-430);
- total hit count alone: z only 0.4-4.6, so it is a weak statistic and is reported only for completeness.

In-run controls: every SW run carries 4 planted lanes of section length (mF2 / drop2 / unmodified / mF2 + 15% random length noise) from a rotating library source. The exact mF2 plant was found in the correct text, above the shuffle maximum, in all 8 sections for 38 of the 42 variants. The exceptions are variants that merge or drop far more words than the plant: mP13 (7 of 8), mP20 (5), mP26 (4) and drop26 (7). The unmodified plant was found in 8 of 8 sections in every variant except mF13 (7), mP13 (7), mF20 (5), mP20 (5), mF26 (4) and mP26 (4). The noisy plant was found in 8 of 8 in most variants, but in only 3-7 of 8 under the mid-to-large stop sets. See compact_sw.md, column "plants detected".

## 3. k-mer index (kmer.py, analysis_kmer.md)

For each of the 42 variants and 10 targets (s0-s8, whole book), against the real target, 200 order shuffles and 20 held-out English windows:
- H: total k-mer hits, k = 6 and 8;
- band: the most k-mer hits on one 64-word diagonal band, i.e. a seed cluster;
- run: the longest exact common run of word lengths;
- per-text hit counts.

- 2,100 cells: z mean -0.37, sd 0.71, max +3.25, one cell above z 3, minimum empirical p = 0.020, and in no cell does the real value reach the shuffle maximum. By statistic: H6 z mean -0.62; H8 -0.47; band6 -0.32 (max +2.68); band8 -0.22 (max +3.25); run6 -0.25 (max +2.75).
- Best cells:
  - THonly band8 in s6: 7 against a null of 4.6 ± 0.7 (max 8);
  - noEA band8 in s6: 7;
  - base_mP1 run6 in s3: 14 against a shuffle max of 15.
  - All are inside the null range, and the held-out English maxima are the same size.
- Real band sizes are 4-17, against 293-722 for planted controls of section length.
- Whole book (base / mF2 / drop3 / letters):
  - band6: 17 / 17 / 16 / 16, against a null maximum of 57-61;
  - run6: 11-12, against a null mean of 12.5-12.8.
- Per-text hit counts:
  - 798 cells; real max-over-texts z has p < 0.01 in 1 cell (8 expected by chance) and p < 0.05 in 14 cells (40 expected).
  - The lowest p values are artefacts of repeated refrains that one target 8-gram happens to hit many times: Arabian Nights (Burton) in s0, 17 of 27 hits on "THE DAWN OF DAY AND CEASED TO SAY" (Shahrazad's refrain); Mabinogion II in s2, 31 of 36 hits on "EASY THOUGH THOU GET THIS THERE IS YET" (repeated formula).
  - Neither is a diagonal cluster.

## 4. Exhaustive Smith-Waterman (run_sw.py, sw.c; analysis_sw.md, compact_sw.md)

Smith-Waterman (match +1, mismatch -2, linear gap -2) runs for every section against the whole 15.7M-word library, with no seeding. An AVX-512 kernel runs 32 targets per pass: the real target, 23 shuffles, 4 held-out English windows and 4 plants. All 42 variants were run this way. Six key variants (base, mF2, mP2, drop2, drop3, letters) received 6 more passes of 32 shuffles, for 215 shuffles per section. The whole book was also run as a single target for the key variants. This replaces the seeded "top candidates only" route in the brief, so there is no seed-miss risk.

- Best-over-library scores of the real target are 10-15, against shuffle means of 9.4-12.5. Real scores sit slightly below the shuffles on average: z mean -0.24 over 378 cells; the sum over s0-s7 has z between -3.75 and +1.00. Held-out English windows sit slightly above (+0.33 against -0.18 for the real target, pooled), which is the same order effect as finding 3.
- Key variants, real best per section (shuffle mean in brackets), 215 shuffles each:

| variant | s0 | s1 | s2 | s3 | s4 | s5 | s6 | s7 | max z | sum z |
|---|---|---|---|---|---|---|---|---|---|---|
| base | 11 (10.8) | 12 (11.6) | 12 (11.7) | 11 (11.8) | 11 (11.3) | 11 (11.8) | 12 (11.8) | 11 (12.3) | +0.5 | -0.93 |
| base_mF2 | 10 (10.5) | 10 (11.4) | 11 (11.6) | 11 (11.5) | 11 (11.1) | 11 (11.5) | 12 (11.5) | 11 (12.1) | +0.6 | -1.92 |
| base_mP2 | 10 (10.5) | 11 (11.4) | 12 (11.6) | 11 (11.5) | 11 (11.2) | 10 (11.5) | **15** (11.6, max 14) | 12 (12.1) | +4.5 | +0.24 |
| base_drop2 | 10 (10.6) | 11 (11.6) | 12 (11.9) | 12 (11.7) | 12 (11.3) | 11 (11.7) | 12 (11.8) | 11 (12.3) | +0.8 | -0.91 |
| base_drop3 | 10 (10.6) | 11 (11.7) | 11 (11.8) | 12 (11.7) | 12 (11.3) | 11 (11.6) | 11 (11.7) | 11 (12.3) | +0.8 | -1.64 |
| letters | 11 (10.6) | 10 (11.4) | 12 (11.8) | 12 (11.6) | 12 (11.4) | 11 (11.7) | 12 (11.6) | 11 (12.2) | +0.7 | -0.55 |

- Only 4 cells score above z = 3. All four are the same Imitation island in base_mP2/3/4/6, s6, with z = 3.7-5.2; the mP3/4/6 values rest on only 23 shuffles.
- Family-wise test: the p0 shuffle permutations are identical across variants, so each replicate is a coherent fake target over all 336 cells. The real maximum z (5.23) ranks 2nd of 24 (replicate mean 4.10, maximum 6.27). The real maximum score excess (+2) ranks 9th of 24.
- Per text and section, key variants with 215 shuffles: the real max-over-texts z is 3.9-5.0, with p = 0.34-0.94, in base, mF2, drop2, drop3 and letters. In mP2 it is 7.93 (Imitation, s6), against a null maximum of 7.50.
- Whole book as one target, real against 23 shuffles: 12 against 12.9-13.3 (z -0.9 to -1.6) in base, mF2, drop2, drop3 and letters; 15 (Imitation, the same island) against a mean of 12.9 and a maximum of 15 (z +2.5) in mP2. Planted whole-book controls score 1,137-2,896.

### Task item 5: displaying alignments that beat the null

Only the Imitation island exceeds a cell null (show_align.py; island_key.py). Ciphertext word lengths against the candidate:

```
cipher #  1979 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992        1993    1994    1995   1996
cipher L     2    5    3    3    7    3    5    4    2    5    8    5    3    5           6       6       3      2
text      HE LOVETH FOR HIS BELOVED FOR JESUS WILL BE LOVED ALONE ABOVE ALL THINGS+THE LOVE+OF CREATED THINGS IS
text L       2    5    3    3    7    3    5    4    2    5    5    5    3    5           6       6       3      2
15 words before: cipher 2 5 6 10 3 9 10 2 7 5 5 7 4 3 8 / text 4 5 3 2 7 7 3 5 4 2 4 4 2 3 3   (no alignment)
15 words after:  cipher 3 2 11 8 3 8 3 2 3 4 5 4 4 6 4  / text 3 2 7 3 8 5 6 5 2 7 3 5 2 3 6   (no alignment)
```

The island spans 18 words (17 matches), below the 40-word threshold for key derivation. As a check, the key was derived anyway on the 63 runes of the 16 exactly matched words (two words skipped because the rune count differs; see Limitations):
- additive chain key, k = (D - 1 - x(p)) mod 28: IoC 1.13 normalised, which is random (sd about 0.2 at n = 63);
- GF(29) form, k = D · x(p)^-1: no visible pattern.

Not submitted to the oracle; there is nothing to submit.

## 5. Serial-structure test (order_test*.py, *.log; finding 3 above)

| model (Markov trained on library variant) | unsolved z, Markov-1 | unsolved z, Markov-2 | held-out English, section-sized windows (20): mean z (min), Markov-1 | Markov-2 |
|---|---|---|---|---|
| base | -1.08 | -1.32 | 9.5 (6.9) | 9.7 (6.9) |
| base_mF2 | -1.43 | -1.31 | 7.7 (5.7) | 8.1 (5.1) |
| base_mP2 | -0.55 | -0.61 | 6.4 (3.5) | 6.8 (4.6) |
| base_drop2 | -1.11 | -1.14 | 7.4 (2.6) | 8.1 (2.7) |
| base_drop3 | -1.00 | -0.98 | 6.7 (1.6) | 7.2 (2.0) |
| base_drop4 | -1.74 | -1.30 | 5.5 (1.9) | 5.9 (2.3) |
| letters | -0.77 | -0.73 | 10.0 (5.7) | 10.5 (6.7) |
| letters_drop2 | -1.16 | -0.88 | 6.8 (1.7) | 7.1 (1.9) |
| THonly_drop2 | -1.23 | -1.24 | 8.1 (5.2) | 8.4 (5.7) |

- Whole book as one 2,896-word sequence, 40 held-out windows: base +8.79 ± 1.80 (min 4.78); mF2 +7.37 ± 1.60 (min 3.95); drop3 +6.74 ± 1.42 (min 2.04). Unsolved: -1.06 / -1.30 / -1.02.
- LP1 solved pages (true runes, 695 words): Markov-1 z +4.31 / +3.12 / +3.39. Held-out windows of 695 words: +4.40 / +3.73 / +3.59.
- Unsolved, four 695-word blocks: -0.87, +0.92, -2.17, -0.59.
- Bigram independence chi-square (7x7 table, permutation null):
  - LP1 solved: z +4.0 (p 0.0015);
  - unsolved whole: -0.06 (p 0.49);
  - unsolved blocks: -1.18, +0.54, +2.09, -0.18.

## Limitations

- **Coverage.** The library covers 149 texts, mostly the repos' Cicada-adjacent canon plus 37 GITenberg texts. Kybalion, Zarathustra, Corpus Hermeticum, Gibran, Gödel Escher Bach, the Book of Enoch and Dhammapada are missing, and so is anything not on GitHub. A different translation or edition of a listed work counts as a different text.
- **Merge models.** Merged lengths are the sum of the separate word lengths, so digraphs formed across the junction are ignored (LOVE+OF = 6 here but L-O-U-EO-F = 5 if transliterated as one string). This changes a minority of merged words and would cost a true source a few points, not hundreds.
- **What finding 3 rests on.** It assumes the ciphertext separators are the only word-boundary information. The conclusion holds if the dashes in krisyotam_runes.txt are the book's word dividers; a transcription that reordered words would be needed to undo it.
- **Null sizes.** Non-key variants have only 23 shuffles in SW, so z values there use a noisy sd; empirical ranks and the 200-shuffle k-mer stage are the robust statistics.

## Files

| file | role |
|---|---|
| build_lib.py, lib.pkl, build_lib.log | library |
| fetched/ | fetched GITenberg texts |
| core.py | transliteration, variants, SW wrappers |
| sw.c, libsw.so | AVX-512 32-lane SW kernel |
| run_sw.py, sw_out/*.npz | per-text best scores and end positions for all lanes |
| kmer.py, kmer_out/*.pkl | k-mer stage |
| analyze.py, analysis_sw.md, compact_sw.md | SW analysis |
| analyze_kmer.py, analysis_kmer.md | k-mer analysis |
| posctrl.py, posctrl.log | positive control |
| show_align.py, island_key.py | alignment display, island key derivation |
| order_test.py, order_test2.py, order_test3.py, order_test4.py, order_test*.log, order_test.json | serial-structure tests |
