import pickle, glob, numpy as np, sys, collections, json
HERE='./agents/laneH_bookcode_pointers'
rows=[]
for f in glob.glob(HERE+'/results/*.pkl'):
    if f.endswith('controls.pkl'): continue
    rows+=pickle.load(open(f,'rb'))
print(len(rows),'rows')
def fam(sem):
    if sem in ('L','Lp','Lpi','S1'): return 'letter-ptr'
    if sem in ('W','Wp','Wpi'): return 'word-ptr'
    if sem in ('Lcum','Wcum'): return 'cumulative'
    return 'tuple%d'%(len(sem)-1)
MINV=20
def zs(r):
    n=r['nulls']; sh=n[:50]; rd=n[50:100]; ch=n[100:150]
    out={}
    for nm,arr in (('sh',sh),('rd',rd),('ch',ch)):
        a=arr[~np.isnan(arr)]
        if len(a)<MINV or np.isnan(r['real']) or a.std()==0:
            out[nm]=(np.nan,None); continue
        z=(r['real']-a.mean())/a.std()
        # leave-one-out z for each null replicate
        loo=np.full(len(arr),np.nan)
        for i,x in enumerate(arr):
            if np.isnan(x): continue
            o=np.delete(arr,i); o=o[~np.isnan(o)]
            if len(o)>=MINV-1 and o.std()>0: loo[i]=(x-o.mean())/o.std()
        out[nm]=(z,loo)
    return out
for r in rows:
    z=zs(r); r['z_sh'],r['loo_sh']=z['sh']; r['z_rd'],r['loo_rd']=z['rd']; r['z_ch'],r['loo_ch']=z['ch']
    r['fam']=fam(r['sem'])
pickle.dump(rows,open(HERE+'/results/_analyzed.pkl','wb'))
def cellstat(rs,key='sh'):
    """real max z, and null max-z array (len50) over rows rs"""
    zr=[r['z_'+key] for r in rs if not np.isnan(r['z_'+key])]
    if not zr: return np.nan,None
    L=[r['loo_'+key] for r in rs if r['loo_'+key] is not None]
    nm=np.nanmax(np.vstack(L),axis=0) if L else None
    return max(zr),nm
def table(group_keys, label):
    g=collections.defaultdict(list)
    for r in rows: g[tuple(r[k] for k in group_keys)].append(r)
    out=[]
    for k,rs in sorted(g.items()):
        zs_,nm_s=cellstat(rs,'sh'); zr_,nm_r=cellstat(rs,'rd')
        out.append((k,len(rs),zs_,None if nm_s is None else (np.nanmax(nm_s),np.nanmean(nm_s),np.nanstd(nm_s)),zr_,None if nm_r is None else (np.nanmax(nm_r),np.nanmean(nm_r),np.nanstd(nm_r))))
    return out
if __name__=='__main__':
    top=sorted([r for r in rows if not np.isnan(r['z_sh'])],key=lambda r:-r['z_sh'])[:30]
    print('TOP 30 by z vs shuffle')
    for r in top: print(f"{r['view']:13s} {r['src']:10s} {r['sem']:6s} b={r['b']} {r['mode']:3s} {r['score']:9s} real={r['real']:.3f} z_sh={r['z_sh']:.2f} z_rd={r['z_rd']:.2f} n={r['nout']}")
    top=sorted([r for r in rows if not np.isnan(r['z_rd'])],key=lambda r:-r['z_rd'])[:15]
    print('TOP 15 by z vs random')
    for r in top: print(f"{r['view']:13s} {r['src']:10s} {r['sem']:6s} b={r['b']} {r['mode']:3s} {r['score']:9s} real={r['real']:.3f} z_sh={r['z_sh']:.2f} z_rd={r['z_rd']:.2f} n={r['nout']}")
    allz=np.array([r['z_sh'] for r in rows if not np.isnan(r['z_sh'])]); print('n rows',len(allz),'max',allz.max(),'frac>3',(allz>3).mean(),'frac>4',(allz>4).mean())
    # global null max
    L=np.vstack([r['loo_sh'] for r in rows if r['loo_sh'] is not None]); nm=np.nanmax(L,axis=0)
    print('global: real max z',allz.max(),'; null max z over 50 shuffle replicates: max',nm.max(),'mean',nm.mean(),'sd',nm.std())
