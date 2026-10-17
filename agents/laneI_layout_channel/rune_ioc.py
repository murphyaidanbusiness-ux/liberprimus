import numpy as np, channels as ch, core, json
import sys
sys.path.insert(0,core.S+'/lp')
def ioc(v,m=29):
    c=np.bincount(v,minlength=m); n=len(v); return m*float((c*(c-1)).sum())/(n*(n-1))
# quadgram on rune-level translit letters (no shift) and also best shift
import enc
out={}
rng=np.random.default_rng(11)
for nm in ('FW','LWr','FL','LLr','FS','LS','FP','LP'):
    c=ch.CH[nm]; v=c.real()
    r=ioc(v)
    nul=[ioc(c.null(rng)) for _ in range(300)]
    # doublet rate and chi2 vs uniform
    cnt=np.bincount(v,minlength=29); chi=((cnt-len(v)/29)**2/(len(v)/29)).sum()
    dbl=float((v[1:]==v[:-1]).mean())
    # best quad over 58 maps
    best=max(core.letter_stats(L)['Qall'] for lab,L in enc.map_variants(v,nm,s26=False))
    bn=[max(core.letter_stats(L)['Qall'] for lab,L in enc.map_variants(c.null(rng),nm,s26=False)) for _ in range(40)]
    out[nm]=dict(n=len(v),IoC=r,null_mean=float(np.mean(nul)),null_sd=float(np.std(nul)),z=float((r-np.mean(nul))/np.std(nul)),chi2_28=float(chi),doublet=dbl,bestQ=float(best),nullQ_mean=float(np.mean(bn)),nullQ_sd=float(np.std(bn)),Qz=float((best-np.mean(bn))/np.std(bn)))
    print(nm,{k:(round(v,3) if isinstance(v,float) else v) for k,v in out[nm].items()},flush=True)
json.dump(out,open('rune_ioc.json','w'),indent=1)
