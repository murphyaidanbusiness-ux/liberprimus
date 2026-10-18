# hashhunt

Offline hash hunt for the Cicada 3301 Liber Primus page-56 target

```
36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4
```

Question asked of every stored capture: do its bytes, under any of ~160 normalisations, hash to the target with
SHA-512, SHA3-512, BLAKE2b-512, original BLAKE-512, Whirlpool or Skein-512-512? (The page names no algorithm; see
`NOTES.md` for what the community already tried, so you do not repeat it.)

Python 3.8+, standard library only. Files: `hashhunt.py` (CLI, network, store, hash stage, selftest),
`hashfuncs.py` (pure-Python BLAKE-512 / Whirlpool / Skein-512-512 and their test vectors).

## Scope: the allowlist mode (required)

`plan` and `fetch` refuse to run unless you pass either `--allowlist FILE` or an explicit `--blind`. Use the allowlist.

An onion address says nothing about what is behind it. A gateway-wide query (`url=onion.to&matchType=domain`) returns
rows for every onion site the archive ever saw through that gateway, and fetching them would mean downloading unknown
darknet content. With `--allowlist FILE` (one onion label per line, `#` comments):

* every Wayback query is `matchType=host` for one allowlisted label on one gateway (or bare `.onion`); every Common
  Crawl query is `url=<label>.<gateway>&matchType=host`. No domain-wide or wildcard query is ever sent;
* any row an archive returns for a host off the list is dropped before anything is written (counted as `offlist` in
  `plan_state.jsonl`; the URL itself is not stored);
* `fetch` never downloads a capture whose host is off the list, even if one is in `captures.jsonl` from an earlier run;
* `--hosts-from-captures` and `--all-hosts` (both widen the scope) are refused.

`cicada_onions_allowlist.txt` holds the four labels named in Cicada PGP-signed messages, with the evidence in
`cicada_onions.md` (2012 enrollment page, the two 2013 onions, the 2014 welcome onion). `cicada_onions.md` also records
the community-attributed 2014 onions 1 to 6, which are **not** on the list: they are well documented but no signed
message names them. Selftest section 5 checks all of the above against a mocked archive that misbehaves on purpose.

```
python -I hashhunt.py --dir data --allowlist cicada_onions_allowlist.txt --contact you@example.org plan --run
python -I hashhunt.py --dir data --allowlist cicada_onions_allowlist.txt --contact you@example.org fetch
python -I hashhunt.py --dir data hash --jobs 4
```

## Safety boundaries (by construction)

* **Text only.** Only `text/html`, `text/plain` (plan) and `application/xhtml+xml` (fetch gate) are accepted. The
  server's Content-Type is never trusted alone: known binary magic numbers (PNG, JPEG, GIF, PDF, ZIP, ELF, MZ ...)
  are refused even when labelled text. Anything else is logged as `refused_type:*` / `refused_binary` and **not stored**.
* **5 MB cap** per capture, enforced while reading (a larger body is dropped, never buffered whole); WARC and gzip
  decompression are size-capped too, so a decompression bomb is refused.
* **Never executed, never rendered, never opened.** Stored bytes are only read as bytes and hashed. Text extraction
  uses `html.parser`, which does not run scripts or fetch resources. No Tor, no `.onion` access, no browser.
* **Surface-web archives only.** Network access is limited to an allowlist (`web.archive.org`, `*.archive.org`,
  `index.commoncrawl.org`, `data.commoncrawl.org`) over https; redirects off the list are refused (`--allow-host` to
  widen deliberately). It never contacts a gateway or an onion host.
* Archive-derived strings (URLs) are sanitised before printing, so a hostile URL cannot inject terminal escapes.
* Rate-limited (default 2 s between requests), exponential backoff on 429/5xx/network errors (4, 8, 16 ... s, capped
  at 300 s, honours `Retry-After`). Set `--contact you@example.org` (or `HASHHUNT_CONTACT`) so archive operators can
  reach you from the User-Agent.

### If you get a MATCH

