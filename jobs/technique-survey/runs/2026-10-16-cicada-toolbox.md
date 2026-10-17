# Technique survey: cicada-toolbox (2026-10-16)

Topic: every cipher, encoding and puzzle technique Cicada 3301 used in the 2012, 2013 and 2014 puzzles and on the solved Liber Primus pages, and the techniques solvers used to break each step. Each entry is graded against toolbox/CONSTRAINTS.md (C1-C6) and checked against the lane results in REPORT.md, REPORT_ROUND2.md, the agents/ lanes A-R, and the community ledgers.

## Access and method notes
- Local corpus read: dl/dukotah/corpus/A-primary-artifacts/pgp/messages (2012-2017 signed messages), dl/dukotah/liber-primus/SOLVED-PAGES.json, the community ledgers and campaign results, and the Uncovering Cicada wiki export under dl/dukotah/corpus/C-community/wikis/uncovering-cicada/ (MediaWiki XML, 1,763 pages).
- Clearweb: the fandom wiki returned HTTP 402 on a live fetch, so wiki pages are cited from the local export (canonical URLs listed under Sources opened). The NSA PDF returned HTTP 403. outguess.org does not resolve from this machine. An Oosterhof search returned nothing relevant.
- toolbox/CONSTRAINTS.md refers to toolbox/fingerprint.py, which is not in the repo. Statistics below were computed from lp/lpdata.py directly.
- Nothing downloaded and no binaries run. Community Python rig modules (dl/dukotah/liber-primus/src/lp) were imported read-only for a few checks. No onion or tor2web access. No network calls from those checks.

## Checks run for this survey
- LP2 (pages 0-54, 12,956 runes; loader pin matches): F = 458 (3.54%). Adjacent doublets 86, of which 4 involve F. Pairs touching F: 912 (4 doublets). Non-F adjacent pairs: 12,043 with 82 doublets = 0.68%, against about 3.5% uniform.
- Solved-page ciphertext (pages 01, 05, 06, 03, 14 as parsed by the rig): non-F adjacent pairs 1,692 with 46 doublets = 2.72%.
- Page 05 grid, with the Gematria Primus prime values (SHADOWS = CABAL = 341): every row, column and both diagonals sum to 1033. The 'An instruction' numeric grid: every row, column and diagonal sums to 3301.
- The 2014 RSA-OAEP modulus (130 digits, e = 65537) equals p x q for the two 65-digit primes published on the wiki (checked: True).
- Prime-totient stream with the F-interrupter beam on the AN END page (lpdata index 55, labelled 56.jpg; 85 runes, 5 F): decodes to ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGE..., score -4.573, one interrupter. The same stream on index 56 does not decode (-7.344).
- Page 03 with the wiki's in-range skip indices and the F read as a pass-through: WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEYTOWARDTHEENDOFALL..., score -4.332. The rig's beam (solve.find_interrupters) deletes a skipped F, giving ENDOALL (score -4.363 for the same skips); SOLVED-PAGES.json page 03 carries that deletion. Four of the wiki's eleven skip indices (421, 443, 465, 514) lie beyond the 394 runes parsed for that page, and for page 14 the wiki index 56 is not an F. The wiki's skip indexing does not fully reproduce here.
- The rune spelling of CIRCUMFERENCE occurs once in the whole book, at rune index 13,094, which is after LP2's 12,956 runes.
- The six-rune DJUBEI occurs twice: global index 6,555 (page index 27, position 28) and 12,950 (page index 54, position 70).
- The transcription has 6 digit tokens, all page markers. LP2 contains no numeric grid.

### T: Atbash, constant shifts and unencrypted passages
- Source: Solved-page methods in dl/dukotah/liber-primus/SOLVED-PAGES.json (page 01 atbash+shift+0, page 06 atbash+shift+3, page 05 shift+0 and direct transliterations); https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved (local export, sections 'A warning', 'Some wisdom', 'Koan 1').
- Exploits: A fixed 29-letter reflection (i to 28-i) and a constant shift mod 29 are monoalphabetic maps with one key value per page. Unencrypted pages are the same map with the zero key. Atbash on a keystream is a sign flip of the key (x to -x).
- LP2 constraints: C1 (flat at every order: LP2 IoC is 1.000; any fixed monoalphabetic map or plaintext keeps English-level IoC of about 1.7-1.8).
- Prior coverage: lane N negates and shifts every fragment in both signs (agents/laneN_cribdrag/RESULTS.md); lane D treats Atbash of a prime-order alphabet as the same unit map (agents/laneD_chain_variants/RESULTS.md); unencrypted English was tested by lane E (agents/laneE_language_id).
- Verdict: not-applicable (C1: a monoalphabetic or zero-key page would show English-level IoC, and LP2 is flat at 1.000 over all 12,956 runes; the sign flip inside a keystream is covered by lane N).
- Test design: none needed, excluded by a statistic.

