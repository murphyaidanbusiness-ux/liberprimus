# Lane R: are the doublet deficit and the lag-5 echo robust to the transcription?

Scope: every rune transcription found under `dl/` (lineage-scanned, 87 files with at least 100 runic characters), placed on loader pages 0-54 (12,956 runes), compared with `lp/lpdata.py`. `lp/` was not modified.

## Verdict

- **Reproduction.** Loader: 12,956 runes, sha 023312066df4... (asserted). Doublets 86 (within-word 63, cross-word 23). Within-word lag-5 coincidence 104/2105 = 4.94%, z = +3.75 against 1/29. Both numbers reproduce exactly.
- **Doublet deficit: robust to transcription.** Every full-book reading except the two low-fidelity ones (V, T) gives 86 doublets: all copies of the loader's rune stream, the J-normalised variants, AU, S, H, and the classifier CL under its substitutions. Within/cross is 63/23, or 64/22 under scream314's sentence-end convention; the total does not depend on word boundaries by construction. Expected count for a uniform 29-symbol stream is (N-1)/29 = 446.7, so 86 is about 0.19 of uniform.
- **Lag-5 echo: present in every full-book reading, with the convention caveat.** z = +3.63 to +3.96 across the readings (A and M +3.86, MT and M2 +3.86, H +3.96, R, AU and L +3.75, CL +3.63 under its substitutions). The exception is scream314's sentence-end convention at +3.26. The echo depends on the word-boundary convention: +3.14 if sentence ends are not breaks, +2.06 if line breaks are word breaks (rate 4.38%, n = 1645). All stay above +2 under the conventions tested, but the magnitude is convention-dependent.
- **Error tolerance (control).** Random replacement of reference runes (boundaries kept): z stays above +2 up to about 20% corrupted positions (+2.26), falls to +1.34 at 35%, and is -0.25 at 100%. Doublets rise from 86 to 94 (1%), 121 (5%), 154 (10%), 211 (20%), 431 (100%).
- **Low-fidelity readings** (vision 14.95% identical, template 65.8% of covered runes) are not usable as transcriptions; their subs-only statistics are reported but not interpreted.

## Reproduction commands (from repo root)

    python -I agents/laneR_transcriptions/compare.py K A M MT M2 AU S S2 H R C J P V T RN H+J R+J RN+J L L+J CL C1B C1A IN > agents/laneR_transcriptions/out_compare.txt
    python -I agents/laneR_transcriptions/compare.py lineage > agents/laneR_transcriptions/out_lineage.txt
    python -I agents/laneR_transcriptions/compare.py corruption > agents/laneR_transcriptions/out_corruption.txt

Files: `transcriptions.py` (loaders for each file format), `compare.py` (alignment, boundary decoding, statistics, lineage, corruption control), `out_compare.txt`, `out_lineage.txt`, `out_corruption.txt`, `per_page.tsv` (per-page substitutions/insertions/deletions for paged families).

## Transcriptions found (lineage by sha of the runic-character stream)

Runic-stream sha is `sha256(runic characters)[:12]`; count = runic characters in the file (all 30 symbols; U+16C2 counted separately).

