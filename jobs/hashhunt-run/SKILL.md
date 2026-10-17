---
name: hashhunt-run
description: Runs the page-56 hash hunt over archived captures of allowlisted Cicada onion hosts only, and writes up the result. Use when asked to hash, hunt or check archives for the page-56 target.
---

## Trigger
The orchestrator asks for a hash-hunt run (for example the Common Crawl half once its index is up).

## Inputs
- `hashhunt/` (tool, README, NOTES), `hashhunt/cicada_onions_allowlist.txt` and `hashhunt/cicada_onions.md` (evidence per label).
- The previous run: `agents/laneP_hashhunt/RESULTS.md` and `hashhunt/data/` (resumable state).

## Steps
1. Run `python -I hashhunt/hashhunt.py selftest`; stop if it does not pass.
2. Check the archive is up with one host-scoped query before a long plan (Common Crawl returned 504 for a whole day in round two).
3. `plan --run` with `--allowlist hashhunt/cicada_onions_allowlist.txt`, `--contact`, and `--no-cc` or `--no-wayback` as asked; `--delay 3` or more.
4. `fetch` with the same `--allowlist`; then `hash --jobs 3`.
5. Run `python jobs/hashhunt-run/tools/check_scope.py hashhunt/data hashhunt/cicada_onions_allowlist.txt`.
6. Write the result into the lane's RESULTS.md (numbers per stage, from `plan_state.jsonl`, `fetch_log.jsonl`, `results/`).
7. Run PROOF.md and fix every fail before returning.

## Rules
- Only allowlisted hosts. An onion address says nothing about the site behind it, so `--blind`, wider allowlists, Tor and any direct onion or gateway contact are out unless the owner says otherwise in chat.
- Never open, render or quote a stored capture. Metadata and hashes only.
- Stop a run against a failing service (repeated 5xx) rather than retrying for hours; say when to resume.
