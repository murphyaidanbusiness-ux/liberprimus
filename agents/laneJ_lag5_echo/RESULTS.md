# laneJ_lag5_echo — within-word distance-5 echo: significance, mechanisms, attack

All scripts and raw outputs are in this directory (`core.py`, `s1_signif.py` -> `s1_out.txt`, `s2_mech.py` -> `s2_out.txt`/`s5_table.txt`, `s3_attack.py` -> `s3_out.txt`, `s3b_fairdict.py` -> `s3b_out.txt`, `s4_bylength.txt`, `s6_seam_vs_chainzero.txt`, `discord_hits*.txt`). Corpus: lpdata.unsolved() (sha 0233…1585), 12,956 runes, 2,896 words. English plaintext: War & Peace in runeglish (relikd `baseline-rune-words.txt`, 400k words), resampled to the LP's exact word-length sequence, plus the solved LP pages.

## 1. What the community already has (do not redo)

**Discord export** (`jaxonkuipers/cicada3301` discord.db, 109,917 messages). Nothing on the d5 echo itself. The only hits are links to aldegonde files by `.sltn` (2024-02, 2026-07) and mortlach's 2026-01 note on phase-aligned repeated bigrams in 54–55. The d5 discussion happens in the aldegonde repo (Oosterhof, who posts as `.sltn`).

**ZzNible** (FINDINGS.md). Same count as ours, 104/2105, Z = 3.75. Preregistered max-|Z| over d = 2..12 under a null that keeps word lengths, rune multiset and the doublet count: p = 0.0086. ZzNible explicitly declines any mechanism. NEGATIVE_RESULTS: the XY···XY digraph sub-pattern is *not* significant after full look-elsewhere correction.

**micheloosterhof/aldegonde `hypotheses/`** (180 files, 84 mention d5). The current state:
- *Observation* (`within-word-d5-coincidence.md`). Their tokenisation has 32 extra boundaries: 102/2073, word-length permutation null p = 0.0014, Bonferroni ×7 → 0.006, family-blind over a 124-cell battery → 0.020. The echo is uniform over start position (χ² p = 0.77), so there is no drift. d10 is unmeasurable (88 pairs, 0.76 sd separation). d6 is suppressed (p = 0.016), read as the "phase-1 image" of the d1 suppression. The rune S carries about 22% of the echo.
- *Same-alphabet leak* (`d5-partial-alphabet-leak.md`). With d3/d4 as controls, one-alphabet-per-word is **refuted** (φ3 = 0.13 ± 0.14), so a step permutation g of order exactly 5 is inferred. φ5 is 0.64–0.71, consistent with full leak. Uniform dilution is refuted because d1 lies below its floor.
- *Additive per-word 5-periodic key* (`within-word-key-sharing.md`): **disproved**, 3.6σ. The within-word lag-5 delta histogram is flat off zero, so the leak is equality-only and not Vigenère-type. `lag5-back-reference.md` (literal copying) is unfalsifiable.
- *Mechanism candidates.* The first is `length-clocked-walk.md`: c = base_w(g^(j mod 5)(p)), with base_(w+1) = base_w ∘ g^((L−1) mod 5) ∘ σ and a ~200-bit key. The second is `doublet-dodge-walk.md`: the clock skips on a would-be repeat, which suppresses doublets and partially breaks the d5 alignment with one rule. That fit is "fitting, not predicting": d3w, d6w and the seam land together in only 11/320 draws, the rate independence predicts. Also there: `quagmire-odometer.md` (unresolved) and `pure-quagmire-word-restart.md` (restart disproved). `hill-cipher-per-word`, `mobius-order5`, word-length-context keys (`word-length-keystream-and-boundaries.md` §A) and a uniform-drift q are all disproved.
- *Attack budget* (`crib-budget-for-g.md`). Within-word collisions at known plaintext constrain g base-free at about 1 constraint per 10 crib runes. g needs about 300 known words, and the titles supply 29. `g-can-be-filtered-not-found.md` is negative.

