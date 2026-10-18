# Expected audit of the fixture (aldegonde upstream 04f5ccc, the five dodge-sweep entry points)

`python jobs/port-community-code/tools/audit_static.py dl/aldegonde_clone experiments/dodge_priority_sweep.py experiments/dodge_score_kernel.py experiments/dodge_aware_scorer.py experiments/quagmire_dodge.py experiments/quagmire_dodge_decode.py`
must reproduce `aldegonde_dodge_audit.txt` in this folder: a closure of 53 files and exactly these 8 risky sites (no `write` sites):

| kind | site | judgement (lane O, round two) |
|---|---|---|
| process | dodge_score_kernel.py:48 `_library` | the known `cc` compile; replaced by the MSVC DLL via `DODGE_KERNEL_DLL` |
| native | dodge_score_kernel.py:61 `_library` | loads that compiled kernel; acceptable |
| network | doublet_position_profile.py:188 `main` | not reachable from the entry points |
| network | ea_direction_test.py:93 `main` | not reachable (the register is supplied by `DODGE_PROSE`) |
| process | external_text_length_match.py:155 `fetch` | `curl`; not reachable |
| network | sigma_algebraic_floor.py:138 `main` | not reachable |
| process / native | walk_score_kernel.py:54 / :67 `_library` | an older kernel's compile; not called by the sweep |

Reachability was checked by lane O's call-graph walk (`agents/laneO_quagmire_dodge/audit/reachability.txt`).
