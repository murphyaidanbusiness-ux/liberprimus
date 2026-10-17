# Lane U: period-13 delta match on the 308-rune section "54-55" (2026-10-17)

**Verdict: INCONCLUSIVE (power).** The fixed rule does not flag period 13 (M13 = 18, threshold 19), but the rule flags only 18 of 50 planted period-13 keywords at this length (power 0.36), so the community peak is neither reproduced nor excluded.

- Gate: none. This re-tests a community claim (catalogue entry B4), not a cipher-family key model, so the hypothesis gate does not apply; the lane predates it.

## Hypothesis
**Claim** (research/scout1_community.md sections 5.4 and 6 item 3; jobs/technique-survey/runs/2026-10-16-agency-classical.md): a period-13 peak in the increments D_i = (c_i - c_(i-1)) mod 29 of one late 308-rune section, reported as S1(13) = 1.72, p about 0.016, after interrupter tuning, and not replicated elsewhere.

**Section mapping (lp/lpdata.py page ids).** The claim's "54-55" is the wiki's label "Hollow 54-55, 308 runes, 3 doublets". In lpdata ids it is pages 53 and 54 (232 + 76 = 308 runes). Evidence:
1. Rune count: lpdata pages 53 and 54 sum to 308. Pages 54 and 55 sum to 161, so the label is not 54 plus 55 in lpdata ids.
2. Wiki labels: the wiki rows match lpdata page ids exactly for pages 0 to 39. Its "Spiral/Branches 40-53" (3,008 runes) equals lpdata pages 40 to 52, so the wiki's last labels run one ahead of lpdata.
3. Content: lpdata page 53 begins with a 1-rune word then an 8-rune word (the "1 rune + 8 runes" header the community describes), and page 54 contains the 13-rune word.
4. Doublets: the section has 3 doublets, as the wiki row says. The whole 0-54 pin has 86 doublets, as the wiki total says. All of these checks are logged in period13_log.txt (mapping line).

The 0-54 pin (SHA-256 023312...) holds. Pages 55 (85 runes) and 56 (95 runes) are not in the claim. This mapping is mine; the community's own page ids are not in the repo.

**Statistic (fixed before the run).** For the 307 increments D_j of the section (zero increments kept, no interrupter removed), M_k = #{j : D_j = D_(j+k)}. Scan periods k = 2..40. The community's S1 normalisation is not in the repo, so S1 is not reproduced exactly. The S-style ratio reported here is M13 divided by its null mean.

**Fixed rule.** Flag period 13 iff M13 > T13, where T13 is the 99th percentile of M13 over 10000 null draws (numpy quantile, method "higher"). Null: the 307 increments shuffled within the section, which keeps the zero-increment count.

**Key space.** No key search. The look-elsewhere family is the 39 periods 2 to 40, all covered.

**What is new.** Lane D s8 ran periods 2 to 60 on page-level difference streams, not this section under a fixed threshold. Leo's per-section lag-kappa (research/scout6_delta.md, 2026-09-07 addendum) found best-lag z 2.5 to 3.8 against 3.1 plus or minus 0.5 in real sections.

## Control
Plants: 50. Each plant uses English plaintext runes p_i from `toolbox/runes.english_stream(308, skip_chars=20000+5000*j)`, j = 0 to 49 (50 different passages of the Moby Dick text in the toolbox). It is enciphered as the chain c_i = c_(i-1) + 1 + ((p_i + k_(i mod 13)) mod 28), mod 29, with a keyword k of 13 values drawn uniformly from 0 to 27 per plant. Length is 308, as in the real section. The statistic ignores word boundaries, so the section's word lengths are carried but have no effect on the result.

Deviation: the chain formula cannot produce a zero increment. Plants have 0 zero increments and the real section has 3. The null and the threshold come from the real section, as the fixed rule requires.

recovered 18/50 (flagged by the fixed rule, M13 > 19). Plant M13: mean 18.5, sd 4.568, min 10, max 32. Rank 1 among periods 2 to 40 (exact period 13): 18/50. Top period a multiple of 13: 40/50 (13 in 18, 26 in 12, 39 in 10, other 10).

Power at n = 308: 0.36 (Wilson 95% interval 0.24 to 0.50). The control misses the 80% requirement, so the real test is underpowered.

