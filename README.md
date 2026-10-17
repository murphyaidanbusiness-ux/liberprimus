# Liber Primus: a controlled cryptanalysis campaign

An attempt to break the unsolved part of Cicada 3301's *Liber Primus* with an orchestrated team of
AI research and attack agents, over three days in October 2026.

**It did not break it.** What it produced instead is, as far as we can tell, the largest set of
*controlled* negative results anyone has published on this text: fourteen attack families, each with
a planted-key positive control recovered at rank 1 and a size-matched null, each null on the real
runes. Plus six verified structural constraints that narrow the cipher to one family, and a safe tool
for the one lead the book itself gives.

Read [REPORT.md](REPORT.md) for the full account. This file is the map.

## The problem in one paragraph

Liber Primus is a 58-page runic book released in 2014. Part one was solved quickly with simple
ciphers. Part two, pages 0–54, 12,956 runes in a 29-symbol alphabet, has resisted everyone for twelve
years. Its statistics are flat at every order except one: adjacent identical runes occur 86 times
where about 447 are expected. That doublet deficit is the only fingerprint the ciphertext has.

## What the campaign established

Each of these was found by a lane or a scout and then verified independently by the orchestrator.

1. **Flat at every order.** No periodicity whole-corpus, per section, per page, or aligned to word starts; no key shared between sections; linear complexity n/2.
2. **The key varies by position.** The conditional distribution of each rune given the previous one is exactly what flat increments predict; any fixed feedback table is excluded at ~245σ.
3. **Repeated cipher words are at chance.** 16 repeated words of three or more runes, against 11 ± 3 for a random stream and 999 for English of the same size. Any cipher with a small per-word state is excluded by counting.
4. **The layout is not the plaintext's layout.** Word lengths have English marginals but zero sequential structure (z = +0.9 vs +7 to +15 for English); sentence marks are placed independently of word length; line breaks are a glyph-width fill. Two community members found this independently in 2026.
5. **One weak word-aware signal.** Runes five apart inside a word coincide at 4.9% vs 3.45% (about 2.5σ after correction). Found by ZzNible and Oosterhof; replicated here. No visible feature explains it.
6. **The "chain with EA as the zero step" model is refuted** by the cross-word doublet count (p ≈ 1e-11).

The only cipher shape consistent with all six is an evolving-alphabet walk with skip-on-repeat
(Oosterhof's model). Lane K showed it cannot be reached by global search; lane L exhausted its
keyword-built corner.

## The attack lanes (all null, all controls passed)

| lane | family | scale |
|---|---|---|
| A | per-page keyword chain attack, 362,700 keys, 128 variants | ~2×10⁹ decryptions |
| B | hash/KDF keystreams, 3,400 seeds, 20 byte mappings | 152M trials |
| C | gematria-number keystreams, full period; word-sum autokeys | ~2M offsets |
| D | 7 alternative constructions, each with a predicted signature | — |
| E | plaintext language/register from word structure | 906 distributions |
| F | word-length alignment vs 149 texts | 15.7M words |
| G | era-correct PRNGs (CPython 2.7/3.2 string seeds, glibc, PHP, Java, MSVC), bit-exact | 16.9M streams |
| H | book-code pointers into Self-Reliance, Liber AL, Mabinogion | 10,880 configs |
| I | layout as a cover channel, 22 channels | 221k cells |
| J | lag-5 echo mechanism search, 23 simulated constructions | — |
| K | global search feasibility for the walk model | 5/5 plants on fixed alphabets, 0/63 on the walk |
| L | keyword-built walk keys | 2^55.6 keys per start |
| M | title cribs at 17 section and 55 page openings | 1.5×10⁹ key fragments |
| N | full-position crib drag, 5,075 cribs | ~2×10¹⁰ fragments |

Every lane directory under `agents/` has a `RESULTS.md` with the method, the null calibration,
the control, the numbers, and the verdict, plus the code and raw outputs.

## The research scouts

Five scouts surveyed the community state, recent AI code-breaking, no-repeat generators, Cicada's
demonstrable source texts, and layout hypotheses before the second round of attacks. Their reports
are under `research/`, with `research/SYNTHESIS.md` turning them into the action table above.

## hashhunt

Page 56 of the book says a page on the deep web hashes to a given 512-bit value. `hashhunt/` is a
standard-library-only tool that enumerates archived captures of 2013–2017 tor2web gateway URLs in
the Wayback Machine and Common Crawl, downloads text-only originals, and hashes them under six
functions (including original BLAKE-512, verified against published vectors) and ~160
normalisations. It never renders or executes anything. Self-test: 35/35. Odds of a match are low;
see its README for why.

## Reproducing

```
./scripts/fetch_sources.sh          # clones the community repos into ./dl (git-ignored)
python3 lp/lpdata.py                # prints 12956 and the SHA-256 pin
python3 lp/t1_stats.py              # fingerprint, locality, periodicity
python3 lp/verify_candidate.py FILE # score any candidate plaintext
```

All scripts expect to be run from the repository root. Lane scripts were written against a
scratch layout and have had their absolute paths rewritten to repo-relative ones; most run as-is,
some need their large intermediate files regenerated (they were not committed).

## Credit

This work stands on the public record of the Cicada solving community and on four repositories in
particular: [Dukotah/cicada3301](https://github.com/Dukotah/cicada3301) (exclusion ledger, oracle,
corpora), [Leo-Y-Zhang/LiberPrimusAnalysis](https://github.com/Leo-Y-Zhang/LiberPrimusAnalysis)
(fingerprint and chain model), [TheronEagle/liber-primus-research](https://github.com/TheronEagle/liber-primus-research),
and [micheloosterhof/aldegonde](https://github.com/micheloosterhof/aldegonde) (the walk model, the
lag-5 echo, the layout findings). The rune transcription is the krisyotam/rtkd lineage. The chain
model has been the CicadaSolvers Discord's working model since 2016; the layout findings were first
noted there by mae3301 and Oosterhof. None of the constraints above should be read as this project's
discoveries; the controlled exclusions are its contribution.

## What this repository is not

It is not a solution, a partial solution, or a claim of one. If you think you have a key, run it
through the community oracle in `dl/dukotah/liber-primus/verify_solution.py` and
`lp/verify_candidate.py` before telling anyone, including yourself.

MIT licensed.
