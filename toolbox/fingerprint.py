"""The LP2 fingerprint (toolbox/CONSTRAINTS.md) for any rune stream, and a coarse gate against LP2's values.

    import sys; sys.path.insert(0, "toolbox"); import fingerprint as fp
    f = fp.fingerprint(runes, word_ids, line_ids=None, page_ids=None)
    for row in fp.gate(f): print(row)        # (constraint, value, LP2 value, band, PASS/FAIL/INFO)

CLI:
    python toolbox/fingerprint.py              LP2 itself: prints the fingerprint and asserts the pinned values
    python toolbox/fingerprint.py --english    an English rune stream of the same size, as the reference

The gate bands are deliberately coarse. They decide whether a hypothesis is worth a lane, not whether it is right.
They are scaled to the stream's size, so a simulated cipher should be about as long as LP2 (12,956 runes).
"""
import math
import random
import sys
from collections import Counter

sys.path.insert(0, "lp")
sys.path.insert(0, "toolbox")
import lpdata  # noqa: E402

M = 29
CHI2_001 = {2: 10.83, 3: 13.82, 4: 16.27, 5: 18.47, 6: 20.52, 7: 22.46, 8: 24.32}   # chi-square, df = k-1, p = 0.001
LP2 = {"n": 12956, "ioc": 1.000, "doublets": 86, "doublets_within": 63, "doublets_cross": 23, "cond_ioc": 1.026,
       "lag5_hits": 104, "lag5_pairs": 2105, "repeated_words": 16}


def _ioc(x):
    c = Counter(x)
    n = len(x)
    return 29 * sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) if n > 1 else 0.0


def _cond_ioc(runes, page):
    num = den = 0
    tab = Counter()
    for i in range(1, len(runes)):
        if page[i] == page[i - 1]:
            tab[(runes[i - 1], runes[i])] += 1
    rows = Counter()
    for (a, _b), v in tab.items():
        rows[a] += v
    for (a, b), v in tab.items():
        num += v * (v - 1)
    for a, na in rows.items():
        den += na * (na - 1)
    return 29 * num / den if den else 0.0


def _words(runes, word):
    out, cur, last = [], [], None
    for r, w in zip(runes, word):
        if w != last and cur:
            out.append(tuple(cur))
            cur = []
        cur.append(r)
        last = w
    if cur:
        out.append(tuple(cur))
    return out


def _repeated(words):
    c = Counter(w for w in words if len(w) >= 3)
    return sum(1 for v in c.values() if v >= 2)


def fingerprint(runes, word, line=None, page=None, null_shuffles=5, seed=3301):
    n = len(runes)
    page = page or [0] * n
    d_in = d_x = 0
    for i in range(1, n):
        if runes[i] == runes[i - 1]:
            if word[i] == word[i - 1]:
                d_in += 1
            else:
                d_x += 1
    hits = pairs = s_hits = s_pairs = 0
    for a in range(n - 5):
        if word[a] == word[a + 5]:
            pairs += 1
            m = runes[a] == runes[a + 5]
            hits += m
            if line is not None and line[a] != line[a + 5]:
                s_pairs += 1
                s_hits += m
    dpos = [i for i in range(1, n) if runes[i] == runes[i - 1]]
    resid = {}
    for k in range(2, 9):                # C2c: are doublet positions uniform mod k?
        cnt = [0] * k
        for x in dpos:
            cnt[x % k] += 1
        e = len(dpos) / k
        resid[k] = sum((c - e) ** 2 / e for c in cnt) if dpos else 0.0
    words = _words(runes, word)
    rep = _repeated(words)
    rng = random.Random(seed)            # null for C3: same word lengths, runes shuffled across the stream
    rnull = []
    for _ in range(null_shuffles):
        pool = list(runes)
        rng.shuffle(pool)
        it = iter(pool)
        rnull.append(_repeated([tuple(next(it) for _ in w) for w in words]))
    lens = [len(w) for w in words]
    mu = sum(lens) / len(lens)
    var = sum((x - mu) ** 2 for x in lens) / len(lens)
    r1 = sum((lens[i] - mu) * (lens[i + 1] - mu) for i in range(len(lens) - 1)) / ((len(lens) - 1) * var) if var else 0
    e = pairs / 29
    return {
        "n": n, "ioc": _ioc(runes), "doublets": d_in + d_x, "doublets_within": d_in, "doublets_cross": d_x,
        "doublet_rate": (d_in + d_x) / max(1, n - 1), "doublet_residue_chi2": resid,
        "cond_ioc": _cond_ioc(runes, page),
        "lag5_hits": hits, "lag5_pairs": pairs, "lag5_rate": hits / max(1, pairs),
        "lag5_z": (hits - e) / math.sqrt(e * 28 / 29) if pairs else 0.0,
        "lag5_straddle": (s_hits, s_pairs) if line is not None else None,
        "repeated_words": rep, "repeated_words_null": (sum(rnull) / len(rnull),
                                                        (sum((x - sum(rnull) / len(rnull)) ** 2 for x in rnull) / len(rnull)) ** 0.5),
        "wordlen_r1": r1, "wordlen_z": r1 * math.sqrt(len(lens)), "n_words": len(words),
    }


