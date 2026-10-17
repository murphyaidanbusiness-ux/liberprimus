import sys, time, numpy as np
sys.path.insert(0,'.')
from keysearch import *
from report_hits import *
t=time.time(); ci=CorpusIndex(); print('index',time.time()-t,file=sys.stderr)
pw=np.array([29**(K-1-j) for j in range(K)],dtype=np.int64)
def fast_search(k,m):
    k=np.array(k); L=len(k)
    if L<K: return []
    out=[]
    A=np.empty((2*m,L),dtype=np.int64); meta=[]
    r=0
    for o in (0,1):
        base=(m-k)%m if o else k
        for s in range(m):
            A[r]=np.where(k<0,-1,(base+s)%m); meta.append((o,s)); r+=1
    idx=np.arange(L-K+1)[:,None]+np.arange(K)[None,:]
    Wn=A[:,idx]            # (V, nw, K)
    bad=(Wn<0).any(axis=2)
    codes=(np.where(Wn<0,0,Wn)*pw).sum(axis=2)
    hit,pos=ci.lookup(codes.ravel())
    hit=hit.reshape(codes.shape)&~bad
    res=[]
    for v,j in zip(*np.nonzero(hit)):
        res.append(meta[v]+(int(j),)+ci.where(int(pos.reshape(codes.shape)[v,j])))
    return res
rows=[]
for F in (0,1):
    for line in open(LANE+'/out/dump_F%d.txt'%F):
        p=line.split()
        rows.append(dict(F=F,crib=int(p[0]),pos=int(p[1]),mt=int(p[2]),var=int(p[3]),shift=int(p[4]),orient=int(p[5]),W=int(p[6]),al=int(p[7]),cls=int(p[8]),L=int(p[9]),Z=float(p[10]),dict=int(p[11]),per=int(p[12]),k=[int(x) for x in p[14].strip(',').split(',')]))
print('dumped real rows',len(rows),file=sys.stderr)
found=[]; nq=0
for r in rows:
    m=28 if r['mt']==0 else 29
    res=fast_search(r['k'],m); nq+=1
    if res: found.append((r,res))
print('searched fragments',nq,'with corpus 12-mer matches',len(found))
for r,res in found[:20]: print(r['F'],r['mt'],r['crib'],r['pos'],r['Z'],res[:3])
# false-positive baseline: random fragments
rng=np.random.default_rng(5); fp=0
for _ in range(2000):
    L=int(rng.integers(12,60)); fp+=len(fast_search(rng.integers(0,28,L).tolist(),28))>0
print('baseline: random fragments with matches',fp,'/2000')
# DICT / PER top hits
import collections
for key,name in (('dict','DICT'),('per','PER')):
    best=sorted(rows,key=lambda r:-r[key])[:12]
    print('\nTOP',name)
    for r in best:
        cb=cribs[r['crib']]; m=28 if r['mt']==0 else 29
        extra=''
        if key=='dict' and r['mt']!=1:
            dm=dict_match(r['k'],m); extra=str(dm[:2])
        print(r['F'],MT[r['mt']],CLS[r['cls']],'al' if r['al'] else 'un',' '.join(cb['words'])[:50],where(r['pos']),'L',r['L'],name,r[key],'raw key',''.join(TR[x] if x>=0 else '?' for x in r['k']),extra)
