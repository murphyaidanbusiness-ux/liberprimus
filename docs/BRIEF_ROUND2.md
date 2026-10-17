# Round-two brief (every lane reads this first)

Round one (2026-10-08/09) ran fourteen attack lanes on LP2 and all came back null. Read `REPORT.md` for the six
verified constraints and `research/SYNTHESIS.md` for what the community already knows. This brief is the same
contract as `docs/BRIEF_COMMON.md` adapted to the machine round two runs on.

## Machine and paths
- Windows 11, 16 cores, Python 3.13 (`python`), numpy 2.5. **No C compiler.** Use numpy vectorisation or
  `multiprocessing` (guard with `if __name__ == "__main__":`, Windows spawns).
- Use the Bash tool with POSIX syntax. Always `cd "/c/Users/aidan murphy/liberprimus"` and run from the repo root.
- Loader: `import sys; sys.path.insert(0, "lp"); import lpdata; U, C, sha = lpdata.unsolved()`.
  `U` = 55 page dicts (per-rune lists `idx` 0..28, `word`, `line`, `sent`, `chap`); `C` = flat list of 12,956 indices;
  `sha` must equal `023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585` (assert it).
  `lpdata.TR` = transliterations, `lpdata.PRIMES` = Gematria Primus values.
- Community repos (read-only reference) under `dl/`: `dl/dukotah` (ledger `LEDGER.json`, oracle
  `liber-primus/verify_solution.py`, quadgrams `liber-primus/data/english_quadgrams.txt`, solved pages
  `liber-primus/SOLVED-PAGES.json`), `dl/leo`, `dl/theron`, `dl/aldegonde_clone`.
- Write ALL code and outputs under `agents/<your-lane>/`. Do not edit `lp/`, `hashhunt/`, other lanes, or `dl/`.
- Large intermediates (> 5 MB) go in files ending `.bin` or `.npy` (git-ignored), never committed.

## Alphabet
29 runes, index order: F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA. Key arithmetic mod 29
unless stated. Solved pages used atbash, shift, Vigenère with word keys (DIVINITY, FIRFUMFERENFE) with F-rune
interrupts (skipped, key not consumed), and p_i = c_i - (prime_i - 1).

## Non-negotiable protocol
1. **Planted-key positive control first.** Encrypt real English (convert a solved page or any English text to runes)
   under your hypothesis with a random key from the space you search; your search must recover it at rank 1.
   No control, no result.
2. **Size-matched null.** Run the identical search on >= 20 shuffles of the same text. Chain-model nulls must shuffle
   the increments D_i = (c_i - c_{i-1}) mod 29 *within pages* (keeps the doublet deficit). Report real best vs null max
   as a z-score.
3. **Scoring.** Normalised IoC (1.0 random, ~1.7-1.8 English runes) and quadgram log-score per quadgram
   (English -4.1..-5.0, noise ~-7.5). A hit must beat the null max clearly AND read as English.
4. **Candidates** go to `python dl/dukotah/liber-primus/verify_solution.py --plaintext FILE` (read `--help` first) and
   `python lp/verify_candidate.py FILE`. Never claim a solve without the oracle passing.
5. **Before running**, grep `dl/dukotah/LEDGER.json`, the elimination ledger and `dl/leo/docs/FINDINGS.md` for your
   family and say what is new about your test.

## Deliverable
`agents/<lane>/RESULTS.md`: what was tested (family, parameter ranges, trial counts), the control (recovered? rank?),
the null (mean, sd, max), the real result with z, any candidate plaintext (first 120 runes transliterated), and an
honest verdict. Numbers, not adjectives. A clean null is a good result. Final chat reply under 300 words.
