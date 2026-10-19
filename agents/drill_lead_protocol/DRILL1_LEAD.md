# TEST DRILL 1: a full solve (PLANTED cipher, not LP2) — 2026-10-18

> Drill of the CLAUDE.md lead protocol. The "discovery" is lane X's planted odometer-dodge key on LP2's word layout
> (seed 55000, advance). Nothing here concerns LP2's real runes.

**What was found:** lane X's attack decrypts the whole ciphertext to English (Moby-Dick): "BUT EMBARKS FOR THE REMOTEST
INDIES OF THIS LIVING EARTH. WHY THE LIFE INSURANCE COMPANIES PAY DEATH FORFEITURES UPON IMMORTALS..."

**Step 1, verification (`drill.py`, `out/drill.json`):**
| check | result |
|---|---|
| stage-1 score vs 50 nulls | +0.234 against 0.0158 +- 0.0029 (max 0.0218): z +75 |
| re-run from scratch, new seed | 99.7% of runes identical |
| language on every page independently | 55 of 55 pages in the English band (worst -5.01, best -4.43; a shuffled page -6.19) |
| independent scorer `lp/verify_candidate.py` | IoC 1.649, quadgram -4.842, vocabulary hit 0.148; shuffle null -6.747 |
| oracle `verify_solution.py --plaintext` | NOT-ADJUDICABLE: by design it only checks that a text is English and needs a key |
| (drill only) agreement with the planted plaintext | 91.4% |

**Lesson for the protocol:** the oracle cannot adjudicate a dodge-family solve from a plaintext. A real claim needs the
compact key (K, schedule, dials, variant) and a re-encipherment of the recovered plaintext that reproduces LP2 rune for
rune, plus a re-derivation by verify-lane. CLAUDE.md was updated.

**Step 2, applied to the rest of the book:** the attack already covers all 55 pages; every page reads.

**Commands:** `python -I -X utf8 agents/drill_lead_protocol/drill.py`
