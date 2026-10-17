# Technique survey: agency-classical (2026-10-16)

Topic: standard cryptanalytic methods of signals-intelligence agencies and classical cryptanalysis (Friedman, Callimahos, Kullback, Sinkov, Kerckhoffs, Turing and Good, Tutte and the Testery, Rejewski, Hagelin, progressive and autokey systems). Each entry is graded against `toolbox/CONSTRAINTS.md` (C1 to C6) and checked against lanes A to R (`REPORT.md`, `REPORT_ROUND2.md`) and the community ledgers.

Method note: nsa.gov PDFs returned HTTP 403 to the fetch tool, and the arXiv PDF and several scanned PDFs came back as unreadable binary. Agency-specific claims therefore rest on search excerpts (listed under "Seen, not opened") or on secondary sources that were opened (listed under "Sources opened"). Where a fact is from memory it is marked "from memory, unverified". No binary was downloaded.

### T: Index of coincidence and Friedman key-length formula
- Source: Friedman's IoC theorem and key-length corollary (Riverbank Publication 22), as presented in ch. 6 sections 6.2.1 and 6.4.1 of an online cryptanalysis text, https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part2_classical_polyalphabetic/ch06_index_of_coincidence.html (opened)
- Exploits: a periodic key pulls the IoC of each column toward the language value, so the formula L = (kappa_p - kappa_r) / (IC - kappa_r) returns the key length
- LP2 constraints: C1 kills it. IoC is 1.000 on the scale where random text is 1.000, so the formula's denominator is zero, and no period 1..1500 exists
- Prior coverage: REPORT.md constraint 1 (IoC 1.000, no period 1..1500 on runes, sections, pages); lp/t4_perpage_period.py
- Verdict: not-applicable (C1: IoC 1.000 equals the random value; no period 1..1500)
- Test design: none needed

### T: Kasiski examination
- Source: Kasiski (1863) as described in ch. 5 section 5.2.3 and Theorem 5.1 of the same online text, https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part2_classical_polyalphabetic/ch05_vigenere_kasiski.html (opened)
- Exploits: repeated plaintext n-grams sit at distances divisible by the key length, so the divisors shared by the repeat distances give the key length
- LP2 constraints: C1: no period 1..1500 on runes, sections, pages or word-aligned cosets, so there is no common divisor to find; C3 leaves few repeats to factor
- Prior coverage: REPORT.md constraints 1 and 3; lp/t4_perpage_period.py
- Verdict: not-applicable (C1: no period 1..1500 on any stream)
- Test design: none needed

### T: Kullback chi-square period tests
- Source: Kullback, Statistical Methods in Cryptanalysis (NSA technical paper, 1959 revised edition per its cover). The NSA scan was seen in search results but not opened (nsa.gov returned HTTP 403). Kullback's career is confirmed at https://en.wikipedia.org/wiki/Solomon_Kullback (opened). The list of tests here is from memory, unverified.
- Exploits: chi-square tests of symbol distributions against candidate periods, and homogeneity tests across sections; the statistical successor to Friedman's IoC scan
- LP2 constraints: C1: a chi-square period scan over 1..1500 is the scan C1 already ran (no period on runes, sections or pages)
- Prior coverage: REPORT.md constraint 1 (period scan 1..1500 on runes, sections, pages)
- Verdict: not-applicable (C1: no period 1..1500 under a chi-square scan)
- Test design: none needed