## Null
10000 shuffles of the 307 increments within the section (numpy permutation, zero count kept). Period-13 M13 null: mean 11.013, sd 3.229, max 28; 99th percentile T13 = 19. Check on 10000 fresh shuffles: 67 exceed T13 (0.0067), in line with the discrete threshold.

## Real result
Real M13 = 18 against T13 = 19: not flagged. z = 2.164 against the null (mean 11.013, sd 3.229); S-style ratio 1.634, against the claimed S1 = 1.72 on an unknown normalisation after interrupter tuning. Best real score M13 = 18 against the null max 28 (the null max is over all shuffles, not a threshold).

Scan of periods 2 to 40: period 13 ranks 3 of 39 by z (39: z 3.534; 26: z 2.361; 13: z 2.164). Look-elsewhere correction for period 13: P(max over 2 to 40 of null z >= 2.164) = 0.579. Strongest period overall is 39 (z 3.534), family-wise p = 0.0325. The elevated lags are the multiples of 13, the harmonic pattern a period-13 keyword gives, but the pre-registered test at 13 is not flagged. Planted period-13 keywords put their top period at 39 in 10 of 50 plants, so the real pattern is consistent with a period-13 keyword and equally with noise. The 39 result is an exploratory lead, not a pre-registered finding. Section is fixed, so no new data can confirm it.

Full per-period table and all numbers: agents/laneU_period13/out/period13_log.txt and period13_results.json.

## Verdict
INCONCLUSIVE (power). The pre-registered rule does not flag period 13 (M13 = 18 against threshold 19, z 2.164, scan rank 3 of 39, look-elsewhere p 0.579). The control shows power 0.36 at 308 runes against the required 0.80, so this negative cannot be read as evidence against a period-13 keyword in the section. The community's peak is neither reproduced under the fixed rule nor excluded. No candidate was produced, so no oracle run applies.

## Files
- agents/laneU_period13/period13_test.py: the full test (section mapping, statistic, null, plants, scan). Run from the repo root: `python agents/laneU_period13/period13_test.py`. Single process, BELOW_NORMAL priority set via ctypes.
- agents/laneU_period13/out/period13_log.txt: every number in this file (stdout copy in period13_stdout.txt).
- agents/laneU_period13/out/period13_results.json: the same numbers in machine-readable form, including the 50 plant keys.

## Orchestrator follow-up (2026-10-17)

Lane U noticed lags 13, 26 and 39 all elevated in the increments of pages 53-54. Checked with independent code:

- Lag 13: 18 matches (null 10.95 +- 3.22, p 0.026); lag 26: 18 (10.41 +- 3.16, p 0.019); lag 39: 21 (10.01 +- 3.11,
  p 0.0009). The harmonic sum 13+26+39 = 57 against a shuffle mean of 31.4: 0 of 10,000 within-section shuffles reach
  it, and base period 13 beats every other base 2..13 (next best 42). The matches are spread over the section and over
  all 13 residues, with almost no adjacent pairs, so they are not one repeated block.
- But the section was picked because it peaked. `lp/t8_harmonic_scan.py` runs the same harmonic statistic over every
  page and page pair, raw and increments, base periods 2..13 (2,568 cells), and repeats the whole scan on 100 books
  shuffled within pages (increments, so the doublet deficit is kept). The real book's top cell is this one (z +4.72),
  but the null's top cell averages +3.87 +- 0.43 (max +5.43), and 5 of 100 shuffled books beat it: **book-wide p about
  0.05**. One shuffled book put its top cell at pages 52-53, base 13, z +4.56.
- `lp/t9_period13_solve.py` solves the section as a period-13 Vigenere or Beaufort on the increments (chain cipher with
  a periodic inner key). Controls: 10/10 planted English passages of this length recovered with all 13 key letters
  (quadgram -4.2 to -4.7). Real: Vigenere -6.340 (null -6.335 +- 0.056, z -0.08), Beaufort -6.290 (null -6.360 +- 0.063,
  z +1.11); the decrypts are noise.

Reading: the strongest local periodic signal in LP2 is a 2-sigma event once the whole book is scanned, and the simplest
cipher that would produce it does not decrypt the section. It stays a recorded lead, not a finding.
