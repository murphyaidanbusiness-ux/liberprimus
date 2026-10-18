# Technique catalogue (graded against toolbox/CONSTRAINTS.md)

Built 2026-10-16 from three technique-survey runs (`jobs/technique-survey/runs/`): **agency-classical** (Friedman,
Kullback, Kerckhoffs, Turing and Good, Tutte, Rejewski), **computational-ai** (Lasry, Jakobsen, Knight/Ravi/Nuhn,
neural decipherment, Copiale, Z340, DECRYPT, LLM agents) and **cicada-toolbox** (every cipher Cicada used 2012-2014 and in
the solved pages). 64 techniques: 16 applicable and untested, 20 applicable and already tested, 28 not applicable.
Each entry's source, test design and grep evidence are in its survey file.

## How to use this file
- A new idea: find it below first. If it is listed as not applicable, the constraint that kills it is given.
- A cipher family goes to `jobs/hypothesis-gate/` before any compute; a signal analysis goes straight to `jobs/attack-lane/`
  with a planted control and a null.
- Caveats: nsa.gov refused the surveys' PDF requests (HTTP 403), so the agency entries rest on opened secondary sources and
  are flagged where they come from memory or search excerpts. The fandom wiki returned HTTP 402; wiki facts come from the
  local export in `dl/dukotah/corpus/C-community/wikis/`.

## Applicable and untested (16)

### A. Cipher families: gate them (`jobs/hypothesis-gate/`), then attack
| # | technique | survey | why it is live |
|---|---|---|---|
| A1 | Dynamic substitution with skip-on-repeat | computational-ai | Chaocipher-style per-letter evolving alphabet; plain Chaocipher gives 3.7-4.2% doublets (fails C2), the skip variant is untested |
| A2 | Prime-totient keystream with literal F and collision skip | cicada-toolbox | the solved-page machinery (phi(prime) shifts, F passed through) plus the repeat suppression LP2 needs; no code path runs both |
| A3 | Prime-seeded Oosterhof walk | cicada-toolbox | the one family consistent with C1-C6, with its permutations generated from Cicada's own prime/totient numerology instead of free or keyword-built |
| A4 | Gibson's Agrippa poem as a book code | cicada-toolbox | Cicada's 2012 source text; lane H tested Self-Reliance, Liber AL and the Mabinogion, not Agrippa |
| A5 | Interconnectedness MP3 as a running-key carrier | cicada-toolbox | a signed 2014 file never used as a key; needs a skip rule to meet C2 and the file on disk (a download needs the owner's OK) |
| A6 | Quagmire-odometer dodge over Cicada's vocabulary | cicada-toolbox, lane O | validated port, 3.9e9 keys (~360 core-hours); waiting for the owner's go-ahead |

### B. Analyses of the two signals: run as attack lanes with a plant and a null
| # | technique | survey | question |
|---|---|---|---|
| B1 | Turing decibans for lag-5 mechanism ranking | agency-classical | rank lane J's candidate mechanisms by likelihood on the echo, not by count tests |
| B2 | Turing's general theory of repeats (run lengths) | agency-classical | are coincidence runs at lag 5 longer than chance? a sharper statistic than counts |
| B3 | Good's sequential burst scan of the lag-5 echo | agency-classical | is the echo localised in some pages or sections, or diffuse? |
| B4 | Period-13 delta match on sections 54-55, fixed threshold | agency-classical | the community's one tuned periodic peak, re-tested without tuning |
| B5 | DJUBEI six-gram key-state coincidence | cicada-toolbox | the only live long repeat in LP2: chance or a state return? |
| B6 | Zodiac Z340 bigram-stride detector | computational-ai | a never-run stride scan; low prior (C3) |

### C. Method aids
| # | technique | survey | use |
|---|---|---|---|
| C1 | Cipher-type identification from statistics | computational-ai | run a catalogue of families through `gate_sim.py`: which, if any, reproduce the fingerprint |
| C2 | ML cipher-type classifiers | computational-ai | the trained version of C1, with a label-shuffle null |
| C3 | Neural-LM scorer inside a skip-aware beam | computational-ai | a scorer swap for decoders that already have calibrated bars; low prior |
| C4 | Tutte delta pre-screen for the dodge sweep | agency-classical | a cheap filter that could cut lane O's 360 core-hours, if it keeps every planted key |

## Corrections the surveys found
- Word-level scrambles of English are excluded by C1: IoC is permutation-invariant, so scrambled English keeps IoC ~1.7.
  `research/scout1_community.md` lists them as untested.
- Cicada's solved pages show no repeat suppression (2.72% doublets; the cicada-toolbox survey's figure, not re-derived
  here), and the F-interrupt cannot make LP2's deficit: pairs involving F hold 4 of the 86 doublets and non-F pairs run
  at 0.68%. The suppression is a mechanism Cicada never demonstrated on a solved page.
