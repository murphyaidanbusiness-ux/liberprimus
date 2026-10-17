# PROOF: verify-lane

Run on `runs/YYYY-MM-DD-<lane>.md` before returning. Every line pass or fail. Fix every fail first.

## Output
- [ ] The report lists every headline number from the lane's RESULTS.md summary, one row each, with the lane's value and ours
- [ ] Each row says `reproduced`, `differs` (with both values and the reason found) or `not checked` (with why)
- [ ] Our code is saved next to the report (`runs/<lane>_verify.py`) and does not import the lane's code; it may import `lp/` and `toolbox/`
- [ ] Re-running `runs/<lane>_verify.py` prints the numbers in the report
- [ ] At least one control is replayed on a fresh seed or fresh plaintext, not only on the lane's own plant
- [ ] Any `differs` row names which number should be trusted and whether the lane's verdict changes

## Fixture
- [ ] `python jobs/verify-lane/data/fixture/laneQ_verify.py` prints `lag 6002: 304 6954 z=+4.18` and a top-lag list starting with lag 6002, matching `data/fixture/expected.md`
