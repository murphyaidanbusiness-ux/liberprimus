import lpdata, math, json
import numpy as np
exec(open('t2_multseq.py').read().split('results=[]')[0])   # reuse SEQ, ioc28, INV, pages setup
del SEQ['n!']
rng=np.random.default_rng(1)
S={name:(np.array([int(v)%29 for v in seq],dtype=np.int64)) for name,seq in SEQ.items()}
SI={name:np.array([INV[v] for v in s]) for name,s in S.items()}
def best_for(D):
    best=(0,None)
    for conv in ('A','B'):
        Dc=D[D!=0] if conv=='B' else D; n=len(Dc)
        for name,s in S.items():
            si=SI[name]
            for off in range(300):
                k=s[off:off+n]; ki=si[off:off+n]
                if len(k)<n: break
                for op,kk in (('div',ki),('mul',k)):
                    x=(Dc*kk)%29; x=x[k!=0]; v=ioc28(x)
                    if v>best[0]: best=(v,(name,conv,off,op))
    return best
pages=[(p['page'],np.array(p['idx'])) for p in U]
print("page n  real_best  null(mean,max of 8 shuffles)  z")
for pg,ix in pages:
    D=(ix[1:]-ix[:-1])%29
    rb=best_for(D)
    nulls=[]
    for _ in range(8):
        Ds=D.copy(); rng.shuffle(Ds); nulls.append(best_for(Ds)[0])
    m=np.mean(nulls); sd=np.std(nulls)+1e-9
    flag='  <<<' if rb[0]>max(nulls)+0.05 else ''
    print("%3s %4d  %.3f %s   %.3f %.3f  z=%.1f%s"%(pg,len(ix),rb[0],rb[1],m,max(nulls),(rb[0]-m)/sd,flag),flush=True)