My work below extends this in four ways. I add a global-shuffle family-wise null and a section-drop / length / transcription robustness test. I simulate the mechanisms the brief lists (mostly absent from aldegonde) against the full within/across lag-1..10 profile, using the chain cipher and an additive key as bases. I add a dictionary attack that directly tests the additive per-word 5-key. I add the D-stream test of chain + 5-key.

## 2. Significance, corrected for multiple testing (`s1_out.txt`)

Observed profile (rate, z vs 1/29):

| lag | within (n) | z | across (n) | z |
|---|---|---|---|---|
| 1 | 0.0063 (10060) | −15.5 | 0.0079 (2895) | −7.8 |
| 2 | 0.0348 (7247) | +0.1 | 0.0331 | −0.6 |
| 3 | 0.0371 (4882) | +1.0 | 0.0320 | −1.2 |
| 4 | 0.0405 (3237) | +1.9 | 0.0338 | −0.4 |
| **5** | **0.0494 (2105)** | **+3.75** | 0.0346 (10846) | +0.05 |
| 6 | 0.0248 (1290) | −1.9 | 0.0363 | +1.1 |
| 7 | 0.0410 (731) | +1.0 | 0.0345 | 0.0 |
| 8 | 0.0258 (388) | −0.9 | 0.0341 | −0.3 |
| 9–12 | 5/201, 2/92, 1/35, 0/10 | ≤ −0.2 | flat except lag 11 across −2.9 | |

Family-wise p for "within lag 5 = 3.75":

| null (2000 draws each) | single-cell p | family-wise p |
|---|---|---|
| A: global rune shuffle, word structure kept, max upward z over all **24 cells** | 0.0010 | **0.011** (null max: median 1.96, 95% 3.11) |
| A, 12 within cells only | | 0.009 |
| B: rune stream fixed (keeps doublet suppression), word lengths permuted within each of the 9 sections; lag-5 = 104 vs 77.8 ± 7.8, z = +3.36 | < 0.0005 | **0.016** (12 within cells), **0.019** (24 cells) |

**Corrected p ≈ 0.01–0.02.** This agrees with ZzNible's 0.0086 and aldegonde's 0.006–0.020. It is real at about 2.3–2.6σ after correction, not 3.75σ. No other cell exceeds +1.9.

Robustness:
- **Drop one section** (9 sections): z ranges +3.02 to +4.09. Sections 2 and 3 are the strongest (alone z = +2.56, +2.50); section 1 alone is −0.5.
- **Word length**:

  | lengths | matches | rate | z |
  |---|---|---|---|
  | 6–9 | 65/1468 | 4.43% | +2.06 |
  | 10–14 | 39/637 | 6.12% | +3.70 |
  | 8–14 | 76/1417 | 5.36% | +3.95 |
  | 6 alone | 9/256 | 3.5% | 0.1 |

  The heterogeneity over L against W&P's per-length plaintext lag-5 rate with a common leak fraction is not significant: χ² = 10.6 on 9 cells, Monte-Carlo P = 0.22. L = 10 alone is z = +2.8 above the common fit (20/260), which is not significant after looking at 9 cells.
- **Transcriptions.** relikd/LiberPrayground pages have identical runes and identical boundaries, so the result is the same 104/2105. aldegonde `page0-58.txt` has identical runes plus 32 recovered line-initial boundaries: 102/2073, z = +3.67. cicada-library's `liber_primus.txt` uses the same format and source as our krisyotam file.
- **Leak fraction.** Using W&P per-length full-leak rates on the LP length mix: 120.8 expected under full leak, 104 observed, so φ = 0.65 (common-φ ML fit 0.53).
- **Lag 10.** Plaintext lag-10 is 4.52%. A φ = 0.6 echo predicts 3.8 matches in 92 pairs, against 3.2 under flat and 2 observed. Lag 10 cannot discriminate (as aldegonde also says).
- **Increments D** (chain-model object). Within-word D lag-5 is 55/1290 = 4.26%, z = +1.34 vs 1/28. There is no D echo.

## 3. Mechanism simulations (`s2_mech.py`, 30 replicates × 12,956 runes each, LP word-length sequence, W&P plaintext)

