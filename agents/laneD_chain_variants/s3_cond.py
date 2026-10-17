"""Candidate 3: fixed-table ciphertext-feedback c_i = T[p_i][c_{i-1}] (no-repeat Latin square). Conditional-IoC test, real vs null vs controls."""
import math, time
from common import *
from sim import *
rng=np.random.default_rng(3)
def pairs(pages,depth=1,backward=False):
    """returns arrays (ctx, out) over within-page positions"""
    ctx=[];out=[]
    for p in pages:
        n=len(p)
        if n<=depth: continue
        if not backward:
            c=np.zeros(n-depth,dtype=np.int64)
            for d in range(depth): c=c*29+p[d:n-depth+d]
            ctx.append(c); out.append(p[depth:])
        else:  # predict c_{i-1}.. from following depth runes: context = next `depth` runes
            c=np.zeros(n-depth,dtype=np.int64)
            for d in range(depth): c=c*29+p[1+d:n-depth+1+d]
            ctx.append(c); out.append(p[:n-depth])
    return np.concatenate(ctx),np.concatenate(out)
def condstats(pages,depth=1,backward=False):
    ctx,out=pairs(pages,depth,backward); K=29**depth
    tab=np.bincount(ctx*29+out,minlength=K*29).reshape(K,29).astype(np.float64)
    na=tab.sum(1); num=(tab*(tab-1)).sum(1)
    den=na*(na-1)
    pooled=29*num.sum()/den.sum()
    rows=np.where(den>0,29*num/np.maximum(den,1),np.nan)
    return pooled,rows,na
def latin_noreeat(rng,star=28,switches=4000):
    L=np.array([[(r+c)%29 for c in range(29)] for r in range(29)])
    # make row 0 identity; relabel rows so that plaintext symbol `star` has the identity row, others shuffled
    perm=list(range(1,29)); rng.shuffle(perm)
    rowmap={}; others=[s for s in range(29) if s!=star]
    T=np.zeros((29,29),dtype=np.int64); T[star]=L[0]
    for s,r in zip(others,perm): T[s]=L[r]
    for _ in range(switches):
        r1,r2=rng.choice(others,2,replace=False)
        c0=int(rng.integers(29)); cols=[c0]; v=T[r1][c0]
        # follow cycle: column c' where T[r2][c']==T[r1][c]
        c=c0
        while True:
            nxt=int(np.where(T[r2]==T[r1][c])[0][0])
            if nxt==c0: break
            cols.append(nxt); c=nxt
        for c in cols: T[r1][c],T[r2][c]=T[r2][c],T[r1][c]
    assert all(sorted(T[r])==list(range(29)) for r in range(29)) and all(sorted(T[:,c])==list(range(29)) for c in range(29))
    assert (T[star]==np.arange(29)).all() and all((T[p]!=np.arange(29)).all() for p in others)
    return T
def enc_T(p,T,rng):
    c=np.zeros(len(p),dtype=np.int64); c[0]=rng.integers(29)
    for i in range(1,len(p)): c[i]=T[p[i],c[i-1]]
    return c
def enc_additive_fixed(p,rng):   # c_i = c_{i-1}+p_i+1 (Leo's constant-key chain)
    c=np.zeros(len(p),dtype=np.int64); c[0]=rng.integers(29)
    for i in range(1,len(p)): c[i]=(c[i-1]+p[i]+1)%29
    return c
def enc_depth2(p,rng,tab=None):
    h=rng.integers(0,29,size=29) if tab is None else tab
    c=np.zeros(len(p),dtype=np.int64); c[:2]=rng.integers(0,29,size=2)
    for i in range(2,len(p)): c[i]=(c[i-1]+p[i]+1+h[c[i-2]])%29
    return c
