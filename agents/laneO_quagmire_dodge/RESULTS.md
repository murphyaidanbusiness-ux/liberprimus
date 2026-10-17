# Lane O: port of the zero-offset dodge priority sweep (Oosterhof, upstream 04f5ccc)

> **Orchestrator update (section 7): the full run IS cleared.** The failed control (c) is not a port or
> plant bug. It is one instance of a ~5% failure mode of the community's scorer: 95 of 100 fresh
> keyword-alphabet plants rank 1 against 2,000 wrong schedules (median z +23.7), and the same MOBIUS key
> enciphered on a different English text ranks 1 at z +16. The full run was not started because the
> machine was busy; see section 7 for the launcher and its single-task smoke run.

**Lane verdict as handed back: the port works, but two validations fail, so the full run is NOT cleared.**

- (c) Our odometer + dodge control: FAIL. The planted key ranks 24,558 of 105,980 (z = +0.70).
- (b) Community selftest, every schedule of the planted alphabet: FAIL by one place. The planted key
  ranks 2 of 105,980 (z = +19.4). The top-ranked schedule was not identified.

Per the brief, validation failures mean stop and report. The smoke run was stopped after (c) failed and
produced no output. The orchestrator decides whether the 360 core-hour run goes ahead.

## 0. Register (deviation from upstream)

The sweep's register is Gutenberg #1342 (Pride and Prejudice, `tempdir/pg1342.txt`). That file is not on
this machine, and the brief forbids web access, so it was not downloaded. Per the orchestrator, the
register is Moby-Dick:

- `dl/dukotah/liber-primus/data/keys/armada18/melville_moby_dick.txt`
- sha256 `9a6844ac0703853720010787c7b6c70b0020f1ab1862dcd74452fa46474d1215`, 1,276,263 bytes, UTF-8, CRLF,
  no `1342` string.
- Set with `DODGE_PROSE` (patch 3). This deviates from upstream. The register only supplies plaintext for
  controls and the null tables. With `BANDS` empty, the schedule set does not depend on those tables
  (`pooled`, `v4`, `v6` are computed but unused). The letter statistics of long English prose should not
  change the search, but the controls below use this register, so they are not the upstream controls.

Earlier numbers from a `pydoc_data` stand-in register were withdrawn and are superseded.

## 1. Step 0 security audit (read-only, before anything ran)

Files: `audit/`. `ast.parse` only, nothing imported or executed. The closure of the five entry points is
51 files: 26 `experiments/` plus 25 `src/aldegonde/` (`audit/closure_files.txt`, `audit/closure.txt`).

- Network: `urlretrieve` to gutenberg in `main()` of `ea_direction_test`, `doublet_position_profile` and
  `sigma_algebraic_floor`; `curl` in `external_text_length_match.fetch()`. All behind a `__main__` guard or
  an unreached `main()`. A name-resolved call graph from each entry point confirms none is reached
  (`audit/reachability.txt`).
- Processes: only the known `cc` compile in `dodge_score_kernel._library` is reachable.
- Deletion, `eval`/`exec`, `pickle`, `marshal`, dynamic import: none in the closure.
- Writes: in-tree candidate files, and the tempdir progress file and cached `.so`.
- Import-time code only reads packaged n-gram data. No stdlib-shadowing names, no `.pth`, `sitecustomize`,
  `conftest` or binaries anywhere in the tree. The clone matches `audit/clone_manifest.sha256`.
- Caveat: `_library` loads `tempdir/dodge_score_<hash>_29.so` if it exists, a predictable temp path. The
  port bypasses it when `DODGE_KERNEL_DLL` is set.

Nothing suspicious beyond this.

## 2. Patches (`port.patch`, 189 lines, CRLF sources)

Apply with `patch -p1 --binary`. `setup_port.sh` copies the clone, verifies the manifest and applies the
patch. A fresh apply was checked byte-identical to the working port.

