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

| text | mean word len (runes) | 1-rune | 2-rune | 3-rune | 8+ rune | mean sentence len (words) | sentences <=3 words | mean first-word len | mean last-word len | adjacent 2-2 pairs |
|---|---|---|---|---|---|---|---|---|---|---|
| UNSOLVED (2,896 words, 175 sentences) | 4.47 | 2.9 | 15.5 | 24.9 | 11.8 | 16.5 | 14.3 | 4.43 | 4.29 | 2.2 |
| Cicero Tusculan (English tr.) [-THE/OF/TO] | 4.49 | 3.2 | 15.2 | 25.4 | 12.9 | 22.7 | 17.1 | 3.62 | 5.30 | 2.0 |
| Emerson Essays I [-THE/OF/TO] | 4.44 | 3.3 | 15.7 | 25.3 | 11.6 | 17.9 | 3.1 | 3.71 | 5.58 | 2.0 |
| Moby Dick [-THE/OF] | 4.37 | 3.5 | 15.1 | 23.6 | 10.0 | 18.3 | 19.6 | 3.87 | 4.99 | 2.1 |
| Moby Dick [base (Cicada rules)] | 4.13 | 3.2 | 23.4 | 21.3 | 9.0 | 20.2 | 18.6 | 3.61 | 4.98 | 4.8 |
| Moby Dick [letters (no digraphs)] | 4.41 | 3.2 | 16.3 | 22.9 | 11.0 | 20.2 | 18.6 | 3.85 | 5.19 | 1.9 |
| Plato Republic (Jowett) [base (Cicada rules)] | 4.06 | 2.7 | 27.8 | 21.9 | 10.0 | 24.1 | 13.9 | 3.39 | 5.61 | 5.4 |
| Dutch: bible-corpus | 4.36 | 2.0 | 18.6 | 25.9 | 10.8 | 14.7 | 2.9 | 3.59 | 6.09 | 2.3 |
| Danish: bible-corpus | 4.17 | 2.7 | 18.9 | 28.3 | 8.0 | 21.9 | 2.7 | 3.43 | 5.17 | 2.6 |
| Latin: Newton Principia | 5.22 | 6.0 | 19.6 | 11.7 | 23.9 | 13.7 | 43.5 | 4.04 | 4.62 | 5.5 |
| Old English: Beowulf | 3.97 | 4.1 | 22.0 | 20.8 | 4.9 | 5.6 | 61.7 | 3.34 | 3.03 | 4.1 |
| German: Faust | 4.80 | 0.5 | 9.8 | 28.4 | 13.0 | 8.2 | 39.0 | 4.87 | 6.36 | 0.7 |
| Welsh: CCG treebank | 4.32 | 11.3 | 19.6 | 14.7 | 13.2 | 17.6 | 0.9 | 3.89 | 5.61 | 2.5 |

The unsolved profile is a long-word text (mean 4.47 runes) with very few 1-rune words (2.9%), a small 2-rune class (15.5%, against 23-28% in ordinary Cicada-transliterated English) and almost no adjacent 2-2 pairs (2.2%; "OF THE", "IN THE", "TO THE" give 4.8-5.4% in unmodified English). The adjacent 2-2 bigram cell is the single clearest second-order signature: it supports "THE/OF/TO are absent" over any explanation that merely rescales the length distribution. Last-word and first-word means are discussed under "Sentence marks".

### Table 2. Ranked candidates (individual corpus x variant)

Score columns as defined above; "rank 95% interval" is the 2.5th-97.5th percentile of the candidate's rank among all 906 candidates over the bootstrap. The z columns are against each candidate's own-corpus window null.

**Table 2a. Top 25 individual candidates, full score (mean of the 5 JS divergences, each divided by its median over all candidates; lower = closer)**

