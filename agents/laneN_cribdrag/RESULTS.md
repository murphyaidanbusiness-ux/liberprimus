# RESULTS: laneN_cribdrag

Full-position crib drag for a RUNNING-TEXT key or KEYWORD key under the decryptable models (chain additive mod 28, chain GF(29), raw Vigenere/Beaufort with/without skip-on-repeat, with/without F-interrupt). Code, tables and raw outputs are in SCRATCH/agents/laneN_cribdrag/ (engine `drag.c`, cribs `prep_cribs.py`, tables `prep_tables.py`, controls `make_controls.py`/`analyze_ctrl.py`, aggregation `aggregate.py`/`top50.py`/`final_scan.py`; per-run outputs in `out/`).

## Verdict (one paragraph)

**Null.** Across about 3.1e8 key fragments per data version (real stream plus 50 doublet-matched shuffles for the unmodified stream, plus 20 shuffles for the F-deleted stream), no model x crib-class x aligned cell has a real family-wise maximum above the null maximum, for any of the three signatures (running-text quadgram Z, dictionary-keyword hit, periodicity). Real-vs-null z over the 125 cell-statistics ranges -2.7 to +2.1; the smallest empirical p is 1/50 (0.02 at the cell level; 1-2 of 125 cells are expected at that level by chance). 0 of the 3,200 listed real top hits exceed the null max of their own cell. A corpus search (128 local texts, 52.8M runes) of all 23,475 real fragments with Z >= 5 (or DICT >= 11, or PER >= 7) finds no 12-rune match under any of 58 shift/orientation variants (baseline 0/2000 on random fragments; the same search finds the key text at the right offset in the planted control). The positive controls are recovered. No candidate beats null, so nothing was extended or submitted to the oracle. A short crib set cannot exclude a running key longer than the cribs can reveal, but any English-ish or Cicada-keyword key that reaches a 20+ rune crib in these models would have shown at Z 10-18 (control) versus null max 6-12.

## 1. What cribdrag.py (ARMADA-20) already covered, and the dedup

`SCRATCH/dl/dukotah/liber-primus/analysis/armada20/cribdrag.py` ran: 9 cribs (INSTAR, EMERGENCE, DIVINITY, WISDOM, THEPRIMES, PARABLE, SACRED, TOTIENT, CIRCUMFERENCE; no spaces, no word-length use); every position of each of 56 pages separately; two raw additive mod-29 directions only (K = C - P and K = P - C, no chain model, no GF(29), no skip-on-repeat, no F-interrupt); scoring = mean quadgram of the transliterated key at shift 0 only (no shifts, no Atbash), plus an exact-substring test against ~15 reference texts; printed the top 20; no shuffle null, no positive control. ELIMINATION-LEDGER lists it as "Hill 2x2 / 3x3, crib-dragging: dead, nothing". The ledger's "page-local semantic keys (B3, 0 hits / 168k crib readouts)" is a near-duplicate of the unaligned part (different statistic, no word alignment, no chain).

What is new here: ~5,000 cribs (not 9) incl. word-boundary alignment as a filter, the chain-Z28 and chain-GF29 key fragments (D-stream, doublet = unknown), raw Beaufort, <=1 skip (rawskip), F-deleted streams, all 29 (28 for Z28) shifts plus Atbash/negation of every fragment, three signatures, a 50-shuffle null per cell, and positive controls. Exact repeat: none (the 9 old cribs are a subset of C1, at shift 0 under raw Vig/Beaufort).

## 2. Setup (what was run)