1. `dodge_score_kernel.py::_library`: `DODGE_KERNEL_DLL` loads a prebuilt DLL, otherwise the original `cc` path.
2. `dodge_priority_sweep.py`:
   - `get_context("spawn")` instead of fork.
   - `_init_worker(lens, keys)` is the pool initializer: it runs `_prepare(lens)` in each worker and takes the
     parent's `keys` list, so `keys[lo::240]` matches the fork version by construction.
   - The pool is created only if there is work.
   - On resume the merged `best` is trimmed to `KEEP` before new work (the fork version left it untrimmed).
   - `DODGE_PROGRESS` and `DODGE_OUT` override the two paths; parent directories are created.
   - `--tasks a,b,c`, range-checked to 0..239.
3. `ea_direction_test.py`: `DODGE_PROSE` overrides `PROSE_CACHE`. The other closure modules import that
   name from here, so one override reaches all of them (checked by grep).
4. The C kernel needed no change: `/W3`, no warnings.

## 3. Build and environment

- `build_kernel.bat` (MSVC 14.51, `/O2 /std:c11 /W3 /LD /DM=29 /EXPORT:score_dials`) produces
  `build/dodge_score_kernel_m29.dll`. `build/` and `*.dll` are git-ignored. The vswhere message is harmless.
- `env.sh` sets `PYTHONUTF8=1` (aldegonde's n-gram loader calls `open()` without an encoding, and
  cp1252 fails on byte 0x8f), `PYTHONPATH=dl/aldegonde_port/src` (not installed), `DODGE_KERNEL_DLL`, and
  `DODGE_PROSE`.
- Memory: about 0.8 GB was free of 16 GB during the runs, and each spawned worker holds 150–270 MB, so
  worker counts were kept low.

## 4. Validation

### (a) C kernel against the Python reference: PASS (Moby-Dick)

`logs/a_kernel_parity_moby.log`, 400 words, 841 dial pairs:

```
   (21,11)  python 1.0380  kernel 1.0380  diff 0.00000 <- planted
   (0,0)    0.5923         0.5923         -0.00000
   (7,19)   0.5812         0.5812          0.00000
   (28,3)   0.5898         0.5898          0.00000
largest disagreement 0.00000 nats/rune
planted dials (21, 11) score +1.0380, rank 1 of 841; runner-up +1.0380
largest score spread across the 29 OUTER dials: 0.000000
```

The tie with the runner-up is the free outer dial. Throughput 2,741 keys/s/core (841 pairs in 0.307 s).

### (b) community selftest

Sample 4000, Moby-Dick (`logs/b_selftest_sample4000_moby.log`): PASS.

```
COVERAGE: planted schedule IN the swept set
SENSITIVITY: planted key ranks 1 of 4001, score +1.0380 vs wrong mean +0.6420 (z = +20.3)
measured 2,999 keys/s/core (4,001 schedules x 29 dials in 38.7 s)
```

All schedules of the planted alphabet (`logs/b_selftest_all_moby.log`): FAIL by one place.

```
COVERAGE: planted schedule IN the swept set
SENSITIVITY: planted key ranks 2 of 105980, score +1.0380 vs wrong mean +0.6423 (z = +19.4)
measured 2,989 keys/s/core (105,980 schedules x 29 dials in 1028.3 s)
so the unbanded priority sweep is 361 core-hours
```

Not yet established: which schedule ranks first. Its score is not printed, and its score must be at least
+1.0380. The selftest prints only the planted rank, so identifying the top entry needs a rerun that prints
the top few.

The earlier run of this log was killed by mistake (I stopped the wrong pid) and then restarted. The
restart produced this result.

Projection. The sweep has 1,264 keyed alphabets (316 vocabulary words x 4 rules; 1,216 distinct), and
each alphabet has 105,980 schedules x 29 inner dials. That is 3.885e9 keys, which at 2,989 keys/s/core is
360 core-hours (the same calculation from the 2,999 keys/s/core on 4000 schedules gives 360). At nproc 12
that is about 30 h wall, if scaling holds. The brief's ~218 core-hours was not reproduced.

### (c) planted control, odometer + dodge family: FAIL

`our_plant.py` (`logs/c_our_plant_odometer.log`, `out/our_plant_result.json`):

- Planted: keyword MOBIUS, rule R2 reversed, schedule [25, 17, 14, 0, 2], start dials (7, 8), register =
  matched Moby-Dick over all 2,928 LP word lengths, cipher = `doublet_phase_test.encipher` ("advance").
