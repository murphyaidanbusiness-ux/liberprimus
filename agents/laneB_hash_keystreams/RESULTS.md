# laneB_hash_keystreams — RESULTS

(Section 1 written BEFORE any computation, per the brief. Later sections appended after the runs.)

## 1. Deduplication: what dukotah/leo already swept (read from LEDGER.json, ELIMINATION-LEDGER.md, analysis/round12-26)

**Common structure of ALL prior hash/KDF/PRNG sweeps: the keystream was applied ADDITIVELY (c = p +/- k mod 29, optionally atbash,
forward/reversed) under a "skip-aware beam" (pinned soft anti-repeat key-skip filter, supp 0.83, max_skip 3).  NO prior hash/KDF lane
applied a derived keystream through the CHAIN family (D_i = c_i - c_{i-1} = f(p_i, k_i), s_i in 1..28, EA = 0), nor through a
GF(29)-multiplicative chain.**  Leo's chain tests (tests5/6) used only integer sequences (primes, Fibonacci, pi digits, ...) and autokey, never hash outputs;
Leo's own "not tried" list names "keys derived from outguess data / page numbers / hashes".

| Lane (ledger id / path) | Seeds | Generators | Reductions to Z29 | Application | Size |
|---|---|---|---|---|---|
| R12-D3 pc_derivedkey.py | b"CICADA3301" (positive control only) | SHA-256 counter mode | mod29 | additive+key-skip, beam | control |
| R13-B04 (analysis/round13/B04) | 2,165 byte strings: LP/koan/puzzle words (756) + lines (500), lore titles, slogans, thematic keys, 132 onion forms, "3301"/1033/761/845145127/1595277641/dates (decimal-ASCII AND raw BE/LE 2/4/8 byte), first 5/10/15/29 primes, AN-END hash (ascii hex, raw 64B, reversed, halves), canon_256 payload, PGP fpr 6D854CD7...7A35090F/keyid/longid/uid; forms as-written/UPPER/lower/despaced. Core subset = 504 | 16: sha256/512/1/md5 counter (4B BE appended); sha256 ctr LE and ASCII ctr; sha256/512/1/md5 chain h=H(h); HMAC-SHA256(key=seed,msg=ctr); HMAC-DRBG-SHA256; RC4; AES-CTR (zero IV, derived IV); ChaCha20 | mod29, rej29(<232), hi-nibble%29, lo-nibble&15, bits5(reject>=29) | ADDITIVE (+/-), atbash, fwd/rev | 6.22M decodes: A offset 0 (all seeds), B 10 offsets (core), C per-page restart (core x 55 pages), D escalation. Best -6.185 (bar -5.5) |
| R13-B05 | pp49-51 256-byte payload (raw, reversed, bit-reversed, byte-swapped, hex-ascii) + contested-byte sweeps | same families | mod29, rej | additive+skip | ~70k decodes |
| R15/R16-KDF (analysis/round16/KDF) | 534 secrets (504 B04 core + 30 passphrases x forms) | PBKDF2-HMAC-SHA1/256 (1000,2048,4096,10000,100000,3301), SHA512 (1000,4096,10000), scrypt 16384/8/1, iterated H^n SHA256 (1000,10000,100000,3301), MD5 (1000,10000,3301), EVP_BytesToKey MD5/SHA256 (1,3301); salts empty/'3301'/self only; then 64B block expanded by SHA-256 counter mode | mod29, rej29 | additive+skip, atbash, +/-, fwd/rev, offset 0, 120-rune HEAD only | 692,064 decodes, best -6.259 |
| R16-PRNG, R8 SEED, R10-L5, R19/R21/R25/R26-A | integer seeds (unix seconds 2011-15, 32-bit slices) | MT (Py2.7 init_by_array), PHP mt_rand, .NET Random, ISAAC, BBS, LFSR, Geffe, Perl/glibc, TeX, drand48, ... (NOT hash functions) | various | additive+skip | ~2.5e9 |
| R26-C semantic seed | 323 values (292 int + 31 str): primes, totients, prime indices, 3301, 0x7A35090F fragments, dates, coords, gematria sums of 16 solved phrases, 31 solved-plaintext/koan strings | 7 generators (MT variants, glibc, totient/prime ladders) - NOT hashes | - | additive keyskip1/keyskip2 | 4,274 rows, best -6.578 |
| R12-C2 / R16-F-01 | running keytexts, LP2-as-key | - | - | additive | - |
| Anend preimage (iter 4/6) | page-56 SHA-512 as a TARGET: SHA-2/3, BLAKE/BLAKE2, Skein, Whirlpool, Streebog of held objects | - | - | not a keystream test | - |
| Leo tests5/6 | integer sequences, discrete-log bijections, ciphertext/plaintext autokey | - | - | CHAIN model (IoC28 1.08-1.15 = noise) | sequences only, no hashes |

