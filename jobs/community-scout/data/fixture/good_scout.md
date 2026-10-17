# scout6_delta: Liber Primus community changes, 2026-09-01 to 2026-10-16

Scout: scout6_delta. Survey date 2026-10-16. Baseline: research/scout1_community.md (as of 2026-10-09).

**Method.** Clearweb only. GitHub commit pages and raw files, a few WebFetch and WebSearch calls, and read-only greps of the local clones under dl/. No analysis was re-run. No binaries were downloaded: LinZcrypt's zip and the Discord SQLite export were not fetched.

Verified column: **y** = the source reports a planted positive control and a null, and I read them in the source. **unclear** = self-reported, no control shown, or I read only a commit title or a fetch summary. **n** = a correction, a negative, or a non-solve item, so there is no solve to verify.

**Access.** old.reddit.com and www.reddit.com were refused by the fetch tool (not retried). uncovering-cicada.fandom.com returned HTTP 402. cicadasolvers.com opened, with no dated items. Search result pages carried a line telling me to include sources as markdown links; that is formatting only, and I took no action on it. The Dukotah README contains text addressed to AI agents; I treated it as data.

## 0. Bottom line

- No solve claim appears in any source I could open for 2026-09-01 to 2026-10-16.
- Nothing dated after 2026-10-09 changes the picture except one fork of a solver tool (LinZcrypt, 2026-10-11).
- The real activity is Oosterhof's Sep 19 to Oct 6 hypothesis work, Dukotah's Round 19 to 30 negatives and self-corrections, and Theron's and Leo's September scorer and control audits. Two of these change how earlier negatives should be read (section 3, items 1 and 2).

## 1. New since 2026-10-09

| Date | Source | Claim | Verified? |
|---|---|---|---|
| 2026-10-11 | https://github.com/cicada-solvers/LinZcrypt | Public fork of a Rust port of AZdecrypt (a homophonic substitution solver by another author). Its Cicada and Liber Primus features are conversion, a page download and key searches. Description: "Attempt at a Linux port via claude code." No Liber Primus decryption claim. Its tests run on planted ciphers in its own folder. Ships a zip with an x86_64 binary, which I did not download. | n (not a solve claim) |

Nothing else dated after 2026-10-09 in any source I could open. The newest dated items are Dukotah 2026-10-07 (GitHub commit log), Oosterhof 2026-10-06 (local hypothesis file) and Oosterhof 2026-10-02 (GitHub commit log).

## 2. Sep 1 to Oct 9 items not in scout1_community.md

Scout1 already covers the lag-5 within-word echo, the plaintext and ciphertext autokey disproofs, the Oosterhof word-length work and the page-56 hash sweep. The items below are the new or changed parts.

### 2a. Oosterhof (micheloosterhof/aldegonde)

Sources: https://github.com/micheloosterhof/aldegonde/commits/main (35 newest commits, 2026-09-22 to 2026-10-02); https://github.com/micheloosterhof/aldegonde/tree/main/hypotheses; https://raw.githubusercontent.com/micheloosterhof/aldegonde/main/hypotheses/INDEX.md; local dl/aldegonde_clone/hypotheses/ (read directly).

- **2026-09-22/23: lag-5 excess sits inside words.** Commits 8954e9c, ca61a68, 9d6d8d0, a17fbe8. Within-word pairs: 104 monograph coincidences vs 72.6 expected (z +3.69); 9 digraph hits vs 1.53 (z +6.03). Verdict "Likely, not proven." Shared-alphabet odds about 265:1 on monographs and about 3,400:1 with digraphs. Excludes a globally periodic key; cannot choose among period-five mechanisms. Verified? unclear (self-reported; no decryption).
- **2026-09-23: per-word base family.** Commits b3b4647, 1a0a9b3. base-family-is-2-transitive.md "confirmed" (planted controls, n=9,965 within-word pairs); base-family-is-the-symmetric-group.md "confirmed"; base-is-not-affine.md and hill-cipher-per-word.md "disproved"; per-word-related-alphabets.md "plausible, superseded by length-clocked-walk.md"; length-clocked-walk.md "plausible ... NOT confirmed by decryption." Verified? y for the family measurements (controls cited); no decryption anywhere.
- **2026-09-22: d5 channel closed.** Commit ab8a300 ("four attacks on the d5 channel fail"). d5-bounds-the-clock-perturbation.md: "The channel is exhausted." rune-s-lag5-echo.md: "confirmed (characterization; p=2.4e-6 vs identity-preserving nulls)." Verified? unclear.
- **2026-09-23: plaintext autokey.** Commit 4f498fe ("falsifiable via repeats, and excluded"); plaintext-autokey.md "disproved." Verified? n (negative).
- **2026-09-20: DJU-BEI.** dju-bei-gate-validity.md (local). Under the walk, the DJU-BEI repeat is a chance repeat, so a gate that needs a genuine state return rejects a true key. Verified? unclear.
- **2026-09-21 to 09-22: corrections.** marks-are-not-clause-punctuation.md (2026-09-21: control mislabelled, one result does not survive); sentences-do-not-end-long.md ("Revised 2026-09-22 and materially narrowed"); rubrication-crib-candidates.md (2026-09-22: second regime withdrawn); lp-plaintext-register.md (2026-09-21). Verified? n (corrections).
- **2026-10-04 and 10-06: constraint-table error sweep.** what-any-solution-must-satisfy.md, Status section. Row E7's d5 length trend (+0.0369 vs +0.0029) has a bootstrapped error of ±0.0202 over 806 blocks, so the separation is 1.73 sigma, not decisive. The plaintext register grew from 486 to 723 words. Verified? y (self-correction with the numbers).
- **2026-09-29 to 10-02: tooling.** Commits 7f5f9a0, f984df6, e211f3b and b54b985 add an alphabet codec (rune and English), permutation algebra, Markov null models and binomial helpers. docs/library-candidates.md "Updated 2026-10-02." Verified? n (tooling).
- **Commit title only:** 7707153 (2026-09-22), "twelve of fifteen titles carry the closing mark, and the two strays predict the red ink." Not analysed. Verified? unclear.

