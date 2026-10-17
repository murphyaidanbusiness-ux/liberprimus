# laneG_prng_generators — RESULTS

**Verdict: NULL.** No off-the-shelf PRNG in the tested set (19 generator×reduction idioms, 7 emission models, 143,022 seeds)
emits the LP2 runes or their chain increments. The best real match is a 10-rune exact run. Chance predicts 1.9 such runs over
the sweep, and the D-shuffle null produces 3.3. A true hit would give runs of about 150 (up to the next doublet). All four planted
controls came back at rank 1 with runs of 213–271. The keystream-through-chain variant (model f) is also at the null
(best IoC 1.0277, z = 8.0, against a null max of 1.0282, z = 8.9). No candidate exists, so nothing was sent to the oracle.

## 1. Deduplication (what was already swept)
Read from dukotah `LEDGER.json` (entries B-01, B-03, B-21, R16-PRNG, R19-G1/G2/G3, R20-SG3, R21-L3, R24-C2, R25, R26-C, R27-CPORT, R28-L4),
`analysis/seed_sweep/*` (results_full32.txt, results_timeseed.txt, string_seed_results.json), and the Leo and Theron repos. Every prior PRNG
sweep shares one structure: **keystream added to an English plaintext (c = p ± k), decoded with a skip-aware beam and scored by English
quadgrams.** That covers MSVC, MT19937 init_genrand %29 and double, py3 seed(int) randrange and int(random()*29), Java nextInt(29), glibc
random() scaled and %29+norepeat (all 2^32 integer seeds), glibc random()%29 over the 2011–2015 time band, Python 2.7 init_by_array([w]) over
all 2^32 (R27 S1), and Perl, TeX, bash, PHP mt_rand, .NET, ISAAC, BBS, LFSR and Geffe over priors or slices. R28-L4 (glibc gen 0 full, PHP mt_rand
both twists) is queued and never ran. Leo and Theron have no PRNG sweeps.
**Not tested anywhere:** (i) the runes as the *direct output* of a generator (no plaintext). The scout notes call this the "Occam reading", and
it needs no language model. (ii) Generator output as the chain increments themselves. (iii) Generator output as the per-position key of the
CHAIN cipher (lane B did this for hashes only). This lane covers all three. The additive-keystream family it does *not* re-test is excluded
by the doublet theorem anyway (BRIEF §3).

