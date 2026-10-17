import glob, re, collections, numpy as np
rows = collections.OrderedDict()
for f in sorted(glob.glob('runs/*.log')):
    n = f[5:-4]
    if n.startswith('walk') or n.startswith('real'): continue
    rung = n.rsplit('_', 1)[0]
    rs = [l for l in open(f) if l.startswith('RESTART')]
    tr = [l for l in open(f) if l.startswith('TRUTH')][0]
    tacc = float(tr.split()[4])
    accs = [float(re.search(r'acc (\S+)', l).group(1)) for l in rs]
    mvs = [float(re.search(r'moves/s (\S+)', l).group(1)) for l in rs]
    secs = [float(re.search(r'secs (\S+)', l).group(1)) for l in rs]
    r = rows.setdefault(rung, dict(plants=0, solved=0, rs=0, rsok=0, acc=[], tacc=[], mv=[], secs=[]))
    r['plants'] += 1; r['rs'] += len(accs); ok = [a > 0.95 for a in accs]; r['rsok'] += sum(ok); r['solved'] += any(ok)
    r['acc'].append(max(accs)); r['tacc'].append(tacc); r['mv'] += mvs; r['secs'] += secs
print('| rung | plants solved | restarts solved | best acc (median) | true-key decode acc | moves/s | s/restart |')
print('|---|---|---|---|---|---|---|')
for k, r in rows.items():
    print('| %s | %d/%d | %d/%d | %.4f | %.4f | %s | %.1f |' % (k, r['solved'], r['plants'], r['rsok'], r['rs'], np.median(r['acc']),
          np.median(r['tacc']), ('%.0f' % np.median(r['mv'])) if np.median(r['mv']) > 0 else 'n/a', np.median(r['secs'])))
