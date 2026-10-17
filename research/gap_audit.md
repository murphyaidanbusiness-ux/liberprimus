# Gap audit: untested cipher/key hypotheses consistent with the six constraints

Date: 2026-10-16. Scope: local files only (no web, no downloads, no commits). Constraints are those in
`REPORT.md` (1 flat at every order; 2 doublet deficit 86 vs 447 with flat conditional; 3 repeated cipher
words at chance; 4 layout is not plaintext layout; 5 within-word lag-5 echo; 6 chain-with-EA refuted).

## Bottom line

- The only family our constraints leave is Oosterhof's doublet-dodge walk. Our lanes K and L searched
  its order-5 `g` form, and lane J simulated its fingerprint. The community's own file `aldegonde_clone/hypotheses/quagmire-dodge.md` describes a
  sibling (additive 5-step schedule with exactly one zero offset, plus a clock skip on repeat) that
  nobody has swept. Its zero-offset sweep was written, priced and parked, and the scorer it needs is
  described as fixed but unrun. This is ranked first.
- Most generator gaps are already queued by the community (R28-L4, B-01, B-21, R20-SMARS) and are still
  open. Every community sweep of those generators scored an additive keystream against English. The
  direct-output and chain-increment models (runes = generator output, no plaintext) were never run at full
  seed scale. An exact screen of that kind needs no language model and costs about an hour of generation
  on this PC (measured here).
- Homophonic substitution is dead. Any i.i.d.-homophone model has a doublet floor of 1.7 to 2.7 percent on
  English letter statistics, against 0.66 percent observed (computed here, section 4).
- Suggested execution order differs from the ranking. Run the cheap premise check (candidate 6) and the
  exact generator screens (2, 3) first, because each returns a decisive answer in hours. Then run the
  quagmire slice (1), which carries the higher prior but needs a pruned sweep.

## 1. Sources read, and what was not checked

Read in full or in the relevant sections: `REPORT.md`; `research/SYNTHESIS.md`; `agents/laneA` to `laneN`
RESULTS.md (scope sections, plus the cited lines below); `dl/dukotah/liber-primus/PICKUP-HERE.md`;
`ELIMINATION-LEDGER.md` (open frontier, "Do NOT re-run", Round 24 and 30 rows); `LEDGER.json` (all 172
entries filtered by status and by keyword); `analysis/seed_sweep/results_full32.txt`; `FINAL-SYNTHESIS.md`
(head); `corpus/GAPS.md` (grep); `leo/docs/FINDINGS.md` and `REPORT.md` (grep for open items);
`theron/UPDATES.md` and `FINAL_SUMMARY.md`; `aldegonde_clone/docs/*.md` (in part); `aldegonde_clone/hypotheses/INDEX.md`
and the hypothesis files cited below; the list of `aldegonde_clone/experiments/` names.

Not checked: the other ~4,900 aldegonde files were surveyed by name and by INDEX only. I did not verify
the community's claim that `dodge_aware_scorer.py` recovers a planted key at z = 12 to 20. Results from
dukotah `corpus/` and `identity/` were not read. "Grep found nothing" below means these files were searched
for the terms listed.

## 2. Coverage map (what is already done)

Ours (lanes A to N, all null): A keyword chain; B hash/KDF keystreams; C gematria keystreams; D chain
variants (base lag, fixed-table feedback, skip-on-collision Vigenere); E language identification; F word-length
alignment; G era PRNGs on 143,022 seeds, emissions = direct output, chain increments, additive keystream;
H book-code pointers; I layout channels; J lag-5 mechanisms (includes walk + dodge simulation only); K walk
search (fixed-alphabet sets excluded by pigeonhole, K section 2; g-power walk ladder); L keyword-built walk
(structured g, 220k keyword alphabets, shifts/reflections, Gematria grids); M and N crib drags.

Community: 172 ledger entries. Full 2^32 integer-seed sweeps with additive keystream against English
(`analysis/seed_sweep/results_full32.txt`): MSVC, MT19937 (two forms), py3 seed randrange and int(random()*29),
Java nextInt, glibc `random()` scaled (gen=1) and `%29 +norepeat` (gen=2). Not run: glibc `random()%29`
plain (gen=0) (LEDGER B-01 and R19-G3-CORRECTION: "still absent, still the one open row"); PHP mt_rand, xorshift,
RC4, .NET, Java 48-bit full (LEDGER B-03 open; B-21 "PHP mt_rand alone is an open, named, high-prior gap";
R28-L4 never-run, 25 cells x 2^32). Marsaglia CDROM: 77 of 756 units run (B-13-MARSAGLIA); 679 units never run
(R20-SMARS). Zero-offset Quagmire dodge: never run (`quagmire-dodge.md` lines 244 to 282, 373). Quagmire-odometer:
"unresolved" (`quagmire-odometer.md`). Homophonic: D-03 open; Round 24 planning gate killed C7 homophonic-downward
on the doublet-deficit exclusion (ELIMINATION-LEDGER.md row Round 24).

