# PROOF: community-scout

Run on `research/scoutN_<name>.md` before returning. Every line pass or fail. Fix every fail first.

## Output
- [ ] `python jobs/community-scout/tools/check_scout.py <file>` prints PASS (sections, dated rows with a URL or local path and a y/n/unclear flag, no onion or gateway URLs)
- [ ] Every item was opened in this run; items seen only in a search snippet are listed as such and not counted
- [ ] Every solve or partial-solve claim says whether an oracle or a planted control backs it (`verified` = y only then)
- [ ] The "what changes" section maps each item to a concrete action or says "no action", and names any of our lanes it affects
- [ ] Sources that failed (refused, 4xx, paywalled) are listed under Sources checked, not skipped silently

## Fixture
- [ ] `check_scout.py data/fixture/good_scout.md` prints PASS and `... data/fixture/bad_scout.md` prints the FAIL lines in `data/fixture/expected.md`
