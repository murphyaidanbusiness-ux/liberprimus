# laneM_title_cribs — title cribs at section and page openings: key-fragment recovery and structure tests

All code and outputs are in `SCRATCH/agents/laneM_title_cribs/`. Corpus: `lpdata.unsolved()`, sha 0233…1585 (asserted).

**Verdict: no signal.** Every fragment test sits on its null. Nothing beat the null, so nothing qualified for step 5 as a candidate. For the record, the single best real onward decryption was sent to the oracle anyway: English score −7.99, which is noise.

The positive control is only partly passed:
- **Keyword key (Vigenère, skip-on-repeat): recovered.** Detected at z = 13 by onward decryption, and by a dictionary extension that only the true fragment survived.
- **Running-English-text key (chain cipher): not recoverable from a title crib by any test.** This is a real power limit of the method, covered in §5.

## 0. What already existed (not repeated)

- **dukotah `armada20/cribdrag.py`:** 9 cribs (INSTAR, EMERGENCE, DIVINITY, WISDOM, THEPRIMES, PARABLE, SACRED, TOTIENT, CIRCUMFERENCE) dragged over every position of every page. Raw Vigenère K = C−P and K = P−C only. The implied key was scored by quadgram and by substring match against reference texts. No anchoring at openings, no chain or GF model, no skip rule, no null.
- **Ledger, other crib work:** "crib-drag fixed-function autokey" (XVII) and Hill crib-dragging (ARMADA-20).
- **Not found in the ledgers:** title cribs anchored at openings under chain / GF / skip-on-repeat / F-interrupt models with fragment-structure tests against nulls.

## 1. Openings and candidate cribs (`geom.py`, `vocab.py`, `cand_table.md`)

**Openings.** There are 17 section openings (chapter ids) and 55 page openings. 31 of the pages begin mid-word; for those, the opening is the next word start. Pages that coincide with a section are merged, which leaves **62 distinct opening positions**. The word lengths match the addendum.

**Spelling.** Cicada spelling: K/Q→C, V→U, Z→S, ING→NG, IO→IA, and greedy TH/EO/NG/OE/AE/IA/EA. Every word also gets its variants with IO split, ING as I+NG, and EA split, up to 8 per word. With the Cicada spelling INSTRUCTION is 10 runes, so "AN INSTRUCTION" fits section 1 (2,11) only with IO split.

**Vocabulary.**
- Cicada words: 939, taken from the koans/LP sections, the 2012–13 puzzle texts, the PGP messages, thematic.txt, words_expanded.txt and the solved titles.
- Cicada phrases: 2,107. These are every 1–3-word n-gram of those texts plus the 18 solved titles.
- Title words: 22,234. This is the noun list (taikuukaits SimpleWordlists, 91k) ∩ Google-20k, plus all abstract-suffix nouns (‑NESS ‑TION ‑ITY ‑MENT ‑ANCE ‑ENCE ‑DOM ‑HOOD ‑ISM ‑SHIP ‑URE …), plus the Cicada words. Kept at 3–12 runes.

**Templates.** Each template is matched against the first 1, 2 or 3 word lengths of the opening:

| template | form | source of the words |
|---|---|---|
| T1 | single title word | title words |
| T1c | single Cicada word | Cicada words, any length |
| PH | Cicada phrase | Cicada phrases |
| T2 | {A, AN, THE(TH-E), SOME} + title word | title words |
| T3 | {LOSS OF, END OF} + title word | title words |
| T4 | Cicada word + Cicada word | Cicada words |
| T5 | determiner + Cicada word + Cicada word | Cicada words |
| T6 | Cicada word + {OF, ON} + Cicada word | Cicada words |

**Candidate counts.** **1,431,517 crib candidates over the 62 positions** (1,644,247 if the sec/page duplicates are counted twice). The 17 section openings have 399,544 and the 45 page-only openings have 1,031,973. Per opening the count ranges from 1,104 (page 16, lengths 13,8,1) to 88,378 (section 7, lengths 4,2,5). The full per-opening table, with 1/2/3-word splits, is `cand_table.md`. Selected rows:

| opening | lens | cribs | | opening | lens | cribs |
|---|---|---|---|---|---|---|
| sec0/p0 | 8,5,4 | 17,822 | | sec9/p27 | 3,12,4 | 2,213 |
| sec1/p3 | 2,11,3 | 8,634 | | sec10/p33 | 2,8,2 | 12,102 |
| sec4 | 2,4,3 | 41,303 | | sec12 | 6,7,3 | 16,676 |
| sec7 | 4,2,5 | 88,378 | | sec16/p53 | 1,8,8 | 11,550 |
| sec8/p23 | 2,6,3 | 27,267 | | p16 | 13,8,1 | 1,104 |