"Chain" means c_i = c_(i−1) + s_i, with s_i = 0 for EA and otherwise 1 + ((p_i + k_i) mod 28). Column guide:
- W = within-word coincidence rate; X = across-word.
- The z columns compare the real counts to the model rate; |z| > 3 means the model is excluded on that cell.
- "deltaT" is the projection of the within-word lag-5 nonzero-difference histogram onto the plaintext difference profile. It is N(0,1) for an equality-only leak and large for an additive leak. The real value is 0.53.
- "Dl5" is the within-word D lag-5 rate (real 0.0426).

| mechanism | W1 | W3 | W4 | **W5** | W6 | W10 | X1 | X5 | coset z | deltaT | Dl5 | z(W1) | **z(W5)** | z(X1) | z(X5) | z(Dl5) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **REAL** | .0063 | .0371 | .0405 | **.0494** | .0248 | .0217 | .0079 | .0346 | −0.1 | 0.53 | .0426 | | | | | | |
| plaintext | .0365 | .0537 | .0510 | .0568 | .0628 | .0476 | .0387 | .0601 | 215 | 13.3 | | −16 | −1.5 | −8.6 | −11 | | |
| ref chain, flat k | .0071 | .0349 | .0335 | .0345 | .0357 | .0335 | **.0012** | .0341 | 0.4 | 0.0 | .0354 | −1.0 | **+3.8** | **+10.7** | 0.3 | +1.4 | no echo; seam doublets 7× too few |
| a1 chain, k = H(word length) | .0072 | .0376 | .0339 | .0345 | .0366 | .0364 | .0014 | .0341 | 0.0 | 0.3 | .0697 | −1.1 | +3.7 | +9.6 | 0.3 | −3.8 | excluded |
| a2 chain, k = H(len,pos) | .0069 | .0351 | .0345 | .0350 | .0356 | .0407 | .0012 | .0343 | 0.2 | −0.1 | .0345 | −0.8 | +3.6 | +10.7 | 0.2 | +1.6 | no echo |
| a3 Vig, keyword restarts each word | .0354 | .0344 | .0356 | .0368 | .0310 | .0328 | .0362 | .0417 | **572** | 0.5 | | −16 | +3.1 | −8.1 | −3.7 | | excluded (position cosets) |
| a4 Vig, key period = current word length | .0364 | .0352 | .0342 | .0337 | .0339 | .0371 | .0355 | .0384 | **74** | 0.3 | | −16 | +4.0 | −8.0 | −2.1 | | excluded (cosets, no echo) |
| a5 chain, key period = word length | .0070 | .0334 | .0357 | .0337 | .0353 | .0299 | .0012 | .0345 | 0.2 | 0.0 | .0359 | −0.9 | +4.0 | +10.4 | 0.1 | +1.3 | no echo |
| b chain restarts at offset 2 in word | .0137 | .0346 | .0350 | .0342 | .0340 | .0364 | .0014 | .0343 | 3.4 | −0.2 | .0352 | −6.4 | +3.8 | +9.6 | 0.2 | +1.5 | excluded |
| **c Vig, per-word 5-key, random phase** | .0355 | .0344 | .0350 | **.0587** | .0332 | .0321 | .0349 | .0342 | 0.0 | **13.5** | .0382 | −16 | −1.8 | −7.9 | 0.2 | +0.8 | echo YES, but additive leak (deltaT) and no lag-1 suppression |
| c chain, per-word 5-key, random phase | .0070 | .0341 | .0337 | .0353 | .0343 | .0339 | .0013 | .0350 | 0.3 | 0.1 | **.0710** | −0.9 | +3.5 | +9.7 | −0.3 | **−4.0** | excluded: no C echo, predicted D echo absent |
| c 5 independent random alphabets/word, random phase | .0347 | .0346 | .0344 | **.0577** | .0355 | .0331 | .0345 | .0345 | 0.1 | −0.2 | .0355 | −16 | −1.6 | −7.8 | 0.1 | +1.4 | echo shape right (equality-only); needs a doublet rule |
| c walk base_w∘g^clock (order-5 g, 4 fixed pts), no dodge | .0398 | .0340 | .0382 | .0576 | .0354 | .0360 | .0334 | .0346 | 0.0 | −0.1 | .0353 | −17 | −1.6 | −7.6 | 0.0 | +1.4 | lag-1 fails |
| **c walk + doublet-dodge (Oosterhof)** | **.0057** | .0388 | .0378 | **.0543** | .0353 | .0382 | **.0048** | .0348 | 0.1 | 0.2 | .0376 | **+0.7** | **−1.0** | +2.4 | −0.1 | +0.9 | **only model matching every key cell**; W6 dip not reproduced (z ≈ −2) |
| d in-word 5-col transposition + chain | .0068 | .0351 | .0352 | .0352 | .0353 | .0335 | .0012 | .0346 | −0.1 | 0.0 | .0365 | −0.7 | +3.5 | +10.7 | 0.0 | +1.2 | no echo (chain hides plaintext) |
| d in-word 5-col transp. + 5 alphabets/word | .0343 | .0340 | .0341 | .0527 | .0335 | **.0911** | .0346 | .0341 | 0.2 | 0.1 | | −16 | −0.7 | −7.8 | 0.3 | | transposition adds nothing |
| e 5-col route transposition (500-rune blocks) + chain | .0057 | .0341 | .0347 | .0358 | .0345 | .0281 | .0053 | .0342 | 0.0 | 0.1 | .0348 | +0.7 | +3.4 | +1.9 | 0.2 | +1.5 | no echo |
| e route transp. + per-word 5-key Vig | .0337 | .0342 | .0350 | .0621 | .0348 | .0527 | .0341 | .0344 | 0.2 | 4.3 | | −15 | −2.4 | −7.8 | 0.1 | | excluded |
| f lagged Fibonacci k = k(−1) + k(−5), Vig / chain | .0345/.0070 | | | .0345/.0345 | | | .0333/.0012 | .0344 | | | | | +3.8 | | 0.1 | | no echo at all |
| f k = k(−5) + t (t sparse, 60%), Vig | .0346 | .0346 | .0343 | .0436 | .0329 | .0415 | .0344 | **.0443** | −0.1 | 4.9 | | −16 | +1.3 | −7.8 | **−4.9** | | excluded: echo leaks across words |
| **g skip-on-repeat Vig, 5-key/word, random phase** | .0000 | .0346 | .0362 | **.0548** | .0318 | .0440 | .0000 | .0343 | −0.1 | **11.6** | .0374 | (0 doublets) | −1.1 | | 0.2 | +1.0 | echo + suppression, but additive leak (deltaT) |

