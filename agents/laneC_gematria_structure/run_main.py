import sys, json, time, pickle
sys.path.insert(0,'.')
import numpy as np, multiprocessing as mp
import eng, fam_solved as FS, fam_self as FSELF, fam_auto as FA
NNULL=int(sys.argv[1]) if len(sys.argv)>1 else 20
FAMS=sys.argv[2].split(',') if len(sys.argv)>2 else ['solved','self','auto']
st,c=eng.real_struct(); D0=eng.Data(c,st)
def get_data(s):
    if s==0: return D0
    return eng.shuffle_data(D0,np.random.default_rng(1000+s))
def task(a):
    fam,s=a
    d=get_data(s); t=time.time()
    if fam=='solved': r=FS.run_specs(FS.specs(d))
    elif fam=='self': r=FS.run_specs(FSELF.specs(d))
    else: r=FA.run_all(d)
    return fam,s,r,time.time()-t
if __name__=='__main__':
    tasks=[(f,s) for s in range(NNULL+1) for f in FAMS]
    out={}
    with mp.Pool(4) as pool:
        for fam,s,r,secs in pool.imap_unordered(task,tasks):
            out[(fam,s)]=r
            print(fam,s,'%.0fs'%secs,flush=True)
            pickle.dump(out,open('main_results_%s.pkl'%'_'.join(FAMS),'wb'))
