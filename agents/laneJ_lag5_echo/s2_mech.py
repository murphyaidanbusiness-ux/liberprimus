"""Task 3: simulate candidate mechanisms on English runic plaintext with the LP word-length sequence,
compare within/across lag profiles 1..10 to the real ciphertext."""
import numpy as np, core, sys
EA = 28
C0, wid0, chap0, page0 = core.lp_main()
pos0, wl0, starts0, lens0 = core.word_meta(wid0)
WORDS = core.load_wp_words(400000)
BYL = core.by_length(WORDS)
K = 10
REAL = core.lag_counts(C0, wid0, K)
R = int(sys.argv[1]) if len(sys.argv) > 1 else 20

# ---------- building blocks ----------
def chain_from_k(P, k, rng):
    """c_i = c_{i-1} + s_i, s_i = 0 if p=EA else 1 + ((p + k_i) mod 28)"""
    s = np.where(P == EA, 0, 1 + ((P + k) % 28))
    c = (rng.integers(29) + np.cumsum(s)) % 29
    return c

def vig(P, k): return (P + k) % 29

def per_word_5key(wid, pos, rng, mod):
    W = wid.max() + 1
    G = rng.integers(mod, size=(W, 5)); ph = rng.integers(5, size=W)
    return G[wid, (pos + ph[wid]) % 5]

def rand_perm_order5(rng, nfix=4):
    """random permutation of 29 points with 5 five-cycles and nfix=4 fixed points"""
    pts = rng.permutation(29); g = np.arange(29)
    for c in range(5):
        cyc = pts[nfix + 5*c: nfix + 5*c + 5]
        for j in range(5): g[cyc[j]] = cyc[(j+1) % 5]
    return g

# ---------- mechanisms: enc(P, wid, pos, wl, rng) -> C ----------
def m_plain(P, wid, pos, wl, rng): return P.copy()
def m_vig_flat(P, wid, pos, wl, rng): return vig(P, rng.integers(29, size=len(P)))
def m_chain(P, wid, pos, wl, rng): return chain_from_k(P, rng.integers(28, size=len(P)), rng)
def m_a1_chain_wordconst_len(P, wid, pos, wl, rng):
    H = rng.integers(28, size=40); return chain_from_k(P, H[wl], rng)
def m_a2_chain_len_pos(P, wid, pos, wl, rng):
    H = rng.integers(28, size=(40, 40)); return chain_from_k(P, H[wl, pos], rng)
def m_a3_vig_restart_kw(P, wid, pos, wl, rng):
    KW = rng.integers(29, size=40); return vig(P, KW[pos])
def m_a4_vig_period_eq_len(P, wid, pos, wl, rng):
    # running key whose period equals the CURRENT word's length (key index = global i mod L_w)
    KW = rng.integers(29, size=40); i = np.arange(len(P)); return vig(P, KW[i % wl])
def m_a5_chain_period_eq_len(P, wid, pos, wl, rng):
    KW = rng.integers(28, size=40); i = np.arange(len(P)); return chain_from_k(P, KW[i % wl], rng)
def m_b_chain_restart_r2(P, wid, pos, wl, rng):
    k = rng.integers(28, size=len(P)); s = np.where(P == EA, 0, 1 + ((P + k) % 28))
    A = rng.integers(29); c = np.zeros(len(P), np.int64); prev = rng.integers(29)
    for i in range(len(P)):
        prev = (A + s[i]) % 29 if pos[i] == 2 else (prev + s[i]) % 29
        c[i] = prev
    return c
def m_c_vig_5key(P, wid, pos, wl, rng): return vig(P, per_word_5key(wid, pos, rng, 29))
def m_c_chain_5key(P, wid, pos, wl, rng): return chain_from_k(P, per_word_5key(wid, pos, rng, 28), rng)
def m_c_mixed_5alph(P, wid, pos, wl, rng):
    """per word: 5 independent random alphabets, cycled with random phase (no relation between them)"""
    W = wid.max() + 1; out = np.zeros(len(P), np.int64)
    ph = rng.integers(5, size=W)
    st = np.r_[0, np.nonzero(np.diff(wid))[0] + 1, len(P)]
    for w in range(W):
        A = np.array([rng.permutation(29) for _ in range(5)])
        for i in range(st[w], st[w+1]):
            out[i] = A[(pos[i] + ph[w]) % 5, P[i]]
    return out