| Id | Runic sha / count | Files (under dl/) | Relation to loader pages 0-54 |
|---|---|---|---|
| K | ee1b43cf7534 / 13136 | dukotah/liber-primus/data/krisyotam_runes.txt (loader source); aldegonde_clone/data/page0-58.txt; corpus/B-liber-primus/fetched/r4nd0mD3v3l0p3r__LiberPrimusSolver/data/unsolved.txt; analysis/foundation/consensus_runes.txt; analysis/foundation/trans_krisyotam.txt; analysis/vision/canonical_pages.json | reference |
| A | 79b14e630946 / 12956 (pages 0-54 only) | aldegonde_clone/data/page0-56.txt; analysis/foundation/trans_relikd.txt; analysis/foundation/trans_uncovering_wiki.txt | identical runes; aldegonde's own word marks |
| M | ee1f3d0d10e9 / 15933 | aldegonde_clone/data/liber-primus__transcription--master.txt; corpus/B-liber-primus/fetched/Taiiwo__cicada/cicada/liber_primus.txt (MT); fetched/zenodo_18199474/liber-primus__transcription--master.txt; corpus/E-tooling/iddqd_versions/master_3089b65.txt, master_ed95eb7.txt, master_cicadasolvers_4bbb9680.txt | identical runes; M uses aldegonde marks, MT uses krisyotam separators |
| M2 | b2ca5aa9cd6e / 15935 | corpus/E-tooling/iddqd_versions/master_218ed88.txt | identical runes on 0-54; differs only in LP1 prefix |
| AU | 22ff1d0fbf23 / 15843 | corpus/B-liber-primus/fetched/aautcsh__idkfa/data/liber; assets/liber-primus-crc-chapters.txt; assets/liber-primus-crc-words.txt | one substitution and one deletion on 0-54 |
| AU-crc | 4302e31634df / 15857 | fetched/aautcsh__idkfa/assets/liber-primus-crc-pages.txt | AU plus 14 inserted U+16A0 (interrupter-rune page markers); not a new reading |
| S | 5cdffa884f16 / 15938 | dukotah/liber-primus/data/scream314_lp.md; H-branch-recovery/.../scream314_liber_primus.md; fetched/aautcsh__idkfa/assets/liber-primus-translation.txt | scream314 full book (2801 LP1 runes + S2) |
| S2 | 913ad7ceebd2 / 13137 | analysis/foundation/trans_scream314.txt | LP2 part of S, rune-only |
| H | 7b201738a6c3 / 13072 | fetched/henkman__liberprimus/liberprimus.txt and liberprimus.go | U+16C2 for J; page 0 missing 54 runes |
| R | 13db850ea9b5 / 13136 | fetched/transcriptions.rne | U+16C2 for J; otherwise identical |
| C | 41340f45a33d / 13041 (pages 0-55) | analysis/foundation/trans_cicadasolvers.txt; trans_r4nd0mD3v3l0p3r.txt | identical runes on 0-54 |
| L | 1e2213107640 / 26881 (17 sections = 13136 runes) | aldegonde_clone/lp_section_data.py; src/lp_section_data.py (mortlach/lp-decrypter) | U+16C2 for J; word-level, boundaries agree exactly with the loader |
| J | e50f29254333 / 13166 | dukotah/liber-primus/dataset/liber_primus.json | identical runes on 0-54 |
| P | bcf5c9ba375d / 14979 | corpus/B-liber-primus/PAGES.json | identical runes on 0-54 (includes LP1) |
| V | 7347abdd8c29 / 14929 | analysis/vision/vision_results.json (automated re-reading) | 14.95% identical |
| T | 062131a9d853 / 9188 | analysis/structure/template_transcription.txt (self-labelled low confidence) | 48 of 55 pages |
| CL | 05dc05f69823 / 12764 | analysis/stones/classifier_transcription.txt (automated) | 98.17% identical, 192 deletions |
| RN | a52b150f0a39 / 776 (pages 40-42) | fetched/thomasandfriends__Cicada3301Runes/data/runes4012 (runes4012~ is a 272-rune backup, not analysed) | partial, U+16C2 for J |
| C1B | 4f42736d9ccc / 1433 (pages 27-32) | corpus/E-tooling/c1cada_versions/page.27-32_fe9b225.txt | identical after J normalisation |
| C1A | a0ad9981f483 / 1674 (partial) | corpus/E-tooling/c1cada_versions/page.27-32_f75c1de.txt | different segmentation; 65.1% identical in best window |
| IN | 7ecb645e3b05 / 262 | fetched/r4nd0mD3v3l0p3r__LiberPrimusSolver/testResources/input.txt | exact copy of loader page 0 with the same boundaries |

