# laneK_walk_search: global key search for the period-5 mixed-alphabet cipher with skip-on-repeat

Everything is in this directory. Corpus: `lpdata.unsolved()`, sha 0233…1585, 12,956 runes in 2,896 words.

Scripts and outputs:
- `kcore.py`: ciphers, corpora, statistics.
- `s0_census.py` → `s0_out.txt`; `s0b_bound.py` → `s0b_out.txt`.
- `lm_train.py` → `lm4.bin`, `lm_out.txt`.
- `mk_sa.c`: the C annealer. `gen_inst.py` writes the instances. `ladder*.sh` / `real_run.sh` run the jobs, with logs in `runs/`. Tables: `ladder_table.py` → `ladder_table.txt`, `summarize.py` → `real_summary.txt`.
- `walk_sa.c` and `gen_walk.py` → `walk_landscape.txt`, `runs/walk_*.log`.
- `s3_deficit.py` → `s3_deficit_out.txt`.
- `oracle_out.txt`.

## 0. Oosterhof's model, taken from aldegonde (clone at SCRATCH/dl/aldegonde_clone, HEAD 04f5ccc, 2026-10-02)

**Exact definition** (`experiments/doublet_dodge_walk.py::encipher`, `hypotheses/doublet-dodge-walk.md`):
```
c_j = base_w[ g^(clock mod 5)[p_j] ]              (base and g are arrays; g has order 5, nominally 4 fixed points + five 5-cycles)
if c_j == previous ciphertext rune (across word boundaries too): clock += 1, recompute c_j once (no re-check)
clock += 1 after every rune; the clock is GLOBAL and never resets at a word
after each word: base_{w+1} = base_w o g^((clock-1) mod 5) o sigma      ((a o b)[x] = a[b[x]])
```
- **Key.** The key is (base_0, g, σ). `how-big-is-the-key-really.md` prices it at **283 bits** for free permutations: g 79.7, σ 101.8, base_0 101.8. `key-local-channel-is-empty.md` says about 178 bits once base_0 is treated as derivable. "~200 bits" sits between the two. With a structured g and keyword-built σ and base_0 the key would be 38 bits, and his own test leans about 3:1 against keyword-built alphabets.
- **The per-word alphabets are NOT a fixed set.** σ lies outside ⟨g⟩, so base_w visits a large group. `sigma-power-step.md` shows that σ = g^k (only 5 bases) is refuted by the identity census: about 2,500 identical cipher words predicted against 17 observed. The code comment says the same: "Stepping by a bare sigma … shows up at once as a non-flat IoC and hundreds of identical cipher words."
- **Fitting code and results.** Only statistical-profile fits exist. Nothing decrypts.
  - `walk_full_profile.py`: fits g and σ to the d-profile. Cells land, but that is fitting, not prediction.
  - `dodge_three_cells.py`: the joint landing rate is 11/320, which is what independence predicts.
  - `g_cannot_be_annealed.py`: hill-climbing g against the d-profile overfits, and on the body it is no better than random.
  - `hillclimb_single_g.py`: a stepped g with no base IS climbable on plants. `hillclimb_lp_sweep.py`: on the LP, periods 2..50 all reach IoC ≤ 1.002.
  - `quagmire_dodge_decode.py`: a beam decoder holding the key recovers 12,382–12,388 of 12,388 runes.
  - The only search costing (`how-big-is-the-key-really.md`) is 10^9–10^11 keys under the keyword/structured assumption. It was never run.

Grepping the dukotah LEDGER / ELIMINATION-LEDGER and leo FINDINGS for walk/dodge/quagmire/per-word-phase/anneal finds nothing, so this lane duplicates no prior work there.

## 1. Models tested

**M_K, the brief's model.** K fixed alphabets A_0..A_{K-1} (free 29-permutations) and a free per-word phase φ_w. The clock t starts at φ_w in each word, and c_j = A_{t mod K}[p_j], then t += 1. Skip variants:
- `adv` (Oosterhof's rule): if the emission equals the previous ciphertext rune (the previous word's last rune for j = 0), set t += 1 and recompute once. The extra step persists for the rest of the word.
- `redraw`: only this position uses t+1, and the clock is not shifted.
- `none`: no skip rule.

