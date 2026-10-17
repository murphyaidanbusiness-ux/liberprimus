"""laneK core: LP loader, English corpora, M_K cipher (K fixed alphabets, per-word phase, skip rule),
Oosterhof walk cipher, census statistics, LM training."""
import sys, os
import numpy as np
S = '.'
OUT = S + '/agents/laneK_walk_search'
sys.path.insert(0, S + '/lp'); sys.path.insert(0, S + '/agents/laneJ_lag5_echo')
import lpdata, core
TR = lpdata.TR; N29 = 29; BND = 29

def lp_main():
    C, wid, chap, page = core.lp_main()
    return C, wid, chap

def words_of(C, wid):
    starts = np.r_[0, np.nonzero(np.diff(wid))[0] + 1]
    return [C[a:b] for a, b in zip(starts, np.r_[starts[1:], len(C)])]

_WP = None
def wp_words():
    global _WP
    if _WP is None: _WP = core.load_wp_words(maxw=600000)
    return _WP

def wp_split():
    """train = first 480k words; heldout = rest (plants)."""
    W = wp_words(); return W[:480000], W[480000:]

def plain_contig(words, n=12956, seed=0):
    rng = np.random.default_rng(seed)
    o = rng.integers(len(words) - 5000); out = []; k = 0; i = o
    while k < n:
        w = words[i]; i += 1
        if k + len(w) > n: w = w[:n - k]
        out.append(np.array(w, dtype=np.int64)); k += len(w)
    return out

def plain_lenmatched(words, lens, seed=0):
    """Markov(0) word text with the LP's exact word-length sequence (word unigram draws from heldout)."""
    rng = np.random.default_rng(seed); bl = {}
    for w in words: bl.setdefault(len(w), []).append(w)
    out = []
    for L in lens:
        pool = bl[L] if L in bl and len(bl[L]) > 5 else None
        if pool is None:  # long words: concatenate two words
            a = bl[3][rng.integers(len(bl[3]))]; rest = L - 3
            b = bl[rest][rng.integers(len(bl[rest]))] if rest in bl else [0] * rest
            out.append(np.array(list(a) + list(b), dtype=np.int64)); continue
        out.append(np.array(pool[rng.integers(len(pool))], dtype=np.int64))
    return out

def solved_words():
    return [np.array(w, dtype=np.int64) for w in core.solved_words() if len(w)]

# ---------------- M_K cipher ----------------
# A: (K,29) array, A[a][p] = cipher rune. phase: per-word start clock.
# skip modes: 'none'; 'adv' (Oosterhof: if emission == previous cipher rune, clock += 1 extra, recompute once,
# extra step persists for the rest of the word); 'redraw' (only this position uses clock+1).
def enc_MK(words, A, phase, skip='adv', prev0=-1):
    K = A.shape[0]; out = []; prev = prev0
    for w, ph in zip(words, phase):
        t = int(ph); cw = np.empty(len(w), dtype=np.int64)
        for j, p in enumerate(w):
            c = A[t % K][p]
            if skip != 'none' and c == prev:
                if skip == 'adv':
                    t += 1; c = A[t % K][p]
                else:
                    c = A[(t + 1) % K][p]
            cw[j] = c; prev = c; t += 1
        out.append(cw)
    return out

def dec_MK_word(cw, Ainv, A, ph, prev, skip='adv', prefer='N'):
    """deterministic decode of one word; returns plaintext; ambiguity resolved by `prefer`."""
    K = A.shape[0]; t = ph; out = np.empty(len(cw), dtype=np.int64)
    for j, c in enumerate(cw):
        pN = Ainv[t % K][c]; okN = (skip == 'none') or (c != prev)
        if skip == 'none':
            out[j] = pN; prev = c; t += 1; continue
        t2 = t + 1; pD = Ainv[t2 % K][c]; okD = (A[t % K][pD] == prev)
        if okN and (not okD or prefer == 'N'):
            out[j] = pN
        else:
            out[j] = pD
            if skip == 'adv': t += 1
        prev = c; t += 1
    return out

def rand_perm(rng): return rng.permutation(29).astype(np.int64)

def rand_order5(rng, nfix=4):
    """order-5 permutation of 29 points with nfix fixed points and (29-nfix)/5 five-cycles."""
    pts = rng.permutation(29); g = np.arange(29)
    cyc = pts[nfix:]
    for k in range(0, len(cyc), 5):
        c = cyc[k:k+5]
        for i in range(5): g[c[i]] = c[(i + 1) % 5]
    return g.astype(np.int64)

# ---------------- Oosterhof walk (exact, experiments/doublet_dodge_walk.py) ----------------
def compose(a, b): return a[b]          # (a o b)[x] = a[b[x]]
def ppow(g, k):
    r = np.arange(29)
    for _ in range(k): r = g[r]
    return r

def enc_walk(words, base0, g, sigma):
    gp = [ppow(g, k) for k in range(5)]; base = base0.copy(); out = []; clock = 0; prev = -1
    for w in words:
        cw = np.empty(len(w), dtype=np.int64)
        for j, p in enumerate(w):
            c = base[gp[clock % 5][p]]
            if c == prev:
                clock += 1; c = base[gp[clock % 5][p]]
            cw[j] = c; prev = c; clock += 1
        out.append(cw)
        base = compose(base, compose(gp[(clock - 1) % 5], sigma))
    return out

# ---------------- statistics ----------------
def ioc(x):
    n = np.bincount(np.asarray(x), minlength=29).astype(float); N = n.sum()
    return 29 * (n * (n - 1)).sum() / (N * (N - 1))

def census(cwords, minlen=2):
    """number of word tokens (len>=minlen) whose exact cipher word occurred earlier; and identical pairs."""
    from collections import Counter
    cnt = Counter(tuple(w) for w in cwords if len(w) >= minlen)
    rep = sum(v - 1 for v in cnt.values()); pairs = sum(v * (v - 1) // 2 for v in cnt.values())
    return rep, pairs

def lag_profile(cwords, maxlag=6):
    C = np.concatenate(cwords); wid = np.repeat(np.arange(len(cwords)), [len(w) for w in cwords])
    cnt = core.lag_counts(C, wid, maxlag)
    return cnt[0] / np.maximum(cnt[1], 1), cnt[2] / np.maximum(cnt[3], 1)
