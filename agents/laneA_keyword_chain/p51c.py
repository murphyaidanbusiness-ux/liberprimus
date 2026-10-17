# Is page 51's period-7 structure key-like? Hill-climb a free period-L key (quadgram) under each cipher model; compare to shuffles.
import common, ciph, numpy as np, sys
U,C=common.pages(); QT=ciph.QT
pg=[p for p in U if p['page']==51][0]; c0=np.array(pg['idx'])
pos=sum(len(p['idx']) for p in U if p['page']<51); prev=C[pos-1]
TAU=np.full((14,29),255,dtype=np.int64)
for t in range(14):
    for D,v in ciph.TAU[t].items(): TAU[t,D]=v
def quad(o): q=((o[:-3]*29+o[1:-2])*29+o[2:-1])*29+o[3:]; return float(QT[q].mean())
def make_dec(mode,c):
    n=len(c); D=np.diff(np.r_[prev,c])%29
    if mode=='vig': return lambda k: (c-k[np.arange(n)%len(k)])%29
    if mode=='beau': return lambda k: (k[np.arange(n)%len(k)]-c)%29
    if mode in ('skipvig','skipbeau'):
        v=3 if mode=='skipvig' else 4
        return lambda k: np.array(ciph.dec(3,list(c),prev,list(k),v))
    if mode.startswith('tau'):
        t=int(mode[3:]); T=TAU[t][D]
        return lambda k: np.where(T==255,28,(T-k[np.arange(n)%len(k)])%28)
    if mode=='mult':
        return lambda k: np.where(D==0,28,(D*(k[np.arange(n)%len(k)]+1)-1)%29)
LU=np.log(np.fromfile('uni29.f64'))
def uni_init(dec,L,K):
    # per-coset unigram-optimal key (cosets independent under unigram scoring for non-skip models)
    k=np.zeros(L,dtype=np.int64); n=len(dec(k))
    for j in range(L):
        best=None
        for v in range(K):
            kk=np.zeros(L,dtype=np.int64); kk[:]=v; o=dec(kk); s=LU[o[j::L]].sum()
            if best is None or s>best[0]: best=(s,v)
        k[j]=best[1]
    return k
def climb(dec,L,K,rng,restarts=12,passes=3):
    best=(-99,None)
    k0=uni_init(dec,L,K)
    for r in range(restarts):
        if r==0: k=k0.copy()
        else:
            k=best[1].copy(); m=rng.random(L)<0.3; k[m]=rng.integers(K,size=m.sum())
        s=quad(dec(k))
        for p in range(passes):
            for j in range(L):
                for v in range(K):
                    kk=k.copy(); kk[j]=v; ss=quad(dec(kk))
                    if ss>s: s=ss; k=kk
        if s>best[0]: best=(s,k.copy())
    return best
MODES=['vig','beau','mult']+['tau%d'%t for t in range(14)]+['skipvig','skipbeau']
L=int(sys.argv[1]) if len(sys.argv)>1 else 7
rng=np.random.default_rng(L)
NS=12
for mode in MODES:
    K=28 if mode.startswith('tau') or mode=='mult' else 29
    rs=3 if mode.startswith('skip') else 12
    s,k=climb(make_dec(mode,c0),L,K,rng,restarts=rs)
    o=make_dec(mode,c0)(k)
    ns=[]
    for i in range(NS):
        if mode in ('vig','beau','skipvig','skipbeau'): x=rng.permutation(c0)
        else:
            D=np.diff(np.r_[prev,c0])%29; x=(prev+np.cumsum(rng.permutation(D)))%29
        ns.append(climb(make_dec(mode,x),L,K,rng,restarts=rs)[0])
    ns=np.array(ns)
    print('L=%d %-8s real %.3f | null %.3f+-%.3f max %.3f | z=%.2f | key %s | %s'%(L,mode,s,ns.mean(),ns.std(),ns.max(),(s-ns.mean())/ns.std(),list(k),common.tr(o[:60])),flush=True)