Note on our lane G section 1: its statement that glibc `random()` scaled and `%29+norepeat` were swept over all
2^32 seeds matches the community table (gen=1 and gen=2). The distinction matters below: those community runs
score an additive keystream against English. They do not test runes as the direct output of a generator.

## 3. Top 8, ranked by prior plausibility x feasibility

### 1. Zero-offset Quagmire dodge on the priority vocabulary (Michel's family)

- **Family.** Letter step is an additive Quagmire schedule in keyed-alphabet coordinates, A_k = K o (+S_k).
  S is a five-step schedule with exactly one zero offset (sum of offsets = 0 mod 29). When the emission
  would repeat the previous rune, the clock advances one step and the rune is re-emitted. The per-word base
  advances (`quagmire-dodge.md` lines 7 to 13).
- **Consistency.** Constraint 2: P(doublet) = P(zero step) x P(would-be doublet) = (1/5)(1/29) = 0.69 percent,
  against 0.66 percent observed. I took the would-be rate as 1/29; the file calls it a shift diagonal, which is near
  1/29 for a flat plaintext difference. The arithmetic is mine, the mechanism is the file's. Constraint 5: within-word
  lag-5 positions share an alphabet, so the coincidence rate is roughly the plaintext rate (the clock skips shift the phase only slightly), which is the community's
  "same-alphabet leak" reading (`d5-partial-alphabet-leak.md`). The "no visible phase rule" nulls under
  constraint 5 do not bite, because the dodge clock is index plus skips and an index-phase test has no power on
  it (`quagmire-dodge.md` lines 25 to 27, "absolute-position test ... has no power"). Constraint 1: flat in K
  coordinates. Constraint 3: a fixed base over the book is excluded by pigeonhole (our K section 2: at least 482
  repeated words for K = 5). A per-word base advance escapes it, so the family requires that advance. Constraint
  6: not a chain. Strain: the per-word advance rule is not specified in the community file.
- **Untested evidence.** Our K section 2 covers fixed alphabet sets only. Our L (section 1 and section 6) enumerates
  order-5 `g` only, so the additive 5-step schedule is outside it. Our J simulates the walk with dodge (lines 15
  and 85 to 86) and has no quagmire mechanism (grep "quagmire": none in `agents/laneJ_lag5_echo/`). The community
  repo: `quagmire-dodge.md` line 95 (the `nz` mask removes every zero-offset schedule: "None of them could have
  returned a key of this form"); lines 244 to 268 (scorer blind: planted key 0.493 vs best of 2000 wrong 0.619,
  gap -0.126); lines 281 to 282 (zero-offset sweep planned); line 373 ("It has NOT been run"). LEDGER.json and
  ELIMINATION-LEDGER.md: grep for dodge, quagmire, odometer returns 0 hits in each.
- **Test design.** (a) Alphabets: keyword-then-rest rules R1 to R4, reversals and inverses (our L section 1
  rules), applied to the 316-word priority list the community names (`quagmire-dodge.md` lines 239 to 240:
  register, solved pages, puzzle words), about 3.8k alphabets. (b) Schedules: 105,980 (one zero offset, other four
  nonzero, sum 0 mod 29; matches `schedule-band-retention.md` line 22). (c) Clock phase: five. (d) Per-word base
  rule: pre-register two variants, a fixed shift and Oosterhof's rule base_{w+1} = base_w o g^e o sigma. (e) Scorer:
  the community's dodge-aware scorer, ported to numpy, alternating base_0 and clock phase over three passes on
  200-rune windows. (f) Planted control: 20 keys, random K from the vocabulary, random one-zero schedule, dodge
  on, planted into a synthetic text at the corpus doublet rate. Require rank 1 with margin of at least 5 sigma over
  2000 wrong keys. The community's no-dodge control failed with the old scorer, so this gate is essential. (g)
  Null: 1000 doublet-matched corpus shuffles (our L section 4 protocol). (h) Any survivor goes to
  `dl/dukotah/liber-primus/verify_solution.py --plaintext` (CLAUDE.md rule).
