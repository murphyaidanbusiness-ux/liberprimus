# RESULTS: laneE_language_id

Lane: identify the most likely plaintext language / register of the 55 unsolved pages from every ciphertext-visible word-level statistic (not only the word-length marginal). Data pin: sha256 matched (12,956 runes, 2,896 words, 175 sentences, 594 lines, 55 pages). All code and outputs are in `SCRATCH/agents/laneE_language_id/`.

## Verdict in plain words

1. **Best supported: English prose (formal or discursive prose is mildly favoured on the word-level score, aphoristic and novel prose on the sentence-level score; the register is not resolved), in which the very frequent short function words THE and OF (and possibly TO, AND) are absent from the word stream, with Cicada's digraph-merging rune transliteration (TH, NG, EA, EO, OE, AE, IA/IO merged into one rune each).** At the word-length level this reproduces the unsolved profile to within the sampling floor: best candidates have JS(length marginal) = 0.0008-0.0015 and JS(length bigram) = 0.005-0.008, against 0.006-0.012 and 0.020-0.036 for ordinary English with THE/OF/TO present.
2. **The ciphertext statistics cannot tell the individual flavours apart.** "-THE/OF", "-THE/OF/TO" and "-THE/OF/TO/AND" are statistically tied (paired bootstrap, 45 English corpora: -THE/OF vs -THE/OF/TO difference +0.002, 95% CI [-0.05, +0.05], -THE/OF better in 22 of 45 corpora). The top registers (Cicero translation, Paine, Emerson, Plato, Agrippa, Gospel of Buddha, Moby Dick, Austen with function words removed) all have overlapping 95% rank intervals (for example ranks 1-16 to 1-60). No register (Emerson versus Plato versus occult versus novel) is separated at the word-length level; what is supported is "English prose with mean word length about 4.4-4.5 after removal of THE/OF", not a specific genre.
3. **Rejected (word-length statistics, bootstrap P(best English variant is closer) >= 0.998 in each case):** unmodified English of any register (2-rune words 23-28% against 15.5% observed; median chi-square 293 against 19-25 for the best removal variants), English verse (Whitman, Milton, Shakespeare), KJV / Douay / Tyndale-style archaic prose, Latin (5 corpora, JS_A 0.019-0.049), Romance (French, Italian, Spanish), Welsh and Irish, Old English (Beowulf and the Sacred-Texts corpus; verse), Gothic, Esperanto, Finnish, Hungarian, Turkish, Estonian, Basque, Maori, and "all function words removed". Old Norse, Icelandic, Faroese, German (Faust and Bible), Swedish and Norwegian are rejected at JS_A 0.007-0.022 and word-level scores 4.7-10 times the best English variant.
4. **Not cleanly excluded by length statistics alone: Dutch and Danish (Bible translations).** Dutch Bible has JS_A = 0.0028 and JS_B = 0.0114, which sit inside Dutch's own window noise (z = 0.0 and +0.6) and is only about 2.4x worse on the combined word-level score than the best English variant; it beats the median English-minus-THE/OF corpus. A direct multinomial chi-square on the 11-bin length histogram still rejects it decisively (chi2 = 72 on 10 df, p = 2e-11, against 19-23 for the best English variants), but a heterogeneous corpus can look fine under a window test. Dutch is excluded in practice by priors (Cicada's solved pages are English, and the rune set is an Anglo-Saxon futhorc), not by this lane's statistics.
5. **Letter-by-letter spelling (no digraph runes) is a clearly weaker second hypothesis than "digraphs merged + THE/OF removed"**: paired word-level difference +0.184, CI [+0.056, +0.306], P(removal variant better) = 0.998; the removal variant is better in 33 of 45 corpora. Merging only TH (and removing THE/OF/TO) is nearly as good as merging all digraphs (+0.063, CI [+0.006, +0.115]); the length data cannot settle which digraphs are merged.
6. **New negative finding (sentence marks):** the 175 "." marks do not behave like English sentence boundaries. In every real text tested, the first word of a sentence is short and the last word is long (z = -2 to -5 for first-word length, with the Gospel of Buddha the exception at -0.3, and +3 to +10 for last-word length, against randomly placed marks; Cicero tr. -4.9/+5.1, Emerson -4.5/+7.3, Plato -3.8/+7.5, Dutch -4.5/+10.6). In the unsolved pages the first and last word lengths are indistinguishable from randomly placed marks (z = -0.4 and -1.1; first mean 4.43, last mean 4.29, overall 4.47), and the sentence-length distribution is a geometric fit to random placement (chi-square 12.0 on 8 df, p = 0.10). So the two sentence-position statistics and sentence length carry no usable language signal, and the ranking below uses the word-level statistics (length marginal and length bigram) as primary. Sentence-level statistics are reported but not trusted.
7. **Implication for the community key sweeps (English-only scorers):** English quadgram and IoC scorers remain valid for the favoured hypothesis. English with THE/OF/TO deleted loses only 0.13 per quadgram (-4.40 -> -4.54, compare noise near -7.5) and keeps rune IoC at 1.76 (normal English 1.78). Non-English plaintext would score -5.3 to -6.5 per quadgram, which sits well below an English acceptance threshold. The real risk is not the scorer but the crib set: any crib or sentence-structure assumption that relies on the word THE (or OF) is useless if the plaintext lacks them. Details at the end.

