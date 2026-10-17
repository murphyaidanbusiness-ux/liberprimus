# PROOF: hashhunt-run

Run on the run's working directory and its write-up before returning. Every line pass or fail. Fix every fail first.

## Output
- [ ] `python -I hashhunt/hashhunt.py selftest` ends `SELFTEST PASSED (39/39 checks)` (or more checks, all passing) on this run's code
- [ ] Every `plan` and `fetch` command in the write-up has `--allowlist`; none has `--blind`
- [ ] The allowlist is `hashhunt/cicada_onions_allowlist.txt`, or a file the owner approved in chat, with the approval quoted in the write-up
- [ ] `python jobs/hashhunt-run/tools/check_scope.py <dir> <allowlist>` prints PASS
- [ ] The write-up states queries run and completed, captures found, fetch outcomes by status, captures hashed, functions used, and the number of matches
- [ ] No stored capture was opened, rendered or quoted; only metadata (URL, timestamp, size, hashes) appears in the write-up
- [ ] A match, if any, is reported as the banner/`matches.jsonl` provenance only, and re-checked with a second implementation if its function is UNVERIFIED

## Fixture
- [ ] `check_scope.py data/fixture/scoped hashhunt/cicada_onions_allowlist.txt` prints PASS and `check_scope.py data/fixture/blind ...` prints FAIL (blind query, off-list host)
