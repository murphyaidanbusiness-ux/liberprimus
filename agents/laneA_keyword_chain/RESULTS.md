# Lane A: keyword (dictionary) attack on the per-page chain-cipher family. Result: NULL

All code and outputs are in this directory. Corpus sha256 = 023312066df4…af1585 (verified on every load).
Machine: 4 cores, shared with other lanes for most of the run.

## 0. Ledger check (what was new)
- dukotah ran about 620 Vigenère keywords under a skip-aware beam (Round XVIII). It also ran 58 themed keys through a no-repeat
  combiner (LP1-H). Both act on **raw runes**. leo ran **integer sequences** on chain increments (tests5, with 14 bijections).
- **Not previously run:** a dictionary of **362,700 word keys** on the chain-increment stream D_i = c_i − c_{i−1}. It covered the Z28-additive
  family (14 bijections) and the GF(29)-multiplicative family, each key restarting on every page or on every section. Families 1 and 2
  below are new. Family 3 is a control that repeats dukotah's ground with a list about 580× larger.

## 1. What was tested
**Keys (`keys.txt`, built by `build_keys.py`).** dwyl `words_alpha` (370,105 words) transliterated with Cicada's rules
(K,Q→C; QU→CW; V→U; Z→S; greedy TH EO NG OE AE IA IO→IA EA), kept at 3..16 runes: 360,518 unique keys.
Cicada vocabulary: 1,343 keys. This includes every word of the solved LP sections and koans, the 2012–13 puzzle texts and PGP texts,
dukotah `thematic.txt` and `words_expanded.txt`, section titles as single words and as joined phrases (ANINSTRUCTION, THELOSSOFDIVINITY, …),
the lore words (DIVINITY, CIRCUMFERENCE, INSTAR, EMERGENCE, PILGRIM, PRIMES, TOTIENT, KOAN, MOBIUS, INTUS, …), and every word containing C
also respelled with C→F (the FIRFUMFERENFE pun). Finally, all 1- and 2-rune keys were included exhaustively (839).
**Total: 362,700 keys.**

**Units.** (a) Each of the 55 pages, with the key restarting at the page start. (b) Each of the 17 sections (`&` chapters), with the key
restarting at the section start and the chain continuous across pages. Sections under 60 runes were not scored (2 of 17).

**Models.** D_0 is taken from the previous page's last rune (from 0 for page 0). "align0" puts key letter 0 on D_0. "align1" drops the first
rune and puts key letter 0 on D_1. "EAconsumes" means a zero increment advances the key; "EAskips" means it does not.
- **F1, Z28 additive.** For D≠0, u = τ(D) ∈ Z28 and p = (u ∓ k_j) mod 28, which is a rune index 0..27. D=0 decodes as EA.
  There are 14 choices of τ: D−1, 28−D (the reversed / Atbash ring), and log_g D for each of the 12 primitive roots of 29.
  k = rune index mod 28. With 2 signs, 2 EA conventions and 2 alignments, that is **112 variants**.
  (The EAconsumes variant is skipped on units that have no zero increment, because there it gives the same output as EAskips.)
- **F2, GF(29) multiplicative.** x = D·k⁻¹ or x = D·k, and p = x − 1 (x = 0 gives EA). k = idx+1, or the prime value mod 29;
  key letters whose value is 0 are dropped. With 2 EA conventions and 2 alignments, that is **16 variants**.
- **F3, control.** On raw runes: Vigenère p=c−k, Beaufort p=k−c, and variant p=c+k (mod 29). Also the skip rule for Vigenère and for
  Beaufort ("advance the key if the output would repeat the previous rune"), decoded greedily with a 5-rune quadgram lookahead
  wherever the decode is ambiguous. That is **5 variants**.

**Trial counts (page-unit decryptions).** F1: 1.97e9 real pages + 3.9e10 null. F2: about 3.2e8 real + 6.4e9 null. F3: about 1.0e8 real + 2.0e9 null.
Sections were run the same way.