## What was measured

Word units: the unsolved stream has 2,896 words (global word ids; a word split across a page break counted once), 175 sentences (the "." marks plus the "&", "$", "§" paragraph and section marks, as in the loader), 594 lines. Plaintext candidates are transliterated with Cicada's rules (K->C, V->U, Q->C, Z->S, ING->NG as in the solved pages "THNGS", IO->IA, then greedy digraphs TH NG EA EO OE AE IA); other modes are "letters" (no digraphs) and "TH-only". Þ/ð->TH, æ->AE, œ->OE, accents stripped for foreign languages.

Five discrete statistics, each compared to a candidate by Jensen-Shannon divergence (natural log):

| id | statistic | bins |
|---|---|---|
| A | word-length marginal | 1..10, 11+ (11 bins) |
| B | word-length bigram (length of word i vs word i+1, inside a sentence) | 8x8 with 8+ clipped (64 cells) |
| C | length of the first word of a sentence | 1..6, 7+ |
| D | length of the last word before a "." mark | 1..6, 7+ |
| E | sentence length in words | 10 bins (<=3, <=6, <=9, <=12, <=16, <=21, <=28, <=40, <=60, >60) |

Line statistics (not comparable bin-by-bin to corpora with arbitrary layout) are in the "Lines" section.

Score columns: JS per statistic; "full score" = mean over A-E of JS_s divided by the median of JS_s over all candidates (each statistic gets equal weight; lower is closer); "word-level score" = the same over A and B only. Because the 2,896-word sample has its own noise, three honesty devices are used:
- **Bootstrap**: 1,000 resamples of the 175 unsolved sentences (cluster bootstrap), recomputing all JS for all 906 candidate distributions each time. Reported: standard error of the score, 95% interval of the candidate's rank, and paired-difference intervals for head-to-head claims (absolute bootstrap JS is biased upward by resampling with duplicates, so differences, ranks and standard errors are used instead of absolute percentile intervals).
- **Own-corpus window null** (z column): for each candidate 100 contiguous windows of the same size (2,896 words for A, B; 175 sentences for C, D, E) are drawn from the candidate corpus itself and scored against the whole-corpus distribution. z = (JS_obs - mean_window) / sd_window. z near 0 means the unsolved is as close to the candidate as a random same-size slice of the candidate is to itself. This is generous for heterogeneous corpora (Bible, Gospel of Buddha, Web text), so it is used for calibration, not for ranking.
- **Direct chi-square** on the length histogram (df = 10) for the marginal alone.

Candidate set: 906 candidate distributions of at least 15,000 words (84 unmodified corpora plus 822 synthetic variants, 16 per English non-verse corpus), plus 9 small English corpora (under 15,000 words) listed separately. The "full" rank covers corpora with at least 200 sentences and mean sentence length 3-60 words; Latin Vulgate, Italian and Maori Bibles lack sentence punctuation and are ranked on A and B only.

### Corpora used and fetch log

