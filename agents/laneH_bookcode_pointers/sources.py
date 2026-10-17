import sys, numpy as np
S='.'
sys.path.insert(0,S+'/lp')
import lpdata
P=np.array(lpdata.PRIMES,dtype=np.int64)
def build_sources(idx,starts):
    ends=np.r_[starts[1:],len(idx)]
    wlen=ends-starts
    gsum=np.add.reduceat(P[idx],starts); isum=np.add.reduceat(idx,starts); isum1=isum+wlen
    w29=[]
    for a,b in zip(starts,ends):
        v=0
        for x in idx[a:b]: v=(v*29+int(x))%(2**61-1)
        w29.append(v)
    d={'gsum':gsum,'isum':isum,'isum1':isum1,'wlen':wlen,'w29':np.array(w29,dtype=np.int64),
       'rprime':P[idx],'ridx':idx,'ridx1':idx+1}
    for k in (2,3,4):
        sel=[(a,b) for a,b in zip(starts,ends) if b-a==k]
        d[f'wt{k}_idx1']=np.array([int(x)+1 for a,b in sel for x in idx[a:b]],dtype=np.int64)
        d[f'wt{k}_prime']=np.array([int(P[x]) for a,b in sel for x in idx[a:b]],dtype=np.int64)
    return d
def lp2_raw():
    U,C,sha=lpdata.unsolved()
    assert sha=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
    wid=np.concatenate([np.array(p['word']) for p in U]); idx=np.array(C,dtype=np.int64)
    starts=np.r_[0,np.flatnonzero(np.diff(wid)!=0)+1]
    return idx,starts
def lp2_sources():
    idx,starts=lp2_raw()
    return build_sources(idx,starts),idx,starts
def chain_runes(n,rng,p0=86/12955):
    """chain cipher stand-in: c_i = c_{i-1}+s_i, s_i flat 1..28 except s_i=0 w.p. p0 (matches the observed doublet deficit)"""
    s=rng.integers(1,29,size=n); s[rng.random(n)<p0]=0
    s[0]=rng.integers(0,29)
    return np.cumsum(s)%29
if __name__=='__main__':
    s,idx,st=lp2_sources()
    for k,v in s.items(): print(k,len(v),v.min(),v.max(),v.mean())
    rng=np.random.default_rng(1); c=chain_runes(len(idx),rng); print((c[1:]==c[:-1]).sum())
