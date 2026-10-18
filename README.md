# Liber Primus: a controlled cryptanalysis campaign

An attempt to break the unsolved part of Cicada 3301's *Liber Primus* with an orchestrated team of
AI research and attack agents, in October 2026: round one over three days, round two on 16-18 October.

**It did not break it.** What it produced instead is, as far as we can tell, the largest set of
*controlled* negative results anyone has published on this text: fourteen attack families in round one
and ten more lanes in round two, each attack with a planted-key positive control and a size-matched null,
each null on the real runes. Plus seven verified structural constraints that narrow the cipher to one
family, a safe tool for the one lead the book itself gives, and a graded census of 232 methods the
community has already ruled out.

Read [REPORT.md](REPORT.md) (round one) and [REPORT_ROUND2.md](REPORT_ROUND2.md) (round two) for the full
account. This file is the map.

**Round two in one paragraph.** The best-fitting family left by the constraints is the Quagmire dodge (a
five-step alphabet clock with a skip on every would-be repeat). Lane O ported and ran the community's
never-run sweep of its odometer form over Cicada's own 47 named words: 577.8 million keys, held out on
unseen text, null. Lane X then built a new, key-free attack on the same form that needs no keyword at all,
and excluded it for every possible alphabet under one continuous key. Lane W found that the community's
scorer for the family's clock-dependent form was only ever validated on the odometer and cannot see the
clock form, which so far has no working search tool. The census found that almost every method the
community has tried is ruled out by the fingerprint itself, not by a failed search.

## How the work is organised

`AGENTS.md` is the map. Each recurring task is a folder under `jobs/` with a pass/fail `PROOF.md`, a `SKILL.md`
playbook, its scripts and a test fixture; shared code and the LP2 fingerprint live in `toolbox/`; `CHANGELOG.md` records
every fix with the model that was running. Any new cipher idea goes through `jobs/hypothesis-gate/` first, which
simulates it on English and grades it against the seven constraints in `toolbox/CONSTRAINTS.md` before compute is spent.
Before a lane starts, `research/EXHAUSTED.md` says whether the community has already ruled the idea out, and how solidly.
Agents extract and run; the orchestrator judges every verdict and re-derives every headline number before it is reported.

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
7. **The 86 doublets sit uniformly on every small position modulus** (2 to 8, by book and by page index). Oosterhof measured the mod-5 case first; round two extended it. No repeat-suppression rule keyed to the absolute position can be LP2's.

The only cipher shapes consistent with all seven are evolving-alphabet walks with skip-on-repeat:
Oosterhof's walk and its Quagmire-dodge siblings. Lane K showed the walk cannot be reached by global
search; lane L exhausted its keyword-built corner; round two's lane X excludes the odometer dodge for any
alphabet under one continuous key.

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

## Round two lanes

| lane | question | result |
|---|---|---|
| O | Quagmire-odometer dodge keyed by Cicada's 47 named words (tiers A and B) | 577.8M keys, every retained candidate held out on unseen text: null at ~89% power; covers both dodge variants |
| P | Does an archived capture of a Cicada-signed onion hash to the page-56 target? | Wayback half null (3 captures); Common Crawl half nearly finished, 0 captures so far |
| Q | Is any keystream reused at any shift? | null; reuse of about 3,200 runes or more excluded at 90% power |
| R | Do the two signals survive the choice of transcription? | yes, on every faithful reading |
| S | Cicada's solved-page totient stream with a collision skip, from every start | null; found the doublet-position constraint |
| T | Oosterhof's walk keyed by Cicada's prime and totient ladder (20,000 keys) | null |
| U | Is the period-13 peak in pages 53-54 real? | inconclusive (power); book-wide p about 0.05 |
| V | Is the lag-5 echo localised, and which mechanism explains it? | diffuse; no mechanism selected |
| W | Can the community's dodge-aware scorer see the clock-dependent dodge? | no (0/20 planted keys); it was validated on the odometer only |
| X | The odometer dodge with ANY alphabet, by a key-free attack | null for one continuous key: 24/24 planted keys detected, LP2 inside 50 nulls (z +1.5) |
| census | What has the community already ruled out, and how solidly? | 232 methods: 130 dead by the fingerprint, 6 partial and finite, none high-hope (`research/EXHAUSTED.md`) |

Each lane directory under `agents/` has its `RESULTS.md`; independent re-derivations are in `jobs/verify-lane/runs/`.

## The research scouts

Five scouts surveyed the community state, recent AI code-breaking, no-repeat generators, Cicada's
demonstrable source texts, and layout hypotheses before the second round of attacks. Their reports
are under `research/`, with `research/SYNTHESIS.md` turning them into the action table above.

## hashhunt

Page 56 of the book says a page on the deep web hashes to a given 512-bit value. `hashhunt/` is a
standard-library-only tool that enumerates archived captures of 2013–2017 tor2web gateway URLs in
the Wayback Machine and Common Crawl, downloads text-only originals, and hashes them under six
functions (including original BLAKE-512, verified against published vectors) and ~160
normalisations. It never renders or executes anything, and `plan`/`fetch` refuse to run without an
allowlist of onion hosts: by default the four named in Cicada's own signed messages, so it never pulls
content from unknown darknet sites. Self-test: 39/39. The round-two run over the Wayback Machine was
null; the Common Crawl run is nearly finished; see `agents/laneP_hashhunt/RESULTS.md`.

## Reproducing

```
./scripts/fetch_sources.sh          # clones the community repos into ./dl (git-ignored)
python3 lp/lpdata.py                # prints 12956 and the SHA-256 pin
python3 lp/t1_stats.py              # fingerprint, locality, periodicity
python3 lp/verify_candidate.py FILE # score any candidate plaintext
python3 toolbox/fingerprint.py      # the seven constraints on LP2 (asserts the pins)
python3 -I -X utf8 agents/laneX_general_alphabet/run_lane.py real   # lane X on LP2 (about 35 s)
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
lag-5 echo, the layout findings, the Quagmire dodge, its scorer and sweep, and the mod-5 doublet phase
test). Round two's census also drew on the public notes of ZzNible, Wulfic and Pitchfork-and-Torch.
The rune transcription is the krisyotam/rtkd lineage. The chain
model has been the CicadaSolvers Discord's working model since 2016; the layout findings were first
noted there by mae3301 and Oosterhof. None of the constraints above should be read as this project's
discoveries; the controlled exclusions are its contribution.

## What this repository is not

It is not a solution, a partial solution, or a claim of one. If you think you have a key, run it
through the community oracle in `dl/dukotah/liber-primus/verify_solution.py` and
`lp/verify_candidate.py` before telling anyone, including yourself.

MIT licensed.