- **Key space and CPU cost.** Community count: unbanded priority sweep 3.9e9 keys, 216 core-hours at their C
  kernel (`schedule-band-retention.md` line 71; `quagmire-dodge.md` lines 281 to 282). This PC has no C compiler
  (gcc, cc and clang not found), so the sweep must be ported to numpy. If numpy runs 3 to 10 times slower than C,
  the full sweep takes 40 to 140 wall-hours on 16 cores, and 12 hours covers roughly 10 to 30 percent. Pre-register
  the slice and report its fraction as the power. Measure numpy throughput in the first hour.
- **Prior and feasibility.** Prior: moderate-high. It is the only family here that explains constraints 2 and 5
  together, and the community calls it "still the best-fitting mechanism in this directory"
  (`quagmire-dodge.md` lines 39 to 40). Feasibility: moderate-low (slice). Rank 1 on prior, which outweighs
  feasibility here.

### 2. Exact direct-output screen: PHP mt_rand (MT19937 with PHP reductions) over all 2^32 seeds

- **Family.** Each rune is a PHP `mt_rand` draw, with no plaintext. Emissions: (a) direct `mt_rand(0,28)` with
  redraw while equal to the previous rune (norepeat), (b) `mt_rand()%29` with norepeat, (c) chain increments
  c += 1 + draw(28). Twists: MT_RAND_MT19937 (PHP >= 7.1) and the PHP < 7.1 broken twist. Lane G implemented and
  validated these reductions against real PHP 8.3 (lane G section 2: PHP7R, PHP7M, PHP5R, PHP5M); the sweep was
  on 143,022 seeds only.
- **Consistency.** Constraint 2: norepeat gives a deficit with a flat conditional, which is the required shape. Constraint 1: flat.
  Constraint 3: no cipher state, so repeated words are at chance. Constraint 4: layout is independent of the
  runes, so an English-fitting length marginal must be a designer choice (a strain, not a contradiction).
  Constraint 5: no echo mechanism (a strain; the echo is about 2.5 sigma after correction).
- **Untested evidence.** LEDGER R28-L4-UNSWEPT-GENERATORS-QUEUE: never-run, "PHP mt_rand (canonical
  MT_RAND_MT19937 AND the pre-7.1 MT_RAND_PHP broken twist ...)", described as "CENSUS section C's highest-prior
  open generator". LEDGER B-21: "PHP mt_rand alone is an open, named, high-prior gap". No PHP row in
  `results_full32.txt`. Our lane G: 143,022 seeds (section 3). The community additive sweeps do not test this
  emission model (lane G section 1, "not tested anywhere (i)").
- **Test design.** Seeds: all 2^32 32-bit integers. Per seed, `init_genrand(s)`, the chosen twist and reduction,
  and the chosen emission. Screen: exact match of the first 12 emitted runes against LP2 at every stream alignment
  0 to 5000 (our lane G uses the same alignment range). Chance: 29^-12 = 2.8e-18 per test, about 2.6e14 tests, so
  the expected number of chance hits is about 7e-4. Any hit is confirmed by a full-length match and then by the
  oracle. Planted control: plant one seed and emission into the corpus and require exact recovery. Null: the same
  pipeline with a shuffled target (exact-match rate should be zero). Note: emission (c) uses 28 symbols, so the
  same chance bound holds.
- **CPU cost (measured here).** Generation only, numpy 2.5.3, single thread, `bench.py` in the session scratchpad:
  MT19937 init plus 32 twist outputs, 73k seeds/s per core. 2^32 seeds is 16 core-hours, about 1 hour on 16
  cores. Offset-0 screens of 624 outputs need roughly a further twist pass, so estimate about 2 hours. Offsets to
  5000 are too costly for every seed (extrapolated, not measured: about 120 core-hours, roughly 7 wall-hours on 16 cores). Restrict those to a prior-dense subset.
- **Prior and feasibility.** Prior: moderate. B-21 calls it high-prior, but a direct-output generator with no
  plaintext does not explain constraint 5. Feasibility: high (exact screen, about 2 hours). Rank 2.

### 3. Exact direct-output screen: glibc TYPE_3 `random() % 29` (plain, gen=0), full 2^32

- **Family.** Same as candidate 2 with glibc TYPE_3 (16807 init, 310 discards, additive feedback). Plain `%29`
  with no rejection gives 3.45 percent doublets (447 expected), so it is excluded by constraint 2. Only the norepeat
  and chain-increment emissions are live. Lane G's glibc generators are validated (section 2, GLMOD, GLSC, GLDIV).
