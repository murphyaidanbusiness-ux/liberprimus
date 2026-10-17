# Build corpus binaries: real corpus + 20 within-page D-shuffled nulls (doublet count preserved).
import sys, numpy as np
S='.'
L=S+'/agents/laneG_prng_generators'
sys.path.insert(0,S+'/lp'); import lpdata
U,C,sha=lpdata.unsolved(); assert sha=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
C=np.array(C,dtype=np.uint8); N=len(C)
pstart=[];pos=0
for u in U: pstart.append(pos); pos+=len(u['idx'])
chap=[c for u in U for c in u['chap']]
rs=sorted(set(pstart)|{i for i in range(1,N) if chap[i]!=chap[i-1]})
def dshuffle(c,rng):
    out=c.copy()
    for k,s in enumerate(pstart):
        e=pstart[k+1] if k+1<len(pstart) else N
        seg=c[s:e].astype(int); D=np.diff(np.concatenate([[0],seg]))%29
        rng.shuffle(D); out[s:e]=np.cumsum(D)%29
    return out
def make(c0, path, nnull=20, seed=12345):
    rng=np.random.default_rng(seed)
    allc=[c0]+[dshuffle(c0,rng) for _ in range(nnull)]
    np.concatenate(allc).astype(np.uint8).tofile(path)
    return allc
if __name__=='__main__':
    allc=make(C, L+'/corpus.bin')
    for a in allc[:3]: print('doublets',int((a[1:]==a[:-1]).sum()))
    open(L+'/restarts.txt','w').write(' '.join(map(str,rs))+'\n')
    open(L+'/pagestarts.txt','w').write(' '.join(map(str,pstart))+'\n')
    print(N,len(rs),'restarts')
