"""Test (d): cross-opening coincidence of key fragments (key restarting per section/page).
For each model, count pairs (opening1 != opening2, crib1, crib2) whose fragments agree exactly on their first l elements, l = 6, 8, 10, 12.
Runs on the same job files as frag.c (real / nullR / nullP1 / nullP2)."""
import numpy as np, sys, json, collections, glob
from common import *
def read_blocks(name):
    blocks=[]
    for fn in sorted(glob.glob(OUT+'/jobs/%s_*.txt'%name)):
        cur=None
        for line in open(fn):
            t=line.split()
            if t[0]=='OPEN':
                cur=dict(oid=int(t[1]),pos=int(t[2]),prev=int(t[3]),c=list(map(int,t[5:5+int(t[4])])),cribs=[]); blocks.append(cur)
            else: cur['cribs'].append(tuple(map(int,t[2:])))
    return sorted(blocks,key=lambda b:b['oid'])
INV=[0]*29
for x in range(1,29):
    for y in range(1,29):
        if x*y%29==1: INV[x]=y
BTa=np.array([[0]+b[1][1:] for b in BIJ]); SGa=np.array([s[1] for s in SIG])
def models():
    ms=[]
    for b in range(14):
        for s in range(30):
            for fo in (0,1): ms.append(('chain',b,s,fo))
    for off in range(28):
        for orr in (0,1):
            for iv in (0,1): ms.append(('gf',off,orr,iv))
    for fo in (0,1): ms.append(('vig',fo,0,0))
    return ms
MS=models()
def tables(model,blk,l):
    """per-fragment-element table (l x 29) mapping crib rune -> key value (-1 invalid) and the crib positions used"""
    kind,a,b,cc=model; c=blk['c']; prev=blk['prev']
    if kind=='vig':
        if len(c)<l: return None
        kept=list(range(l)); m=29
        T=np.array([[(c[j]+p)%29 if a else (c[j]-p)%29 for p in range(29)] for j in kept]); return T,kept,m
    D=[(c[j]-(prev if j==0 else c[j-1]))%29 if (j>0 or prev>=0) else 0 for j in range(len(c))]
    kept=[j for j in range(len(c)) if D[j]!=0][:l]
    if len(kept)<l: return None
    if kind=='chain':
        m=28; T=np.array([[(BIJ[a][1][D[j]]+SG_[b][p])%28 if cc else (BIJ[a][1][D[j]]-SG_[b][p])%28 for p in range(29)] for j in kept])
    else:
        m=29; T=[]
        for j in kept:
            row=[]
            for p in range(29):
                x=0 if p==28 else 1+(((a-p)%28) if b else (p+a)%28)
                row.append(-1 if x==0 else ((x*INV[D[j]])%29 if cc else (D[j]*INV[x])%29))
            T.append(row)
        T=np.array(T)
    return T,kept,m
SG_=[s[1] for s in SIG]
def run(name, ls=(6,8,10), keep_examples=False):
    B=read_blocks(name)
    res={}
    for l in ls:
        tot=0; per_model=[]; examples=[]
        # precompute per block distinct prefix matrices for each needed length (depends on kept, which depends on model kind)
        cache={}
        for mi,model in enumerate(MS):
            allc=[];allo=[]
            for bi,blk in enumerate(B):
                tb=tables(model,blk,l)
                if tb is None: continue
                T,kept,m=tb; need=kept[-1]+1
                key=(bi,need)
                if key not in cache:
                    pref=sorted(set(cr[:need] for cr in blk['cribs'] if len(cr)>=need))
                    cache[key]=np.array(pref,dtype=np.int64).reshape(-1,need)
                Pm=cache[key]
                if len(Pm)==0: continue
                V=np.stack([T[i][Pm[:,kept[i]]] for i in range(l)],1)
                V=V[(V>=0).all(1)]
                code=np.zeros(len(V),dtype=np.int64)
                for i in range(l): code=code*29+V[:,i]
                code=np.unique(code)
                allc.append(code); allo.append(np.full(len(code),blk['pos']))
            if not allc: per_model.append(0); continue
            allc=np.concatenate(allc); allo=np.concatenate(allo)
            pr=np.unique(np.stack([allc,allo],1),axis=0); allc,allo=pr[:,0],pr[:,1]   # identical positions count once
            u,inv,cnt=np.unique(allc,return_inverse=True,return_counts=True)
            pairs=int((cnt*(cnt-1)//2).sum()); tot+=pairs; per_model.append(pairs)
            if keep_examples and pairs:
                for ui in np.nonzero(cnt>1)[0][:5]:
                    idx=np.nonzero(inv==ui)[0]; examples.append((str(model),[int(allo[i]) for i in idx]))
        res[l]=dict(total=tot,max_model=int(max(per_model)),examples=examples[:40])
        print(name,'l=%d'%l,'colliding cross-opening pairs',tot,'max per model',max(per_model),flush=True)
    return res
if __name__=='__main__':
    import os
    ls=tuple(int(x) for x in os.environ.get('LS','6,8,10').split(','))
    out={}
    for name in sys.argv[1:]:
        out[name]=run(name,ls=ls,keep_examples=(name=='real'))
    json.dump(out,open(OUT+'/cross_%s_%s.json'%('_'.join(sys.argv[1:]),'-'.join(map(str,ls))),'w'),indent=1)