- **Consistency.** Same as candidate 2. Constraint 5: same strain.
- **Untested evidence.** LEDGER B-01: gen=0 "absent" from `results_full32.txt`, "the highest-prior generator"
  in the community's priority order. LEDGER R19-G3-CORRECTION: "gen=0 ... still absent, still the one open row".
  Our lane G covers 143,022 seeds only.
- **Test design.** As candidate 2 with the glibc engine, emissions (a) with norepeat and (c), offset 0 plus the
  alignment scan. The screen is exact and needs no English scorer. Planted control and null as in candidate 2.
- **CPU cost (measured here).** glibc init plus 32 outputs: 344k seeds/s per core, so about 3.5 core-hours for
  2^32, about 15 minutes on 16 cores (generation only).
- **Prior and feasibility.** Prior: moderate-low. Feasibility: very high. Rank 3. It is the cheapest decisive test on
  this list; running it first is recommended.

### 4. Oosterhof walk with shuffle-derived alphabets (seeded permutations)

- **Family.** The walk of `length-clocked-walk.md` and `doublet-dodge-walk.md` (our lanes K and L decode this).
  The three permutations g (structured: fix four runes, step by five over 25, as in our L section 1), sigma and
  base_0 are generated by a seeded era shuffle of the 29 runes. Candidate generators: Python 2.7 `random.shuffle`,
  Python 3 shuffle, PHP shuffle, Java `Collections.shuffle`. Seeds: the lane G dictionary (143,022 integers,
  5,760 strings and their hashed keys, 433 PGP timestamps).
- **Consistency.** The walk is the only family consistent with constraints 1 to 6 by the REPORT's own account.
  Within it, the per-word base update and the clock behaviour are the same as in K and L, so constraints 2, 3 and
  5 hold for the same reasons. Strain: a seed reduces the 280-bit walk key to about 32 bits, which is a designer
  assumption, not a constraint.
- **Untested evidence.** Grep for walk, with shuffle, seed, prng or random, across `aldegonde_clone/hypotheses`,
  `experiments` and `dl/dukotah/liber-primus/analysis`: no seeded-walk entry. The aldegonde walk artifacts use
  "freely-designed" or annealed permutations (`length-clocked-walk.md` lines 170 to 173). Our L uses keyword-built
  and Gematria-grid g, not shuffle-derived; our G's shuffle (emission (s)) is a stream, not walk alphabets.