There is also a step-permutation variant ("tied"): A_k = base o g^k with g of order 5. This is the same family as π^k o base, since π = base g base⁻¹.

**Decryption.** The decoder knows c_{j-1}. Two readings are possible at each position:
- N: p = A_t⁻¹(c), valid iff c ≠ c_{j-1}.
- D: p = A_{t+1}⁻¹(c), valid iff A_t(p) = c_{j-1}.

A greedy decoder with the true key reads only 88.8% (prefer N) or 89.5% (prefer D) of runes correctly (`s0_out.txt`). The solver therefore profiles out both the phase and the skip branches. A word's score is the maximum, over φ and over all valid N/D branch paths (capped at 16), of the word-internal rune 4-gram log-probability. The total score is the sum over words. With the true key this reaches 99.4–99.95% accuracy; the residue is short words whose phase is ambiguous.

**LM.** A 30-symbol word-internal 4-gram (runes plus word end), trained on the W&P runeglish words 0–480k. Cross-entropy (`lm_out.txt`): held-out 1.86 nats/symbol, solved LP pages 1.92, random runes 4.97.

**Plaintexts for plants.**
- P1: held-out W&P words drawn to the LP's exact word-length sequence.
- P2: the solved LP pages (735 words) followed by contiguous held-out W&P text up to 12,956 runes.

**M_walk, Oosterhof's exact model** (above). The planted encryptor is asserted identical to his `encipher` (`gen_walk.py`). On LP-length English, plants give IoC 0.9995–0.9998, 14–18 repeated cipher words of length ≥ 3 (LP: 16) and doublets 0.003–0.012.

## 2. M_K is refuted on the real text before any search (`s0_out.txt`, `s0b_out.txt`)

| quantity | LP | M_K, random alphabets, 20 sims (P1 / contiguous) |
|---|---|---|
| unigram IoC | **0.9999** | K=4: 1.16/1.20; K=5: 1.155±0.046 / 1.146; K=6: 1.12; K=7: 1.10–1.12 |
| repeated cipher words, len ≥ 3 | **16** | K=4: 829/971; K=5: **763±13** / 903±78; K=6: 704/839; K=7: 660/789 |
| same, Oosterhof walk (contrast) | 16 | 12 / 13 |

- **IoC can be fixed.** Hand-balanced alphabets can flatten the K=5 mixture to an IoC of 1.00004.
- **The repeated-word count cannot be fixed by any key or phase choice.** A word type that occurs n times has at most 2K cipher forms (K phases, times skip or no skip on the first rune). That gives a pigeonhole lower bound of Σ_t max(0, n_t − 2K) repeated cipher words.

Pigeonhole bound on held-out English, 12,956 runes:

| K | 4 | 5 | 6 | 7 | 10 | 20 | 50 |
|---|---|---|---|---|---|---|---|
| minimum repeated words | 555 | **482** | 423 | 375 | 274 | 125 | 22 |

The LP has 16. **Any fixed-alphabet-set version of "period-5 alphabets + free per-word phase + skip" is excluded absolutely for K ≤ ~50**, and the tied/step-permutation subfamily goes with it. This is Oosterhof's σ ∈ ⟨g⟩ refutation, reproduced as a key-free bound. The surviving shape needs per-word alphabets drawn from a large set (his base_w), not a free phase over a fixed set.

## 3. Feasibility ladder for M_K at n = 12,956 (`ladder_table.txt`)

A run counts as "solved" at > 95% plaintext accuracy.

