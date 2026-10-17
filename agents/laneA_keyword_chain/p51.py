import common, numpy as np, sys
U,C=common.pages()
QT=np.fromfile('quad29.f32',dtype=np.float32); UNI=np.fromfile('uni29.f64'); LU=np.log(UNI)
pg=[p for p in U if p['page']==51][0]; c=np.array(pg['idx'])
pos=sum(len(p['idx']) for p in U if p['page']<51); prev=C[pos-1]
D=np.diff(np.r_[prev,c])%29
print('page 51 n=%d doublets=%d prev=%d'%(len(c),(D[1:]==0).sum(),prev))
def coset_ioc(x,L,m):
    tot=cnt=0
    for j in range(L):
        col=x[j::L]; col=col[col>=0]; n=len(col)
        if n>1:
            h=np.bincount(col,minlength=m); tot+=(h*(h-1)).sum()/(n*(n-1))*m; cnt+=1
    return tot/cnt
def quad(o):
    o=np.asarray(o); q=((o[:-3]*29+o[1:-2])*29+o[2:-1])*29+o[3:]; return QT[q].mean()
def ioc(o):
    h=np.bincount(o,minlength=29); n=len(o); return 29*(h*(h-1)).sum()/(n*(n-1))
# decoders: given stream and period L, choose per-coset key maximising unigram loglik, then 3 rounds of quad coordinate ascent
def solve(x,L,mode,rounds=2):
    # mode 'vig': p=(x-k)%29 over raw;  'beau': p=(k-x)%29 ; 'chainp'/'chainm': x=D (0->EA), p=(D-1 -+ k)%28 ; 'mult': p=D*k-1 mod 29, k in 1..28
    n=len(x)
    def dec(keys):
        k=np.array(keys)[np.arange(n)%L]
        if mode=='vig': return (x-k)%29
        if mode=='beau': return (k-x)%29
        if mode in('chainp','chainm'):
            s=-1 if mode=='chainp' else 1
            return np.where(x==0,28,(x-1+s*k)%28)
        if mode=='mult': return np.where(x==0,28,(x*k-1)%29)
    K=list(range(29)) if mode in('vig','beau') else list(range(28)) if mode.startswith('chain') else list(range(1,29))
    keys=[]
    for j in range(L):
        best=None
        for k in K:
            kk=[0]*L; kk[j]=k
            p=dec([k]*L)[j::L]; s=LU[p].sum()
            if best is None or s>best[0]: best=(s,k)
        keys.append(best[1])
    for r in range(rounds):
        for j in range(L):
            best=None
            for k in K:
                kk=list(keys); kk[j]=k; s=quad(dec(kk))
                if best is None or s>best[0]: best=(s,k)
            keys[j]=best[1]
    o=dec(keys); return quad(o),ioc(o),keys,o
rng=np.random.default_rng(51)
NS=int(sys.argv[1]) if len(sys.argv)>1 else 200
Dm=np.where(D==0,-1,D-1)
print('\n== coset IoC, real vs %d-shuffle null (raw shuffles raw runes; increments shuffle D) =='%NS)
nullR=[rng.permutation(c) for _ in range(NS)]
nullD=[]
for _ in range(NS):
    Dp=rng.permutation(D); nullD.append(Dp)
for L in (7,14,28):
    r=coset_ioc(c,L,29); nr=np.array([coset_ioc(x,L,29) for x in nullR])
    d=coset_ioc(Dm,L,28); nd=np.array([coset_ioc(np.where(x==0,-1,x-1),L,28) for x in nullD])
    print('L=%2d raw %.3f null %.3f+-%.3f max %.3f z=%.2f p=%.3f | incr %.3f null %.3f+-%.3f max %.3f z=%.2f p=%.3f'%(L,r,nr.mean(),nr.std(),nr.max(),(r-nr.mean())/nr.std(),(nr>=r).mean(),
        d,nd.mean(),nd.std(),nd.max(),(d-nd.mean())/nd.std(),(nd>=d).mean()))
# look-elsewhere: max over periods 2..40
Ls=range(2,41)
r=max(coset_ioc(c,L,29) for L in Ls); nr=np.array([max(coset_ioc(x,L,29) for L in Ls) for x in nullR[:NS]])
d=max(coset_ioc(Dm,L,28) for L in Ls); nd=np.array([max(coset_ioc(np.where(x==0,-1,x-1),L,28) for L in Ls) for x in nullD[:NS]])
print('max over L=2..40: raw %.3f null max-dist %.3f+-%.3f max %.3f z=%.2f p=%.3f | incr %.3f null %.3f+-%.3f z=%.2f p=%.3f'%(r,nr.mean(),nr.std(),nr.max(),(r-nr.mean())/nr.std(),(nr>=r).mean(),d,nd.mean(),nd.std(),(d-nd.mean())/nd.std(),(nd>=d).mean()))
print('argmax raw L=',max(Ls,key=lambda L:coset_ioc(c,L,29)),' incr L=',max(Ls,key=lambda L:coset_ioc(Dm,L,28)))
# per-coset detail at L=28 raw
print('\nper-coset raw L=28: column sizes and repeated runes')
for j in range(28):
    col=c[j::28]; h=np.bincount(col,minlength=29); rep=[(common.TR[i],h[i]) for i in range(29) if h[i]>1]
    print(j,len(col),rep)
print('\n== coset-shift solve (key-likeness): real vs null (%d shuffles), quad and IoC of solved text =='%min(NS,40))
NS2=min(NS,40)
for L in (7,14,28):
    for mode,src,nulls in (('vig',c,nullR),('beau',c,nullR),('chainp',D,nullD),('chainm',D,nullD),('mult',D,nullD)):
        q,i,k,o=solve(src,L,mode)
        nq=[];ni=[]
        for x in nulls[:NS2]:
            a,b,_,_=solve(x,L,mode); nq.append(a); ni.append(b)
        nq=np.array(nq); ni=np.array(ni)
        print('L=%2d %-6s real q %.3f ioc %.3f | null q %.3f+-%.3f max %.3f z_q=%.2f | null ioc %.3f+-%.3f max %.3f z_i=%.2f | %s'%(L,mode,q,i,nq.mean(),nq.std(),nq.max(),(q-nq.mean())/nq.std(),ni.mean(),ni.std(),ni.max(),(i-ni.mean())/ni.std(),common.tr(o[:40])))