- `dl/dukotah/liber-primus/SOLVED-PAGES.json` carries deletion artefacts: page 03 reads `...TOWARDTHEENDOALLTHNGS...`
  where the sense is "toward the end of all things" (checked by the orchestrator). Scorers trained on it inherit the gaps.

## Applicable and already tested (use these as methods; do not re-run without saying what is new)

| technique | survey | grading |
|---|---|---|
| Probable-word crib method | agency-classical | lane M (agents/laneM_title_cribs/RESULTS.md): 1.43M cribs at 17 section and 55 page openings, all null, control z 13; lane N (agents/laneN_cribdrag/R… |
| Kerckhoffs superimposition on same-key messages | agency-classical | lane Q (agents/laneQ_superposition/RESULTS.md): all 55 page and 17 chapter units at every shift with overlap at least 60, raw and increments, 200 nul… |
| Turing theory of repeats at each shift | agency-classical | lane Q (agents/laneQ_superposition/RESULTS.md) ran this X count at every shift for pages and chapters, raw and increments |
| Tutte delta and the 1+2 comparison | agency-classical | REPORT.md lane me (periodicity and locality on increments, all null); lane D (agents/laneD_chain_variants/s8_out.txt): periods 2 to 60 on lag-1 and l… |
| Progressive-alphabet isomorph search | agency-classical | dl/aldegonde_clone/experiments/isomorph_census.py (pattern rates against per-distance rates: summed z 6.6 on 6 df, p about 0.36; no cell survives Bon… |
| Vigenere with word key and F-interrupt | cicada-toolbox | lane A keyword chain with skip-aware Vigenere and Beaufort (agents/laneA_keyword_chain/RESULTS.md); lane M Vigenere with skip-on-repeat and F-interru… |
| Collision-skip on prime-totient keystream | cicada-toolbox | P1 ran 2,876 skip-aware real decodes (phi(prime), primes, totients, prime gaps, Fibonacci seeds, 21 keytexts, offsets, both signs, plus or minus Atba… |
| Collision skip on other keystreams and walks | cicada-toolbox | lane D candidate 6, per-page keyword key-skip, excluded for L = 5 to 20 (agents/laneD_chain_variants/RESULTS.md); lane K, free walk with skip, search… |
| Book-code pointers 2012 to 2014 | cicada-toolbox | lane H (agents/laneH_bookcode_pointers/RESULTS.md): 10,880 configurations, 32,512 scored rows. The Self-Reliance parse was validated on the 2014 code… |
| Gematria Primus values and word sums as key | cicada-toolbox | lane C: per-letter primes, word sums, totients, prime-counting indices and self-keying by word sums, all at the size-matched null (30 observables, ma… |
| Numerology seeds 3301 and 761 | cicada-toolbox | lane B (3301-seeded hash and KDF keystreams, 152M trials, best 1.0279 against null maximum 1.0287; agents/laneB_hash_keystreams/RESULTS.md); lane G (… |
| OutGuess payloads in JPEG images | cicada-toolbox | REPORT.md section 'On top of the community record' (OutGuess of every image: null); community RUN-numeric2-full.log (payload-as-key at all offsets: 0… |
| Whitespace and trailing-space encodings | cicada-toolbox | lane I (agents/laneI_layout_channel/RESULTS.md): 22 layout channels, 221k cells, 200 shuffles each; 9 cells under 0.05 against 5 expected; no readabl… |
| External running-key texts | cicada-toolbox | lane N: 5,075 cribs, full-position drag; a running English key is recovered from any crib of at least 20 runes (z 10 to 18), so the test has power (a… |
| Autokey on plaintext and ciphertext | cicada-toolbox | lane C (self-keying by ciphertext primes and word sums, autokey family: null at the size-matched floor; agents/laneC_gematria_structure/RESULTS.md). … |
| CicadaOS binaries as pads | cicada-toolbox | LEDGER.json R12-A1 (five pads; best per-page -6.517 at 560.17, page 54) and R28-L1-CICADAOS-PADS-DENSE-PAIR (24,080 of 24,080 rows, negative); campai… |
| Lasry hill climbing and annealing | computational-ai | lane K (`agents/laneK_walk_search/RESULTS.md`, line 29): IoC hill climb over periods 2..50 on LP2 reaches IoC at most 1.002; line 143 says no global … |
| Nuhn beam search with n-gram language model | computational-ai | lane K (`agents/laneK_walk_search/RESULTS.md`, sequential beam section); `dl/dukotah/liber-primus/ELIMINATION-LEDGER.md` Round 18 (skip-tolerant beam… |
| DECRYPT image-to-text pipeline | computational-ai | lane R (`agents/laneR_transcriptions/RESULTS.md`, about 20 distinct readings among 87 runic files; `REPORT_ROUND2.md` section 3: every faithful readi… |
| Hash verifier oracle (Paradigm design) | computational-ai | lane P (`agents/laneP_hashhunt/RESULTS.md`: null across the Wayback captures of the four signed onions, 6 hash functions and about 160 normalisations… |

## Not applicable (the constraint that kills each)

| technique | survey | grading |
|---|---|---|
| Index of coincidence and Friedman key-length formula | agency-classical | not-applicable (C1: IoC 1.000 equals the random value; no period 1..1500) |
| Kasiski examination | agency-classical | not-applicable (C1: no period 1..1500 on any stream) |
| Kullback chi-square period tests | agency-classical | not-applicable (C1: no period 1..1500 under a chi-square scan) |
| Trithemius progressive alphabet | agency-classical | not-applicable (C1: stepping period 26 or 29; C2: 3.3 percent repeats against 0.66 percent) |
| Autokey analysis | agency-classical | not-applicable (C2: 2.7 to 4.8 percent repeats against 0.66 percent) |
| Hill cipher and linear polygraphic systems | agency-classical | not-applicable (C2: about 3.4 percent repeats for a block-linear map) |
| Transposition and columnar analysis | agency-classical | not-applicable (C1: any permutation of English keeps IoC about 1.7; LP2 is 1.000; holds only if the plaintext is itself flat, which lane E does not s… |
| Rejewski cycle method | agency-classical | not-applicable (C3: 16 repeated words against 11.0 plus or minus 3.1 at random) |
| Hagelin M-209 ciphertext-only attack | agency-classical | not-applicable (C2: predicts about 3.4 to 3.8 percent repeats against 0.66 percent; analytic) |
| Chaining and symmetry of position for primary alphabets | agency-classical | not-applicable (C3: chaining needs aligned repeats; 16 repeated words against chance) |
| Atbash, constant shifts and unencrypted passages | cicada-toolbox | not-applicable (C1: a monoalphabetic or zero-key page would show English-level IoC, and LP2 is flat at 1.000 over all 12,956 runes; the sign flip ins… |
| F-interrupt as the doublet mechanism | cicada-toolbox | not-applicable (C2: the F rule touches 7% of adjacent pairs and only 4 of 86 doublets, so it cannot produce the suppression of non-F doublets. As a c… |
| Rigid prime-totient keystream | cicada-toolbox | not-applicable (C2: a rigid phi(prime) stream predicts about 3.5% doublets on English; LP2 has 0.68%. It was tested per page anyway; the skip variant… |
| Magic squares with constants 1033 and 3301 | cicada-toolbox | not-applicable (C4: LP2 has no numeric or word-sum grid to complete; the constants were tested as seeds in lane B). |
| RSA and PGP steps of 2014 | cicada-toolbox | not-applicable (C1: the RSA step produces a message, not a stream, and no link to LP2's aperiodic runes is shown. The modulus is factored, which clos… |
| Repeating-key XOR and totient strings from 2014 | cicada-toolbox | not-applicable (C1: a repeating key is periodic, and LP2 has no period 1..1500). |
| Hill and digraphic ciphers | cicada-toolbox | not-applicable (C2: a generic linear layer predicts about 3.5% adjacent repeats; LP2 has 0.68%). |
| Stego-keyed permutation of runes | cicada-toolbox | not-applicable (C2: an independent permutation keeps about 3.5% adjacent repeats on random-like runes. A value-dependent one is a collision skip, cov… |
| Jakobsen fast substitution hill climber | computational-ai | not-applicable (C1: bijections keep IoC; LP2 IoC 1.000 against English 1.7-1.8). |
| Ravi and Knight Bayesian sampling and EM | computational-ai | not-applicable (C2: homophone floor 1.7-2.7% against LP2's 0.66% doublet rate, per the gap audit's computation). |
| Aldarrab and May sequence-to-sequence | computational-ai | not-applicable (C1: a fixed 1:1 map on English keeps IoC near 1.7-1.8; LP2 is 1.000). |
| Copiale cipher solve 2011 | computational-ai | not-applicable (C2: homophone floor 1.7-2.7% against 86 adjacent repeats, 0.66%). |
| Lasry-style post-chain transposition search | computational-ai | not-applicable (C2: post-chain reordering destroys the reading-order deficit of 0.66%; lane D Candidate 5). A pre-chain transposition is untestable f… |
| Lasry Playfair record | computational-ai | not-applicable (C2: a Playfair floor of about 1.7-2.0% against 0.66% observed; the parity split rules it out too). |
| Lasry Chaocipher Exhibit 6 as published | computational-ai | not-applicable (C2: plain dynamic substitution gives about 3.7-4.2% doublets against LP2's 0.66%; the scratch rerun is not committed). |
| Lasry M-209 nested hill climb | computational-ai | not-applicable (C2: additive keystream gives 1/29 = 3.45% doublets against 0.66% observed). |
| LLM agent on the Marmont letter | computational-ai | not-applicable (C2: homophone floor 1.7-2.7% against 0.66%; C1: IoC 1.000 leaves no French-like signal). |
| LLM agents on Kryptos K4 and classical benchmarks | computational-ai | not-applicable (C1: IoC 1.000 against 1.7-1.8 gives an LLM no English cue; lane N: LP2 has no crib of 20 runes or more to anchor on). |
