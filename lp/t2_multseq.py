import lpdata, math, random, json
import numpy as np
from collections import Counter
U,C,h=lpdata.unsolved()
INV=[0]+[pow(a,-1,29) for a in range(1,29)]
def ioc28(x):
    x=x[x!=0]; n=len(x)
    if n<20: return 0
    c=np.bincount(x,minlength=29)[1:]; return (c*(c-1)).sum()/(n*(n-1))*28
# sequences (length >= 3000+400)
M=4000
def primes(n):
    ps=[];k=2
    while len(ps)<n:
        if all(k%p for p in ps if p*p<=k): ps.append(k)
        k+=1
    return ps
PR=primes(M+10)
def tot(n):
    r=n;m=n;p=2
    while p*p<=m:
        if m%p==0:
            while m%p==0: m//=p
            r-=r//p
        p+=1
    if m>1: r-=r//m
    return r
fib=[1,1]
while len(fib)<M: fib.append(fib[-1]+fib[-2])
pi_digits=open(lpdata.DL+'/leo/pi.txt').read(); pi_digits=[int(ch) for ch in pi_digits if ch.isdigit()][:M]
SEQ={
 'n':list(range(1,M+1)),'n+1':list(range(2,M+2)),'n0':list(range(0,M)),'prime':PR[:M],'prime-1':[p-1 for p in PR[:M]],'prime+1':[p+1 for p in PR[:M]],
 'n^2':[n*n for n in range(1,M+1)],'tri':[n*(n+1)//2 for n in range(1,M+1)],'fib':fib[:M],'tot(n)':[tot(n) for n in range(1,M+1)],
 'tot(prime)':[p-1 for p in PR[:M]],'2^n':[pow(2,n,29) for n in range(M)],'3^n':[pow(3,n,29) for n in range(M)],'3301n':[3301*n for n in range(1,M+1)],
 'pi':pi_digits,'primegap':[PR[i+1]-PR[i] for i in range(M)],'cumprime':list(np.cumsum(PR[:M])),'n!':[math.factorial(n)%29 for n in range(1,M+1)],
 'tot(tot(n))':[tot(tot(n)) for n in range(2,M+2)],
}
# running keys from solved LP plaintext (Dukotah SOLVED-PAGES translits -> indices), raw and atbash
sp=json.load(open(lpdata.DL+'/dukotah/liber-primus/SOLVED-PAGES.json'))
def tr2idx(s):
    out=[];i=0;T=lpdata.TR
    while i<len(s):
        for L in (2,1):
            if s[i:i+L] in T: out.append(T.index(s[i:i+L])); i+=L; break
        else: i+=1
    return out
solved=[]
for pg in sp['pages']: solved+=tr2idx(pg['plaintext_transliteration'])
print('solved plaintext runes:',len(solved))
SEQ['LPtext+1']=[x+1 for x in solved]+[1]*M; SEQ['LPtext']=[x for x in solved]+[1]*M; SEQ['LPprime']=[lpdata.PRIMES[x] for x in solved]+[1]*M
results=[]
pages=[(p['page'],np.array(p['idx'])) for p in U]
# whole-corpus too
pages.append(('ALL',np.array(C)))
rng=np.random.default_rng(0)
for name,seq in SEQ.items():
    s=np.array([int(v)%29 for v in seq],dtype=np.int64)
    sinv=np.array([INV[v] for v in s])
    best=(0,None)
    for pg,ix in pages:
        D=(ix[1:]-ix[:-1])%29
        for conv in ('A','B'):
            if conv=='B': Dc=D[D!=0]    # doublets don't consume key
            else: Dc=D
            n=len(Dc)
            for off in range(0,300):
                k=s[off:off+n]; ki=sinv[off:off+n]
                if len(k)<n: break
                for op,kk in (('div',ki),('mul',k)):
                    x=(Dc*kk)%29
                    x=x[k!=0]
                    v=ioc28(x)
                    if v>best[0]: best=(v,(pg,conv,off,op))
    results.append((best[0],name,best[1]))
    print('%-12s best IoC28=%.3f %s'%(name,best[0],best[1]),flush=True)
# null: same procedure on random text
print('NULL on random 260-rune pages x 55, same trial count, 3 sequences:')
for name in ('prime','n','fib'):
    s=np.array([int(v)%29 for v in SEQ[name]]); sinv=np.array([INV[v] for v in s]); best=0
    for _ in range(56):
        ix=rng.integers(0,29,260); D=(ix[1:]-ix[:-1])%29
        for conv in ('A','B'):
            Dc=D[D!=0] if conv=='B' else D; n=len(Dc)
            for off in range(300):
                k=s[off:off+n]; ki=sinv[off:off+n]
                for kk in (ki,k):
                    x=(Dc*kk)%29; x=x[k!=0]; best=max(best,ioc28(x))
    print('  %-8s null best IoC28=%.3f'%(name,best))
