"""Candidates 1 and 7: lag-L coincidence profile (L=1..300) and increment histogram D_i, real vs shuffle null vs positive controls."""
import math, time
from common import *
from sim import *
rng=np.random.default_rng(1)
LMAX=300
_np=[sum(max(len(p)-L,0) for p in PAGES) for L in range(LMAX+1)]
LV=max(L for L in range(1,LMAX+1) if _np[L]>=1000)
print('valid lags 1..%d (>=1000 pairs)'%LV)
def cat(pages):
    x=np.concatenate(pages); pid=np.concatenate([np.full(len(p),i) for i,p in enumerate(pages)]); return x,pid
def lagprof(pages, LMAX=LMAX):
    x,pid=cat(pages); eq=np.zeros(LMAX+1); npairs=np.zeros(LMAX+1)
    for L in range(1,LMAX+1):
        m=pid[L:]==pid[:-L]; e=(x[L:]==x[:-L])&m
        eq[L]=e.sum(); npairs[L]=m.sum()
    return eq,npairs
def dhist(pages):
    h=np.zeros(29)
    for p in pages:
        d=(p[1:]-p[:-1])%29; h+=np.bincount(d,minlength=29)
    return h
def zlag(eq,npairs,p0):
    mu=npairs*p0; sd=np.sqrt(np.maximum(npairs*p0*(1-p0),1e-9)); z=np.zeros_like(mu); z[1:]=(eq[1:]-mu[1:])/sd[1:]; return z
def p0_of(pages):
    c=np.bincount(np.concatenate(pages),minlength=29); n=c.sum(); return (c*(c-1)).sum()/(n*(n-1))
def dsummary(h):
    nz=h[1:]; n=nz.sum(); p=1/28; z=(nz-n*p)/math.sqrt(n*p*(1-p))
    chi=((nz-n*p)**2/(n*p)).sum()
    return z,chi,n
def report(name,pages,nsh=200):
    eq,npairs=lagprof(pages); p0=p0_of(pages); z=zlag(eq,npairs,p0)
    h=dhist(pages); zd,chi,n=dsummary(h)
    return dict(name=name,z=z,eq=eq,npairs=npairs,p0=p0,h=h,zd=zd,chi=chi,n=n)

t0=time.time()
real=report('real',PAGES)
print('REAL lag1 doublets',int(real['eq'][1]),'of',int(real['npairs'][1]),'rate %.5f'%(real['eq'][1]/real['npairs'][1]),'p0=%.5f'%real['p0'],'z1=%.1f'%real['z'][1])
print('REAL z at lags 2..10:',np.round(real['z'][2:11],2))
print('REAL min z over lags 2..LV: %.2f at lag %d ; max z: %.2f at lag %d'%(real['z'][2:].min(),2+real['z'][2:].argmin(),real['z'][2:].max(),2+real['z'][2:].argmax()))
# shuffle null
nsh=300
mins=[];maxs=[];z1=[];chis=[];maxabs=[];zd1=[];zd28=[]
for s in range(nsh):
    r=report('sh',shuffled_pages(PAGES,rng))
    mins.append(r['z'][2:].min()); maxs.append(r['z'][2:].max()); z1.append(r['z'][1]); chis.append(r['chi']); maxabs.append(np.abs(r['zd']).max()); zd1.append(r['zd'][0]); zd28.append(r['zd'][27])
mins=np.array(mins);maxs=np.array(maxs)
print('NULL(300 shuffles) min z lags2..LV: mean %.2f sd %.2f  | max z mean %.2f sd %.2f | z1 mean %.2f'%(mins.mean(),mins.std(),maxs.mean(),maxs.std(),np.mean(z1)))
print('real min z %.2f -> null-percentile %.1f%%; real max z %.2f -> upper percentile %.1f%%'%(real['z'][2:].min(),100*(mins<=real['z'][2:].min()).mean(),real['z'][2:].max(),100*(maxs>=real['z'][2:].max()).mean()))
print('D histogram real (D=0..28):',real['h'].astype(int).tolist())
zd=real['zd']; print('D z-scores (D=1..28):',np.round(zd,2).tolist())
print('chi2 uniform(D=1..28, df27): real %.1f ; null mean %.1f sd %.1f ; pctile %.1f%%'%(real['chi'],np.mean(chis),np.std(chis),100*(np.array(chis)>=real['chi']).mean()))
print('max|zD| real %.2f ; null mean %.2f sd %.2f ; max %.2f'%(np.abs(zd).max(),np.mean(maxabs),np.std(maxabs),np.max(maxabs)))
n=real['n']; k1=real['h'][1]; k28=real['h'][28]
print('D=1: %d (expect %.1f) z=%.2f one-sided p(binom normal)=%.3f ; D=28: %d z=%.2f'%(k1,n/28,zd[0],0.5*math.erfc(zd[0]/math.sqrt(2)),k28,zd[27]))
rest=np.delete(real['h'][1:],[0,27]); print('D=1,28 vs mean of other 26 values: %.1f, %.1f vs %.1f (sd %.1f)'%(k1,k28,rest.mean(),rest.std()))
print('ratio D=1 / mean(other 26) = %.3f  (bump-rewrite hypothesis predicts ~1.8)'%(k1/rest.mean()))
print('time',time.time()-t0)

# ---- positive controls ----
def ctrl(name,fn,reps=12):
    zs1=[];zl=[];ratio=[];zD1=[];chi=[];dr=[];zmin2=[]
    for r in range(reps):
        pg=synth_pages(fn,rng); rr=report(name,pg)
        zs1.append(rr['z'][1]); zl.append(rr['z'][2]); dr.append(rr['eq'][1]/rr['npairs'][1])
        zD1.append(rr['zd'][0]); chi.append(rr['chi']); zmin2.append(rr['z'][2:LV+1].min())
        rest=np.delete(rr['h'][1:],[0,27]); ratio.append(rr['h'][1]/rest.mean())
    print('%-46s dbl-rate %.4f | z(lag1) %7.1f | z(lag2) %7.1f | minz(2..LV) %6.1f | D1/other %.2f | zD1 %6.1f | chi2(D) %7.1f'%(name,np.mean(dr),np.mean(zs1),np.mean(zl),np.mean(zmin2),np.mean(ratio),np.mean(zD1),np.mean(chi)))
print('\nPOSITIVE CONTROLS (mean of 12 syntheses at real page lengths; solved plaintext tiled)')
ctrl('chain L=1 (s!=0 except EA)',lambda p,r:chain(p,r,1))
ctrl('chain L=2 (s!=0 except EA)',lambda p,r:chain(p,r,2))
ctrl('chain L=3',lambda p,r:chain(p,r,3))
ctrl('lag-2 base + bump rule leak .19',lambda p,r:lagL_with_rule(p,r,2,.19,'bump'))
ctrl('lag-2 base + redraw rule leak .19',lambda p,r:lagL_with_rule(p,r,2,.19,'redraw'))
ctrl('lag-1 base(Vig-diff)+bump rule leak .19',lambda p,r:lagL_with_rule(p,r,1,.19,'bump'))
ctrl('iid base-29 digits + bump(+1) leak .19',lambda p,r:iid_rule(len(p),r,.19,'bump'))
ctrl('iid base-29 digits + redraw leak .19',lambda p,r:iid_rule(len(p),r,.19,'redraw'))
ctrl('flat Vigenere (random key) [no rule]',lambda p,r:(p+r.integers(0,29,size=len(p)))%29)
