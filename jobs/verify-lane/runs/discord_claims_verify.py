"""Re-derive three CicadaSolvers Discord claims (scout 7, 2026-10-19) with our own data and fresh code.

    python jobs/verify-lane/runs/discord_claims_verify.py [--seed 1] [--perms 100000] [--only 1|2|3]

1. solver A 2026-08-19: sentence Gematria Primus sums of the solved plaintext are prime ~47% vs ~15% by chance.
2. solver B 2026-09-23..25: the 86 doubled runes of LP2 in order; lag-1 circular GP-index distance, separations 5/12/14,
   D(i+3) - D(i) = +4; with a look-elsewhere correction over lags 1-10 and every separation / difference value.
3. solver C 2026-08-09: ~100 one-rune words in LP2, none adjacent; apostrophes at LP2 positions 1110, 5138, 8515, 10089.

Data: lp/lpdata.py (LP2, pin asserted), jobs/verify-lane/tools/solved_plaintext.py (LP1 and the two solved LP2 pages,
decoded here), toolbox/runes.py (English), the aldegonde master transcriptions (marks). Writes
discord_claims_out_seed<seed>.json next to this file and prints every number in the report.
"""
import argparse
import ctypes
import json
import re
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, "lp")
sys.path.insert(0, "toolbox")
sys.path.insert(0, "jobs/verify-lane/tools")
import lpdata  # noqa: E402
import runes  # noqa: E402
import solved_plaintext as sp  # noqa: E402

PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
M = 29
GP = np.array(lpdata.PRIMES)
ENGLISH = [runes.DEFAULT_TEXT,
           "dl/dukotah/liber-primus/data/keys/armada18/dante_inferno_longfellow.txt"]
OUT = {}

try:  # below-normal priority on the shared PC
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
except Exception:
    pass


def sieve(n):
    s = np.ones(n + 1, dtype=bool)
    s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return s


ISP = sieve(400000)


def summ(obs, null, lower=False):
    null = np.asarray(null, dtype=float)
    mu, sd = float(null.mean()), float(null.std(ddof=1))
    z = (obs - mu) / sd if sd > 0 else float("nan")
    if lower:
        p = (np.sum(null <= obs) + 1) / (len(null) + 1)
    else:
        p = (np.sum(null >= obs) + 1) / (len(null) + 1)
    return dict(obs=float(obs), mean=mu, sd=sd, min=float(null.min()), max=float(null.max()), z=float(z),
                p=float(p), margin_over_max=float(obs - null.max()), margin_under_min=float(obs - null.min()), n=len(null))


def fmt(name, s, lower=False):
    edge = f"min {s['min']:.4g}" if lower else f"max {s['max']:.4g}"
    return (f"  {name}: obs {s['obs']:.4g} | null {s['mean']:.4g} +- {s['sd']:.3g}, {edge} | z {s['z']:+.2f} | "
            f"p {s['p']:.2g} (n={s['n']})")


# ------------------------------------------------------------------ claim 1: prime sentence sums
def sent_sums(sents):
    return np.array([int(GP[s].sum()) for s in sents])


def shuffle_null_prime(sents, rng, reps):
    """Runes pooled over the corpus, permuted, re-cut at the same sentence lengths."""
    pool = np.concatenate([np.array(s) for s in sents])
    vals = GP[pool]
    cuts = np.cumsum([len(s) for s in sents])[:-1]
    out = np.empty(reps)
    odd = np.empty(reps)
    for r in range(reps):
        v = vals[rng.permutation(len(vals))]
        sums = np.add.reduceat(v, np.r_[0, cuts])
        out[r] = ISP[sums].mean()
        odd[r] = (sums % 2 == 1).mean()
    return out, odd


def english_text(path, skip=20000):
    """Body of an English text: past any header, and cut before a Project Gutenberg licence footer."""
    text = open(path, encoding="utf-8", errors="replace").read()[skip:]
    m = re.search(r"end of (the )?project gutenberg", text, re.I)
    return text[:m.start()] if m else text


def english_sentences(path):
    text = english_text(path)
    out = []
    for chunk in re.split(r"[.!?;:]+", text):
        r = []
        for w in re.findall(r"[A-Za-z]+", chunk):
            r.extend(runes.eng2runes(w))
        if r:
            out.append(r)
    return out


