# Survey: computational-ai (run 2026-10-16)

Topic: computational and AI-assisted decipherment that has actually broken real ciphers, graded against the LP2 fingerprint in `toolbox/CONSTRAINTS.md` and the prior lanes A-R (`REPORT.md`, `REPORT_ROUND2.md`) and the community ledgers.

## Scope and method

- Every web source below was opened with the fetch tool. Where the fetch returned only metadata (ACL landing pages), that is said in the entry. Where it returned a PDF body, the tool gave no readable text (ACL P11-1025 and P13-1154 PDFs, the HistoCrypt 2019 Playfair PDF, the CrypTool 20-years PDF); the arXiv HTML versions were used where they exist (2012.15229, 2403.17350).
- Facts that rest on a search-index summary I could not open are marked "search index, unverified" and carry no URL. These include the Lasry thesis content (the Kassel repository record was blocked by a bot check), the Cryptologia 2016 Chaocipher article (403), Ravi and Knight's and Nuhn's method details, Kopal 2020, and the Lasry M-209 and Playfair claims.
- Not used, because unverified: a Grok 3 K4 claim (only as reported by the gist), CryptanalysisBench (arXiv ID looked wrong for its date, not opened), and the Solitaire papers.
- `toolbox/CONSTRAINTS.md` names `toolbox/fingerprint.py`, but that file is not in `toolbox/`. The C1-C6 numbers below are taken from CONSTRAINTS.md text and from `REPORT.md`.
- Prior-coverage greps (repo and ledgers): `grep -ri` for lasry, jakobsen, anneal, beam, homophon, Playfair, chaocipher, M-209, enigma, solitaire, dynamic substitution, cipher type, IDENTIFY, classif, neural, LSTM, transformer, seq2seq, stride, bigram, transposition, columnar, decimation, over `agents/`, `research/`, `lp/`, `toolbox/`, `REPORT*.md`, and `dl/dukotah/liber-primus`, `dl/leo`, `dl/aldegonde_clone`, `dl/theron`. The lane D and K files were read directly.
- My own check, not in the repo: a scratch rerun of the Chaocipher simulation (scout code, copied to the session scratchpad) on about 5,500 to 5,800 letters of English-like prose from the repo's reports. Results are in the Chaocipher entry.

## Entries

