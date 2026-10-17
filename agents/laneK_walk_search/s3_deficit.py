"""Sequential-search bit budget for Oosterhof's walk on planted instances.
Process words in order; a beam/tree search must commit to every key value a word's decryption touches.
unknown bits = sum log2(remaining choices) for each newly needed value of tau=sigma^-1 (and base0^-1, g);
evidence bits = per decrypted symbol (runes + word end) the LM's mean log-likelihood ratio English vs
random under the true key, measured on the plant itself (bits). The beam must hold ~2^(max deficit)."""
import numpy as np, kcore as k, math
L = np.fromfile(k.OUT + '/lm4.bin', dtype=np.float32).reshape(30, 30, 30, 30)
uni = math.log(29)  # random-rune model cost per symbol (nats), boundary treated alike
def run(fn, base_unknown, g_bits):
    t = open(fn).read().split('\n'); nw = int(t[0]); lens = list(map(int, t[1].split()))
    c = np.array(t[2].split(), int); p = np.array(t[3].split(), int); kj = np.array(t[4].split(), int)
    ew = np.array(t[5].split(), int); base0 = np.array(t[6].split(), int); g = np.array(t[7].split(), int); sig = np.array(t[8].split(), int)
    b0i = np.argsort(base0); gp = [k.ppow(g, j) for j in range(5)]; gpi = [np.argsort(x) for x in gp]; tau = np.argsort(sig)
    known_tau = set(); known_b = set(); unk = g_bits; ev = 0.0; maxdef = g_bits; at = 0; st = 0; trace = []
    for w in range(nw):
        a = b = cc = 29
        for j in range(lens[w]):
            i = st + j; y = c[i]
            if base_unknown and y not in known_b:
                unk += math.log2(29 - len(known_b)); known_b.add(y)
            v = b0i[y]
            for e in ew[:w]:
                v = gpi[e][v]
                if v not in known_tau: unk += math.log2(29 - len(known_tau)); known_tau.add(v)
                v = tau[v]
            x = p[i]; ev += (L[a, b, cc, x] + uni) / math.log(2); a, b, cc = b, cc, x
        ev += (L[a, b, cc, 29] + uni) / math.log(2)
        st += lens[w]; d = unk - ev
        if d > maxdef: maxdef = d; at = w
        trace.append((w, len(known_tau), unk, ev))
        if len(known_tau) == 29 and (not base_unknown or len(known_b) == 29) and ev > unk + 50: break
    return maxdef, at, trace
for s in [1, 2, 3]:
    fn = 'inst/walk_%d.txt' % s
    for name, bu, gb in [('oracle: g, base0, clock known', 0, 0), ('base0 unknown, g known', 1, 0),
                         ('base0 unknown, structured g (14.5 b)', 1, 14.5), ('base0 unknown, free order-5 g (79.7 b)', 1, 79.7)]:
        md, at, tr = run(fn, bu, gb)
        print('plant %d  %-42s max deficit %6.1f bits at word %3d  (tau fully needed by word %d)' % (
            s, name, md, at, next(w for w, n, u, e in tr if n == 29) if any(n == 29 for _, n, _, _ in tr) else -1))
