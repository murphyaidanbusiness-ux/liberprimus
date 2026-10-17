"""Task 3/4 follow-ups: plaintext reference by word length, partial-leak calibration of the delta test,
and the dictionary attack on a per-word additive 5-key (Vigenere and chain/D-domain variants)."""
import numpy as np, core
from collections import Counter, defaultdict
from s2_mech import delta_T, lens0, BYL, WORDS, C0, wid0, chain_from_k, EA
rng = np.random.default_rng(99)
pos0, wl0, starts0, _ = core.word_meta(wid0)

print('== 1. plaintext within-word lag-5 / lag-10 coincidence by word length (War&Peace runes, token-weighted) ==')
ref5 = {}; ref10 = {}
cnt = defaultdict(lambda: np.zeros(4))
for w in WORDS:
    L = len(w); a = np.array(w)
    if L > 5: cnt[L][0] += (a[:-5] == a[5:]).sum(); cnt[L][1] += L - 5
    if L > 10: cnt[L][2] += (a[:-10] == a[10:]).sum(); cnt[L][3] += L - 10
sol = core.solved_words(); cs = defaultdict(lambda: np.zeros(2))
for w in sol:
    a = np.array(w); L = len(a)
    if L > 5: cs[min(L, 10)][0] += (a[:-5] == a[5:]).sum(); cs[min(L, 10)][1] += L - 5
for L in range(6, 15):
    m, n = 0, 0
    msk = (wl0 == L) if L < 14 else (wl0 >= 14)
    i = np.arange(len(C0) - 5); ok = (wid0[i] == wid0[i+5]) & msk[i]
    m = (C0[i][ok] == C0[i+5][ok]).sum(); n = ok.sum()
    pr = cnt[L][0] / cnt[L][1]; ref5[L] = pr
    phi = (m/n - 1/29) / (pr - 1/29) if n else np.nan
    print('  L=%2d  W&P lag5 %.4f (n=%7d)  solved-LP %s | LP %3d/%4d = %.4f  implied phi=%.2f' % (
        L, pr, cnt[L][1], ('%.4f' % (cs[L][0]/cs[L][1])) if L <= 10 and cs[L][1] else '  -  ', m, n, m/n, phi))
# expected LP total under full leak, using LP's own length mix
i = np.arange(len(C0) - 5); ok = wid0[i] == wid0[i+5]
exp_full = sum(ref5.get(min(wl0[j], 14), ref5[14]) for j in i[ok])
print('  full-leak expectation for the LP length mix: %.1f matches of %d (observed 104) -> phi_total = %.2f' % (
    exp_full, ok.sum(), (104 - ok.sum()/29) / (exp_full - ok.sum()/29)))
m10 = sum(cnt[L][2] for L in cnt); n10 = sum(cnt[L][3] for L in cnt)
print('  plaintext lag-10 (words >= 11): %.4f; LP: 2/92; predicted under phi=0.6 echo: %.1f matches of 92 (flat 3.2)' % (
    m10/n10, 92*(1/29 + 0.6*(m10/n10 - 1/29))))

print('\n== 2. delta-histogram test (equality-only vs additive leak), partial-leak calibration ==')
def vig5_partial(P, wid, pos, q, skip=False):
    W = wid.max() + 1; G = rng.integers(29, size=(W, 5)); ph = rng.integers(5, size=W)
    per = rng.random(W) < q
    k = np.where(per[wid], G[wid, (pos + ph[wid]) % 5], rng.integers(29, size=len(P)))
    if not skip: return (P + k) % 29
    out = np.zeros(len(P), np.int64); prev = -1; st = np.r_[0, np.nonzero(np.diff(wid))[0] + 1, len(P)]
    for w in range(W):
        clk = ph[w]
        for i in range(st[w], st[w+1]):
            kk = G[w, clk % 5] if per[w] else rng.integers(29)
            c = (P[i] + kk) % 29
            while c == prev:
                clk += 1; kk = G[w, clk % 5] if per[w] else rng.integers(29); c = (P[i] + kk) % 29
            out[i] = c; prev = c; clk += 1
    return out
print('  REAL deltaT = %.2f (N(0,1) under flat nonzero bins)' % delta_T(C0, wid0))
for q in [1.0, 0.7, 0.6, 0.5]:
    for skip in [False, True]:
        T = []; r5 = []
        for _ in range(40):
            P, w = core.matched_plain(lens0, BYL, rng); p = core.word_meta(w)[0]
            Cs = vig5_partial(P, w, p, q, skip); T.append(delta_T(Cs, w))
            c = core.lag_counts(Cs, w, 5); r5.append(c[0, 4] / c[1, 4])
        T = np.array(T)
        print('  additive per-word 5-key q=%.1f skip=%s: W5=%.4f  deltaT=%.2f+-%.2f  P(T<=real)=%.3f' % (
            q, skip, np.mean(r5), T.mean(), T.std(), (T <= delta_T(C0, wid0)).mean()))

