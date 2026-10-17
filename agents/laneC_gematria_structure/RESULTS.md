# RESULTS: laneC_gematria_structure

Lane: Gematria numbers of the book's own text as chain-cipher keystreams (Goal 1) and the 2-rune-word anomaly (Goal 2).
All code and raw logs are in this directory (SCRATCH/agents/laneC_gematria_structure/). Data pin: sha256 matched (12,956 runes, 2,896 words, 55 pages).

## Verdict in one paragraph

Goal 1: every keystream family built from Gematria numbers of the book's own text is null at the size-matched noise floor: solved-page word sums, per-letter prime values of solved plaintext and solved ciphertext, running totals, totients, prime-counting indices, unsolved-book structure (word/line/page lengths and sums, doublet positions and gaps), self-keying by ciphertext primes/word sums, and plaintext autokey by prime value / word sum / running total with brute-forced seeds. Each sub-family was first validated with a planted positive control that the identical search recovers at the planted offset (IoC about 1.76, z of 145 to 1255). A model-free test (below) additionally excludes, for the chain model, ANY keystream that is a function of the large set of observables I could compute (previous ciphertext runes, previous word's sum, running totals, position in word, page, line...). Goal 2: the 2-rune deficit is uniform over all 55 pages (permutation p = 0.92) and all 9 sections, so it is not a page-level or section-level artifact; it is matched best by English with THE/OF/TO absent (JS 0.0009, vs 0.0085 for Cicada's own solved pages), with letter-by-letter spelling (no digraph runes) a weaker second (JS 0.0018-0.0037). Word-length data alone cannot separate those two. Word-initial/final runes and increments are flat. Latin and Old English are rejected (JS 0.035-0.058). No candidate solve; the oracle was not invoked (nothing to submit).

## Method (common to all Goal 1 searches)

Chain decode on increments D_i = (c_i - c_{i-1}) mod 29 over the flat 12,955-increment stream (page boundaries ignored, matching the brief). For key k_i:
- additive: D_i != 0 -> x = (D_i - 1 -/+ k_i) mod 28; D_i = 0 -> EA symbol. Score = normalised IoC of the output symbols (invariant under the unknown bijection sigma).
- GF(29) multiplicative: x = D_i * k_i^(+1/-1) mod 29 (k_i = 0 mod 29 positions dropped); EA = 0.
- Raw control: c_i -/+ k_i mod 29 on raw runes (excluded by theory, run as a control).
- Key reductions tried: v mod 28 and v mod 29 (the latter used as an integer in Z28 for additive, as a field element for multiplicative).
- Key-consumption conventions: A (a zero increment does not consume a key element) and B (it does). Key modes: continuous over the corpus, and restart at every page; per-word keys (one key value per ciphertext word, constant within the word; continuous or restart per page); and per-letter keys; word values also expanded per letter ("Wx").
- Directions: key sequence forward and reversed. Offsets 0..500 (cyclic wrap for plain sequences; for cumulative sequences the sequence is tiled and the running total restarts at the offset). Self-keyed/unsolved-structure sequences: offsets -500..+500 (negative = earlier elements, i.e. causal self-keying with lag).
- Null: 20 chain-consistent shuffles (the 12,955 increments permuted, c rebuilt by cumulative sum, so doublet count, flatness and word/line/page structure are preserved; self-keyed keys recomputed from the shuffled ciphertext). The identical search is run on each. Per spec, trials are scored z = (IoC - median)/MAD over offsets; the group statistic is the max z over all its specs/offsets. Real max is compared to the null distribution of the same max.
- Solved-text sources: LP1 solved pages 01, 03-04, 05, 06-09, 10-13, 14-15, 16, 73(AN END), 74 re-decrypted by me (F-interrupts resolved by beam search + quadgrams; scores -4.1 to -4.7 per quadgram): 695 words, 2,795 runes of plaintext and the same of solved ciphertext.

## Positive controls (run BEFORE the real runs)

English (Moby-Dick through Cicada transliteration rules, 12,956 runes, real page sizes) chain-encrypted with a random sigma and a key taken from a member of the family, then the FULL spec list of the family run on it (so recovery is against the whole search space, not just the right spec).

Solved-number families (2,112 specs x 501 offsets; /ctrl_solved.json): all 8 planted keys recovered at the exact planted offset:
- PT letter primes, rev0, rune-cont convA, mod28, o=431: z=460, IoC 1.79
- CT letter index, rev1, rune-page convB, mod29, o=450: z=547, IoC 1.76
- PT word sums, per-word key (changes per word, constant in word), continuous, o=300: z=899, IoC 1.77
- CT word totients expanded, GF(29) mult, o=350: z=863, IoC 1.76
- PT word cumulative sums (running total), mult, convA, o=400: z=1225, IoC 1.79
- CT letter cumulative primes, page-restart, o=440: z=419, IoC 1.76
- PT word pi(sum) per-word page-restart, mult, reversed, o=200: z=145, IoC 1.76
- raw-shift control on PT indices, o=500: z=508, IoC 1.77

Self/structure families (/ctrl_self.json): recovered at the planted offset, IoC about 1.76: position-in-word (z=224), line length with GF(29) (z=387), doublet gaps (z=290), ciphertext prime lag 3 (z=1015, online/self-keyed encryption), running total of ciphertext primes lag 1 (z=1256), previous-word ciphertext sum GF(29) lag 1 and 2 (z=921, 978), raw shift keyed by ciphertext prime at lag 7 (z=1222). One plant (page ciphertext sums at own-page offset) is non-causal and cannot be encrypted online; it was not recovered and is excluded from the control claim.

Autokey family (/ctrl_auto.json): continuous-mode plants (letter lag1 prime, lag3 prime, previous-word totient sum, mult lag1) recovered, mean z 1175/1175/1176/108 with IoC 1.73; page-restart plants (lag2 by index, running total) recovered with mean page z about 22 (best per-page IoC about 2.05) and were also picked up by the continuous variant (self-synchronising enough).

Positive control for "key constant within a unit" (const_units.py): English, chain cipher, key random per unit: within-unit increment coincidence word 0.0440, line 0.0574, sentence 0.0600, chapter 0.0618, page 0.0613 (flat = 0.0357).

## Goal 1 results

### 1a. Constant-within-word (per-word key) and other unit-constant keys: explicitly excluded

Real unsolved data, pooled within-unit coincidence of nonzero increments (flat 0.03571; null from 100 shuffles):

```
REAL data: pooled within-unit coincidence of nonzero increments (flat = 1/28 = 0.03571)
  word      units= 2896 pairs=     59762 rate=0.03598  null 0.03570+-0.00104  z=+0.26
  line      units=  594 pairs=    269950 rate=0.03577  null 0.03575+-0.00052  z=+0.03
  sentence  units=  175 pairs=   1701384 rate=0.03622  null 0.03573+-0.00018  z=+2.74
  chapter   units=   17 pairs=  18791740 rate=0.03580  null 0.03575+-0.00005  z=+0.93
  page      units=   55 pairs=   3155412 rate=0.03582  null 0.03575+-0.00014  z=+0.55
  within-word lag-1 D coincidence: 0.0356 (n=9929; flat 0.0357, SE 0.0019)
  within-word lag-2 D coincidence: 0.0341 (n=7145; flat 0.0357, SE 0.0022)
  within-word lag-3 D coincidence: 0.0365 (n=4820; flat 0.0357, SE 0.0027)
```
Word-constant key: real 0.03598 +- 0.00104 vs 0.0440 expected from the positive control (7.3 sd below the keyed prediction; the real value sits at +0.26 sd of the random null). My earlier-measured 0.0355 is confirmed. So a key that is constant within each word is excluded in the fixed-sigma chain model, whatever the per-word values are (word sums included). Line/page/chapter constants are excluded far harder (control 0.057-0.062 vs real 0.0357-0.0358). One un-replicated blip: sentence units give 0.03622 (z=+2.74; both halves of the book give 0.0362); the effect is 0.0005 vs the 0.024 that a sentence-constant key would produce, and I count it as one of ~150 statistics in this lane, not a lead. The lag-1..60 increment coincidence profile is flat (mean z -0.01).

### 1b. Model-free exclusion: key = ANY function of an observable (condtest.py)

If k_i = g(V_i) for any g and observable V, then D | V = v is a shifted English letter distribution and the pooled within-group coincidence rises from 0.0357 to about 0.062-0.08. Controls (cond_ctrl.py, planted random g over V): c[i-1] 0.0639, (c[i-1],c[i-2]) 0.0645, previous-word cipher sum mod 29 0.0620, cumulative prime sum mod 28 0.0622, partial word sum mod 29 0.0661, position in word 0.0799, page 0.0621, previous-word cipher sum exact 0.0613. Real data (40-shuffle null):

```
observable V                                          groups     pairs    rate |  null mu  null sd       z
c[i-1]                                                    29   5709754 0.03580 |  0.03574  0.00011    0.53
c[i-2]                                                    29   5708950 0.03568 |  0.03576  0.00012   -0.71
(c[i-1],c[i-2])                                          840    201946 0.03542 |  0.03567  0.00064   -0.40
(c[i-1..i-3])                                           9945      7078 0.03645 |  0.03585  0.00264    0.23
D[i-1]                                                    29   5848044 0.03562 |  0.03577  0.00011   -1.41
(D[i-1],D[i-2])                                          837    205754 0.03547 |  0.03583  0.00066   -0.54
c[i+1] (non-causal)                                       29   5709168 0.03569 |  0.03573  0.00010   -0.39
prev word cipher-sum (exact)                             586    450880 0.03581 |  0.03583  0.00036   -0.05
prev word cipher-sum mod 28                               28   5955968 0.03600 |  0.03576  0.00010    2.32
prev word cipher-sum mod 29                               29   5762722 0.03582 |  0.03574  0.00010    0.76
prev word length                                          14  24433722 0.03572 |  0.03574  0.00004   -0.45
(prev word len, pos in word)                             158   3927458 0.03570 |  0.03575  0.00012   -0.42
pos in word                                               14  26650222 0.03579 |  0.03575  0.00006    0.61
(pos in word, word length)                               105   4453858 0.03561 |  0.03575  0.00014   -0.98
current word cipher-sum (exact; includes c[i])           586    368188 0.03646 |  0.03654  0.00038   -0.21
current word cipher-sum mod 28                            28   5966414 0.03578 |  0.03583  0.00011   -0.41
current word cipher-sum mod 29                            29   5748892 0.03587 |  0.03579  0.00009    0.94
cum prime sum thru i-1 mod 28                             28   5909754 0.03572 |  0.03576  0.00010   -0.47
cum prime sum thru i-1 mod 29                             29   5704200 0.03570 |  0.03575  0.00010   -0.48
cum prime sum thru i-1 mod 58                             58   2851188 0.03569 |  0.03575  0.00015   -0.45
cum rune-index sum thru i-1 mod 28                        28   5913758 0.03590 |  0.03579  0.00012    0.91
cum rune-index sum thru i-1 mod 29                        29   5706968 0.03581 |  0.03579  0.00011    0.19
partial word sum before i mod 28                          28  13769692 0.03581 |  0.03577  0.00008    0.53
partial word sum before i mod 29                          29  13622206 0.03587 |  0.03577  0.00008    1.15
partial word sum before i (exact)                        596   8727530 0.03582 |  0.03578  0.00011    0.37
page                                                      55   3155412 0.03582 |  0.03576  0.00015    0.42
line                                                     594    269950 0.03577 |  0.03575  0.00047    0.05
word index in page                                        70   2757008 0.03550 |  0.03577  0.00016   -1.64
word index global (exact)                               2896     59762 0.03598 |  0.03604  0.00102   -0.07
(prev word sum mod 29, pos in word)                      348    917864 0.03627 |  0.03570  0.00027    2.12
```
All 30 observables sit at the null (max |z| 2.3, two values near 2.1-2.3 out of 30, consistent with chance). This kills, in one stroke, every self-keyed function of: the last 1-3 ciphertext runes, the last 1-2 increments, the previous word's gematria sum (exact, mod 28, mod 29, hence also its totient, prime index etc.), the current word's sum, running totals of ciphertext primes or indices (mod 28/29/58), the partial word sum, position and word length, page, line, global word index. Note it needs enough samples per group: 3-rune context (9,945 groups, ~7,000 pairs) has little power (control not run at that size), so only context up to 2 runes is solidly excluded.

### 1c. Scanned keystream families, real vs 20 shuffled nulls

Trial counts: solved-number family 2,112 spec-forms x ~501 offsets = 1,058,112 offset trials per run; self/structure family 444 spec-forms x 1,001 offsets = 398,424 per run; autokey 204 variants x 2 restart modes, 337,212 seed brute-force decodes per segment set (lag-3 uses all 29^3 seeds). Each run was repeated on 20 shuffles.

Family-wide maxima (real vs null max over the family):
- solved numbers (a,b,c): real max z 7.27; null max z mean 7.67, sd 0.59, max 8.99. Real does not exceed the null.
- self / structure (d): real max z 42.94 (the lag +-1 raw-shift entry, which is just D itself with its doublet deficit; same in the nulls: 42.17 +- 1.86); excluding that artifact, real 5.92 vs nulls (see table).
- autokey (e): real max mean-z 4.05; null max 4.14 +- 0.36, max 5.40.

Per-group tables (group = sequence name and word/letter level; z = max over its specs; columns: real z, real best IoC, null mean / sd / max of the group maximum, and how many null-sd the real is above the null mean). Top 25 of each family by sd-above:

```
=== family self: 39 groups, 20 null runs ===
family-wide max z: real 42.94 | null max-z: mean 42.17 sd 1.86 max 44.93  => real-minus-null-mean in sd = 0.42 ; real beats null max: False
group                                            real z   real IoC |  nullmu  nullsd nullmax | sd-above
SELF:r.pos_in_page                                 5.26     1.0250 |    4.30    0.54    5.96 |   1.77
SELF:w.pi                                          5.57     1.0265 |    4.63    0.67    5.80 |   1.40
SELF:r.pos_in_line                                 5.20     1.0266 |    4.48    0.51    5.59 |   1.40
SELF:dbl.pos_cyc                                   5.92     1.0257 |    4.56    1.10    8.32 |   1.24
SELF:r.index                                       5.40     1.0265 |    4.89    0.43    5.53 |   1.19
SELF:l.cumsum                                      4.92     1.0271 |    4.09    0.71    5.61 |   1.18
SELF:l.id                                          4.36     1.0275 |    3.93    0.67    5.12 |   0.64
SELF:w.in_page                                     4.86     1.0256 |    4.50    0.61    5.49 |   0.58
RAW-SELF:r.index                                  42.94     1.0244 |   42.17    1.86   44.93 |   0.42
SELF:w.len                                         4.72     1.0261 |    4.48    0.74    6.19 |   0.32
SELF:dbl.gap_cyc                                   4.68     1.0256 |    4.45    0.77    6.42 |   0.30
RAW-SELF:r.wordsum_cur                             4.85     1.0026 |    4.70    0.57    5.89 |   0.26
RAW-SELF:r.wordlen                                 4.84     1.0031 |    4.70    0.70    6.09 |   0.19
SELF:p.len                                         3.73     1.0256 |    3.59    0.84    5.10 |   0.17
SELF:w.idxsum                                      4.86     1.0262 |    4.74    0.69    6.23 |   0.17
SELF:w.sum                                         4.59     1.0263 |    4.52    0.53    5.41 |   0.12
SELF:w.first                                       4.84     1.0263 |    4.77    0.58    5.75 |   0.11
SELF:l.sum                                         4.16     1.0268 |    4.14    0.68    5.18 |   0.03
SELF:p.sum                                         3.29     1.0249 |    3.28    0.67    4.53 |   0.01
SELF:w.cumlen                                      4.60     1.0266 |    4.68    0.68    6.29 |  -0.12
SELF:dbl.count_gap                                 3.53     1.0254 |    3.60    0.55    4.70 |  -0.12
RAW-SELF:r.prime                                   4.75     1.0027 |    4.82    0.43    5.51 |  -0.15
SELF:dbl.count_pos                                 3.60     1.0261 |    3.70    0.62    4.72 |  -0.16
SELF:w.last                                        4.55     1.0261 |    4.66    0.62    6.26 |  -0.17
SELF:l.len                                         3.82     1.0279 |    3.93    0.65    5.06 |  -0.18

=== family solved: 60 groups, 20 null runs ===
family-wide max z: real 7.27 | null max-z: mean 7.67 sd 0.59 max 8.99  => real-minus-null-mean in sd = -0.68 ; real beats null max: False
group                                            real z   real IoC |  nullmu  nullsd nullmax | sd-above
PT.W.sum [Wx]                                      7.27     1.0274 |    5.78    0.54    6.92 |   2.74
PT.L.prime [L]                                     6.87     1.0267 |    5.92    0.39    7.11 |   2.44
PT.L.totient [L]                                   6.87     1.0267 |    5.82    0.44    6.73 |   2.40
CT.W.idxsum [Wx]                                   6.61     1.0266 |    5.71    0.40    6.54 |   2.27
PT.W.last [W]                                      6.11     1.0281 |    5.18    0.42    6.24 |   2.25
PT.W.totient [W]                                   6.34     1.0268 |    5.43    0.41    6.70 |   2.23
PT.W.sumtot1 [Wx]                                  7.27     1.0274 |    5.97    0.59    7.40 |   2.20
PT.W.idxsum [Wx]                                   6.96     1.0274 |    5.86    0.55    7.30 |   1.99
CT.W.last [W]                                      5.74     1.0267 |    5.18    0.28    5.64 |   1.96
CT.L.cumprime [L]                                  6.39     1.0263 |    5.63    0.43    6.97 |   1.77
CT.W.first [W]                                     5.99     1.0263 |    5.28    0.52    6.26 |   1.35
PT.W.last [Wx]                                     6.11     1.0394 |    5.55    0.46    6.32 |   1.20
CT.W.cumsum [W]                                    5.96     1.0264 |    5.48    0.46    6.29 |   1.05
CT.W.pi [Wx]                                       6.05     1.0395 |    5.65    0.45    6.67 |   0.88
PT.W.pi [Wx]                                       6.45     1.0273 |    5.82    0.82    7.88 |   0.77
PT.W.primeidx [W]                                  6.05     1.0264 |    5.63    0.56    7.00 |   0.76
CT.W.cumtot [Wx]                                   6.31     1.0267 |    5.87    0.70    7.84 |   0.64
CT.W.primeidx [W]                                  5.49     1.0262 |    5.36    0.43    6.37 |   0.30
RAW shift control: CT.L.index                      5.25     1.0030 |    5.06    0.75    6.64 |   0.25
PT.W.idxsum [W]                                    5.66     1.0263 |    5.56    0.55    6.40 |   0.18
PT.W.len [W]                                       5.43     1.0263 |    5.39    0.63    7.16 |   0.06
CT.W.len [W]                                       5.43     1.0263 |    5.39    0.63    7.16 |   0.06
PT.W.cumtot [W]                                    5.48     1.0260 |    5.48    0.54    6.43 |   0.01
CT.W.totient [Wx]                                  5.94     1.0389 |    5.94    0.54    6.96 |   0.00
RAW shift control: PT.L.prime                      4.83     1.0026 |    4.85    0.59    6.34 |  -0.03
```
Autokey (e) groups (the "real IoC" column here is the max single-page z):

```
=== family auto: 10 groups, 20 null runs ===
family-wide max z: real 4.05 | null max-z: mean 4.14 sd 0.36 max 5.40  => real-minus-null-mean in sd = -0.26 ; real beats null max: False
group                                            real z   real IoC |  nullmu  nullsd nullmax | sd-above
LET lag1 / restart=cont                            3.49     3.4926 |    2.43    0.65    4.26 |   1.63
LET lag1 / restart=page                            2.81     3.4297 |    2.23    0.48    3.05 |   1.22
CUMSUM / restart=cont                              3.67     3.6731 |    3.24    0.65    5.40 |   0.66
WORDSUM / restart=cont                             3.17     3.1662 |    2.84    0.56    4.09 |   0.59
LET lag3 / restart=page                            4.05     7.0278 |    4.00    0.12    4.22 |   0.45
WORDSUM / restart=page                             1.67     5.1779 |    1.64    0.07    1.78 |   0.37
LET lag3 / restart=cont                            2.01     2.0102 |    2.30    0.89    4.86 |  -0.33
CUMSUM / restart=page                              2.19     4.3559 |    2.21    0.07    2.38 |  -0.38
LET lag2 / restart=cont                            2.09     2.0917 |    2.47    0.62    3.65 |  -0.62
LET lag2 / restart=page                            2.62     5.6575 |    2.69    0.09    2.89 |  -0.79
```
Largest real-minus-null margin anywhere: PT.W.sum expanded, 2.74 sd (a family of 60 groups: 2.7 sd is expected by chance for the best of 60; null max for that group 6.92 vs real 7.27 i.e. within range of other nulls). Best raw IoC at the real best hit is 1.027 (flat is 1.023 with doublet deficit). None clears the null max in any family-wide sense, none produces readable text, so no candidate plaintext and nothing to submit to the oracle.

### 1d. Verdicts per sub-family

| sub-family | verdict |
|---|---|
| (a) per-word gematria sums of solved words as key (PT and CT, sum, totient of sum, pi(sum), prime of sum mod 29, sum of indices, first/last letter, length; per-word; continuous and page-restart; both directions; additive and GF(29)) | NULL; also excluded structurally by the word-constant test (7.3 sd) |
| (b) per-letter prime values / totient / index of solved plaintext and solved ciphertext, offsets 0..500, both directions, conv A and B, page-restart | NULL |
| (c) running totals mod 28/29, totients of word sums, prime-index reductions | NULL |
| (d) unsolved-book structure and ciphertext-derived self-keys (word/line/page lengths and sums, cumulative sums, pos in word/line/page, doublet positions and gaps, ciphertext prime/index at lag -500..+500, previous-word ciphertext sums) | NULL; plus model-free exclusion for any function of the listed observables |
| (e) plaintext autokey by prime value / index (lags 1-3, 6 g-tables, both signs, identity and reversed letter map, additive and multiplicative, all seeds) and by previous plaintext word's sum (6 h-tables) and running total of decoded primes | NULL |
| raw-rune shift control (mod 29) with the same sequences | NULL (as theory requires) |

## Goal 2: the 2-rune-word anomaly

Raw numbers (goal2_wl.log, goal2_b.log, goal2_c.log): unsolved 2,896 words (global word ids; the earlier 2,928 figure was per-page counting, probably words split across pages counted twice), mean 4.47 runes; share of 1/2/3/4/5/6/7/8/9/10/11+ rune words = 2.9/15.5/24.9/17.7/10.9/8.8/7.5/5.4/2.7/1.8/2.0 %.

(i) Uniformity: the 2-rune share by page runs 0.0 to 0.29 but heterogeneity is exactly what small pages give: chi-square 43.1 on 54 df, permutation p = 0.92 (null mean 56.1, sd 9.8). The five pages at or above 0.22 (pp 1, 33, 43, 49, 54) are 63, 53, 59, 18 and 17 words, inside the binomial range (0.057-0.260 for 50 words). By section (Leo's 9): 2-rune share 0.177, 0.125, 0.146, 0.169, 0.147, 0.156, 0.164, 0.149, (0.294 on 17 words) with 3-rune share 0.23-0.27: uniform. So there are no English-normal pages; the deficit is global and homogeneous.

(ii) Hypotheses against the unsolved profile (JS divergence, Monte-Carlo p from 2,896-word multinomial samples; noise floor of JS about 0.0004; the best reachable p is limited by genre differences between my corpora):

| hypothesis | best corpus | JS | f2 | f3 | mean |
|---|---|---|---|---|---|
| Cicada rules (digraphs merged, ING->NG, IO->IA), all words | Moby Dick | 0.0076 | 0.236 | 0.207 | 4.11 |
| ... minus THE | Agrippa | 0.0023 | 0.195 | 0.223 | 4.37 |
| ... minus THE/OF/TO | Emerson / Plato | 0.0009 (p=0.03) | 0.156 | 0.253 | 4.43 |
| ... minus THE/OF/TO/AND | Cicero (Engl. transl.) | 0.0012 | 0.159 | 0.229 | 4.50 |
| letter-by-letter (no digraph runes at all) | Moby Dick | 0.0019 | 0.166 | 0.222 | 4.38 |
| letter-by-letter, minus THE | Emerson | 0.0056 | 0.214 | 0.185 | 4.44 |
| TH-only merged, all words | Moby Dick | 0.0067 | 0.232 | 0.197 | 4.24 |
| TH-only merged, minus THE/OF/TO | Emerson | 0.0012 | 0.154 | 0.240 | 4.55 |
| Cicada's own 695 solved words, as is | | 0.0085 | 0.240 | 0.243 | |
| Cicada's own solved words minus THE/OF/TO (6.6% THE, 1.3% OF, 3.3% TO) | | 0.0030 | 0.144 | 0.274 | |

Unsolved: f2 0.155, f3 0.249, mean 4.47. Reading: the deficit is almost exactly the weight of THE (about 6.6% of tokens, always exactly 2 runes as TH+E) plus OF and TO. Removing THE/OF/TO reproduces the whole profile (f2, f3 and mean together) in every English prose corpus I tried (Plato, Emerson, Cicero/Suetonius translations: JS 0.0009-0.0029 against a 0.0085 for the unmodified Cicada solved text). The alternative that the plaintext is spelled letter-by-letter (T-H-E, three runes) also lands near (JS 0.0018 Moby Dick, 0.0026 Emerson, 0.0037 Plato) because it moves THE into the 3-rune bin. The lengths cannot decide between "no THE/OF/TO" (a style or constraint on the text: very archaic/odd register, or a deliberate lipogram-like text) and "no digraph merging" (a different transliteration for the unsolved part); merging only TH while removing function words is also acceptable (JS 0.0012). Both hypotheses make the same prediction for flat, key-masked ciphertext, so the ciphertext cannot test them; they predict different plaintext (no THE at all, vs TH as two letters). A practical crib consequence: if the text contains no THE/OF/TO, the usual THE-based cribs are useless; if it is letter-by-letter, the cipher alphabet carries 26 letters (+ rare ones) and the zero-increment letter would be one of the 0.66% letters (K at 0.77% in English letters is the natural candidate), which is a change from EA.

(iii) Positional uniformity (goal2_c.log). Increments D and raw runes by within-word position (chi-square vs flat, df 27/28):

```
--- increments D (nonzero) by within-word position (flat expected; chi2 df=27)
word-initial (first rune of word)  n= 2872 chi2=  33.1 df=27 z=+0.84
word-final                         n= 2877 chi2=  23.6 df=27 z=-0.47
second rune                        n= 2801 chi2=  25.3 df=27 z=-0.24
third rune                         n= 2344 chi2=  44.4 df=27 z=+2.37
all other                          n= 7203 chi2=  41.7 df=27 z=+1.99
--- raw ciphertext runes by position (chi2 df=28)
word-initial                       n= 2895 chi2=  23.2 df=28 z=-0.64
word-final                         n= 2896 chi2=  33.2 df=28 z=+0.70
interior                           n= 7247 chi2=  26.0 df=28 z=-0.26
--- by word length
D, words of length 1               n=   83 chi2=  25.3 df=27 z=-0.23 |    first rune of len-1 words, D    n=   83 chi2=  25.3 df=27 z=-0.23
D, words of length 2               n=  892 chi2=  25.8 df=27 z=-0.16 |    first rune of len-2 words, D    n=  445 chi2=  29.5 df=27 z=+0.34
D, words of length 3               n= 2144 chi2=  33.1 df=27 z=+0.82 |    first rune of len-3 words, D    n=  714 chi2=  28.5 df=27 z=+0.21
D, words of length 4               n= 2035 chi2=  22.9 df=27 z=-0.55 |    first rune of len-4 words, D    n=  508 chi2=  15.6 df=27 z=-1.55
D, words of length 5               n= 1573 chi2=  31.8 df=27 z=+0.66 |    first rune of len-5 words, D    n=  311 chi2=  18.1 df=27 z=-1.22
D, words of length 6               n= 1527 chi2=  31.7 df=27 z=+0.64 |    first rune of len-6 words, D    n=  255 chi2=  19.2 df=27 z=-1.06
D, words of length 7               n= 1505 chi2=  15.9 df=27 z=-1.50 |    first rune of len-7 words, D    n=  216 chi2=  22.0 df=27 z=-0.68
D, words of length 8               n= 1236 chi2=  45.2 df=27 z=+2.48 |    first rune of len-8 words, D    n=  154 chi2=  26.0 df=27 z=-0.14
```
Pooled chi-square over the position x length cells: 879.6 on 945 df (z = -1.50). Word-initial D z=+0.84, word-final -0.47, word-initial rune -0.64, word-final +0.70. Two cells at +2.4-2.5 out of ~25 are chance. Repeated word types by length (1..6): real [55, 94, 16, 0, 0, 0] vs null mean [55.6, 102.4, 10.8, 0.2, 0, 0]: no repeated words beyond chance (3-rune words z=+1.66). All flat, as the chain model requires; no lead here.

(iv) Other languages. Latin without digraph rule or with Cicada rules: Newton 0.0346-0.0405, Virgil 0.050-0.058, Caesar 0.039-0.046; Old English Beowulf (verse) 0.043-0.051; German Faust 0.0076-0.0081 (a mid-range fit, similar to unmodified English); all are 10x or more worse than English minus THE/OF/TO. NOTE: two files in dukotah armada19 labelled "cicero_tusculan_disputations" and "suetonius_twelve_caesars" are English translations, not Latin, so my earlier t3_lang-style labels are wrong in that regard; the only Latin used for the verdict are Newton, Virgil, Caesar. No Old English PROSE corpus exists in the repos (only Beowulf); raw.githubusercontent.com for the UD Old English treebank returned 404 and Project Gutenberg is proxy-blocked, so the prose comparison could not be done.

## Limitations (honest)

- Offsets only 0..500 (as briefed). Plain solved-text sequences have period 2,795 (letters) or 695 (words); the remainder of the period was not scanned in the null-calibrated run. Cumulative sequences are tiled and restarted at the offset, which is one of several reasonable definitions.
- The plaintext-autokey family decodes under sigma = identity or reversed index order only; an arbitrary sigma breaks the recurrence (the feedback uses the real letter). The conditional-observable test (1b) is sigma-free and covers the self-keyed ciphertext cases.
- 3-rune-context conditional test has low power. Constant-in-word is excluded at 7.3 sd, not at hundreds of sd, because words are short.
- MAD-based z has heavy right tails (null group maxima 5-9); I rely on the empirical null maxima, not on Gaussian z. With 20 shuffles the null sd of a group maximum is itself uncertain.
- Goal 2 JS values depend on corpus genre; the THE/OF/TO versus letter-by-letter distinction is not resolved by word lengths.

## Files
solved.py (solved-page decode with F-interrupt beam search), seqs.py, fam_solved.py, fam_self.py, fam_auto.py, scan.c/autokey.c (engines), ctrl.py, run_*_controls.py, run_main.py, aggregate.py, condtest.py, cond_ctrl.py, const_units.py, goal2_wl.py, goal2_b.py, goal2_c.py; logs *.log; results ctrl_*.json, main_results_*.pkl.

## Follow-up: full-period running keys

Scope: solved-text running keys extended from offsets 0..500 to the full period (letters 0..2794, words 0..694; the new short sources use their own period 0..84/94/179). Sequences: PT and CT per-letter prime values and rune indices, PT and CT per-word gematria sums (per-word and expanded per letter). Each source was tried in both directions, both consumption conventions (A/B), continuous and page-restart, additive (mod 28 and mod 29 reductions, both signs) and GF(29) (k and k^-1), plus the raw-shift control. New sources added: LP2 page 55 (the 85-rune AN END ciphertext), page 56 (the 95-rune parable runes) and their concatenation, each as prime values, indices and word sums. Same engine, same chain-consistent shuffle null (20 shuffles).

LP1 "unsolved" rune pages: none exist in scream314_lp.md. Every LP1 page (00-16) that has a rune block also has a documented plaintext and is already in the solved set; pages 07, 08, 11, 12, 15 have no rune transcription there. Note that pages 55 and 56 of lpdata.load() are the already-solved pages 73 (AN END) and 74 (parable), so they overlap the solved CT/PT sets and add only short stand-alone keys.

Trials: 920 spec-forms, 987,520 offset trials per run, 21 runs (real + 20 nulls).

Positive control: PT letter primes planted at offset 2300 (beyond the old limit), recovered at exactly 2300, z = 420, IoC 1.752 (next best 75.7 is a related spec).

Result: family-wide max z real 7.66 versus null max z 7.19 +- 0.38 (max 8.18). The real maximum is PT.W.sum at offset 2492 (z 7.66, IoC 1.0402 against the convention-A baseline 1.0357, i.e. flat); that group's own null max is 7.28, 3.07 null-sd above its null mean, but it does not exceed the family-wide null maximum and is one of 15 groups, so it is within chance. All other groups are within 1.3 sd of their nulls, including PT/CT letter primes and indices, the raw-shift control, and all page 55/56 sources (<= 0.3 sd). No readable text; nothing was submitted to the oracle.

Verdict: NULL for full-period solved-text running keys and the page 55/56 keys. The earlier null result for offsets 0..500 was not hiding a signal at longer offsets. Logs: full.log, full_results.pkl, run_full.py.
