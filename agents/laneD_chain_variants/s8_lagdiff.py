"""Null = increments (D) shuffled within page, rebuilt by cumsum: keeps the exact doublet hole. Candidate 1 key-structure test (not covered by prior lanes): periodic keyword on LAG-L difference streams E_i = c_i - c_{i-L}, L=1..4."""
import math, time
from common import *
from sim import *
rng=np.random.default_rng(8)
PMAX=60
def coset_z_page(E):
    n=len(E); best=-9;bp=0
    for P in range(2,min(PMAX,n//4)+1):
        coin=0;pairs=0
        for r in range(P):
            sub=E[r::P]; m=len(sub)
            if m<2: continue
            c=np.bincount(sub,minlength=29); coin+=int((c*(c-1)).sum()//2); pairs+=m*(m-1)//2
        p0=1/29; z=(coin-pairs*p0)/math.sqrt(pairs*p0*(1-p0))
        if z>best: best=z;bp=P
    return best,bp
def stat(pages,L):
    zs=[]
    for p in pages:
        E=(p[L:]-p[:-L])%29
        zs.append(coset_z_page(E)[0])
    return np.array(zs)
def dshuffled_pages(pages,rng):
    out=[]
    for p in pages:
        D=(p[1:]-p[:-1])%29; D=rng.permutation(D); out.append(np.concatenate([[p[0]],(p[0]+np.cumsum(D))%29]))
    return out
t0=time.time()
for L in (1,2,3,4):
    real=stat(PAGES,L); S=real.sum()
    nul=np.array([stat(dshuffled_pages(PAGES,rng),L).sum() for _ in range(40)])
    print('lag-%d differences: sum over pages of best-period z (periods 2..%d): real %.1f ; null %.1f +- %.1f -> z=%.2f ; best single page z=%.1f (page %d)'%(L,PMAX,S,nul.mean(),nul.std(),(S-nul.mean())/nul.std(),real.max(),real.argmax()))
print('time',time.time()-t0)
def enc_lag_keyword(p,rng,L=2,per=7,leak=0.19,mode='bump'):
    n=len(p); key=rng.integers(0,29,size=per); c=np.zeros(n,dtype=np.int64); c[:L]=rng.integers(0,29,size=L)
    for i in range(L,n):
        v=(c[i-L]+p[i]+key[i%per])%29
        if v==c[i-1] and rng.random()>=leak:
            v=(c[i-1]+1)%29 if mode=='bump' else (c[i-1]+int(rng.integers(1,29)))%29
        c[i]=v
    return c
print('\nPOSITIVE CONTROL: c_i=c_{i-2}+p_i+keyword[i mod 7], repeat-avoidance rewrite (leak .19); Markov plaintext; real page lengths')
nul2={L:np.array([stat(dshuffled_pages(PAGES,rng),L).sum() for _ in range(40)]) for L in (1,2)}
for per in (7,13,23):
    pg=[enc_lag_keyword(markov_plain(len(p),rng),rng,2,per) for p in PAGES]
    for L in (1,2):
        S=stat(pg,L).sum(); print('  period %2d: lag-%d diff stat %.1f (z vs shuffle null %.1f)'%(per,L,S,(S-nul2[L].mean())/nul2[L].std()))
