# scout5_layout_and_nontext — LP2 layout, non-text readings, "undecipherable?" and transposition literature

Scout: `scout5_layout_and_nontext`. Date: 2026-10-09.

## 0. Method, limits, labels

**Access limits (important).** The sandbox egress proxy blocked everything except GitHub (arxiv.org, wikipedia, reddit, web.archive.org, eprint.iacr.org all returned 403 CONNECT; WebFetch fails DNS). So:
- Cicada-community material was read from **local mirrors** already in the working tree: Uncovering Cicada wiki XML export, the CicadaSolvers wiki (WordPress JSON), and the Dukotah repo (`dl/dukotah/...`, ledger rounds 8–30).
- Literature on Z340, Lasry, Nuhn & Knight, Wayner, Union route cipher comes from **WebSearch result summaries only** (label `[S]` = search-snippet-level, not read in full).
- Reddit, DEF CON 31/26 talks, the 2021+ documentary, and press pieces could not be opened. Where I say "not found" it means not retrievable here.

**Labels.** (a) = primary/verified (artifact, signed message, direct measurement). (b) = community consensus or community-wiki statement. (c) = speculation. **(m)** = my own quick measurement on the local transcription (`dl/dukotah/liber-primus/data/krisyotam_runes.txt`, identical lineage to rtkd/relikd). Script: `research/sentstats.py` plus inline snippets. Descriptive only, not key attacks.

Abbreviations: UC = Uncovering Cicada wiki (uncovering-cicada.fandom.com). CS = cicadasolvers.com wiki. DK = Dukotah repo (`github.com/Dukotah/cicada3301`).

---

## 1. Layout: what is established

### 1.1 How LP2 is typeset (a, m)
- **Flowed text, character-level wrap, no hyphenation marks.** Of 604 line breaks in the transcription, 458 (76%) fall mid-word, 107 after a `-`, 39 after a `.` (m). If breaks were placed at random character positions, about 1/(mean word length+1) ≈ 18–22% would land on a word boundary; observed 24%. So wrapping ignores word boundaries entirely.
- **Fixed column, 12 lines per full page.** Lines hold 21.7 ± 2.7 runes (plus 3–7 separator dots). 35 of 57 segments have exactly 12 lines. Full pages hold 255–277 runes; short pages are the ends of sections (137, 131, 121, 66, 76, ...) (m). That is what you get when a single stream is poured into a page template, then cut off at the end of each section.
- **DK R18 L3** (`analysis/round18/L3-ornaments/RESULTS.md` ~l.16, 249–261) independently found "typesetter justified to a fixed column width; a line packs more runes when its glyphs are narrow", i.e. typographic justification, not a channel. **DK R30 A1/A2/A3 + R29 L4**: the runes are a deterministic vector font; the book was rasterised from a PDF/PS through Ghostscript (ICC byte-identical to GS 9.06 `srgb.icc`), 400 dpi, then IM re-encode q92. No glyph-variant or sub-pixel channel above a ~2 px detection threshold.
- **LP1 uses the same typesetting** (b/a). The community Latin line-by-line transliteration of LP1 (UC "Runes Transcriptions") shows plaintext words cut across lines with no hyphen, e.g. `...A R E . S A C / R E D ...`, `...E N C R Y / P T E D`. UC "How the solved pages were solved" gives the rtkd-format ciphertext with the same wrap. So **mid-word wrapping is not a mark of a decoy**; it is the book's house style.
- **Delimiters** (a: transcription; b: meaning). `-` word (interpunct), `.` sentence/clause mark (a small cross glyph), `/` line wrap, `%` page, `&` and `$` section-end ornaments (18 and 9), literal digits 1–5 at line starts on pp36–38 and a `7` in p10 (DK transcription). CS "Delimiter" page: "1:1 delimiter congruency is assumed to be maintained, as it is in LP1 and the two solved pages of LP2" and "the dot delimiters correspond to ASCII LF, CR and ETB" (b, and the ASCII mapping is (c)).
- **Quotation marks and apostrophes** are visible in the unsolved text (UC "Liber Primus Unsolved Pages": pp 4, 6, 7, 21, 22, 35, 40, 41, 42...). They are anti-aliased unlike the rune glyphs, i.e. added in a separate raster step (b/a). In LP1 the solved plaintext has no such punctuation inside words. This says the author's pipeline had a "punctuation overlay" stage. It does not by itself say the marks encode anything.
- **LP1 is faithful: layout tracks plaintext.** In LP1 `.` falls exactly where the plaintext sentence ends ("A WARNING." "BELIEVE NOTHING FROM THIS BOOK." ...), and `-` at plaintext word breaks (UC "How the solved pages..."). The 3301 convention is therefore: delimiters are cleartext copies of plaintext structure. LP2 is the first place the convention is in doubt.

