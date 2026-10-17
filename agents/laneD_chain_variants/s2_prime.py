"""Candidate 2: Gematria prime-value chains."""
import math
from common import *
from sim import *
rng=np.random.default_rng(2)
P=np.array(PRIMES)
cnt=np.bincount(CALL,minlength=29); N=cnt.sum()
print('real rune counts chi2 vs flat (df28): %.1f  (null mean 28 sd 7.5)'%(((cnt-N/29)**2/(N/29)).sum()))
print('real normalised IoC %.4f'%ioc(CALL))
def snap_table(M,mode):
    t=np.zeros(M,dtype=np.int64)
    for x in range(M):
        if mode=='next':
            cand=[i for i,q in enumerate(P) if q>=x]; t[x]=cand[0] if cand else 0
        elif mode=='prev':
            cand=[i for i,q in enumerate(P) if q<=x]; t[x]=cand[-1] if cand else 28
        else:
            t[x]=int(np.argmin([(abs(q-x), q) for q in P], axis=0)[0]) if False else min(range(29),key=lambda i:(abs(P[i]-x),P[i]))
    return t
print('\n== B. v(c_i)=v(c_{i-1})+v(p_i)+k_i mod M, snapped back to a prime-valued rune (k flat) ==')
print('%-14s %-5s | pred IoC | pred dbl-rate | LLR(real counts | snap-pmf vs flat) | chi2(real vs snap-pmf)'%('M','snap'))
for M in (109,110,111,113,116):
    for mode in ('next','prev','nearest'):
        t=snap_table(M,mode); q=np.bincount(t,minlength=29)/M   # k flat => v_out uniform on Z_M => marginal is snap pmf
        pioc=29*(q**2).sum(); pd=(q**2).sum()
        llr=sum(cnt[r]*math.log(max(q[r],1e-12)*29) for r in range(29))
        chi=sum((cnt[r]-N*q[r])**2/max(N*q[r],1e-9) for r in range(29)) if (q>0).all() else float('inf')
        # simulated doublet rate via chain recursion
        pt=synth_plain(12000,rng); c=np.zeros(len(pt),dtype=np.int64); k=rng.integers(0,M,size=len(pt))
        for i in range(1,len(pt)): c[i]=t[(P[c[i-1]]+P[pt[i]]+k[i])%M]
        print('%-14d %-7s| %.3f   | sim %.4f (iid %.4f)| %9.1f | %s'%(M,mode,pioc,doublets(c)/len(c),pd,llr,'%.0f'%chi if np.isfinite(chi) else 'inf (pmf=0)'))
print('(real IoC 1.000, real dbl-rate 0.0066 ; LLR strongly negative = real counts reject the snap model in favour of flat)')

print('\n== A. index chain s_i = f(v(p_i), k_i) mod 29: zero set and implied doublet rate ==')
res=P%29
print('prime residues mod 29 by rune:',res.tolist())
from collections import defaultdict
bucket=defaultdict(list)
for r,x in enumerate(res): bucket[x].append(r)
print('A1. additive s=v(p)+k, k flat on Z29 -> P(s=0)=1/29 -> dbl-rate 3.45%: sim:')
def prime_add(p,rng):
    k=rng.integers(0,29,size=len(p)); s=(P[p]+k)%29; c=np.zeros(len(p),dtype=np.int64)
    for i in range(1,len(p)): c[i]=(c[i-1]+s[i])%29
    return c
dr=np.mean([doublets(c)/len(c) for c in [prime_add(synth_plain(12000,rng),rng) for _ in range(5)]]); print('   sim dbl-rate %.4f vs real 0.0066 -> z=%.1f'%(dr,(0.0066-dr)/math.sqrt(dr*(1-dr)/12900)))
print('A2. multiplicative s=k*(v(p)+a) mod 29, k flat on GF(29)*: s=0 iff v(p)=-a mod 29 -> doublet rate = freq(letters with that residue)')
print('   a | zero-letters (residue -a) | freq in solved plaintext | note')
rows=[]
for a in range(29):
    z=(-a)%29; letters=bucket.get(z,[])
    f=sum(PTFREQ[r] for r in letters); rows.append((a,[TR[r] for r in letters],f))
    print('  %2d | %-14s | %.4f' %(a,','.join(TR[r] for r in letters) or '-',f))
ok=[r for r in rows if 0.0057<=r[2]<=0.0076]
print('   offsets a whose zero set has frequency in the real band [0.57%,0.76%] (86+-9 doublets):',[(r[0],r[1],round(r[2],4)) for r in ok])
print('   (note: with a=0 and plain v(p) the zero letter is N (v=29), freq %.3f -> excluded; a=-1 (the solved-page p=c-(prime-1) convention) zero letter: prime 1? none; residue 1 -> %s)'%(PTFREQ[9],[TR[r] for r in bucket.get(1,[])]))
# multiplicative sim with a=0
def prime_mul(p,rng,a=0):
    k=rng.integers(1,29,size=len(p)); s=(k*((P[p]+a)%29))%29; c=np.zeros(len(p),dtype=np.int64)
    for i in range(1,len(p)): c[i]=(c[i-1]+s[i])%29
    return c
for a in (0,28,8):
    dr=np.mean([doublets(c)/len(c) for c in [prime_mul(synth_plain(12000,rng),rng,a) for _ in range(5)]]); print('   a=%d sim dbl-rate %.4f'%(a,dr))
print('   distinct residues of the 29 prime values mod 29: %d of 29 -> x(p)=v(p)+a mod 29 is NOT injective; several plaintext letter pairs would encrypt identically (lossy, undecryptable): %s'%(len(set(res.tolist())),{x:[TR[r] for r in b] for x,b in bucket.items() if len(b)>1}))
print('A3. Atbash / reversed prime-order alphabet: c -> -c is a unit map on Z29; chain with s -> -s; statistically identical to the plain chain. SKIPPED (no observable difference).')