| # | candidate (corpus [variant]) | words | mean len | score ± boot SE | rank 95% interval | JS A len | JS B bigram | JS C first | JS D last | JS E sent-len | z vs own-corpus window null (A,B,C,D,E) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Moby Dick [-THE/OF] | 195k | 4.37 | 0.33 ± 0.08 | 1-21 | 0.0017 | 0.0081 | 0.0083 | 0.0198 | 0.0166 | -0.5 +0.6 -0.3 +0.2 -0.3 |
| 2 | Moby Dick [TH-only -THE/OF/TO] | 190k | 4.57 | 0.34 ± 0.07 | 1-22 | 0.0018 | 0.0082 | 0.0058 | 0.0258 | 0.0159 | -0.2 +1.2 -0.4 +0.5 -0.4 |
| 3 | Gospel of Buddha (Carus) [-THE/OF] | 77k | 4.49 | 0.34 ± 0.07 | 1-35 | 0.0010 | 0.0072 | 0.0040 | 0.0293 | 0.0230 | -0.8 -0.7 -1.1 -0.4 -1.3 |
| 4 | Moby Dick [archaic -THE/OF/TO] | 190k | 4.42 | 0.34 ± 0.08 | 2-28 | 0.0022 | 0.0086 | 0.0082 | 0.0204 | 0.0159 | +0.1 +1.0 -0.3 +0.4 -0.3 |
| 5 | Bhagavad Gita (Arnold) [-THE/OF] | 21k | 4.44 | 0.35 ± 0.07 | 1-20 | 0.0027 | 0.0089 | 0.0077 | 0.0232 | 0.0100 | -0.2 +0.0 -0.6 +0.1 -0.7 |
| 6 | Moby Dick [-THE/OF/TO] | 190k | 4.42 | 0.35 ± 0.08 | 3-30 | 0.0023 | 0.0088 | 0.0083 | 0.0202 | 0.0159 | +0.1 +1.2 -0.3 +0.4 -0.4 |
| 7 | Gospel of Buddha (Carus) [archaic -THE/OF/TO] | 75k | 4.56 | 0.36 ± 0.07 | 1-47 | 0.0014 | 0.0068 | 0.0043 | 0.0300 | 0.0251 | -0.8 -0.7 -1.1 -0.3 -1.4 |
| 8 | Gospel of Buddha (Carus) [-THE/OF/TO] | 75k | 4.56 | 0.36 ± 0.07 | 3-49 | 0.0015 | 0.0069 | 0.0043 | 0.0300 | 0.0251 | -0.7 -0.6 -1.1 -0.4 -1.2 |
| 9 | Moby Dick [-THE] | 202k | 4.29 | 0.36 ± 0.08 | 2-38 | 0.0022 | 0.0107 | 0.0083 | 0.0196 | 0.0176 | -0.0 +1.7 -0.2 +0.6 -0.2 |
| 10 | Moby Dick [-THE/OF/TO/AND] | 184k | 4.47 | 0.36 ± 0.08 | 3-35 | 0.0031 | 0.0103 | 0.0068 | 0.0202 | 0.0154 | +0.7 +1.6 -0.3 +1.3 -0.4 |
| 11 | Bhagavad Gita (Arnold) [archaic -THE/OF/TO] | 20k | 4.50 | 0.37 ± 0.07 | 3-31 | 0.0032 | 0.0093 | 0.0078 | 0.0234 | 0.0122 | +0.0 +0.2 -0.5 +0.2 -0.2 |
| 12 | Bhagavad Gita (Arnold) [-THE/OF/TO] | 20k | 4.50 | 0.38 ± 0.07 | 4-34 | 0.0033 | 0.0096 | 0.0078 | 0.0232 | 0.0122 | +0.2 +0.5 -0.6 +0.4 -0.0 |
| 13 | Gospel of Buddha (Carus) [-THE/OF/TO/A] | 74k | 4.63 | 0.38 ± 0.07 | 1-59 | 0.0018 | 0.0083 | 0.0039 | 0.0291 | 0.0267 | -0.8 -0.6 -1.2 -0.3 -1.2 |
| 14 | Austen Emma [-THE/OF/TO/AND/A/IN] | 136k | 4.40 | 0.39 ± 0.08 | 1-60 | 0.0024 | 0.0080 | 0.0125 | 0.0194 | 0.0209 | +0.9 +1.2 +0.3 +3.2 +1.2 |
| 15 | Bhagavad Gita (Arnold) [-THE] | 22k | 4.34 | 0.40 ± 0.07 | 4-43 | 0.0034 | 0.0126 | 0.0090 | 0.0230 | 0.0077 | -0.0 +0.4 -0.3 +0.1 -0.7 |
| 16 | Bhagavad Gita (Arnold) [-THE/OF/TO/A] | 20k | 4.53 | 0.40 ± 0.07 | 9-45 | 0.0039 | 0.0116 | 0.0068 | 0.0231 | 0.0125 | +0.2 +0.5 -0.6 +0.3 -0.0 |
| 17 | Bhagavad Gita (Arnold) [TH-only -THE/OF/TO] | 20k | 4.66 | 0.40 ± 0.07 | 8-53 | 0.0030 | 0.0100 | 0.0072 | 0.0301 | 0.0122 | -0.0 +0.4 -0.6 +0.7 -0.0 |
| 18 | Moby Dick [-THE/OF/TO/A] | 186k | 4.51 | 0.40 ± 0.08 | 5-66 | 0.0041 | 0.0115 | 0.0073 | 0.0208 | 0.0155 | +1.2 +1.7 -0.3 +0.6 -0.3 |
| 19 | Gospel of Buddha (Carus) [-THE] | 81k | 4.38 | 0.41 ± 0.07 | 5-71 | 0.0024 | 0.0146 | 0.0038 | 0.0271 | 0.0188 | -0.5 +0.2 -1.1 -0.4 -1.5 |
| 20 | Austen Emma [-THE/OF/TO/A] | 143k | 4.31 | 0.41 ± 0.08 | 2-73 | 0.0028 | 0.0096 | 0.0131 | 0.0195 | 0.0177 | +1.1 +1.8 +0.3 +3.7 +0.5 |
| 21 | Austen Emma [TH-only -THE/OF/TO] | 146k | 4.37 | 0.41 ± 0.08 | 2-67 | 0.0022 | 0.0085 | 0.0145 | 0.0228 | 0.0170 | +0.9 +1.8 +0.8 +4.8 +0.7 |
| 22 | Bhagavad Gita (Arnold) [-THE/A/AN] | 22k | 4.37 | 0.42 ± 0.07 | 9-53 | 0.0041 | 0.0146 | 0.0080 | 0.0229 | 0.0075 | +0.1 +0.5 -0.6 +0.2 -0.7 |
| 23 | Paine Age of Reason [-THE/OF/TO] | 63k | 4.55 | 0.42 ± 0.08 | 4-63 | 0.0010 | 0.0062 | 0.0074 | 0.0286 | 0.0412 | -0.7 -0.3 -0.2 +1.2 +3.1 |
| 24 | Paine Age of Reason [archaic -THE/OF/TO] | 63k | 4.55 | 0.42 ± 0.08 | 4-65 | 0.0011 | 0.0062 | 0.0075 | 0.0286 | 0.0412 | -0.6 -0.1 -0.3 +1.1 +3.1 |
| 25 | Moby Dick [-THE/A/AN] | 196k | 4.37 | 0.42 ± 0.08 | 7-83 | 0.0042 | 0.0136 | 0.0073 | 0.0202 | 0.0169 | +1.4 +2.5 -0.3 +0.5 -0.3 |

**Table 2b. Top 25 individual candidates, word-level score only (A length marginal + B length bigram)**

