"""t7: does the within-word lag-5 echo sit in pairs that straddle a line break? (round two, verifying lane R)
Part 1: lag-5 split by straddle, length strata, length-stratified permutation test. Part 2: lags 1..10 by word x line."""
import sys, math, collections
sys.path.insert(0, "lp"); import lpdata
U, C, sha = lpdata.unsolved(); assert sha.startswith("023312066df4")
W = [w for p in U for w in p["word"]]; L = [l for p in U for l in p["line"]]; N = len(C)
wlen = collections.Counter(W)
rows = []
for a in range(N - 5):
    b = a + 5
    if W[a] == W[b]:
        rows.append((C[a] == C[b], L[a] != L[b], wlen[W[a]]))
def stat(sel, name):
    n = len(sel); m = sum(r[0] for r in sel); e = n / 29
    z = (m - e) / math.sqrt(e * 28 / 29) if n else 0
    print("%-34s n=%5d match=%4d rate=%.4f z=%+.2f" % (name, n, m, m / max(n, 1), z))
stat(rows, "all within-word lag-5")
stat([r for r in rows if r[1]], "straddles a line break")
stat([r for r in rows if not r[1]], "same line")
print("by word length (straddle | same line):")
for lo, hi in [(6, 7), (8, 9), (10, 11), (12, 99)]:
    s = [r for r in rows if lo <= r[2] <= hi]
    a = [r for r in s if r[1]]; b = [r for r in s if not r[1]]
    print("  len %2d-%2d  straddle n=%4d m=%3d (%.3f)   same n=%4d m=%3d (%.3f)" % (
        lo, hi, len(a), sum(r[0] for r in a), sum(r[0] for r in a) / max(1, len(a)),
        len(b), sum(r[0] for r in b), sum(r[0] for r in b) / max(1, len(b))))
# word-length-matched expectation for straddle pairs under "same-line rate per length"
import random
exp = 0.0
bylen = collections.defaultdict(lambda: [0, 0])
for m, s, l in rows:
    if not s: bylen[l][0] += m; bylen[l][1] += 1
for m, s, l in rows:
    if s:
        k = bylen[l]; exp += (k[0] / k[1]) if k[1] else 1 / 29
obs = sum(r[0] for r in rows if r[1]); ns = sum(1 for r in rows if r[1])
print("straddle observed %d vs same-line-rate-matched expectation %.1f (n=%d)" % (obs, exp, ns))
# permutation test: shuffle the straddle label within word-length strata
lab = collections.defaultdict(list)
for i, r in enumerate(rows): lab[r[2]].append(i)
rng = random.Random(3301); ge = 0; T = 20000
mm = [r[0] for r in rows]
for t in range(T):
    tot = 0
    for l, idx in lab.items():
        k = sum(1 for i in idx if rows[i][1])
        tot += sum(mm[i] for i in rng.sample(idx, k))
    ge += tot >= obs
print("permutation p (straddle excess, length-stratified) = %.4f" % ((ge + 1) / (T + 1)))

print()

W = [w for p in U for w in p["word"]]; L = [l for p in U for l in p["line"]]; N = len(C)
def z(m, n): e = n / 29; return (m - e) / math.sqrt(e * 28 / 29) if n else 0
print("lag | within-word: straddle (n, rate, z) | same line (n, rate, z) || cross-word: straddle | same line")
for k in range(1, 11):
    cell = {}
    for a in range(N - k):
        b = a + k
        key = (W[a] == W[b], L[a] != L[b])
        m, n = cell.get(key, (0, 0)); cell[key] = (m + (C[a] == C[b]), n + 1)
    out = []
    for key in [(True, True), (True, False), (False, True), (False, False)]:
        m, n = cell.get(key, (0, 0))
        out.append("%5d %.4f %+5.2f" % (n, m / max(n, 1), z(m, n)))
    print("%2d | %s | %s || %s | %s" % (k, *out))
