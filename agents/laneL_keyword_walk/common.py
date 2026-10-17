"""laneL common: paths, transliteration, keyword alphabets, g constructions, lexicon, LM."""
import sys, os, re, itertools, collections
import numpy as np
S = '.'
OUT = S + '/agents/laneL_keyword_walk'
KDIR = S + '/agents/laneK_walk_search'
sys.path.insert(0, S + '/lp'); sys.path.insert(0, KDIR); sys.path.insert(0, S + '/agents/laneJ_lag5_echo')
import lpdata
M = 29
TR = lpdata.TR
PRIMES = lpdata.PRIMES
R2I = {r: i for i, r in enumerate(lpdata.RUNES)}

# ---- transliteration (two conventions: aldegonde/W&P 'ING'->NG, lane-A greedy I+NG) ----
_SP = {lab: (i,) for i, lab in enumerate(TR)}
_SP.update({'ING': (21,), 'IO': (27,), 'QU': (5, 7), 'K': (5,), 'Q': (5,), 'V': (1,), 'Z': (15,)})
_LONG = max(len(k) for k in _SP)
def eng_runes(text, ing=True):
    s = re.sub('[^A-Z]', '', text.upper()); out = []; i = 0
    while i < len(s):
        for L in range(_LONG, 0, -1):
            sp = s[i:i + L]
            if len(sp) == L and sp in _SP and (ing or sp != 'ING'):
                out.extend(_SP[sp]); i += L; break
        else:
            i += 1
    return out

def tr(idx): return '-'.join(TR[i] for i in idx)
def trs(idx): return ''.join(TR[i] for i in idx)

# ---- keyword alphabets (aldegonde keyword_exhaustion.alphabets, plus reversed forms) ----
def dedup(seq):
    out = []
    for r in seq:
        if r not in out: out.append(r)
    return out

def alph_rules(seq):
    """seq = de-duplicated keyword runes. Returns dict rule -> 29-rune alphabet (list)."""
    rest = [i for i in range(M) if i not in seq]
    d = {'R1': seq + rest,                 # keyword, rest in rune (= prime-value) order
         'R2': seq + rest[::-1]}           # keyword, rest in Atbash (reverse) order
    if seq:
        k = seq[-1]
        d['R3'] = seq + [i for i in list(range(k + 1, M)) + list(range(k + 1)) if i not in seq]  # cyclic continuation
    full = seq + rest
    d['R4'] = [x for c in range(6) for x in full[c::6]]  # keyword into 6-wide grid, read by columns
    d['R1rev'] = d['R1'][::-1]; d['R2rev'] = d['R2'][::-1]
    return d

def inv(p):
    q = [0] * M
    for i, x in enumerate(p): q[x] = i
    return q

def perm_order(p):
    seen = [False] * M; o = 1
    from math import gcd
    for i in range(M):
        if not seen[i]:
            L = 0; j = i
            while not seen[j]: seen[j] = True; j = p[j]; L += 1
            o = o * L // gcd(o, L)
    return o

def ppow(p, k):
    r = list(range(M))
    for _ in range(k): r = [p[x] for x in r]
    return r

# ---- g constructions ----
ENG_ORDER = sorted(range(M), key=lambda i: TR[i])      # aldegonde 'english-alphabetical'
def grid_fill(cells, fill):
    if fill == 'row': return [cells[r * 5:(r + 1) * 5] for r in range(5)]
    if fill == 'col': return [[cells[c * 5 + r] for c in range(5)] for r in range(5)]
    if fill == 'bou':
        return [cells[r * 5:(r + 1) * 5] if r % 2 == 0 else cells[r * 5:(r + 1) * 5][::-1] for r in range(5)]
    raise ValueError

def g_from_grid(grid, k=1):
    """columns of the 5x5 grid become 5-cycles, rotated down by k (aldegonde g_construction_survey.build_g with uniform offsets)."""
    g = list(range(M))
    for c in range(5):
        col = [grid[r][c] for r in range(5)]
        for r in range(5): g[col[r]] = col[(r + k) % 5]
    return g

def structured_g_oosterhof(fixed):
    rest = [x for x in range(M) if x not in fixed]
    g = list(range(M))
    for i, x in enumerate(rest): g[x] = rest[(i + 5) % 25]
    return g

# ---- corpora ----
def wp_words(maxw=None):
    ws = []
    with open(S + '/dl/transcr/LiberPrayground/data/baseline-rune-words.txt', encoding='utf-8') as f:
        for line in f:
            w = [R2I[c] for c in line.strip() if c in R2I]
            if w: ws.append(tuple(w))
            if maxw and len(ws) >= maxw: break
    return ws

def cicada_vocab():
    out = []
    for line in open(S + '/agents/laneA_keyword_chain/keys.txt'):
        a = line.split()
        if a[0] == '1': out.append(tuple(int(x) for x in a[2:]))
    return out

def lp_pages():
    U, C, h = lpdata.unsolved()
    assert h == '023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
    return U

def words_of_page(p):
    ws = []; cur = []; last = None
    for i, x in zip(p['word'], p['idx']):
        if i != last and cur: ws.append(cur); cur = []
        cur.append(x); last = i
    if cur: ws.append(cur)
    return ws

def solved_words():
    import core
    return [tuple(w) for w in core.solved_words() if len(w)]

def write_text(path, words):
    with open(path, 'w') as f:
        f.write('%d\n' % len(words)); f.write(' '.join(str(len(w)) for w in words) + '\n')
        f.write(' '.join(str(x) for w in words for x in w) + '\n')

def ioc(x):
    n = np.bincount(np.asarray(x), minlength=29).astype(float); N = n.sum()
    return 29 * (n * (n - 1)).sum() / (N * (N - 1))

# ---- Oosterhof walk (exact; identical to laneK kcore.enc_walk / aldegonde doublet_dodge_walk.encipher) ----
def enc_walk(words, base0, g, sigma, reset=False, fixed=False):
    gp = [ppow(g, k) for k in range(5)]; base = list(base0); out = []; clock = 0; prev = -1
    for w in words:
        if reset: clock = 0
        cw = []
        for p in w:
            c = base[gp[clock % 5][p]]
            if c == prev:
                clock += 1; c = base[gp[clock % 5][p]]
            cw.append(c); prev = c; clock += 1
        out.append(cw)
        if not fixed:
            e = (clock - 1) % 5
            base = [base[gp[e][sigma[x]]] for x in range(M)]
    return out