## 2. Generators: exact algorithms and verification (`prng.h`, `validate.py`, `validation.json`: 261/261 PASS)
| idiom | algorithm (draw(n) = integer in [0,n)) | verified against |
|---|---|---|
| PY2 | CPython 2.7 `random.seed(x)`: int → init_by_array(32-bit limbs of abs(x)); str → `(unsigned long)hash(str)` (2.7 string_hash, 64-bit, and 32-bit/i386 = low limb) → init_by_array. draw = `int(random()*n)` with random = genrand_res53. In 2.7, randrange, randint, choice and shuffle all use this. | 14 stream vectors + 1 hash value captured from **real CPython 2.7.3** (dukotah round19/G3) |
| PY3 | CPython ≥3.2 seed(str/bytes) = `int.from_bytes(a + sha512(a).digest(),'big')` → init_by_array; draw = `_randbelow`: getrandbits(n.bit_length()) = u32>>(32-k), reject ≥ n (randrange/randint/choice/shuffle) | real Python 3.13 (same algorithm as 3.2): randrange, choice, shuffle, models b/c/d/s/e, int and str and bytes seeds |
| PYGM | getrandbits(bitlen n) % n | real Python 3.13 |
| MTMOD | init_genrand(seed); u32 % n (C++ std::mt19937) | real g++ std::mt19937 |
| NPR53 / NPINT | numpy RandomState(int) = init_genrand; int(random_sample()*n); randint = low-bit mask rejection | real numpy RandomState |
| STDUID | libstdc++ 4.6 uniform_int_distribution downscaling (scaling = 2^32-1 div n, reject ≥ n·scaling) | **from source only** (modern g++ uses Lemire's method, so no binary of the era was available) |
| PHP7R / PHP7M | PHP ≥7.1 mt_rand(0,n-1) (range32 rejection on the full tempered u32) / mt_rand()%n (u32>>1) | real PHP 8.3 (MT_RAND_MT19937) |
| PHP5R / PHP5M | PHP <7.1: buggy twist (loBit(u)), mt_rand(0,n-1) = RAND_RANGE scaling of u32>>1; mt_rand()%n | real PHP 8.3 `MT_RAND_PHP` mode; mt_srand(1) → 1244335972 |
| GLMOD / GLSC / GLDIV | glibc srandom TYPE_3 (16807 init, 310 discards, r[i]=r[i-3]+r[i-31], >>1); %n, (int)(n·r/(RAND_MAX+1.0)) (= PHP5 rand(min,max)), r/(RAND_MAX/n+1) | real glibc rand(); srand(1) → 1804289383 |
| MSMOD / MSSC | MSVC LCG 214013/2531011, (x>>16)&0x7fff; %n, r·n/32768 | published srand(1) vector 41, 18467, 6334, … |
| JINT / JDBL | java.util.Random 48-bit LCG with seed scramble; nextInt(n) with the int-overflow rejection; (int)(nextDouble()·n) | real JVM (also Collections.shuffle and String.hashCode) |
| D48 | srand48/drand48; (int)(drand48()·n) (= Perl 5.14 int(rand(n))) | real glibc drand48 |

Note: GLSC and GLDIV differ by less than 1 part in 10^8 in their scale factor, so their streams are almost identical (both rows appear in the tables).

**Emission models** (`emit()`), validated with real Python for b/c/d/s/e, numpy for d and Java for s:
(a) rune = draw(29); (b) redraw while equal to previous; (c) one redraw if equal; (d) draw(28) skipping prev (= `choice([r for r in R if r!=prev])`);
(s) concatenated Fisher–Yates shuffles of the 29 runes (py shuffle / Java Collections.shuffle form); (e) chain c += 1+draw(28); (e0) chain c += draw(29).
For e/e0 the generated increments are compared with the corpus increments D and −D, so the unknown first rune does not matter.

## 3. Seeds (`build_seeds.py`, `seeds_all.txt`: 143,022 lines)
- **114,674 integers.** 0..100,000; 3301, 1033, 509, 503 and 761 with their products and 3301·k for k ≤ 1000; PGP ids (0x7A35090F, 0x181F01E5, the 64-bit id),
  845145127, 1595277641, 2^31−1, 2^32−1. Every date from 2011-01-01 to 2015-12-31 as YYYYMMDD, DDMMYYYY, MMDDYYYY, YYMMDD, DDMMYY, MMDDYY and YYYYDDD,
  plus its unix 00:00Z and 12:00Z. Years 1990–2030. The 433 dukotah P3b PGP-timestamp seeds (rank 1 = 1325734783).
  Each integer seeds all 19 idioms (MT-py through Python int seeding).
- **5,760 distinct strings/byte strings.** The brief's list in case variants; page numbers 0–74 in 10 formats; the lane-A Cicada vocabulary
  (rebuilt from the same sources) in UPPER/lower/Capitalised; LP section lines; lane B's whole global seed dictionary (solved titles and
  plaintexts, page 56/57 texts, rune strings, gematria sums, the AN END hash, PGP fingerprints, 33 onions); 63 onion addresses in 4 forms; and
  SOLVED-PAGES.json fields. Each string gives 3 MT-py keys (py2.7 hash64, py2.7 hash32, py3 sha512), which make **17,058 distinct keys**, plus
  crc32 and Java hashCode integers fed to the 16 non-MT-py idioms (**11,290 distinct ints**).
