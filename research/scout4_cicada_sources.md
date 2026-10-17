# scout4_cicada_sources — what Cicada 3301 demonstrably drew on (2012–2014 + solved LP pages), and what is untested

Scope: sourced inventory of texts, authors and ideas; Cicada's prose; the running-key and crib coverage already recorded in the community repo (dukotah, ./dl/dukotah); numerology. No cryptanalysis run beyond checking the numerology claims themselves.

Evidence grades: **A** = primary (a Cicada-signed text in the local PGP corpus, or a verified local artifact); **B** = secondary consensus (several wiki/news/solver sources agree); **C** = speculation or single-source claim.

Access notes: fandom wiki (uncovering-cicada.fandom.com) is not resolvable from this sandbox, and Gutenberg / fandom return CONNECT 403 via curl. Web search works. raw.githubusercontent.com returns 200. All texts below marked "local" are in dukotah `liber-primus/data/keys/` unless stated.

---

## 0. Corrections to the brief's premises

1. **"Agrippa" in 2012 is William Gibson's poem *Agrippa (A Book of the Dead)* (1992), not Cornelius Agrippa's *Three Books of Occult Philosophy*.** The 2012 book code pointed to Gibson's poem (B: wiki, UCSB Agrippa Files, The Millions). Cornelius Agrippa's Occult Philosophy is in the local keytext set, but no source found ties it to Cicada (C).
2. **Gödel, Escher, Bach; "Songs of the Dead"; Beethoven; Zen koan collection; Tao/Kybalion/Jung/Wilson as Cicada citations**: no primary or secondary source found that ties them to Cicada (searches returned nothing relevant). Treat as C or unverified.
3. **The 2013 "A book whose study is forbidden / once dictated to a beast"** is Crowley's *Liber AL vel Legis* (B: connortumbleson, consensus in dukotah notes).
4. **The 2014 "Interconnectedness" track contains no publicly reported hidden content.** Local file inspection (section 4) shows its ID3 title is "Interconnectedness" and its ID3 artist field is "3301". No spectrogram result was found (C).

---

## 1. Primary Cicada-signed texts that name or quote sources (grade A unless noted)

Local copy: `dukotah/corpus/A-primary-artifacts/pgp/messages/*.asc`. Cleartext extracted to `scratchpad/s4/pgp_cleartext_all.txt`.

