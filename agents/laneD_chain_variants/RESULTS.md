# laneD_chain_variants: cipher constructions that reproduce the fingerprint but are not the plain chain

Lane: `laneD_chain_variants`. Code and raw outputs are in this directory (`s1_lags_D.py` ... `s8b.py`, `*_out.txt`; shared helpers `common.py`, `sim.py`).
Data check: loader SHA-256 matches the pin (12,956 runes, 55 pages). Within-page adjacent pairs: 12,901, of which 86 are doublets (0.667%, z = -17.3 against p0 = 0.03448).

## Summary

No construction tested gives a new decryptable lead.

Every construction I could build that matches the fingerprint falls into one of three classes:

1. A chain or "repeat-avoiding rewrite" whose only distinguishing content is the plaintext. No ciphertext statistic separates it from the plain chain.
2. A construction that the ciphertext excludes at |z| >> 5 against a matched null, with a positive control showing the statistic would have fired.
3. A construction that is statistically allowed but is lossy or not decryptable.

New hard constraints, beyond the earlier lanes and the community ledgers:

- **Lag.** The only deficit anywhere in lags 1..238 is lag 1. At lags 2..238 the minimum z is -3.10, against a null minimum of -2.91 +- 0.35. A base lag of 2 or more with nonzero increments is excluded.
- **Rewrite target.** No rewrite target is detectable. D = 1 holds 457 against 458.8 expected for the other values (ratio 0.996). A bump encoder predicts a ratio of about 1.83. The fraction of would-be collisions rewritten to +1 is -0.002 +- 0.049, and any single offset is below about 0.08. The deficit needs 0.81.
- **Fixed table.** Fixed-table ciphertext feedback is excluded at more than 200 sigma, even if the table differs per page. The key must vary by position.
- **Independent key.** No key independent of the text can give the fingerprint on letter-level English. Doublet rate >= min_x P(q_i - q_{i-1} = x), which is about 1.3-1.6%. The real rate is 9 standard errors below that bound.
- **Reading order.** Reading order is the chain order, and no other reordering family reproduces the deficit. Transposition after the chain is excluded for any non-adjacency-preserving permutation. Transposition before the chain is invisible to any ciphertext statistic.
- **Key-skip Vigenere.** Per-page-keyword Vigenere with key-skip-on-collision would leak a period peak, which is absent. Its doublet rate also needs 19% of adjacent keyword letters to be equal, which a keyword cannot supply.

What stays alive is what was alive before: a chain (or equivalent rewrite) over a flat, aperiodic key. The one new surface is the lag-2 form of that family. Its periodic-keyword form is now excluded (z 0.49 against positive controls at z 24-76). A running or PRNG key on lag-2 differences remains untested here, but it is no more or less plausible than the lag-1 version.

## Common conventions

- Null: independent shuffle of each page's runes (preserves page composition and length). Where the statistic depends on the doublet hole itself, I shuffle the increments D within each page and rebuild the page by cumulative sum, which keeps the exact hole (`s8`).
- Positive controls: synthetic ciphertext from the solved plaintext at the real page lengths. Only the five solved pages with recoverable plaintext are available, which is 1,769 runes with EA = 1.0% (the community figure is 0.67% from 2,979 runes). For ciphers with ciphertext feedback I used an order-1 Markov plaintext trained on those pages (`common.markov_plain`), because tiling the 1,769 runes creates verbatim repeats that fixed-table ciphers reproduce. The chain controls therefore show a doublet rate of about 1.0% (the EA frequency), not 0.66%. That does not affect any conclusion.
- Large-corpus English for the Fourier bound in section 4: 354,569 runes transliterated from Python's `pydoc_data.topics` (`eng_runes.npy`). This is technical English, not Cicada prose, so it is used only for difference spectra.
- The oracle was not run, because no candidate keystream was produced.

## Real-text baseline used throughout (`s1_out.txt`)

