# Lane W: the dodge-aware scorer on the clock-dependent Quagmire dodge

Job: port-community-code, 2026-10-17, model claude-haiku-5-5. Community code: `dl/aldegonde_port` (upstream
04f5ccc, unmodified; lane W edits nothing under `dl/`). Everything lane W wrote is in `agents/laneW_clock_dodge/`.

## Verdict

- **The clock variant is not recovered.** 0/20 planted keys rank 1 against 2,000 wrong keys (median z +0.3). Below the
  90% bar in the brief, so no sweep is priced or launched.
- **The odometer reference is recovered 17/20** with exact-tie equivalents counted as wins (0/20 strictly). The three
  misses are genuine: a non-equivalent wrong key scores higher.
- **The clock failure is in the path, not the score.** The word model is correct: with the true key and the true phase
  of every rune, the plaintext decrypts exactly (1,802 of 1,802 runes), and the true key scores above all 2,000 wrong keys
  on 20 of 20 plants. What breaks is inferring the clock path from the ciphertext (section 5).

## 1. What dodge_aware_scorer's own planted test enciphers with

From `dl/aldegonde_port/experiments/dodge_aware_scorer.py`, `main()`, read in full.

- **Cipher:** `doublet_phase_test.encipher`, the ODOMETER, variants `advance` and `hold`. It is not
  `quagmire_dodge.encipher`.
- **Plaintext:** `matched_register` over the LP's first 400 word lengths, from `PROSE_CACHE`.
- **Known to the score (passed as the truth):** K (keyed alphabet), `offsets` (one-zero schedule), `startdials` (a0, b0).
- **Enumerated:** nothing. The wrong keys are 60 random draws in each of three categories: alphabet only, schedule only,
  everything. There is no dials-only category.
- **Fitted by the scorer:** a clock phase per 18-rune window (5 options, three alternating passes), and a relabelling of
  the cipher symbols (greedy assignment, which the code calls base_0). Seed: a five-phase sum.
- **Not present:** no base_0 in the planted cipher (the odometer has none), no sigma, no "disk".
- **Its own result on the port** (`out/upstream_dodge_aware_selftest.txt`, exit 0): z +12.7 to +18.2 in all six
  categories (two variants, three categories), all FOUND. This reproduces the "z 12 to 20" claim for the odometer only.

## 2. Measurement

Setup: 20 planted keys per variant, each scored against 2,000 wrong keys (500 in each of four categories). Register:
Moby-Dick via `DODGE_PROSE`, the first 400 LP words (1,802 runes). Odometer: `doublet_phase_test.encipher`, `advance`.
Clock: `quagmire_dodge.encipher` with `schedule(zeros=1)`, sigma = `conj_shift(random permutation, delta)`, base_0 random,
as in lane W's simulator. Source: `out/measure.json`, `out/summary.json`, `out/diagnose.txt`.

| | odometer (own word model) | clock (`quagmire_dodge.encipher`) |
|---|---|---|
| rank 1, ties lose (strict) | 0/20 | 0/20 |
| rank 1, ties counted as wins | 17/20 | 0/20 |
| rank 1, dials / sigma category excluded | 17/20 | 0/20 |
| rank 1, equivalent keys removed | 17/20 (misses: plants 1, 4, 5) | not applicable |
| median z, all 2,000 wrong | +8.2 | +0.3 (range -1.3 to +2.3) |
| median z, equivalent keys removed | +14.4 | not applicable |
| exact ties with the true key, sigma category | not applicable | 0 in 20 plants |
| median fitted phase accuracy (per rune) | not applicable | 0.188 (chance 0.2) |
| median fitted base_0 accuracy | identity: 1.00 | 0.034 (chance 1/29) |
| oracle: true phase per rune, same key | not applicable | beats the best wrong key on 20/20 |

- Literal run (the clock ciphertext scored by the UNMODIFIED odometer path, planted dials (0,0)): 0/20, median z -0.2.
- The misses on the odometer (equivalents removed): plant 1 by an "everything" key (-3.495 vs -3.549); plants 4 and 5 by
  "schedule" keys (-3.457 vs -3.503; -3.491 vs -3.505).
