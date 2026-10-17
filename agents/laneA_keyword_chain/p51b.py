import common, numpy as np, collections
U,C=common.pages()
pg=[p for p in U if p['page']==51][0]; c=np.array(pg['idx']); n=len(c)
def cioc(x,L,m=29):
    tot=0;cnt=0
    for j in range(L):
        col=x[j::L]; k=len(col); h=np.bincount(col,minlength=m); tot+=(h*(h-1)).sum()/(k*(k-1))*m; cnt+=1
    return tot/cnt
rng=np.random.default_rng(777)
r=cioc(c,7); nl=np.array([cioc(rng.permutation(c),7) for _ in range(5000)])
print('L7 raw coset IoC %.3f; 5000-shuffle null mean %.3f sd %.3f max %.3f; p=%.4f z=%.2f'%(r,nl.mean(),nl.std(),nl.max(),(nl>=r).mean(),(r-nl.mean())/nl.std()))
# halves
for a,b in ((0,n//2),(n//2,n)):
    x=c[a:b]; rr=cioc(x,7); nn=np.array([cioc(rng.permutation(x),7) for _ in range(1000)])
    print(' half %d-%d: %.3f null %.3f+-%.3f p=%.3f'%(a,b,rr,nn.mean(),nn.std(),(nn>=rr).mean()))
# line structure
lines=collections.Counter(pg['line']); print('line lengths', [lines[k] for k in sorted(lines)])
words=collections.Counter(pg['word']); print('word count',len(words))
# per-coset dominant runes at L=7
for j in range(7):
    col=c[j::7]; h=np.bincount(col,minlength=29); top=np.argsort(-h)[:4]
    print(' coset',j,len(col),[(common.TR[t],int(h[t])) for t in top], 'IoC %.2f'%(29*(h*(h-1)).sum()/(len(col)*(len(col)-1))))
# kappa at lag 7,14,21,28 vs others
for lag in (7,14,21,28,35):
    k=(c[lag:]==c[:-lag]).mean(); print(' kappa lag',lag,'%.4f (random 0.0345, n=%d)'%(k,n-lag))
ks=[(c[l:]==c[:-l]).mean() for l in range(1,80)]
print(' top kappa lags', sorted(range(1,80),key=lambda l:-ks[l-1])[:8], ['%.3f'%ks[l-1] for l in sorted(range(1,80),key=lambda l:-ks[l-1])[:8]])
# neighbouring pages at L=7
for p in U:
    if p['page'] in (48,49,50,52,53):
        x=np.array(p['idx']); rr=cioc(x,7); nn=np.array([cioc(rng.permutation(x),7) for _ in range(500)]); print(' page',p['page'],len(x),'L7 %.3f z %.2f'%(rr,(rr-nn.mean())/nn.std()))