- Scored on the first 400 words over all 105,980 schedules with `score_key` (the sweep's path, 3 workers,
  564 s).
- Result: planted rank **24,558** of 105,980; score +0.6494 vs rest mean +0.6417 (sd 0.0111); z = +0.70;
  best other +0.7009; recovered dial 24 (planted 7).

Diagnostics (`diag_*.py`, `logs/c_diag_*.log`). These are not validations and were not used to change the
sweep.

- Same plaintext, schedule and dial, true-dial scores:
  - MOBIUS R2 keyword alphabet: +0.587.
  - Random alphabet: +1.056.
  - MOBIUS R2 with the selftest schedule: +0.773 (random: +0.934).
- C kernel vs Python reference on the MOBIUS R2 alphabet: 0.58717 vs 0.58717 (diff 4e-7). K is a valid
  permutation and `fast_log_table` equals the reference. So the miss is not in the kernel or the table.
- Across 12 random vocabulary keywords vs 12 random alphabets (one plaintext, schedule and dial):
  keyword mean +1.016 (range +0.67 to +1.12), random mean +0.971 (range +0.60 to +1.10). The keyword
  alphabets are not systematically worse. The true-dial score varies widely with alphabet and draw. Some
  true keys sit at about +0.6 to +0.7, the same level as wrong keys (+0.64).

Interpretation (not proven): the first-400-word signal is draw-dependent. The selftest's one plant scored
well (z = +20), but this plant and some random-alphabet plants did not. The sweep's KEEP list may miss true
keys at this text length. Estimating the miss rate needs many plants and was not done.

Not covered by this control: `quagmire_dodge.encipher`. Its base steps by `alpha_k` composed with `sigma`
each word, a clock-dependent walk. That is a different variant from the odometer the sweep scores, so
this sweep does not test it.

### (d) held-out adjudication: validation PASS on the planted true key

`adjudicate.py`: the first 400 words are the sweep's data. The remaining 2,528 LP words give six full
400-word chunks (the 128-word tail is dropped). Each candidate is scored at its pinned inner dial
`(a0 + global start) mod 29`, outer 0. Null: 200 random keys (K from the sweep's vocabulary, schedule from
the generator, random dial), scored on the same chunks. A best-dial variant (best of 29 inner dials per
chunk) is also reported.

Validation on the planted true key (MOBIUS, schedule [25,17,14,0,2], dial 7) against
`out/planted_corpus.json` (`logs/d_adjudicate_validation_planted.log`):

```
null (200 keys): pinned chunk-mean mean +0.5855 sd 0.0117 max +0.6160
null best-dial:  mean +0.6358 sd 0.0052 max +0.6470
MOBIUS  pinned chunk-mean +0.8314 (z +21.0, margin over null max +0.2154)
        best-dial chunk-mean +0.8314 (z +37.6)
per-chunk pinned: [0.677, 1.020, 0.746, 0.911, 0.991, 0.644]
```

The held-out test separates the true key from 200 random keys, but the chunk values are uneven. The last
chunk (0.644) is barely above the null max (0.616), so the mean carries the result. Note
`planted_candidate.jsonl` uses the scorer's best dial (24), not the true start dial. Use
`planted_true_candidate.jsonl` (dial 7) for the validation.

### Smoke run (d in the brief): NOT RUN, stopped

The smoke run (`--nproc 4 --tasks 0,1`, `DODGE_PROGRESS=out/smoke_progress.jsonl`,
`DODGE_OUT=out/smoke_candidates.jsonl`) was started at 18:19 and stopped at 18:32, after the (c) failure,
with no task finished. Consequences:

- Per-task wall time was not measured. Estimate: about 5.3 keyed alphabets per task (1,264 / 240),
  about 90 min per task on one core at 2,989 keys/s.
- Resume was not tested in this run.
- `smoke_candidates.jsonl` does not exist, so adjudicate was not run on smoke output.

## 5. Commands

Environment (every run): `source agents/laneO_quagmire_dodge/env.sh` from the repo root.

Full resumable sweep (launch only after the failures are resolved):