| statistic | real | note |
|---|---|---|
| lag-1 doublets | 86 / 12,901 = 0.667% | z = -17.3 |
| lag-2..10 coincidence z | -0.38, -0.34, 0.58, 1.25, 0.28, 0.17, -0.52, 1.25, -0.13 | normal |
| lag z over 2..238 | min -3.10 (lag 11), max 2.13 (lag 213) | null (300 shuffles): min -2.91 +- 0.35, max 2.98 +- 0.77 |
| D = c_i - c_{i-1} histogram | D=0: 86; D=1..28 about 457 each | chi2 (df 27) = 42.1 against null 26.9 +- 7.6, a 3.3% tail that is mild and uncorrected for multiple tests; max abs z over D = 2.70 against null 2.28 +- 0.48 |
| IoC | 0.9999 | rune-count chi2 against flat = 26.4 (df 28) |

## Candidate 1: base lag other than 1, with an explicit avoid-c_{i-1} rule (`s1`, `s8`)

**Constructions.**

- **1a.** c_i = c_{i-2} + s_i with s_i nonzero (zero only for EA) and no extra rule.
- **1b.** c_i = c_{i-2} + (p_i + k_i), with s_i flat on 0..28 and a repeat-avoidance rewrite against c_{i-1}, which leaks at 19% to match 0.66%.

**Predicted signatures.**

- 1a: the deficit sits at lag 2 only, and lag 1 is normal.
- 1b: marginals are identical to the lag-1 chain, because the rewrite creates the lag-1 hole. The only available difference is the rewrite target, which gives a D = 1 excess if the rule is "+1" (candidate 7).
- 1b with a periodic keyword: the lag-2 difference stream E_i = c_i - c_{i-2} = p_i + k_i is a Vigenere stream, so its coset IoC is elevated at the key period.

**Measurements** (z against shuffle null; positive controls are means of 12 syntheses):

| construction | lag-1 z | lag-2 z | min z lags 2..238 | D=1/other |
|---|---|---|---|---|
| **real** | **-17.3** | **-0.38** | **-3.10** | **0.996** |
| chain L=1 (EA-zero) | -15.2 | 0.7 | -2.6 | 0.98 |
| chain L=2 | -0.3 | **-15.0** | -15.0 | 0.99 |
| chain L=3 | 0.0 | -0.5 | -15.2 (at lag 3) | 1.00 |
| 1b lag-2 + rewrite, bump | -17.5 | 0.9 | -2.8 | 1.83 |
| 1b lag-2 + rewrite, redraw | -17.5 | 0.4 | -2.7 | 0.99 |

Periodic keyword on lag-L difference streams (`s8`, periods 2..60 per page, summed over pages, null = D-shuffled pages with the hole preserved):

| L | real z | best single-page z (real vs null max, 60 shuffles) |
|---|---|---|
| 1 | 1.02 | 4.82 against 4.56 +- 0.54 |
| 2 | 0.49 | 4.56 against 4.11 +- 0.48 |
| 3 | 1.67 | 4.91 against 4.08 +- 0.42 |
| 4 | -1.00 | 3.74 against 4.13 +- 0.42 |

Positive control for the periodic-keyword lag-2 form: c_i = c_{i-2} + p_i + keyword[i mod P], with rewrite leak 0.19. The lag-2 difference stream gives z = 76.4 (P=7), 44.8 (P=13) and 24.7 (P=23). The lag-1 stream gives only 1.9 to 2.9, so the test discriminates the lag.

**Verdict.**

- 1a is excluded. A lag-2 chain with nonzero increments predicts z = -15 at lag 2. Real is -0.38.
- Explicit-rule lag-2 (1b) is statistically indistinguishable from the lag-1 chain at every order tested. It is not excluded and it is not a lead, because its marginals are the same.
- Periodic keywords on E_L (L = 1..4) are excluded.
- The decryption model for 1b would be p_i = (c_i - c_{i-2}) - k_i. Rewritten positions (about 81% of the 3.45% would-be collisions, roughly 360 positions) destroy information unless the rewrite is key-deterministic. It would need a keystream search on the E-stream with unknown resynchronisation points. Nothing in the ciphertext suggests a starting point.

