"""t8: harmonic periodicity scan (lags b, 2b, 3b; b = 2..13) over every page and page pair, raw runes and increments,
with an empirical null for the MAXIMUM cell: the same scan on whole-book replicates shuffled within pages.
Motivated by lane U (pages 53-54, period 13). Usage: python lp/t8_harmonic_scan.py [replicates] [shuffles_per_cell]"""
import sys
import numpy as np
sys.path.insert(0, "lp")
import lpdata

U, C, sha = lpdata.unsolved()
assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 20
S = int(sys.argv[2]) if len(sys.argv) > 2 else 300
pages = [np.array(p["idx"]) for p in U]
rng = np.random.default_rng(3301)


def inc(r):
    return (r[1:] - r[:-1]) % 29


def harm(X, b):
    return sum((X[..., :-k] == X[..., k:]).sum(-1) for k in (b, 2 * b, 3 * b))


def scan(pgs):
    best, cells = None, []
    units = [("p%02d" % p, pgs[p]) for p in range(55)] + \
            [("p%02d-%02d" % (p, p + 1), np.concatenate([pgs[p], pgs[p + 1]])) for p in range(54)]
    for name, r in units:
        for stream, X in (("D", inc(r)), ("raw", r)):
            n = len(X)
            if n < 79:
                continue
            sh = np.array([rng.permutation(X) for _ in range(S)])
            for b in range(2, 14):
                if 3 * b >= n - 20:
                    continue
                real = int(harm(X, b))
                nul = harm(sh, b)
                z = (real - nul.mean()) / max(nul.std(), 1e-9)
                cells.append((z, name, stream, b))
    return max(cells), cells


top, cells = scan(pages)
print("real: max cell z %+.2f at %s %s base %d; cells %d" % (top[0], top[1], top[2], top[3], len(cells)))
real_d13 = [c for c in cells if c[1] == "p53-54" and c[2] == "D" and c[3] == 13][0][0]
maxes = []
for rep in range(REPS):
    shuf = [inc_shuffled for inc_shuffled in pages]
    rp = []
    for p in pages:                       # shuffle increments within each page, rebuild runes (keeps the doublet deficit)
        d = inc(p)
        d = rng.permutation(d)
        rp.append(np.concatenate([[p[0]], (p[0] + np.cumsum(d)) % 29]))
    m, _ = scan(rp)
    maxes.append(m[0])
    print("replicate %2d: max cell z %+.2f (%s %s base %d)" % (rep, m[0], m[1], m[2], m[3]), flush=True)
maxes = np.array(maxes)
print("null max-cell z: mean %.2f sd %.2f max %.2f; replicates >= real max (%.2f): %d of %d" % (
    maxes.mean(), maxes.std(), maxes.max(), top[0], int((maxes >= top[0]).sum()), REPS))
print("p53-54 D base 13 cell z %+.2f" % real_d13)