| # | candidate (corpus [variant]) | words | mean len | score ± boot SE | rank 95% interval | JS A len | JS B bigram | JS C first | JS D last | JS E sent-len | z vs own-corpus window null (A,B,C,D,E) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Cicero Tusculan (English tr.) [-THE/OF/TO] | 161k | 4.49 | 0.17 ± 0.04 | 1-16 | 0.0010 | 0.0054 | 0.0245 | 0.0328 | 0.0387 | -0.8 -0.4 +0.4 +0.9 +1.0 |
| 2 | Cicero Tusculan (English tr.) [archaic -THE/OF/TO] | 161k | 4.49 | 0.17 ± 0.04 | 1-21 | 0.0010 | 0.0056 | 0.0245 | 0.0328 | 0.0387 | -0.8 -0.4 +0.4 +0.9 +1.0 |
| 3 | Cicero Tusculan (English tr.) [-THE/OF/TO/AND] | 155k | 4.55 | 0.19 ± 0.05 | 1-30 | 0.0014 | 0.0051 | 0.0184 | 0.0328 | 0.0339 | -0.5 -0.5 +0.1 +0.9 +0.6 |
| 4 | Emerson Essays I [-THE/OF/TO] | 64k | 4.44 | 0.19 ± 0.04 | 1-30 | 0.0008 | 0.0068 | 0.0131 | 0.0488 | 0.0430 | -0.4 +1.7 +1.3 +20.2 +8.3 |
| 5 | Paine Age of Reason [-THE/OF/TO] | 63k | 4.55 | 0.19 ± 0.04 | 2-22 | 0.0010 | 0.0062 | 0.0074 | 0.0286 | 0.0412 | -0.7 -0.3 -0.2 +1.2 +3.1 |
| 6 | Paine Age of Reason [archaic -THE/OF/TO] | 63k | 4.55 | 0.19 ± 0.04 | 2-25 | 0.0011 | 0.0062 | 0.0075 | 0.0286 | 0.0412 | -0.6 -0.1 -0.3 +1.1 +3.1 |
| 7 | Emerson Essays I [archaic -THE/OF/TO] | 64k | 4.44 | 0.19 ± 0.04 | 1-38 | 0.0009 | 0.0070 | 0.0132 | 0.0489 | 0.0430 | -0.3 +2.1 +1.0 +18.3 +8.5 |
| 8 | Agrippa Occult Phil I [-THE/OF] | 57k | 4.50 | 0.20 ± 0.04 | 1-34 | 0.0009 | 0.0074 | 0.0060 | 0.0341 | 0.0566 | -0.7 +0.4 -0.6 +2.4 +0.5 |
| 9 | Emerson Essays II [-THE/OF/TO] | 50k | 4.49 | 0.21 ± 0.04 | 5-35 | 0.0009 | 0.0073 | 0.0144 | 0.0575 | 0.0507 | +0.2 +3.6 +2.0 +17.3 +9.3 |
| 10 | Plato Republic (Jowett) [archaic -THE/OF/TO] | 185k | 4.42 | 0.21 ± 0.04 | 2-41 | 0.0010 | 0.0073 | 0.0282 | 0.0481 | 0.0223 | -0.8 +0.1 +2.4 +5.9 -0.4 |
| 11 | Emerson Essays II [archaic -THE/OF/TO] | 50k | 4.49 | 0.21 ± 0.04 | 5-38 | 0.0010 | 0.0073 | 0.0144 | 0.0575 | 0.0507 | +0.1 +3.3 +1.8 +15.6 +9.6 |
| 12 | Plato Republic (Jowett) [-THE/OF/TO] | 185k | 4.42 | 0.21 ± 0.04 | 2-45 | 0.0010 | 0.0073 | 0.0282 | 0.0481 | 0.0223 | -0.7 -0.0 +1.5 +4.6 -0.4 |
| 13 | Gospel of Buddha (Carus) [-THE/OF] | 77k | 4.49 | 0.21 ± 0.05 | 1-46 | 0.0010 | 0.0072 | 0.0040 | 0.0293 | 0.0230 | -0.8 -0.7 -1.1 -0.4 -1.3 |
| 14 | Poe Complete Works [-THE/OF/TO/A] | 377k | 4.64 | 0.21 ± 0.05 | 1-51 | 0.0014 | 0.0062 | 0.0157 | 0.0348 | 0.0151 | -0.8 -0.6 -0.2 +0.8 -0.6 |
| 15 | Emerson Essays I [TH-only -THE/OF/TO] | 64k | 4.56 | 0.22 ± 0.04 | 7-44 | 0.0012 | 0.0074 | 0.0114 | 0.0571 | 0.0430 | +0.4 +2.4 +0.9 +25.3 +8.4 |
| 16 | Gospel of Buddha (Carus) [archaic -THE/OF/TO] | 75k | 4.56 | 0.22 ± 0.05 | 1-57 | 0.0014 | 0.0068 | 0.0043 | 0.0300 | 0.0251 | -0.8 -0.7 -1.1 -0.3 -1.4 |
| 17 | Gospel of Buddha (Carus) [-THE/OF/TO] | 75k | 4.56 | 0.23 ± 0.05 | 2-61 | 0.0015 | 0.0069 | 0.0043 | 0.0300 | 0.0251 | -0.7 -0.6 -1.1 -0.4 -1.2 |
| 18 | English: EWT (web) [-THE/OF/TO/A] | 154k | 4.54 | 0.23 ± 0.05 | 1-61 | 0.0012 | 0.0075 | 0.0132 | 0.0242 | 0.0364 | -0.9 -0.6 -0.3 +0.9 +0.3 |
| 19 | Plato Symposium [-THE/OF/TO] | 30k | 4.41 | 0.23 ± 0.04 | 4-69 | 0.0014 | 0.0070 | 0.0230 | 0.0428 | 0.0450 | -1.1 -0.6 +0.4 +1.5 +1.1 |
| 20 | Plato Symposium [archaic -THE/OF/TO] | 30k | 4.41 | 0.23 ± 0.04 | 5-70 | 0.0015 | 0.0071 | 0.0229 | 0.0428 | 0.0450 | -1.0 -0.5 +0.5 +1.8 +1.1 |
| 21 | Cicero Tusculan (English tr.) [TH-only -THE/OF/TO] | 161k | 4.62 | 0.23 ± 0.05 | 5-66 | 0.0016 | 0.0069 | 0.0226 | 0.0433 | 0.0387 | -0.4 +0.0 +0.3 +2.3 +1.3 |
| 22 | Plato Republic (Jowett) [TH-only -THE/OF/TO] | 185k | 4.54 | 0.23 ± 0.05 | 8-53 | 0.0013 | 0.0077 | 0.0260 | 0.0566 | 0.0223 | -0.7 +0.1 +1.2 +6.6 -0.4 |
| 23 | Agrippa Occult Phil I [archaic -THE/OF/TO] | 55k | 4.56 | 0.24 ± 0.05 | 5-58 | 0.0013 | 0.0077 | 0.0065 | 0.0346 | 0.0533 | -0.4 +0.3 -0.5 +2.3 +0.2 |
| 24 | Emerson Essays I [-THE/OF/TO/AND] | 61k | 4.51 | 0.24 ± 0.06 | 3-59 | 0.0016 | 0.0070 | 0.0126 | 0.0488 | 0.0438 | +1.0 +2.1 +1.1 +17.0 +9.5 |
| 25 | Agrippa Occult Phil III [-THE/OF] | 71k | 4.58 | 0.24 ± 0.05 | 5-66 | 0.0013 | 0.0078 | 0.0060 | 0.0394 | 0.0953 | -0.3 +0.6 -1.0 +5.5 +12.1 |

Reading Table 2: a block of about 40 English variants (THE/OF/(TO/AND) removed; Moby Dick, Gospel of Buddha, Bhagavad Gita, Austen, Cicero, Paine, Emerson, Plato, Agrippa, Poe, Web text) have overlapping rank intervals; the full score prefers corpora with short-sentence novels and aphoristic texts (Moby Dick, Gospel of Buddha, Gita) because their sentence statistics happen to resemble the unsolved marks, which finding 6 says is not meaningful; the word-level score prefers formal philosophical prose (Cicero tr., Paine, Emerson, Plato). Neither orders registers with any confidence.

### Table 3. Best non-English natural corpora

**Table 3. Best NON-English natural corpora (full score)**