- Generator output length per stream: **5,300 symbols**, so every offset from 0 to 5,000 is covered with room for a run.

## 4. Matching statistics (`search.c`) and null
Every stream is compared against the real 12,956 runes **and** against 20 D-shuffled corpora (increments permuted within each page; doublet count
86 → 87–89), built into the same index, so every stream yields one real value and 20 null values:
1. **exact**: the longest exact run at any alignment (gen offset × corpus position), Gematria order. Seeds are 5-gram hits. This covers
   whole-corpus generation, per-page restart, per-section restart and any other restart point. For e/e0 the same is done against D and −D.
2. **pattern (label-invariant)**: the longest run consistent with *some* bijection of the 29 runes (Unicode order, atbash, any rune list
   order), seeded by exact 5-grams of the previous-occurrence-distance transform (invariant under relabelling), at any alignment.
3. **hamming**: the maximum number of matches in a 64-rune window at each of the 55 real page starts, for gen offsets 0..1000. This catches a
   generator stream that is only partly overwritten. Offsets were capped at 1000 rather than 5000 for CPU (the machine was shared with other lanes).
   The null is analytic, Binomial(64, 1/29).

**Positive controls** (`control.py`, `ctrl/plants.json`; a control corpus with 4 plants, swept over all string seeds + ints 55k/66k/77k ±1000,
2.02M streams, its own 20 nulls):
| plant | found by | real value | next best (any seed) |
|---|---|---|---|
| P1 (brief): py2.7 `random.seed('cicada')`, PY2, model b, 262-rune page 0 | exact | **262, rank 1** (j=0, pos 0) | 8 |
| P2: glibc srand(77777), GLSC, model d, gen offset 137, relabelled to Unicode order, page 30 | pattern (exact correctly misses: 7) | **213, rank 1** | 19 |
| P3: Java Random(55555) nextInt, chain model e, page 40 | exact on D | **231, rank 1** | 8 |
| P4: numpy RandomState(66666) randint, model a, gen offset 2000, page 45 | exact | **271, rank 1** | 8 |

## 5. Results: direct emission and chain increments (16,874,340 streams)
Stream counts: MT-py idioms 131,732 seeds × 7 models each; other idioms 125,964 × 7. Per-cell bests are in `res/direct_table.md`; tails in `res/direct_tails.txt`.

**Exact runs, all direct models (12,053,100 streams; 8.3×10^14 alignments)**
| run length ≥ | real streams | null (mean of 20 shuffles) | analytic (q = 1/29) |
|---|---|---|---|
| 8 | 1,839 | 1,850 | 1,595 |
| 9 | 63 | 63.3 | 55.0 |
| 10 | **2** | 3.3 | 1.9 |
| 11 | 0 | 0.4 | 0.07 |

Chance expectation of the global best: log_29(8.3×10^14) ≈ 10.2. **Observed best: 10** (D48 model s, seed 87168; PHP5R model d, crc32 seed).

**Exact runs, chain increments e/e0 vs D and −D (4,821,240 streams)**: ≥9: 62 real / 50.1 null / 60.3 analytic; ≥10: **3** / 1.45 / 2.15;
≥11: 0. Best = 10 (PY3/PYGM model e, seed py32sha:"Accept"; PY3 e0, seed 67810).

**Label-invariant runs (direct)**: the best real run is 20, against a null mean of 47 streams per shuffle reaching ≥20 (real: 47) and 8.5 reaching ≥21 (real: 0).
At every threshold the real count is at or below the null. The largest values come from the model-s all-distinct blocks lining up with
all-distinct stretches of the corpus, and they move from shuffle to shuffle.

**Hamming (64-rune window at page starts, offsets 0..1000)**: direct best 18/64 (expected streams ≥18: 2.5; observed 1); ≥17: 32 against 26.7.
Chain best 17/64 (≥17: 7 against 10.7). The chain rows run about 15% above the 1/29 analytic baseline because s (1..28) is compared with
nonzero D, where the match rate is 1/28, not 1/29. A planted page scores 64/64.

