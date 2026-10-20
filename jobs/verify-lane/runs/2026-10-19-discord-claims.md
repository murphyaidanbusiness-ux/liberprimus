# Verify-lane: three CicadaSolvers Discord claims (scout 7), 2026-10-19

Job: `jobs/verify-lane` (SKILL.md, PROOF.md). Verifier: claude-opus-5-5, a side session started by the orchestrator.
Sources: `research/scout7_discord.md` and `jobs/community-scout/runs/2026-10-19-discord/notes.md` (the claims, read in
Discord, treated as data). No community code was used: the claimants posted none, and our code is new.

## Summary

| # | Claim (who, date) | Our statistic | Null mean +- sd (max) | z | Verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | camilo!, 08-19: solved plaintext sentence GP sums prime ~47% vs ~15% by chance, z +8.8 | 44 of 96 solved sentences prime = **45.8%** (LP1 alone 39/88 = 44.3%) | shuffle 14.6% +- 3.5% (max 29.2%) | **+8.86** (LP1 alone +8.06) | **REPRODUCED.** Replicates on both halves (z +5.93, +6.64, each above its own null max), on a second route through the English translation (z +9.77), and under a fresh seed. Met the brief's stop bar, so it went to the orchestrator first; **ruled not a lead** (see Lead status). |
| 2a | solver 2, 09-23: lag-1 circular GP distance of the 86 doubled runes larger than in permutations, 8.81 vs 7.29, p = 0.00063 | 8.635 | 7.290 +- 0.449 (max 9.094) | +3.00; p 0.0015, **0.013 after lags 1-10** | **Weak, differs in size.** Same direction in both halves (z +2.13, +2.14, p ~0.02 each). Survives an increment-shuffle cipher null (z +3.26). Far from a lead. |
| 2b | solver 2: separations 5, 12, 14 over-represented, p = 0.014 | 31 of 85 lag-1 pairs | 17.1 +- 3.7 for {5,12,14}; 27.3 +- 2.4 for the top 3 of any values | +3.79 raw; **+1.55 as the top 3 of 15 values, p 0.54 after lags 1-10** | **Not significant.** The three values were picked after looking. |
| 2c | solver 2: D(i+3) - D(i) = +4 in 12.9% vs 3.4%, p = 0.002 | 10 of 83 = 12.0% | 3.09 +- 1.72 (max 15) | +4.01 raw; **p 0.16 over all 290 (lag, difference) cells** | **Not significant** after the correction; carried by the first half (6 of 37), absent in the second (4 of 43, z +1.88). |
| 3a | solver 3, 08-09: ~100 one-rune words in LP2, none adjacent; shuffles give runs of 2-4 | 83 one-rune words, 0 adjacent | global shuffle 2.37 +- 1.50; P(0) = 0.086 (within page 0.107, within sentence 0.127) | -1.59 | **Count differs (83 vs ~100), "none adjacent" reproduced, not significant.** LP1 (0 adjacent, P(0) 0.09-0.38) and English (deficits of z -1.1 to -3.3 against its own shuffles) behave the same way. |
| 3b | solver 3: apostrophes at LP2 positions 1110, 5138, 8515, 10089, each followed by one rune | 1110, 5138, 8515, 10089 (0-based index of the rune after the mark; pages 4, 21, 35, 41) | n/a | n/a | **REPRODUCED** in both aldegonde transcriptions. RDP v2's master has only three: it lacks the mark at 8515 (page 35). |