## 2. Models and fragment counts (`frag.c`, mirrored in `pyfrag.py` and cross-checked against it)

- **Chain, additive mod 28.** u = B(D), with D = c_i − c_{i−1} ≠ 0. Doublet positions are dropped, so their key element is unknown and not consumed.
  - B is one of 14 step embeddings: s−1, 28−s, and the 12 discrete logs.
  - σ is one of 29 shifts, σ_s(p) = ((p+s) mod 29) mod 28, or Atbash.
  - Two forms: k = u−σ(p) and k = u+σ(p). The third form, σ−u, is the negation of the first and is covered because every test is negation-invariant.
  - That gives **840 models** (1,260 literal ones).
  - For section 0 / page 0 there is no previous rune, so its first increment is unknown.
- **Chain, GF(29) multiplicative.** x(EA) = 0 and x(p) = 1 + ((p+off) mod 28) or 1 + ((off−p) mod 28), with off = 0..27. Two forms: k = D/x and k = x/D. A crib that puts EA on a non-zero step is invalid. That gives **112 models**, each read in two views: raw k in Z29 and dlog₂k in Z28.
- **Vigenère k = c−p and Beaufort k = c+p.** Variant Beaufort is the negation of Vigenère, so it is covered. The skip-on-repeat variants allow one skip at any crib position j: the skipped key element is exactly c_{j−1}−p_j, so it is known, and the fragment gets length L+1.
- **F-interrupt.** For every model, crib positions with p = F and c = F are dropped and the key is not consumed there. The chain previous-rune pointer skips the interrupt.

**Fragments computed: 1,540,340,502 real.** By family:

| family | fragments |
|---|---|
| chain-additive | 1.202e9 |
| GF raw | 1.449e8 |
| GF dlog | 1.449e8 |
| Vigenère/Beaufort | 2.86e6 |
| skip-on-repeat | 2.83e7 |
| F-interrupt | 1.69e7 |

The nulls are the same size: 1.478e9 (R), 1.544e9 (P1), 1.547e9 (P2).

## 3. Nulls

- **nullR:** random rune cribs, one per real crib, with the same length and the same count (≥ 1,104 per opening; the brief asked for ≥ 200). Same openings.
- **nullP1 and nullP2:** the identical real crib lists applied at 62 random word starts, each ≥ 40 runes from every real opening. This keeps the strong correlation among real cribs (shared prefixes such as "AN …").

nullR understates the clustering of real cribs. Two examples:
- Its (a)-tail count is 924 against 1,236 and 1,219 for the two P nulls.
- Its (d) l=6 collision count is 1.74M against about 230k, because random cribs have many more distinct prefixes.

So **P1 and P2 are the operative nulls**. nullP2 drew two duplicate positions, and the (d) counts are computed with identical positions merged (`cross.py`).

## 4. Tests: real vs null

**(a) English-ness of the fragment.**
- Statistic: the 4-gram log10 score per rune under the best of its own 29 (or 28) shifts plus Atbash. The LM is lane A's Cicada-transliterated English 4-gram, made conditional (`common.lm_tables`).
- p-values come from the pooled nullR histogram for the same family and fragment length. Fragments shorter than 5 runes are excluded.
- IoC was not used per fragment, because for 4–15 runes it has no resolution. The 4-gram score contains the unigram/IoC signal.

| statistic | real | nullR | nullP1 | nullP2 |
|---|---|---|---|---|
| fragments with p ≤ 1e‑4 | 130,493 | 124,148 | 131,828 | 135,630 |
| fragments with p ≤ 1e‑5 | 11,428 | 10,658 | 11,232 | 12,765 |
| fragments with p ≤ 1e‑6 | 1,267 | 924 | 1,236 | 1,219 |
| global best −log10 p | 8.60 | 7.66 | 8.60 | 8.62 |

- Openings where the real best beats all three nulls at that opening: **17/62**. Chance expectation is 15.5.
- The best real fragment is at page 11, crib "XIYP OF HAS", model chain[dlog2,sh19,u−s], n = 9. The crib is junk, as are the other top fragments: "MIT REMAIN" at page 7, "SOME PRIME NEXT" at section 6, "REALITIES ARRIVED" at page 4.

**(b) Keyword-ness.** Does the fragment, up to a shift and/or negation (Z28 or Z29), equal a window of a periodically repeated keyword? The keywords are 22,796 rune spellings (Google-20k + Cicada vocabulary + solved titles). Lookup is a hash of the difference sequence.

**(c) Numeric-ness.** Same lookup against windows at offsets 0..13,599 of these sequences, mod 28 and mod 29:
- n, 3301·n, n², n³, triangular numbers
- primes, prime gaps, cumulative prime sums, Fibonacci, Lucas, φ(n), φ(p)
- π digits, 2ⁿ, 3ⁿ
- page number per rune
- Gematria prime values of the solved titles, and of the solved-text runes

