# Lane V: is the within-word lag-5 echo localised, and which mechanism does it favour? (2026-10-17)

**Verdict: NULL.** The echo is not localised: the best burst window (pages 50-50) has Z = 2.89 against a null mean of 2.99 (permutation p = 0.51), and planted localised echoes of the same size are found 50/50. Under the mechanism decibans, walk and quagmire beat the no-echo baseline on the lag-5 cell (+22.8 and +21.1 dB), but the full-profile ranking is unstable (totient first under the per-cell beta-binomial, walk first under the pooled-covariance Gaussian, quagmire first on lags 1-5), so no mechanism is selected.

- Gate: none. Both questions are statistical tests of the C5 echo (toolbox/CONSTRAINTS.md), not a key model. The mechanism simulators are the hypothesis gate's own (see Hypothesis); no key is searched, so no oracle step applies.

## Hypothesis
**Q1 (burst scan, TECHNIQUES B3).** The echo sits in a run of consecutive pages rather than uniformly. LP2 has 2105 within-word lag-5 pairs and 104 coincidences (rate 0.0494); the flat-rate expectation is 72.6, so the echo's excess is 31.4 (rounded to 31 for the plants). Scan statistic T = max over 514 windows of the standardised excess Z_w = (O_w - E_w)/sqrt(V_w): 505 runs of 1-10 consecutive pages and lane J's nine page-group sections (agents/laneJ_lag5_echo/core.py). Expectation and variance are hypergeometric under permutation of the coincidence labels within the nine word-length strata (lengths 6-14), so the stratum totals are kept, as in lp/t7_lag5_lines.py. Raw excess is logged but dominated by the largest windows, so the standardised form is the statistic. This differs from B3's text (word-length shuffles within sections, counting flagged windows): the brief's stratum-label protocol was used instead. New vs lane J, which had no sequential scan.