def claim1(rng, reps):
    secs = sp.build()
    res = {"sections": [(s["name"], s["method"], round(s["quad"], 3), len(s["p"])) for s in secs]}
    print("CLAIM 1 (solver A): prime sentence GP sums in the solved plaintext")
    for s in secs:
        print(f"  {s['name']}: {len(s['p'])} runes, {s['method']}, quadgram {s['quad']:.3f}")
    corpora = {
        "LP1 (7 segments)": sp.sentences(secs, lambda n: n.startswith("LP1")),
        "LP1 + AN END + PARABLE": sp.sentences(secs),
    }
    for nm, sents in corpora.items():
        sums = sent_sums(sents)
        rate = ISP[sums].mean()
        nul, odd = shuffle_null_prime(sents, rng, reps)
        st = summ(rate, nul)
        res[nm] = dict(n_sent=len(sents), n_prime=int(ISP[sums].sum()), rate=float(rate),
                       odd_rate=float((sums % 2 == 1).mean()), odd_null_mean=float(odd.mean()),
                       prime_given_odd=float(ISP[sums][sums % 2 == 1].mean()),
                       shuffle=st)
        print(f" {nm}: {len(sents)} sentences, {int(ISP[sums].sum())} prime = {rate:.1%}; odd sums {np.mean(sums % 2 == 1):.1%}"
              f" (null {odd.mean():.1%}); prime among odd sums {ISP[sums][sums % 2 == 1].mean():.1%}")
        print(fmt("shuffle null (runes across sentences, lengths kept)", st))
    # definition checks on the full solved corpus
    TITLES = {"AWARNNG", "WELCOME", "SOMEWISDOM", "ACOAN", "ANINSTRUCTIAN", "THELOSSOFDIUINITY", "CONSUMPTIAN",
              "PRESERUATIAN", "ADHERENCE", "CNOWTHIS", "PARABLE", "ANEND", "WIDSOM"}
    variants = {
        "F interrupters left out": sp.sentences(secs, drop_skips=True),
        "section titles left out": [x for x in corpora["LP1 + AN END + PARABLE"] if runes.tr(x) not in TITLES],
    }
    res["variants"] = {}
    for nm, sents in variants.items():
        sums = sent_sums(sents)
        nul, _ = shuffle_null_prime(sents, rng, reps // 2)
        res["variants"][nm] = dict(n_sent=len(sents), n_prime=int(ISP[sums].sum()), shuffle=summ(ISP[sums].mean(), nul))
        print(fmt(f"variant, {nm} ({len(sents)} sentences, {int(ISP[sums].sum())} prime)", res["variants"][nm]["shuffle"]))
    res["sentence_list"] = [(runes.tr(x), int(v), bool(ISP[v])) for x, v in
                            zip(corpora["LP1 + AN END + PARABLE"], sent_sums(corpora["LP1 + AN END + PARABLE"]))]
    # per section and held-out halves, LP1 + solved LP2
    sents_all = corpora["LP1 + AN END + PARABLE"]
    per = []
    for s in secs:
        ss = sp.sentences([s])
        sm = sent_sums(ss)
        per.append((s["name"], len(ss), int(ISP[sm].sum())))
    res["per_section"] = per
    print("  per section (sentences, prime): " + "; ".join(f"{a} {b}/{c}" for a, c, b in [(x, y, z) for x, y, z in per]))
    h = len(sents_all) // 2
    halves = {}
    for nm, ss in (("first half", sents_all[:h]), ("second half", sents_all[h:])):
        sm = sent_sums(ss)
        nul, _ = shuffle_null_prime(ss, rng, reps // 2)
        halves[nm] = summ(ISP[sm].mean(), nul)
        print(fmt(f"{nm} ({len(ss)} sentences)", halves[nm]))
    res["halves"] = halves
    # sentence-length dependence: the null rate as a function of length alone
    lens = np.array([len(s) for s in sents_all])
    res["len_stats"] = dict(min=int(lens.min()), median=float(np.median(lens)), max=int(lens.max()))
    # English, transliterated with toolbox/runes.py
    N = len(sents_all)
    eng = {}
    for path in ENGLISH:
        es = english_sentences(path)
        es = [s for s in es if 1 <= len(s) <= 400]
        esum = np.array([int(GP[s].sum()) for s in es])
        blocks = [ISP[esum[i:i + N]].mean() for i in range(0, len(es) - N + 1, N)]
        # length-matched: one English sentence of the same rune length per solved sentence
        bylen = {}
        for s, v in zip(es, esum):
            bylen.setdefault(len(s), []).append(v)
        keys = np.array(sorted(bylen))
        draws = np.empty(reps // 10)
        for r in range(len(draws)):
            hits = 0
            for L in lens:
                k = keys[np.argmin(np.abs(keys - L))]
                arr = bylen[k]
                hits += ISP[arr[rng.integers(len(arr))]]
            draws[r] = hits / len(lens)
        nm = path.split("/")[-1]
        bmax = int(np.argmax(blocks))
        blk = es[bmax * N:(bmax + 1) * N]
        print(f"  English {nm}: highest block {bmax} ({max(blocks):.1%}), mean sentence length "
              f"{np.mean([len(x) for x in blk]):.1f} runes, starts: {' | '.join(runes.tr(x)[:30] for x in blk[:4])}")
        eng[nm] = dict(max_block=dict(index=bmax, mean_len=float(np.mean([len(x) for x in blk])),
                                      start=[runes.tr(x)[:40] for x in blk[:6]]),
                       n_sent=len(es), rate_all=float(ISP[esum].mean()), blocks=summ(ISP[sent_sums(sents_all)].mean(), blocks),
                       length_matched=summ(ISP[sent_sums(sents_all)].mean(), draws))
        print(f"  English {nm}: {len(es)} sentences, prime rate {ISP[esum].mean():.1%}")
        print(fmt(f"   blocks of {N} consecutive English sentences", eng[nm]["blocks"]))
        print(fmt("   length-matched English sentences", eng[nm]["length_matched"]))
    res["english"] = eng
    # LP2 ciphertext sentences, for reference (solver A reported LP2 clauses at the null)
    U, idx, h2 = lpdata.unsolved()
    assert h2 == PIN
    c = np.array(idx)
    sid = np.array([s for p in U for s in p["sent"]])
    l2 = [list(c[sid == k]) for k in np.unique(sid)]
    sm = sent_sums(l2)
    nul, _ = shuffle_null_prime(l2, rng, reps // 10)
    res["LP2 cipher sentences"] = summ(ISP[sm].mean(), nul)
    print(fmt(f"LP2 ciphertext sentences ({len(l2)}), reference", res["LP2 cipher sentences"]))
    OUT["claim1"] = res


# ------------------------------------------------------------------ claim 2: doublet stream
def circ(a, b):
    d = np.abs(a - b) % M
    return np.minimum(d, M - d)


def doublet_stats(D, lags=range(1, 11)):
    """Per lag: mean circular distance, histogram of circular distances (0..14), histogram of signed differences."""
    D = np.asarray(D)
    mean, hist, diff = [], [], []
    for L in lags:
        a, b = D[:-L], D[L:]
        cd = circ(a, b)
        mean.append(cd.mean())
        hist.append(np.bincount(cd, minlength=15))
        diff.append(np.bincount((b - a) % M, minlength=M))
    return np.array(mean), np.array(hist), np.array(diff)


def claim2_on(D, rng, reps, label):
    D = np.asarray(D)
    m0, h0, d0 = doublet_stats(D)
    P = np.empty((reps, 10))
    S = np.empty(reps)            # count of lag-1 distances in {5, 12, 14}
    TOP3 = np.empty((reps, 10))   # top-3 distance-value counts summed, per lag
    DH = np.empty((reps, 10, M))  # signed-difference histograms
    HH = np.empty((reps, 10, 15))
    for r in range(reps):
        q = D[rng.permutation(len(D))]
        m, h, d = doublet_stats(q)
        P[r] = m
        HH[r] = h
        S[r] = h[0][[5, 12, 14]].sum()
        TOP3[r] = np.sort(h, axis=1)[:, -3:].sum(axis=1)
        DH[r] = d
    out = {}
    # lag-1 mean circular distance, raw and corrected over lags 1-10
    zP = (P - P.mean(0)) / P.std(0, ddof=1)
    z0 = (m0 - P.mean(0)) / P.std(0, ddof=1)
    out["lag1_mean_dist"] = summ(m0[0], P[:, 0])
    out["lag1_mean_dist"]["p_lee_lags1_10"] = float((np.sum(zP.max(1) >= z0[0]) + 1) / (reps + 1))
    out["mean_dist_by_lag"] = [round(float(x), 3) for x in m0]
    out["z_by_lag"] = [round(float(x), 2) for x in z0]
    # separations 5/12/14 at lag 1 (raw), and the top-3 values over all separations and lags (corrected)
    s0 = h0[0][[5, 12, 14]].sum()
    out["lag1_sep_5_12_14"] = summ(s0, S)
    top0 = np.sort(h0, axis=1)[:, -3:].sum(axis=1)
    zT = (TOP3 - TOP3.mean(0)) / TOP3.std(0, ddof=1)
    zt0 = (top0 - TOP3.mean(0)) / TOP3.std(0, ddof=1)
    out["lag1_top3_sep"] = summ(top0[0], TOP3[:, 0])
    out["lag1_top3_sep"]["top3_values"] = [int(x) for x in np.argsort(h0[0])[-3:][::-1]]
    out["lag1_top3_sep"]["p_lee_lags1_10"] = float((np.sum(zT.max(1) >= zt0[0]) + 1) / (reps + 1))
    out["lag1_dist_hist"] = [int(x) for x in h0[0]]
    # D(i+3) - D(i) = +4, raw and corrected over every (lag, difference) cell
    n3 = len(D) - 3
    c0 = d0[2][4]
    out["lag3_diff4"] = summ(c0, DH[:, 2, 4])
    out["lag3_diff4"]["frac"] = float(c0 / n3)
    mu, sd = DH.mean(0), DH.std(0, ddof=1)
    sd[sd == 0] = np.inf
    zcell = (DH - mu) / sd
    zc0 = (d0 - mu) / sd
    out["lag3_diff4"]["p_lee_cells"] = float((np.sum(zcell.reshape(reps, -1).max(1) >= zc0[2, 4]) + 1) / (reps + 1))
    best = np.unravel_index(np.argmax(zc0), zc0.shape)
    out["max_cell"] = dict(lag=int(best[0] + 1), diff=int(best[1]), count=int(d0[best]), z=float(zc0[best]),
                           p_lee=float((np.sum(zcell.reshape(reps, -1).max(1) >= zc0[best]) + 1) / (reps + 1)))
    print(f" {label}: n = {len(D)} doublets")
    print(fmt("lag-1 mean circular GP distance", out["lag1_mean_dist"]) +
          f" | look-elsewhere (lags 1-10) p {out['lag1_mean_dist']['p_lee_lags1_10']:.2g}")
    print(f"   mean distance by lag 1-10: {out['mean_dist_by_lag']}; z: {out['z_by_lag']}")
    print(fmt("lag-1 separations in {5,12,14}", out["lag1_sep_5_12_14"]))
    print(fmt(f"lag-1 top-3 separation values {out['lag1_top3_sep']['top3_values']} summed", out["lag1_top3_sep"]) +
          f" | look-elsewhere (any 3 values, lags 1-10) p {out['lag1_top3_sep']['p_lee_lags1_10']:.2g}")
    print(f"   lag-1 distance histogram 0..14: {out['lag1_dist_hist']}")
    print(fmt(f"D(i+3)-D(i)=+4 count (of {n3}; {out['lag3_diff4']['frac']:.1%})", out["lag3_diff4"]) +
          f" | look-elsewhere (all lags 1-10 x 29 differences) p {out['lag3_diff4']['p_lee_cells']:.2g}")
    mc = out["max_cell"]
    print(f"   most extreme (lag, difference) cell: lag {mc['lag']} diff +{mc['diff']} count {mc['count']} "
          f"z {mc['z']:+.2f}, look-elsewhere p {mc['p_lee']:.2g}")
    return out


def claim2(rng, reps):
    U, idx, h = lpdata.unsolved()
    assert h == PIN
    c = np.array(idx)
    pos = np.nonzero(c[:-1] == c[1:])[0]
    triples = int(np.sum((c[:-2] == c[1:-1]) & (c[1:-1] == c[2:])))
    D = c[pos]
    print("CLAIM 2 (solver B): the doubled-rune stream D of LP2")
    print(f"  {len(pos)} doublets, {triples} triples; D = {' '.join(lpdata.TR[x] for x in D)}")
    res = dict(n=len(D), triples=triples, positions=[int(x) for x in pos], D=[int(x) for x in D])
    res["full"] = claim2_on(D, rng, reps, "whole book")
    mid = len(c) // 2
    for nm, sel in (("first half (runes 0-%d)" % (mid - 1), pos < mid), ("second half (runes %d-%d)" % (mid, len(c) - 1), pos >= mid)):
        res[nm] = claim2_on(D[sel], rng, reps // 2, nm)
    # a doublet-preserving cipher null: the same statistic on increment-shuffled LP2 (chain model, keeps the deficit)
    pages = [list(p["idx"]) for p in U]
    sys.path.insert(0, "toolbox")
    import nulls
    pyr = __import__("random").Random(int(rng.integers(1 << 30)))
    chain = []
    for _ in range(200):
        q = np.array([x for pg in nulls.shuffle_increments(pages, pyr) for x in pg])
        pq = np.nonzero(q[:-1] == q[1:])[0]
        chain.append(circ(q[pq][:-1], q[pq][1:]).mean())
    res["chain_null_lag1"] = summ(res["full"]["lag1_mean_dist"]["obs"], chain)
    print(fmt("lag-1 mean distance vs 200 increment-shuffled LP2 streams (doublet values re-drawn)", res["chain_null_lag1"]))
    OUT["claim2"] = res


# ------------------------------------------------------------------ claim 3: one-rune words and apostrophes
def adj_count(L, same=None):
    a = (L[:-1] == 1) & (L[1:] == 1)
    if same is not None:
        a &= same
    return int(a.sum())


def group_shuffle(n, groups, rng):
    return np.lexsort((rng.random(n), groups))


def word_table_lp2():
    U, idx, h = lpdata.unsolved()
    assert h == PIN
    wid = np.array([w for p in U for w in p["word"]])
    sid = np.array([s for p in U for s in p["sent"]])
    pg = np.array([p["page"] for p in U for _ in p["idx"]])
    words, first = np.unique(wid, return_index=True)
    L = np.bincount(np.searchsorted(words, wid))
    return L, sid[first], pg[first], first


def word_table_runs(word_ids, sent_ids, page_ids):
    wid = np.asarray(word_ids)
    words, first = np.unique(wid, return_index=True)
    L = np.bincount(np.searchsorted(words, wid))
    return L, np.asarray(sent_ids)[first], np.asarray(page_ids)[first]


def onerune_test(L, sid, pg, rng, reps, label):
    n = len(L)
    obs_any = adj_count(L)
    obs_in = adj_count(L, sid[:-1] == sid[1:])
    out = dict(words=n, one_rune=int((L == 1).sum()), adjacent_any=obs_any, adjacent_within_sentence=obs_in)
    nulls_ = {}
    for nm, grp in (("global word shuffle", np.zeros(n, int)), ("within-page shuffle", pg), ("within-sentence shuffle", sid)):
        a = np.empty(reps)
        b = np.empty(reps)
        for r in range(reps):
            o = group_shuffle(n, grp, rng)
            Lq = L[o]
            a[r] = adj_count(Lq)
            b[r] = adj_count(Lq, sid[o][:-1] == sid[o][1:])
        nulls_[nm] = dict(any=summ(obs_any, a, lower=True), within_sentence=summ(obs_in, b, lower=True),
                          p_zero=float(np.mean(a == 0)))
    out["nulls"] = nulls_
    print(f" {label}: {n} words, {out['one_rune']} one-rune words ({out['one_rune'] / n:.1%}); adjacent one-rune pairs:"
          f" {obs_any} (within a sentence: {obs_in})")
    for nm, d in nulls_.items():
        print(fmt(f"{nm}, any adjacency", d["any"], lower=True) + f" | P(0 adjacent) {d['p_zero']:.3f}")
    return out


def english_words(path, n_words, start_word):
    text = english_text(path)
    L, S, sent = [], [], 0
    for chunk in re.split(r"([.!?;:]+)", text):
        if re.fullmatch(r"[.!?;:]+", chunk or "x"):
            sent += 1
            continue
        for w in re.findall(r"[A-Za-z]+", chunk):
            r = runes.eng2runes(w)
            if r:
                L.append(len(r)); S.append(sent)
    L, S = np.array(L[start_word:start_word + n_words]), np.array(S[start_word:start_word + n_words])
    return L, S


def apostrophes(path):
    """Apostrophes in a transcription, counted in runes from the start of LP2 page 0 (the first SHEOGMIOF)."""
    t = open(path, encoding="utf-8").read().replace("ᛂ", "ᛄ")  # RUNIC LETTER E -> our J rune
    t = t[t.index("ᛋᚻᛖᚩᚷᛗᛡᚠ"):]
    out, k = [], 0
    for i, ch in enumerate(t):
        if ch in lpdata.R2I:
            k += 1
        elif ch == "'":
            after = ""
            j = i + 1
            while j < len(t) and t[j] in lpdata.R2I:
                after += t[j]; j += 1
            before = ""
            j = i - 1
            while j >= 0 and t[j] in lpdata.R2I:
                before = t[j] + before; j -= 1
            out.append(dict(runes_before=k, word_before=before, runes_after_in_word=len(after), after=after))
    stream = [lpdata.R2I[ch] for ch in t if ch in lpdata.R2I]
    return out, stream


def claim3(rng, reps):
    print("CLAIM 3 (solver C): one-rune words in LP2 and the apostrophe positions")
    res = {}
    L, sid, pg, first = word_table_lp2()
    res["LP2"] = onerune_test(L, sid, pg, rng, reps, "LP2 pages 0-54")
    # held-out halves of LP2 by page
    for nm, sel in (("LP2 pages 0-27", pg <= 27), ("LP2 pages 28-54", pg >= 28)):
        res[nm] = onerune_test(L[sel], sid[sel], pg[sel], rng, reps // 2, nm)
    # LP1 (cipher word marks = plaintext words), solved plaintext
    secs = sp.build()
    w, s, p = [], [], []
    for k, sc in enumerate(secs):
        if not sc["name"].startswith("LP1"):
            continue
        w += [10 ** 7 * k + x for x in sc["word"]]; s += [10 ** 7 * k + x for x in sc["sent"]]; p += [k] * len(sc["word"])
    L1, s1, p1 = word_table_runs(w, s, p)
    res["LP1"] = onerune_test(L1, s1, p1, rng, reps, "LP1 (solved, 7 segments)")
    # English blocks of the LP2 word count
    eng = []
    for path in ENGLISH:
        for b in range(3):
            Le, Se = english_words(path, len(L), b * len(L))
            nm = f"English {path.split('/')[-1]} block {b + 1}"
            eng.append((nm, onerune_test(Le, Se, Se, rng, reps // 5, nm)))
    res["English"] = eng
    # apostrophes: two transcriptions, mapped onto our pinned stream
    U, idx, h = lpdata.unsolved()
    ours = list(idx)
    words_by_rune = np.array([w for p_ in U for w in p_["word"]])
    page_by_rune = np.array([p_["page"] for p_ in U for _ in p_["idx"]])
    ap = {}
    for path in ("dl/aldegonde_clone/data/page0-58.txt",
                 "dl/aldegonde_clone/data/liber-primus__transcription--master.txt",
                 "dl/rdp/assets/liber_primus/liber-primus__transcription--master-v2.txt"):
        try:
            marks, stream = apostrophes(path)
        except (OSError, ValueError) as e:
            ap[path] = f"not read: {e}"
            continue
        same = stream[:len(ours)] == ours
        rows = []
        for m in marks:
            k = m["runes_before"]
            if k < len(ours) and same:
                wid_after = words_by_rune[k] if k < len(ours) else None
                L_after = int(np.sum(words_by_rune == wid_after))
                rows.append(dict(rune_before=k - 1, rune_after=k, page=int(page_by_rune[k]),
                                 word_before=m["word_before"], our_word_len_after=L_after,
                                 runes_after_in_word=m["runes_after_in_word"]))
            else:
                rows.append(dict(runes_before=k, beyond_or_misaligned=True, **m))
        ap[path] = dict(identical_to_pin=bool(same), n_runes=len(stream), marks=rows)
        print(f"  apostrophes in {path} (rune stream identical to our pin for the first 12,956: {same}):")
        for r in rows:
            print(f"    {r}")
    res["apostrophes"] = ap
    res["solverC_positions"] = [1110, 5138, 8515, 10089]
    OUT["claim3"] = res


if __name__ == "__main__":
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--seed", type=int, default=1)
    ap_.add_argument("--perms", type=int, default=100000)
    ap_.add_argument("--only", type=int, default=0)
    a = ap_.parse_args()
    rng = np.random.default_rng(a.seed)
    if a.only in (0, 1):
        claim1(rng, max(2000, a.perms // 5))
    if a.only in (0, 2):
        claim2(rng, a.perms)
    if a.only in (0, 3):
        claim3(rng, max(2000, a.perms // 5))
    OUT["seed"] = a.seed
    OUT["perms"] = a.perms
    suffix = "" if a.only == 0 else f"_only{a.only}"
    with open(f"jobs/verify-lane/runs/discord_claims_out_seed{a.seed}{suffix}.json", "w", encoding="utf-8") as f:
        json.dump(OUT, f, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
