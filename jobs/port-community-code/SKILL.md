---
name: port-community-code
description: Audits, ports to this Windows PC and validates a community repository's analysis code so its search can run here. Use when asked to run, reproduce or port a community sweep, kernel or experiment.
---

## Trigger
The orchestrator names a community tree under `dl/`, the entry points, and what the run should produce.

## Inputs
- The clone (`dl/<name>`), its docs for the experiment, and the upstream commit (`git -C dl/<name> rev-parse HEAD`).
- `tools/audit_static.py`; the worked example of a full port: `agents/laneO_quagmire_dodge/` (patch, setup, MSVC build, env, launcher, controls, adjudicator).
- `docs/BRIEF_ROUND2.md` for this machine.

## Steps
1. Audit first: `python jobs/port-community-code/tools/audit_static.py dl/<name> <entry.py ...>` into the lane's `audit/`. Judge every risky site; stop and report if any is reachable and not explained.
2. Copy the clone (`cp -r dl/<name> dl/<name>_port`) and patch only the copy.
3. Port the parts Windows breaks: `fork` -> `spawn` with a pool initializer, `cc` builds -> MSVC (`agents/laneO_quagmire_dodge/build_kernel.bat`), hard-coded temp paths -> env vars, `PYTHONUTF8=1` for files opened without an encoding.
4. Write `port.patch` and `setup_port.sh`; rebuild from a fresh copy and diff against the working copy.
5. Validate: kernel against the Python reference, the upstream selftest, then our own control with >= 20 plants through the code's own score path (`agents/laneO_quagmire_dodge/diag_alphabet_kind.py` is the pattern).
6. When a control fails, replay the same key on fresh plaintext before blaming the port or the scorer (lane O's MOBIUS plant was a scorer miss, not a bug).
7. Smoke run one task with `agents/laneO_quagmire_dodge/launch_sweep.ps1`-style launching (BelowNormal, logged); measure time per task and memory per worker; rerun to test resume.
8. Write the lane's RESULTS.md with every number and the exact launch command, then run PROOF.md and fix every fail.

## Rules
- The owner decides on runs longer than 2 hours; give the cost and the command, do not start it.
- No network access from ported code; supply inputs from files already on disk and say which.
- `cmd //c start ...` from Git Bash can fail silently; launch with PowerShell `Start-Process` and check the process exists.
