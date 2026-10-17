# Hypothesis gate: walk_dodge_prime (2026-10-16)

## Hypothesis
The doublet-dodge walk with the same rule as `walk_dodge_random` (community definition; see `2026-10-16-walk_dodge_random.md`). The three permutations are read from the prime/totient ladder that reproduces the solved page 56 (AN END; `dl/dukotah/analysis/reproduce/reproduce_page_56_an_end.py`: key[i] = (p_i - 1) mod 29 over the primes 2, 3, 5, 7, ...).

- Streams: phi, t_j = (p_j - 1) mod 29; prime, t_j = p_j mod 29 (p_0 = 2).
- Ordering(kind, s): the order in which the 29 residues FIRST appear in the stream from index s, read over a window of 1,000 primes. This is a permutation of the 29 runes.
- Key from one offset k0: g has five 5-cycles on the first 25 runes of ordering(k0), in consecutive blocks, and its last 4 runes are fixed; sigma = ordering(k0 + 1000); base0 = ordering(k0 + 2000).

## Key space
- 10,000 offsets (k0 = 0 to 9,999) times 2 streams = **20,000 keys**. The key is a function of (k0, stream) only, so the family is enumerated completely by the census below.
- Choices inside the hypothesis: the stream (2), the window (1,000 primes) and the offset spacing (1,000) between g, sigma and base0, and the placement of the one residue the ladder never produces (LAST here; FIRST is gated as `walk_dodge_prime_front`).

## Structural finding: the ladder never produces one residue
The only prime congruent to 0 mod 29 is 29 itself. So residue 28 never appears in the phi stream, and residue 0 never appears in the prime stream, after index 9. Under the LAST placement this residue is always fixed by g:
- rune 28 is a fixed point of g in 11,140 of 20,000 keys, and rune 0 in 11,241 (a uniform 4-set would give 2,759 each).
- English within-word doubles on this stream: rune 0 (F) 14 and rune 28 (EA) 0, out of 339.
- Mean within-word English doubles on the four fixed runes, over all 20,000 keys: 41.8. A uniform 4-set expects 46.8.

This is why the gate's three seeds fail C2 low. The FRONT placement, which removes the forced fixed point, is gated separately (`2026-10-16-walk_dodge_prime_front.md`).

## Simulator
`jobs/hypothesis-gate/runs/walk_dodge_prime_cipher.py`, defining `encrypt(plain, words, rng)`. The key (k0, stream) is drawn from rng. Five rng seeds give five different ciphertexts for one plaintext.

## Gate output (`gate_sim.py --seeds 3`)
```
cipher: walk_dodge_prime: doublet-dodge walk, g/sigma/base0 from the prime/totient ladder at offset k0
seed 0: doublets 0 (0 within, 0 cross), lag-5 100/1828
  C1 IoC                               1.0203     LP2 1.0      FAIL
  C2 doublet rate                      0.0        LP2 0.00664  FAIL
  C2b conditional IoC                  1.0551     LP2 1.026    PASS
  C3 repeated words >=3                8          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0547     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    0.0        LP2 23       FAIL
seed 1: doublets 24 (14 within, 10 cross), lag-5 99/1828
  C1 IoC                               1.0193     LP2 1.0      FAIL
  C2 doublet rate                      0.00185    LP2 0.00664  FAIL
  C2b conditional IoC                  1.0544     LP2 1.026    PASS
  C3 repeated words >=3                7          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0542     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    10.0       LP2 23       FAIL
seed 2: doublets 18 (15 within, 3 cross), lag-5 100/1828
  C1 IoC                               0.9993     LP2 1.0      PASS
  C2 doublet rate                      0.00139    LP2 0.00664  FAIL
  C2b conditional IoC                  1.031      LP2 1.026    PASS
  C3 repeated words >=3                8          LP2 16       PASS
  C4 adjacent word-length z            -5.69      LP2 0.9      INFO
  C5 within-word lag-5 rate            0.0547     LP2 0.0494   PASS
  C6 cross-word doublets (LP2-size)    3.0        LP2 23       FAIL
GATE FAIL: C1 C2 C6
```

Gate seeds (`random.Random(1000 + s)` draws k0 and stream): seed 0 is k0 7028 (phi), fixed points {2, 11, 26, 28}, 0 within-word doublets, C2 0.0, C6 0, C1 1.0203. Seed 1 is k0 960 (phi), fixed points {0, 14, 25, 28}, C2 0.00185, C6 10, C1 1.0193. Seed 2 is k0 8535 (prime), fixed points {0, 11, 24, 26}, C2 0.00139, C6 3, C1 0.9993.

