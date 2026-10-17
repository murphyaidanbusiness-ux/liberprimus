# scout2_ai_codebreaking — how AI / computation actually broke famous ciphers, and what transfers to LP2

Date of research: 2026-10-09. Scout: scout2_ai_codebreaking.

Evidence labels: (a) verified primary fact, (b) community / press consensus, (c) speculation or my own inference.

Access caveat: WebFetch only resolved github.com in this sandbox, and curl was blocked by the permission classifier. Every news, blog and arXiv item below therefore comes from search-engine summaries of the pages, not from reading the pages. I have flagged anything where the summaries disagreed. The two local checks I ran (Chaocipher simulation, linear-combination power calculation) are my own, on synthetic English, not on LP data. Scripts: `research/s2/chao.py`, `research/s2/comb.py`.

---

## 0. TL;DR

1. The "OpenAI Astra solved that code" memory is real but smaller than it sounds. It is **GPT-6 "Astra"** (reported Sept-Oct 2026) used by individual engineers on two *historical, non-flat* ciphers. Neither is a famous unsolved puzzle in the Kryptos/Zodiac/Cicada sense.
   - 1809 Napoleon-era letter to Marshal Marmont: a homophonic substitution. Carter Church (SentinelOne) wrote it up on 2026-09-18. The press often miscalls it a "nomenclator". Cryptiana's maintainer marked it solved. This is the most probable "famous code" the user remembers.
   - 1918 German ADFGVX radio message: Prinz, 2026-09-17. The keyword was already known, the date check has a hole, and nobody independent has confirmed it.
2. **No AI system has solved Kryptos K4, Zodiac, Dorabella, Beale, Voynich, or any part of Cicada's Liber Primus.**
   - K4's plaintext was recovered from a Smithsonian archive in 2025, not by cryptanalysis. The method is still unknown.
   - The only 2025-26 AI attempts on LP2 that I could find are GitHub research logs. All report nulls.
3. Every verified computational solve (Zodiac 340, Copiale, Marmont, Chaocipher, M-209, Playfair records) needed **non-flat statistics plus a smooth fitness landscape** (a partially right key gives partially readable text). LP2 has IoC 1.000 and a key that varies by position. Hill-climbing, annealing, beam search, EM and neural decipherment therefore **do not transfer as key searchers**. They transfer only as *decoders* once a concrete key-generator family is hypothesised. That is how the community oracle already uses them.
4. Seed-agnostic keystream tests have **no power** here. Berlekamp-Massey and PRNG state recovery assume you see raw generator output. The ciphertext is `plaintext + key`, passed through an anti-repeat filter. Key-cancelling linear relations also destroy most plaintext redundancy (section 3.3). The only productive route is "hypothesise a generator or cipher family, decode, score".
5. The community repos (Dukotah, Leo-Y-Zhang, TheronEagle) have already run BM over GF(29), many PRNG families, KDFs and ~200 running keys. See section 4.3 for what looks un-run.

---

## 1. The recent "AI solved a code" events (2025-2026)

### 1.1 GPT-6 Astra: what happened (b, with some (a) from the author's own write-up)

**Marmont letter (1809).**
- Who: Carter Church, SentinelOne engineer, using OpenAI's GPT-6 "Astra". The model name varies by outlet ("GPT-6 Astra" vs "ChatGPT-6 Astra").
- Source cipher: a letter to Marshal Marmont, known only from one plate in a 1969 French army journal. It was on the standard unsolved-historical-cipher lists.
- Primary source: Church's write-up "Breaking the Marmont Cipher, 1809", dated 2026-09-18, https://carter.church/writeups/the-letter-to-marmont/ . I could not fetch it directly.
- Method as reported:
  - Astra took one scanned image (1,202 x 1,836 px), cut it into rows, transcribed hand-drawn signs, and merged variants (175 hand-drawn marks reduced to about 155 unique signs).
  - Anchors: a partial table of 33 sign values from historian Daniel Tant covered 435 of about 1,300 cipher units. Plain-text letters spelling CONSEQUENT in row 14 also helped. Together these covered about a third of the units before any new search.
  - Search: **simulated annealing** over letter assignments for the remaining signs, scored by French 3-, 4- and 5-gram statistics from Hugo, Dumas and Marmont's memoirs. The reference list cites Kopal's HistoCrypt 2019 paper on fixed-temperature annealing for homophonic ciphers.
  - Some signs were handled as whole words.
  - Cross-check: each new sign mapping was tested against all other occurrences of that sign.
- Verification:
  - Church reran with Marmont's memoirs and all Napoleonic texts removed from the LM and reportedly got the same reading.
  - Satoshi Tomokiyo (Cryptiana, which listed it as unsolved) reviewed it and marked it solved.
  - Historians quoted by Live Science (Michael Rowe, Zack White) call it useful, not revolutionary. Napoleon's other correspondence already described the expected content, and some troop figures look off.
