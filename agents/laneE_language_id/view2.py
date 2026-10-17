import pickle, numpy as np, collections
d=pickle.load(open('results_main.pkl','rb')); R=d['R']
from variants import VARIANTS
big={k for k,r in R.items() if r['nw']>=30000 and r['valid']}
by=collections.defaultdict(list)
for (n,v),r in R.items():
    if v=='natural' or (n,v) not in big: continue
    by[v].append((r['js'][:2].sum(),r['js'].sum(),n,r))
print('%-28s %3s | %-9s %-9s | best corpus (JS_A+B) | JS A,B,C,D,E'%('variant','n','medA+B','med all'))
for lab,*_ in VARIANTS:
    L=sorted(by[lab],key=lambda x:x[0])
    print('%-28s %3d | %.4f   %.4f   | %-30s %.4f | %s'%(lab,len(L),np.median([x[0] for x in L]),np.median([x[1] for x in L]),L[0][2][:30],L[0][0],' '.join('%.4f'%x for x in L[0][3]['js'])))
