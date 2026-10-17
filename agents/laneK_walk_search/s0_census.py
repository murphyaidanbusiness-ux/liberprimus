"""s0: can the brief's M_K model (K fixed alphabets, free per-word phase, skip) produce the LP's
unigram IoC and identical-cipher-word census?  Also round-trip test of enc/dec, and Oosterhof walk contrast."""
import kcore as k, numpy as np
C, wid, ch = k.lp_main(); W = k.words_of(C, wid); lens = [len(w) for w in W]
tr, ho = k.wp_split()
print('LP: ioc %.4f  census(len>=2) %s  census(len>=3) %s' % (k.ioc(C), k.census(W), k.census(W, 3)))
rng = np.random.default_rng(1)
# round trip
P = k.plain_lenmatched(ho, lens, 5); A = np.array([k.rand_perm(rng) for _ in range(5)]); Ainv = np.argsort(A, axis=1)
ph = rng.integers(0, 5, len(P))
for skip in ['none', 'adv', 'redraw']:
    Cw = k.enc_MK(P, A, ph, skip)
    prev = -1; ok = 0; tot = 0
    for pw, cw, f in zip(P, Cw, ph):
        d = k.dec_MK_word(cw, Ainv, A, f, prev, skip, 'N'); prev = cw[-1]; ok += (d == pw).sum(); tot += len(pw)
    prev = -1; okD = 0
    for pw, cw, f in zip(P, Cw, ph):
        d = k.dec_MK_word(cw, Ainv, A, f, prev, skip, 'D'); prev = cw[-1]; okD += (d == pw).sum()
    print('roundtrip skip=%-6s preferN %.4f preferD %.4f  doublets %.4f' % (skip, ok / tot, okD / tot,
          np.mean(np.diff(np.concatenate(Cw)) == 0)))
rows = []
for K in [4, 5, 6, 7]:
    for src in ['lenmatched', 'contig']:
        io, c2, c3 = [], [], []
        for r in range(20):
            P = k.plain_lenmatched(ho, lens, 100 + r) if src == 'lenmatched' else k.plain_contig(ho, seed=100 + r)
            A = np.array([k.rand_perm(rng) for _ in range(K)]); ph = rng.integers(0, K, len(P))
            Cw = k.enc_MK(P, A, ph, 'adv')
            io.append(k.ioc(np.concatenate(Cw))); c2.append(k.census(Cw)[0]); c3.append(k.census(Cw, 3)[0])
        print('M_K K=%d %-10s ioc %.4f+-%.4f  repeats(len>=2) %.0f+-%.0f  repeats(len>=3) %.0f+-%.0f' % (
            K, src, np.mean(io), np.std(io), np.mean(c2), np.std(c2), np.mean(c3), np.std(c3)))
# plaintext census itself and per-word-fresh alphabets (lower bound of chance repeats)
for src in ['lenmatched', 'contig']:
    c2 = []; c3 = []; cw2 = []; cw3 = []
    for r in range(20):
        P = k.plain_lenmatched(ho, lens, 100 + r) if src == 'lenmatched' else k.plain_contig(ho, seed=100 + r)
        c2.append(k.census(P)[0]); c3.append(k.census(P, 3)[0])
        g = k.rand_order5(rng); s = k.rand_perm(rng); b = k.rand_perm(rng)
        Cw = k.enc_walk(P, b, g, s); cw2.append(k.census(Cw)[0]); cw3.append(k.census(Cw, 3)[0])
    print('plaintext %-10s repeats(len>=2) %.0f  (len>=3) %.0f ;  Oosterhof walk: %.0f / %.0f' % (
        src, np.mean(c2), np.mean(c3), np.mean(cw2), np.mean(cw3)))
# best-case flattening: can K=5 alphabets be chosen to make unigram IoC flat? greedy balance
fr = np.bincount(np.concatenate([np.array(w) for w in ho[:100000]]), minlength=29) / sum(len(w) for w in ho[:100000])
best = 9
for trial in range(200):
    A = np.array([k.rand_perm(rng) for _ in range(5)])
    for it in range(4000):
        a = rng.integers(5); i, j = rng.integers(29, size=2)
        f = np.zeros(29)
        for b in range(5): np.add.at(f, A[b], fr)
        v0 = (f ** 2).sum(); A[a, [i, j]] = A[a, [j, i]]
        f = np.zeros(29)
        for b in range(5): np.add.at(f, A[b], fr)
        if (f ** 2).sum() > v0: A[a, [i, j]] = A[a, [j, i]]
    f = np.zeros(29)
    for b in range(5): np.add.at(f, A[b], fr)
    best = min(best, 29 * (f / 5) @ (f / 5))
    if trial >= 3: break
print('flattest K=5 mixture expected IoC (designed alphabets): %.5f' % best)
