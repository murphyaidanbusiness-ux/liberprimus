"""Model-free exclusion of 'key = any function of observable V' for the chain model:
if k_i = g(V_i) and D_i = 1+sigma(p_i)+k_i then D | V=v is a shifted English letter distribution => pooled within-group coincidence ~0.065 vs 1/28=0.0357."""
import numpy as np
import eng
from eng import PRIMES, condcoinc

def obs(d, which=None):
    c=d.c; n=d.n; m=d.m; st=d.st
    i=np.arange(1,n)       # rune index for D position
    def lag(a,l):          # a[i-l], -1 if out of range
        r=np.full(m,-1,dtype=np.int64); idx=i-l; ok=idx>=0; r[ok]=a[idx[ok]]; return r
    def lead(a,l):
        r=np.full(m,-1,dtype=np.int64); idx=i+l; ok=idx<n; r[ok]=a[idx[ok]]; return r
    O={}
    c1=lag(c,1); c2=lag(c,2); c3=lag(c,3)
    O['c[i-1]']=c1
    O['c[i-2]']=c2
    O['(c[i-1],c[i-2])']=np.where((c1>=0)&(c2>=0),c1*29+c2,-1)
    O['(c[i-1..i-3])']=np.where((c1>=0)&(c2>=0)&(c3>=0),(c1*29+c2)*29+c3,-1)
    Dfull=np.concatenate([[0],d.D.astype(np.int64)])
    D1=lag(Dfull,1); D2=lag(Dfull,2)
    O['D[i-1]']=D1
    O['(D[i-1],D[i-2])']=np.where((D1>=0)&(D2>=0),D1*29+D2,-1)
    O['c[i+1] (non-causal)']=lead(c,1)
    # word structure
    w=st.word; nw=d.nw
    pv=PRIMES[c]
    wsum=d.wsum
    prevw=w[1:]-1
    O['prev word cipher-sum (exact)']=np.where(prevw>=0,wsum[np.maximum(prevw,0)],-1)
    O['prev word cipher-sum mod 28']=np.where(prevw>=0,wsum[np.maximum(prevw,0)]%28,-1)
    O['prev word cipher-sum mod 29']=np.where(prevw>=0,wsum[np.maximum(prevw,0)]%29,-1)
    O['prev word length']=np.where(prevw>=0,d.wlen_all[np.maximum(prevw,0)],-1)
    O['(prev word len, pos in word)']=np.where(prevw>=0,d.wlen_all[np.maximum(prevw,0)]*64+d.pos_word,-1)
    O['pos in word']=d.pos_word
    O['(pos in word, word length)']=d.pos_word*64+d.wlen
    O['current word cipher-sum (exact; includes c[i])']=wsum[w[1:]]
    O['current word cipher-sum mod 28']=wsum[w[1:]]%28
    O['current word cipher-sum mod 29']=wsum[w[1:]]%29
    cum=np.cumsum(pv)
    O['cum prime sum thru i-1 mod 28']=(cum[i-1])%28
    O['cum prime sum thru i-1 mod 29']=(cum[i-1])%29
    O['cum prime sum thru i-1 mod 58']=(cum[i-1])%58
    cumi=np.cumsum(c)
    O['cum rune-index sum thru i-1 mod 28']=cumi[i-1]%28
    O['cum rune-index sum thru i-1 mod 29']=cumi[i-1]%29
    # partial word sum so far (runes of the current word before c[i])
    cw=np.cumsum(pv)
    start=np.zeros(nw,dtype=np.int64); first_pos=np.zeros(nw,dtype=np.int64)
    for k in range(n-1,-1,-1): first_pos[w[k]]=k
    base=np.where(first_pos>0,cw[np.maximum(first_pos-1,0)],0)
    part=cw[i-1]-base[w[1:]]    # sum of primes of runes in the word strictly before i (0 if first)
    O['partial word sum before i mod 28']=part%28
    O['partial word sum before i mod 29']=part%29
    O['partial word sum before i (exact)']=part
    O['page']=d.page
    O['line']=d.line
    O['word index in page']=d.wip
    O['word index global (exact)']=d.word
    O['(prev word sum mod 29, pos in word)']=np.where(prevw>=0,(wsum[np.maximum(prevw,0)]%29)*64+d.pos_word,-1)
    return O

def stats(d):
    O=obs(d); X=d.D
    out={}
    for k,v in O.items():
        v=np.where(v>=0,v,-1)
        # compress ids
        ok=v>=0
        u,inv=np.unique(v[ok],return_inverse=True)
        vv=np.full(len(v),-1,dtype=np.int64); vv[ok]=inv
        rate,pairs=condcoinc(X,vv)
        out[k]=(rate,pairs,len(u))
    return out
if __name__=='__main__':
    import sys
    st,c=eng.real_struct(); d=eng.Data(c,st)
    real=stats(d)
    rng=np.random.default_rng(11)
    nul={k:[] for k in real}
    for t in range(40):
        dd=eng.shuffle_data(d,rng); s=stats(dd)
        for k in s: nul[k].append(s[k][0])
    print('%-52s %7s %9s %7s | %8s %8s %7s'%('observable V','groups','pairs','rate','null mu','null sd','z'))
    rows=[]
    for k,(rate,pairs,ng) in real.items():
        mu=np.mean(nul[k]); sd=np.std(nul[k])
        rows.append((k,ng,pairs,rate,mu,sd,(rate-mu)/sd))
        print('%-52s %7d %9.0f %7.5f | %8.5f %8.5f %7.2f'%(k,ng,pairs,rate,mu,sd,(rate-mu)/sd))
    import pickle; pickle.dump(rows,open('cond_real.pkl','wb'))
