# Liber Primus campaign, round two (2026-10-16)

**Outcome: not cracked.** Round two used the one thing round one lacked, network access to the public
archives. It ran the first safe, live hash hunt for the page-56 target, two new controlled tests, a
transcription robustness check, and a port of the community's best-motivated, never-run sweep to this PC.
Every completed test is null. The sweep is validated and ready, but not yet run (section 6).

In the second half of the session the work was reorganised into the owner's folder method (one map, one folder per job,
proof before playbook), three research agents graded 64 published cryptanalytic techniques against the LP2 fingerprint,
and a new hypothesis gate simulated the most promising untested families on English (section 5). The gate added a seventh
constraint (C2c, first measured at mod 5 by Oosterhof; see section 5) and left one family standing: the Quagmire-odometer dodge that the validated sweep searches.

Round one's six constraints (`REPORT.md`) stand. Nothing here weakens them; C5 is sharpened and C2c is added (an extension of Oosterhof's mod-5 phase test, found independently).

Work was split across Haiku agents, each with the protocol in `docs/BRIEF_ROUND2.md`, and every headline
number below was re-derived by the orchestrator before it went into this file.

## 1. What changed since round one

- **The archives are reachable.** `web.archive.org` and `index.commoncrawl.org` answer from this machine.
  Common Crawl's index was down (HTTP 504) for the whole session.
- **The community moved, but did not solve anything** (`research/scout6_delta.md`). No solve claim anywhere,
  2026-09-01 to 10-16. Oosterhof's period-5 per-word structure is the live lead; Dukotah's sweeps have been
  dead since a 2026-09-15 reboot; Theron found a scorer defect in his own nulls; Leo corrected the IoC null
  spread. One loose end, Dukotah's round-27 "HIT-CANDIDATE" seed 35563892, is already closed by their own
  adjudication (`round27/ORACLE-35563892.md`): its score regresses from 7.67 to 4.96 when the window doubles,
  and the decrypt is not language.
- **The tools here got stricter.** `hashhunt` refuses to run without an onion allowlist (section 2).

## 2. Safety: what was and was not scraped

The owner's rule for this round: nothing harmful, illegal or disgusting, and no malware, may come through.
An onion address says nothing about the site behind it, so a blind sweep of archived darknet pages cannot
meet that rule. It was not attempted.

- `hashhunt` now has an `--allowlist` mode and refuses `plan`/`fetch` without it (or an explicit `--blind`,
  which was never used). Every archive query names one allowlisted host; any row returned for another host is
  dropped before it is written; off-list captures are never fetched. Selftest: 39/39, including a mocked
  archive that misbehaves on purpose.
- The allowlist is the 4 onions named in Cicada's own PGP-signed messages, each signature re-verified
  (`hashhunt/cicada_onions.md`). The 2014 onions 1 to 6 are well documented but attributed only by the
  community record; they were not queried and widening the list is the owner's call.