Every (idiom, model) cell sits at the null: per-cell bests are 8–10 exact and 16–20 pattern (`res/direct_table.md`).

## 6. Results: model (f), generator output as the chain-cipher key (`keystream.c`, `analyze_f.py`, `res/f_summary.md`)
Decodes: additive chain p = (D−1 ± k) mod 28 (D=0 → EA) and GF(29) multiplicative p = D·K^±1 (K = 1+k, x(EA)=0), with k = draw(28).
Key consumed at every rune (X) or not on D=0 (Y), and continuous over the corpus (C) or restarted per page (R). That gives 16 decodes per stream.
Screen: normalised IoC (×29) of the decoded 12,956 runes. The noise floor is 1.023 because only 28 effective symbols appear.
- Controls: glibc srand(4242) %28 additive chain on English runes → **IoC 2.016, rank 1** (next 1.033). Per-page seeds 900+p, PY3, GF(29) →
  **1.918, rank 1** (next 1.033 for the wrong decodes).
- One stream per seed: 38,569,920 real trials. Null: 20 D-shuffles × 1/5 of the seeds = 154,279,680 trials. Null per-trial mean 1.02301,
  sd 0.00058. **Real max 1.02769 (z = 8.0) against null max 1.02818 (z = 8.9).** No real or null trial reached 1.030. English plaintext under the correct key gives about 1.7–2.0.
- Fresh seed per page (seed = s + page, s over all 114,674 integers): 17,430,448 real and 17,430,448 null trials. **Real max 1.02758 (z = 7.8) against null max 1.02803 (z = 8.6).**
- Per-idiom maxima, real against null, are tabulated in `res/f_summary.md`. Every real value is within about ±0.0008 of the null max for the same idiom.

## 7. Verdict per family
| family | verdict |
|---|---|
| Direct emission (a, b, c, d, s), 19 idioms, 143k seeds, offsets 0..5000, any restart point, Gematria order | **Excluded at power ≈1** (controls give 262–271 against a chance ceiling of about 10) |
| Same under any relabelling of the 29 runes | **Excluded** (P2 control 213 against null ≤ 22) |
| Chain increments as generator output (e: 1+draw(28); e0: draw(29)), ± direction | **Excluded** (P3 control 231 against best 10) |
| Partial overwrite near page starts (64-window Hamming, offsets ≤1000) | at the analytic null |
| Generator as chain-cipher key (f), 16 decodes, continuous, per-page restart and per-page seed | **null** (real max below the shuffle null max); covers English-like plaintexts only, through IoC |

**Limits (what this does NOT exclude):** integer seeds above 100,000, except the listed dates, timestamps and products (the 2^32 integer sweep exists only
for the additive model); generator idioms not in the table (e.g. Ruby, Perl ≥5.20 own drand48, .NET, OpenSSL/urandom, LCGs inside TeX);
offsets beyond 5,000 draws; generators whose draws are interleaved with other uses (e.g. also drawing word lengths); STDUID is unverified against a
binary. For model (f), plaintexts that are not English-like (low IoC) are out of reach of the screen.

## 8. Files
`prng.h` (generators/idioms/models), `vecgen.c` + `val/` (reference programs in C, C++, Java, PHP), `validate.py`/`validation.json` (261/261),
`seedfns.py`, `build_seeds.py`/`seeds_all.txt`/`seeds_counts.json`, `prep.py` (corpus.bin = real + 20 D-shuffles), `search.c`, `keystream.c`,
`control.py`/`control_f.py`/`ctrl/` (controls and results), `analyze.py`, `tails.py`, `analyze_f.py`, `res/` (raw shard outputs, `direct_summary.txt`,
`direct_tails.txt`, `direct_table.md`, `f_summary.md`).
