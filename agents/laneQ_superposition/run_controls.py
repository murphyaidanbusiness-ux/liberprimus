"""Lane Q: planted positive controls and power curves for the all-shift reuse scan.

Run from the repository root:  python agents/laneQ_superposition/run_controls.py

Planted design (per plant): two English passages P1, P2 (disjoint segments of the English corpus)
are enciphered with ONE random keystream K: unit u uses K from offset 0, unit v uses K from offset s
(random relative shift, overlap n = L - s >= 60). Three cipher kinds:
  add   : c = p + k mod 29 (raw stream carries the match)
  chain : c_i = c_{i-1} + 1 + ((p_i + k_i) mod 28) mod 29 (increment stream D carries the match)
  skip  : additive with skip-on-repeat (if the output equals the previous rune, consume the next key)
Each plant is placed into a null-style background (page-shuffled real stream, cut into units of
length L, or the real page structure, or the whole stream with two planted segments).
Detection = planted cell z > null max (max over 200 null backgrounds of the global max z).
"""
import os
import sys
import json
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shiftscan as S  # noqa: E402

OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
NULLS = 200
NPLANT = 20
LENGTHS = [250, 500, 1000, 2000]
KINDS = ['add', 'chain', 'skip']
MODES = ['raw', 'D']
BASE = 20261016


def log(*a):
    print(*a, flush=True)


def stats(x):
    x = np.asarray(x, dtype=float)
    return {'mean': float(x.mean()), 'sd': float(x.std(ddof=1)) if len(x) > 1 else 0.0,
            'max': float(x.max()), 'min': float(x.min())}


pages, starts, ends = S.load_real()
ENG = S.english_runes('prose')
half = len(ENG) // 2
pm = np.bincount(ENG, minlength=S.A) / len(ENG)
q_add = float(pm @ pm)
r28 = np.zeros(28)
for c in range(S.A):
    r28[c % 28] += pm[c]
q_chain = float(r28 @ r28)
log('English source: prose, %d runes; monogram IoC (29*sum f^2) = %.3f' % (len(ENG), 29 * q_add))
log('plaintext coincidence rate q (rune-equal) = %.5f ; mod-28 coincidence q28 = %.5f ; random 1/29 = %.5f'
    % (q_add, q_chain, 1 / 29))


def english_pair(rng, L):
    o1 = int(rng.integers(0, half - L))
    o2 = int(rng.integers(half, len(ENG) - L))
    return ENG[o1:o1 + L].copy(), ENG[o2:o2 + L].copy()


def make_keys(rng, L):
    return rng.integers(0, S.A, size=3 * L + 1000)


# ------------------------------------------------------------------ 0. sanity: FFT vs brute
log('\n[0] FFT scan vs brute-force cells (real data)')
rng0 = np.random.default_rng(BASE)
for kind in ['pages', 'chap', 'stream']:
    for mode in MODES:
        us = S.stream_of(S.units_for(kind, pages, starts, ends), mode)
        r = S.scan(us, collect=True)
        cells = r['cells']
        pick = np.r_[rng0.choice(len(cells), size=min(300, len(cells)), replace=False), int(np.argmax(cells[:, 5]))]
        dM = dz = 0.0
        for j in pick:
            iu, iv, t, n, M, z = cells[j]
            b = S.cell_brute(us[int(iu)], us[int(iv)], int(t))
            dM = max(dM, abs(b['M'] - M), abs(b['n'] - n))
            dz = max(dz, abs(b['z'] - z))
        log('   %-6s %-3s cells=%6d  max|dM|=%g max|dz|=%g' % (kind, mode, len(cells), dM, dz))
        assert dM == 0 and dz < 1e-8

# ------------------------------------------------------------------ 1. block power curve
results = {'english': {'q_add': q_add, 'q_chain': q_chain, 'n_runes': int(len(ENG))}, 'blocks': {}, 'stream': {},
           'pages_real': {}}