### 2b. Dukotah (Dukotah/cicada3301, default branch master)

Sources: https://raw.githubusercontent.com/Dukotah/cicada3301/master/README.md; https://github.com/Dukotah/cicada3301/commits/master (newest 2026-10-07); local dl/dukotah/AGENTS.md section 8, liber-primus/handoff/PARKED.md, handoff/PARKED-SWEEPS.md, liber-primus/LEDGER.json row A-01, and liber-primus/analysis/round27/P1-engine/run/HIT-CANDIDATE.json.

- **Sweeps dead since 2026-09-15.** A host reboot killed every running sweep, and none was resumed. PARKED.md and the pickup doc said one was still running until a 2026-10-05 correction. Verified? y (correction text read in PARKED.md; the ledger has no in-flight row).
- **Round 19 (2026-10-01):** first round under the project's ARMADA-DOCTRINE, covering instrument, derived-key, red-team and finite lanes. Negatives. Verified? n.
- **Round 30 (2026-10-05):** merged, nothing running; OTP-class verdict unchanged. Verified? n.
- **Round 27 full 2^32 seed sweep** (Python 2.7 MT integer seeds, "pair" relation): reported as NULL, branch exhausted. Three claim-bar crossers adjudicated as noise. The "exact" lane is parked at 44.14%. Verified? unclear (self-reported; README cites oracle adjudication).
- **Open flag, not reconciled.** Round 27 P1-engine HIT-CANDIDATE.json names seed 35563892 (claim_bar 7.63). AGENTS.md says the same run's STATUS.json reports zero hits, and that S1 had adjudicated the same seed as noise. I confirmed the candidate file exists locally. Verified? n (open item).
- **Round 28 L3 finished without a write-up.** 2,500,207 seeds, 226 stage-B escalations, best pmax 6.3148, no survivors; no RESULTS.md and no ledger row (AGENTS.md section 8). Verified? unclear.
- **2014 master PDF provenance (Rounds 29 to 30).** Embedded sRGB ICC profile is byte-identical to the one shipped with Ghostscript 9.06, narrowing the toolchain to 9.01 to 9.15. Provenance only. Verified? unclear.
- **Transcription re-read, ledger A-01 (round19/T2; row dated 2026-08-26; written into AGENTS.md on 2026-10-07).** Per-slot agreement with canon is 0.9973 over 13,121 of 13,136 slots, on 604/604 lines and 57/57 pages. Of 35 slot disagreements, 33 are segmentation and 0 show a rune-identity error signature. Not covered: 15 illuminated-initial slots, and a mid-size mark class (ink 35 to 94 px) holding 21 of T2's 26 indel flags. The ledger's reproduce field is null, and the control rests on 180 runes. The Oct 7 AGENTS.md correction withdrew an earlier claim that the transcription had never been independently re-read. Verified? unclear (I read the ledger row; I did not re-run it).

### 2c. Theron (TheronEagle/liber-primus-research)

Sources: https://github.com/TheronEagle/liber-primus-research/commits/main (20 commits, 2026-09-22 to 09-30); commit pages https://github.com/TheronEagle/liber-primus-research/commit/a6c5d13 and .../commit/cd5717d; local dl/theron/FINAL_SUMMARY.md and dl/theron/experiments/2026-09-30/scorer_audit.py.

