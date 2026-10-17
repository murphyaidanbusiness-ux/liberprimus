# scout1_community — what the Cicada 3301 community knows about Liber Primus part 2 (as of 2026-10-09)

Scout: scout1_community. Method: reading only, no cryptanalysis of my own.
Labels: **[V]** verified primary fact, **[C]** community consensus, **[S]** speculation or single-author claim.

## 0. Access notes and corrections to the brief

- **Network limits.** uncovering-cicada.fandom.com, reddit, archive.org, pastebin, steemit, boards.net, 3301archive and boxentriq were blocked by the sandbox egress policy. I did not retry them. GitHub raw files and `github.com` pages worked.
- **Wiki text.** I read the wiki from a full MediaWiki export (89 XML files, 1,763 pages) archived in the local copy of Dukotah/cicada3301, under `corpus/C-community/wikis/uncovering-cicada/`. The latest revisions in it run to 2025-10.
  - I extracted the pages to `scratchpad/research/s1/wiki/`.
  - Original URL form: `https://uncovering-cicada.fandom.com/wiki/<Title>`.
- **Forum text.** The cicada3301.boards.net threads are in the same archive (`corpus/C-community/forums/boards_net_live/`).
- **Discord.** The CicadaSolvers Discord export (109,917 messages, 13 channels, 2019-04-30 to 2026-07-30) came from `https://raw.githubusercontent.com/jaxonkuipers/cicada3301/main/discord.db` (SQLite). It is third-party scraped data, so I treated it as data only.
  - Queries are in `scratchpad/research/s1/scripts/`.
  - Authors are Discord handles. Quotes below are short.
- **The brief's "2016 page 56/57 release" is wrong.** Pages 56 and 57 (scan 73 and 74, "An End" and "Parable") were in the original LP2 release on the 7th onion in spring 2014 (§3). I found no 2016 release of any Liber Primus page. The 2016 event was a single signed message (§2).
- **Page 55 numbering.** The wiki, Wulfic and Dukotah count unsolved LP2 as pages 0–55 (56 unsolved pages). Your "0–54, 12,956 runes" matches Dukotah, Oosterhof and Leo, who put the 12,956 runes in pages 0–54 or 15–70 by scan numbering. The wiki table sums to the same 12,956 for "0–55".
  - Scan 72 (page 55) is almost empty of runes. Oosterhof says 95 runes sit outside his body.
  - Treat page 55 as a naming discrepancy, not a different corpus.
- **Tokenisation trap.** Words wrap across lines and pages.
  - Correct: 2,928 words in the clean body, mean length 4.42 (Oosterhof, `hypotheses/README.md`).
  - Wrong: 3,367, which counts line-wrap fragments. Dukotah's early "language signal" came from this.
  - Use the merged-line tokenisation.

## 1. Uncovering Cicada wiki: Liber Primus

### 1.1 Status per page [V from wiki text]

Source: wiki pages "Liber Primus", "Liber Primus Unsolved Pages" and "How the solved pages of the Liber Primus were solved".

The wiki headline is "17 already solved pages". The scan numbering is LP1 = scans 00–16 (17 pages) and LP2 = scans 17–74 = pages 0–57 (58 pages).

| Section | Scan | Wiki method | Notes |
|---|---|---|---|
| Cover "Liber Primus" and Intus title (scans 00, 02) | 00, 02 | cleartext English | |
| A Warning | 01 | Atbash: `dec' = 28 − dec` | |
| Welcome | 03–04 | Vigenère, key DIVINITY, F-skip | skip indices 48, 74, 84, 132, 159, 160, 250, 421, 443, 465, 514 (11 skips) |
| Some Wisdom (incl. first magic square) | 05 | direct gematria transliteration | |
| Koan 1 | 06–09 | Atbash then +3 | |
| The Loss of Divinity | 10–13 | direct | |
| Koan 2 | 14–15 | Vigenère, key FIRFUMFERENFE, F-skip | skip indices 49, 56 (2 skips) |
| An Instruction (second magic square) | 16 | direct | |
| LP2 pages 0–55 | 17–72 | **UNSOLVED** | |
| An End (p56) | 73 | stream cipher, shift `(prime_i − 1) mod 29`, i.e. φ(prime) | F-skip, exactly one |
| Parable (p57) | 74 | direct | |

**Interrupter and skip convention [V].**
- The interrupter is the rune ᚠ (F, value 0), and only that rune.
- It applies to plaintext F. The wiki states: "multiple ciphers skip over values of F in plaintext… treat the skipped F's as though they do not affect the cipher in any way, i.e. do not go to the next prime/Vigenère key position."
- Not every F is skipped. The skipped positions were found by trial and error and are listed on the wiki.
- The decoder gets the plaintext first and then knows whether to skip. Oosterhof's `interrupter-is-a-plaintext-rule.md` says the same.
- On An End, the 57th rune (index 56 from 0) is an F, the fourth of five F's on the page and the only unencrypted one. Without the skip, prime 269 is consumed there. With the skip, "the next rune is shifted using prime 269" (wiki "PAGE 56").
- In LP2 body ᚠ is flat (458 against 447 expected), so no F-passthrough exists there. Wulfic §10 and Dukotah agree.

**What the wiki says about the unsolved pages [V].**
- Unsolved pages are grouped by marginalia. These are the sections: Cross 0–2, Spirals 3–7, Branches 8–14, Möbius 15–22, Mayfly 23–26, Wing/Tree 27–32, Cuneiform 33–39, Spiral/Branches 40–53, Hollow 54–55.
- Pages 49–51 are a 256-token base-59/60 grid (not runes). Pages 50–51 and the Cuneiform pages 34–39 carry 3301 and 1033 in base 60.
- "Liber Primus pp49-51 data interpreted as base 59, 60, 62 and 64" (a wiki page) tabulates the conversions. Nothing decoded.
- Transcription delimiters: word `-`, clause `.`, paragraph `&`, segment `$`, chapter `§`, line `/`, page `%`.
- The master transcription is rtkd/iddqd.

