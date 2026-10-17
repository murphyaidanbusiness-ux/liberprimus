# laneL_keyword_walk: exhaustive keyword-built corner of Oosterhof's doublet-dodge walk

Everything lives in `SCRATCH/agents/laneL_keyword_walk/`. The corpus is `lpdata.unsolved()`, sha 0233…1585. **Verdict: no solve.** The real page 0 gives exactly the null result in every mode, and nothing went to the oracle as a beating candidate.

## 0. Model and verified implementation

The model is Oosterhof's walk, as lane K extracted it:

- c_j = base_w[g^(clock mod 5)(p_j)]
- If the emission equals the previous cipher rune, the clock advances once more and the rune is recomputed. This also applies across word gaps.
- The clock is global.
- After each word, base_{w+1} = base_w ∘ g^((clock−1) mod 5) ∘ σ.

**Checks of the implementation.**
- `common.enc_walk` is identical to lane K's `kcore.enc_walk` and to aldegonde's `experiments/doublet_dodge_walk.encipher`. The aldegonde function was loaded through `ast`, because its module imports scipy. The check covered 20 random keys × 200 words (`verify_aldegonde.py`, `runs/verify_out.txt`).
- The C beam decoder `kwdec` round-trips 262/262 runes on the plant. On 3,000-rune plants it scores 0.9993–1.0000 in all three modes. The residue is the model's intrinsic ambiguity: a plaintext doublet and a skip can produce the same cipher.

**Decryption.** The decoder only ever needs binv_w = base_w⁻¹, updated as binv_{w+1} = σ⁻¹ ∘ g^(−e_w) ∘ binv_w. At each rune there are two readings:
- N: p = g^(−t)(binv(c)).
- D, a skip: p = g^(−(t+1))(binv(c)).

A useful fact for fast pruning: **D is valid exactly when the N-reading repeats the previous plaintext rune.** For the rune that opens a new word, it is valid exactly when g⁻¹(binv(c)) = binv(c_prev).

**A further exact consequence (`runs/doublet_fixedpoint.txt`).** Every cipher doublet forces the second plaintext rune to be a fixed point of g. Inside a word it is moreover a plaintext doublet of that fixed rune: in plants, 260 of 260 cipher doublets showed this.

The LP has 86 doublets, 63 of them inside words. So under this model the LP's 63 within-word doublets must all be doubled letters drawn from g's 4 fixed runes, when g has 4 fixed points. That works as a free verifier of about 2.9 bits per doublet. It is why every page-0 candidate dies at a later body doublet (runes 122, 207, 456, …) when decrypted across the whole body (`runs/body_out.txt`).

## 1. Construction rules (from aldegonde) and the widened enumeration

**Oosterhof's 38-bit pricing** (`hypotheses/how-big-is-the-key-really.md`, `experiments/how_big_is_the_key_really.py`):

- **g**, called `structured_g(fixed)`: fix 4 runes and list the other 25 in rune order. Then g[rest[i]] = rest[(i+5) mod 25], that is, "step by five". This gives C(29,4) = 23,751 permutations (14.5 bits).
- **σ and base_0**, called `keyword_alphabet(word)` in `is_the_key_keyword_built.py`: the keyword runes, de-duplicated, followed by the remaining runes in rune order. He used 3,518 prose word types with all-distinct runes and length 3–12 (11.8 bits each).
- Total 38 bits, about 2.9e11 keys. **He never ran it.**

**What was enumerated here** (`prep.py`, `prep_out.txt`):

**Keywords.**
- Cicada vocabulary: 1,343 words, from lane A's `keys.txt` with src=1.
- Google top-20,000 English (first20hours `20k.txt`), transliterated aldegonde-style: ING→NG, IO→IA, K/Q→C, V→U, Z→S.
- Together that is 20,645 distinct rune words and 18,523 distinct de-duplicated sequences. Repeated runes are dropped, so words with repeats are allowed.