### T: Lasry hill climbing and annealing
- Source: G. Lasry, PhD thesis, Kassel University Press, 2018 (title "A Methodology for the Cryptanalysis of Classical Ciphers with Search Metaheuristics" per search index, unverified; repository record blocked by bot check, not read, https://kobra.uni-kassel.de/handle/123456789/15274); Exhibit 6 chapter and author role per https://chaocipher.com/chaocipher-026.htm (opened).
- Exploits: hill climbing and simulated annealing over keys, scored by n-gram or index-of-coincidence fitness, which needs a partly readable partial key to climb (thesis content from search index, unverified; chaocipher.com page confirms the thesis covers the Exhibit 6 solution and that IoC was used as an evaluation function in his search work).
- LP2 constraints: C1 (LP2 IoC 1.000 gives a climber no gradient on a flat stream) and C2b (a fixed feedback table is excluded at about 245 sigma, so a climb over a fixed table cannot be right).
- Prior coverage: lane K (`agents/laneK_walk_search/RESULTS.md`, line 29): IoC hill climb over periods 2..50 on LP2 reaches IoC at most 1.002; line 143 says no global SA, EM or parallel-tempering search can solve the walk at n = 12,956. `REPORT.md` reports 0 of 63 annealing runs recovered the walk. Also lane L.
- Verdict: applicable-tested (lane K: annealing and IoC climbing on the walk family, 0 of 63 runs per REPORT.md; planted fixed-alphabet controls recovered, 5 of 5).
- Test design: none new; lane K's planted controls and null runs stand.

### T: Jakobsen fast substitution hill climber
- Source: T. Jakobsen, "A fast method for the cryptanalysis of substitution ciphers", Cryptologia 19(3), 1995, pp. 265-274, as cited and described by https://www.cs.trincoll.edu/~crypto/hcryptoj/docs0.51/hcrypto/analyzer/DigramAnalyzer.html (opened).
- Exploits: pairwise-swap hill climbing on a substitution key, scoring how far the cryptogram's digram matrix departs from English's, without decrypting at each step (per the analyzer page).
- LP2 constraints: C1 (a bijective substitution preserves the IoC; English is 1.7-1.8 and LP2 is 1.000, so no bijection of English-like text gives LP2).
- Prior coverage: `REPORT.md` and `dl/dukotah/liber-primus/ELIMINATION-LEDGER.md` (row "Substitution / homophonic": dead, preserves IoC, cannot turn flat 1.00 into English 1.78). Greps for "substitution" and "homophon" found no run on LP2.
- Verdict: not-applicable (C1: bijections keep IoC; LP2 IoC 1.000 against English 1.7-1.8).
- Test design: none needed.

### T: Ravi and Knight Bayesian sampling and EM
- Source: S. Ravi and K. Knight, "Bayesian Inference for Zodiac and Other Homophonic Ciphers", ACL 2011, pp. 239-247, ACL Anthology P11-1025; metadata only from https://aclanthology.org/P11-1025/ (opened; the abstract field on that page is a form placeholder, and the PDF body was not readable).
- Exploits: EM and Bayesian sampling over homophonic key assignments, combining letter n-gram models with word dictionaries (method from search index, unverified).
- LP2 constraints: C2 (an i.i.d. homophone model gives a doublet floor of 1.7-2.7% on English letter statistics, against 86 observed adjacent repeats, 0.66%).
- Prior coverage: `research/gap_audit.md` section 4 (computes the homophone floor; D-03 open); `ELIMINATION-LEDGER.md` Round 24 row (C7 homophonic-downward killed at planning). Lane K tested global SA, EM and parallel tempering on the walk and found no solve.
- Verdict: not-applicable (C2: homophone floor 1.7-2.7% against LP2's 0.66% doublet rate, per the gap audit's computation).
- Test design: none needed.

### T: Nuhn beam search with n-gram language model
- Source: M. Nuhn, J. Schamper and H. Ney, "Beam Search for Solving Substitution Ciphers", ACL 2013, pp. 1568-1576, ACL Anthology P13-1154; metadata only from https://aclanthology.org/P13-1154/ (opened; PDF body not readable here).
- Exploits: beam search over partial key assignments scored by an n-gram language model with a future-cost heuristic; partial keys earn partial credit (method from search index, unverified).
- LP2 constraints: C1 (no partial credit on LP2's flat stream, so a sequential beam over a fixed key has no ordering signal; lane K's bit budget shows the beam must carry about 2^90 hypotheses).
- Prior coverage: lane K (`agents/laneK_walk_search/RESULTS.md`, sequential beam section); `dl/dukotah/liber-primus/ELIMINATION-LEDGER.md` Round 18 (skip-tolerant beam recovers a planted key at -4.15 and 100% where the rigid test fails) and Round 24 (pair decoder, plant recovery 100%, calibrated bar 7.384 at N = 1e6, 245,975 words, 0 hits).
- Verdict: applicable-tested (lane K beam bit budget; ELIMINATION-LEDGER.md skip-aware beam sweeps over the community families).
- Test design: none new; the skip-aware beam's planted-key controls and null bars stand.

### T: Neural-LM scorer in skip-aware beam
- Source: N. Kambhatla, A. Mansouri Bigvand and A. Sarkar, "Decipherment of Substitution Ciphers with Neural Language Models", EMNLP 2018, pp. 869-874, abstract read at https://aclanthology.org/D18-1102/ (opened; abstract only, Beale claim as stated there).
- Exploits: beam search that scores full candidate plaintexts with a neural language model and a neural rest-cost estimate, reaching lower error at much smaller beams than n-gram baselines, including on the Beale cipher (abstract).
- LP2 constraints: C1 (a scorer only helps once the right decode is in the beam, and LP2 gives no English-level signal to rank partial decodes) and C2 (the family the scorer would rescore must carry the skip rule the deficit requires).
- Prior coverage: grep for neural, LSTM, transformer, seq2seq over `ELIMINATION-LEDGER.md`, `agents/*/RESULTS.md` and `research/SYNTHESIS.md` found no neural scorer run. Round 24 used language-aware scorers for Latin, Greek, Old English and Enochian; Round 18 built the skip beam.
- Verdict: applicable-untested
- Test design: Control: plant a Latin or Old English text of 12,956 runes through the skip-aware keyskip decode with a known key, and require the neural-rescored beam to recover it at least as often as the n-gram scorer (recovery 0.90 or better at a matched beam size). Null: the same pipeline on word-shuffled plaintext and on 400 random keys, with the neural scorer's maximum over that null kept below a bar calibrated the way Round 24 calibrated its bar (7.384 at N = 1e6). Only keys that pass both gates go to `dl/dukotah/liber-primus/verify_solution.py`.

### T: Aldarrab and May sequence-to-sequence
- Source: N. Aldarrab and J. May, "Can Sequence-to-Sequence Models Crack Substitution Ciphers?", ACL 2021, arXiv 2012.15229, full HTML read at https://arxiv.org/html/2012.15229 (opened).
- Exploits: a character-level transformer (6 encoder and 6 decoder layers, about 44M parameters, beam 100) trained on synthetic 1:1 substitution ciphers maps ciphertext to plaintext; on the real Borg cipher (256 characters) a Latin-only model reaches 3.91% symbol error and a 14-language model 5.47% (per the paper).
- LP2 constraints: C1 (the model assumes a fixed 1:1 symbol-to-letter map with English-like frequency ranks; LP2's IoC 1.000 against English 1.7-1.8 gives it no ranking to use).
- Prior coverage: none in the repo (grep for seq2seq, transformer and neural over `ELIMINATION-LEDGER.md`, `agents/*/RESULTS.md`, `research/SYNTHESIS.md` found nothing).
- Verdict: not-applicable (C1: a fixed 1:1 map on English keeps IoC near 1.7-1.8; LP2 is 1.000).
- Test design: none needed.

### T: Copiale cipher solve 2011
- Source: K. Knight, B. Megyesi and C. Schaefer, "The Copiale Cipher", BUCC 2011, pp. 2-9, ACL Anthology W11-1202 (https://aclanthology.org/W11-1202/, metadata only, opened); cipher size and history from https://www.su.se/english/research/research-projects/decipherment-of-historical-manuscripts/the-copiale-cipher-1.688288 (opened).
- Exploits: symbol-frequency and grouping analysis showed the abstract symbols carried the German text; homophone groups were then identified and the plaintext recovered (per project page and search index; the method details are not in the page).
- LP2 constraints: C2 (a homophone-group solve needs an i.i.d. homophone model, which predicts a doublet floor of 1.7-2.7% against LP2's 0.66%).
- Prior coverage: `research/gap_audit.md` section 2 (homophonic D-03 open; C7 killed in Round 24 per `ELIMINATION-LEDGER.md`).
- Verdict: not-applicable (C2: homophone floor 1.7-2.7% against 86 adjacent repeats, 0.66%).
- Test design: none needed.

### T: Zodiac Z340 stride detector
- Source: S. Blake, D. Oranchak and J. Van Eycke, "The Solution of the Zodiac Killer's 340-Character Cipher", arXiv 2403.17350, sections read to 5.4 at https://arxiv.org/html/2403.17350 (opened; page truncated mid-section).
- Exploits: a repeated-bigram excess at pseudo-period 19 in the 20-by-17 grid (37 repeating bigrams) suggested a transposition, and 655,088 periodic grid-reading variants were then scored with AZdecrypt n-gram statistics (6-grams at that stage, per the paper). The detector and the solver are separate steps.
- LP2 constraints: C3 (repeated cipher words are at chance, 16 against 11.0 +/- 3.1, so a stride-level repeat excess has no repeat mechanism to ride on) and C2 (the adjacent deficit is in reading order, so a post-chain reordering removes it, per lane D).
- Prior coverage: grep for stride and bigram-period over `agents/`, `research/SYNTHESIS.md` and both ledgers found no bigram-stride scan. Lane D (`agents/laneD_chain_variants/RESULTS.md`, Candidate 5) tested columnar and rail-fence reorderings, not decimation grids; C1's period scans test rune matches, not bigram repeats.
- Verdict: applicable-untested
- Test design: Control: plant a period-19 decimation transposition of an English-derived 17-by-20 grid over a repeat-rich homophonic text, and require the stride-bigram scan to put period 19 first with z of at least 5 against shuffles. Null: the same scan on LP2 at every lag 2..1500 and grid width 2..200, against 1000 within-page increment shuffles that keep the doublet deficit (CLAUDE.md convention); report the maximum z per width against that null.

### T: Lasry-style post-chain transposition search
- Source: G. Lasry thesis record at https://kobra.uni-kassel.de/handle/123456789/15274 (opened; blocked, chapter list not read, so the transposition method is from search index, unverified); the repo's own transposition test is `agents/laneD_chain_variants/RESULTS.md` Candidate 5.
- Exploits: columnar, double-transposition and grid reorderings solved by hill climbing against an n-gram fitness (search index, unverified).
- LP2 constraints: C2 (a reordering after the chain scatters the adjacent pairs that carry the 0.66% doublet deficit; lane D's controls recover the inverse permutation at z -14 to -15, and LP2's reorderings sit at chance).
- Prior coverage: lane D (`agents/laneD_chain_variants/RESULTS.md`, Candidate 5: 470 reorderings per page; "transposition after the chain" excluded for every non-adjacency-preserving permutation in the family). ELIMINATION-LEDGER.md row "Transposition-only": dead, doublet-transparent.
- Verdict: not-applicable (C2: post-chain reordering destroys the reading-order deficit of 0.66%; lane D Candidate 5). A pre-chain transposition is untestable from the ciphertext, per lane D.
- Test design: none needed.

### T: Lasry Playfair record
- Source: HistoCrypt 2019 PDF at https://ep.liu.se/ecp/158/010/ecp19158010.pdf (opened; scanned pages, no readable text, PDF metadata author "Jugin", so Lasry's authorship is not confirmed here).
- Exploits: simulated annealing with hexagram scoring on a 40-letter Playfair (search index, unverified).
- LP2 constraints: C2 (Playfair ciphertext digraphs never contain equal letters, so half the adjacent positions cannot repeat, giving a floor of about half the random rate: 1.7-2.0% against LP2's 0.66%).
- Prior coverage: `research/scout3_norepeat_generators.md` (Playfair row: overall 1.66% for a 5x6 square, parity split 51/35 on LP2 against 0/86 a Playfair would give on one parity). Grep for playfair in the ledgers found no LP2 run.
- Verdict: not-applicable (C2: a Playfair floor of about 1.7-2.0% against 0.66% observed; the parity split rules it out too).
- Test design: none needed.

### T: Lasry Chaocipher Exhibit 6 as published
- Source: Chaocipher Exhibit 6 page https://chaocipher.com/chaocipher-026.htm (opened; names the solver and that the account is in his thesis, does not name the method); the cipher definition and simulation are the repo's `research/s3/sim2.py` and `research/scout3_norepeat_generators.md`.
- Exploits: a dynamic substitution (two keyed alphabets permuted after every letter, Byrne's Chaocipher); Exhibit 6 has about 50 in-depth messages sharing a start state, which Lasry solved (per the page).
- LP2 constraints: C2 (chance doublets: the ciphertext doublet rate is about (1 - plaintext doublet rate)/N, and about 3.4-4.2% for English-like plaintext, against LP2's 0.66%).
- Prior coverage: `research/scout3_norepeat_generators.md` (Chaocipher row: 3.45% on flat plaintext at N = 29; plaintext doublets never give ciphertext doublets); `research/s3/sim2.py`. Scratch rerun today on 5,518 and 5,829 letters of repo prose: IoC times N about 1.00, doublets 3.7-4.2% across three seeds.
- Verdict: not-applicable (C2: plain dynamic substitution gives about 3.7-4.2% doublets against LP2's 0.66%; the scratch rerun is not committed).
- Test design: none needed.

### T: Dynamic substitution with skip-on-repeat
- Source: Chaocipher-type progressive-alphabet cipher, family context at https://chaocipher.com/chaocipher-026.htm (opened); the skip-on-repeat variant is this survey's construction, not a published cipher.
- Exploits: keep the per-letter alphabet evolution of Chaocipher (no two occurrences of a word share a state, so the C3 counting bound does not apply) and add a skip-on-repeat rule that redraws the step when the output would repeat the previous rune. This is the mechanism that lowers the doublet rate from about 3.4-4% to 0.66%, the same kind of rule CONSTRAINTS.md names for the walk family.
- LP2 constraints: C2 (the skip rule supplies the deficit; the residual 0.66% needs the rule enforced about 84% of the time, per `research/scout3_norepeat_generators.md`), C3 (per-letter state is not a small per-word state, so the counting bound does not exclude it), and C5 (tension: a per-letter alphabet has no same-alphabet positions at lag 5, so it predicts a lag-5 echo at chance; LP2 shows 4.94% against 3.45%, about 2.5 sigma).
- Prior coverage: lane K and lane L cover the walk (per-word base, period-5 alphabets, `agents/laneK_walk_search/RESULTS.md`, `agents/laneL_keyword_walk`). Grep for chaocipher over `agents/` found nothing; `research/scout2_ai_codebreaking.md` Lead 2 proposes this family and says it is unrun.
- Verdict: applicable-untested
- Test design: Control: encipher English-derived runes (29 symbols, LP2 length, with the skip rule) from a keyword-derived start, and require the keyword decoder with the skip rule to recover the planted keyword at rank 1 with a margin of 5 sigma over 2000 wrong keywords. Null: the same decoder over word-shuffled LP2 and over 1000 random keyword draws, with only keys above the null maximum passing; survivors go to `dl/dukotah/liber-primus/verify_solution.py`. The 362,700-word keyword list from lane A is the candidate set; C5 is the second gate, since the family predicts no lag-5 echo.

### T: Lasry M-209 nested hill climb
- Source: Lasry's M-209 chapter per the thesis record https://kobra.uni-kassel.de/handle/123456789/15274 (opened; blocked, not read); the M-209 letter-count figures are from search index, unverified and not used.
- Exploits: an additive lug-driven keystream over 26 letters attacked by nested hill climbing on the keystream (search index, unverified).
- LP2 constraints: C2 (any additive keystream independent of the ciphertext gives exactly 1/29 = 3.45% doublets, against LP2's 0.66%).
- Prior coverage: `toolbox/CONSTRAINTS.md` quick exclusions (additive keystream, about 3.4%); `research/scout3_norepeat_generators.md` key theorem (flat keystream independent of plaintext gives exactly 1/N).
- Verdict: not-applicable (C2: additive keystream gives 1/29 = 3.45% doublets against 0.66% observed).
- Test design: none needed.

### T: Cipher-type identification from statistics
- Source: IDENTIFY Cipher tool statistics (BION 2005 reference method) at https://www.sites.google.com/site/cryptocrackprogram/user-guide/tools-tab/identify-cipher (opened); the crate `cipher_identifier` at https://docs.rs/cipher_identifier (opened; no feature list). CrypTool 2 identification (Kopal, HistoCrypt 2018) per search index, unverified.
- Exploits: score a ciphertext's statistics (IoC, max IoC and kappa over periods 1-15, digraphic IoC, three-symbol repeats, odd-spaced repeats, English digraph measures) against reference profiles for each cipher type and rank the types (per the IDENTIFY page; the page offers no "random" class).
- LP2 constraints: C1 (IoC 1.000 lands LP2 in the flat profiles only) and C2 (none of the listed features is the adjacent-repeat rate or the increment-zero hole, so the 0.66% deficit is invisible to the ranking).
- Prior coverage: grep for cipher-type, identify-cipher and classifier terms over `agents/`, `research/`, `lp/` and `dl/` found no identifier run on LP2. `REPORT.md` and the ledgers test families one at a time, not by ranking.
- Verdict: applicable-untested
- Test design: Control: plant nine families at 12,956 runes (Vigenere, Quagmire III, Playfair, homophonic, Chaocipher, additive M-209-type, Enigma-type, skip-on-repeat dynamic substitution, transposition-only), 50 instances each, with the identifier extended by the adjacent-repeat rate and lag-1 to lag-6 repeat rates; the planted family must rank first in at least 80% of trials. Null: the same ranking with label-shuffled profiles, which fixes the chance band; LP2 is then reported against that band. The expected result is that LP2 falls outside every catalogued class, which is a calibration result, not a solve.

### T: ML cipher-type classifiers
- Source: N. Kopal, "Of ciphers and neurons", HistoCrypt 2020, pp. 77-86, cited from the reference list of B. Dalton and M. Stamp, arXiv 2307.00501 (https://arxiv.org/abs/2307.00501, opened; the Kopal paper itself not opened). Dalton and Stamp's abstract: Enigma, M-209, SIGABA, Purple and Typex classified from histograms and digram counts, with above 97% accuracy at 1,000 characters in their most realistic scenario.
- Exploits: a trained classifier (neural or feature-based) assigns the cipher type to a ciphertext from statistical features, using synthetic training data for each family.
- LP2 constraints: C1 and C2b (a classifier trained on library families with IoC-type features will place a flat stream in the random class, and the walk is not a library class).
- Prior coverage: grep for classif, random forest, kNN, SVM and CNN over `agents/`, `research/`, `lp/`, `toolbox/` and the two reports found no classifier on LP2 (the only "classif" hit is the lane R transcription label `CL`, which is not a classifier).
- Verdict: applicable-untested
- Test design: Control: train on nine synthetic families at 12,956 runes (1,000 instances each) with the features of the entry above; a held-out planted instance of each family must be labelled correctly at 90% or better. Null: the same classifier trained on label-shuffled data must score at chance (1/9, with its binomial band); LP2 is then scored, and its class probabilities are reported against the random-stream null. LP2 counts as identified only if it clears both gates, and the walk is not in the training library, so a random-class answer is the expected output.

### T: DECRYPT image-to-text pipeline
- Source: Uppsala University news on DECRYPT, https://www.uu.se/en/news/2019/2019-03-26-the-goal-is-to-be-able-to-automatically-read-enciphered-historical-manuscripts (opened); Yin, Aldarrab, Megyesi and Knight, "Decipherment of Historical Manuscript Images", arXiv 1810.04297, https://arxiv.org/abs/1810.04297 (opened; abstract only).
- Exploits: unsupervised segmentation of cipher symbols from manuscript images, clustering of symbol images, and decipherment of the cluster sequence; the project is led by B. Megyesi at Uppsala and funded by the Swedish Research Council (SEK 29.5 million over seven years, per the news page). The pipeline is for handwritten images.
- LP2 constraints: C2 and C5 (transcription sensitivity: any faithful reading must keep the 86-doublet deficit and the lag-5 echo).
- Prior coverage: lane R (`agents/laneR_transcriptions/RESULTS.md`, about 20 distinct readings among 87 runic files; `REPORT_ROUND2.md` section 3: every faithful reading gives 86 doublets and a lag-5 echo of z +3.63 to +3.96).
- Verdict: applicable-tested (lane R tested the transcription question the pipeline would answer; the image pipeline itself is not needed, since LP2 is read from a glyph set, not handwriting).
- Test design: none new.

### T: LLM agent on the Marmont letter
- Source: C. Church, "Breaking the Marmont Cipher, 1809" write-up dated 2026-09-18, https://carter.church/writeups/the-letter-to-marmont/ (opened); press framing (model name and the ADFGVX claim) from https://hackaday.com/2026/09/20/world-war-i-coded-message-appears-cracked-finally/ (opened).
- Exploits: a model cut the plate into rows, read the 175 marks and merged repeated signs, and ran simulated annealing against French 3-, 4- and 5-gram scores; a published 33-value table (Tant) covered 435 of about 1,300 units as the only partial key; each sign value was checked against every occurrence and the solver was rerun without Napoleonic texts. The write-up does not name the model; the press name is GPT-6 Astra (search index). The Hackaday item reports a second, AI-credited decryption of a 1918 ADFGVX intercept with an already-known keyword, with no independent check.
- LP2 constraints: C2 (a homophonic layer gives an i.i.d. doublet floor of 1.7-2.7% against LP2's 0.66%) and C1 (the annealing needs French n-gram structure; LP2's IoC 1.000 gives it nothing to score).
- Prior coverage: `research/scout2_ai_codebreaking.md` section 1.1 (same claims, from search summaries); `research/gap_audit.md` section 4 (homophonic floor).
- Verdict: not-applicable (C2: homophone floor 1.7-2.7% against 0.66%; C1: IoC 1.000 leaves no French-like signal).
- Test design: none needed.

### T: LLM agents on Kryptos K4 and classical benchmarks
- Source: Paradigm post on K4, https://www.paradigm.xyz/writing/kryptos (opened; post dated "06.12.2026", ambiguous; authors state K4 is unsolved and that AI-assisted attempts have not succeeded, as their own claim); critique with released cribs, https://gist.github.com/atoponce/1cd01f40786ab21af011f0d6257fba0c (opened); CipherBank, https://arxiv.org/abs/2504.19093 (opened; abstract only, 2,358 problems, 9 algorithms, headline accuracy not on the abstract page).
- Exploits: LLM and agent attempts on K4 whose outputs do not place the four released cribs (the gist's reading of the cited posts), and benchmark studies showing that LLMs do weakly on classical decryption when they are given known cipher types with English plaintext.
- LP2 constraints: C1 (LP2 gives no English-level signal for a model to recognise, IoC 1.000 against 1.7-1.8) and C3 (no repeated cipher word, so no crib anchoring across the book).
- Prior coverage: lane N (`agents/laneN_cribdrag/RESULTS.md`, 5,075 cribs and about 2e10 fragments, all null; control: running English key recovered from any crib of 20 runes or more) and lane M (`REPORT.md`).
- Verdict: not-applicable (C1: IoC 1.000 against 1.7-1.8 gives an LLM no English cue; lane N: LP2 has no crib of 20 runes or more to anchor on).
- Test design: none needed.

### T: Hash verifier oracle (Paradigm design)
- Source: Paradigm K4 post, https://www.paradigm.xyz/writing/kryptos (opened; authors' description of a hash-and-HMAC verifier with $1 per guess, unsourced design claim).
- Exploits: a paid, rate-limited verifier that gives a binary signal on guesses for an unsolved cipher, so that search or AI attempts get feedback without the plaintext being exposed.
- LP2 constraints: C1 (LP2 has no English-level feedback, so the only available verifier is the page-56 hash target).
- Prior coverage: lane P (`agents/laneP_hashhunt/RESULTS.md`: null across the Wayback captures of the four signed onions, 6 hash functions and about 160 normalisations; Common Crawl not covered); `REPORT_ROUND2.md` section 5 (Common Crawl half pending).
- Verdict: applicable-tested (lane P ran the page-56 hash target as the verifier, null on archived captures).
- Test design: none new; the Common Crawl half remains open.

## Top 5

1. **Dynamic substitution with skip-on-repeat**: untested, consistent with C1, C2b and C3, and the only family here that pairs a Chaocipher-style per-letter alphabet with the skip rule the deficit requires; its lag-5 tension (C5) makes the test informative either way.
2. **Cipher-type identification from statistics**: a ranking over statistics that have never been run on LP2, with a planted-family control that shows whether LP2 falls outside every catalogued class.
3. **ML cipher-type classifiers**: the trained version of entry 2, with a label-shuffle null, and the expected random-class answer is itself a result.
4. **Neural-LM scorer in skip-aware beam**: a scorer swap inside a decoder that already has calibrated bars; low prior, but cheap to test on the Latin and Old English registers that Round 24 left n-gram-only.
5. **Zodiac Z340 stride detector**: a cheap, never-run bigram-stride scan of LP2, with a planted period-19 control; low prior because C3 gives repeats no mechanism at the stride scale.

## Sources opened
- https://chaocipher.com/chaocipher-026.htm (Exhibit 6 page, opened)
- https://kobra.uni-kassel.de/handle/123456789/15274 (Lasry thesis record, blocked by bot check, not read)
- https://aclanthology.org/P11-1025/ (Ravi and Knight, metadata only)
- https://aclanthology.org/P13-1154/ (Nuhn, Schamper and Ney, metadata only)
- https://aclanthology.org/D18-1102/ (Kambhatla et al., abstract)
- https://arxiv.org/html/2012.15229 (Aldarrab and May, full HTML)
- https://arxiv.org/html/2403.17350 (Blake, Oranchak and Van Eycke, sections to 5.4)
- https://aclanthology.org/W11-1202/ (Copiale, metadata only)
- https://www.su.se/english/research/research-projects/decipherment-of-historical-manuscripts/the-copiale-cipher-1.688288 (Copiale project page)
- https://www.cs.trincoll.edu/~crypto/hcryptoj/docs0.51/hcrypto/analyzer/DigramAnalyzer.html (Jakobsen citation and method)
- https://ep.liu.se/ecp/158/010/ecp19158010.pdf (HistoCrypt 2019 PDF, not readable)
- https://www.sites.google.com/site/cryptocrackprogram/user-guide/tools-tab/identify-cipher (IDENTIFY Cipher statistics)
- https://docs.rs/cipher_identifier (crate page, no feature list)
- https://arxiv.org/abs/2307.00501 (Dalton and Stamp, abstract)
- https://www.uu.se/en/news/2019/2019-03-26-the-goal-is-to-be-able-to-automatically-read-enciphered-historical-manuscripts (DECRYPT news)
- https://arxiv.org/abs/1810.04297 (Yin, Aldarrab, Megyesi and Knight, abstract)
- https://carter.church/writeups/the-letter-to-marmont/ (Church write-up)
- https://hackaday.com/2026/09/20/world-war-i-coded-message-appears-cracked-finally/ (press, ADFGVX claim)
- https://www.paradigm.xyz/writing/kryptos (Paradigm K4 post)
- https://gist.github.com/atoponce/1cd01f40786ab21af011f0d6257fba0c (K4 critique)
- https://arxiv.org/abs/2504.19093 (CipherBank, abstract)