def _walk(P, wid, pos, rng, dodge, g=None):
    """community walk: c = base_w(g^clock(p)); base_w random per word; clock continues; dodge = skip on repeat"""
    g = rand_perm_order5(rng) if g is None else g
    gp = [np.arange(29)]
    for j in range(1, 5): gp.append(g[gp[-1]])
    W = wid.max() + 1; out = np.zeros(len(P), np.int64)
    st = np.r_[0, np.nonzero(np.diff(wid))[0] + 1, len(P)]
    clock = rng.integers(5); prev = -1
    for w in range(W):
        base = rng.permutation(29)
        for i in range(st[w], st[w+1]):
            c = base[gp[clock % 5][P[i]]]
            if dodge and c == prev:
                clock += 1; c = base[gp[clock % 5][P[i]]]
            out[i] = c; prev = c; clock += 1
    return out
def m_walk_nododge(P, wid, pos, wl, rng): return _walk(P, wid, pos, rng, False)
def m_walk_dodge(P, wid, pos, wl, rng): return _walk(P, wid, pos, rng, True)
def m_d_wordcolumnar5_chain(P, wid, pos, wl, rng):
    out = P.copy(); st = np.r_[0, np.nonzero(np.diff(wid))[0] + 1, len(P)]
    for w in range(len(st) - 1):
        seg = P[st[w]:st[w+1]]; L = len(seg)
        order = np.concatenate([np.arange(c, L, 5) for c in range(min(5, L))])
        out[st[w]:st[w+1]] = seg[order]
    return chain_from_k(out, rng.integers(28, size=len(P)), rng)
def m_d_wordcolumnar5_mixed5(P, wid, pos, wl, rng):
    out = P.copy(); st = np.r_[0, np.nonzero(np.diff(wid))[0] + 1, len(P)]
    for w in range(len(st) - 1):
        seg = P[st[w]:st[w+1]]; L = len(seg)
        order = np.concatenate([np.arange(c, L, 5) for c in range(min(5, L))])
        out[st[w]:st[w+1]] = seg[order]
    return m_c_mixed_5alph(out, wid, pos, wl, rng)
def m_e_route5_chain(P, wid, pos, wl, rng):
    out = []; B = 500
    for b0 in range(0, len(P), B):
        blk = P[b0:b0+B]; out.append(np.concatenate([blk[c::5] for c in range(5)]))
    return chain_from_k(np.concatenate(out), rng.integers(28, size=len(P)), rng)
def m_e_route5_vig5key(P, wid, pos, wl, rng):
    out = []; B = 500
    for b0 in range(0, len(P), B):
        blk = P[b0:b0+B]; out.append(np.concatenate([blk[c::5] for c in range(5)]))
    return vig(np.concatenate(out), per_word_5key(wid, pos, rng, 29))
def m_f_lagfib_vig(P, wid, pos, wl, rng):
    k = np.zeros(len(P), np.int64); k[:5] = rng.integers(29, size=5)
    for i in range(5, len(P)): k[i] = (k[i-1] + k[i-5]) % 29
    return vig(P, k)
def m_f_lagfib_chain(P, wid, pos, wl, rng):
    k = np.zeros(len(P), np.int64); k[:5] = rng.integers(28, size=5)
    for i in range(5, len(P)): k[i] = (k[i-1] + k[i-5]) % 28
    return chain_from_k(P, k, rng)
def m_f_tap5_sparse_vig(P, wid, pos, wl, rng):
    k = np.zeros(len(P), np.int64); k[:5] = rng.integers(29, size=5)
    t = np.where(rng.random(len(P)) < 0.6, rng.integers(1, 29, size=len(P)), 0)
    for i in range(5, len(P)): k[i] = (k[i-5] + t[i]) % 29
    return vig(P, k)
