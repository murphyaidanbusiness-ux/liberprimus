# Expected checker output on the fixtures

`check_scout.py data/fixture/good_scout.md` (a copy of round two's `research/scout6_delta.md`) -> `PASS`

`check_scout.py data/fixture/bad_scout.md` -> `FAIL` with exactly:
- no section heading containing 'change'
- no section heading containing 'Sources checked'
- onion or gateway URL: http://ky2khlqdf7qdznac.onion.to/
- row without a URL or local path: | 2026-10-12 | somewhere | big claim | maybe |
- row without a verified flag (y/n/unclear): | 2026-10-12 | somewhere | big claim | maybe |