| Message (year) | Verbatim cue | What it points to |
|---|---|---|
| 2012-01 book-code-poem | "A poem of fading death, named for a king / Meant to be read only once and vanish / Alas, it could not remain unseen." | Gibson's *Agrippa* (self-erasing floppy, read-once); the "named for a king" phrase is unexplained |
| 2012-01 mabinogion-book-code | "In twenty-nine volumes, knowledge was once contained." / "Go that far in from the beginning and find my first name." | Mabinogion (B: Guest translation most likely; Gutenberg #5160; see table). Addresses use prime expressions: "the first prime" = 2, "the product of the first two primes" = 6 |
| 2013-01 opening-book-code | "A book whose study is forbidden / Once dictated to a beast; / To be read once and then destroyed / Or you shall have no peace." | Crowley, *Liber AL vel Legis* (B). Coordinates are three-part (I:1:6 …) |
| 2013 knock-on-the-sky / instar poem (Mp3 760/761 hidden poem, B) | "Like the instar tunneling to the surface / We must shed our own circumferences; / Find the divinity within and emerge." | Original Cicada text. No external source found for "instar", "circumference" as Cicada phrasing |
| 2014-01 opening-book-code | "The work of a private man / who wished to transcend, / He trusted himself, / to produce from within." then coordinates 1:2:3:1 … | Emerson, *Self-Reliance* (B: secondary solver sources + local text confirms the "trust(ed) himself" cue). Coordinates are paragraph:sentence:word:letter (B, one site). Pointers were tested against Agrippa/Blake/KJV/Mabinogion/Milton but **not** Self-Reliance (see §3) |
| 2014 onion5 / let-the-text-guide-you (JPEG payloads) | "Let the text guide you." | Image payloads, not text sources |
| 2016-01 liber-primus | "The path lies empty; epiphany seeks the devoted. Liber Primus is the way. Its words are the map, their meaning is the road, and their numbers are the direction." | Self-referential; motivates "numbers are the direction" test (R22-B, negative) |
| 2017-04 final-warning | "Beware false paths. Always verify PGP signature from 7A35090F." | Authentication rule; the key is the only authenticity gate |

Recurring formulae in the signed messages (A): sign-off "Good luck. / 3301"; "You have done well to come this far"; "Patience is a virtue"; "Beware false paths"; "Thank you for your dedication and effort"; "Stop making it more difficult than it is"; "The key has always been right in front of your eyes"; "Some news organisations have recently claimed …" (2012, 2015 disavowals, same structure).

---

## 2. Table — text | Cicada-referenced? | edition | tested as key? | tested as crib/pointer? | available

Key-test sources: `armada18/`, `armada19/` (local, dukotah `data/keys`), campaign12/13 keytext sets (`analysis/campaign12/keytext_manifest.json`, `analysis/campaign13/sweep_results.json` lanes_detail), armada20 (`analysis/ARMADA-20-FINDINGS.md`), campaign18 skip-aware sweeps (`analysis/campaign18_skip/CAMPAIGN-XVIII-FINDINGS.md`), round24/26 skip-aware (`LEDGER.json` R24-C2-*, R26-B).

Pointer/book-cipher tests: `analysis/bookcipher/bookcipher.py` and `bookcipher_expand.py` (schemes L1, L2, W1, W2, WA, LN, PG). Books tested: Agrippa (Occult Philosophy), Blake, KJV, Mabinogion, Milton PL — all NULL.

| # | Text | Referenced by Cicada? | Edition / translation | Tested as running key? | Tested as crib / pointer? | Available locally / online |
|---|---|---|---|---|---|---|
| 1 | **Mabinogion** (Welsh tales) | **A/B** — 2012 book-code message names it; "Lady of the Fountain" opening cited by solvers | Guest (1877); Gutenberg #5160 (full), vols #19959, #19976 (B). Alt: Jones & Jones 1948 (C) | Yes: armada18 `mabinogion_vol1/2_guest_edwards_ed.txt`; campaign13 armada sweep | Yes: bookcipher (L1,L2,W1,W2,WA,LN,PG) — NULL | Local (armada18). Online: Gutenberg (search-confirmed; direct fetch blocked here) |
| 2 | **Gibson, *Agrippa (A Book of the Dead)*** | **A/B** — 2012 book-code poem + cipher-erasure design | Poem is copyrighted; UCSB Agrippa Files hosts a ciphertext/metadata archive; floppy/emulator reconstruction (B) | **No** | **No** | Not on disk. UCSB Agrippa Files (agrippa.english.ucsb.edu) — access, not reproduction |
| 3 | **Cornelius Agrippa, *Three Books of Occult Philosophy* (1651 JF)** | **C** — no source ties it to Cicada (the 2012 "Agrippa" is Gibson's poem) | 1651 J.F. translation | Yes: armada18 `agrippa_occult_philosophy_book1/2/3_1651jf.txt`; 0 hits | Yes (bookcipher): NULL | Local |
| 4 | **Crowley, *The Book of the Law / Liber AL vel Legis*** | **B** — 2013 book code ("dictated to a beast") | Hermetic/clean text (local `crowley_book_of_the_law_hermetic.txt`, 31 KB) | Yes: armada18 literary sweep (0 hits); B04 lore seed | **No** pointer test with AL chapter:verse addressing (bookcipher lacked AL) | Local. Public domain. Chapter:verse scheme not yet mapped |
| 5 | **Emerson, *Self-Reliance*** | **B** — 2014 opening book-code; "He trusted himself" cue; quoted in OutGuess payload (secondary) | *Self-Reliance and Other Essays*; local `self_reliance.txt` (56 KB, epigraph "Ne te quaesiveris extra") | Yes: R24-C2-EXT skip-generators (negative, 113k keys); R26-B skip-aware (negative) | **No** — the 2014 paragraph:sentence:word:letter pointer scheme was never applied to LP2 | Local. Public domain |
| 6 | **Emerson, *Essays First Series* (incl. "Circles")** | **C** — "Circles" carries "circumference" + "centre everywhere / circumference nowhere" (Augustine/Hermes) — motif match only | Local `emerson_essays_first_series.txt` | Yes: armada18 (0 hits) | No | Local |
| 7 | **Anglo-Saxon Rune Poem** (futhorc source) | **B/C** — futhorc names; Gematria Primus is a Cicada construction; no direct citation found | OE + translit local (`runepoem_oe.txt`, `runepoem_translit.txt`) | Yes: armada20 #2 (running key + 6 stanza schedules): negative, −6.22 | Partially (stanza schedules) | Local |
| 8 | **Blake, *Marriage of Heaven and Hell*** | **B** — 2014 image (plate with faint cicada marking, news/WNYC) | Text: Gutenberg / local `blake.txt` (bookcipher) | Yes: armada20 #4 negative (−6.104); C13 Blake Songs/Thel/Urizen | Yes (bookcipher blake.txt): NULL. Image: R22-D drop-cap negative | Local (bookcipher/books/blake.txt) |
| 9 | **Gospel of Thomas** | **C** | — | Yes: armada20 #4 | — | Local (armada20) |
| 10 | **Tao Te Ching (Legge)** | **C** — the dukotah notes flag this as "Cicada's Taoist 'the way'" (rationale only) | Legge | Yes: C12 (−6.117), armada19 (local `tao_te_ching_legge.txt`), armada20 #4 | — | Local |
| 11 | **Kybalion (Three Initiates)** | **C** — "as above so below" rationale only | 1908 | Yes: C13 hermetica lane (not in C12 download; ERR) | — | Online (Gutenberg, not fetched) |
| 12 | **Jung** (Red Book / Collected Works) | **C** — one 2019 book (Brunet, *Answer to Jung*) claims LP ↔ Jungian references (interpretive, not Cicada-confirmed) | — | **No** | **No** | Not on disk |
| 13 | **Robert Anton Wilson, *The New Inquisition* (1986)** | **C** — one secondary claim (2013 round "mixed … Crowley's Liber AL and Robert Anton Wilson's The New Inquisition") | — | **No** | **No** (ledger C-02 mentions Wilson; contents not inspected) | Not on disk |
| 14 | **Gödel, Escher, Bach** | **C/none** — no source found | — | No | No | — |
| 15 | **Zen koan collections** (Mumonkan / Gateless Gate, Blue Cliff Record) | **C/none** — no source found; the in-puzzle koans (LP1 p06, p14) are original Cicada prose | — | No (koans-as-operations negative, R22-C; LP1 koans not used as keys) | No | Mumonkan English translations: status unverified; check raw.githubusercontent mirrors |
| 16 | **"Songs of the Dead"** | **none** — zero hits in repo and no search evidence | — | — | — | — |
| 17 | **King in Yellow (Chambers)** | **C/conflation** (dukotah: flagged likely conflation) | — | No | No | Not on disk |
| 18 | **Lady of Shalott / Lady of the Fountain** | Conflicting: search snippet says 2012 book was "The Lady of Shalott"; dukotah notes say "Lady of the Fountain" (Mabinogion) | — | — | — | — |
| 19 | **Instar Emergence (2013 MP3, 761.mp3)** | **A** — the MP3 itself; hidden poem text in the 2013 cycle | Original Cicada audio | n/a (not a text key) | n/a | Local: `puzzles/2013/artifacts/761_The-Instar-Emergence.mp3` NOT present in dukotah (README only); spectrogram/reversed-audio checks reported negative by community (B) |
| 20 | **Interconnectedness (2014 MP3)** | **A** — signed 2014 audio (`corpus_2014-01-interconnectedness-hex.asc` = hex of MP3) | Original | n/a | n/a | Local: `2014/signed_interconnectedness_decoded.bin` (6.65 MB MPEG Layer III, ID3v2.3, title "Interconnectedness", artist "3301", LAME 3.98.2) |
| 21 | **Cicada's own PGP prose** (as keytext) | **A** | Local `pgp_cleartext_all.txt` | Yes: armada20 #3 (combined/individual/reversed): negative, −6.255 | — | Local |
| 22 | **Solved LP1 plaintext** (as key, runes) | **A** | `SOLVED-PAGES.json` | Yes: armada20 #1 (rune/gematria index space), R26-C (semantic seed zoo) | — | Local |
| 23 | **Dante, Lovecraft, Poe, Moby Dick, Milton, Plato, Blavatsky, Levi, Hall, KJV, etc.** | **C** — no Cicada citation; included in the armada literary sweeps as thematic nets | Local | Yes: armada18/19 (41+47 texts, skip-aware; 0 hits) | Yes (pointers into Milton, KJV): NULL | Local |
| 24 | **Beethoven** | **none** — 3 local hits, unexamined; no citation found | — | No | No | — |

---

## 3. Cicada's prose style (solved pages + signed messages; grade A unless noted)

Sources: `dukotah/liber-primus/SOLVED-PAGES.json` (5 solved LP1 pages + p56 "AN END" per dukotah notes), `pgp_cleartext_all.txt`.

- **Vocabulary**: abstract nouns in caps (DIVINITY, CIRCUMFERENCE, INSTAR, EMERGENCE, PILGRIM, ENLIGHTENMENT, CONSUMPTION, PRESERVATION, ADHERENCE, DECEPTION, PRIMES, TOTIENT, ENCRYPTED, WISDOM, KOAN, PARABLE, MOBIUS, PRIMALITY), plus Latin/philosophical fragments ("Ne te quaesiveris extra" in Self-Reliance epigraph style; LP1 p05 contains "OBSCURA FORM", "MOBIUS ANALOGUOID", "ETHEREAL CABAL", "CARNAL" as Latin-flavoured coinages).
- **Sentence patterns**: short imperative declaratives ("KWESTION ALL THINGS. DISCOVER TRUTH INSIDE YOURSELF. FOLLOW YOUR TRUTH. IMPOSE NOTHING ON OTHERS. KNOW THIS."); a repeated template "WE X BECAUSE WE BELIEVE … THIS IS THE DECEPTION / MOST THINGS ARE NOT WORTH X" (CONSUMPTION, PRESERVATION); Q&A dialogue in the koans ("WHO ARE YOU WHO WISHES TO STUDY HERE" repeated; "THAT IS NOT WHO YOU ARE THAT IS ONLY WHAT YOU ARE CALLED").
- **Sign-off formula**: "Good luck. 3301" in nearly every message. Authentication formula: "Beware false paths … verify PGP signature".
- **Runeglish orthography (A, from the solved transliteration)**: K written C (KNOW→CNOW, CIRCUMFERENCE→CIRCUMERENCE), V written U (VOICE→UOICE, DIVINITY, DISCOVER→DISCOUER), seven runes expand to digraphs TH EO NG OE AE IA EA (per SOLVED-PAGES `reading_note`). F is an interrupter (skip marker) on some pages; the transliteration drops it, so "CIRCUMFERENCE" appears as "CIRCUMERENCE". Note "THINGS" renders as "THNGS" in the solved transliteration (dukotah note) — treat that spelling as a lossy artifact to be verified against the rune canon.
- **Recurring motifs (A)**: circumference / "shed our own circumferences" (2013 MP3 poem, LP1 p14 koan); instar / emergence (2013 poem, LP1 p03, p05 sentence); "divinity within" (2013 poem, LP1 p03 "DIVINITY" key); primes and totient as sacred (LP1 p05 "THE PRIMES ARE SACRED / THE TOTIENT FUNCTION IS SACRED / ALL THINGS SHOULD BE ENCRYPTED"; @3301actual Twitter repeats it, B); numbers as direction (2016); self-trust (2014 Self-Reliance pointer).
- **Circumference provenance (C)**: Emerson "Circles" (Essays First Series) contains "centre everywhere / circumference nowhere" and "the eye is the first circle". This is a motif match, not a citation. It is covered by the armada18 Emerson run (0 hits).

---

## 4. Numerology (grade A where computed here; B where cited)

Computed locally in this session:
- 509 × 503 × 3301 = **845,145,127** (the 2012 domain 845145127.com). 509, 503, 3301, 1033 and 761 are prime (Miller-Rabin, verified).
- The 2012 end-of-puzzle P.S. number (131 digits: 1041279065891998535982789873959431895640 442510695567564373922695237268242385295908173 9834390370374475764863415203423499357108713631) is **composite** (probable-prime test fails). It has **no factor below 2,000,000**, and is not divisible by 3301. It is an untested lead (see leads).
- Solved-page prime sums (Gematria Primus values F=2 … EA=109 applied to the lossy plaintext transliteration of SOLVED-PAGES.json): page 01 = 7,409; page 05 = 7,028; page 06 = 34,459; page 03 = 17,343; page 14 = 15,150. **None is prime.** Word sums were not computed (no word boundaries in the transliteration).
- Ciphertext page prime sums (rune transcription `data/krisyotam_runes.txt`, 13,136 runes; segmentation by separator marks gives 65 segments, not 75): 6 of 65 segment sums are prime (9.2%), roughly the base rate 1/ln(13,000) ≈ 10%. **No detectable prime-sum engineering** at this segmentation. Segmentation is approximate; the test is not conclusive.

From the sources (B):
- 2012 book codes use prime-valued addresses ("the first prime" = 2, "the product of the first two primes" = 6) — documented Cicada practice. Verified in the 2012 mabinogion-book-code message text (A).
- 3301 is the 2012 "third prime" of the original image (B; 509×503×3301 check above is consistent).

---

## 5. Running-key / crib coverage — summary table (the requested table is §2)

Already tested (no hits): all 33 R12-C2 texts with skip-aware decoders (R26-B, 0/1,562 clear); 82 further texts in campaign13 (best −5.809); 15 further in campaign12 (best −6.048); armada18 (41 texts incl. Agrippa, Mabinogion, Crowley AL, Emerson, Lovecraft, Dante) and armada19 (47 texts) skip-aware; Tao, Blake, Gospel of Thomas (armada20 #4); Rune Poem (armada20 #2); Cicada PGP prose (armada20 #3); solved plaintext (armada20 #1); Self-Reliance (R24-C2-EXT, R26-B); autokey on 45 primers; ~620 keyword Vigenère; interrupter+skip on 10 texts × 55 pages (0 hits, best −5.911, p49 runepoem_oe).

Not tested (from this scout's inventory):
- Gibson's *Agrippa* (any role).
- Jung, Robert Anton Wilson, Gödel Escher Bach, Zen koan collections, Beethoven.
- Self-Reliance, Crowley AL, Mabinogion as **pointer / book-code** into LP2 with the 2012 and 2014 coordinate schemes. (The bookcipher pointer set covers Agrippa/Blake/KJV/Mabinogion/Milton only, and not with the 2014 4-tuple scheme.)
- The 2014 Interconnectedness MP3 as a carrier (spectrogram, post-frame data, ID3 fields).

---

## 6. Actionable leads (ranked by prior probability × testability)

1. **Emerson *Self-Reliance* as a paragraph:sentence:word:letter pointer (the 2014 scheme) applied to LP2 runes.** Prior: moderate–high (the same author set and scheme as the 2014 opening code, A/B). Testability: high (local `self_reliance.txt`). Steps: fix a paragraph/sentence segmentation (the 2014 code used 1:2:3:1 etc.), map each rune's value (position or prime) to a coordinate tuple, decode letters, and score with the existing quadgram pipeline with skip-aware beams. Not in the bookcipher set.
2. **Crowley *Liber AL* chapter:verse pointer applied to LP2.** Prior: moderate (the 2013 code is "dictated to a beast"; coordinates I:1:6 etc., A). Testability: high (local `crowley_book_of_the_law_hermetic.txt`; map the verse numbering first). Not yet tested as a pointer.
3. **Mabinogion (Guest 1877, Gutenberg #5160) with the 2012 tuple format (line:word, with prime expressions for addresses).** Prior: moderate (A: 2012 message). Testability: high. The prime-step (L2/W2) and line-pointer (LN) variants were already NULL, so run the **exact 2012 tuple format** (including "product of the first two primes" = 6) rather than generic prime steps. Check the Guest vs Jones 1948 edition question at the same time.
4. **Gibson, *Agrippa (A Book of the Dead)* as a book-code source.** Prior: moderate for the 2012 role; unknown for LP2. Testability: low to medium (text not on disk; the poem is copyrighted, so do not reproduce it; the UCSB Agrippa Files archive offers the ciphertext and metadata). Recommended: request legitimate access, then run the 2012 tuple scheme.
5. **2014 Interconnectedness MP3 — carrier analysis.** Prior: low–moderate (no public finding; ID3 artist "3301" in the file is A). Testability: high (local `2014/signed_interconnectedness_decoded.bin`). Checks: spectrogram; data after the last MP3 frame (note a long 0x55 'U' run near the end, which is probably LAME padding; check it); ID3 frame strings; and whether the 13.5 MB hex corpus equals the bytes of the MP3 exactly.
6. **Factor the 2012 P.S. 131-digit number** (composite; no factor < 2×10⁶; not divisible by 3301). Prior: low. Testability: medium (ECM or gmpy2 / yafu-style attack; cheap to attempt). Only worth it if the factors line up with 3301, 509, 503 or the 2012 prime clues.
7. **Crib set of Cicada motif words** (CIRCUMFERENCE, INSTAR, EMERGENCE, DIVINITY, PRIMES, TOTIENT, ENCRYPTED, PILGRIM, WISDOM) against LP2 with skip-aware decoders. Prior: low (already done as thematic cribs; controls beat thematic cribs, armada20 #14). Testability: high. Included only so the orchestrator knows it is covered.
8. **Mumonkan / Gateless Gate English translation as running key** — low prior (no Cicada citation found), testability medium (need raw mirror). Low priority.
9. **Jung (Red Book), Robert Anton Wilson (*New Inquisition*) as running keys** — low prior (single secondary claims), testability low (not on disk).
10. **Emerson "Circles" alone as a running key** — low prior; the full Essays run already covered it (armada18 0 hits). Only worth doing if the orchestrator wants a sub-text control.

---

## Sources

Primary/local (A):
- `dukotah/corpus/A-primary-artifacts/pgp/messages/` (2012-01 book-code-poem, mabinogion-book-code, end-of-puzzle, location-numbers; 2013-01 opening-book-code; 2014-01 opening-book-code, magic-square-upload-outguess-*, onion5, interconnectedness hex; 2016-01 liber-primus; 2017-04 final-warning).
- `dukotah/liber-primus/SOLVED-PAGES.json`, `dukotah/liber-primus/data/keys/armada18/`, `armada19/`, `self_reliance.txt`, `runepoem_oe.txt`, `dukotah/liber-primus/data/krisyotam_runes.txt`.
- `dukotah/corpus/A-primary-artifacts/2014/signed_interconnectedness_decoded.bin` (ID3/LAME header, computed here).

Ledger/analysis (A for what was run):
- `dukotah/liber-primus/LEDGER.json` (R12-C2, R26-B, R24-C2-*, R22-B, R22-C, R22-D, R28-L1, R20-*).
- `dukotah/liber-primus/analysis/ARMADA-20-FINDINGS.md`; `analysis/CAMPAIGN-XII-FINDINGS.md`; `analysis/CAMPAIGN-XIII-FINDINGS.md`; `analysis/campaign18_skip/CAMPAIGN-XVIII-FINDINGS.md`; `analysis/campaign12/keytext_manifest.json`; `analysis/campaign13/sweep_results.json`; `analysis/bookcipher/bookcipher.py`.
- `dukotah/research/01-origins-2012.md`, `02-puzzle-2013.md`, `03-puzzle-2014-liber-primus.md` (secondary notes, used for context only).

Web (B/C, searched this session):
- Gibson *Agrippa*: https://en.wikipedia.org/wiki/Agrippa_(A_Book_of_the_Dead) ; https://agrippa.english.ucsb.edu/?p=227 ; https://themillions.com/2012/07/unlocking-agrippa.html
- 2014 Self-Reliance and Blake pairing: https://nahgcorp.substack.com/p/part-2-the-internets-most-beautiful ; https://wnyc.org/story/heres-how-to-start-solving-new-cicada-3301-puzzle-2014/
- Mabinogion editions: https://gutenberg.org/files/5160/5160-h/5160-h.htm ; https://gutenberg.org/cache/epub/19959/pg19959-images.html ; https://gutenberg.org/cache/epub/19976/pg19976-images.html ; https://www.gutenberg.org/ebooks/19959.epub.noimages
- Jung/Brunet: https://oalib-perpustakaan.upi.edu/Record/doab_20_500_12854_77301
- Wilson *New Inquisition* claim and Gödel/Escher/Bach absence: search results (no direct URL pinned; see Wikipedia https://en.wikipedia.org/wiki/Cicada_3301)
- Interconnectedness / 2014 round: https://en.wikipedia.org/wiki/Cicada_3301 ; https://www.ilpost.it/2014/01/07/enigma-cicada-3301-2014/
- Liber Primus overview: https://www.boxentriq.com/guides/cicada-3301-liber-primus ; https://github.com/krisyotam/cicada3301
- Mumonkan background (no Cicada link found): https://tricycle.org/magazine/what-is-a-koan/