### 1.2 Section "titles", incipits, drop-caps (a/b)
- CS and UC both describe LP2 as an **illuminated manuscript**: sections announced by marginalia and **rubricated incipits**; 7.jpg also has a rubricated **explicit** (CS "Rubrication", "Explicit", "Incipit", "Marginalia"). Sections: 0–2 Signpost/Cross, 3–7 Spirals, 8–14 Branches, 15–22 Mobius, 23–26 Mayfly, 27–32 Wing & Tree, 33–39 Cuneiform, 40–53 Spiral Branches, 54–55 Spiral & Dead Tree, 56 Deep Web Hash, 57 Parable (CS "LP2").
- **LP1 precedent for the red/title text:** UC marks "A Warning:" and "For all is sacred." in red, and these are real plaintext (page 1 "A WARNING", last line "FOR ALL IS SACRED"). Section-opening phrases in LP1 are real words (WELCOME / A KOAN / SOME WISDOM / AN INSTRUCTION / THE LOSS OF DIVINITY / AN END / PARABLE). So the 8+5 run on p0 and the 1+8 on p54 are *probably* titles in the same enciphered stream, not separate objects.
- **DK R22-D** catalogued red drop-caps: 15 of 58 pages (0, 3, 6, 7, 8, 15, 23, 27, 33, 39, 40, 53, 54, 56, 57); read in page order they give `SLXHXFUMDSFAINGP`; tests against a seed-3301 null min p = 0.18. Null.
- **Not found anywhere I could read:** a community write-up of the p54 1+8 run or of an "odd page word counts" claim. My own count (m): 35 of 57 segments have an odd word count (p ≈ 0.09 two-sided, not significant); 21 of 57 have a prime word count and 14 of 57 a prime rune count, consistent with chance for numbers in the 20–280 range. No evidence of a number-theoretic page structure.

### 1.3 Statistics of the layout (m, with English control)
Control text: Emerson, *Self-Reliance* (`data/keys/self_reliance.txt`, letters, not futhorc, so absolute values differ; the signs and sizes of the effects are what matter).

| statistic | English control | LP2 | comment |
|---|---|---|---|
| adjacent word-length mutual information, n≈2,900 words | 0.088 bit vs 0.030 for shuffled (sd 0.004), i.e. +0.058 bit, >10 sd | reported by caller as indistinguishable from shuffle | test has strong power at LP2's size, so "no sequential structure" is a hard result, not a power failure |
| sentence-FINAL word length minus interior | +1.65 letters (sd 0.14 at n=204) | **−0.11 ± 0.17 runes** (n=204 sentences with ≥3 words) | 10 sd away from English |
| sentence-FIRST word length minus interior | −0.96 | **−0.24 ± 0.18** | English function-word openers absent |
| sentence length (words) | mean 21.9, CV 0.71 | mean 13.1, CV 0.79 (227 units) | geometric (independent per-word mark) would be CV 0.96, so marks are *more regular than Bernoulli* but nothing like English clause structure |
| boundary-after-rune vs preceding rune (χ²) | n/a | 32.1 / 28 df; vs following rune 24.9 / 29 df | boundaries independent of rune identity; no rule like "break after rune X" |
| boundary vs cumulative rune index mod k (k=2..29) | n/a | all χ² ≈ df | no running-sum segmentation (index in Unicode order, caveat) |
| 1-rune words | English ≈ 3–4% | ≈ 10% (DK Campaign XIV P5) | already known |
| mean rune-word length | 4.10–4.15 for English-in-futhorc | 4.425 (DK R8/R9, 458 F-interrupters explain +0.156) | residue +0.17 unexplained |

DK STRUCTURE-FINDINGS table (a): the doublet deficit crosses **every** boundary type at the same rate: within word 0.0062 (n=9640), across `-` 0.0081 (2589), across `.` 0.0075 (133), across line wrap 0.0075 (534), across page join 0.0000 (54). Random would be ~0.0345.

**Consequences of that table (my inference, c but tight):**
1. The cipher runs over the **reading-order rune stream** and ignores word, line and page edges. The segmentation sits either on top of the ciphertext or in a plaintext that was fed into the chain intact.
2. **Word transposition AFTER encryption is excluded.** Shuffling ciphertext words would restore a 3.45% doublet rate at the `-` seams (observed 0.81%, n=2589).
3. **Word transposition BEFORE encryption is invisible** in the ciphertext. It could only be told apart by the plaintext itself, once decrypted. See §4.

