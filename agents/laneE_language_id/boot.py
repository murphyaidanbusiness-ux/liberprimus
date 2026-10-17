import pickle, numpy as np, collections, json
from stats import *
from variants import VARIANTS
d=pickle.load(open('results_main.pkl','rb')); R=d['R']
rng=np.random.default_rng(777)
sents=unsolved_seq()
# per-sentence count matrices for unsolved
mats=[[] for _ in range(5)]
for s in sents:
    q=Seq([s]); c=q.counts()
    for i in range(5): mats[i].append(c[i])
M=[np.array(m,float) for m in mats]    # 175 x bins
keys=[k for k,r in R.items() if r['nw']>=15000]
# candidate dists
P=[np.array([r['gc'][i]/r['gc'][i].sum() for k,r in ((k,R[k]) for k in keys)]) for i in range(5)]
valid=np.array([R[k]['valid'] for k in keys])
def jsmat(cnt,Pm):
    p=cnt/cnt.sum(); m=(p[None,:]+Pm)/2
    with np.errstate(divide='ignore',invalid='ignore'):
        t1=np.where(p[None,:]>0,p[None,:]*np.log(p[None,:]/m),0).sum(1)
        t2=np.where(Pm>0,Pm*np.log(Pm/m),0).sum(1)
    return (t1+t2)/2
def js_all(w):
    return np.stack([jsmat(w@M[i],P[i]) for i in range(5)],1)   # ncand x 5
obs=js_all(np.ones(len(sents)))
# scale S_s: median over valid candidates
S_=np.median(obs[valid],0)
def comb(J):
    full=np.where(valid[:,None],J/S_,np.nan)
    cf=np.where(valid,np.nanmean(np.where(valid[:,None],J/S_,np.nan),1),(J[:,:2]/S_[:2]).mean(1))
    cw=(J[:,:2]/S_[:2]).mean(1)
    return cf,cw
cf0,cw0=comb(obs)
NB_=1000
CF=np.zeros((NB_,len(keys)));CW=np.zeros((NB_,len(keys)));JSb=np.zeros((NB_,len(keys),5))
n=len(sents)
for b in range(NB_):
    idx=rng.integers(0,n,n); w=np.bincount(idx,minlength=n).astype(float)
    J=js_all(w); cf,cw=comb(J); CF[b]=cf;CW[b]=cw;JSb[b]=J
pickle.dump(dict(keys=keys,obs=obs,S=S_,cf0=cf0,cw0=cw0,CF=CF,CW=CW,JSb=JSb,valid=valid),open('boot.pkl','wb'))
print('done',len(keys),S_)