## Candidate 2: Gematria prime-value domain (`s2`)

**Constructions.**

- **B.** v(c_i) = v(c_{i-1}) + v(p_i) + k_i mod M, snapped back to a prime-valued rune (next, previous or nearest prime), for M = 109, 110, 111, 113, 116.
- **A1.** Additive s = v(p) + k mod 29.
- **A2.** Multiplicative s = k * (v(p) + a) mod 29, with k in GF(29)*.

**Predicted signatures.**

- B: with k flat, v_out is uniform on Z_M. Rune probability is proportional to the snap cell width (the prime gap), so IoC is above 1, rune counts are non-flat, and doublets are at least 3.4%.
- A1: s = 0 with probability 1/29, so doublets are 3.45%.
- A2: the zero-letter is whichever rune has residue -a. Doublet rate equals that letter's frequency.

**Measurements.**

- **B:**
  - Predicted IoC is 1.10 to 1.25 for all 15 (M, snap) combinations. Real is 1.000, and real rune counts match flat (chi2 26.4).
  - Log-likelihood ratio of real counts under the snap pmf against flat is between -581 and -11,304, so the real counts reject every snap model.
  - Simulated doublet rate is 3.4% to 4.7%.
  - Excluded.
- **A1:** simulated 3.47%. The real rate is 17.4 standard errors below it. Excluded.
- **A2 with a=0** (zero letter N, v=29): simulated 5.6%. **a=28:** 6.9%.
- **A2 with a=8:** zero letter NG (0.73% of plaintext) gives a simulated rate of 0.74%, which is within the real band. It is the only offset in the real band, and it is a one-parameter fit. The 29 prime values occupy only 24 of 29 residues mod 29. F/I/D share residue 2, U/B share 3, C/M share 13, and P/AE share 14. So x(p) = v(p) + a mod 29 is not injective and the cipher would be lossy. This is therefore not a clean decryptable candidate, and the doublet rate does not discriminate it.
- **Atbash / reversed prime-order alphabet:** this is the unit map x -> -x on Z29, which turns a chain with s into a chain with -s. The statistics are identical, so it is skipped.

**Verdict.** Prime-domain, mod-109/110 snap constructions are excluded. The multiplicative prime-residue chain is not excluded by statistics, but it is non-injective. Its injective relabellings were already covered by Leo's 14 bijections, including the 12 discrete logs, in tests5.

## Candidate 3: fixed-table ciphertext feedback c_i = T[p_i][c_{i-1}] (`s3`)

**Argument.**

- For every previous rune a, the map p -> T[p][a] is a bijection (Latin column). Hence P(c_i = b | c_{i-1} = a) = P(p_i = T_a^{-1}(b) | c_{i-1} = a).
- Given the whole plaintext and a uniform c_0, c_{i-1} is uniform, because each step applies a permutation. So c_{i-1} is independent of p_i up to the language's own p_{i-1} -> p_i dependence.
- The conditional distribution of c_i is therefore a permutation of the plaintext unigram, and its IoC is sum_p P(p)^2 = 1.76 normalised. The same holds backwards, because rows are bijections too.
- "No repeat except one p*" means the p* row is the identity. Any Latin square whose p* row is the identity automatically satisfies T[p][c] != c elsewhere.
- Depth 2 is sharper still: (a, b) fixes p_{i-1}, so the conditional equals the bigram-conditional IoC, about 3.5.

**Measurements** (200 within-page shuffles; the shuffle null has no hole, so 29/28 = 1.036 is the flat-on-28 value):

| statistic | real | prediction for a fixed T | null / control |
|---|---|---|---|
| pooled forward conditional IoC | 1.0257 | 1.74-1.79 | null 1.0001 +- 0.0030 |
| pooled backward conditional IoC | 1.0257 | 1.74-1.79 | null 0.9998 +- 0.0031 |
| per-previous-rune row IoC | min 0.995, max 1.062 | all rows about 1.56-1.8 | null min 0.971, null max 1.039 |
| depth-2 pooled | 1.0123 | about 3.5 | null 1.0010 +- 0.0165 |
| per-page table, context = (page, previous) | 1.0304 | 1.70-1.75 | null 0.9869 +- 0.0224 |

