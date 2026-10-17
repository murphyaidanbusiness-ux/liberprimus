"""Write a planted M_K instance (or the real LP / a shuffled LP) for mk_sa.
usage: gen_inst.py out K skip(0/1/2) tied(0/1) seed ptype(P1 lenmatched | P2 solved+contig | REAL | SHUF<seed>)"""
import sys, re, kcore as k, numpy as np
out, K, skip, tied, seed, ptype = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
SK = {0: 'none', 1: 'adv', 2: 'redraw'}[skip]
C, wid, ch = k.lp_main()
sec = None
m = re.search(r'sec(\d+)', ptype)
if m:
    sec = int(m.group(1)); msk = ch == sec; C = C[msk]; wid = wid[msk]; ptype = ptype.replace(m.group(0), '').rstrip('_')
W = k.words_of(C, wid); lens = [len(w) for w in W]
rng = np.random.default_rng(seed)
tr, ho = k.wp_split()
if ptype in ('P1', 'P2'):
    if ptype == 'P1': P = k.plain_lenmatched(ho, lens, seed)
    else:
        P = k.solved_words(); n = sum(len(w) for w in P); P = P + k.plain_contig(ho, n=12956 - n, seed=seed)
        if sec is not None: P = P[:len(lens)]
    if tied:
        base = k.rand_perm(rng); g = k.rand_order5(rng, 4)
        A = np.array([base[k.ppow(g, j)] for j in range(K)])
    else:
        A = np.array([k.rand_perm(rng) for _ in range(K)])
    ph = rng.integers(0, K, len(P))
    Cw = k.enc_MK(P, A, ph, SK)
    plain = np.concatenate(P)
else:
    if ptype in ('REAL', 'P'): Cw = W
    else:
        r2 = np.random.default_rng(int(ptype[4:])); perm = r2.permutation(len(C)); C2 = C[perm].copy()
        # repair: break adjacent duplicates by random swaps until the doublet count equals the real one
        target = int((np.diff(C) == 0).sum())
        for _ in range(200000):
            d = np.nonzero(np.diff(C2) == 0)[0]
            if len(d) <= target: break
            i = d[r2.integers(len(d))] + 1; j = r2.integers(len(C2))
            C2[i], C2[j] = C2[j], C2[i]
        Cw = k.words_of(C2, wid)   # same word lengths, runes shuffled globally (doublet rate NOT preserved)
    plain = -np.ones(len(C), dtype=np.int64); ph = np.zeros(len(Cw), dtype=np.int64)
    A = np.array([np.arange(29)] * K); base = np.arange(29); g = np.arange(29)
with open(out, 'w') as f:
    f.write('%d\n' % len(Cw)); f.write(' '.join(str(len(w)) for w in Cw) + '\n')
    f.write(' '.join(map(str, np.concatenate(Cw))) + '\n'); f.write(' '.join(map(str, plain)) + '\n')
    f.write(' '.join(map(str, ph)) + '\n')
    if tied == 1: f.write(' '.join(map(str, base)) + '\n' + ' '.join(map(str, g)) + '\n')
    else:
        for a in A: f.write(' '.join(map(str, a)) + '\n')
Call = np.concatenate(Cw)
print('inst %s n=%d words=%d doublets=%.4f ioc=%.4f' % (out, len(Call), len(Cw), np.mean(np.diff(Call) == 0), k.ioc(Call)))
