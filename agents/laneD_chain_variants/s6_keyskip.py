"""Candidate 6: key-skip-on-collision Vigenere with a per-page keyword: leak statistics beyond doublets."""
import math, time
from common import *
from sim import *
rng=np.random.default_rng(6)
def keyskip(p,key,once=True):
    """c_i=p_i+key[j]; j advances every letter; on collision with c_{i-1} the key letter is skipped (advance once more); once=False: skip until no collision (cap L)"""
    n=len(p); c=np.zeros(n,dtype=np.int64); L=len(key); j=0
    for i in range(n):
        v=(p[i]+key[j%L])%29; j+=1
        if i>0 and v==c[i-1]:
            if once:
                v=(p[i]+key[j%L])%29; j+=1
            else:
                t=0
                while v==c[i-1] and t<L: v=(p[i]+key[j%L])%29; j+=1; t+=1
        c[i]=v
    return c
def sticky_key(L,a,rng):
    k=[int(rng.integers(29))]
    for _ in range(L-1): k.append(k[-1] if rng.random()<a else int(rng.integers(29)))
    return np.array(k)
def lag_maxz(p,LM=60):
    n=len(p); p0=1/29; best=(-9,0)
    for L in range(2,min(LM,n//3)+1):
        eq=int((p[L:]==p[:-L]).sum()); m=n-L; z=(eq-m*p0)/math.sqrt(m*p0*(1-p0))
        if z>best[0]: best=(z,L)
    return best
def pagestats(pages):
    mx=[lag_maxz(p)[0] for p in pages]
    cnt=np.array([doublets(p) for p in pages]); npr=np.array([len(p)-1 for p in pages]); rho=cnt.sum()/npr.sum()
    disp=(((cnt-npr*rho)**2)/(npr*rho*(1-rho))).sum() if rho>0 else float('nan')   # chi2 df 54 under homogeneity
    # D-IoC28
    h=np.zeros(29)
    for p in pages: h+=np.bincount((p[1:]-p[:-1])%29,minlength=29)
    nz=h[1:]; dioc=28*(nz*(nz-1)).sum()/(nz.sum()*(nz.sum()-1))
    return sum(mx), disp, dioc, cnt.sum()/npr.sum()
t0=time.time()
real=pagestats(PAGES)
nul=np.array([pagestats(shuffled_pages(PAGES,rng)) for _ in range(150)])
print('REAL : sum_pages max-lag z (lags 2..60) = %.1f ; doublet dispersion chi2(54) = %.1f ; D-IoC28 = %.4f ; dbl %.4f'%real)
print('NULL(150 shuffles): sum-max-z %.1f +- %.1f ; dispersion chi2 (shuffled: doublets ~3.45%%, not comparable) ; D-IoC28 %.4f +- %.4f'%(nul[:,0].mean(),nul[:,0].std(),nul[:,2].mean(),nul[:,2].std()))
print('   real sum-max-z z-score vs null: %.2f ; real D-IoC28 z vs null: %.2f'%((real[0]-nul[:,0].mean())/nul[:,0].std(),(real[2]-nul[:,2].mean())/nul[:,2].std()))
# dispersion reference: binomial resampling at the real rate with real page lengths
npr=np.array([len(p)-1 for p in PAGES]); rho=real[3]
dref=[]
for _ in range(2000):
    cnt=rng.binomial(npr,rho); r2=cnt.sum()/npr.sum(); dref.append((((cnt-npr*r2)**2)/(npr*r2*(1-r2))).sum())
dref=np.array(dref); print('Dispersion reference (homogeneous binomial at rate %.4f): mean %.1f sd %.1f ; real %.1f -> z %.2f ; per-page real counts: max %d, #pages with 0 doublets %d'%(rho,dref.mean(),dref.std(),real[1],(real[1]-dref.mean())/dref.std(),max(doublets(p) for p in PAGES),sum(doublets(p)==0 for p in PAGES)))
pc=np.array([doublets(p) for p in PAGES]); print('   Poisson expectation of empty pages at mean %.2f/page: %.1f'%(pc.mean(),55*math.exp(-pc.mean())))
print('time',time.time()-t0)
print('\n== Key-skip Vigenere constructions (Markov plaintext, per-page keyword, real page lengths; 8 syntheses) ==')
def ctrl(name,keyfn,once=True,reps=8):
    S=[]
    for _ in range(reps):
        pg=[keyskip(markov_plain(len(p),rng),keyfn(rng),once) for p in PAGES]
        S.append(pagestats(pg))
    S=np.array(S)
    print('%-52s dbl %.4f | sum-maxz %.1f (z vs null %5.1f) | disp chi2 %6.1f | D-IoC28 %.4f (z %5.1f)'%(name,S[:,3].mean(),S[:,0].mean(),(S[:,0].mean()-nul[:,0].mean())/nul[:,0].std(),S[:,1].mean(),S[:,2].mean(),(S[:,2].mean()-nul[:,2].mean())/nul[:,2].std()))
    return S
for L in (5,8,13,20):
    ctrl('S1 skip-once, random keyword L=%d (a=1/29)'%L,lambda r,L=L:sticky_key(L,0.0,r))
for L in (8,13):
    for a in (0.19,0.30):
        S=ctrl('S1 skip-once, sticky keyword L=%d a=%.2f'%(L,a),lambda r,L=L,a=a:sticky_key(L,a,r))
        dr=S[:,1]; print('      -> dispersion z vs homogeneous-binomial ref: %.1f (real: %.2f)'%((dr.mean()-dref.mean())/dref.std(),(real[1]-dref.mean())/dref.std()))
ctrl('S2 skip-until-clear, random keyword L=13',lambda r:sticky_key(13,0.0,r),once=False)
# doublet position vs key phase check: leak doublets occur only at key positions with equal adjacent letters
L=13; key=np.array([5,5,9,1,2,2,2,30%29,14,7,7,3,20]); n=40000
p=markov_plain(n,rng); c=keyskip(p,key,True); idx=np.where(c[1:]==c[:-1])[0]+1
print('\nDoublet-position test (single long text, keyword with adjacent equals at positions 0-1, 4-5-6, 9-10): doublets=%d (%.4f); share of doublets at key-phase classes (i mod 13) is non-uniform:'%(len(idx),len(idx)/n),np.bincount(idx%13,minlength=13).tolist())

b=np.bincount(idx%13,minlength=13); print('   chi2 of doublet-phase histogram (df 12): %.1f  (p~0.06) -> skips randomise the key phase; doublet positions are NOT a usable period leak'%(((b-b.mean())**2/b.mean()).sum()))