def gate(f):
    """Coarse consistency with LP2, scaled to f's size. Returns rows (id, value, LP2, band, verdict)."""
    k = (f["n"] - 1) / (LP2["n"] - 1)
    sd_ioc = math.sqrt(2 * 28) / f["n"] * 1.0
    rows = []
    rows.append(("C1 IoC", round(f["ioc"], 4), LP2["ioc"], "1.000 +- %.3f" % (4 * sd_ioc),
                 "PASS" if abs(f["ioc"] - 1) <= 4 * sd_ioc + 0.005 else "FAIL"))
    lo, hi = 0.004, 0.010
    rows.append(("C2 doublet rate", round(f["doublet_rate"], 5), round(86 / 12955, 5), "[%.3f, %.3f]" % (lo, hi),
                 "PASS" if lo <= f["doublet_rate"] <= hi else "FAIL"))
    rows.append(("C2b conditional IoC", round(f["cond_ioc"], 4), LP2["cond_ioc"], "[0.98, 1.08]",
                 "PASS" if 0.98 <= f["cond_ioc"] <= 1.08 else "FAIL"))
    ratio = max(f["doublet_residue_chi2"][k] / CHI2_001[k] for k in CHI2_001)
    worst = max(CHI2_001, key=lambda k: f["doublet_residue_chi2"][k] / CHI2_001[k])
    rows.append(("C2c doublet positions mod 2..8", "mod%d chi2 %.1f" % (worst, f["doublet_residue_chi2"][worst]),
                 "uniform", "every chi2 < its p=0.001 value",
                 "INFO" if f["doublets"] < 20 else ("PASS" if ratio < 1 else "FAIL")))
    mu, sd = f["repeated_words_null"]
    zc3 = (f["repeated_words"] - mu) / max(sd, 1.0)
    rows.append(("C3 repeated words >=3", f["repeated_words"], LP2["repeated_words"],
                 "within 3 sd of own shuffle null (%.1f +- %.1f)" % (mu, sd), "PASS" if zc3 <= 3 else "FAIL"))
    rows.append(("C4 adjacent word-length z", round(f["wordlen_z"], 2), 0.9, "|z| < 3 (layout, not cipher)",
                 "PASS" if abs(f["wordlen_z"]) < 3 else "INFO"))
    rows.append(("C5 within-word lag-5 rate", round(f["lag5_rate"], 4), round(104 / 2105, 4), "[0.039, 0.060] (soft)",
                 "PASS" if 0.039 <= f["lag5_rate"] <= 0.060 else "FAIL(soft)"))
    xd = f["doublets_cross"] / k
    rows.append(("C6 cross-word doublets (LP2-size)", round(xd, 1), LP2["doublets_cross"], "[12, 35]",
                 "PASS" if 12 <= xd <= 35 else "FAIL"))
    return rows


def lp2():
    U, C, sha = lpdata.unsolved()
    assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    W = [w for p in U for w in p["word"]]
    L = [x for p in U for x in p["line"]]
    P = [p["page"] for p in U for _ in p["idx"]]
    return C, W, L, P


def _show(f):
    for k, v in f.items():
        print("  %-22s %s" % (k, v))
    for row in gate(f):
        print("  %-36s %-10s LP2 %-8s band %-46s %s" % row)


if __name__ == "__main__":
    if "--english" in sys.argv:
        import runes as rn
        R, W = rn.english_stream(12956)
        print("English (Moby-Dick) runes, 12,956:")
        _show(fingerprint(R, W))
    else:
        C, W, L, P = lp2()
        f = fingerprint(C, W, L, P)
        print("LP2 pages 0-54:")
        _show(f)
        assert f["doublets"] == 86 and f["doublets_within"] == 63 and f["doublets_cross"] == 23
        assert (f["lag5_hits"], f["lag5_pairs"]) == (104, 2105)
        assert f["lag5_straddle"] == (32, 460)
        assert abs(f["cond_ioc"] - 1.026) < 0.002, f["cond_ioc"]
        print("pins OK")