- Hype and caveats:
  - Five signs that occur once remain ambiguous.
  - "Six hours" is the model run time. The wider project took several evenings.
  - Metafilter commenters note that annealing is one step among transcription and building a period-French dictionary. They asked whether the model chose annealing or Church told it to. Whether the code is released is reported inconsistently.
  - "Single prompt" and "217 years unsolved" are press framing.
- Why it does not transfer: a homophonic substitution has non-flat unigram and n-gram statistics, and a partial key is partially readable.

**ADFGVX message (27 Nov 1918).**
- Who: a developer called Prinz, write-up dated 2026-09-17.
- Claim: 170-symbol ADFGVX intercept decoded with the keyword TRUPPENVERSCHIEBUNG. The plaintext says an English cruiser arrived at Sevastopol. Prinz reports checking this against HMS Canterbury logs (Canterbury reached Sevastopol on 24 Nov 1918).
- Hype and caveats:
  - The keyword was already in the historical literature (Childs).
  - Reported introduction date of the keyword is 9 Dec 1918, which conflicts with a 27 Nov transmission. Prinz flags it as a loose end.
  - One digit of the date is uncertain.
  - The account involves human steering and keyword selection, so the AI's contribution is hard to isolate.
  - No independent validation. Hackaday and Tom's Hardware repeat it.
- Why it does not transfer: the key was known, so this is verification and decryption, not key discovery.

**What this means for the user's memory.** "Astra solved that code" is almost certainly one of these two. Neither involved a flat stream or an unknown generator.

Sources:
- https://www.calcalistech.com/ctechnews/article/h1dthf69mg
- https://www.tomshardware.com/tech-industry/artificial-intelligence/chatgpt-6-astra-cracks-217-year-old-napoleonic-code-in-just-six-hours-single-prompt-ai-run-solves-24-rows-of-custom-symbols-from-a-single-image-reveals-lost-troop-orders
- https://www.metafilter.com/214680/Breaking-the-Marmont-Cipher
- https://runtimewire.com/article/gpt-6-astra-marmont-cipher-carter-church
- https://hackaday.com/2026/09/20/world-war-i-coded-message-appears-cracked-finally/
- https://cybernews.com/ai-news/gpt-6-astra-cracks-100-year-old-wwi-cipher/
- https://runtimewire.com/article/gpt-6-astra-might-have-cracked-a-world-war-i-radio-cipher

### 1.2 Kryptos K4 (the other likely half-memory)

