"""Family (e): plaintext-autokey by numbers in the chain model, seeds brute-forced."""
import ctypes, numpy as np
import eng, seqs
from eng import PRIMES
lib=ctypes.CDLL(eng.HERE+'/libauto.so')
lib.best_seed.argtypes=[ctypes.c_void_p]*2+[ctypes.c_int]*4+[ctypes.c_void_p]*2+[ctypes.c_int]*3+[ctypes.c_void_p]*3
lib.decode_out.argtypes=[ctypes.c_void_p]*2+[ctypes.c_int]*4+[ctypes.c_void_p]*2+[ctypes.c_int]*3+[ctypes.c_long,ctypes.c_void_p]
HMAX=812000
def _phi_table(N):
    phi=np.arange(N+1,dtype=np.int64)
    for p in range(2,N+1):
        if phi[p]==p:
            phi[p::p]-=phi[p::p]//p
    return phi
_PHI=None; _PI=None
def tables():
    global _PHI,_PI
    if _PHI is None:
        _PHI=_phi_table(HMAX)
        sv=np.ones(HMAX+1,bool); sv[:2]=False
        for i in range(2,int(HMAX**.5)+1):
            if sv[i]: sv[i*i::i]=False
        _PI=np.cumsum(sv)
    x=np.arange(HMAX)
    H={'sum%28':x%28,'sum%29':x%29,'phi%28':_PHI[:HMAX]%28,'phi%29':_PHI[:HMAX]%29,'pi%28':_PI[:HMAX]%28,'pi%29':_PI[:HMAX]%29}
    G={'prime%28':PRIMES%28,'prime%29':PRIMES%29,'(prime-1)%28':(PRIMES-1)%28,'(prime-1)%29':(PRIMES-1)%29,'index':np.arange(29),'index+1':np.arange(29)+1}
    return {k:v.astype(np.int32) for k,v in G.items()},{k:v.astype(np.int32) for k,v in H.items()}
G,H=tables()
def _arr(a,dt): return np.ascontiguousarray(a,dtype=dt)
def segs_for(d,mode):
    """segment boundaries over D positions"""
    if mode=='cont': return [(0,d.m)]
    pg=d.page; b=[0]+[i for i in range(1,d.m) if pg[i]!=pg[i-1]]+[d.m]
    return list(zip(b[:-1],b[1:]))
def wstart(d):
    w=d.word; ws=np.zeros(d.m,dtype=np.uint8); ws[1:]=(w[1:]!=w[:-1]); ws[0]=1; return ws
def run_variant(d, segs, mode, lag, table, sgn, mp, form):
    D=_arr(d.D,np.uint8); WS=_arr(wstart(d),np.uint8)
    gt=_arr(table,np.int32)
    tot_z=0.0; n_used=0; zs=[]; ioc_all=[]; seeds=[]
    for a,b in segs:
        ioc=ctypes.c_double(); sd=ctypes.c_long(); nv=ctypes.c_int()
        if mode==0: lib.best_seed(D.ctypes.data,WS.ctypes.data,a,b,0,lag,gt.ctypes.data,gt.ctypes.data,sgn,mp,form,ctypes.byref(ioc),ctypes.byref(sd),ctypes.byref(nv))
        else: lib.best_seed(D.ctypes.data,WS.ctypes.data,a,b,mode,0,gt.ctypes.data,gt.ctypes.data,sgn,mp,form,ctypes.byref(ioc),ctypes.byref(sd),ctypes.byref(nv))
        if nv.value<30: continue
        z=(ioc.value-1.0233)/(np.sqrt(2*28)/nv.value*29/28)
        zs.append(z); ioc_all.append((ioc.value,nv.value)); seeds.append(sd.value)
    if not zs: return -99.0,-99.0,[],[]
    return float(np.mean(zs)), float(np.max(zs)), ioc_all, seeds
def variants(lite=False):
    """yield (label, mode, lag, table_name, table, sgn, map, form)"""
    for lag in (1,2,3):
        gn=list(G) if lag<3 else ['prime%28','prime%29','index']
        for tn in gn:
            for sgn in (1,-1):
                for mp in (0,1):
                    for form in ((0,1) if lag<3 else (0,)):
                        yield (f'LET lag{lag} g={tn} s={sgn:+d} map{mp} f{form}',0,lag,tn,G[tn],sgn,mp,form)
    for tn in H:
        for sgn in (1,-1):
            for mp in (0,1):
                for form in (0,1):
                    yield (f'WORDSUM prev-word h={tn} s={sgn:+d} map{mp} f{form}',1,0,tn,H[tn],sgn,mp,form)
                    yield (f'CUMSUM running-total h={tn} s={sgn:+d} map{mp} f{form}',2,0,tn,H[tn],sgn,mp,form)
def run_all(d, restart_modes=('cont','page'), only=None):
    res={}
    segc={m:segs_for(d,m) for m in restart_modes}
    for (lab,mode,lag,tn,tab,sgn,mp,form) in variants():
        if only and not any(o in lab for o in only): continue
        for rm in restart_modes:
            mz,xz,iocs,seeds=run_variant(d,segc[rm],mode,lag,tab,sgn,mp,form)
            res[f'{lab} | {rm}']=(mz,xz,max(i for i,_ in iocs) if iocs else 0)
    return res
if __name__=='__main__':
    import time
    st,c=eng.real_struct(); d=eng.Data(c,st)
    t=time.time(); r=run_all(d,only=['lag1']); print(time.time()-t, len(r))
    for k,v in sorted(r.items(),key=lambda kv:-kv[1][0])[:5]: print(k,v)
