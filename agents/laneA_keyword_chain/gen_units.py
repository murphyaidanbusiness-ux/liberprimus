import common, ciph, numpy as np, re, sys
U,C=common.pages()
def w(fn,units):
    with open(fn,'w') as f:
        for uid,prev,c in units: f.write('%d %d %d %s\n'%(uid,prev,len(c),' '.join(map(str,c))))
pages=[]; pos=0
for p in U:
    prev = C[pos-1] if pos else 0
    pages.append((p['page'],prev,list(p['idx']))); pos+=len(p['idx'])
w('units_pages.txt',pages)
chap=[c for p in U for c in p['chap']]
secs={}; 
for i,(r,ch) in enumerate(zip(C,chap)): secs.setdefault(ch,[]).append(i)
su=[(100+ch, C[ix[0]-1] if ix[0] else 0, [C[i] for i in ix]) for ch,ix in sorted(secs.items())]
w('units_sections.txt',su)
NS=20; rng=np.random.default_rng(3301)
nD=[];nR=[]
for s in range(1,NS+1):
    for pid,prev,c in pages:
        c=np.array(c); D=(np.diff(np.r_[prev,c]))%29; D=rng.permutation(D); cc=(prev+np.cumsum(D))%29
        nD.append((1000*s+pid,prev,list(cc)))
        nR.append((1000*s+pid,prev,list(rng.permutation(c))))
w('units_nullD.txt',nD); w('units_nullR.txt',nR)
print(len(pages),len(su),[len(x[2]) for x in su])
