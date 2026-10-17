"""Candidate 5: transposition before/after chain. Unscramble scan over reorderings of each page."""
import math, time
from common import *
from sim import *
rng=np.random.default_rng(5)
WS=list(range(2,41))
def col_order(n,w,rev_cols,up):
    r=-(-n//w); idx=[]
    cols=range(w-1,-1,-1) if rev_cols else range(w)
    for c in cols:
        rows=range(r-1,-1,-1) if up else range(r)
        for rr in rows:
            i=rr*w+c
            if i<n: idx.append(i)
    return np.array(idx)
def rail_order(n,r):
    if r<2: return np.arange(n)
    per=2*(r-1); rail=np.array([min(i%per, per-i%per) for i in range(n)])
    return np.argsort(rail,kind='stable')
def serp_order(n,w):
    idx=[]
    for rr in range(-(-n//w)):
        row=list(range(rr*w,min((rr+1)*w,n)))
        idx+= row[::-1] if rr%2 else row
    return np.array(idx)
def blockrev(n,b):
    idx=[]
    for s in range(0,n,b): idx+=list(range(min(s+b,n)-1,s-1,-1))
    return np.array(idx)
def build_orders(n):
    O={}
    O['identity']=np.arange(n); O['reverse']=np.arange(n)[::-1]
    for w in WS:
        for rc in (0,1):
            for up in (0,1):
                o=col_order(n,w,rc,up); nm='col(w=%d,%s,%s)'%(w,'Rcols' if rc else 'Lcols','up' if up else 'down')
                O[nm]=o; O[nm+'^-1']=np.argsort(o)
        o=rail_order(n,w); O['rail(r=%d)'%w]=o; O['rail(r=%d)^-1'%w]=np.argsort(o)
        O['serp(w=%d)'%w]=serp_order(n,w); O['blockrev(b=%d)'%w]=blockrev(n,w)
    return O
KEYS=list(build_orders(50).keys())
def overlap(pages):
    ov={k:0 for k in KEYS}; tt=0
    for p in pages:
        O=orders_for(len(p)); tt+=len(p)-1
        for k in KEYS:
            o=O[k]; ov[k]+=int((np.abs(o[1:]-o[:-1])==1).sum())
    return {k:v/tt for k,v in ov.items()}
FAM=lambda k:k.split('(')[0]+('^-1' if k.endswith('^-1') else '')
_cache={}
def orders_for(n):
    if n not in _cache: _cache[n]=build_orders(n)
    return _cache[n]
def scan(pages):
    tot={k:0 for k in KEYS}; npairs=sum(len(p)-1 for p in pages)
    for p in pages:
        O=orders_for(len(p))
        for k in KEYS:
            y=p[O[k]]; tot[k]+=int((y[1:]==y[:-1]).sum())
    return tot,npairs
def p0_of(pages):
    c=np.bincount(np.concatenate(pages),minlength=29); n=c.sum(); return (c*(c-1)).sum()/(n*(n-1))
def zof(tot,npairs,p0): 
    mu=npairs*p0; sd=math.sqrt(npairs*p0*(1-p0)); return {k:(v-mu)/sd for k,v in tot.items()}
t0=time.time()
OV=overlap(PAGES); GEN=[k for k in KEYS if OV[k]<0.2 and k not in('identity','reverse')]
print('reorderings total %d ; genuinely different adjacency (<20%% of adjacent pairs preserved): %d ; adjacency-preserving (>=20%%): %s'%(len(KEYS),len(GEN),[k for k in KEYS if OV[k]>=0.2 and k not in('identity','reverse')][:40]))
tot,npairs=scan(PAGES); p0=p0_of(PAGES); Z=zof(tot,npairs,p0)
print('REAL scan: %d reorderings x 55 pages; identity doublets %d (z=%.1f); reverse z=%.1f'%(len(KEYS),tot['identity'],Z['identity'],Z['reverse']))
rest=[(Z[k],k) for k in GEN]
rest.sort()
print('best 12 non-trivial reorderings by pooled doublet z:'); 
for z,k in rest[:12]: print('   %-34s doublets %5d  z=%.2f'%(k,tot[k],z))
nb=rest
print('best genuinely-different reordering: z = %.2f (%s)'%(nb[0][0],nb[0][1]))
adj=[(Z[k],k,OV[k]) for k in KEYS if k not in GEN and k not in('identity','reverse')]; adj.sort()
print('adjacency-preserving reorderings keep the deficit in proportion to their overlap (z, overlap):',[(k,round(z,1),round(o,2)) for z,k,o in adj[:6]],'...')
print('blockrev z by b (b=2..12):',[round(Z['blockrev(b=%d)'%b],1) for b in range(2,13)],' ... b=40: %.1f'%Z['blockrev(b=40)'])
# family level summary: min z by family
fam={}
for z,k in rest: fam.setdefault(FAM(k),[]).append((z,k))
print('family minima:',{f:(round(v[0][0],2),v[0][1]) for f,v in fam.items()})
# null: shuffled pages, same scan; min z over non-trivial, non-blockrev reorderings
nm=[];
for s in range(60):
    sp=shuffled_pages(PAGES,rng); t,npr=scan(sp); z=zof(t,npr,p0_of(sp))
    nm.append(min(z[k] for k in GEN))
nm=np.array(nm); print('NULL (60 shuffled corpora): min z over %d non-trivial reorderings: mean %.2f sd %.2f min %.2f ; real best %.2f -> z-vs-null %.2f'%(len(nb),nm.mean(),nm.std(),nm.min(),nb[0][0],(nb[0][0]-nm.mean())/nm.std()))
# per-page: is the real order the unique minimum? count pages where identity has strictly fewer doublets than every non-adjacency-preserving reordering
strict=0;le=0;ranks=[]
for p in PAGES:
    O=orders_for(len(p)); c0=doublets(p)
    others=[doublets(p[O[k]]) for k in GEN]
    mn=min(others); strict+= c0<mn; le+= c0<=mn; ranks.append(np.mean(np.array(others)<c0))
print('per page: identity strictly below ALL %d genuinely different reorderings on %d/55 pages, <= on %d/55; mean fraction of reorderings beating identity %.3f'%(len(GEN),strict,le,np.mean(ranks)))
# same per-page uniqueness for shuffled corpora (calibration)
sct=[];
for s in range(10):
    sp=shuffled_pages(PAGES,rng); c=0
    for p in sp:
        O=orders_for(len(p)); c0=doublets(p)
        mn=min(doublets(p[O[k]]) for k in GEN); c+= c0<mn
    sct.append(c)
print('   shuffled-corpus calibration: identity strictly lowest on %.1f +- %.1f of 55 pages'%(np.mean(sct),np.std(sct)))
print('scan time',time.time()-t0)

print('\n== POSITIVE CONTROLS: chain(EA-zero) on Markov plaintext, then transposition of the ciphertext (page-level) ==')
def control(name,tf,reps=3):
    global GEN
    zid=[];best=[]
    for _ in range(reps):
        pg=[]
        for n in [len(p) for p in PAGES]:
            c=chain(markov_plain(n,rng),rng,1); pg.append(c[tf(n)])
        t,npr=scan(pg); z=zof(t,npr,p0_of(pg)); zid.append(z['identity'])
        b=min((z[k],k) for k in GEN)
        best.append(b)
    print('%-40s reading-order z %6.1f | best reordering: %s'%(name,np.mean(zid),'; '.join('%s z=%.1f'%(k,v) for v,k in best)))
control('no transposition',lambda n:np.arange(n))
control('columnar w=13 (read cols)',lambda n:col_order(n,13,0,0))
control('columnar w=7 reversed cols, up',lambda n:col_order(n,7,1,1))
control('rail fence r=5',lambda n:rail_order(n,5))
control('serpentine w=17',lambda n:serp_order(n,17))
control('block reversal b=6',lambda n:blockrev(n,6))
control('columnar w=29 (alphabet width)',lambda n:col_order(n,29,0,0))
