import time,numpy as np,core
L=core.variant_stream(('base','mF',2)); print(len(L))
T,pg,ch=core.target(); secs=core.sections(pg); print([len(s) for s in secs], len(T))
rng=np.random.default_rng(0)
m=200; lanes=[T[:m]]+[rng.permutation(T[:m]) for _ in range(31)]
t=time.time(); b,j=core.sw32(L[:3000000],lanes,200); dt=time.time()-t
print('cells/s per lane-vector',3e6*m/dt/1e9,'G; est per variant full 2896 rows: %.0f s'%(dt/3e6*len(L)*2896/m))