**Explicitly flagged as NOT covered by dukotah** (their own "not_covered"/"open" lines): CHAIN application of any derived key; other
reductions (mod 28, base-29 digits of the integer value, hex characters as digits); SHA-3 / BLAKE2b / SHA-224/384 generators; HMAC other than
SHA-256; PBKDF2 with ITERATION COUNTS below 1000 and salts beyond empty/3301/self; seeds that vary PER PAGE (page number, title, previous
page's ciphertext, page's own first/last rune, cumulative ciphertext hash chaining); Gematria sum of each solved page as a hash seed (R26-C
used sums only as PRNG integer seeds, not as hash inputs); trailing-newline seed forms; rune-string forms of solved pages as hash seeds;
hash chains over the hex digest (h = H(hexdigest(h))); decoding past the 120-rune head under KDFs.

**Therefore this lane targets:** {chain-additive (2 key-consumption conventions, +/-), GF(29) multiplicative chain (mult/div; log form), plain-OTP control}
x {MD5, SHA-1, SHA-256, SHA-512, SHA3-256/512, BLAKE2b} x {counter-appended (BE4/ASCII 0/ASCII 1), counter-prepended, chain on digest, chain on hex digest, HMAC(seed, ctr), small-iteration PBKDF2}
x {byte mod 28/29, rejection 28/29, nibbles, bits5, hex ASCII, base-28/29 digits of the integer} x {continuous, per-page restart, per-page seeds}.
Pure additive-with-skip duplicates of B04 (sha256/512/1/md5, mod29/rej29, ctr/chain) are kept ONLY as the plain-OTP control row and are not counted as new coverage.

---

## 2. What was tested (all code in this directory: core.py, gens.py, seeds.py, driver.py, sweep.c, control.py, run_real.py, analyze.py)

**Cipher families applied to every keystream** (decode of the real 12,956 runes; chain increments D_i = c_i - c_{i-1} mod 29, prev = 0 at each page start):
- chain-additive: D = 0 -> EA; else p = (D-1 -/+ k) mod 28, k in Z28 (x2 signs)
- GF(29) multiplicative chain, x(EA) = 0: p = D*K or D/K, K = k+1 (x2)
- GF(29) multiplicative, log form K = g^k, p = log_g D -/+ k, g in {2,3} on the full dictionary (x2 signs) and the other 10 primitive roots {8,10,11,14,15,18,19,21,26,27} on the 578-seed "core" dictionary
- both key-consumption conventions (X: key consumed at every rune; Y: key not consumed on D = 0 / EA) for all of the above
- control: plain one-time pad p = c -/+ k mod 29 on raw runes (fails by construction: the doublet fingerprint excludes it)
- key start offset koff = 0 and 1 (full dictionary), keystream modes: continuous over the corpus, restarted at each page, and a different seed per page ("perpage")

**Keystream sources (distinct hash-keystream configurations = "streams"):**
- G (global seed): 2,184 seeds x 49 generators = 107,016 streams. Seeds (string AND bytes forms, +/- trailing newline, as-is/UPPER/lower): the brief's words (3301, cicada, cicada3301, liberprimus, liber primus, ...), page numbers 0..57 (decimal ASCII, raw big/little-endian 1/2/4/8 bytes, zero-padded, "N.jpg", "page N", i.e. the page indices 0..54, 1..55 and the onion7 file numbers 0..57), the titles and plaintexts of the 5 solved pages (SOLVED-PAGES.json), the page-56 and page-57 texts, rune strings (utf-8 runes / index bytes / transliteration) of the solved pages and of the loader's pages 55-56, the Gematria Primus sum of each solved page (+ total, + rune counts, in all integer forms), the page-56 SHA-512 hex (ascii lower/upper, raw, reversed, halves), PGP key id 7A35090F / long id / fingerprint 6D854CD7...7A35090F (hex and raw, spaced, 0x-prefixed), the 33 onion addresses from dukotah's seed file (with/without ".onion").
  Generators (7 hashes MD5, SHA-1, SHA-256, SHA-512, SHA3-256, SHA3-512, BLAKE2b x 7 constructions): H(seed||ctr_BE4), H(seed||ascii ctr from 0), H(seed||ascii ctr from 1), H(ascii ctr||seed), chain h=H(h), chain on hex digest h=H(hex(h)), HMAC_H(key=seed, msg=ctr).
