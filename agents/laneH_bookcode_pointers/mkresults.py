H='./agents/laneH_bookcode_pointers'
mat=open(H+'/table_view_src.md').read()
oth=open(H+'/tables_other.md').read().split('\n\n')
fin=open(H+'/finalists.txt').read()
ctl=open(H+'/control.log').read()
doc=f'''# RESULTS: laneH_bookcode_pointers

Hypothesis: the 2,896 LP2 words are *pointers* (book-code addresses), not ciphertext, into a text Cicada demonstrably used
("its words are the map, their meaning is the road, and their numbers are the direction").

**Verdict: NULL.** No text x number-source x pointer-semantics combination (10,880 configurations, 32,512 scored rows, each against
150 nulls) beats the null. The real best z (5.17 vs shuffle null, 5.29 vs chain null) is *below* the mean of the best-of-family z that
pure-noise replicates reach (5.83 and 5.61). No output is readable English; no config passes the word-hit test. Everything that looked
significant against the plain shuffle null (103 rows with z > 4; 98 of them per-rune sources) is the known doublet-deficit artifact and collapses under a doublet-matched null (below); the other 5 are windowed extreme-value scores inside the null max distribution.

Code, raw per-config results (pickles), full CSV: `{H}/` (`all_configs.csv` has every config; `run.py`, `engine.py`, `texts.py`, `sources.py`, `control.py`, `finalists.py`, `analyze.py`, `tables.py`).

## 1. Texts and how they were validated

16 text "views" (paragraph > sentence > word > letter hierarchy; addresses resolve against it, 0- and 1-based, mod-reduced or raw/invalid-dropped):

| view | what | notes |
|---|---|---|
| SR_doyle | Emerson *Self-Reliance*, local Gutenberg text, epigraph blocks + the one indented verse block + "4." section numbers removed; paragraphs = blank-line blocks; sentences split on . ! ? | **Validated on the 2014 book code** (below). 50 paras, 508 sentences, 10,047 words |
| SR_doyle_semi, SR_withverse, SR_lines | alt segmentations: sentences also split on ; : / verse block kept as a paragraph / physical file lines as "sentences" | alt paragraphings requested by the brief |
| AL_verse, AL_flat, AL_allverses | Crowley *Liber AL*, chapter:verse structure (66/79/75 = 220 verses, from raw.githubusercontent.com Barclay-McClay/PoimandresDiscordBot al.json, verse texts agree with the local hermetic file where compared); flat = chapter->one sentence; allverses = one paragraph of 220 verses | **2013 AL book code could NOT be validated** (see below) |
| Mab_para, Mab_lines | Mabinogion, Guest translation, Gutenberg #5160 (local): blank-line paragraphs; physical lines (2012 line:word / line:letter style) | 107,785 words |
| RunePoem | Anglo-Saxon Rune Poem, transliteration, 29 stanza-lines | |
| LP1_solved | the 5 solved LP1 pages' plaintext (letters only, one letter = one "word", page = paragraph) | |
| CicadaPGP | Cicada's own signed prose | |
| KJV | control; chapters = paragraphs, verses = sentences | already null in prior work |
| Blake, Milton, Agrippa | priors (rune-stream cumulative pointers were null) re-run with the new number sources | |

**Self-Reliance parse check (positive validation of the 2014 scheme).** The 2014 message "1:2:3:1, 3:3:13:5, 45:5:2:3, ..." (paragraph:sentence:word:letter)
decodes with my vectorised resolver on SR_doyle to `AUQGNXJTVDBLL`, the literal "3", `PV` = **`auqgnxjtvdbll3pv.onion`**, matching the community-published
answer (scream314_2014.md in the dukotah corpus): 15/15 pointers + literal. Getting there needed (a) dropping the epigraph blocks, (b) dropping the
indented verse block "His hidden meaning lies in our endeavors" (otherwise paragraphs 45+ are off by one) and (c) stripping the "4." section number. So SR_doyle *is* the 2014 paragraphing.
The pipeline that is used for LP2 reproduces a real Cicada book-code decode.

**Liber AL 2013 code not reproduced.** The 2013 message (I:1:6, I:2:15, ... chapter:verse:N) has 32/32 first-group pointers inside the verse length when characters are counted including spaces and
punctuation (29/32 with letters only) but decodes to unreadable text under 100 variants (verse offset -2..+2, char offset -2..+2, 4 character-counting modes; best quadgram -5.2 on 32 letters = noise).
So either Cicada used a different AL edition/verse split, or the third number is not a character index. The AL views therefore test "AL as a text under the generic semantics", not "AL under the verified Cicada 2013 format".
The 2012 Mabinogion code format (line:word-ish pairs, "the product of the first two primes" = 6) has no published decode, so it is covered only by the generic (line, letter)/(line, word) 2-tuples and the n-th-prime convention.

## 2. Number sources (per LP2 word or per rune)

gsum (Gematria prime sum of the word, 2..933), isum (sum of 0-based rune indices), isum1 (sum of 1-based indices), wlen (word length 1..14), w29 (base-29 value of the word's rune indices, mod 2^61-1),
rprime (each rune's prime value, 12,956 pointers), ridx (each rune's 0-based index), ridx1 (1-based).
Plus "word as its own tuple": wtK_idx1 / wtK_prime for K = 2,3,4 = the runes of every K-rune word taken as a K-tuple (448 / 720 / 513 words), read only with a K-level address (PS, PSW, PSWL ...).

## 3. Pointer semantics (all with b = 0 or 1, mod-reduced or raw, 10,880 configs in total)

* 1-level: L (letter n), Lp (n -> n-th prime -> letter: the 2012 prime convention), Lpi (n -> pi(n), prime-counting), W / Wp / Wpi (same, selecting a WORD), S1 (first letter of sentence/line n), Lcum / Wcum (cumulative skip, the old bookcipher.py scheme with the new number sources).
* Tuples formed from consecutive numbers (groups of 2, 3, 4), each level resolved relative to the previous one: 2-tuples PS PW PL SW SL WL; 3-tuples PSW PSL PWL SWL; 4-tuple PSWL (= 2014 format). (P = paragraph/chapter/stanza, S = sentence/verse/line, W = word, L = letter.)
* Scores: q = quadgram mean of the selected letters (primary for letter outputs), qwin = best 100-letter window mean quadgram; for word outputs: qfirst (first letters), qall (concatenated words), pmi (mean pointwise mutual information of adjacent selected words under a bigram model of ~1.1M words of local English, the "word-level English model") and the windowed versions (qfirstwin, pmiwin). IoC and word-hit are computed for finalists (IoC is uninformative for pointer outputs: it is set by which text positions the numbers can reach, and is identical in the null: e.g. 8.66 vs null 8.69 +- 0.01).

## 4. Null calibration

Three nulls per config, 50 each (150 per config, ~1.6M pointer decodes + scorings overall):
1. **shuffle**: the same numbers in random order (keeps the marginal).
2. **random**: uniform integers over the source's min..max. Reported but not used for decisions: z vs random reaches 44 only because LP2's marginal (e.g. word length 1..14) reaches a few early words; it measures marginal, not structure.
3. **chain**: runes regenerated from the campaign's chain model (c_i = c_{{i-1}} + flat 1..28, s=0 with p=0.66%) with the *real* word boundaries, all sources recomputed. This keeps the doublet deficit (86/12,955 adjacent equal runes vs 3.45%) that the shuffle null destroys.

**The doublet artifact.** Pointer schemes map equal adjacent numbers to equal adjacent letters, and doubled letters are penalised by quadgrams, so a stream with a deficit of repeated runes scores systematically higher than a shuffle under *any* many-to-one pointer map. Per-rune sources (rprime/ridx/ridx1, 12,956 pointers) therefore show mean z_shuffle = +0.77 on q-type scores vs +0.10 under the chain null (word-level sources: +0.02).
All of the 98 per-rune rows with z_shuffle > 4 (e.g. SR rprime W qfirst z=5.17, SR ridx1 L z=5.03, AL ridx S1 z=5.10) fall to z_chain between -1.4 and +4.1 (median 1.7; refined with 150 fresh replicates: 2.1, 1.8, 1.5). Not a text signal.
Max-statistics use leave-one-out z of the null replicates themselves, so "null max z" is the best z a pure-noise stream reaches over the same set of configs (windowed scores are extreme-value distributed, so Gaussian z for them is not meaningful on its own; the null-max comparison is).

## 5. Positive controls (200+ letter English message, 211 letters; null = 50 shuffles + 50 random of the control numbers)

```
{ctl}
```
Reading: letter-number, word-number (first letter), n-th-prime, and Self-Reliance 4-tuple (mod) pointers read back at z = 11-16 (>10). The raw (drop-invalid) variants read back exactly (the decode is deterministic) but their *z* is lower (5-9) only because shuffled/random numbers are mostly out of range in raw mode, leaving few outputs to compare. A 211-pointer message hidden inside the real 2,896-word gsum stream is invisible to whole-stream scores (z 5 / 1.8) but detected by the windowed score (qfirstwin z = 21), which is why windowed scores are in the grid. Word-sequence messages (54 words) are detected by pmi (z = 11) and not by letter statistics, as designed.
Sensitivity statement: any message of >= ~100 consecutive pointers in a clean pointer encoding (the semantics listed above) would have produced z > 10 in at least one score. None did.

## 6. Results: text x number source (real best z / null best-of-family z; "shuffle null ; chain null"; cell = max over all semantics, b, mode, scores)

{mat}

(wlen has no chain null: word boundaries are shared with the real data, so the chain stream's word lengths are identical; the 1.0 entries are degenerate.)

## 7. Results by semantics family / semantic / score / text / source

Best real z per slice vs the best z reached by 50 pure-noise replicates over the same slice (mean +- sd; max of 50) and the empirical p.

{oth[0]}

{oth[1]}

{oth[2]}

{oth[3]}

{oth[4]}

Reading: the only slices with empirical p near 0.04 are q/qall/qfirst against the shuffle null, which is the doublet artifact (p = 0.47-0.71 against the chain null), and Wcum against the chain null (p = 0.04) which is 1 of ~40 slices tested and is driven by a single windowed score on KJV (the control text) with w29 pointers whose cumulative sum overflows int64 (pseudo-random pointers); its output is unreadable (below) and its word-hit z is -1.1. The 4-tuple Self-Reliance slice (TPSWL, the exact 2014 format) is the *worst* slice (real 2.94 vs null 3.78, p = 0.98).

## 8. Best real results, with outputs

Ranked by min(z_shuffle, z_chain) (the first block) and by z_shuffle alone (second block, doublet artifacts). z(150) = recomputed with 150 fresh nulls of each type. Word-hit = share of letters covered by words >= 4 letters from the local vocabulary, vs 30 shuffles.

```
{fin}
```

None is readable. Where a window of "words" looks fluent (Blake pmiwin: "WEEPBOYTOMOONWEEPSPEAKHAPPYISINAM..." ; SR_lines isum: "FROMADMONITIONALL...") it is a run of high-frequency words from the first few hundred words of the text (small numbers can only reach the start of the text) with word-hit equal to the null (0.66 vs 0.69, 0.60 vs 0.60), i.e. word salad.

## 9. Verdicts per family

| family | verdict |
|---|---|
| Letter pointer (L, Lp, Lpi, S1) into SR, AL, Mabinogion, Rune Poem, LP1, Cicada prose, KJV, Blake, Milton, Agrippa; all 8 number sources, 0/1-based, mod/raw | NULL (best z 5.1 shuffle / 4.0 chain; p 0.2 / 0.73) |
| Word pointer (W, Wp, Wpi) scored by letters and by a word-bigram PMI model | NULL (5.17 / 3.95; PMI 3.8 vs null 3.8) |
| Cumulative skip with new number sources | NULL (3.3 / 2.8 for letters; the Wcum 5.3 outlier is a KJV control artifact) |
| 2-tuples (paragraph/sentence/line x word/letter) | NULL |
| 3-tuples (incl. chapter:verse:letter, para:sent:word) | NULL |
| 4-tuple paragraph:sentence:word:letter (exact 2014 format on the validated Self-Reliance parse) | NULL, worst slice (2.94 vs null 3.78) |
| Word-as-tuple (each K-rune word read as a K-tuple) | NULL |
| 2012 prime-index convention (n -> n-th prime -> position; reverse pi) | NULL |

Not excluded (stated honestly): (i) the exact 2013 AL edition/format (could not be reproduced) and the exact 2012 Mabinogion format; (ii) Gibson's *Agrippa* (copyrighted, not on disk); (iii) texts we do not have (Jung, Wilson, GEB, ...); (iv) pointer formats where the address is spread across *non-consecutive* words, or structure unrelated to word boundaries (e.g. rune-pair base-29 addresses were not run beyond w29); (v) the 2,896-word segmentation itself may be decorative (the campaign's word-length-order finding says adjacent word lengths carry no English structure), which would make any word-level source meaningless; the per-rune sources do not depend on it and are also null once the doublet deficit is accounted for.
Consistent with the campaign: the numbers are flat/chain-like, and nothing in the book connects to a Cicada-demonstrated text under the book-code formats Cicada actually used.
'''
open(H+'/RESULTS.md','w').write(doc)
