# PROOF: exhaustion-census

Run on your census file (`research/census/<part>.md`) before returning. Every line pass or fail. Fix every fail first.

## Output (checked by `python jobs/exhaustion-census/tools/check_census.py <file> --min N`)
- [ ] Sections exist: `## Bottom line`, `## Census`, `## Reopen candidates`, `## Sources checked`
- [ ] The census table has at least N rows (the orchestrator gives N), each with all 10 cells
- [ ] Every row's `control` and `null` cells are `y`, `n` or `unclear`; `strength` is `A`, `B`, `C` or `D`
- [ ] Every row's `source` is an http(s) URL or a local path that exists (a `:line` or `#entry` suffix is allowed)
- [ ] Every row's `constraint` cell starts with `dead C<n>` (the method cannot produce LP2's fingerprint, constraint named)
      or `consistent` or `unclear`
- [ ] Every reopen candidate names a census id whose strength is C or D and whose constraint cell is not `dead`
- [ ] No URL points at an onion address or a tor2web-style gateway

## By reading (two people would agree)
- [ ] Every row was read in its source in this run; nothing is filled in from a search snippet or from memory
- [ ] `strength` follows the definitions in SKILL.md: A needs both an exhaustive stated space and a planted key
      recovered by the same search; a sweep with no stated space is D, not C
- [ ] `our coverage` names the lane (A-W) or says `none`, checked against `REPORT.md` and `REPORT_ROUND2.md`
- [ ] Sources that failed (refused, 4xx, too large) are listed under Sources checked, not skipped silently

## Orchestrator (after the parts are back)
- [ ] `python research/census/write_judgments.py && python research/census/merge.py` exit 0: every row of every part has
      exactly one verdict and one bucket, and no dead row is bucketed elsewhere
- [ ] Each re-grade quotes the constraint number and the reason; each `partial` row says what a finite re-test would search

## Fixture
- [ ] `python jobs/exhaustion-census/tools/check_census.py jobs/exhaustion-census/data/fixture/good.md --min 3` prints
      PASS, and the same on `data/fixture/bad.md` prints the FAIL lines listed in `data/fixture/expected.md`