- PB: PBKDF2-HMAC (SHA-1/256/512) with iterations {1,2,3,10,100,1000} and salts {empty,"3301"} on 538 core seeds + page numbers = 20,304 streams.
- G_extra: 290 further seeds (35 additional onion addresses found by grepping all repos, + the second fingerprint 67F363C6...7A35090F seen in repos) x 49 gens x koff {0,1} = 28,420 streams.
- G_core_roots: 578 core seeds x 49 gens x 10 further GF(29) primitive roots = 28,322 streams.
- G koff=1: full G dictionary again with the key starting at index 1 (107,016 streams).
- P (page-indexed seeds): 931 seed functions of the page index p x 49 generators = 45,619 stream-sets (each set = a separate stream per page, 55 pages, ~2.5M page streams): str(p) and p+1 with 12 prefixes (none, cicada, cicada3301, 3301, liberprimus, liber primus, page, Page, LP, p, Cicada, CICADA) x 6 separators x {dec, zero-padded, N.jpg} x newline +/-; raw integer bytes; the previous page's ciphertext (utf-8 runes / index bytes / transliteration), page p-2, the cumulative ciphertext of pages < p, the page's own ciphertext, the page's own first / last / first+last rune (several encodings, also of the previous page), Gematria sum of own/previous page, page length, and page-to-page hash chains s_p = H(s_{p-1} || ct_{p-1}) (both orders, 3 inits, 7 hashes).

**Byte-to-key mappings (20):** byte mod 28 / 29; rejection sampling (drop >= 252 for mod 28, >= 232 for mod 29); nibbles (hi, lo); bits grouped in 5 (mod 28/29 and rejection <28/<29); hex-digest ASCII characters mod 28/29; base-28 digits and base-29 digits of the integer value of each digest (least-significant-first fixed width and most-significant-first), reduced to Z28 by mod or rejection.

**Trial counts (a trial = one stream x mapping x application x convention x mode):**

| sweep | streams | trials |
|---|---|---|
| G, koff 0 | 107,016 | 44,518,656 |
| G, koff 1 | 107,016 | 44,518,656 |
| G_extra (koff 0,1) | 28,420 | 11,822,720 |
| G_core_roots (10 more primitive roots) | 28,322 | 33,533,248 |
| PB (PBKDF2) | 20,304 | 8,446,464 |
| P (per-page seeds) | 45,619 sets | 9,488,752 |
| **total real** | **336,697** | **152,328,496** |
| null: G (40 D-shuffled corpora, 5% of the streams each, koff 0) | 214,476 | 89,222,016 |
| null: P (40 D-shuffled corpora, 5% of the sets each) | 91,169 sets | 18,963,152 |

## 3. Scoring, positive controls and null calibration

