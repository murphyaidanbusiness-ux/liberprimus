# Reference: Cicada's own SOLVED pages (true rune word lengths) and held-out English, same Markov order test.
import numpy as np, core, json
from order_test import model, gain
import lpdata
P=lpdata.load(); sol=[p for p in P if p['page']>54]
d={}
for p in sol:
    for wid in p['word']: d[wid]=d.get(wid,0)+1
S=np.array(list(d.values())); print('solved pages: %d pages, %d words, mean len %.2f'%(len(sol),len(S),S.mean()))
T,PG,CH=core.target()
rng=np.random.default_rng(2); lib=core.lib()
for v in [('base','none',0),('base','mF',2),('base','drop',3)]:
    M=model(core.variant_stream(v))
    for nm,seq in (('LP solved pages (true runes)',S),('unsolved, first %d words'%len(S),T[:len(S)]),('unsolved all',T)):
        g=gain([seq],M); sh=np.array([gain([rng.permutation(seq)],M) for _ in range(1000)])
        print(core.vname(v),nm,'M1 z=%.2f M2 z=%.2f'%((g[0]-sh[:,0].mean())/sh[:,0].std(),(g[1]-sh[:,1].mean())/sh[:,1].std()))
    hz=[]
    for rep in range(40):
        pool=lib['hold'] if rep%2==0 else lib['ewt']; off=int(rng.integers(0,len(pool)-8000))
        st=core.variant_stream(v,pool[off:off+8000]); st=st[st>0][:len(T)]
        g=gain([st],M); sh=np.array([gain([rng.permutation(st)],M) for _ in range(200)]); hz.append((g[0]-sh[:,0].mean())/sh[:,0].std())
    hz=np.array(hz); print(core.vname(v),'held-out English (%d words, n=40): M1 z mean %.2f sd %.2f min %.2f'%(len(T),hz.mean(),hz.std(),hz.min()))
# bigram independence chi-square (8x8, 8+ pooled) real vs held-out
def chi(seq):
    s=np.minimum(np.asarray(seq),8); tab=np.zeros((9,9)); np.add.at(tab,(s[:-1],s[1:]),1); tab=tab[1:,1:]
    e=tab.sum(1,keepdims=True)*tab.sum(0,keepdims=True)/tab.sum(); return ((tab-e)**2/np.maximum(e,1e-9)).sum()
print('bigram independence chi2 (df=49): unsolved %.1f'%chi(T))
for v in [('base','mF',2),('base','drop',3)]:
    cs=[]
    for rep in range(20):
        pool=lib['hold'] if rep%2==0 else lib['ewt']; off=int(rng.integers(0,len(pool)-8000))
        st=core.variant_stream(v,pool[off:off+8000]); st=st[st>0][:len(T)]; cs.append(chi(st))
    print(core.vname(v),'held-out English chi2 mean %.1f min %.1f max %.1f'%(np.mean(cs),np.min(cs),np.max(cs)))
print('solved pages chi2 (n=%d) %.1f; unsolved first %d words %.1f'%(len(S),chi(S),len(S),chi(T[:len(S)])))
