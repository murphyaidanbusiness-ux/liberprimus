"""Real page 0 vs 20 doublet-matched nulls; controls; per-start restart runs. Writes summary_out.txt."""
import json, os, glob
import numpy as np
from common import *
import analyze
out = open(OUT + '/summary_out.txt', 'w')
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); out.write(s + '\n'); out.flush()

def get(run):
    f = OUT + '/runs/%s_an.json' % run
    if not os.path.exists(f): analyze.analyze(run)
    return json.load(open(f))

STATS = ('pref_lm', 'full_lm', 'quad', 'ioc')
MN = {0: 'global clock (Oosterhof)', 1: 'clock reset per word', 2: 'fixed base (no sigma)'}
real = get('full_real_page00')
nulls = [get('full_null_p0_s%02d' % s) for s in range(20) if os.path.exists(OUT + '/runs/full_null_p0_s%02d.txt' % s)]
P('page 0 (262 runes, prefix 151 runes / 34 words), full keyword corner; real vs %d doublet-matched shuffles' % len(nulls))
P(real['hdr'])
for m in (0, 1, 2):
    P('\nmode %d: %s   %s' % (m, MN[m], real['modes'][str(m)]['hdr']))
    P('  %-8s %9s %9s %9s %9s %7s' % ('stat', 'real', 'null mean', 'null sd', 'null max', 'z'))
    for k in STATS:
        r = real['modes'][str(m)]['best'][k]; v = np.array([n['modes'][str(m)]['best'][k] for n in nulls]); v = v[~np.isnan(v)]
        P('  %-8s %9.3f %9.3f %9.3f %9.3f %7.2f  (nulls with a value: %d)' % (k, r, v.mean(), v.std(ddof=1), v.max(), (r - v.mean()) / v.std(ddof=1), len(v)))
    for t in real['modes'][str(m)]['top'][:3]:
        P('  top: base=%s g=%s sigma=%s pref_lm %.3f full_lm %.3f quad %.3f ioc %.3f' % (t['base'], t['g'], t['sigma'], t['pref_lm'], t['full_lm'], t['quad'], t['ioc']))
        P('       ' + t['text'])
for c in ('full_plant1', 'full_plant2'):
    if os.path.exists(OUT + '/runs/%s.txt' % c):
        r = get(c); d = json.load(open(OUT + '/texts/%s.json' % c.replace('full_', '')))
        P('\ncontrol %s: planted %s' % (c, d['label']))
        for m in ('0',):
            t = r['modes'][m]['top'][0]
            P('  mode 0 rank-1: base=%s g=%s sigma=%s key=%s pref_lm %.3f full_lm %.3f quad %.3f ioc %.3f' % (t['base'], t['g'], t['sigma'], t['key'], t['pref_lm'], t['full_lm'], t['quad'], t['ioc']))
            P('       ' + t['text'])
            if len(r['modes'][m]['top']) > 1:
                t2 = r['modes'][m]['top'][1]; P('  rank-2: pref_lm %.3f full_lm %.3f quad %.3f' % (t2['pref_lm'], t2['full_lm'], t2['quad']))
starts = sorted(f for f in glob.glob(OUT + '/runs/start_*.txt') + glob.glob(OUT + '/runs/start4_*.txt') if 'placeholder' not in open(f).read() and '_m' not in os.path.basename(f) and 'sec06' not in f)
if starts:
    P('\nper-start restart runs (independent key per start; per mode: best prefix LM/sym / best full-page LM/sym / best full-page quadgram)')
    for f in starts:
        run = os.path.basename(f)[:-4]
        try: r = get(run)
        except Exception as e: P(run, 'ERR', e); continue
        hdr = r['hdr'].split();
        row = []
        for m in ('0', '1', '2'):
            if m not in r['modes']: row.append('not-run'); continue
            d = r['modes'][m]
            row.append('%.3f/%.3f/%.3f' % (d['best']['pref_lm'], d['best']['full_lm'], d['best']['quad']) if d else 'no-survivor')
        sz = ' '.join(hdr[hdr.index('|base|'):hdr.index('|sigma|') + 2]); sv = hdr[hdr.index('survivors') + 1]
        P('  %-24s %s surv %s  %s' % (run, sz, sv, '  '.join(row)))