def m_g_skip_vig_5key(P, wid, pos, wl, rng):
    W = wid.max() + 1; G = rng.integers(29, size=(W, 5)); ph = rng.integers(5, size=W)
    out = np.zeros(len(P), np.int64); st = np.r_[0, np.nonzero(np.diff(wid))[0] + 1, len(P)]; prev = -1
    for w in range(W):
        clk = ph[w]
        for i in range(st[w], st[w+1]):
            c = (P[i] + G[w, clk % 5]) % 29
            while c == prev: clk += 1; c = (P[i] + G[w, clk % 5]) % 29
            out[i] = c; prev = c; clk += 1
    return out
def m_g_skip_vig_flat(P, wid, pos, wl, rng):
    k = rng.integers(29, size=len(P) * 2); out = np.zeros(len(P), np.int64); j = 0; prev = -1
    for i in range(len(P)):
        c = (P[i] + k[j]) % 29
        while c == prev: j += 1; c = (P[i] + k[j]) % 29
        out[i] = c; prev = c; j += 1
    return out

MECH = [
    ('plain (no cipher)', m_plain),
    ('ref: Vigenere flat random key', m_vig_flat),
    ('ref: chain c=c_prev+s, flat k', m_chain),
    ('ref: flat key + skip-on-repeat', m_g_skip_vig_flat),
    ('a1 chain, k const per word = H(len)', m_a1_chain_wordconst_len),
    ('a2 chain, k = H(len,pos)', m_a2_chain_len_pos),
    ('a3 Vig, keyword restarts each word', m_a3_vig_restart_kw),
    ('a4 Vig, key period = word length (global i)', m_a4_vig_period_eq_len),
    ('a5 chain, key period = word length', m_a5_chain_period_eq_len),
    ('b  chain restarts at offset 2 in word', m_b_chain_restart_r2),
    ('c  Vig, per-word 5-key, random phase', m_c_vig_5key),
    ('c  chain, per-word 5-key, random phase', m_c_chain_5key),
    ('c  5 random alphabets/word, random phase', m_c_mixed_5alph),
    ('c  walk base_w.g^clock (order-5 g), no dodge', m_walk_nododge),
    ('c  walk + doublet-dodge (Oosterhof)', m_walk_dodge),
    ('d  in-word 5-col transposition + chain', m_d_wordcolumnar5_chain),
    ('d  in-word 5-col transp. + 5-alph/word', m_d_wordcolumnar5_mixed5),
    ('e  5-col route transp. (500 blk) + chain', m_e_route5_chain),
    ('e  5-col route transp. + per-word 5-key Vig', m_e_route5_vig5key),
    ('f  lagged-Fib k=k-1+k-5, Vig', m_f_lagfib_vig),
    ('f  lagged-Fib k=k-1+k-5, chain', m_f_lagfib_chain),
    ('f  k=k-5+t (t sparse 60%), Vig', m_f_tap5_sparse_vig),
    ('g  skip-on-repeat Vig, 5-key/word, rand phase', m_g_skip_vig_5key),
]

def coset_ioc_z(C, pos, L=5):
    """sum over position-mod-L cosets of chi2 vs global frequency; returns z of chi2 vs its df"""
    f = np.bincount(C, minlength=29) / len(C); chi = 0; df = 0
    for r in range(L):
        x = C[(pos % L) == r]; n = len(x)
        o = np.bincount(x, minlength=29); e = f * n; chi += ((o - e)**2 / np.maximum(e, 1e-9)).sum(); df += 28
    df = (L - 1) * 28
    return (chi - df) / np.sqrt(2 * df)

# plaintext lag-5 within-word difference distribution Q (for delta test)
def delta5_hist(C, wid):
    same = wid[:-5] == wid[5:]; d = (C[5:] - C[:-5])[same] % 29
    return np.bincount(d, minlength=29)
