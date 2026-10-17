import lpdata, numpy as np
U,C,h=lpdata.unsolved()
rng=np.random.default_rng(7)
def coset_ioc(x,L,m):
    tot=cnt=0
    for j in range(L):
        col=x[j::L]; col=col[col>=0]
        n=len(col)
        if n>1:
            c=np.bincount(col,minlength=m); tot+=(c*(c-1)).sum()/(n*(n-1))*m; cnt+=1
    return tot/cnt
def scan(x,m,Ls): return max((coset_ioc(x,L,m),L) for L in Ls)
Ls=range(2,41)
print("per-page periodic coset-IoC, periods 2..40.  raw c (m=29) and increments D (m=28, zeros masked). null = max over 30 shuffles")
flags=0
for p in U:
    ix=np.array(p['idx']); D=(ix[1:]-ix[:-1])%29; Dm=np.where(D==0,-1,D-1)
    rc=scan(ix,29,Ls); rd=scan(Dm,28,Ls)
    nc=[scan(rng.permutation(ix),29,Ls)[0] for _ in range(30)]
    nd=[scan(rng.permutation(Dm),28,Ls)[0] for _ in range(30)]
    fc='  <<C' if rc[0]>max(nc) else ''; fd='  <<D' if rd[0]>max(nd) else ''
    flags+=bool(fc)+bool(fd)
    print("p%2d n=%3d  C: %.3f@L%-2d (null mean %.3f max %.3f)   D: %.3f@L%-2d (null mean %.3f max %.3f)%s%s"%(p['page'],len(ix),rc[0],rc[1],np.mean(nc),max(nc),rd[0],rd[1],np.mean(nd),max(nd),fc,fd))
print("pages exceeding null max:",flags,"of",2*len(U),"tests (expect ~%.1f by chance at 1/31 each)"%(2*len(U)/31))
