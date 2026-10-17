"""Lane Q: the real all-shift scan on LP2 (pages 0-54), unit types pages / chapters / whole stream,
streams raw and D (increments within unit), against 200 shuffled corpora through the identical pipeline.

Run from the repository root:  python agents/laneQ_superposition/run_real.py
Output: agents/laneQ_superposition/out/real.json (real results, top cells, null distributions).
"""
import os
import sys
import json
import time
import multiprocessing as mp
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shiftscan as S  # noqa: E402

OUT = os.path.join(HERE, 'out')
NULLS = 200
KINDS = ['pages', 'chap', 'stream']
MODES = ['raw', 'D']
BASE = 20261016 + 777
_DATA = None


def _init():
    global _DATA
    _DATA = S.load_real()


def _null_one(seed):
    pages, starts, ends = _DATA
    out = {}
    for mode in MODES:
        rng = np.random.default_rng([BASE, seed, 0 if mode == 'raw' else 1])
        npg = S.null_pages(pages, rng, mode)
        for kind in KINDS:
            us = S.stream_of(S.units_for(kind, npg, starts, ends), mode)
            r = S.scan(us)
            out['%s|%s' % (kind, mode)] = {'maxz': r['maxz'], 'n4': r['n4'], 'binmax': r['binmax'],
                                            'binn4': r['binn4']}
    return seed, out


def _label(kind, i):
    if kind == 'pages':
        return 'p%02d' % i
    if kind == 'chap':
        return 'chap%02d' % i
    return 'stream'


def real_pass(pages, starts, ends):
    res = {}
    for kind in KINDS:
        for mode in MODES:
            us = S.stream_of(S.units_for(kind, pages, starts, ends), mode)
            r = S.scan(us, collect=True)
            cells = r['cells']
            order = np.argsort(-cells[:, 5], kind='stable')[:20]
            top = []
            for j in order:
                iu, iv, t, n, M, z = cells[j]
                iu, iv, t = int(iu), int(iv), int(t)
                det = S.cell_detail(us[iu], us[iv], t)
                top.append({'unit_a': _label(kind, iu), 'unit_b': _label(kind, iv), 'shift': t,
                            'n': int(n), 'M': int(M), 'z': float(z), 'p0': det['p0'],
                            'neglog10_binom_tail': det['neglog10_binom_tail'],
                            'longest_run': det['longest_run']})
            entry = {'maxz': r['maxz'], 'arg': r['arg'], 'n4': r['n4'], 'ncells': r['ncells'],
                     'binmax': r['binmax'], 'binn4': r['binn4'], 'top20': top,
                     'nunits': len(us), 'unit_lengths': [int(len(u)) for u in us]}
            if kind == 'stream':
                lag = cells[:, 2]
                entry['maxz_lag_le_6478'] = float(cells[lag <= 6478, 5].max())
                entry['n4_lag_le_6478'] = int(np.count_nonzero(cells[lag <= 6478, 5] > 4))
                entry['maxz_lag_gt_6478'] = float(cells[lag > 6478, 5].max())
            res['%s|%s' % (kind, mode)] = entry
            print('REAL %-6s %-3s units=%2d cells=%7d maxz=%.3f arg=%s n4=%d'
                  % (kind, mode, len(us), r['ncells'], r['maxz'], r['arg'], r['n4']), flush=True)
    return res


