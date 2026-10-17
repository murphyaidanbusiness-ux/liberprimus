# Liber Primus (Cicada 3301) — cryptanalysis campaign, 2026-10-08

**Outcome: not cracked.** LP2 pages 0–54 (12,956 runes) remain unsolved. This session ran an orchestrated
campaign: my own structural tests plus six delegated lanes (two Opus, four Sonnet), each with planted-key
positive controls and size-matched shuffle nulls, with every claimed number spot-checked by me. Every attack
family came back at the noise floor. The campaign did, however, establish three new structural facts about the
book and formally closed several families the public ledgers had left open.

## Data
- krisyotam/rtkd transcription, pages 0–54, SHA-256 of indices = 023312066df4...af1585 (matches the community pin).
- 2,896 words, 174 sentence marks, 9 chapter sections; words run across line breaks (72% of line breaks fall mid-word: justified prose layout).
- Code: SCRATCH/lp/*.py (loader, my tests, verifier); SCRATCH/agents/lane*/RESULTS.md (each lane's full write-up, code, raw outputs).

## Fingerprint (reproduced and extended)
| statistic | observed | random |
|---|---|---|
| IoC (29 symbols) | 1.000 | 1.000 |
| adjacent identical runes | 86 / 12,955 = 0.66% | 3.45% (z = -17) |
| increment stream Δc, IoC on nonzero values | 1.001 | 1.000 |
| conditional IoC of next rune given previous | 1.026 | 1.023 predicted by flat-28 increments |
| doublet gaps | mean 150.8, sd 142 | geometric 150.7 / 150.7 |

The only cipher family consistent with this is a chain: c_i = c_{i-1} + s_i, s_i a keyed flat nonzero increment,
with s_i = 0 for one rare letter. Lane D proved the conditional-IoC result formally: any FIXED feedback table is
excluded at ~245 sigma, so the key must vary by position; it is aperiodic (periods 1..1500 whole-corpus, 2..40 per page)
and constant over no word, line, sentence, page or chapter.

## New structural findings (ciphertext-only, language-agnostic)
1. **Word lengths look English only in the marginal.** The per-word rune-length histogram fits English prose with
   THE and OF absent (JS 0.0008; Latin, Romance, Celtic, Germanic, Old English, Old Norse, Gothic, Esperanto,
   Finno-Ugric, Turkic rejected; letter-by-letter spelling rejected, P = 0.998 for digraph runes). Lane E, 906 candidate distributions.
2. **But the ORDER of word lengths has no structure.** Adjacent-length dependence: unsolved z = +0.9 against a
   shuffle null; English windows of the same size z = +7 to +15, even with THE/OF/TO removed; Cicada's own solved
   pages z = +4. Verified by me and by Lane F. The visible words are not plaintext words in reading order.
3. **Sentence marks are placed independently of word length.** Sentence-first words average 4.39 runes and
   sentence-last 4.30 against a random-placement null of 4.42 ± 0.17 (z = -0.2 / -0.7). In every real text the
   first word of a sentence is markedly short. The "." marks are not sentence boundaries of running prose.
4. **Word gematria sums carry nothing.** Residues mod 29/28/26/10, primality rate, parity and cumulative sums all
   match uniform-random runes (|z| < 2.1). "Their numbers" are not the message, at least not per word.
Together: the layout (words, sentences) has the *statistics* of English without its *sequence*. Either the plaintext
words are transposed, or the segmentation is synthetic decoration on a flat stream.

## Attack lanes (all null; controls all recovered)
| lane | family | scale | control | real best vs null |
|---|---|---|---|---|
| mine | periodic / local keys on increments; GF(29) multiplicative sequences (21 seqs × 300 offsets × 55 pages) | ~1M | — | max z 2.9 over 55 pages |
| A (Opus) | per-page and per-section keyword chain attack: 362,700 keys (English dictionary + 1,343 Cicada words), Z28 additive (112 variants) + GF(29) (16 variants) + Vigenère/Beaufort/skip-rule controls; C/OpenMP | ~2×10⁹ page decryptions | 15/15 planted keys rank 1, z 32–45 | best quadgram -6.4 (English -4.2); units beating null at chance; oracle FAIL |
| B (Sonnet) | hash/KDF keystreams: MD5, SHA-1/256/512, SHA3, BLAKE2b, HMAC, PBKDF2 ≤1000; 7 constructions; 20 byte mappings; 2.5k global + 931 per-page seeds; chain, GF(29), OTP | 152M trials | 5/5 planted streams rank 1 | best IoC 1.0279 vs null max 1.0287; oracle FAIL |
| C (Sonnet) | gematria-number keystreams from solved text and the book's own structure, full period (0..2794); word-sum and prime-value autokeys, all seeds | ~2M offset trials | planted key at offset 2300, z = 420 | family max z 7.7 vs null 7.2 ± 0.4 (max 8.2) |
| D (Sonnet) | 7 alternative constructions (lag-L chains, prime-domain, fixed Latin square, two-layer, transposition, key-skip Vigenère, base-29 encoders) | — | synthetic controls z 14–76 | each excluded by its predicted signature or indistinguishable from the plain chain |
| E (Sonnet) | plaintext language/register from word structure | 906 distributions, 1,000 bootstraps | — | English-minus-THE/OF; sentence marks random |
| F (Opus) | word-length alignment vs 149 texts (15.7M words), 42 merge/drop/digraph models, Smith-Waterman + k-mer index | full local alignment | planted passage z = 344 | real best 10–15 vs shuffle 9–12 (planted 68–437) |

Community exclusions these sit on top of: autokey; ~200 running-key texts; 46 integer sequences in raw and chain form;
all 2^32 Python-2.7 Mersenne Twister seeds; ~14.5×10⁹ offsets into Bitcoin/NIST/RANDOM.ORG/RAND randomness; Outguess of
all page images; hidden structural channels (Dukotah/cicada3301 LEDGER.json, 172 rows; Leo-Y-Zhang FINDINGS.md).

## Assessment
Nothing measurable in the ciphertext links consecutive runes beyond "not equal to the previous one", and nothing in
the layout links the visible words to each other. Every key family that could be enumerated from the book, from
Cicada's vocabulary, from standard hashes of plausible seeds, or from published texts is excluded at calibrated
noise. The remaining possibilities are: (1) a true external pad, in which case the ciphertext is uninformative by
construction; (2) a seed-derived pad from a generator and seed outside everything enumerated, which only new
external information can narrow (the page-56 SHA-512 deep-web page, never found, is the book's own pointer);
(3) a plaintext that is not running prose at all (the layout statistics point this way), which would defeat every
English-text scorer in use, including the oracle, even if a key were right. The third point is the one actionable
thing this campaign adds: any future sweep should score candidates with a language-agnostic statistic
(increment IoC, conditional IoC) first and an English model second.