### 1.2 "Frequency Analysis Unsolved Pages" [V, wiki, 2024-03]

Per-section doublet table (the wiki's own):

| Section | Pages | Runes | IC | Doublets | Rate |
|---|---|---|---|---|---|
| Cross | 0–2 | 729 | 0.988 | 4 | 0.549% |
| Spirals | 3–7 | 1145 | 1.004 | 6 | 0.524% |
| Branches | 8–14 | 1729 | 0.999 | 9 | 0.520% |
| Möbius | 15–22 | 1903 | 1.000 | 10 | 0.525% |
| Mayfly | 23–26 | 1021 | 0.993 | 11 | 1.078% |
| Wing/Tree | 27–32 | 1433 | 0.991 | 13 | 0.907% |
| Cuneiform | 33–39 | 1680 | 0.996 | 12 | 0.714% |
| Spiral/Branches | 40–53 | 3008 | 1.001 | 18 | 0.598% |
| Hollow | 54–55 | 308 | 0.980 | 3 | 0.977% |
| Total | 0–55 | 12956 | 0.999 | **86** | **0.663%** (random 3.45%) |

- **Wiki's interpretation [C]:** "Analysis of bigrams shows the only deviation from random text… This is likely a direct result of the utilized key/cipher." And: "Low doublet counts point traditionally to some form of autoclave or autokey cipher. Alternatively… 3301 created their own cipher or used autokey as well as another encryption method."
- **Wiki's n-gram section [V].**
  - Unique bigrams 840 against 841 random.
  - Repeated trigrams 2508 against 2433.5 ± 31.
  - Repeated quadgrams 127 against 117.2 ± 10.9. These are consistent with random.
- **Wiki's repeat table [V].**
  - It lists exact repeated runs: DJU-BEI (6 runes, starts 6555 and 12950), BMRNM (5448, 12001), OUNWM (6985, 8016), OFLEING (7393, 12385), IMINGYA (10671, 12764).
  - Only DJU-BEI is above chance (expected 6-gram repeats ≈0.14). The 5-gram repeats are about what chance gives (≈4).
  - Oosterhof's `repeated-phrase-dju-bei.md` says the "7th rune ᚫ" often cited belongs to the first rune of the An End page (a cross-boundary coincidence, retracted).
- **Wiki's "Frequency Analysis (Liber Primus)" [V].**
  - Rune frequency is flat (individual pages 1–3%, some above 6%).
  - A "shift clue" in page 0 against page 2 is the only pattern noted, and it is weak.

### 1.3 "Liber Primus Ideas and Suggestions" (the wiki talk page) [V text, mostly C/S content]

This is the earliest community statement of the structure. Key entries:

- **Bigram anomaly.** "Analysis of two grams… shows strange and unexpected low number of rune pairs with two same runes… 86 same rune 2-grams in ~13.000 runes… almost impossible… using standard polyalphabetic cipher with most stream shift keys. This is so far only solid clue."
- **Stream keys that reproduce it.** "We have found some sequences of numbers that when used as a stream key produce low number of same rune 2-grams" (OEIS A061474 and a pastebin sequence).
- **Prior art for the chain/feedback and skip ideas [C].**
  - "We can reproduce similar results with made up enciphering algorithms… Such algorithms include previous rune gematria position or value when calculating shift."
  - "Note that cipher doesnt totally exclude 2 rune repetition, it only makes it happen ~5 times less likely."
  - An "UPDATE: algorithm that generates low same-two bigrams… you can achieve same effect if you jump to (n+1)th number in stream key, or if you reset the key, instead of switching it."
  - So both "chain with previous ciphertext rune" and "advance the key when output would repeat" were on the wiki by about 2016–2018. Neither was developed into a solution there.
- **89 repeated pairs [S].** One author counts 89 repeated-rune pairs (Fibonacci prime), with GP sum 4337 (twin prime), and a suggestive "WWW" near the end.
- **Outguess data [C].**
  - "EDIT_3… FORGET THE OUTGUESS DATA… The outguess data is a coincidence and the similar headers it gives is due to the fact that all the pages are alike with a lot of whitespace." Someone reproduced the artefact on synthetic pages.
  - Header and footer overlap, each file ≈58 kB, one entry says it "often outputs false positive outputs".
  - The 2025 wiki stub "Liber Primus Updates 2025" still claims all pages have outguess data (S).
- **Other entries.**
  - Cicada_Breaker (word search by pattern).
  - A bijection argument for brute force.
  - Numerology about 58 and 57.
  - A Cuneiform base-60 reading, 17·60+13 = 1033 and 55·60+1 = 3301.
  - Repeated "DJU BEI" (first noted on this page).
  - A shuffled-page "map" idea.
  - A list of untried ideas: use outguess data to relocate runes, count spaces as runes, first-rune shifts.

### 1.4 "Cicada Part 9 – Attempts" [V]

- Friedman key-size scans for blocks of 50–5000 runes gave max IoC < 1.15. The page concludes it is "not likely any cyclicly-repeating polyalphabetic cipher".
- Autokey with key length 3–20 (practicalcryptography stochastic script) found nothing.
- Hill cipher with the 2×2 and 4×4 matrices from the base-60 numbers found nothing.
- ELA of the JPGs found nothing (up to image 4).

### 1.5 Did anyone already notice word lengths have no sequential order, or that sentence marks are random? **Yes, but only in 2026.**

The wiki pre-2025 has nothing. The first appearances are:

1. **mae3301 (Discord #54-55, 2026-05-30).**
   - "The word length auto-correlation of almost all other sections was close to 0, which suggests unstructured lists of words."
   - Section 54–55 is the exception: its autocorrelation "is similar to that of Runenglish… a piece of writing not a bunch of words."
   - On 2026-07-20 she calls word lengths "the strongest evidence for a generation of random texts."
2. **Oosterhof (micheloosterhof/aldegonde, `hypotheses/word-length-keystream-and-boundaries.md`, June–Aug 2026) [S, careful and reproducible].**
   - Word-length autocorrelation, lags 1–6, unsolved (n=2953): −0.007, +0.018, −0.017, +0.012, +0.024, −0.018. All flat.
   - English prose is +0.05 to +0.06 at every lag. The solved pages alternate (−0.086 at lag 1, +0.092 at lag 2).
   - Register-matched test (solved against unsolved, lags 1–2): p≈0.036. He calls it "not yet a finding" because the short-word deficit explains the flatness.
   - **Short-word deficit.** 2-rune words are 15.9% against 24.2% in solved text (z≈−4.9; 50k-word English reference: ratio 0.66, z≈−10). It is confined to length 2. Every section shows it and it does not drift. Oosterhof reads it as a "THE" shortage or merging.
   - **Sentence marks fail English semantics.**
     - Unsolved sentence-final word length is 4.19 against 4.42 overall (z=−1.21). Solved is 5.56 (z=+7.06).
     - Contrast z=+5.9. Direction-independent: the reversed reading also fails.
   - **Layout coupling.** 19.9% of `.` marks sit at line ends against 3.7% baseline for `-` (z=+11.3). The solved pages show the same (26.7% against 5.5%).
   - **Not decorative.** Typeset (anti-aliased) quotation marks align with `.` marks: 8 of 14 quote-span edges land on one against 0.7 expected (p=1.5e-7). Marks are depleted inside quote spans. His own conclusion: the marks are not English sentence ends, but they delimit something the plaintext respects.
   - Mean sentence length is 17–20 words against 8–9 in the solved pages.
   - The word-length sequence by itself carries nothing: the keystream is not a function of local length context (bucket test, all z within ±1).
3. **mortlach (Discord, 2026-07-23).** "i think the general word lengths are fine – but you can always check these things in more detail. sentence lengths are certainly odd… too many long ones."
4. **iglooparty (2026-07-23/24).** Asked whether anyone had measured word-length bigrams: "in English adjacent word lengths are not independent events. If they are for the LP that's a sign something is screwy/cooked up." He also said a transposition that moves the delimiters is ruled out by the length match: "It is not the case… that the LP is encrypted with a transposition step that also transposes punctuation."
   - **The case where only the words move was not argued.** iglooparty's own line is the case where the delimiters move with the text. He did not separate the word-only case.
5. **Dukotah/cicada3301 (`research/FRESH-ANGLES-2026-08.md`, DEAD_ENDS R9-LENGTH).**
   - The word-length marginal matches English (KS 0.050 against solved LP1 English).
   - Their earlier claim of a "word-length language signal" was line-wrap typography. They closed the "word-length excess" lead.
   - They report a clause-final length effect (p=0.039) that Oosterhof's data contradicts.

**Bottom line for the brief.** Word-length marginals are English-like (excess 2-rune deficit); there is no sequential structure; sentence marks do not behave like English sentence marks; marks are layout-coupled and nest with quotes. All of this is already known to the 2026 community. The word-scramble idea ("list of words", "words transposed") appears in mae3301's phrase "unstructured lists of words" but I found no one who has tested it as a hypothesis (§5).

### 1.6 "Chain" and "autokey" on the wiki

- The wiki frames the doublet deficit as pointing to autokey/"autoclave" (§1.2).
- Oosterhof, `ciphertext-autokey.md`: **disproved for keyless ciphertext autokey** (`C[i] = f(P[i], C[i-1])`) by the preceding-rune split test. Grouping C[i] by C[i−1] must yield permuted-plaintext IoC; he measures mean group IoC 0.0354 (random). Depth 1–8 lags are also flat. A flat keyed term defeats this test, so the verdict covers only the keyless case.
- Also disproved there: accumulator autokey, plaintext autokey, multi-layer autokey, autokey with keyword, and "dual autokey lag1+lag5" (the last was closed in Aug 2026).

## 2. PGP-signed Cicada messages

Key: RSA, UID "Cicada 3301 (845145127)", fingerprint `6D85 4CD7 9333 22A6 01C3 286D 181F 01E5 7A35 090F`, short ID `7A35090F`. Same key 2012–2017 [V from the signature outputs reproduced in scream314/cicada3301 and the wiki].

| Date (signature time) | How released | Content relevant to LP | Hash | Community conclusion |
|---|---|---|---|---|
| 2014-01-06 → Feb 2014 | OutGuess payloads in the LP1 images | cover and `00–02`: signed 512-hex strings; `03`: "Let the text guide you" plus a hex JPEG; `08`: "For those who have fallen behind" (columnar transposition, period 7, key 1736254, decodes to "TO BELIEVE TRUTH IS TO DESTROY POSSIBILITY" plus the next onion address); `10–13`: instructions to build a Tor hidden service and post three magic squares | SHA1 | All solved in 2014 [V] |
| 2014-05-02 | `message.txt.asc` POSTed to every hidden service registered on onion 6 | "Hello. Your enlightenment awaits you" and the 7th onion address. Whitespace spells the primes 2,3,5,7,11,13,17,23,29,31,37 (19 missing) | SHA1 | The 7th onion served the 58 LP2 JPGs [V] |
| 2015-07-28 07:12 | Pastebin, linked from Twitter | Denies Planned Parenthood hack. Not LP-related. Whitespace 5-3-2-5-7 | SHA1 | Same key, so authentic [C] |
| **2016-01-01 00:01:07 UTC** (Dec 31 2015, 7:01 PM EST) | Tweet 2016-01-05, image 563×569, OutGuess | "Hello. The path lies empty; epiphany seeks the devoted. Liber Primus is the way. Its words are the map, their meaning is the road, and their numbers are the direction. Seek and you will be found. Good luck. 3301. Beware false paths. Verify OpenPGP 7A35090F." | SHA1 | See below |
| **2017-04-04 23:23 GMT** | Pastebin `yEiTHhvF`, found 2017-04-29 by user psilynt1 in #cicadasolvers by searching "7A35090F" | "Beware false paths. Always verify PGP signature from 7A35090F. 3301" | **SHA512**, `Version: CicadaPG v.3301` | Last verified message [C]. 113 views when found. |

**Community reading of 2016 [C/S].**
- "Numbers are the direction" is read as: use gematria values (GP sums), not letter order.
- 7he5haman's GP-sum analysis: sentences 1–3, sentence 4 and the remainder are each 59 runes (with the F moved). Their GP sums (2999, 2819, 2581) fit prime and Fibonacci-index patterns, and the 2017 message (45 runes) sums to 2131. This is [S] pattern-finding with weak controls.
- mortlach (boards, 2016-09): three options for progress — (1) find the hashed page first ("until you do all decrypting efforts are pointless"), (2) decrypt, (3) a missed hidden message.
- "Path lies empty" is read as: no further puzzle exists beyond the book.

**Community reading of 2017 [C].** A reminder to check signatures. Other pastebin-posted "messages" after it are fakes.

**Key 7A35090F status.**
- No revocation or replacement known [V].
- Searching the key ID on pastebin found the 2017 message. In Nov 2024, `.ayca22` scanned IPv4 for pages containing a PGP signed block; none was from Cicada [V, Discord].
- There is **no verified message after 2017-04-04** [C]. Discord, Feb 2025 (iglooparty): "Latest verified contact." Server rule 8 requires independent verification for any claim of "a new message by 3301".
- A March 2026 ResearchGate preprint, "On the Forgery of Cicada 3301 PGP Signatures via SHA-1 Collision Attacks", argues that SHA-1 signed messages cannot be authenticated. I could only see a search snippet. Treat as [S].

## 3. Release history

The 2014 sequence below is condensed from scream314/cicada3301 `2014.md`, `liber_primus.md` and `pages_and_ciphers.md`, and the wiki "What Happened Liber Primus (Post 2014)".

| Date | Event |
|---|---|
| 2014-01-06 ≈07:30 GMT | Tweet with image; OutGuess; a signed message points to onion 1 `auqgnxjtvdbll3pv.onion` (book cipher on Emerson's *Self-Reliance*). Onion 1 serves `1033.jpg` = the cover. |
| Jan 2014 | Onion 2 (`cu343l33nqaekrnw`): a string that grows by 2 characters every few minutes for ≈23 hours; XOR and transposition lead to onion 3. Its JPGs become scans 00–02. |
| 2014-01-06 → 11 | Onion 3 (`fv7lyucmeozzd5j4`): Apache server-status leak holds hex with the images **05** (Jan 6) and **03, 04** (Jan 11, 10:07 UTC). The 03/04 runes were Vigenère-encoded (DIVINITY). |
| 2014-01-29 | Onion 4 (`avowyfgl5lkzfj3n`) comes back as a signed hex gzip (internal timestamp Jan 24). It holds **06–09** and a columnar transposition clue to onion 5. |
| 2014-01-31 | Onion 5 (`q4utgdi2n4m4uim5`): an MP3 titled **"Interconnectedness"** (artist 3301, 277.133 s, Gematria Primus sum 772), a Goya portrait with hidden data, and a book cipher on Hofstadter. The MP3 hides the three magic squares (OpenPuff, password `33011033`). |
| Jan–Feb 2014 | Onion 6 (`ut3qtzbrvs7dtvzp`): four JPGs **10–13** (Loss of Divinity). The signed message asks solvers for three magic squares and a Tor hidden service. Submitting valid squares and a URL returned **107.jpg, 167.jpg, 229.jpg** = scans **14, 15, 16**. Onion down 2014-02-11. |
| **2014-04-02 → 2014-05-02** | Onion 7 `ky2khlqdf7qdznac.onion` (thttpd 2.25b, last-modified 2014-04-02 08:33:19 GMT, announced via the 2014-05-02 signed message). `index.html` lists `0.jpg … 57.jpg`: all 58 **LP2** pages, including pages 56 and 57. Michel Oosterhof's repo preserves these 58 blobs, and the maintainer says he downloaded them directly from the onion. |
| 2015-07-28 | Planned Parenthood message (no LP content). |
| 2016-01-05 | Tweeted "path lies empty" message. |
| 2017-04-04 | Last signed message (found 2017-04-29). |

**Package boundary [V, ZzNible].** Scans 17–74 are byte-identical to the preserved onion 7 `0.jpg–57.jpg` with a +17 offset. Scans 00–16 come from earlier onions. Several physical glyph regimes change at exactly the 16→17 boundary (red terminal glyph form; isolated two-dot glyph present only before).

**Pages 56 and 57.** They were part of the original May 2014 release. The wiki says page 56 "was decrypted using a running stream of the Totient function, and a modulo of 29" and has a Python script link. I found no source giving a solving date or solver. The DEF CON 31 slides (Aug 2023) say "two pages were solved immediately".

**Extra material released with pages [V unless stated].**
- OutGuess payloads on LP1 pages as above (all solved).
- On LP2 images, default-key OutGuess returns ≈58.2 kB of garbage on several pages (17, 21, 43, 65, 68–71 per Wulfic). [C] artefact (reproduced on synthetic pages). Leo (2026-09) re-ran OutGuess on all 75 images and recovers only the known 2014 payloads. ZzNible rejects the 58,152-byte default-key output.
- Numeric artefacts in the pages themselves, all unresolved:
  - **Page 15 (scan 32): 4×4 grid** `3258 3222 3152 3038 / 3278 3299 3298 2838 / 3288 3294 3296 2472 / 4516 1206 708 1820`. 3301 − x gives primes 43…; their prime indices are Fibonacci numbers laid out as a spiral. The two bottom-left cells use 3301+x. [C] This is a genuine structural pattern. Its function is unknown.
  - **Pages 49–51 (scans 66–68): 256-token base-60 grid** (32×8 tokens, first character 0–4, last character from 60 symbols, maximum `4F` = 255). Only 161 unique tokens (noxxprojects, May 2026). Not a permutation of 0–255. 2026 tests: Wulfic stages I, M, N, X, Y (full-grid keys, 256-byte readings, running-key search over on-disk bytes) all null. A Jan 2026 Discord reading maps tokens to words of the solved pages (joaquinserna); nobody has validated it.
  - **Magic squares** on two LP1 pages (sums 3301 and 1033) with words in some cells ("shadows, buffers, void, carnal, obscura, mobius, analog, mournful, aethereal, cabal"). Their use as a key is unproven.
  - 2012 "P.S." 131-digit number, 2013 telnet "primes" list (primes 73–1223 missing), 2013 cookies `167`/`761`: never used. Wulfic's compiled doc lists them as ideas; I did not find a published exhaustive test.

## 4. The deep-web page: SHA-512 `36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4` (128 hex chars)

Source: wiki "PAGE 56", the Discord #deep-web-hash channel (13,840 messages), crashdemons/Cicada-DWH-HashcatAttempts, Leo's README.

- The text (page 56): "AN END. Within the deep web there exists a page that hashes to [hex]. It is the duty of every pilgrim to seek out this page."
- **Algorithm not stated [V].** The wiki lists SHA-512, BLAKE-512 and BLAKE2b as "potential candidates". Taiiwo (Oct 2020) lists 14 hashes with 512-bit output (BLAKE-512, BLAKE2b, ECOH, FSB, Grøstl, JH, LSH, MD6, SHA-512, SHA3-512, Spectral Hash, Streebog, SWIFFT, Whirlpool). The best argument for SHA-512 [C]: the 2017 message was signed with SHA512 (tz18).
- **What is hashed is unknown.** A URL, an image, a page of HTML, a file, a DHT identifier (Freenet, GNUnet, IPFS multihash, I2P)? The community reading of "page" is open (ayca22, 2024: "page" could be an image or a book page).
- **Searches attempted [V that they were run; none found it]:**
  - Old: SHA1/SHA512 of every outguessed payload (and character-by-character combinations).
  - Taiiwo (2021-03): subtracting `(prime − 1)` from the digits of the hash itself, with and without an F-skip.
  - hashcat-style brute force: all byte strings of length 1–5 (about hours on a GTX 1080) and 6–7 feasible; US phone numbers; domain names `www.[a-z]{1,8}.com`; across SHA-512, BLAKE2b, SHA3-512, Streebog, Whirlpool, crc32 (crashdemons). 0 matches.
  - ayca22: all 4.3 billion IPv4 addresses, HTTPS and HTTP, plus reverse DNS, for 2+ months; 2012's P.S. number and the cookies; nothing.
  - cmbsolver (C# tool): all 2014 hex strings, the base-60 values, concatenations, 18 algorithm families; nothing.
  - tz18 converted the hash to IPFS multihash form; nothing found.
  - Leo (2026-09): the hash matches none of about 697,000 archive candidates and none of the no-key payloads.
  - Dukotah: all hashing of 3,400 seeds and similar.
  - The TheronEagle and Pitchfork repos list many "onion/IPFS/Freenet/I2P/GNUnet locator" families as non-productive (the list itself is withheld).
- **Candidates [S, all unverified].** None verified. Ideas voiced in Discord: the hashed object is a "missing 59th page" (slacker3), a challenge hash (knightoftheidotic, with no basis), the key to the other pages.
- **Community attitude [C].** Cannot be brute-forced without knowing the input form. cmbsolver (Dec 2025): "Your best guess is to solve the rest of the LP2 and figure it out from there." mortlach considered "maybe the deep-web page has a one-time pad on it" (Aug 2016, boards).
- The wiki notes the 2013 Instar Emergence MP3 ID3 tag number 1,595,277,641 = product of the GP sums of the Parable's three lines (1259·1031·1229). So Parable (page 57) was pre-announced in 2013.

## 5. Community attack history

### 5.1 Infrastructure and big efforts

- **2014:** Transcription and analysis by rtkd (`idkfa`, `iddqd`: master transcription, all outguess outputs `lp_outguessed/`, translation and key analysis folders), the Uncovering Cicada wiki, /x/ threads, the IRC channel #cicadasolvers (later defunct).
  - Eva Valkiriya's page-56 blog post, titan pad transcription, remlong/cicada-runes numeric transcript.
- **2016–2018:** cicada3301.boards.net (mortlach is administrator).
  - Threads on combining runes, modular exponentiation ciphers, a Pi-count spreadsheet, a "Why is solving hard?" essay (2016-09), "Red Runes Key Search" code (2018-07), and "Hangman" and word n-gram tools.
  - The Red Runes code generates keys for many cribs under simple arithmetic ops and a recursive method. It found 491 keys consistent with a shifted prime sequence and 285 with Fibonacci.
- **2019–:** the CicadaSolvers Discord (channels per section, `3301.gq` mirrors, Taiiwo's `cicada-library`, relikd/LiberPrayground with its interrupt database and OEIS checker, mortlach's tools).
  - **DEF CON 31 (Aug 2023):** Taiiwo, Artorias, Puck, TheClockworkBird, "Cracking Cicada 3301: The Future of Collaborative Puzzle-Solving" [S from search snippets].
  - cicada-solvers GitHub org: 55 repositories, mostly forks (e.g. `aldegonde`, `neuroretransmit-cicada`, `cmbcidada3301`, `libergo`, `lp-decrypter`, `LiberPrimusSolver`, `lphelper`, `3301tools`).
- **2020-12:** mortlach pins that **54–55** are a short (308-rune) probably self-contained section and a place where "practically anything is in play apart from simple substitutions". It has a red 2-word header (1 rune + 8 runes) with a likely first plaintext 'A'. This section has been the focal point since.
  - July 2025 call in #solving-lp-general: "I need all hands on deck in #54-55-jpg".
- **2026 wave:** public AI-assisted repos: Leo-Y-Zhang/LiberPrimusAnalysis, Dukotah/cicada3301 (172-row ledger and "OTP-class" verdict), TheronEagle/liber-primus-research, Pitchfork-and-Torch/liber-research, ZzNible findings, Wulfic/Cicada3301-Liber_Primus (reproducible tests), micheloosterhof/aldegonde hypotheses (the most thorough public ledger). All report null results. The Discord rule says extraordinary claims need independent verification.

### 5.2 Classes of cipher tried (public record) [V that they were tried]

Periodic Vigenère/Beaufort/Quagmire (key lengths up to ~6400; Friedman, Kasiski; 314M-key Quagmire sweep); mono- and homophonic substitution; Hill; Playfair/bifid/fractionation; plaintext, ciphertext, accumulator and multi-layer autokey; Atbash combinations; affine and multiplicative ops; Fibonacci/prime/φ/OEIS/Fibonacci-mod-29 streams (period 14); LFSR; running keys from literature (Self-Reliance, Liber AL, Mabinogion and others); XOR with Cicada files; hash-derived and PRNG keys; columnar and route transposition (widths 2–40 in Dukotah); steganography (OutGuess, ELA, colour channels); numerology; word-length-keyed schedules; base-60 grid keys; cribbing (circumference, A/I, 'the'); genetic/hill-climbing solvers; AI agents.

### 5.3 Claimed partial solves and why rejected

- **Echo446Ghq "Cracked Third Puzzle"** (the 131-digit P.S. number via "every 5th digit"): arbitrary transforms, no cryptographic basis (Wulfic's write-up) [C].
- **2retooz270703 "AS I GO, THE WEATHER TURNS COLD"** (27×27 grid, totient/Möbius key phase): key chosen post hoc and no independent verification; I found no community endorsement [S].
- **vionorromanov "full translation" 00–74, leorahross "full translation", johnvteixido "25,000-rune geometric payload in the ink"** (repo descriptions only): unverified, treat as noise [S].
- **noxxprojects, page 53 "KNOWLEDGE IS…"** (2026-05-28): mortlach — "if you pick any plaintext, you can always calculate a key that makes it fit, you now need to justify the key."
- **iamlupo OEIS-guided "ABSOLUTE TRUTHS" for pages 17–19** (2026-06): partial, one 8-rune crib; no verification.
- **apoptosis_reich2741, collision-skip decoder and "prime-sentence statistic"** (2026-06-24): retracted the certainty after a reviewer noted that additive+skip would leave in-phase key fragments that are not observed.
- **Dukotah's own false positives:** the word-length "language" signal (line-wrap), "surviving English phonotactics" (sample noise).

### 5.4 Has anyone tested chain / ciphertext-feedback ciphers?

**Yes, extensively, and the community's working hypothesis is essentially this.**

- **mortlach (boards, 2016-08).** "The single anomalous fact about the runes… an astronomically low number of double runes (~10^-69)… the runes have a memory of the preceding rune. No-one has found any other significant correlations… make your algorithm have a memory of the previously encoded rune… a very simple recursive algorithm can exactly generate the distributions we see." He also warned against "fine tuning" a specific key.
- **mortlach 2024–2026 (Discord).** The "add previous rune" trick is "basically a given", "well-motivated through Fibonacci and self-referential themes as well as stats". "Most popular candidate for the last encryption step is probably add previous rune." Subtracting the previous ciphertext rune raised the hit rate of simpler decryptions.
  - Working model among mortlach, scott.g., iglooparty, kylestanley, 7he5haman: *inner transform (period-13?) + outer ciphertext-autokey step*, analysed in the delta stream `D[n] = C[n] − C[n−1]`.
  - Evidence for 13 (section 54–55, 308 runes): S1(13) = 1.72 against 1.0–1.2 for neighbouring periods. A matched null that includes interrupter tuning gives about 3σ (p≈0.016). A holdout test with Fisher combination was run. Mortlach (2025-11-05) concedes the tuned interrupters may just exploit noise.
  - A 2025-11 consensus line: "the clearest thing the community has discovered as potential progress in the past 10 years" (kylestanley, the enthusiast). scott.g. says only that it is "not a random event".
  - Interrupters in the delta stream: 6 candidate positions (v=1 removals), e.g. positions 62, 73, 109, 168, 180, 306 in scott.g.'s optimiser run.
- **Oosterhof (aldegonde):**
  - Plain ciphertext autokey, accumulator autokey, plaintext autokey, multi-layer, dual lag-1/lag-5: all disproved (reasoning in §1.6).
  - The surviving family is a **word-clocked progressive substitution with a doublet-dodge rule**:
    - Rule: when the emission would repeat the previous rune, the letter clock skips one extra step.
    - Result: a doublet survives only when the plaintext double sits on a fixed point of the step permutation.
    - Fit: d1 within words 0.0009 with no tuned diagonal (observed 0.0063).
    - It also suppresses the seam doublet rate like the within-word rate.
    - It is unresolved ("most economical proposal").
  - Observed acceptance probability "exactly 1/5": the doublet rate fits (1/5)×(1/29) with z=−0.36.
- **Leo**: the chain cipher — non-zero flat step — reproduces the fingerprint (your own conclusion).
- **Dukotah**: "soft anti-repeat filter, p_keep≈0.18, ≈83% suppression", OTP-class; "plaintext and ciphertext autokey positively refuted"; first-difference/integral inversion in the pre-ledger dead ends.

### 5.5 'Sampling without replacement' key generators

**I found no community document that tests this.** Nearest relatives:
- "Self-avoiding" keystream: Dukotah H2 (self-avoiding LCG walk) was killed pre-execution as unfalsifiable.
- Collision-skip and no-repeat output filters: wiki Ideas page, mortlach, Oosterhof `stream-cipher-no-repeat.md` (reformulated, open), Dukotah's constrained decoders, apoptosis_reich2741.
- Deck or shuffle ideas: none beyond gonflynn's 2019 boards question about shuffling letters between words; mortlach: "this is possible, but there must also be an encryption stage as the rune frequencies are so flat".
- Oosterhof notes that doublet-avoidance gives permanent clock drift (his clock-drift file).

### 5.6 Transposition of words

- **Rune-level** columnar/route/rail transposition was tested (Dukotah: widths 2–40 re-measured; the file order is the unique global doublet minimum 0.0067. Oosterhof: "lines are not cipher units", "no block partition").
- **Word-level** transposition has no dedicated test I could find. What exists:
  - 7he5haman (2026-02-24): "the community… resists this idea because (1) there's no precedent, (2) there appears to be no hints towards it, (3) it would add another layer." There were "at least two transposition puzzles in the 2014 puzzle", and "the moving F in the 2016-17 message solution could be viewed as a hint".
  - iglooparty (2026-07-15): a transposition that also moves the punctuation would be "the worst case"; the word-length match argues against it.
  - mortlach (2020): sections might be read in reverse order; mae3301: "unstructured lists of words".
  - Oosterhof (`word-length-keystream-and-boundaries.md`): all the sequential structure in the visible metadata is absent, "which would be expected if the boundaries were placed to match a length histogram without copying English word order" — a statement about *boundaries*, not about words moving.
  - Nothing tests "the words are real English words in scrambled order".

## 6. Leading hypotheses now (Oct 2026) and live efforts

1. **Chain/feedback final step plus unknown inner cipher** [C among the Discord core group, 2016→2026]. Evidence: doublet deficit; the delta-stream k=13 signal in 54–55 (p≈0.016 after tuning, unreplicated elsewhere). Counter: keyless variants are disproved; inner cipher unknown.
2. **Structured walk with word clocking and a doublet-dodge** [S, Oosterhof, "plausible"]. Evidence: within-word lag-5 echo (his p≈0.001; ZzNible preregistered max-|Z| family p=0.0086; 102/2073 = 4.92% against 3.45%; 9 XY···XY repeats against 1.5; concentrated on rune S); seam doublet suppression equals within-word; DJU-BEI state return. Counter: unresolved d5 miss; no decryption.
3. **OTP-class unpublished pad, key not derivable** [S, Dukotah, partly mortlach 2016]. Evidence: IoC 1.000, entropy 4.8565 against 4.858, no running key or seed found. This claim is itself negative evidence only.
4. **Text is generated filler with decorative segmentation** [S, mae3301, iglooparty's "worst case"]. Evidence: flat word-length autocorrelation, sentence marks failing English semantics. Counter: marks are layout- and quote-coupled, and the English-like length marginal is hard to get by accident. 54–55 is claimed as the exception.
5. **54–55 is a separate short section** [C]. The community's focus. No decryption.
6. **Hints in the 2016/2017 messages (GP sums with Fibonacci/prime structure) describe the method** [S, 7he5haman]. Unfalsifiable so far.
7. **Pages 49–51 grid, magic squares, page-15 Fibonacci grid are key material** [S]. All specific tests null. Nothing falsifies "used as parameters".
8. **Find the deep-web page first** [S, mortlach 2016 option 1]. No traction in 12 years.

**Ongoing coordinated efforts we can plug into:**
- CicadaSolvers Discord (invite `https://discord.com/invite/eMmeaA9` per Wulfic; channels #solving-lp-general, #54-55-jpg, #deep-web-hash). Rules: reproducible claims; mortlach and the staff review; the "community solving tool" request (scott.g.: a standard file format for cipher steps plus a replay tool).
- scott.g.'s RuneDecrypterPrime (GitHub, mortlach's "RDP" language models forward/reverse encoded).
- `micheloosterhof/aldegonde` `hypotheses/` (issues welcome; AGENTS.md describes the format; observations have scripts).
- TheronEagle/liber-primus-research, Dukotah/cicada3301 (issues open; a "CicadaSolvers-accepted reproducible page solve" or a new 7A35090F release would reopen).
- GitHub issue tracker conventions in all of these ask for a positive control.

## 7. Actionable leads (ranked by prior × testability)

1. **Check whether the segmentation is cipher-relevant (within-word lag-5 and seam tests) on our own data.**
   - Statistic: within-word equality at distance 5 (reported 102/2073 = 4.92% against 3.45%; independent p 0.0086–0.001); cross-word d5 at chance; seam doublet rate against within-word doublet rate (reported ratio about 1.25); concentration on rune S.
   - Use the merged-line tokenisation (2,928 words). Control for the doublet-suppressed null (a uniform null overstates everything: Oosterhof's repeated "doublet trap").
   - If it replicates, word boundaries are real ciphertext-side structure. That kills "layout is decoration" and favours word-clocked state or a word-level scramble.
2. **Test the "bag of words in scrambled order" model explicitly and change the scoring.**
   - Predictions to check: word-length autocorrelation flat at all lags (observed), sentence-final length unrelated to `.` (observed), the doublet rule still acting across seams (observed, if the chain runs after the scramble), quote spans still aligned with `.` marks (observed), 2-rune deficit as a register fact.
   - If words are real but order is not, every running-text n-gram or sentence-level scorer is blind. Switch to per-word dictionary hit rates, rune-in-word trigrams, and word-length-pattern cribs (DJU-BEI context 2,[3,3],2; the 13- and 14-rune words; A/I one-rune words).
   - Untested in the public record, so no one else is competing.
3. **Delta-stream periodicity replication, on every section with a proper null.**
   - Compute `D = C[n] − C[n−1] mod 29` per section and run IoC-by-column for k = 2..64, with a null that preserves the `D ≠ 0` deficit (a uniform null misleads).
   - Replicate or refute the 54–55 k=13 peak (S1 = 1.72, p≈0.016 after tuning) without interrupter tuning, then test whether any other section shows it. Community says no.
   - This is the community's actual "inner periodic cipher + outer add-previous-rune" test. Our raw-stream "no periodicity" finding does not by itself cover it, unless the delta test was already run.
4. **Generator-seed search from the release artefacts, using the 1/5-acceptance structure.**
   - Seeds and parameters: page-15 grid (3301 − x, Fibonacci spiral), the 256-token grid, the magic squares' words and numbers, the missing-prime list (73–1223), the P.S. number, 2016/2017 GP sums.
   - Run them as LFSR/LCG/PRNG parameters and as step-permutation constructions. Oosterhof's `g-from-5x5-grid`, `magic-square-grid-key` (undecided) and Wulfic's stages cover only some of it.
   - Prior is low, but nothing in the record rules out using these as seeds rather than as keys.
5. **Section 54–55 end-to-end (308 runes, 66 words, header 'A' + 8-rune noun, long 13-rune word).**
   - Short enough for exhaustive searches under the chain-plus-skip model. The community has the best cribs here (lanfear6881 `54_cribbing`, ≈7,000 noun candidates).
   - Run our chain/skip decoder with word-level scoring (lead 2) on this section only, and share null results with the Discord group.
6. **Use the typeset quote and apostrophe anchors.** Quote and apostrophe glyphs are anti-aliased and unencrypted: 7 quote spans, 4 contraction sites (pages 4, 6, 7, 21, 22, 35, 40–43, 53). Oosterhof gives p≈1.2e-4 for the nesting. Treat them as known structural landmarks for the scramble test (lead 2) and as small cribs for the key-generator tests.
7. **Coordinate rather than duplicate.**
   - Open an issue or PR on `micheloosterhof/aldegonde` (hypotheses format) and post our ledger in #solving-lp-general. Offer the doublet-gap geometry and the MT-seed null.
   - Ask mortlach whether the delta-stream tuning data and the "RDP" forward/reverse language models are shareable.
   - Their "1/5 acceptance", "skip additive+skip leaves fragments" and "OTP-class" claims overlap with ours; cross-checking the 5.2x figure is cheap.
8. **Deep-web hash: no new angle.** If any effort is spent, it is hash-of-file candidates for each of the 58 LP2 JPGs and the original (pre-Imgur) files under SHA-512, BLAKE2b, Whirlpool, SHA3, with the other 2014 binaries. Leo's 697k-candidate sweep makes a miss likely. Algorithm uncertainty remains (SHA-512 favoured because 2017 used it).

**Already-dead ends not to repeat (community record):** periodic Vigenère of any period ≤ ~6400 with or without F interrupts; keyless ciphertext/plaintext/accumulator autokey; OEIS sequence keys (46+) and prime/φ/Fibonacci streams; default-key OutGuess on LP2; running keys from the standard literary corpora; columnar transposition widths 2–40; hash brute force on short strings, phone numbers, short .com domains; IPv4 sweeps.

## 8. Source list

- scream314/cicada3301: `https://raw.githubusercontent.com/scream314/cicada3301/master/{2014,2015,2016,2017,liber_primus,pages_and_ciphers,hints_never_used}.md`
- Uncovering Cicada wiki, via the local export in `scratchpad/dl/dukotah/corpus/C-community/wikis/uncovering-cicada/` (pages: Liber Primus, Liber Primus Unsolved Pages, Frequency Analysis Unsolved Pages, Frequency Analysis (Liber Primus), How the solved pages of the Liber Primus were solved, What Happened Liber Primus (Post 2014), PAGE 56, 2016 Message, PGP Signed Message April 2017, Liber Primus Ideas and Suggestions, Cicada Part 9 - Attempts, Onion 7 numbers on page 15, Unresolved AFAIK, Liber Primus Updates 2025)
- Wulfic: `https://raw.githubusercontent.com/Wulfic/Cicada3301-Liber_Primus/main/{README.md,reference/community/community_research.md,echo446ghq_analysis.md,ideas_suggestions.docx}`
- cicada3301.boards.net threads 10, 30, 32, 34, 55–58 (local archive `corpus/C-community/forums/boards_net_live/`)
- Discord archive: `https://raw.githubusercontent.com/jaxonkuipers/cicada3301/main/discord.db`
- micheloosterhof/aldegonde: `https://raw.githubusercontent.com/micheloosterhof/aldegonde/main/hypotheses/{README,INDEX,word-length-keystream-and-boundaries,ciphertext-autokey,doublet-dodge-walk,explicit-doublet-avoidance,interrupted-walk,accumulator-autokey}.md`
- ZzNible: `https://raw.githubusercontent.com/ZzNible/cicada3301-liber-primus-findings/main/{FINDINGS,NEGATIVE_RESULTS}.md`
- Leo-Y-Zhang/LiberPrimusAnalysis, Dukotah/cicada3301, TheronEagle/liber-primus-research, Pitchfork-and-Torch/liber-research (GitHub READMEs)
- crashdemons/Cicada-DWH-HashcatAttempts (README)
- Search snippets only [S]: DEF CON 31 slides, March 2026 SHA-1 preprint, Wikipedia status line