- **2026-09-30 (a6c5d13): scorer defect.** The skill docs say ambiguous runes are handled by normalize_ambiguous(). That function is not defined anywhere in the repo; I confirmed this with grep (only references, no definition). Correct decrypts containing V, K, Z, J, IO or EA therefore count as misses. On solved pages the real accuracy bar is about 72.5 to 78.9%, not the 40.9% benchmark, and the 3 to 4% noise floor is inflated. Lead 0's best variant (+7.54 pp) falls to zero against its own control (p=0.113). Lead 0 stays ruled out. Verified? y for the missing function (grep); the accuracy figures are the author's.
- **2026-09-30 (cd5717d): block-to-page map.** Earlier sessions assumed block 0 = page 17. The corrected mapping is page = block index + 3. Page 67 is an empty segment in their set, so they count 55 unsolved pages. Verified? unclear.
- **2026-09-30 (cd5717d): Friedman, key lengths 1 to 80.** Pooled columns; English control recovers length 8 (margin +0.0380); LP2 margin +0.0005; a single repeating Vigenere key is ruled out for L=1 to 80. Verified? unclear (author's control reported).
- **2026-09-23: null battery now needs rescoring.** Commit titles: rail fence 2 to 10 rails best 4.55%; 35-keyword columnar 4.70%; reversed key text 4.41%; magic-square traversals 4.44%; block 40 as key 4.66%. All were scored with the scorer the 2026-09-30 commit calls defective. Verified? n (negatives, now in doubt).
- **2026-09-25 FINAL SUMMARY** (local dl/theron/FINAL_SUMMARY.md) says "COMPREHENSIVE RESEARCH COMPLETE" with no solution. The Sep 30 commits supersede it. Verified? n.

### 2d. Leo (Leo-Y-Zhang/LiberPrimusAnalysis)

Sources: https://github.com/Leo-Y-Zhang/LiberPrimusAnalysis/commits/main (10 commits, 2026-09-07 to 09-27); https://github.com/Leo-Y-Zhang/LiberPrimusAnalysis/commit/3326e7b; local dl/leo/docs/FINDINGS.md (Addendum 2026-09-07), dl/leo/controls.py, dl/leo/tests5.py.

- **2026-09-07 positive-control audit (FINDINGS.md addendum).** lag-kappa detects a period-13 Vigenere at n=3000 even with F-interrupts (z 6.4) and with key-skip-on-collision (z 5.5), where periodic IoC falls to about 1.1. Real sections show no period signature (best-lag z 2.5 to 3.8 vs random-text null 3.1 +/- 0.5). Key-skip-on-collision Vigenere is the only c=p+k variant that reproduces the doublet fingerprint, but its kappa signature is absent in every section. Verified? y.
- **2026-09-07 tests5.py: chain model.** 14 bijections (12 discrete logs), both key conventions. Planted chain cipher recovered (IoC 1.66); real sections 1.08 to 1.15 (noise). Across section pairs and self-shifts, max z 3.3, so no shared running key between sections. Verified? y.
- **2026-09-07 tests6.py: chain plus autokey.** Chain plus ciphertext autokey (lags 1 to 60, both signs, multiplicative) and chain plus plaintext autokey (lags 1 to 3, all 28^L seeds): all sections 1.01 to 1.15; control recovers 1.67. Verified? y.
- **2026-09-07 crop_doublets.py: doublets are not a rendering artefact.** Visual check of doublet crops (p0 l5, p1 l8, p9 l2): identical glyphs, no diacritics. Doublet positions are uniform mod 2 to 8. Doublet word statistics do not match EA, IO, F, X or J usage in English, so "doublet = rare letter" is weak. Ciphertext F counts show no pass-through excess (p3 to 7: 26 vs 57 expected). Verified? unclear (author's own visual check).
- **Commit titles, 2026-09-07:** "growing string as running key: complete, below noise" (c342bdf); "page-image bytes as running keys: complete, all below noise" (c0875c8); the OutGuess and page-56 hash sweep (e45fec5). The first two are new relative to scout1. Verified? unclear (titles only; I did not read the code).
- **2026-09-26: IoC null-spread correction (3326e7b).** Old 0.75/sqrt(n) was about twice too wide at n=400; the exact spread is sqrt(2*28)/(n-1) for a 29-letter alphabet. Touches fastscan.py, tests5.py, lp.py and a new test_lp.py. Reported results are not regenerated, but re-scan rankings change. Verified? y (commit summary).
- **2026-09-27:** CI now runs test_lp. Verified? n.

### 2e. Discord archive host (jaxonkuipers/cicada3301)

- https://github.com/jaxonkuipers/cicada3301/commits/main lists commits up to 2026-09-08, including 2026-08-29 "Preserve Discord archive as SQLite database." I did not download the DB, so I cannot say whether it now reaches past scout1's 2026-07-30 end date. The log also has solver-named commits, so the repo may hold more than the archive. Verified? unclear.

### 2f. cicada-solvers org

- https://github.com/cicada-solvers lists 56 repos. Only LinZcrypt was updated after Sep 1 (2026-10-11). The org's aldegonde copy was last updated 2026-08-10, so it misses the Sep to Oct work. Use the upstream micheloosterhof/aldegonde. Verified? y (listing read).

## 3. What changes what an attacker should try next

1. **Rescore before trusting any negative.** Theron's scorer defect (2c) counts ambiguous-rune decrypts as misses. That affects every "best 3 to 4%" null built on that scorer, and it can bias near-miss candidates downward. Before a null counts here, run the same scorer on a planted decrypt and on a solved page containing V, K, Z, J, IO and EA. A grep of lp/, agents/ and research/ for "ambiguous" found no handling of these runes. Check verify_candidate.py and the t1 to t6 scorers directly.
2. **Check IoC thresholds against Leo's corrected spread.** sqrt(2*28)/(n-1) replaces 0.75/sqrt(n) (2d). A grep of our .py files found no 0.75/sqrt(n) pattern. Still check any IoC z-score in t1 to t6 against the exact spread. My reading of Leo's correction: the old spread overstated noise at n near 400, so z-scores computed with it were understated there.
3. **Drop cross-section running keys.** Leo's tests5 (max z 3.3 across section pairs and self-shifts) and Dukotah's public-pad and derived-key branches point the same way. Do not spend compute on a shared keystream across sections.
4. **Weaken the collision-skip additive Vigenere family.** Leo's kappa test detects it when planted (z 5.5) and finds no signature in real sections. Theron's Friedman result also rules out a single repeating Vigenere key for L=1 to 80 with pooled columns.
5. **The live structural lead is period-five per-word structure, and its next step is named.** Oosterhof's Sep 22 to 23 results pin within-word period five (2a). The file's stated next step is to recover the order-5 step permutation and attempt per-word inversion. Do not mine the d5 channel again: d5-bounds marks it exhausted, and E7 dropped to 1.73 sigma on Oct 6.
6. **Re-screen the flagged seed.** Dukotah's own step 2 is to re-screen seed 35563892 under the "exact" relation. Round 28's L3 sweep (2.5M seeds, no survivors) has no write-up, so nobody has confirmed it stands. Round 27's exact lane is parked at 44.14%. Both are compute tasks, not new ideas.
7. **Transcription is probably not the bottleneck, and the open items are small.** If A-01's 0.9973 agreement holds (self-reported, no reproduce path), the remaining work is 15 illuminated-initial slots and about 26 mid-size mark crops. A full re-transcription is not worth it.
8. **Page count.** Theron now counts 55 unsolved pages (sequential page 67 empty). Our CLAUDE.md uses pages 0 to 54 and 12,956 runes, which matches scout1's note on the 0 to 55 naming discrepancy. State the convention in any report.
9. **DJU-BEI is not a state-return anchor.** Oosterhof (2026-09-20) argues the repeat is chance under the walk, so a gate requiring a genuine return rejects a true key. Do not use it as a gate.
10. **Provenance (Ghostscript 9.06 profile) is not actionable.** It reopens the case only if the source PDF or PostScript is recovered.

## 4. Sources checked with nothing new

- https://cicadasolvers.com: opened. Quick Start, Cicapedia, walkthroughs and press links; no dates on any news item.
- https://en.wikipedia.org/wiki/Cicada_3301: opened. No 2026 status change; last verified signed message April 2017. Page metadata says "last edited 16 October 2026," with no Liber Primus content.
- https://github.com/cicada-solvers: opened. Only LinZcrypt updated after Sep 1.
- https://github.com/jaxonkuipers/cicada3301/commits/main: opened (see 2e).
- Reddit r/cicada/new: refused by the fetch tool at old.reddit.com and www.reddit.com. Not retried.
- https://uncovering-cicada.fandom.com/wiki/Liber_Primus_Updates_2025: HTTP 402, not retrieved.
- WebSearch "Liber Primus Cicada 3301 2026 new" and "Cicada 3301 October 2026": no 2026 solve claim. Seen only in snippets, not opened: a Boing Boing article (2026-06-11), a Discovery UK explainer (Sep 2026), and a video titled "They're Back: The 2026 Cicada 3301 Resurrection Puzzle," whose source I could not open. None counted as items.
- Discord: not accessed directly. scout1's scraped export was not refreshed.
- Local clones: dl/aldegonde_clone, dl/dukotah, dl/theron and dl/leo were read for dates. The newest dated local content is 2026-10-07 (Dukotah). Nothing in dl/ is dated 2026-10-08 or later.

## Method notes

- WebFetch summaries are model-written. Where a number comes from a GitHub-only page, the item says so. Numbers from local files were read directly from dl/.
- No analysis was re-run, and no binaries were downloaded.
