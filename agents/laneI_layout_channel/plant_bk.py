import numpy as np, pickle, json
import booksc, core, channels as ch
MSG="ALLTHINGSMUSTPASSTHETRUTHISHIDDENINPLAINSIGHTSEEKANDYEWILLFINDIT"[:60]
idx=[ord(c)-65 for c in MSG]
d=pickle.load(open('out_BK_SW.pkl','rb')); Nl=d['nulls'].astype(np.float64); mu=Nl.mean(0); sd=Nl.std(0); ok=sd>1e-9
zn=np.where(ok[None],(Nl-mu)/np.where(ok,sd,1),-99); nm=zn.max(1)
res=[]
for tn,pos in (('SR',0),('LP1',0)):
    letters=booksc.TEXTS[tn][1]
    for seed in range(5):
        rng=np.random.default_rng(900+seed)
        x=ch.sw.copy()
        s=int(rng.integers(0,len(x)-60))
        for j,i in enumerate([ord(c)-65 for c in (MSG if tn=="SR" else MSG.replace("K","C"))]):
            cands=np.flatnonzero(letters[:200]==i)
            if len(cands)==0: cands=np.flatnonzero(letters[:1800]==i)
            x[s+j]=int(rng.choice(cands))
        labs,rows,prs=booksc.evalb(x,'SW')
        R=rows[:,:5]; z=np.where(ok,(R-mu)/np.where(ok,sd,1),-99)
        k=int(np.argmax(z[:,1])); want='%s letter#n+0 mod'%tn
        kw=[i for i,l in enumerate(labs) if want in l][0]
        print(tn,seed,'best Qwin z=%.1f [%s]; planted cell [%s] z=%.1f ; null max p95 %.1f max %.1f'%(z[k,1],labs[k],labs[kw],z[kw,1],np.percentile(nm[:,1],95),nm[:,1].max()),flush=True)
        res.append(dict(text=tn,seed=seed,bestz=float(z[k,1]),best=labs[k],plantz=float(z[kw,1]),p95=float(np.percentile(nm[:,1],95)),mx=float(nm[:,1].max())))
json.dump(res,open('plant_bk.json','w'),indent=1)
