# ABOUTME: Lane Y library: lane X's key-free odometer-dodge attack for keys that restart at each section or page
# ABOUTME: (segment-local word cycles and clock, free clock reset at segment starts, anchors kept inside segments).
"""Lane X assumed one key running unbroken over pages 0-54. Here the same key (K, schedule, start dials) restarts at
the start of every segment (a chapter or a page), the way LP1's keyed pages restarted their key. Then:

  - the inner dial restarts, so a word's cycle is its index inside the segment: r = w_local mod 29;
  - the outer dial restarts, so y = c - floor(w_local / 29);
  - the clock restarts, so the base phase is the rune's index inside the segment, and the hidden drift is free to
    jump at a segment start (the transition matrix is uniform there);
  - a doublet across a segment start is not an anchor (the dodge has no previous rune to compare with).

Groups (r, phase) are again fixed substitutions shared by every segment, so the evidence of all segments pools.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(HERE), str(REPO / "agents" / "laneX_general_alphabet")]
import xlib as X  # noqa: E402
import stage2 as S2  # noqa: E402

M, NG = X.M, X.NG


def lp2_words_meta():
    """LP2 words with the page and chapter of each word (of its first rune)."""
    import lpdata
    U, _C, sha = lpdata.unsolved()
    assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    words, page, chap, cur, last = [], [], [], [], None
    for p in U:
        for x, wid, ch in zip(p["idx"], p["word"], p["chap"]):
            key = (p["page"], wid)
            if key != last:
                if cur:
                    words.append(cur)
                cur = []
                page.append(p["page"])
                chap.append(ch)
            cur.append(x)
            last = key
    words.append(cur)
    return words, page, chap


def seg_ids(labels):
    """Word labels (page or chapter per word) -> segment index per word, a new segment wherever the label changes."""
    out, s, prev = [], -1, object()
    for lab in labels:
        if lab != prev:
            s += 1
            prev = lab
        out.append(s)
    return out


def encipher_segments(words, segw, K, offsets, start, space_skip, variant):
    """The same key restarted at every segment: encipher each segment separately, concatenate."""
    out, phases = [], []
    i = 0
    while i < len(words):
        j = i
        while j < len(words) and segw[j] == segw[i]:
            j += 1
        cw, ph = X.encipher_trace(words[i:j], K, offsets, start, space_skip, variant)
        out += cw
        phases += ph
        i = j
    return out, phases


def local_obs(words, segw, kspace=0):
    """Per rune: y, r, base phase t, segment-start mask, anchor positions (inside segments only)."""
    y, r, t, start, c = [], [], [], [], []
    wl, il, prev_seg = 0, 0, None
    for w, word in enumerate(words):
        if segw[w] != prev_seg:
            wl, il, prev_seg = 0, 0, segw[w]
            first = True
        else:
            first = False
        for k, x in enumerate(word):
            y.append((x - wl // 29) % M)
            r.append(wl % 29)
            t.append((il + kspace * wl) % 5)
            start.append(first and k == 0)
            c.append(x)
            il += 1
        wl += 1
    y, r, t, start, c = (np.array(a) for a in (y, r, t, start, c))
    dbl = np.flatnonzero(c[1:] == c[:-1]) + 1
    anc = dbl[~start[dbl]]
    return y.astype(np.int64), r.astype(np.int64), t.astype(np.int64), start, c.astype(np.int64), anc


def anchor_counts(words, segw, L=8):
    y, r, _t, start, _c, anc = local_obs(words, segw)
    seg_start_pos = np.flatnonzero(start)
    C = np.zeros((29, 5, M))
    for j in range(L + 1):
        p = anc + j
        ok = p < len(y)
        # stop at the next segment start
        nxt = np.searchsorted(seg_start_pos, anc, side="right")
        bound = np.where(nxt < len(seg_start_pos), seg_start_pos[np.minimum(nxt, len(seg_start_pos) - 1)], len(y))
        ok &= p < bound
        p = p[ok]
        np.add.at(C, (r[p], j % 5, y[p]), 1.0)
    return C, len(anc)


def _fb_reset(E, T, reset):
    """Forward-backward with the uniform transition at positions where `reset` is true."""
    B, N, _ = E.shape
    U = np.full((5, 5), 0.2)
    fa = np.empty((N, B, 5))
    a = np.full((B, 5), 0.2) * E[:, 0, :]
    s = a.sum(1, keepdims=True)
    loglik = np.log(s[:, 0])
    fa[0] = a / s
    for n in range(1, N):
        a = (fa[n - 1] @ (U if reset[n] else T)) * E[:, n, :]
        s = a.sum(1, keepdims=True)
        loglik += np.log(s[:, 0])
        fa[n] = a / s
    be = np.ones((B, 5))
    post = np.empty((N, B, 5))
    post[N - 1] = fa[N - 1]
    for n in range(N - 2, -1, -1):
        be = (E[:, n + 1, :] * be) @ (U if reset[n + 1] else T).T
        be /= be.sum(1, keepdims=True)
        p = fa[n] * be
        post[n] = p / p.sum(1, keepdims=True)
    return post.transpose(1, 0, 2), loglik


def fit_tied(words, segw, starts, kspace=0, iters=20, eps=0.035, alpha=0.5, L=8):
    y, r, t, start, c, anc = local_obs(words, segw, kspace)
    N, B = len(y), len(starts)
    i = np.arange(N)
    G = r[:, None] * 5 + (t[:, None] + np.arange(5)[None, :]) % 5
    T = X._transitions(eps, "both")
    mask = np.ones((N, 5))
    if len(anc):
        mask[anc, :] = 0.0
        mask[anc, (-t[anc]) % 5] = 1.0
    C0, _ = anchor_counts(words, segw, L=L)
    Sh = np.array(starts, np.int64)
    theta = X.tied_theta(np.broadcast_to(C0.reshape(1, NG, M), (B, NG, M)), Sh, alpha)
    yy = y[None, :, None]
    for _it in range(iters):
        E = theta[np.arange(B)[:, None, None], G[None], yy] * mask[None]
        gam, loglik = _fb_reset(E, T, start)
        flat = ((np.arange(B)[:, None, None] * NG + G[None]) * M + yy).ravel()
        cnt = np.bincount(flat, weights=gam.ravel(), minlength=B * NG * M).reshape(B, NG, M)
        for b in range(B):
            Sh[b] = X.fit_shifts(cnt[b], Sh[b], sweeps=1)
        theta = X.tied_theta(cnt, Sh, alpha)
    out = []
    for b in range(B):
        d = gam[b].argmax(1)
        g = G[i, d]
        cnt = np.bincount(g * M + y, minlength=NG * M).reshape(NG, M).astype(float)
        out.append({"S": list(map(int, Sh[b])), "score": float(X.dm_score(X.pool(cnt, Sh[b]))) / N,
                    "phase": (t + d) % 5, "kspace": kspace, "finite": bool(np.isfinite(loglik[b]))})
    return out


def stage2(words, segw, best, q, rng):
    """a0 by S-pooled coherence with segment-local outer-dial steps, then lane X's alignment and substitution solve."""
    y0, r, _t, _s, c, _a = local_obs(words, segw)
    wl = []
    prev, k = None, 0
    for w, word in enumerate(words):
        k = 0 if segw[w] != prev else k + 1
        prev = segw[w]
        wl += [k] * len(word)
    wl = np.array(wl)
    phase = np.asarray(best["phase"])
    scores = []
    for a0 in range(M):
        y = (c - (a0 + wl) // 29) % M
        cnt = np.bincount((r * 5 + phase) * M + y, minlength=NG * M).reshape(NG, M).astype(float)
        scores.append(float(X.dm_score(X.pool(cnt, best["S"]))))
    a0 = int(np.argmax(scores))
    x = (c - (a0 + wl) // 29) % M
    tau = (wl + np.asarray(best["S"])[phase]) % M
    res = S2.solve_stage2(x, tau, q, rng)
    return {"a0": a0, "ioc": res["ioc"], "quad_full": res["quad_full"], "plain": res["plain"]}


def attack(words, segw, seed, kspaces=(0, 1, 2, 3, 4), do_stage2=True):
    rng = np.random.default_rng(seed)
    C, n_anchor = anchor_counts(words, segw)
    starts = [s for v in ("advance", "hold") for _sc, s in X.shift_scan(C, v, top=4)[0]]
    fits = []
    for ks in kspaces:
        fits += fit_tied(words, segw, starts, kspace=ks)
    best = max(fits, key=lambda f: f["score"])
    rec = {"anchors": int(n_anchor), "s1_score": best["score"], "S": best["S"], "kspace": best["kspace"],
           "phase": best["phase"], "chains": len(fits), "dead_chains": sum(not f["finite"] for f in fits),
           "best_finite": best["finite"]}
    if do_stage2:
        rec.update(stage2(words, segw, best, S2.quad_table(), rng))
    return rec