**(e) Recurrence.** Same lookup against every run of these streams, excluding a window around the opening itself:
- the raw stream, D, raw mod 28
- the 14 step-embedded increment streams

Hits per million fragments, with z of real against the three nulls (between-null sd):

| test | n 4–5 | n 6–7 | n 8–9 | n 10–12 | n ≥ 13 |
|---|---|---|---|---|---|
| (b) keyword: real / R / P1 / P2 | 646,977 / 649,280 / 581,028 / 682,345 (z 0.2) | 6,084 / 6,053 / 5,539 / 5,569 (z 1.3) | 10.1 / 10.3 / 12.0 / 9.2 (z −0.2) | 0 / 4 hits / 0 / 0 | 0 everywhere |
| (c) numeric | 242,453 / 241,920 / 218,365 / 256,531 (z 0.2) | 2,663 / 2,874 / 2,505 / 2,626 (z 0.0) | 5.2 / 5.0 / 5.4 / 3.8 (z 0.6) | 0 / 12 / 2 / 0 | 0 |
| (e) recurrence | 527,414 / 529,657 / 484,950 / 548,596 (z 0.2) | 5,106 / 5,199 / 4,660 / 4,642 (z 0.9) | 8.0 / 7.9 / 8.6 / 6.1 (z 0.3) | 0 | 0 |

- **No real fragment longer than 9 has a keyword, numeric or recurrence match.**
- Per family (n ≥ 8), real is inside the null range in every cell. The one apparent excess, F-interrupt numeric (104 real against 50 / 30 / 0), is 44 copies of a single crib under shift-equivalent models. That is clustering, not a key.
- **Continuation check** (key running through the book). Numeric hits whose window offset equals the opening's absolute key index (position, or position minus preceding doublets, ±1): real 0 of 5,114, nullR 0, P1 0, P2 0.

**(d) Cross-opening consistency** (key restarting per section or page; `cross.py`).
- Statistic: pairs (opening₁ ≠ opening₂, crib₁, crib₂) whose fragments agree exactly on their first l elements under the same model.
- Models: 840 chain-additive + 112 GF + 2 Vigenère/Beaufort, all pairs of the 62 positions.

| l | real | nullP1 | nullP2 | nullR (not comparable) |
|---|---|---|---|---|
| 6 | 229,339 | 236,734 | 221,876 | 1,737,740 |
| 8 | 653 | 1,004 | 747 | 1,667 |
| 10 | 0 | 0 | 8 | 2 |

The addendum's named template pairs give the same picture (`named.py`):
- AN INSTRUCTION (sec1, IO split) / AN INSTAR (sec8) / AN EPIPHANY or AN AWAKENING (sec10): their fragments agree on **0** leading elements under every model. They cannot agree on the first, because D₀ differs between the openings.
- Best English-ness z of these named cribs against the same crib at 100 random word starts (`named_null.json`):

  | crib | z |
  |---|---|
  | AN EPIPHANY | +0.9 |
  | AN INSTAR | +0.2 |
  | AN AWAKENING | −1.7 |
  | AN INSTRUCTION | −1.8 |

- Other suggested titles (LOSS OF DIVINITY at sec7, AN END at sec4, A KOAN at sec16, PARABLE at sec12) do not fit the opening word lengths.

**(f) Extension** (`ftest.py`, `ext2.py`).
- The top 100 fragments per run, de-duplicated by crib and canonical fragment: 40 by (a) p-value, plus the 20 longest hits each for (b), (c) and (e).
- Each is extended by every dictionary word of the next word's rune length (Google-20k + Cicada spellings), beam 5, 3 rounds.
- For (a) the statistic is the z of the extended key against random fragments of the same length. For (b), (c) and (e) the question is whether any extension keeps a hit of the same type.

| run | (a) mean z after rounds 1/2/3 | (a) max | (b) surviving 1/2/3 words | (c) | (e) |
|---|---|---|---|---|---|
| real | 13.8 / 16.9 / 18.5 | 21.9 | 4/0/0 | 3/0/0 | 2/0/0 |
| nullP1 | 14.4 / 17.2 / 18.4 | 21.0 | 1/0/0 | 0/0/0 | 2/0/0 |
| nullP2 | 14.1 / 17.3 / 18.6 | 21.4 | 7/1/0 | 3/0/0 | 2/0/0 |

**Nothing real keeps its structure past one extension word.**

