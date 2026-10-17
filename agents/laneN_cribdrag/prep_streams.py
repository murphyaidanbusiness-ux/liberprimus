import numpy as np, sys, struct
sys.path.insert(0,'.')
from common import *
U,C,h=lpdata.unsolved(); assert h=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
c=np.array(C,dtype=np.uint8)
pg=np.concatenate([[p['page']]*len(p['idx']) for p in U]).astype(np.int16)
wd=np.concatenate([p['word'] for p in U]).astype(np.int32)
print(len(c), len(set(wd.tolist())), len(set(pg.tolist())))
np.save(LANE+'/pg.npy',pg); np.save(LANE+'/wd.npy',wd)
def write(path,cc,pgg=pg,wdd=wd):
    with open(path,'wb') as f:
        f.write(struct.pack('<i',len(cc))); f.write(cc.astype(np.uint8).tobytes()); f.write(pgg.astype(np.int16).tobytes()); f.write(wdd.astype(np.int32).tobytes())
import os; os.makedirs(LANE+'/streams',exist_ok=True)
write(LANE+'/streams/real.bin',c)
D=(np.diff(c.astype(int))%29)
print('doublets',int((D==0).sum()),'F count',int((c==0).sum()))
for s in range(1,51):
    rng=np.random.default_rng(1000+s)
    Dp=rng.permutation(D)
    cs=np.concatenate([[c[0]],(c[0]+np.cumsum(Dp))%29]).astype(np.uint8)
    write(LANE+'/streams/null%02d.bin'%s,cs)
print('done')
