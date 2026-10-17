# What the community already hashed (so you do not redo it)

Target: `36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4`
(Liber Primus p.56 "AN END": "WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO ...", no algorithm, no address.)

Sources read: `SCRATCH/dl/leo/outguess/{hash_hunt.py,RESULTS.md}` and a grep of `SCRATCH/dl/dukotah` for
`hash_hunt`, `36367763`, `tor2web`, `onion.to`, `cdx` (the useful hits are listed per row below). Everything here is
second-hand from those write-ups and scripts; none of it was re-run. Where a claim comes only from a prose summary and
I could not see the script, it says "(summary only)".

## 1. Function x input matrix (all NULL; nothing has ever matched)

| Work (where) | Inputs hashed | Functions | Normalisations | Count |
|---|---|---|---|---|
| `leo/outguess/hash_hunt.py` (RESULTS.md s.2, run 2026-09-07) | every file of the 2012-17 archive; 41 Cicada phrases ("3301", "liber primus", "an end", "welcome pilgrim", key ids ...); the 13 onion addresses found in the archive; every non-empty line of every text file; 4,521 outguess payloads | **SHA-512 only** | files: raw, CRLF->LF, strip, CRLF->LF+strip+"\n"; strings and onion names: scheme `""/http:///https://` x suffix `""/"/"/"\n"/"/\n"/"\r\n"`, each also UPPER-cased (30 variants) | 692,438 |
| `dukotah/.../pp49_51/hash_hunt.py` (Campaign XVII s.1; re-run in round19/C1 with a positive control) | the pp49-51 2048-bit data object (`canon_256.bin`, two canonical variants), runic ciphertext of the unsolved pages (UTF-8 and index bytes) | sha512, sha256, sha384, sha3_512, sha3_256, blake2b, blake2s, shake_256(64), md5, sha1 | raw, reversed, hex lower/upper, +"\n", hex-file raw/stripped; **also accepts truncated/prefix matches** (a flipped last nibble still prints PARTIAL) | 140 (50 in the C1 re-run) |
| `pp49_51/anend_preimage_broad.py` | all solved-page plaintexts, PGP prose blocks, koans, `canon_256` + quarters | sha512/256/384, sha3_512/256, blake2b, blake2s, shake_256, md5, sha1, ripemd160 | raw, +"\n", stripped, upper, lower, no-spaces, rune-transliterated, reversed | (summary only) |
| `pp49_51/blake_closure/` (2026-07-28) | same candidate set (78 text + 14 binary objects) | **original BLAKE-512** and BLAKE-256, KAT-validated (1x00, 144x00 bytes; same vectors as here) | raw/strip/strip+nl/nospace/upper/lower/reversed/transliterated; binaries also rev/+nl/hex/HEX | 1,572 |
| ledger "reopened preimage gate" (iter 6, 2026-07-29) | every held blob + internal candidate set | **Skein-512-512, Whirlpool, Streebog-512** (KAT-validated) | whole-file, byte/digest orientation | 2,658 |
| `anend_hunt/repr_hashscan.py` (2026-08) | 77 held files: iBotPeaches onion1-7 captures, held onion/wiki HTML, decrypted AN-END/PARABLE text | sha512, sha3_512, blake2b512 | raw, utf8, CRLF->LF, rstrip("\n"), strip, **HTML->visible text (regex tag strip + unescape)**, whitespace-collapsed, collapsed+UPPER, alnum, alnum-UPPER, letters-UPPER | 2,574 |
| same, vs the *original* 2014 captures from `micheloosterhof/cicada-2014` (server-status, index.html.2, onion7 index) | 3 files | same 3 | same | 132 |
| ledger / iter-4 archival sweep | IA 2020 re-uploads of 5 of the 8 Cicada onions (onion7 `index.html`, the 256-byte RSA blob raw+hex) | sha512 (summary only) | raw + hex | few |
| `campaign7/b4_hash_kdf.py` | the *target itself* as a key seed (SHA-512/BLAKE2b chains, SHAKE-256) | - | - | not a preimage test |
| Outside community: `cicada-solvers/Cicada-DWH-HashcatAttempts` (vendored logs summarised in `corpus/E-tooling/CROSSCHECK-CICADA-SOLVERS.md`) | hashcat mask spaces: **IPv4 addresses, all-bytes length 1-5, US phone numbers** | sha512, sha3-512, blake2b-512, whirlpool, streebog | masks only | 0 matches, last activity 2025-10-29 |
| Outside community: `tweqx/3301-hash-alarm` (summary only) | passive detector over ~15 families incl. SHA-512, BLAKE2b, BLAKE-512, SHA-3, Streebog, Skein, Whirlpool | - | - | never fired; dormant since 2021 |