The tool prints a banner and appends the full record to `results/matches.jsonl`. **Do not open, render, run or share
the stored file, and do not browse to the archive URL.** The page is unknown content from the darknet era. Copy the
banner / the `matches.jsonl` line (capture id, original URL, timestamp, source, function, normalisation, digest) and
report that provenance. Anyone can verify independently by hashing the bytes at the stated archive location. A
match from a function marked `UNVERIFIED` should be re-checked with a second implementation first.

## Install / run

No install. Use isolated mode so Python does not import anything from the current directory (the working data
directory holds untrusted downloads):

```
python3 -I hashhunt.py selftest                      # run this first; ~1 s
python3 -I hashhunt.py --allowlist cicada_onions_allowlist.txt --contact you@example.org plan --run   # candidate list (network)
python3 -I hashhunt.py --allowlist cicada_onions_allowlist.txt --contact you@example.org fetch        # original bytes (network)
python3 -I hashhunt.py hash --jobs 8                          # offline; prints MATCH loudly
```

All stages are **resumable**: state is append-only JSONL under `--dir` (default `./hashhunt_data`); rerun the same
command to continue after Ctrl-C or a crash. Torn final lines are ignored.

### 1. `plan`

Without `--run` it only writes `queries.json` (279 queries by default) and prints a count; no network is used. Each entry has the full
URL, e.g.

```
https://web.archive.org/cdx/search/cdx?url=onion.to&matchType=domain&from=2013&to=2017&filter=mimetype:text/html
  &filter=statuscode:200&fl=timestamp,original,mimetype,statuscode,digest,length&collapse=digest&output=json
  &showResumeKey=true&limit=5000                       (+&resumeKey=... until none)
https://index.commoncrawl.org/CC-MAIN-2015-18-index?url=*.onion.to&output=json&filter=mime:text/(html|plain)
  &filter==status:200                                  (&showNumPages=true, then &page=0..N-1)
```

* Wayback: 9 gateways (`onion.to onion.cab tor2web.org onion.link onion.city onion.nu onion.lu onion.sh tor2web.fi`;
  `--extra-gateways` adds `tor2web.io onion.ws`; `--gateways a,b` overrides) x {`text/html`, `text/plain`},
  `matchType=domain`, 2013-2017, paginated with `showResumeKey` / `resumeKey`.
* Common Crawl: CC-MAIN-2013-20 ... CC-MAIN-2016-50 (static list of 29; `--discover-cc` reads the authoritative list
  from `collinfo.json`) x 9 gateways, `page=` pagination. CC captures are later fetched by **byte range** from
  `https://data.commoncrawl.org/<filename>` (`Range: bytes=offset-offset+length-1`); each range is one gzip WARC
  member.
* `--run` executes the queries and appends to `captures.jsonl` (the candidate manifest; one capture per line) and
  `plan_state.jsonl`; `manifest.json` summarises. Rows are re-filtered client-side (mime, status), so a server that
  ignores a filter cannot widen the scope. `--status any` drops the HTTP 200 filter. `--only TEXT` runs queries whose
  id contains TEXT; `--max-requests`, `--max-pages` bound a run.
* Fallback if Wayback refuses wildcard/domain queries (a 2026 community note reports HTTP 403 for blind queries):
  run the Common Crawl half first (`--no-wayback`), then `plan --run --no-cc --hosts-from-captures` (or
  `--hosts-file labels.txt`) to ask Wayback host by host (`matchType=host`).

### 2. `fetch`

For each candidate: Wayback `https://web.archive.org/web/<ts>id_/<original>` (the `id_` flag returns the unmodified
captured bytes) or the CC byte range, parsed with stdlib `zlib` as a WARC record (`WARC-Type: response`, HTTP
status 200, chunked transfer decoded, truncated records skipped). Stored as `store/<sha256(url+timestamp)>.bin` plus a
sidecar `.json` (provenance, content type, as-served length, sha256, base32-sha1 and whether it equals the CDX
digest). Skips hosts that do not carry a 16- or 56-char onion label (`--all-hosts` to include gateway home pages),
dedups by CDX digest before downloading and by content hash after, and logs every outcome to `fetch_log.jsonl`
(`ok`, `dup_digest`, `dup_content`, `refused_*`, `too_large`, `truncated`, `http_4xx`, `error`; `error` is retried on
the next run). The bytes kept are **as served**; gzip content-encoding is not undone here (the hash stage hashes both).

