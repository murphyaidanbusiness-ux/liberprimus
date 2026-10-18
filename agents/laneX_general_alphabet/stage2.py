# ABOUTME: Lane X stage 2: recover the keyed alphabet K (and the dial constants) from stage 1's schedule and clock
# ABOUTME: path, by hill-climbing K against a rune quadgram model trained on texts other than the plant source.
"""Stage 2.

Given stage 1's schedule S (anchor coordinates) and phase f_i per rune, every rune's decryption is

    p_i = K[ (K^-1[(x_i - b0) mod 29] - A - tau_i) mod 29 ],   x_i = c_i - floor((a0 + w_i) / 29),   tau_i = w_i + S[f_i]

with a0 the start inner dial (it fixes where the outer dial steps), A = a0 + S_true[anchor phase] (the shift constant)
and b0 the start outer dial. K, A and b0 cannot be absorbed into one another, so stage 2 climbs K for each (A, b0).
a0 is found first from stage 1 alone (it decides which word cycles share an outer-dial step; `choose_a0`).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import xlib as X  # noqa: E402

M = 29
TRAIN = ["dl/dukotah/liber-primus/data/keys/armada18/poe_complete_works.txt",
         "dl/dukotah/liber-primus/data/keys/armada18/plato_republic_jowett.txt",
         "dl/dukotah/liber-primus/data/keys/armada18/emerson_essays_first_series.txt"]
_Q = {}


def quad_table(n_per_text=1_200_000):
    """log10 rune 4-gram probabilities (add-0.5), trained on TRAIN (not Moby-Dick, the plants' source)."""
    if "q" not in _Q:
        import runes as rn
        cnt = np.zeros(M ** 4)
        for path in TRAIN:
            R, _W = rn.english_stream(n_per_text, path=path, skip_chars=5000)
            R = np.array(R, np.int64)
            idx = ((R[:-3] * M + R[1:-2]) * M + R[2:-1]) * M + R[3:]
            cnt += np.bincount(idx, minlength=M ** 4)
        cnt += 0.5
        _Q["q"] = np.log10(cnt / cnt.sum()).astype(np.float64)
    return _Q["q"]


def quad_score(p, q):
    p = np.asarray(p, np.int64)
    idx = ((p[:-3] * M + p[1:-2]) * M + p[2:-1]) * M + p[3:]
    return float(q[idx].mean())


def choose_a0(words, phase, S, alpha=0.5):
    """The start inner dial: the a0 whose outer-dial steps make the S-pooled tables most coherent."""
    c = np.array([x for word in words for x in word], np.int64)
    _y, r, w = X.observations(words)
    out = []
    for a0 in range(M):
        y = (c - (a0 + w) // 29) % M
        g = r * 5 + np.asarray(phase)
        cnt = np.bincount(g * M + y, minlength=X.NG * M).reshape(X.NG, M).astype(float)
        out.append(float(X.dm_score(X.pool(cnt, S), alpha)))
    best = int(np.argmax(out))
    return best, out


def setup(words, phase, S, a0):
    c = np.array([x for word in words for x in word], np.int64)
    _y, _r, w = X.observations(words)
    x = (c - (a0 + w) // 29) % M
    tau = (w + np.asarray(S)[np.asarray(phase)]) % M
    return x, tau


def decrypt(K, Kinv, x, tau, A, b0):
    return K[(Kinv[(x - b0) % M] - A - tau) % M]


def climb(x, tau, A, b0, q, rng, iters=6000, start=None, temp0=0.0):
    """First-improvement random-swap climb on K (simulated annealing if temp0 > 0). Returns (score, K)."""
    K = np.array(start if start is not None else rng.permutation(M), np.int64)
    Kinv = np.argsort(K)
    cur = quad_score(decrypt(K, Kinv, x, tau, A, b0), q)
    best = (cur, K.copy())
    for it in range(iters):
        i, j = rng.choice(M, 2, replace=False)
        K[i], K[j] = K[j], K[i]
        Kinv[K[i]], Kinv[K[j]] = i, j
        s = quad_score(decrypt(K, Kinv, x, tau, A, b0), q)
        T = temp0 * (1 - it / iters)
        if s >= cur or (T > 0 and rng.random() < math.exp((s - cur) / T)):
            cur = s
            if s > best[0]:
                best = (s, K.copy())
        else:
            K[i], K[j] = K[j], K[i]
            Kinv[K[i]], Kinv[K[j]] = i, j
    return best


def decrypt2(P, Q, x, tau):
    return P[(Q[x] - tau) % M]


def climb2(x, tau, q, rng, iters=30000, start=None):
    """Climb two free permutations: p = P[(Q[x] - tau) mod 29].

    The true key is the special case P = K, Q = K^-1 shifted by b0 and A, so A and b0 are absorbed and need no
    enumeration (and a Quagmire-IV-style odometer with separate plaintext and cipher alphabets is covered too).
    Returns (score, P, Q).
    """
    if start is None:
        P, Q = rng.permutation(M), rng.permutation(M)
    else:
        P, Q = (np.array(a, np.int64) for a in start)
    P, Q = np.array(P, np.int64), np.array(Q, np.int64)
    cur = quad_score(decrypt2(P, Q, x, tau), q)
    for _ in range(iters):
        T = P if rng.random() < 0.5 else Q
        i, j = rng.choice(M, 2, replace=False)
        T[i], T[j] = T[j], T[i]
        s = quad_score(decrypt2(P, Q, x, tau), q)
        if s >= cur:
            cur = s
        else:
            T[i], T[j] = T[j], T[i]
    return cur, P, Q


def decryptU(U, Uinv, x, tau, A, b0):
    """With U = K^-1 composed with the outer shift, p = U^-1[(U[x] - A - tau)] - b0 (the same map as decrypt)."""
    return (Uinv[(U[x] - A - tau) % M] - b0) % M


def best_shift(out, q, ks=range(M)):
    sc = [quad_score((out - k) % M, q) for k in ks]
    k = int(np.argmax(sc))
    return list(ks)[k], sc[k]


def climbU(x, tau, q, rng, A=None, iters=6000, reopt=300):
    """Climb U with b0 (and A, if A is None) re-optimised every `reopt` steps. Returns (score, U, A, b0)."""
    U = np.array(rng.permutation(M), np.int64)
    Uinv = np.argsort(U)
    fixedA = A is not None
    A = A if fixedA else int(rng.integers(M))
    b0 = 0
    cur = quad_score(decryptU(U, Uinv, x, tau, A, b0), q)
    for it in range(iters):
        if it % reopt == 0:
            if not fixedA:
                cand = [(best_shift(decryptU(U, Uinv, x, tau, a, 0), q), a) for a in range(M)]
                (b0, cur), A = max(cand, key=lambda z: z[0][1])
            else:
                b0, cur = best_shift(decryptU(U, Uinv, x, tau, A, 0), q)
        i, j = rng.choice(M, 2, replace=False)
        U[i], U[j] = U[j], U[i]
        Uinv[U[i]], Uinv[U[j]] = i, j
        s = quad_score(decryptU(U, Uinv, x, tau, A, b0), q)
        if s >= cur:
            cur = s
        else:
            U[i], U[j] = U[j], U[i]
            Uinv[U[i]], Uinv[U[j]] = i, j
    if not fixedA:
        cand = [(best_shift(decryptU(U, Uinv, x, tau, a, 0), q), a) for a in range(M)]
        (b0, cur), A = max(cand, key=lambda z: z[0][1])
    return cur, U, A, b0


def diff_table(n_per_text=1_200_000):
    """log10 trigram model of rune differences d_i = p_i - p_(i-1): English scored up to a global Caesar shift."""
    if "d" not in _Q:
        import runes as rn
        cnt = np.zeros(M ** 3)
        for path in TRAIN:
            R, _W = rn.english_stream(n_per_text, path=path, skip_chars=5000)
            d = np.diff(np.array(R, np.int64)) % M
            idx = (d[:-2] * M + d[1:-1]) * M + d[2:]
            cnt += np.bincount(idx, minlength=M ** 3)
        cnt += 0.5
        _Q["d"] = np.log10(cnt / cnt.sum())
    return _Q["d"]


def diff_score(out, dq):
    d = np.diff(np.asarray(out, np.int64)) % M
    return float(dq[(d[:-2] * M + d[1:-1]) * M + d[2:]].mean())


def climbU_diff(x, tau, A, dq, rng, iters=6000, start=None):
    """Climb U for one A with the shift-invariant difference model (b0 drops out). Returns (score, U)."""
    U = np.array(start if start is not None else rng.permutation(M), np.int64)
    Uinv = np.argsort(U)
    cur = diff_score(Uinv[(U[x] - A - tau) % M], dq)
    for _ in range(iters):
        i, j = rng.choice(M, 2, replace=False)
        U[i], U[j] = U[j], U[i]
        Uinv[U[i]], Uinv[U[j]] = i, j
        s = diff_score(Uinv[(U[x] - A - tau) % M], dq)
        if s >= cur:
            cur = s
        else:
            U[i], U[j] = U[j], U[i]
            Uinv[U[i]], Uinv[U[j]] = i, j
    return cur, U


def U_to_key(U, A, x, tau, q):
    """From U (= K^-1 after the outer shift) pick b0 by the quadgram model and return (K, b0, score)."""
    Uinv = np.argsort(U)
    out = Uinv[(U[x] - A - tau) % M]                      # = p + b0
    b0, s = best_shift(out, q)
    K = (Uinv - b0) % M                                   # K[v] = U^-1[v] - b0
    return K, b0, s


def ioc_of(out):
    n = len(out)
    c = np.bincount(out, minlength=M).astype(float)
    return float(M * (c * (c - 1)).sum() / (n * (n - 1)))


def climb_ioc(x, tau, b0, rng, iters=5000, start=None, A=0):
    """Climb K for the unigram IoC of the decrypt. With K and b0 right, every table decrypts through the same fixed
    permutation whatever A is, so the output is a relabelled English (IoC ~1.7); misaligned tables flatten it.
    Returns (ioc, K)."""
    K = np.array(start if start is not None else rng.permutation(M), np.int64)
    Kinv = np.argsort(K)
    cur = ioc_of(decrypt(K, Kinv, x, tau, A, b0))
    for _ in range(iters):
        i, j = rng.choice(M, 2, replace=False)
        K[i], K[j] = K[j], K[i]
        Kinv[K[i]], Kinv[K[j]] = i, j
        s = ioc_of(decrypt(K, Kinv, x, tau, A, b0))
        if s >= cur:
            cur = s
        else:
            K[i], K[j] = K[j], K[i]
            Kinv[K[i]], Kinv[K[j]] = i, j
    return cur, K


def best_A(K, x, tau, b0, q):
    Kinv = np.argsort(K)
    sc = [quad_score(decrypt(K, Kinv, x, tau, A, b0), q) for A in range(M)]
    A = int(np.argmax(sc))
    return A, sc[A]


def climb_sub(o, q, rng, iters=4000, n_fit=3000, restarts=3):
    """Solve a monoalphabetic substitution: find Z^-1 maximising the quadgram score of Z^-1[o]. Returns (score, Zinv)."""
    o = np.asarray(o, np.int64)
    fit = o[:n_fit]
    # start from a frequency match: most frequent cipher symbols -> most frequent English runes
    eng = np.argsort(-np.bincount(np.array(_eng_sample()), minlength=M))
    obs = np.argsort(-np.bincount(fit, minlength=M))
    best = (-99.0, None)
    for r in range(restarts):
        Zinv = np.empty(M, np.int64)
        Zinv[obs] = eng
        if r:
            for _ in range(3):
                i, j = rng.choice(M, 2, replace=False)
                Zinv[i], Zinv[j] = Zinv[j], Zinv[i]
        cur = quad_score(Zinv[fit], q)
        for _ in range(iters):
            i, j = rng.choice(M, 2, replace=False)
            Zinv[i], Zinv[j] = Zinv[j], Zinv[i]
            s = quad_score(Zinv[fit], q)
            if s >= cur:
                cur = s
            else:
                Zinv[i], Zinv[j] = Zinv[j], Zinv[i]
        if cur > best[0]:
            best = (cur, Zinv.copy())
    return best


def _eng_sample():
    if "e" not in _Q:
        import runes as rn
        _Q["e"] = rn.english_stream(200000, path=TRAIN[0], skip_chars=5000)[0]
    return _Q["e"]


def solve_stage2(x, tau, q, rng, ioc_iters=3000, ioc_restarts=2):
    """Align the tables by an IoC climb on K (b0 = A = 0 is enough: alignment leaves a fixed substitution Z),
    then solve that substitution. Returns dict with the plaintext and scores."""
    best = (-1.0, None)
    for _ in range(ioc_restarts):
        s, K = climb_ioc(x, tau, 0, rng, iters=ioc_iters)
        if s > best[0]:
            best = (s, K)
    ioc, K = best
    o = decrypt(K, np.argsort(K), x, tau, 0, 0)
    qs, Zinv = climb_sub(o, q, rng)
    plain = Zinv[o]
    return {"ioc": ioc, "quad_fit": qs, "quad_full": quad_score(plain, q), "plain": plain, "K_aligned": K, "Zinv": Zinv}