print('\n== 3. dictionary attack: per-word additive 5-key (lag-5 differences are key-free) ==')
def load_dict(L):
    ws = set()
    try:
        for line in open(core.S + '/dl/transcr/LiberPrayground/data/dictionary_%d.txt' % L, encoding='utf-8'):
            w = tuple(core.R2I[c] for c in line.strip() if c in core.R2I)
            if len(w) == L: ws.add(w)
    except FileNotFoundError: pass
    for w in BYL.get(L, []): ws.add(tuple(w))
    for w in sol:
        if len(w) == L: ws.add(tuple(w))
    return ws
DICT = {L: load_dict(L) for L in range(6, 15)}
WPF = Counter(tuple(w) for w in WORDS)
def sig_vig(a): a = np.asarray(a); return tuple(((a[5:] - a[:-5]) % 29).tolist())
def sig_D(a):
    a = np.asarray(a); D = (a[1:] - a[:-1]) % 29; x = np.where(D == 0, -1, D - 1)
    if (x[5:] < 0).any() or (x[:-5] < 0).any(): return None
    return tuple(((x[5:] - x[:-5]) % 28).tolist())
def sig_Dplain(a):
    a = np.asarray(a); x = np.where(a == EA, -1, a)[1:]
    if (x < 0).any(): return None
    return tuple(((x[5:] - x[:-5]) % 28).tolist())
TAB = {}; TABD = {}
for L, ws in DICT.items():
    t = defaultdict(list); td = defaultdict(list)
    for w in ws:
        t[sig_vig(w)].append(w)
        s = sig_Dplain(w)
        if s is not None: td[s].append(w)
    TAB[L] = t; TABD[L] = td
    print('  dict L=%d: %d words, %d distinct Vig signatures (space 29^%d)' % (L, len(ws), len(t), L - 5))
LPW = [C0[wid0 == k] for k in range(wid0.max() + 1)]
def attack(words, Lmin, mode):
    hits = defaultdict(int); tot = defaultdict(int); wf = 0.0; found = []
    for a in words:
        L = len(a)
        if L < Lmin or L > 14: continue
        tot[L] += 1
        s = sig_vig(a) if mode == 'vig' else sig_D(a)
        if s is None: continue
        cand = (TAB if mode == 'vig' else TABD)[L].get(s, [])
        if cand:
            hits[L] += 1; best = max(cand, key=lambda w: WPF.get(w, 0)); wf += np.log1p(WPF.get(best, 0))
            found.append((a, best))
    return hits, tot, wf, found
def report(tag, words, Lmin, mode, nnull=100):
    h, t, wf, found = attack(words, Lmin, mode)
    nh = []; nwf = []
    for _ in range(nnull):
        sh = [rng.permutation(a) for a in words]
        h2, _, wf2, _ = attack(sh, Lmin, mode); nh.append(sum(h2.values())); nwf.append(wf2)
    nh = np.array(nh); nwf = np.array(nwf)
    H = sum(h.values()); T = sum(t.values())
    print('  %-34s words(L>=%d)=%d hits=%d  null %.1f+-%.1f (max %d) z=%+.2f | freq-score %.1f null %.1f+-%.1f z=%+.2f' % (
        tag, Lmin, T, H, nh.mean(), nh.std(), nh.max(), (H - nh.mean())/max(nh.std(), 1e-9), wf, nwf.mean(), nwf.std(), (wf - nwf.mean())/max(nwf.std(), 1e-9)))
    return found
for mode, Lmin in [('vig', 9), ('vig', 10), ('D', 10)]:
    print(' mode=%s Lmin=%d' % (mode, Lmin))
    found = report('REAL LP', LPW, Lmin, mode)
    # planted controls: LP word lengths filled with English, encrypted by the hypothesised mechanism
    for q in [1.0, 0.6]:
        P, w = core.matched_plain(lens0, BYL, rng); p = core.word_meta(w)[0]
        if mode == 'vig': Cs = vig5_partial(P, w, p, q)
        else:
            W = w.max() + 1; G = rng.integers(28, size=(W, 5)); ph = rng.integers(5, size=W); per = rng.random(W) < q
            k = np.where(per[w], G[w, (p + ph[w]) % 5], rng.integers(28, size=len(P)))
            Cs = chain_from_k(P, k, rng)
        PW = [Cs[w == k] for k in range(w.max() + 1)]
        report('PLANTED q=%.1f' % q, PW, Lmin, mode, nnull=30)
    if mode == 'vig' and Lmin == 10:
        print('  real hits (cipher word -> best dictionary candidate):')
        for a, b in found[:15]:
            print('    %-40s -> %s' % ('.'.join(core.TR[x] for x in a), ''.join(core.TR[x] for x in b)))
