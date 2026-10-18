# Census fixture (bad)

## Bottom line
- Broken on purpose.

## Census
| id | method | family | scope searched | control | null | source | strength | our coverage | constraint |
|---|---|---|---|---|---|---|---|---|---|
| FX-01 | Vigenere | polyalphabetic-periodic | periods 1-1500 | yes | y | `toolbox/CONSTRAINTS.md` | A | lane A | dead C1 |
| FX-02 | book code | running-key/book | some offsets | n | n | `dl/nowhere/missing.md` | E | none | probably dead |
| FX-03 | short row | other | x | n | n | `REPORT.md` | D |
| FX-04 | hash keystream | PRNG/hash keystream | 3,400 seeds | y | y | http://abcdefghijklmnop.onion.to/x | A | lane B | dead C2 |

## Reopen candidates
- FX-04: rerun it.

## Sources checked
- none
