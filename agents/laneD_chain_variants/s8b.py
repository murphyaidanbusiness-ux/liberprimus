import re
src=open('s8_lagdiff.py').read().split("t0=time.time()")[0]
exec(src)
for L in (1,2,3,4):
    real=stat(PAGES,L).max()
    nm=np.array([stat(dshuffled_pages(PAGES,rng),L).max() for _ in range(60)])
    print('lag-%d: best single-page best-period z real %.2f ; null max over 55 pages: mean %.2f sd %.2f max %.2f -> z=%.2f'%(L,real,nm.mean(),nm.std(),nm.max(),(real-nm.mean())/nm.std()))
