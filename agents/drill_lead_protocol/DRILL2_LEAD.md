# TEST DRILL 2: a lead, not a solve (PLANTED cipher, not LP2) — 2026-10-18

> Drill of the CLAUDE.md lead protocol. The "discovery" is lane Y's planted restart-per-chapter key (seed 66000,
> advance) on LP2's layout. Nothing here concerns LP2's real runes.

**What was found:** lane Y's key-free detector finds strong odometer-dodge structure with the key restarting at each
chapter (schedule tie [0, 20, 17, 20, 0]), but stage 2 does not decrypt it (quadgram -6.46, noise).

**Step 1, verification (`drill.py`, `out/drill.json`):**
| check | result |
|---|---|
| stage-1 score | +0.126; lane Y's chapter nulls sit near +0.016 |
| re-run from scratch, new seed | +0.126 (identical) |
| held out: even chapters alone | +0.083 against 5 shuffles at mean 0.014, max 0.016 |
| held out: odd chapters alone | +0.099 against 5 shuffles at mean 0.016, max 0.020 |
| plaintext | none yet (stage 2 fails) |
| (drill only) agreement with the planted plaintext | 6.2% |

**Verdict:** a lead. The structure is real and replicates in two independent halves, but nothing reads yet.

**Step 2, next actions:** fix the schedule tie and refit the clock path per chapter; try stage 2 with more restarts and
per-chapter dial offsets; plant ciphers like this one to find out why stage 2 misses them.

**Commands:** `python -I -X utf8 agents/drill_lead_protocol/drill.py`