**Scoring.** Each decryption gets two scores. The first is the normalised IoC on 29 symbols (1.0 random, 1.70 English runes).
The second is the mean log10 of a rune-domain 4-gram model (`quad29.f32`), built from 6.0M runes of English (Melville, Emerson, Plato,
Poe, Homer, Aristotle, Bacon, KJV) transliterated with the same rules. On this model, solved Cicada text scores −4.22 and noise scores −7.49 ± 0.075 at
260 runes. The top candidates were also rescored with the dukotah letter-quadgram scorer (column "dukQ"; English is about −4.5,
noise about −7).

**Speed.** The kernel is C with OpenMP (`kc2.c`). Rune-steps are the decrypt plus score of one output rune:
2.9e8 /s on one core and 1.2–1.5e9 /s on 4 idle cores (0.35–0.45e9 /s under contention).
F1 over all pages in full takes 306 s when the machine is idle. To make the 20-shuffle F1 null affordable, `kc3.c` adds a **stage-1 prune**.
The first 64 output runes must reach a mean 4-gram score of at least −7.0 (0.35% of candidates pass). Only survivors get a full score.
The real F1 pages, the F1 null and all section runs used this same pruned procedure. F1 pages were also run unpruned (see §3).

## 2. Positive controls (`gen_ctrl.py`, `analyze_ctrl.py`, `ctrl_report.txt`)
The plaintext was a 260-rune window of the solved Koan page (SOLVED-PAGES.json 06.jpg), chosen to contain 3 EA. Each control used a
random dictionary key, and the attack ran over the full 362,700-key list.
| family / variant | planted key | rank by quad | rank by IoC | planted q | best wrong q | z vs candidate distribution |
|---|---|---|---|---|---|---|
| F1 τ0 −, EAskips, align0 | AROMATOPHOR | 1 | 1 | −4.220 | −5.546 | 44.8 |
| F1 τ0 −, EAskips, align1 | SISTERISE | 1 | 1 | −4.220 | −5.197 | 43.3 |
| F1 τ0 +, EAconsumes, align0 | PEPLOS | 1 | 1 | −4.220 | −5.687 | 41.7 |
| F1 τ5 −, EAconsumes, align1 | CERMIS | 1 | 1 | −4.220 | −5.465 | 42.0 |
| F1 τ1 +, EAskips, align0 | AURENE | 1 | 1 | −4.220 | −5.574 | 38.5 |
| F1 τ12 +, EAconsumes, align0 | INFUSIANISM | 1 | 1 | −4.220 | −4.931 | 43.1 |
| F2 (4 variants, both conventions) | UNSHOWY, STELLA, FORCED, EMBITTERING | 1 | 1 | −4.220 | ≤ −5.0* | 32–40 |
| F3 vig / beau / varbeau / skip-vig / skip-beau | 5 keys | 1 | 1 | −4.220 | −5.0 … −6.5 | 37–40 |

\* For FORCED the "best wrong" key decodes identically. It is a key that differs only by a letter whose value is 0, which the model drops.
The pruned F1 kernel recovers all 6 F1 controls at rank 1 as well (z 32–39).

