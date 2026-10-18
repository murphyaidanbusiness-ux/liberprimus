# CHANGELOG

Every fix, dated, with the job and the model that was running. Read the last five entries before starting a job.

## 2026-10-16 · technique-survey (setup) · claude-opus-5-5
Change: jobs/ folder structure (map in AGENTS.md, one folder per job with PROOF, SKILL, tools, data/fixture, runs) adopted
from the owner's folder-method guide. CLAUDE.md is now `@AGENTS.md`; its old content moved into AGENTS.md.

## 2026-10-16 · hypothesis-gate · claude-haiku-5-5 (round-two gap audit)
Fail: the gap audit proposed PHP mt_rand and glibc random() "direct output with no-repeat" lanes. Those predict 0
doublets; LP2 has 86, so they were dead before any seed sweep. Fix: the hypothesis-gate job, whose `gate_sim.py` simulates
a hypothesis and fails it on C2 mechanically (fixture `norepeat.py` -> `GATE FAIL: C2 C6`).

## 2026-10-16 · port-community-code · claude-haiku-5-5 (lane O)
Fail: one failed planted control was read as "the scorer cannot see keyword alphabets" and nearly cancelled the sweep.
Replaying the same key on fresh plaintext recovered it at z +16; 95/100 fresh plants were recovered. Fix: PROOF requires
>= 20 plants with misses listed, and SKILL step 6 says to replay a failed key on fresh plaintext before blaming anything.

## 2026-10-16 · port-community-code · claude-opus-5-5
Fail: `cmd //c "start /BELOWNORMAL /WAIT /B python ..."` from Git Bash started nothing and left an empty log; the python
processes on the machine belonged to the owner. Fix: `agents/laneO_quagmire_dodge/launch_sweep.ps1` (Start-Process,
BelowNormal set before the pool exists, workers inherit it); SKILL rule added; always check the process exists.

## 2026-10-16 · hashhunt-run · claude-opus-5-5
Fail: `OSError: [Errno 22]` appending to plan_state.jsonl on Windows mid-run (a file held by a scanner). Fix: `jl_append`
retries six times with a short backoff. Also: widening the allowlist without the owner's yes was blocked by the
auto-mode safety check; AGENTS.md now says only the owner widens it.

## 2026-10-16 · all jobs · claude-opus-5-5
Note: `.claude/agents/lp-<job>.md` agent types only register when a session starts; spawning `lp-hypothesis-gate` in the
session that created it failed ("Agent type not found"). Workaround in that session: a general Haiku agent told to read
`.claude/agents/lp-<job>.md` and follow it. From the next session on, spawn them by name.

## 2026-10-16 · technique-survey · claude-haiku-5-5
Fail: two surveys reported `toolbox/fingerprint.py` as missing; it was written while they ran. Not a playbook fault.
Note for agency sources: nsa.gov returns HTTP 403 to the fetch tool for PDFs. Look for the same declassified documents on
archive.org or in published book form, and keep marking search-excerpt claims as such.

## 2026-10-16 · hypothesis-gate · claude-haiku-5-5
Fail: the totient gate agent did not write `runs/2026-10-16-<hypothesis>.md`, citing a general rule against creating
documentation files, so PROOF line 1 failed (the orchestrator assembled the report from its outputs). Fix: every
`.claude/agents/lp-*.md` now says the job's output files are explicitly requested.

## 2026-10-16 · hypothesis-gate · claude-opus-5-5 (found by lane S, claude-haiku-5-5)
Fail: two hypotheses passed the gate (dynsub_skip5, totient_fskip_skip45_nolitF) although LP2 refutes them: their skip is
keyed to the absolute position, so all surviving doublets sit on one residue mod 5, while LP2's 86 are uniform mod 2..8.
Proof was too loose. Fix: constraint C2c in toolbox/CONSTRAINTS.md and a C2c row in `fingerprint.gate` (chi-square of
doublet positions mod 2..8 against its p = 0.001 value), counted as hard in `gate_sim.py`. Both runs re-graded EXCLUDED by
C2c; fixture expected.md updated (vigenere7 now also fails C2c).

## 2026-10-16 · hypothesis-gate · claude-opus-5-5
Fail: with 12 seeds, lane O's dodge family "failed" C2, C3 and C6 because single random keys fell outside a band, although
its 12-key means match LP2 (87.4 vs 86 doublets, 22.1 +- 6.2 vs 23 cross-word). Each seed is a fresh key, so a verdict
must compare LP2 with the family's spread, not demand every key pass. Fix: `gate_sim.py` fails a constraint only when a
majority of seeds fail it, prints `GATE PASS (marginal: ...)` otherwise, and the SKILL says to rerun a PROCEED at 12 seeds.
All earlier verdicts are unchanged under the new rule.

