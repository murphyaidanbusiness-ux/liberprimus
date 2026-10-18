# Cicada onion labels: provenance check

Checked 2026-10-16 from local files only. No network, no onion or gateway access.
Scope: the 33 labels in `dl/dukotah/corpus/D-archives/build_targets.py` (`onions`), which includes `gy3hoy2zizvuzvdb`.
Paths below are repo-relative. Line numbers are 1-based.

## Counts

| Verdict | Count | Labels |
|---|---|---|
| CICADA-PRIMARY | 4 | sq6wmgv2zcsrix6t, xsxnaksict6egxkq, pklmx2eeh6fjt7zf, ky2khlqdf7qdznac |
| COMMUNITY-ONLY | 16 | auqgnxjtvdbll3pv, cu343l33nqaekrnw, fv7lyucmeozzd5j4, avowyfgl5lkzfj3n, q4utgdi2n4m4uim5, ut3qtzbrvs7dtvzp, p7amjopgric7dfdi, emiwp4muu2ktwknf, gbyh7znm6c7ezsmr, y2wyuvrqraowagc5, cginiziglyaobyph, 4l6uipnstbggwjyv, wzwmcwmsk5cb7gjn, vj7suk6t5bfjugdv, qw7mhchzvuq6f2mf, erwfcsdvx6pm2rsk |
| UNKNOWN | 12 | 5fpp2orjc2ejd2g7, lwplxqzvmgu43uff, yniir5c6cmuwslfl, rjzdqt4z3z3xo73h, n5gvslqnb4yomt6q, bah37war75xzkpla, bljflz7gy23uv73l, dbwkwbdidiwbwfau, dxwd42hgpd7qrccm, a6d7f6hjfg6eyrye, 5qcyeerbnina7esx, 2lol7ha4j442rqeg |
| NOT-CICADA | 1 | gy3hoy2zizvuzvdb |

Allowlist: `hashhunt/cicada_onions_allowlist.txt` (the 4 CICADA-PRIMARY labels only).

## Method

- **Primary artifact** means a Cicada PGP-signed message in `dl/dukotah/corpus/A-primary-artifacts/pgp/messages/` or `.../ibotpeaches/messages/`. Each of the four cited files was re-verified here with gpg 2.4.9 in a throwaway keyring, using the repo's key copy `pgp/keys/cicada-3301-pubkey.keyserver.ubuntu.com.asc`. Fingerprint `6D854CD7933322A601C3286D181F01E57A35090F`, uid "Cicada 3301 (845145127)". Result: GOODSIG on all four. The keys.openpgp.org copy has no user ID, so gpg skips it.
- A GOODSIG shows the message was made by that key. It does not establish that Cicada holds the key. Trust is TRUST_UNDEFINED.
- The search covered all of `dl/`. CDX lookup files, `targets.tsv`, `build_targets.py`, `TIMELINE.json`, `MANIFEST.json`, and `_logs/` are lookup or index entries. They are not evidence of a label's status.
- Extra labels: a scan of primary human-readable text (`pgp/messages`, `ibotpeaches/messages`, `2014/`, `2016-2017/`, `signed-payloads/`) found no 16-char onion label beyond the four above. The other hits are PGP base64 fragments. No additional candidates qualify.

## Table

