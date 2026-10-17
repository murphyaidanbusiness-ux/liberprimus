import sys, collections, numpy as np
sys.path.insert(0,'.')
from report_hits import *
from aggregate import load
allt=[]; nullmax={}
for F in (0,1):
    (rc,rt),nulls=load(F)
    for h in rt: h['F']=F
    allt+=[h for h in rt if h['kind']=='TOPZ']
    for key in rc: nullmax[(F,)+key]=(max(n[key][1] for n in nulls if key in n), np.mean([n[key][1] for n in nulls if key in n]), len(nulls))
z=uniq(allt); z.sort(key=lambda h:-h['Z'])
out=['| # | F | model | class | al | crib | pos (page+offset) | L | W | Z | cell null max / mean | key fragment (best shift/orient) |','|---|---|---|---|---|---|---|---|---|---|---|---|']
for i,h in enumerate(z[:50]):
    cb,ks=show(h); nm=nullmax[(h['F'],h['mt'],h['cls'],h['al'])]
    out.append('| %d | %d | %s | %s | %s | %s | %s | %d | %d | %.2f | %.2f / %.2f | %s |'%(i+1,h['F'],MT[h['mt']],CLS[h['cls']].split()[0],'y' if h['al'] else 'n',' '.join(cb['words'])[:60],where(h['pos']),h['L'],h['W'],h['Z'],nm[0],nm[1],ks))
top=z[:50]
out.append('\nDistribution of the 50: model %s; class %s; aligned %s; F-variant %s; L median %d (range %d-%d); distinct pages %d; hits exceeding their own cell null max: %d; exceeding null mean+3sd-equivalent: n/a'%(
 dict(collections.Counter(MT[h['mt']] for h in top)),dict(collections.Counter(CLS[h['cls']].split()[0] for h in top)),dict(collections.Counter(h['al'] for h in top)),dict(collections.Counter(h['F'] for h in top)),int(np.median([h['L'] for h in top])),min(h['L'] for h in top),max(h['L'] for h in top),len(set(int(pg[h['pos']]) for h in top)),sum(1 for h in top if h['Z']>nullmax[(h['F'],h['mt'],h['cls'],h['al'])][0])))
# top by margin over cell null mean in sd units is not available per-hit; also count hits exceeding null max in any cell among all tops
over=[h for h in z if h['Z']>nullmax[(h['F'],h['mt'],h['cls'],h['al'])][0]]
out.append('Among all %d listed real hits (top-100/thread/model lists), those exceeding their own cell\'s null max (over 50 or 20 shuffles): %d'%(len(z),len(over)))
for h in over[:10]:
    cb,ks=show(h); out.append('  OVER: F%d %s %s %s Z=%.2f null max %.2f %s'%(h['F'],MT[h['mt']],' '.join(cb['words']),where(h['pos']),h['Z'],nullmax[(h['F'],h['mt'],h['cls'],h['al'])][0],ks))
open('top50.md','w').write('\n'.join(out)); print('\n'.join(out[-14:]))
