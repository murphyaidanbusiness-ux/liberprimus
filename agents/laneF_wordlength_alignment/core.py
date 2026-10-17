import sys, pickle, ctypes, os
import numpy as np
S='.'
HERE=S+'/agents/laneF_wordlength_alignment'
sys.path.insert(0,S+'/lp'); import lpdata
STOP=['THE','OF','TO','A','AN','AND','IN','IS','IT','OR','BE','AS','AT','BY','HE','WE','SO','NO','ON','IF','MY','UP','DO','ME','US','I']
SETSIZES=[1,2,3,4,6,9,13,20,26]
SECS=[(0,2),(3,7),(8,14),(15,22),(23,26),(27,32),(33,39),(40,53),(54,54)]
ALLDIG=('TH','NG','EA','EO','OE','AE','IA')
def rlen(w,digs=ALLDIG,ing1=True,io=True):
    w=w.replace('K','C').replace('V','U').replace('Q','C').replace('Z','S')
    i=0;n=0;L=len(w)
    while i<L:
        if ing1 and 'NG' in digs and w.startswith('ING',i): i+=3
        elif w[i:i+2] in digs: i+=2
        elif io and 'IA' in digs and w.startswith('IO',i): i+=2
        else: i+=1
        n+=1
    return n
def target():
    U,C,sha=lpdata.unsolved(); assert sha=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
    d={}
    for p in U:
        for k,wid in enumerate(p['word']):
            if wid not in d: d[wid]=[0,p['page'],p['chap'][k]]
            d[wid][0]+=1
    v=list(d.values())
    return np.array([x[0] for x in v],np.int16), np.array([x[1] for x in v]), np.array([x[2] for x in v])
def sections(page):
    return [np.where((page>=a)&(page<=b))[0] for a,b in SECS]
_lib=None
def lib():
    global _lib
    if _lib is None: _lib=pickle.load(open(HERE+'/lib.pkl','rb'))
    return _lib
def type_lengths(scheme):
    tl=lib()['types']
    if scheme=='base': f=lambda w: rlen(w)
    elif scheme=='ing2': f=lambda w: rlen(w,ing1=False)
    elif scheme=='letters': f=lambda w: rlen(w,digs=())
    elif scheme=='THonly': f=lambda w: rlen(w,digs=('TH',))
    elif scheme.startswith('no'):
        dg=scheme[2:]; ds=tuple(x for x in ALLDIG if x!=dg); f=lambda w: rlen(w,digs=ds)
    else: raise ValueError(scheme)
    return np.array([min(f(w),15) for w in tl],np.uint8)
def stopmask(nset):
    tl=lib()['types']; st=set(STOP[:nset])
    return np.array([w in st for w in tl],bool)
def apply_model(tokids, tlen, model, nset):
    """tokids: int32 type ids (-1 = separator). returns uint8 length stream (0 = separator)"""
    sep=tokids<0
    ln=np.where(sep,0,tlen[np.maximum(tokids,0)]).astype(np.int32)
    if model=='none': return np.minimum(ln,15).astype(np.uint8)
    stp=np.zeros(len(tokids),bool); sm=stopmask(nset); stp[~sep]=sm[tokids[~sep]]
    if model=='drop': return np.minimum(ln[~stp],15).astype(np.uint8)
    ns=~stp
    if model=='mF': g=np.cumsum(ns)-ns
    elif model=='mP': g=np.maximum(np.cumsum(ns)-1,0)
    else: raise ValueError(model)
    G=g.max()+1
    out=np.bincount(g,weights=ln,minlength=G)
    hassep=np.bincount(g,weights=sep,minlength=G)>0
    out[hassep]=0
    return np.minimum(out,15).astype(np.uint8)
def variant_list():
    V=[('base','none',0),('ing2','none',0)]+[('no'+d,'none',0) for d in ALLDIG]+[('letters','none',0),('THonly','none',0)]
    for s in SETSIZES:
        for mdl in ('mF','mP','drop'): V.append(('base',mdl,s))
    for sc in ('letters','THonly'):
        for mdl in ('drop','mF'): V.append((sc,mdl,2))
    return V
def vname(v):
    sc,mdl,s=v
    return sc if mdl=='none' else '%s_%s%d'%(sc,mdl,s)
_tl_cache={}
def variant_stream(v, tokids=None):
    sc,mdl,s=v
    if sc not in _tl_cache: _tl_cache[sc]=type_lengths(sc)
    if tokids is None: tokids=lib()['tok']
    return apply_model(tokids,_tl_cache[sc],mdl,s)
_so=ctypes.CDLL(HERE+'/libsw.so')
_so.sw32.argtypes=[ctypes.c_void_p,ctypes.c_int64,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
_so.swmat.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p]
def sw32(Lstream, lanes, ntext):
    """lanes: list of up to 32 int arrays, all length m. returns best[ntext,32], bestj[ntext,32]"""
    m=len(lanes[0]); T=np.zeros((m,32),np.int16)
    for k,a in enumerate(lanes): assert len(a)==m; T[:,k]=a
    T=np.ascontiguousarray(T); L=np.ascontiguousarray(Lstream,dtype=np.uint8)
    best=np.zeros((ntext,32),np.int16); bj=np.zeros((ntext,32),np.int32)
    _so.sw32(L.ctypes.data,len(L),T.ctypes.data,m,ntext,best.ctypes.data,bj.ctypes.data)
    return best,bj
def swmat(W,T):
    W=np.ascontiguousarray(W,dtype=np.uint8); T=np.ascontiguousarray(T,dtype=np.int16)
    H=np.zeros((len(T)+1,len(W)+1),np.int16); _so.swmat(W.ctypes.data,len(W),T.ctypes.data,len(T),H.ctypes.data); return H
def traceback(W,T):
    """local alignment with traceback; returns score, list of (ti or None, wj or None)"""
    H=swmat(W,T).astype(np.int32); i,j=np.unravel_index(np.argmax(H),H.shape); sc=H[i,j]; path=[]
    while i>0 and j>0 and H[i,j]>0:
        s=1 if T[i-1]==W[j-1] else -2
        if H[i,j]==H[i-1,j-1]+s: path.append((i-1,j-1)); i-=1; j-=1
        elif H[i,j]==H[i-1,j]-2: path.append((i-1,None)); i-=1
        else: path.append((None,j-1)); j-=1
    return sc,path[::-1]