rng = np.random.default_rng(7)
Qc = np.zeros(29)
for _ in range(10):
    P, w = core.matched_plain(lens0, BYL, rng); Qc += delta5_hist(P, w)
Q = Qc[1:] / Qc[1:].sum(); Qd = Q - Q.mean(); Qd /= np.linalg.norm(Qd)
def delta_T(C, wid):
    h = delta5_hist(C, wid)[1:].astype(float); n = h.sum(); e = n / 28
    return float(((h - e) / np.sqrt(e)) @ Qd)   # ~N(0,1) under flat nonzero bins

def profile_rates(cnt):
    return (cnt[0] + 0.5) / (cnt[1] + 1), (cnt[2] + 0.5) / (cnt[3] + 1)

def run_stat(C, wid):
    """within-word lag-5: P(match at (i,i+5) | match at (i-1,i+4)), both pairs inside one word"""
    N = len(C); i = np.arange(1, N - 5)
    ok = (wid[i-1] == wid[i+5])
    prev = (C[i-1] == C[i+4]) & ok; cur = (C[i] == C[i+5]) & ok
    return cur[prev].sum(), prev.sum()

def dlag5(C, wid):
    D = (C[1:] - C[:-1]) % 29; w = wid[1:]; inw = wid[1:] == wid[:-1]
    a = np.arange(len(D) - 5); m = inw[a] & inw[a+5] & (w[a] == w[a+5])
    return (D[a][m] == D[a+5][m]).sum(), m.sum()

if __name__ == '__main__':
    rw, rx = profile_rates(REAL)
    print('REAL within :', ' '.join('%.4f' % v for v in rw))
    print('REAL across :', ' '.join('%.4f' % v for v in rx))
    a, b = run_stat(C0, wid0); c_, d_ = dlag5(C0, wid0)
    print('REAL coset(pos mod 5) z=%.2f  deltaT=%.2f  run %d/%d=%.3f  Dlag5-within %d/%d=%.4f' % (coset_ioc_z(C0, pos0), delta_T(C0, wid0), a, b, a/b, c_, d_, c_/d_))
    rows = []
    for name, fn in MECH:
        acc = np.zeros((4, K)); cz = []; dT = []; rs = np.zeros(2); dl = np.zeros(2)
        for r in range(R):
            P, w = core.matched_plain(lens0, BYL, rng)
            p, wlen_ = core.word_meta(w)[0], core.word_meta(w)[1]
            Cs = fn(P, w, p, wlen_, rng)
            acc += core.lag_counts(Cs, w, K); cz.append(coset_ioc_z(Cs, p)); dT.append(delta_T(Cs, w))
            rs += run_stat(Cs, w); dl += dlag5(Cs, w)
        sw, sx = profile_rates(acc)
        # fit: real counts vs sim rates over within 1..8 and across 1..8
        zW = (REAL[0, :8] - sw[:8] * REAL[1, :8]) / np.sqrt(np.maximum(REAL[1, :8] * sw[:8] * (1 - sw[:8]), 1e-9))
        zX = (REAL[2, :8] - sx[:8] * REAL[3, :8]) / np.sqrt(np.maximum(REAL[3, :8] * sx[:8] * (1 - sx[:8]), 1e-9))
        chi = float((zW**2).sum() + (zX**2).sum())
        rows.append((name, sw, sx, np.mean(cz), np.mean(dT), np.std(dT), chi, zW, zX, rs[0]/max(rs[1],1), dl[0]/max(dl[1],1)))
        print('%-46s W:' % name, ' '.join('%.4f' % v for v in sw), '| X1-6:', ' '.join('%.4f' % v for v in sx[:6]),
              '| coset z %.1f | dT %.2f+-%.2f | run %.3f | Dl5 %.4f | chi16 %.0f' % (np.mean(cz), np.mean(dT), np.std(dT), rs[0]/max(rs[1],1), dl[0]/max(dl[1],1), chi), flush=True)
    import pickle; pickle.dump(rows, open(core.OUT + '/s2_rows.pkl', 'wb'))
