# PROOF: hypothesis-gate

Run on the gate report you are about to return (`runs/YYYY-MM-DD-<hypothesis>.md`). Every line pass or fail. Fix every fail first.

## Output
- [ ] The report names the hypothesis, links its simulator `runs/<hypothesis>_cipher.py`, and the simulator defines `encrypt(plain, words, rng)`
- [ ] The report pastes the full `gate_sim.py --seeds 3` output for that simulator, including the final `GATE ...` line
- [ ] The verdict is exactly one of: `PROCEED` (gate pass, not tested before), `EXCLUDED by <constraint ids>` (gate fail), `ALREADY TESTED by <lane or ledger path>`
- [ ] A gate FAIL is never followed by PROCEED, and every failed constraint id is named in the verdict
- [ ] The prior-coverage line lists the grep terms used and the files searched (REPORT.md, REPORT_ROUND2.md, the ledgers in toolbox/CONSTRAINTS.md)
- [ ] For PROCEED, the report states the key space size and a planted-control and null design for the attack-lane job
- [ ] The simulator draws every key from `rng` (two seeds give different ciphertexts on the same plaintext)

## Fixture
- [ ] `gate_sim.py` on each file in `data/fixture/*.py` gives the final line listed in `data/fixture/expected.md`
