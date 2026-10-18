# Exhaustion census, part web (WB-), LP2 pages 0-54

## Bottom line
- 43 rows, all from pages opened in this run; 0 strength A, 0 strength B, 2 C, 41 D. No web source gives a stated key space with a planted control that I could read.
- 18 rows are dead by C1 or C2 (quick exclusions); 25 are not dead and all 25 are reopen candidates, mostly transposition and book-index families that no lane here covers.
- Every Wulfic control cell is unclear: its table says "Yes" but the test file it cites is not in the source. Pitchfork and ZzNible report nulls or exclusions without null distributions.
- No source claims a solve. Reddit refused (fetch tool), Fandom returned 402, and the DEF CON captions and the kookscience wiki could not be read; see Sources checked.
- Largest gap against our lanes: page-level transposition families (rail fence, spirals, wing-and-tree, columnar) and Playfair-type digraphs have no lane (coverage none).

## Census
| id | method | family | scope searched | control | null | source | strength | our coverage | constraint |
|---|---|---|---|---|---|---|---|---|---|
| WB-01 | Periodic keys, including a plus-or-minus F interrupter | polyalphabetic-periodic | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane A (keyword chains); lanes M and N (Vigenere and Beaufort, with and without skip) | unclear: dead C1 for periods up to 1500 only; periods 1501 and up are not excluded by C1 |
| WB-02 | Integer-sequence keys: 46 sequences, raw and chained | prime/totient stream | 46 sequences, raw and chained; chain depth not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | C | lane C (gematria-number keystreams, prime autokeys); REPORT.md:61 (46 integer sequences) | unclear: raw sequence keys are dead C2 (about 3.4% doublets); chained forms are not sized |
| WB-03 | Autokey, variant not stated | autokey/chain | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane C (word-sum and prime autokeys); REPORT.md:61 (autokey) | unclear: variant not stated, so C1 and C2 cannot be checked from this source |
| WB-04 | Prime feedback | autokey/chain | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane C (prime autokeys); lane S (totient stream) | unclear: feedback form not stated |
| WB-05 | Cicada running keys | running-key/book | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane N (running-text keys of any English text, cribs of 20 runes or more); lane H (book-code pointers) | dead C2: an additive running key independent of the ciphertext predicts about 3.4% doublets (LP2 0.66%) |
| WB-06 | Shared keys, one key over two sections | polyalphabetic-periodic | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane Q (key reuse at every shift and lag) | dead C1: one key shared by two sections is excluded by C1 |
| WB-07 | Digraphic ciphers; Playfair, two-square and four-square | other | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md, https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: fixed digraph table, no key space stated |
| WB-08 | Key-text search over about 200 key texts | running-key/book | about 200 key texts (stated count, not exhaustive over all texts) | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | C | lane N (any English running key); REPORT.md:61 (about 200 running-key texts) | dead C2: an additive running key predicts about 3.4% doublets |
| WB-09 | Key derivation functions and PRNG keystreams | PRNG/hash keystream | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane B (hash and KDF keystreams); lane G (era PRNGs) | dead C2: an additive keystream independent of the ciphertext predicts about 3.4% doublets |
| WB-10 | Public random archives and on-disk byte sources as running key (stage Y) | PRNG/hash keystream | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md, https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/README.md | D | REPORT.md:61 (14.5e9 offsets into public randomness); lane G | dead C2: an additive running key from a byte source predicts about 3.4% doublets |
| WB-11 | Simple (monoalphabetic) substitution | monoalphabetic | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | none | dead C1: a fixed substitution is period 1, and LP2 is flat at every order |
| WB-12 | Standard Vigenere or Beaufort with keyword keys | polyalphabetic-periodic | keyword keys; no search size reported | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane A (keyword chains); lanes M and N | dead C1: keyword keys have periods far below 1500 |
| WB-13 | Transposition followed by a stream cipher | transposition | not stated | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | none | dead C2: the final additive stream is independent of the ciphertext |
| WB-14 | Single-rune-word known-plaintext attack at a fixed key position | other | fixed key position; no key size | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane M (title cribs); lane N (crib drag) | unclear: source says it constrains plaintext only and fails once a skip rule desynchronises the stream |
| WB-15 | Prime-based streams: totient of primes, Fibonacci-prime, spiral-ordered primes | prime/totient stream | stream alone, on LP-English; analytic prediction, no search | unclear | unclear | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane S (totient stream, all starts and skip phases); lane T (prime-seeded walk) | dead C2: predicted doublet rate 3.2 to 3.6 percent against LP2 0.66 percent |
| WB-16 | F-skip rule on unsolved pages (rune-0 count) | other | count test on the LP2 body; no search | unclear | unclear | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md | D | lane S (literal F and collision skip) | unclear: rune-0 count argument (458 against 447 expected), not one of C1 to C6 |
| WB-17 | Branches: binary-fork and left-right half-merge | transposition | pages 8 to 14; no size stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: page-level permutation; no key size stated |
| WB-18 | Spirals: spiral-order and ring-order | transposition | pages 3 to 7; no size stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: page-level permutation; no key size stated |
| WB-19 | Wing-and-Tree: leaf-order and branch-order | transposition | pages 27 to 32; no size stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: page-level permutation; no key size stated |
| WB-20 | Cross-height rail-fence | transposition | pages 0 to 2; rail count not stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: rail count not stated |
| WB-21 | Mayfly: GP-direction, numbers as direction | other | pages 23 to 26; rule not stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: direction rule not stated |
| WB-22 | Sexagesimal block as transposition instruction | transposition | pages 33 to 39; no size stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: no size stated |
| WB-23 | Sexagesimal block as running key | running-key/book | pages 32 to 39; one base-60 block | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | dead C2: an additive running key independent of the ciphertext predicts about 3.4% doublets |
| WB-24 | Mobius direction-reversal (Gauntlet cycle 3) | other | pages 15 to 22; no size stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: no size stated |
| WB-25 | OutGuess: default key, and passworded passes 1 and 2 | layout/stego | default-key output of 58,152 bytes; passworded passes, passwords not listed | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research, https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane I (cover channels); REPORT.md:61 (OutGuess of every image) | unclear: stego extraction, not a rune cipher; no key space stated |
| WB-26 | Book-index cipher | running-key/book | not stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | lane H (book-code pointers) | unclear: index mapping not sized |
| WB-27 | Word-unit book cipher | running-key/book | not stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | lane H (book-code pointers) | unclear: word-unit mapping not sized |
| WB-28 | Columnar transposition | transposition | width not stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: no width stated |
| WB-29 | Acrostic (first runes of lines) | other | not stated | n | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | unclear: calibration failed, so a negative here is not informative |
| WB-30 | Homophonic substitution (zkdecrypto-lite) | monoalphabetic | not stated | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | none | dead C2: homophonic i.i.d. choice predicts about 3.4% doublets |
| WB-31 | Archive lookup for the AN END (page-56) hash | other | one hash; archive captures not sized | unclear | n | https://github.com/Pitchfork-and-Torch/liber-research | D | lane P (hash hunt, Wayback captures) | unclear: a lookup for one hash, not a rune decryption |
| WB-32 | Per-page Caesar or fixed substitution keyed to the 3:5:8 selection | monoalphabetic | per page; selector 3:5:8 | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | none | dead C1: a fixed key per page is period 1 at page level |
| WB-33 | Period-55 Vigenere over the 55 runes picked by 3:5:8 | polyalphabetic-periodic | period 55 over 55 runes | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | none | unclear: a period equal to the text length cannot be tested by C1 on 55 runes |
| WB-34 | Periods 5, 19 and 1279 as general cipher explanations | polyalphabetic-periodic | periods 5, 19 and 1279; no search | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane U (period 13); lanes J and V (lag-5 echo) | dead C1: periods 5, 19 and 1279 all lie within 1 to 1500 |
| WB-35 | Short-key Vigenere, basic Caesar, basic affine | polyalphabetic-periodic | short keys; no search size | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane A; lane M | dead C1: short periodic keys and period-1 maps |
| WB-36 | Reading the 55 runes picked by 3:5:8 directly as English | other | 55 runes | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | none | unclear: no key; direct reading not sized |
| WB-37 | Historical item-4 material on [39:135] used as a pad | running-key/book | one span [39:135] | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane N (running-text keys) | dead C2: an additive pad independent of the ciphertext predicts about 3.4% doublets |
| WB-38 | T13 subpixel A/B channels and JPEG 9 and 10 pixel-grid channels | layout/stego | channels; no key space | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane I (cover channels, 22 channels with encodings) | unclear: image channel, not a rune stream |
| WB-39 | Basic Fibonacci keystreams | prime/totient stream | Fibonacci sequences; no size | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane C (gematria-number keystreams, full period) | dead C2: an additive keystream predicts about 3.4% doublets |
| WB-40 | Pure no-repeat and simple max-run-2 models for K=86 | walk/dodge | K=86 doublet count; no key size | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane O (Quagmire dodge, tiers A and B); lane T | dead C2: the pure no-repeat model predicts zero doublets against 86 observed |
| WB-41 | Word-reset architectures as the main explanation of the adjacent-equality anomaly | walk/dodge | not stated | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane K (walk feasibility) | unclear: an explanation of the anomaly, not a key model with a size |
| WB-42 | Literal, uncontrolled use of the phrase "shed your circumference" as key | running-key/book | one phrase | unclear | n | https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md | D | lane M (Cicada phrase cribs); lane N | dead C2: a literal running key is additive and independent of the ciphertext |
| WB-43 | Key-free tests of the 256-byte base-60 grid (stage X): rules out a periodically keyed text, an RSA modulus and compressed streams | other | 256 bytes of the pages 49-51 grid; no key | unclear | n | https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/README.md | D | none | unclear: tests the 256-byte grid, not the 12,956 runes, so the LP2 fingerprint does not apply |