| Label | Verdict | Year / step | Evidence (path:line, quoted) |
|---|---|---|---|
| sq6wmgv2zcsrix6t | CICADA-PRIMARY | 2012, enrollment page (community: "RSA/MIDI Onion") | `dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2012-01-anonymous-email-enrollment.asc:14`: `"http://sq6wmgv2zcsrix6t.onion/3894894230934209")`. GOODSIG. Same line also at `dl/dukotah/corpus/A-primary-artifacts/ibotpeaches/messages/2012/congratulations.asc:14`. |
| xsxnaksict6egxkq | CICADA-PRIMARY | 2013, telnet-hello step | `dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2013-01-telnet-hello.asc:9`: `xsxnaksict6egxkq.onion` (signed "Very good. You have done well to come this far."). GOODSIG. Copies at `ibotpeaches/messages/2013/very-good.asc:9` and `pgp/messages/ky_2013-01-telnet-hello.asc:9`. |
| pklmx2eeh6fjt7zf | CICADA-PRIMARY | 2013, onion-pointer step | `dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2013-01-onion-pointer.asc:7`: `pklmx2eeh6fjt7zf.onion` (signed "Well done. You have come far."). GOODSIG. Copy at `ibotpeaches/messages/2013/well-done-you-have-come-far.asc:7`. |
| ky2khlqdf7qdznac | CICADA-PRIMARY | 2014, onion welcome message (community: "Onion 7") | `dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2014-01-onion-welcome.asc:6`: `ky2khlqdf7qdznac.onion` (signed "Hello. Your enlightenment awaits you."). GOODSIG. Copies at `ibotpeaches/messages/2014/hello-your-enlightenment.asc:6` and `pgp/messages/ky_2014-01-final-message.asc:6`. |
| auqgnxjtvdbll3pv | COMMUNITY-ONLY | 2014, "Onion 1" (community) | `dl/dukotah/corpus/C-community/wikis/uncovering-cicada/export_cur_00020.xml:1680`: "onion 1 Apache Server at auqgnxjtvdbll3pv.onion Port 5240". Numbering from `dl/dukotah/liber-primus/analysis/armada_osint/onions_ibotpeaches/MANIFEST.md` (inventory table). |
| cu343l33nqaekrnw | COMMUNITY-ONLY | 2014, "Onion 2" (community) | `.../export_cur_00020.xml:1681`: "onion 2 Apache Server at cu343l33nqaekrnw.onion Port 5241". |
| fv7lyucmeozzd5j4 | COMMUNITY-ONLY | 2014, "Onion 3" (community) | `.../export_cur_00020.xml:1682`: "onion 3 Apache Server at fv7lyucmeozzd5j4.onion Port 5242". |
| avowyfgl5lkzfj3n | COMMUNITY-ONLY | 2014, "Onion 4" (community) | `.../export_cur_00020.xml:63`: "[https://avowyfgl5lkzfj3n.onion Onion 4] came online again" (after 29/01/2014 UTC). |
| q4utgdi2n4m4uim5 | COMMUNITY-ONLY | 2014, "Onion 5" (community) | `.../export_cur_00160.xml:394`: "onion 5 We didnt get same error anymore   http://q4utgdi2n4m4uim5.onion" (a chat log quoted in the wiki). The signed onion-5 message `dl/dukotah/corpus/A-primary-artifacts/pgp/messages/2014-01-onion5-liber-primus.asc` is primary but does not name the label. |
| ut3qtzbrvs7dtvzp | COMMUNITY-ONLY | 2014, "Onion 6" (community) | `dl/dukotah/corpus/C-community/forums/boards_net_live/thread_75_page-4-ut3qtzbrvs7dtvzp-onion.html:5`: "<title>Page 4 in ut3qtzbrvs7dtvzp.onion \| Cicada3301</title>". Numbering from `dl/dukotah/liber-primus/analysis/armada_osint/onions_ibotpeaches/onions__ut3qtzbrvs7dtvzp.onion__README.md`. |
| p7amjopgric7dfdi | COMMUNITY-ONLY | 2013 drop list (community) | `.../wikis/uncovering-cicada/export_cur_00000.xml:12654` (drop list). Also `.../export_cur_00820.xml:61`: "[http://p7amjopgric7dfdi.onion p7amjopgric7dfdi.onion]". |
| emiwp4muu2ktwknf | COMMUNITY-ONLY | 2013, claimed telnet prompt host (community) | `.../wikis/uncovering-cicada/export_cur_00840.xml:326`: "the telnet prompt is a TCP server provided by 3301 as an hidden service at the address <code>emiwp4muu2ktwknf.onion</code>". No primary line names this host. |
| gbyh7znm6c7ezsmr | COMMUNITY-ONLY | 2013 drop list (community) | `.../wikis/uncovering-cicada/export_cur_00000.xml:12658`: "Onions from drops: ... onion: gbyh7znm6c7ezsmr.onion". |
| y2wyuvrqraowagc5 | COMMUNITY-ONLY | 2013 drop list, "onion 3" (community) | `.../export_cur_00000.xml:12656`: "y2wyuvrqraowagc5.onion   onion 3 5". Repo script `dl/dukotah/liber-primus/analysis/round10b/B1-overlooked-artifact/b1_keys.py:99` labels it "Dallas 2013". |
| cginiziglyaobyph | COMMUNITY-ONLY | 2012, "second chance" onion (community) | `.../wikis/uncovering-cicada/export_cur_00120.xml:394`: "The content hosted on cginiziglyaobyph.onion (the second chance onion address)". The primary `pgp/messages/2012-01-second-chance.asc` does not contain the label. |
| 4l6uipnstbggwjyv | COMMUNITY-ONLY | 2013 drop list (community) | `.../wikis/uncovering-cicada/export_cur_00120.xml:517`: "4l6uipnstbggwjyv.onion &lt; -- AK". Repo script `b1_keys.py:102` labels it "Little Rock 2013". |
| wzwmcwmsk5cb7gjn | COMMUNITY-ONLY | 2013 drop list (community) | `.../wikis/uncovering-cicada/export_cur_00000.xml:12658`: "onion: wzwmcwmsk5cb7gjn.onion". Also `.../export_cur_00140.xml:441`: "http://wzwmcwmsk5cb7gjn.onion.to/". |
| vj7suk6t5bfjugdv | COMMUNITY-ONLY | undated, single wiki link | `.../wikis/uncovering-cicada/export_cur_00600.xml:432`: "http://www.vj7suk6t5bfjugdv.onion/". |
| qw7mhchzvuq6f2mf | COMMUNITY-ONLY | 2013 ("Moscow 2013" in repo script) | `.../wikis/uncovering-cicada/export_cur_00160.xml:1525`: "\|qw7mhchzvuq6f2mf.onion" (wiki table). Repo script `b1_keys.py:101`: "qw7mhchzvuq6f2mf.onion, Moscow 2013". |
| erwfcsdvx6pm2rsk | COMMUNITY-ONLY | 2013 drop list (community) | `.../wikis/uncovering-cicada/export_cur_00000.xml:12654`: "erwfcsdvx6pm2rsk.onion&lt;br /&gt;p7amjopgric7dfdi.onion...". Repo script `b1_keys.py:103` labels it "Annapolis 2013". |
| 5fpp2orjc2ejd2g7 | UNKNOWN | 2015-2017 captures, Portuguese-language site | `dl/dukotah/corpus/D-archives/GAPS-D.md:99-102`: "attribution is undetermined ... Whether the site is Cicada 3301, Cicada-adjacent, or an imitator is not established." |
| lwplxqzvmgu43uff | UNKNOWN | none (tor2web error family) | `dl/dukotah/corpus/D-archives/mkfetch.py:3`: `NOISE=("yniir5c6cmuwslfl","lwplxqzvmgu43uff")`. `dl/dukotah/corpus/D-archives/CONFLICTS-D.md:238-245`: proxy error pages, "say nothing about Cicada content". |
| yniir5c6cmuwslfl | UNKNOWN | 2017 captures | `dl/dukotah/corpus/D-archives/CONFLICTS-D.md:67`: "`https://yniir5c6cmuwslfl.onion.link/*` (19 media files) ... identical per file". The files are generic names (gold.png, airhorn.ogg, wewlad.png, ...). `mkfetch.py:3` lists it as NOISE. No attribution. |
| rjzdqt4z3z3xo73h | UNKNOWN | none | `CONFLICTS-D.md:245` (tor2web error family). Also a campaign list at `dl/dukotah/liber-primus/analysis/round17/P3_tables/build_pads.py:49`. |
| n5gvslqnb4yomt6q | UNKNOWN | none | Only `dl/dukotah/corpus/D-archives/build_targets.py:7` and CDX lookup files. |
| bah37war75xzkpla | UNKNOWN | none | Only `build_targets.py:8` and CDX lookup files. |
| bljflz7gy23uv73l | UNKNOWN | none | Only `build_targets.py:7` and CDX lookup files. |
| dbwkwbdidiwbwfau | UNKNOWN | none | Only `build_targets.py:8`, CDX lookups, and a campaign-made seed `dl/dukotah/liber-primus/analysis/round13/B04/seeds.py:68` ("3301aidbwkwbdidiwbwfau.onion"). |
| dxwd42hgpd7qrccm | UNKNOWN | none | Only `build_targets.py:4`, CDX lookups, and campaign seed `round13/B04/seeds.py:61`. |
| a6d7f6hjfg6eyrye | UNKNOWN | none | Campaign seeds and results only: `round13/B04/seeds.py:60`; `round13/B04/results_B.json:344` ("seed": "http://a6d7f6hjfg6eyrye.onion/"). |
| 5qcyeerbnina7esx | UNKNOWN | none | Campaign seeds and results only: `round13/B04/seeds.py:59`; `dl/dukotah/liber-primus/analysis/round15/KDF/results_A.json:550` ("secret": "http://5qcyeerbnina7esx.onion/"). |
| 2lol7ha4j442rqeg | UNKNOWN | none | Wiki file title only: `dl/dukotah/corpus/C-community/wikis/_ns6.json:1` ("File:2lol7ha4j442rqeg.PNG"). The image is not held locally. No onion context. |
| gy3hoy2zizvuzvdb | NOT-CICADA | none | `dl/dukotah/liber-primus/analysis/anend_hunt/FINDINGS.md:41-42`: "`gy3hoy2zizvuzvdb.onion` REFUTED as the destination ... a search-summary hallucination with zero primary corroboration." Also `hashhunt/NOTES.md:29`. |

