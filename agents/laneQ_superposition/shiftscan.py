"""Lane Q (round two): all-shift keystream-reuse scan over LP2 units.

Statistic for an ordered unit pair (a, b) at shift t (a index i is compared with b index i+t):
    M(t) = #{i : a_i == b_{i+t}},   n(t) = overlap,
    p0   = sum_c fa_c * fb_c   (cross-marginal coincidence rate under independence),
    z    = (M - n p0) / sqrt(n p0 (1 - p0)).
Self cells (a == b) use t >= 1 and p0 = sum_c f_c^2.
Overlap must be >= MIN_OV = 60.  All M(t) for a pair come from one FFT cross-correlation
of the 29 one-hot indicator vectors (summed over symbols in the frequency domain).
"""
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'lp'))
import lpdata  # noqa: E402

A = 29
MIN_OV = 60
SHA = '023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'


def load_real():
    """Return (pages, starts, ends): 55 page arrays of rune indices and the chapter runs
    (contiguous runs of equal per-rune chap id) as positions in the flat stream."""
    U, C, sha = lpdata.unsolved()
    assert sha == SHA, sha
    pages = [np.asarray(u['idx'], dtype=np.int64) for u in U]
    chap = np.concatenate([np.asarray(u['chap'], dtype=np.int64) for u in U])
    chg = np.flatnonzero(np.diff(chap) != 0) + 1
    starts = np.r_[0, chg].astype(np.int64)
    ends = np.r_[chg, len(chap)].astype(np.int64)
    return pages, starts, ends


def units_for(kind, pages, starts, ends):
    """Raw-rune units: 'pages' (55), 'chap' (17 chapter runs), 'stream' (one unit)."""
    if kind == 'pages':
        return list(pages)
    flat = np.concatenate(pages)
    if kind == 'chap':
        return [flat[s:e] for s, e in zip(starts, ends)]
    if kind == 'stream':
        return [flat]
    raise ValueError(kind)


def stream_of(units, mode):
    """'raw' keeps runes; 'D' takes increments within each unit (first rune dropped)."""
    if mode == 'raw':
        return list(units)
    return [np.diff(u) % A for u in units]


def null_pages(pages, rng, mode):
    """Null corpus, built page by page.
    raw: permute the runes within each page.
    D:   permute the increments within each page and rebuild the runes from the page's first rune
         (keeps the doublet deficit and the page's first rune)."""
    out = []
    for p in pages:
        if mode == 'raw':
            out.append(rng.permutation(p))
        else:
            r = np.empty_like(p)
            r[0] = p[0]
            d = rng.permutation(np.diff(p) % A)
            r[1:] = (p[0] + np.cumsum(d)) % A
            out.append(r)
    return out


BIN_EDGES = [60, 100, 150, 250, 500, 1000, 10 ** 9]   # overlap bins: [60,100), [100,150), ...