- **Test design.** For each seed: three shuffles, g = structured g from the first four shuffled runes and the rest
  from shuffle 2, sigma and base_0 from shuffles 2 and 3. Decode the first 48 runes of LP2 with the walk decoder
  (numpy port of L's beam, width 8) and score the best beam against a doublet-matched null on the real page 0
  start (our L section 4 protocol). Planted control: plant one seeded walk and recover it at rank 1. The skip
  ambiguity (about 0 to 6 runes per 12,388) requires the beam.
- **Key space and CPU cost.** 143k seeds x 3 generators: about 0.4 million head decodes at beam width 8. Minutes to an hour in numpy (estimate, not measured).
  Full 2^32 is not feasible here.
- **Prior and feasibility.** Prior: low-moderate. Feasibility: high on the dictionary. Rank 4.

### 5. Quagmire-odometer (two dials, one zero offset)

- **Family.** `quagmire-odometer.md`: K one keyed alphabet; S the running sums of a five-step schedule with exactly
  one zero offset; the doublet preventer advances the clock on a repeat. The per-word step is a shift a inside K and
  b outside, with 29 x 29 = 841 steps, driven as an odometer (a every word, b only when a wraps). "Every operation
  is a shift; there is no general permutation in the key."
- **Consistency.** Same zero-offset mechanism as candidate 1, so the same constraint 2 and 5 arguments. The file
  reports 17 of 19 free cells fitted on a length-matched register, against six for the walk (`quagmire-odometer.md`,
  "Evidence for"). Key about 137 bits. Strain: the file's status is "unresolved", and the fit has not been tested by a decode.
- **Untested evidence.** The file's status is "unresolved"; no sweep is recorded. Grep for odometer in agents: none.
  LEDGER and ELIMINATION-LEDGER: none.
- **Test design.** Shares candidate 1's alphabets, schedule enumeration, scorer, planted control and null. Add the
  odometer dial rule (pre-registered as the file's rule) and the 841-step per-word variant. Run only after candidate
  1's scorer passes its planted control.
- **Prior and feasibility.** Prior: moderate-low (overlaps candidate 1, and the community treats the two as one
  piece of evidence against one mechanism). Feasibility: as candidate 1. Rank 5.

### 6. All-offset page-pair superposition (two-time key test)

- **Family.** Two pages (or sections) drawn from one keystream at a relative shift s. Then c_p(i) = c_q(i + s) iff
  the plaintext letters agree, which gives a match rate near the plaintext coincidence rate (about 6.5 percent for
  English letters) against 3.45 percent chance.
- **Consistency.** No constraint is contradicted. The premise "keystream continuous across pages" is what would
  make the test null by construction.
- **Untested evidence.** ARMADA `analysis/armada/FOLLOWUP-TESTS.md` section 4: "Of 1,485 page pairs (aligned)"; only
  aligned offsets. `analysis/structure/RESULTS2.txt` 3d: head- and tail-aligned match rates. `research/DEAD_ENDS.md`
  lines 209 to 211 dismisses the family by the continuity premise alone. Grep for superimpos, two-time and page
  pair: aligned results only. No all-shift scan in any ledger.
- **Test design.** For each of the 1,485 page pairs and every shift |s| <= 12,955, count matches via FFT
  cross-correlation of 29 one-hot indicators per page. Null: 200 doublet-matched corpora. Planted control: a
  two-time plant (same key at shift s for two pages) must be found. Survivors go to a per-shift adjudicator.
- **CPU cost.** Minutes in numpy.
- **Prior and feasibility.** Prior: low. Feasibility: trivial. Rank 6. Worth running first as a premise check, because
  the result also bounds the continuity premise used to dismiss other families.

### 7. Marsaglia CDROM: the 679 unswept units under the anti-repeat filter

- **Family.** A window of the Marsaglia Random Number CDROM (1995, 634 MB) reduced mod 29, with the community's
  soft anti-repeat filter (~83 percent suppression). Physical randomness, no plaintext.
- **Consistency.** Constraints 2 and 3 hold (uniform pad plus filter, no state). Constraint 5 is the same strain as
  candidates 2 and 3.
- **Untested evidence.** LEDGER R20-SMARS-SCAFFOLDED: "never-run", "ZERO. 0 of 679 units swept", "~21 CPU-h".
  LEDGER B-13-MARSAGLIA: partially run, 77 of 756 units, 1.54e9 offsets, English quadgram beam. LEDGER R19-C2
  identifies 63 hash-verified pads and holds the other 679 units as "HELD, not excluded". ELIMINATION-LEDGER line
  986: "Live and unswept".
- **Blocker.** The ISO is not in this checkout (`find` for `*.iso` and marsaglia returns only code and outputs under
  `dl/dukotah/liber-primus/analysis/round18/L6-offset-marsaglia/`). Obtaining it means downloading the archive
  (archive.org item named in `scripts/fetch_marsaglia.sh`). That needs your approval, with the source and size stated,
  before I fetch it.
- **Test design.** The community's L6 pipeline with mod-29 builder, English beam, and their power gate (R21-L1
  flags any survivor as oracle-only). Run the 679 units only after the gate is re-measured.
- **CPU cost.** Community estimate about 21 CPU-hours for the 679 units. Numpy on 16 cores: a guess of 2 to 4 hours if
  the gate vectorizes (not measured).
- **Prior and feasibility.** Prior: low (no structural reason for a physical pad). Feasibility: moderate (data).
  Rank 7.

### 8. Magic-square 5x5 grid as the walk's `g`

- **Family.** `magic-square-grid-key.md`: the printed 5x5 square with constant 3301 (master transcription lines 179 to
  183) supplies the cell order from which `g` is built (25 runes in a grid, columns rotated, 4 fixed runes).
- **Consistency.** Constraint 2 requires a low-diagonal layout: `g-from-5x5-grid.md` shows the naive Gematria order
  gives a doublet rate of 0.0319, near chance, while arranged grids can reach 0.000. The printed square is therefore
  testable against constraint 2 in one step.
- **Untested evidence.** `magic-square-grid-key.md`: "UNDECIDED"; the seven g-only constraints give 16.0 bits, and the
  2-rune verifier is needed for sigma, which "has no construction". Our L section 6 covers "Gematria grids
  (285,012)" and "keyword-grid" constructions. Whether the printed square's cell order is among those 285,012 grids
  is not verified here. If it is, candidate 8 reduces to sigma and base_0, which L section 6 has covered for keyword
  alphabets.
- **Test design.** Step 1 (seconds): compute the doublet rate predicted by the printed-square `g` on English bigrams
  against 0.0066. Step 2, only if step 1 passes: decode the first 48 runes with the walk decoder and sigma, base_0 from
  keyword alphabets, against the L null.
- **Prior and feasibility.** Prior: low-moderate (the square is a real book artifact, but the community's own bit
  count says g alone cannot decide). Feasibility: high for step 1. Rank 8, with partial coverage flagged.

## 4. Rejected (one line each)

- i.i.d. homophonic substitution (D-03 open; C7 killed in Round 24): floor of min over integer allocations of
  sum d_s / h_s is 2.1 percent for 26 letters and 1.7 to 2.7 percent for 5 to 20 plaintext symbols (300 random
  partitions, English letter pairs from five texts in `dl/dukotah/liber-primus/data/keys/`), against 0.66 percent
  observed. Computed here (scratchpad `homo.py`, `homo2.py`). Excluded for i.i.d. choice. Anti-correlated choice is
  the skip rule, already in candidates 1 to 5.
- 30th symbol as cipher output (`thirty-symbol-disk.md`, `mobius-order5-thirty-points.md`): an algebraic order-5 map
  must emit the extra point 135 to 359 times, with a doublet diagonal of 0.0250 against 0.0063 (z = -11.9). Excluded.
  The boundary-synchronised reading has no decodable specification.
- Autokey family incl. Quagmire III with identity character (`lp_doublet_hypotheses.md` H1 to H6; ELIMINATION-LEDGER
  section B): fixed-tableau feedback is excluded by constraint 2 (conditional IoC, about 245 sigma).
- Fixed-table ciphertext feedback c_i = T[p_i][c_{i-1}] (our lane D candidate 3; community D-04 on 3 pages): excluded by
  constraint 2.
- Fixed-alphabet-set walks with a free per-word phase (our K, M_K): excluded absolutely for K <= 50 (K section 2).
- Oosterhof's 38-bit keyword corner (structured g times keyword-then-rest alphabets): tested and empty (our L section 6,
  lines 186 to 188).
