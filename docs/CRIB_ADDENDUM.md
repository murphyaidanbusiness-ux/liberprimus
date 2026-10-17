# Crib addendum (read with BRIEF_COMMON.md)

## State of the models after lanes A–L (all in SCRATCH/agents/lane*/RESULTS.md; read J, K, L)
- The chain model with EA as the zero step is refuted (cross-word doublets). If the cipher is a chain c_i = c_{i-1} + s_i, the zero step is key-set, so treat doublet positions as "key value unknown / skipped" rather than as a known letter.
- Any cipher with a small per-word state (K alphabets × phase) is excluded by counting (16 repeated cipher words vs ≥ 482 required).
- The only cipher shape consistent with all statistics is Oosterhof's evolving walk; its keyword-built corner is exhausted (lane L), and its free form cannot be searched without an outside handle (lane K). A short crib does NOT open the free walk (it fixes a few entries of base_0 only); do not spend time there unless you find a construction where it does.
- Decryptable models where a crib DOES give leverage, because the crib yields a key fragment directly:
  (1) chain: k_i = (D_i - 1 - σ(p_i)) mod 28 for D_i ≠ 0, σ ∈ {29 shifts, Atbash, reversed, the 12 discrete-log bijections of lane J/K if available}; GF(29) form k_i = D_i · x(p_i)^-1 with x(EA)=0 and the 28 offsets.
  (2) raw Vigenère / Beaufort / variant Beaufort: k_i = c_i - p_i, p_i - c_i, etc., with the skip-on-repeat convention (if c_i == c_{i-1} would have occurred the key advanced: model this as 'key index may advance by one at doublet positions').
  (3) F-interrupt conventions from the solved pages (F rune skipped, key not consumed).
- Dukotah has a crib-drag tool at SCRATCH/dl/dukotah/liber-primus/analysis/armada20/cribdrag.py: read it and its results first; do not repeat its exact runs; record what it covered.

## Crib geometry (my extraction, SCRATCH/lp data; sentence marks are unreliable as sentence ends, so treat 'first sentence' loosely)
section openings: chapter id, page, word lengths of the first 8 words, (first sentence mark after word N)
  0 p0  [8,5,4,3,3,11,5,4] (N=2)     1 p3  [2,11,3,4,7,7,7,4] (N=3)    2 p3  [3,3,3,2,2,5,6,3] (N=1)
  3 p6  [4,1,4,2,7,6,3,3] (N=4)      4 p7  [2,4,3,2,3,4,8,3] (N=2)     5 p8  [4,8,3,2,3,9,4,3] (N=2)
  6 p15 [4,5,4,2,5,4,5,6] (N=2)      7 p15 [4,2,5,4,5,6,5,6] (N=3)     8 p23 [2,6,3,5,8,3,3,7] (N=4)
  9 p27 [3,12,4,7,2,3,3,2] (N=3)    10 p33 [2,8,2,9,6,3,3,5] (N=2)    11 p33 [3,5,6,7,4,3,4,2] (N=2)
 12 p38 [6,7,3,2,10,2,7,5]          13 p39 [3,4,6,5,4,3,5,6] (N=1)    14 p40 [3,5,5,4,3,5,4,2] (N=2)
 15 p50 [3,6,5,5,3,4,3,3]           16 p53 [1,8,8,3,6,2,5,3] (N=2)
Solved part-one titles for the pattern: A WARNING (1,7), SOME WISDOM (4,6), A KOAN (1,4), WELCOME (7), AN INSTRUCTION (2,11), LOSS OF DIVINITY (4,2,8), AN END (2,3), PARABLE (7), INTERCONNECTEDNESS. Fits: section 1 = AN INSTRUCTION (2,11); section 8 = AN INSTAR (2,6); section 10 = AN EPIPHANY / AN AWACENING (2,8); section 7 = LOSS OF ????? (4,2,5); section 16 = A ???????? ???????? (1,8,8); section 4 = AN ???? (2,4). Build the full candidate list mechanically from the Cicada vocabulary (lane A folder) and a title-word list (English nouns/abstract nouns 3–12 runes under Cicada transliteration), filtered by the length pattern of the first 1–3 words of each section and each page (page-opening lengths are in SCRATCH/lp output of the extraction; recompute from the loader).
