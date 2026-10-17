# Positive control (task item 4): 300 consecutive words of a library text, Cicada-transliterated,
# THE/OF merged into the following word; the full-SW pipeline (variant base_mF2) and the k-mer index
# must identify the source text and the offset. Also run the same plant against mismatched variants.
import numpy as np, core, json
from kmer import Index
lib=core.lib(); names=lib['names']; st=lib['starts']; tok=lib['tok']; ntext=len(names)
rng=np.random.default_rng(31337)
out={}
for srcname in ['emerson_essays_second_series','agrippa_occult_philosophy_book3']:
    src=[i for i,n in enumerate(names) if srcname in n][0]
    off=int(rng.integers(st[src]+1000, st[src+1]-2000))
    win=tok[off:off+600]
    for var in [('base','mF',2),('base','drop',2),('base','mP',2),('base','none',0),('letters','none',0)]:
        L=core.variant_stream(var)
        plant=core.variant_stream(('base','mF',2),win)[:300].astype(np.int16)
        lanes=[plant]+[np.random.default_rng(k).permutation(plant) for k in range(31)]
        b,j=core.sw32(L,lanes,ntext)
        real=b[:,0]; sh=b[:,1:].max(0)
        top=int(real.argmax()); z=(real.max()-sh.mean())/sh.std()
        # expected offset: position of the planted window in this variant's stream
        sepL=np.where(L==0)[0]; tstart=0 if top==0 else sepL[top-1]+1
        pre=core.variant_stream(var,tok[st[src]:off])
        jend=int(j[top,0])-tstart
        # traceback to get start offset of the alignment in the text
        W=L[max(tstart,j[top,0]-700):j[top,0]+1]; sc,path=core.traceback(W,plant)
        jstart=[q for p,q in path if q is not None][0]+max(tstart,j[top,0]-700)-tstart
        res=dict(variant=core.vname(var),src=names[src].split('/')[-1],found=names[top].split('/')[-1],score=int(real.max()),
                 second_text=int(np.sort(real)[-2]),shuffle_max=int(sh.max()),shuffle_mean=float(sh.mean()),z=float(z),
                 align_start_in_text=int(jstart),true_start_in_text=int(len(pre)))
        print(json.dumps(res),flush=True); out[(srcname,core.vname(var))]=res
    # k-mer index on the matched variant
    L=core.variant_stream(('base','mF',2)); plant=core.variant_stream(('base','mF',2),win)[:300]
    for k in (6,8):
        I=Index(L,k); r=I.stats(plant,ntext)
        shs=[I.stats(np.random.default_rng(100+q).permutation(plant),ntext) for q in range(50)]
        for stn in ('H','band','run'):
            v=np.array([s[stn] for s in shs]); print(json.dumps(dict(src=srcname,k=k,stat=stn,real=int(r[stn]),null_mean=float(v.mean()),null_sd=float(v.std()),null_max=int(v.max()),z=float((r[stn]-v.mean())/max(v.std(),1e-9)),band_text=names[r['band_text']].split('/')[-1] if stn=='band' else '')),flush=True)