- Median skips (clock advances without a step) per 1,802 runes: 63.

## 3. Odometer ties: an exact symmetry, not a scorer bug

Checked in `diagnose.py` sections 1a and 1b, and `summary.py`.

- With K and the schedule fixed, changing ONLY the outer dial b leaves the score and the assignment exactly unchanged.
  Tested with pure b-shifts of +1 and +5 on 5 plants (difference 0.00e+00 each, assignment unchanged); the shifts are
  applied to the start dials, so every word's b moves by the same constant. In the odometer cipher b enters only as an
  additive constant on cipher symbols (c = K[...] + b), so a constant b relabels the cipher alphabet, and the assignment
  absorbs a relabel exactly. Changing the inner dial a changes the score by 0.02 to 0.51 nats per rune.
- The tie set equals, exactly, the wrong keys that keep K and the schedule and share the true a. Checked on all 20 plants
  (ties = equivalent set, `True` every time). Median 15.5 per plant, the expected 500/29.
- So the dials category holds equivalent keys, not wrong ones. Counting them as wins is the right rule. The sweep's
  "outer absorbed" convention (lane O's `our_plant.py` docstring) relies on the same fact.
- The clock sigma category has no ties in any of the 20 plants.

## 4. Clock: the word model and the assignment are correct

- `verify_port.py` step 3: the clock word maps equal the inverse of base0_inv[base_w] for all 400 words.
- `diagnose.py` section 2: with the true K, schedule, sigma, base_0 and the true phase of every rune, decrypting through
  the scorer's own word maps recovers the plaintext exactly on plants 0, 1 and 2 (1,802 of 1,802 runes, 0 mismatches).
- `diagnose.py` section 4 (oracle): with the true phases, the scorer's assignment recovers base_0 exactly (1.00) on all 20
  plants, and the planted key scores -2.96 to -3.01 nats per rune against -3.73 to -3.75 for the best of 2,000 wrong keys
  (margin about 0.75). Caveat: the wrong keys get the fitted path, which is their best case, so the comparison favours
  them. The margin is large enough that this does not change the conclusion.

## 5. Diagnosis: which assumption breaks

The score path assumes the clock advances exactly one step per rune inside an 18-rune window, so it fits one phase per
window. The cipher skips the clock about once per 29 runes (a would-be repeat is re-emitted one step on, 63 times in 1,802
runes). A skip is invisible in the ciphertext. Two things follow.

1. Inside a window, a skip shifts every later phase in that window, and the window fit can only pick a compromise phase.
2. The word maps are cumulative in this cipher: base_w = base_0 . S_0 . ... . S_(w-1) with S_j = alpha[ph_j] . sigma, where
   ph_j is the phase of word j's last rune. One wrong boundary phase replaces every later word map with a different
   permutation. The odometer has no such coupling: its word map is closed form in the word index, which is why the same
   windowed path works for it.

The seed (clock equals position, the assumption `dodge_scorer_check.py` makes) is wrong after the first skip, the first
assignment is built from wrong maps, and the alternation never recovers. Measured: phase accuracy 0.19 against chance
0.2, base_0 accuracy 0.034 against chance 1/29. The assignment is not at fault (1.00 with the true phases), and the model is
not wrong (exact decryption).

## 6. What a scorer would need

The missing piece is the phase path, not the score. A usable scorer has to do one of these, and both are new algorithms
rather than a tweak to `dodge_aware_scorer`:

- A joint search over base_0 with a left-to-right decoder that tracks skips. Given base_0, K, the schedule and sigma,
  the decode forks at about 5% of runes, not rarely (orchestrator correction, section 12: 97 forks per 1,802 runes, and every
  true skip is one). The community's "0 to 6 runes in 12,388" is the residual error of a beam search that holds the key,
  not the fork rate; their collision rate is 4.5-6.5% (`quagmire-dodge.md`). So each candidate base_0 costs a beam
  decode, not one decode, and the search needs its own planted controls.
- Or a base_0 estimate from a skip-free stretch, which is short at one skip per 29 runes.

The oracle margin (about 0.75 nats per rune) says that a scorer which finds the path would separate the key easily. I stopped
here as the brief asks; nothing was built beyond the diagnostic.

## 7. Throughput and the sweeps (not priced)

- No sweep is priced or launched: the clock variant is 0/20, below the 90% bar. Step 3 is not triggered.
- Measured per key on one process, 1,802 runes, with three workers running concurrently (`out/measure.json`):
  clock path 0.0129 s (about 78 keys/s/core), odometer path 0.0136 s (about 74), literal path 0.0120 s (about 83).
  Lane O's C kernel does about 3,000 keys/s/core, so this Python-plus-numpy scorer is roughly 40 times slower. Any future
  clock scorer would need a C port as well.
- The vectorised copy of `dodge_aware_scorer.score` runs about 13 times faster than the community's Python version
  (0.18 s per key in its own selftest).

## 8. Deviations from upstream, with reasons

1. `clock_lib.py` vectorises `dodge_aware_scorer.score` (numpy, same arithmetic). It agrees with the community function to
   0.00e+00 on three odometer keys (`verify_port.py` step 1). The community file is untouched.
2. The clock word model replaces `word_shifts` inside the same score path (`score_clock`). The seed is clock = position.
   The refit uses the word chain from the previous pass (simultaneous, not sequential). A sequential refit was not tried.
3. 2,000 wrong keys per planted key, not the 60 per category in the community main. The brief asks for at least 2,000.
4. Register: Moby-Dick via `DODGE_PROSE`, as lane O did.
5. Odometer reference uses `advance` only (lane O's variant). The community main also runs `hold`.
6. Planted keys use random K permutations rather than keywords. For the clock variant the key parts are drawn as in the
   simulator (`quagmire_dodge_clock_cipher.py`).
7. The literal path plants dials (0,0), because the odometer scorer has no sigma slot.
8. The upstream selftests run through `runpy` with the port's `src` added to `sys.path`, because `python -I` hides
   `PYTHONPATH`. No code changed.
9. Three workers plus the main process for the measurement (see limits).

## 9. Limits and what was not done

- Processes: the measurement ran three workers plus the main process. An earlier launch with four workers plus the main
  (five processes) ran for a few minutes before I stopped it and relaunched. It wrote no output and was killed by PID.
  Another job's `hashhunt` process (pid 5188) was running on the same PC; I did not touch it.
- Keep-awake: `stay_awake.py` held the PC awake for the 528-second run and exited with it.
- Time: the measurement took 528 s wall. Nothing ran over two hours. No network.
- Memory: free RAM at the start was 3.5 GB of 15.9 GB. Per-worker memory was not measured.
- Not done: no sweep was ported, no `dl/aldegonde_port_clock` copy was made, and no launch command was written (step 3 is
  not triggered). The sequential refit and the base_0 search (section 6) were not tried.
- The odometer reference was measured against its own planted keys only, not against lane O's C kernel.

## 10. Audit

- `audit/audit_static_laneW_entries.txt`: `audit_static.py` on the port tree, entries = the eight community modules this lane
  imports. Closure: 47 files. Risky sites and judgements:
  - network, `doublet_position_profile.py:188` in `main`: `main` is not called by any lane W path. Unreachable.
  - network, `ea_direction_test.py:100` in `main`: same. The register comes from `DODGE_PROSE`.
  - process, `external_text_length_match.py:155` in `fetch` (`curl`): `fetch` is not reached.
  - network, `sigma_algebraic_floor.py:138` in `main`: not reached.
- `audit/reach_laneW.py`: name-based reachability from every community function lane W calls. No sink call reached, and
  `main`, `fetch` and `selftest` not reached.
- Lane O's closure audit (`agents/laneO_quagmire_dodge/audit/closure_files.txt`) already lists all eight modules.
- `audit/fixture_rerun.txt` reproduces the fixture audit; `audit/fixture_diff.txt` is empty (identical).

## 11. PROOF (`jobs/port-community-code/PROOF.md`), line by line

Output
1. PASS. Audit saved to `audit/`, every risky site judged in section 10.
2. FAIL (ordering). `verify_port.py` and a smoke run executed community code before this audit file was written, so the
   audit is not older than every run log. This cannot be undone after the fact. The substance is covered: lane O's audit
   already covers all eight modules, and this audit and the reachability check found no reachable sink.
3. PASS. `git -C dl/aldegonde_clone status` is clean at HEAD 04f5ccc9152f24305309164482c798fdfdb97a67. Lane W edited only
   `agents/laneW_clock_dodge/`.
4. N/A. Lane W made no port. `port.patch` and `setup_port.sh` belong to lane O and were not rebuilt here.
5. N/A for a compiled kernel (none built). Nearest check: the vectorised copy against `das.score`, maximum difference 0.0 on
   three odometer keys. PASS on that analogue.
6. PASS. Upstream `dodge_aware_scorer.py` selftest exits 0 on the port (z +12.7 to +18.2, section 1). Upstream
   `quagmire_dodge.py` self-test passes (survivors 0.267 against the 0.2 prediction; zero-offset-free control doublet rate
   0.00000).
7. PASS as a measurement: 20 plants per variant, 2,000 wrong keys each, misses listed. The result fails for the clock
   variant (0/20).
8. N/A. No sweep was ported or launched, so there is no sweep smoke run. The 60-task measurement ran end to end in 528 s on
   three workers (about 26 s per task). Memory per worker was not measured, and no resume was tested.
9. PASS. Deviations listed in section 8.

Fixture
10. PASS. `audit_static.py` on the fixture tree reproduces `aldegonde_dodge_audit.txt` exactly (`audit/fixture_diff.txt` is
    empty).

## Files

- `clock_lib.py`: the scorer copy, the clock word maps, the instrumented encipher.
- `verify_port.py`: checks for the copy, the trace and the chain (all PASS).
- `measure.py`: the planting and scoring driver (`--planted 20 --wrong 2000 --procs 3`).
- `diagnose.py`, `summary.py`: the tie, invariance, decrypt, oracle and summary checks.
- `audit/`: the static audit, the reachability check, the fixture rerun and its diff.
- `out/`: `measure.json` (all scores), `measure.log`, `summary.json`, `diagnose.txt`, and the upstream selftest outputs.

## 12. Orchestrator check (claude-opus-5-5, 2026-10-17)

Fresh code (`orch_check.py`), fresh plaintext (Moby-Dick through `toolbox/runes.english_stream`, not the matched register),
new seeds. Output: `out/orch_check.txt`.

- **Recount of `out/measure.json`: confirmed.** Odometer strict 0/20, ties as wins 17/20, dials category dropped 17/20,
  median z +8.23, exact ties per plant median 15.5. Clock 0/20 either way, median z +0.32. Literal 0/20, median z -0.20.
- **Odometer outer dial: confirmed as a symmetry.** Shifting the start outer dial by d adds d to every cipher rune, on 5/5
  fresh plants. Those "wrong" keys are relabels of the true key, so counting their ties as wins is right.
- **Clock base_0 is an exact outer relabel.** Enciphering with base_0 = P gives P applied to the identity-base_0 cipher,
  rune by rune, on 5/5 fresh plants. The skip test (would-be rune equals the previous rune) survives a relabel, so base_0
  can in principle be fitted by assignment once the path is known. This agrees with section 4 (assignment 1.00 with the
  true phases).
- **Skips are forks, and there are many.** A decoder written from scratch, given the TRUE full key and no phase
  information, decodes 20/20 plants exactly when each fork is settled by the true plaintext, and 0/20 (median accuracy
  0.045, chance level) when every fork takes the no-skip reading. Per ~1,802 runes: skips median 62 (44-92), forks median
  97 (73-135). Every true skip is a fork, because the no-skip reading of the emitted rune is also consistent. This
  corrects section 6's "rare forks" (fixed above). It sharpens the diagnosis in section 5: even with the key, recovering
  the path needs a language model in the loop.
- Lane W's verdict stands: the clock variant is not recoverable with `dodge_aware_scorer`, and no sweep should be run for
  it with the existing tools.
- PROOF item 2 (audit written after the first run of community code) is accepted as a recorded ordering fail; lane O's audit
  of the same eight modules predates both runs, and nothing reachable touches the network or spawns a process.