t_start = time.time()
log('\n[1] block units of length L (background = page-shuffled real stream cut into L-blocks)')
for L in LENGTHS:
    for mode in MODES:
        nb = sum(len(p) for p in pages) // L
        rng_n = np.random.default_rng(BASE + 10 * L + (0 if mode == 'raw' else 1))
        null_max, null_n4 = [], []
        for _ in range(NULLS):
            flat = np.concatenate(S.null_pages(pages, rng_n, mode))
            blocks = [flat[i * L:(i + 1) * L] for i in range(nb)]
            r = S.scan(S.stream_of(blocks, mode))
            null_max.append(r['maxz'])
            null_n4.append(r['n4'])
        T = float(np.max(null_max))
        key = '%d|%s' % (L, mode)
        results['blocks'][key] = {'nblocks': nb, 'null_maxz': stats(null_max), 'null_n4': stats(null_n4),
                                  'threshold_nullmax': T, 'plants': {}}
        log('  L=%4d mode=%-3s blocks=%2d  null maxz mean=%.3f sd=%.3f max=%.3f | null n4 mean=%.2f'
            % (L, mode, nb, np.mean(null_max), np.std(null_max, ddof=1), T, np.mean(null_n4)))
        for kind in KINDS:
            rng = np.random.default_rng(BASE + 7 * L + KINDS.index(kind) * 101 + (0 if mode == 'raw' else 5))
            rows = []
            for r_i in range(NPLANT):
                flat = np.concatenate(S.null_pages(pages, rng, mode))
                blocks = [flat[i * L:(i + 1) * L].copy() for i in range(nb)]
                a, b = sorted(rng.choice(nb, size=2, replace=False).tolist())
                s = int(rng.integers(1, L - S.MIN_OV + 1))
                uu_is_lo = bool(rng.integers(0, 2))
                P1, P2 = english_pair(rng, L)
                K = make_keys(rng, L)
                u_arr = S.ENC[kind](P1, K, 0)
                v_arr = S.ENC[kind](P2, K, s)
                if uu_is_lo:
                    blocks[a], blocks[b] = u_arr, v_arr
                    t = -s
                else:
                    blocks[a], blocks[b] = v_arr, u_arr
                    t = s
                us = S.stream_of(blocks, mode)
                scan = S.scan(us)
                cell = S.cell_brute(us[a], us[b], t)
                rows.append({'a': a, 'b': b, 't': t, 'n': cell['n'], 'M': cell['M'], 'z': cell['z'],
                             'global_max': scan['maxz'], 'argmax_is_planted': bool(scan['arg'][:3] == (a, b, t)),
                             'det_cell': bool(cell['z'] > T), 'det_global': bool(scan['maxz'] > T)})
            zs = [x['z'] for x in rows]
            dc = np.mean([x['det_cell'] for x in rows])
            dg = np.mean([x['det_global'] for x in rows])
            results['blocks'][key]['plants'][kind] = {'rows': rows, 'z_planted': stats(zs),
                                                      'detect_cell': float(dc), 'detect_global': float(dg)}
            log('    plant=%-5s planted z mean=%6.2f sd=%5.2f (overlap n %d-%d)  detect(cell>T)=%.2f  detect(global>T)=%.2f'
                % (kind, np.mean(zs), np.std(zs, ddof=1), min(x['n'] for x in rows), max(x['n'] for x in rows), dc, dg))

# ------------------------------------------------------------------ 2. whole stream, two local plants
log('\n[2] whole-stream self-scan (all lags), two planted segments of length L in the 12,956-rune stream')
for L in LENGTHS:
    for mode in MODES:
        N = int(sum(len(p) for p in pages))
        rng_n = np.random.default_rng(BASE + 99 + 10 * L + (0 if mode == 'raw' else 1))
        null_max = []
        for _ in range(NULLS):
            flat = np.concatenate(S.null_pages(pages, rng_n, mode))
            null_max.append(S.scan(S.stream_of([flat], mode))['maxz'])
        T = float(np.max(null_max))
        rows = []
        for kind in KINDS:
            rng = np.random.default_rng(BASE + 555 + 7 * L + KINDS.index(kind) * 101 + (0 if mode == 'raw' else 5))
            for r_i in range(NPLANT):
                flat = np.concatenate(S.null_pages(pages, rng, mode)).copy()
                a = int(rng.integers(0, N - 2 * L))
                b = int(rng.integers(a + L, N - L + 1))
                s = int(rng.integers(1, L - S.MIN_OV + 1))
                P1, P2 = english_pair(rng, L)
                K = make_keys(rng, L)
                flat[a:a + L] = S.ENC[kind](P1, K, 0)
                flat[b:b + L] = S.ENC[kind](P2, K, s)
                x = flat if mode == 'raw' else (np.diff(flat) % S.A)
                t = b - a - s
                cell = S.cell_brute(x, x, t)
                g = S.scan([x])
                rows.append({'kind': kind, 'a': a, 'b': b, 's': s, 't': t, 'n': cell['n'], 'z': cell['z'],
                             'det_cell': bool(cell['z'] > T), 'global_max': g['maxz']})
        for kind in KINDS:
            rr = [x for x in rows if x['kind'] == kind]
            results['stream'].setdefault('%d|%s' % (L, mode), {})[kind] = {
                'threshold_nullmax': T, 'null_maxz': stats(null_max), 'z_planted': stats([x['z'] for x in rr]),
                'detect_cell': float(np.mean([x['det_cell'] for x in rr])), 'rows': rr}
            log('  L=%4d mode=%-3s plant=%-5s T(null max over lags)=%.3f  planted z mean=%5.2f  detect=%.2f'
                % (L, mode, kind, T, np.mean([x['z'] for x in rr]), np.mean([x['det_cell'] for x in rr])))

