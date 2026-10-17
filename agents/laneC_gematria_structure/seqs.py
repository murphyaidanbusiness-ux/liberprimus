import numpy as np, pickle, math
import eng
from eng import PRIMES, TR
P=pickle.load(open(eng.HERE+'/solved.pkl','rb'))
def totient(n):
    r=n;m=n;p=2
    while p*p<=m:
        if m%p==0:
            while m%p==0: m//=p
            r-=r//p
        p+=1
    if m>1: r-=r//m
    return r
def sieve(N):
    s=np.ones(N+1,bool); s[:2]=False
    for i in range(2,int(N**.5)+1):
        if s[i]: s[i*i::i]=False
    return s
SV=sieve(200000); PI=np.cumsum(SV)  # prime counting
PLIST=np.nonzero(SV)[0]
def solved_words(which):
    out=[]
    for p in P:
        out+= p['pw'] if which=='PT' else p['cw']
    return out
def seq_sets():
    """returns dict name -> dict(arr=int64 array, dom='L'|'W', cum=bool, src)"""
    S={}
    for src in ('PT','CT'):
        W=solved_words(src)
        runes=np.array([r for w in W for r in w],dtype=np.int64)
        pv=PRIMES[runes]
        S[f'{src}.L.prime']=dict(arr=pv,dom='L',cum=False)
        S[f'{src}.L.totient']=dict(arr=pv-1,dom='L',cum=False)
        S[f'{src}.L.index']=dict(arr=runes,dom='L',cum=False)
        S[f'{src}.L.cumprime']=dict(arr=pv,dom='L',cum=True)
        S[f'{src}.L.cumindex']=dict(arr=runes,dom='L',cum=True)
        ws=np.array([PRIMES[w].sum() for w in W],dtype=np.int64)
        S[f'{src}.W.sum']=dict(arr=ws,dom='W',cum=False,words=W)
        S[f'{src}.W.totient']=dict(arr=np.array([totient(int(x)) for x in ws]),dom='W',cum=False,words=W)
        S[f'{src}.W.pi']=dict(arr=PI[ws].astype(np.int64),dom='W',cum=False,words=W)   # prime-counting index
        S[f'{src}.W.primeidx']=dict(arr=PRIMES[ws%29],dom='W',cum=False,words=W)       # prime of rune index (sum mod 29)
        S[f'{src}.W.idxsum']=dict(arr=np.array([sum(w) for w in W]),dom='W',cum=False,words=W)
        S[f'{src}.W.len']=dict(arr=np.array([len(w) for w in W]),dom='W',cum=False,words=W)
        S[f'{src}.W.cumsum']=dict(arr=ws,dom='W',cum=True,words=W)
        S[f'{src}.W.cumtot']=dict(arr=ws,dom='W',cum=True,words=W,post='tot')  # totient of running total: handled (cum then totient)
        S[f'{src}.W.first']=dict(arr=np.array([PRIMES[w[0]] for w in W]),dom='W',cum=False,words=W)
        S[f'{src}.W.last']=dict(arr=np.array([PRIMES[w[-1]] for w in W]),dom='W',cum=False,words=W)
        S[f'{src}.W.sumtot1']=dict(arr=ws-1,dom='W',cum=False,words=W)
    return S
if __name__=='__main__':
    S=seq_sets()
    for k,v in S.items(): print(k,len(v['arr']),v['arr'][:8])