def scan(units, collect=False):
    """Global shift scan over all unordered unit pairs (incl. self cells at t>=1).
    units: list of int64 arrays (already in the analysis stream, raw or D).
    Returns dict: maxz, arg=(iu,iv,t,n,M), n4 (#cells z>4), ncells, binmax / binn4 (per overlap
    bin BIN_EDGES: max z and count z>4), and cells (rows [iu,iv,t,n,M,z]) when collect=True."""
    us = [np.asarray(u, dtype=np.int64) for u in units]
    lens = np.array([len(u) for u in us], dtype=np.int64)
    keep = np.flatnonzero(lens >= MIN_OV)
    nbin = len(BIN_EDGES) - 1
    st = {'maxz': -np.inf, 'arg': None, 'n4': 0, 'ncells': 0, 'store': [] if collect else None,
          'binmax': np.full(nbin, -np.inf), 'binn4': np.zeros(nbin, dtype=np.int64)}

    def acc(iu, iv, ts, n, M, z):
        j = int(np.argmax(z))
        if z[j] > st['maxz']:
            st['maxz'] = float(z[j])
            st['arg'] = (int(iu), int(iv), int(ts[j]), int(n[j]), int(M[j]))
        st['n4'] += int(np.count_nonzero(z > 4.0))
        st['ncells'] += int(len(z))
        bi = np.clip(np.searchsorted(BIN_EDGES, n, side='right') - 1, 0, nbin - 1)
        np.maximum.at(st['binmax'], bi, z)
        np.add.at(st['binn4'], bi, (z > 4.0).astype(np.int64))
        if st['store'] is not None:
            st['store'].append(np.stack([np.full(len(z), iu), np.full(len(z), iv), ts, n, M, z], axis=1).astype(float))

    if len(keep) == 0:
        return _finish(st)
    P = 1
    while P < 2 * int(lens.max()):
        P *= 2
    nu = len(us)
    F = np.zeros((nu, A, P // 2 + 1), dtype=np.complex128)
    freq = np.zeros((nu, A))
    for i in keep:
        x = us[i]
        oh = np.zeros((A, P))
        oh[x, np.arange(len(x))] = 1.0
        F[i] = np.fft.rfft(oh, axis=1)
        freq[i] = np.bincount(x, minlength=A) / len(x)
    for iu in keep:
        Lu = int(lens[iu])
        # self cells: t = 1 .. Lu-MIN_OV, n = Lu - t
        ts = np.arange(1, Lu - MIN_OV + 1)
        if len(ts):
            S = np.sum(np.conj(F[iu]) * F[iu], axis=0)
            r = np.fft.irfft(S, n=P)
            n = Lu - ts
            p0 = float(freq[iu] @ freq[iu])
            M = np.rint(r[ts]).astype(np.int64)
            z = (M - n * p0) / np.sqrt(n * p0 * (1 - p0))
            acc(iu, iu, ts, n, M, z)
        others = keep[keep > iu]
        if len(others) == 0:
            continue
        S = np.einsum('cf,vcf->vf', np.conj(F[iu]), F[others])
        R = np.fft.irfft(S, n=P, axis=1)
        for k, iv in enumerate(others):
            Lv = int(lens[iv])
            # M(t) = sum_i a_i b_{i+t};  n(t) = min(Lu, Lv-t) - max(0,-t);  need n >= MIN_OV
            ts = np.arange(-(Lu - MIN_OV), Lv - MIN_OV + 1)
            n = np.minimum(Lu, Lv - ts) - np.maximum(0, -ts)
            M = np.rint(R[k, ts % P]).astype(np.int64)
            p0 = float(freq[iu] @ freq[iv])
            z = (M - n * p0) / np.sqrt(n * p0 * (1 - p0))
            acc(iu, iv, ts, n, M, z)
    return _finish(st)


def _finish(st):
    out = {'maxz': st['maxz'], 'arg': st['arg'], 'n4': st['n4'], 'ncells': st['ncells'],
           'binmax': [float(x) for x in st['binmax']], 'binn4': [int(x) for x in st['binn4']]}
    if st['store'] is not None:
        out['cells'] = np.concatenate(st['store'], axis=0) if st['store'] else np.zeros((0, 6))
    return out


def cell_brute(a, b, t):
    """Direct (non-FFT) computation of one cell, used to verify the scan."""
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    La, Lb = len(a), len(b)
    i0 = max(0, -t)
    i1 = min(La, Lb - t)
    n = i1 - i0
    M = int(np.sum(a[i0:i1] == b[i0 + t:i1 + t]))
    p0 = float((np.bincount(a, minlength=A) / La) @ (np.bincount(b, minlength=A) / Lb))
    z = (M - n * p0) / np.sqrt(n * p0 * (1 - p0))
    return {'M': M, 'n': int(n), 'p0': p0, 'z': float(z)}


# ---------- planted plaintext and ciphers (used by the controls) ----------

def enc_additive(p, K, s):
    return (np.asarray(p) + K[s:s + len(p)]) % A


def enc_chain(p, K, s):
    """c_i = c_{i-1} + 1 + ((p_i + k_i) mod 28) mod 29, c_{-1} = 0."""
    p = np.asarray(p)
    inc = (1 + ((p + K[s:s + len(p)]) % 28)) % A
    return np.cumsum(inc) % A


def enc_skip(p, K, s):
    """additive; if the output equals the previous output, consume the next key value instead."""
    p = np.asarray(p)
    out = np.empty(len(p), dtype=np.int64)
    j = s
    prev = -1
    for i, x in enumerate(p):
        r = (int(x) + int(K[j])) % A
        j += 1
        while r == prev:
            r = (int(x) + int(K[j])) % A
            j += 1
        out[i] = r
        prev = r
    return out


ENC = {'add': enc_additive, 'chain': enc_chain, 'skip': enc_skip}


def english_runes(source='prose'):
    """English plaintext as rune indices via lane N's eng2runes (agents/laneN_cribdrag/common.py).
    source='prose': sentences of Python's own documentation prose (pydoc_data.topics), a long
    English corpus that ships with the interpreter. source='solved': the transliterations of the
    five solved pages in dl/dukotah/liber-primus/SOLVED-PAGES.json (only ~1,800 runes)."""
    sys.path.insert(0, os.path.join(ROOT, 'agents', 'laneN_cribdrag'))
    import common  # noqa: E402  (eng2runes)
    if source == 'prose':
        import pydoc_data.topics as T
        keep = []
        for ln in '\n'.join(T.topics.values()).split('\n'):
            s = ln.strip()
            words = s.split()
            if len(words) >= 8 and sum((ch.isalpha() or ch in " ,.;:'-") for ch in s) >= 0.95 * len(s):
                keep.append(s)
        text = ' '.join(keep)
    elif source == 'solved':
        import json
        d = json.load(open(os.path.join(ROOT, 'dl', 'dukotah', 'liber-primus', 'SOLVED-PAGES.json'), encoding='utf-8'))
        text = ' '.join(p['plaintext_transliteration'] for p in d['pages'] if p.get('plaintext_transliteration'))
    else:
        raise ValueError(source)
    return np.asarray(common.eng2runes(text), dtype=np.int64)


def cell_detail(a, b, t):
    """Extra diagnostics for a reported cell: exact binomial upper-tail -log10 p of M under p0,
    and the longest run of consecutive equal positions (scattered plaintext coincidences give short
    runs; a copied passage gives a long run)."""
    from math import lgamma, log, exp
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    La, Lb = len(a), len(b)
    i0 = max(0, -t)
    i1 = min(La, Lb - t)
    eq = (a[i0:i1] == b[i0 + t:i1 + t]).astype(np.int8)
    n = int(i1 - i0)
    M = int(eq.sum())
    p0 = float((np.bincount(a, minlength=A) / La) @ (np.bincount(b, minlength=A) / Lb))
    # log upper tail: log sum_{k>=M} C(n,k) p^k (1-p)^(n-k)
    lc = lambda k: lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)  # noqa: E731
    terms = [lc(k) + k * log(p0) + (n - k) * log(1 - p0) for k in range(M, n + 1)]
    mx = max(terms)
    logtail = mx + log(sum(exp(x - mx) for x in terms))
    run = best = 0
    for v in eq:
        run = run + 1 if v else 0
        best = max(best, run)
    return {'p0': p0, 'neglog10_binom_tail': float(-logtail / log(10)), 'longest_run': int(best)}