## Caveats

1. **Community numbering.** The "Onion 1" to "Onion 7" and "RSA/MIDI" names come from the iBotPeaches `onions/` READMEs and the armada MANIFEST. The primary 2014 text names only ky2khlqdf7qdznac. The other 2014 onions are therefore COMMUNITY-ONLY, even though the signed onion-5 message is primary.
2. **README heading error.** `dl/dukotah/liber-primus/analysis/armada_osint/onions_ibotpeaches/onions__auqgnxjtvdbll3pv.onion__README.md` has the heading "# avowyfgl5lkzfj3n.onion" while saying "Onion 1". The MANIFEST table gives auqgnx = Onion 1 and avow = Onion 4. Treated as a copy error in the README.
3. **Dates.** The file `2014-01-onion-welcome.asc` has a signature packet dated 2014-04-02 (gpg VALIDSIG 1396428591; see `dl/dukotah/corpus/A-primary-artifacts/SIGNATURES.json`). The year is 2014 either way. `pgp/messages/ky_2014-05-liber-primus-release.asc` has the same welcome text under a different name. File names in the mirrors are not reliable step labels.
4. **Third-party copies.** The signed messages come from GitHub mirrors (jaxonkuipers/cicada3301, krisyotam/cicada3301, iBotPeaches/cicada_3301). Their bytes verify against the key. The link from that key to Cicada is not independently established.
5. **Telnet claim.** The wiki (export_cur_00840.xml:326) says the 2013 telnet host was emiwp4muu2ktwknf. The primary 2013 telnet-hello names only xsxnaksict6egxkq. No primary line supports the emi claim.
6. **Drop list disclaimer.** The wiki drop list (`export_cur_00000.xml:12652`) carries its author's note: "many of them can be fishy and not related to cicada at all". Drop-list labels are at most COMMUNITY-ONLY.
7. **Not checked.** The iBotPeaches `onions/` HTML captures are not in the local tree. Only READMEs and the MANIFEST are. Their page content was not examined here. If those pages are later fetched, re-run this check on them.
8. **File-name matches.** Matches in wiki `_ns6.json` and in fandom image lists are file titles. A matching file name is not an onion claim.
9. **Tor2web noise.** Most captured bodies for onion hosts are proxy error pages. The D-archives lanes say so in `CONFLICTS-D.md:238-245`. A matching capture is not evidence of content.

## Appendix: other label-shaped strings (out of scope, not in primary artifacts)

- `ll5afyskb6v6g7ga`, `lw4ipk5choakk5ze`: wiki drop list (`export_cur_00000.xml:12658` lists ll5a...).
- `7z6bnpmiyxp2sgmn`: campaign seed (`round13/B04/seeds.py`).
- `zerobinqmdqd236y`: CDX and log lookups only.
- `emiwp4muu2ktwkkf`: one character from `emiwp4muu2ktwknf` (wiki file list `_ns6.json`).
- `a4qgnxjtvdbll3pv`: one character from `auqgnxjtvdbll3pv` (campaign seed `seeds.py`).
