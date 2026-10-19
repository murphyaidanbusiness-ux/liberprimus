# ABOUTME: Lane AA probe of a phase-free, schedule-free statistic for one chapter's key: same-phase rune pairs in words
# ABOUTME: w and w+d satisfy y_u = rho^d(y_t) when their letters agree; climb the 29-cycle rho; plants, nulls, LP2.
"""python -I -X utf8 agents/laneAA_chapter_keys/coincidence_probe.py > agents/laneAA_chapter_keys/out/coincidence_probe.txt

Two runes at the same clock phase in words w and w+d have keys that differ by exactly d, so y_u = rho^d(y_t) whenever
their plaintext letters agree, where rho = K' add(1) K'^-1 is a 29-cycle (K' is K with the outer start dial folded in).
Climb K' to maximise those coincidences. No phase path, schedule or tables are needed, only the space skip and a0.
"""
import random
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO / "agents" / "laneY_section_reset")]
import ylib as Y  # noqa
import xlib as X  # noqa

M = 29
SW = np.array([(i, j) for i in range(M) for j in range(i + 1, M)])


def mats(words, kspace, a0, D=4, L=24):
    c = np.array([x for w in words for x in w])
    wi = np.array([k for k, w in enumerate(words) for _ in w])
    y = (c - (a0 + wi) // 29) % M
    N = len(c)
    Ms = np.zeros((D + 1, M, M))
    for lag in range(1, L + 1):
        t = np.arange(N - lag)
        u = t + lag
        d = wi[u] - wi[t]
        ok = (d >= 1) & (d <= D) & (((lag + kspace * d) % 5) == 0)
        np.add.at(Ms, (d[ok], y[t[ok]], y[u[ok]]), 1.0)
    return Ms


def score_many(Ks, Ms):
    B = Ks.shape[0]
    kap = np.argsort(Ks, axis=1)
    s = np.zeros(B)
    ar = np.arange(M)[None, :]
    rows = np.arange(B)[:, None]
    for d in range(1, Ms.shape[0]):
        img = Ks[rows, (kap + d) % M]          # rho^d(a) for every a
        s += Ms[d][ar, img].sum(1)
    return s


def climb(Ms, rng, restarts=30):
    best, bestK = -1, None
    for _ in range(restarts):
        K = np.array(rng.permutation(M))
        cur = score_many(K[None], Ms)[0]
        while True:
            C = np.repeat(K[None], len(SW), 0)
            C[np.arange(len(SW)), SW[:, 0]] = K[SW[:, 1]]
            C[np.arange(len(SW)), SW[:, 1]] = K[SW[:, 0]]
            sc = score_many(C, Ms)
            j = int(np.argmax(sc))
            if sc[j] <= cur:
                break
            K, cur = C[j], sc[j]
        if cur > best:
            best, bestK = cur, K
    return best, bestK


def main():
    words, _p, chap = Y.lp2_words_meta()
    rng = np.random.default_rng(1)
    for ch in (14, 8):
        lens = [len(w) for w, cc in zip(words, chap) if cc == ch]
        for idx in range(3):
            r = random.Random(4242 + idx + ch)
            flat = [x for w in X.english_words(sum(lens), 500000 + 7000 * idx) for x in w]
            it = iter(flat)
            plain = [[next(it) for _ in range(L)] for L in lens]
            K = r.sample(range(29), 29)
            offs = X.schedule(r)
            a0, b0 = r.randrange(29), r.randrange(29)
            ks = r.randrange(5)
            variant = "advance" if idx % 2 == 0 else "hold"
            cw, _ph = X.encipher_trace(plain, K, offs, (a0, b0), ks, variant)
            Ms = mats(cw, ks, a0)
            Kp = np.array([(k + b0) % 29 for k in K])
            true = score_many(Kp[None], Ms)[0]
            t0 = time.time()
            got, gK = climb(Ms, rng)
            # same rho? compare the cycle images
            kap = np.argsort(gK)
            same = all(gK[(kap[a] + 1) % 29] == Kp[(np.argsort(Kp)[a] + 1) % 29] for a in range(29))
            tot = Ms[1:].sum()
            print("ch %2d plant %d %-7s pairs %5d  true %4d  climbed %4d  same_rho %s  (%.1fs)" % (
                ch, idx, variant, tot, true, got, same, time.time() - t0), flush=True)
        # nulls: increment shuffles cut to the chapter, true settings unknown -> use kspace 0, a0 0
        import nulls
        for idx in range(3):
            pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(777 + idx))
            it = iter([x for p in pages for x in p])
            nw = [[next(it) for _ in w] for w in words]
            cw = [w for w, cc in zip(nw, chap) if cc == ch]
            Ms = mats(cw, 0, 0)
            got, _ = climb(Ms, rng)
            print("ch %2d null  %d          pairs %5d  climbed %4d" % (ch, idx, Ms[1:].sum(), got), flush=True)
        cw = [w for w, cc in zip(words, chap) if cc == ch]
        for ks in range(5):
            Ms = mats(cw, ks, 0)
            got, _ = climb(Ms, rng)
            print("ch %2d LP2 kspace %d     pairs %5d  climbed %4d" % (ch, ks, Ms[1:].sum(), got), flush=True)


if __name__ == "__main__":
    main()