## 3. Results against the null
Null method: 20 shuffles per unit. For F1 and F2 the increments D are shuffled, which keeps the doublet count. For F3 the raw runes are shuffled.
The identical search with the same key list is run on each shuffle. z = (real best − mean of the null bests) / sd of the null bests.
| run | units | best quad on any unit | z_q mean / sd / max | units > null max (quad) | z_IoC mean / max | units > null max (IoC) |
|---|---|---|---|---|---|---|
| F1 pages (pruned, own-page null) | 55 | −6.415 | 0.04 / 1.16 / 4.68 | 4 (2.6 expected) | 0.03 / 2.65 | 2 |
| F1 pages, unpruned, length-matched null† | 55 | −6.415 | 0.23 / 1.62 / 4.45 | 7 | 0.31 / 5.27† | 4 |
| F2 pages | 55 | −6.530 | 0.12 / 1.36 / 3.59 | 3 | 0.20 / 3.50 | 4 |
| F3 pages | 55 | −6.451 | −0.06 / 0.84 / 2.61 | 1 | 0.10 / 3.90 | 4 |
| F1 sections (pruned) | 15 | −6.488 | 0.08 / 1.05 / 2.31 | 0 (0.7 expected) | −0.07 / 2.11 | 0 |
| F2 sections (pruned) | 15 | −6.634 | 0.36 / 1.46 / 4.74 | 1 | 0.83 / 3.74 | 3 |
| F3 sections (pruned) | 15 | −6.535 | 0.18 / 0.94 / 1.78 | 0 | 0.39 / 2.58 | 0 |

† The unpruned F1 null was 20 shuffles of 7 pages spanning the length range (66…277 runes); each real page was matched to the
nearest length. That null is **not valid for IoC**. For F1, the output IoC depends on the page's own increment histogram, which a shuffle keeps.
Page 13's histogram is somewhat uneven (z 2.85 against a uniform multinomial; max over 55 pages is 3.3, p ≈ 0.2 after correction), so its IoC "z 5.27" is an artifact
of borrowing another page's null. The pruned run with each page's own null is the valid one.

**Per key length.** For each (unit, key length 1..16, 17+) cell, the best real score was compared with the best null score for that length.
The cells where the real score beat all 20 nulls were F1 53/880, F2 44/935 and F3 58/935; chance alone gives 42 / 44.5 / 44.5.
The largest cell z values are 4.9–6.7. They come from estimating the sd from 20 draws of a skewed maximum. Every one of those cells
has an absolute score of −6.9 to −7.0, which is noise.

**Best candidates (first 120 runes, transliterated).** None is English. Every best is −6.4 or lower, against −4.2 for Cicada English.
- F1 p47 GEMEINDE (τ5, p=u−k, EAconsumes, align1): q −6.931 vs null max −6.978, z 4.68, dukQ −6.87:
  `BUYCNXRMINGTILMMEPGARJNSRMIWEOOEUAJJLAETHTSTOONEUCOBROYDUNGHOSNRWWWSORBEFNNWOETHRLNGTHPSHGEOFLDAWEOHTFDIAAESPEAROEEOGUIA`
- F2 p32 INTONING (k=idx+1, x=D/k, EAskips, align0): q −6.700 vs null max −6.730, z 3.59:
  `MOXNAIEALDBELISTAEIARMHAPPDFEEOOEEAGGBBCLTTHORIGNOENCSUSHECOASIUENOELTSIFREFTCNGBBRUCYPLEDBWETHOEEOBBLXJOEIMRSRMXEOIAUEA`
- F2 section 14 (pp40–49, 2,474 runes) CICCSHAW: q −7.349 vs null max −7.363, z 4.74:
  `TETHROUCNGIAHHLLHETEIASRELBEOIDSTHHOOAWHFDYGREWPFHJCNUROEYOEEDCFGTHOEDLNXICATMORLRJPRRTHOEHUWDGNEOXSPGTTCLEXIATOELHIAEOD`
- F3 p1 MUDS (skip-rule Beaufort): q −6.972, z 2.61:
  `ALRFISUJEDHANGHEAMIASFTHOAEMPNGYGEOAEEADECLWOENUOEOMTHMEOYJSAEPBSMJNGLWOEHHAIAIAEYAEGAHNOOEDMAHLEALIAYRESXMOMINGTHETUUPB`

**Oracle.** `verify_solution.py --selftest` passes. For submission, the best F1 key on each page was turned into an equivalent additive keystream
(k = c − p, 12,956 symbols, `oracle_keystream_f1best.txt`). The oracle verdict is **FAIL**: best page −7.019 against a bar of −5.5,
0 pages passing, "> 1.5 short: noise" (`oracle_f1best.json`).

