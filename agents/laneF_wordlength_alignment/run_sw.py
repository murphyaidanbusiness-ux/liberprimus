# Full (unseeded) Smith-Waterman of every section target against the whole library, per variant.
# Lanes: 0 real | 1..23 shuffles | 24..27 held-out English | 28..31 planted positive controls.
import sys, os, time, json, numpy as np, core
from multiprocessing import Pool
OUT=core.HERE+'/sw_out'; os.makedirs(OUT,exist_ok=True)
T,PG,CH=core.target(); SECS=core.sections(PG)
KEY=[('base','none',0),('base','mF',2),('base','mP',2),('base','drop',2),('base','drop',3),('letters','none',0)]
PLANT_SRC=['self_reliance','emerson_essays_first','agrippa_occult_philosophy_book1','plato_republic_jowett','gospel_of_buddha','paine_age_of_reason','cicero_tusculan','crowley_book_of_lies','melville_moby_dick','upanishads']
def plant_lanes(s, m):
    lib=core.lib(); names=lib['names']; st=lib['starts']; tok=lib['tok']
    rng=np.random.default_rng(777+s)
    src=[i for i,n in enumerate(names) if PLANT_SRC[s%len(PLANT_SRC)] in n][0]
    a,b=st[src],st[src+1]-1
    off=int(rng.integers(a,b-3*m-10)); win=tok[off:off+3*m]
    mf=core.variant_stream(('base','mF',2),win)[:m]
    dr=core.variant_stream(('base','drop',2),win)[:m]
    bs=core.variant_stream(('base','none',0),win)[:m]
    marg=T.astype(int)
    nz=mf.astype(int).copy(); flip=rng.random(m)<0.15; nz[flip]=rng.choice(marg,flip.sum())
    meta=dict(src=names[src],src_idx=src,tok_off=int(off-a))
    return [mf,dr,bs,nz],meta
def null_lanes(s,m):
    lib=core.lib(); rng=np.random.default_rng(555+s); out=[]
    for k,(pool,v) in enumerate([(lib['hold'],('base','mF',2)),(lib['ewt'],('base','mF',2)),(lib['hold'],('base','drop',3)),(lib['ewt'],('base','drop',3))]):
        off=int(rng.integers(0,len(pool)-3*m-10)); out.append(core.variant_stream(v,pool[off:off+3*m])[:m])
    return out
def job(args):
    v,mode=args; name=core.vname(v); fn=OUT+'/%s__%s.npz'%(name,mode)
    if os.path.exists(fn): return fn
    t0=time.time(); L=core.variant_stream(v); ntext=len(core.lib()['names'])
    res={}
    targets=[('whole',np.arange(len(T)))] if mode=='whole' else [('s%d'%i,ix) for i,ix in enumerate(SECS)]
    for sname,ix in targets:
        tgt=T[ix]; m=len(tgt); s=int(sname[1:]) if sname!='whole' else 99
        p=0 if mode in('p0','whole') else int(mode[1:])
        rng=np.random.default_rng(1000*p+s)
        if mode in ('p0','whole'):
            lanes=[tgt]+[rng.permutation(tgt) for _ in range(23)]+null_lanes(s,m)
            pl,meta=plant_lanes(s,m); lanes+=pl; res[sname+'_meta']=json.dumps(meta)
        else:
            lanes=[rng.permutation(tgt) for _ in range(32)]
        b,j=core.sw32(L,lanes,ntext); res[sname+'_best']=b; res[sname+'_j']=j
    np.savez_compressed(fn,**res); print(name,mode,'%.0fs'%(time.time()-t0),flush=True); return fn
if __name__=='__main__':
    which=sys.argv[1]
    if which=='p0': jobs=[(v,'p0') for v in core.variant_list()]
    elif which=='extra': jobs=[(v,'p%d'%p) for p in range(1,7) for v in KEY]
    elif which=='whole': jobs=[(v,'whole') for v in KEY]
    elif which=='test': jobs=[(('base','mF',2),'p0')]
    jobs=[j for j in jobs if not os.path.exists(OUT+'/%s__%s.npz'%(core.vname(j[0]),j[1]))]
    with Pool(4) as P:
        for r in P.imap_unordered(job,jobs): pass
