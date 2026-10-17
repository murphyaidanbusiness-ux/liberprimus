# RESULTS: laneH_bookcode_pointers

Hypothesis: the 2,896 LP2 words are *pointers* (book-code addresses), not ciphertext, into a text Cicada demonstrably used
("its words are the map, their meaning is the road, and their numbers are the direction").

**Verdict: NULL.** No text x number-source x pointer-semantics combination (10,880 configurations, 32,512 scored rows, each against
150 nulls) beats the null. The real best z (5.17 vs shuffle null, 5.29 vs chain null) is *below* the mean of the best-of-family z that
pure-noise replicates reach (5.83 and 5.61). No output is readable English; no config passes the word-hit test. Everything that looked
significant against the plain shuffle null (103 rows with z > 4; 98 of them per-rune sources) is the known doublet-deficit artifact and collapses under a doublet-matched null (below); the other 5 are windowed extreme-value scores inside the null max distribution.

Code, raw per-config results (pickles), full CSV: `./agents/laneH_bookcode_pointers/` (`all_configs.csv` has every config; `run.py`, `engine.py`, `texts.py`, `sources.py`, `control.py`, `finalists.py`, `analyze.py`, `tables.py`).

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
3. **chain**: runes regenerated from the campaign's chain model (c_i = c_{i-1} + flat 1..28, s=0 with p=0.66%) with the *real* word boundaries, all sources recomputed. This keeps the doublet deficit (86/12,955 adjacent equal runes vs 3.45%) that the shuffle null destroys.

**The doublet artifact.** Pointer schemes map equal adjacent numbers to equal adjacent letters, and doubled letters are penalised by quadgrams, so a stream with a deficit of repeated runes scores systematically higher than a shuffle under *any* many-to-one pointer map. Per-rune sources (rprime/ridx/ridx1, 12,956 pointers) therefore show mean z_shuffle = +0.77 on q-type scores vs +0.10 under the chain null (word-level sources: +0.02).
All of the 98 per-rune rows with z_shuffle > 4 (e.g. SR rprime W qfirst z=5.17, SR ridx1 L z=5.03, AL ridx S1 z=5.10) fall to z_chain between -1.4 and +4.1 (median 1.7; refined with 150 fresh replicates: 2.1, 1.8, 1.5). Not a text signal.
Max-statistics use leave-one-out z of the null replicates themselves, so "null max z" is the best z a pure-noise stream reaches over the same set of configs (windowed scores are extreme-value distributed, so Gaussian z for them is not meaningful on its own; the null-max comparison is).

## 5. Positive controls (200+ letter English message, 211 letters; null = 50 shuffles + 50 random of the control numbers)

```
message letters 211
SR_doyle L b1 mod (letter number): q: real=-4.253 z_shuf=14.6 z_rand=13.5; qwin: real=-4.041 z_shuf=11.4 z_rand=10.5 
SR_doyle W b1 mod (word number, first letter): qfirst: real=-4.253 z_shuf=15.2 z_rand=15.4; qfirstwin: real=-4.041 z_shuf=11.7 z_rand=12.6; qall: real=-4.366 z_shuf=-0.3 z_rand=-2.0; pmi: real=-3.938 z_shuf=-0.9 z_rand=-0.3; pmiwin: real=-3.502 z_shuf=-0.3 z_rand=-0.2 
SR_doyle TPSWL b1 raw (2014 para:sent:word:letter): q: real=-4.253 z_shuf=6.3 z_rand=nan; qwin: real=-4.041 z_shuf=nan z_rand=nan 
SR_doyle TPSWL b1 mod: q: real=-4.253 z_shuf=15.3 z_rand=13.9; qwin: real=-4.041 z_shuf=11.3 z_rand=11.1 
SR_doyle Lp b1 mod (n-th prime -> letter): q: real=-4.253 z_shuf=16.4 z_rand=14.7; qwin: real=-4.041 z_shuf=11.7 z_rand=11.7 
AL_verse TPSL b1 raw (chapter:verse:letter): q: real=-4.253 z_shuf=5.5 z_rand=nan; qwin: real=-4.041 z_shuf=nan z_rand=nan 
Mab_lines TSL b1 raw (line:letter): q: real=-4.253 z_shuf=8.9 z_rand=nan; qwin: real=-4.041 z_shuf=nan z_rand=nan 
SR_doyle W b1 mod: 200-pointer message embedded in the real 2896-word gsum stream (whole-stream score): qfirst: real=-7.152 z_shuf=5.2 z_rand=1.8; qfirstwin: real=-4.041 z_shuf=20.9 z_rand=18.2; qall: real=-4.222 z_shuf=0.9 z_rand=4.6; pmi: real=-3.762 z_shuf=0.2 z_rand=0.8; pmiwin: real=-2.894 z_shuf=-0.2 z_rand=-0.1 
missing words []
SR_doyle W b1 mod (word-sequence message, 54 words): qfirst: real=-6.657 z_shuf=2.2 z_rand=1.5; qfirstwin: real=nan z_shuf=nan z_rand=nan; qall: real=-4.021 z_shuf=5.3 z_rand=3.1; pmi: real=1.028 z_shuf=11.4 z_rand=11.1; pmiwin: real=nan z_shuf=nan z_rand=nan 

```
Reading: letter-number, word-number (first letter), n-th-prime, and Self-Reliance 4-tuple (mod) pointers read back at z = 11-16 (>10). The raw (drop-invalid) variants read back exactly (the decode is deterministic) but their *z* is lower (5-9) only because shuffled/random numbers are mostly out of range in raw mode, leaving few outputs to compare. A 211-pointer message hidden inside the real 2,896-word gsum stream is invisible to whole-stream scores (z 5 / 1.8) but detected by the windowed score (qfirstwin z = 21), which is why windowed scores are in the grid. Word-sequence messages (54 words) are detected by pmi (z = 11) and not by letter statistics, as designed.
Sensitivity statement: any message of >= ~100 consecutive pointers in a clean pointer encoding (the semantics listed above) would have produced z > 10 in at least one score. None did.