**A, the alphabets** (base_0 and σ): **220,280 distinct permutations.** For each keyword:
- the six rules of aldegonde `keyword_exhaustion.alphabets` plus reversals:
  - R1: keyword, then the rest in rune order. This is the same as prime-value order, because the Gematria primes increase with the index.
  - R2: keyword, then the rest in Atbash (reverse) order.
  - R3: keyword, then the rest continuing cyclically after the last keyword rune.
  - R4: keyword in a 6-wide grid, read by columns.
  - reverse(R1) and reverse(R2).
- each taken both as the permutation and as its inverse.

Added to these:
- the 29 shifts, which include the identity (σ = id gives the "no σ" walk);
- the 29 reflections x → s−x, which include Atbash.

**G, the order-5 steps: 1,127,284 distinct permutations**, every one asserted to have order 5.
- 23,751: Oosterhof's exact structured g. These are the first indices, `lists/goost.txt`.
- +546,273 structured grids:
  - ordering: Gematria (= prime) or English-alphabetical, the two from aldegonde `g_construction_survey`;
  - fill: row-major, column-major or boustrophedon;
  - any fixed 4 runes;
  - columns rotated as 5-cycles by a uniform k = 1..4, which covers steps of 5, 10, 15 and 20. Reversed orderings collapse onto these.
  - Per-column independent rotations (×256) are **not** included.
- +437,976 keyword grids: the keyed alphabet (R1 or R2), with its first 25 runes in a 5×5 grid and its last 4 fixed; the three fills; k = 1..4.
- +119,284 powers of keyed permutations: for every π in A whose order is divisible by 5 (78,446 of them), take π^(ord/5) and its powers 2–4. These carry 1–5 five-cycles.
- **No affine map x → ax+b mod 29 has order 5** (0 found). The order of a divides 28, and a = 1 gives a translation of order 29.

