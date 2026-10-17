import sys, pickle, numpy as np, time
from stats import *
from variants import *
rng=np.random.default_rng(12345)
NWIN=100
C=pickle.load(open(HERE+'/streams.pkl','rb'))
uq=Seq(unsolved_seq()); uc=uq.counts()
def valid_sent(q): return 3<=q.slen.mean()<=60 and q.ns>=200
def score(q,uc):
    gc=q.counts()
    vs=valid_sent(q)
    jsv=[js(uc[i],gc[i]) for i in range(5)]
    # windows
    wj=[[] for _ in range(5)]
    tries=0
    while len(wj[0])<NWIN and tries<NWIN*5:
        tries+=1
        s0=int(rng.integers(0,q.ns)); s1=int(np.searchsorted(q.starts,q.starts[s0]+2896))
        if s1>q.ns: continue
        w0,w1=q.starts[s0],q.starts[s1]
        cA=q.counts(w0,w1,s0,s1)
        # sentence stats from a fresh 175-sentence window
        if vs and q.ns>=175:
            t0=int(rng.integers(0,q.ns-175+1)); cS=q.counts(q.starts[t0],q.starts[t0+175],t0,t0+175)
        else: cS=cA
        for i in (0,1): wj[i].append(js(cA[i],gc[i]))
        for i in (2,3,4): wj[i].append(js(cS[i],gc[i]))
    mu=np.array([np.mean(x) for x in wj]); sd=np.array([max(np.std(x),1e-5) for x in wj])
    jsa=np.array(jsv); z=(jsa-mu)/sd
    pw=np.array([np.mean(np.array(wj[i])>=jsa[i]) for i in range(5)])
    return dict(js=jsa,mu=mu,sd=sd,z=z,pw=pw,valid=vs,gc=gc,nw=q.nw,ns=q.ns,meanlen=float(q.L.mean()),meansent=float(q.slen.mean()))
R={}
t0=time.time()
for name,(st,lang,reg) in C.items():
    q=seq_from_stream(st); r=score(q,uc); r.update(lang=lang,reg=reg,variant='natural'); R[(name,'natural')]=r
print('natural done',time.time()-t0,flush=True)
ENG=[n for n,(st,l,r) in C.items() if l=='en' and r!='verse']
for name in ENG:
    st=C[name][0]; lang,reg=C[name][1],C[name][2]
    for lab,rem,mode,arch in VARIANTS:
        s=archaic(st) if arch else st
        q=seq_from_stream(s,rem,mode); r=score(q,uc); r.update(lang=lang,reg=reg,variant=lab); R[(name,lab)]=r
    print(name,time.time()-t0,flush=True)
pickle.dump(dict(R=R,uc=uc),open(HERE+'/results_main.pkl','wb'))