**Step 5: onward decryption of every structural hit** (`step5.py`, `onward.py`).
- Every keyword, numeric or recurrence hit with n ≥ 8 implies a key, up to the shift or negation fixed by alignment, that continues past the crib.
- The next 60 runes were decrypted under it with the same model. A beam of 12 resolves the skip-on-repeat branch and the 29→28 σ collision. The plaintext was scored with the LM.

| run | decryptions | mean | sd | max |
|---|---|---|---|---|
| real | 18,340 | −1.831 | 0.078 | **−1.609** |
| nullR | 17,218 | −1.827 | 0.079 | −1.579 |
| nullP1 | 19,817 | −1.830 | 0.077 | −1.581 |
| nullP2 | 15,171 | −1.833 | 0.077 | −1.606 |

- **0 real decryptions exceed any null's maximum.**
- The real best is page 12, keyword LITHUANIA, chain[dlog19,sh5]: `OEAEDJBGRNGNGIIAYOAOCGNJMOREXNAEPXCAEXIWFGEATHOGEA`.
- Sent to the oracle with `--plaintext` (`oracle_best_real_pt.json`): English score −7.99, which is noise. A plaintext-only submission is NOT-ADJUDICABLE by design.
- No keystream qualified for a `--keystream` submission.

## 5. Positive controls (`control.py`, `ctrl_ext*.py`, `step5.py control5`)

**Setup.** The solved A KOAN text, 742 runes, was placed at section 0's slot: position 0, with no previous rune, like section 0. The pipeline was run with the control's own opening word lengths (1,4,1). That gives 4,778 candidate cribs, and "A KOAN" and "A KOAN A" are among them. There were five nullR replicates with the same cipher.

**(ii) Vigenère with skip-on-repeat, keyed by PILGRIMAGE.**

| check | result |
|---|---|
| A KOAN fragment (n = 5) | P‑I‑L‑G‑R, a (b) hit; but 35% of n = 5 fragments hit by chance |
| A KOAN A fragment (n = 6) | a hit; background 1.7% (53 of 3,152); (a) z = +1.89, p = 0.05 |
| (f) extension keeping a keyword hit, 270 n ≥ 6 keyword hits at the control | 243 survive 1 word, 28 survive 2, **1 survives 4 words: A KOAN A under vig c−p**; nulls: 0 of 1,170 survive 4 words |
| step-5 onward decryption | `MANDECIDEDTOGOANDSTUDYWITHAMASTERHEWENTTO`, score −0.829 against null −1.796 ± 0.074 (max −1.580): **z = 13.0** |
| oracle `--plaintext` | −4.07, English |

So (b) on its own does not reach z > 5 on a 5–6-rune title. (b) + (f) and (b) + onward decryption do.

**(i) Chain cipher keyed by running English text** (Emerson, Self-Reliance).
- The true fragment (n = 4–5, because the first increment is unknown at position 0) has (a) z = −0.53, p = 0.72. More than 960k of the 1.32M fragments in the same family and length score higher.
- Dictionary extension of the true crib and model gives a z trajectory of 1.4 → 4.8 → 9.5 → 12.5. Random crib/model pairs reach 14.4 ± 1.3 (max 17.7), because with both plaintext and key free, the extension finds an English key for any crib. True against null: **z = −1.4**.
- The same weakness shows on control (ii) under the (a)-extension (z +0.9), which is why the (a)/(f) rows in §4 are uninformative by construction.

**Result.** The pipeline has demonstrated power for keyword and structured keys, and **no power for a running-text key from title-length cribs**. A z > 5 on (a) is not attainable from 4–15-rune fragments.

## 6. Verdict per family

- **Chain additive mod 28** (14 embeddings × 30 σ × 2 forms) **and GF(29) multiplicative** (112), with doublets as unknown/skipped:
  - Fragments at every opening under 1.43M title cribs show no keyword, numeric, Gematria or recurrence structure above null at any length.
  - No hit longer than 9 runes; no cross-opening restart agreement above null.
  - **Excluded for structured keys** (periodic keyword from the 22.8k-word list, the listed sequences, cipher-derived streams) starting at a section or page opening with a title from this candidate set.
  - **Not excluded for running-text keys** (no power, per control (i)).
- **Vigenère/Beaufort/variant Beaufort, with and without skip-on-repeat:** same verdict. The control shows that this family's keyword case would have been found (z = 13).
- **F-interrupt variants:** same verdict.
- **Key restart per section/page:** no evidence at l ≥ 8. Real 653 vs nullP1 1,004 and nullP2 747 at l = 8; 0 vs 0 and 8 at l = 10.
- **Limits.**
  - Title vocabulary: the noun and Cicada lists. Two-word title pairs were limited to Cicada words.
  - The models enumerated are the addendum's list (1)–(3). Lane K's free walk is out of scope, because a short crib does not open it.
  - The key-restart test uses exact equality.
