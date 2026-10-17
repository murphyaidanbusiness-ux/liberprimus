import pickle, glob, sys, math
import numpy as np
import core, gens
from core import *
def load(p):
    return pickle.load(open(p,'rb'))
def hstats(h):
    c=np.arange(1000)*0.0001+0.98+0.00005
    n=h.sum()
    if n==0: return (0,0,0,0)
    mu=(h*c).sum()/n; sd=math.sqrt(((h*(c-mu)**2).sum())/n)
    nz=np.nonzero(h)[0]; return (n,mu,sd,c[nz[-1]])
def merged_null(prefix):
    fs=sorted(glob.glob(HERE+'/res_%s_null_*.pkl'%prefix))
    hist={}; ntr=0; ns=0; pm=[]; tops=[]; ptops=[]
    for f in fs:
        st=load(f)
        ntr+=st['ntr']; ns+=st['nstreams']
        for g,h in st['hist'].items(): hist[g]=hist.get(g,0)+h
        pm.append(st['pmax'])
        tops.append(sorted(st['top_w'],reverse=True)[:3]); ptops.append(sorted(st['top_p'],reverse=True)[:3])
    return dict(n=len(fs),ntr=ntr,ns=ns,hist=hist,pmax=np.array(pm) if pm else None,tops=tops,ptops=ptops)
def fmt_meta(meta,m,a,md):
    lab,sd,gt,hn,koff=meta
    sdr=sd if len(sd)<=40 else sd[:37]+b'...'
    return 'seed=%r[%s] gen=%s/%s koff=%d map=%s app=%s mode=%s'%(sdr,lab,gt,hn,koff,MAPS[m][0],APPS[a]['name'],('cont','restart','perpage')[md])
def report(name, st, null):
    L=[]
    L.append('### %s'%name)
    L.append('streams=%d  trials=%d  elapsed=%.0fs'%(st['nstreams'],st['ntr'],st.get('elapsed',0)))
    for g,h in st['hist'].items():
        n,mu,sd,mx=hstats(h)
        L.append('  real %s group: n=%d mean IoC=%.5f sd=%.5f max(bin)=%.4f'%(g,n,mu,sd,mx))
        if null and g in null['hist']:
            nn,nmu,nsd,nmx=hstats(null['hist'][g])
            L.append('  null %s group (%d shuffles, %d trials): mean=%.5f sd=%.5f max(bin)=%.4f'%(g,null['n'],nn,nmu,nsd,nmx))
    top=sorted(st['top_w'],reverse=True)[:8]
    ntop=null['tops'] if null else []
    nmax=max([t[0][0] for t in ntop if t],default=None)
    L.append('  top real configs by whole-corpus IoC (null per-shuffle max: %s):'%(('%.4f'%nmax) if nmax else 'n/a'))
    for (v,w,p,meta,m,a,md) in top:
        grp='chain' if MAPS[m][1]==28 else 'otp'
        z=''
        if null and grp in null['hist']:
            nn,nmu,nsd,nmx=hstats(null['hist'][grp]); z=' z=%.1f'%((w-nmu)/nsd)
        L.append('    IoC=%.4f prefix3000=%.4f%s  %s'%(w,p,z,fmt_meta(meta,m,a,md)))
    top=sorted(st['top_p'],reverse=True)[:3]
    if null: L.append('  null pooled max of first-3000-rune IoC: %.4f ; null per-shuffle maxima: %s'%(max(t[0][0] for t in null['ptops']), sorted(round(t[0][0],4) for t in null['ptops'])[-5:]))
    L.append('  top by first-3000-rune IoC:')
    for (v,w,p,meta,m,a,md) in top: L.append('    prefix=%.4f whole=%.4f %s'%(p,w,fmt_meta(meta,m,a,md)))
    L.append('  per-page max IoC over all trials: real mean-over-pages %.3f max %.3f; null (per-shuffle) mean-over-pages %.3f max-over-shuffles %.3f'%(
        st['pmax'].mean(), st['pmax'].max(), null['pmax'].mean() if null and null['pmax'] is not None else float('nan'), null['pmax'].max() if null and null['pmax'] is not None else float('nan')))
    if null and null['pmax'] is not None:
        L.append('  pages where real per-page max exceeds the pooled null max (null trials %d vs real %d; chance expectation %.1f of 55): %d'%(null['ntr'],st['ntr'],55*st['ntr']/(st['ntr']+null['ntr']),int((st['pmax']>null['pmax'].max(axis=0)).sum())))
        # per-page z: real page max vs distribution of null page maxima over shuffles
        mu=null['pmax'].mean(axis=0); sd=null['pmax'].std(axis=0)+1e-9
        z=(st['pmax']-mu)/sd
        L.append('  per-page z of real max vs null max (n=%d shuffles): max z=%.2f (page %d), mean z=%.2f; pages with real max > every null max: %d / 55'%(null['n'],z.max(),int(z.argmax()),z.mean(),int((st['pmax']>null['pmax'].max(axis=0)).sum())))
    return '\n'.join(L)
if __name__=='__main__':
    out=[]
    for tag,real in (('G','res_G_real_k0.pkl'),('G1','res_G_real_k1.pkl'),('P','res_P_real_k0.pkl'),('PB','res_PB_real.pkl')):
        try: st=load(HERE+'/'+real)
        except Exception as e: continue
        nl=merged_null('P' if tag=='P' else 'G')
        out.append(report(real,st,nl if nl['n'] else None))
    print('\n\n'.join(out))

import seeds
_Pf=None
def decode_item(item, corp=None):
    global _Pf
    (v,w,p,meta,m,a,md)=item
    corp=corp or REAL
    lab,sd,gt,hn,koff=meta
    if md==2:
        if _Pf is None: seeds.build_G(); _Pf=dict(seeds.build_P())
        f=_Pf[lab]
        keys=np.zeros(corp.KLP,dtype=np.uint8)
        for pg in range(corp.npages):
            L=len(corp.pages[pg])+8
            data,hl=gens.stream(gt,hn,f(pg),L*2+200)
            res=make_keys(data,hl,L); off=int(corp.pkoff[pg]); keys[off:off+L]=res[MAPS[m][0]]
        return decode_cfg(corp,keys,a,md,koff,corp.pkoff)
    KL=corp.n+16
    data,hl=gens.stream(gt,hn,sd,KL+800); res=make_keys(data,hl,KL)
    return decode_cfg(corp,res[MAPS[m][0]],a,md,koff)
def qg_report(st, n=5, corp=None):
    L=[]
    top=sorted(st['top_w'],reverse=True)[:n]
    for it in top:
        out=decode_item(it,corp)
        q=qscore(list(out))
        L.append('    quadgram %.3f IoC(check)=%.4f | %s'%(q,it[1],text_of(list(out[:60]))))
    return '\n'.join(L)
