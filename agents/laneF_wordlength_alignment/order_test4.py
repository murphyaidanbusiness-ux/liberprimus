# Model-free bigram-independence test (8x8 length table, permutation null) for LP1 solved vs unsolved; and
# effect of random F-interrupter-like insertions (+1 rune) on held-out English order structure.
import pickle, numpy as np, core
from order_test import model, gain
d=pickle.load(open(core.S+'/agents/laneC_gematria_structure/solved.pkl','rb'))
S=np.array([len(w) for p in d for w in p['cw']]); T,PG,CH=core.target(); rng=np.random.default_rng(4); lib=core.lib()
def chi(seq,K=7):
    s=np.minimum(np.asarray(seq),K); tab=np.zeros((K+1,K+1)); np.add.at(tab,(s[:-1],s[1:]),1); tab=tab[1:,1:]
    e=tab.sum(1,keepdims=True)*tab.sum(0,keepdims=True)/tab.sum(); return ((tab-e)**2/np.maximum(e,1e-9)).sum()
for nm,seq in [('LP1 solved (695)',S)]+[('unsolved block %d (695)'%b,T[b*695:(b+1)*695]) for b in range(4)]+[('unsolved all (2896)',T)]:
    c=chi(seq); null=np.array([chi(rng.permutation(seq)) for _ in range(2000)])
    print('%-26s chi2=%.1f  perm-null %.1f±%.1f  z=%+.2f  p=%.4f'%(nm,c,null.mean(),null.std(),(c-null.mean())/null.std(),(null>=c).mean()))
M=model(core.variant_stream(('base','drop',3)))
for rate in (0.0,0.035,0.07):
    zs=[]
    for rep in range(20):
        pool=lib['hold'] if rep%2==0 else lib['ewt']; off=int(rng.integers(0,len(pool)-8000))
        st=core.variant_stream(('base','drop',3),pool[off:off+8000]).astype(int); st=st[st>0][:len(T)]
        st=st+rng.binomial(st,rate)   # each rune slot may get an inserted interrupter rune
        g=gain([st],M); sh=np.array([gain([rng.permutation(st)],M) for _ in range(200)]); zs.append((g[0]-sh[:,0].mean())/sh[:,0].std())
    print('held-out English drop3, insertion rate %.3f per rune: M1 z mean %.2f sd %.2f min %.2f'%(rate,np.mean(zs),np.std(zs),np.min(zs)))
