"""Claim 1 cross-check by a second route: no rune decoding at all (2026-10-19).

    python -X utf8 jobs/verify-lane/runs/discord_claim1_crosscheck.py [--seed 3] [--reps 20000]

Sentences are the English lines of the community translation (aautcsh idkfa `liber-primus-translation.txt`, one line
per dot-delimited sentence, as printed under each page's runes), transliterated with toolbox/runes.py (ING -> NG etc.).
Solved pages only: 01-16.jpg (LP1) and 73-74.jpg (AN END, PARABLE). Null: runes pooled and re-cut at the same sentence
lengths, as in discord_claims_verify.py, but written again here.
"""
import argparse
import re
import sys

import numpy as np

sys.path.insert(0, "toolbox")
import runes  # noqa: E402

PATH = "dl/dukotah/corpus/B-liber-primus/fetched/aautcsh__idkfa/assets/liber-primus-translation.txt"
GP = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
               103, 107, 109])


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def blocks():
    cur, pages = None, []
    for ln in open(PATH, encoding="utf-8").read().split("\n"):
        t = ln[2:].strip() if ln.startswith("#\t") else ""
        m = re.match(r"^(\d\d)\.jpg", t)
        if m:
            cur = dict(pages=[int(x) for x in re.findall(r"(\d\d)\.jpg", t)], lines=[])
            pages.append(cur)
            continue
        if cur is not None and t:
            cur["lines"].append(t)
    return pages


def sentences():
    out = []
    for b in blocks():
        if not any(p <= 16 or p in (73, 74) for p in b["pages"]):
            continue
        rl = [i for i, t in enumerate(b["lines"]) if any("ᚠ" <= ch <= "᛿" for ch in t)]
        if not rl:
            continue
        for t in b["lines"][rl[-1] + 1:]:
            if re.fullmatch(r"[A-Z][A-Z '\-]*", t) and not t.startswith(("SEGMENT", "CHAPTER")):
                out.append((t, runes.eng2runes(t)))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--reps", type=int, default=20000)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    S = sentences()
    sums = [int(GP[r].sum()) for _, r in S]
    obs = np.mean([is_prime(x) for x in sums])
    pool = GP[np.concatenate([r for _, r in S])]
    lens = np.array([len(r) for _, r in S])
    starts = np.r_[0, np.cumsum(lens)[:-1]]
    # vectorised primality for the null (sieve to the largest possible sentence sum)
    lim = int(max(lens) * GP.max()) + 1
    sv = np.ones(lim + 1, dtype=bool); sv[:2] = False
    for i in range(2, int(lim ** 0.5) + 1):
        if sv[i]:
            sv[i * i::i] = False
    null = np.array([sv[np.add.reduceat(pool[rng.permutation(len(pool))], starts)].mean() for _ in range(a.reps)])
    z = (obs - null.mean()) / null.std(ddof=1)
    print(f"translation route: {len(S)} sentences, {int(round(obs * len(S)))} prime = {obs:.1%}")
    print(f"  null {null.mean():.4f} +- {null.std(ddof=1):.4f}, max {null.max():.4f}; z {z:+.2f}; "
          f"p {(np.sum(null >= obs) + 1) / (len(null) + 1):.2g} (n={len(null)})")
    print("  first sentences: " + " | ".join(f"{t} = {s}{'*' if is_prime(s) else ''}" for (t, _), s in list(zip(S, sums))[:12]))
