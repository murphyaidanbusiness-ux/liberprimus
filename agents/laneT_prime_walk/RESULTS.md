# Lane T: prime-seeded doublet-dodge walk, all 20,000 keys (2026-10-16)

**Verdict: NULL.** Over the full 20,000-key space no key gives an English decode of LP2: the best 300-rune key sits at z = -1.56 and below the null max (-6.870 against -6.667), the 50 best keys all die before the end of LP2, and the one key that survives all 12,956 runes decodes to noise (mean -7.31). The planted control recovers 20/20 keys at rank 1.

- Gate: jobs/hypothesis-gate/runs/2026-10-16-walk_dodge_prime.md (GATE FAIL C1 C2 C6 on the gate's three seeds; the census of all 20,000 keys finds 1,550 that pass every hard constraint, re-counted by this lane as C1 9332, C2 8159, C2b 19476, C3 18331, C6 6082, all 1550, matching the gate census exactly). The orchestrator asked for this lane as an exhaustive decode of the whole key space, not on a PROCEED, so the verdict covers all 20,000 keys and not only the 1,550.

## Hypothesis
The cipher is the gate simulator `jobs/hypothesis-gate/runs/walk_dodge_prime_cipher.py`, inverted exactly. It is a doublet-dodge walk over 29 runes: the clock starts at 0 and advances per rune; a rune whose ciphertext equals the previous ciphertext is re-enciphered one clock step later (a dodge); after each word the base permutation is composed with g^(clock-1) and sigma. The key is (stream in {phi, prime}, k0 in 0..9999): g is an order-5 permutation built from the first 25 runes of ordering(k0), sigma = ordering(k0+1000), base0 = ordering(k0+2000), each read from the prime/totient ladder.

- Key space: 20,000 keys (10,000 offsets x 2 streams). All 20,000 were searched in the 300-rune screen, the 20 control plants, the 20 nulls and the full-length scan (100% coverage).
- Decoder (new in this lane, `tdec.py`, numba): an exact inverse of the walk. For an observed rune c with clock e (mod 5) and inverse base Binv, branch A (no dodge; valid unless c equals the previous rune) gives p = g^(-e)(Binv[c]); branch B (dodge; valid only if the forced check holds) gives p = g^(-e)(Binv[prev]). A beam of W = 512 states (clock mod 5, inverse base, cumulative quadgram score from `toolbox/score.py`, tail of three letters) keeps the best paths; the base update at each word end is applied per state. The inverse is checked in `logs/checks.txt`: 40 of 40 decoded paths re-encrypt to the cipher, and the decoder never scores below the true path (0 of 40).
- Ranking: a key is ranked by (runes decoded before every state dies, then mean quadgram log10 score). A key that dies early is inconsistent with the cipher and ranks below every full-window key.
- New vs lanes A-R and the ledgers: this family was never decoded. `jobs/hypothesis-gate/runs/2026-10-16-walk_dodge_prime.md` records the survey entry T ("prime-seeded selectors were not run") and that the ladder was tested only as an additive keystream and as a seed generator. Lane L's decoder is not reused.

## Control
Plants: 20 English plaintexts of 300 runes from `toolbox/runes.english_stream` (each from a different passage), enciphered with the simulator's `walk` under one key each: 10 drawn from the 1,550 passing keys and 10 from the other 18,450. Every plant was screened over all 20,000 keys.

Recovered 20/20 plants at rank 1 over all 20,000 keys (`out/control.json`). The true-key mean ranged from -4.14 to -4.95, and the best wrong key in every plant scored at most -6.66, and the smallest true-minus-wrong margin over the 20 plants is 1.81 log10 units. The true key's decode reproduced the planted plaintext exactly in 18 of 20 plants; in the other two (plants 12 and 18) the key still ranks first, because the walk admits alternative plaintexts with the same cipher and the beam keeps one of them. The criterion is key recovery, not plaintext recovery.

Full-length power check (`out/long_plant_check.json`): 8 independent plants of 12,956 runes (4 at W = 512, 4 at W = 4096, different keys) all survive the full length under their true key (12,956 of 12,956 runes) with English-level means between -4.45 and -4.46. The planted text is exact in only 1 of the 8, for the same alternative-path reason.

## Null
20 shuffles (`toolbox/nulls.shuffle_increments` on LP2 pages 0-54, seeds 7000 to 7019; the first 300 runes of each shuffled stream), each screened with the same pipeline over all 20,000 keys at W = 512 (`out/null.json`). Best score (mean of the top-ranked key): mean -6.7953, sd 0.0483, max -6.6669 (min -6.8901). Each null window had 2 or 3 doublets, as the LP2 window does (2, at positions 122 and 207; `logs/checks.txt`).

## Real result
LP2 first 300 runes, screened over all 20,000 keys: the best key is prime k0 = 1143 (index 11143), alive 300 of 300, mean -6.8704. Against the null, z = -1.56 (mean -6.7953, sd 0.0483); the null max is -6.6669, so the real best sits 0.203 below it and exceeds only one of the 20 null bests (`out/summary.json`). 14,549 keys survive the 300-rune window. At W = 4096 the same key is still best with the same mean, -6.8704 (`out/real_wide_W4096.json`), so the verdict does not depend on the beam width.

Full length: the top 50 keys by the screen all die before the end of LP2, at positions 932 to 5,836 (`out/real_top50.json`). Over all 20,000 keys, decoded over the whole 12,956 runes at W = 512 (`out/fulllp.json`), exactly one key survives: prime k0 = 9144 (index 19144), mean -7.308, IoC 1.012 against 0.9998 for random runes (quadgram -7.505). That decode is noise, not English, and at W = 4096 the same key dies at position 4,774, so its survival is a beam artifact. No key decodes all of LP2 to English.

Throughput (BelowNormal, 8 workers, 16 cores shared with the owner's work): census 306 s; control about 4 min; 20 nulls 41 s; real screen 8 s; full-length scan 110 s; W = 4096 screen 7 s. The key tables are held as int32 in each worker (the `out/tables.npz` cache is 111 MB on disk).

## Verdict
NULL. The walk_dodge_prime family, over all 20,000 keys, does not decrypt LP2 at beam width 512, and the 300-rune result is unchanged at W = 4096. The control recovers 20/20 keys at rank 1; the real best is inside the null range (z = -1.56, below the null max); and no key decodes LP2 to English over its full length (the one full-length survivor is noise, -7.31). This is a beam-limited exclusion of the full key space, not a solve. Nothing was sent to the oracle (`verify_solution.py`) because no decode reads as English.

## Files
- `agents/laneT_prime_walk/tdec.py`: exact inverse of the walk (numba beam), key and quadgram tables (`out/tables.npz`, 111 MB, git-ignored).
- `agents/laneT_prime_walk/lane_t.py`: subcommands census, control, null, real, fulllp, report.
- `agents/laneT_prime_walk/screen_wide.py` (W = 4096 robustness), `long_plant_check.py` (full-length plants), `checks.py` (inverse self-test, survivor decode, window doublets).
- `agents/laneT_prime_walk/out/`: census.json (the 1,550 passing keys), control.json, null.json, summary.json, real_alive.npy and real_mean.npy (all 20,000 scores), real_top50.json, fulllp.json, fulllp_alive.npy, long_plant_check.json, real_wide_W4096.json.
- `agents/laneT_prime_walk/logs/`: lane_t_run.log (all runs), checks.txt, and the stdout captures.
