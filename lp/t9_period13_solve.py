"""t9: try to solve LP2 pages 53-54 (the community's "54-55", 308 runes) as a period-P Vigenere or Beaufort on the
increment stream D_i = (c_i - c_(i-1)) mod 29, i.e. a chain cipher c_i = c_(i-1) + f(p_i, k_(i mod P)).
Motivated by the period-13 harmonic (lags 13, 26, 39) found by lane U and t8.

Solver: per-column unigram start, then coordinate ascent of each column's shift on English quadgrams, with restarts.
Controls: planted English of the same length and period, both models. Null: the same solve on D shuffled within the
section (keeps the doublet count). Usage: python lp/t9_period13_solve.py [period] [restarts] [nulls]
"""
import math
import random
import sys

sys.path[:0] = ["lp", "toolbox"]
import lpdata  # noqa: E402
import runes as rn  # noqa: E402
import score as sc  # noqa: E402

P = int(sys.argv[1]) if len(sys.argv) > 1 else 13
RESTARTS = int(sys.argv[2]) if len(sys.argv) > 2 else 12
NULLS = int(sys.argv[3]) if len(sys.argv) > 3 else 20
M = 29
lq, floor = sc._table()
# unigram log-frequencies of English runes (from the register text)
R, _W = rn.english_stream(60000)
cnt = [1] * M
for r in R:
    cnt[r] += 1
LU = [math.log(c / sum(cnt)) for c in cnt]


def decrypt(D, key, model):
    return [((d - key[i % P]) if model == "V" else (key[i % P] - d)) % M for i, d in enumerate(D)]


def qs(p):
    return sc.quadgram(p)


def solve(D, model, rng, restarts=RESTARTS):
    best = (-1e9, None)
    cols = [[d for i, d in enumerate(D) if i % P == j] for j in range(P)]
    start = []
    for j in range(P):                        # unigram-best shift per column
        sc_ = [(sum(LU[((d - k) if model == "V" else (k - d)) % M] for d in cols[j]), k) for k in range(M)]
        start.append(max(sc_)[1])
    for r in range(restarts):
        key = list(start) if r == 0 else [rng.randrange(M) for _ in range(P)]
        cur = qs(decrypt(D, key, model))
        improved = True
        while improved:
            improved = False
            for j in rng.sample(range(P), P):
                old = key[j]
                for k in range(M):
                    if k == old:
                        continue
                    key[j] = k
                    s = qs(decrypt(D, key, model))
                    if s > cur + 1e-12:
                        cur, old, improved = s, k, True
                key[j] = old
        if cur > best[0]:
            best = (cur, list(key))
    return best


def inc(r):
    return [(r[i] - r[i - 1]) % M for i in range(1, len(r))]


def main():
    rng = random.Random(1301)
    U, C, sha = lpdata.unsolved()
    assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    pg = {p["page"]: p["idx"] for p in U}
    sec = pg[53] + pg[54]
    D = inc(sec)
    print("period %d; section pages 53-54: %d runes, %d increments, %d zero increments" % (P, len(sec), len(D), D.count(0)))
    # controls
    E, _ = rn.english_stream(40000)
    for model in ("V", "B"):
        rec = []
        for t in range(5):
            o = rng.randrange(0, len(E) - 400)
            p = E[o:o + len(D)]
            key = [rng.randrange(M) for _ in range(P)]
            Dp = [((x + key[i % P]) if model == "V" else (key[i % P] - x)) % M for i, x in enumerate(p)]
            s, k = solve(Dp, model, rng)
            right = sum(a == b for a, b in zip(k, key))
            rec.append((round(s, 3), right))
        print("control %s: (quadgram score, key letters right of %d) %s" % (model, P, rec))
    # null and real
    for model in ("V", "B"):
        nul = []
        for t in range(NULLS):
            Ds = D[:]
            rng.shuffle(Ds)
            nul.append(solve(Ds, model, rng, restarts=max(4, RESTARTS // 3))[0])
        mu = sum(nul) / len(nul)
        sd = (sum((x - mu) ** 2 for x in nul) / len(nul)) ** 0.5
        s, k = solve(D, model, rng)
        p = decrypt(D, k, model)
        print("model %s: null %.3f +- %.3f (max %.3f, %d shuffles); REAL %.3f z %+.2f key %s" % (
            model, mu, sd, max(nul), len(nul), s, (s - mu) / sd, k))
        print("   real decrypt (first 120 runes): %s" % "".join(lpdata.TR[x] for x in p[:120]))
        print("   IoC of real decrypt %.3f" % sc.ioc(p))


if __name__ == "__main__":
    main()
