import pickle, numpy as np, sys, glob, os, json
STATS=['Qall','Qwin','IoC','Hall','Hwin']
NMIN=30
def fam(name):
    d=pickle.load(open('out_%s.pkl'%name,'rb'))
    if len(d['labs'])==0: return None
    labs=d['labs']; R=d['real'][:,:5].astype(np.float64); Nl=d['nulls'][:,:,:5].astype(np.float64)
    n=d['real'][:,5]
    nn_=np.median(d['nulls'][:,:,5],axis=0) if d['nulls'].shape[2]>5 else n
    out={}
    # minimum informative length: n>=60 for window stats otherwise still fine
    for j,s in enumerate(STATS):
        mu=Nl[:,:,j].mean(0); sd=Nl[:,:,j].std(0)
        nmin=100 if s=='IoC' else NMIN
        ok=(sd>1e-9)&(n>=nmin)&(nn_>=nmin)
        z=np.where(ok,(R[:,j]-mu)/np.where(ok,sd,1),-99)
        zn=np.where(ok[None,:],(Nl[:,:,j]-mu)/np.where(ok,sd,1)[None,:],-99)
        nm=zn.max(1)       # per-null max over cells
        k=int(np.argmax(z)); zmax=float(z[k])
        p=(1+int((nm>=zmax).sum()))/(1+len(nm))
        out[s]=dict(zmax=zmax,label=labs[k],null_max_mean=float(nm.mean()),null_max_p95=float(np.percentile(nm,95)),null_max_max=float(nm.max()),p=p,real=float(R[k,j]),null_mu=float(mu[k]),null_sd=float(sd[k]),idx=k)
    return dict(ncells=len(labs),nrep=Nl.shape[0],out=out,labs=labs,R=R,n=n)
if __name__=='__main__':
    res={}
    for f in sorted(glob.glob('out_*.pkl')):
        nm=f[4:-4]; r_=fam(nm)
        if r_ is not None: res[nm]=r_
    json.dump({k:dict(ncells=v['ncells'],nrep=v['nrep'],out=v['out']) for k,v in res.items()},open('summary.json','w'),indent=1)
    for k,v in res.items():
        print(k,v['ncells'],'cells',v['nrep'],'nulls')
        for s in STATS:
            o=v['out'][s]; print('   %-5s zmax=%6.2f p=%.4f nullmax mean %.2f p95 %.2f max %.2f | %s (real %.4f null %.4f+-%.4f)'%(s,o['zmax'],o['p'],o['null_max_mean'],o['null_max_p95'],o['null_max_max'],o['label'],o['real'],o['null_mu'],o['null_sd']))
