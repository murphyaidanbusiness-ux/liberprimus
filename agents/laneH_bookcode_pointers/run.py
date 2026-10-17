import sys, os, pickle, time, numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from multiprocessing import Pool
from engine import *
from sources import lp2_sources, build_sources, chain_runes, lp2_raw
NSH=50; NRD=50; NCH=50
HERE=os.path.dirname(os.path.abspath(__file__))
G={}
def init():
    G['V']=views(); G['pmi']=PMI(G['V'])
    src,idx,st=lp2_sources(); G['src']=src
    rng=np.random.default_rng(20261009)
    nulls={}
    for k,a in src.items():
        sh=[rng.permutation(a) for _ in range(NSH)]
        rd=[rng.integers(a.min(),a.max()+1,size=len(a),dtype=np.int64) for _ in range(NRD)]
        nulls[k]=sh+rd
    idx0,starts0=lp2_raw()
    for j in range(NCH):
        cs=build_sources(chain_runes(len(idx0),rng),starts0)
        for k in src: nulls[k].append(cs[k])
    G['nulls']=nulls
def one_view(vname):
    V=G['V'][vname]; pmi=G['pmi']; vid=pmi.vid(V)
    rows=[]
    t0=time.time()
    for sname,a in G['src'].items():
        for sem in SEMS:
            if sname.startswith('wt') and not (sem.startswith('T') and len(sem)-1==int(sname[2])): continue
            cum=sem in ('Lcum','Wcum')
            for b in ((0,) if cum else (0,1)):
                for mode in (('mod',) if cum else ('mod','raw')):
                    if mode=='raw' and sem in ('Lcum','Wcum'): continue
                    try:
                        r=apply_semantic(V,sem,a,b,mode)
                    except Exception as e:
                        print('ERR',vname,sname,sem,e); continue
                    if r is None: continue
                    kind,arr=r
                    real=score_output(V,kind,arr,pmi,vid)
                    nlen=len(arr)
                    nulls={k:[] for k in real}
                    for na in G['nulls'][sname]:
                        rr=apply_semantic(V,sem,na,b,mode)
                        if rr is None: 
                            for k in real: nulls[k].append(np.nan)
                            continue
                        o=score_output(V,rr[0],rr[1],pmi,vid)
                        for k in real: nulls[k].append(o[k])
                    for k in real:
                        rows.append(dict(view=vname,src=sname,sem=sem,b=b,mode=mode,score=k,real=real[k],nulls=np.array(nulls[k]),nout=nlen))
    pickle.dump(rows,open(f'{HERE}/results/{vname}.pkl','wb'))
    return vname,len(rows),time.time()-t0
if __name__=='__main__':
    names=sys.argv[1:] 
    Vtmp=views()
    if not names: names=sorted(Vtmp.keys(),key=lambda n:-Vtmp[n].nL)
    with Pool(4,initializer=init) as p:
        for r in p.imap_unordered(one_view,names): print(r,flush=True)
