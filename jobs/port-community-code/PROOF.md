# PROOF: port-community-code

Run on the lane's `RESULTS.md` and files before returning. Every line pass or fail. Fix every fail first.

## Output
- [ ] `audit_static.py` output for the entry points is saved in the lane's `audit/`, and every risky site in it has a one-line judgement (unreachable, replaced, or acceptable and why) in RESULTS.md
- [ ] Nothing from the community tree ran before that audit was written (the audit file is older than every run log)
- [ ] The upstream clone under `dl/` is unchanged (its manifest or `git -C dl/<clone> status` is clean); all edits are in a copy
- [ ] `port.patch` plus `setup_port.sh` rebuild the copy from a fresh clone, and the rebuilt tree is identical to the working copy
- [ ] Any compiled kernel equals the upstream Python reference on a planted key (max difference stated)
- [ ] The upstream selftest passes on the port, with its numbers quoted
- [ ] An independent planted control of ours, through the code's own score path: `recovered k/n` with n >= 20 and the misses listed
- [ ] A one-task smoke run of the real job finished, its time per task and memory per worker are stated, and a rerun skipped the finished task
- [ ] Every deviation from upstream (inputs, register texts, parameters) is listed with the reason

## Fixture
- [ ] `audit_static.py` on the fixture tree reproduces `data/fixture/aldegonde_dodge_audit.txt` (53 files, the 8 sites in `expected.md`)
