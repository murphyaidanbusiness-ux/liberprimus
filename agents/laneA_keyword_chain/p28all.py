# Look-elsewhere: the L=28 (and 14, 7) coset-IoC z-score on every page, 200 shuffles each.
import common, numpy as np
U,C=common.pages(); rng=np.random.default_rng(2828)
def cioc(x,L,m):
    n=len(x); idx=np.arange(n)%L; tot=0;cnt=0
    for j in range(L):
        col=x[idx==j]; col=col[col>=0]; k=len(col)
        if k>1: h=np.bincount(col,minlength=m); tot+=(h*(h-1)).sum()/(k*(k-1))*m; cnt+=1
    return tot/cnt
pos=0; rows=[]
for p in U:
    c=np.array(p['idx']); prev=C[pos-1] if pos else 0; pos+=len(c)
    D=np.diff(np.r_[prev,c])%29; Dm=np.where(D==0,-1,D-1)
    row=[p['page'],len(c)]
    for L in (7,14,28):
        r=cioc(c,L,29); nr=np.array([cioc(rng.permutation(c),L,29) for _ in range(200)])
        d=cioc(Dm,L,28); nd=np.array([cioc(np.where(x==0,-1,x-1),L,28) for x in (rng.permutation(D) for _ in range(200))])
        row+=[(r-nr.mean())/nr.std(),(d-nd.mean())/nd.std()]
    rows.append(row); print('p%2d n=%3d  L7 raw z %5.2f incr z %5.2f | L14 raw %5.2f incr %5.2f | L28 raw %5.2f incr %5.2f'%tuple(row),flush=True)
R=np.array(rows)
for k,name in enumerate(['L7raw','L7inc','L14raw','L14inc','L28raw','L28inc']):
    col=R[:,2+k]; o=np.argsort(-col)
    print(name,'mean z %.2f sd %.2f; top pages:'%(col.mean(),col.std()),[(int(R[i,0]),round(col[i],2)) for i in o[:4]])