### T: Probable-word crib method
- Source: crib definition and wartime use (Bletchley Park, Turing's Eins catalogue), https://en.wikipedia.org/wiki/Crib_(cryptanalysis) (opened). The method as run in this repo is lanes M and N.
- Exploits: a guessed plaintext word is slid along the ciphertext; a fragment that reads as language under the implied key is a candidate
- LP2 constraints: C3 limits what a crib can find (16 repeated words against chance); C1 forces the crib to be tested against whole key families, not a single period
- Prior coverage: lane M (agents/laneM_title_cribs/RESULTS.md): 1.43M cribs at 17 section and 55 page openings, all null, control z 13; lane N (agents/laneN_cribdrag/RESULTS.md): 5,075 cribs, full-position drag, real below null max in all 125 cells
- Verdict: applicable-tested (lanes M and N ran the crib method with planted controls and nulls)
- Test design: none needed

### T: Kerckhoffs superimposition on same-key messages
- Source: Kerckhoffs' 1883 two-part paper in Le Journal des Sciences Militaires, whose 2018 edition title names a decryption process for double-key systems, per https://en.wikipedia.org/wiki/Auguste_Kerckhoffs (opened). The superposition technique itself is from memory, unverified; the article does not describe it.
- Exploits: several messages of the same length under one key are placed one above another, so the columns share one key letter, and the common keystream shows as agreement at the right alignment
- LP2 constraints: C1 and C3: a keystream reused at any shift is the only way two stretches of LP2 could share a key; C3 says the repeats it would produce are missing
- Prior coverage: lane Q (agents/laneQ_superposition/RESULTS.md): all 55 page and 17 chapter units at every shift with overlap at least 60, raw and increments, 200 nulls each; REPORT_ROUND2.md row Q
- Verdict: applicable-tested (lane Q: null; page-length reuse not excluded at this sample size)
- Test design: none needed

### T: Turing theory of repeats at each shift
- Source: Turing, The Applications of Probability to Cryptography, section 2.3 (simple form: two cipher texts placed one under the other, X for agreement and O for difference), https://ar5iv.labs.arxiv.org/html/1505.04714 (opened; typeset edition of National Archives HW 25/37)
- Exploits: at each alignment, count agreements X against differences O; a shared substitution raises the X count at the true shift
- LP2 constraints: C1 and C3: the shift scan is the key-reuse test that rules out a periodic key at any shift (C1), and C3 caps the repeats it would find at chance
- Prior coverage: lane Q (agents/laneQ_superposition/RESULTS.md) ran this X count at every shift for pages and chapters, raw and increments
- Verdict: applicable-tested (lane Q; the X count at every shift, null)
- Test design: none needed

### T: Turing general theory of repeats run lengths
- Source: Turing section 2.3, general form, which uses runs of consecutive X marks, https://ar5iv.labs.arxiv.org/html/1505.04714 (opened)
- Exploits: a run of consecutive agreements at one shift is much rarer by chance than a single agreement, so run lengths are sharper than counts when agreements cluster
- LP2 constraints: C5 (the lag-5 echo is a clustered agreement, so runs are the natural test); C2 (a doublet is a run of length 1 at lag 1)
- Prior coverage: no run-length statistic in lane Q or lane J (grep for run, runs, consecutive finds none in either RESULTS.md). The community's within-word lag-5 digraph hits (9 against 1.53, research/scout6_delta.md) are the length-2 case at lag 5 inside words only
- Verdict: applicable-untested
- Test design: For every shift d from 1 to 40 and every page, count maximal runs of agreements c_i = c_(i-d) of length 2, and of length 3 or more, separately for runs inside words and runs crossing word boundaries. Null: 200 page-wise shuffles that keep the doublet count (lane Q protocol). Planted control: a period-13 Vigenere and a period-5 within-word walk, each planted into English at page length, which the run count must detect in at least 90% of replicates. List every cell before reporting the largest z.

### T: Turing decibans for lag-5 mechanism ranking
- Source: Turing sections 1.5 (factor principle: each piece of evidence multiplies the odds) and 1.6 (decibanage, log-odds in tenths of a log10 unit), https://ar5iv.labs.arxiv.org/html/1505.04714 (opened)
- Exploits: score each piece of evidence in decibans and add the scores, so competing models are ranked by total log-odds rather than only accepted or rejected by a z-value
- LP2 constraints: C5 (the within-word echo is the only positive signal, so each mechanism must reproduce 104 of 2105); C2 (a mechanism must also keep the doublet deficit)
- Prior coverage: lane J (agents/laneJ_lag5_echo/RESULTS.md) fitted 23 simulated mechanisms by fingerprint and significance. Its RESULTS.md has no likelihood, log-odds or deciban comparison. dl/aldegonde_clone/experiments/mechanism_fingerprint.py is a fingerprint, not a likelihood
- Verdict: applicable-untested
- Test design: For each within-word lag-5 pair in LP2, compute the deciban factor of "coincidence at the mechanism's predicted rate" against "coincidence at 1/29"; sum in word order for each mechanism and rank them. Planted control: lane J's s2_mech.py simulation of each mechanism at LP2's word structure (30 replicates per mechanism); the planted mechanism must rank first in at least 90% of replicates. Null: the real LP2 total against 1000 shuffles of word lengths within each section (lane J protocol B); report the margin of the top mechanism over the null maximum.

### T: Tutte delta and the 1+2 comparison
- Source: Tutte's delta (modulo-2 sum of successive characters) and the comparison of cipher delta with key delta at candidate settings, https://technicshistory.com/2017/09/20/the-electronic-computers-part-2-colossus/ (opened). The "1+2" label is from memory, unverified; the page does not use it.
- Exploits: the deltas of cipher and key change together, so a candidate setting is flagged when its match rate is well above 50 percent
- LP2 constraints: C1 (no period on runes; lane me is the only scan of increment periods) and C2 (a zero delta is the doublet, so the deficit is the delta statistic itself)
- Prior coverage: REPORT.md lane me (periodicity and locality on increments, all null); lane D (agents/laneD_chain_variants/s8_out.txt): periods 2 to 60 on lag-1 and lag-2 difference streams, per page; lag-1 sum z 1.02, lag-2 sum z 0.49
- Verdict: applicable-tested (lane me and lane D s8: null)
- Test design: none needed

### T: Period-13 delta match on sections 54-55
- Source: the Tutte delta-match comparison (https://technicshistory.com/2017/09/20/the-electronic-computers-part-2-colossus/, opened); the claim under test is the community's 54-55 k=13 peak, research/scout1_community.md section 6 item 3
- Exploits: a period-13 keyword added to the increments shows as a delta-match peak at lag 13. The community reports S1 = 1.72 and p about 0.016 after tuning, not replicated elsewhere
- LP2 constraints: C1 (no period 1..1500 on the whole stream; one 308-rune section is a weak test)
- Prior coverage: lane D s8 ran page-level difference streams with periods 2 to 60, not sections 54-55 under a fixed threshold. Leo's per-section lag-kappa (cited in research/scout6_delta.md, 2026-09-07 addendum) found no period signature in the real sections. The community peak was reached after interrupter tuning
- Verdict: applicable-untested
- Test design: Fix the threshold before running: the period-13 delta match on the 308 runes of 54-55 must exceed the 99th percentile of 10,000 null draws. Planted control: a period-13 keyword added to English increments at the same length and word structure; the rule must flag at least 80% of the plants. Null: 10,000 shuffles of the increments within the section that keep the zero-increment count (the doublet deficit). No interrupter removal is allowed.

### T: Trithemius progressive alphabet
- Source: https://en.wikipedia.org/wiki/Trithemius_cipher (opened): the shift grows by one per letter, equivalent to a Vigenere with the key ABC...Z
- Exploits: a progressive alphabet is a stepped periodic key; the stepping period sets the repeat structure
- LP2 constraints: C1 kills it: the counter is periodic with period 26 for the classic form, or 29 for a 29-symbol version (inference); both are far below 1500. C2: the progressive scores 3.3 percent repeats on English against 0.66 percent observed
- Prior coverage: REPORT.md constraint 1; research/scout3_norepeat_generators.md (Trithemius/progressive row: 3.3 percent English, NO)
- Verdict: not-applicable (C1: stepping period 26 or 29; C2: 3.3 percent repeats against 0.66 percent)
- Test design: none needed

### T: Progressive-alphabet isomorph search
- Source: the progressive-alphabet isomorph method, from a Friedman military-cryptanalysis chapter with an isomorph section (table of contents seen in an NSA search excerpt, not opened). The period behaviour of progressive systems is in https://en.wikipedia.org/wiki/Trithemius_cipher (opened).
- Exploits: under a progressive alphabet, pattern-equal words (isomorphs) share a step, which reveals the alphabet sequence
- LP2 constraints: C3 (repeated words at chance) and C5 (the only within-word coincidence signal is the lag-5 echo, which isomorph counts must account for)
- Prior coverage: dl/aldegonde_clone/experiments/isomorph_census.py (pattern rates against per-distance rates: summed z 6.6 on 6 df, p about 0.36; no cell survives Bonferroni); isomorph_corrected.py (doublet-corrected null); isomorph_g_score.py (g-only isomorph objective: gradient real, recovery 0 to 3 of 29 positions, negative); dl/aldegonde_clone/docs/lag5-phenomenon.md
- Verdict: applicable-tested (community isomorph census and g-score; a ledger-style record, not a lane A-R)
- Test design: none needed

### T: Autokey analysis
- Source: https://en.wikipedia.org/wiki/Autokey_cipher (opened): Kasiski and IoC do not work on ciphertext; the probable-word attack on autokey. The Callimahos Part III chapters IV to XI revise the autokey monograph, per https://www.schneier.com/blog/archives/2021/01/military-cryptanalytics-part-iii.html (opened)
- Exploits: the key is a primer followed by the text (plaintext autokey) or by the ciphertext, so the key never repeats
- LP2 constraints: C2: plaintext autokey gives 4.8 percent repeats and ciphertext autokey 2.7 percent (research/scout3_norepeat_generators.md simulation) against 0.66 percent observed. C1: no period, so Kasiski-type attacks are void
- Prior coverage: lane C (agents/laneC_gematria_structure/autokey.c and RESULTS.md); lane D (agents/laneD_chain_variants/RESULTS.md); dl/dukotah/liber-primus/LEDGER.json entry R12-C1 (autokey, negative)
- Verdict: not-applicable (C2: 2.7 to 4.8 percent repeats against 0.66 percent)
- Test design: none needed

### T: Hill cipher and linear polygraphic systems
- Source: https://en.wikipedia.org/wiki/Hill_cipher (opened): block vector times an invertible matrix mod 26, completely linear, broken from n-squared known pairs. The Sinkov chapter on matrix and polygraphic methods (Elementary Cryptanalysis, MAA 1966) was seen in a catalogue excerpt, not opened.
- Exploits: a block-linear map, so known-plaintext pairs solve the matrix; adjacent outputs inside a block are linear in the plaintext
- LP2 constraints: C2: a linear map over Z29 repeats adjacent runes at about 1/29 = 3.4 percent, far from 0.66 percent
- Prior coverage: research/scout2_ai_codebreaking.md (Berlekamp-Massey over GF(29) on LP2: linear complexity n/2); REPORT.md constraint 1
- Verdict: not-applicable (C2: about 3.4 percent repeats for a block-linear map)
- Test design: none needed

### T: Transposition and columnar analysis
- Source: https://en.wikipedia.org/wiki/Transposition_cipher (opened): transposition preserves letter frequencies; columnar attacks guess column lengths and search for anagrams
- Exploits: runes are reordered, not changed, so symbol counts and the index of coincidence survive
- LP2 constraints: C1: the IoC depends only on symbol counts, so any permutation of English keeps about 1.7 to 1.8, while LP2 is 1.000. This also covers word-level scrambles of English, which research/scout1_community.md lists as untested (the IoC argument is an exclusion, not a test)
- Prior coverage: research/scout5_layout_and_nontext.md (seam tests exclude shuffling after encryption); research/scout1_community.md section 6 lead 2 (word-level scramble listed as untested); lane E (agents/laneE_language_id: plaintext language identification, English minus THE/OF)
- Verdict: not-applicable (C1: any permutation of English keeps IoC about 1.7; LP2 is 1.000; holds only if the plaintext is itself flat, which lane E does not support)
- Test design: none needed

### T: Good sequential burst scan of the lag-5 echo
- Source: Turing sections 1.5 and 1.6 (factor principle and decibans), https://ar5iv.labs.arxiv.org/html/1505.04714 (opened). Good's sequential extension (I. J. Good, Probability and the Weighing of Evidence, 1950) is from memory, unverified.
- Exploits: a running deciban total along the stream flags a short cluster of lag-5 coincidences that a whole-book count would dilute
- LP2 constraints: C5 (the echo is reported as diffuse; a localized burst is a different claim); C2 (the doublet rate in a window sets the null's reference rate)
- Prior coverage: REPORT.md constraint 5 (diffuse across positions and sections, from count tests); lane J (agents/laneJ_lag5_echo/RESULTS.md): protocol B word-length shuffles; no sequential scan in lane J
- Verdict: applicable-untested
- Test design: Running deciban total over within-word lag-5 pairs in stream order, with the echo's fitted rate (4.94 percent) against 1/29. The flag threshold is fixed before running so that the null false-flag rate per section is 5 percent. Planted control: insert 12 extra within-word lag-5 coincidences into a 200-pair window of a null stream; the scan must flag that window in at least 90% of replicates. Null: 1000 word-length shuffles within sections (lane J protocol B), counting flagged windows per shuffle; the real count must sit inside the null band.

### T: Tutte delta pre-screen for the quagmire-dodge sweep
- Source: https://technicshistory.com/2017/09/20/the-electronic-computers-part-2-colossus/ (opened): delta match at candidate settings, flagged well above 50 percent
- Exploits: a cheap delta-match statistic on 200-rune windows, used as a pre-filter before the full dodge-aware scorer of the planned sweep
- LP2 constraints: C2 (the dodge family is the one that fits the doublet deficit, so C2 is its main test); C5 (the lag-5 echo is the family's second test)
- Prior coverage: REPORT_ROUND2.md row O (validated, not run, 3.9e9 keys, about 360 core-hours); agents/laneO_quagmire_dodge/RESULTS.md section 7. No delta pre-screen exists in any lane
- Verdict: applicable-untested
- Test design: For each candidate key in lane O's enumeration, compute the delta-match rate between the cipher's increments and the key's increments over 200-rune windows. Keep keys whose best window exceeds the null maximum from 1000 doublet-preserving shuffles of the rune stream. Planted control: lane O's own 100 planted keyword keys (REPORT_ROUND2.md row O); at least 95 must pass the screen, and the true key must pass in every planted run. Report the fraction of the sweep kept as the screen's power.

### T: Rejewski cycle method
- Source: https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part4_enigma/ch11_polish_codebreakers.html (opened): sections 11.2.2 to 11.2.5
- Exploits: the doubled message key gives three characteristic permutations; their cycle structure is a fingerprint of rotor positions, looked up in a precomputed catalogue of 26 cubed starts
- LP2 constraints: C3: the method needs the same six-rune indicator structure repeated across messages, and the catalogue's rotor-start space is a small per-word state that C3 excludes (16 repeated words against 11.0 plus or minus 3.1 random)
- Prior coverage: none. No LP2 analogue of the doubled key, and no run of this method in the repo
- Verdict: not-applicable (C3: 16 repeated words against 11.0 plus or minus 3.1 at random)
- Test design: none needed

### T: Hagelin M-209 ciphertext-only attack
- Source: https://en.wikipedia.org/wiki/M-209 (opened): period 26 x 25 x 23 x 21 x 19 x 17 = 101,405,850 letters; the ciphertext-only attack by Reeds, Ritchie and Morris was described but not published, per the article
- Exploits: six pin wheels drive a letter-dependent shift, so the keystream depends on wheel positions and pins, not on the ciphertext
- LP2 constraints: C2: a keystream independent of the previous rune predicts about 3.4 to 3.8 percent adjacent repeats, and the M-209 has no anti-repeat rule (analytic, not simulated). C1 does not kill it: its period is about 1e8
- Prior coverage: none in the repo
- Verdict: not-applicable (C2: predicts about 3.4 to 3.8 percent repeats against 0.66 percent; analytic)
- Test design: none needed

### T: Chaining and symmetry of position for primary alphabets
- Source: https://en.wikipedia.org/wiki/Trithemius_cipher (opened): a stepped alphabet is a chain of alphabets, each shifted from the last. The chaining procedure in Friedman and Callimahos, Military Cryptanalytics, was seen in a search excerpt, not opened. The symmetry-of-position method is from memory, unverified.
- Exploits: aligned plaintext fixes the relation between two alphabets, so chaining rebuilds the primary alphabet step by step; symmetry of position uses messages whose key positions are mirrored
- LP2 constraints: C3: chaining needs repeated plaintext at aligned positions, and LP2's 16 repeated cipher words are at chance; C1: a stepped chain would also be periodic
- Prior coverage: research/gap_audit.md section 2 (fixed-alphabet sets excluded by pigeonhole); REPORT.md row K (fixed-alphabet model excluded; K = 5 forces at least 482 repeated words)
- Verdict: not-applicable (C3: chaining needs aligned repeats; 16 repeated words against chance)
- Test design: none needed

## Top 5
1. Turing decibans for lag-5 mechanism ranking: the strongest signal, and no lane compares the mechanisms by likelihood; the planted control reuses lane J's own simulator.
2. Turing general theory of repeats run lengths: a sharper statistic than the count tests of lanes Q and J, and cheap to run under lane Q's protocol.
3. Good sequential burst scan of the lag-5 echo: tests whether the echo is localized, a different claim from the diffuse count results already reported.
4. Period-13 delta match on sections 54-55: the community's only tuned peak, untested under a fixed threshold; the 308-rune section gives low power.
5. Tutte delta pre-screen for the quagmire-dodge sweep: a cheap filter for the best-fitting family before the roughly 360 core-hour run.

## Sources opened
- https://ar5iv.labs.arxiv.org/html/1505.04714 (Turing, The Applications of Probability to Cryptography; typeset HTML of National Archives HW 25/37)
- https://technicshistory.com/2017/09/20/the-electronic-computers-part-2-colossus/ (Tutte delta and match-rate comparison, secondary)
- https://www.schneier.com/blog/archives/2021/01/military-cryptanalytics-part-iii.html (Callimahos, Military Cryptanalytics Part III, 1977; scope and revised chapters; secondary)
- https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part2_classical_polyalphabetic/ch06_index_of_coincidence.html (IoC and Friedman theorem; online text)
- https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part2_classical_polyalphabetic/ch05_vigenere_kasiski.html (Kasiski examination; online text)
- https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part4_enigma/ch11_polish_codebreakers.html (Rejewski cycle method; online text)
- https://en.wikipedia.org/wiki/M-209 (Hagelin M-209; secondary)
- https://en.wikipedia.org/wiki/Crib_(cryptanalysis) (cribs and probable words; secondary)
- https://en.wikipedia.org/wiki/Auguste_Kerckhoffs (Kerckhoffs 1883; secondary)
- https://en.wikipedia.org/wiki/Trithemius_cipher (progressive key; secondary)
- https://en.wikipedia.org/wiki/Hill_cipher (Hill cipher; secondary)
- https://en.wikipedia.org/wiki/Transposition_cipher (transposition; secondary)
- https://en.wikipedia.org/wiki/Autokey_cipher (autokey; secondary)
- https://en.wikipedia.org/wiki/Solomon_Kullback (Kullback's career; secondary)

## Seen, not opened
These came from search excerpts or failed to load. No entry relies on them for a URL, and each fact that depends on them is marked in the entry.
- https://www.nsa.gov/Portals/75/documents/news-features/declassified-documents/friedman-documents/publications/FOLDER_242/41748189078749.pdf (Military Cryptanalytics Part I, NSA scan, December 1952; HTTP 403)
- https://www.nsa.gov/news-features/declassified-documents/friedman-documents/assets/files/publications/FOLDER_228/41760349079953.pdf (Kullback, Statistical Methods in Cryptanalysis, NSA scan A58459; HTTP 403)
- https://www.nsa.gov/news-features/declassified-documents/friedman-documents/assets/files/publications/FOLDER_241/41748389078762.pdf (NSA Friedman document; HTTP 403)
- https://www.governmentattic.org/39docs/NSAmilitaryCryptalyticsPt3_1977.pdf (Part III 1977 redacted copy, linked from the Schneier post; not opened)
- https://www.theblackvault.com/documentarchive/cryptologic-quarterly-articles/ (Cryptologic Quarterly list; no stepping or isomorph article found in the excerpt)
- https://bookstore.ams.org/NML/22 and https://old.maa.org/node/109915 (Sinkov listing; HTTP 403 and 521)
- https://bibliotheques-numeriques.defense.gouv.fr/impression/document/8802e9ea-9d80-4d75-921e-fc3907a2a472 (French defence library record of Kerckhoffs 1883; connection refused)
- https://arxiv.org/pdf/1505.04714 and https://bribes.org/crypto/Military_Cryptanalysis_Friedman_3.pdf (PDF binaries; unreadable through the fetch tool)
- https://ecp.ep.liu.se/index.php/histocrypt/article/download/694/600 (Ekhall and Schmeh, M-209 paper; PDF binary, unreadable)
- An NSA 1949 stepping-wheel memo (cribs, depths and isomorphs named as required data) appeared only in a search excerpt. It is not cited.