### 3. `hash`

For every stored capture, builds the variants below, hashes each unique byte string with each selected function and
compares to the target plus `--targets FILE` (`<128 hex> [label]` per line, `#` comments). Output:
`results/hash_results.jsonl`, one line per capture, listing **every (normalisation, function, first 12 hex of the
digest)** tuple; matches additionally go to `results/matches.jsonl` with the full digest. Resumes by capture, keyed to
a fingerprint of (functions, tier, targets, normaliser version); changing any of these re-hashes.

Normalisations (`view/whitespace`; names appear in the results):

| Group | Variants |
|---|---|
| roots | as-served bytes; gzip/zlib-decompressed bytes (`gz:` prefix) when the body is compressed (then the served root contributes just the literal bytes) |
| views | `raw`; `nobanner`; `from_html` (everything from the first `<html`); `body_inner` (inside `<body>` ... last `</body>`); `unproxied` (`x.onion.to` -> `x.onion` link rewrite); and `nobanner` combined with each |
| whitespace | `as_is`, `lf` (CRLF->LF), `crlf` (LF->CRLF), each with tails `rstrip`, `rstrip+nl`, `add_nl`, `strip` |
| text | visible text (head/script/style removed) and all text, from raw / nobanner / body_inner, as: whitespace-collapsed, +"\n", line-per-block, +"\n", lower-cased collapsed, +"\n" |
| identity | the URL (and +"\n"); bare onion hostname with/without `.onion`, `http://x.onion`, `http://x.onion/`, gateway host; each with and without "\n" |

Tor2web banner stripping (`nobanner`) is a best-effort regex set: injected `<script>`/`<link>`/`<style>` that mention
`antanistaticmap` / `tor2web` / `onionlink`, HTML comments mentioning them, and (with nesting) `<div>` blocks whose tag
mentions `tor2web`/`t2w`/`antanistaticmap`; one trailing newline after a removed element is removed too. Evidence for the
patterns: archived gateway pages reference `/antanistaticmap/tor2web.js`, `tor2web.css` and `tor2web-small.png`
(seen in Wayback CDX listings for `*.onion.to`), and gateways rewrite onion links. The exact 2013-2016 banner markup
is **not verified** against a real capture; that is why the unconditional `from_html`, `body_inner` and text views exist.
Tiny gateway error pages ("Tor2web Error", "OnionLink: Could not connect", "503 Backend fetch failed") are skipped
unless `--no-skip-errors`.

Speed: SHA-2/SHA-3/BLAKE2 are native. The pure-Python functions cost about 1-3 us/byte each, so a 30 KB page with ~20
distinct core variants takes ~4 s for all three. By default they run only on **tier-1** variants (raw/nobanner x
5 whitespace forms, 4 visible-text forms, identity strings); `--pure-tier 2` runs them on everything, `--funcs
sha512,sha3_512,blake2b512` drops them, `--jobs N` uses N processes.

### 4. `selftest`