- Text only, 5 MB cap, never rendered, opened or executed; no Tor, no onion or gateway contact.
- Community code (Oosterhof's sweep) was audited for network, process, deletion and write calls before any of
  it ran (`agents/laneO_quagmire_dodge/audit/`): nothing reachable beyond the expected compile step.

## 3. Results

| lane | question | result |
|---|---|---|
| **P** hash hunt | Does any archived capture of a Cicada-signed onion hash to the page-56 target? | **Null.** 80 Wayback queries, 3 captures (a 2015 gateway placeholder and two `robots.txt`), 2 distinct, hashed under 6 functions x ~160 normalisations (672 and 780 tuples), 0 matches. Common Crawl not covered (index down). `agents/laneP_hashhunt/RESULTS.md` |
| **Q** key reuse | Is any stretch of LP2 enciphered with a keystream reused elsewhere at any shift? | **Null, power-limited.** All pairs of 55 pages and 17 chapters at every shift, and the whole stream at lags 1 to 12,896, raw and increments, 200 doublet-preserving nulls per cell set. Real maxima inside the null (pages raw z 6.86, emp. p 0.065; stream raw z 4.18 at lag 6002, p 0.32). Excluded: single-lag reuse of about 3,200 runes or more in the whole stream at 90% power. **Not** excluded: page- or chapter-length reuse (planted page-length reuse is detected 0/20 times at this sample size). `agents/laneQ_superposition/RESULTS.md` |
| **R** transcriptions | Do the two signals survive the choice of transcription? | **Yes.** ~20 distinct readings among 87 runic files; every faithful full-book reading gives 86 doublets and a lag-5 echo of z +3.63 to +3.96. The echo's size depends on which marks count as word breaks (+3.14 without sentence breaks, +2.06 if line breaks count). `agents/laneR_transcriptions/RESULTS.md` |
| **O** Quagmire dodge | Port, validate and run Oosterhof's never-run zero-offset Quagmire-odometer-dodge sweep over Cicada's vocabulary | **Validated, not yet run.** C kernel builds with MSVC and equals the Python reference; community selftest z +20.3; our own 100-plant control recovers 95/100 keyword keys at rank 1 (median z +23.7); held-out adjudicator separates a planted key at z +21. Full run: 3.9e9 keys, ~360 core-hours. `agents/laneO_quagmire_dodge/RESULTS.md` section 7 |
| **O** tier A | Does the Quagmire-odometer dodge, keyed by any of Cicada's 14 signature words (incl. the real key FIRFUMFERENFE), decrypt LP2? | **Null.** 172,111,520 keys (56 alphabets x 105,980 schedules x 29 dials) in 177 min; best +0.706 on the scored text; all 280 retained candidates held out on 2,528 unseen words: 0 above the null max at their own dial, held-out z mean +0.11 sd 0.86 (noise); a planted key holds out at z +21. Power ~89%. `agents/laneO_quagmire_dodge/RESULTS.md` section 9 |
| **O** tier B | The same, keyed by the other 33 named puzzle terms | **Null.** 405,691,440 keys in 404 min; best +0.720 (SACRED); all 655 retained candidates held out: 0 above the null max at their own dial, z mean +0.06 sd 0.94. Tiers A+B: 577.8M keys, 47 words, both null. `agents/laneO_quagmire_dodge/RESULTS.md` section 10 |
| **S** totient stream | Does Cicada's solved-page prime-totient keystream, with a collision skip, decrypt LP2 from any start? | **Null.** Every start k0 0..9999 and skip phase 0..4 (50,000 keys) in both sign conventions, exact decoder; control 19/20 and 5/5 at rank 1; real best z +0.35 and -0.63 against 20-shuffle nulls, both below the null max; full-text decodes of the top 50 reach -7.24 per quadgram (noise). The family is also excluded by C2c, which this lane found. `agents/laneS_totient_skip/RESULTS.md` |
| **T** prime-seeded walk | Does Oosterhof's dodge walk, with its permutations built from Cicada's prime/totient ladder, decrypt LP2 under any of its 20,000 keys? | **Null.** Exhaustive decode at beam width 512 (300-rune screen unchanged at 4,096); control 20/20 at rank 1 over all 20,000 keys; real best -6.870 per quadgram, z -1.56 against a 20-shuffle null (max -6.667); the top 50 keys all die before the end of the text. `agents/laneT_prime_walk/RESULTS.md` |
| **U** period 13 | Is the community's period-13 peak in pages 53-54 (their "54-55") real under a threshold fixed in advance? | **Inconclusive (power).** Lag-13 count 18 against a fixed 99th-percentile threshold of 19; planted period-13 keys flagged 18/50 at this length. Orchestrator follow-up: lags 13, 26 and 39 are all high (harmonic sum 57 vs 31.4), but scanning every page and pair puts it at book-wide p about 0.05 (`lp/t8_harmonic_scan.py`, 100 shuffled books), and a period-13 Vigenere/Beaufort on the increments does not decrypt it (`lp/t9_period13_solve.py`: controls 10/10, real at null). `agents/laneU_period13/RESULTS.md` |
| **V** lag-5 echo | Is the echo localised, and which mechanism explains it best? | **Null / no selection.** Burst scan: best window pages 50 (Z 2.89) vs null 3.00 +- 0.62, p 0.51 (diffuse); localised plants of the same size found 50/50. Deciban ranking of five mechanisms: on the echo cell the walk (+22.8 dB) and the Quagmire dodge (+21.1 dB) beat the no-echo baseline, dynamic substitution and the totient stream do not (about 0), but the overall ranking flips with the cell set, so no mechanism is selected. `agents/laneV_lag5_mechanisms/RESULTS.md` |
| **W** clock-variant scorer | Can the community's dodge-aware scorer recognise a planted key of the clock-dependent dodge (`quagmire_dodge.encipher`)? | **No.** 0/20 planted keys at rank 1 against 2,000 wrong keys each (median z +0.3); its fitted clock phase is at chance (0.19 against 0.20). The odometer reference on the same harness: 17/20, counting exact ties with equivalent keys as wins. With the true key and the true phases the word model decrypts exactly and the planted key beats every wrong key, so what fails is recovering the clock path. Re-derived by the orchestrator with fresh code and text (`orch_check.py`). `agents/laneW_clock_dodge/RESULTS.md` |
| scout 6 | What is new in the community? | No solves; items and their bearing on next steps in `research/scout6_delta.md` |
| gap audit | Which hypotheses are consistent with the constraints and untested? | Ranked list in `research/gap_audit.md`; see section 4 for the corrections |
| exhaustion census | What has the community already ruled out, and how solidly? | 232 methods from four ledgers and the public web, every row judged by the orchestrator: 130 dead by the fingerprint, 21 searched in full or refuted, 21 open-ended, 34 off the rune stream, 20 structure probes, 6 partial and finite (5 of them walk/dodge variants; none high-hope). It also caught two errors in our own record (C2c's attribution; the dodge's "hold" variant, which tiers A and B turn out to cover). `research/EXHAUSTED.md` |
| provenance | Which onions are verifiably Cicada's? | 4 signed, 16 community-only, 12 unknown, 1 hallucination. `hashhunt/cicada_onions.md` |

## 4. Corrections and sharpened findings

**Constraint 5, sharpened (orchestrator, `lp/t7_lag5_lines.py`).** Lane R found the lag-5 echo drops to
z +2.06 when line breaks are counted as word breaks. Split directly: within-word lag-5 pairs that straddle a
line break coincide at 32/460 = 6.96% (z +4.12); pairs on one line at 72/1645 = 4.38% (z +2.06). Matched
for word length, the straddling excess has a permutation p of 0.018. The doublet deficit is line-blind
(lag 1: 0.71% straddling vs 0.62% same line). Other lags show no general straddle excess (lag 3 +1.70,
lag 7 +2.35, lag 8 -2.05). This is post hoc and about 2 sigma: an observation to pre-register against, not
a constraint. If it is real, the echo is tied to the layout, which no cipher in the community's catalogue
predicts.

**Gap-audit candidates 2 and 3 are excluded, not open.** Runes as the direct output of PHP `mt_rand` or
glibc `random()` with a no-repeat redraw (or as chain increments drawn from 1..28) produce zero doublets.
The book has 86 (constraint 2). These are dead before any seed sweep.

**The parked dodge sweep was runnable, and it would have mostly worked.** The community priced it at 218
core-hours and parked it. Here it measures ~3,000 keys/s/core, so ~360 core-hours. Its scorer misses about
1 true key in 20 outright (the plaintext draw decides), and a near-true neighbour can outrank the truth, so
the run must be adjudicated over all 1,200 retained candidates, not by its global top.

**The community's dodge-aware scorer was only ever tested on the odometer (lane W, checked by the orchestrator).**
The community's hypothesis file for the clock-dependent dodge says `dodge_aware_scorer.py` puts a planted key of that
family on top at z 12 to 20. Its self-test and the parked sweep both plant `doublet_phase_test.encipher`, the odometer,
not `quagmire_dodge.encipher`. On the clock variant the scorer is at chance (0/20). So lane O's tier A and B nulls cover
the odometer form only, and the clock form, which passes the gate, has no working search tool. The obstacle is
structural. A clock skip leaves no mark in the ciphertext, so every skip is a fork in the decode: 97 forks per 1,802 runes
with the true key in hand (about 5%, matching the community's 4.5-6.5% collision rate). One wrong fork scrambles every
later word, because each word's map is built from all earlier ones. base_0 itself is harmless (it is an exact relabel of
the cipher symbols, checked on 5/5 fresh plants), but even decoding with the true key needs a beam search over the
forks. A scorer would have to run that beam decode inside a search over base_0.

## 5. The job system, the technique surveys and the gate

**Structure** (from the owner's guide, murphmaxxing.com, "The folder method"): `AGENTS.md` is the map, `CLAUDE.md` is
`@AGENTS.md`, `CHANGELOG.md` logs every fix with the model that was running, `toolbox/` holds what every job shares, and
`jobs/` has seven folders (technique-survey, hypothesis-gate, attack-lane, verify-lane, port-community-code, hashhunt-run,
community-scout), each with a pass/fail `PROOF.md` written before its `SKILL.md` playbook, scripts that check the proof
mechanically, and a fixture that the checker must pass and fail correctly. Each job has a Haiku agent file,
`.claude/agents/lp-<job>.md` (they register from the next session; this session used general Haiku agents told to read
them). The shared gate is `toolbox/fingerprint.py`: C1-C6 plus C2c for any rune stream, reproducing LP2's pinned values.

**Surveys** (`jobs/technique-survey/runs/`, catalogue in `toolbox/TECHNIQUES.md`): agency and classical methods (Friedman,
Kullback, Kerckhoffs, Turing and Good, Tutte, Rejewski; official public sources only, and nsa.gov refused PDF fetches, so
those entries rest on secondary sources), computational and AI decipherment (Lasry, Jakobsen, Knight/Ravi/Nuhn, neural
decipherment, Copiale, Z340, DECRYPT, LLM agents), and Cicada's own toolbox. 64 techniques: 28 excluded by a named
constraint, 20 already tested, 16 untested. Every verified historical solve rests on non-flat statistics that LP2 lacks.
Two corrections came out: Cicada's solved pages show no repeat suppression and the F-interrupt cannot make LP2's deficit;
and the community's `SOLVED-PAGES.json` has deletion artefacts (page 03 reads `...THEENDOALLTHNGS...`).

**Gate verdicts** (`jobs/hypothesis-gate/runs/`), each re-run by the orchestrator:

| hypothesis | gate | verdict |
|---|---|---|
| Chaocipher-29 dynamic substitution, strict skip-on-repeat | FAIL C2 C6 (0 doublets) | excluded |
| the same, skip at 4 of 5 positions | FAIL C2c (chi-square 300+ at mod 5) | excluded (passed the first version of the gate; see below) |
| Cicada's totient stream, literal F, collision skip (and keyword-shift, skip-45 variants) | FAIL C1 (rune 0 at 5.6% vs 3.54%), C2, C6 | excluded; matches the community's "body passes no F through" (-8.9 sigma) |
| the totient stream, no literal F, skip at 4 of 5 positions | FAIL C2c | excluded |
| Oosterhof doublet-dodge walk, random permutations | FAIL C2 (majority of keys) | typical keys excluded; a census finds 14% of random keys pass every hard constraint |
| the walk with g, sigma and base from Cicada's prime/totient ladder (20,000 keys) | FAIL C1 C2 C6 | typical keys excluded; 1,550 of 20,000 keys pass; lane T decoded LP2 under every key: null |
| Quagmire dodge, clock-dependent word step (the community's `quagmire_dodge.encipher`, never swept) | PASS (C2 marginal on 1 of 12 keys) | **proceed, but not yet attackable**: 12-key means match LP2 as well as the odometer's (doublets 90.9, cross-word 24.2, share 0.266, lag-5 5.7%); raw key space ~10^96 (K, schedule, a free 29-cycle sigma, base0); the community's old scorer misses a planted key of this variant (0.493 vs 0.619), and a vocabulary sweep is ~4,600 core-hours. Needs a validated scorer first; lane W found the dodge-aware scorer is blind to it too (0/20), so that means a new beam-decode scorer. `jobs/hypothesis-gate/runs/2026-10-17-quagmire_dodge_clock.md` |
| Quagmire-odometer dodge (lane O's family) | PASS, marginal C6 on 1 of 3 seeds | **proceed**: over 12 keys, doublets 87.4 (LP2 86), cross-word 22.1 +- 6.2 (23), lag-5 5.7% (4.94%) |

**C2c, the added constraint.** Attribution: Oosterhof measured LP2's mod-5 doublet phase counts first, in
`dl/aldegonde_clone/hypotheses/doublet-preventer-clock-drift.md` (18, 21, 16, 11, 20; chi-square 3.7; flat at every space
skip), and used them to rule out drift-free preventers. We missed that file and found the same counts independently; the
exhaustion census (`research/EXHAUSTED.md`) caught it. Lane S, sweeping the totient variant, noticed that its simulator puts every surviving doublet
on one residue mod 5, while LP2's 86 fall on residues 0-4 as 18, 21, 16, 11, 20. Checked by the orchestrator: LP2's
doublet positions are uniform for every modulus 2-8, by global and within-page index (largest chi-square 11.3 against
24.3 at p = 0.001). So no repeat-suppression rule keyed to the absolute position can be LP2's; an exempt phase has to
drift, as the dodge family's clock does. Two "PROCEED" verdicts were withdrawn, the gate now checks C2c, and the gate
counts a constraint as failed only when most random keys fail it (one unlucky key had been failing a family whose
twelve-key average matches LP2). Both fixes are in `CHANGELOG.md`.

**What it adds up to.** Of every family simulated this round, only the Quagmire-odometer dodge reproduces the lag-5
echo, the doublet rate, the cross-word share and the uniform doublet positions together. That is the family the
validated, never-run sweep searches, which makes the sweep the round's best next step.

## 6. What is pending, and why

| item | state | needs |
|---|---|---|
| Dodge sweep, tier C | tiers A and B done and null; C (1,080 alphabets) launch-ready and resumable | Owner's go-ahead: ~57 h at 10 workers, or ~34 h if the 60% prefilter is added and validated first; run with `stay_awake.py`. `powershell -ExecutionPolicy Bypass -File agents\laneO_quagmire_dodge\launch_sweep.ps1 -Tier C -NProc 10` |
| Clock-variant scorer | not built; lane W showed the existing scorer cannot see this variant | A new algorithm: a beam decode over skip forks inside a base_0 search, with its own planted controls, then a C port. Several days, uncertain to work, and even a working scorer faces a key space of ~10^96 (free sigma) unless sigma is assumed keyword-built. Hope 2/10 |
| Common Crawl half of the hash hunt | 1,044 host-scoped queries planned | Common Crawl's index back up; then `plan --no-wayback`, `fetch`, `hash` |
| 2014 onions 1 to 6 | documented, not queried | Owner's decision to add the community-attributed tier to the allowlist |
| Upstream register text | Moby-Dick used in place of Pride and Prejudice | Optional: owner's OK to download Gutenberg #1342 (~770 KB) to match upstream exactly |
| Marsaglia CDROM units (gap audit #7) | not started | A 634 MB archive.org download, owner's OK; low prior |

## 7. Files added this round

- `REPORT_ROUND2.md` (this file), `docs/BRIEF_ROUND2.md`
- `research/scout6_delta.md`, `research/gap_audit.md`
- `hashhunt/cicada_onions.md`, `hashhunt/cicada_onions_allowlist.txt`; `hashhunt.py` allowlist mode and a
  Windows file-lock retry; README section "Scope: the allowlist mode"
- `agents/laneO_quagmire_dodge/` (port patch, setup, MSVC build, env, launcher, controls, adjudicator, audit, logs)
- `agents/laneP_hashhunt/RESULTS.md`, `agents/laneQ_superposition/`, `agents/laneR_transcriptions/`
- `lp/t7_lag5_lines.py`
- `agents/laneW_clock_dodge/` (scorer copy, clock word model, measurement, diagnosis, audit; `orch_check.py`)
- `AGENTS.md`, `CHANGELOG.md`, `toolbox/` (CONSTRAINTS, TECHNIQUES, fingerprint, runes, nulls, score), `jobs/` (seven jobs), `.claude/agents/lp-*.md`
- `jobs/technique-survey/runs/` (three surveys), `jobs/hypothesis-gate/runs/` (gate reports and simulators), `agents/laneS_totient_skip/`
