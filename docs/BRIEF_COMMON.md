# Common brief: Liber Primus (Cicada 3301) attack campaign

## Paths (all absolute)
- SCRATCH = .
- Loader: SCRATCH/lp/lpdata.py  ->  `import sys; sys.path.insert(0, SCRATCH+'/lp'); import lpdata; U, C, sha = lpdata.unsolved()`
  U = list of 55 page dicts (keys: page, idx (rune indices 0..28), word, line, sent, chap  — per-rune ids); C = flat list of 12,956 indices.
  lpdata.TR = transliterations, lpdata.PRIMES = Gematria Primus prime values (F=2 ... EA=109). sha must equal 023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585.
- Prior results and scripts: SCRATCH/lp/REPORT.md, t1..t4 *.py (read REPORT.md first).
- Community repos (cloned, read-only reference): SCRATCH/dl/dukotah (ledger: liber-primus/LEDGER.json, ELIMINATION-LEDGER.md, FINAL-SYNTHESIS.md; oracle: liber-primus/verify_solution.py; quadgrams: liber-primus/data/english_quadgrams.txt; solved pages: liber-primus/SOLVED-PAGES.json), SCRATCH/dl/leo (docs/FINDINGS.md, docs/REPORT.md, lp.py, tests*.py), SCRATCH/dl/theron.
- Write ALL your code and outputs under SCRATCH/agents/<your-lane-name>/. Run python with the loader on sys.path. numpy 2.5 is available; gcc is available if you need C for speed. No pip network guarantees (GitHub raw fetches via curl work; most other hosts are blocked by proxy).

## Alphabet
29 runes, index order: F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA. All key arithmetic mod 29 unless stated. No K (->C), no V (->U), no Q, no Z in plaintext. Solved pages used: atbash, shift, Vigenere with word keys (DIVINITY, FIRFUMFERENFE) with F-rune interrupts (skipped, key not consumed), and p_i = c_i - (prime_i - 1).

## Hard constraints from the ciphertext (verified twice; do not fight them)
1. Unsolved stream is flat: IoC = 1.000, entropy 4.857 bits. No periodicity on whole corpus, sections, or per page (periods 2..1500 tested on raw runes and on increments). No key shared between sections.
2. The ONLY anomaly: adjacent identical runes 86/12955 = 0.66% vs 3.45% random. Doublet gaps are geometric; doubled runes uniform over runes.
3. Consequence: any cipher c_i = p_i + k_i with k independent of the ciphertext yields ~3.4% doublets on English -> EXCLUDED, whatever k is. Only families consistent: (a) CHAIN cipher c_i = c_{i-1} + s_i where s_i in 1..28 is a keyed flat increment and s_i = 0 only for one rare plaintext letter (EA is 0.67% in Cicada English; doublet rate fits), e.g. s_i = 1 + ((x(p_i) + k_i) mod 28) or s_i = k_i * x(p_i) in GF(29) with x(EA)=0; (b) a flat cipher plus "advance key when the output would repeat the previous rune" (leaks a few doublets). In both, the per-position key k_i is flat and aperiodic, and constant over no word/line/page/chapter.
4. Increments D_i = (c_i - c_{i-1}) mod 29 are the natural object to attack: for the chain family, D_i (nonzero) = bijection(p_i, k_i).

## Scoring protocol (mandatory — this is how every previous false alarm was made)
- Primary: IoC of the candidate output stream (normalised: 1.0 random, ~1.7-1.8 English in runes). Secondary: quadgram log-score from dukotah english_quadgrams.txt (English -4.1..-5.0 per quadgram, noise ~-7.5).
- ALWAYS compute a size-matched null: run the identical search on shuffled versions of the same page/section (>= 20 shuffles) and report the real best against the null max. A hit is real only if it beats the null max by a clear margin AND the decrypted text contains readable Cicada-style English words. Report z-scores, not adjectives.
- Submit any serious candidate keystream to the oracle: `python3 SCRATCH/dl/dukotah/liber-primus/verify_solution.py --keystream FILE` (read its --help / --selftest first).
- Before running a family, grep the dukotah LEDGER.json / ELIMINATION-LEDGER.md and leo FINDINGS.md for it; skip exact duplicates, note near-duplicates, and spend time on what is NOT there.

## Deliverable
A file SCRATCH/agents/<lane>/RESULTS.md with: what you tested (families, parameter ranges, trial counts), the null calibration, the best real results with z-scores, any candidate plaintexts (first 120 runes transliterated), and an honest verdict per family. Do not claim a solve unless the oracle passes. Keep the final chat report under 400 words and point to RESULTS.md.
