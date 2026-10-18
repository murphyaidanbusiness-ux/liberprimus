# Liber Primus campaign

A controlled cryptanalysis campaign against the unsolved part of Cicada 3301's Liber Primus (LP2: pages 0-54,
12,956 runes, 29 symbols). It has not solved the book. Negative results with planted controls are the product.
Read `REPORT.md`, then `REPORT_ROUND2.md`, then `toolbox/CONSTRAINTS.md` (the fingerprint every idea must meet).

One orchestrator, one folder per job. Find the job below, open its folder, follow SKILL.md.

## Rules that apply to every job
- Read the job's SKILL.md fully before doing anything, and the last five entries of CHANGELOG.md.
- Reuse what is in the job's tools/ and in toolbox/ before building anything new; save what you build to tools/ and link it.
- Run the job's PROOF.md before returning. Fix every fail first.
- Run everything from the repository root. Data pin: SHA-256 of pages 0-54's comma-joined indices is
  023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585 (`lp/lpdata.py` asserts it).
- Never claim a solve without the community oracle passing (`dl/dukotah/liber-primus/verify_solution.py --plaintext`).
- Archive scraping only through `hashhunt` with `--allowlist hashhunt/cicada_onions_allowlist.txt`. No Tor, no onion or
  gateway contact, no wider allowlist without the owner's yes in chat.
- The PC is shared with the owner's own work: long jobs at below-normal priority, check free RAM, ask before anything over 2 hours,
  and remember it idle-sleeps after 15 min: start `python agents/laneO_quagmire_dodge/stay_awake.py <pid>` alongside an
  unattended run (a per-process keep-awake request; it changes no settings and ends with the run), and check progress after the first task.
- If a job is not listed here, stop and ask.

## Jobs
| When asked to... | Open |
| --- | --- |
| research techniques, methods or literature that might break LP2 | jobs/technique-survey/ |
| decide whether a cipher idea is worth a lane | jobs/hypothesis-gate/ |
| attack, sweep or test a key model on LP2 | jobs/attack-lane/ |
| check a finished lane's numbers before they are reported | jobs/verify-lane/ |
| run or port a community repository's sweep or experiment | jobs/port-community-code/ |
| hunt archives for the page-56 hash | jobs/hashhunt-run/ |
| find what the community has done or claimed recently | jobs/community-scout/ |
| list what the community has already ruled out, and how solidly | jobs/exhaustion-census/ |

Each job also has a Haiku agent wrapper, `.claude/agents/lp-<job>.md` (spawn it by that name; it just points at the job folder).

## Shared
- `toolbox/`: `CONSTRAINTS.md` (C1-C6 and quick exclusions), `TECHNIQUES.md` (the graded technique catalogue),
  `fingerprint.py` (C1-C6 for any rune stream, with a gate), `runes.py` (English to runes), `nulls.py` (doublet-preserving
  shuffles), `score.py` (IoC, quadgrams).
- `lp/`: the loader, the orchestrator's own tests t1-t7, `verify_candidate.py`.
- `agents/`: one directory per lane (A-N round one, O-R round two), each with RESULTS.md, code and outputs.
- `research/`: scout reports, the gap audit, SYNTHESIS.md. `docs/`: the lane briefs (`BRIEF_ROUND2.md` for this machine).
- `dl/`: git-ignored community repos (`scripts/fetch_sources.sh`); ports go in `dl/<name>_port`, never edit a clone.
- `CHANGELOG.md`: every fix, dated, with the job and the model that was running.