Sigma distances of the real value from the prediction:

- Forward depth 1: 245 sigma below the English prediction of 1.76.
- Backward depth 1: 237 sigma below.
- Depth 2: 45 sigma below the single-table prediction used for the z (1.76; the control prediction is about 3.5).
- Per-page table: 32 sigma below.

The real pooled value 1.0257 is not 1.000. It sits 8.5 sigma above the shuffle null because of the doublet hole itself. The flat-on-28 value is 1.036, and the bound for any input with a 0.66% rare symbol and flat otherwise is 1.0234. The real value is 1.2 sigma from that bound. So the ciphertext is exactly what a flat-increment chain predicts, and nothing English survives conditioning on the previous rune.

Positive controls (Markov plaintext, three random no-repeat Latin squares built by cycle-switching from the cyclic square, plus the constant-key chain): forward 1.738-1.749, backward the same, depth 2 about 3.5, minimum row 1.58-1.61. Position-varying keyed chain: 1.017. Flat Vigenere: 1.001. A different Latin square per page: 1.70-1.75.

**Formal exclusion.** For ANY fixed T, and even a different fixed T per page, the conditional IoC given the previous rune equals the plaintext-symbol IoC, which is at least about 1.76 for English-like letters. The real value is 1.026. The table therefore cannot be fixed, and the cipher must vary by position. That is equivalent to a keyed stream.

Escape hatch, stated honestly: the input to T could itself be pre-flattened by a homophonic or compressing stage. The measured English-like word-length profile argues against it, and it would amount to a keyed first stage anyway.

## Candidate 4: flat cipher after a doublet-free transform (`s4`)

**Bound.** Let q be any transformed text, X_i = q_i - q_{i-1}, and let d_i = k_i - k_{i-1} be the key increment. If the key is independent of q, then

P(c_i = c_{i-1}) = sum_x P_X(x) P_d(-x) >= min_x P_X(x).

For plain letters:

| corpus | min_x P_X |
|---|---|
| solved pages | 0.0158 |
| 354k-rune English | 0.0132 |
| Markov plaintext | 0.0163 |

The real rate is 0.0067 +- 0.0007, which is 9.1 standard errors below the 354k-rune bound. For a doublet-free q, P_X(0) = 0 and the bound is vacuous. But making the key increments avoid -X forces d_i = 0 most of the time, which leaves X as the increment, and X is not flat (IoC28(X) is 1.10 to 1.16, against real D at 1.001).

**Fourier version.** For a hole-flat D with hole eps, |phi_D(t)| = 1/29 - eps = 0.0278 for t != 0. Independence gives |phi_D| = |phi_X| |phi_d| <= |phi_X|. So every t needs |phi_X(t)| >= 0.0278.

- English 354k runes: min |phi_X| = 0.0142 (t=9), with 4 of 28 values below the line.
- Solved pages: min 0.0090, with 2 of 28 below.
- Deconvolving d from these gives negative probabilities (min -0.31).

The real |phi_D| averages 0.0298 against 0.0278 predicted for a chain. The power of the real data against the independent-key alternative is mild at this sample size, which is why the doublet bound is the stronger statement.

**Simulated constructions** (Markov plaintext, 6 syntheses, real page lengths; real: dbl 0.0067, D-IoC28 1.001, IoC 1.000):

