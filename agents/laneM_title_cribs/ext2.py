"""Vectorised dictionary extension (test f). Same semantics as ext.extend, numpy over the whole dictionary."""
import numpy as np, collections
from common import *
import pyfrag, ext
from pyfrag import fragment, decode_model, BT, SGT, INV, DL2, eng_batch, H, TG, NH
FNV0=np.uint64(0xcbf29ce484222325); FP=np.uint64(0x100000001b3)
def vfnv(m,D):
    N,l=D.shape; h=np.full(N,FNV0,dtype=np.uint64)
    with np.errstate(over='ignore'):
        for v in [np.full(N,m,np.uint64),np.full(N,l,np.uint64)]+[D[:,j].astype(np.uint64) for j in range(l)]:
            h^=v; h*=FP
    return h
def vhit(F,m,typ,pos):
    """F (N,n) -> bool array: shift/negation-canonical match of type typ (first 24 elements)."""
    F=F[:,:24]; D=(F[:,1:]-F[:,:-1])%m; ok=np.zeros(len(F),bool)
    for DD in (D,(-D)%m):
        h=vfnv(m,DD); i=np.searchsorted(H,h)
        for step in range(4):
            j=np.minimum(i+step,NH-1); eq=(H[j]==h)
            t=TG[j]; tt=(t>>30)
            good=eq&(tt==typ)
            if typ==3: good&=np.abs((t&16383).astype(np.int64)-pos)>F.shape[1]+2
            ok|=good
    return ok
def word_table(model,c,prev,start,wl):
    """value table (wl x 29) for crib positions start..start+wl-1 (-1 = dropped position, -2 = invalid); returns table, m"""
    fint,fam,dl,a,b,cc=decode_model(model)
    T=np.zeros((wl,29),dtype=np.int64)
    for i in range(wl):
        j=start+i
        if fam in (0,1):
            D=(c[j]-c[j-1])%29
            if D==0: T[i,:]=-1; continue
            for p in range(29):
                if fam==0: T[i,p]=(BT[a][D]+SGT[b][p])%28 if cc else (BT[a][D]-SGT[b][p])%28
                else:
                    x=0 if p==28 else 1+(((a-p)%28) if b else (p+a)%28)
                    if x==0: T[i,p]=-2; continue
                    k=(x*INV[D])%29 if cc else (D*INV[x])%29
                    T[i,p]=DL2[k] if dl else k
        else:
            for p in range(29): T[i,p]=(c[j]+p)%29 if a else (c[j]-p)%29
    m=28 if fam==0 or (fam==1 and dl) else 29
    return T,m
def extend(item,c,prev,pos,lens,rounds=3,beam=5):
    Dct=ext.dictionary(); cur=[(tuple(item['crib']),item['nw'])]; traj=[]
    for r in range(rounds):
        cand=[]
        for crib,nw in cur:
            if nw>=len(lens): continue
            wl=lens[nw]; W=np.array(Dct.get(wl,[]),dtype=np.int64).reshape(-1,wl)
            if len(W)==0 or len(crib)+wl+1>len(c): continue
            fr=fragment(item['model'],list(crib),c,prev)
            if fr is None: continue
            f0,m=fr
            T,m2=word_table(item['model'],c,prev,len(crib),wl)
            cols=[T[i][W[:,i]] for i in range(wl) if T[i,0]!=-1]
            if cols:
                V=np.stack(cols,1); okw=(V>=0).all(1)
            else:
                V=np.zeros((len(W),0),dtype=np.int64); okw=np.ones(len(W),bool)
            F=np.concatenate([np.tile(np.array(f0,dtype=np.int64),(len(W),1)),V],1)[okw]; Wk=W[okw]
            if len(F)==0: continue
            if item['test']=='a':
                sc=eng_batch(F,m); mu,sd,_=ext.ref(m,F.shape[1]); z=(sc-mu)/sd
                for i in np.argsort(-z)[:beam]: cand.append((float(z[i]),crib+tuple(Wk[i]),nw+1,F.shape[1]))
            else:
                ok=vhit(F,m,{'b':1,'c':2,'e':3}[item['test']],pos)
                for i in np.nonzero(ok)[0][:beam]: cand.append((F.shape[1],crib+tuple(Wk[i]),nw+1,F.shape[1]))
        if not cand: traj.append(None); break
        cand.sort(key=lambda x:-x[0]); cur=[(x[1],x[2]) for x in cand[:beam]]
        traj.append((round(float(cand[0][0]),3),cand[0][3],len(cand)))
    return traj