**Streams.** lpdata.unsolved(), 12,956 runes, 2,896 words, 55 pages. Windows never cross a page boundary. Chain increments D_i = c_i - c_(i-1); D_i = 0 (86 doublets) and plaintext EA are treated as an unknown key letter (gap): windows containing a gap are skipped, not scored.
**Null.** 50 shuffles: the 12,955 increments are permuted globally (c rebuilt by cumulative sum), so doublet count (86), flatness and the word/page structure are exactly preserved. The same C engine, same cribs, same calibration. The F-deleted stream (all F runes removed, words and lengths recomputed) uses 20 of these shuffles (the F-delete is applied after shuffling) because of run time.
**Cribs (5,075 distinct).** C1 phrases: 240 unaligned (every solved part-one line, LP1 section titles, all named phrases in the brief incl. AN INSTRUCTION, COMMAND YOUR OWN SELF, DO FOUR UNREASONABLE THINGS EACH DAY, PROGRAM YOUR MIND, PROGRAM REALITY, THE PRIMES ARE SACRED, THE TOTIENT FUNCTION IS SACRED, ALL THINGS SHOULD BE ENCRYPTED, WHO ARE YOU WHO WISHES TO STUDY HERE, THE INSTAR, CIRCUMFERENCE, DIVINITY WITHIN, FIND THE DIVINITY WITHIN AND EMERGE, and 150+ clauses from the Cicada PGP messages/puzzle texts, 4-100 runes) plus 4,335 aligned-only contiguous sub-phrases (1-6 words, >=6 runes) of those lines. C2: the 300 most frequent English words of >=5 runes (from 11 corpora, Cicada transliteration: TH EO NG OE AE IA EA digraphs, K->C, V->U, Z->S, ING->NG). C3: 200 word bigrams/trigrams (130 bigrams + 70 trigrams by corpus frequency, forced to include OF THE, IN THE, AND THE, IT IS, YOU ARE; >=4 runes). Unaligned = all page-internal positions (12,956 starts); aligned = crib word lengths must equal consecutive full ciphertext word lengths, starting at a word start.
**Models (key fragment k_i).** (1) chain-Z28: k = D - p (mod 28) and k = D + p (mod 28) (Atbash-plaintext); (2) chain-GF29: k = D * x(p)^-1 with x(p) = ((p+o) mod 28)+1, 28 offsets (the Atbash/reversed sigma x -> -x is exactly the key negation, already covered by the orientation search, so there are 28 distinct variants, not 56; the inverse-key form k' = 1/k was not run); (3) raw Vigenere/variant Beaufort (k = c - p; variant Beaufort is its negation) and Beaufort (k = c + p); (4) rawskip: <= 1 skipped key letter anywhere in the fragment (gap between letters g-1 and g, g = 0..L-1, so a superset of (3)). F-interrupt variant = every model rerun on the stream with all F runes deleted.
**Signatures.** (a) Running text: sum of rune-quadgram log10 probabilities (LM trained on 11 English corpora in the Cicada rune domain) over all gap-free 4-windows, maximised over all 29 shifts (28 for Z28) x {identity, negation} (negation + shift covers Atbash); standardised to Z with mean/sd from 1-4k random fragments of the same number of windows W; only fragments in the top 4% of a shift-invariant difference-trigram prefilter get the exact score. (b) Keyword: longest run of consecutive 8-letter key windows (shift/negation invariant, cyclic) that are windows of a cyclic dictionary word (361,830 words: Cicada vocabulary, English list; 3.3M windows), reported as run + 7 letters; not computed for chain-GF29 unaligned (cost); equals the raw value for rawskip. (c) Periodicity: longest run of k[i] = k[i+p], p = 1..12.
**Counts.** About 3.13e8 fragments per run (F=0), 3.02e8 (F=1); 51 + 21 full runs = 72 engine runs, ~2.2e10 fragments scored in total.
**Caveats.** The exact score is computed only after the prefilter (4% pass); on pure-noise fragments it retains only ~10-45% of the Z>=3 events (calibration recall printout), but real English fragments pass almost always (controls). It affects real and null identically. Z is a standardised score of a best-of-58 statistic and has a heavy right tail (null max 6-12 over the cells), so only the real-vs-null comparison is meaningful. Cribs are literal Cicada-transliterated English; spelling variants are not enumerated.

## 3. Positive controls (full 12,956-rune streams with the real word/page layout; English Walden background plaintext; running key = Leviathan, held out of the LM; 500 planted runes of the solved Koan text at p10 start; engine and cribs identical)

(i) chain cipher, c_i = c_(i-1) + 1 + ((p_i + key_i) mod 28), running English key. `chain_A` = planted region keeps its own word boundaries (aligned and unaligned views); `chain_B` = real LP2 word lengths everywhere (unaligned view only). (ii) Vigenere with Cicada keyword DIVINITY and skip-on-repeat (0 doublets), same layouts (`vig_A`, `vig_B`).
Results (full printout below): for chain, every true crib occurrence with L >= 20 runes is flagged (71/71 views in chain_A, 12/12 in chain_B), Z = 10 to 18 (median 10.8), against null maxima of 6-12 in the same cells, so detection is at Z > 5 and above the null max; L 12-19: 122/163 at Z > 5 (140/163 at Z >= 3); L 8-11: 20/128 at Z > 5 (median Z 4.3, i.e. not reliably detectable); L < 8: not detectable (as expected, W <= 3). The key text is recovered by the corpus search (finds leviathan.txt at the right offset). For the keyword case, true positions with L >= 16 show periodicity run median 10 to 34 (chance probability ~29^-r; null max 6-8) and a dictionary hit (DIVINITY) in 107/114 (L 16-23), 23/23, 7/7, 4/4 for longer cribs; rawskip Z >= 5 in 111/114. Control failures: crib occurrences shorter than ~12 runes (no signal is claimed there).

```
===== chain_A dump rows 895165
true crib-occurrences tested (aligned+unaligned views): 524  in dump with Z>=3: 310
  L<8    n=158  detected(Z>=3)= 11  Z>5=  0  median Z(detected)=3.443  max=3.865
  8-11   n=128  detected(Z>=3)= 84  Z>5= 20  median Z(detected)=4.292  max=6.497
  12-19  n=163  detected(Z>=3)=140  Z>5=122  median Z(detected)=7.12  max=11.819
  20-39  n= 71  detected(Z>=3)= 71  Z>5= 71  median Z(detected)=10.764  max=17.296
  40+    n=  4  detected(Z>=3)=  4  Z>5=  4  median Z(detected)=18.083  max=18.083
  Z>=5 chain rows: in planted region 279  elsewhere (background English incl. true C2/C3 cribs in Walden) 581
  of in-region Z>=5 rows, not a true crib occurrence: 62
   top: Z=18.1 L=42 al=0 crib=THAT IS NOT WHO YOU ARE THAT IS ONLY WHAT YOU ARE 
   top: Z=18.1 L=42 al=1 crib=THAT IS NOT WHO YOU ARE THAT IS ONLY WHAT YOU ARE 
   top: Z=17.3 L=33 al=0 crib=A MAN DECIDED TO GO AND STUDY WITH A MASTER
   top: Z=17.3 L=33 al=1 crib=A MAN DECIDED TO GO AND STUDY WITH A MASTER
   top: Z=16.5 L=29 al=0 crib=WHO ARE YOU WHO WISHES TO STUDY HERE
   top: Z=16.5 L=29 al=1 crib=WHO ARE YOU WHO WISHES TO STUDY HERE
   top: Z=15.0 L=41 al=0 crib=THAT IS WHAT YOU DO NOT WHO YOU ARE REPLIED THE MA
   top: Z=15.0 L=41 al=1 crib=THAT IS WHAT YOU DO NOT WHO YOU ARE REPLIED THE MA
  long (L>=12) true occurrences with Z<5 or missing: 41 of 238
===== chain_B dump rows 894677
true crib-occurrences tested (aligned+unaligned views): 64  in dump with Z>=3: 14
  L<8    n= 51  detected(Z>=3)=  2  Z>5=  0  median Z(detected)=3.308  max=3.308
  8-11   n=  1  detected(Z>=3)=  0  Z>5=  0  median Z(detected)=None  max=None
  20-39  n= 10  detected(Z>=3)= 10  Z>5= 10  median Z(detected)=13.504  max=17.296
  40+    n=  2  detected(Z>=3)=  2  Z>5=  2  median Z(detected)=18.083  max=18.083
  Z>=5 chain rows: in planted region 56  elsewhere (background English incl. true C2/C3 cribs in Walden) 581
  of in-region Z>=5 rows, not a true crib occurrence: 44
   top: Z=18.1 L=42 al=0 crib=THAT IS NOT WHO YOU ARE THAT IS ONLY WHAT YOU ARE 
   top: Z=17.3 L=33 al=0 crib=A MAN DECIDED TO GO AND STUDY WITH A MASTER
   top: Z=16.5 L=29 al=0 crib=WHO ARE YOU WHO WISHES TO STUDY HERE
   top: Z=15.0 L=41 al=0 crib=THAT IS WHAT YOU DO NOT WHO YOU ARE REPLIED THE MA
   top: Z=15.0 L=38 al=0 crib=AFTER A MOMENT OF THOUGHT THE PROFESSOR REPLIED
   top: Z=13.7 L=28 al=0 crib=THE STUDENT TOLD THE MASTER HIS NAME
   top: Z=13.5 L=24 al=0 crib=HE WENT TO THE DOOR OF THE MASTER
   top: Z=13.5 L=29 al=0 crib=WHO ARE YOU WHO WISHES TO STUDY HERE
  long (L>=12) true occurrences with Z<5 or missing: 0 of 12
===== vig_A dump rows 947091
keyword control: true occurrences 524
  raw(mt2) fragments 18456034.0
  L in [0,8): n=158  PER median 0 max 0 | DICT>=9: 0 | rawskip Z>=5: 0
  L in [8,16): n=218  PER median 1 max 8 | DICT>=9: 141 | rawskip Z>=5: 52
  L in [16,24): n=114  PER median 10 max 15 | DICT>=9: 107 | rawskip Z>=5: 111
  L in [24,32): n=23  PER median 14 max 21 | DICT>=9: 23 | rawskip Z>=5: 23
  L in [32,40): n=7  PER median 21 max 24 | DICT>=9: 7 | rawskip Z>=5: 7
  L in [40,48): n=4  PER median 34 max 34 | DICT>=9: 4 | rawskip Z>=5: 4
  cell counts raw (cls,al): nfrag, maxPER, nP5, nP6, nP8
    (2, 0, 0) nfrag 5460054 maxPER 33 nP5 92 nP6 29 nP8 23 maxDICT 41 nD9 811
    (2, 0, 1) nfrag 211808 maxPER 33 nP5 187 nP6 157 nP8 78 maxDICT 41 nD9 198
    (2, 1, 0) nfrag 7568832 maxPER 5 nP5 3 nP6 0 nP8 0 maxDICT 10 nD9 17
    (2, 1, 1) nfrag 144900 maxPER 4 nP5 0 nP6 0 nP8 0 maxDICT 8 nD9 0
    (2, 2, 0) nfrag 5045240 maxPER 4 nP5 0 nP6 0 nP8 0 maxDICT 10 nD9 35
    (2, 2, 1) nfrag 25200 maxPER 3 nP5 0 nP6 0 nP8 0 maxDICT 0 nD9 0
  raw rows with PER>=8 not at a true crib occurrence: 22  PER>=10: 9
===== vig_B dump rows 946305
keyword control: true occurrences 64
  raw(mt2) fragments 18449272.0
  L in [0,8): n=51  PER median 0 max 0 | DICT>=9: 0 | rawskip Z>=5: 0
  L in [8,16): n=1  PER median 0 max 0 | DICT>=9: 0 | rawskip Z>=5: 0
  L in [24,32): n=7  PER median 13 max 21 | DICT>=9: 7 | rawskip Z>=5: 7
  L in [32,40): n=3  PER median 21 max 24 | DICT>=9: 3 | rawskip Z>=5: 3
  L in [40,48): n=2  PER median 34 max 34 | DICT>=9: 2 | rawskip Z>=5: 2
  cell counts raw (cls,al): nfrag, maxPER, nP5, nP6, nP8
    (2, 0, 0) nfrag 5460054 maxPER 33 nP5 92 nP6 29 nP8 23 maxDICT 41 nD9 811
    (2, 0, 1) nfrag 206992 maxPER 3 nP5 0 nP6 0 nP8 0 maxDICT 9 nD9 2
    (2, 1, 0) nfrag 7568832 maxPER 5 nP5 3 nP6 0 nP8 0 maxDICT 10 nD9 17
    (2, 1, 1) nfrag 143496 maxPER 4 nP5 0 nP6 0 nP8 0 maxDICT 8 nD9 0
    (2, 2, 0) nfrag 5045240 maxPER 4 nP5 0 nP6 0 nP8 0 maxDICT 10 nD9 35
    (2, 2, 1) nfrag 24658 maxPER 3 nP5 0 nP6 0 nP8 0 maxDICT 0 nD9 0
  raw rows with PER>=8 not at a true crib occurrence: 14  PER>=10: 6

```

## 4. Real vs null, family-wise maxima per model and crib class

All maxima over every position x crib x variant in the cell. "z" = (real max - null mean)/null sd; "nulls >= real" counts shuffles whose max is at least the real max. Models: chain-Z28, chain-GF29, raw Vig/Beau (k = c-p, c+p), raw+skip (<=1 skip).

### F-interrupt variant = stream as given  (null shuffles: 50)


**running-text Z (quadgram, best of 29 shifts x 2 orientations)**

| model | class | aligned | #fragments (real) | real max | null mean | null sd | null max | z(real vs null) | nulls >= real |
|---|---|---|---|---|---|---|---|---|---|
| chain-Z28 | C1 phrases | no | 5.45e+06 | 8.086 | 8.690 | 0.527 | 9.876 | -1.15 | 45/50 |
| chain-Z28 | C1 phrases | yes | 2.07e+05 | 5.052 | 5.382 | 0.462 | 6.944 | -0.71 | 36/50 |
| chain-Z28 | C2 words | no | 7.57e+06 | 5.606 | 5.787 | 0.285 | 6.408 | -0.63 | 39/50 |
| chain-Z28 | C2 words | yes | 1.43e+05 | 4.370 | 4.392 | 0.350 | 5.379 | -0.06 | 26/50 |
| chain-Z28 | C3 n-grams | no | 5.04e+06 | 7.057 | 6.496 | 0.506 | 7.545 | +1.11 | 9/50 |
| chain-Z28 | C3 n-grams | yes | 2.46e+04 | 3.996 | 3.830 | 0.329 | 4.915 | +0.51 | 10/50 |
| chain-GF29 | C1 phrases | no | 7.62e+07 | 10.046 | 10.253 | 0.650 | 12.154 | -0.32 | 26/50 |
| chain-GF29 | C1 phrases | yes | 2.9e+06 | 6.211 | 6.450 | 0.371 | 7.282 | -0.65 | 36/50 |
| chain-GF29 | C2 words | no | 1.06e+08 | 6.319 | 6.490 | 0.264 | 7.074 | -0.65 | 36/50 |
| chain-GF29 | C2 words | yes | 2.01e+06 | 5.340 | 5.073 | 0.287 | 5.960 | +0.93 | 8/50 |
| chain-GF29 | C3 n-grams | no | 7.06e+07 | 7.330 | 7.892 | 0.538 | 9.177 | -1.05 | 45/50 |
| chain-GF29 | C3 n-grams | yes | 3.45e+05 | 4.966 | 4.494 | 0.308 | 5.451 | +1.53 | 2/50 |
| raw Vig/Beau | C1 phrases | no | 5.45e+06 | 8.919 | 8.734 | 0.419 | 9.734 | +0.44 | 14/50 |
| raw Vig/Beau | C1 phrases | yes | 2.07e+05 | 5.317 | 5.393 | 0.386 | 6.381 | -0.20 | 26/50 |
| raw Vig/Beau | C2 words | no | 7.57e+06 | 5.910 | 5.881 | 0.319 | 6.739 | +0.09 | 21/50 |
| raw Vig/Beau | C2 words | yes | 1.43e+05 | 4.568 | 4.508 | 0.396 | 5.989 | +0.15 | 18/50 |
| raw Vig/Beau | C3 n-grams | no | 5.04e+06 | 6.622 | 6.572 | 0.449 | 7.660 | +0.11 | 22/50 |
| raw Vig/Beau | C3 n-grams | yes | 2.46e+04 | 3.737 | 3.887 | 0.288 | 4.852 | -0.52 | 32/50 |
| raw+skip | C1 phrases | no | 5.45e+06 | 9.244 | 9.406 | 0.594 | 11.359 | -0.27 | 26/50 |
| raw+skip | C1 phrases | yes | 2.07e+05 | 5.317 | 5.596 | 0.360 | 6.482 | -0.77 | 36/50 |
| raw+skip | C2 words | no | 7.57e+06 | 6.363 | 5.943 | 0.305 | 6.739 | +1.38 | 5/50 |
| raw+skip | C2 words | yes | 1.43e+05 | 4.568 | 4.537 | 0.376 | 5.989 | +0.08 | 20/50 |
| raw+skip | C3 n-grams | no | 5.04e+06 | 7.218 | 7.090 | 0.523 | 8.151 | +0.25 | 22/50 |
| raw+skip | C3 n-grams | yes | 2.46e+04 | 3.737 | 3.993 | 0.283 | 4.852 | -0.90 | 41/50 |

**dictionary-keyword hit length (letters, >= 8)**

| model | class | aligned | #fragments (real) | real max | null mean | null sd | null max | z(real vs null) | nulls >= real |
|---|---|---|---|---|---|---|---|---|---|
| chain-Z28 | C1 phrases | no | 5.45e+06 | 12.000 | 11.520 | 0.614 | 13.000 | +0.78 | 23/50 |
| chain-Z28 | C1 phrases | yes | 2.07e+05 | 9.000 | 8.860 | 0.495 | 10.000 | +0.28 | 40/50 |
| chain-Z28 | C2 words | no | 7.57e+06 | 9.000 | 9.560 | 0.501 | 10.000 | -1.12 | 50/50 |
| chain-Z28 | C2 words | yes | 1.43e+05 | 8.000 | 7.940 | 1.185 | 9.000 | +0.05 | 49/50 |
| chain-Z28 | C3 n-grams | no | 5.04e+06 | 10.000 | 9.640 | 0.598 | 11.000 | +0.60 | 29/50 |
| chain-Z28 | C3 n-grams | yes | 2.46e+04 | 0.000 | 3.380 | 4.015 | 9.000 | -0.84 | 50/50 |
| chain-GF29 | C1 phrases | no | 7.62e+07 | 0.000 | 0.000 | 0.000 | 0.000 | n/a | 50/50 |
| chain-GF29 | C1 phrases | yes | 2.9e+06 | 9.000 | 9.580 | 0.499 | 10.000 | -1.16 | 50/50 |
| chain-GF29 | C2 words | no | 1.06e+08 | 0.000 | 0.000 | 0.000 | 0.000 | n/a | 50/50 |
| chain-GF29 | C2 words | yes | 2.01e+06 | 9.000 | 8.640 | 0.525 | 10.000 | +0.69 | 31/50 |
| chain-GF29 | C3 n-grams | no | 7.06e+07 | 0.000 | 0.000 | 0.000 | 0.000 | n/a | 50/50 |
| chain-GF29 | C3 n-grams | yes | 3.45e+05 | 8.000 | 8.100 | 0.303 | 9.000 | -0.33 | 50/50 |
| raw Vig/Beau | C1 phrases | no | 5.45e+06 | 11.000 | 11.500 | 0.580 | 13.000 | -0.86 | 50/50 |
| raw Vig/Beau | C1 phrases | yes | 2.07e+05 | 9.000 | 8.840 | 0.370 | 9.000 | +0.43 | 42/50 |
| raw Vig/Beau | C2 words | no | 7.57e+06 | 10.000 | 9.320 | 0.471 | 10.000 | +1.44 | 16/50 |
| raw Vig/Beau | C2 words | yes | 1.43e+05 | 8.000 | 8.080 | 0.274 | 9.000 | -0.29 | 50/50 |
| raw Vig/Beau | C3 n-grams | no | 5.04e+06 | 9.000 | 9.460 | 0.542 | 11.000 | -0.85 | 50/50 |
| raw Vig/Beau | C3 n-grams | yes | 2.46e+04 | 0.000 | 3.040 | 3.923 | 8.000 | -0.78 | 50/50 |

**periodicity (longest run of k[i]=k[i+p], p<=12)**

| model | class | aligned | #fragments (real) | real max | null mean | null sd | null max | z(real vs null) | nulls >= real |
|---|---|---|---|---|---|---|---|---|---|
| chain-Z28 | C1 phrases | no | 5.45e+06 | 6.000 | 5.900 | 0.505 | 8.000 | +0.20 | 42/50 |
| chain-Z28 | C1 phrases | yes | 2.07e+05 | 3.000 | 3.920 | 0.340 | 5.000 | -2.70 | 50/50 |
| chain-Z28 | C2 words | no | 7.57e+06 | 4.000 | 4.480 | 0.505 | 5.000 | -0.95 | 50/50 |
| chain-Z28 | C2 words | yes | 1.43e+05 | 4.000 | 3.340 | 0.479 | 4.000 | +1.38 | 17/50 |
| chain-Z28 | C3 n-grams | no | 5.04e+06 | 5.000 | 4.560 | 0.501 | 5.000 | +0.88 | 28/50 |
| chain-Z28 | C3 n-grams | yes | 2.46e+04 | 3.000 | 3.080 | 0.396 | 4.000 | -0.20 | 48/50 |
| chain-GF29 | C1 phrases | no | 7.62e+07 | 7.000 | 6.620 | 0.602 | 8.000 | +0.63 | 28/50 |
| chain-GF29 | C1 phrases | yes | 2.9e+06 | 5.000 | 4.560 | 0.541 | 6.000 | +0.81 | 27/50 |
| chain-GF29 | C2 words | no | 1.06e+08 | 5.000 | 5.240 | 0.431 | 6.000 | -0.56 | 50/50 |
| chain-GF29 | C2 words | yes | 2.01e+06 | 4.000 | 4.040 | 0.198 | 5.000 | -0.20 | 50/50 |
| chain-GF29 | C3 n-grams | no | 7.06e+07 | 5.000 | 5.300 | 0.463 | 6.000 | -0.65 | 50/50 |
| chain-GF29 | C3 n-grams | yes | 3.45e+05 | 4.000 | 3.720 | 0.454 | 4.000 | +0.62 | 36/50 |
| raw Vig/Beau | C1 phrases | no | 5.45e+06 | 6.000 | 5.920 | 0.634 | 8.000 | +0.13 | 39/50 |
| raw Vig/Beau | C1 phrases | yes | 2.07e+05 | 3.000 | 3.920 | 0.444 | 5.000 | -2.07 | 50/50 |
| raw Vig/Beau | C2 words | no | 7.57e+06 | 5.000 | 4.500 | 0.544 | 6.000 | +0.92 | 24/50 |
| raw Vig/Beau | C2 words | yes | 1.43e+05 | 4.000 | 3.520 | 0.544 | 5.000 | +0.88 | 25/50 |
| raw Vig/Beau | C3 n-grams | no | 5.04e+06 | 4.000 | 4.500 | 0.544 | 6.000 | -0.92 | 50/50 |
| raw Vig/Beau | C3 n-grams | yes | 2.46e+04 | 2.000 | 3.020 | 0.428 | 4.000 | -2.38 | 50/50 |
| raw+skip | C1 phrases | no | 5.45e+06 | 6.000 | 6.480 | 0.580 | 8.000 | -0.83 | 50/50 |
| raw+skip | C1 phrases | yes | 2.07e+05 | 5.000 | 4.180 | 0.388 | 5.000 | +2.11 | 9/50 |
| raw+skip | C2 words | no | 7.57e+06 | 5.000 | 5.040 | 0.283 | 6.000 | -0.14 | 49/50 |
| raw+skip | C2 words | yes | 1.43e+05 | 4.000 | 3.800 | 0.452 | 5.000 | +0.44 | 39/50 |
| raw+skip | C3 n-grams | no | 5.04e+06 | 5.000 | 5.120 | 0.328 | 6.000 | -0.37 | 50/50 |
| raw+skip | C3 n-grams | yes | 2.46e+04 | 2.000 | 3.060 | 0.470 | 4.000 | -2.26 | 50/50 |

**Tail counts (real vs null mean), running-text Z>=4 / Z>=5 and PER>=5 / DICT>=10 counts**

| model | class | aligned | real nZ>=4 | null mean | real nZ>=5 | null mean | real nPER>=5 | null mean | real nDICT>=10 | null mean |
|---|---|---|---|---|---|---|---|---|---|---|
| chain-Z28 | C1 phrases | no | 2546 | 2527.6 | 552 | 545.9 | 63 | 54.8 | 117 | 123.1 |
| chain-Z28 | C1 phrases | yes | 33 | 30.4 | 2 | 1.8 | 0 | 0.0 | 0 | 0.1 |
| chain-Z28 | C2 words | no | 401 | 419.1 | 19 | 14.0 | 0 | 0.7 | 0 | 0.9 |
| chain-Z28 | C2 words | yes | 2 | 2.5 | 0 | 0.1 | 0 | 0.0 | 0 | 0.0 |
| chain-Z28 | C3 n-grams | no | 335 | 297.7 | 36 | 21.5 | 1 | 0.9 | 5 | 1.4 |
| chain-Z28 | C3 n-grams | yes | 0 | 0.3 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 |
| chain-GF29 | C1 phrases | no | 37385 | 37574.0 | 8219 | 8271.9 | 825 | 791.6 | 0 | 0.0 |
| chain-GF29 | C1 phrases | yes | 497 | 475.3 | 27 | 31.3 | 1 | 1.0 | 0 | 1.2 |
| chain-GF29 | C2 words | no | 7283 | 7285.0 | 261 | 246.1 | 8 | 14.1 | 0 | 0.0 |
| chain-GF29 | C2 words | yes | 51 | 47.4 | 1 | 0.9 | 0 | 0.0 | 0 | 0.0 |
| chain-GF29 | C3 n-grams | no | 5042 | 5138.5 | 300 | 333.2 | 10 | 15.2 | 0 | 0.0 |
| chain-GF29 | C3 n-grams | yes | 4 | 4.9 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 |
| raw Vig/Beau | C1 phrases | no | 2521 | 2538.4 | 557 | 560.3 | 46 | 55.9 | 108 | 110.0 |
| raw Vig/Beau | C1 phrases | yes | 33 | 35.2 | 1 | 2.0 | 0 | 0.1 | 0 | 0.0 |
| raw Vig/Beau | C2 words | no | 559 | 540.5 | 12 | 18.5 | 2 | 0.6 | 1 | 0.4 |
| raw Vig/Beau | C2 words | yes | 6 | 3.8 | 0 | 0.1 | 0 | 0.0 | 0 | 0.0 |
| raw Vig/Beau | C3 n-grams | no | 348 | 362.3 | 27 | 22.3 | 0 | 1.0 | 0 | 1.2 |
| raw Vig/Beau | C3 n-grams | yes | 0 | 0.4 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 |
| raw+skip | C1 phrases | no | 8626 | 8689.3 | 1744 | 1827.7 | 376 | 394.2 | 0 | 0.0 |
| raw+skip | C1 phrases | yes | 77 | 73.2 | 1 | 4.0 | 1 | 0.2 | 0 | 0.0 |
| raw+skip | C2 words | no | 899 | 853.3 | 18 | 25.8 | 4 | 3.7 | 0 | 0.0 |
| raw+skip | C2 words | yes | 6 | 5.1 | 0 | 0.1 | 0 | 0.0 | 0 | 0.0 |
| raw+skip | C3 n-grams | no | 704 | 699.7 | 60 | 55.2 | 4 | 5.6 | 0 | 0.0 |
| raw+skip | C3 n-grams | yes | 0 | 0.5 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 |

### F-interrupt variant = F-runes deleted from stream  (null shuffles: 20)


**running-text Z (quadgram, best of 29 shifts x 2 orientations)**

| model | class | aligned | #fragments (real) | real max | null mean | null sd | null max | z(real vs null) | nulls >= real |
|---|---|---|---|---|---|---|---|---|---|
| chain-Z28 | C1 phrases | no | 5.23e+06 | 9.444 | 8.713 | 0.646 | 10.455 | +1.13 | 3/20 |
| chain-Z28 | C1 phrases | yes | 2.05e+05 | 5.014 | 5.335 | 0.447 | 6.509 | -0.72 | 15/20 |
| chain-Z28 | C2 words | no | 7.29e+06 | 6.216 | 5.759 | 0.332 | 6.450 | +1.38 | 2/20 |
| chain-Z28 | C2 words | yes | 1.37e+05 | 4.005 | 4.351 | 0.290 | 5.098 | -1.20 | 19/20 |
| chain-Z28 | C3 n-grams | no | 4.86e+06 | 7.692 | 6.705 | 0.638 | 8.010 | +1.55 | 1/20 |
| chain-Z28 | C3 n-grams | yes | 2.7e+04 | 3.996 | 3.871 | 0.246 | 4.272 | +0.51 | 7/20 |
| chain-GF29 | C1 phrases | no | 7.32e+07 | 10.336 | 10.084 | 0.623 | 11.992 | +0.40 | 5/20 |
| chain-GF29 | C1 phrases | yes | 2.86e+06 | 5.558 | 6.446 | 0.376 | 7.578 | -2.36 | 20/20 |
| chain-GF29 | C2 words | no | 1.02e+08 | 6.319 | 6.589 | 0.397 | 7.881 | -0.68 | 15/20 |
| chain-GF29 | C2 words | yes | 1.92e+06 | 5.340 | 5.021 | 0.270 | 5.544 | +1.18 | 2/20 |
| chain-GF29 | C3 n-grams | no | 6.8e+07 | 7.330 | 7.693 | 0.506 | 8.704 | -0.72 | 15/20 |
| chain-GF29 | C3 n-grams | yes | 3.78e+05 | 4.966 | 4.555 | 0.395 | 6.038 | +1.04 | 1/20 |
| raw Vig/Beau | C1 phrases | no | 5.23e+06 | 9.054 | 8.782 | 0.764 | 10.909 | +0.36 | 5/20 |
| raw Vig/Beau | C1 phrases | yes | 2.05e+05 | 5.179 | 5.368 | 0.294 | 6.279 | -0.64 | 15/20 |
| raw Vig/Beau | C2 words | no | 7.29e+06 | 5.923 | 5.879 | 0.347 | 6.797 | +0.13 | 7/20 |
| raw Vig/Beau | C2 words | yes | 1.37e+05 | 4.568 | 4.580 | 0.412 | 5.989 | -0.03 | 7/20 |
| raw Vig/Beau | C3 n-grams | no | 4.86e+06 | 5.865 | 6.456 | 0.470 | 7.660 | -1.26 | 18/20 |
| raw Vig/Beau | C3 n-grams | yes | 2.7e+04 | 3.737 | 3.822 | 0.254 | 4.237 | -0.33 | 12/20 |
| raw+skip | C1 phrases | no | 5.23e+06 | 9.594 | 9.283 | 0.702 | 11.359 | +0.44 | 5/20 |
| raw+skip | C1 phrases | yes | 2.05e+05 | 5.864 | 5.538 | 0.360 | 6.744 | +0.90 | 3/20 |
| raw+skip | C2 words | no | 7.29e+06 | 5.923 | 5.949 | 0.310 | 6.797 | -0.08 | 10/20 |
| raw+skip | C2 words | yes | 1.37e+05 | 4.568 | 4.590 | 0.408 | 5.989 | -0.05 | 7/20 |
| raw+skip | C3 n-grams | no | 4.86e+06 | 6.611 | 7.093 | 0.608 | 8.151 | -0.79 | 16/20 |
| raw+skip | C3 n-grams | yes | 2.7e+04 | 3.737 | 3.925 | 0.256 | 4.463 | -0.74 | 16/20 |

**dictionary-keyword hit length (letters, >= 8)**

| model | class | aligned | #fragments (real) | real max | null mean | null sd | null max | z(real vs null) | nulls >= real |
|---|---|---|---|---|---|---|---|---|---|
| chain-Z28 | C1 phrases | no | 5.23e+06 | 12.000 | 11.400 | 0.503 | 12.000 | +1.19 | 8/20 |
| chain-Z28 | C1 phrases | yes | 2.05e+05 | 9.000 | 8.950 | 0.605 | 10.000 | +0.08 | 16/20 |
| chain-Z28 | C2 words | no | 7.29e+06 | 9.000 | 9.500 | 0.513 | 10.000 | -0.97 | 20/20 |
| chain-Z28 | C2 words | yes | 1.37e+05 | 8.000 | 8.050 | 0.224 | 9.000 | -0.22 | 20/20 |
| chain-Z28 | C3 n-grams | no | 4.86e+06 | 10.000 | 9.650 | 0.587 | 11.000 | +0.60 | 12/20 |
| chain-Z28 | C3 n-grams | yes | 2.7e+04 | 0.000 | 3.250 | 4.089 | 9.000 | -0.79 | 20/20 |
| chain-GF29 | C1 phrases | no | 7.32e+07 | 0.000 | 0.000 | 0.000 | 0.000 | n/a | 20/20 |
| chain-GF29 | C1 phrases | yes | 2.86e+06 | 10.000 | 9.500 | 0.513 | 10.000 | +0.97 | 10/20 |
| chain-GF29 | C2 words | no | 1.02e+08 | 0.000 | 0.000 | 0.000 | 0.000 | n/a | 20/20 |
| chain-GF29 | C2 words | yes | 1.92e+06 | 9.000 | 8.500 | 0.513 | 9.000 | +0.97 | 10/20 |
| chain-GF29 | C3 n-grams | no | 6.8e+07 | 0.000 | 0.000 | 0.000 | 0.000 | n/a | 20/20 |
| chain-GF29 | C3 n-grams | yes | 3.78e+05 | 8.000 | 8.100 | 0.308 | 9.000 | -0.32 | 20/20 |
| raw Vig/Beau | C1 phrases | no | 5.23e+06 | 11.000 | 11.650 | 0.671 | 13.000 | -0.97 | 20/20 |
| raw Vig/Beau | C1 phrases | yes | 2.05e+05 | 9.000 | 8.650 | 0.587 | 10.000 | +0.60 | 12/20 |
| raw Vig/Beau | C2 words | no | 7.29e+06 | 10.000 | 9.350 | 0.489 | 10.000 | +1.33 | 7/20 |
| raw Vig/Beau | C2 words | yes | 1.37e+05 | 8.000 | 8.050 | 0.224 | 9.000 | -0.22 | 20/20 |
| raw Vig/Beau | C3 n-grams | no | 4.86e+06 | 9.000 | 9.450 | 0.510 | 10.000 | -0.88 | 20/20 |
| raw Vig/Beau | C3 n-grams | yes | 2.7e+04 | 8.000 | 2.000 | 3.554 | 8.000 | +1.69 | 5/20 |

**periodicity (longest run of k[i]=k[i+p], p<=12)**

| model | class | aligned | #fragments (real) | real max | null mean | null sd | null max | z(real vs null) | nulls >= real |
|---|---|---|---|---|---|---|---|---|---|
| chain-Z28 | C1 phrases | no | 5.23e+06 | 6.000 | 5.700 | 0.470 | 6.000 | +0.64 | 14/20 |
| chain-Z28 | C1 phrases | yes | 2.05e+05 | 3.000 | 3.950 | 0.394 | 5.000 | -2.41 | 20/20 |
| chain-Z28 | C2 words | no | 7.29e+06 | 4.000 | 4.250 | 0.444 | 5.000 | -0.56 | 20/20 |
| chain-Z28 | C2 words | yes | 1.37e+05 | 4.000 | 3.250 | 0.444 | 4.000 | +1.69 | 5/20 |
| chain-Z28 | C3 n-grams | no | 4.86e+06 | 5.000 | 4.600 | 0.503 | 5.000 | +0.80 | 12/20 |
| chain-Z28 | C3 n-grams | yes | 2.7e+04 | 3.000 | 3.050 | 0.224 | 4.000 | -0.22 | 20/20 |
| chain-GF29 | C1 phrases | no | 7.32e+07 | 7.000 | 6.700 | 0.571 | 8.000 | +0.53 | 13/20 |
| chain-GF29 | C1 phrases | yes | 2.86e+06 | 4.000 | 4.450 | 0.510 | 5.000 | -0.88 | 20/20 |
| chain-GF29 | C2 words | no | 1.02e+08 | 5.000 | 5.250 | 0.444 | 6.000 | -0.56 | 20/20 |
| chain-GF29 | C2 words | yes | 1.92e+06 | 4.000 | 4.150 | 0.366 | 5.000 | -0.41 | 20/20 |
| chain-GF29 | C3 n-grams | no | 6.8e+07 | 5.000 | 5.200 | 0.410 | 6.000 | -0.49 | 20/20 |
| chain-GF29 | C3 n-grams | yes | 3.78e+05 | 4.000 | 3.800 | 0.410 | 4.000 | +0.49 | 16/20 |
| raw Vig/Beau | C1 phrases | no | 5.23e+06 | 6.000 | 5.800 | 0.834 | 8.000 | +0.24 | 12/20 |
| raw Vig/Beau | C1 phrases | yes | 2.05e+05 | 3.000 | 4.050 | 0.510 | 5.000 | -2.06 | 20/20 |
| raw Vig/Beau | C2 words | no | 7.29e+06 | 5.000 | 4.400 | 0.503 | 5.000 | +1.19 | 8/20 |
| raw Vig/Beau | C2 words | yes | 1.37e+05 | 4.000 | 3.700 | 0.571 | 5.000 | +0.53 | 13/20 |
| raw Vig/Beau | C3 n-grams | no | 4.86e+06 | 4.000 | 4.500 | 0.513 | 5.000 | -0.97 | 20/20 |
| raw Vig/Beau | C3 n-grams | yes | 2.7e+04 | 3.000 | 3.000 | 0.324 | 4.000 | +0.00 | 19/20 |
| raw+skip | C1 phrases | no | 5.23e+06 | 6.000 | 6.450 | 0.605 | 8.000 | -0.74 | 20/20 |
| raw+skip | C1 phrases | yes | 2.05e+05 | 4.000 | 4.250 | 0.550 | 5.000 | -0.45 | 19/20 |
| raw+skip | C2 words | no | 7.29e+06 | 5.000 | 5.000 | 0.324 | 6.000 | +0.00 | 19/20 |
| raw+skip | C2 words | yes | 1.37e+05 | 4.000 | 3.950 | 0.394 | 5.000 | +0.13 | 18/20 |
| raw+skip | C3 n-grams | no | 4.86e+06 | 5.000 | 5.000 | 0.000 | 5.000 | n/a | 20/20 |
| raw+skip | C3 n-grams | yes | 2.7e+04 | 3.000 | 3.200 | 0.523 | 4.000 | -0.38 | 19/20 |

**Tail counts (real vs null mean), running-text Z>=4 / Z>=5 and PER>=5 / DICT>=10 counts**

| model | class | aligned | real nZ>=4 | null mean | real nZ>=5 | null mean | real nPER>=5 | null mean | real nDICT>=10 | null mean |
|---|---|---|---|---|---|---|---|---|---|---|
| chain-Z28 | C1 phrases | no | 2428 | 2395.9 | 561 | 515.7 | 59 | 51.0 | 108 | 122.0 |
| chain-Z28 | C1 phrases | yes | 28 | 29.6 | 1 | 1.9 | 0 | 0.1 | 0 | 0.2 |
| chain-Z28 | C2 words | no | 357 | 407.6 | 18 | 13.4 | 0 | 0.4 | 0 | 0.8 |
| chain-Z28 | C2 words | yes | 1 | 2.2 | 0 | 0.1 | 0 | 0.0 | 0 | 0.0 |
| chain-Z28 | C3 n-grams | no | 327 | 283.1 | 32 | 20.8 | 1 | 0.8 | 6 | 1.2 |
| chain-Z28 | C3 n-grams | yes | 0 | 0.4 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 |
| chain-GF29 | C1 phrases | no | 35947 | 35826.9 | 7935 | 7857.4 | 748 | 747.7 | 0 | 0.0 |
| chain-GF29 | C1 phrases | yes | 453 | 455.2 | 22 | 31.1 | 0 | 0.6 | 1 | 0.7 |
| chain-GF29 | C2 words | no | 6814 | 6974.6 | 244 | 234.2 | 10 | 13.6 | 0 | 0.0 |
| chain-GF29 | C2 words | yes | 47 | 42.6 | 1 | 0.8 | 0 | 0.1 | 0 | 0.0 |
| chain-GF29 | C3 n-grams | no | 4813 | 4886.9 | 292 | 313.8 | 10 | 14.5 | 0 | 0.0 |
| chain-GF29 | C3 n-grams | yes | 6 | 5.2 | 0 | 0.1 | 0 | 0.0 | 0 | 0.0 |
| raw Vig/Beau | C1 phrases | no | 2468 | 2449.6 | 568 | 539.1 | 49 | 52.0 | 118 | 106.2 |
| raw Vig/Beau | C1 phrases | yes | 34 | 33.4 | 1 | 1.9 | 0 | 0.3 | 0 | 0.1 |
| raw Vig/Beau | C2 words | no | 513 | 525.4 | 10 | 18.6 | 3 | 0.6 | 1 | 0.3 |
| raw Vig/Beau | C2 words | yes | 5 | 3.9 | 0 | 0.1 | 0 | 0.1 | 0 | 0.0 |
| raw Vig/Beau | C3 n-grams | no | 346 | 351.8 | 27 | 22.9 | 0 | 0.9 | 0 | 0.9 |
| raw Vig/Beau | C3 n-grams | yes | 0 | 0.3 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 |
| raw+skip | C1 phrases | no | 8409 | 8399.9 | 1803 | 1764.0 | 339 | 384.4 | 0 | 0.0 |
| raw+skip | C1 phrases | yes | 76 | 70.3 | 1 | 3.8 | 0 | 0.5 | 0 | 0.0 |
| raw+skip | C2 words | no | 827 | 828.2 | 19 | 25.6 | 5 | 3.4 | 0 | 0.0 |
| raw+skip | C2 words | yes | 6 | 5.2 | 0 | 0.1 | 0 | 0.1 | 0 | 0.0 |
| raw+skip | C3 n-grams | no | 686 | 675.1 | 64 | 52.6 | 7 | 6.5 | 0 | 0.0 |
| raw+skip | C3 n-grams | yes | 0 | 0.5 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 |

Reading: the largest positive deviations are z = +2.1 (raw+skip, C1, aligned, periodicity 5 vs null mean 4.2, F=0; the F=1 rerun of the same cell is -0.45), z = +1.5 (running-text, chain-GF29, C3, aligned, 2/50 nulls at least as high; F=1 +1.04, 1/20), and +1.4 (raw+skip C2). Over 125 cell-statistics, deviations of this size are the expected spread; none reproduces across the F=0 / F=1 variants. The tail counts (number of fragments with Z >= 4, Z >= 5, PER >= 5, DICT >= 10) match the null means within Poisson noise in every cell.

## 5. Distribution of the top 50 real running-text hits (pooled F=0 and F=1; fragment = key letters under the best shift/orientation)

| # | F | model | class | al | crib | pos (page+offset) | L | W | Z | cell null max / mean | key fragment (best shift/orient) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | chain-GF29 | C1 | n | THAT IS NOT WHO YOU ARE THAT IS ONLY WHAT YOU ARE CALLED | p30+94 | 42 | 39 | 10.34 | 11.99 / 10.08 | GNJNSTEFEEROADUPAEIUMYOLEGHISMILSIANTSITEREB |
| 2 | 1 | chain-GF29 | C1 | n | IF YOU WERE UNABLE TO COMPLETE THE TEST OR DID NOT RECEIVE A | p37+169 | 64 | 57 | 10.06 | 11.99 / 10.08 | ARSYTHGCNNONIAJANOSONIMCONAMETANTOOONAECRIESHYATH?THWAMOGALALOTHOTERJJ |
| 3 | 0 | chain-GF29 | C1 | n | A BOOK WHOSE STUDY IS FORBIDDEN | p3+119 | 26 | 23 | 10.05 | 12.15 / 10.25 | NTHADICATAPAIRTHECICILENTEUC |
| 4 | 1 | chain-GF29 | C1 | n | A BOOK WHOSE STUDY IS FORBIDDEN | p3+81 | 26 | 23 | 10.05 | 11.99 / 10.08 | NTHADICATAPAIRTHECICILENTEUC |
| 5 | 1 | chain-GF29 | C1 | n | EPIPHANY SEEKS THE DEVOTED | p27+14 | 22 | 19 | 9.98 | 11.99 / 10.08 | LOWISATHEROFTOCOUTRAGET |
| 6 | 0 | chain-GF29 | C1 | n | AND THE STUDENTS WERE ENLIGHTENED | p9+67 | 28 | 25 | 9.61 | 12.15 / 10.25 | TESRDEAMATRINEITSLATIANANNWOMA |
| 7 | 1 | raw+skip | C1 | n | WHO ARE YOU WHO WISHES TO STUDY HERE | p29+65 | 29 | 23 | 9.59 | 11.36 / 9.28 | LMININDHERRUNSENIBBRATHRCIMENT |
| 8 | 1 | chain-GF29 | C1 | n | BECAUSE YOU HAVE DEMONSTRATED THAT YOU CANT BE TRUSTED TO FO | p29+38 | 76 | 69 | 9.57 | 11.99 / 10.08 | XSGEECIFPMOWCYPEINGTHASOFSOEYHCJLTHYALFSATRUICTDS?UFTHNGWLSOOAEAEOXTHOOWSTHEUSAMARISU |
| 9 | 1 | chain-Z28 | C1 | n | THANK YOU FOR YOUR PARTICIPATION TO THIS POINT | p22+31 | 36 | 29 | 9.44 | 10.46 / 8.71 | TBUTITHECWIESPROFOOCCSOTHIESG?JFCFUTITH |
| 10 | 0 | chain-GF29 | C1 | n | WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK | p10+186 | 36 | 27 | 9.27 | 12.15 / 10.25 | WYNRINEUNFUSELONGPEENONEANETREREA?ASG?G |
| 11 | 1 | chain-GF29 | C1 | n | WE PRESERVE THINGS BECAUSE WE BELIEVE WE ARE WEAK | p10+101 | 36 | 27 | 9.27 | 11.99 / 10.08 | WYNRINEUNFUSELONGPEENONEANETREREA?ASG?G |
| 12 | 0 | raw+skip | C1 | n | AND THE STUDENTS WERE ENLIGHTENED | p40+162 | 28 | 23 | 9.24 | 11.36 / 9.41 | MTORSOFREWIPNALAMIGROUSAYTDTH |
| 13 | 1 | chain-GF29 | C1 | n | CARE FOR A SECOND CHANCE | p41+144 | 20 | 17 | 9.16 | 11.99 / 10.08 | OILETEROWNAWITHALTHEEX |
| 14 | 0 | chain-GF29 | C1 | n | RESPONSIBILITY FOR ATTACKS AGAINST PLANNED PARENTHOOD | p16+154 | 47 | 44 | 9.11 | 12.15 / 10.25 | OHIWTEANEWMEASARTEDOPADSATHCARSUNGFRNARSERONBOFROJIA |
| 15 | 0 | chain-GF29 | C1 | n | WE WILL CRYPTOGRAPHICALLY SIGN ALL MESSAGES WITH THIS KEY | p27+6 | 47 | 40 | 9.07 | 12.15 / 10.25 | PRTORUORO?JNEJECHBEGOFGEITMRADUTHEDANROTNOIFDUSD |
| 16 | 1 | raw Vig/Beau | C1 | n | WHO ARE YOU WHO WISHES TO STUDY HERE | p29+65 | 29 | 26 | 9.05 | 10.91 / 8.78 | LMININDHERRUNSENIBBRATHRCIMENT |
| 17 | 0 | chain-GF29 | C1 | n | SOME NEWS ORGANISATIONS HAVE RECENTLY CLAIMED THAT THREE THR | p21+82 | 59 | 56 | 9.00 | 12.15 / 10.25 | ELESNGDNGHFMLPFLSJXEAIALDESHEWASORYMPUENHORTWOMPBODIYHINITOFWJ |
| 18 | 0 | raw Vig/Beau | C1 | n | AND THE STUDENTS WERE ENLIGHTENED | p40+162 | 28 | 25 | 8.92 | 9.73 / 8.73 | MTORSOFREWIPNALAMIGROUSAYTDTH |
| 19 | 0 | chain-GF29 | C1 | n | IT IS NOT AN EASY TRIP BUT FOR THOSE WHO FIND THEIR WAY HERE | p44+146 | 61 | 51 | 8.87 | 12.15 / 10.25 | IBOECDE?CAE?MIAHUNGATIAUNOWUCNDMOTTENDOFWAEAEHHASSETHWERCIDAFUNCRONGTC |
| 20 | 0 | raw+skip | C1 | n | DO NOT EDIT OR CHANGE THIS BOOK | p17+204 | 23 | 17 | 8.86 | 11.36 / 9.41 | OTHANDTHEPUEJERTTHENSSECTN |
| 21 | 0 | chain-GF29 | C1 | n | FIND THE DIVINITY WITHIN AND EMERGE | p44+159 | 28 | 25 | 8.79 | 12.15 / 10.25 | EAEDMOTHENCOMENTSURMEAEAASISTHULEO |
| 22 | 1 | raw+skip | C1 | n | THE STUDENT TOLD THE MASTER HIS NAME | p11+62 | 28 | 24 | 8.79 | 11.36 / 9.28 | EOWNGRANSFERSHREBRSTORUEDEASILA |
| 23 | 0 | chain-GF29 | C1 | n | DURING A LESSON THE MASTER EXPLAINED THE I | p5+211 | 31 | 28 | 8.78 | 12.15 / 10.25 | WNGAECHWERISELFBYYESDRURDISLEARMIG |
| 24 | 1 | chain-GF29 | C1 | n | DURING A LESSON THE MASTER EXPLAINED THE I | p5+155 | 31 | 28 | 8.78 | 11.99 / 10.08 | WNGAECHWERISELFBYYESDRURDISLEARMIG |
| 25 | 1 | chain-GF29 | C1 | n | HOW MANY LINES OF THE CODE REMAINED WHEN THE MABINOGION PAUS | p35+17 | 49 | 46 | 8.73 | 11.99 / 10.08 | THXHWDAURONCAMCCSEINGANORADARCHSIETHESSAENEULGWOEWSEE |
| 26 | 0 | chain-GF29 | C1 | n | WE ARE NOT ASSOCIATED WITH THIS INDIVIDUAL | p45+82 | 32 | 27 | 8.71 | 12.15 / 10.25 | EA?RDCORDGLODIDLITECCYOURTHAELANTATH |
| 27 | 0 | chain-GF29 | C1 | n | GO THAT FAR IN FROM THE BEGINNING AND FIND MY FIRST NAME | p10+97 | 41 | 38 | 8.69 | 12.15 / 10.25 | JOEGMNGRTHELOTHELSESSMILIETIUILGECDHARINFTFEM |
| 28 | 0 | chain-GF29 | C1 | n | PLEASE PASTE THE MAGIC SQUARES INTO THE APPROPRIATE TEXTAREA | p21+44 | 52 | 38 | 8.69 | 12.15 / 10.25 | EOB?OECEELCIUELITUUMBWYMYANGEAOEPS?TMYALLECAESCONSS?NTEREM |
| 29 | 1 | chain-GF29 | C1 | n | GO THAT FAR IN FROM THE BEGINNING AND FIND MY FIRST NAME | p10+16 | 41 | 38 | 8.69 | 11.99 / 10.08 | JOEGMNGRTHELOTHELSESSMILIETIUILGECDHARINFTFUA |
| 30 | 1 | chain-GF29 | C1 | n | A POEM OF FADING DEATH NAMED FOR A KING | p31+132 | 24 | 17 | 8.65 | 11.99 / 10.08 | UEHISECRISW?NGRTACCORSTHEH |
| 31 | 1 | raw Vig/Beau | C1 | n | THE STUDENT TOLD THE MASTER HIS NAME | p11+62 | 28 | 25 | 8.60 | 10.91 / 8.78 | EOWNGRANSFERSHREBRSTORUEDEASILA |
| 32 | 1 | raw+skip | C1 | n | STOP MAKING IT MORE DIFFICULT THAN IT IS | p47+122 | 30 | 24 | 8.59 | 11.36 / 9.28 | LGETERAFOEMPRSETSOSISISEDOLFAPN |
| 33 | 0 | chain-GF29 | C1 | n | YOU HAVE DONE WELL TO COME THIS FAR | p36+89 | 27 | 24 | 8.56 | 12.15 / 10.25 | GYOMIANEXWEREHARMTHEDOCEIMILI |
| 34 | 1 | chain-GF29 | C1 | n | YOU HAVE DONE WELL TO COME THIS FAR | p35+50 | 27 | 24 | 8.56 | 11.99 / 10.08 | NYOMIANEXWEREHARMTHEDOCEIMILI |
| 35 | 0 | raw+skip | C1 | n | TO BE READ ONCE AND THEN DESTROYED | p40+96 | 25 | 19 | 8.47 | 11.36 / 9.41 | MELLUTONOCUOUSICATEBEAICSS |
| 36 | 1 | raw+skip | C1 | n | TO BE READ ONCE AND THEN DESTROYED | p39+6 | 25 | 19 | 8.47 | 11.36 / 9.28 | MELLUTONOCUOUSICATEBEAICSS |
| 37 | 0 | chain-GF29 | C1 | n | THUS OUR MONTH LONG JOURNEY ENDS | p8+152 | 24 | 20 | 8.46 | 12.15 / 10.25 | ?NGRALCOMRATSORCENUTSOCRI |
| 38 | 1 | chain-GF29 | C1 | n | WE DO NOT ENGAGE IN ILLEGAL ACTIVITIES WE ARE NOT ASSOCIATED | p41+223 | 47 | 38 | 8.46 | 11.99 / 10.08 | BTUBDLJTHEBERHUSFANARALTOTDOEOYJJO?YNDHISFREECIA?M |
| 39 | 0 | chain-GF29 | C1 | n | IF YOU WERE UNABLE TO COMPLETE THE TEST | p5+25 | 31 | 28 | 8.46 | 12.15 / 10.25 | ATPSEWHIUEHITHWROOCOURSUMUTDIDFA |
| 40 | 1 | chain-GF29 | C1 | n | NAMED FOR A KING MEANT TO BE READ ONLY ONCE AND VANISH ALAS | p39+216 | 42 | 27 | 8.43 | 11.99 / 10.08 | DDOANUTINYES?EOOEBIAPTHAE?IATHSEDHEP?ILEMEFINDMOT |
| 41 | 1 | chain-GF29 | C1 | n | NEVER BECOME ATTACHED TO WHAT YOU OWN | p25+139 | 30 | 20 | 8.43 | 11.99 / 10.08 | LHISPRF?ES?OONEDDOFAPEREASTROIX |
| 42 | 0 | chain-GF29 | C1 | n | THERE IS NOTHING TO BE RIGHT ABOUT TO BELONG IS DEATH | p17+211 | 36 | 31 | 8.41 | 12.15 / 10.25 | UAXTSNMOTICADOFTOTEPUEHITHASNDEDHIC?EO |
| 43 | 0 | chain-GF29 | C1 | n | CHECK BACK ON THE FIFTH OF JANUARY TWO THOUSAND SEVENTEEN AT | p40+107 | 86 | 79 | 8.40 | 12.15 / 10.25 | NHMEORHIGNGFEPWIHGIDERNAWIMEARNRIXEASEAPYAXEBTHIAEANGATHOUERRANMONYBDHADRDASTTH?CEOCWSLTHYSICTTITHES |
| 44 | 0 | chain-GF29 | C1 | n | I AM A CONSCIOUSNESS INHABITING AN ARBITRARY BODY | p1+163 | 38 | 31 | 8.40 | 12.15 / 10.25 | GMUOICEUELUSESJGMITABILEWWEEWHS?EMHAMW |
| 45 | 0 | chain-GF29 | C1 | n | DURING A LESSON THE MASTER EXPLAINED THE I | p47+70 | 31 | 24 | 8.40 | 12.15 / 10.25 | NOHOUNDEFTHEMENSTIMBUBAMFRN?CTYR |
| 46 | 1 | chain-GF29 | C1 | n | DURING A LESSON THE MASTER EXPLAINED THE I | p45+199 | 31 | 24 | 8.40 | 11.99 / 10.08 | NOHOUNDEFTHEMENSTIMBUBAMFRN?CTYR |
| 47 | 1 | raw+skip | C1 | n | WE WILL CRYPTOGRAPHICALLY SIGN ALL MESSAGES WITH THIS KEY | p39+153 | 47 | 41 | 8.37 | 11.36 / 9.28 | RIAEDTHWBROUSAULIINFDCNAASONGASHTHONOEBESTWERCIFEJR |
| 48 | 1 | chain-GF29 | C1 | n | THE TOTIENT FUNCTION IS SACRED | p35+90 | 24 | 21 | 8.36 | 11.99 / 10.08 | THSUTHTHANISITEDAYEANDRTHERPR |
| 49 | 1 | raw+skip | C1 | n | NAME NUMBER OR SYMBOLISM | p15+107 | 21 | 17 | 8.36 | 11.36 / 9.28 | OEISABSCOLOFTOSESEMONC |
| 50 | 1 | raw+skip | C1 | n | POST THE THREE MAGIC SQUARES AND THE URL TO YOUR TOR HIDDEN  | p12+31 | 56 | 50 | 8.33 | 11.36 / 9.28 | NDNLENTACAWILLERPGTWEOMOYATIEYCISEEARITHEATHUSEXNGYPUGEYOUWEOEAO |

Distribution of the 50: model {'chain-GF29': 36, 'raw+skip': 10, 'chain-Z28': 1, 'raw Vig/Beau': 3}; class {'C1': 50}; aligned {0: 50}; F-variant {1: 27, 0: 23}; L median 31 (range 20-86); distinct pages 27; hits exceeding their own cell null max: 0; exceeding null mean+3sd-equivalent: n/a
Among all 3200 listed real hits (top-100/thread/model lists), those exceeding their own cell's null max (over 50 or 20 shuffles): 0

All 50 are unaligned C1 long phrases (L 20-86): the heavy Z tail simply grows with fragment length W, and every one is below the null maximum of its own cell (hits exceeding their cell's null max: 0 of 3,200 listed). The fragments are the usual best-of-58 pseudo-English ("TH", "ER", "ING" runs) of random keys, not text: the corpus search finds no 12-rune match for any of them. The top keyword (dictionary) hits are single long-fragment coincidences (e.g. 12 letters ROYALISATIAN for the THE MASTER STOPPED THE STUDENT AND SAID fragment; null max 13). The strongest periodicity is PER = 7 (GF, "SSAESSAESSAES" period 4 for IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE at p44+62, reproduced as p42+224 on the F-deleted stream; null max 8, 28/50 shuffles at least 7).

## 6. Anything beating null

Nothing. Corpus search of all 23,475 dumped real fragments (Z >= 5, DICT >= 11 or PER >= 7; both F variants): 0 matches (control finds its key; random baseline 0/2000). No crib was extended and no plaintext was submitted to `verify_solution.py --plaintext`.

## 7. Verdict per family

| family | verdict |
|---|---|
| chain-Z28, running English / Cicada text key (word-aligned and unaligned, F and F-deleted) | no signal; real max inside null in all 12 cells; control detects at L >= 12 |
| chain-GF29 (28 offsets), running text | same; Z up to 10.0 (C1 unaligned) vs null mean 10.3, max 12.2 |
| raw Vigenere/Beaufort running text, with and without one skip | same |
| keyword key (dictionary windows / exact periodicity), all models | real max inside null in every cell (DICT 12 vs null max 13; PER 7 vs null max 8); positive control recovers DIVINITY |
| what this does NOT test | keys that enter through a non-additive bijection (the discrete-log sigmas of lanes J/K), keys scaled or permuted before use, plaintext that is not the literal Cicada-transliterated English cribs, and the free Oosterhof walk (a short crib does not open it, per the addendum). The 4% prefilter and the absence of the dictionary signature on chain-GF29 unaligned are the engine limits to keep in mind. |
