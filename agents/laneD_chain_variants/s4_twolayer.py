"""Candidate 4: flat outer cipher after a doublet-free transform."""
import math
from common import *
from sim import *
rng=np.random.default_rng(4)
ENG=np.load('eng_runes.npy')
def dpmf(x): 
    return np.bincount((x[1:]-x[:-1])%29,minlength=29)/(len(x)-1)
def Dioc28(pages):
    h=np.zeros(29)
    for p in pages: h+=np.bincount((p[1:]-p[:-1])%29,minlength=29)
    nz=h[1:]; n=nz.sum(); return 28*(nz*(nz-1)).sum()/(n*(n-1))
print('== Formal bound: key independent of the transformed text q  =>  P(doublet) = sum_x P_X(x) P_d(-x) >= min_x P_X(x), X=q_i-q_{i-1} ==')
for name,x in (('solved Cicada pages (1769 runes)',PT),('technical English->runes (354k runes)',ENG),('Markov(bigram) plaintext 200k',markov_plain(200000,rng))):
    X=dpmf(x); print('  %-40s min_x P_X = %.4f at x=%d ; P_X(0)=%.4f ; IoC28 of nonzero X = %.3f'%(name,X.min(),X.argmin(),X[0],28*(X[1:]**2).sum()/(X[1:].sum()**2)))
eps=86/12901; se=math.sqrt(eps*(1-eps)/12901)
print('  real doublet rate %.4f (se %.4f).'%(eps,se))
print('  So for q = plain letters, ANY independent key gives rate >= %.4f => real is %.1f se below the bound.'%(dpmf(ENG).min(),(eps-dpmf(ENG).min())/se))
# Fourier necessary condition
w=np.exp(2j*np.pi/29)
for name,x in (('technical English',ENG),('solved pages',PT)):
    X=dpmf(x); phi=np.array([abs(sum(X[a]*w**(t*a) for a in range(29))) for t in range(1,29)])
    need=1/29-eps
    print('  Fourier: need |phi_X(t)|>=%.4f for all t!=0 (|phi_D(t)|=1/29-eps for hole-flat D, |phi_d|<=1); %s: min|phi_X|=%.4f (t=%d), #t violating=%d/28'%(need,name,phi.min(),1+phi.argmin(),(phi<need).sum()))
# real phi_D
Dall=np.concatenate([(p[1:]-p[:-1])%29 for p in PAGES]); Dp=np.bincount(Dall,minlength=29)/len(Dall)
phiD=np.array([abs(sum(Dp[a]*w**(t*a) for a in range(29))) for t in range(1,29)])
print('  real |phi_D(t)| mean over t=%.4f (chain prediction %.4f), min %.4f max %.4f; noise sd per t ~ %.4f'%(phiD.mean(),1/29-eps,phiD.min(),phiD.max(),1/math.sqrt(len(Dall))))

print('\n== Positive/negative controls: synthetic ciphertext on Markov plaintext, real page lengths ==')
def collapse(p):   # run-length convention: drop a letter equal to its predecessor
    out=[p[0]]
    for a in p[1:]:
        if a!=out[-1]: out.append(a)
    return np.array(out)
def bump(p):
    q=p.copy()
    for i in range(1,len(q)):
        if q[i]==q[i-1]: q[i]=(q[i]+1)%29
    return q
def nonrep_key(n,rng):
    k=np.zeros(n,dtype=np.int64); k[0]=rng.integers(29)
    for i in range(1,n): k[i]=(k[i-1]+rng.integers(1,29))%29
    return k
def pw_key(n,rng,r):
    k=np.zeros(n,dtype=np.int64); k[0]=rng.integers(29)
    for i in range(1,n): k[i]=(k[i-1]+rng.integers(1,29))%29 if rng.random()<r else k[i-1]
    return k
def vig(L): 
    return lambda n,rng:np.tile(rng.integers(0,29,size=L),n//L+1)[:n]
Xmin=dpmf(markov_plain(300000,rng)); xstar=int(Xmin.argmin())
def optwalk(n,rng):   # key increments concentrated on the value that cancels the rarest plaintext difference
    return np.cumsum(np.where(rng.random(n)<0.5,(-xstar)%29,rng.integers(0,29,size=n)))%29
def run(name,q_fn,k_fn,reps=6):
    dr=[];di=[];ic=[]
    for _ in range(reps):
        pg=[]
        for n in [len(p) for p in PAGES]:
            q=q_fn(markov_plain(n+60,rng))[:n]
            if len(q)<n: q=np.concatenate([q,markov_plain(n-len(q),rng)]) 
            pg.append((q+k_fn(n,rng))%29)
        a,b=page_doublets(pg); dr.append(a/b); di.append(Dioc28(pg)); ic.append(ioc(np.concatenate(pg)))
    r=np.mean(dr); print('%-52s dbl %.4f (z vs real %6.1f) | D-IoC28 %.3f | IoC %.3f'%(name,r,(eps-r)/math.sqrt(r*(1-r)/12901),np.mean(di),np.mean(ic)))
flat=lambda n,rng:rng.integers(0,29,size=n)
ident=lambda p:p
print('REAL: dbl %.4f | D-IoC28 %.3f | IoC %.3f'%(eps,Dioc28(PAGES),ioc(CALL)))
run('raw plaintext + flat iid key (reference OTP)',ident,flat)
run('4a collapse-runs q + flat iid key',collapse,flat)
run('4b bump(+1) q + flat iid key',bump,flat)
run('4c raw plaintext + non-repeating iid key',ident,nonrep_key)
run('4d collapse q + Vigenere keyword L=7',collapse,vig(7))
run('4d collapse q + Vigenere keyword L=13',collapse,vig(13))
run('4e collapse q + piecewise-const key (change p=.18)',collapse,lambda n,r:pw_key(n,r,0.18))
run('4f collapse q + piecewise-const key (change p=.05)',collapse,lambda n,r:pw_key(n,r,0.05))
run('4g bump q + optimal-walk key (cancels rarest X=%d)'%xstar,bump,optwalk)
run('REFERENCE keyed chain (EA-zero) on raw plaintext',lambda p:p,lambda n,r:np.zeros(n,dtype=np.int64)) if False else None
pg=synth_pages_m(lambda p,r:chain(p,r,1),rng); a,b=page_doublets(pg); print('%-52s dbl %.4f | D-IoC28 %.3f | IoC %.3f'%('REFERENCE keyed chain (EA-zero)',a/b,Dioc28(pg),ioc(np.concatenate(pg))))
