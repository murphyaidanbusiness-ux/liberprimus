import sys, os, pickle, numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from engine import *
from sources import *
HERE=os.path.dirname(os.path.abspath(__file__))
rows=pickle.load(open(HERE+'/results/_analyzed.pkl','rb'))
Vd=views(); pmi=PMI(Vd)
src,idx,st=lp2_sources()
idx0,starts0=lp2_raw()
rng=np.random.default_rng(99)
# vocabulary for word-hit
from collections import Counter
cnt=Counter()
for v in Vd.values():
    if v.name!='LP1_solved': cnt.update(v.words)
VOC={w for w,c in cnt.items() if c>=20 and len(w)>=4}
def wordhit(s):
    n=len(s); cov=np.zeros(n,bool)
    for L in range(4,10):
        for i in range(n-L+1):
            if s[i:i+L] in VOC: cov[i:i+L]=True
    return cov.mean()
def out_letters(V,kind,arr):
    return V.L[arr] if kind=='L' else word_letters(V,arr)
def txt(a): return ''.join(chr(65+x) for x in a)
def z_of(real,nl): nl=np.array(nl); return (real-nl.mean())/nl.std()
def finalist(r):
    V=Vd[r['view']]; a=src[r['src']]
    kind,arr=apply_semantic(V,r['sem'],a,r['b'],r['mode'])
    L=out_letters(V,kind,arr)[:3000]
    # first-letter readout for qfirst
    if r['score'] in ('qfirst','qfirstwin') : L=V.L[V.wstart[arr]][:3000]
    ioc=ioc26(L); wh=wordhit(txt(L[:3000]))
    nl_ioc=[];nl_wh=[]
    for j in range(30):
        na=rng.permutation(a); k2,ar2=apply_semantic(V,r['sem'],na,r['b'],r['mode'])
        L2=out_letters(V,k2,ar2)[:3000]
        if r['score'] in ('qfirst','qfirstwin'): L2=V.L[V.wstart[ar2]][:3000]
        nl_ioc.append(ioc26(L2)); nl_wh.append(wordhit(txt(L2)))
    return txt(L[:200]),ioc,wh,np.mean(nl_ioc),np.std(nl_ioc),np.mean(nl_wh),np.std(nl_wh),z_of(wh,nl_wh)
if __name__=='__main__':
    # top by z_sh and top by min(z_sh, z_ch)
    ok=[r for r in rows if not np.isnan(r['z_sh']) and not np.isnan(r['z_ch'])]
    ok.sort(key=lambda r:-min(r['z_sh'],r['z_ch']))
    seen=set(); fin=[]
    for r in ok:
        key=(r['view'][:2],r['src'],r['sem'],r['b'],r['score'])
        if key in seen: continue
        seen.add(key); fin.append(r)
        if len(fin)>=12: break
    out=[]
    for r in fin:
        t,ioc,wh,mi,si,mw,sw,zw=finalist(r)
        line=f"{r['view']} {r['src']} {r['sem']} b={r['b']} {r['mode']} {r['score']}: real={r['real']:.3f} z_sh={r['z_sh']:.2f} z_ch={r['z_ch']:.2f} z_rd={r['z_rd']:.2f} | IoC={ioc:.3f} (null {mi:.3f}+-{si:.3f}) wordhit={wh:.3f} (null {mw:.3f}+-{sw:.3f}, z={zw:.1f})\n   first200: {t}"
        print(line,flush=True); out.append(line)
    open(HERE+'/finalists.txt','w').write('\n'.join(out))

def refine(r,n=300):
    V=Vd[r['view']]; vid=pmi.vid(V); a=src[r['src']]
    def sc(arr):
        res=apply_semantic(V,r['sem'],arr,r['b'],r['mode'])
        if res is None: return np.nan
        return score_output(V,res[0],res[1],pmi,vid)[r['score']]
    real=sc(a)
    sh=[sc(rng.permutation(a)) for _ in range(n)]
    ch=[]
    for _ in range(n):
        cs=build_sources(chain_runes(len(idx0),rng),starts0)
        ch.append(sc(cs[r['src']]))
    sh=np.array(sh);ch=np.array(ch)
    return real,z_of(real,sh[~np.isnan(sh)]),z_of(real,ch[~np.isnan(ch)])