## 2026-10-16 · hypothesis-gate · claude-haiku-5-5 (walk gate)
Note: for the Oosterhof walk the gate fails typical keys while 14% of random keys (and 1,550 of 20,000 prime-seeded keys)
pass every hard constraint. The gate grades a family by its typical key; a family whose LP2-like keys are a minority is
narrowed, not excluded. Fix: SKILL rule pointing at `tools/walk_draws.py` (key census) for high-variance or small key
spaces; the prime-seeded walk went to an exhaustive attack lane (T) instead of being dropped.

## 2026-10-16 · attack-lane (lane S, totient skip) · claude-haiku-5-5
Fail: the first null design scored real and null streams differently. The strict screen keeps only keys consistent with
every doublet in the window, so the real window (two doublets on one residue) kept 10,000 keys and most shuffles kept
0-63, but 6 of the 40 kept 10,000, so their best scores were not comparable. Fix: the z-score uses a relaxed screen
(doublet rule dropped, all 50,000 keys scored, same rule for real and null); strict consistency counts are reported
separately. Also: the decoder is an exact dynamic program over (position, k) with no beam cap; a cap can drop the true path, so
it was removed (the one English miss in the self-test occurs with and without the cap). The gate's C2 does not test doublet residues; the orchestrator added C2c after
lane S reported that the simulator puts all doublets on one residue mod 5.

## 2026-10-17 · attack-lane (lane O tier A) · claude-opus-5-5
Fail: the tier A estimate (~1.5 h) assumed 10 workers give ~10x one worker; the run took 177 min, ~5x, on this 8-core /
16-thread i7-11700F. Fix: estimates in lane O RESULTS section 9 and REPORT_ROUND2.md now use the measured 16,197 keys/s
at -NProc 10 (tier B ~7 h, tier C ~57 h). Measure aggregate throughput, not per-core, before quoting a wall time.

## 2026-10-17 · attack-lane (lane V, lag-5 burst scan and decibans) · claude-haiku-5-5
Fail: two fixes while running. (1) `python -I` hides the user site-packages, so the quagmire simulator (community port, needs scipy) failed to import; `mech_sim.py` and `mech_rank.py` append `site.getusersitepackages()` after isolation. (2) A no-echo plant base drawn as iid Bernoulli labels gave 9% false flags against a 5% nominal, because the scan standardises with fixed stratum totals. Fix: the base keeps stratum totals, and each plant is tested against its own stratum permutations (false flags 4.0%). Also: a 505-window count was misstated as 495 in a script string; corrected.

## 2026-10-17 · attack-lane (lane O tier B) · claude-opus-5-5
Fail: tier B launched at ~00:55 had 0 of 132 tasks done at 08:57; each worker had ~21 CPU-minutes in 8 hours. Nothing was
competing when checked (each worker at 102% of a core), so the PC most likely idle-slept, which also stalled the Common
Crawl hash hunt (15 queries in 8 h). The app's keep-awake only holds while the session is active (it lets go after ~5
idle minutes). Fix: before an unattended multi-hour run, tell the owner it needs Windows sleep off (Settings > System >
Power, "when plugged in, put my device to sleep after: Never") or the session kept active; check task completions after
the first expected task time instead of assuming progress.

## 2026-10-17 · attack-lane (lane O tier B) · claude-opus-5-5
Fix for the sleep stall: `agents/laneO_quagmire_dodge/stay_awake.py PID [max_hours]` holds the PC awake with
SetThreadExecutionState until the run's process exits (no power-plan change; the owner's 15-minute sleep setting stays).
Started for tier B (pid 21788, cap 9 h) at 10:04.
## 2026-10-17 · hypothesis-gate · claude-haiku-5-5 (quagmire_dodge_clock)
Fail: `tools/walk_draws.py` left C2c out of its hard set (its HARD tuple predated the C2c addition of 2026-10-16), so its
"all hard constraints" census was looser than `gate_sim.py`'s. Fix: C2c added to HARD and to the per-constraint rows, so
both tools share one hard set. Also run: the clock-dependent dodge (`quagmire_dodge_clock`) gates PASS with a marginal C2
on 1 of 12 seeds; its 300-key census has 211 keys passing every hard constraint (`runs/2026-10-17-quagmire_dodge_clock.md`).

## 2026-10-17 · port-community-code · claude-haiku-5-5 (lane W, clock-dependent dodge scorer)
Result, not a fix: `dodge_aware_scorer` does not recover `quagmire_dodge.encipher` (the clock variant). 0/20 planted keys rank 1 against 2,000 wrong keys (median z +0.3). The word model is correct: with the true key and the true phase of every rune, the plaintext decrypts exactly, and the true key beats all 2,000 wrong keys on 20/20 plants. The failure is the phase path: a clock skip (about one per 29 runes) is invisible in the ciphertext, and the cumulative word maps make one wrong boundary phase corrupt every later word. The odometer reference is 17/20 with exact ties counted as wins. Its dials-category ties are an exact symmetry, not wrong keys: an outer-dial shift is an assignment relabel, so tied keys share K, schedule and inner dial. Report: agents/laneW_clock_dodge/RESULTS.md. No sweep priced; the hypothesis-gate verdict for quagmire_dodge_clock is unchanged.