**Q2 (mechanism decibans, TECHNIQUES B1).** Five models, each simulated on the gate's English runes (toolbox/runes.py source, Moby-Dick) laid out in LP2's exact word-length sequence, since the within/cross split depends on word lengths. Each replicate uses a different English passage (60 disjoint passages of 13,000 runes, so plaintext variation enters the spread). Mechanisms: walk (jobs/hypothesis-gate/runs/walk_dodge_random_cipher.py), quagmire (quagmire_odometer_dodge_cipher.py, lane O's family), dynsub5 (dynsub_skip5_cipher.py), totient (totient_fskip_skip45_nolitF_cipher.py); baseline = no-echo dodge (jobs/hypothesis-gate/data/fixture/otp_dodge5.py). Key spaces (log10 sizes, out/mech_sim_out.txt): walk 85.9 (sigma and base0 in S29, g an order-5 permutation with 4 fixed points: C(29,4) x 25!/(5^5 5!)); dynsub5 61.9 ((29!)^2); quagmire at least 30.9 (the keyed alphabet 29!, plus the schedule and dials, not counted); totient 4.0 (k0 in range(10000)); baseline not enumerable. Coverage: 40 training keys per model and 20 held-out keys, a Monte Carlo sample (for totient, 60/10,000 = 0.6%; elsewhere effectively 0%). Simulation stage: two workers, median 0.02 s per stream (out/mech_sim_timing.txt; the first quagmire call in each worker takes 4.7 s because it imports the community port).

Likelihood (primary): per-cell beta-binomial, because the high-lag cells hold only 35-201 pairs and a Gaussian approximation is poor there. For each mechanism and cell, the 40 keys give a mean mu and a variance v; the rate is Beta(mu, tau^2) with tau^2 = (v - mu(1-mu)/n)/(1-1/n), so the predictive count is BetaBin(n, a, b), which carries the key-to-key spread. LP2's log-likelihood is summed over the 20 cells. Deciban weight against the baseline = 10 log10 e^(lnL_M - lnL_base) = 4.3429 (lnL_M - lnL_base). Cells are treated as independent, so totals overcount if cells are correlated. Sensitivity: multivariate normal on the 20 rates with covariance pooled within mechanisms; weight = -2.1715 (d2_M - d2_base).

## Control
Q1 plants, threshold per plant = p < 0.05 from 499 within-stratum permutations of that plant's own labels (same test as the real data). Localised, same total size (31 extra coincidences in one random 5-page block of a no-echo base): recovered 50/50 (flagged, and the argmax window overlaps the block). Half size (15): recovered 44/50. Diffuse, same total size spread uniformly over non-matching pairs: flagged 1/50. No-echo bases: flagged 8/200 = 4.0% (nominal 5%).

Q2 ranking control: 20 held-out ciphertexts per mechanism (never fitted, distinct passages), each ranked against the five fitted models. The true mechanism should be rank 1: walk 15/20, quagmire 19/20, dynsub5 19/20, totient 15/20, baseline 17/20; recovered 85/100 at rank 1 under the beta-binomial (63/100 under the Gaussian). Log: out/mech_rank_out.txt.

## Null
Q1: 2000 shuffles (coincidence labels permuted within the nine word-length strata, totals kept): best window Z mean 2.995, sd 0.621, max 7.809; 95th percentile 4.154, 99th 4.915 (out/burst_scan_out.txt, out/burst_null_T.npy).

Q2: 20 baseline held-out streams give the null of each deciban weight (mean, sd, max): walk -70.3, 23.0, -11.5; quagmire -79.4, 25.7, -11.2; dynsub5 -9.5, 7.3, +3.2; totient -14.4, 10.8, +1.8. LP2's weights (table below) are compared with these; walk, quagmire and totient exceed the baseline null maximum, dynsub5 does not.

## Real result
**Q1.** Best window pages 50-50: Z = 2.885 (3 coincidences observed in 15 pairs, 0.69 expected). Against the null, z = -0.18 (null mean 2.995, sd 0.621, null max 7.809); permutation p = 0.514; the real best is below the null max. The largest raw excess is pages 9-18 (+9.07 coincidences, Z 2.47), inside lane J's section 2 (pages 8-14, Z +1.14). Section Z values run from -1.39 (pages 3-7) to +1.14. No window is extreme: the echo is consistent with diffuse.

**Q2 deciban table** (LP2 against the no-echo baseline; positive favours the mechanism; full 20 cells, then lags 1-5 and within-word lags 1-10 only; out/mech_rank_out.txt):

| mechanism | dB beta-binomial (20 cells) | dB Gaussian (20 cells) | beta-binomial (lags 1-5) | Gaussian (lags 1-5) | beta-binomial (within 1-10) | Gaussian (within 1-10) |
| --- | --- | --- | --- | --- | --- | --- |
| walk | +3.22 | +16.34 | +7.7 | +23.3 | +14.5 | +22.9 |
| quagmire | -3.31 | +8.43 | +18.1 | +25.2 | +9.1 | +11.9 |
| dynsub5 | +2.38 | +1.33 | +3.7 | +1.4 | +7.4 | +3.9 |
| totient | +4.64 | +3.89 | +0.1 | -2.9 | +6.5 | +3.7 |
| baseline | 0 | 0 | 0 | 0 | 0 | 0 |

Rankings (20 cells): beta-binomial totient > walk > dynsub5 > baseline > quagmire; Gaussian walk > quagmire > totient > dynsub5 > baseline.

Per-cell contributions (beta-binomial, against baseline): within lag 5 walk +22.77, quagmire +21.10, totient +1.88, dynsub5 -0.05. Cross-word lag 1 walk -7.92, quagmire -3.10, totient -3.75, dynsub5 -1.54. Predicted cross-word lag-1 rate: walk 0.0042, quagmire 0.0063, dynsub5 0.0066, totient 0.0059, baseline 0.0077; LP2 0.0079 (23 of 2895). So walk and quagmire match the echo cell but predict fewer cross-word doublets than LP2 has; the baseline predicts it.

## Verdict
**NULL.** The echo is not localised (Q1: best window Z = 2.89, z = -0.18 against the null, p = 0.51; localised plants of the same size recovered 50/50, diffuse ones flagged 1/50). Mechanism ranking (Q2): the two period-5 families (walk, quagmire) carry the echo, +21 to +23 dB on lag 5, but no single ranking is stable across cell sets and approximations, so no mechanism is selected. No key was recovered, so the community oracle does not apply.

## Files
- agents/laneV_lag5_mechanisms/common.py (LP2 loader, English runes laid out as LP2, priority helper)
- agents/laneV_lag5_mechanisms/burst_scan.py -> out/burst_scan_out.txt, out/burst_null_T.npy (git-ignored)
- agents/laneV_lag5_mechanisms/mech_sim.py -> out/mech_profiles.npz (40 training + 20 held-out keys per model), out/mech_sim_timing.txt
- agents/laneV_lag5_mechanisms/mech_rank.py -> out/mech_rank_out.txt
- Note: the quagmire simulator imports scipy from this machine's user site-packages; mech_sim.py and mech_rank.py append that directory to sys.path after the -I isolation flag, and the run is otherwise isolated.
