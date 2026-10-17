import sys, numpy as np, time, pickle
import channels as ch
from multiprocessing import Pool
nrep=int(sys.argv[2]) if len(sys.argv)>2 else 200
names=sys.argv[1].split(',')
def job(a):
    name,seed=a
    c=ch.CH[name]
    rng=np.random.default_rng(1000+seed)
    labs,rows,prs=ch.evaluate(c,c.null(rng))
    return rows.astype(np.float32)
if __name__=='__main__':
    for name in names:
        t=time.time(); c=ch.CH[name]
        labs,rows,prs=ch.evaluate(c,c.real())
        with Pool(4) as p: nulls=p.map(job,[(name,s) for s in range(nrep)],chunksize=4)
        nulls=np.stack(nulls)
        pickle.dump(dict(labs=labs,real=rows,prs=prs,nulls=nulls),open('out_%s.pkl'%name,'wb'))
        print(name,len(labs),'cells',nrep,'nulls %.0fs'%(time.time()-t),flush=True)