| construction | dbl | z vs real | D-IoC28 |
|---|---|---|---|
| raw + flat iid key (OTP) | 0.0344 | -17.3 | 1.000 |
| 4a collapse-runs q + flat iid key | 0.0355 | -17.7 | 1.000 |
| 4b bump(+1) q + flat iid key | 0.0348 | -17.4 | 1.000 |
| 4c raw + non-repeating iid key | 0.0356 | -17.7 | 1.000 |
| 4d collapse + Vigenere keyword L=7 | 0.0349 | -17.5 | 1.001 |
| 4d collapse + Vigenere keyword L=13 | 0.0348 | -17.4 | 1.001 |
| 4e collapse + piecewise-constant key, change p=0.18 | 0.0064 | +0.4 | **1.102** |
| 4f same, change p=0.05 | 0.0021 | +11.4 | 1.131 |
| 4g bump + biased-walk key | 0.0269 | -14.2 | 1.055 |
| reference keyed chain (EA-zero) | 0.0106 | n/a | 0.999 |

**Verdict.**

- Any text transform followed by a text-independent flat key is excluded (4a-4d, 4g).
- The only variant matching the doublet rate is 4e (a key that changes about every 5 letters). It leaves the plaintext-difference distribution visible: D-IoC28 is 1.10 against the real 1.001, far outside the shuffle-null sd of 0.0006 (`s6`).
- The chain's key is coupled to the text, which is exactly what makes it a chain.

## Candidate 5: transposition before or after the chain (`s5`)

**Search.** 470 reorderings per page: columnar (widths 2..40, left/right column order, up/down, and the inverse of each), rail fence (2..40 and inverse), serpentine, block reversal, identity and reverse. 390 of them keep under 20% of adjacent pairs, which I call genuinely different.

**Predicted signature.** If the chain was applied in a different reading order and the book shows a transposed ciphertext, the deficit would appear in the unscrambled order and not in reading order.

**Real.**

- Reading order: 86 doublets, z = -17.3.
- Best of the 390 genuinely different reorderings: z = -3.18 (`col(w=11,Lcols,down)`, and its mirror forms). The null minimum over the same 390 reorderings in 60 shuffled corpora is -2.96 +- 0.38 (min -3.90), so the real best is not distinguishable from noise.
- The reading order has strictly fewer doublets than every one of the 390 other reorderings on 23 of 55 pages, and no more than all of them on 37 of 55. In shuffled corpora the strict count is 0.1 +- 0.3 of 55.
- Block-reversal and serpentine permutations preserve most adjacency and so retain the deficit in proportion to the fraction of pairs preserved (blockrev b=2 gives z = -8.5, b=40 gives -17.1). A permutation that keeps adjacency cannot be excluded by this statistic.

**Positive controls** (chain on Markov plaintext, then transposition of the ciphertext at page level; 3 syntheses each): the unscramble scan finds the exact inverse permutation as the unique best, with z about -14 to -15.

| transposition applied after the chain | reading-order z | best reordering found |
|---|---|---|
| none | -14.4 | none (best -3.0) |
| columnar w=13 | -0.1 | `col(w=13)^-1`, z = -13.8 to -15.2 |
| columnar w=7, reversed columns, up | 0.3 | `col(w=7,Rcols,up)^-1`, z = -14.3 to -15.0 |
| rail fence r=5 | 0.5 | `rail(r=5)^-1`, z = -14.4 to -14.8 |
| columnar w=29 | 0.4 | `col(w=29)^-1`, z = -14.1 to -14.7 |
| serpentine w=17 | -15.0 | stays in reading order; no genuinely different reordering exceeds -3.4 |
| block reversal b=6 | -12.3 | stays in reading order; no genuinely different reordering exceeds -3.8 |

**Which lag statistics survive.**

- After a columnar or rail transposition of the chain output, the chain-adjacent pairs end up at a page-dependent lag of about n/w, or at a structured set of lags for rail fence. A single pooled lag profile dilutes this, because page lengths vary.
- The real lag profile shows only lag 1 (candidate 1). The unscramble scan above is the right test.
- A chain applied to a transposed plaintext (transposition before the chain) gives ciphertext statistically identical to the plain chain for any flat key. It is unfalsifiable from the ciphertext, and only a decryption could test it.

**Verdict.** Transposition after the chain is excluded for all non-adjacency-preserving permutations in the family. Transposition before the chain is neither excluded nor testable without the key.