## Reopen candidates
- WB-01: periodic keys with periods 1501 to about 6400 (C1 does not exclude them), each with a planted key and a shuffled-key null.
- WB-02: chained integer-sequence keys with ciphertext feedback, over the 46 sequences, with a planted key and a null.
- WB-03, WB-04: autokey and prime-feedback forms with the feedback rule written out, a planted key and a null.
- WB-07: keyed Playfair, two-square and four-square tables over a stated keyword list, with a planted key and a doublet-rate and word-hit null.
- WB-14: single-rune crib at fixed key positions, with a planted key and a null.
- WB-16: F-passthrough rule with a planted key; compare the rune-0 count with the 447 expectation.
- WB-17, WB-18, WB-19, WB-20, WB-21, WB-22, WB-28: page-level transposition families (binary fork, spirals, wing-and-tree, rail fence, mayfly direction, sexagesimal instruction, columnar widths), with a planted permutation and a null over shuffles. No lane here covers them.
- WB-24: Mobius direction reversal, same design as the transposition set.
- WB-25: OutGuess with a stated password list over every LP2 image, with a planted payload and a null; REPORT.md:61 already ran the default key, so only new passwords add.
- WB-26, WB-27: book-index and word-unit book cipher with a stated list of source texts and a planted control.
- WB-29: acrostic re-run with a calibration that works, since the source's calibration failed.
- WB-31: any new archive pass only through hashhunt with --allowlist; lane P already ran 80 Wayback queries.
- WB-33: period-55 key on the 3:5:8 selection, with a plaintext-scoring null (C1 cannot test it on 55 runes).
- WB-36: direct reading of the 55 runes, scored against English with a shuffle null.
- WB-38: image-channel tests of the T13 and JPEG grid channels, with a planted channel and a null (lane I covers similar channels).
- WB-41: the word-reset rule written as a key model, with a planted control.
- WB-43: the key-free grid tests re-run on a planted grid, with a null, if the grid is ever tied to the rune stream.

