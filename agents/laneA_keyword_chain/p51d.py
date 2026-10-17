# tail p-value for page-51 period-7 raw coset IoC, and look-elsewhere: max over 55 pages x periods 2..40 under shuffles
import common, numpy as np
U,C=common.pages(); rng=np.random.default_rng(4242)
def cioc_batch(X,L,m=29):
    # X: (B,n)
    B,n=X.shape; tot=np.zeros(B); 
    for j in range(L):
        col=X[:,j::L]; k=col.shape[1]
        H=np.zeros((B,m)); np.add.at(H,(np.repeat(np.arange(B),k),col.ravel()),1)
        tot+=(H*(H-1)).sum(1)/(k*(k-1))*m
    return tot/L
pg=[p for p in U if p['page']==51][0]; c=np.array(pg['idx'])
r=cioc_batch(c[None,:],7)[0]
cnt=0;tot=0;allv=[]
for b in range(20):
    X=np.array([rng.permutation(c) for _ in range(5000)]); v=cioc_batch(X,7); allv.append(v); cnt+=(v>=r).sum(); tot+=len(v)
allv=np.concatenate(allv)
print('page51 L7 raw IoC %.4f: %d of %d shuffles >= real -> p=%.2e ; null mean %.3f sd %.3f'%(r,cnt,tot,max(cnt,1)/tot,allv.mean(),allv.std()))
# per-test p-values for all pages x L=2..40 (empirical with 2000 shuffles each is costly); use the p for page51 and Bonferroni count
ntests=55*39
print('tests in the scan (55 pages x 39 periods, raw only): %d ; Bonferroni-adjusted p <= %.3f'%(ntests,min(1,ntests*max(cnt,1)/tot)))