**Statistic.** Primary: IoC of the decoded rune stream over all 12,956 runes (also over the first ~3,000 runes, and per page). IoC is invariant to the (unknown) rune<->index bijection sigma and to a constant offset in k, so the screen is robust to the unknown plaintext labelling; it only needs the key stream to be right. Secondary: quadgram score (dukotah quadgram file, log10/quadgram, identical to the oracle's score_norm; English -4.1..-5.0, noise ~ -7.6) on the top candidates.
Because the chain apps can only emit EA when D = 0 (0.66% of positions), the decoded stream has 28 effective symbols, so the noise baseline is **1.02302 (sd 0.00058)**, not 1.000; the OTP control group has baseline 1.00002.

**Null (important correction).** A plain within-page shuffle of the ciphertext is NOT a valid null for the chain family: it restores the 3.45% doublet rate (D = 0), moving the noise baseline to 1.000 and inflating every z-score to ~48. I ran it first (kept in nullpos/), saw the baseline mismatch, and replaced it with a **D-shuffle null**: within each page the increments D_i are permuted and the corpus rebuilt by cumulative sum, preserving the D multiset (0.66% doublets, EA rate) while destroying any order-dependent structure. Null = 40 shuffles (>= 20 per page, same procedure, same generators, same mappings/applications, 5% of the streams per shuffle so that total null trials >= real trials); the per-trial IoC distribution of the null (mean 1.02302, sd 0.00059) is identical to the real one.

**Positive controls (all PASS).** A synthetic chain ciphertext was generated from the solved-page plaintext (tiled to the real page lengths; plaintext IoC 1.774, ciphertext IoC 1.00, doublet rate 1.0%), enciphered with hash-derived keystreams and then pushed through the unmodified full pipeline (dictionary search over all generators/mappings/applications, same C kernel):

| control | planted config | recovered rank | IoC planted / best other | decode |
|---|---|---|---|---|
| G1 | SHA-256 ctr_BE4, seed "cicada3301", byte mod 28, chain-additive+ conv X, continuous; full 2,184-seed x 49-gen dictionary (44.5M trials, 107,016 streams) | #1 | 1.7742 / 1.0755 (same stream, wrong app) | quadgram -4.314, text exact ("AWARNNGBELIEUENOTHNGFROMTHISBOOC...") |
| G2 | SHA3-512 HMAC-ctr, seed "THE PRIMES ARE SACRED", base-29 digits MSD rejection, GF(29) log g=3 (-), conv Y, per-page restart | #1 | 1.7742 / 1.0904 | exact |
| G3 | BLAKE2b chain-on-hex, seed "7A35090F", hex-ASCII mod 28, GF(29) mult, conv X, continuous | #1 | 1.7742 / 1.1444 | exact |
| G4 | SHA-1 ctr_ASCII1, seed "3301", byte rejection mod 29, plain OTP (-), continuous | #1 | 1.7742 / 1.0046 | exact |
| P1 | BLAKE2b ctr_ASCII1, per-page seed "cicada3301-<p+1>", hex-ASCII mod 28, GF(29) mult, conv X | #1 (of 4,900 sets) | 1.7742 / 1.1419 | exact |

A correct stream therefore sits at IoC 1.774, i.e. ~1,270 sd above the noise mean and 0.746 above the null maximum. Detection power: a stream correct on only ~0.76% of the corpus (about 97 contiguous or scattered runes) already exceeds the null max, so a page-sized partial hit would also have been seen. The C decoder was cross-checked against an independent Python encipher for all 36 (application x convention) tables x 2 modes: 0 mismatches.

## 4. Results (real data)

| sweep | trials | max whole-corpus IoC (real) | null max (pooled) | max first-3000-rune IoC real / null | verdict |
|---|---|---|---|---|---|
| G koff 0 | 44.5M | 1.0278 (z = 8.2 vs per-trial null; quadgram -7.69) | 1.0287 (82.4M chain trials) | 1.0463 / 1.0435 | null |
| G koff 1 | 44.5M | 1.0279 (z = 8.3) | 1.0287 | 1.0456 / 1.0435 | null |
| G_extra | 11.8M | 1.0277 | 1.0287 | - | null |
| G_core_roots | 33.5M | 1.0278 | 1.0287 | - | null |
| PB | 8.4M | 1.0273 | 1.0287 | 1.0427 / 1.0435 | null |
| P (per-page seeds) | 9.5M | 1.0275 (z = 7.6) | 1.0275 (17.5M chain trials) | 1.0438 / 1.0447 | null |
| OTP-control rows (all sweeps) | ~9M | 1.0044 | 1.0044 | - | null (expected) |

- A z of ~8 looks large but is simply the extreme-value tail of 4e7 non-independent trials: the identical null procedure reaches 1.0287 (z = 9.5) in its pooled sample, and the per-shuffle null maxima are 1.0268..1.0287 at only 1/20 of the trials each; the real best (1.0278) is at the expected order statistic. The real maximum never exceeds the null maximum in any sweep.
- First-3000-rune statistic: real 1.0463 / 1.0456 vs null pooled max 1.0435 (G) and 1.0447 (P): the two real top values are 0.0028 above the null, but both decode to noise (quadgram -7.56/-7.67), whole-corpus IoC 1.0245 and are the best-of-89M values of a statistic with sd ~0.003; with equal real/null trial counts the chance (k0+k1 pooled, equal trial counts) of the top two both falling on the real side is ~1/6. No English.
- Per-page maxima (55 pages): pages on which the real per-page max exceeds the pooled null max: 23/55 (G k0), 15/55 (G k1), 15/55 (P) against 18.3/55 expected by chance. Nothing.
- Quadgram of the top-5 real candidates by IoC: -7.56 .. -7.69 (noise band; English would be -4.1..-5.0). Best candidate "plaintext" (G, koff 1, seed "Page 8\n", MD5 ctr_ASCII1, byte rej-28, GF(29) log g=3, conv Y), first 120 runes: `CIAOENGTHJEEONHLTHTGGEOJRDJDDNRPRJGOWENRFPHJMIAYIAFFASRRIIFSEOWYHBJBJIASSDIAAESSRTYUEIEOTHOEXRAELWCGCNGNENFHINGNGAEAMUFONGNGIPOEJLNGNTHIAPGOEIOEOEIA` - noise.
  Best by whole-corpus IoC at koff 0: `EOGRPEOTHPIXOEFNTHXOEHOEOIAIJTNEODCYEULPSDRAJIAALJCBNGLXXRIAGNGMXFRIAHSUXXIWGGPDDHMNFHTHLJAEDRDNJJFWICGTETNEOEOICSPUEOABEOBUIAIBTHTYAETHOEHOEUDCOR` (seed = bytes of 184, SHA3-512 ctr, base-29 digits MSD mod 28, chain-additive+, restart) - noise.

**Oracle.** Nothing beat the null, so nothing qualifies for submission. For completeness, the single best real candidate (above, G koff 0) was converted to its equivalent additive keystream (e_i = c_i - p_i) and submitted: `verify_solution.py --keystream cand_G_top1_keystream.txt --pages 3` -> **FAIL**, best page -6.973 vs bar -5.500 (the oracle's self-test passes).

## 5. Verdict per family (honest)

- **Chain-additive (both conventions, +/- key), hash-derived keystreams, all 7 hashes, 7 constructions, 20 byte-to-key mappings, the seed dictionary of this brief, continuous / per-page restart / per-page seed:** NEGATIVE over the stated bound. 152M trials, controls recover the plant at rank 1 in every mode.
- **GF(29) multiplicative chain (K = k+1 or g^k for all 12 primitive roots; mult and div):** NEGATIVE over the same bound (roots 2,3 on the full dictionary; the other 10 roots on the 578-seed core dictionary).
- **PBKDF2 with small iteration counts (1..1000), salts empty/3301:** NEGATIVE on 538 core seeds + page numbers.
- **Per-page seeds (page number in 300+ textual forms, previous-page ciphertext, first/last rune, page-to-page hash chain):** NEGATIVE.
- **Plain OTP control (c - k mod 29):** NEGATIVE (as predicted by the doublet fingerprint; also dukotah's B04/KDF lanes had covered this with a skip-aware decoder).
- What this does NOT show: that the key is not derived from a hash. Not covered: seeds outside the dictionary (the dictionary here is ~2.2k global + 0.9k page-indexed + 0.3k extra forms); salts other than empty/"3301" and KDFs other than PBKDF2 at small counts; HMAC with a keyed construction other than HMAC(seed, ctr); keystream offsets other than 0 and 1; a chain that starts from a non-zero initial value or uses c_{i-1} across page boundaries; sigma/x(EA) conventions other than "EA is the rune whose increment is 0" (IoC is insensitive to sigma but not to which rune takes the D=0 slot, and to the key being a function of position only); a filter-style construction (family (b): flat cipher + advance key on output repeat) with hash keys is NOT re-tested here beyond dukotah's B04 (which used 2,165 seeds, SHA-1/256/512/MD5, additive+skip).
- Net: the SHA-2/SHA-3/BLAKE2b/MD5/SHA-1 counter / chain / HMAC / PBKDF2-keystream family, as applied through the chain ciphers (the only family consistent with the fingerprint) and seeded from this brief's Cicada-semantic dictionary, is closed to 152M trials, with a demonstrated ability to recover a planted key at IoC 1.774 (null max 1.029).

## 6. Files
- ./agents/laneB_hash_keystreams/ : sweep.c/libsweep.so (C kernel), core.py (apps, mappings, scoring), gens.py, seeds.py, driver.py, run_real.py, control.py, analyze.py; analysis_G.txt, analysis_P.txt (full numeric reports); res_*.pkl (raw results incl. top-60 lists, histograms, per-page maxima); control_*.log (positive controls); nullpos/ (the discarded plain-shuffle null); cand_G_top1_keystream.txt (oracle submission).