| # | candidate (corpus [variant]) | words | mean len | score ± boot SE | rank 95% interval | JS A len | JS B bigram | JS C first | JS D last | JS E sent-len | z vs own-corpus window null (A,B,C,D,E) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Dutch: bible-corpus | 728k | 4.36 | 0.96 ± 0.11 | 1-3 | 0.0028 | 0.0114 | 0.0222 | 0.0780 | 0.0685 | +0.0 +0.6 +1.2 +12.1 +2.3 |
| 2 | Danish: bible-corpus | 655k | 4.17 | 1.01 ± 0.12 | 1-5 | 0.0057 | 0.0156 | 0.0459 | 0.0385 | 0.0555 | +1.1 +1.0 +1.4 +4.0 +0.7 |
| 3 | Icelandic: IcePaHC (hist.) | 621k | 4.41 | 1.06 ± 0.12 | 1-5 | 0.0104 | 0.0272 | 0.0164 | 0.0709 | 0.0320 | +2.9 +3.8 -0.2 +11.4 -0.1 |
| 4 | Norwegian: bible-corpus | 721k | 3.97 | 1.13 ± 0.13 | 2-7 | 0.0094 | 0.0236 | 0.0581 | 0.0245 | 0.0405 | +3.8 +3.1 +2.4 +2.2 +0.5 |
| 5 | Old Norse: sagas (Perseus/CLTK) | 381k | 4.49 | 1.18 ± 0.12 | 2-7 | 0.0113 | 0.0272 | 0.0148 | 0.0813 | 0.0495 | +6.5 +6.8 -0.2 +14.0 +3.7 |
| 6 | German: Faust | 32k | 4.80 | 1.26 ± 0.11 | 3-8 | 0.0125 | 0.0309 | 0.0116 | 0.0786 | 0.0685 | +0.8 +1.2 -0.2 +8.5 +5.3 |
| 7 | Swedish: bible-corpus | 733k | 4.32 | 1.33 ± 0.14 | 5-9 | 0.0074 | 0.0180 | 0.0609 | 0.0523 | 0.0777 | +3.3 +2.6 +4.7 +7.6 +2.4 |
| 8 | Faroese: FarPaHC | 18k | 4.18 | 1.43 ± 0.13 | 6-10 | 0.0151 | 0.0371 | 0.0382 | 0.0452 | 0.0731 | +28.3 +26.3 +16.1 +12.6 +23.6 |
| 9 | Latin: PROIEL treebank | 177k | 5.25 | 1.45 ± 0.13 | 6-10 | 0.0194 | 0.0407 | 0.0090 | 0.0904 | 0.0444 | +7.6 +7.5 -0.7 +3.9 +0.6 |
| 10 | Welsh: CCG treebank | 24k | 4.32 | 1.66 ± 0.12 | 9-13 | 0.0249 | 0.0615 | 0.0092 | 0.0517 | 0.0735 | +33.4 +51.6 +2.6 +5.2 +1.9 |
| 11 | Gothic: Wulfila Bible (PROIEL) | 35k | 5.21 | 1.73 ± 0.13 | 10-15 | 0.0229 | 0.0493 | 0.0265 | 0.0790 | 0.0561 | +9.4 +9.3 +0.4 +9.7 +3.5 |
| 12 | Old English: Beowulf | 62k | 3.97 | 1.73 ± 0.14 | 8-17 | 0.0154 | 0.0297 | 0.0401 | 0.0556 | 0.1566 | +3.5 +5.2 +2.6 +0.8 +2.1 |
| 13 | Old English: Sacred-Texts corpus (poetry+psalms) | 147k | 4.61 | 1.78 ± 0.15 | 10-16 | 0.0174 | 0.0366 | 0.0384 | 0.1104 | 0.0663 | +13.8 +10.9 +2.7 +10.7 +1.4 |
| 14 | French: bible-corpus | 779k | 4.07 | 1.82 ± 0.15 | 11-16 | 0.0179 | 0.0516 | 0.0392 | 0.0967 | 0.0555 | +10.4 +8.8 +1.4 +10.2 +1.3 |

**Table 3b. Best NON-English natural corpora (word-level score)**

| # | candidate (corpus [variant]) | words | mean len | score ± boot SE | rank 95% interval | JS A len | JS B bigram | JS C first | JS D last | JS E sent-len | z vs own-corpus window null (A,B,C,D,E) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Dutch: bible-corpus | 728k | 4.36 | 0.40 ± 0.07 | 1-1 | 0.0028 | 0.0114 | 0.0222 | 0.0780 | 0.0685 | +0.0 +0.6 +1.2 +12.1 +2.3 |
| 2 | Danish: bible-corpus | 655k | 4.17 | 0.65 ± 0.09 | 2-3 | 0.0057 | 0.0156 | 0.0459 | 0.0385 | 0.0555 | +1.1 +1.0 +1.4 +4.0 +0.7 |
| 3 | Swedish: bible-corpus | 733k | 4.32 | 0.79 ± 0.11 | 2-3 | 0.0074 | 0.0180 | 0.0609 | 0.0523 | 0.0777 | +3.3 +2.6 +4.7 +7.6 +2.4 |
| 4 | Norwegian: bible-corpus | 721k | 3.97 | 1.02 ± 0.12 | 4-6 | 0.0094 | 0.0236 | 0.0581 | 0.0245 | 0.0405 | +3.8 +3.1 +2.4 +2.2 +0.5 |
| 5 | Icelandic: IcePaHC (hist.) | 621k | 4.41 | 1.16 ± 0.13 | 4-6 | 0.0104 | 0.0272 | 0.0164 | 0.0709 | 0.0320 | +2.9 +3.8 -0.2 +11.4 -0.1 |
| 6 | Old Norse: sagas (Perseus/CLTK) | 381k | 4.49 | 1.20 ± 0.13 | 5-7 | 0.0113 | 0.0272 | 0.0148 | 0.0813 | 0.0495 | +6.5 +6.8 -0.2 +14.0 +3.7 |
| 7 | German: Faust | 32k | 4.80 | 1.35 ± 0.13 | 5-9 | 0.0125 | 0.0309 | 0.0116 | 0.0786 | 0.0685 | +0.8 +1.2 -0.2 +8.5 +5.3 |
| 8 | Old English: Beowulf | 62k | 3.97 | 1.49 ± 0.15 | 7-9 | 0.0154 | 0.0297 | 0.0401 | 0.0556 | 0.1566 | +3.5 +5.2 +2.6 +0.8 +2.1 |
| 9 | Faroese: FarPaHC | 18k | 4.18 | 1.63 ± 0.15 | 8-11 | 0.0151 | 0.0371 | 0.0382 | 0.0452 | 0.0731 | +28.3 +26.3 +16.1 +12.6 +23.6 |
| 10 | Old English: Sacred-Texts corpus (poetry+psalms) | 147k | 4.61 | 1.75 ± 0.15 | 9-11 | 0.0174 | 0.0366 | 0.0384 | 0.1104 | 0.0663 | +13.8 +10.9 +2.7 +10.7 +1.4 |