## 4. Page-51 period-28 anomaly (`p51.py`, `p28all.py`, `p51b.py`, `p51c.py`, `p51ctrl.py`, `p51d.py`)
- The anomaly reproduces and is really a **period-7** structure, with 14 and 28 inheriting it. Coset IoC on raw runes with 200 shuffles:
  L=7 1.259 (null 0.964 ± 0.069, z 4.30), L=14 1.315 (z 3.37), L=28 1.559 (null max 1.513, z 3.76).
  On increments: L=7 z 1.61, L=14 z 2.74, L=28 1.578 (null max 1.383, z 3.61).
  Raw kappa at lags 7, 14, 21, 28, 35, 56 and 77 is 0.041–0.072, against 0.0345 for random text. The second half of the page carries more of it (p 0.03 vs 0.09).
- **Look-elsewhere.** Over 100,000 shuffles, p = 1.5e-4 for L=7 raw. The scan covered 55 pages × 39 periods (2..40) × 2 streams.
  Bonferroni on raw alone gives p ≤ 0.32. Page 51 is the top page at L=7, 14 and 28 (raw), but the per-page z values for L=28
  across all 55 pages average 0.06 with sd 1.18, and page 5 also reaches 3.44. Neighbouring pages 48–53 show nothing at L=7 (z −0.3 … 1.4).
  **Not significant after correction.**
- **Is it key-like?** I fitted a free period-L key for L = 7, 14, 28 using a per-coset unigram start plus quadgram coordinate ascent with 12 restarts.
  The models were Vigenère, Beaufort, the skip-rule pair, GF(29) multiplicative, and all 14 F1 bijections.
  *Control:* the same climber recovers a planted period-28 τ1 chain key on 263 runes of the Koan exactly (28/28 letters, −4.29),
  and a period-7 key likewise (7/7).
  *Page 51:* the best of all 19 models is −6.86 at L=7, −6.46 at L=14 and −6.01 at L=28. None comes near English.
  At L=28, τ7 and τ1 beat the shuffle nulls by about 4 sd. That is expected, because the shuffles destroy the coset concentration the
  climber feeds on, and the decrypts are still gibberish.
  Page 51 also has only 1 doublet against about 9 expected under a raw additive period-7 key, so a raw periodic key is excluded independently.
  **Verdict: the structure is not a periodic key under any tested model. It is most likely a selection effect.**

## 5. Verdicts
- **F1 (Z28 additive chain, 14 bijections, word keys, per page or per section): NULL.** Controls are recovered at z ≈ 40. On the real
  text no unit comes within 2 log10-units of English, and the count of units beating the null maximum is at chance.
- **F2 (GF(29) multiplicative chain, idx+1 or prime keys, per page or per section): NULL**, on the same evidence.
- **F3 (Vigenère, Beaufort and skip-rule on raw runes): NULL.** This confirms the fingerprint exclusion with a key list 580× larger than dukotah's.
- **Scope limits.** The key restarts only at a page or section start; mid-page restarts and key rotations are not covered.
  F1 key values are taken mod 28, so F and EA collide. The language model is English only.
  The skip-rule decoder is greedy with lookahead, not a full beam. A key that continues across a page boundary is covered only by the section runs.
  The 20-shuffle nulls estimate z from small samples, so judge by the exceedance counts and the absolute scores, not by single z values.

## Files
`build_keys.py`, `build_lm.py`, `common.py`, `ciph.py` (reference encrypt/decrypt), `kc2.c`/`kc3.c` (kernels), `gen_units.py`,
`gen_ctrl.py`, `analyze.py` → `analyze.out` and `summary.json`, `res_*.tsv` (top-30 by quad and by IoC for every unit,
per-length bests, stats), `run_all2.sh`/`run_all3.sh`, page-51 outputs `p51*.out` and `p28all.out`, and the oracle files.
