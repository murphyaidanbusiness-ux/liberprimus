import numpy as np, re, math
from qg import T as QT
from texts import views, View

# ---------- primes
def _sieve(n):
    s=np.ones(n+1,bool); s[:2]=False
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=False
    return s
_SV=_sieve(3_000_000)
PR=np.flatnonzero(_SV)                 # PR[k-1] = k-th prime
PI=np.cumsum(_SV)                      # PI[n] = number of primes <= n
def nth_prime(n):
    n=np.asarray(n,dtype=np.int64); ok=(n>=1)&(n<=len(PR)); out=np.where(ok,PR[np.clip(n-1,0,len(PR)-1)],0); return out,ok
def pi_of(n):
    n=np.asarray(n,dtype=np.int64); ok=(n>=2)&(n<len(PI)); out=np.where(ok,PI[np.clip(n,0,len(PI)-1)],0); return out,ok

# ---------- resolution helpers
def top(cnt,a,b,mode):
    x=a-b
    if mode=='mod': return x%cnt, np.ones(len(a),bool)
    v=(x>=0)&(x<cnt); return np.where(v,x,0), v
def sub(startarr,parent,a,b,mode):
    c=startarr[parent+1]-startarr[parent]
    x=a-b
    if mode=='mod':
        v=c>0; return startarr[parent]+np.where(v,x%np.maximum(c,1),0), v
    v=(x>=0)&(x<c)&(c>0); return startarr[parent]+np.where(v,x,0), v

def level_resolve(V,spec,nums,b,mode):
    """nums: list of arrays (one per level in spec). returns (unit_index_at_last_level, valid)"""
    cnt={'P':V.nP,'S':V.nS,'W':V.nW,'L':V.nL}
    idx,valid=top(cnt[spec[0]],nums[0],b,mode)
    prev=spec[0]
    for lev,a in zip(spec[1:],nums[1:]):
        # starts of `lev` units within `prev` units, expressed as arrays over prev units (len nprev+1)
        if prev=='P':
            st={'S':V.ps,'W':V.pw,'L':V.pl}[lev]
        elif prev=='S':
            st={'W':V.sw,'L':V.sl}[lev]
        elif prev=='W':
            st={'L':V.wstart}[lev]
        i2,v2=sub(st,idx,a,b,mode)
        idx=i2; valid=valid&v2; prev=lev
    return idx,valid,prev

SPECS=['PS','PW','PL','SW','SL','WL','PSW','PSL','PWL','SWL','PSWL']

def apply_semantic(V,sem,n,b,mode,minm=20):
    """n: 1-D int array of pointer numbers. returns ('L',letters) or ('W',word_idx) or None"""
    n=np.asarray(n,dtype=np.int64)
    if sem=='L':
        i,v=top(V.nL,n,b,mode); return 'L',V.L[i[v]]
    if sem=='Lp':
        m,ok=nth_prime(n); i,v=top(V.nL,m,b,mode); v=v&ok; return 'L',V.L[i[v]]
    if sem=='Lpi':
        m,ok=pi_of(n); i,v=top(V.nL,m,b,mode); v=v&ok; return 'L',V.L[i[v]]
    if sem=='W':
        i,v=top(V.nW,n,b,mode); return 'W',i[v]
    if sem=='Wp':
        m,ok=nth_prime(n); i,v=top(V.nW,m,b,mode); v=v&ok; return 'W',i[v]
    if sem=='Wpi':
        m,ok=pi_of(n); i,v=top(V.nW,m,b,mode); v=v&ok; return 'W',i[v]
    if sem=='S1':
        i,v=top(V.nS,n,b,mode); return 'L',V.L[V.sl[i[v]]]
    if sem=='Lcum':
        c=np.cumsum(n); return 'L',V.L[c%V.nL]
    if sem=='Wcum':
        c=np.cumsum(n); return 'W',(c%V.nW)
    if sem.startswith('T'):
        spec=sem[1:]; k=len(spec); m=len(n)//k
        if m<minm: return None
        nums=[n[j:m*k:k] for j in range(k)]
        idx,valid,last=level_resolve(V,spec,nums,b,mode)
        idx=idx[valid]
        if last=='L': return 'L',V.L[idx]
        if last=='W': return 'W',idx
        if last=='S': return 'L',V.L[V.sl[idx]]
        if last=='P': return 'L',V.L[V.pl[idx]]
    raise ValueError(sem)

