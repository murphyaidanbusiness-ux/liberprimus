import numpy as np
import eng
from eng import Data, Struct
S=eng.S
MOBY=S+'/dl/dukotah/liber-primus/data/keys/armada18/melville_moby_dick.txt'
_real=None
def real():
    global _real
    if _real is None:
        st,c=eng.real_struct(); _real=(st,c)
    return _real
def page_sizes():
    st,c=real(); return np.bincount(st.page)
def synth_plain(start=5000, path=MOBY, total=12956):
    words=eng.english_plain(path,total+50,start=start)
    # truncate to exactly total runes
    out=[];t=0
    for w in words:
        if t+len(w)>=total:
            w=w[:total-t]
            if w: out.append(w)
            t=total; break
        out.append(w); t+=len(w)
    assert t==total,t
    p=np.array([r for w in out for r in w],dtype=np.int64)
    st=eng.struct_from_words(out,list(page_sizes()))
    return out,p,st
def dummy_data(p,st):
    """Data whose zero-increment pattern equals the plaintext EA pattern (so idx arrays are right)"""
    D=np.where(p[1:]==28,0,1); c=np.concatenate([[0],np.cumsum(D)])%29
    return Data(c,st)
def keys_for_spec(sp,m,o):
    K=sp['K'].astype(np.int64); L=len(K); idx=sp['idx'].astype(np.int64)
    j=idx+o
    valid=idx>=0
    if sp['cyc']: j=np.mod(j,L)
    else: valid&=(j>=0)&(j<L); j=np.clip(j,0,L-1)
    k=K[j]
    if sp['rm']:
        jb=o-1
        if sp['cyc']: jb%=L
        base=K[jb] if 0<=jb<L else 0
        k=np.mod(k-base,sp['rm'])
    k=np.where(valid,k,0)
    return k
def encrypt_with_spec(sp,p,o,rng):
    """returns cipher c (len n) planting spec sp at offset o; plaintext p aligned to runes (p[0] unused)"""
    form=sp['form']; n=len(p)
    k=keys_for_spec(sp,n-1,o)
    pp=p[1:]
    if form in (0,1):
        sigma=eng.rand_sigma(rng,False)
        k28=k%28
        D=1+((sigma[pp]+k28)%28) if form==0 else 1+((sigma[pp]-k28)%28)
    elif form in (2,3):
        sigma=eng.rand_sigma(rng,True)
        kk=np.where(k%29==0,1,k%29)
        inv=np.array([0]+[pow(a,-1,29) for a in range(1,29)])
        D=(sigma[pp]*kk)%29 if form==2 else (sigma[pp]*inv[kk])%29
    D=np.where(pp==28,0,D)
    c=np.zeros(n,dtype=np.int64); c[0]=11; c[1:]=(11+np.cumsum(D))%29
    return c
def encrypt_raw(sp,p,o,rng):
    k=keys_for_spec(sp,len(p)-1,o); n=len(p)
    sgn=1 if sp['form']==4 else -1   # form4 decodes c-k => c=p+k
    c=p.copy(); c[1:]=(p[1:]+(1 if sp['form']==4 else -1)*k)%29
    return c