The Germanic Bibles (Dutch, Danish, Swedish) are the only non-English texts that come within a factor of 2.4-4.7 of the best English variant on the word-level score; Romance, Latin, Celtic, Finnic, Hungarian, Turkic, Basque and Oceanic texts are 10-30 times worse (JS_A 0.018-0.073). Old Norse sagas, Icelandic, German Faust and Old English verse: JS_A 0.010-0.017.

### Table 4. Best unmodified English corpora

**Table 4. Best unmodified English corpora (all registers, full score)**

| # | candidate (corpus [variant]) | words | mean len | score ± boot SE | rank 95% interval | JS A len | JS B bigram | JS C first | JS D last | JS E sent-len | z vs own-corpus window null (A,B,C,D,E) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Bhagavad Gita (Arnold) | 23k | 4.22 | 0.60 ± 0.09 | 1-4 | 0.0069 | 0.0204 | 0.0165 | 0.0230 | 0.0081 | +1.1 +2.0 +0.2 +0.2 -0.6 |
| 2 | Moby Dick | 216k | 4.13 | 0.62 ± 0.10 | 1-5 | 0.0067 | 0.0211 | 0.0152 | 0.0196 | 0.0217 | +3.6 +5.1 +0.8 +1.4 +0.0 |
| 3 | Austen Emma | 160k | 4.04 | 0.66 ± 0.10 | 1-5 | 0.0074 | 0.0224 | 0.0202 | 0.0197 | 0.0143 | +7.5 +9.7 +2.3 +3.5 +0.3 |
| 4 | English: EWT (web) | 176k | 4.21 | 0.67 ± 0.10 | 1-5 | 0.0059 | 0.0196 | 0.0210 | 0.0234 | 0.0249 | +0.8 +1.8 +0.3 +1.0 -0.3 |
| 5 | Gospel of Buddha (Carus) | 88k | 4.18 | 0.71 ± 0.09 | 2-6 | 0.0101 | 0.0330 | 0.0040 | 0.0240 | 0.0143 | +0.7 +1.7 -1.4 -0.7 -1.5 |
| 6 | Chesterton Ball | 82k | 4.05 | 0.85 ± 0.11 | 5-9 | 0.0077 | 0.0239 | 0.0313 | 0.0310 | 0.0197 | +10.2 +10.5 +4.8 +9.6 +0.5 |
| 7 | Lovecraft Dunwich | 17k | 4.30 | 0.87 ± 0.11 | 6-11 | 0.0073 | 0.0229 | 0.0195 | 0.0331 | 0.0579 | +14.5 +24.2 +5.8 +8.4 +7.6 |
| 8 | Voltaire Candide (tr.) | 38k | 4.19 | 0.92 ± 0.13 | 6-13 | 0.0071 | 0.0213 | 0.0355 | 0.0483 | 0.0172 | +1.7 +2.2 +1.8 +0.9 +0.1 |
| 9 | Agrippa Occult Phil I | 64k | 4.21 | 0.95 ± 0.11 | 6-12 | 0.0082 | 0.0260 | 0.0160 | 0.0327 | 0.0747 | +5.1 +6.6 +0.2 +3.1 +1.3 |
| 10 | Whitman Leaves of Grass | 124k | 4.06 | 1.01 ± 0.12 | 8-16 | 0.0090 | 0.0252 | 0.0399 | 0.0256 | 0.0437 | +6.2 +6.5 +2.3 +1.5 +2.8 |
| 11 | Cicero Tusculan (English tr.) | 184k | 4.18 | 1.05 ± 0.12 | 9-18 | 0.0091 | 0.0281 | 0.0328 | 0.0322 | 0.0559 | +4.2 +6.0 +1.2 +1.0 +1.5 |
| 12 | Shakespeare Hamlet | 29k | 3.89 | 1.08 ± 0.13 | 7-27 | 0.0115 | 0.0307 | 0.0431 | 0.0221 | 0.0339 | +37.3 +38.2 +7.7 +0.7 +7.7 |

Even the closest unmodified English (Bhagavad Gita, Moby Dick, Austen, Web text) has JS_A = 0.006-0.007 (z_A = +1 to +8) and JS_B = 0.020-0.022, three to seven times the removal variants. Their apparent full-score lead comes entirely from statistics C, D, E.

### Table 5. Head-to-head, English synthetic variants (45 English corpora, 30k+ words each, paired bootstrap)

| variant | median over corpora (word-level) | median over corpora (all 5) | corpora where variant beats ref (-THE/OF/TO) | paired diff vs ref, word-level: median over corpora, 95% boot CI | P(variant better than ref) |
|---|---|---|---|---|---|
| base (Cicada rules) | 1.519 | 1.341 | 0/45 | +0.925 [+0.648, +1.142] | 0.000 |
| base, ING kept | 1.482 | 1.346 | 0/45 | +0.860 [+0.641, +1.124] | 0.000 |
| -THE | 0.832 | 0.961 | 4/45 | +0.242 [+0.114, +0.351] | 0.001 |
| -THE/OF | 0.577 | 0.816 | 22/45 | +0.002 [-0.052, +0.054] | 0.491 |
| -THE/OF/TO | 0.566 | 0.833 | 0/45 | +0.000 [+0.000, +0.000] | 0.000 |
| -THE/OF/TO/AND | 0.696 | 0.706 | 14/45 | +0.066 [-0.007, +0.145] | 0.033 |
| -THE/OF/TO/A | 0.815 | 0.844 | 10/45 | +0.159 [+0.078, +0.256] | 0.000 |
| -THE/A/AN | 1.159 | 0.963 | 2/45 | +0.299 [+0.145, +0.453] | 0.000 |
| -THE/OF/TO/AND/A/IN | 0.789 | 0.767 | 15/45 | +0.210 [+0.074, +0.342] | 0.003 |
| -all function words | 7.517 | 3.994 | 0/45 | +7.154 [+6.615, +7.685] | 0.000 |
| letters (no digraphs) | 0.739 | 1.009 | 12/45 | +0.184 [+0.056, +0.306] | 0.002 |
| letters -THE/OF/TO | 0.933 | 0.949 | 10/45 | +0.357 [+0.207, +0.522] | 0.000 |
| TH-only merged | 1.458 | 1.372 | 1/45 | +0.900 [+0.676, +1.113] | 0.000 |
| TH-only -THE/OF/TO | 0.633 | 0.821 | 17/45 | +0.063 [+0.006, +0.115] | 0.018 |
| archaic (thou/thee/-eth) | 1.561 | 1.358 | 0/45 | +0.933 [+0.666, +1.174] | 0.000 |
| archaic -THE/OF/TO | 0.573 | 0.833 | 26/45 | -0.001 [-0.004, +0.001] | 0.884 |

Chi-square goodness of fit of the length histogram alone (df = 10, critical 18.3):

