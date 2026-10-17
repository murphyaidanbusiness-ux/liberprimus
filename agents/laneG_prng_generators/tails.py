import sys, math, collections; sys.path.insert(0,'.')
import analyze
from math import comb
seeds,rows,HR,HN,N,TOP=analyze.summarize(sys.argv[1])
NG=5300; NC=12956
out=[]
def tail(H,v): return sum(c for x,c in H.items() if x>=v)
for st,name in ((0,'exact'),(1,'pattern'),(2,'hamming')):
    for kind,mods in (('direct (a,b,c,d,s)',(0,1,2,3,4)),('chain increments (e,e0)',(5,6))):
        R=collections.Counter(); Nn=collections.Counter(); ns=0
        for (a,m,s),H in HR.items():
            if s!=st or m not in mods: continue
            R.update(H); Nn.update(HN[(a,m,s)]); ns+=N[(a,m)]
        if ns==0 or not R: continue
        mx=max(R)
        out.append('%s / %s: %d streams, real max %d'%(name,kind,ns,mx))
        for v in range(max(0,mx-4),mx+3):
            r=tail(R,v)
            if st<2:
                nexp=tail(Nn,v)/20.0
                # analytic expected streams with an exact run >= v anywhere: alignments * q^v
                if st==0:
                    q=1/29 if mods[0]==0 else 1/28
                    A=(NG-v)*NC*(1 if mods[0]==0 else 2)
                    lam=A*q**v*(1-q); an=ns*(1-math.exp(-lam))
                    out.append('   >=%-3d real %-8d null(empirical, per 20 shuffles avg) %-10.4g analytic %.4g'%(v,r,nexp,an))
                else:
                    out.append('   >=%-3d real %-8d null(empirical, per 20 shuffles avg) %-10.4g'%(v,r,nexp))
            else:
                p=sum(comb(64,k)*(1/29)**k*(28/29)**(64-k) for k in range(v,65))
                A=1001*55; an=ns*(1-math.exp(-A*p))
                out.append('   >=%-3d real %-8d analytic Binomial(64,1/29) over 55 pages x 1001 offsets: %.4g'%(v,r,an))
print('\n'.join(out))
