# Expected checker output on the fixtures

`check_results.py data/fixture/good_RESULTS.md` -> `PASS`

`check_results.py data/fixture/bad_RESULTS.md` -> exactly:
```
FAIL
  - missing section '## Real result'
  - no 'Gate:' line
  - Control: no 'recovered k/n' count
  - Control: rank 1 recovery not stated
  - Null: fewer than 20 shuffles stated
  - Null: 'sd' not given
  - Null: 'max' not given
  - Verdict: first line must start with one of ('NULL', 'CANDIDATE', 'INCONCLUSIVE (power)')
```