chi-square GOF of the unsolved 11-bin word-length histogram (N=2896) against each candidate length distribution, df=10 (critical 18.3 at p=0.05)
candidates with >=30k words: 770; not rejected at p>0.05: 0
not-rejected by variant: {}
natural (unmodified) corpora not rejected: []
best 20: Emerson Essays I [-THE/OF/TO] chi2=18.7 p=0.04; Cicero Tusculan (English tr.) [-THE/OF/TO] chi2=20.1 p=0.03; Emerson Essays I [archaic -THE/OF/TO] chi2=20.2 p=0.03; Agrippa Occult Phil I [-THE/OF] chi2=20.4 p=0.03; Cicero Tusculan (English tr.) [archaic -THE/OF/TO] chi2=21.0 p=0.02; Paine Age of Reason [-THE/OF/TO] chi2=21.1 p=0.02; Emerson Essays II [-THE/OF/TO] chi2=21.2 p=0.02; Paine Age of Reason [archaic -THE/OF/TO] chi2=21.7 p=0.02; Emerson Essays II [archaic -THE/OF/TO] chi2=22.0 p=0.02; Plato Republic (Jowett) [archaic -THE/OF/TO] chi2=22.0 p=0.01; Gospel of Buddha (Carus) [-THE/OF] chi2=22.2 p=0.01; Plato Republic (Jowett) [-THE/OF/TO] chi2=22.9 p=0.01; Plato Republic (Jowett) [TH-only -THE/OF/TO] chi2=25.8 p=0.00; Emerson Essays I [TH-only -THE/OF/TO] chi2=25.8 p=0.00; Moby Dick [letters (no digraphs)] chi2=26.5 p=0.00; Gospel of Buddha (Carus) [letters (no digraphs)] chi2=27.5 p=0.00; English: EWT (web) [-THE/OF/TO/A] chi2=28.3 p=0.00; Cicero Tusculan (English tr.) [-THE/OF/TO/AND] chi2=28.8 p=0.00; Agrippa Occult Phil III [-THE/OF] chi2=29.7 p=0.00; Agrippa Occult Phil I [archaic -THE/OF/TO] chi2=30.1 p=0.00
  natural Dutch: bible-corpus                chi2=72.0 p=1.8e-11
  natural Danish: bible-corpus               chi2=156.4 p=1.8e-28
  natural Swedish: bible-corpus              chi2=186.3 p=1.2e-34
  natural Norwegian: bible-corpus            chi2=289.7 p=2.3e-56
  natural Icelandic: IcePaHC (hist.)         chi2=250.9 p=3.5e-48
  natural Old Norse: sagas (Perseus/CLTK)    chi2=279.2 p=3.8e-54
  natural German: Faust                      chi2=510.5 p=2.5e-103
  natural Latin: PROIEL treebank             chi2=507.2 p=1.3e-102
  natural French: bible-corpus               chi2=366.6 p=1.2e-72
  natural English: EWT (web)                 chi2=127.2 p=1.7e-22
  natural Moby Dick                          chi2=146.6 p=1.8e-26
  natural Austen Emma                        chi2=176.3 p=1.3e-32
| variant (English corpora, >=30k words) | n | not rejected (p>0.05) | median chi2 |
|---|---|---|---|
| base (Cicada rules) | 45 | 0 | 293.0 |
| -THE | 45 | 0 | 147.2 |
| -THE/OF | 45 | 0 | 107.3 |
| -THE/OF/TO | 44 | 0 | 99.0 |
| -THE/OF/TO/AND | 43 | 0 | 140.4 |
| -THE/A/AN | 45 | 0 | 307.6 |
| -THE/OF/TO/A | 44 | 0 | 254.0 |
| -THE/OF/TO/AND/A/IN | 42 | 0 | 211.6 |
| letters (no digraphs) | 45 | 0 | 120.9 |
| letters -THE/OF/TO | 44 | 0 | 201.1 |
| TH-only merged | 45 | 0 | 286.2 |
| TH-only -THE/OF/TO | 44 | 0 | 122.3 |
| archaic (thou/thee/-eth) | 45 | 0 | 294.7 |
| archaic -THE/OF/TO | 44 | 0 | 100.1 |
| -all function words | 32 | 0 | 6242.4 |

No candidate reaches a comfortable fit on a strict chi-square (best 18.7, p = 0.04), which is expected because a single corpus is never exactly the author's distribution, but the ordering is stable: removal variants 19-25 at best and a median of 99-107, letters 121, unmodified English 293, Dutch 72, every other language 150-6000.

### Table 6. Class level (best member of each class, bootstrap probability that it is the overall best)

| class | n | best member | word-level comb. best (obs) | P(this class is best of all classes) | median-of-class word-level | all-5 combined of best | JS A | JS B |
|---|---|---|---|---|---|---|---|---|
| English [-THE/OF/TO] | 45 | Cicero Tusculan (English tr.) | 0.168 | 0.658 | 0.566 | 0.56 | 0.0010 | 0.0054 |
| English [-THE/OF/TO/AND] | 45 | Cicero Tusculan (English tr.) | 0.185 | 0.184 | 0.696 | 0.50 | 0.0014 | 0.0051 |
| English [-THE/OF] | 45 | Agrippa Occult Phil I | 0.205 | 0.149 | 0.577 | 0.49 | 0.0009 | 0.0074 |
| English [TH-only, -THE/OF/TO] | 45 | Emerson Essays I | 0.221 | 0.008 | 0.633 | 0.61 | 0.0012 | 0.0074 |
| English [-THE/A/AN] | 45 | English: EWT (web) | 0.317 | 0.000 | 1.159 | 0.46 | 0.0017 | 0.0107 |
| English [letters, no digraphs] | 45 | Moby Dick | 0.322 | 0.000 | 0.739 | 0.43 | 0.0011 | 0.0123 |
| English [-THE only] | 45 | Moby Dick | 0.348 | 0.000 | 0.832 | 0.36 | 0.0022 | 0.0107 |
| English [letters, -THE/OF/TO] | 45 | Emerson Essays I | 0.359 | 0.000 | 0.933 | 0.68 | 0.0027 | 0.0098 |
| Germanic (nl,da,sv,no,de,is,fo,ang,non,got) [natural] | 12 | Dutch: bible-corpus | 0.398 | 0.001 | 1.276 | 0.96 | 0.0028 | 0.0114 |
| English verse [natural] | 4 | Milton Paradise Lost | 0.686 | 0.000 | 1.109 | 1.20 | 0.0057 | 0.0174 |
| English [TH-only merged] | 45 | Moby Dick | 0.712 | 0.000 | 1.458 | 0.58 | 0.0055 | 0.0191 |
| English prose [natural, unmodified] | 45 | English: EWT (web) | 0.744 | 0.000 | 1.519 | 0.67 | 0.0059 | 0.0196 |
| English KJV-style [natural] | 6 | KJB Job | 1.426 | 0.000 | 1.776 | 1.17 | 0.0119 | 0.0361 |
| Latin (5 corpora) [natural] | 4 | Latin: PROIEL treebank | 1.945 | 0.000 | 2.990 | 1.45 | 0.0194 | 0.0407 |
| Romance (fr,it,es) [natural] | 3 | French: bible-corpus | 2.087 | 0.000 | 2.454 | 1.82 | 0.0179 | 0.0516 |
| Celtic (cy,ga) [natural] | 2 | Welsh: CCG treebank | 2.691 | 0.000 | 2.970 | 1.66 | 0.0249 | 0.0615 |
| Esperanto [natural] | 1 | Esperanto: bible-corpus | 2.971 | 0.000 | 2.971 | 2.64 | 0.0274 | 0.0683 |
| English [-all function words] | 45 | KJB Psalms | 4.532 | 0.000 | 7.517 | 3.16 | 0.0464 | 0.0917 |
| Finno-Ugric/Turkic/Basque/Maori [natural] | 6 | Hungarian: bible-corpus | 4.975 | 0.000 | 6.259 | 3.08 | 0.0516 | 0.0989 |