# ------------------------------------------------------------------ 3. real page lengths
log('\n[3] page-level control on real page lengths (two real pages replaced by planted units of their lengths)')
for mode in MODES:
    rng_n = np.random.default_rng(BASE + 4242 + (0 if mode == 'raw' else 1))
    null_max = [S.scan(S.stream_of(S.null_pages(pages, rng_n, mode), mode))['maxz'] for _ in range(NULLS)]
    T = float(np.max(null_max))
    results['pages_real'][mode] = {'threshold_nullmax': T, 'null_maxz': stats(null_max), 'plants': {}}
    log('  mode=%-3s null maxz mean=%.3f sd=%.3f max(=T)=%.3f' % (mode, np.mean(null_max), np.std(null_max, ddof=1), T))
    for kind in KINDS:
        rng = np.random.default_rng(BASE + 9000 + KINDS.index(kind) * 37 + (0 if mode == 'raw' else 3))
        rows = []
        for r_i in range(NPLANT):
            bg = S.null_pages(pages, rng, mode)
            a, b = rng.choice(len(pages), size=2, replace=False).tolist()
            uu = a if rng.integers(0, 2) == 0 else b
            vv = b if uu == a else a
            Lu = len(pages[uu])
            s = int(rng.integers(1, Lu - S.MIN_OV + 1))
            Lv = len(pages[vv])
            P1, P2 = english_pair(rng, max(Lu, Lv))
            K = make_keys(rng, max(Lu, Lv))
            u_arr = S.ENC[kind](P1[:Lu], K, 0)
            v_arr = S.ENC[kind](P2[:Lv], K, s)
            pl = list(bg)
            pl[uu] = u_arr
            pl[vv] = v_arr
            lo, hi = min(a, b), max(a, b)
            t = -s if uu == lo else s
            us = S.stream_of(pl, mode)
            cell = S.cell_brute(us[lo], us[hi], t)
            g = S.scan(us)
            rows.append({'lo': lo, 'hi': hi, 't': t, 'n': cell['n'], 'z': cell['z'], 'global_max': g['maxz'],
                         'det_cell': bool(cell['z'] > T), 'det_global': bool(g['maxz'] > T)})
        results['pages_real'][mode]['plants'][kind] = {
            'rows': rows, 'z_planted': stats([x['z'] for x in rows]),
            'detect_cell': float(np.mean([x['det_cell'] for x in rows])),
            'detect_global': float(np.mean([x['det_global'] for x in rows]))}
        log('  mode=%-3s plant=%-5s planted z mean=%5.2f  detect(cell)=%.2f  detect(global)=%.2f  overlap n range %d-%d'
            % (mode, kind, np.mean([x['z'] for x in rows]), np.mean([x['det_cell'] for x in rows]),
               np.mean([x['det_global'] for x in rows]), min(x['n'] for x in rows), max(x['n'] for x in rows)))

# ------------------------------------------------------------------ 4. analytic power curve
log('\n[4] analytic expectation: E[z_planted | overlap n] = sqrt(n) (q - p0) / sqrt(p0 (1-p0)); p0 = 1/29 (raw) or 1/28 (D)')
for lab, q, p0 in [('raw/add', q_add, 1 / 29), ('D/chain', q_chain, 1 / 28)]:
    c = (q - p0) / np.sqrt(p0 * (1 - p0))
    row = ', '.join('n=%d: %.2f' % (n, np.sqrt(n) * c) for n in [60, 100, 250, 500, 1000, 2000])
    log('  %-8s c=%.4f  %s' % (lab, c, row))
    results.setdefault('analytic', {})[lab] = {'c': c, 'p0': p0, 'q': q}

json.dump(results, open(os.path.join(OUT, 'controls.json'), 'w'), indent=1, default=float)
log('\nwrote %s (%.0f s)' % (os.path.join(OUT, 'controls.json'), time.time() - t_start))