| rung | plants solved | restarts solved | best acc (median) | true-key acc | moves/s/core | s/restart |
|---|---|---|---|---|---|---|
| (a) known phases, unknown alphabets, K=5, adv, 50k moves | 5/5 | 5/5 | 0.9995 | 0.9995 | 11,000 | 4.5 |
| (b) known alphabets, unknown phases (direct argmax) | 5/5 | 5/5 | 0.9955 | 0.9955 | n/a | 0 |
| (c) both unknown, K=5, no skip, 100k | 5/5 | 14/20 | 0.9964 | 0.9964 | 7,800 | 13 |
| **(d) both unknown, K=5, adv skip, 100k** | **5/5** | **14/20** | 0.9955 | 0.9955 | 2,550 | 39 |
| (d) P2 plaintext (solved pages + prose) | 3/3 | 6/12 | 0.9923 | 0.9925 | 2,780 | 36 |
| (d) K=4 / K=6 / K=7, 150k | 3/3 each | 12/12, 6/12, 7/12 | 0.991–0.996 | same | 3,200 / 2,160 / 1,830 | 47 / 69 / 82 |
| (d) redraw variant | 3/3 | 6/12 | 0.9928 | 0.9928 | 2,520 | 40 |
| (d) section size: ch. 14 (2,474 runes) / ch. 8 (1,021 runes) | 3/3 / 3/3 | 8/12 / 9/12 | 0.997 / 0.993 | | 14,600 / 33,900 | 7 / 3 |
| (d) tied plant (base o g^k), tied solver with g conjugation moves | **0/3** | 0/12 | 0.28 | 0.9954 | 2,100 | 47 |
| (d) tied plant, tied solver, g known | 3/3 | 6/6 | 0.9954 | | 2,280 | 22 |
| (d) tied plant, **free** 5-alphabet solver | 3/3 | 9/12 | 0.9954 | | 2,570 | 39 |

- **Every rung recovers**, so M_K is trivially searchable. A free-alphabet SA with phases and skips profiled out solves it in under a minute per restart, with about 50–70% of restarts succeeding.
- The tied variant is best solved as a free model, since it is a subfamily of it. The g-conjugation landscape alone is too rough.
- Failed restarts stall at about −3.2 nats/symbol, against −1.84 for a solve, so success is unambiguous. A solved plant reads "ATTENTIANBEGANMOSTANDTHATINOPPORTUNE…" with IoC 1.78 and dukotah quadgram −4.51.

## 4. M_K on the real text: per section and whole corpus, against doublet-matched shuffle nulls (`real_summary.txt`)

**Null construction.** Each null is a global shuffle of the same section, keeping its word lengths and repaired to the real doublet count. The null runs use the identical budget: 4 restarts × 100k moves.

| text | real best (nats/sym) | null mean ± sd (max) | z | real IoC / quad | null IoC / quad |
|---|---|---|---|---|---|
| whole corpus, K=5 (20 nulls) | −3.676 | −3.675 ± 0.004 (−3.668) | −0.22 | 1.284 / −6.72 | 1.273 / −6.77 |
| ch. 5, 1,729 runes | −3.294 | −3.304 ± 0.015 (−3.271) | +0.71 | 1.389 / −6.41 | 1.371 / −6.38 |
| ch. 7, 1,894 runes | −3.307 | −3.312 ± 0.012 (−3.289) | +0.45 | | |
| ch. 8, 1,021 runes | −3.175 | −3.158 ± 0.012 (−3.138) | −1.44 | | |
| ch. 9, 1,433 runes | −3.270 | −3.248 ± 0.014 (−3.216) | −1.57 | | |
| ch. 11, 1,307 runes | −3.239 | −3.224 ± 0.018 (−3.195) | −0.81 | | |
| ch. 14, 2,474 runes | −3.371 | −3.391 ± 0.010 (**−3.372**) | +2.05 (equals the null max) | 1.358 / −6.39 | 1.346 / −6.46 |
| whole corpus, K=4 / 6 / 7 (5 nulls each) | −3.788 / −3.593 / −3.514 | −3.784 / −3.586 / −3.515 | −0.79 / −2.39 / +0.16 | | |

- **Real equals null everywhere.** Every real run sits at the null level and about 1.5–1.9 nats/symbol worse than any solved plant of the same size.
- **Nothing readable.** The whole-corpus decryption starts "P-EO-EA-T-Y-S-R-G-P-U-EA-E-D-P-B-I-N-L-O-F-F-U-P-A-EA-I-M-B-P-A-X-I-M-B…"; first 120 runes are in `summarize.py` output.
- **Oracle.** The two best decryptions (whole corpus and ch. 14) went to the oracle with `--plaintext`. Verdict NOT-ADJUDICABLE, English score −6.73 and −6.39, against roughly −4.5 for English (`oracle_out.txt`).