English, from the repos: Moby Dick; Plato Republic, Symposium, Timaeus; Emerson Essays I and II, Self-Reliance; Agrippa Occult Philosophy I-III; Blavatsky Secret Doctrine I; Crowley Book of Lies, Book of the Law, Liber 777; Manly Hall; Levi; Lovecraft (2); Poe; Mabinogion (Guest); Homer Odyssey (Butler); Dante (Longfellow); KJB books (Genesis, Psalms, Job, Isaiah, Ezekiel, John, Revelation, Ecclesiastes), the whole KJV, Tyndale NT, Douay-Rheims; Tao Te Ching (Legge); Bhagavad Gita (Arnold); Upanishads (Hume); Gospel of Buddha (Carus); Nietzsche Twilight of the Idols; Kant; Schopenhauer; Leibniz; Bacon; Aristotle; Mill; Paine; Cicero Tusculan Disputations and Suetonius (English translations; Lane C noted the repo labels them as Latin but they are English); Lucretius (English); Gibbon; Bunyan; Shelley; Stoker; Voltaire; De Quincey; Magna Carta. From the NLTK data repo (raw.githubusercontent.com): Whitman, Blake, Milton, Hamlet, Macbeth, Austen Emma, Carroll Alice, Chesterton. English UD web treebank (EWT). Cicada's own texts: LP1 solved text (729 words), 2012-13 puzzle texts (314 words), koans (752 words): only LP1 is used, as a reference (too short to rank).

