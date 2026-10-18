# The LP2 fingerprint: what any hypothesis must reproduce

LP2 = pages 0-54, 12,956 runes, 29 symbols, loader `lp/lpdata.py` (SHA-256 pin in AGENTS.md). Each number below
was verified twice (round one, `REPORT.md`; round two, `REPORT_ROUND2.md`). `toolbox/fingerprint.py` computes
all of them for any rune stream with word ids, so a hypothesis can be simulated on English and compared.

| id | constraint | LP2 value | English / random reference | consequence |
|---|---|---|---|---|
| C1 | flat at every order | IoC 1.000; no period 1..1500 (corpus, section, page, word-aligned); linear complexity n/2 | English runes IoC ~1.7-1.8 | no periodic or shared-section key; key is aperiodic. The one local periodic peak (pages 53-54, harmonics of 13 in the increments) is at book-wide p about 0.05 and does not decrypt as a period-13 Vigenere/Beaufort (lane U, `lp/t8`, `lp/t9`) |
| C2 | doublet deficit | 86 adjacent repeats of 12,955 (0.66%); 63 within words, 23 across | random 447 (3.45%) | any c = p + k with k independent of c gives ~3.4% on English: excluded. Something suppresses repeats, ~84% of the time |
| C2b | flat conditional | IoC of next rune given previous = 1.026 | flat-increment prediction 1.026 | any FIXED feedback table excluded (~245 sigma); the key varies by position |
| C2c | doublet positions uniform | (first measured at mod 5 by Oosterhof, `dl/aldegonde_clone/hypotheses/doublet-preventer-clock-drift.md`) LP2's 86 doublets fall on positions mod 5 as 18, 21, 16, 11, 20; every modulus 2..8 is uniform (largest chi-square 11.3 vs 24.3 at p = 0.001), by global and by within-page index | a rule tied to absolute position concentrates them (chi-square 300+) | no repeat-suppression rule keyed to the absolute position; any exempt phase must drift (e.g. a clock that advances on each skip) |
| C3 | repeated cipher words at chance | 16 repeated words of >= 3 runes (round one); `fingerprint.py` counts 15 distinct words of >= 3 runes seen twice or more, against 10.0 +- 3.5 for its shuffle null (round one's exact definition was not recorded) | random stream 11.0 +- 3.1; English of this size 999 | any cipher with a small per-word state is excluded by counting |
| C4 | layout is not plaintext layout | adjacent word lengths independent (z +0.9); sentence-first/last words average length (z -0.2/-0.7) | English z +7..+15; Cicada's solved pages +4 | word lengths have English marginals (THE/OF absent) but no English sequence |
| C5 | within-word lag-5 echo | 104/2105 = 4.94% (z +3.75 raw, ~2.5 sigma after the lag scan); straddling a line break 32/460 = 6.96%, same line 72/1645 = 4.38% | random 3.45% | weak, word-aware, unexplained by any visible phase rule; the line-break split is post hoc (p 0.018) |
| C6 | chain-with-EA refuted | 23 cross-word doublets | 3.7-11.8 predicted if EA were the zero step | if the cipher is a chain, its zero step is key-set |

## Quick exclusions (check these before proposing anything)
- Predicts 0 doublets (strict no-repeat, redraw-until-different, chain increments drawn from 1..28): excluded by C2 (86 observed).
- Lets repeats survive only at a fixed absolute position phase (skip at 4 of every 5 positions): excluded by C2c
  (lane S found it; round two's dynsub_skip5 and totient_skip45 variants fail it at chi-square 300+).
- Predicts ~3.4% doublets (any additive keystream independent of the ciphertext, homophonic i.i.d. choice, most stream ciphers): excluded by C2.
- Periodic key of any length <= 1500, or one key shared by two sections: excluded by C1.
- A fixed alphabet set with a small per-word phase: excluded by C3 (K = 5 alphabets would force >= 482 repeated words).
- The only family consistent with C1-C6 so far: an evolving-alphabet walk with period-5 alphabets inside words and a skip-on-repeat
  rule (Oosterhof; and the Quagmire-odometer-dodge sibling in `agents/laneO_quagmire_dodge`).

## Already tested (do not repeat without saying what is new)
Round one lanes A-N and round two O-R: see the tables in `REPORT.md` and `REPORT_ROUND2.md`. Community ledgers:
`dl/dukotah/liber-primus/LEDGER.json`, the elimination ledger (`find dl/dukotah -name ELIMINATION-LEDGER.md`),
`dl/leo/docs/FINDINGS.md`, `dl/aldegonde_clone/hypotheses/INDEX.md`.