### T: Vigenere with word key and F-interrupt
- Source: SOLVED-PAGES.json pages 03 (key DIVINITY, 7 beam-found interrupters) and 14 (key FIRFUMFERENFE, 2 interrupters); wiki 'How the solved pages...' (Welcome: skip indices 48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514; Koan 2: skip indices 49, 56), https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved (local export). Friedman's Military Cryptanalytics Part II covers repeating-key systems per https://en.wikipedia.org/wiki/Military_Cryptanalytics (summary only; the NSA PDF was not readable).
- Exploits: The key index advances once per emitted rune; a literal F (rune index 0) is copied through and does not consume the key. Page 03 with the in-range wiki skips reads WELCOMEWELCOMEPILGRIMTOTHEGREATJOURNEY (checked here).
- LP2 constraints: C1 (no period 1..1500 in rune position; a skip moves the key index off the rune index, so C1 alone does not kill a skip-Vigenere) and C3 (small key state; repeated cipher words at chance: 16 against 11 random).
- Prior coverage: lane A keyword chain with skip-aware Vigenere and Beaufort (agents/laneA_keyword_chain/RESULTS.md); lane M Vigenere with skip-on-repeat and F-interrupts (agents/laneM_title_cribs/RESULTS.md); lane N raw Vigenere with and without skip and F-interrupt (agents/laneN_cribdrag/RESULTS.md); community RUN-keywords-full.log: about 620 keywords, 0 hits, best -6.021.
- Verdict: applicable-tested (lanes A, M, N; community RUN-keywords-full.log).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: F-interrupt as the doublet mechanism
- Source: The literal-F readings on pages 03, 14 and AN END (above); dl/dukotah/analysis/reproduce/reproduce_page_56_an_end.py (community script, read, not run; it applies the F beam to the prime-totient key); https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Ideas_and_Suggestions (local export: the community's doublet observation, 86 same-rune pairs in about 13,000 runes).
- Exploits: A literal F leaves the output unchanged and does not advance the key. It shifts the alignment of everything after it but produces no repeat suppression by itself.
- LP2 constraints: C2 (doublet deficit): 912 pairs touch an F and only 4 are doublets; 82 of 12,043 non-F pairs are doublets (0.68%, against about 3.5%). Skipping F cannot remove the non-F suppression.
- Prior coverage: lanes M and N model F-interrupts (agents/laneM_title_cribs/RESULTS.md, agents/laneN_cribdrag/RESULTS.md); community RUN-interrupter-full.log: 10 texts by 55 pages, 0 hits, best -5.911 (dl/dukotah/liber-primus/analysis/campaign18_skip/CAMPAIGN-XVIII-FINDINGS.md).
- Verdict: not-applicable (C2: the F rule touches 7% of adjacent pairs and only 4 of 86 doublets, so it cannot produce the suppression of non-F doublets. As a component of a larger model it is applicable and tested; see the joint entry.)
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Rigid prime-totient keystream
- Source: The AN END page (LP page 56, lpdata index 55): key (p_i - 1) mod 29 over consecutive primes, decrypt C - K, with F interrupters (dl/dukotah/analysis/reproduce/reproduce_page_56_an_end.py, read); reproduced here (85 runes, one literal F, readable ANEND text). https://uncovering-cicada.fandom.com/wiki/Gematria_Primus (local export) for the 29-value table.
- Exploits: The key advances once per emitted rune through phi(2)=1, phi(3)=2, phi(5)=4, ... mod 29. This is the one solved-page generator beyond keywords.
- LP2 constraints: C2 (a rigid aperiodic stream against English gives about 3.5% adjacent repeats; LP2 has 0.68%). C1 is satisfied (no period), so C2 is the killer.
- Prior coverage: per-page prime-totient decodes with the F beam and no unsolved page above -5.5 (dl/dukotah/liber-primus/analysis/structure/CAMPAIGN-IV-FINDINGS.md); community campaign18 RUN-rosetta.log (phi(prime) with the skip-aware beam, global best -6.334, 0 hits).
- Verdict: not-applicable (C2: a rigid phi(prime) stream predicts about 3.5% doublets on English; LP2 has 0.68%. It was tested per page anyway; the skip variant is the next entry.)
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Collision-skip on prime-totient keystream
- Source: Campaign XV probe P1: dl/dukotah/corpus/H-branch-recovery/recovered/claude_cicada-3301-scope-cigxzi/liber-primus/analysis/campaign15/P1-skip-beam_RESULT.md and P1-skip-beam.py. The doublet observation is at https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Ideas_and_Suggestions (local export).
- Exploits: When the candidate rune would equal the previous output, the key advances an extra step with probability p_soft. P1's synthetic plant (phi(prime), p_soft 0.83) gives 0.375% doublets, which mimics LP2's 0.66%.
- LP2 constraints: C2 (the family produces the suppression with one parameter) and C1 (aperiodic stream).
- Prior coverage: P1 ran 2,876 skip-aware real decodes (phi(prime), primes, totients, prime gaps, Fibonacci seeds, 21 keytexts, offsets, both signs, plus or minus Atbash); grand best -6.442 against gate -5.2, none clear. Community campaign18 RUN-rosetta.log: 0 hits. LEDGER.json R18-L2-A-LOCUS (skip is the pinned model M1). P1 has no literal-F rule.
- Verdict: applicable-tested (P1-skip-beam_RESULT.md; campaign18 RUN-rosetta.log; LEDGER.json R18-L2-A-LOCUS).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Prime-totient keystream with literal F and collision skip
- Source: Both halves are solved-page or community evidence: the literal-F rule on AN END (entry above) and the collision-skip fingerprint (entry above). dl/dukotah/liber-primus/analysis/campaign18_skip/armada/rosetta_keys.py docstring says the LP1 F-skip is 'the same mechanic class as the LP2 doublet filter' but the two are never run together. Code check: sweep.beam (campaign18) and P1 handle only the collision skip; solve.find_interrupters (dl/dukotah/liber-primus/src/lp/solve.py) handles only F. Pass-through reading per https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved (local export).
- Exploits: One decoder with both Cicada-demonstrated machinery and the LP2 mechanism: a literal F does not advance the key, and a would-be repeat does. Generators: phi(p_i) mod 29, and p_i mod 29 as a second generator.
- LP2 constraints: C2 (the collision skip carries the suppression; the literal F leaves non-F pairs alone), C1 (aperiodic stream), C3 (a continuous stream has no per-word state to repeat, consistent with 16 repeats against 11 random). C5 is not explained by this model; a failure there is informative.
- Prior coverage: not run. Nearest: P1 (collision only), rosetta (collision only), CAMPAIGN-IV-FINDINGS.md (F only, rigid). No lane or ledger row combines them.
- Verdict: applicable-untested.
- Test design: Decoder: beam over (position, key index j). A ciphertext F is either literal (emit F, j unchanged) or encrypted (emit the plaintext, j+1). On a would-be repeat, allow j to advance by 2 at a penalty, as in P1. Output must be pass-through, not deletion (the rig's find_interrupters deletes the F and misreads page 03). Grid: generator phi(p) and p; offsets 0-1,000 at step 1 and 1,000-12,955 at step 16; both signs; plus or minus Atbash; plus or minus +3; gate score_norm > -5.2; top decodes adjudicated on held-out 400-rune chunks. Planted control: 1,600 runes of SOLVED-PAGES page 05 text enciphered with the same joint model at p_soft 0.83; the decoder must recover at least 90% and beat the wrong generators (plain primes, Fibonacci mod 29) by 2 or more score units. Size-matched null: the same grid on 200 within-page shuffles of the LP2 ciphertext (these keep doublet counts) and 200 random-offset copies; report the real maximum against the null maximum per cell.

### T: Prime-seeded Oosterhof walk
- Source: Oosterhof's walk as described in toolbox/CONSTRAINTS.md (quick exclusions) and agents/laneK_walk_search/RESULTS.md (model M_K and the doublet-dodge walk); the phi(p) generator from SOLVED-PAGES.json (AN END). The doublet observation is at https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Ideas_and_Suggestions (local export).
- Exploits: The per-word choices (exponent e_w and permutation index sigma_w) come from the solved-page generator instead of free keys. Period-5 alphabets inside words and skip-on-repeat stay as in the walk. This puts the Cicada generator into the only family consistent with C1-C6.
- LP2 constraints: C2 (skip-on-repeat supplies the suppression), C5 (period-5 phases inside words are the only structure fitting the lag-5 echo), C3 (per-word base keeps repeated words at chance).
- Prior coverage: lane K (free-key walk: searchable only when most of the walk is given; no global search solves the doublet-dodge walk at n = 12,956; agents/laneK_walk_search/RESULTS.md); lane L (keyword-built walk keys, 2^55.6 per start, null; agents/laneL_keyword_walk). Prime-seeded selectors were not run.
- Verdict: applicable-untested.
- Test design: Enumerate the generator offset, sign and Atbash (a few thousand combinations). Build the walk with per-word selectors read from the stream and decode with the skip-aware beam used in lane K. Planted control: encipher 1,600 runes of SOLVED-PAGES page 05 text with the same selector walk and recover at least 90%; the decoder must separate it from wrong offsets. Size-matched null: 200 walks whose selectors come from shuffled stream values, and the same grid on LP2 with word lengths shuffled; report the real score against the null maximum.

### T: Quagmire odometer dodge over Cicada vocabulary
- Source: The community sweep ported and audited in agents/laneO_quagmire_dodge (RESULTS.md section 4 for validation and section 7 for the orchestrator checks); REPORT_ROUND2.md section 3 (lane O row) and section 5 (launch command).
- Exploits: An odometer of keyword alphabets advances when the output would repeat, which is a collision skip on the alphabet index. Zero-offset keyword alphabets come from Cicada's vocabulary (DIVINITY, CIRCUMFERENCE and others).
- LP2 constraints: C2 (the dodge gives the suppression), C3 (odometer state per word is small against the repeat count), C1 (aperiodic odometer schedule).
- Prior coverage: lane O validation: 95 of 100 keyword plants at rank 1 (median z +23.7). One counter-plant at rank 24,558 of 105,980 (RESULTS.md section 4c), and the orchestrator reproduces about a 5% miss rate (section 7). The full run was not executed: 3.9e9 keys, about 360 core-hours.
- Verdict: applicable-untested.
- Test design: Planted control: 100 keyword alphabets (seeds 100-199) scored with the sweep's own score_key, 2,000 wrong schedules per plant (95 of 100 at rank 1 already measured; repeat to confirm). Null: the same scorer on the LP2 word-length register with rune values shuffled, and the sweep's own 3.9e9 wrong keys. A true key counts only if it clears the global null maximum and survives held-out chunk adjudication of the 1,200 retained candidates (adjudicate.py). Run only after the owner's go-ahead (REPORT_ROUND2.md section 5).

### T: Collision skip on other keystreams and walks
- Source: Oosterhof's doublet-dodge walk and the community's pinned LP2 model (LEDGER.json R18-L2-A-LOCUS: ciphertext key-skip M1 is the repo's pinned model, compared with M0 to M5). The doublet observation is at https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Ideas_and_Suggestions (local export).
- Exploits: Skip the key on a would-be repeat. This is the one rule that makes an LP2-sized deficit at small cost. It is not shown on any solved page: their non-F doublet rate is 2.72% (46 of 1,692 pairs), against 0.68% in LP2.
- LP2 constraints: C2 (this is the mechanism that fits the deficit), C1 (keystream aperiodic), C3 (per-word state).
- Prior coverage: lane D candidate 6, per-page keyword key-skip, excluded for L = 5 to 20 (agents/laneD_chain_variants/RESULTS.md); lane K, free walk with skip, search infeasible at n = 12,956 (agents/laneK_walk_search/RESULTS.md); lane M, skip-on-repeat Vigenere keyed by PILGRIMAGE and DIVINITY (agents/laneM_title_cribs/RESULTS.md); LEDGER.json R24-C2-SKIP-BY-TWO-DECODER (negative).
- Verdict: applicable-tested (lanes D, K, M; LEDGER.json R18-L2-A-LOCUS).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Book-code pointers 2012 to 2014
- Source: 2014 opening book code (dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2014-01-opening-book-code.asc; paragraph:sentence:word:letter); 2013 opening book code (I:1:6 chapter:verse, Liber AL); 2012 Mabinogion book code (line:word tuples, 'the product of the first two primes' = 6); research/scout4_cicada_sources.md section 1; https://en.wikipedia.org/wiki/Cicada_3301 (book codes named, method not described).
- Exploits: A coordinate names a symbol in a fixed text. The pointer changes the source of the symbol, not how the key advances.
- LP2 constraints: C3 (a fixed-text pointer gives repeated cipher words the same source, and LP2's 16 repeated words sit at chance), C4 (layout is not plaintext layout).
- Prior coverage: lane H (agents/laneH_bookcode_pointers/RESULTS.md): 10,880 configurations, 32,512 scored rows. The Self-Reliance parse was validated on the 2014 code (15 of 15 pointers). The 2013 Liber AL code was not reproduced. The 2012 Mabinogion format has no published decode and is covered only by generic tuples.
- Verdict: applicable-tested (lane H).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Gibson Agrippa poem as 2012 book code
- Source: https://en.wikipedia.org/wiki/Agrippa_%28A_Book_of_the_Dead%29 (fetched: 1992 poem by Gibson, Ashbaugh and Begos; a floppy designed to scramble after one viewing; Agrippa served as the key for a book cipher in the 2012 puzzle); the 2012 book-code message (dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2012-01-book-code-poem.asc).
- Exploits: The poem's words are the pointer target. The 2012 coordinates address it.
- LP2 constraints: C3 (a fixed-text pointer must keep repeated cipher words at chance; LP2 has 16 repeats against 11 random).
- Prior coverage: research/scout4_cicada_sources.md row 2 and lead 4 (untested; the text is not on disk and is copyrighted). Lane H covers Cornelius Agrippa's Occult Philosophy (agents/laneH_bookcode_pointers/RESULTS.md); community RUN-armada18 ran that same book, not Gibson's poem.
- Verdict: applicable-untested (blocked: the poem is not in the corpus and cannot be reproduced here; it needs a licensed copy).
- Test design: Planted control: encode a 60-rune English sentence with the 2012 coordinate scheme over a public-domain stand-in with the same line-word structure (for example the 1651 Occult Philosophy text already in armada18), and confirm the decoder returns it. Null: the same scheme with coordinates drawn uniformly over the stand-in's line-word table, 200 draws, scored with the same statistic. The real test needs the poem under a licence; not run.

### T: Gematria Primus values and word sums as key
- Source: Gematria Primus value table (F=2 to EA=109) in https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved (local export, 'Gematria Values'); https://uncovering-cicada.fandom.com/wiki/Gematria_Primus (local export: the 761.mp3 XOR that produced the alphabet, and the 'Count' command).
- Exploits: Runes carry consecutive prime values, so word sums, prime-valued keys and gematria-driven shifts are natural candidates. The rig works mod 29 on rune indices.
- LP2 constraints: C1 (flat), C2 (prime-domain and word-sum keys predict about 3.5% doublets unless snapped with a skip rule).
- Prior coverage: lane C: per-letter primes, word sums, totients, prime-counting indices and self-keying by word sums, all at the size-matched null (30 observables, max |z| 2.3; agents/laneC_gematria_structure/RESULTS.md). Lane D: prime-domain mod 109 and 110 snap constructions excluded (LLR -581 to -11,304; agents/laneD_chain_variants/RESULTS.md). Lane A: GF(29) multiplicative and prime-value chains null (agents/laneA_keyword_chain/RESULTS.md).
- Verdict: applicable-tested (lanes C, D, A).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Magic squares with constants 1033 and 3301
- Source: Solved page 05 'Some wisdom' 5x5 grid of numbers and rune words (SOLVED-PAGES.json page 05; wiki section 'Some wisdom' in https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved, local export); the solved 'An instruction' numeric grid (same page); https://uncovering-cicada.fandom.com/wiki/Gematria_Primus (local export: 'gematria summing the words completes a magic square').
- Exploits: A 5x5 grid whose rows, columns and diagonals share one constant. Checked here: gematria-summed rune words give 1033 on every line of the first grid, and the numeric grid gives 3301 on every line.
- LP2 constraints: C4 (LP2's layout is not plaintext layout, and LP2 holds no numeric grid: the transcription has 6 digit tokens, all page markers).
- Prior coverage: lane C (solved-page word sums as key families: null) and lane B (3301 as a hash seed, 152M trials) cover the constants as keys. No grid exists in LP2 to complete.
- Verdict: not-applicable (C4: LP2 has no numeric or word-sum grid to complete; the constants were tested as seeds in lane B).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Numerology seeds 3301 and 761
- Source: https://uncovering-cicada.fandom.com/wiki/Mentioned_PRIMES (local export: 1729 = 3301 in octal, 1033 = 2011 in octal); research/scout4_cicada_sources.md section 4 (509 x 503 x 3301 = 845,145,127, computed there); the 761 'Instar' value in the Gematria Primus page (local export).
- Exploits: Numbers as PRNG seeds, offsets or sums.
- LP2 constraints: C1 (a numeric seed gives a PRNG keystream, which is aperiodic) and C2 (a PRNG stream predicts about 3.5% doublets unless skipped).
- Prior coverage: lane B (3301-seeded hash and KDF keystreams, 152M trials, best 1.0279 against null maximum 1.0287; agents/laneB_hash_keystreams/RESULTS.md); lane G (era PRNGs, 143,022 seeds, 16.9M streams; agents/laneG_prng_generators/RESULTS.md); lane C numerology families.
- Verdict: applicable-tested (lanes B, G, C).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: RSA and PGP steps of 2014
- Source: 2014 RSA-OAEP challenge (dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2014-01-rsa-oaep-challenge.asc: e = 65537, Crypt::RSA::ES::OAEP); https://uncovering-cicada.fandom.com/wiki/Program_to_decrypt_RSA_message (local export: the p and q values); https://uncovering-cicada.fandom.com/wiki/CICADA_3301_2014_PUZZLE (local export; the cado-nfs factorization, about 8 hours, is in an IRC log in the same export); 2012 key announcement (key ID 7A35090F).
- Exploits: Factor a 130-digit modulus, then decrypt the OAEP message. The factors are verified here (p x q = n). The decrypted message is not in the local corpus.
- LP2 constraints: C1 (the RSA output is a fixed message, not a keystream; LP2's runes are flat and aperiodic, and no link from an RSA plaintext to them is shown).
- Prior coverage: campaign15 P9 (dl/dukotah/corpus/H-branch-recovery/recovered/claude_cicada-3301-scope-cigxzi/liber-primus/analysis/campaign15/P9-rsa-rescore_RESULT.md): 0 of 12 pow() structure tests on the 4096-bit PGP moduli. The 2014 challenge plaintext was never run through LP2.
- Verdict: not-applicable (C1: the RSA step produces a message, not a stream, and no link to LP2's aperiodic runes is shown. The modulus is factored, which closes the puzzle layer.)
- Test design: none needed; excluded by the constraint named in Verdict.

### T: OutGuess payloads in JPEG images
- Source: https://uncovering-cicada.fandom.com/wiki/OutGuess (local export: the outguess -r extraction and the 2012 image chain); the 2014 messages 2014-01-magic-square-upload-outguess-10 to 13 and 2014-01-fallen-behind-outguess-08 (local .asc under dl/dukotah/corpus/A-primary-artifacts/pgp/messages).
- Exploits: Message bits hidden in JPEG DCT coefficients. The 2012 and 2014 payloads carry instructions and PGP text. A payload could in principle hold a key or a selector.
- LP2 constraints: C1 (a payload used as a key must be flat and aperiodic) and C2 (a payload used as a plain key predicts about 3.5% doublets).
- Prior coverage: REPORT.md section 'On top of the community record' (OutGuess of every image: null); community RUN-numeric2-full.log (payload-as-key at all offsets: 0 hits); LEDGER.json R29-L1-ONION-STEGO (onion image payload: negative).
- Verdict: applicable-tested (REPORT.md; LEDGER.json R29-L1-ONION-STEGO).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Whitespace and trailing-space encodings
- Source: 2013 rune table in tabs and spaces (dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2013-01-rune-table-morse.asc); 2012 final message trailing-space counts 0, 2, 3, 5, 7, 11, 13 (https://uncovering-cicada.fandom.com/wiki/Possible_hints_never_used, local export).
- Exploits: Whitespace counts carry numbers (here the prime sequence), and a tab/space alphabet carries a rune table. This is a separate layer from the cipher.
- LP2 constraints: C4 (layout is not plaintext layout; adjacent word lengths are independent) and C5 (the only layout-level echo is about 2.5 sigma).
- Prior coverage: lane I (agents/laneI_layout_channel/RESULTS.md): 22 layout channels, 221k cells, 200 shuffles each; 9 cells under 0.05 against 5 expected; no readable fragment.
- Verdict: applicable-tested (lane I).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Repeating-key XOR and totient strings from 2014
- Source: https://uncovering-cicada.fandom.com/wiki/2014_THINGS_THAT_HAD_BEEN_XORED (local export: example 2, repeating key of length 3 or 11; the totient strings from numints); ledger row H-03 (the 2013 cookies XORed against the hex strings, recorded as never executed).
- Exploits: Byte-wise XOR of hex strings with repeating keys of length 1 to 3 or 11.
- LP2 constraints: C1 (a repeating key of any length up to 1,500 is excluded: LP2 has no period 1..1500).
- Prior coverage: LEDGER.json H-03 and R12-A1 (CicadaOS binaries as pads: negative). The wiki's own example 2 tries keys of length 1 to 3 only.
- Verdict: not-applicable (C1: a repeating key is periodic, and LP2 has no period 1..1500).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Hill and digraphic ciphers
- Source: The solved-page method table in https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved (local export: no digraphic cipher among the methods). Community record: dl/dukotah/liber-primus/analysis/campaign18_skip/armada2/COVERAGE-MATRIX.md (Hill 2x2 and 3x3: rigid null, outside the skip lens).
- Exploits: A linear mix over pairs or triples of runes mod 29.
- LP2 constraints: C2 (a generic linear layer gives c_i = c_(i+1) about 1/29 of the time, far above LP2's 0.68%).
- Prior coverage: campaign18 COVERAGE-MATRIX.md (rigid null, stated as excluded by alignment-independent statistics).
- Verdict: not-applicable (C2: a generic linear layer predicts about 3.5% adjacent repeats; LP2 has 0.68%).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Stego-keyed permutation of runes
- Source: dl/dukotah/liber-primus/analysis/armada/recon-community-exhausted.md section 5, item 2 (OutGuess-driven re-ordering listed as untried); https://uncovering-cicada.fandom.com/wiki/OutGuess (local export).
- Exploits: Reorder runes by a permutation read from a stego payload, before or after substitution.
- LP2 constraints: C2 (a permutation chosen independently of the values keeps the 1/29 expectation for random-like runes; only a value-dependent permutation can cut doublets, and that is a skip rule in disguise).
- Prior coverage: listed as untried in recon-community-exhausted.md; no lane here.
- Verdict: not-applicable (C2: an independent permutation keeps about 3.5% adjacent repeats on random-like runes. A value-dependent one is a collision skip, covered by the collision-skip entries.)
- Test design: none needed; excluded by the constraint named in Verdict.

### T: External running-key texts
- Source: community corpus armada18 (41 texts) and armada19 (47 texts) under dl/dukotah/liber-primus/data/keys; campaign18 RUN-fullcorpus.log (122 texts by 55 pages); Cicada's own solved text as key (SOLVED-PAGES.json); research/scout4_cicada_sources.md section 2; https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved (local export, for the solved text).
- Exploits: A text's runes (or letters) used as the running key, decrypted at a start offset.
- LP2 constraints: C1 (text keystreams are aperiodic) and C2 (a plain text key predicts about 3.5% doublets unless the skip rule is applied).
- Prior coverage: lane N: 5,075 cribs, full-position drag; a running English key is recovered from any crib of at least 20 runes (z 10 to 18), so the test has power (agents/laneN_cribdrag/RESULTS.md). Lane M: 1.43M cribs (agents/laneM_title_cribs/RESULTS.md). Community RUN-fullcorpus.log: 0 hits, best -5.808.
- Verdict: applicable-tested (lanes M, N).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Autokey on plaintext and ciphertext
- Source: The community's leading hypothesis (dl/dukotah/liber-primus/analysis/armada/recon-community-exhausted.md section 2). Friedman, Military Cryptanalytics Part II, covers repeating-key and periodic systems per the summary at https://en.wikipedia.org/wiki/Military_Cryptanalytics; autokey is not named there, and the NSA PDF was not read.
- Exploits: The key is the plaintext or ciphertext itself, after a primer.
- LP2 constraints: C1 (flat IoC; a plaintext autokey flattens English IoC, so C1 does not decide it) and C2 (a rigid autokey predicts a doublet rate that a skip rule must bring down).
- Prior coverage: lane C (self-keying by ciphertext primes and word sums, autokey family: null at the size-matched floor; agents/laneC_gematria_structure/RESULTS.md). Community RUN-autokey-full.log: 45 primers, both signs, skip-aware, 0 hits, best -6.627.
- Verdict: applicable-tested (lane C; campaign18 RUN-autokey-full.log).
- Test design: none needed; excluded by the constraint named in Verdict.

### T: Interconnectedness MP3 as running-key carrier
- Source: dl/dukotah/corpus/A-primary-artifacts/2014/signed_interconnectedness_decoded.bin (MPEG Layer III, ID3v2.3, title 'Interconnectedness', artist '3301', LAME 3.98.2) and the signed hex message corpus_2014-01-interconnectedness-hex.asc; research/scout4_cicada_sources.md section 6, lead 5 (spectrogram and post-frame data not yet checked).
- Exploits: The signed 2014 file's bytes, reduced mod 29, as a running key; or its post-frame data as a carrier. The file is signed by Cicada, so it is a Cicada artifact rather than a community pad.
- LP2 constraints: C1 (a byte stream is aperiodic and flat) and C2 (a plain byte key predicts about 3.5% doublets; it needs the collision-skip decoder).
- Prior coverage: LEDGER.json R12-A1 (five CicadaOS pads including 761.mp3: negative) and R28-L1-CICADAOS-PADS-DENSE-PAIR (negative). The 2014 Interconnectedness file is not among those pads.
- Verdict: applicable-untested.
- Test design: Mapping: key byte b to b mod 29, with b mod 28 and rejection variants as sensitivity checks. Decoder: the skip-aware beam of the collision-skip entry, offsets 0-4,096 bytes, both signs, plus or minus Atbash. Planted control: encipher 1,600 runes of SOLVED-PAGES page 05 text with the MP3's own bytes as the key under the same mapping and decoder, and recover at least 90%. Size-matched null: 200 byte-shuffled copies of the MP3 (same histogram) and 200 random byte offsets, scored with the same statistic; gate -5.2 as in P1. Check the post-frame bytes and ID3 fields as a separate carrier first.

### T: DJUBEI six-gram key-state coincidence test
- Source: research/scout5_layout_and_nontext.md section 4.1 (DJUBEI occurs twice, pages 27 to 32 and the end of 54 to 55); dl/dukotah/liber-primus/analysis/armada/recon-community-exhausted.md section 4 ('the only live crib'); locally, rune indices 6,555 (page index 27, position 28) and 12,950 (page index 54, position 70) in lp/lpdata.py.
- Exploits: An identical six-rune cipher run at distance 6,395 means either equal plaintext with equal key state, or a chance repeat. Under a continuous aperiodic key, equal key windows of length six have probability about 29 to the minus 6 at a given alignment, so the test asks which model class can produce equal states.
- LP2 constraints: C3 (repeated cipher words at chance; a six-gram repeat is rare under any small-state cipher) and C1 (no period).
- Prior coverage: lane Q (key reuse at lags 1 to 12,896; power-limited for page-length reuse; agents/laneQ_superposition/RESULTS.md). Scout 5 counts the repeat only. Not run as a key-state test.
- Verdict: applicable-untested.
- Test design: For each model (the rigid stream, the collision-skip stream, the walk), compute the key windows at both occurrences using the skip-aware index. A model passes only if equal plaintext there implies equal key windows. Planted control: insert one six-rune English phrase at two positions 6,395 apart in a synthetic LP2-like stream made with the same model, and check that the test flags it. Null: 1,000 random pairs of six-rune positions at distance 6,395 in the real stream, and 1,000 page-internal shuffles; report the count of consistent pairs against the null. Expected to be null; low prior.

### T: CicadaOS binaries as pads
- Source: https://uncovering-cicada.fandom.com/wiki/Files_found_in_Cicada_OS (local export: folly, wisdom, aberr, 98-tc.rules); the telnet missing-primes list at https://uncovering-cicada.fandom.com/wiki/Possible_hints_never_used (local export); 761.mp3 (Gematria Primus page: the XOR that produced the alphabet).
- Exploits: Period-correct binaries and text files used as pads: keystreams taken from bytes.
- LP2 constraints: C1 (a pad from a file is aperiodic; the test is about which pad) and C2 (a plain byte pad predicts 3.5% doublets; it needs a skip rule).
- Prior coverage: LEDGER.json R12-A1 (five pads; best per-page -6.517 at 560.17, page 54) and R28-L1-CICADAOS-PADS-DENSE-PAIR (24,080 of 24,080 rows, negative); campaign18 RUN-numeric.log (prime-list streams).
- Verdict: applicable-tested (LEDGER.json R12-A1; LEDGER.json R28-L1-CICADAOS-PADS-DENSE-PAIR).
- Test design: none needed; excluded by the constraint named in Verdict.

## Key-advance rules Cicada used, and whether a variant can make LP2's fingerprint

| rule | on solved pages | can it alone produce C2? | status |
|---|---|---|---|
| literal F, key not consumed | yes: pages 03 and 14 (wiki and rig), AN END (one literal F) | no: F pairs are 7% of the stream and hold 4 of 86 doublets | tested (lanes M, N); the joint variant is untested (entry 6) |
| prime-totient step, key advances per emitted rune | yes: AN END | no: rigid gives about 3.5% doublets | rigid excluded by C2; skip variant tested (P1, rosetta) |
| word-key Vigenere (DIVINITY, FIRFUMFERENFE) | yes: pages 03, 14 | no: C1 kills short periods; skip versions tested | tested |
| key continues across pages | per rosetta_keys.py notes on pages 14/15 and 73 (community code docstring; not verified here) | not applicable | tested (P1, rosetta) |
| collision skip (key advances when the output would repeat) | no: solved non-F doublet rate is 2.72% (46 of 1,692), not suppressed | yes, with one parameter (P1 synthetic: 0.375% at p_soft 0.83) | tested on keyword, prime, walk and PRNG sources: null |
| rejection draw skipping (skip-by-two) | no | yes, as a community model | LEDGER.json R24-C2-SKIP-BY-TWO-DECODER: negative |
| atbash and constant shift | yes: pages 01, 06 | not a key advance | tested as a sign flip (lane N) |

Reading: the only rule with solved-page evidence that could sit inside LP2's fingerprint is the literal F plus the collision skip, run on a solved-page generator. That combination is untested (entry 6). The solved pages show no repeat suppression (2.72%, against 0.68% in LP2; Poisson z about 10 for the difference at LP2's rate), so the deficit is not a property of Cicada's demonstrated ciphers and must come from a skip rule that is either absent from the solved pages or specific to LP2. Two rig caveats for any joint test: the skipped F must be passed through, and the wiki's skip indices for page 03 do not all reproduce in our parse.

## Top 5
1. **Prime-totient keystream with literal F and collision skip**: the only rule set that uses both Cicada-demonstrated machinery (literal F, phi(p) generator) and the LP2 suppression mechanism; no code path runs the two together.
2. **Prime-seeded Oosterhof walk**: ties the walk family, the only one consistent with C1-C6, to the solved-page generator; the seed space is small enough to sweep completely.
3. **Quagmire odometer dodge over Cicada vocabulary**: validated and ready; the full run is 3.9e9 keys (about 360 core-hours) and needs the owner's go-ahead.
4. **Interconnectedness MP3 as running-key carrier**: a signed 2014 Cicada file never tested as a key; local, and cheap to run.
5. **DJUBEI six-gram key-state coincidence test**: the only live repeat in LP2; low prior, likely null, but decisive for the key-state models.

## Sources opened
- https://uncovering-cicada.fandom.com/wiki/How_the_solved_pages_of_the_Liber_Primus_were_solved (live fetch returned HTTP 402; read from the local export under dl/dukotah/corpus/C-community/wikis/uncovering-cicada/)
- https://uncovering-cicada.fandom.com/wiki/Gematria_Primus (local export)
- https://uncovering-cicada.fandom.com/wiki/OutGuess (local export)
- https://uncovering-cicada.fandom.com/wiki/Possible_hints_never_used (local export)
- https://uncovering-cicada.fandom.com/wiki/Mentioned_PRIMES (local export)
- https://uncovering-cicada.fandom.com/wiki/2014_THINGS_THAT_HAD_BEEN_XORED (local export)
- https://uncovering-cicada.fandom.com/wiki/Program_to_decrypt_RSA_message (local export)
- https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Ideas_and_Suggestions (local export)
- https://uncovering-cicada.fandom.com/wiki/Files_found_in_Cicada_OS (local export)
- https://uncovering-cicada.fandom.com/wiki/CICADA_3301_2014_PUZZLE (local export)
- https://en.wikipedia.org/wiki/Agrippa_%28A_Book_of_the_Dead%29 (fetched)
- https://en.wikipedia.org/wiki/Military_Cryptanalytics (fetched; summary of declassification status and Part II content)
- https://en.wikipedia.org/wiki/Cicada_3301 (fetched; no method named for book codes or OutGuess)
- Local files read (not URLs): dl/dukotah/liber-primus/SOLVED-PAGES.json; dl/dukotah/analysis/reproduce/reproduce_page_56_an_end.py; dl/dukotah/liber-primus/analysis/armada/recon-community-exhausted.md; dl/dukotah/liber-primus/analysis/structure/CAMPAIGN-IV-FINDINGS.md; dl/dukotah/liber-primus/analysis/campaign18_skip/ (armada/rosetta_keys.py, armada/rosetta_sweep.py, sweep.py, RUN-*.log, armada2/COVERAGE-MATRIX.md, CAMPAIGN-XVIII-FINDINGS.md); dl/dukotah/liber-primus/LEDGER.json; the campaign15 P1 and P9 files under dl/dukotah/corpus/H-branch-recovery/; dl/dukotah/corpus/A-primary-artifacts/pgp/messages/*.asc; dl/dukotah/corpus/A-primary-artifacts/2014/signed_interconnectedness_decoded.bin (size and ID3 header only); research/scout4_cicada_sources.md; research/scout5_layout_and_nontext.md; REPORT.md; REPORT_ROUND2.md; toolbox/CONSTRAINTS.md; agents/laneA through laneQ (RESULTS.md).
