"""Candidate 7 extras: rewrite-offset bounds (all delta) and byte-block base-29 phase test."""
import math, time
from common import *
from sim import *
rng=np.random.default_rng(7)
Dall=np.concatenate([(p[1:]-p[:-1])%29 for p in PAGES]); h=np.bincount(Dall,minlength=29).astype(float); N=len(Dall)
would=N/29   # would-be collisions if stream were flat: 444.9
nz=h[1:]; base=np.delete(nz,0).mean()
print('N=%d ; would-be collisions ~%.0f ; observed doublets %d (kept fraction %.3f)'%(N,would,h[0],h[0]/would))
print('Rewrite-to-offset-delta model: a fraction f of would-be collisions is moved to D=delta. f_delta = (n_delta - mean_of_rest)/%.0f, se ~ %.3f'%(would,math.sqrt(base)/would))
fs=[]
for d in range(1,29):
    rest=(nz.sum()-h[d])/27; f=(h[d]-rest)/would; fs.append(f)
fs=np.array(fs); se=math.sqrt(base*(1+1/27))/would
print('  f_delta (delta=1..28):',np.round(fs,3).tolist())
print('  f_1 = %.3f +- %.3f (bump +1) ; f_28 = %.3f +- %.3f (bump -1) ; max f over delta = %.3f (delta=%d) ; 95%% upper bound for any single delta ~ %.3f'%(fs[0],se,fs[27],se,fs.max(),1+fs.argmax(),1.645*se))
print('  a bump-type rewrite that explains the deficit needs f = 1-kept = %.2f -> excluded by %.0f se'%(1-h[0]/would,(1-h[0]/would-fs[0])/se))
# mixture of two targets: D=1 and D=28 or D=+-2 etc.  Test: sum over delta in {1,28}
for S in ([1,28],[1,2],[1,28,2,27]):
    f=sum(fs[d-1] for d in S); print('  rewrite spread over delta in %s: total f = %.3f +- %.3f'%(S,f,se*math.sqrt(len(S))))
# ---- byte-block base-29 phase test ----
def phase_chi(x,m):
    best=(0,0)
    for ph in range(m):
        c=np.bincount(x[ph::m],minlength=29); n=c.sum(); e=n/29; chi=((c-e)**2/e).sum()
        if chi>best[0]: best=(chi,ph)
    return best
def maxphase(pages,M=64):
    # pooled by position-in-page mod m (pages restart): sum chi over pages not possible per phase; use global concatenation with per-page phase = idx mod m
    out=[]
    for m in range(2,M+1):
        c=np.zeros((m,29))
        for p in pages:
            for ph in range(m): c[ph]+=np.bincount(p[ph::m],minlength=29)
        n=c.sum(1,keepdims=True); e=n/29; chi=((c-e)**2/e).sum(1)   # df 28 each
        out.append((chi.max()-28)/math.sqrt(56))
    return np.array(out)
t0=time.time()
real=maxphase(PAGES); 
nul=np.array([maxphase(shuffled_pages(PAGES,rng)).max() for _ in range(60)])
print('\nByte-block / base-conversion phase test: per-phase chi2 (df28), best phase for each block length m=2..64 (z=(chi-28)/sqrt(56))')
print('  REAL max over m,phase: z=%.2f (m=%d) ; null max over m (60 shuffles) mean %.2f sd %.2f max %.2f'%(real.max(),2+real.argmax(),nul.mean(),nul.std(),nul.max()))
def bytes_to_digits(nb,rng,k=3,d=5):
    out=[]
    for _ in range(nb//k):
        v=int.from_bytes(rng.integers(0,256,size=k,dtype=np.uint8).tobytes(),'big'); dig=[]
        for _ in range(d): dig.append(v%29); v//=29
        out+=dig[::-1]
    return np.array(out)
def mkpages(gen):
    s=gen(); out=[];o=0
    for p in PAGES: out.append(s[o:o+len(p)]); o+=len(p)
    return out
pg=mkpages(lambda:bytes_to_digits(3*(len(CALL)//5+2),rng,3,5)[:len(CALL)])
# pages restart phase: pages of arbitrary length break block alignment across pages; so use per-page alignment (block starts at page start)
pg=[bytes_to_digits(3*(len(p)//5+1),rng,3,5)[:len(p)] for p in PAGES]
r=maxphase(pg); print('  CONTROL random bytes -> 5 base-29 digits per 3 bytes, per page aligned: max z=%.1f at m=%d'%(r.max(),2+r.argmax()))
pg=[bytes_to_digits(2*(len(p)//4+1),rng,2,4)[:len(p)] for p in PAGES]
r=maxphase(pg); print('  CONTROL random bytes -> 4 base-29 digits per 2 bytes: max z=%.1f at m=%d'%(r.max(),2+r.argmax()))
print('  (real stream has no phase deficit for any block length 2..64, so no fixed-width byte/base-29 block packing aligned at page starts)')
print('time',time.time()-t0)
