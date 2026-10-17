"""Write cipher texts for kwwalk: real page starts, section starts, page-0 doublet-matched nulls, plants.
usage: mk_texts.py real | nulls | plant NAME SEED [kw_base kw_sigma g_index | --offlist WORD]"""
import sys, os, random, json
import numpy as np
from common import *
os.makedirs(OUT + '/texts', exist_ok=True)
U = lp_pages()
Ameta = open(OUT + '/A_meta.txt').read().split('\n')[:-1]
Gmeta = open(OUT + '/G_meta.txt').read().split('\n')[:-1]
A = np.fromfile(OUT + '/A.bin', dtype=np.uint8).reshape(-1, 29)
G = np.fromfile(OUT + '/G.bin', dtype=np.uint8).reshape(-1, 29)

def page_words(i): return [list(w) for w in words_of_page(U[i])]

def doublet_null(words, seed, target):
    lens = [len(w) for w in words]; C = np.array([x for w in words for x in w])
    r = np.random.default_rng(seed); C2 = C[r.permutation(len(C))].copy()
    for _ in range(200000):
        d = np.nonzero(np.diff(C2) == 0)[0]
        if len(d) == target: break
        if len(d) > target:      # break a doublet
            i = d[r.integers(len(d))] + 1; j = r.integers(len(C2)); C2[i], C2[j] = C2[j], C2[i]
        else:                    # create one (copy-swap keeps the multiset: swap a neighbour-equal rune in)
            i = r.integers(1, len(C2)); cand = np.nonzero(C2 == C2[i - 1])[0]; cand = cand[cand != i - 1]
            if len(cand): j = cand[r.integers(len(cand))]; C2[i], C2[j] = C2[j], C2[i]
    out = []; k = 0
    for L in lens: out.append(list(C2[k:k + L])); k += L
    return out

mode = sys.argv[1]
if mode == 'real':
    for i in range(len(U)):
        write_text(OUT + '/texts/real_page%02d.txt' % i, page_words(i))
    body = [w for i in range(len(U)) for w in page_words(i)]
    write_text(OUT + '/texts/body.txt', body)
    # section starts (chapter changes inside the flat stream, incl. mid-page ones)
    flat_ch = [c for p in U for c in p['chap']]; flat_w = [w for p in U for w in p['word']]
    starts = [0] + [k for k in range(1, len(flat_ch)) if flat_ch[k] != flat_ch[k - 1]]
    allw = [];  cur = []; last = None; wstart = []
    for k, (x, wid) in enumerate(zip([x for p in U for x in p['idx']], flat_w)):
        if wid != last and cur: allw.append(cur); cur = []
        if wid != last: wstart.append(k)
        cur.append(x); last = wid
    allw.append(cur)
    secs = []
    for s in starts:
        wi = wstart.index(s) if s in wstart else None
        if wi is None: continue
        ch = flat_ch[s]; ws = []
        for w2 in range(wi, len(allw)):
            if flat_ch[wstart[w2]] != ch: break
            ws.append(allw[w2])
        write_text(OUT + '/texts/real_sec%02d.txt' % ch, ws); secs.append((ch, s, len(ws[0]), sum(len(w) for w in ws)))
    print('sections (chap, rune offset, first word len, runes):', secs)
elif mode == 'nulls':
    w0 = page_words(0); C = [x for w in w0 for x in w]
    tgt = sum(1 for a, b in zip(C, C[1:]) if a == b)
    for s in range(20):
        nw = doublet_null(w0, 1000 + s, tgt); Cn = [x for w in nw for x in w]
        assert sum(1 for a, b in zip(Cn, Cn[1:]) if a == b) == tgt and sorted(Cn) == sorted(C)
        write_text(OUT + '/texts/null_p0_s%02d.txt' % s, nw)
    print('20 nulls of page 0 written; doublets', tgt)
elif mode == 'plant':
    name, seed = sys.argv[2], int(sys.argv[3]); rng = random.Random(seed)
    lens = [len(w) for w in page_words(0)]
    sw = solved_words(); bl = {}
    for w in sw: bl.setdefault(len(w), []).append(list(w))
    WP = wp_words(); ho = WP[int(0.84 * len(WP)):]
    for w in ho: bl.setdefault(-len(w), []).append(list(w))
    P = [rng.choice(bl[L]) if L in bl else rng.choice(bl[-L]) for L in lens]
    if sys.argv[4] == '--offlist':
        # sigma from a keyword NOT in the enumeration list; base0 and g from the set
        word = sys.argv[5]; sq = dedup(eng_runes(word)); sig = alph_rules(sq)['R1']
        assert tuple(sig) not in set(map(tuple, A)), 'keyword alphabet is in the set'
        bi = rng.randrange(len(A)); gi = rng.randrange(23751); si = -1; b0 = list(A[bi]); g = list(G[gi])
        lab = 'base=%s g=%s sigma=%s:R1 (NOT in set)' % (Ameta[bi], Gmeta[gi], word)
    else:
        bi = Ameta.index(sys.argv[4]); si = Ameta.index(sys.argv[5]); gi = int(sys.argv[6])
        b0 = list(A[bi]); g = list(G[gi]); sig = list(A[si])
        lab = 'base=%s g=%s sigma=%s' % (Ameta[bi], Gmeta[gi], Ameta[si])
    Cw = enc_walk(P, b0, g, sig)
    write_text(OUT + '/texts/%s.txt' % name, Cw)
    Cf = [x for w in Cw for x in w]
    json.dump({'label': lab, 'b': bi, 'g': gi, 's': si, 'plain': [list(map(int, w)) for w in P]}, open(OUT + '/texts/%s.json' % name, 'w'))
    print(name, lab, 'doublets', sum(1 for a, b in zip(Cf, Cf[1:]) if a == b), 'plain:', ' '.join(trs(w) for w in P[:12]))