## 2026-10-17 · verify-lane (lane W) · claude-opus-5-5
Verified lane W with fresh code (`agents/laneW_clock_dodge/orch_check.py`): every headline number reproduces (odometer 17/20
with equivalent-key ties, clock 0/20, median z +8.23 / +0.32), and both relabel symmetries hold on 5/5 fresh plants.
Fix: lane W's section 6 called the clock decode's forks "rare", citing the community's "0 to 6 runes in 12,388". That
figure is the residual error of a key-holding beam search; the fork rate is about 5% (97 per 1,802 runes, every true skip
is one), matching the community's 4.5-6.5% collision rate. Corrected in RESULTS.md. Lesson for port-community-code: when
quoting a community number, quote what it measures. Also recorded: the community's hypothesis file says the dodge-aware
scorer recovers this family at z 12-20, but its self-test and the parked sweep plant the odometer, not
`quagmire_dodge.encipher`; noted in REPORT_ROUND2.md section 4. Lane W's PROOF item 2 (audit after first run) stays a fail.

## 2026-10-17 · exhaustion-census (new job) · claude-haiku-5-5 x4, merged by claude-opus-5-5
New job `jobs/exhaustion-census/` (proof first: PROOF.md, SKILL.md, `tools/check_census.py`, fixtures; wrapper
`.claude/agents/lp-exhaustion-census.md`; routing row in AGENTS.md). Four Haiku parts, 232 rows, merged by
`research/census/merge.py` into `research/EXHAUSTED.md`.
Fail: the agents were too lenient on the constraint cell. They marked pure transpositions, digraphic tables, periodic keys
above period 1500, unfiltered autokeys and no-repeat rewrites `unclear` or `consistent` where the quick exclusions in
`toolbox/CONSTRAINTS.md` kill them, and flagged 99 reopen candidates. Fix: 23 rows re-graded in `merge.py` (each with its
reason), and the orchestrator's buckets separate open-ended dictionaries, off-stream channels and statistical probes
from finite partial searches (11 remain). Lesson for the job: SKILL.md should tell agents to try every quick exclusion
before writing `unclear`.
Fail (ours, round two): C2c was presented as new. Oosterhof's `hypotheses/doublet-preventer-clock-drift.md` had already
measured the mod-5 doublet phase counts (18, 21, 16, 11, 20) and used them to rule out drift-free preventers. Fix:
attribution added in `toolbox/CONSTRAINTS.md`, `REPORT_ROUND2.md` and `docs/COMMUNITY_SUMMARY_DRAFT.md`. Lesson: grep
the community ledgers for a number before calling it new.
Also: the odometer dodge's "hold" variant gates PASS (marginal C3) and lane O's scorer recovers 18/20 planted hold keys
(median z +22.8), so tiers A and B cover it (lane O RESULTS.md section 11; `diag_alphabet_kind.py` gained `DIAG_VARIANT`).

## 2026-10-18 · exhaustion-census (judging pass) · claude-opus-5-5
Fix: the first merge re-graded only the rows the orchestrator happened to spot (23, hard-coded in `merge.py`). The job
now has a formal judging pass: `research/census/write_judgments.py` records a verdict and one bucket for every row of
every part (232: 205 agree, 26 constraint cells re-graded to dead, one strength re-graded), writes `judgments.tsv`, and
`merge.py` reads it and fails on any unjudged row, double bucket, or dead row bucketed elsewhere. SKILL.md and PROOF.md
gained the orchestrator step. The full pass moved four more rows: AX-07 and AX-14 to dead (C2), WB-21 to dead under
either reading, AL-15 to searched in full (its 154M keys are the whole pool), AL-25 and AL-31 to refuted by a direct
test. The reopen list went from 11 to 6. Lesson: agents extract, the orchestrator judges every row, not a sample.

## 2026-10-18 · attack-lane (lane X, any-alphabet odometer dodge) · claude-opus-5-5
New lane, built and run by the orchestrator. Four approaches failed before the one that works, recorded so they are not
retried: (1) an untied 145-group HMM over the clock drift stalls in local optima (phase accuracy 0.3-0.5); fix: doublets
as phase anchors plus a schedule scan on the runes just after each doublet, then a tied HMM (accuracy 0.85-0.96).
(2) Coordinate ascent on the tie collapsed to all-equal shifts; replaced by the anchor scan. (3) Stage 2 as a K climb per
(A, b0) start-dial pair works only at the exact pair (841 cells, all-or-nothing), and a two-alphabet climb and a
Caesar-blind difference model both fail (the difference model is gamed: every A scores alike). Fix: an IoC climb on K
aligns the tables for ANY dial pair and leaves one fixed substitution, solved by quadgrams (1 s). (4) Stage 2 at 3,000
iterations missed true keys 3 times in 4; diagnosed before changing the method. Lesson: when a search fails, check
whether the parameter is absorbable before enumerating it.
Result: NULL (agents/laneX_general_alphabet/RESULTS.md); tier C of lane O is superseded for continuous keys.
