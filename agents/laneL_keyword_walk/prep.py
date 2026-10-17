"""Build the enumeration sets (keyword alphabets A, order-5 steps G), the lexicon and the int16 LM.
Writes: A.bin (uint8 NA x 29), A_meta.txt; G.bin (uint8 NG x 29), G_meta.txt; lex.bin; lm16.bin; prep_out.txt"""
import itertools, collections, random, sys
import numpy as np
from common import *

log = open(OUT + '/prep_out.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); log.write(s + '\n'); log.flush()

# ---------- 0. verify the walk implementation round-trips and matches aldegonde + laneK ----------
sys.path.insert(0, S + '/dl/aldegonde_clone/aldegonde/experiments'); sys.path.insert(0, S + '/dl/aldegonde_clone/aldegonde/src')
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location('ddw', S + '/dl/aldegonde_clone/aldegonde/experiments/doublet_dodge_walk.py')
    ddw = importlib.util.module_from_spec(spec); spec.loader.exec_module(ddw); ALD = True
except Exception as e:
    P('aldegonde import failed:', repr(e)); ALD = False
import kcore
rng = random.Random(1)
WP = wp_words()
for trial in range(5):
    b0 = list(range(29)); rng.shuffle(b0); s = list(range(29)); rng.shuffle(s)
    g = structured_g_oosterhof(sorted(rng.sample(range(29), 4)))
    o = rng.randrange(400000); words = [list(w) for w in WP[o:o + 60]]
    c1 = enc_walk(words, b0, g, s)
    c2 = kcore.enc_walk([np.array(w) for w in words], np.array(b0), np.array(g), np.array(s))
    assert all(list(a) == list(b) for a, b in zip(c1, c2))
    if ALD:
        c3 = ddw.encipher(words, b0, g, s); assert all(list(a) == list(b) for a, b in zip(c1, c3))
P('walk encipher identical to laneK kcore.enc_walk%s on 5 random keys x 60 words' % (' and aldegonde doublet_dodge_walk.encipher' if ALD else ''))

# ---------- 1. keywords ----------
cic = cicada_vocab()
cnt = collections.Counter(WP)
cics = set(cic)
g20 = [l.strip() for l in open(OUT + '/dl/20k.txt') if l.strip().isalpha()]
eng = [tuple(eng_runes(w)) for w in g20]; eng = [w for w in eng if w]
kws = list(dict.fromkeys(cic + eng))
P('keywords: cicada %d + google-20k English (first20hours/google-10000-english 20k.txt, transliterated ING->NG, IO->IA, K/Q->C, V->U, Z->S) %d -> %d distinct rune words' % (len(cic), len(eng), len(kws)))
seqs = list(dict.fromkeys(tuple(dedup(list(w))) for w in kws))
P('distinct de-duplicated keyword rune sequences: %d' % len(seqs))
kwsrc = {}
for w in kws:
    kwsrc.setdefault(tuple(dedup(list(w))), w)

# ---------- 2. alphabet set A ----------
A = {}; meta = []
def addA(p, lab):
    t = tuple(p)
    if t not in A: A[t] = len(meta); meta.append(lab)
for q in range(29): addA([(x + q) % 29 for x in range(29)], 'shift%d' % q)
for q in range(29): addA([(q - x) % 29 for x in range(29)], 'refl%d' % q)   # refl28 = atbash
for sq in seqs:
    name = trs(kwsrc[sq])
    for rule, alph in alph_rules(list(sq)).items():
        addA(alph, '%s:%s' % (name, rule)); addA(inv(alph), '%s:%s:inv' % (name, rule))
Aarr = np.array(list(A.keys()), dtype=np.uint8)
assert all(sorted(r) == list(range(29)) for r in Aarr[:1000])
Aarr.tofile(OUT + '/A.bin'); open(OUT + '/A_meta.txt', 'w').write('\n'.join(meta) + '\n')
P('A (keyword alphabets x rules R1,R2,R3,R4,R1rev,R2rev x {perm, inverse} + 29 shifts + 29 reflections): %d distinct permutations' % len(Aarr))

# ---------- 3. g set ----------
G = {}; gmeta = []
def addG(g, lab):
    t = tuple(g)
    assert perm_order(g) == 5, lab
    if t not in G: G[t] = len(gmeta); gmeta.append(lab)
# 3a Oosterhof's exact structured g first (so indices 0..23750 are his family)
for F in itertools.combinations(range(29), 4):
    addG(structured_g_oosterhof(F), 'oost:%s' % ','.join(map(str, F)))
n_oost = len(gmeta)
# 3b structured grids: ordering x fill x fixed-4 x uniform rotation k=1..4
for oname, order in (('gem', list(range(29))), ('eng', ENG_ORDER)):
    for F in itertools.combinations(range(29), 4):
        cells = [x for x in order if x not in F]
        for fill in ('row', 'col', 'bou'):
            grid = grid_fill(cells, fill)
            for k in (1, 2, 3, 4):
                addG(g_from_grid(grid, k), 'grid:%s:%s:%s:k%d' % (oname, fill, ','.join(map(str, F)), k))
n_struct = len(gmeta)
# 3c keyword grids: keyed alphabet (R1 / R2), first 25 in the grid, last 4 fixed
for sq in seqs:
    name = trs(kwsrc[sq]); rr = alph_rules(list(sq))
    for rule in ('R1', 'R2'):
        cells = rr[rule][:25]
        for fill in ('row', 'col', 'bou'):
            grid = grid_fill(cells, fill)
            for k in (1, 2, 3, 4):
                addG(g_from_grid(grid, k), 'kwgrid:%s:%s:%s:k%d' % (name, rule, fill, k))
n_kwgrid = len(gmeta)
# 3d powers of keyed permutations: g = pi^(ord/5) and its powers, for every pi in A with 5 | ord(pi)
npow = 0
for t, i in list(A.items()):
    o = perm_order(list(t))
    if o % 5 == 0:
        npow += 1; h = ppow(list(t), o // 5)
        for k in (1, 2, 3, 4): addG(ppow(h, k), 'pow:%s:k%d' % (meta[i], k))
Garr = np.array(list(G.keys()), dtype=np.uint8)
Garr.tofile(OUT + '/G.bin'); open(OUT + '/G_meta.txt', 'w').write('\n'.join(gmeta) + '\n')
P('G: Oosterhof structured %d; + grid orderings{gem(=prime),eng} x fills{row,col,boustro} x fixed-4 x k=1..4 -> %d; + keyword grids -> %d; + powers of %d keyed perms with 5|ord -> total %d distinct order-5 g'
  % (n_oost, n_struct, n_kwgrid, npow, len(Garr)))
# affine maps cannot have order 5
aff = [(a, b) for a in range(1, 29) for b in range(29) if perm_order([(a * x + b) % 29 for x in range(29)]) == 5]
P('affine maps x->ax+b mod 29 with order 5: %d (orders of a in Z29* divide 28; a=1 gives order 29 or 1)' % len(aff))
fp = collections.Counter(sum(1 for x in range(29) if g[x] == x) for g in Garr)
P('fixed-point census of G:', sorted(fp.items()))

# ---------- 4. lexicon ----------
lex = set(WP[:int(0.84 * len(WP))])           # W&P train part (first 84% of tokens)
n_wp = len(lex)
for line in open(S + '/agents/laneA_keyword_chain/dl/words_alpha.txt'):
    w = line.strip()
    if w.isalpha():
        for ing in (True, False):
            r = tuple(eng_runes(w, ing))
            if 1 <= len(r) <= 16: lex.add(r)
lex |= set(cic)
sw = solved_words(); lex |= set(sw)
lex = {w for w in lex if 1 <= len(w) <= 16}
P('lexicon: W&P train types %d + words_alpha (both ING conventions) + cicada vocab + solved-LP words -> %d types (len 1-16)' % (n_wp, len(lex)))
P('lexicon types by length:', sorted(collections.Counter(len(w) for w in lex).items()))
with open(OUT + '/lex.bin', 'wb') as f:
    arr = np.zeros((len(lex), 17), dtype=np.uint8)
    for i, w in enumerate(sorted(lex)): arr[i, 0] = len(w); arr[i, 1:1 + len(w)] = w
    arr.tofile(f)
# OOV check on held-out W&P tokens and on solved LP tokens
ho = WP[int(0.84 * len(WP)):]
for L in (4, 5, 6, 7, 8, 9, 10, 11):
    t = [w for w in ho if len(w) == L]
    P('  held-out W&P tokens len %2d: %6d, OOV %.4f   | random strings in lexicon: %.2e' % (
        L, len(t), np.mean([w not in lex for w in t]), sum(1 for w in lex if len(w) == L) / 29.0 ** L))

# ---------- 5. int16 LM (laneK lm4.bin, rune 4-gram with word boundaries) ----------
L4 = np.fromfile(KDIR + '/lm4.bin', dtype=np.float32)
q = np.clip(np.round(L4 * 1000), -32000, 0).astype(np.int16)
q.tofile(OUT + '/lm16.bin')
P('lm16: laneK lm4.bin quantised to int16 milli-nats, max abs err %.4f' % np.abs(q / 1000 - L4).max())