## 5. Oosterhof's walk (the actual surviving model): SA cannot search it, even with an oracle

**Rung (e), the most generous setting possible** (`walk_sa.c`): g, base_0 and the true clock with every skip are all given, so only σ is unknown and decryption is deterministic. Throughput is 4,500 full-text evaluations per second per core, and 140k–440k per second on 30–100-word prefixes.

- **The landscape is a delta function** (`walk_landscape.txt`, 3 plants, 40 draws each). One non-trivial transposition away from the true σ (27/29 entries correct), full-text accuracy falls to chance (3.5–3.6%). The score falls from −29,213 to about −78,900, which is random level. Accuracy at 2, 3, 4, 6 and 29 transpositions is the same: 0.036–0.038. The error compounds through the 2,895-fold product base_w, so there is no partial credit after the first ~30 words. On a 30-word prefix, one transposition still leaves 48% accuracy; on 100 words, 19%.
- **SA results.** Starts at 2, 4, 6, 8 or 12 transpositions from the truth and random starts were tried, with 2 restarts × 100k evaluations each on full text. **0/36** runs returned to the truth. Even the starts 2 transpositions away drifted to chance (best −77,859). Prefix-scored SA (30, 100 or 300 words, 1M evaluations × 3 restarts) failed **0/27**: best −620 against a truth of −287 on 30 words, and the search did not even reach the truth's score.

**A sequential (beam) search is the only alternative, and its bit budget is out of reach** (`s3_deficit_out.txt`). Words are processed in order; each newly needed key value costs log2(remaining choices), and each decrypted symbol earns the LM's mean log-likelihood ratio. A beam must carry about 2^(maximum deficit) hypotheses.

| what is known | max deficit (3 plants) |
|---|---|
| g, base_0, clock known (only σ unknown) | 13–28 bits (a beam might succeed) |
| g known, base_0 unknown | **89–105 bits** |
| structured g (14.5 bits) + base_0 unknown | 103–119 bits |
| free order-5 g + base_0 unknown | **168–184 bits** |

The peak is always at words 4–7, where σ is first needed in full. The clock and skip schedule are not even charged here.

## Verdict

1. **The brief's model** (K fixed alphabets with K = 4–7, free per-word phase, skip-on-repeat in either form, including the order-5 step-permutation subfamily):
   - **It is searchable.** Every rung of the feasibility ladder, (a) through (d), recovers planted text at n = 12,956 and at section sizes down to about 1,000 runes, in under a minute per restart (2–3k moves/s/core with skip, 8–11k without).
   - **On the real text it gives exactly the null** (whole corpus z = −0.22; all sections |z| ≤ 2.05 and never above the null max).
   - **It is independently excluded without any search.** The LP has 16 repeated cipher words where any key or phase choice must produce at least 482 (K=5) and still 22 at K=50.
   - **Dead.**
2. **Oosterhof's doublet-dodge walk** (per-word base_w = base_{w−1} o g^e o σ, about 180–283 bits) is the only form compatible with the census. **No global SA, EM or parallel-tempering search can solve it at n = 12,956.** Planted instances show a delta-function landscape even when g, base_0 and the full skip schedule are handed to the solver: one wrong transposition in σ gives chance-level output. A sequential beam faces a deficit of about 90–185 bits in realistic settings.
   - Per the brief's stop rule, (d) for this model does not recover plants, **so no real-text run was made for the walk.**
   - The family could be broken only with an external handle on g and base_0: a long crib, a solved body page, or a short constructive key (Oosterhof's 38-bit keyword/structured reading, 10^9–10^11 keys, about 220+ core-hours with a compiled scorer). Only in that case does σ fall to a beam: once g and base_0 are fixed, the bit budget above is 13–28 bits.
3. No candidate key exists, nothing passed the oracle, and there is no solve.
