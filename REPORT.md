# Liber Primus (Cicada 3301) — full campaign report, 2026-10-08/09

**Outcome: not cracked.** LP2 pages 0–54 (12,956 runes) remain unsolved. Two days, five research scouts, fourteen
attack lanes (A–N), and my own structural tests. Every attack came back at calibrated noise, with planted-key
positive controls recovered in every lane. What the campaign produced instead is a set of hard, language-agnostic
constraints that narrow the cipher to one family and show that family has no searchable key without outside material.

Everything is reproducible: SCRATCH/lp/*.py (my tests and verifier), SCRATCH/agents/lane*/RESULTS.md (each lane's code,
raw outputs, nulls), SCRATCH/research/*.md (scout reports and SYNTHESIS.md).

## The constraints (each verified by me, independent of the lane that found it)
1. **Flat at every order.** IoC 1.000; no periodicity whole-corpus (1..1500), per section, per page (2..40), or aligned to
   word starts (cosets by position-in-word, L = 1..12); no key shared between sections; linear complexity n/2.
2. **Doublet deficit.** 86 adjacent repeats vs 447 expected; geometric gaps; uniform over runes; present within words
   (0.63%) and across word, line and page seams (0.79%). Conditional IoC of next rune given previous = 1.026, exactly the
   flat-increment prediction: any FIXED feedback table is excluded (~245σ). The key varies by position.
3. **Repeated cipher words are at chance.** 16 repeated cipher words of ≥3 runes vs 11.0 ± 3.1 for a random stream vs
   999 for English of the same size. The cipher's state is essentially never the same at two occurrences of a word:
   any cipher with a small per-word state (K alphabets × phase) is excluded by counting (K = 5 would force ≥ 482).
4. **The layout is not plaintext layout.** Word-length marginal fits English with THE/OF absent, but adjacent lengths are
   independent (z = +0.9 vs +7..+15 for English of the same size, +4 for Cicada's own solved pages); sentence-first and
   sentence-last words have average length (z = −0.2 / −0.7; English: first words short, last words +1.65 runes);
   line breaks are a variable-glyph-width fill. Two community members (mae3301, Oosterhof) reached the same in 2026.
5. **One weak word-aware signal.** Within-word lag-5 coincidence 4.94% vs 3.45% (z = +3.75 raw; ~2.5σ after correcting
   for the lag scan; also found by ZzNible and Oosterhof). Diffuse across positions and sections. Not explained by any
   word-restarted key (cosets flat) or by any visible phase rule (word length, index, line, page, sentence, previous
   word, first rune, previous rune: all null).
6. **The chain-with-EA model is refuted.** EA is ~90% word-medial in English, so a chain whose zero step is EA predicts
   4–12 cross-word doublets; the book has 23 (p ≈ 1e-11). If the cipher is a chain, its zero step is key-set.

## What the constraints leave
Exactly one cipher shape is consistent with 1–6: a polyalphabetic walk where alphabets cycle with period 5 inside words,
the base alphabet evolves after every word, and a skip-on-repeat rule suppresses doublets (Oosterhof's model). Its key
is ~180–280 bits if the permutations are free. Lane K showed it cannot be reached by global search: with everything but
one permutation given, 0 of 63 annealing runs recovered it (one wrong transposition → chance accuracy), and beam search
needs ≥ 2^90 hypotheses. Lanes M and N then closed the crib route: a keyword key starting at any section or page opening is excluded (M), and a running-text key of ANY English text is excluded for cribs ≥ 20 runes (N). Lane L exhausted its keyword-built corner (2^55.6 keys per start, 20,645 keywords, 220k
alphabets, 1.13M order-5 permutations, three clock variants): null. Lane L also derived that under this model every
within-word doublet must be a doubled plaintext letter drawn from the 4 fixed runes of the step permutation, a further
strain on the model itself.

## Attack lanes (all null; every lane's planted control recovered)
| lane | family | scale | real vs null |
|---|---|---|---|
| A | per-page/section keyword chain attack, 362,700 keys, 128 variants, C/OpenMP | ~2×10⁹ decryptions | best −6.4 (English −4.2); oracle FAIL |
| B | hash/KDF keystreams (MD5…BLAKE2b, HMAC, PBKDF2), 3,400 seeds, 20 mappings, chain + GF(29) + OTP | 152M trials | 1.0279 vs null max 1.0287 |
| C | gematria-number keystreams, full period; word-sum/prime autokeys; per-word keys | ~2M offsets | max z 7.7 vs null 7.2 ± 0.4 |
| D | 7 alternative constructions, each with predicted signature | — | each excluded or indistinguishable from chain |
| E | plaintext language from word structure, 906 distributions | — | English minus THE/OF; all other languages rejected |
| F | word-length alignment vs 149 texts (15.7M words), 42 models | full local alignment | real 10–15 vs shuffle 9–12 (plants 68–437) |
| G | era-correct PRNGs (CPython 2.7/3.2 string seeds, glibc, PHP, Java, MSVC, numpy), bit-exact, 143,022 seeds, runes/increments/key | 16.9M streams | best run 10 = chance (10.2) |
| H | book-code pointers into Self-Reliance (parser validated on the real 2014 code), Liber AL, Mabinogion, 16 views × 14 sources | 10,880 configs | best z 5.2 vs noise replicates 5.6–5.8 |
| I | layout as cover channel, 22 channels × encodings | 221k cells, 200 nulls each | 9 cells < 0.05 of 102 (5 expected); no readable fragment |
| J | lag-5 echo: corrected significance, 23 simulated mechanisms | — | only Oosterhof's walk fits; chain-with-EA refuted |
| K | global search for the walk: feasibility ladder | 5/5 plants on fixed-alphabet model; 0/63 on walk | fixed-alphabet model excluded by counting |
| L | keyword-built walk keys, 2^55.6 per start, 3 clock variants | 4–8 min per start | z ≤ 1.9, never above null max |
| M | title cribs at 17 section + 55 page openings: 1.43M cribs (Cicada phrases/words, 22k title nouns, A/AN/THE/SOME/LOSS OF templates) × chain (14 bijections × 30 σ), GF(29) (112 models), Vigenère/Beaufort ± skip, F-interrupts; 6 fragment-structure tests vs random-crib and random-position nulls | 1.54×10⁹ fragments; 18,340 onward decryptions | every test on null; control: keyword+skip recovered from a 5-rune title (z 13) |
| N | full-position crib drag: 5,075 cribs (solved part-one sentences, Cicada phrases, common words, word-aligned and not) × chain Z28/GF(29), Vigenère/Beaufort ± skip, ± F-deletion; 3 signatures; fragment search vs 53M runes of text | ~2×10¹⁰ fragments, 72 null runs | real max below null max in all 125 cells; control: running English key found from any crib ≥ 20 runes (z 10–18) |
| me | periodicity/locality on increments; GF(29) sequences; doublet side channel; word-aligned cosets; phase rules; repeated-word count | — | all null |

On top of the community record: autokey; ~200 running-key texts; 46 integer sequences; all 2^32 MT integer seeds;
14.5×10⁹ offsets into public randomness; Outguess of every image; Berlekamp–Massey; hidden structural channels.

## Assessment
The ciphertext contains no exploitable regularity beyond "not equal to the previous rune" and a 2.5σ word-internal
echo. The only consistent cipher family has a key too large and a landscape too flat for any search, and its short-key
corner is empty. Every key source Cicada demonstrably used (their vocabulary, their book-code texts, their era's
generators, their numerology) is exhausted. Solving LP2 now requires outside material: a long crib, a body page
solved by other means, the never-found page-56 hash target, or 3301 itself. That is the same conclusion the best
community analysts hold, now with a counting bound (constraint 3) and a layout analysis (constraint 4) behind it.

## What is worth passing to the community
Constraints 3 and 4 and the lane G/L exhaustions are new or newly quantified; Oosterhof's aldegonde repo and the
CicadaSolvers Discord are the venues. Everything needed to reproduce them is in this scratchpad.