## Sources checked
Opened and read as text in this run (WebFetch returns a model summary of each page, so quotes in the rows are paraphrase):
- https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/reference/community/community_research.md: rows WB-01 to WB-16 (section 10 table).
- https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/README.md: stage list; only stages X and Y state an outcome (WB-10, WB-43); stages Z to AH give none and are not counted.
- https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/NEGATIVE_RESULTS.md: rows WB-32 to WB-42.
- https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/FINDINGS.md: one glyph detector with 0 hits; not a decryption method, so no row. Its lag-5 result is positive.
- https://github.com/Pitchfork-and-Torch/liber-research: rows WB-07 and WB-17 to WB-31.
- https://raw.githubusercontent.com/crashdemons/Cicada-DWH-HashcatAttempts/master/README.md and https://github.com/crashdemons/Cicada-DWH-HashcatAttempts: describe hashcat tests and a results folder; the results are not in the text I read, so no row.
- https://raw.githubusercontent.com/scream314/cicada3301/master/hints_never_used.md: labels with no outcome; no row.
- https://raw.githubusercontent.com/scream314/cicada3301/master/pages_and_ciphers.md: solved-method labels and "?" ranges; no failure claim; no row.
- https://github.com/cicada-solvers: organisation listing (names only).
- https://github.com/cicada-solvers/cmbcidada3301: tool README, no results.
- https://github.com/cicada-solvers/LiberPrimusSolver: Hill, Vigenere and Atbash task runner; no results or controls stated.
- https://github.com/cicada-solvers/lp-decrypter: functions-of-two-runes brute force; no results.
- https://github.com/cicada-solvers/lphelper: no description; no results.
- https://github.com/cicada-solvers/miteo-3301tools: file names only; no results.
- https://github.com/yo-yo-yo-jbo/cicada_tools: untested hypotheses (digraph model); no failures reported.
- https://www.cicadasolvers.com/wiki/liber-primus/: LP1 solved, LP2 0-55 unsolved; no failed method listed.
- https://cicadasolvers.com: navigation only.
- https://boxentriq.com/guides/cicada-3301-liber-primus: no failed method reported.
- https://cicada3301.boards.net/: index with thread titles only ("fibonacci mod[29]", "Why is solving hard?"); no failure text read.

Failed (not retrieved):
- https://old.reddit.com/r/cicada/search?q=liber+primus+failed&restrict_sr=1: refused by the fetch tool.
- https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Unsolved_Pages: HTTP 402.
- https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/echo446ghq_analysis.md: HTTP 404.
- https://github.com/krisyotam/cicada3301: HTTP 404.
- https://nahgcorp.substack.com/p/part-2-the-internets-most-beautiful: HTTP 404.
- DEF CON 31 "Cracking Cicada 3301" caption file on media.defcon.org: connection reset, twice.
- https://hatch.kookscience.com/wiki/Cicada_3301: self-signed certificate error.

Search snippets only, not opened (not sources): the Boxentriq totient cipher page, freebsd12.rsyslog.com mirrors, the cicada-solvers idkfa-web repo, and blog and news results.