P(best English[-THE/OF/TO] beats best of class):
  vs Germanic (nl,da,sv,no,de,is,fo,ang,non,got) [natural]   0.999
  vs Romance (fr,it,es) [natural]                            1.000
  vs Latin (5 corpora) [natural]                             1.000
  vs Celtic (cy,ga) [natural]                                1.000
  vs Finno-Ugric/Turkic/Basque/Maori [natural]               1.000
  vs Esperanto [natural]                                     1.000
  vs English prose [natural, unmodified]                     1.000
  vs English [-THE/OF]                                       0.806
  vs English [-THE only]                                     0.999
  vs English [-THE/OF/TO/AND]                                0.769
  vs English [-THE/A/AN]                                     0.995
  vs English [letters, no digraphs]                          0.998
  vs English [letters, -THE/OF/TO]                           1.000
  vs English [TH-only merged]                                1.000
  vs English [TH-only, -THE/OF/TO]                           0.979
  vs English [-all function words]                           1.000
  vs English verse [natural]                                 1.000
  vs English KJV-style [natural]                             1.000

The class table is biased in favour of classes with many members (45 English corpora against 1-12 for the others), so median-of-class is shown next to the best. Using medians, Dutch (0.40) is better than the median English-minus-THE/OF corpus (0.57); this is the reason finding 4 declines to call Dutch excluded by length data alone.

### Table 7. Which words must be removed? Greedy search on pooled English

Ten English prose corpora (564k words), top-45 frequent words as candidates, greedy forward removal of the word that most reduces the word-level objective (mean of normalised JS_A and JS_B) against the unsolved pages:

| step | pooled English, Cicada digraphs (obj / JS A / JS B / mean len) | pooled, letter-by-letter | pooled, TH-only |
|---|---|---|---|
| 0 | (none): 1.111 / 0.0093 / 0.0281 / 4.13 | (none): 0.427 / 0.0021 / 0.0149 / 4.40 | (none): 1.107 / 0.0093 / 0.0280 / 4.25 |
| 1 | +THE: 0.483 / 0.0031 / 0.0146 / 4.28 | +OF: 0.253 / 0.0009 / 0.0096 / 4.50 | +THE: 0.497 / 0.0033 / 0.0150 / 4.41 |
| 2 | +OF: 0.201 / 0.0010 / 0.0068 / 4.38 | +THERE: 0.247 / 0.0009 / 0.0094 / 4.50 | +OF: 0.228 / 0.0013 / 0.0074 / 4.52 |
| 3 | +IN: 0.165 / 0.0008 / 0.0057 / 4.44 | +OR: 0.243 / 0.0009 / 0.0092 / 4.52 | +IN: 0.202 / 0.0012 / 0.0065 / 4.57 |
| 4 | +THERE: 0.162 / 0.0008 / 0.0056 / 4.44 | +HAVE: 0.238 / 0.0009 / 0.0091 / 4.52 | +WHICH: 0.199 / 0.0012 / 0.0064 / 4.57 |
| 5 | +I: 0.159 / 0.0006 / 0.0059 / 4.48 | +WHAT: 0.236 / 0.0009 / 0.0090 / 4.52 | +THERE: 0.199 / 0.0012 / 0.0064 / 4.57 |
| 6 | +WHICH: 0.155 / 0.0006 / 0.0058 / 4.47 | +THEIR: 0.234 / 0.0008 / 0.0090 / 4.52 | +I: 0.197 / 0.0010 / 0.0068 / 4.61 |
| 7 | +OR: 0.152 / 0.0006 / 0.0056 / 4.49 | +WILL: 0.233 / 0.0008 / 0.0089 / 4.52 | +OR: 0.197 / 0.0010 / 0.0067 / 4.63 |
| 8 | +WITH: 0.148 / 0.0006 / 0.0054 / 4.50 | +HIS: 0.232 / 0.0009 / 0.0086 / 4.53 | +WHAT: 0.198 / 0.0010 / 0.0067 / 4.63 |

THE and OF are the first two words chosen under Cicada digraphs and under TH-only merging in the pooled search, and in all four single-corpus searches (Plato, Moby Dick, Emerson, Cicero; Moby Dick picks THE then OF then I, Emerson/Cicero pick TO third, Cicero AND fourth). The third removal is corpus-dependent and modest (IN, 0.036, in the pooled search; I, TO, TO in the single-corpus searches with gains 0.07-0.13, i.e. 1.5-3 bootstrap standard errors of about 0.04-0.05); every removal after the third changes the objective by less than 0.04, so nothing beyond THE + OF (+ one more short word) is individually resolved, and the cross-corpus paired test above finds -THE/OF and -THE/OF/TO tied. Under letter-by-letter spelling the search starts much lower (0.427, because THE is a 3-rune word there) and chooses OF first; it never reaches the digraph-variant optimum (0.232 against 0.148 after eight removals) and has a worse bigram fit (JS_B 0.0086 against 0.0054-0.0068).

### Sentence marks: first word, last word, sentence length

(`marks.py`, `marks_out.txt`.) Unsolved: overall mean word length 4.474, first-word mean 4.429, last-word mean 4.291. Under 5,000 random placements of 174 interior marks among the 2,895 word gaps, first mean 4.49 +- 0.17 and last mean 4.47 +- 0.17, so z = -0.38 and -1.06; the fraction of first words of length 2 (0.183 vs 0.154 +- 0.026), of last words of length 2 (0.160) and of length 7+ (0.200 and 0.160) are all inside the random band (|z| <= 1.1). Real texts with real punctuation, 175-sentence windows against the same random-placement null, mean z(first), z(last): Cicero tr. -4.9/+5.1; Emerson -4.5/+7.3; Moby Dick -3.8/+3.8; Plato -3.8/+7.5; Agrippa -2.2/+3.0; Gospel of Buddha -0.3/+4.2; Dutch Bible -4.5/+10.6. Sentence length: unsolved mean 16.5, sd 14.7 (CV 0.89); chi-square against the geometric distribution implied by random placement is 12.0 on 8 df (p = 0.10 by simulation). English windows have CV 0.73-1.0, so sentence length per se does not discriminate, but the position effect (short first words, long last words) does, and the unsolved pages do not show it.