t0=time.time()
_m=markov_plain(60000,rng); print('Markov plaintext (bigram model of solved pages) unigram IoC %.3f; conditional-on-prev-plaintext IoC %.3f'%(ioc(_m),condstats([_m],1,False)[0]))
print('plaintext (solved pages) unigram normalised IoC = %.3f  => predicted conditional IoC for ANY fixed T'%ioc(PT))
fl=0.0066
q=np.full(29,(1-fl)/28); q[28]=fl; print('lower bound on any input distribution with a 0.66%% rare symbol: IoC_norm >= %.4f'%(29*(q**2).sum()))
for depth,backward in ((1,False),(1,True),(2,False)):
    tag=('backward ' if backward else 'forward ')+'depth%d'%depth
    pr,rows,na=condstats(PAGES,depth,backward)
    nul=[];nulmin=[];nulmax=[]
    for s in range(200):
        a,r,_=condstats(shuffled_pages(PAGES,rng),depth,backward); nul.append(a)
        if depth==1: nulmin.append(np.nanmin(r)); nulmax.append(np.nanmax(r))
    nul=np.array(nul)
    print('\n[%s] REAL pooled conditional IoC %.4f ; null (200 within-page shuffles) mean %.4f sd %.4f -> z=%.2f'%(tag,pr,nul.mean(),nul.std(),(pr-nul.mean())/nul.std()))
    print('   z of English-like prediction 1.76 vs real: (1.76-%.4f)/null sd = %.0f sigma ; z of generic bound 1.022: %.1f sigma'%(pr,(1.76-pr)/nul.std(),(1.022-pr)/nul.std()))
    if depth==1:
        print('   per-previous-rune IoC: min %.3f max %.3f (null min mean %.3f, null max mean %.3f); English-like rows would all be ~1.76'%(np.nanmin(rows),np.nanmax(rows),np.mean(nulmin),np.mean(nulmax)))
        print('   rows:',np.round(rows,2).tolist())
print('time',time.time()-t0)
print('\nPOSITIVE CONTROLS (synthetic ciphertext of solved plaintext at real page lengths; 6 syntheses each)')
def ctrl(name,fn,reps=6):
    out={k:[] for k in ('f1','b1','f2','dr','minrow')}
    for r in range(reps):
        pg=synth_pages_m(fn,rng)
        a,rows,_=condstats(pg,1,False); b,_,_=condstats(pg,1,True); c2,_,_=condstats(pg,2,False)
        out['f1'].append(a);out['b1'].append(b);out['f2'].append(c2);out['dr'].append(page_doublets(pg)[0]/page_doublets(pg)[1]);out['minrow'].append(np.nanmin(rows))
    print('%-44s fwd1 %.3f | bwd1 %.3f | fwd2 %.3f | min row %.3f | dbl %.4f'%(name,np.mean(out['f1']),np.mean(out['b1']),np.mean(out['f2']),np.mean(out['minrow']),np.mean(out['dr'])))
Ts=[latin_noreeat(rng) for _ in range(3)]
for i,T in enumerate(Ts):
    ctrl('random no-repeat Latin square #%d (T[EA]=id)'%i,lambda p,r,T=T:enc_T(p,T,r),reps=4)
ctrl('constant-key chain c=c_prev+p+1',enc_additive_fixed)
ctrl('keyed flat chain (position-varying key)',lambda p,r:chain(p,r,1))
ctrl('flat Vigenere (random key)',lambda p,r:(p+r.integers(0,29,size=len(p)))%29)

print('\n== Per-page tables (a different fixed T for every page): context = (page, previous rune) ==')
def perpage_cond(pages):
    num=0.0; den=0.0
    for p in pages:
        if len(p)<3: continue
        tab=np.bincount(p[:-1]*29+p[1:],minlength=841).reshape(29,29).astype(float)
        na=tab.sum(1); num+=(tab*(tab-1)).sum(); den+=(na*(na-1)).sum()
    return 29*num/den
r=perpage_cond(PAGES); nl=np.array([perpage_cond(shuffled_pages(PAGES,rng)) for _ in range(300)])
print('REAL per-page pooled conditional IoC %.4f ; null mean %.4f sd %.4f -> z=%.2f (hole-aware chain prediction ~1.02)'%(r,nl.mean(),nl.std(),(r-nl.mean())/nl.std()))
print('English-like (fixed T per page) prediction ~1.74 -> %.0f sigma away'%((1.74-r)/nl.std()))
Tl=[latin_noreeat(rng) for _ in range(55)]
vals=[]
for rep in range(4):
    pg=[enc_T(markov_plain(len(p),rng),Tl[(i+rep)%55],rng) for i,p in enumerate(PAGES)]
    vals.append(perpage_cond(pg))
print('control: independent random no-repeat Latin square per page, Markov plaintext: per-page cond IoC = %s'%np.round(vals,3))