## 6. Results: text x number source (real best z / null best-of-family z; "shuffle null ; chain null"; cell = max over all semantics, b, mode, scores)

| text view | gsum | isum | isum1 | wlen | w29 | rprime | ridx | ridx1 | wt2_idx1 | wt2_prime | wt3_idx1 | wt3_prime | wt4_idx1 | wt4_prime |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AL_allverses | 3.4 (3.0) ; 2.5 (3.0) | 2.8 (3.1) ; 2.7 (3.1) | 3.3 (3.1) ; 3.0 (3.0) | 2.9 (3.1) ; 1.0 (1.0) | 3.4 (3.0) ; 2.8 (3.1) | 4.2 (3.1) ; 3.9 (3.2) | 4.8 (3.3) ; 2.8 (3.3) | 4.0 (3.2) ; 3.9 (3.1) | 1.7 (2.4) ; 1.8 (2.3) | 1.3 (2.4) ; 1.6 (2.4) | 2.4 (2.1) ; 2.3 (2.1) | 1.4 (2.1) ; 1.9 (2.0) | 2.2 (0.9) ; 2.2 (0.9) | 0.7 (0.9) ; 1.0 (1.0) |
| AL_flat | 3.1 (2.8) ; 2.9 (2.9) | 2.6 (2.9) ; 2.5 (3.0) | 2.3 (2.9) ; 2.7 (2.7) | 2.9 (2.9) ; 1.0 (1.0) | 3.3 (2.9) ; 2.8 (3.0) | 4.2 (3.0) ; 3.9 (3.0) | 5.1 (3.1) ; 2.7 (3.1) | 4.0 (3.0) ; 3.9 (3.0) | 3.1 (2.2) ; 2.8 (2.2) | 2.0 (2.2) ; 1.9 (2.1) | 3.1 (1.9) ; 2.4 (1.9) | 2.0 (1.9) ; 2.5 (1.9) | 0.7 (0.9) ; 0.5 (1.0) | 0.9 (1.0) ; 1.0 (0.8) |
| AL_verse | 3.1 (3.0) ; 2.9 (3.0) | 2.6 (3.1) ; 2.5 (3.0) | 3.3 (3.1) ; 3.0 (3.1) | 3.2 (3.0) ; 1.0 (1.0) | 3.4 (3.0) ; 2.8 (3.0) | 4.4 (3.1) ; 3.9 (3.2) | 4.8 (3.2) ; 2.8 (3.3) | 4.0 (3.4) ; 3.9 (3.2) | 3.1 (2.5) ; 2.8 (2.5) | 2.0 (2.5) ; 2.3 (2.5) | 2.7 (2.2) ; 3.2 (2.2) | 2.6 (2.0) ; 2.5 (2.0) | 2.0 (0.9) ; 2.0 (0.9) | 0.6 (0.8) ; 0.5 (1.0) |
| Agrippa | 2.8 (3.1) ; 3.5 (3.0) | 2.5 (3.0) ; 2.7 (3.0) | 2.2 (3.1) ; 2.3 (3.1) | 4.2 (3.0) ; 1.0 (1.0) | 2.8 (3.1) ; 2.8 (2.9) | 4.2 (3.3) ; 2.7 (3.3) | 3.2 (3.1) ; 2.9 (3.3) | 4.2 (3.3) ; 2.6 (3.3) | 3.2 (2.5) ; 2.8 (2.5) | 3.2 (2.4) ; 3.2 (2.5) | 1.8 (2.1) ; 1.7 (2.1) | 1.2 (2.0) ; 1.4 (2.0) | 1.2 (0.9) ; 1.1 (0.9) | 1.0 (1.0) ; 1.1 (0.9) |
| Blake | 3.2 (3.1) ; 2.5 (3.0) | 2.9 (3.1) ; 2.7 (3.0) | 3.0 (2.9) ; 2.6 (3.0) | 2.9 (2.9) ; 1.0 (1.0) | 3.5 (3.1) ; 3.3 (3.0) | 4.3 (3.2) ; 4.1 (3.1) | 4.7 (3.3) ; 2.7 (3.4) | 4.5 (3.2) ; 3.0 (3.4) | 2.4 (2.5) ; 2.5 (2.5) | 2.1 (2.4) ; 2.5 (2.5) | 1.6 (2.1) ; 1.6 (2.1) | 1.4 (2.1) ; 1.2 (2.0) | 1.8 (0.9) ; 2.1 (0.9) | 1.3 (1.0) ; 1.4 (0.9) |
| CicadaPGP | 2.8 (3.0) ; 3.3 (3.0) | 3.1 (3.2) ; 2.9 (3.0) | 2.5 (3.1) ; 2.5 (3.0) | 2.5 (3.2) ; 1.0 (1.0) | 3.3 (3.3) ; 3.5 (3.2) | 5.1 (3.2) ; 3.5 (3.3) | 3.6 (3.3) ; 2.8 (3.2) | 3.5 (3.2) ; 2.6 (3.2) | 2.4 (2.6) ; 2.3 (2.4) | 1.9 (2.3) ; 2.0 (2.3) | 1.6 (2.0) ; 1.9 (2.0) | 1.3 (2.0) ; 1.2 (2.0) | 1.6 (0.9) ; 1.6 (0.9) | 1.5 (0.9) ; 1.6 (0.8) |
| KJV | 3.5 (3.0) ; 2.8 (3.1) | 2.7 (3.0) ; 2.2 (3.1) | 3.4 (3.0) ; 3.6 (3.0) | 3.3 (3.0) ; 1.0 (1.0) | 4.9 (3.1) ; 5.3 (3.2) | 4.0 (3.2) ; 4.0 (3.1) | 4.3 (3.2) ; 4.0 (3.4) | 4.3 (3.4) ; 4.0 (3.5) | 1.6 (2.4) ; 1.6 (2.5) | 2.6 (2.4) ; 2.7 (2.4) | 2.8 (2.3) ; 2.3 (2.3) | 2.3 (2.3) ; 1.9 (2.3) | 0.9 (1.1) ; 0.9 (1.1) | 1.4 (1.0) ; 1.4 (0.9) |
| LP1_solved | 2.1 (2.8) ; 1.6 (2.8) | 2.6 (2.5) ; 2.5 (2.7) | 3.0 (2.9) ; 2.2 (2.8) | 2.3 (2.8) ; 1.0 (1.0) | 3.2 (2.8) ; 2.7 (2.8) | 4.0 (2.9) ; 2.0 (2.9) | 3.2 (2.9) ; 2.6 (2.9) | 2.8 (2.9) ; 2.0 (2.9) | 1.3 (2.0) ; 1.4 (1.9) | 1.3 (1.8) ; 0.8 (1.9) | 2.7 (1.7) ; 2.6 (1.8) | 2.2 (1.8) ; 1.7 (1.7) | -0.5 (0.9) ; -0.6 (0.9) | 1.4 (0.9) ; 1.4 (0.9) |
| Mab_lines | 2.9 (2.9) ; 3.2 (2.8) | 3.1 (3.0) ; 3.5 (3.1) | 2.9 (3.0) ; 2.7 (2.9) | 3.9 (3.0) ; 1.0 (1.0) | 3.3 (3.0) ; 3.1 (3.1) | 4.4 (3.0) ; 3.5 (3.2) | 4.8 (3.2) ; 2.4 (3.2) | 3.5 (3.2) ; 2.6 (3.3) | 1.7 (2.4) ; 1.6 (2.4) | 2.8 (2.3) ; 2.8 (2.3) | 3.5 (2.0) ; 2.9 (2.2) | 2.6 (2.0) ; 3.0 (2.1) | 1.3 (0.9) ; 1.6 (0.9) | 1.8 (0.9) ; 1.6 (1.0) |
| Mab_para | 3.5 (2.9) ; 3.9 (2.9) | 3.7 (3.1) ; 3.2 (3.0) | 2.9 (3.1) ; 2.6 (3.2) | 3.9 (2.9) ; 1.0 (1.0) | 3.2 (3.0) ; 3.1 (3.1) | 4.4 (3.2) ; 3.5 (3.2) | 4.8 (3.2) ; 2.7 (3.3) | 3.2 (3.3) ; 3.2 (3.3) | 1.9 (2.4) ; 1.7 (2.5) | 2.1 (2.4) ; 1.9 (2.6) | 2.3 (2.3) ; 2.6 (2.2) | 1.4 (2.0) ; 1.2 (2.1) | 1.4 (0.8) ; 2.0 (0.9) | 1.4 (0.9) ; 1.2 (0.8) |
| Milton | 3.0 (3.1) ; 2.8 (3.1) | 2.7 (3.0) ; 2.7 (2.9) | 2.6 (3.1) ; 2.7 (3.1) | 3.3 (3.0) ; 1.0 (1.0) | 2.8 (3.2) ; 2.9 (3.0) | 2.9 (3.3) ; 3.7 (3.2) | 3.3 (3.3) ; 3.9 (3.3) | 3.6 (3.2) ; 3.5 (3.2) | 2.1 (2.6) ; 2.1 (2.5) | 2.2 (2.4) ; 1.9 (2.6) | 2.0 (2.3) ; 2.3 (2.1) | 2.2 (2.1) ; 2.5 (2.2) | -0.6 (0.9) ; -0.8 (1.0) | 0.2 (0.8) ; 0.1 (0.9) |
| RunePoem | 3.4 (3.2) ; 2.5 (3.1) | 2.7 (3.1) ; 3.1 (2.9) | 2.6 (3.0) ; 2.5 (3.0) | 3.4 (3.0) ; 1.0 (1.0) | 3.4 (3.1) ; 3.6 (3.0) | 3.0 (3.2) ; 2.7 (3.2) | 3.3 (3.1) ; 3.0 (3.2) | 3.4 (3.3) ; 3.2 (3.2) | 1.6 (2.4) ; 1.5 (2.4) | 2.5 (2.4) ; 3.0 (2.3) | 0.7 (2.1) ; 0.8 (2.1) | 1.5 (1.9) ; 1.3 (2.0) | 0.2 (0.9) ; 0.8 (0.9) | 0.9 (0.9) ; 0.8 (1.0) |
| SR_doyle | 2.3 (3.0) ; 4.0 (3.0) | 3.3 (3.0) ; 4.0 (2.9) | 2.4 (3.0) ; 2.5 (2.9) | 2.0 (3.0) ; 1.0 (1.0) | 3.3 (3.2) ; 2.9 (3.2) | 5.2 (3.2) ; 2.7 (3.2) | 4.2 (3.2) ; 2.5 (3.3) | 5.0 (3.3) ; 2.7 (3.2) | 1.3 (2.5) ; 1.2 (2.4) | 2.1 (2.5) ; 1.8 (2.4) | 2.1 (2.3) ; 1.7 (2.2) | 1.1 (2.1) ; 1.3 (2.0) | 1.3 (1.0) ; 1.8 (0.9) | -1.1 (1.0) ; -0.9 (0.9) |
| SR_doyle_semi | 3.5 (3.1) ; 2.7 (3.0) | 3.3 (3.1) ; 4.0 (3.0) | 3.4 (3.0) ; 2.6 (3.0) | 3.0 (3.1) ; 1.0 (1.0) | 3.3 (3.1) ; 2.9 (3.2) | 5.2 (3.2) ; 2.7 (3.3) | 4.2 (3.3) ; 3.6 (3.3) | 5.0 (3.2) ; 2.9 (3.2) | 4.1 (2.5) ; 4.5 (2.4) | 1.8 (2.4) ; 1.2 (2.4) | 2.5 (2.2) ; 1.9 (2.3) | 1.4 (2.2) ; 1.6 (2.0) | 0.1 (0.9) ; 0.6 (0.9) | 0.2 (1.0) ; 0.3 (0.9) |
| SR_lines | 3.1 (3.1) ; 2.4 (2.9) | 4.2 (3.2) ; 3.7 (3.1) | 2.9 (3.0) ; 3.7 (3.0) | 3.0 (3.1) ; 1.0 (1.0) | 2.7 (3.1) ; 2.9 (3.1) | 4.0 (3.2) ; 2.7 (3.3) | 3.8 (3.2) ; 4.0 (3.3) | 3.8 (3.1) ; 4.0 (3.1) | 1.8 (2.4) ; 1.6 (2.3) | 3.0 (2.4) ; 2.5 (2.4) | 2.5 (2.0) ; 2.0 (2.1) | 2.0 (2.1) ; 1.8 (2.0) | 2.3 (0.8) ; 1.9 (0.9) | -0.4 (0.8) ; -0.4 (0.8) |
| SR_withverse | 2.5 (3.2) ; 2.7 (3.1) | 3.3 (3.0) ; 4.0 (3.0) | 3.0 (3.0) ; 2.6 (3.1) | 2.0 (3.0) ; 1.0 (1.0) | 3.9 (3.3) ; 3.1 (3.0) | 5.2 (3.2) ; 2.7 (3.0) | 4.2 (3.3) ; 2.5 (3.3) | 5.0 (3.3) ; 2.7 (3.2) | 1.3 (2.5) ; 1.2 (2.4) | 3.0 (2.4) ; 3.4 (2.4) | 2.1 (2.3) ; 1.7 (2.2) | 2.0 (2.1) ; 2.1 (2.1) | 1.3 (1.0) ; 1.8 (0.9) | 0.2 (1.0) ; 0.1 (1.0) |

