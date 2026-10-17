# Research synthesis — five scouts, 2026-10-09

## What the field knows (verified primary facts unless marked)
- LP2 (58 images incl. pages 56/57) was released whole on the 7th onion, announced by the signed message of 2014-05-02. Nothing was released later. Last verified Cicada message: 2017-04-04 (key 7A35090F). No source states a pad or key was ever distributed. The page-56 hash's algorithm is not even certain (SHA-512 / BLAKE-512 / BLAKE2b all listed). [scout1]
- The Discord core group has used "inner cipher + add previous ciphertext rune" (our chain model) as its working model since 2016 and analyses the delta stream. Skip-on-repeat was on the wiki; mortlach's 2016 recursive algorithm reproduces the doublet distribution. [scout1]
- Our layout findings were first noticed in 2026 by mae3301 (Discord) and Oosterhof (aldegonde repo): word-length autocorrelation flat, sentence-final words indistinguishable from random, marks layout-coupled and aligned with typeset quote marks (p = 1.5e-7). [scout1] Independently confirmed by scout5 (sentence-final contrast −0.11 vs +1.65 in English) and by me.
- Strongest unexplained signal in the corpus: within-word distance-5 coincidence 4.92% vs 3.45% (ZzNible preregistered p = 0.0086; Oosterhof p ≈ 0.001). Replicated by me: 104/2105, z = +3.75, diffuse across positions and sections. It is word-boundary-aware. [scout1, my t5]
- The "Astra" event: GPT-6 assisting two engineers on an 1809 homophonic letter and a 1918 ADFGVX message — simulated annealing on non-flat statistics with partial keys supplied by humans. Not transferable. No AI has solved K4 (found in an archive, 2025), Zodiac, Dorabella, Beale, Voynich or any LP2 page. Berlekamp–Massey over GF(29) was already run on LP2: linear complexity n/2 (random-like). [scout2]
- No known cipher or generator natively suppresses immediate repeats (Chaocipher, LC4, Enigma, RC4, Spritz, LCG, lagged Fibonacci, Solitaire, all autokeys: 2.7–4.8%). The wiki's "autokey explains low doublets" is wrong. Matching 0.66% needs an avoid-repeat rule enforced ~84% of the time; the natural mechanism is the chain with one rare zero letter. [scout3]
- Toolchain: GnuPG 1.4.11 (GNU/Linux) headers 2012–14, an Ubuntu 12.04-era box (Python 2.7.3 / 3.2.3). The community's 2^32 MT sweep covered integer seeds only, additive model only. glibc/PHP/Java/MSVC generator cells were queued by Dukotah and never run. [scout2, scout3]
- Cicada's demonstrable sources: Gibson's Agrippa (2012), Emerson's Self-Reliance (2014 book code, paragraph:sentence:word:letter), Liber AL (2013, consensus), Mabinogion (2014), the Anglo-Saxon rune poem. Self-Reliance and Liber AL were never tested as pointer targets for LP2 numbers. [scout4]
- Dukotah's seam table: doublet deficit holds across word, line and page seams → shuffling words AFTER encryption is excluded; shuffling BEFORE is undetectable. [scout5]

## Corrections to my earlier assumptions
- Pages 56/57 were not a 2016 release. The 2016 event is one signed message.
- The 2012 "Agrippa" is Gibson's poem, not Cornelius Agrippa. GEB, Tao, Kybalion, Jung, Wilson, Zen collections: no sourced Cicada citation.
- Dukotah's "language signal" came from the 3,367 line-fragment word count; the merged count is 2,928. My loader already merges.
- The word segmentation is NOT pure decoration: the d5 echo is boundary-aware.

## Actions taken from the synthesis
| lane | lead source | hypothesis | status |
|---|---|---|---|
| G (Opus) | scout2 #1, scout3 #1/#5 | era-correct PRNGs (CPython 2.7/3.2 string seeds, glibc, PHP, Java, MSVC) with avoid-repeat emission or chain keystream | running |
| H (Sonnet) | scout4 #1-3 | LP2 word numbers as book-code pointers into Self-Reliance / Liber AL / Mabinogion (2012 and 2014 formats) | running |
| I (Sonnet) | scout5 #5 | layout (word lengths, sentence lengths, line structure, acrostics) as a cover channel | running |
| J (Opus) | scout1 #1 | the within-word lag-5 echo: corrected significance, mechanism search with simulated lag profiles, attack if a mechanism fits | running |
| me | scout3 #2 | 86 doublets as a side channel (gaps, positions, neighbours, moduli) | done: null, all |z| ≤ 2 |
| me | scout1 #1 | word-aligned periodic keys (cosets by position-in-word, L = 1..12, raw and increments) | done: null |

## Leads deliberately not pursued (and why)
- Hashing hidden-service archives against the page-56 hash: archive.org and onion access are blocked here, and the hash algorithm is uncertain.
- Chaocipher-family on 29 symbols: scout3's simulation shows no doublet deficit, so it fails the fingerprint before any key search.
- Seed-agnostic LFSR / lagged-Fibonacci scans: scout2's power calculation shows ≤ 1.7σ detectability at n = 12,956.
