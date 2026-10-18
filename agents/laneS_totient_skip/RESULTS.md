# Lane S: totient skip45 nolitF, exhaustive key sweep on LP2 (2026-10-16)

**Verdict: NULL.** Neither convention's real best clears its null max (forward -6.74446 vs null max -6.68295, z +0.35; reverse -6.80664 vs null max -6.70989, z -0.63), and the family fails the doublet-residue rule (gate C2c, see the banner in the gate report).

- Gate: jobs/hypothesis-gate/runs/2026-10-16-totient_fskip.md (family variant totient_fskip_skip45_nolitF; the gate banner records GATE FAIL: C2c, EXCLUDED by C2c, found by this lane)

## Hypothesis
The gate's PROCEED family: p = c - (prime_k - 1) mod 29 (simulator convention, sign +1), key start k0 in 0..9999 (index into the primes, prime_0 = 2), k advancing once per enciphered rune, plus a collision skip at positions with i mod 5 != phase (key advances twice on a skip; the literal F rule is absent). The sweep covers all 50,000 keys (10,000 start indices x 5 skip phases), so 100% of the key space, in both conventions: sign +1 (simulator, c = p + PHI) and sign -1 (reverse, c = p - PHI). The cipher is the simulator's logic with k0, phase and sign as parameters; it reproduces the simulator's encrypt exactly for phase 0 (60/60 random plaintexts, `lane_s.py selftest`).

Decoder: an exact dynamic program over (position, k), with the skip ambiguity handled as two branches (no skip, skip) and states with equal k merged (they share their future). No beam cap: a cap of 8 was removed because a cap can drop the true path.

Screen window: the first 300 runes of the LP2 stream. Page 0 has 262 runes, so the window is page 0 plus 38 runes of page 1 (the brief said 300 runes of page 0; this is the only deviation).

Two screens per key:
- STRICT: the model as simulated. A key is consistent with the window only if every doublet in the window lies on the forbidden residue or its prime gap is 0 mod 29. Score: quadgram mean (toolbox/score.py) of the best consistent path.
- RELAXED (the z-score screen): the same dynamic program with the doublet rule dropped; the skip branch is still allowed at non-forbidden positions. This is not the plain no-skip keystream, which was not swept separately. Every key gets a score, so real and null are ranked over the same 50,000 keys.

What is new against the ledgers: the first complete sweep of the 10,000 start indices with all five skip phases for this variant (the earlier dukotah P1 run covered 2,876 decodes at 100-spaced starts with phase 0; `dl/.../campaign18` covered start 0 only). The doublet residue check (below) is new.

## Control
Plants: 20 forward (seed 20261016) and 5 reverse (seed 20261017) English plaintexts of 300 runes from `toolbox/runes.english_stream` (a different Moby-Dick passage per plant), enciphered at random k0 (0..9399) and random phase with the same cipher code. Each plant is searched over the full 50,000-key sweep of its own convention.

Recovered 19/20 forward plants at rank 1 (relaxed screen); reverse 5/5 at rank 1. Strict screen: the true key is consistent with its window in 20/20 forward and 5/5 reverse plants. Miss: plant 16 (k0 3792, phase 0) ranks 3, behind k0 3791 (same phase), which realigns with the true key sequence after two runes. Only those two runes differ, which is an identifiability limit of the model, not a search failure. Decoding the true key returns the exact plaintext in 20/20 forward and 5/5 reverse relaxed decodes. Numbers: `out/control.json`, `logs/control_stdout.txt`, `logs/lane_s_run.log`.

## Null
20 shuffles per convention (`toolbox/nulls.shuffle_increments` within pages; seeds 1000-1019 forward, 1500-1519 reverse), first 300 runes of each shuffled stream, same 50,000-key relaxed sweep, best score per shuffle.

- Sign +1: mean -6.75653, sd 0.03423, max -6.68295 (min -6.80938; n = 20).
- Sign -1: mean -6.78105, sd 0.04040, max -6.70989 (min -6.84337; n = 20).

Strict consistency counts in the nulls: 0-63 keys for most shuffles; 2 of 20 forward and 4 of 20 reverse shuffles kept 10,000 (one phase class). Output: `out/null_sign+1.json`, `out/null_sign-1.json`.

## Real result
Real window: doublets at window positions 122 and 207, both on residue 2 mod 5. Strict consistency: 10,000 keys for phase 2 in both conventions (the doublet rule is satisfied by one phase class only).

- Sign +1: relaxed best -6.74446 at phase 0, k0 9378. z = +0.35 against the null; real is below the null max -6.68295.
- Sign -1: relaxed best -6.80664 at phase 1, k0 8223. z = -0.63 against the null; real is below the null max -6.70989.

Top 50 per convention, decoded over the whole 12,956-rune stream under the relaxed rule: best full-stream quadgram -7.2416 (sign +1, phase 3, k0 5504; median -7.2736) and -7.2438 (sign -1, phase 4, k0 7261; median -7.2695). No top-50 key stays consistent with the strict rule to the end of the stream (0/50 in each convention). These are noise-level quadgram scores (English is about -4.1 to -5.0). Output: `out/real_relaxed_sign+1.npy`, `out/real_strict_sign+1.npy`, `out/real.json`, `out/top50_sign+1.json`, `out/top50_sign-1.json`, `out/report.json`.

Structural check (not from the sweep): the simulator places all doublets on the forbidden residue (249/249 over 3 x 12,956 English runes). LP2's 86 doublets fall on residues 0-4 as 18, 21, 16, 11, 20. A constant-phase skip rule cannot produce that across the book. This is the reason the family is excluded by C2c in the gate report.

## Verdict
NULL. No key in either convention beats its null max, and the top-50 full-stream decodes read as noise. The family is excluded by C2c (gate banner); the sweep finds no key that decodes LP2's window as English. Reading this result: the relaxed screen covers the plain prime-totient keystream with optional skips at every start index and phase, with the doublet rule dropped.

## Files
- `lane_s.py`: decoder, encryptor, sweep and drivers (`selftest`, `throughput`, `control`, `null --sign`, `real`, `report`).
- `logs/lane_s_run.log`: all run lines (timings, priority, every stage's numbers).
- `logs/control_stdout.txt`, `logs/null_fwd_stdout.txt`, `logs/null_rev_stdout.txt`, `logs/real_stdout.txt`, `logs/report_stdout.txt`: stage stdout.
- `logs/control_strict_only_superseded_stdout.txt`: an earlier control run with the strict screen only (19/20 forward, 5/5 reverse); superseded by the relaxed screen.
- `out/`: `.npy` score tables, `.json` summaries (git-ignored for `.npy`/`.bin`).
- Priority: wmic setpriority failed (exit 1); the process set BELOW_NORMAL through ctypes (0x4000), and the workers inherited it.