(wlen has no chain null: word boundaries are shared with the real data, so the chain stream's word lengths are identical; the 1.0 entries are degenerate.)

## 7. Results by semantics family / semantic / score / text / source

Best real z per slice vs the best z reached by 50 pure-noise replicates over the same slice (mean +- sd; max of 50) and the empirical p.

| family | rows | real max z (shuffle null) | null max z (mean +- sd, max of 50) | emp p | real max z (chain null) | null max z | emp p |
|---|---|---|---|---|---|---|---|
| letter-ptr | 4096 | 5.10 | 4.58 +- 0.74, max 7.26 | 0.20 | 3.99 | 4.43 +- 0.75, max 6.78 | 0.73 |
| word-ptr | 7680 | 5.17 | 4.90 +- 0.85, max 7.44 | 0.31 | 3.95 | 4.67 +- 0.69, max 7.29 | 0.88 |
| cumulative | 896 | 4.90 | 4.05 +- 0.95, max 8.19 | 0.14 | 5.29 | 3.95 +- 0.83, max 7.81 | 0.04 |
| tuple2 | 11520 | 5.06 | 5.08 +- 0.79, max 7.14 | 0.45 | 4.47 | 5.03 +- 0.80, max 7.03 | 0.80 |
| tuple3 | 7040 | 4.21 | 4.66 +- 0.69, max 6.69 | 0.71 | 4.03 | 4.62 +- 0.71, max 6.84 | 0.78 |
| tuple4 | 1280 | 2.94 | 3.78 +- 0.64, max 5.73 | 0.98 | 3.58 | 3.58 +- 0.45, max 5.25 | 0.45 |
| ALL | 32512 | 5.17 | 5.83 +- 0.86, max 8.19 | 0.75 | 5.29 | 5.61 +- 0.84, max 7.81 | 0.53 |

| semantic | rows | real max z (shuffle) | null max z | emp p | real max z (chain) | null max z | emp p |
|---|---|---|---|---|---|---|---|
| L | 1024 | 5.03 | 3.85 | 0.04 | 3.99 | 3.69 | 0.29 |
| Lcum | 256 | 3.26 | 3.37 | 0.41 | 2.83 | 3.33 | 0.67 |
| Lp | 1024 | 4.37 | 3.77 | 0.16 | 3.89 | 3.72 | 0.37 |
| Lpi | 1024 | 4.30 | 3.73 | 0.18 | 3.99 | 3.72 | 0.29 |
| S1 | 1024 | 5.10 | 3.99 | 0.06 | 3.46 | 3.76 | 0.63 |
| TPL | 1280 | 3.58 | 3.94 | 0.73 | 3.22 | 3.64 | 0.78 |
| TPS | 1280 | 5.06 | 4.00 | 0.12 | 3.91 | 3.93 | 0.43 |
| TPSL | 1280 | 3.61 | 3.97 | 0.63 | 3.97 | 3.77 | 0.27 |
| TPSW | 3200 | 4.21 | 4.34 | 0.49 | 4.03 | 4.19 | 0.43 |
| TPSWL | 1280 | 2.94 | 3.78 | 0.98 | 3.58 | 3.58 | 0.45 |
| TPW | 3200 | 3.75 | 4.45 | 0.86 | 3.74 | 4.41 | 0.82 |
| TPWL | 1280 | 2.92 | 3.69 | 0.94 | 2.84 | 3.85 | 0.98 |
| TSL | 1280 | 3.37 | 4.05 | 0.90 | 3.25 | 3.99 | 0.90 |
| TSW | 3200 | 4.33 | 4.33 | 0.39 | 4.47 | 4.26 | 0.33 |
| TSWL | 1280 | 3.53 | 3.81 | 0.73 | 3.52 | 3.63 | 0.59 |
| TWL | 1280 | 3.14 | 3.72 | 0.76 | 3.47 | 3.68 | 0.61 |
| W | 2560 | 5.17 | 4.20 | 0.10 | 2.95 | 4.08 | 1.00 |
| Wcum | 640 | 4.90 | 3.80 | 0.10 | 5.29 | 3.76 | 0.04 |
| Wp | 2560 | 4.78 | 4.24 | 0.22 | 3.95 | 4.17 | 0.61 |
| Wpi | 2560 | 4.73 | 4.33 | 0.25 | 3.70 | 4.04 | 0.67 |

| score | rows | real max z (shuffle) | null max z | emp p | real max z (chain) | null max z | emp p |
|---|---|---|---|---|---|---|---|
| pmi | 3584 | 3.83 | 3.76 | 0.45 | 3.22 | 3.75 | 0.88 |
| pmiwin | 3584 | 4.33 | 4.78 | 0.67 | 4.07 | 4.85 | 0.84 |
| q | 7296 | 5.10 | 3.99 | 0.04 | 3.70 | 3.90 | 0.71 |
| qall | 3584 | 4.78 | 3.71 | 0.04 | 3.49 | 3.63 | 0.61 |
| qfirst | 3584 | 5.17 | 3.77 | 0.04 | 3.70 | 3.77 | 0.47 |
| qfirstwin | 3584 | 4.90 | 5.04 | 0.55 | 5.29 | 4.70 | 0.20 |
| qwin | 7296 | 4.41 | 5.26 | 0.92 | 3.99 | 4.98 | 0.98 |

| view | rows | real max z (shuffle) | null max z | emp p | real max z (chain) | null max z | emp p |
|---|---|---|---|---|---|---|---|
| AL_allverses | 2032 | 4.76 | 4.15 +- 0.55 | 0.14 | 3.89 | 4.17 +- 0.69 | 0.63 |
| AL_flat | 2032 | 5.10 | 3.99 +- 0.60 | 0.10 | 3.89 | 3.99 +- 0.59 | 0.51 |
| AL_verse | 2032 | 4.76 | 4.12 +- 0.57 | 0.16 | 3.91 | 4.15 +- 0.65 | 0.59 |
| Agrippa | 2032 | 4.22 | 4.10 +- 0.61 | 0.37 | 3.49 | 4.14 +- 0.62 | 0.80 |
| Blake | 2032 | 4.73 | 4.33 +- 0.71 | 0.22 | 4.07 | 4.09 +- 0.69 | 0.37 |
| CicadaPGP | 2032 | 5.06 | 4.33 +- 0.86 | 0.14 | 3.52 | 4.06 +- 0.68 | 0.82 |
| KJV | 2032 | 4.90 | 4.23 +- 0.60 | 0.10 | 5.29 | 4.31 +- 0.84 | 0.14 |
| LP1_solved | 2032 | 3.99 | 4.11 +- 0.81 | 0.53 | 2.70 | 3.78 +- 0.69 | 1.00 |
| Mab_lines | 2032 | 4.78 | 4.00 +- 0.72 | 0.14 | 3.47 | 4.13 +- 0.93 | 0.84 |
| Mab_para | 2032 | 4.78 | 4.20 +- 0.66 | 0.20 | 3.89 | 4.26 +- 0.93 | 0.59 |
| Milton | 2032 | 3.63 | 4.40 +- 0.83 | 0.86 | 3.87 | 4.14 +- 0.61 | 0.71 |
| RunePoem | 2032 | 3.45 | 4.30 +- 0.70 | 0.90 | 3.64 | 3.97 +- 0.73 | 0.67 |
| SR_doyle | 2032 | 5.17 | 4.25 +- 0.79 | 0.10 | 4.03 | 4.09 +- 0.59 | 0.53 |
| SR_doyle_semi | 2032 | 5.17 | 4.16 +- 0.68 | 0.10 | 4.47 | 4.15 +- 0.59 | 0.27 |
| SR_lines | 2032 | 4.19 | 4.29 +- 0.87 | 0.41 | 3.97 | 4.23 +- 0.70 | 0.57 |
| SR_withverse | 2032 | 5.17 | 4.33 +- 0.91 | 0.14 | 3.95 | 4.02 +- 0.58 | 0.57 |

| source | rows | real max z (shuffle) | null max z | emp p | real max z (chain) | null max z | emp p |
|---|---|---|---|---|---|---|---|
| gsum | 3568 | 3.55 | 4.46 +- 0.71 | 1.00 | 4.03 | 4.14 +- 0.49 | 0.57 |
| isum | 3568 | 4.19 | 4.38 +- 0.67 | 0.61 | 3.95 | 4.24 +- 0.75 | 0.59 |
| isum1 | 3568 | 3.41 | 4.17 +- 0.52 | 0.96 | 3.70 | 4.34 +- 0.82 | 0.80 |
| wlen | 3568 | 4.21 | 4.31 +- 0.82 | 0.43 | 1.00 | 1.00 +- 0.00 | 1.00 |
| w29 | 3568 | 4.90 | 4.55 +- 0.93 | 0.27 | 5.29 | 4.29 +- 0.64 | 0.08 |
| rprime | 3568 | 5.17 | 4.54 +- 0.80 | 0.12 | 4.07 | 4.57 +- 0.75 | 0.80 |
| ridx | 3568 | 5.10 | 4.64 +- 0.77 | 0.24 | 3.99 | 4.76 +- 0.85 | 0.80 |
| ridx1 | 3568 | 5.03 | 4.79 +- 0.85 | 0.31 | 3.99 | 4.62 +- 0.82 | 0.82 |
| wt2_idx1 | 1152 | 4.15 | 3.54 +- 0.47 | 0.10 | 4.47 | 3.51 +- 0.55 | 0.10 |
| wt2_prime | 1152 | 3.24 | 3.54 +- 0.46 | 0.73 | 3.36 | 3.57 +- 0.50 | 0.61 |
| wt3_idx1 | 704 | 3.55 | 3.46 +- 0.63 | 0.41 | 3.22 | 3.34 +- 0.52 | 0.51 |
| wt3_prime | 704 | 2.57 | 3.38 +- 0.49 | 0.98 | 2.96 | 3.35 +- 0.43 | 0.76 |
| wt4_idx1 | 128 | 2.30 | 2.58 +- 0.64 | 0.61 | 2.22 | 2.54 +- 0.68 | 0.67 |
| wt4_prime | 128 | 1.79 | 2.65 +- 0.56 | 0.96 | 1.63 | 2.54 +- 0.48 | 1.00 |

Reading: the only slices with empirical p near 0.04 are q/qall/qfirst against the shuffle null, which is the doublet artifact (p = 0.47-0.71 against the chain null), and Wcum against the chain null (p = 0.04) which is 1 of ~40 slices tested and is driven by a single windowed score on KJV (the control text) with w29 pointers whose cumulative sum overflows int64 (pseudo-random pointers); its output is unreadable (below) and its word-hit z is -1.1. The 4-tuple Self-Reliance slice (TPSWL, the exact 2014 format) is the *worst* slice (real 2.94 vs null 3.78, p = 0.98).

## 8. Best real results, with outputs

Ranked by min(z_shuffle, z_chain) (the first block) and by z_shuffle alone (second block, doublet artifacts). z(150) = recomputed with 150 fresh nulls of each type. Word-hit = share of letters covered by words >= 4 letters from the local vocabulary, vs 30 shuffles.

```
## TOP by min(z_shuffle,z_chain)
KJV w29 Wcum b=0 mod qfirstwin: real=-5.781 z_sh(150)=5.38 z_ch(150)=4.35 [grid: 4.90/5.29] | IoC=2.301 (shuf-null 2.201+-0.065) wordhit=0.011 (null 0.018+-0.006, z=-1.1)
    first200: AWSTYHBNKTTLHIALAASSPBMSHHPAFTMAATHSIGSGTATOJHSMHHATGWOLAOOTFOCOAWFMAATBFSOATSETWHWITRWFHBCALOTPASHAAURGSHNSTADOHWTTEHCOSTWNAIHTTSUIHTIMWMSTHAUUIADRWSTAIATJSOUTYHDTSIBPABTTWSGASBRTIBVTTHAFWASWCTDITTWC
SR_doyle_semi wt2_idx1 TSW b=0 mod qfirstwin: real=-6.272 z_sh(150)=3.25 z_ch(150)=3.39 [grid: 4.15/4.47] | IoC=1.792 (shuf-null 1.843+-0.054) wordhit=0.000 (null 0.016+-0.012, z=-1.3)
    first200: AWWSYHRSWCDTYSCHUDNCTWRSIASWTHMINISMSOFBAHIANTNNICTODHIRRIAIHUTTBGLAMFILITFAHSBIOEBUITWAANIHIIAEMRDBNNLDLIMIHRNAHSDHTGTBSTTOIWCSYMTFANTAGIWFHMNIMSLAITHTHIAAABHSMANCBIWOIETNCORBITPSHNEWBASTSITASHNIMAFA
Blake rprime TSW b=1 mod pmiwin: real=-2.008 z_sh(150)=4.12 z_ch(150)=3.95 [grid: 4.33/4.07] | IoC=1.672 (shuf-null 1.668+-0.024) wordhit=0.659 (null 0.686+-0.016, z=-1.8)
    first200: WEEPBOYTOMOONWEEPSPEAKHAPPYISINAMOFANDLITTLEANDWEEPCLOUDWITHTHEEANDANDBOYHEAVENSBOYANDANDWITHMERRYONSPEAKBYIWEEPSOMYWITHTHYSITSSPRINGWILLIAMSONGSSWEETANDCOMPANIESMERRYTHUSLIKESLEEPINPITYDOSTMADEBENEAT
AL_verse rprime TPS b=1 mod qwin: real=-6.371 z_sh(150)=4.01 z_ch(150)=3.18 [grid: 4.41/3.91] | IoC=4.773 (shuf-null 4.781+-0.069) wordhit=0.035 (null 0.023+-0.005, z=2.3)
    first200: NAADANAADAESAETNHNNNEHEHOHOHOUDHDHHAAOETONNAAONAANOAANUADOHHAHNHAAOAAOASTEAAAEOAHNOSEAAHONADAADSHEANONOUAAATNOTAOAEHNNOAOODATHNNAANEEENOHTOOHEANAAANTOANNAAHNSAAHAAEANAHAAAAOHOAHTAOHTTNENONEAOEOAAAONHN
AL_flat ridx1 Lp b=1 mod qwin: real=-5.995 z_sh(150)=3.66 z_ch(150)=3.64 [grid: 3.87/3.89] | IoC=3.657 (shuf-null 3.664+-0.060) wordhit=0.011 (null 0.028+-0.005, z=-3.7)
    first200: HFTSNHOHHTTNNAMNEHMOSFAFTTONHOANNTFENNAFOFODOFAMANNTHOODTOHHNHHDNHDTNTNHOTFOTNSDNEANEFHADNTHNNMANHNNNOTFANFEOHTTTNNHFAAMNAADTNHTFTTOHNTONHOOHHNFTHMFTNOHNATNONNNHMESTATNDNAOMOFTHHHEDNHHTTANEHNFHATFNHHE
KJV ridx L b=0 mod qwin: real=-5.466 z_sh(150)=3.39 z_ch(150)=3.52 [grid: 3.66/3.99] | IoC=7.257 (shuf-null 7.139+-0.094) wordhit=0.001 (null 0.003+-0.002, z=-0.8)
    first200: GICGEEGIGECENEIEGIIEGGEGCETEGEGGEGGGEGEITGGETGGIEEEEETHECGIEEIGEHIEGEEEEGEITGEGEEGEGGIEEEEEIENIEEEGEGGEIGHIGGEECGENIGGEIGEEEEEEEGCEHEEETNEHTIEHGCEIGIETEEEEGHEEEEIEGIGEHEGEHIEIIEIEGEEEIIEGHGIEGEGIGEEIE
SR_lines isum TPSW b=0 mod pmiwin: real=-2.272 z_sh(150)=4.28 z_ch(150)=4.17 [grid: 4.11/3.66] | IoC=1.708 (shuf-null 1.754+-0.029) wordhit=0.595 (null 0.597+-0.021, z=-0.1)
    first200: FROMADMONITIONALLFROMWHICHMOSESANDBEINPUBERTYENVIABLEANDGROWFACESSEATEDIMADEORIGINALINPITHISWILLWORLDISNOTOBEYINGHIMCANPITDISCONCERTEDHIMWHATONEWITHANOTHERCHILDLIKETHELIGHTANDHISEXTRAANDMUSEEYEBELIEVE
SR_lines ridx1 TPSL b=1 mod qwin: real=-5.659 z_sh(150)=3.46 z_ch(150)=3.18 [grid: 3.61/3.97] | IoC=3.152 (shuf-null 3.181+-0.041) wordhit=0.042 (null 0.038+-0.007, z=0.6)
    first200: ITEISEARSTFREEIREALEELRSNSEELAERREALRRESESSFIESEIIINEAUEEFVIETTUEIRESSSUCTASUIINVSVSUARIIIIASTAILESRUNIRLITIEIREISENIRIRSAETFISREELTEISISETESVVALNNNTSUSVTIVICRIINIESENFISESEREARTSUEILTSISRTIERETNARUIE
AL_flat rprime L b=1 mod qwin: real=-5.995 z_sh(150)=3.83 z_ch(150)=3.05 [grid: 3.60/3.89] | IoC=3.657 (shuf-null 3.641+-0.050) wordhit=0.011 (null 0.028+-0.007, z=-2.6)
    first200: HFTSNHOHHTTNNAMNEHMOSFAFTTONHOANNTFENNAFOFODOFAMANNTHOODTOHHNHHDNHDTNTNHOTFOTNSDNEANEFHADNTHNNMANHNNNOTFANFEOHTTTNNHFAAMNAADTNHTFTTOHNTONHOOHHNFTHMFTNOHNATNONNNHMESTATNDNAOMOFTHHHEDNHHTTANEHNFHATFNHHE
Mab_para gsum TSW b=1 mod pmiwin: real=-2.371 z_sh(150)=4.11 z_ch(150)=3.52 [grid: 3.53/3.89] | IoC=1.724 (shuf-null 1.786+-0.033) wordhit=0.644 (null 0.648+-0.018, z=-0.2)
    first200: SWORDOUTTOWILLWENTOFTHEYHEADAPPLIESOWAINOWAINWOMENTHATTHANISTREETOOFWASWEATHERGOISITANDTHOUISSIRARMSLONGGOWOODSUMMITWILLANDSAWLYRICATEFROMONDIRECTEDONLYSEENINDIDGOWESHEAIIIMANTHOUTHEANDCASTLEACCORDTHE
## TOP by z_shuffle alone (doublet artifact check)
SR_doyle_semi rprime W b=0 mod qfirst: real=-7.265 z_sh(150)=4.12 z_ch(150)=2.11 [grid: 5.17/2.12] | IoC=3.085 (shuf-null 3.098+-0.033) wordhit=0.018 (null 0.010+-0.004, z=1.8)
    first200: TAFWCILTTTFSWSICUTISWSSSFSIITSVWSOSUCWSAISLAISVISISTCITAFLTCCTTAFTAOSTSCLTAIOCWASUSWUACSACTTSWISIIWSWLTAVFAULCTFOSWTSVSIWSSATSFTSFTTCSSIWCTITIFSFFISSCICCSTWTISCIIPWSVTFAWSTISASFTCUACCTSSVFUTCSIVSSSITP
AL_flat ridx S1 b=1 mod q: real=-6.823 z_sh(150)=4.18 z_ch(150)=1.50 [grid: 5.10/1.54] | IoC=8.663 (shuf-null 8.690+-0.013) wordhit=0.085 (null 0.078+-0.007, z=1.0)
    first200: HTHHHAHHHTHHTTTHAHTAHHTHHATHHAHAHAHAHATTTHHATHHTTHHTTTTAHHHTHHHAAHAAHTHTHTTTAHHAHATAATTTAHTHHTTTHAAHAHTTHATAHTTHAHTHHHTTATTATHATHHTTTHATTTTTHAAHHATHTHTTHTTATHHHATAHTHTAAATTTATTAHTAAHTHTAHAAHHHAHTHHAHA
CicadaPGP rprime TPS b=0 raw q: real=-7.305 z_sh(150)=3.42 z_ch(150)=2.45 [grid: 5.06/2.00] | IoC=12.489 (shuf-null 9.883+-1.235) wordhit=0.000 (null 0.000+-0.000, z=nan)
    first200: COCCCCOCCCCCCOCCRCOCCCRRCCCCCOERRCCRCOCCOCOCOCOCCCCCCOCOCCCOR
SR_doyle_semi ridx1 L b=0 mod q: real=-6.416 z_sh(150)=4.00 z_ch(150)=1.77 [grid: 5.03/2.67] | IoC=4.533 (shuf-null 4.411+-0.048) wordhit=0.062 (null 0.058+-0.008, z=0.5)
    first200: MEDADEOOMODOEIODROOMAEIEDARMMMADODERDDIEREOIREAOIMOOERDIDOOEDOMIAOIDOOOEOOERDDAIORIDREEIIDOOOEOIMEDODOOEAAEROEODDOEOEAIODIIIOOEOEDODEOAREEDROEAEDEOEDDREDIODDMODEOEADAOAIDIDOMEDEOERIDEODAAARODEEADEOEOE
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
