# Lane P: Cicada-scoped hash hunt for the page-56 target (round two, 2026-10-16)

**Verdict: null.** Every text capture the Wayback Machine holds for the four onion hosts named in Cicada's own
PGP-signed messages was fetched and hashed. None hashes to the page-56 target under any of the six functions and
~160 normalisations `hashhunt` tests. Common Crawl was not covered: its index returned HTTP 504 for every request
during the run, including trivial lookups on recent crawls.

## Scope (and why it is this narrow)

Round one built `hashhunt` but could not reach the archives. This round the network reached `web.archive.org` and
`index.commoncrawl.org`, so the tool was run for the first time against the real services.

It ran in the new **allowlist mode** only (`hashhunt/README.md`, "Scope"). Gateway-wide queries return rows for every
onion site an archive ever saw, and an onion address says nothing about the site behind it. The tool therefore asked
the archives only about named hosts, dropped any off-list row before writing it, and never fetched off-list captures.
Selftest section 5 checks this against a mocked archive that misbehaves on purpose (39/39 checks pass).

The allowlist is the four labels named in a Cicada-signed message, each signature re-verified (GOODSIG, key
`6D854CD7933322A601C3286D181F01E57A35090F`) by the provenance pass in `hashhunt/cicada_onions.md`:

| label | step | evidence |
|---|---|---|
| sq6wmgv2zcsrix6t | 2012 enrollment page | `pgp/messages/2012-01-anonymous-email-enrollment.asc:14` |
| xsxnaksict6egxkq | 2013 telnet-hello | `pgp/messages/2013-01-telnet-hello.asc:9` |
| pklmx2eeh6fjt7zf | 2013 onion pointer | `pgp/messages/2013-01-onion-pointer.asc:7` |
| ky2khlqdf7qdznac | 2014 welcome onion | `pgp/messages/2014-01-onion-welcome.asc:6` |

(paths under `dl/dukotah/corpus/A-primary-artifacts/`). Sixteen more labels are attributed to Cicada only by the
community record, including the 2014 onions 1 to 6. They are documented in `cicada_onions.md` and were **not**
queried. Widening the list is a decision for the project owner; the 2013 physical-drop onions should stay off it in
any case (the wiki that lists them warns they may be unrelated).

## Run

| stage | numbers |
|---|---|
| Wayback CDX plan | 80 queries = 4 labels x (9 gateways + bare `.onion`) x {text/html, text/plain}, 2013 to 2017, status 200, `collapse=digest`. All 80 completed; 0 off-list rows returned. |
| captures found | 3: `ky2khlqdf7qdznac.onion.to/` (2015-05-25, text/html, 842 B), `ky2khlqdf7qdznac.onion.to/robots.txt` (2017-07-13, 75 B), `pklmx2eeh6fjt7zf.onion.to/robots.txt` (2017-07-13, same digest as the first robots.txt) |
| fetch | 2 ok (Wayback `id_` original bytes; both sha1 equal the CDX digest), 1 dedup by digest |
| hash | 2 captures; 672 and 780 (normalisation, function) tuples; functions sha512, sha3_512, blake2b512, BLAKE-512, Whirlpool, Skein-512-512 (all KAT-verified at start); **0 matches** |
| Common Crawl | 1,044 host-scoped queries planned (29 crawls 2013 to 2016 x 9 gateways x 4 labels). Not run: HTTP 504 on every request, including `CC-MAIN-2024-10` lookups for `archive.org`; stopped rather than retried against a failing service |

The 2015 root capture is the gateway's "temporarily not available" placeholder that the community already recorded
(`hashhunt/NOTES.md` section 2). Nothing here contradicts the community's conclusion that Wayback never held real
Cicada content for these hosts.

## What this adds to the community record

The community's per-host Wayback lookups used 9 gateway suffixes with `limit=3000` and SHA-512-family hashing of the
raw files. This run adds the original BLAKE-512, Whirlpool and Skein over ~160 page representations (banner-stripped,
body-only, CRLF/LF/trailing-newline forms, visible-text forms, host-name forms) of the captures, plus three gateways
they did not query (`onion.nu`, `onion.lu`, `tor2web.fi`), which held nothing. It is a small, clean negative.

## Reproduce

```
python -I hashhunt/hashhunt.py selftest
python -I hashhunt/hashhunt.py --dir hashhunt/data --allowlist hashhunt/cicada_onions_allowlist.txt --contact you@example.org plan --no-cc --run
python -I hashhunt/hashhunt.py --dir hashhunt/data --allowlist hashhunt/cicada_onions_allowlist.txt --contact you@example.org fetch
python -I hashhunt/hashhunt.py --dir hashhunt/data hash --jobs 3
```

Common Crawl, when its index is back: the same `plan` with `--no-wayback` in place of `--no-cc`, then `fetch` and `hash`.
