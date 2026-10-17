import lpdata, numpy as np
from collections import Counter
U,C,h=lpdata.unsolved(); C=np.array(C); N=len(C)
word=np.array([w for p in U for w in p['word']])
# position in word (from start) and from end
pos=np.zeros(N,int); wlen=np.zeros(N,int)
starts={}; 
for i,w in enumerate(word): starts.setdefault(w,i)
counts=Counter(word)
for i,w in enumerate(word): pos[i]=i-starts[w]; wlen[i]=counts[w]
rpos=wlen-1-pos
D=np.full(N,-1); D[1:]=(C[1:]-C[:-1])%29
def coinc(X,lag,mask_same):
    a=np.arange(N-lag); m=mask_same(a,a+lag); return np.mean(X[a][m]==X[a+lag][m]), m.sum()
print("A) raw-rune coincidence at lag k, within word vs across word (random 0.0345)")
for lag in range(1,11):
    rw,nw=coinc(C,lag,lambda a,b: word[a]==word[b]); rx,nx=coinc(C,lag,lambda a,b: word[a]!=word[b])
    z=(rw-1/29)/np.sqrt((1/29)*(28/29)/nw)
    print("  lag %2d within %.4f (n=%5d, z=%+.2f)   across %.4f (n=%5d)"%(lag,rw,nw,z,rx,nx))
def coset_ioc(X,key,m,valid):
    tot=cnt=0
    for g in np.unique(key[valid]):
        col=X[valid & (key==g)]; n=len(col)
        if n>1: c=np.bincount(col,minlength=m); tot+=(c*(c-1)).sum()/(n*(n-1))*m; cnt+=1
    return tot/cnt
rng=np.random.default_rng(0)
print("B) coset IoC with cosets = (position in word mod L); raw C (m=29) and increments D (m=28); null = 100 global shuffles of the rune stream")
for L in range(1,13):
    kS=pos%L; kE=rpos%L
    vC=np.ones(N,bool); vD=D>0
    rS=coset_ioc(C,kS,29,vC); rE=coset_ioc(C,kE,29,vC); dS=coset_ioc(np.where(D>0,D-1,0),kS,28,vD); dE=coset_ioc(np.where(D>0,D-1,0),kE,28,vD)
    nl=[]
    for _ in range(100):
        Cs=rng.permutation(C); nl.append(coset_ioc(Cs,kS,29,vC))
    print("  L=%2d  C by start %.4f | C by end %.4f | D by start %.4f | D by end %.4f   null %.4f±%.4f"%(L,rS,rE,dS,dE,np.mean(nl),np.std(nl)))
# C) per-position-in-word unigram IoC (position 0,1,2,... separately, no modulus): is the first rune of words structured?
print("C) IoC of runes at fixed position in word (from start / from end), n in parentheses; random 1.0")
for j in range(0,8):
    a=C[pos==j]; b=C[rpos==j]
    ia=(np.bincount(a,minlength=29)*(np.bincount(a,minlength=29)-1)).sum()/(len(a)*(len(a)-1))*29
    ib=(np.bincount(b,minlength=29)*(np.bincount(b,minlength=29)-1)).sum()/(len(b)*(len(b)-1))*29
    print("  pos %d from start: %.3f (n=%d)   from end: %.3f (n=%d)"%(j,ia,len(a),ib,len(b)))
