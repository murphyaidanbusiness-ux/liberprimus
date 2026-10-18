# Survey: fixture (two entries, the shape a real run must have)

### T: Kasiski examination and Friedman's kappa test
- Source: W. F. Friedman, Military Cryptanalysis Part II, section 5 (declassified; book citation, fixture only)
- Exploits: repeated plaintext under a periodic key gives repeated ciphertext at multiples of the period; kappa rises at the period
- LP2 constraints: C1 kills it: no period 1..1500 on runes or increments, and kappa is flat
- Prior coverage: round one t1/t4 (`lp/t4_perpage_period.py`), Leo `dl/leo/docs/FINDINGS.md` addendum 2026-09-07
- Verdict: not-applicable (C1: no period 1..1500)
- Test design: none needed

### T: Progressive-alphabet isomorphs
- Source: W. F. Friedman and L. D. Callimahos, Military Cryptanalytics Part III, chapter 2 (declassified)
- Exploits: under a progressive (stepped) mixed alphabet, repeated plaintext produces ciphertext with the same pattern of repeats (isomorphs), whose alignment reconstructs the primary alphabet
- LP2 constraints: C3 (repeated cipher words at chance) limits exact repeats; C5 (lag-5 echo) suggests same-alphabet positions inside words
- Prior coverage: none found (grep: isomorph, isomorphism in agents/, research/, dl/dukotah/liber-primus/LEDGER.json)
- Verdict: applicable-untested
- Test design: search LP2 for pattern-isomorphic word pairs (same internal repeat pattern, length >= 7) above a word-shuffle null; planted control: encipher English with a stepped Quagmire and require the attack to recover the primary alphabet from the isomorphs it finds

## Top 5
1. Progressive-alphabet isomorphs

## Sources opened
- (fixture: book citations only, no URLs)
