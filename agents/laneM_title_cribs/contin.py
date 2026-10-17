"""(c)/(d) continuation: numeric-sequence hits whose window offset equals the opening's absolute key index
(rune position, or position minus preceding doublets for the chain models): one key running through the book."""
import glob, json, sys, numpy as np, geom
C=geom.C; dbl=np.r_[0,np.cumsum([1 if C[i]==C[i-1] else 0 for i in range(1,len(C))])]
def run(name):
    pos={}
    for fn in glob.glob('jobs/%s_*.txt'%name):
        for line in open(fn):
            if line.startswith('OPEN'): t=line.split(); pos[int(t[1])]=int(t[2])
    tot=0; near=0; ex=[]
    for fn in glob.glob('runs/%s_*.hits'%name):
        for line in open(fn):
            t=line.split()
            if len(t)<9: continue
            oid=int(t[1]); p=pos[oid]
            for tg in t[8:]:
                typ,src,off=map(int,tg.split(':'))
                if typ!=2: continue
                tot+=1
                cands=[p,p-int(dbl[p]),p+1,p-1]
                if any(abs(off-x)<=0 for x in cands): near+=1; ex.append((oid,p,src,off,t[5]))
    return tot,near,ex[:10]
for nm in sys.argv[1:]: print(nm,run(nm))