SEMS=['L','Lp','Lpi','W','Wp','Wpi','S1','Lcum','Wcum']+['T'+s for s in SPECS]

# ---------- word-level model (PMI)
class PMI:
    def __init__(self,V_dict):
        from collections import Counter
        cnt=Counter()
        for v in V_dict.values():
            if v.name in ('LP1_solved',): continue
            cnt.update(v.words)
        vocab=[w for w,c in cnt.items() if c>=2]
        self.id={w:i+1 for i,w in enumerate(vocab)}; self.NV=len(vocab)+1
        toks=[]
        for v in V_dict.values():
            if v.name in ('LP1_solved','SR_doyle_semi','SR_withverse','SR_lines','AL_flat','AL_allverses','Mab_lines'): continue
            toks.append(np.array([self.id.get(w,0) for w in v.words],dtype=np.int64))
        N=sum(len(t) for t in toks)
        c1=np.zeros(self.NV); 
        keys=[]
        for t in toks:
            c1+=np.bincount(t,minlength=self.NV); keys.append(t[:-1]*self.NV+t[1:])
        keys=np.concatenate(keys); uk,uc=np.unique(keys,return_counts=True)
        self.uk=uk; self.uc=uc.astype(float); self.c1=c1; self.N=N
        self.p=(c1+1)/(N+self.NV)
    def vid(self,v): return np.array([self.id.get(w,0) for w in v.words],dtype=np.int64)
    def score(self,ids):
        a=ids[:-1]; b=ids[1:]
        k=a*self.NV+b
        pos=np.searchsorted(self.uk,k); pos=np.clip(pos,0,len(self.uk)-1)
        c12=np.where(self.uk[pos]==k,self.uc[pos],0.0)
        p2=self.p[b]
        return float(np.mean(np.log((c12+p2)/((self.c1[a]+1)*p2))))

def ioc26(L):
    if len(L)<2: return float('nan')
    c=np.bincount(L,minlength=26).astype(float); n=len(L)
    return float((c*(c-1)).sum()/(n*(n-1))*26)

def qscore_arr(a):
    if len(a)<30: return float('nan')
    q=((a[:-3]*26+a[1:-2])*26+a[2:-1])*26+a[3:]
    return float(QT[q].mean())

def word_letters(V,idx):
    lens=V.wl[idx]; tot=int(lens.sum())
    starts=np.repeat(V.wstart[idx],lens)
    off=np.arange(tot)-np.repeat(np.cumsum(lens)-lens,lens)
    return V.L[starts+off]

WIN=100
def _winmax(x,w=WIN):
    """max over windows of w consecutive entries of the mean of x"""
    if len(x)<w: return float('nan')
    c=np.cumsum(np.r_[0.0,x]); return float(((c[w:]-c[:-w])/w).max())
def qwin_arr(a):
    if len(a)<WIN+3: return float('nan')
    q=((a[:-3]*26+a[1:-2])*26+a[2:-1])*26+a[3:]
    return _winmax(QT[q])
def pmi_vec(self,ids):
    a=ids[:-1]; b=ids[1:]
    k=a*self.NV+b
    pos=np.searchsorted(self.uk,k); pos=np.clip(pos,0,len(self.uk)-1)
    c12=np.where(self.uk[pos]==k,self.uc[pos],0.0)
    p2=self.p[b]
    return np.log((c12+p2)/((self.c1[a]+1)*p2))
PMI.vec=pmi_vec

def score_output(V,kind,arr,pmi,vid):
    """returns dict of score name -> value"""
    if kind=='L':
        return {'q':qscore_arr(arr),'qwin':qwin_arr(arr)}
    # word indices
    out={}
    nan=float('nan')
    fl=V.L[V.wstart[arr]] if len(arr)>=30 else None
    out['qfirst']=qscore_arr(fl) if len(arr)>=30 else nan
    out['qfirstwin']=qwin_arr(fl) if len(arr)>=30 else nan
    out['qall']=qscore_arr(word_letters(V,arr)) if len(arr)>=30 else nan
    if len(arr)>=30:
        pv=pmi.vec(vid[arr]); out['pmi']=float(pv.mean()); out['pmiwin']=_winmax(pv)
    else: out['pmi']=nan; out['pmiwin']=nan
    return out
