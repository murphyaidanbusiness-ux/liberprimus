# Liber Primus campaign — guide for future sessions

This repository is the record of a multi-agent cryptanalysis campaign against the unsolved part of
Cicada 3301's Liber Primus (LP2, pages 0–54, 12,956 runes). It did NOT solve the book. It produced
fourteen controlled negative results, six verified structural constraints, and a safe archive-hash tool.
Read REPORT.md first, then research/SYNTHESIS.md.

## Layout
- `lp/`        loader (`lpdata.py`), the orchestrator's own tests (t1–t6), candidate verifier, early and final reports
- `agents/`    one directory per attack lane (A–N); each has RESULTS.md (the deliverable), code, nulls, raw outputs
- `research/`  five scout reports and SYNTHESIS.md; small helper code under s2/ s3/
- `docs/`      the briefs every lane was given (BRIEF_COMMON.md, CRIB_ADDENDUM.md)
- `hashhunt/`  stdlib-only tool to hash archived tor2web captures against the page-56 hash (text-only, never renders)
- `dl/`        git-ignored; community repos fetched by `scripts/fetch_sources.sh`

## Conventions (keep them)
- Run everything from the repository root; scripts use `./dl/...`, `./lp/...` paths.
- Data object: pages 0–54, SHA-256 of comma-joined indices 023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585.
- Every attack needs a planted-key positive control and a size-matched shuffle null before its result counts.
  Chain-model nulls must shuffle increments within pages (keeps the doublet deficit) or the baseline is wrong.
- Candidates go to the community oracle (`dl/dukotah/liber-primus/verify_solution.py --plaintext`) and to `lp/verify_candidate.py`.
- Never claim a solve without the oracle passing. Negative results are the product here; write them down.