Lead status. Claim 1 is far outside its size-matched null (z +8.9; obs 45.8% against a null max of 29.2%) and
replicates on held-out halves and a second derivation, so it meets the bar the brief set ("z >= 5 beyond the null max and
replicates on held-out halves"). It is a property of the **solved** text, not of LP2: LP2's own ciphertext sentences sit at
the null (16.0% vs 13.0% +- 2.5%, z +1.22), as any cipher that hides letters would make them. It gives no key and no
plaintext. It is a plaintext-side check that an LP2 decryption could be scored against. This session stopped and
reported to the orchestrator, which ruled on 2026-10-19 that it is **not a lead** under CLAUDE.md: it is a property of
the already-solved plaintext, not key information or structure in LP2, and it is not new (camilo! posted it publicly on
2026-08-19; the orchestrator also said the community wiki "has long noted" prime-sum sentences in LP1, but that was
not checked against the wiki, so who found it first is unverified). No email or notification was sent. It
goes to `jobs/hypothesis-gate` as a candidate optional scorer. Claims 2 and 3 are not leads (best z +4.0 raw,
corrected p >= 0.013).

## Inputs and code

- `jobs/verify-lane/tools/solved_plaintext.py` (new, reusable): the solved plaintext as runes with word and sentence
  ids. LP1 = lines 1-187 of `dl/aldegonde_clone/data/liber-primus__transcription--master.txt` (seven `$` segments); AN
  END and PARABLE = pages 55-56 of `lp/lpdata.py`. Each segment is decoded by search, not by a typed-in key: every
  affine map (direct, Atbash, Atbash + shift), and the running keys DIVINITY, FIRFUMFERENFE and phi(prime) in both
  signs, with a beam over F interrupters; best quadgram wins. It finds Atbash (A WARNING), DIVINITY sign -1 with 11
  interrupters (WELCOME), direct (SOME WISDOM, LOSS OF DIVINITY, AN INSTRUCTION, PARABLE), Atbash + 3 (KOAN 1),
  FIRFUMFERENFE with 2 interrupters (KOAN 2) and phi(prime) with 1 interrupter (AN END). All nine read as the known
  English (`python -X utf8 jobs/verify-lane/tools/solved_plaintext.py` prints them). `SOLVED-PAGES.json` was not usable:
  it drops the word and sentence marks and the plaintext F of every interrupter.
- `jobs/verify-lane/runs/discord_claims_verify.py`: all three claims. Imports `lp/lpdata.py` (SHA pin asserted),
  `toolbox/runes.py`, `toolbox/nulls.py` (claim 2's cipher null) and the tool above. Runs at below-normal priority.
  `python -X utf8 jobs/verify-lane/runs/discord_claims_verify.py --seed 1 --perms 100000` (about 2 minutes) prints every
  number in this report; outputs `discord_claims_out_seed1.txt`/`.json`. Seed 2 is the fresh-seed replay.
- `jobs/verify-lane/runs/discord_claim1_crosscheck.py`: claim 1 by a second route with its own code (no rune decoding):
  the English lines of the community translation (`aautcsh__idkfa/assets/liber-primus-translation.txt`, solved pages
  01-16 and 73-74), transliterated with `toolbox/runes.py`.
- Sentence: a run of runes between sentence marks ('.', '&', '$'; in the LP2 loader also '§'). Word: between word marks,
  sentence marks or numbers. Line and page breaks end neither.

## Claim 1: prime sentence sums in the solved plaintext (camilo!)

Statistic: the share of sentences whose Gematria Primus sum (sum of the rune primes 2..109) is prime.

| Corpus / null | Sentences | Prime | Rate | Null mean +- sd | Null max | z | p |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LP1, 7 segments, shuffle null | 88 | 39 | 44.3% | 14.66% +- 3.68% | 32.95% | +8.06 | 5e-05 (20,000) |
| LP1 + AN END + PARABLE, shuffle null | 96 | 44 | 45.8% | 14.63% +- 3.52% | 29.17% | +8.86 | 5e-05 (20,000) |
| first half (sentences 1-48) | 48 | 21 | 43.8% | 14.32% +- 4.96% | 35.42% | +5.93 | 1e-04 (10,000) |
| second half (sentences 49-96) | 48 | 23 | 47.9% | 14.99% +- 4.96% | 35.42% | +6.64 | 1e-04 (10,000) |
| variant: F interrupters left out of the sums | 96 | 41 | 42.7% | 15.64% +- 3.59% | 31.25% | +7.54 | 1e-04 |
| variant: section titles left out | 78 | 36 | 46.2% | 13.98% +- 3.86% | 29.49% | +8.34 | 1e-04 |
| English (Moby-Dick, 14,572 sentences, 14.0% prime), blocks of 96 consecutive sentences | 96 | | | 13.95% +- 3.44% | 26.04% | +9.28 | 0.0066 (151 blocks) |
| English (Moby-Dick), one length-matched sentence per solved sentence | 96 | | | 15.79% +- 3.46% | 28.12% | +8.67 | 5e-04 (2,000) |
| English (Dante, Longfellow, 5,958 sentences, 13.1% prime), blocks of 96 | 96 | | | 13.10% +- 3.39% | 19.79% | +9.66 | 0.016 (62 blocks) |
| English (Dante), length-matched | 96 | | | 12.68% +- 3.22% | 27.08% | +10.31 | 5e-04 (2,000) |
| second route: translation lines via toolbox/runes.py | 79 | 42 | 53.2% | 15.11% +- 3.90% | 31.65% | +9.77 | 5e-05 (20,000) |
| reference: LP2 ciphertext sentences (175), shuffle null | 175 | 28 | 16.0% | 12.97% +- 2.48% | 21.71% | +1.22 | 0.14 |

The shuffle null pools every plaintext rune of the corpus, permutes them, and cuts at the same sentence lengths (so
sentence length and the rune frequencies are kept). Our 45.8% vs 14.6% at z +8.86 is camilo!'s ~47% vs ~15% at z +8.8.
English sentences transliterated with `toolbox/runes.py` are prime 13-14% of the time (sentences split at . ! ? ; :,
Project Gutenberg licence cut off: its one-letter "sentences" such as "1.E.8" are prime by construction, since every
single rune's value is a prime, and before the cut they put one Moby-Dick block at 41.7%).

Where it comes from. Prime sentences per section: A WARNING 9/10, WELCOME 7/14, SOME WISDOM 4/6, KOAN 1 3/22,
LOSS OF DIVINITY 9/23, KOAN 2 2/7, AN INSTRUCTION 5/6, AN END 1/4, PARABLE 4/4. The short doctrinal sentences are
nearly all prime (all nine after the title of A WARNING; all four of PARABLE, title included; QUESTION ALL THINGS / DISCOVER TRUTH
INSIDE YOURSELF / FOLLOW YOUR TRUTH / IMPOSE NOTHING ON OTHERS; THE PRIMES ARE SACRED / THE TOTIENT FUNCTION IS SACRED /
ALL THINGS SHOULD BE ENCRYPTED). The two narrative koans are at chance (5 of 29, 17%). Odd sums are 65.6% of sentences
(null 51.1%), and 69.8% of the odd sums are prime, so the excess is primality itself, not only parity. This reads as
deliberate composition of the aphorisms, which fits A WARNING's own text ("EITHER THE WORDS OR THEIR NUMBERS ... FOR
ALL IS SACRED"). It does not depend on our decoder: the four direct-rune sections need no key and give 22 of 39.

What it means for LP2. If LP2's plaintext was written the same way, a correct decryption should show prime sums on its
175 visible sentence marks well above ~13-15%. That is a check on a candidate decryption, independent of letter
statistics, and strongest on short sentences. It cannot find a key by itself (the ciphertext's sentence sums are at the
null). On `toolbox/score.py`: it belongs there as an optional channel (sentence-prime rate of a candidate, with this
shuffle null), but the toolbox is not edited here; it goes to `jobs/hypothesis-gate` first, which should also ask how
much of LP2 is narrative (where LP1 shows no effect) before weighting it.

## Claim 2: the doubled-rune stream (solver 2)

D = the rune of each of LP2's 86 doublets, in order (0 triples), from `lp/lpdata.py`:
`TH X EA J L AE S NG G AE N OE J F Y G X U AE G IA O M H W D X J EA AE G IA O S N X U L S E L O E R C F EO AE M TH EO F N T D H R A TH J T AE F X W I OE W EA N OE I AE OE X E O E P W W W Y NG G TH`.
Null: 100,000 permutations of D (50,000 per half). Circular distance = min(|a - b|, 29 - |a - b|) on GP indices.

| Statistic | solver 2 | Ours | Null mean +- sd | Null max | z | p raw | p corrected | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lag-1 mean circular distance | 8.81 vs 7.29 | 8.635 | 7.290 +- 0.449 | 9.094 | +3.00 | 0.0015 | 0.013 (max z over lags 1-10) | differs (8.81 vs 8.635; his list is not posted, so the cause is unknown); direction reproduced |
| mean distance, lags 2-10 | "gone at lag 2" | 7.43 7.54 6.82 7.78 7.59 7.27 7.96 6.77 8.08 | | | z +0.31 +0.55 -1.03 +1.07 +0.65 -0.05 +1.43 -1.10 +1.67 | | | reproduced |
| lag-1 distances in {5, 12, 14} | over-represented, p 0.014 | 31 of 85 | 17.12 +- 3.66 | 34 | +3.79 | 0.0003 | 0.54 (top 3 of 15 values, lags 1-10) | not significant once the choice of values is counted |
| D(i+3) - D(i) = +4 (mod 29) | 12.9% vs 3.4%, p 0.002 | 10 of 83 = 12.0% | 3.09 +- 1.72 | 15 | +4.01 | 0.00095 | 0.16 (max over 10 lags x 29 differences) | value close (12.0% vs 12.9%); not significant after correction |
| first half (runes 0-6477, 40 doublets): lag-1 distance | | 8.795 | 7.381 +- 0.664 | 10.03 | +2.13 | 0.018 | 0.15 | same direction |
| second half (runes 6478-12955, 46 doublets): lag-1 distance | | 8.644 | 7.336 +- 0.612 | 9.911 | +2.14 | 0.017 | 0.15 | same direction |
| first half: D(i+3) - D(i) = +4 | | 6 of 37 | 1.09 +- 1.01 | 7 | +4.84 | 0.0005 | 0.056 | |
| second half: D(i+3) - D(i) = +4 | | 4 of 43 | 1.65 +- 1.25 | 9 | +1.88 | 0.08 | 1.0 | does not replicate |
| lag-1 distance vs 200 increment-shuffled LP2 streams (`toolbox/nulls.shuffle_increments`) | | 8.635 | 7.219 +- 0.434 | 8.318 | +3.26 | 0.005 | | the chain statistics alone do not produce it |

Lag-1 distance histogram (values 0..14): 2 2 1 6 4 10 4 4 5 7 8 3 10 8 11. Only the lag-1 mean distance survives the
look-elsewhere correction (p 0.013), and it is about +2 sigma in each half. It is a small, consistent effect at n = 86:
consecutive doublets tend to sit far apart on the rune circle. It is nowhere near the lead bar, and no key model in
CONSTRAINTS.md predicts it yet. Cheap to keep as a C2-side observation; a follow-up would need a mechanism to test.

## Claim 3: one-rune words and apostrophes (solver 3)

Words from `lp/lpdata.py` (2,896 words on pages 0-54). Adjacent = consecutive in reading order, across sentence and
page breaks too (counting only pairs inside a sentence gives the same zeros). Nulls keep the word-length multiset:
global shuffle, shuffle within each page, shuffle within each sentence; 20,000 each (10,000 for the halves, 4,000 for
English). The claim is a deficit, so the tail is P(null <= obs).

| Text | Words | One-rune words | Adjacent pairs | Global shuffle mean +- sd, P(0) | Within page, P(0) | Within sentence, P(0) | z (global) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LP2 pages 0-54 | 2,896 | 83 (2.9%) | 0 | 2.37 +- 1.50, 0.086 | 2.13, 0.107 | 1.76, 0.127 | -1.59 |
| LP2 pages 0-27 | 1,509 | 48 | 0 | 1.50 +- 1.18, 0.210 | 1.41, 0.232 | 0.94, 0.366 | -1.27 |
| LP2 pages 28-54 | 1,387 | 35 | 0 | 0.86 +- 0.91, 0.414 | 0.72, 0.469 | 0.82, 0.357 | -0.95 |
| LP1 solved (7 segments) | 694 | 26 (3.7%) | 0 | 0.93 +- 0.93, 0.380 | 1.61, 0.175 | 2.08, 0.093 | -1.01 |
| English, Moby-Dick block 1 | 2,896 | 160 (5.5%) | 5 | 8.76 +- 2.79, 0.000 | (no pages) | 12.36, 0.000 | -1.35 (within sentence -2.66) |
| English, Moby-Dick block 2 | 2,896 | 162 (5.6%) | 2 | 8.98 +- 2.91, 0.000 | | 8.98, 0.000 | -2.40 (-2.57) |
| English, Moby-Dick block 3 | 2,896 | 247 (8.5%) | 8 | 21.04 +- 4.19, 0.000 | | 20.33, 0.000 | -3.12 (-3.12) |
| English, Dante block 1 | 2,896 | 130 (4.5%) | 1 | 5.79 +- 2.36, 0.003 | | 6.59, 0.000 | -2.03 (-2.40) |
| English, Dante block 2 | 2,896 | 90 (3.1%) | 1 | 2.79 +- 1.60, 0.053 | | 3.41, 0.023 | -1.12 (-1.44) |
| English, Dante block 3 | 2,896 | 108 (3.7%) | 0 | 4.00 +- 1.92, 0.013 | | 3.37, 0.022 | -2.08 (-2.02) |

English blocks are the first three runs of 2,896 words of each text (`toolbox/runes.py` transliteration), sentences
split at . ! ? ; :, so the within-page column does not apply to them.

solver 3's count (~100, "84/100 confirmed against page images") differs from ours (83); our word marks come from the
pinned loader, and his figure of 84 confirmed is close to ours. "None adjacent" reproduces, but a shuffle gives zero
adjacent pairs 9-13% of the time, so it is not a signal. English shows the same thing more strongly (A and I rarely
stand next to each other), so the LP2 pattern is what English word order gives. A small aside on the layout result
(word order changed before encryption): a fully random word order would give about 2.4 adjacent pairs, so the zero
leans weakly (p ~0.09) against complete scrambling.

Apostrophes, mapped onto our pinned stream (each transcription's LP2 runes equal ours for all 12,956):

| solver 3 | Our rune index after the mark (0-based) | Page | Word before the mark | Runes after the mark in the word | aldegonde page0-58 | aldegonde master | RDP v2 master |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1110 | 1110 | 4 | ᛗᛉᛁ | 1 | yes | yes | yes |
| 5138 | 5138 | 21 | ᚫᚩ | 1 | yes | yes | yes |
| 8515 | 8515 | 35 | ᛈᛖ | 1 | yes | yes | **no** |
| 10089 | 10089 | 41 | ᛉᛚᛄ | 1 | yes | yes | yes |

His positions are the 0-based index of the rune after the apostrophe, and every mark is followed by exactly one rune
and then a word mark (reproduced). Our loader does not treat the apostrophe as a word break, so the words there are
4, 3, 3 and 4 runes long. RDP v2 (mortlach's corrected transcription) drops the page-35 mark; check this against the
page image and against a community member's corrected transcription when it is posted.

## Fresh-seed replay

Lead protocol step 1 (re-run from scratch with a new seed) for every headline number: `--seed 2 --perms 100000`
(`discord_claims_out_seed2.txt`). The English nulls are deterministic, so they are equal by construction.

| Number | Seed 1 | Seed 2 |
| --- | --- | --- |
| claim 1, solved corpus: z (null mean, max) | +8.86 (14.63%, 29.17%) | +8.91 (14.59%, 29.17%) |
| claim 1, LP1 alone: z (null max) | +8.06 (32.95%) | +8.01 (31.82%) |
| claim 1, halves: z | +5.93, +6.64 | +5.93, +6.63 |
| claim 1, variants (F left out, titles left out): z | +7.54, +8.34 | +7.57, +8.30 |
| claim 1, length-matched English (Moby-Dick, Dante): z | +8.67, +10.31 | +8.77, +10.37 |
| claim 2a, lag-1 distance: z, p raw, p corrected | +3.00, 0.0015, 0.013 | +3.02, 0.0011, 0.012 |
| claim 2b, top 3 separations: p corrected | 0.54 | 0.52 |
| claim 2c, D(i+3)-D(i) = +4: z, p corrected | +4.01, 0.16 | +4.01, 0.16 |
| claim 2a, vs increment-shuffle cipher null: z | +3.26 | +3.18 |
| claim 3a, LP2: P(0 adjacent), global shuffle | 0.086 | 0.091 |

Fresh plaintext as well as a fresh seed: the second route for claim 1 (`discord_claim1_crosscheck.py`, seed 3: the
community English translation, no decoder, its own null code) gives 42/79 = 53.2% against 15.1% +- 3.9% (max 31.6%),
z +9.77. Its count differs from the decoder route (79 vs 96 sentences) because the translation omits the KNOW THIS
word block and splits a few sentences differently; both routes agree on the size of the effect.

## PROOF

| PROOF line | Result |
| --- | --- |
| Every headline number, one row each, the claimant's value and ours | PASS (Summary and each claim's table; the claims come from the scout notes, as there is no lane RESULTS.md) |
| Each row reproduced / differs (both values, reason) / not checked | PASS. Differs: 2a size (8.81 vs 8.635; solver 2's doublet list was not posted; trust ours, which is printed in full from the pinned loader; verdict unchanged); 3a count (~100 vs 83; word-mark convention; trust ours for our loader; verdict unchanged) |
| Our code next to the report, no lane code imported | PASS: `discord_claims_verify.py`, `discord_claim1_crosscheck.py`, `tools/solved_plaintext.py`; imports only `lp/` and `toolbox/` (no community code exists for these claims) |
| Re-running prints the report's numbers | PASS: a second full `--seed 1 --perms 100000` run is byte-identical to `discord_claims_out_seed1.txt` and `.json`. (`--only N` draws different nulls, because one random stream runs through the claims in order; its observed values are the same) |
| A control replayed on a fresh seed or fresh plaintext | PASS: seed 2 for every number; fresh plaintext (translation route) for claim 1; English and LP1 controls for claim 3 |
| Any `differs` row names the number to trust and whether the verdict changes | PASS (above) |
| Fixture `data/fixture/laneQ_verify.py` | PASS: `lag 6002: 304 6954 z=+4.18`, top lags 6002, 9428, 8686, 2039, 4908 |

This session stopped at the brief's bar and reported claim 1 to the orchestrator before the close-out. After the ruling
(not a lead), the CHANGELOG entry, the commit on round-two and the push to origin were done.
