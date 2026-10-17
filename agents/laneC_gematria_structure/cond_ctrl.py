import sys; sys.path.insert(0,'.')
import numpy as np, eng, ctrl, condtest
from eng import PRIMES
rng=np.random.default_rng(3)
words,p,st=ctrl.synth_plain(start=20000)
n=len(p)
sigma=eng.rand_sigma(rng,False)
def enc(Vfun,ngroups):
    g=rng.integers(0,28,size=ngroups+1)
    c=np.zeros(n,dtype=np.int64); c[0]=11
    cum=np.zeros(n,dtype=np.int64); cum[0]=PRIMES[11]
    wsum=np.zeros(st.word.max()+2,dtype=np.int64); wsum[st.word[0]]=PRIMES[11]
    pos=np.zeros(n,dtype=np.int64)
    for r in range(1,n):
        pos[r]=pos[r-1]+1 if st.word[r]==st.word[r-1] else 0
    partial=0
    for r in range(1,n):
        if st.word[r]!=st.word[r-1]: partial=0
        V=Vfun(r,c,cum,wsum,pos,partial)
        k=g[V] if V>=0 else 0
        D=0 if p[r]==28 else 1+((sigma[p[r]]+k)%28)
        c[r]=(c[r-1]+D)%29
        cum[r]=cum[r-1]+PRIMES[c[r]]; wsum[st.word[r]]+=PRIMES[c[r]]; partial+=PRIMES[c[r]]
    return c
tests={
 'c[i-1]':(lambda r,c,cum,ws,pos,pa: c[r-1],29),
 '(c[i-1],c[i-2])':(lambda r,c,cum,ws,pos,pa: c[r-1]*29+c[r-2] if r>=2 else -1,841),
 'prev word cipher-sum mod 29':(lambda r,c,cum,ws,pos,pa: ws[st.word[r]-1]%29 if st.word[r]>0 else -1,29),
 'cum prime sum thru i-1 mod 28':(lambda r,c,cum,ws,pos,pa: cum[r-1]%28,28),
 'partial word sum before i mod 29':(lambda r,c,cum,ws,pos,pa: pa%29,29),
 'pos in word':(lambda r,c,cum,ws,pos,pa: pos[r],20),
 'page':(lambda r,c,cum,ws,pos,pa: st.page[r],60),
 'prev word cipher-sum (exact)':(lambda r,c,cum,ws,pos,pa: ws[st.word[r]-1] if st.word[r]>0 else -1,3000),
}
for name,(f,ng) in tests.items():
    c=enc(f,ng)
    d=eng.Data(c,st)
    S=condtest.stats(d)
    # also baseline: what does a non-matching observable show
    print('%-36s planted: rate=%.4f (groups %d)  | unrelated obs "line": %.4f ; "word index global": %.4f'%(name,S[name][0],S[name][2],S['line'][0],S['word index global (exact)'][0]))
