# ABOUTME: Lane X library: the Quagmire-odometer dodge with a traced clock, LP2 and English loaders, and the
# ABOUTME: key-free stage-1 detector (an HMM over the clock drift that groups runes by word cycle and phase).
"""Why a key-free detector exists for this family.

The community cipher (doublet_phase_test.encipher) is   c = K[pos[p] + a_w + S[phase]] + b_w   (mod 29), where
the inner dial a_w rises by one per word, the outer dial b_w rises by one each time a_w wraps (every 29 words), S
is the running sum of a one-zero five-step schedule, and phase = clock mod 5 with the clock advancing one per rune
plus a drift of +1 ("advance") or -1 ("hold") at every dodged repeat.

Fix a word cycle r = w mod 29 and a phase k. Every rune in that group is enciphered by the same permutation
p -> K[pos[p] + a + S[k]], shifted by b_w; and inside the group b_w rises by exactly one per 29-word cycle, so
y = c - floor(w / 29) removes it up to a per-group constant (a relabel, which no within-group statistic sees).
So each of the 29 x 5 groups is a monoalphabetic substitution of English, whatever K and the schedule are. The
only unknown that decides the grouping is the clock drift, which is piecewise constant (it moves at the dodges,
about 3% of runes). Stage 1 fits it as a five-state hidden Markov chain and scores the grouping by a
Dirichlet-multinomial marginal likelihood (no fitted parameters in the score, so a null cannot win by
overfitting the per-group tables). Stage 2 (stage2.py) recovers the schedule and K from the groups.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PORT = REPO / "dl" / "aldegonde_port"
sys.path[:0] = [str(REPO / "toolbox"), str(REPO / "lp"), str(PORT / "src"), str(PORT / "experiments")]
# -I hides the user site-packages, where scipy lives (needed by the port and by dm_score)
import site  # noqa: E402
sys.path.append(site.getusersitepackages())
M = 29
NG = 29 * 5
VARIANTS = {"advance": (+1, 2), "hold": (-1, 0)}  # (phase used by the re-emit, clock step), as doublet_phase_test


def running(offsets):
    out, t = [], 0
    for s in offsets:
        t = (t + s) % M
        out.append(t)
    return out


def schedule(rng):
    """Five offsets summing to 0 mod 29 with exactly one zero (pure_quagmire_restart.schedule, zeros=1)."""
    while True:
        free = [rng.randrange(1, M) for _ in range(3)]
        last = (-sum(free)) % M
        if last == 0:
            continue
        offs = [*free, last, 0]
        rng.shuffle(offs)
        return offs


def encipher_trace(words, K, offsets, start, space_skip=0, variant="advance"):
    """doublet_phase_test.encipher for the two drifting variants, also returning the phase each rune used."""
    direction, advance = VARIANTS[variant]
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b = start
    out, phases, previous, clock = [], [], None, 0
    for word in words:
        cw = []
        for p in word:
            ph = clock % 5
            c = (K[(pos[p] + a + S[ph]) % M] + b) % M
            step = 1
            if c == previous:
                ph = (clock + direction) % 5
                c = (K[(pos[p] + a + S[ph]) % M] + b) % M
                step = advance
            cw.append(c)
            phases.append(ph)
            previous = c
            clock += step
        out.append(cw)
        clock += space_skip
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return out, phases


def lp2_words():
    """LP2 (pages 0-54) as a list of words, a word being a run of runes with one (page, word) id."""
    import lpdata
    U, _C, sha = lpdata.unsolved()
    assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    words, cur, last = [], [], None
    for p in U:
        for x, wid in zip(p["idx"], p["word"]):
            key = (p["page"], wid)
            if key != last and cur:
                words.append(cur)
                cur = []
            cur.append(x)
            last = key
    words.append(cur)
    return words


def english_words(n_runes, offset):
    """n_runes of English (toolbox/runes.english_stream) from rune `offset`, as words."""
    import runes as rn
    R, W = rn.english_stream(offset + n_runes + 200)
    R, W = R[offset:offset + n_runes], W[offset:offset + n_runes]
    out, cur, last = [], [], W[0]
    for x, w in zip(R, W):
        if w != last and cur:
            out.append(cur)
            cur = []
        cur.append(x)
        last = w
    out.append(cur)
    return out


def observations(words):
    """Flatten words to (y, r, w): y = c - floor(w/29) mod 29, r = w mod 29, w = word index."""
    y, r, w = [], [], []
    for wi, word in enumerate(words):
        for c in word:
            y.append((c - wi // 29) % M)
            r.append(wi % 29)
            w.append(wi)
    return np.array(y, np.int64), np.array(r, np.int64), np.array(w, np.int64)


def dm_score(counts, alpha=1.0):
    """Dirichlet-multinomial log marginal likelihood of hard counts (groups x 29), minus the uniform model, in nats."""
    from scipy.special import gammaln
    n_g = counts.sum(-1)
    ll = (gammaln(M * alpha) - gammaln(n_g + M * alpha)).sum(-1) + (gammaln(counts + alpha) - gammaln(alpha)).sum((-1, -2))
    return ll + n_g.sum(-1) * math.log(M)


def fit_stage1(words, kspaces=(0,), restarts=8, iters=25, eps=0.03, alpha=0.5, seed=0, n_use=None, drift="both",
               anchors=True, tie=False, tie_after=0):
    """Batched Baum-Welch over the clock drift for every (space skip, restart) chain.

    Returns a list of dicts, one per chain: kspace, restart, score (DM nats per rune, Viterbi-free: the posterior
    argmax path), phase (found phase per rune), loglik.
    """
    y, r, w = observations(words)
    if n_use:
        y, r, w = y[:n_use], r[:n_use], w[:n_use]
    N = len(y)
    chains = [(ks, rs) for ks in kspaces for rs in range(restarts)]
    B = len(chains)
    i = np.arange(N)
    t = np.stack([(i + ks * w) % 5 for ks, _ in chains])                       # (B, N) base phase
    G = r[None, :, None] * 5 + (t[:, :, None] + np.arange(5)[None, None, :]) % 5  # (B, N, 5) group per state
    T = np.full((5, 5), 0.0)
    for d in range(5):
        T[d, d] = 1 - eps
        if drift in ("both", +1):
            T[d, (d + 1) % 5] += eps / (2 if drift == "both" else 1)
        if drift in ("both", -1):
            T[d, (d - 1) % 5] += eps / (2 if drift == "both" else 1)
    rng = np.random.default_rng(seed)
    # Anchors: under this family a doublet survives only where the dodge re-emits with the alphabet it would have
    # used anyway, i.e. at one fixed clock phase. So at the second rune of every doublet the phase is that phase,
    # which the global relabel lets us call 0. The mask allows only the state giving phase 0 there.
    c = np.array([x for word in words for x in word], np.int64)[:N]
    anc = np.flatnonzero(c[1:] == c[:-1]) + 1 if anchors else np.array([], np.int64)
    mask = np.ones((B, N, 5))
    if len(anc):
        mask[:, anc, :] = 0.0
        need = (-t[:, anc]) % 5                                                     # (B, n_anchor) state giving phase 0
        mask[np.arange(B)[:, None], anc[None, :], need] = 1.0
    # init: restart 0 holds each anchor's state back to the previous anchor; the others add a random drift walk
    theta = np.empty((B, NG, M))
    for b in range(B):
        if len(anc):
            seg = np.searchsorted(anc, i, side="left").clip(max=len(anc) - 1)
            d0 = need[b][seg].copy()
            if b % restarts:
                steps = rng.choice([-1, 0, 1], size=N, p=[eps / 2, 1 - eps, eps / 2])
                d0 = (d0 + np.cumsum(steps) * (rng.random() < 0.5)) % 5
        else:
            steps = rng.choice([-1, 0, 1], size=N, p=[eps / 2, 1 - eps, eps / 2])
            d0 = (np.cumsum(steps) + rng.integers(5)) % 5
        g = G[b, i, d0]
        cnt = np.bincount(g * M + y, minlength=NG * M).reshape(NG, M) + alpha
        theta[b] = cnt / cnt.sum(1, keepdims=True)
    yy = y[None, :, None]
    bidx = np.arange(B)[:, None, None]
    loglik = np.zeros(B)
    Sh = np.zeros((B, 5), np.int64)
    Sh[:, 1:] = rng.integers(0, M, size=(B, 4))
    for _it in range(iters):
        E = theta[bidx, G, yy] * mask                                            # (B, N, 5)
        fa = np.empty((N, B, 5))
        a = np.full((B, 5), 0.2) * E[:, 0, :]
        s = a.sum(1, keepdims=True)
        loglik = np.log(s[:, 0])
        fa[0] = a / s
        for n in range(1, N):
            a = (fa[n - 1] @ T) * E[:, n, :]
            s = a.sum(1, keepdims=True)
            loglik += np.log(s[:, 0])
            fa[n] = a / s
        be = np.ones((B, 5))
        post = np.empty((N, B, 5))
        post[N - 1] = fa[N - 1]
        for n in range(N - 2, -1, -1):
            be = (E[:, n + 1, :] * be) @ T.T
            be /= be.sum(1, keepdims=True)
            p = fa[n] * be
            post[n] = p / p.sum(1, keepdims=True)
        gam = post.transpose(1, 0, 2)                                            # (B, N, 5)
        flat = ((np.arange(B)[:, None, None] * NG + G) * M + yy).ravel()
        cnt = np.bincount(flat, weights=gam.ravel(), minlength=B * NG * M).reshape(B, NG, M)
        if tie and _it >= tie_after:
            for b in range(B):
                Sh[b] = fit_shifts(cnt[b], Sh[b])
            theta = tied_theta(cnt, Sh, alpha)
        else:
            cnt = cnt + alpha
            theta = cnt / cnt.sum(2, keepdims=True)
    out = []
    for b, (ks, rs) in enumerate(chains):
        d = gam[b].argmax(1)
        g = G[b, i, d]
        cnt = np.bincount(g * M + y, minlength=NG * M).reshape(NG, M).astype(float)
        rec = {"kspace": ks, "restart": rs, "score": float(dm_score(cnt)) / N, "loglik": float(loglik[b]),
               "phase": (t[b] + d) % 5, "shifts": list(map(int, Sh[b]))}
        if tie:
            pooled = pool(cnt, Sh[b])
            rec["tied_score"] = float(dm_score(pooled)) / N
        out.append(rec)
    return out


def pool(cnt, S):
    """Pool (29 word cycles x 5 phases) counts into 29 shift tables: group (r, k) is shift (r + S[k]) mod 29."""
    C = cnt.reshape(29, 5, M)
    P = np.zeros((29, M))
    for k in range(5):
        P += np.roll(C[:, k, :], int(S[k]), axis=0)
    return P


def _ll(P):
    n = P.sum(-1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(P > 0, P * np.log(P / n), 0.0).sum((-1, -2))


def fit_shifts(cnt, S, sweeps=2):
    """Coordinate ascent on the per-phase shifts S[1..4] (S[0] = 0 fixes the relabel) by pooled likelihood."""
    C = cnt.reshape(29, 5, M)
    S = np.array(S, np.int64)
    for _ in range(sweeps):
        for k in range(1, 5):
            other = np.zeros((29, M))
            for j in range(5):
                if j != k:
                    other += np.roll(C[:, j, :], int(S[j]), axis=0)
            cand = np.stack([other + np.roll(C[:, k, :], v, axis=0) for v in range(M)])
            S[k] = int(np.argmax(_ll(cand)))
    return S


def tied_theta(cnt, Sh, alpha):
    B = cnt.shape[0]
    theta = np.empty((B, NG, M))
    r = np.arange(29)
    for b in range(B):
        P = pool(cnt[b], Sh[b]) + alpha
        P /= P.sum(1, keepdims=True)
        for k in range(5):
            theta[b, r * 5 + k] = P[(r + Sh[b][k]) % 29]
    return theta


def phase_accuracy(found, true):
    """Fraction of runes whose found phase equals the true phase, maximised over a global relabel k -> k + c."""
    found, true = np.asarray(found), np.asarray(true)
    return max(float(np.mean((found + c) % 5 == true)) for c in range(5))


def anchor_counts(words, L=8):
    """Counts (29 word cycles, 5 phases, 29 symbols) from the runes just after each doublet.

    The second rune of a doublet sits at phase 0 (the anchor); until the next dodge the clock advances one per rune,
    so the rune j after it is at phase j mod 5, in both the advance and the hold variant. Dodges hit about 3% of
    runes, so most of these L + 1 runes per anchor carry their true phase.
    """
    y, r, _w = observations(words)
    c = np.array([x for word in words for x in word], np.int64)
    anc = np.flatnonzero(c[1:] == c[:-1]) + 1
    C = np.zeros((29, 5, M))
    for j in range(L + 1):
        p = anc + j
        p = p[p < len(y)]
        np.add.at(C, (r[p], j % 5, y[p]), 1.0)
    return C, len(anc)


def shift_scan(C, variant, alpha=0.5, top=10):
    """Score every schedule tie by the DM likelihood of the anchor counts pooled into 29 shift tables.

    In anchor coordinates the re-emit phase is 0 and shares its alphabet with the would-be phase: phase 4 for the
    advance variant (S = [0, s1, s2, s3, 0]) and phase 1 for hold (S = [0, 0, s2, s3, s4]). Three free shifts each.
    Returns the top candidates as (score, S) and the score of every candidate (for a z against the rest).
    """
    from scipy.special import gammaln
    R = np.stack([np.stack([np.roll(C[:, k, :], v, axis=0) for v in range(M)]) for k in range(5)])  # (5, 29, 29, 29)
    if variant == "advance":
        fixed, free = R[0][0] + R[4][0], (1, 2, 3)
    else:
        fixed, free = R[0][0] + R[1][0], (2, 3, 4)
    a, b, c = free
    P = (fixed[None, None, None] + R[a][:, None, None] + R[b][None, :, None] + R[c][None, None, :])  # (29,29,29,29,29)
    n = P.sum(-1)
    sc = (gammaln(M * alpha) - gammaln(n + M * alpha)).sum(-1) + (gammaln(P + alpha) - gammaln(alpha)).sum((-1, -2))
    flat = sc.ravel()
    order = np.argsort(-flat)[:top]
    out = []
    for o in order:
        s = np.unravel_index(o, sc.shape)
        S = [0] * 5
        for k, v in zip(free, s):
            S[k] = int(v)
        out.append((float(flat[o]), S))
    return out, flat


# Lane X's verified runs used FLOOR = 0. Without a floor a chain dies (all-zero forward mass, NaN) when an anchor demands
# a phase two or more drift steps from where the path is; a small floor on every transition keeps it alive.
FLOOR = 0.0


def _transitions(eps, drift):
    T = np.zeros((5, 5))
    for d in range(5):
        T[d, d] = 1 - eps
        if drift in ("both", +1):
            T[d, (d + 1) % 5] += eps / (2 if drift == "both" else 1)
        if drift in ("both", -1):
            T[d, (d - 1) % 5] += eps / (2 if drift == "both" else 1)
    if FLOOR:
        T = T + FLOOR
        T /= T.sum(1, keepdims=True)
    return T


def _forward_backward(E, T):
    """E (B, N, 5) emission likelihoods -> posteriors (B, N, 5) and log-likelihood (B,)."""
    B, N, _ = E.shape
    fa = np.empty((N, B, 5))
    a = np.full((B, 5), 0.2) * E[:, 0, :]
    s = a.sum(1, keepdims=True)
    loglik = np.log(s[:, 0])
    fa[0] = a / s
    for n in range(1, N):
        a = (fa[n - 1] @ T) * E[:, n, :]
        s = a.sum(1, keepdims=True)
        loglik += np.log(s[:, 0])
        fa[n] = a / s
    be = np.ones((B, 5))
    post = np.empty((N, B, 5))
    post[N - 1] = fa[N - 1]
    for n in range(N - 2, -1, -1):
        be = (E[:, n + 1, :] * be) @ T.T
        be /= be.sum(1, keepdims=True)
        p = fa[n] * be
        post[n] = p / p.sum(1, keepdims=True)
    return post.transpose(1, 0, 2), loglik


def fit_tied(words, starts, kspace=0, iters=20, eps=0.035, alpha=0.5, drift="both", refit=True, L=8):
    """Stage 1b: the drift HMM with the 145 groups tied into 29 shift tables by a schedule S.

    `starts` is a list of S (anchor coordinates), one chain each, e.g. the top of shift_scan. Tables start from the
    anchor counts pooled by S; each M-step pools the expected counts by S, and (refit) re-fits S by coordinate ascent.
    Returns one dict per chain: S, score (DM of the hard path, pooled by S, nats per rune), untied score, phase.
    """
    y, r, w = observations(words)
    N = len(y)
    B = len(starts)
    i = np.arange(N)
    t = (i + kspace * w) % 5
    G = r[:, None] * 5 + (t[:, None] + np.arange(5)[None, :]) % 5          # (N, 5), same for every chain
    T = _transitions(eps, drift)
    c = np.array([x for word in words for x in word], np.int64)
    anc = np.flatnonzero(c[1:] == c[:-1]) + 1
    mask = np.ones((N, 5))
    if len(anc):
        mask[anc, :] = 0.0
        mask[anc, (-t[anc]) % 5] = 1.0
    C0, _ = anchor_counts(words, L=L)
    Sh = np.array(starts, np.int64)
    theta = tied_theta(np.broadcast_to(C0.reshape(1, NG, M), (B, NG, M)), Sh, alpha)
    yy = y[None, :, None]
    loglik = np.zeros(B)
    for _it in range(iters):
        E = theta[np.arange(B)[:, None, None], G[None], yy] * mask[None]
        gam, loglik = _forward_backward(E, T)
        flat = ((np.arange(B)[:, None, None] * NG + G[None]) * M + yy).ravel()
        cnt = np.bincount(flat, weights=gam.ravel(), minlength=B * NG * M).reshape(B, NG, M)
        if refit:
            for b in range(B):
                Sh[b] = fit_shifts(cnt[b], Sh[b], sweeps=1)
        theta = tied_theta(cnt, Sh, alpha)
    out = []
    for b in range(B):
        d = gam[b].argmax(1)
        g = G[i, d]
        cnt = np.bincount(g * M + y, minlength=NG * M).reshape(NG, M).astype(float)
        out.append({"S": list(map(int, Sh[b])), "start": list(map(int, starts[b])),
                    "score": float(dm_score(pool(cnt, Sh[b]))) / N, "untied": float(dm_score(cnt)) / N,
                    "loglik": float(loglik[b]), "phase": (t + d) % 5, "kspace": kspace,
                    "finite": bool(np.isfinite(loglik[b]))})
    return out
