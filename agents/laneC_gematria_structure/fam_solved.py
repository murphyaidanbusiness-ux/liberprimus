"""Families (a),(b),(c): keystreams from numbers of the SOLVED pages (plaintext / ciphertext), word-level and letter-level."""
import numpy as np, itertools
import eng, seqs
from eng import Data, scan
SEQ=seqs.seq_sets()
OMAX=500

def prep_base(name, rev, tile_to):
    """returns (K_int array, cyc, rm_flag_needs) before reduction. cum sequences tiled, then cumsum."""
    s=SEQ[name]; a=s['arr'].copy()
    if rev: a=a[::-1].copy()
    return a

def expand_words(a, words):
    return np.repeat(a, [len(w) for w in words])

def reduce(a, red):
    return (a % (28 if red=='m28' else 29)).astype(np.uint8)

FORMS={'m28':[0,1],'m29':[0,1,2,3]}

def specs(d, names=None, rev_opts=(0,1), include_raw=True):
    """generator of job specs for data d"""
    idxcache={}
    def IDX(kind,mode,conv=None):
        key=(kind,mode,conv)
        if key not in idxcache:
            idxcache[key]=d.idx_rune(mode,conv) if kind=='rune' else d.idx_word(mode)
        return idxcache[key]
    for name,s in SEQ.items():
        if names and name not in names: continue
        for rev in rev_opts:
            a=prep_base(name,rev,None)
            dom=s['dom']; cum=s['cum']
            words=s.get('words')
            if rev and words is not None: words=words[::-1]
            # --- variants of the per-element sequence: native, and (for W) expanded per letter
            variants=[]
            if dom=='L': variants.append(('L',a,None))
            else:
                variants.append(('W',a,None))
                variants.append(('Wx',a,words))
            for vk,arr,wd in variants:
                if vk=='Wx': arr=expand_words(arr,wd)
                if cum:
                    reps=int(np.ceil((len(arr)+d.m+10)/len(arr)))+1
                    big=np.tile(arr,reps); big=np.cumsum(big)
                    if s.get('post')=='tot':
                        big=np.array([seqs.totient(int(x)) for x in big]); 
                    Kint=big; cyc=0; omax_=min(OMAX,len(arr)-1); usecum=(s.get('post')!='tot')
                else:
                    Kint=arr; cyc=1; omax_=min(OMAX,len(arr)-1); usecum=False
                for red in ('m28','m29'):
                    K=reduce(Kint,red); rm=(28 if red=='m28' else 29) if usecum else 0
                    if vk=='W': cfgs=[('word','cont',None),('word','page',None)]
                    else: cfgs=[('rune','cont','A'),('rune','cont','B'),('rune','page','A'),('rune','page','B')]
                    for kind,mode,conv in cfgs:
                        idx=IDX(kind,mode,conv)
                        for form in FORMS[red]:
                            yield dict(label=f'{name}|{vk}|rev{rev}|{kind}-{mode}{conv or ""}|{red}',form=form,X=d.D,idx=idx,K=K,cyc=cyc,omin=0,omax=omax_,rm=rm)
    if include_raw:
        # plain shift control on raw runes (mod 29): key per rune, no chain
        X=d.c[1:].astype(np.uint8)
        for name,s in SEQ.items():
            if s['dom']!='L' or s['cum']: continue
            if names and name not in names: continue
            for rev in rev_opts:
                a=prep_base(name,rev,None); K=reduce(a,'m29')
                for mode in ('cont','page'):
                    idx=d.idx_rune(mode,'B')
                    for form in (4,5):
                        yield dict(label=f'RAW:{name}|L|rev{rev}|rune-{mode}B|m29',form=form,X=X,idx=idx,K=K,cyc=1,omin=0,omax=min(OMAX,len(K)-1),rm=0)

def zscores(ioc,nv):
    vm=nv>0.5*nv.max()
    if vm.sum()<30: return None
    nvmed=np.median(nv[vm])
    r=(ioc[vm]-np.median(ioc[vm]))*nv[vm]/nvmed
    m=np.median(r); s=1.4826*np.median(np.abs(r-m))
    if s<=0: return None
    z=np.full(len(ioc),-1e9); z[vm]=(r-m)/s
    return z

def run_specs(gen):
    """returns per-label best dict"""
    res={}
    for sp in gen:
        ioc,nv=scan(sp['X'],sp['idx'],sp['K'],sp['cyc'],sp['omin'],sp['omax'],sp['form'],sp['rm'])
        z=zscores(ioc,nv)
        if z is None: continue
        j=int(np.argmax(z))
        key=sp['label']
        cur=res.get(key)
        rec=(float(z[j]),float(ioc[j]),sp['omin']+j,int(nv[j]),sp['form'])
        if cur is None or rec[0]>cur[0]: res[key]=rec
    return res
