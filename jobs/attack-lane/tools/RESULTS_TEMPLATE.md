# Lane <X>: <family> (<date>)

**Verdict: <NULL | CANDIDATE | INCONCLUSIVE (power)>.** <one sentence with the key numbers>

- Gate: jobs/hypothesis-gate/runs/<date>-<hypothesis>.md (<GATE PASS line>)

## Hypothesis
<the cipher, the key model, the key space and its size, what fraction was searched, what is new vs lanes A-R and the ledgers>

## Control
<plant: key drawn from the searched space, enciphered with the same cipher code on English from toolbox/runes.py>
Recovered k/n plants at rank 1 (z of each, or median and minimum). <miss cases and why, if any>

## Null
<N> shuffles (<toolbox/nulls.py function used>): best score mean <m>, sd <s>, max <x>.

## Real result
Best real score <v>, z = <(v - m) / s> against the null; null max <x>. <top candidates, first 120 runes transliterated>

## Verdict
<NULL | CANDIDATE | INCONCLUSIVE (power)>. <if CANDIDATE: oracle `verify_solution.py --plaintext` PASS/FAIL and `lp/verify_candidate.py` output>

## Files
<scripts, logs and outputs in this directory>
