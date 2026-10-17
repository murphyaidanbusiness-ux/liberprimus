import pickle, numpy as np, math, collections
d=pickle.load(open('results_main.pkl','rb')); R=d['R']; uc=d['uc']
def sf10(x): return math.exp(-x/2)*sum((x/2)**k/math.factorial(k) for k in range(5))
O=uc[0].astype(float); N=O.sum()
rows=[]
for k,r in R.items():
    if r['nw']<30000: continue
    q=r['gc'][0]/r['gc'][0].sum(); E=N*q
    E=np.maximum(E,1e-9)
    chi=((O-E)**2/E).sum(); rows.append((chi,sf10(chi),k))
rows.sort(key=lambda x:x[0])
out=[]
def P(s): print(s); out.append(s)
P('chi-square GOF of the unsolved 11-bin word-length histogram (N=2896) against each candidate length distribution, df=10 (critical 18.3 at p=0.05)')
P('candidates with >=30k words: %d; not rejected at p>0.05: %d'%(len(rows),sum(1 for c,p,k in rows if p>0.05)))
P('not-rejected by variant: %s'%dict(collections.Counter(k[1] for c,p,k in rows if p>0.05)))
P('natural (unmodified) corpora not rejected: %s'%[(k[0],round(c,1),round(p,3)) for c,p,k in rows if p>0.05 and k[1]=='natural'])
P('best 20: '+'; '.join('%s [%s] chi2=%.1f p=%.2f'%(k[0],k[1],c,p) for c,p,k in rows[:20]))
for nm in ['Dutch: bible-corpus','Danish: bible-corpus','Swedish: bible-corpus','Norwegian: bible-corpus','Icelandic: IcePaHC (hist.)','Old Norse: sagas (Perseus/CLTK)','German: Faust','Latin: PROIEL treebank','French: bible-corpus','English: EWT (web)','Moby Dick','Austen Emma']:
    r=[x for x in rows if x[2]==(nm,'natural')]
    if r: P('  natural %-34s chi2=%.1f p=%.2g'%(nm,r[0][0],r[0][1]))
P('| variant (English corpora, >=30k words) | n | not rejected (p>0.05) | median chi2 |'); P('|---|---|---|---|')
for v in ['base (Cicada rules)','-THE','-THE/OF','-THE/OF/TO','-THE/OF/TO/AND','-THE/A/AN','-THE/OF/TO/A','-THE/OF/TO/AND/A/IN','letters (no digraphs)','letters -THE/OF/TO','TH-only merged','TH-only -THE/OF/TO','archaic (thou/thee/-eth)','archaic -THE/OF/TO','-all function words']:
    x=[(c,p) for c,p,k in rows if k[1]==v and R[k]['lang']=='en']
    if x: P('| %s | %d | %d | %.1f |'%(v,len(x),sum(1 for c,p in x if p>0.05),np.median([c for c,p in x])))
open('chiA.md','w').write('\n'.join(out))