Other languages fetched (all via raw.githubusercontent.com or `git clone` of public repos, which also works through the proxy): Bible corpus (christos-c/bible-corpus) for Esperanto, Finnish, Hungarian, Turkish, Dutch, French, Italian, Spanish, Latin (Vulgate), German, Norwegian, Swedish, Danish, Maori and modern English; Universal Dependencies treebanks for Gothic (Wulfila Bible, PROIEL), Welsh (CCG), Icelandic (IcePaHC, historical), Faroese (FarPaHC), Irish, Basque, Estonian, Latin (PROIEL); Old Norse sagas (cltk/old_norse_text_perseus, 381k words); Old English poetry and psalms (cltk/old_english_text_sacred_texts, 147k words, plus the repo's Beowulf); Latin Newton, Caesar, Virgil; German Faust.

Fetch failures or gaps (no further time spent): Welsh Bible (404; the Welsh treebank is only 24k words of modern Welsh), Old English prose (no source reachable; UD Old English repos 404, Anglo-Saxon Chronicle not found; the Old English set is entirely verse plus metrical psalms), Old Norse UD (404; sagas used instead), Middle English (none found), Zen koan collections (Gateless Gate, Blue Cliff Record), Corpus Hermeticum and Nag Hammadi (not found; Crowley, Agrippa, Blavatsky, Manly Hall, Levi, Gospel of Buddha, Upanishads and Gita are the nearest mystic/occult registers), Project Gutenberg itself (blocked). Crowley, Manly Hall, Blake, Magna Carta and the shorter KJB books are under 15,000 words and are listed unranked below.

## Results

### Table 1. Raw marginals (what the data look like)

{{final_tables_marginals.md}}

The unsolved profile is a long-word text (mean 4.47 runes) with very few 1-rune words (2.9%), a small 2-rune class (15.5%, against 23-28% in ordinary Cicada-transliterated English) and almost no adjacent 2-2 pairs (2.2%; "OF THE", "IN THE", "TO THE" give 4.8-5.4% in unmodified English). The adjacent 2-2 bigram cell is the single clearest second-order signature: it supports "THE/OF/TO are absent" over any explanation that merely rescales the length distribution. Last-word and first-word means are discussed under "Sentence marks".

### Table 2. Ranked candidates (individual corpus x variant)

Score columns as defined above; "rank 95% interval" is the 2.5th-97.5th percentile of the candidate's rank among all 906 candidates over the bootstrap. The z columns are against each candidate's own-corpus window null.

{{final_tables_ranked.md}}

Reading Table 2: a block of about 40 English variants (THE/OF/(TO/AND) removed; Moby Dick, Gospel of Buddha, Bhagavad Gita, Austen, Cicero, Paine, Emerson, Plato, Agrippa, Poe, Web text) have overlapping rank intervals; the full score prefers corpora with short-sentence novels and aphoristic texts (Moby Dick, Gospel of Buddha, Gita) because their sentence statistics happen to resemble the unsolved marks, which finding 6 says is not meaningful; the word-level score prefers formal philosophical prose (Cicero tr., Paine, Emerson, Plato). Neither orders registers with any confidence.

### Table 3. Best non-English natural corpora

{{final_tables_nonEN.md}}

The Germanic Bibles (Dutch, Danish, Swedish) are the only non-English texts that come within a factor of 2.4-4.7 of the best English variant on the word-level score; Romance, Latin, Celtic, Finnic, Hungarian, Turkic, Basque and Oceanic texts are 10-30 times worse (JS_A 0.018-0.073). Old Norse sagas, Icelandic, German Faust and Old English verse: JS_A 0.010-0.017.

### Table 4. Best unmodified English corpora

{{final_tables_enNat.md}}

Even the closest unmodified English (Bhagavad Gita, Moby Dick, Austen, Web text) has JS_A = 0.006-0.007 (z_A = +1 to +8) and JS_B = 0.020-0.022, three to seven times the removal variants. Their apparent full-score lead comes entirely from statistics C, D, E.

### Table 5. Head-to-head, English synthetic variants (45 English corpora, 30k+ words each, paired bootstrap)

{{pairs_variants.md}}

Chi-square goodness of fit of the length histogram alone (df = 10, critical 18.3):

{{chiA.md}}

No candidate reaches a comfortable fit on a strict chi-square (best 18.7, p = 0.04), which is expected because a single corpus is never exactly the author's distribution, but the ordering is stable: removal variants 19-25 at best and a median of 99-107, letters 121, unmodified English 293, Dutch 72, every other language 150-6000.

### Table 6. Class level (best member of each class, bootstrap probability that it is the overall best)

{{pairs_class.md}}

The class table is biased in favour of classes with many members (45 English corpora against 1-12 for the others), so median-of-class is shown next to the best. Using medians, Dutch (0.40) is better than the median English-minus-THE/OF corpus (0.57); this is the reason finding 4 declines to call Dutch excluded by length data alone.

### Table 7. Which words must be removed? Greedy search on pooled English

Ten English prose corpora (564k words), top-45 frequent words as candidates, greedy forward removal of the word that most reduces the word-level objective (mean of normalised JS_A and JS_B) against the unsolved pages:

{{greedy_tab.md}}

THE and OF are the first two words chosen under Cicada digraphs and under TH-only merging in the pooled search, and in all four single-corpus searches (Plato, Moby Dick, Emerson, Cicero; Moby Dick picks THE then OF then I, Emerson/Cicero pick TO third, Cicero AND fourth). The third removal is corpus-dependent and modest (IN, 0.036, in the pooled search; I, TO, TO in the single-corpus searches with gains 0.07-0.13, i.e. 1.5-3 bootstrap standard errors of about 0.04-0.05); every removal after the third changes the objective by less than 0.04, so nothing beyond THE + OF (+ one more short word) is individually resolved, and the cross-corpus paired test above finds -THE/OF and -THE/OF/TO tied. Under letter-by-letter spelling the search starts much lower (0.427, because THE is a 3-rune word there) and chooses OF first; it never reaches the digraph-variant optimum (0.232 against 0.148 after eight removals) and has a worse bigram fit (JS_B 0.0086 against 0.0054-0.0068).

### Sentence marks: first word, last word, sentence length

(`marks.py`, `marks_out.txt`.) Unsolved: overall mean word length 4.474, first-word mean 4.429, last-word mean 4.291. Under 5,000 random placements of 174 interior marks among the 2,895 word gaps, first mean 4.49 +- 0.17 and last mean 4.47 +- 0.17, so z = -0.38 and -1.06; the fraction of first words of length 2 (0.183 vs 0.154 +- 0.026), of last words of length 2 (0.160) and of length 7+ (0.200 and 0.160) are all inside the random band (|z| <= 1.1). Real texts with real punctuation, 175-sentence windows against the same random-placement null, mean z(first), z(last): Cicero tr. -4.9/+5.1; Emerson -4.5/+7.3; Moby Dick -3.8/+3.8; Plato -3.8/+7.5; Agrippa -2.2/+3.0; Gospel of Buddha -0.3/+4.2; Dutch Bible -4.5/+10.6. Sentence length: unsolved mean 16.5, sd 14.7 (CV 0.89); chi-square against the geometric distribution implied by random placement is 12.0 on 8 df (p = 0.10 by simulation). English windows have CV 0.73-1.0, so sentence length per se does not discriminate, but the position effect (short first words, long last words) does, and the unsolved pages do not show it.

Interpretation (not proven): either the "." marks in the transcription are not sentence terminators in the plaintext sense (they may be inserted, positional or cipher-mapped marks), or the plaintext follows an unusual syntax in which sentences start and end on words of average length. A related observation: the marks are strongly coupled to the line layout. Of 164 sentence changes, 16.5% fall exactly at a line end (5.1% expected if marks fell at random rune positions), and the mean relative position in the line is 0.636 (expected 0.52; z about +5), histogram over fifths of the line [10, 25, 37, 35, 57]. This is a typesetting/transcription property, not a language property.

### Lines

(`extra.py`, `extra_out.txt`.) 594 lines of 21.8 +- 2.6 runes (interior lines 22.0 +- 2.3; CV 0.11). Of 539 internal line breaks, 72.0% fall inside a word and only 28.0% at a word boundary (a uniformly random break position would give 22.4% at a boundary; the excess, 28.0 vs 22.4, is z about +3, so scribes mildly prefer word boundaries but do not require them). The text is therefore justified, hyphenless prose in a fixed-width column, not verse. Every verse corpus breaks lines at word boundaries 100% of the time, with line lengths in runes of mean 24-37 and CV 0.11-0.41 (Beowulf 35.0, CV 0.32; Faust 28.5, CV 0.34; Whitman CV 0.36; Hamlet CV 0.30; Virgil CV 0.12 and Milton CV 0.11, but those still end on word boundaries). Old English verse and Latin verse are rejected on line structure independently of the word-length results. Line-length CV cannot distinguish prose languages from each other.

### Cicada's own solved text (LP1) as a reference

(`final_tables.py`, `extra.py`.) LP1 solved text has 729 words, 4.08 mean runes, 7.1 words per line-sentence (very aphoristic), 2-rune words about 24% (THE 6.6%, OF 1.3%, TO 3.3% of tokens). It is too short to be a decisive comparison.

{{final_tables_lp1.md}}

Length marginal: LP1 as written differs from the unsolved marginal by JS_A 0.0091, 1.4 sd above the 729-word floor of 0.0046 +- 0.0033 (not significant at this sample size); with THE/OF/TO deleted it is inside the floor (0.0030). Length bigram: LP1 as written is 4.5 sd above its floor (0.0496 against 0.0184 +- 0.0069, because it contains ordinary OF THE / IN THE pairs), with THE/OF/TO deleted 1.8 sd (0.0309), letter-by-letter 0.8 sd (0.0243). So LP1 is too short to discriminate between the removal and letter-by-letter hypotheses, is directionally consistent with the removal hypotheses, and as written (with THE) does not reproduce the unsolved bigram profile. LP1 is aphoristic (mean 7 words per line-sentence) while the unsolved sentences average 16.5 words, so the register differs from LP1 even if the author is the same.

### Zero-increment symbol candidates (link to the brief's chain-cipher families)

The brief's chain families require the zero-increment symbol to have the observed doublet rate, 86/12,955 = 0.66% (95% CI 0.52-0.80%). In English transliterated with Cicada rules, averaged over 8 prose corpora, the only symbols whose share falls in that interval are EA (0.69%; 0.74% when THE/OF/TO are removed) and IA (0.58%; 0.62%). Under letter-by-letter spelling only K (0.59-0.64%) falls in the interval. The rarer runes J, X, EO, OE, AE are far too rare (0.02-0.23%) and NG (0.85-0.92%) is just above. So EA or IA are the right candidates for the zero-increment letter under the favoured hypothesis; K, the letter Lane C suggested for the letter-by-letter hypothesis, only works if there are no digraph runes, which Table 5 disfavours.

## Implications for the community key sweeps (English-only scorers)

Scorers tested (`scorers.py`): the dukotah english_quadgrams table (log10 probability per quadgram) and rune IoC (x29, 1.0 random), on 13k-rune windows (30 per condition), eight English corpora averaged:

{{scorers_tab.md}}

1. **The English quadgram scorer is still valid for the favoured plaintext.** Removing THE costs 0.12 per quadgram, removing THE/OF/TO 0.13, THE/OF/TO/AND 0.19 (against a gap of about 3.0 to random noise at -7.5, and 0.7-2.0 to the non-English languages tested). A sweep whose acceptance threshold is around -5.0 to -5.5 per quadgram would still pass English-minus-THE/OF/TO plaintext (-4.4 to -4.6) but would reject German, Dutch, Latin, Old Norse and anything else non-English (-5.3 to -6.5 per quadgram) if those thresholds are tight. Because the sweeps are English-only, they would fail silently on non-English plaintext; this lane finds that unlikely, not impossible (Dutch/Danish word lengths are not excluded by A and B alone).
2. **IoC detection still works.** Rune IoC of English-minus-THE/OF/TO is 1.76 (normal 1.78). Letter-by-letter English would give 1.95 (digraphs unmerged: a 26-symbol text mapped on 29 symbols), higher, which does not hurt an "IoC above x" filter but would push the "English around 1.7-1.8" window the brief gives; any IoC band test with an upper bound near 1.85 would reject a letter-by-letter plaintext. Latin, German, Dutch, Gothic and Finnish plaintext give 1.9-2.55.
3. **What does break: THE-based cribs.** If THE and OF are absent from the plaintext (JS_A 0.0008-0.0015 against 0.0059 with them present, 2-2 pairs 2.2% against 4.8-5.4%), any crib, word-frequency scorer or dictionary-word score weighted towards THE, OF, or "OF THE" patterns will rank true plaintext below chance candidates; and a scorer calibrated on "THE" counts as a reward will penalise it. Scorers based on quadgrams of the whole stream are robust (above); scorers that count dictionary words are robust only if THE/OF are not in the scored list.
4. **Word boundaries are informative and should be used**: with the removal hypothesis, the plaintext word-length sequence is a predictable stream (mean 4.47, 2-rune 15.5%, 3-rune 24.9%, almost no 2-2 neighbours). A candidate key whose decrypted text has word lengths that look like ordinary English (23-28% two-letter words, "OF THE" patterns) is evidence against that key, not for it.
5. **Sentence marks should not be used as sentence structure** (finding 6): for example a key restarted at sentence starts, or a scorer that rewards sentence-initial function words ("THE", "IT", "IN") or sentence-final nouns, will score the true plaintext at random level, since in the unsolved layout the first and last words of "sentences" have average length.

## Caveats

- The word-length statistics describe the plaintext only if the ciphertext word boundaries are the plaintext word boundaries. Every result is conditional on that; the profile match to English-minus-THE/OF is itself evidence for that condition.
- Corpora are not the author's text: genre variation among English prose alone puts JS_A between 0.0008 and 0.0024 for the best variants, and strict chi-square never gets above p = 0.04; differences below that scale (THE/OF vs THE/OF/TO vs +AND, or Emerson vs Paine) are not resolved. Window-null z values are generous for heterogeneous corpora (Bible, Web, Gospel of Buddha).
- The 175-sentence samples make C, D, E noisy (n = 175), and the unsolved marks are unlike English sentence boundaries in any case, so the "full" rank mostly adds noise; the word-level rank is the headline.
- The archaic variant (thou/thee/-eth, hath) is a regex approximation applied to modern text and barely changes lengths (JS_A moves by less than 0.0005); archaic spelling is therefore neither supported nor refuted. Real KJV-style archaic prose is rejected at JS_A 0.012-0.016 because KJV has THE/OF/AND and short Anglo-Saxon words, not because of thee/thou.
- ING->NG and IO->IA follow the solved pages; keeping ING changes the word-level score by 0.07 at most (Table 5, "base, ING kept").
- No Old English prose, Middle English, Zen, Hermetic or Gnostic corpora could be fetched; Old English is represented by verse and psalms, which are also excluded by line layout.
- The Bible-corpus texts have uneven punctuation (Latin Vulgate, Italian, Maori have almost none); they are ranked on A and B only.

## Files (all in `SCRATCH/agents/laneE_language_id/`)

`corpora.py` (loaders, normalisation, 94 corpora), `variants.py` (16 synthetic English transformations, function-word list, archaic regex), `stats.py` (transliteration lengths, the five statistics, unsolved loader), `run_main.py` (scores every candidate against the unsolved pages, 100-window own-corpus null; `run_main.log`, `results_main.pkl`), `boot.py` (1,000-replicate cluster bootstrap; `boot.pkl`), `tables.py`, `final_tables.py`, `pairs.py` (paired variant and class comparisons), `chiA.py`, `greedy.py`, `scorers.py`, `marks.py`, `extra.py`, `runefreq.py`, `assemble.py` (builds this file from `results_template.md`), and the data caches in `corp/`.
