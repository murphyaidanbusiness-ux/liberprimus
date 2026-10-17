# PROOF: attack-lane

Run on `agents/<lane>/RESULTS.md` before returning. Every line pass or fail. Fix every fail first.

## Output (checked by `python jobs/attack-lane/tools/check_results.py agents/<lane>/RESULTS.md`)
- [ ] Sections present: Hypothesis, Control, Null, Real result, Verdict
- [ ] A `Gate:` line links the hypothesis-gate report (`jobs/hypothesis-gate/runs/...`) or states why the lane predates the gate
- [ ] Control: planted key from the searched space, enciphered with the same cipher code, recovered at rank 1; plants and recoveries counted (`recovered k/n`), n >= 20 when the search is heuristic
- [ ] Null: >= 20 size-matched shuffles (increment shuffles within pages for chain-family models), with mean, sd and max of the best score
- [ ] Real result: best real score and its z against the null, plus the real best vs the null max
- [ ] Verdict is one of `NULL`, `CANDIDATE`, `INCONCLUSIVE (power)`; a `CANDIDATE` has the oracle result (`verify_solution.py --plaintext`: PASS or FAIL) and the first 120 runes transliterated

## By reading
- [ ] The key space searched and its size are stated, and what fraction of it was covered
- [ ] Every number in the summary appears in a log or output file under `agents/<lane>/` (no invented numbers)

## Fixture
- [ ] `check_results.py data/fixture/good_RESULTS.md` prints PASS and `check_results.py data/fixture/bad_RESULTS.md` prints FAIL with the reasons in `data/fixture/expected.md`
