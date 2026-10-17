import numpy as np, sys
sys.path.insert(0,'.')
from common import *
Q=np.fromfile(S+'/agents/laneA_keyword_chain/quad29.f32',dtype=np.float32)
assert Q.size==29**4
Q.tofile(LANE+'/quad.f32')
P=(10.0**Q.astype(np.float64)).reshape(29,29,29,29)
print('quad range',Q.min(),Q.max(), 'mean (uniform runes) expected', )
for m in (29,28):
    T=np.zeros((29,29,29))
    a=np.arange(m)
    for d1 in range(m):
        for d2 in range(m):
            for d3 in range(m):
                b=(a+d1)%m; c=(b+d2)%m; d=(c+d3)%m
                T[d1,d2,d3]=np.log10(P[a,b,c,d].sum())
    T.astype(np.float32).tofile(LANE+'/t3_%d.f32'%m)
    print(m,'T3 range',T[:m,:m,:m].min(),T[:m,:m,:m].max())
# dictionary windows
keys=[]
for line in open(S+'/agents/laneA_keyword_chain/keys.txt'):
    p=line.split(); src=int(p[0]); L=int(p[1])
    if src in (0,1) and L>=3: keys.append(np.array(list(map(int,p[2:])),dtype=np.int64))
print('dictionary words',len(keys))
import collections
bylen=collections.defaultdict(list)
for k in keys: bylen[len(k)].append(k)
MULT=np.uint64(0x9E3779B97F4A7C15)
for m in (29,28):
    bm6=np.zeros((m**5+7)//8+8,dtype=np.uint8)
    bm8=np.zeros((1<<30)//8,dtype=np.uint8)
    nwin=0
    pw=[m**i for i in range(8)]
    idx5=[]; idx8=[]
    for L,ws in bylen.items():
        W=np.stack(ws)
        if m==28: W=W[~(W==28).any(axis=1)]
        if len(W)==0: continue
        for t in range(L):
            cols=[(t+i)%L for i in range(8)]
            A=W[:,cols]
            Dd=(A[:,1:]-A[:,:-1])%m
            for off in (0,1,2):
                s5=sum(Dd[:,off+i]*pw[i] for i in range(5))
                idx5.append(np.unique(s5))
            s7=sum(Dd[:,i].astype(np.uint64)*np.uint64(pw[i]) for i in range(7))
            h=((s7*MULT)>>np.uint64(34)).astype(np.int64)
            idx8.append(np.unique(h))
            nwin+=len(W)
    i5=np.unique(np.concatenate(idx5)); i8=np.unique(np.concatenate(idx8))
    np.bitwise_or.at(bm6,i5>>3,(1<<(i5&7)).astype(np.uint8))
    np.bitwise_or.at(bm8,i8>>3,(1<<(i8&7)).astype(np.uint8))
    bm6.tofile(LANE+'/bm6_%d.bin'%m); bm8.tofile(LANE+'/bm8_%d.bin'%m)
    print(m,'windows',nwin,'bm6 sigs',len(i5),'density %.4f'%(len(i5)/m**5),'bm8 sigs',len(i8),'density %.5f'%(len(i8)/2**30))