def summarise(real, nulls):
    summ = {}
    for key, rv in real.items():
        nm = np.array([n[key]['maxz'] for n in nulls])
        n4 = np.array([n[key]['n4'] for n in nulls], dtype=float)
        bmax = np.array([n[key]['binmax'] for n in nulls], dtype=float)
        bn4 = np.array([n[key]['binn4'] for n in nulls], dtype=float)
        d = {
            'real_maxz': rv['maxz'],
            'null_maxz_mean': float(nm.mean()), 'null_maxz_sd': float(nm.std(ddof=1)),
            'null_maxz_max': float(nm.max()), 'null_maxz_p50': float(np.median(nm)),
            'z_of_real_maxz_vs_null': float((rv['maxz'] - nm.mean()) / nm.std(ddof=1)),
            'emp_p_maxz': float((1 + np.sum(nm >= rv['maxz'])) / (1 + len(nm))),
            'real_n4': rv['n4'], 'null_n4_mean': float(n4.mean()), 'null_n4_sd': float(n4.std(ddof=1)),
            'null_n4_max': float(n4.max()),
            'z_of_real_n4_vs_null': float((rv['n4'] - n4.mean()) / n4.std(ddof=1)) if n4.std(ddof=1) > 0 else None,
            'emp_p_n4': float((1 + np.sum(n4 >= rv['n4'])) / (1 + len(n4))),
            'bins': []}
        for k, (lo, hi) in enumerate(zip(S.BIN_EDGES[:-1], S.BIN_EDGES[1:])):
            col = bmax[:, k]
            if not np.isfinite(rv['binmax'][k]) or not np.all(np.isfinite(col)):
                continue
            d['bins'].append({'bin': '[%d,%s)' % (lo, '%d' % hi if hi < 10 ** 8 else 'inf'),
                              'real_binmax': rv['binmax'][k], 'null_binmax_mean': float(col.mean()),
                              'null_binmax_sd': float(col.std(ddof=1)),
                              'real_binn4': rv['binn4'][k], 'null_binn4_mean': float(bn4[:, k].mean()),
                              'emp_p_binmax': float((1 + np.sum(col >= rv['binmax'][k])) / (1 + len(col)))})
        summ[key] = d
    return summ


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    pages, starts, ends = S.load_real()
    real = real_pass(pages, starts, ends)
    print('real pass done (%.1f s); running %d nulls' % (time.time() - t0, NULLS), flush=True)
    workers = max(1, min(8, os.cpu_count() or 1))
    with mp.Pool(workers, initializer=_init) as pool:
        nulls = [None] * NULLS
        for seed, out in pool.imap_unordered(_null_one, range(NULLS)):
            nulls[seed] = out
    summ = summarise(real, nulls)
    for key in real:
        s = summ[key]
        print('\n== %s' % key)
        print('  maxz real=%.3f | null maxz mean=%.3f sd=%.3f max=%.3f | z=%+.2f emp_p=%.3f'
              % (s['real_maxz'], s['null_maxz_mean'], s['null_maxz_sd'], s['null_maxz_max'],
                 s['z_of_real_maxz_vs_null'], s['emp_p_maxz']))
        print('  n(z>4) real=%d | null mean=%.2f sd=%.2f max=%d | emp_p=%.3f'
              % (s['real_n4'], s['null_n4_mean'], s['null_n4_sd'], s['null_n4_max'], s['emp_p_n4']))
        for b in s['bins']:
            print('    bin %-14s real max %.3f vs null %.3f+-%.3f  (emp_p %.3f) | n4 real %d null %.1f'
                  % (b['bin'], b['real_binmax'], b['null_binmax_mean'], b['null_binmax_sd'], b['emp_p_binmax'],
                     b['real_binn4'], b['null_binn4_mean']))
        for c in real[key]['top20'][:8]:
            print('    top: %-7s %-7s t=%5d n=%4d M=%3d z=%.3f  -log10 binom=%.2f  longest run=%d'
                  % (c['unit_a'], c['unit_b'], c['shift'], c['n'], c['M'], c['z'],
                     c['neglog10_binom_tail'], c['longest_run']))
        if key.startswith('stream'):
            print('  stream lags <=6478 (campaign XIV range): max z=%.3f, n(z>4)=%d ; lags >6478: max z=%.3f'
                  % (real[key]['maxz_lag_le_6478'], real[key]['n4_lag_le_6478'], real[key]['maxz_lag_gt_6478']))
    json.dump({'nulls': NULLS, 'real': real, 'summary': summ,
               'null_raw': [{k: {'maxz': v['maxz'], 'n4': v['n4']} for k, v in n.items()} for n in nulls]},
              open(os.path.join(OUT, 'real.json'), 'w'), indent=1, default=float)
    print('\nwrote %s (%.0f s)' % (os.path.join(OUT, 'real.json'), time.time() - t0))