Interpretation (not proven): either the "." marks in the transcription are not sentence terminators in the plaintext sense (they may be inserted, positional or cipher-mapped marks), or the plaintext follows an unusual syntax in which sentences start and end on words of average length. A related observation: the marks are strongly coupled to the line layout. Of 164 sentence changes, 16.5% fall exactly at a line end (5.1% expected if marks fell at random rune positions), and the mean relative position in the line is 0.636 (expected 0.52; z about +5), histogram over fifths of the line [10, 25, 37, 35, 57]. This is a typesetting/transcription property, not a language property.

### Lines

(`extra.py`, `extra_out.txt`.) 594 lines of 21.8 +- 2.6 runes (interior lines 22.0 +- 2.3; CV 0.11). Of 539 internal line breaks, 72.0% fall inside a word and only 28.0% at a word boundary (a uniformly random break position would give 22.4% at a boundary; the excess, 28.0 vs 22.4, is z about +3, so scribes mildly prefer word boundaries but do not require them). The text is therefore justified, hyphenless prose in a fixed-width column, not verse. Every verse corpus breaks lines at word boundaries 100% of the time, with line lengths in runes of mean 24-37 and CV 0.11-0.41 (Beowulf 35.0, CV 0.32; Faust 28.5, CV 0.34; Whitman CV 0.36; Hamlet CV 0.30; Virgil CV 0.12 and Milton CV 0.11, but those still end on word boundaries). Old English verse and Latin verse are rejected on line structure independently of the word-length results. Line-length CV cannot distinguish prose languages from each other.

### Cicada's own solved text (LP1) as a reference

(`final_tables.py`, `extra.py`.) LP1 solved text has 729 words, 4.08 mean runes, 7.1 words per line-sentence (very aphoristic), 2-rune words about 24% (THE 6.6%, OF 1.3%, TO 3.3% of tokens). It is too short to be a decisive comparison.

| LP1 treatment | JS A (len) | floor mean ± sd for a 729-word sample of a text that truly matches (Cicero tr. -THE/OF/TO windows vs its own corpus) | JS B (bigram) |
|---|---|---|---|
| as is | 0.0091 | A: 0.0046 ± 0.0033 | 0.0496 (floor B: 0.0184 ± 0.0069) |
| THE/OF/TO deleted | 0.0030 | A: 0.0046 ± 0.0033 | 0.0309 (floor B: 0.0184 ± 0.0069) |
| letters (no digraphs) | 0.0063 | A: 0.0046 ± 0.0033 | 0.0243 (floor B: 0.0184 ± 0.0069) |

Length marginal: LP1 as written differs from the unsolved marginal by JS_A 0.0091, 1.4 sd above the 729-word floor of 0.0046 +- 0.0033 (not significant at this sample size); with THE/OF/TO deleted it is inside the floor (0.0030). Length bigram: LP1 as written is 4.5 sd above its floor (0.0496 against 0.0184 +- 0.0069, because it contains ordinary OF THE / IN THE pairs), with THE/OF/TO deleted 1.8 sd (0.0309), letter-by-letter 0.8 sd (0.0243). So LP1 is too short to discriminate between the removal and letter-by-letter hypotheses, is directionally consistent with the removal hypotheses, and as written (with THE) does not reproduce the unsolved bigram profile. LP1 is aphoristic (mean 7 words per line-sentence) while the unsolved sentences average 16.5 words, so the register differs from LP1 even if the author is the same.

### Zero-increment symbol candidates (link to the brief's chain-cipher families)

The brief's chain families require the zero-increment symbol to have the observed doublet rate, 86/12,955 = 0.66% (95% CI 0.52-0.80%). In English transliterated with Cicada rules, averaged over 8 prose corpora, the only symbols whose share falls in that interval are EA (0.69%; 0.74% when THE/OF/TO are removed) and IA (0.58%; 0.62%). Under letter-by-letter spelling only K (0.59-0.64%) falls in the interval. The rarer runes J, X, EO, OE, AE are far too rare (0.02-0.23%) and NG (0.85-0.92%) is just above. So EA or IA are the right candidates for the zero-increment letter under the favoured hypothesis; K, the letter Lane C suggested for the letter-by-letter hypothesis, only works if there are no digraph runes, which Table 5 disfavours.

## Implications for the community key sweeps (English-only scorers)

Scorers tested (`scorers.py`): the dukotah english_quadgrams table (log10 probability per quadgram) and rune IoC (x29, 1.0 random), on 13k-rune windows (30 per condition), eight English corpora averaged:

| plaintext treatment (8 English corpora, mean) | quadgram score / 4-gram (dukotah table) | rune IoC (x29-normalised) |
|---|---|---|
| base (Cicada rules) | -4.404 | 1.780 |
| -THE | -4.522 | 1.751 |
| -THE/OF/TO | -4.536 | 1.758 |
| -THE/OF/TO/AND | -4.594 | 1.757 |
| -THE/A/AN | -4.517 | 1.745 |
| -all function words | -4.828 | 1.806 |
| letters (no digraphs) | -4.408 | 1.949 |
| TH-only merged | -4.399 | 1.853 |
| archaic (thou/thee/-eth) | -4.384 | 1.780 |

| natural non-English corpus (13k-rune windows) | quadgram / 4-gram | rune IoC |
|---|---|---|
| Latin: Newton Principia | -5.591 | 1.963 |
| Latin: Caesar BG | -5.550 | 2.090 |
| German: Faust | -5.391 | 2.146 |
| Dutch: bible-corpus | -5.669 | 2.272 |
| Danish: bible-corpus | -5.618 | 2.084 |
| Swedish: bible-corpus | -5.491 | 2.019 |
| Welsh: CCG treebank | -6.525 | 1.735 |
| Old English: Beowulf | -5.292 | 1.594 |
| Old Norse: sagas (Perseus/CLTK) | -5.786 | 1.907 |
| Gothic: Wulfila Bible (PROIEL) | -5.607 | 2.555 |
| Esperanto: bible-corpus | -6.232 | 1.913 |
| Italian: bible-corpus | -5.391 | 2.128 |
| Finnish: bible-corpus | -5.917 | 2.553 |
| French: bible-corpus | -5.280 | 2.384 |
| Spanish: bible-corpus | -5.440 | 2.158 |

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