## Candidate 6: key-skip-on-collision Vigenere, per-page keyword (`s6`)

**Construction.** c_i = p_i + key[j]; if this equals c_{i-1}, skip one key letter and recompute. A leaked doublet needs the next key letter to equal the current one, so the leak is (3.45% collision rate) x (fraction of adjacent equal key letters). A "skip until clear" variant gives zero doublets.

**Leak statistics beyond doublets.**

1. The doublet rate is a function of the keyword: 0.11% for random keywords (L=5..20), and 0.65-0.70% needs sticky keywords with a = 0.19, where 19% of adjacent key letters are equal. A natural keyword cannot supply that. Simulated: random keyword 0.0010-0.0014; sticky a=0.19 gives 0.0065 (L=8) and 0.0070 (L=13).
2. A per-page period leaks through the lag coincidence. Statistic: sum over pages of the best-lag z in lags 2..60.

   | | sum of per-page best-lag z | z vs null |
   |---|---|---|
   | real | 136.9 | -0.05 (null 137.1 +- 4.7) |
   | random keyword L=5 | 194.7 | 12.3 |
   | random keyword L=8 | 179.3 | 9.0 |
   | random keyword L=13 | 166.4 | 6.3 |
   | random keyword L=20 | 157.5 | 4.4 |
   | sticky L=8, a=0.19 | 188.7 | 11.1 |
   | sticky L=13, a=0.19 | 172.0 | 7.5 |

3. Per-page doublet dispersion (leaks concentrate on pages whose keyword has equal adjacent letters). Chi2 (df 54) against a homogeneous binomial reference of 53.9 +- 10.5: real 58.9 (z = 0.48); sticky controls give z = 2.6 to 3.4. This test has mild power.
4. D-IoC28 (the signature of English difference leakage): real 1.0012, z = 2.07 against null 1.0000 +- 0.0006. Sticky-keyword controls give 1.0048 to 1.0108 (z 8.5 to 19.1).
5. Doublet phase (i mod L) is not a usable leak. The skips randomise the key phase, and the chi2 of the phase histogram is 20.5 (df 12, p about 0.06).

**Verdict.** Excluded for any period up to about 20 that I tested (L = 5, 8, 13, 20). Only the control with L=20 is weak (z 4.4). Longer keywords, or a key derived from running text, are covered by the earlier lanes' lag scans, not here.

## Candidate 7: base-29 encoding of random bytes with a doublet-avoiding encoder (`s1`, `s7`)

**Construction.** i.i.d. base-29 digits d_i; if d_i equals c_{i-1}, the encoder rewrites it with probability 0.81 and leaves it alone with probability 0.19. This matches Dukotah's pinned soft rewrite (p_keep about 0.18).

**Predictions.**

- Rewrite to +1 gives D = 1 about 1.8 times the other D values, and D = 28 for "-1".
- A redraw encoder gives flat nonzero D, which is the chain's marginal.

**Real** (`s1`, `s7`): D=1 is 457 against an expected 457.7 (z = -0.03). D=28 is 430 (z = -1.32). Ratio D=1 to the mean of the other 26 values is 0.996. The fraction of would-be collisions moved to D = delta has these estimates:

| delta | f_delta |
|---|---|
| 1 | -0.002 +- 0.049 |
| 28 | -0.065 +- 0.049 |
| largest over all 28 deltas | 0.122 (delta = 9), consistent with chance |

A bump-type rewrite that explains the deficit needs f = 0.81, which is 17 standard errors above the measured value. Positive controls (12 syntheses): iid digits with bump +1 give D1/other 1.83 (z = +16.9 for D=1, chi2 311); lag-2 and lag-1 base with bump give 1.83-1.84. Redraw encoders give 0.99-1.00 and chi2 about 27. A fixed-point or multi-target rewrite (delta in {1,28}, {1,2}, {1,28,2,27}) gives total f of -0.07, 0.10 and 0.07, with standard errors 0.07 to 0.10.

