import sys, time, pickle, json
sys.path.insert(0,'.')
import numpy as np, multiprocessing as mp
import eng, ctrl, fam_solved as FS, lpdata
from eng import PRIMES
FS.OMAX=10**6
P=lpdata.load()
def words_of_page(k):
    p=P[k]; ids=p['word']; out=[]; cur=[]; prev=None
    for w,r in zip(ids,p['idx']):
        if prev is not None and w!=prev: out.append(cur); cur=[]
        cur.append(r); prev=w
    out.append(cur); return out
new={}
for nm,ks in (('P55',[55]),('P56',[56]),('P55+56',[55,56])):
    W=[w for k in ks for w in words_of_page(k)]
    r=np.array([x for w in W for x in w]); pv=PRIMES[r]
    new[nm+'.L.prime']=dict(arr=pv,dom='L',cum=False)
    new[nm+'.L.index']=dict(arr=r,dom='L',cum=False)
    new[nm+'.W.sum']=dict(arr=np.array([PRIMES[w].sum() for w in W]),dom='W',cum=False,words=W)
FS.SEQ.update(new)
NAMES=['PT.L.prime','PT.L.index','CT.L.prime','CT.L.index','PT.W.sum','CT.W.sum']+list(new)
st,c=eng.real_struct(); D0=eng.Data(c,st)
def get(s): return D0 if s==0 else eng.shuffle_data(D0,np.random.default_rng(1000+s))
def task(s):
    if s==-1:  # planted control at an offset beyond 500
        rng=np.random.default_rng(77)
        words,p,st2=ctrl.synth_plain(start=61000)
        d0=ctrl.dummy_data(p,st2)
        lab='PT.L.prime|L|rev0|rune-contA|m28'
        sp=[x for x in FS.specs(d0,names=NAMES) if x['label']==lab and x['form']==0][0]
        cc=ctrl.encrypt_with_spec(sp,p,2300,rng)
        res=FS.run_specs(FS.specs(eng.Data(cc,st2),names=NAMES))
        return s,{'planted':res[lab],'max_other':max(v[0] for k,v in res.items() if k!=lab)}
    d=get(s); t=time.time()
    r=FS.run_specs(FS.specs(d,names=NAMES))
    return s,r
if __name__=='__main__':
    out={}
    with mp.Pool(4) as pool:
        for s,r in pool.imap_unordered(task,[-1]+list(range(21))):
            out[s]=r; print(s,flush=True); pickle.dump(out,open('full_results.pkl','wb'))