Partial-leak calibration of the delta test (`s3_out.txt` §2, 40 draws each). For an additive per-word 5-key (with or without skip) diluted to the observed echo size:

| fraction of 5-periodic words q | skip | W5 | predicted deltaT |
|---|---|---|---|
| 0.6 | no | 4.90% | 7.8 ± 1.1 |
| 0.6 | yes | 4.55% | 6.7 ± 1.3 |
| 0.5 | yes | 4.38% | 5.8 ± 1.1 |

The real deltaT is 0.53, below every draw: P = 0/40 at every q, about 5–6σ. **Additive (Vigenère-type) per-word 5-keys, (c) and (g), are excluded at about 5σ, whatever the dilution.** This strengthens aldegonde's 3.6σ result.

Structural conclusions:
1. **No chain-base mechanism can make this echo.** Under any ciphertext-feedback chain, a raw-rune coincidence at lag 5 means that five consecutive increments sum to 0 mod 29. That is not an equality of p_i and p_(i+5). Every chain variant gives W5 = 3.45–3.59%, so the real 4.94% sits at z = +3.4 to +4.0 against all of them. A per-word 5-periodic key under a chain moves the echo into D (predicted 7.1%), but D lag-5 is 4.26%, z = −4.0 against that prediction.
2. **The echo is an equality-only same-alphabet leak.** Positions i and i+5 in a word are enciphered by the same mixed bijection, with unrelated bijections across the word boundary. The only simulated family that also produces the lag-1 suppression *inside and across* words is the mixed walk with a skip-on-repeat (doublet-dodge). That is brief family (b), "flat cipher + advance on repeat", with period-5 mixed alphabets. It is not family (a), the chain.
3. **Side finding against the campaign's chain-with-EA-zero model** (`s6_seam_vs_chainzero.txt`). In that model a seam doublet requires a word beginning with the zero letter. EA is about 90% word-medial: W&P gives P(EA | word-initial) = 0.13%, which predicts 3.7 seam doublets against **23 observed** (P ≈ 1e-11). The solved LP pages give 0.41% from only about 3 tokens, which predicts 11.8 (P = 0.0025). No single plaintext rune fits both the within rate (0.63%) and the seam rate (0.79%); G is the best and is still ΔlogL = −16. aldegonde's `doublet-marker-rune-ea.md` reaches the same refutation from the position profile. A chain cipher survives only if its zero increment is key-driven, not plaintext-driven.