- Running keys from published texts (community ~200 texts, LEDGER R26-B 0 of 1,562; our N): excluded by doublet
  mechanism and skip-aware nulls.
- Plain unfiltered pads: deficit requires active suppression (ELIMINATION-LEDGER section B, "Unfiltered one-time pad").
- Chain with EA as zero step: refuted by constraint 6 (REPORT).
- Date-indexed pad (LEDGER R24-C8): premise fails, no timestamps on LP2 pages.
- Dice, random.org, /dev/urandom pads (LEDGER R17-P2 census): no seed and no record, untestable.
- Lag-5 back-reference (`lag5-back-reference.md`): "unfalsifiable from ciphertext statistics alone".
- Linear recurrences, LFSR, Berlekamp-Massey over GF(29): linear complexity n/2 (REPORT constraint 1).
- Tab and space whitespace channel (LEDGER H-02): layout, and our lane I covered 22 layout channels.
- Turtle, numeric-direction and totient renders (LEDGER R22-B; our C): negative.
- Hash and KDF keystreams (our B; LEDGER B-04, R16-KDF): negative.
- Periodic keys and Friedman period tests (REPORT constraint 1): flat at every period.

## 5. Shared controls, scoring and budget for this PC

- Hardware and software: 16 logical cores; Python 3.13; numpy 2.5.3; no C compiler (gcc, cc, clang not found). Our
  C kernels (lanes A, K, L) cannot run here without a port.
- Every family: planted-seed positive control through the same pipeline, pre-registered threshold, doublet-matched
  null (our L section 4), and any survivor to the community oracle `verify_solution.py` (CLAUDE.md).
- Exact-match screens (candidates 2 and 3) have a chance-hit rate near 1e-3 over their full search, so their nulls
  do not depend on a language model. Scored screens (1, 4, 5, 7) depend on the English beam, and their power must
  be measured, as R21-L1 found for the fold seal.

## 6. Caveats

- Ranks are judgments of prior and feasibility, not probabilities.
- Numpy throughput figures are generation-only benchmarks (`bench.py`: seeds per second for init and first outputs),
  not validated generators. Lane G's `prng.h` is the validated implementation and should be used for the real run.
- The community's dodge-aware scorer z = 12 to 20 claim is unverified here. Candidate 1 starts with its planted gate.
- Our lane G's glibc sentence is consistent with the community table (section 2 above), so no correction is needed there.