### 1.4 What people have said about the segmentation
- **Assumed real:** CS (above); DK Campaign XIV P5 ("directional positive evidence the plaintext is genuine English prose with meaningful boundaries", reference of only 51 solved words), DK R8 SKELETON and R10 L4 (word-length sequence slid over 224 texts / 22.6M words as a plaintext invariant, null; "an OTP hides symbol values, not word boundaries"), DK R8 separator audit (151/170 lines agree with the images; the separators in the transcription match the images).
- **Treated as typography, not a payload:** DK R11 S2 (binary/ternary/run-length decodings of separators, null; run-length variance ratio vs geometric 0.307, so separators are placed far more regularly than a per-symbol event), DK R10 L2-map M3 (word-length parity/threshold → ASCII/Baconian, null).
- **Treated as possibly fake:** I found **no community write-up proposing that the segmentation is decorative or that words are transposed.** Closest items: (i) CS "Impossible LP Theory" / "ImpossiPrimus" (b/c): LP2 is a "nonsense cipher text with tantalizing cryptanalysis" made on purpose so it never gets solved; (ii) the Etherpad "Untried methods" list quoted on UC "Liber Primus Ideas and Suggestions": "Counting spaces AS runes instead of not", "Using the outguess data to relocate the runes before shifting them", "Spirals - Route cipher?", "Rune - base29 integer?", "Undecrypted pages may not use words. Maybe binary", "Breaking LP into sections and applying the first rune's value..." (c); (iii) a GitHub tool (`yo-yo-yo-jbo/cicada_tools`, snippet only) claiming LP2 "encrypts whole words, based on word lengths and punctuation" (c, weak). UC "Thoughts on Runes" (CS copy) notes the author's Latin→rune converter is inconsistent about digraph runes (e.g. `ᛏᚻᚫᛡ` written as T+H+AE+IO, not TH+AE+IO), so encryption happened at the **rune** level on text that was already somewhat messy (b).
- **The only 3301 text that touches this** (a): LP1 p1 "Do not edit or change this book. Or the message contained within. **Either the words or their numbers**. For all is sacred." and the signed 2016-01-01 message "Liber Primus is the way. **Its words are the map, their meaning is the road, and their numbers are the direction.** Seek and you will be found." Read together they allow: the message survives in *either* the words *or* their numbers (so one of the two may be decorative), and "words are the map" is a *route* clue (cf. §4.3).

### 1.5 Best explanations of "English-like length marginal, no sequential structure, marks independent of length"
Ranked by how well they fit the measured facts. All (c) unless noted.