## Key census (every key; `tools/walk_draws.py ... --census`; raw output in `2026-10-16-walk_dodge_prime_census.txt`)
```
cipher: walk_dodge_prime: doublet-dodge walk, g/sigma/base0 from the prime/totient ladder at offset k0
census over ['phi', 'prime'] x K0_RANGE=10000: 20000 draws
  C1   passes 9332 / 20000
  C2   passes 8159 / 20000
  C2b  passes 19476 / 20000
  C3   passes 18331 / 20000
  C6   passes 6082 / 20000
  all hard constraints pass: 1550 / 20000
  ioc             min 0.99846  median 1.01887  max 1.31378
  doublet_rate    min 0.00000  median 0.00363  max 0.02184
  doublets_cross  min 0.00000  median 9.00000  max 138.00000
  cond_ioc        min 1.00441  median 1.04029  max 1.48141
  first keys passing all hard constraints: [('phi', 1), ('phi', 7), ('phi', 8), ('phi', 9), ('prime', 15), ('prime', 24), ('prime', 35), ('prime', 36), ('prime', 37), ('prime', 38), ('prime', 40), ('prime', 41), ('prime', 42), ('prime', 43), ('prime', 49), ('prime', 59), ('prime', 61), ('prime', 62), ('prime', 71), ('prime', 116)]
  passing count: 1550
```

Share passing each constraint: C1 46.7%, C2 40.8%, C2b 97.4%, C3 91.7%, C6 30.4%, all hard constraints 7.75% (1,550 of 20,000). Passing keys include phi with k0 = 1, 7, 8, 9 (windows that still contain prime 29, where residue 28 is not missing) and many prime-stream keys from k0 = 15 on. The census does not isolate the cause for every passing key.

## Verdict
**EXCLUDED by C1 C2 C6** (gate FAIL: C2 and C6 on all three seeds; C1 on seeds 0 and 1).

The census shows that 1,550 of the 20,000 keys (7.75%) pass every hard constraint on English, so the family is not excluded for every key. The three-seed gate reads a typical key, and the protocol verdict still stands: PROCEED is not available after a gate FAIL. Any attack on the 1,550 passing keys would be a new decision for the orchestrator.

## Predictions for the non-deciding constraints
- C4: plaintext word lengths, -5.69 on every draw (LP2 +0.9). INFO.
- C5: 0.0547, 0.0542 and 0.0547 on the three seeds (within the soft band 0.039 to 0.060). Not discriminating.

## Attack-lane design (conditional; not run, and not available under this verdict)
If an owner-approved PROCEED ever covered the passing subset, the design would be:
- Key space: the 20,000 keys above, or the 1,550 passing keys from the census.
- Decoder: the skip-aware beam decoder from lane L (`agents/laneL_keyword_walk/kwdec.c`), with the key's base0, g and sigma. Lane L's own measurements: 262 of 262 runes round-trip on a plant, and recovery is 0.9993 to 1.0000 on 3,000-rune plants.
- Scan: decode LP2 pages 0 to 54 (12,956 runes) under every key, score each decode by quadgram, and rank. Candidates go to `lp/verify_candidate.py` and to `dl/dukotah/liber-primus/verify_solution.py --plaintext`.
- Planted control: plant one key from the family on 1,600 runes of solved-page text (SOLVED-PAGES page 05, as in the survey), require at least 90% recovery, and require the planted key to rank first among the 20,000.
- Size-matched null: the same 20,000-key scan on LP2 with word lengths permuted within each of the 9 sections (keeps the rune stream and the doublet structure). Compare the real best with the null maximum.

## Prior coverage
Grep terms: `totient`, `phi`, `prime`, `ladder`, `AN END`, `Oosterhof`, `dodge`, `walk`, `skip`, `fixed point`.
Files searched: `REPORT.md`, `REPORT_ROUND2.md`, `toolbox/CONSTRAINTS.md`, `dl/dukotah/liber-primus/LEDGER.json`, `dl/dukotah/liber-primus/ELIMINATION-LEDGER.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`, `dl/leo/docs/FINDINGS.md`, `jobs/technique-survey/runs/2026-10-16-cicada-toolbox.md`, `agents/laneC_gematria_structure/RESULTS.md`, `agents/laneK_walk_search/RESULTS.md`, `agents/laneL_keyword_walk/RESULTS.md`.
Hits:
- Survey entry T (`jobs/technique-survey/runs/2026-10-16-cicada-toolbox.md`, around line 70): "Prime-seeded selectors were not run"; status applicable-untested. This is the gap this gate fills.
- Lane L (`agents/laneL_keyword_walk/RESULTS.md`, step and alphabet enumeration): its step grids use rune order, which it calls prime-value order because the Gematria primes increase with the index. That is not the successive-primes-mod-29 residue ordering used here. Lane L is null for keyword-built walks.
- The ladder itself was tested as an additive keystream and as a seed generator, not as walk permutations: `ELIMINATION-LEDGER.md` Round 22 (X4, prime and totient keystream over letters) and Round 26 (C: 323 semantic seeds through the prime, totient and prime-totient ladders, flat-random); `dl/leo/docs/FINDINGS.md` (p56 AN END relation).
- Lanes J and K cover the free walk (see the parent report).

## PROOF (`jobs/hypothesis-gate/PROOF.md`)
- [pass] Names the hypothesis and links `runs/walk_dodge_prime_cipher.py`; the simulator defines `encrypt(plain, words, rng)`.
- [pass] The full `gate_sim.py --seeds 3` output is pasted above, including the final GATE line.
- [pass] Verdict: `EXCLUDED by C1 C2 C6`.
- [pass] No PROCEED after a gate FAIL; every failed id is named.
- [pass] Prior-coverage line lists the grep terms and the files searched.
- [n/a] PROCEED design: not required. The conditional design is recorded above.
- [pass] Every key is drawn from rng; five seeds give five different ciphertexts.
