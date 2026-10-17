import sys, numpy as np, pickle, time
import channels as ch, enc
from multiprocessing import Pool
def ev(c,data): return enc.stat_vec(enc.bdt_encodings(c.kind,data,c.name,c.kw.get('cb')))
def job(a):
    name,seed=a; c=ch.CH[name]; rng=np.random.default_rng(31000+seed)
    return ev(c,c.null(rng))[1].astype(np.float32)
if __name__=='__main__':
    nrep=200
    for name in sys.argv[1].split(','):
        c=ch.CH[name]; labs,rows,prs=ev(c,c.real())
        with Pool(4) as p: nulls=p.map(job,[(name,s) for s in range(nrep)],chunksize=8)
        pickle.dump(dict(labs=labs,real=rows,prs=prs,nulls=np.stack(nulls)),open('out_BDT_%s.pkl'%name,'wb')); print(name,len(labs),flush=True)