```
source agents/laneO_quagmire_dodge/env.sh
export DODGE_PROGRESS=agents/laneO_quagmire_dodge/out/full_progress.jsonl
export DODGE_OUT=agents/laneO_quagmire_dodge/out/full_candidates.jsonl
nohup python -u dl/aldegonde_port/experiments/dodge_priority_sweep.py --nproc 12 \
  > agents/laneO_quagmire_dodge/logs/full_sweep.log 2>&1 &
```

Resumable: rerunning the same command skips every task already in `DODGE_PROGRESS`.

Adjudicate the full output (held-out test, real LP corpus):

```
source agents/laneO_quagmire_dodge/env.sh
python -u agents/laneO_quagmire_dodge/adjudicate.py \
  --candidates agents/laneO_quagmire_dodge/out/full_candidates.jsonl --corpus lp
```

Setup and re-check:

```
bash agents/laneO_quagmire_dodge/setup_port.sh           # fresh dl/aldegonde_port (dir must not exist)
cmd //c "agents\\laneO_quagmire_dodge\\build_kernel.bat" # DLL
```

## 6. Files

- `port.patch`, `setup_port.sh`, `build_kernel.bat`, `env.sh`, `our_plant.py`, `adjudicate.py`
- `audit/` (closure, reachability, import-time and I/O audits, clone manifest)
- `logs/` (every run above), `out/` (planted corpus, planted candidates, plant and adjudication JSON)
- `diag_plant.py`, `diag_kernel_keyword.py`, `diag_keyword_pattern.py` (diagnostics)

## 7. Orchestrator verification (round two)

Everything here was run by the orchestrator after the lane handed back. Scripts: `diag_alphabet_kind.py`
(this directory; env vars `DIAG_WRONG`, `DIAG_SEED0/1`, `DIAG_KINDS`, `DIAG_OUT`), outputs in `out/diag_*.jsonl`.