Runs offline in a temp dir (`--keep` to retain it): (1) test vectors for every function; (2) the Wayback JSON/resumeKey,
Common Crawl NDJSON, dechunk, query-builder, allowlist and content-gate checks on hand-written samples (modelled on
the real CDX rows in the community's `corpus/D-archives/cdx`); (3) a mocked HTTP layer end to end: 429 then 503
(`Retry-After`) backoff, resume from a stored `resumeKey`, Wayback `id_` and CC byte-range + gzip WARC fetch, image
refusal, digest/content dedup, size cap; (4) plants a fake banner-injected page, puts SHA-512 of its cleaned form (and
one digest per other function, and a host-name digest) in a targets file, runs `hash` on the store and requires all of
them found under the expected normalisation, with a decoy target and an unrelated-target negative control that must
stay silent, plus gzip-root and `--jobs 2` checks.

## Verification status of the hash functions

| function | status | evidence |
|---|---|---|
| sha512, sha3_512, blake2b512 | hashlib | stdlib |
| blake512 (original BLAKE) | **verified** | `""` and `00` (given in the brief), 144 x `00` (BLAKE spec 2nd KAT; same value the community's `blake_closure` asserts). Padding branches for message length mod 128 = 111 and >= 112 have no vector here; they follow the spec but are untested |
| whirlpool | **verified** | empty, "abc", quick-brown-fox, plus 31- and 100-byte inputs cross-checked against OpenSSL's legacy provider; 14 further lengths 0-5000 B also matched OpenSSL during development |
| skein512 (Skein-512-512 v1.3) | **verified** | KATs for empty, `FF` and the 128-byte `FF..80` message (two blocks) |

`run_vectors()` runs at every `hash` start; a function that fails is flagged `UNVERIFIED` in warnings and in match banners.

## Expected scale (reasoning, not measurement; the real numbers are unknown until you run `plan --run`)

* The community's per-host Wayback lookups (see `NOTES.md`) found ~18 CDX rows per known onion host on `onion.to`,
  of which ~37% were status-200 text captures (mostly `robots.txt` and gateway error pages). If Wayback holds H
  distinct onion labels across all gateways, expect on the order of 3-4 x H fetchable text captures before dedup.
  H is not known: anything from a few thousand to a few hundred thousand is plausible, so **10^3 to 10^5-10^6
  captures**. Common Crawl contributes far fewer (its 2013-16 crawls rarely touched gateways). `collapse=digest` and
  the dedup step shrink this, and gateway failure pages dominate what is left.
* Cost: fetch ~ N x (delay + latency) = about 3 s per capture at defaults, e.g. 100,000 captures ~ 3.5 days; raise
  `--delay` if you see 429s, lower it only if the operators allow. Storage ~ N x (10-50 KB). Hashing ~ 1-4 s per
  capture for all functions at tier 1 on one core.
* Hit probability is low: the page must (a) have been crawled by a surface archive through a gateway, (b) been served
  successfully, (c) hash to the target under one of the tested byte forms. The community concluded Wayback never held
  real content even for a known Cicada onion. A clean null over a large sample is the likely result; it is still a
  new, documented negative.

## Extending

* **More targets**: put them in a file (`<128 hex> [label]`) and pass `--targets`. Only 512-bit digests are compared
  (full-length equality; no prefix matching, deliberately).
* **A hash function**: add `def myhash(data: bytes) -> bytes` (64-byte output) to `hashfuncs.py`, register it in
  `FUNCS` as `"name": (myhash, True)` (True = pure-Python, tiered), and add at least one published test vector to
  `VECTORS`. Streebog-512 and original Keccak-512 are natural next ones. It is selected by `--funcs` and covered by
  `selftest` once it is in `FUNCS`; unverified functions are flagged automatically.
* **A normalisation**: add it to `all_variants()` (`out["my/name"] = (bytes, tier)`), bump `NORM_VERSION` so old
  results are not treated as complete, and add a plant to `selftest` section 4.
* **Gateways / collections**: `--gateways`, `--extra-gateways`, `--hosts-file`, `--discover-cc`.

## What has and has not been run against the real services

Round two (2026-10-16) ran `plan`, `fetch` and `hash` live against the Wayback Machine in allowlist mode
(`agents/laneP_hashhunt/RESULTS.md`): the Wayback JSON layout, host-scoped CDX queries, `id_` fetches and the CDX digest
check all behaved as designed. A transient Windows file lock (`OSError: [Errno 22]` on append) is now retried. Common
Crawl's index returned HTTP 504 for every request that day, so the CC half is still exercised only against mocks.

Originally the sandbox could not reach archive.org or commoncrawl.org. The following come from the public API docs and
recollection and, for Common Crawl, are still exercised only against mocks: the Wayback JSON layout `[header, rows..., [], [resumeKey]]` and that the resume
key is already percent-encoded (it is passed through verbatim); `to=2017` covering all of 2017; `showNumPages` and
`page=` for CC; CC filter syntax (`filter=mime:regex`, `filter==status:200`; use `--no-server-filter` if rejected);
`data.commoncrawl.org` serving ranges directly (a redirect to another host would be refused; `--allow-host`). If a
first live run shows a parse or 4xx pattern, `plan_state.jsonl` records the HTTP status and the raw query URL is in
`queries.json`; fix the one function and resume.
