# Census fixture (good)

## Bottom line
- Three rows; one reopen candidate.

## Census
| id | method | family | scope searched | control | null | source | strength | our coverage | constraint |
|---|---|---|---|---|---|---|---|---|---|
| FX-01 | Vigenere, periods 1-1500 | polyalphabetic-periodic | every period 1-1500 | y | y | `toolbox/CONSTRAINTS.md` | A | lane A | dead C1: periodic key <= 1500 excluded |
| FX-02 | additive keystream from Self-Reliance | running-key/book | 40 offsets | n | n | https://example.org/selfreliance | C | lane H | dead C2: predicts 3.4% doublets, LP2 0.66% |
| FX-03 | dodge walk with keyword g | walk/dodge | 12 keywords | unclear | n | `REPORT.md` | C | lane L | consistent |

## Reopen candidates
- FX-03: sweep the full keyword register with a planted control.

## Sources checked
- `toolbox/CONSTRAINTS.md`, `REPORT.md`, https://example.org/selfreliance
