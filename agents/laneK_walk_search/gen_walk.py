"""Planted Oosterhof walk instance (exact doublet_dodge_walk.encipher) with the true clock exported.
usage: gen_walk.py out seed"""
import sys, kcore as k, numpy as np
out, seed = sys.argv[1], int(sys.argv[2])
C, wid, ch = k.lp_main(); W = k.words_of(C, wid); lens = [len(w) for w in W]
tr, ho = k.wp_split(); rng = np.random.default_rng(seed)
P = k.plain_lenmatched(ho, lens, seed)
base0 = k.rand_perm(rng); g = k.rand_order5(rng, 4); sigma = k.rand_perm(rng)
gp = [k.ppow(g, j) for j in range(5)]; base = base0.copy(); clock = 0; prev = -1; Cw = []; kj = []; ew = []
for w in P:
    cw = []
    for p in w:
        c = base[gp[clock % 5][p]]
        if c == prev: clock += 1; c = base[gp[clock % 5][p]]
        cw.append(c); kj.append(clock % 5); prev = c; clock += 1
    Cw.append(cw); e = (clock - 1) % 5; ew.append(e)
    base = base[gp[e][sigma]]
ref = k.enc_walk(P, base0, g, sigma); assert all(list(a) == list(b) for a, b in zip(ref, Cw))
with open(out, 'w') as f:
    f.write('%d\n' % len(Cw)); f.write(' '.join(str(len(w)) for w in Cw) + '\n')
    for arr in (np.concatenate([np.array(c) for c in Cw]), np.concatenate(P), kj, ew, base0, g, sigma):
        f.write(' '.join(map(str, arr)) + '\n')
Ca = np.concatenate([np.array(c) for c in Cw])
print('walk inst %s doublets %.4f ioc %.4f repeats(len>=3) %d' % (out, np.mean(np.diff(Ca) == 0), k.ioc(Ca), k.census(Cw, 3)[0]))