## 4. Attack

**For (c)/(g), additive per-word 5-key with random phase.** The lag-5 differences inside a word are key-free: c_(i+5) − c_i = p_(i+5) − p_i. A word of length L therefore gives L−5 constraints, which is unique against a dictionary for L ≥ 10 (29^5 ≫ 44k ten-rune words). I indexed the relikd dictionaries (L = 9..14, 11k–52k words each) plus W&P plus the solved-page words by signature. I ran three variants: the Vigenère form, the skip form (which loses a few constraints), and the chain/D form ((D−1) differences mod 28). Each was checked against a within-word rune-shuffle null (100 draws) and planted controls (`s3_out.txt`, `s3b_out.txt`):

| run | words | hits | null | planted q = 1 | planted q = 0.6 |
|---|---|---|---|---|---|
| Vig, L ≥ 9 | 187 | **5** | 5.2 ± 2.6 | 187 | 109 (z = +56) |
| Vig, L ≥ 10 | 109 | **0** | 0.2 ± 0.4 | 109 | 62 |
| Vig, L ≥ 9, relikd-only dictionary (W&P coverage 0.89–0.96, solved-LP long words 0.97) | 187 | **5** | 5.1 ± 2.0 | 162 | 102 (z = +53) |
| chain/D form, L ≥ 10 | 109 | **5** | 2.1 ± 1.5 (max 7), z = +1.9; all hits are zero-frequency dictionary words | 106 | 76 |

The attack is feasible and powerful: it would recover about 60% of the long words if (c)/(g) were true. On the real text it returns exactly the null. **Verdict: (c) and (g) are dead three ways** (deltaT, the dictionary attack, and lag-1 for the non-skip form).

**For the surviving family**, mixed alphabets with period 5 inside words plus a dodge (the aldegonde walk), the echo carries only equality information. Each within-word lag-5 pair yields at most about 1 bit, and only about 104 informative coincidences exist in the book. This gives no per-word dictionary handle: a 10-rune word has 5 equality bits, against about 15 bits needed to pick one of 44k words. The key is (base_0, g, σ), about 200 bits, and must be searched globally with a language model. The community has costed that search (about 300 known words needed for g) and run filters on it without success. I did not find a cheaper route. **No attack is run; nothing was sent to the oracle** because there is no candidate keystream.

## Verdict

- **The echo is real but modest.** Family-wise corrected p = 0.011 (global shuffle, 24 cells) to 0.019 (doublet-preserving boundary null). It is robust to dropping any section, to both tokenisations, and to the transcription source, and it is concentrated in words of 8 or more runes.
- **Mechanisms (a), (b), (d), (e), (f)** fail: no echo, or position-coset structure, or an echo across words.
- **Mechanisms (c)/(g) with additive keys** reproduce the C-profile but are excluded by the delta-histogram test (~5σ) and by a planted-controlled dictionary attack (0 real hits against 62 expected for L ≥ 10).
- **Chain-base versions** of every mechanism produce no raw-rune echo, and their D-echo prediction fails (z = −4.0).
- **The only consistent family** is an equality-only per-word period-5 mixed-alphabet cipher with a skip-on-repeat rule (Oosterhof's doublet-dodge walk). If the echo is genuine, it is **evidence against the campaign's chain family (a)** and for family (b). The chain's EA-zero variant is independently contradicted by the seam-doublet rate (23 observed against 3.7–11.8 predicted).
- **No decryption.** The surviving family offers no per-word attack from the echo; it needs a global search over g and σ with a language model.
