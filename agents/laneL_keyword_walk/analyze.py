"""Rescore kwwalk top-K lists: full decryption of the text (kwdec beam 16), dukotah quadgram per-quadgram score,
rune IoC, LM per symbol. usage: analyze.py RUNNAME [RUNNAME ...]  (runs/RUNNAME.txt; text inferred from the name)"""
import sys, os, subprocess, json, math
import numpy as np
from common import *
sys.path.insert(0, S + '/dl/dukotah/liber-primus/src')
from lp.score import Quadgram
Q = Quadgram()
Ameta = open(OUT + '/A_meta.txt').read().split('\n')
Gmeta = open(OUT + '/G_meta.txt').read().split('\n')

def text_of(run):
    base = run.split('full_', 1)[1] if 'full_' in run else run.split('_', 1)[1]
    for pre in ('', ):
        p = OUT + '/texts/%s.txt' % base
        if os.path.exists(p): return p
    raise FileNotFoundError(run)

def parse(run):
    modes = {}; cur = None; hdr = None
    for line in open(OUT + '/runs/%s.txt' % run):
        if line.startswith('# text'): hdr = line.strip()
        elif line.startswith('# mode'):
            a = line.split(); cur = int(a[2]); modes[cur] = {'hdr': line.strip(), 'c': []}
        elif line.strip():
            a = line.split(); modes[cur]['c'].append((int(a[0]), int(a[1]), int(a[2]), int(a[3]), int(a[4]), float(a[5])))
    return hdr, modes

def stats(plain):
    s = trs(plain)
    return Q.score_norm(s), ioc(plain) if len(plain) > 1 else 0

def analyze(run, topn=1000, beam=16):
    txt = text_of(run); hdr, modes = parse(run); res = {'run': run, 'hdr': hdr, 'modes': {}}
    for m, d in modes.items():
        cands = d['c'][:topn]
        if not cands: res['modes'][m] = None; continue
        kf = OUT + '/runs/%s_m%d_keys.txt' % (run, m); of = OUT + '/runs/%s_m%d_dec.txt' % (run, m)
        open(kf, 'w').write(''.join('%d %d %d %d\n' % c[:4] for c in cands))
        subprocess.run([OUT + '/kwdec', txt, kf, of, str(beam)], check=True, cwd=OUT)
        rows = []
        for c, line in zip(cands, open(of)):
            if 'DEAD' in line: continue
            a, b = line.split(':'); f = a.split(); plain = [int(x) for x in b.split()]
            q, ic = stats(plain)
            rows.append({'key': c[:4], 'pref_lm': c[5], 'full_lm': int(f[4]) / 1000 / int(f[5]), 'quad': q, 'ioc': ic,
                         'plain': plain})
        ndead = len(cands) - len(rows)
        if not rows:
            res['modes'][m] = {'n': 0, 'ndead': ndead, 'best': {'pref_lm': max(c[5] for c in cands), 'full_lm': float('nan'), 'quad': float('nan'), 'ioc': float('nan')}, 'hdr': d['hdr'], 'top': []}
            continue
        best = {k: max(r[k] for r in rows) for k in ('pref_lm', 'full_lm', 'quad', 'ioc')}
        best['pref_lm'] = max(c[5] for c in cands)
        top = sorted(rows, key=lambda r: -r['full_lm'])[:5]
        res['modes'][m] = {'n': len(rows), 'ndead': ndead, 'best': best, 'hdr': d['hdr'],
                           'top': [{'key': r['key'], 'base': Ameta[r['key'][1]], 'g': Gmeta[r['key'][2]],
                                    'sigma': Ameta[r['key'][3]] if r['key'][3] >= 0 else '-',
                                    'pref_lm': r['pref_lm'], 'full_lm': r['full_lm'], 'quad': r['quad'], 'ioc': r['ioc'],
                                    'text': tr(r['plain'][:120])} for r in top]}
    json.dump(res, open(OUT + '/runs/%s_an.json' % run, 'w'), indent=1)
    return res

if __name__ == '__main__':
    for run in sys.argv[1:]:
        r = analyze(run)
        for m, d in r['modes'].items():
            if d is None or not d['top']: print(run, 'mode', m, 'no full decryptions', d and d['best']); continue
            t = d['top'][0]
            print('%s mode %d n=%d best pref_lm %.3f full_lm %.3f quad %.3f ioc %.3f | top: %s / %s / %s : %s' % (
                run, m, d['n'], d['best']['pref_lm'], d['best']['full_lm'], d['best']['quad'], d['best']['ioc'],
                t['base'], t['g'], t['sigma'], t['text'][:80]))