Excluded because they are not readings of the pages: word-guess and solver output (aautcsh liber-primus-word-guesses.txt), repeat-attack results, DIFF-REPORT.md, divergence_classified.json and hunt_results.json (classification records; they name repos not present in dl/, e.g. an iddqd "sentences" file of 15,856 runes), n-gram tables, LP1 solved pages (firstKoan, welcome, aWarning), an ibotpeaches directory of PGP messages, Taiiwo code, and the notes files. dl/leo and dl/theron contain no rune transcription.

Separator semantics (decided by cross-tabulation against K's separators on aligned runes, `out_compare.txt`):
- K (loader): `-`, `.`, `&`, `$` start a word; `/` marks a line break and the loader does not count it as a word break (of 593 occurrences, 173 coincide with a word start and 420 fall mid-word); `%` is a page break.
- aldegonde (A, M): every aligned circled mark sits at a K word start (no exceptions). U+2460 (①) lies on K `-` in 2,721 cases and on K `.` in 5; U+2463 (④, 139 cases), U+246C (⑬, 25), U+2462 (③, 5) and U+2469 (⑩, 2) lie on K `.` positions. Start marks = {①, ③, ④, ⑩, ⑬, -, ., &, $}.
- henkman, rne, scream314, RN: U+2022 (•) = word break. rne's `:` (27 + 1) and `,` (3) occur only at K word starts that carry K's `.`, so they are counted as breaks; with that choice rne differs from K at 2 word starts (p03, p37).
- c1cada (C1B, C1A): U+2022 (•) = word break.
- mortlach (L): one token per word; word starts = K word starts exactly.

## Per-file alignment against the loader (pages 0-54)

Rune-level: identical = aligned reference positions with the same symbol. "J" rows read U+16C2 as J (the convention in henkman, rne, mortlach, runes4012 and c1cada fe9b225; `codepoint_aliases_normalised` in hunt_results.json lists the same U+16C2 to U+16C4 alias). The J relabelling is a bijection on the J positions, so it does not change any statistic (verified: raw and J rows give identical doublets and lag-5).

| Family | Runes placed | Identical | Substitutions | Insertions | Deletions | Word starts lacking / extra (vs K) | Pages with any difference |
|---|---|---|---|---|---|---|---|
| K | 12956 | 100.00% | 0 | 0 | 0 | 0 / 0 | 0 |
| A | 12956 | 100.00% | 0 | 0 | 0 | 2 / 0 | p37 (K `./-` vs `/`), p50 (K `./&` at page 49 end vs none) |
| M | 12956 | 100.00% | 0 | 0 | 0 | 2 / 0 | same as A |
| MT | 12956 | 100.00% | 0 | 0 | 0 | 1 / 0 | p50 |
| M2 | 12956 | 100.00% | 0 | 0 | 0 | 1 / 0 | p50 |
| AU | 12955 | 99.98% | 1 (p24 AE to A) | 0 | 1 (p33) | 0 / 1 (p20) | p20, p24, p33 |
| S | 12956 | 99.99% | 1 (p24 AE to A) | 0 | 0 | 174 / 0 | 174 word starts on 53 pages (173 at K positions marked `.`, 1 at a bare `-`; max 7 per page) |
| S2 | 12956 | 99.99% | 1 (p24) | 0 | 0 | rune-only | p24 |
| H | 12892 | 96.04% | 447 (445 J to U+16C2; 2 B to W) | 2 | 66 | 4 / 1 | 55 (J) |
| H+J | 12892 | 99.48% | 2 (B to W, p33) | 1 | 65 | 4 / 1 | p00 (del 54), p03 (del 5), p06, p19, p26, p33, p35, p39 |
| R | 12956 | 96.53% | 450 (all J to U+16C2) | 0 | 0 | 1 / 1 | 55 (J) |
| R+J | 12956 | 100.00% | 0 | 0 | 0 | 1 / 1 (p37, p03) | none |
| L | 12956 | 96.53% | 450 (all J to U+16C2) | 0 | 0 | 0 / 0 | 55 (J) |
| L+J | 12956 | 100.00% | 0 | 0 | 0 | 0 / 0 | none |
| C | 12956 | 100.00% | 0 | 0 | 0 | rune-only | none |
| J | 12956 | 100.00% | 0 | 0 | 0 | rune-only | none |
| P | 12956 | 100.00% | 0 | 0 | 0 | rune-only | none |
| RN | 776 (pp. 40-42) | 96.01% of covered | 31 (all J) | 0 | 0 | 0 / 0 | pp. 40-42 (J) |
| RN+J | 776 | 100.00% | 0 | 0 | 0 | 0 / 0 | none |
| C1B | 1433 (pp. 27-32) | 100.00% | 0 (51 J) | 0 | 0 | 0 / 0 | none |
| C1A | 1674 (partial) | 65.11% of window | 36 | 548 | 548 | 12 / 7 | not analysed further |
| IN | 262 (page 0) | 100.00% | 0 | 0 | 0 | 0 / 0 | none |
| CL | 12764 | 98.17% | 45 | 0 | 192 | rune-only (reference boundaries) | flat alignment, 49 pages with events |
| V | 13420 | 14.95% | 1614 | 9869 | 9405 | rune-only | all 55 |
| T | 9156 (48 pages) | 65.78% of covered | 721 | 1097 | 3097 | rune-only | 48 covered pages |

Notes:
- H page 0 lacks one contiguous block of 49 runes (reference positions 134-182 of page 0, 0-based) plus 4 at 117-120 and 1 at 188, so henkman's own stream (raw `own` row below) is not a like-for-like test; the `bnd` row is.
- The page-50 boundary disagreement (K `./&`) reflects that A, M, MT, M2 and H end LP2 page 49 without the chapter and sentence marks K carries (rne ends it with `:`).
- The page-37 disagreement (K `./-`, with word start) is shared by A, M, H and R; MT and M2 agree with K there.
- The aldegonde art-letter block before runeless page 50 is removed as non-rune text; it carries no runes or word starts.

## Statistics (flat stream, reference positions)

Variants: `ref` = reference runes and boundaries. `bnd` = reference runes with the family's word starts where aligned. `subs` = reference boundaries with the family's substitutions only (indels leave the reference symbol). `own` = the family's full stream (runes and boundaries, indels included). Lag-5 = within-word pairs (a, a+5) that agree; z against 1/29.

| Family / variant | Doublets (within / cross) | Lag-5 hits / n | Rate | z |
|---|---|---|---|---|
| Reference (K) | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |
| A, M (bnd) | 86 (63 / 23) | 105 / 2108 | 4.98% | +3.86 |
| MT, M2 (bnd) | 86 (63 / 23) | 105 / 2108 | 4.98% | +3.86 |
| AU (own) | 86 (63 / 23) | 104 / 2104 | 4.94% | +3.76 |
| S, scream314 (bnd = own) | 86 (64 / 22) | 117 / 2527 | 4.63% | +3.26 |
| S2 (subs) | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |
| H (bnd) | 86 (63 / 23) | 106 / 2111 | 5.02% | +3.96 |
| H (own, with 66 deletions) | 86 (63 / 23) | 106 / 2093 | 5.06% | +4.05 |
| R, R+J, L, L+J, C, J, P, RN, IN (subs / bnd / own) | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |
| CL (subs) | 86 (63 / 23) | 103 / 2105 | 4.89% | +3.63 |
| V (subs; 1614 substitutions) | 171 (132 / 39) | 98 / 2105 | 4.66% | +3.04 |
| T (subs; 721 substitutions) | 126 (92 / 34) | 109 / 2105 | 5.18% | +4.35 |

Word-boundary convention (reference runes, only the separators that count changes):

| Convention | Doublets (within / cross) | Lag-5 hits / n | Rate | z |
|---|---|---|---|---|
| Loader: - . & $ | 86 (63 / 23) | 104 / 2105 | 4.94% | +3.75 |
| No sentence breaks: - & $ | 86 (64 / 22) | 114 / 2479 | 4.60% | +3.14 |
| Hyphen only: - | 86 (64 / 22) | 116 / 2514 | 4.61% | +3.20 |
| Loader plus line breaks (/) | 86 (60 / 26) | 72 / 1645 | 4.38% | +2.06 |

Corruption control (`out_corruption.txt`; random replacement of a fraction r of the reference runes, boundaries kept, 60 draws):

| r | Doublets (mean, sd) | Lag-5 rate | z (mean, sd) | draws with z > 2 |
|---|---|---|---|---|
| 0.00 | 86.0 (0.0) | 4.94% | +3.75 (0.00) | 60 |
| 0.01 | 93.8 (3.8) | 4.91% | +3.67 (0.20) | 60 |
| 0.02 | 101.2 (4.6) | 4.87% | +3.57 (0.30) | 60 |
| 0.05 | 121.0 (6.7) | 4.81% | +3.42 (0.47) | 60 |
| 0.10 | 154.2 (9.0) | 4.67% | +3.06 (0.78) | 56 |
| 0.20 | 210.9 (13.7) | 4.35% | +2.26 (0.77) | 39 |
| 0.35 | 291.2 (16.2) | 3.98% | +1.34 (0.89) | 15 |
| 1.00 | 430.7 (21.2) | 3.35% | -0.25 (0.91) | 1 |

## Which differences move the lag-5 number

- **Substitutions in accurate copies: none.** The only rune-level disagreements among the rune-faithful families are the J to U+16C2 relabelling (no effect, see above), AU's one substitution and deletion, and the page-24 AE to A reading shared by S, S2 and AU (no effect on the statistics). H's two B to W substitutions do not change the statistic.
- **Word starts in accurate copies: small effects.** A and M (2 starts lacking, page 37 and page 50) and MT and M2 (1, page 50) move the within-word pair count from 2105 to 2108 and the rate from 4.94% to 4.98% (z +3.75 to +3.86). H's 4 lacking and 1 extra start move n to 2111 and z to +3.96. AU's single extra start (page 20) changes nothing.
- **Sentence-end convention: large effect.** scream314 does not mark K's sentence ends; 174 word starts are absent and the echo falls to 4.63% (z +3.26). The same change applied to the loader gives 4.60% (z +3.14).
- **Line-break convention: largest effect.** Treating line breaks as word breaks removes 460 within-word pairs; the echo falls to 4.38% (z +2.06).
- **Classifier readings.** CL's 45 substitutions and 192 deletions move the rate to 4.89% (z +3.63).

## Caveats and decisions

- Families without separators (C, J, P, V, T, CL, S2, RN, IN) use the loader's word starts; their statistics are the "substitutions only" variant by construction.
- Boundary decoding for aldegonde, scream314 and rne was checked by cross-tabulation, not assumed; word starts agree with K exactly for L and for C1B.
- V and T are reported for completeness. Their subs-only streams are 12.5% and 5.6% substitutions by count, with 9405 and 3097 deletions (V and T), so their z values are not interpretable as readings; compare with the corruption control instead (z falls to +2.26 at 20% random corruption).
- Pages 0-54 only; LP1 prefixes are dropped by offset search (families with prefixes: M, MT, M2, AU, S).
- Independence: the copies share a common root (dataset/liber_primus.json and hunt_results.json record the lineage). Of the 13 distinct full-book reading families (K, A, M, MT, M2, C, J, P, L, R, AU, S, H), 10 match K at every 0-54 rune position after J normalisation. AU has one substitution and one deletion, S one substitution, and H two substitutions plus the 54-rune omission on page 0 (65 deletions after normalisation). This agreement supports the rune reading but is not independent verification of it.
- No multiple-comparison correction; z is against 1/29 as specified.
- Nothing here changes the claim status of the campaign: these are robustness checks of two statistics, not a solve.
