"""Plant2 (sigma from LABYRINTHINE:R1, not in the set): decode with the true base/g and the listed alphabets nearest
to the true sigma; shows how the prefix score degrades near a miss."""
import json, subprocess, sys
from common import *
sys.path.insert(0, S + '/dl/dukotah/liber-primus/src'); from lp.score import Quadgram; Q = Quadgram()
A = np.fromfile('A.bin', dtype=np.uint8).reshape(-1, 29); meta = open('A_meta.txt').read().split('\n')
d = json.load(open('texts/plant2.json')); truth = [x for w in d['plain'] for x in w]
sig = np.array(alph_rules(dedup(eng_runes('LABYRINTHINE')))['R1'])
agree = (A == sig).sum(1); order = np.argsort(-agree)[:8]
keys = ''.join('0 %d %d %d\n' % (d['b'], d['g'], i) for i in order)
open('runs/nm_keys.txt', 'w').write(keys)
subprocess.run(['./kwdec', 'texts/plant2.txt', 'runs/nm_keys.txt', 'runs/nm_out.txt', '16'], check=True)
# also the truth itself (sigma not in A): append it temporarily via python decode = plaintext
lines = open('runs/nm_out.txt').read().split('\n')
with open('runs/nearmiss_out.txt', 'w') as f:
    for i, line in zip(order, lines):
        a, b = line.split(':'); fs = a.split(); p = [int(x) for x in b.split()]
        acc = np.mean([x == y for x, y in zip(p, truth)])
        pref = sum(len(w) for w in d['plain'][:34]); accp = np.mean([x == y for x, y in zip(p[:pref], truth[:pref])])
        s = '%-26s agree %2d/29  LM/sym %.3f  quad %.3f  acc(prefix151) %.3f acc(262) %.3f | %s' % (
            meta[i], agree[i], int(fs[4]) / 1000 / int(fs[5]), Q.score_norm(trs(p)), accp, acc, tr(p[:60]))
        print(s); f.write(s + '\n')