**Byte-block packing.** If the digits were base-29 expansions of byte blocks (3 bytes into 5 digits, or 2 bytes into 4 digits), the leading digit would be missing high values. Per-phase chi2 for block lengths 2..64, aligned at page starts, gives a real maximum z = 3.96 (m=29), against a null maximum 4.53 +- 0.69. Positive controls: 73.5 at m=5 and 3879 at m=4. Excluded for page-aligned fixed-width blocks.

**Verdict.**

- A deterministic offset rewrite (bump +1, -1, or any single delta) is excluded at the 17 standard-error level.
- A redraw or delete rewrite is statistically identical to the chain, but then 81% of the would-be collisions (about 360 positions) carry noise, not text.
- The chain's EA-zero explanation fits the doublet rate without any tuning.

## Per-candidate verdict table

| # | candidate | verdict | strongest z |
|---|---|---|---|
| 1a | lag-2 chain, nonzero increments | excluded | lag-2 z = -0.38 against -15 predicted |
| 1b | lag-2 base + redraw rewrite | not excluded, indistinguishable from the chain | n/a |
| 1b+ | same, with +1 bump | excluded | f_1 = -0.002 +- 0.049, 17 se |
| 1b++ | same, with periodic keyword | excluded | z 0.49 against 24-76 in controls |
| 2B | prime-domain mod 109/110 + snap | excluded | LLR -581 to -11,304; IoC 1.10-1.25 |
| 2A1 | additive s = v(p) + k mod 29 | excluded | dbl z = -17.4 |
| 2A2 | multiplicative with prime residues | N or any common letter excluded; a=8 (NG) fits but is non-injective, so lossy | n/a |
| 3 | fixed Latin-square feedback | excluded (also per page) | 245 and 237 sigma; per page 32 |
| 4 | outer flat cipher after doublet-free q | excluded (independent keys) | -9.1 se vs min_x P_X; 4e: D-IoC 1.10 vs 1.001 |
| 5 | transposition after the chain | excluded for non-adjacency-preserving permutations | best -3.18 vs null -2.96 +- 0.38 |
| 5 | transposition before the chain | unfalsifiable | n/a |
| 6 | key-skip Vigenere, per-page keyword | excluded for L = 5..20 | -0.05 vs 4.4-12.3 in controls |
| 7 | base-29 + bump encoder | excluded | 17 se |
| 7 | base-29 + redraw/delete encoder | not excluded, identical to the chain; 81% of collisions would be noise | n/a |

## Leads

- **None that survive as decryptable.** The surviving statistically allowed constructions are the plain chain, the lag-2 or lag-L base with a redraw rewrite, and a chain applied to a transposed plaintext.
- **What each would need:**
  - Plain chain: a flat aperiodic keystream on the increments, already covered by prior lanes and the community oracle.
  - Lag-2 or lag-L base with a redraw rewrite: a keystream on the lag-L difference stream E_i = c_i - c_{i-L}. This is the one surface the community oracle (`verify_solution.py`, chain model) does not appear to cover. A periodic keyword on E is excluded here. A running-text or PRNG key on E, with unknown resynchronisation positions at the rewrite events, would need a candidate key text first.
  - Chain on a transposed plaintext: the key plus a transposition search at the plaintext level. No ciphertext test can narrow it.
- I did not run the oracle, because no keystream candidate exists.

## Files

`common.py`, `sim.py`: loader, encoders, plaintext generators.
`s1_lags_D.py`: lag profile, D histogram, rewrite controls (candidates 1, 7).
`s2_prime.py`: prime-value domain.
`s3_cond.py`: conditional IoC and Latin-square controls.
`s4_twolayer.py`: independent-key bound and two-layer simulations.
`s5_transpo.py`: reordering scan.
`s6_keyskip.py`: key-skip Vigenere.
`s7_bits.py`: rewrite-offset bound and byte-block phase test.
`s8_lagdiff.py`, `s8b.py`: periodic keywords on lag-L differences.
`eng_runes.npy`: transliterated English used for the difference spectrum.
Outputs: `s*_out.txt`.
