# k-mer index statistics (k=6, 8) of the word-length target vs the library, per variant and section,
# with 200 target-order shuffles, 20 held-out-English windows and a planted positive control as nulls/controls.
import sys, os, time, pickle, numpy as np, core
from run_sw import plant_lanes
T,PG,CH=core.target(); SECS=core.sections(PG)
TG=[('s%d'%i,ix) for i,ix in enumerate(SECS)]+[('whole',np.arange(len(T)))]
NSH=200; NHE=20; BAND=64
OUT=core.HERE+'/kmer_out'; os.makedirs(OUT,exist_ok=True)
def codes(a,k):
    a=a.astype(np.uint64); n=len(a); c=np.zeros(n,np.uint64)
    for t in range(k):
        c[:n-t]|=a[t:]<<np.uint64(4*t)
    c[n-k+1:]=0
    return c
def heldout(m,seed):
    lib=core.lib(); rng=np.random.default_rng(seed); out=[]
    for k in range(NHE):
        pool=lib['hold'] if k%2==0 else lib['ewt']; v=('base','mF',2) if (k//2)%2==0 else ('base','drop',3)
        off=int(rng.integers(0,len(pool)-3*m-10)); out.append(core.variant_stream(v,pool[off:off+3*m])[:m])
    return out
class Index:
    def __init__(s,L,k):
        s.k=k; s.c=codes(L,k); s.order=np.argsort(s.c,kind='stable'); s.sc=s.c[s.order]
        sep=np.where(L==0)[0]; s.sep=sep
    def stats(s,t,ntext):
        k=s.k; m=len(t)
        if m<k: return dict(H=0,pertext=np.zeros(ntext,int),band=0,band_text=-1,run=0)
        tc=codes(np.asarray(t,np.uint8),k)[:m-k+1]
        lo=np.searchsorted(s.sc,tc,'left'); hi=np.searchsorted(s.sc,tc,'right'); c=hi-lo; tot=int(c.sum())
        if tot==0: return dict(H=0,pertext=np.zeros(ntext,int),band=0,band_text=-1,run=0)
        ii=np.repeat(np.arange(len(tc)),c); within=np.arange(tot)-np.repeat(np.cumsum(c)-c,c)
        jj=s.order[np.repeat(lo,c)+within].astype(np.int64)
        tid=np.searchsorted(s.sep,jj)   # text index
        pert=np.bincount(tid,minlength=ntext+1)[:ntext]
        d=jj-ii; b=d//BAND
        ub,cnt=np.unique(b,return_counts=True); bi=cnt.argmax(); band=int(cnt[bi])
        btext=int(np.searchsorted(s.sep,ub[bi]*BAND+BAND//2))
        o=np.lexsort((ii,d)); dd=d[o]; i2=ii[o]
        cont=(np.diff(dd)==0)&(np.diff(i2)==1)
        # longest chain of consecutive True + 1
        if cont.any():
            x=np.concatenate([[0],cont.astype(np.int8),[0]]); dx=np.diff(x); st_=np.where(dx==1)[0]; en=np.where(dx==-1)[0]
            run=int((en-st_).max())+1+k-1
        else: run=k
        return dict(H=tot,pertext=pert,band=band,band_text=btext,run=run)
def do_variant(v):
    name=core.vname(v); fn=OUT+'/%s.pkl'%name
    if os.path.exists(fn): return
    t0=time.time(); L=core.variant_stream(v); ntext=len(core.lib()['names'])
    res={}
    for k in (6,8):
        I=Index(L,k)
        for sname,ix in TG:
            tgt=T[ix]; m=len(tgt); s=int(sname[1:]) if sname!='whole' else 99
            rng=np.random.default_rng(90000+s)
            lst=[('real',tgt)]+[('sh',rng.permutation(tgt)) for _ in range(NSH)]+[('he',h) for h in heldout(m,4242+s)]
            if sname!='whole': pl,_=plant_lanes(s,m); lst.append(('plant',pl[0])); lst.append(('plant_noisy',pl[3]))
            res[(k,sname)]=[(lab,I.stats(t,ntext)) for lab,t in lst]
        del I
    pickle.dump(res,open(fn,'wb')); print(name,'%.0fs'%(time.time()-t0),flush=True)
if __name__=='__main__':
    V=core.variant_list()
    if len(sys.argv)>1 and sys.argv[1]=='test': V=[('base','mF',2)]
    for v in V: do_variant(v)