**Is the scorer blind to keyword alphabets?** No. Each run plants an odometer + dodge key
(`doublet_phase_test.encipher`, `"advance"`, the selftest's call) on a Moby-Dick register matched to the
LP's first 400 word lengths, then scores the planted schedule and N random wrong one-zero schedules under
the planted alphabet with the sweep's own `score_key` (29 inner dials each).

| plants | wrong schedules each | rank 1 | median z | lowest recovered true score |
|---|---|---|---|---|
| 10 random alphabets (the selftest's kind) | 4,000 | 10/10 | +28.2 | +0.786 |
| 10 keyword alphabets (the sweep's kind) | 4,000 | 10/10 | +29.5 | +0.877 |
| 100 keyword alphabets, seeds 100-199 | 2,000 | **95/100** | +23.7 | +0.696 |

The inner dial was recovered exactly in every rank-1 case. The five misses (NEED/R4 rank 25, INNOCENCE/R1
rank 724, THE/R2 rank 98, INDIVIDUALS/R3 rank 1953, IRRITATED/R3 rank 834) score at wrong-key level
(z -1.9 to +2.5): the scorer does not see those keys at all on that text. Cause not diagnosed.

**Lane O's failing plant (section 4c) is one of these misses, not a bug.** Replaying the same key
(MOBIUS R2 reversed, schedule [25, 17, 14, 0, 2], dials (7, 8)) against 2,000 wrong schedules:

| ciphertext | rank | z | dial |
|---|---|---|---|
| fresh 400-word register, same key | 1 / 2,001 | +10.2 | 7 (correct) |
| fresh 2,928-word register, same key, first 400 words | 1 / 2,001 | +16.3 | 7 (correct) |
| lane O's saved corpus (regenerated byte-identical from seed 7301) | 462 / 2,001 | +0.7 | 24 |

So whether a true key is seen depends on the plaintext draw, at roughly a 5% miss rate.

**Selftest rank 2 at `--sample 0`.** A different schedule of the *planted alphabet* outscored the plant
(+1.038). Schedules near the truth share phases and partly decrypt; the sweep keeps 5 per task (1,200 in
the progress file), so a true key beaten by its own neighbour is still in the adjudication set.

**Power statement for the full run.** Per true key in the searched space, about 95% are seen at all by the
first-400-word scorer; a seen key scores +0.70 to +1.13 against a local wrong-key mean of +0.64 (sd ~0.013).
Whether it also clears the global maximum over 3.9e9 wrong keys is measured by the run itself: the top
scores in the progress file are the null, since the real LP is the corpus. Adjudicate all 1,200 retained
candidates with `adjudicate.py` (held-out chunks), not just the global top.

**Launch.** A first attempt through `cmd //c start /BELOWNORMAL` started nothing and wrote an empty log
(the `start` wrapper did not run the interpreter); it was stopped. `launch_sweep.ps1` replaces it: it starts
the real interpreter with `Start-Process`, redirects output to `logs/<tag>_sweep.log`, and sets the parent
to BelowNormal before the pool exists, so workers inherit it (verified: parent and worker both priority 6).
Memory: about 265 MB for the parent and 280 MB per worker.

The full run was **not** started: the owner's own SDXL job held 7.5 GB of the machine's 15.9 GB (2.6 GB
free), and 8 to 12 workers need 2.5 to 3.5 GB. Recommended: `-NProc 12` when the machine is free
(~30 h at the measured ~3,000 keys/s/core), or `-NProc 4` alongside other work (~90 h).

```
powershell -ExecutionPolicy Bypass -File agents\laneO_quagmire_dodge\launch_sweep.ps1 -NProc 12
```

### 7b. Smoke run and power (orchestrator, 2026-10-16)

`launch_sweep.ps1 -NProc 1 -Tasks 0 -Tag smoke1`: task 0 (1/240 of the 1,264 alphabets) scored **18,440,520 keys in
95.6 min** on one BelowNormal worker (3,214 keys/s), wrote `out/smoke1_progress.jsonl` and `out/smoke1_candidates.jsonl`,
and a rerun of the same command printed `resuming: 1 tasks already` and finished in 0.0 min. Full sweep: 240 tasks x
95.6 min = ~382 core-hours, ~32 h at `-NProc 12`.

That task is also the first slice of the real null: its best score on LP2 is **+0.7002** (R1 gematria alphabet, schedule
[23, 24, 4, 0, 7], dial 10), its top five within 0.003 of each other, which is what noise looks like. Of the 100 planted
keyword keys in `out/diag_miss_rate_keyword100.jsonl`, 94 score above 0.70, 92 above 0.72, 89 above 0.75 and 88 above
0.80. If the full-sweep maximum on LP2 lands near 0.75 (the max of 240 such slices), the run has about **89% power** for
a key of this family built from Cicada's vocabulary. The adjudicator then separates any survivor on held-out text.

## 8. Tiered runs (orchestrator, 2026-10-16)

The full sweep is ~382 core-hours, and this PC has 8 physical cores (i7-11700F, 16 threads), so 12-16 workers do not
scale linearly: expect 35-45 h wall for everything. Compiler flags do not rescue it: `/O2 /Oi /fp:fast /arch:AVX2`
gives 3,858 keys/s/core against 3,632 for `/O2` (`build_kernel_fast.bat`; parity with the Python reference holds), +6%.
The kernel's inner loops do not vectorise as written.

So the run is ordered by prior instead. The port now takes `DODGE_WORDS`, `DODGE_EXCLUDE_WORDS` and `DODGE_EXTRA_WORDS`
(patch regenerated; a fresh `setup_port.sh` rebuild is identical to the working port), candidate names carry their word
(`WORD/rule`), and `FIRFUMFERENFE`, one of the two keys Cicada actually used on the solved pages, is added: it was
missing from the upstream vocabulary. `launch_sweep.ps1 -Tier A|B|C` picks the word set, each with its own progress file.

| tier | words | alphabets | core-hours | wall at ~10 effective workers |
|---|---|---|---|---|
| A | DIVINITY, FIRFUMFERENFE, CIRCUMFERENCE, PRIMES, PRIME, TOTIENT, INSTAR, PARABLE, KOAN, CICADA, LIBER, PRIMUS, WISDOM, PILGRIM | 56 | ~15 | ~1.5 h |
| B | the other named puzzle terms (33 words: WITHIN, TUNNELING, EMERGE, MOBIUS, SHADOW, INSTRUCTION, ...) | 132 | ~35 | ~3.5 h |
| C | the remaining register words | 1,080 | ~287 | ~29 h (resumable; overnight chunks) |

```
powershell -ExecutionPolicy Bypass -File agents\laneO_quagmire_dodge\launch_sweep.ps1 -Tier A -NProc 10
```

## 9. Tier A result (orchestrator, run 2026-10-16 21:47 to 2026-10-17 00:45)

**Verdict: NULL for tier A.** `launch_sweep.ps1 -Tier A -NProc 10`: 56 keyed alphabets from 14 words (DIVINITY,
FIRFUMFERENFE, CIRCUMFERENCE, PRIMES, PRIME, TOTIENT, INSTAR, PARABLE, KOAN, CICADA, LIBER, PRIMUS, WISDOM, PILGRIM) x
105,980 one-zero schedules x 29 dials = **172,111,520 keys in 177.1 min**, every one scored. Logs:
`logs/tierA_sweep.log`, progress `out/tierA_progress.jsonl`, top 40 `out/tierA_candidates.jsonl`.

- First-400-word scores: best **+0.7059** (WISDOM/R3 cyclic, schedule [1, 0, 28, 11, 18], dial 19; its rotation and a
  WISDOM/R4 key tie it). The single random-slice smoke task reached +0.7002, and 89 of 100 planted keyword keys score
  above 0.75. Nothing in tier A stands out of the noise on the text it was fitted to.
- Held-out test (`adjudicate.py` on all 280 retained candidates, `progress_to_candidates.py`; log
  `logs/adjudicate_tierA_lp.log`, output `out/adjudicate_tierA_lp.json`): six held-out chunks of 400 words, null of
  200 random keys (pinned chunk-mean +0.5860 +- 0.0122, max +0.6218; best-dial +0.6359 +- 0.0049, max +0.6503).
  - Pinned dial: **0 of 280 above the null max**; max z +2.90 (KOAN/R4, margin -0.0009); the 280 z-scores have mean +0.11
    and sd 0.86, which is the noise expectation (the maximum of 280 standard normals is about +2.9).
  - Best dial: 1 of 280 above the null max by +0.0005 (PARABLE/R3 cyclic, z +3.0; pinned z +1.7, first-400 score 0.690,
    not a top scorer). One exceedance of a 200-draw null max in 280 draws is expected.
  - For scale: lane O's planted true key held out at z +21.
- Power: about 89% for a key of this family built from these 14 words (section 7b), so tier A excludes the Cicada-keyword
  Quagmire-odometer-dodge with those words at roughly that power.

**Throughput correction.** 172.1M keys in 177.1 min is 16,197 keys/s: ten BelowNormal workers on this 8-core/16-thread
machine delivered about 5.0x one worker (3,214 keys/s), not 10x. Revised estimates at -NProc 10: tier B (132 alphabets)
~7 h; tier C (1,080 alphabets) ~57 h, in resumable chunks.

## 10. Tier B result (orchestrator, run 2026-10-17 00:55 to 15:19)

**Verdict: NULL for tier B.** `launch_sweep.ps1 -Tier B -NProc 10`: 132 keyed alphabets from the other 33 named puzzle
terms x 105,980 schedules x 29 dials = **405,691,440 keys in 404.1 min** of run time. The PC idle-slept for most of
the first night (CHANGELOG 2026-10-17); from 10:04 `stay_awake.py` held it awake until the sweep exited (5.3 h).

- Best on the scored 400 words: **+0.7202** (SACRED/R1 gematria, schedule [15, 0, 5, 22, 16], dial 2); next EMERGE
  +0.7105, ADHERENCE +0.7095. Below the +0.75 that 89 of 100 planted keys beat.
- Held-out test on all **655** retained candidates (`logs/adjudicate_tierB_lp.log`, `out/adjudicate_tierB_lp.json`;
  same null as tier A): pinned dial **0 of 655 above the null max**, max z +2.60 (STUDENT/R1), z mean +0.06, sd 0.94;
  best dial 1 of 655 above the null max (INSTRUCTION/R3, z +3.3, pinned z +0.8), within the expected maximum of 655 draws.

Tiers A and B together: 188 alphabets from 47 words, 577.8M keys, both null at ~89% power. Tier C (the 1,080
register-word alphabets, ~57 h) remains.