- (a) No cryptanalytic solve of K4 exists.
- (b) The 2025 "solution" was an **archive discovery**, not a break.
  - Jarett Kobek and Richard Byrne found five pages of strip-scrambled text in Sanborn's Smithsonian donation. With Sanborn's released clues they reconstructed the plaintext. Kobek: "no way on earth that this is a cryptographic solve".
  - Sanborn says K4 "has not been solved or decrypted", and sealed the folders for 50 years.
  - The archive including the K4 solution sold at RR Auction for **$962,500** (closed 2025-11-20) to an anonymous buyer.
  - Paradigm (https://www.paradigm.xyz/writing/kryptos) states it bought the archive. It runs a hash/HMAC verifier (SHA-256 plus Google Cloud KMS HMAC; guesses cost $1). It says there has been "an explosion in AI-assisted attempts on Kryptos, but none have succeeded yet". Its own wording on whether it was the buyer comes from a search summary and is unverified here.
- Hype: Feb 2025 claim by Michael Naughton that Grok 3 cracked K4 ("Berlin Clock"). Critics (https://gist.github.com/atoponce/1cd01f40786ab21af011f0d6257fba0c) say the outputs do not place the four released cribs (EAST 22-25, NORTHEAST 26-34, BERLIN 64-69, CLOCK 70-74) and differ between ChatGPT, Claude and Grok.
- A retracted GitHub "AI-assisted decryption" repo exists: https://github.com/slightofmind369/kryptos-k4-decryption
- kryptos.today and keithadler/kryptos (release 2026-09-29) are self-reported AI-agent null sweeps. The latter claims to rule out repeating-key tableau ciphers up to key length 26, Hill, Trifid and others, using released plaintext letters. Unverified.
- Lesson for LP2: K4 is only 97 characters, has four released cribs, and a human-readable key hint (KRYPTOS-themed). It has resisted 35 years of human and AI effort. LP2 has no cribs.

### 1.3 Other 2025-26 "AI cracked it" claims

- **Voynich:** several 2026 claims (viral TikTok, YouTube) with no accepted decipherment. An Oct 2026 report says the pages may have been bound out of order. (b)
- **Dorabella:** Sept 2025 arXiv "Dorabella Cipher as Musical Inspiration" (https://arxiv.org/abs/2509.17950) treats it as possibly musical, with n-gram LMs. It does not claim a decipherment. A 2021 study found synthetic music ciphers decipher poorly compared with text ciphers. (b)
- **Beale:** only forum claims. The open-source "decipher" repo (https://github.com/matthewdgreen/decipher) is a tool, not a solution. (b)
- **Zodiac 340:** solved 2020 by humans, with no AI involved (section 2.1).

### 1.4 AI and Cicada / Liber Primus specifically (2023-2026)

- **No AI-attributed solve of any LP2 page exists.** Every source says 56 of 58 pages remain unsolved as of Sept-Oct 2026. (b)
- Connor Tumbleson, 2024: GPT-4 knew the book was runic but was bad at OCR transcription. https://connortumbleson.com/2024/01/29/ai-cicada-3301/
- AI-agent-driven repos (all negative, all self-reported):
  - Dukotah / wazar: https://github.com/Dukotah/cicada3301 . Verdict "OTP-class", 27+ pre-registered rounds, an oracle, plant-and-recover controls. It describes the anti-repeat filter as soft, about 83% suppression.
  - TheronEagle: https://github.com/TheronEagle/liber-primus-research . Not a claimed solution. A periodic AI agent logs nulls. Last session 2026-09-22.
  - Leo-Y-Zhang: https://github.com/Leo-Y-Zhang/LiberPrimusAnalysis . Fingerprint is a chain cipher (c_i = c_{i-1} + nonzero step). Reports autokey excluded.
  - Wulfic ("vibes" repo), r4nd0mD3v3l0p3r/LiberPrimusSolver, jens-wedin/liber-primus (exact repeats vs Smirnov null, OEIS keystreams with key-skip), relikd/LiberPrayground.
- DEF CON 31 talk (Taiiwo et al.): community summary, no computational break. https://media.defcon.org/DEF%20CON%2031/DEF%20CON%2031%20presentations/Taiiwo%20Artorias%20Puck%20TheClockworkBird%20-%20Cracking%20Cicada%203301%20The%20Future%20of%20Collaborative%20Puzzle-Solving.pdf
- I found no Claude, GPT, Gemini or DeepMind attempt on LP documented outside these GitHub logs. (Absence of evidence only: search is US-only and limited.)

### 1.5 LLM-versus-cryptanalysis benchmark literature (2025-2026)

| Work | Finding | Relevance |
|---|---|---|
| CipherBank, arXiv 2504.19093 | 2,358 problems; best LLMs under 50% exact decryption on classical ciphers with 3-shot examples | LLMs are weak at classical decryption without tools |
| Benchmarking LLMs for Cryptanalysis, arXiv 2505.24621 | Near zero exact-match on Vigenere, Playfair, Rail Fence, Bacon; high on Caesar | The prompt lists candidate ciphers, which inflates scores |
| AICrypto, arXiv 2507.09580 | MCQ, CTF and proof tasks; 17 LLMs; models match experts on routine tasks | Not flat-stream decipherment |
| KryptoPilot, arXiv 2601.09129 | Agent with open-world knowledge acquisition; InterCode-CTF 100%, NYU-CTF 56-60%; claims bottleneck is knowledge granularity, not reasoning | Supports tool/knowledge-driven agents, not raw LLM guessing |
| CryptanalysisBench, arXiv 2607.18538 | 191 tasks on real primitives; Claude Opus 4.8, Sonnet 5, Mythos 5, GPT-5.5, GLM-5.2 break 65-86% of Tier-1 (known breaks) and some scaled-down variants; reports a SpoC AEAD key-recovery and a KINDI proof error | Success happens where an automated verifier gives a feedback signal. LP2 has no such oracle |

Sources: https://arxiv.org/abs/2504.19093 , https://arxiv.org/abs/2505.24621 , https://arxiv.org/abs/2507.09580 , https://arxiv.org/abs/2601.09129 , https://arxiv.org/pdf/2607.18538 , https://www.schneier.com/blog/archives/2026/07/measuring-llms-ability-to-perform-cryptanalysis.html . The CryptanalysisBench ID looks odd for its date; check it before citing.

The general pattern: LLMs and agents win when a verifier supplies a loss signal (CTF flags, security games, a language model that scores partial plaintext). They fail when the correct key gives no partial credit.

---

## 2. Verified computational solves and their methods

### 2.1 Zodiac 340 (solved Dec 2020; Oranchak, Blake, Van Eycke)

Facts (a/b): announced 2020-12-11; FBI confirmed. Full account: Blake, "The Solution of the Zodiac Killer's 340-Character Cipher", arXiv 2403.17350 (https://arxiv.org/abs/2403.17350). Unicity analysis: von zur Gathen, IACR ePrint 2021/1620.

Method, reimplementable:
1. Observation: Z340 as a 17 x 20 grid shows a spike in repeated bigram counts at a **pseudo-period 19** (count 37 vs about 20 for random shuffles). Other homophonic test ciphers with known plaintext usually show more repeats than Z340 does, which implied a transposition layer.
2. Blake searched a *family* of transpositions: doubly-periodic proper decimations ("n down, m across", wrapping horizontally and vertically) on the 20 x 17 array. About 650,000 transpositions were tested.
3. Each candidate transposition was scored by running a homophonic-substitution hill-climber on the rearranged text. Tools: AZdecrypt (Van Eycke, FreeBASIC, n-grams up to 8, hill-climbing), zkdecrypto, and Mathematica for stats.
4. One transposition produced fragments ("trying to catch me", "gas chamber"). Those were fixed as anchors, the solver was rerun, and more words appeared. The remaining errors turned out to be the Zodiac's own mistakes in the key.
5. Plaintext: read left to right after a 1,2-decimation transposition, with homophones and misspellings.

Transfer to LP2:
- The *detector* is the useful part. A structural statistic (bigram-repeat spike at a stride) pointed at a transposition. LP2 has been scanned the same way (lags 1-6478, Kasiski, coincidence) and shows nothing but the lag-1 deficit.
- Corollary (c): the doublet deficit is present in **reading order**, so the book's adjacency is the cipher's adjacency. A post-chain transposition would erase the deficit. Any transposition must come *before* the chain. Dukotah and lane D already list "chain applied to a transposed plaintext" as the one transposition surviving.
- Solver search needs readable fragments to bootstrap. A flat stream gives none.

### 2.2 Copiale cipher (Knight, Megyesi, Schaefer, ACL BUCC 2011)

(b/a) About 75,000 symbols; the plaintext is German; Roman and Greek letters were nulls or spaces.
- Method from memory, not re-read from the paper (c): symbol-statistics analysis showed the abstract symbols carry text; homophone groups were identified; decipherment ran with EM against a German character LM; the Oculists/eye symbol led to the historical context.
- Sources: https://en.wikipedia.org/wiki/Copiale_cipher , https://today.usc.edu/usc-scientist-cracks-mysterious-copiale-cipher/
- Transfer: none. Needs non-flat unigrams and many repeated symbols.

### 2.3 Nuhn and Ney line, and neural decipherment

| Paper | Method | Takeaway |
|---|---|---|
| Nuhn, Schamper, Ney, ACL 2013, "Beam Search for Solving Substitution Ciphers" (https://aclanthology.org/P13-1154/) | Beam search over partial key assignments with a 6-gram LM and a future-cost heuristic; 1:1 error 4.13% | Partial key gives partial credit |
| Nuhn and Ney, ACL 2013, "Decipherment Complexity in 1:1 Substitution Ciphers" (https://aclanthology.org/P13-1060/) | Optimal decipherment with a bigram LM is NP-hard; equals the quadratic assignment problem | Complexity bound, not a tool |
| Nuhn et al., EMNLP 2014, "Improved Decipherment of Homophonic Ciphers" | Reduced beams for Zodiac 408 from millions to under 100 | Homophonic only |
| Kambhatla, Mansouri Bigvand, Sarkar, EMNLP 2018 (https://aclanthology.org/D18-1102/) | Beam search scored by a neural LM with rest-cost estimation; Beale improvement | Needs fixed alphabet mapping |
| Aldarrab and May, ACL 2021 (https://arxiv.org/abs/2012.15229) | Seq2seq on synthetic ciphers; multilingual; cracks the Borg cipher from about 256 characters | Simple substitution only |
| Kambhatla et al., EACL 2023 Findings, "Decipherment as Regression" | Recurrence encoding plus Transformer on synthetic homophonic data; real ciphers TNA SP106/5 and BnF-f01 | Homophonic only |
| ALICE, arXiv 2509.07282 | Interpretable encoder; notes general LLMs hallucinate and do not respect bijectivity | |
| Attention-augmented LSTMs, arXiv 2606.05078 (2026) | Supervised on synthetic homophonic ciphertext; near-perfect character accuracy | Supervised, needs known plaintext |

Common limit: all rely on monoalphabetic or homophonic structure and a fitness landscape. A position-varying additive key has no such landscape. (c)

### 2.4 Kryptos K1-K3 and Jim Gillogly

- K1 and K2: Vigenere with keyed alphabets (keywords PALIMPSEST, ABSCISSA). The keyed alphabet of the Quagmire III type is KRYPTOS-based. K3: keyed transposition. K1-K3 were broken in the 1990s by Gillogly (CIA analyst David Stein and others also reported solving) using pencil-and-computer methods. (b, from memory)
- Colossus (https://github.com/stblake/polyalphabetic) reproduces the K2 recovery (Quagmire III, keys KRYPTOS / KOMITET) and an autokey primer recovery.
- Decipher repo (above) classes K1, K2 as Quagmire III-class and K3 as TransMatrix-class.
- K4 status: section 1.2.

### 2.5 Chaocipher (Calof, Hill, Rubin; Lasry, Rubin, Kopal, Wacker)

- Exhibit 5 (Cryptologia 1990 challenge) solved Nov 2013 by ciphertext-only hill climbing plus a dictionary attack (Cryptologia 38(1), 2014).
- Exhibit 6 solved by Lasry, Rubin, Kopal and Wacker, "Cryptanalysis of Chaocipher and solution of Exhibit 6", Cryptologia 40(6), 2016. Method: divide-and-conquer hill climbing using the Index of Coincidence, for in-depth messages (same start state). Rubin's plain annealing had failed.
- Conclusion in the literature: Chaocipher is much weaker than Byrne believed.
- Sources: https://www.tandfonline.com/doi/abs/10.1080/01611194.2015.1091797 , https://www.chaocipher.com/ActualChaocipher/calof-exhibit-6/Chaocipher-Exhibit%206%20article.Calof-Rubin.pdf
- **My sanity check (c, `research/s2/chao.py`):** a 26-letter Chaocipher simulation on about 60,000 letters of English gives IoC x N = 1.000 and a doublet rate of 3.8-4.0%, which matches random (3.85%). So **dynamic-substitution (state-permutation) ciphers produce a flat IoC on English with no key periodicity**, but do *not* by themselves produce a doublet deficit. My implementation may differ slightly from Byrne's; treat it as a rough class check. Raw output: plaintext IoC x N 1.73, doublet 2.18%; Chaocipher seeds 1/2/3: IoC 1.0001/1.0004/1.0001, doublets 3.84/4.02/3.99%.
- Not covered by the repos' additive-chain exclusions, which assume a fixed key stream added to the plaintext. See Lead 2.

### 2.6 Hagelin M-209 and Solitaire (reference points for "feedback with flat statistics")

- M-209: Reeds-Morris-Ritchie (late 1970s) ciphertext-only attack needing about 1,500 letters; Lasry's nested hill-climb/annealing needs about 450-500 letters; solved nearly all published challenges (Barker, Bouchaudy). https://scienceblogs.de/klausis-krypto-kolumne/2019/06/09/can-you-solve-this-original-m-209-ciphertext-from-ww2/ , https://www.bell-labs.com/usr/dmr/www/crypt.html
- Solitaire (Schneier): Crowley (1999) found an **excess** of repeated keystream characters (about 1 in 22.5 rather than 1 in 26); Shiu et al. (arXiv 1909.06300) confirmed this and found rarer triples and quadruples. https://arxiv.org/pdf/1909.06300 . This is the *opposite sign* to LP2's deficit, so Solitaire as published is not a match. A modified deck cipher is not excluded.
- Playfair: no doubled letters *within* each digraph, but pairs are not constrained across digraph boundaries, so its overall doublet deficit is only about half, not 5x. Lasry's 40-letter Playfair record (HistoCrypt 2019) used simulated annealing with hexagram scoring. https://ep.liu.se/ecp/158/010/ecp19158010.pdf

### 2.7 Dorabella, Beale, Unabomber

- Dorabella (87 characters, 24 glyphs): no accepted solution; 2025 music-hypothesis paper (section 1.3).
- Beale: papers 1 and 3 unsolved; Kambhatla 2018 improved Beale part 2 error rates. Forum claims only for 1 and 3.
- "Unabomber" in the task text: I found no cipher-analysis literature on it. Likely a mis-recollection. Treat as unverified.

---

## 3. Attack literature for the LP2 fingerprint

Fingerprint recap (from the brief; reproduced by Dukotah, Leo and lane D): IoC 1.000, lag-1 deficit about 5x (86 observed vs about 447 expected), increments flat except for a hole at zero, geometric gaps, no lag-2+ structure.

### 3.1 Autokey, ciphertext autokey, chaining

- Plaintext autokey (PTAK): key is primer then plaintext. Ciphertext-only attack: for each primer length L, hill-climb the L primer symbols and decode forward, scoring with n-grams. Colossus implements this (recovered primer JAMESHERBERTSANBORNJR on K-style test). https://github.com/stblake/polyalphabetic
- Ciphertext autokey (CTAK, NIST glossary): c_i = p_i + c_{i-L}. Then **p_i = c_i - c_{i-L}** with no key needed beyond the first L symbols. This is a famous weakness and was tested by lane D as lag-L differences.
- For LP2, Dukotah's Campaign X reports that all four autokey variants simulate at 3.3-4.2% doublets, so autokey does not reproduce the deficit.
- The surviving model is a chain over a position-varying flat key, as in the brief. Literature on that exact structure is thin: it is a **differential (delta) encoding of a pad**.

### 3.2 Why keystream-structure attacks lose power here

1. Berlekamp-Massey over GF(p): O(n^2) steps; finds a linear recurrence of order L from 2L symbols; a random sequence has linear complexity about n/2. https://galois.readthedocs.io/en/v0.1.1/api/galois.berlekamp_massey/ . With n = 12,956 one can detect L up to about 6,400.
   - **Already run:** Dukotah round 10 lane L9 (`analysis/round10/L9-randomness/linear_complexity.py`) ran BM over GF(29) and GF(2) on binary mappings: linear complexity is n/2 exactly.
   - Conceptual limit (c): BM only applies when the sequence *is* the generator output. For `plaintext + key` it measures the sum. The anti-repeat filter also inserts and deletes symbols, which breaks linearity. L9 included filter-matched controls for this reason.
2. Truncated-LCG lattice attacks (Frieze-Hastad-Kannan-Lagarias-Shamir 1988; Stern 1987; Boyar 1989; Contini-Shparlinski): recover LCG parameters from high bits of consecutive outputs. Requires seeing raw outputs. Also summarised at https://jia.je/ctf-writeups/misc/lcg.html .
3. MT19937 state recovery: GF(2) linear algebra from 624 full 32-bit outputs (https://www.johndcook.com/blog/2026/05/10/reverse-mersenne-twister/ ); partial or truncated outputs need an SMT solver (symbolic_mersenne_cracker, Z3) or GF(2) libraries (gf2bv). With `randrange` rejection sampling the output/word alignment is lost, so you need extra structure (https://blog.zksecurity.xyz/posts/kalmar2026/ ). Information budget: LP2 holds about 62,900 bits, so a 19,937-bit MT state would be identifiable *if raw output were visible*. With a plaintext layer and an anti-repeat filter it is not.
4. **Key-cancelling linear relations (my power calculation, `research/s2/comb.py`).** If the key follows a linear recurrence, a combination of increments cancels the key and leaves a combination of plaintext symbols. On 265k letters of English (Z26), IoC x N is: unigram 1.716; p_i - p_{i-1}: 1.114; p_i - p_{i-2}: 1.069; p_i - p_{i-3}: 1.044; three-term combinations: 1.004-1.033. At n = 12,956 over 29 symbols the null sd is about 0.066 (sd 0.0137 at n = 265k for Z26). So only the lag-1 two-term relation is near detectable, and no three-term relation is. **Seed-agnostic detection of an LFSR, lagged-Fibonacci or additive-generator key is not feasible from IoC alone at this n.** (c, assuming unigram-plus-bigram English plaintext; a different plaintext changes the numbers.)
5. Unicity distance: with plaintext redundancy of roughly 3 bits per symbol, any key with fewer than about 50-60 bits is fixed by the ciphertext. So a short-seed generator is *uniquely determined* if the right family and seed range is searched. The obstacle is coverage of families, not information. (Dukotah's "OTP-class" correction says the same.)

### 3.3 What a decode-and-score search needs

Success cases (Marmont, Z340, Chaocipher) all use a scorer that rewards partial correctness. For a position-varying keystream there is no partial credit unless the whole key (or a long enough local key window) is right. That is why the community built a skip-aware beam decoder with positive controls, and why scoring needs language-agnostic statistics first (increment IoC, conditional IoC), as in `lp/REPORT.md`.

### 3.4 Randomness-test batteries

- Linear complexity profile (not just the NIST end-point test) is the better detector for structured sequences (IEICE reference below). Expected value for p > 2 is not given in the sources I found, so simulate the null.
- Dukotah L9 used ENT and Dieharder as well. No hits.
- Human-generated "random" sequences (Wagenaar 1972; Rapoport and Budescu 1997, from memory) show too few repeats, too many alternations, and too-uniform short-window counts. Whether this applies here is untested in what I read (section 5, Lead 4).

---

## 4. Off-the-shelf tools

### 4.1 Candidate tools

| Tool | What it does | Fit to LP2 | Run here? |
|---|---|---|---|
| AZdecrypt (https://github.com/doranchak/azdecrypt) | Homophonic, bigram, transposition, sparse polyalphabetic hill-climbers; n-grams 2-8 | Needs non-flat statistics. Only a sanity control on planted ciphers | FreeBASIC; README builds on Windows only; Linux harness is partial. Low priority |
| Colossus (https://github.com/stblake/polyalphabetic, MIT) | Slippery hill-climbing for Vigenere, Quagmire, **Autokey**, Playfair, Bifid, Hill, columnar etc.; combined n-gram, crib, IoC, entropy score | Already covered conceptually by the community autokey sweeps | Unclear language; check README |
| Decipher (https://github.com/matthewdgreen/decipher, GPL-3) | Fingerprinting plus Rust solvers for substitution, homophonic, Vigenere family, Quagmire III, transposition, composite (incl. Zodiac 340 family); optional LLM agent; MCP server | Fingerprint will say "random / OTP-class"; could serve as an independent check | Python 3.11 and Rust; we have cargo |
| ciphersleuth (https://github.com/notPlancha/ciphersleuth) | Stdlib Python; fingerprint (IoC, Kasiski, Friedman, chi-square) and hill-climb/anneal | Same as above | Easy |
| CrypTool 2 | Lasry's analyzers (Playfair, M-209, Enigma, Chaocipher components) | Windows GUI; classical non-flat targets | Not here |
| Zenith / `rwa/HomophonicSubstitutionSolver` | Homophonic solvers with n-gram corpora | Same limits | Low priority |
| Python `galois` (BM over GF(p)) | `berlekamp_massey`; docs say 2n symbols needed | Already done in L9; write the profile loop yourself | pip availability unverified |
| randcrack, symbolic_mersenne_cracker, gf2bv, untwister | MT state recovery (needs raw output) or seed brute force | Need raw generator output | Optional |
| Dukotah repo rig: `analysis/round10/L9-randomness/linear_complexity.py`, `verify_solution.py`, skip-aware beam decoder | Everything above, with positive controls | Primary instrument | Local at `dl/dukotah` |

Local machine: gcc, cargo, Go, numpy 2.5.3 present; scipy missing; 4 cores.

### 4.2 Has anyone applied these to LP?

- AZdecrypt: **no evidence** of any application to unsolved LP2 pages (search found none).
- Berlekamp-Massey / linear complexity: yes, once, in Dukotah L9 (null).
- Hill climbing: relikd's LiberPrayground scores shifts by distance to English; Colossus/Zenith-style tools: no evidence.
- Beam decoding with skips: Dukotah rounds 18-26.
- LLM agents as research drivers: Dukotah, TheronEagle, Leo repos.

### 4.3 What the repos' own notes say has NOT been run (read from `dl/dukotah/liber-primus/handoff/*`, `ELIMINATION-LEDGER.md`)

- The queued **glibc `random()` / PHP `mt_rand` both-twist / S3 2^32 cells** ("25 gated 2^32 cells") never ran; Round 21's L4 is stated as unrun.
- Lane D's own note: "a running-text or PRNG key on the lag-L difference stream E_i = c_i - c_{i-L}, with unknown resync positions" is untested. Periodic keywords on E were excluded.
- Dukotah's RECON-A register listed 16 of 30 leads as `never-run` at the time of Round 12 (A-03, B-04, B-05, D-01, F-01 and others). Some were run later (A-03/F-01 at Round 16). Check `analysis/round10/RECON-A/REGISTER.md` before assuming.
- PCG, xoroshiro, xorshift128+ were excluded "by date" (published 2014+) on the grounds that LP2 appeared in Jan 2014.

---

## 5. Ranked actionable leads

Ranked by my estimate of prior x testability. All priors are low; the overall state of the evidence is "a lot of nulls, with controls". Costs assume the 4-core local machine.

### Lead 1. Fire the queued but unrun generator cells under the existing skip-aware decoder
- Run: glibc `random()` (TYPE_3 additive feedback r[i] = r[i-3] + r[i-31], 31-bit seeds), `rand()`/`srand()` variants, PHP `mt_rand` both twists, Java `java.util.Random` (48-bit LCG, top bits), MSVC `rand()`, using Dukotah's `pair` decoder and `hitfn20` gate. Reducers: `x mod 29`, `floor(x*29/m)`, rejection from 5 bits.
- Signature if it works: decoder score near the positive-control level (about -4.2 to -4.7 vs noise -6.3 to -6.9), at least 95% rune match to a self-consistent chain, and a readable plaintext under the oracle.
- Cost: hours to a day per 2^31-2^32 cell; code exists. Estimated prior: about 1-2% total. This is the one family the literature says is *determined by the data* if the right generator is listed (unicity argument, section 3.2).

### Lead 2. Dynamic-substitution / state-permutation cipher class (Chaocipher family), keyword-initialised
- Why: my simulation shows Chaocipher-type feedback gives IoC 1.000 on English with no periodicity, the same flatness LP2 shows, and is outside the "fixed table" and "additive key stream" exclusions. A keyword-derived starting permutation is enumerable, unlike a free key stream.
- Run: (i) build a family generator on 29 symbols in Gematria order (Chaocipher, Ryabko-style dynamic substitution, a Solitaire-style deck variant). Simulate English runes and compute the six-statistic LP2 fingerprint including doublet rate, conditional IoC and the increment hole at 0. Find out whether any variant, perhaps with a no-repeat rule, reproduces the deficit. (ii) If one does, decrypt the whole stream for starting alphabets generated from the Cicada keyword list (the existing 362,700-word list) and, if there are two alphabets, for keyword pairs from a short list.
- Signature: the *decrypted output* has IoC x N >= 1.4 (language-agnostic) against 1.00 +- 0.07 for noise. Then apply the English/Latin scorers. A planted-key control is easy.
- Cost: about a day of coding; the sweep is minutes to hours in C. Prior about 2%. Lasry et al. needed in-depth messages (shared key) to attack Chaocipher; LP2 has one long stream, so the dictionary route is the only one for a single message.

### Lead 3. Running-text or PRNG key on lag-L difference streams
- Run: lane D's flagged gap. For L = 2..8, decode with key texts (the ~200 text corpus) and with the generators from Lead 1 on E_i = c_i - c_{i-L}, with skip-aware alignment.
- Signature: same decoder gates as Lead 1.
- Cost: hours with the existing corpus and decoder. Prior about 1%. Caveat from lane D: the lag-2 + redraw rewrite is statistically indistinguishable from the plain chain, so success could not be confirmed except by a readable decode.

### Lead 4. Human/dice-generated pad diagnostics (cheap)
- Run: compute lag-2..10 repeat rates, ABA (alternation) rate, distinct-symbol count in sliding windows of 29 and 58, and window chi-square dispersion, all against the filter-matched null (Dukotah's ARFILT control). A shuffled-bag or deck-draw generator, or a person avoiding repeats, leaves signatures there.
- Signature: lag-2/3 deficits or window distinct-count above the iid expectation (about 18.4 distinct of 29 per 29-window for iid).
- Cost: minutes. Prior: low (under 1%), because lane D and Round 6 found "pure lag-1 identity". The point is to close a human-factors branch the cryptanalytic literature does not cover.

### Lead 5. External key information (not computational)
- Every successful historical solve with a flat or hard stream used outside information: Marmont used Tant's partial table, ADFGVX used a known keyword, K4's plaintext came from an archive. For LP2 the analogue is the missing page-56 / "AN END" material. Dukotah judges this unreachable; I found nothing new. Prior: low, testability low.

### Lead 6. Do not spend effort on these (ranked last, with reasons)
- AZdecrypt / Colossus / Decipher as key searchers on the flat stream: no partial-credit landscape, so they will return noise. Use them only as independent cross-checks for planted ciphers.
- Fresh BM / linear-complexity runs: done in L9; my power calculation shows key-cancelling relations are too weak at n = 12,956.
- LLM-only attacks: CipherBank and related benchmarks show weak classical-cipher performance, and nothing in the 2025-26 record shows an LLM solving a flat-stream cipher.
- Transposition search of the Blake type: the deficit in reading order argues against a post-chain transposition.
- MT state recovery: needs raw output; LP2 has plaintext and a filter between.

---

## 6. Source list (URLs seen via search; fetch not possible for most)

Astra / Marmont / ADFGVX:
- https://carter.church/writeups/the-letter-to-marmont/
- https://www.calcalistech.com/ctechnews/article/h1dthf69mg
- https://www.tomshardware.com/tech-industry/artificial-intelligence/chatgpt-6-astra-cracks-217-year-old-napoleonic-code-in-just-six-hours-single-prompt-ai-run-solves-24-rows-of-custom-symbols-from-a-single-image-reveals-lost-troop-orders
- https://www.metafilter.com/214680/Breaking-the-Marmont-Cipher
- https://yellow.com/news/gpt-6-astra-napoleonic-cipher-crack
- https://cybernews.com/ai-news/gpt-6-astra-cracks-100-year-old-wwi-cipher/
- https://hackaday.com/2026/09/20/world-war-i-coded-message-appears-cracked-finally/
- https://runtimewire.com/article/gpt-6-astra-might-have-cracked-a-world-war-i-radio-cipher

Kryptos:
- https://www.paradigm.xyz/writing/kryptos
- https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/
- https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/
- https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/
- https://gist.github.com/atoponce/1cd01f40786ab21af011f0d6257fba0c
- https://kryptos.today/
- https://github.com/keithadler/kryptos/releases/tag/v1.0.0

Cicada / LP:
- https://github.com/Dukotah/cicada3301 (mirrored at https://github.com/wazar/cicada3301)
- https://github.com/TheronEagle/liber-primus-research
- https://github.com/Leo-Y-Zhang/LiberPrimusAnalysis
- https://github.com/jens-wedin/liber-primus
- https://github.com/relikd/LiberPrayground
- https://connortumbleson.com/2024/01/29/ai-cicada-3301/
- https://www.boxentriq.com/guides/cicada-3301-liber-primus
- https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Ideas_and_Suggestions

Historical solves and decipherment papers:
- https://arxiv.org/abs/2403.17350 (Blake, Z340)
- https://eprint.iacr.org/2021/1620 (Z340 unicity)
- https://zodiacrevisited.com/340-solution-summary/
- https://aclanthology.org/P13-1154/ , https://aclanthology.org/P13-1060/ , https://aclanthology.org/D18-1102/
- https://arxiv.org/abs/2012.15229 (Aldarrab and May)
- https://arxiv.org/abs/2509.07282 (ALICE), https://arxiv.org/abs/2606.05078 (LSTM homophonic)
- https://www.tandfonline.com/doi/abs/10.1080/01611194.2015.1091797 (Chaocipher Exhibit 6)
- https://arxiv.org/pdf/1909.06300 (Solitaire analysis)
- https://ep.liu.se/ecp/158/010/ecp19158010.pdf (Lasry Playfair)
- https://arxiv.org/abs/2509.17950 (Dorabella)

Keystream tools and theory:
- https://galois.readthedocs.io/en/v0.1.1/api/galois.berlekamp_massey/
- https://export.arxiv.org/pdf/cs/0607104 (fast BM)
- https://jia.je/ctf-writeups/misc/lcg.html
- https://www.johndcook.com/blog/2026/05/10/reverse-mersenne-twister/
- https://blog.zksecurity.xyz/posts/kalmar2026/
- https://github.com/tna0y/Python-random-module-cracker

Tools:
- https://github.com/doranchak/azdecrypt , https://github.com/stblake/polyalphabetic , https://github.com/matthewdgreen/decipher , https://github.com/notPlancha/ciphersleuth