| # | model | fits | misfits |
|---|---|---|---|
| H1 | **Synthetic cover:** the generator draws word lengths i.i.d. from an English-like pmf (a mimic function in Wayner's sense) and places marks by a separate renewal process; the real information is only in the rune values | marginals, zero sequential MI, no first/last-word effect, marks regular but unrelated to length, flowed typeset like LP1, doublet rule crosses seams (cipher ignores seams), absent THE/OF (a generator pmf need not contain them) | needs the author to have done something LP1 did not; one more reason to expect a deliberate decoy (§3) |
| H2 | **Plaintext word-shuffle before encryption** (word-level transposition, "bag of words") | marginals preserved, sentence-position effects destroyed | shuffled English still has THE/OF as the most common 2-rune words (≈9% of tokens). The caller says these are missing. So the plaintext must also be stop-word-stripped, a double special case |
| H3 | **Lengths are a covert channel** (arithmetic/Huffman-coded cover, bits → lengths under an English pmf) | iid draws from a pmf look exactly like H1; capacity ≈ H(length)≈3 bit × 2,928 words ≈ 1.1 kB | no evidence; only parity/threshold decodings were run (DK R10 L2 M3) |
| H4 | Real prose in an unfamiliar register (list/telegraphic/non-English) | DK R8 length anomaly (+0.17) | doesn't produce zero sequential MI at n=2.9k; English controls give >10 sd MI |
| H5 | Separators emitted as symbols of the cipher alphabet (31-ary stream) | cipher ignores seams | separators are far more regular than a per-symbol event (DK S2 ratio 0.307); length pmf is hump-shaped, not geometric |

**What each implies for "where the real message is":**
- H1/H3: the message, if any, is in the rune **values** only. Every attack that uses word boundaries (skeleton matching, word-pattern cribs, per-word key restarts, "words are the map") rests on a false premise and is **void**, not merely null.
- H2: the message is in the values as well, but after a key is found the decrypt will read as English words in scrambled order. Letter-level scorers (quadgram sums, as in DK) would still fire, because most quadgrams lie inside words.
- In all four cases the layout itself carries **no recoverable key information**, and the ledger's null results on separators and line geometry stand.

---

## 2. Non-text / steganographic readings considered

| idea | who | status |
|---|---|---|
| rune stream as base-29 integer / binary data / "maybe binary" | UC Etherpad list (c) | DK R24 PLAN C5 "value-stream-as-binary-object" **killed at the gate** (degenerate null: any byte string decodes to *something*; no positive control); DK R11 N3 (whole book/segments as number-theoretic objects: 0 primes, powers, Mersenne, RSA-shaped; "anti-special"); DK R22-B G3 (base32/onion/lat-long pointer search: none) |
| Tor address / PGP key / image hidden in stream | folk | no support: base32 low-entropy runs at or below shuffle null (R22-B), no OpenPGP structure in blobs (R30 B2) |
| transposition grid keyed by page geometry; columnar at true line width | UC list, DK R22 "Lane G2/B2" | **not run** (shelved, "low expectation"); DK R22-A/R23-A2 only acrostics on solved text. Note §1.1: the line width is a typesetting artifact, so a grid reading at line width has little prior |
| numbers as direction (turtle, grid walk, moves) | 2016 message read literally | DK R22-B: 3 streams × turn moduli {4,6,8,12,29,360} × {abs,rel} × {unit,value-step} = 72 renders vs 6 shape statistics with planted-square positive control; all constrained lattice random walks, 0 flagged. DK R9 DIRECTION (2,670 readings) **had no positive control** (PA-2 caveat); R22-B supersedes it |
| koans as operations (every-4th, reverse then re-encipher, plaintext as running key, prime/totient keystreams) | page 5 koans | DK R22-C: 185 operations, 4 plant-and-recover controls, 0 survivors |
| self-embedded message in solved plaintext | folk | DK R22-A (3,508 selections) and R23-A2 (line/word acrostics, 48 reads), null with controls |
| illustrations / drop-caps | CS, UC "Symbols/Drawing/Art" | DK R22-D drop-cap catalog null; figural motifs (cross, tree, shrouded corpse, mayfly) **not coded as data** (needs a validated extractor) |
| pp49–51 "tables" | UC "Page 49-51", "pp49-51 data interpreted as base 59, 60, 62, 64" | 256 two-char tokens, first char 0–4, second in 60 symbols (never lowercase f, y, z), max `4F`=255 → 256 bytes = 2048 bits. DK Campaigns VII/IX/XII/XX, R18 L5, R30 B2/E1: not prime, not a clean RSA modulus, not PGP, not a stacked digest, no entropy collapse under XOR/subtract with 7+ known key streams, 73 candidate keys × AES/ChaCha/RC4/XOR, HMAC vs AN END hash (1,752 combos). Image re-read confirms `canon_256.bin` unchanged. Behaves like a random blob |
| image stego in the LP2 JPEGs | folk, scream314 | DK `analysis/stego/STEGO-VERDICT.md`: 56/56 SHA-1 identical to the archived onion7 dump; no trailing bytes, no EXIF/XMP, no carved files. OutGuess `-r`: 30/33 pages empty; pages 0, 4, 26 give 58,152-byte, entropy 7.997 blobs, a 1,417-byte shared prefix (pages 4 & 26 share 2,004 B). Explained as the OutGuess false-positive for non-carrier JPEGs of identical size over identical blank margins; the decisive Linux control run (OutGuess on a blank GS-rendered 2400×3600 JPEG; passphrases 3301, 33011033, circumference, firfumferenfe, welcome, instar, pilgrim) was listed as pending in June 2026. DK R29 L1: 4,013 keys × 3 images × 2 tools = 24,078 extractions on the *onion* images, null; corrected the record: onion3 is a "Chapter 1 / Intus" divider, the "A WARNING / BELIEVE NOTHING" runic page is onion2 |
| Ghostscript toolchain | community noticed "Copyright Artifex Software 2011" (UC Ideas page, 2016) | **DK R29 L4 + R30 A3 (a):** ICC byte-identical to GS 9.06 `srgb.icc` (md5 `e409cef1...`), narrowing to GS 9.01–9.15; optimised Huffman; all EXIF stripped; the 2012 images come from a different toolchain. Process attribution only: LP2 was *typeset* from a PDF/PS, not drawn per page. Open: the source PDF (would give kerning arrays and the font name), differential GS-version pinning, art attribution |
| whitespace/typography as a Cicada channel | precedent | (a) The 2014 `message.txt.asc` hides the prime sequence 2,3,5,7,11,13,17,23,29,31,37 (19 omitted) as counts of spaces between lines; the July 2015 Planned-Parenthood message hides 5-3-2-5-7; an OutGuessed "rune table" message is tab/space-coded binary (UC "What Happened Liber Primus (Post 2014)", "OutGuessed message from rune table"). So 3301 *has* used layout-level numeric payloads, in the clear-signed messages, not (as far as found) in the runes |

**Net:** every non-text channel the hints point at has been read at least once, with plant-and-recover controls, and is empty at the tested resolution (DK Round 23 decision line). The only unread items: figural motifs, true-geometry columnar/route readings, the source PDF, the OutGuess control run, and arithmetic/model-based decoding of the length sequence (§1.5 H3).

---

## 3. Is LP2 deliberately undecipherable, or a pad released later?

### 3.1 Documented timeline (a unless marked)
- 2014-01 puzzle starts; 2014-05-02 ~10:00 GMT messages to all hidden services registered on onion 6; `ky2khlqdf7qdznac.onion` serves `0.jpg`...`57.jpg` (thttpd/2.25b, last-modified 2014-04-02). UC calls the 2014 chain "the unfinished Rune Pages step".
- 2014-05+: LP1 (17 pages) solved within weeks; p56 solved days to weeks after release (stream of prime−1, i.e. φ(p) mod 29); p57 plain transliteration.
- 2015-01: nothing. UC: "Some theorized it was because the Liber Primus had not been completed, some believed the members they were looking for were enough, or even that 3301 had given up" (b). 2015-07-27: PGP-signed Planned-Parenthood disclaimer.
- 2016-01-01: PGP-signed "The path lies empty; epiphany seeks the devoted. Liber Primus is the way. Its words are the map, their meaning is the road, and their numbers are the direction. Seek and you will be found. Good luck. 3301. Beware false paths. Verify OpenPGP 7A35090F." (signed 2016-01-01 00:01:07 UTC, hidden also in an oak-tree/cicada image on Infotomb).
- 2017-04-04 (found 2017-04-29): signed "Beware false paths. Always verify PGP signature from 7A35090F. 3301". Last verified message. Nothing since.
- **No signed statement from 3301 about a pad, a key, a "second part", or a planned 2015 continuation exists in any source I could read.**

### 3.2 What historians/witnesses say (b)
- **Witness record (DK `analysis/attribution/CAMPAIGN-XIX-WITNESSES.md`, 100-agent deep-research, 18 sources, adversarial verification):**
  - Marcus Wanner (2012 winner; Nox Populi interview, Rolling Stone 2015, VT Magazine, WNYC): insider surface was a minimal onion forum, chat, a 3301-hosted CAKES wiki, git, PGP email, ~20 winners; the only directive was to build "technological freedom" software; **no mention of Liber Primus, AN END, pages or keys**; forum vanished ~March 2013 ("We've been laid off"), before LP2 existed. So the 2012 forum is excluded as a key location by timeline.
  - Joel Eriksson ("clevcode"): solved the 2012 public stage, **missed the registration window**, never an insider.
  - "Nox Populi" (@NoxPopuli3301; DEF CON 26 talk): self-claimed 2013 winner, not independently verified. Reachable.
  - Per-person distribution precedent: early arrivals each got a *different* RSA-encrypted message at `sq6wmgv2zcsrix6t.onion/NUMBER`; if key material ever went out, it could be individualised.
- **AN END** (p56, a): "Within the deep web there exists a page that hashes to [SHA-512] ... It is the duty of every pilgrim to seek out this page." **Never found** in 12 years (CS: "The referenced hash has never been found"; DK hunted archived onion corpora; page not among them). It is the only artifact in LP2 that explicitly points to *external content*.
- **Impossible LP Theory** (CS, b/c): LP is intentionally unsolvable because an unsolved LP better serves 3301's recruitment/socialisation goal (rationale taken from "The Leaked Email" mission text). This is a community-wiki argument, not a cryptographic one.
- **CS "Cryptanalysis Briefing"** claims "There are cryptographically sound indications that it is solvable" (b) but lists none beyond structural similarities to LP1 and Fibonacci/prime meshing in the 2015–17 messages.
- **DK verdict** (self-published, ledgered, not peer reviewed): "OTP-class, NOT 'unsolvable'". The ciphertext is statistically indistinguishable among (i) true external pad, (ii) SHA-256-counter derived key + anti-repeat filter, (iii) ciphertext autokey over flat non-English plaintext (R10 B4: |z|<2.93 on a 6-statistic battery). DK PA-1: "OTP" is the repo's *own* verdict; 0 of 3 primary community sources claim OTP, 2 of 3 claim solvable. DK explicitly notes the chain/anti-repeat filter, not the key, sets the doublet rate (RECON-B B-16), so the doublet deficit constrains the construction less than first claimed.
- **Press/academic:** Wikipedia and mainstream press (as summarised in DK `research/03`, `06`, and in the search snippets) say only: unsolved since 2014, last verified message 2017-04, creators unidentified. **I found no published argument that LP2 is literally unsolvable without 3301's cooperation**, only (i) the Impossible-LP community theory and (ii) DK's indistinguishability argument. Neither is formal. Related literature on how fragile "it's a one-time pad" inferences are: Ryabko, *The Vernam cipher is robust to small deviations from randomness* (arXiv:1303.2219) and Wase, *The Upplandic Non-Lexical Rune Stones: Ciphers or Nonsense?* (HistoCrypt) (both listed in DK `corpus/F-press-academic/BIBLIOGRAPHY.md`; not read by me).

### 3.3 Reading of the evidence (c)
- The **book's own structure** is the best evidence about intent: unsolved body (0–55) → p56 AN END points outside the book → p57 closing parable. A chain of "decrypt, then be told where to go" is exactly how the 2012/2013 stages worked. The most economical design reading is that the key is *the thing AN END points to* (or something obtainable by passing through that gate). That makes the body unsolvable from ciphertext alone *by design*, whether or not 3301 ever intended to leave the gate open.
- The 2016 message ("Liber Primus is the way ... seek and you will be found") says 3301 regarded LP as still live in 2016, which sits uneasily with "intentionally unsolvable" and fits "pad/pointer withheld or lost".
- A layout that is **independent of the content** fits equally well with a decoy (CS Impossible LP) and with a mechanically generated cover for a stream that is just meant to be keyed externally. It does not discriminate between "never to be solved" and "solved by key delivery".

---

## 4. Transposition + substitution: literature and how it bears on LP2

### 4.1 Detecting and attacking transposition under an unknown substitution
- **Z340 (Oranchak, Blake, Van Eycke; arXiv:2403.17350; Dec 2020 solution; `[S]`).** Method: count **repeated bigrams** in the ciphertext read at different periods; Z408 (no transposition) at period 1 has 62 repeats (7.5 sd above shuffled); Z340 at period 1 has 25 (1.36 sd) but **period 19 gives 37**, and 34 periods in [2,170] reach at least the period-1 count, which is the cue that a transposition is involved. Then search over candidate reading orders (transposition reverser tool) and score each with a homophonic-substitution solver (Van Eycke's AZdecrypt). The statistic is **substitution-invariant** because repeats survive any fixed (homophonic) substitution.
- **Why this fails for LP2:** LP2's repeated n-grams are at null level (CS Structural Overview: repeated bigrams 12,952 vs 12,955 ± 0.06, trigrams 5,517 vs 5,337 ± 67, quadgrams 255 vs 235 ± 22; 6-gram `DJUBEI` only twice, pp 27–32 and the end of 54–55). Once a flat aperiodic key (or a chain/feedback cipher) sits on top, no substitution-invariant repeat statistic survives, so there is **nothing to detect a transposition with** from ciphertext alone. The same holds for IoC-based methods: transposition leaves IoC unchanged, polyalphabetic flattens it, and the combination is indistinguishable from the polyalphabetic case.
- **Search machinery** (Lasry, Kopal, Wacker; Lasry's 2018 Kassel thesis, *A Methodology for the Cryptanalysis of Classical Ciphers with Search Metaheuristics*; `[S]`): hill climbing / simulated annealing with n-gram scoring for single transposition with long keys, double transposition ("divide and conquer"), ADFGVX (substitution + columnar transposition); Kopal's SA for homophonic ciphers; Nuhn & Knight (EMNLP 2014, "Cipher Type Detection", 58 features including repetition and Amsco features, 50 cipher types) as a type classifier; Bean, *Cryptodiagnosis of "Kryptos K4"* (HistoCrypt 2021): Monte-Carlo permutation tests on a short unsolved cipher, concluding a one-to-one plaintext/ciphertext relation and suggesting Gromark. All of these require the polyalphabetic layer to be **keyable by a small hypothesis space** (known keyword, period) so that the inner substitution can be optimised away.
- **Union Army route cipher** (`[S]`: Wikipedia "Transposition cipher", Programming Praxis, Sauerberg's ASA essay): a *word-level* transposition. Words are written into a grid, read off by a keyed route (e.g. down column 3, up column 4, ...), with null words and a code-word layer. The route is the key. This is the clearest historical precedent for a *"words are the map"* construction, and it is exactly the kind of system whose output has English-like word-length marginals with scrambled order.

### 4.2 What it means for the "transposed words" hypothesis (c, tight)
1. **Pre-encryption word transposition cannot be found from the ciphertext** by any method in the literature, because the chain/pad hides the letter statistics the methods rely on. It only shows up *after* a key is found (word salad of real English words).
2. **Post-encryption transposition is already excluded** by the seam doublet rates (§1.3).
3. **Prior key-search negatives are not blind to H2.** A scorer that uses letter n-grams inside words, with 4.4-rune words, still sees most quadgrams intact. The risk is only in scorers that insert word-boundary tokens or use word-level language models. That is a quick audit item.
4. If the plaintext was word-shuffled, the missing THE/OF still has to be explained, which points to stop-word removal or to H1.

### 4.3 What the route-cipher reading would need
If "words are the map, numbers are the direction" were literal: a grid of words (page = 12 lines is a candidate row count; ~11 words per line), a route given by the gematria sums of words or of titles, and nulls. This can only be tested after a key exists (the words are not known until then), so it is **a downstream design, not an attack**.

---

## 5. Actionable leads (ranked by prior × testability)

1. **Layout-fingerprint battery + synthetic-layout model comparison (high testability, certain value).** Compute on LP1-solved text (positive control), 3+ English corpora, stop-word-stripped English, word-shuffled English, i.i.d.-length synthetic text, and LP2: adjacent-length MI, first/last-word contrast, 1- and 2-rune-word successor statistics, the full length pmf, sentence-length CV, boundary vs rune identity. Output: which of H1–H5 fits, and a yes/no on "word boundaries carry plaintext information". My preliminary numbers (§1.3) already say H1/H3/H2+stopwords; the battery turns it into a decision. If boundaries are cosmetic, **audit the ledger for lanes whose planted controls or scorers used word boundaries** (B3 semantic-key crib readouts, R10 L4 skeleton, any word-pattern cribs) and re-run them boundary-free. Prior that it unlocks the key: ≤3%. Prior that it correctly prunes wasted work: ~80%.

2. **AN END hash-page hunt on large public 2013–2015 hidden-service corpora (moderate prior, medium testability).** It is the only LP artifact that points off-book. Hash (SHA-512) whole files and normalised variants (CRLF/LF, stripped headers/trailing newline, HTML-body only, double hashing, SHA-512 of the base64/hex string) for: gwern's *Darknet Market Archives* (2013–2015 Tor HTML), Internet Archive onion captures (the `ky2khlqdf7qdznac.onion` style items), published Tor-crawl datasets, Freenet/GNUnet CHK-style key derivations for known 2014 files. The CS "Deep Web Hash Checker" tool and DK `analysis/anend_hunt` give the scaffolding. Prior that the page exists, is archived and holds the key/pad: ~3–5%. Highest *expected* payoff because it is the only route that would produce a key rather than another null.

3. **Use `canon_256.bin` (pp49–51, 2048 bits) as a generator seed, not as ciphertext or additive key (low prior, high testability).** 256 B = the maximum RC4 key; 32 B + 12/16 B = ChaCha20/AES-CTR key+nonce; 4×64 B = SHA-512 counter blocks / HMAC-DRBG personalisation. Generate keystreams and run them through DK's **skip-aware pair decoder + `hitfn20`** (R24 C2). DK Campaign XX tried AES/ChaCha/RC4 on the payload as *ciphertext* and R26 C used canon_256 only as an integer seed; I did not find an RC4/ChaCha/AES-CTR/DRBG keystream *from the payload* over LP2. Verify in `analysis/round26/C/seeds.json` before spending effort. Prior ~2%.

4. **Delimiter-inclusive key indexing in the cheap sweeps (low prior, very cheap).** Re-run the highest-prior dictionary/sequence/PRNG sweeps with the key index also advancing on `-`, `.`, `/`, `%` (the community's "Counting spaces AS runes" idea), and with key restarts at section starts (`&`/`$`), at drop-cap pages, and after the 7 literal digits on p10/pp36–38. DK showed the *doublet filter* is continuous across seams, but key *indexing* was not varied by delimiter. Prior ~2–3%, nearly free given the harnesses and controls exist.

5. **Length sequence as an arithmetic/Huffman covert channel (low prior, medium testability).** Decode the 2,928 lengths (plus mark positions) as symbols drawn from candidate pmfs (LP1 length pmf, English-in-futhorc, the LP2 marginal itself), convert to a bitstream, test for structure (PGP packet headers `0x85/0x99/0xc6`, `-----BEGIN`, zlib `0x78 9c/da`, JPEG `ffd8`, ASCII bias, base32 onion alphabet). A planted-message control with the same coder is mandatory. DK R10 L2 M3 only did parity/threshold bits and Baconian. Prior ≤3%; the null is clean if the coder is wrong, so only claim a result with the plant control.

6. **Close the OutGuess carrier-artifact question (low prior, cheap).** Linux run: `outguess -r` on a blank/control JPEG produced by the same GS 9.06 → q92 pipeline and 2400×3600 size; if the 1,417-byte prefix reproduces, close it. Then re-extract pages 0/4/26 with `-k` over 3301-flavoured passphrases (DK's list plus words from the AN END text, "CAKES", "brood", "7A35090F", "Intus"). Prior ~1%.

7. **Source-PDF / generator recovery (low prior on the key, real prior on understanding the layout generator).** The book is a rendered PDF (GS 9.06). Recovering the PDF (or the script that produced the dot/rune layout) would show whether the dots are glyphs in a string (generator saw a *string with separators*) or positioned objects, expose TJ kerning arrays, and name the typeface. Also build GS 9.05/9.07/9.10/9.14 and diff DQT/Huffman bytes to pin the version. If the dots are separate objects placed by a rule, the layout is independent of the stream by construction (settles H1 vs H5). Off-repo archival hunt (DK R30 thread 1).

8. **Instrument audit for H2 (cheap, defensive).** Check that DK's English scorer (and any new scorer) uses *letter* n-grams within runs only (no `_` boundary tokens, no word-level LM). Add a word-shuffled-English plant to the positive-control suite so a correct-key decrypt of shuffled plaintext still clears the bar. Prior of mattering ~5%; cost ~hours.

9. **Do not invest (documented dead ends or unfalsifiable):** a route/grid reading of words before a key exists (needs the plaintext); word-length skeleton matching against more corpora (void if H1); further turtle/Gematria-direction renders (R22-B covers 72 combos with control); `Impossible LP` as a *test* (no operational content).

---

## 6. Sources

Local (read):
- UC wiki export: `dl/dukotah/corpus/C-community/wikis/uncovering-cicada/export_cur_*.xml` — "Liber Primus Ideas and Suggestions", "Liber Primus Unsolved Pages", "What Happened Liber Primus (Post 2014)", "How the solved pages of the Liber Primus were solved", "Runes Transcriptions", "Frequency Analysis (Liber Primus)", "Interconnectedness", "Onion 7: numbers on page 15", "OutGuessed message from rune table", "Page 49-51", "Liber Primus pp49-51 data interpreted as base 59, 60, 62 and 64", "Possible hints never used". Live URL: https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Ideas_and_Suggestions , https://uncovering-cicada.fandom.com/wiki/What_Happened_Liber_Primus_(Post_2014) , https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Unsolved_Pages
- CicadaSolvers wiki (WordPress JSON): https://www.cicadasolvers.com/quickstart/ , https://www.cicadasolvers.com/wiki/liber-primus/liber-primus-structural-overview/ , https://www.cicadasolvers.com/wiki/liber-primus/lp2/solvability/impossible-lp-theory/ , https://www.cicadasolvers.com/wiki/liber-primus/delimiter/ , https://www.cicadasolvers.com/wiki/liber-primus/thoughts-on-runes/ , https://www.cicadasolvers.com/wiki/liber-primus/lp2/ , https://www.cicadasolvers.com/wiki/liber-primus/dis-legomenon/
- DK repo (https://github.com/Dukotah/cicada3301): `liber-primus/analysis/STRUCTURE-FINDINGS.md`, `CAMPAIGN-XIV-FINDINGS.md` (P3, P5), `round8` (separator audit, length anomaly), `round10/SYNTHESIS.md`, `round11/SYNTHESIS.md` and `S2/RESULTS.md`, `round18/L3-ornaments/RESULTS.md`, `round22` to `round24` and `round29`/`round30` `SYNTHESIS.md`, `stego/STEGO-VERDICT.md`, `pp49_51/CAMPAIGN-VII/IX/XX`, `attribution/CAMPAIGN-XIX-WITNESSES.md`, `ELIMINATION-LEDGER.md`, `corpus/F-press-academic/BIBLIOGRAPHY.md`, `research/03-puzzle-2014-liber-primus.md`.
- Transcription used for (m): `dl/dukotah/liber-primus/data/krisyotam_runes.txt`; English control `data/keys/self_reliance.txt`.

Search-snippet level (`[S]`, not read in full):
- Oranchak, Blake, Van Eycke, *The Solution of the Zodiac Killer's 340-Character Cipher*, arXiv:2403.17350 (https://arxiv.org/abs/2403.17350)
- Nuhn & Knight, *Cipher Type Detection*, EMNLP 2014 (https://aclanthology.org/D14-1185/)
- Bean, *Cryptodiagnosis of "Kryptos K4"*, HistoCrypt 2021 (https://ecp.ep.liu.se/index.php/histocrypt/article/view/153)
- Lasry, thesis, Univ. Kassel 2018 (https://kobra.uni-kassel.de/handle/123456789/15274); Lasry/Kopal/Wacker double-transposition and long-key columnar papers (Cryptologia)
- Wayner, *Mimic Functions*, Cryptologia 16(3), 1992 (https://en.wikipedia.org/wiki/Mimic_function)
- Union route cipher: https://ww2.amstat.org/mam/06/Sauerberg_route-essay.html , https://programmingpraxis.com/2012/03/06/union-route-cipher/
- Boxentriq LP guide: https://www.boxentriq.com/guides/cicada-3301-liber-primus ; DEF CON 31 talk (Taiiwo et al.), *Cracking Cicada 3301*: https://media.defcon.org/DEF%20CON%2031/DEF%20CON%2031%20presentations/Taiiwo%20Artorias%20Puck%20TheClockworkBird%20-%20Cracking%20Cicada%203301%20The%20Future%20of%20Collaborative%20Puzzle-Solving.pdf (not opened)
- `yo-yo-yo-jbo/cicada_tools` claim about whole-word encryption (https://github.com/yo-yo-yo-jbo/cicada_tools)

Not obtained: Reddit threads, Nox Populi DEF CON 26 talk, the recent Cicada documentary, Rolling Stone/WNYC text (taken second-hand from DK CAMPAIGN-XIX).
