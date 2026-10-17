"""laneJ core: corpora with word structure + lag profiles."""
import sys, os, re
import numpy as np
S = '.'
sys.path.insert(0, S + '/lp')
import lpdata
OUT = S + '/agents/laneJ_lag5_echo'
RUNES = lpdata.RUNES
R2I = {r: i for i, r in enumerate(RUNES)}
TR = lpdata.TR


def lp_main():
    U, C, h = lpdata.unsolved()
    assert h == '023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
    C = np.array(C, dtype=np.int64)
    word = np.array([w for p in U for w in p['word']])
    chap = np.array([c for p in U for c in p['chap']])
    page = np.array([p['page'] for p in U for _ in p['idx']])
    # renumber word ids to 0..W-1
    _, wid = np.unique(word, return_inverse=True)
    return C, wid, chap, page


def parse_generic(txt, boundary_chars, ignore_chars=''):
    """runes -> stream; any char in boundary_chars ends a word; newlines and ignore_chars ignored;
    anything else also treated as boundary (conservative) unless in ignore."""
    C, W = [], []
    w = 0; inword = False
    for c in txt:
        if c in R2I:
            C.append(R2I[c]); W.append(w); inword = True
        elif c in '\n\r' or c in ignore_chars:
            continue
        else:
            if inword: w += 1; inword = False
    C = np.array(C, dtype=np.int64); _, wid = np.unique(np.array(W), return_inverse=True)
    return C, wid


def lp_relikd():
    d = S + '/dl/transcr/LiberPrayground/pages/'
    files = ['p0-2', 'p3-7', 'p8-14', 'p15-22', 'p23-26', 'p27-32', 'p33-39', 'p40-53', 'p54-55']
    Cs, Ws, chs = [], [], []
    off = 0
    for k, f in enumerate(files):
        t = open(d + f + '.txt', encoding='utf-8').read()
        # quotes / apostrophes are typeset marks inside the text; treat as non-boundaries (contractions)
        c, w = parse_generic(t, '', ignore_chars='"\'')
        Cs.append(c); Ws.append(w + off); chs.append(np.full(len(c), k)); off += w.max() + 1
    return np.concatenate(Cs), np.concatenate(Ws), np.concatenate(chs)


def lp_aldegonde():
    t = open(S + '/dl/aldegonde_clone/aldegonde/data/page0-58.txt', encoding='utf-8').read()
    secs = t.split('$')
    Cs, Ws, chs = [], [], []; off = 0; k = 0
    for s in secs:
        # boundaries: circled marks, - . % &; '/' and newline are continuation; digits/latin are grids (boundary)
        c, w = parse_generic(s.replace('/', ''), '', ignore_chars='"\'')
        if len(c) == 0: continue
        Cs.append(c); Ws.append(w + off); chs.append(np.full(len(c), k)); off += w.max() + 1; k += 1
    C = np.concatenate(Cs); W = np.concatenate(Ws); ch = np.concatenate(chs)
    return C, W, ch


# ---------------- profiles -----------------
def lag_counts(C, wid, maxlag=12, valid=None):
    """returns arrays (mw, nw, mx, nx) of within/across matches and pairs for lags 1..maxlag"""
    N = len(C); out = np.zeros((4, maxlag), dtype=np.int64)
    for k in range(1, maxlag + 1):
        same = wid[:-k] == wid[k:]
        eq = C[:-k] == C[k:]
        if valid is not None:
            v = valid[:-k] & valid[k:]; same_v = same & v; diff_v = (~same) & v
        else:
            same_v = same; diff_v = ~same
        out[0, k-1] = (eq & same_v).sum(); out[1, k-1] = same_v.sum()
        out[2, k-1] = (eq & diff_v).sum(); out[3, k-1] = diff_v.sum()
    return out


def zcells(cnt, p0=1/29):
    mw, nw, mx, nx = cnt
    zw = (mw - p0*nw) / np.sqrt(np.maximum(nw, 1)*p0*(1-p0))
    zx = (mx - p0*nx) / np.sqrt(np.maximum(nx, 1)*p0*(1-p0))
    return zw, zx


def word_meta(wid):
    N = len(wid)
    starts = np.r_[0, np.nonzero(np.diff(wid))[0] + 1]
    lens = np.diff(np.r_[starts, N])
    pos = np.arange(N) - np.repeat(starts, lens)
    wl = np.repeat(lens, lens)
    return pos, wl, starts, lens


# ---------------- English plaintext -----------------
def load_wp_words(maxw=400000):
    ws = []
    with open(S + '/dl/transcr/LiberPrayground/data/baseline-rune-words.txt', encoding='utf-8') as f:
        for line in f:
            w = [R2I[c] for c in line.strip() if c in R2I]
            if w: ws.append(w)
            if len(ws) >= maxw: break
    return ws


def solved_words():
    d = S + '/dl/transcr/LiberPrayground/pages/'
    ws = []
    for f in sorted(os.listdir(d)):
        if f.startswith('solved_') and f.endswith('.txt'):
            t = open(d + f, encoding='utf-8').read()
            c, w = parse_generic(t, '', ignore_chars='"\'')
            for k in range(w.max() + 1):
                ws.append(list(c[w == k]))
    return ws


def by_length(words):
    d = {}
    for w in words: d.setdefault(len(w), []).append(w)
    return d


def matched_plain(lens, bylen, rng):
    """plaintext with exactly the LP word-length sequence, words drawn at random from English of that length"""
    out = []
    for L in lens:
        pool = bylen.get(L)
        while pool is None or len(pool) < 5:
            L2 = L - 1; pool = bylen.get(L2); L = L2
        w = pool[rng.integers(len(pool))]
        if len(w) != len(out) and False: pass
        out.append(w)
    C = np.concatenate([np.array(w) for w in out]); wid = np.repeat(np.arange(len(out)), [len(w) for w in out])
    return C.astype(np.int64), wid


def contiguous_plain(words, nrunes, rng):
    o = rng.integers(len(words) - 20000)
    out = []; n = 0; i = o
    while n < nrunes:
        out.append(words[i]); n += len(words[i]); i += 1
    C = np.concatenate([np.array(w) for w in out]); wid = np.repeat(np.arange(len(out)), [len(w) for w in out])
    return C.astype(np.int64), wid