Closed-by-argument leads (not hash runs): CT-log brute force (non-viable: CT logs hold CA-issued names, not page
bodies); "hash = v2-onion payload" (monokro.me 2024; refuted: first-80-bit base32 gives `gy3hoy5lon4dy6xs`, not the
claimed address); "ed25519/v3 onion" (anachronistic); `gy3hoy2zizvuzvdb.onion` (search-summary hallucination).

## 2. Sources the community did and did not look at

Done:
* **Wayback CDX, per known host only.** `corpus/D-archives` built 354 queries: core Cicada domains plus 33 known
  onion labels x 9 suffixes (`""`(.onion), `.to .link .city .cab .direct .lt .sh .ws`), `matchType=domain`,
  `collapse=digest`, `limit=3000` (4 non-onion queries - wiki, boards, reddit - hit the 3,000 row cap and were never paginated). Result over all 354:
  15,474 distinct URLs / 25,064 captures. The 14 `*_to.json` files hold **256 rows** (~18 per host): 109 are `unk`/302,
  90 `text/plain` 200 (mostly `robots.txt`), 6 `text/html` 200, rest images/js/css/500s.
* The known Cicada host `ky2khlqdf7qdznac.onion.to` has 14 rows: a 2015 "temporarily not available" placeholder, a 302
  and `robots.txt`. Captured bodies for onion hosts are dominated by gateway failure pages ("Tor2web Error",
  "OnionLink: Could not connect", "503 Backend fetch failed"). Their conclusion: Wayback never held real Cicada
  content even for a known onion.
* IA items for 5 of 8 Cicada onions (2020 community re-uploads, byte-identical to repo copies); the onion.link /
  onion.city IA WARC item (4 items, 0 Cicada onions).

NOT done (this is where `hashhunt` adds something):
* **Blind discovery** of unknown onion hosts on any gateway. The 2026-08 hunt reports Wayback rejects
  wildcard/"any-onion" CDX queries (HTTP 403, auth required), so only lookup of known hosts was possible. `hashhunt plan`
  still issues the `matchType=domain` queries (cheap to try; a refusal is logged with a hint) and offers a fallback:
  harvest onion labels from Common Crawl, then query Wayback per host (`--hosts-from-captures`).
* **Common Crawl**: "not queried at all" (D-archives GAPS-D.md).
* **Pagination** past 3,000 rows (`showResumeKey`).
* **Any tor2web-banner handling.** No script stripped gateway-injected markup or un-proxied `.onion.to` links.
* **CRLF/LF/trailing-newline variants of an HTML capture** beyond the simple 4 above, and body-only / after-`<html`
  views.
* **Original BLAKE-512, Skein, Whirlpool over page-representations** (they were only run on raw held blobs and
  internal candidates; the representation scan used only the three hashlib functions).
* **The URL / bare onion hostname of unknown hosts** (only the 13 archive-resident addresses were hashed).
* Streebog-512 (GOST R 34.11-2012) over anything fetched: not implemented in `hashhunt` (extension point, see README).

## 3. Cautions inherited from the community record

* The CDX `digest` is unreliable as a byte-identity claim (19 cases: different digests, identical payloads) and CDX
  `length` is the compressed record size. `hashhunt` only uses `digest` to skip fetches and dedups again on content.
* `pp49_51/hash_hunt.py` counts a prefix match as PARTIAL; `hashhunt` matches full 512-bit digests only.
* "SHA-512" is a community default, not sourced: the page names no algorithm.