**Variants.**
- mode 0: the global clock (Oosterhof's model).
- mode 1: the clock reset to 0 at each word start.
- mode 2: a fixed base with no σ step (lane K already excluded this).

**Keys per start**: |A|²·|G| = **5.47 × 10¹⁶** for modes 0 and 1, and 2.48 × 10¹¹ for mode 2. That is 2^55.6, against Oosterhof's 2^38.

## 2. Brute force (`kwwalk.c`; gcc -O3, OpenMP, AVX-512 VBMI; 4 cores)

**Stage A**, all (base_0, g) pairs, 2.48e11 per start.
- Word 0 depends only on (base_0, g). It must be a lexicon word.
- Bases are grouped by (binv(c0), binv(c1)), so p0 and p1 are scalars per group. Then p2 and p3 for 64 bases come from `vpermb`, and the 4-prefix is tested against a per-(p0,p1) mask table. The N/D branches of runes 2–3 are vectorised as well. About 2% of pairs go on to an exact scalar DFS, which uses 5-rune prefix bitmaps and a hash lookup.
- Throughput: **2.4–2.6 × 10⁹ pairs/s** (1.0 × 10⁸ on the first scalar version).

**Stage B**, survivors × all σ.
- Words 1..k, up to at least 5 runes, must be lexicon words. A fast path tests the N-reading 4-prefix.
- Later words are scored by DFS over all N/D branches with lane K's word-internal rune 4-gram LM (int16), up to the first ≥150 runes (whole words). A loose gate of −6 nats/symbol applies.
- The top 1,000 by LM per symbol are kept.
- Throughput: 0.4–2 × 10⁸ (survivor, σ)/s.

**Full decryption.** The top 1,000 per mode are then fully decrypted over the whole page with `kwdec` (beam 16) and rescored with the dukotah quadgram scorer (`lp/score.py`, per quadgram), rune IoC and LM. Calibration (`runs/quad_calib.txt`): solved-LP English scores −4.40 ± 0.21 per quadgram and random text −7.49 ± 0.14 at 262 runes.

**Cost of one full-corner start.** Stage A takes about 100 s. Stage B takes 60–230 s per mode, depending on how much noise survives word 1. The total is about 4–8 min, so the effective coverage is roughly 10¹⁴ keys/s.

**Lexicon** (386,198 rune types, lengths 1–16): W&P train types, words_alpha (both ING spellings), the Cicada vocabulary and the solved-LP words. Held-out W&P OOV rates:

| length | OOV rate |
|---|---|
| 4 | 0.2% |
| 5 | 0.75% |
| 6 | 0.5% |
| 7 | 0.6% |
| 8 | 0.9% |
| 9 | 1.7% |

**Pruning miss probability for a true page-0 key**: P(word 0 or word 1 is OOV) ≈ 1.7%. Random survival per word: 1.2e-7 at length 8 and 1.0e-3 at length 5.

## 3. Controls (page-0 shape: 262 runes, LP word lengths, solved-LP plaintext words drawn to those lengths)

**plant1**: key from the set, with base_0 = PILGRIM:R1, g = Oosterhof structured {4,11,14,20} and σ = MOUNTAIN:R2.
- The full enumeration of 5.47e16 keys puts it at **rank 1**, with prefix LM **−1.834**/symbol. Rank 2 scores −4.14.
- On the page-0 null sd that is z ≈ +40. Full decrypt: quadgram −4.46, IoC 1.75, 262/262 runes correct. It reads "BEHAUIARS AGAIN WHAT END THAT UNREASONABLE OTHERS THREE …".

**plant2**: σ = LABYRINTHINE:R1, which is **not in the list**; base_0 = FEEDERS:R2rev:inv and g = Oosterhof {1,2,17,19}.
- The best found scores −3.937 (quadgram −7.3). That is null level, so there is no signal at all.
- Decoding with the true base and g but the 8 listed alphabets nearest the true σ (17–19 of 29 entries agree) gives 10–17% rune accuracy on the 151-rune prefix and LM −4.46 to −4.69 (`runs/nearmiss_out.txt`).
- Only the 8-rune first word survives; it depends on base_0 and g alone. **A keyword just outside the list is a clean miss**: the walk compounds σ errors, as lane K found.

## 4. Real page 0 vs 20 doublet-matched page-0 shuffles (identical enumeration; `summary_out.txt`)

Each shuffle keeps the word lengths, the rune multiset and the 2 doublets. "Best" is taken over the top 1,000.

| mode | stat | real | null mean ± sd | null max | z |
|---|---|---|---|---|---|
| 0 global clock | prefix LM/sym | −3.885 | −3.940 ± 0.053 | −3.824 | +1.04 |
| | full-page LM/sym | −4.189 | −4.186 ± 0.045 | −4.066 | −0.09 |
| | quadgram | −6.804 | −6.773 ± 0.049 | −6.640 | −0.63 |
| | IoC | 1.171 | 1.171 ± 0.025 | 1.218 | 0.02 |
| 1 reset per word | prefix LM | −3.943 | −3.943 ± 0.045 | −3.852 | 0.00 |
| | quadgram | −6.809 | −6.759 ± 0.081 | −6.575 | −0.62 |
| 2 fixed base | prefix LM | −4.152 | −4.223 ± 0.081 | −4.023 | +0.88 |
| | quadgram | −7.229 | −7.035 ± 0.101 | −6.866 | −1.93 |

- **The real result never exceeds the null max** and |z| ≤ 1.9 everywhere. A true key would sit at about −1.8 (z ≈ +40).
- The real best (mode 0) is base CONTENTS:R2, g kwgrid:CBDAEAB:R2:bou:k2, σ COLLEGE:R1:inv. It reads "C-H-A-U-S-S-E-S-C-R-A-U-NG-M-R-P-I-O-R-F-T-J-C-B-A-G-G-NG-G-I-N-X-I-A-S-A-E-IA-C-Y-IA-T-Y-U-EA-IA-T-N-NG-S-G-EA-L-O-N-TH-N-X-F-L-L-F-EA-NG-TH-NG-C-H-AE-U-IA-J-S-O-F-L-T-NG-G-S-W-O-C-Y-D-U-L-F-AE-S-F-U-C-W-C-B-P-H-L-N-I-E-L-TH-A-H-NG-L-I-C-G-W-I-EO-M-E-S-S-U-T" (the first 120 runes). This is noise apart from the forced first word.
- The top 10 global-clock keys, decrypted across the whole body, all die at body doublets 1–5. No continuation exists.
- **Oracle** (`--plaintext` with the best page-0 decrypt, as a record, since nothing beat the null): VERDICT NOT-ADJUDICABLE, English score −7.077 (`runs/oracle_out.txt`).

## 5. Per-start restart (walk restarted at a page or section start, with an independent key per start; `summary_out.txt`)

**Shared-key variant.** A key shared by all page restarts must decrypt page 0 from a fresh start, so the page-0 enumeration above already covers it.

**Independent keys.** Survivor counts, and so cost, are set by the first-word length L0. The coverage by L0:

| first-word length | starts | coverage |
|---|---|---|
| ≥ 7 | pages 16, 31, 46 | full corner, modes 0, 1 and 2 |
| 6 | pages 6, 13, 18, 38 and section 12 | base/σ ∈ R1 alphabets + shifts/reflections (18,458) × g ∈ Oosterhof + Gematria grids (285,012), modes 0 and 2 |
| 5 | pages 1, 9, 19, 52 | R1 × Oosterhof g (23,751), modes 0 and 2 |
| 4 | pages 8, 11, 15, 30, 35, 37, 48 and sections 3, 6, 7 | Cicada-vocabulary R1 (1,370) × Oosterhof g, modes 0–2 |
| ≤ 3 | 36 pages and 9 sections | **not run**: the word-0 filter passes ≥10% and stage B is infeasible |

- From L0 = 6 down, a top-K pruning (`-dyn 4`) was used. It never prunes a path that runs at better than −4 nats/symbol on the rest.
- Page 16's 13-rune first word decrypts to no lexicon word under any of the 2.48e11 (base, g) pairs, so it has zero survivors.

The table gives, per mode, the best prefix LM/sym / best full-page LM/sym / best full-page quadgram. "surv" is the number of stage-A survivors. "not-run" means mode 1 was skipped for that tier.

| start | base × g × σ | surv | mode 0 | mode 1 | mode 2 |
|---|---|---|---|---|---|
| page08 | 1370 × 23751 × 1370 | 754259 | -4.551/-4.731/-7.182 | -4.404/-4.628/-7.284 | -4.308/-4.393/-7.133 |
| page11 | 1370 × 23751 × 1370 | 35904 | -4.040/-4.244/-6.831 | -3.990/-4.239/-6.847 | -4.225/-4.349/-6.883 |
| page15 | 1370 × 23751 × 1370 | 555298 | -3.990/-4.042/-6.521 | -3.946/-4.006/-6.524 | -4.084/-4.137/-6.573 |
| page30 | 1370 × 23751 × 1370 | 1358564 | -3.946/-4.253/-6.734 | -4.020/-4.282/-6.777 | -4.164/-4.366/-7.056 |
| page35 | 1370 × 23751 × 1370 | 117779 | no-survivor | no-survivor | -4.194/-4.584/-7.291 |
| page37 | 1370 × 23751 × 1370 | 300177 | -4.177/-4.266/-6.876 | -4.137/-4.236/-6.848 | -4.155/-4.261/-6.851 |
| page48 | 1370 × 23751 × 1370 | 763295 | -3.946/-4.115/-6.794 | -3.912/-4.170/-6.820 | -4.163/-4.350/-6.964 |
| sec07 (first 60 words) | 1370 × 23751 × 1370 | 545614 | -3.997/-4.277/-6.771 | -4.025/-4.228/-6.823 | -4.061/-4.288/-6.999 |
| sec03 | 1370 × 23751 × 1370 | 234117 | -4.038/-4.253/-6.831 | -4.055/-4.253/-6.852 | -4.321/-4.469/-6.952 |
| page01 | 18458 × 23751 × 18458 | 981895 | -4.105/-4.265/-6.793 | not-run | -4.119/-4.315/-6.789 |
| page06 | 18458 × 285012 × 18458 | 701297 | -3.945/-4.032/-6.543 | not-run | -4.201/-4.261/-6.854 |
| page09 | 18458 × 23751 × 18458 | 68829 | -4.094/-4.362/-6.914 | not-run | -4.369/-4.461/-7.134 |
| page13 | 18458 × 285012 × 18458 | 362513 | -4.022/-4.263/-6.747 | not-run | -4.152/-4.291/-6.836 |
| page16 | 220280 × 1127284 × 220280 | 0 | no-survivor | no-survivor | no-survivor |
| page18 | 18458 × 285012 × 18458 | 44270 | -3.913/-4.096/-6.684 | not-run | -4.273/-4.408/-6.899 |
| page19 | 18458 × 23751 × 18458 | 240792 | -4.275/-4.423/-6.994 | not-run | -4.541/nan/nan |
| page31 | 220280 × 1127284 × 220280 | 28969 | -3.900/-4.107/-6.694 | -3.901/-4.138/-6.590 | -4.145/-4.268/-6.681 |
| page38 | 18458 × 285012 × 18458 | 734785 | -4.011/-4.144/-6.670 | not-run | -4.166/-4.339/-6.827 |
| page46 | 220280 × 1127284 × 220280 | 523535 | -3.945/-4.161/-6.741 | -3.980/-4.180/-6.709 | -4.133/-4.299/-6.635 |
| page52 | 18458 × 23751 × 18458 | 2124108 | -4.086/-4.108/-6.675 | not-run | -4.127/-4.148/-6.745 |
| sec12 | 18458 × 285012 × 18458 | 2477 | -4.154/-4.167/-6.771 | not-run | -4.270/-4.230/-7.031 |

- **Every start sits at the noise level**: the best prefix score is −3.90 to −4.55 per symbol. A planted English key scores about −1.8, and the page-0 null max is −3.82.
- The highest full-page quadgram, −6.52 on page 15 (only 159 runes), is still far below English (about −4.4).
- Section 7 was rerun on its first 60 words. Its full text (435 words) overflowed kwwalk's 400-word buffer.
- Section 6 (9 runes, 2 words) is excluded. Both of its words are lexicon-forced, so its score is meaningless.
- These restart tiers have no shuffle null of their own. Their maxima are read against the plant margin of more than 2 nats per symbol.


## 6. Verdict

- **Oosterhof's keyword corner of the walk is tested and empty.** That covers his exact 38-bit construction (structured g × keyword-then-rest alphabets, with Cicada vocabulary + 20k English as keywords) and a widening to 5.47e16 keys per start: 6 alphabet rules × inverses, shifts and reflections, 1.13M order-5 g from structured, keyword-grid and keyed-power constructions, a global or per-word clock, and σ = id.
- The search was run on page 0 and on the long-first-word page starts, at about 1.7% miss probability. It recovers a planted key at rank 1 with a 2.3 nats/symbol margin (z ≈ 40). On the real page 0 it returns the shuffle-null best to within |z| ≤ 1.9 in every mode and statistic.
- What remains open:
  - keywords outside the 20.6k list. A miss is clean, with no partial credit, so a larger dictionary is just a linear cost: about 4–8 min per 2.2e5-alphabet block squared at this throughput;
  - per-column rotation grids;
  - other keyword→alphabet rules (columnar transposition with other widths, two-keyword alphabets);
  - restarts at short-first-word pages;
  - free σ (lane K: infeasible).
- Nothing went to the oracle as a candidate because nothing beat the null. The best page-0 decrypt was submitted for the record: NOT-ADJUDICABLE, −7.08.
- New exact constraint for anyone pursuing the walk: every cipher doublet's plaintext rune is a fixed point of g, and inside a word it is a doubled letter. So the LP's 63 within-word doublets must all be doubled letters drawn from the 4 runes g fixes. This can be tested on g alone.

## Files

- Construction:
  - `common.py`: transliteration, the alphabet rules, the g constructions, the walk.
  - `prep.py` → `A.bin`/`A_meta.txt`, `G.bin`/`G_meta.txt`, `lex.bin`, `lm16.bin`, `prep_out.txt`.
- Search: `kwwalk.c`, the brute force. `kwdec.c`, the beam decoder.
- Texts and controls:
  - `mk_texts.py`: the real page and section texts, the nulls and the plants.
  - `verify_aldegonde.py`, `nearmiss.py`.
- Analysis: `analyze.py` (rescoring) and `summary.py` → `summary_out.txt`.
- Runs: `runs/full_*` (page 0, nulls, plants) and `runs/start_*`, `runs/start4_*` (restarts), each with its `.log`, `.txt` (top-1000 keys), `_an.json` and `_dec.txt`.
