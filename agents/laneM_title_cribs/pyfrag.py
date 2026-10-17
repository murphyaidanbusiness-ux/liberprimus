"""Python mirror of frag.c for single fragments: model decode, eng score, hash-table lookups."""
import numpy as np, json
from common import *
_lm=np.fromfile(OUT+'/lm.bin',dtype=np.int16)
n4=29**4; n3=29**3; n2=29**2
Q=_lm[:n4].astype(np.int64); T3=_lm[n4:n4+n3].astype(np.int64); B2=_lm[n4+n3:n4+n3+n2].astype(np.int64); U1=_lm[n4+n3+n2:].astype(np.int64)
_h=open(OUT+'/htab.bin','rb'); NH=int(np.fromfile(_h,np.int64,1)[0]); H=np.fromfile(_h,np.uint64,NH); TG=np.fromfile(_h,np.uint32,NH)
SRC=json.load(open(OUT+'/sources.json'))
INV=[0]*29
for x in range(1,29):
    for y in range(1,29):
        if x*y%29==1: INV[x]=y
DL2=[0]*29; v=1
for e in range(28): DL2[v]=e; v=v*2%29
BT=[b[1] for b in BIJ]; SGT=[s[1] for s in SIG]
def engscore(f,m):
    f=np.asarray(f); n=len(f)
    if n==0: return -99
    best=-10**9; arg=None
    for at in (0,1):
        for s in range(m):
            g=((m-1-f+s) if at else (f+s))%m
            sm=U1[g[0]]
            if n>1: sm+=B2[g[0]*29+g[1]]
            if n>2: sm+=T3[(g[0]*29+g[1])*29+g[2]]
            if n>3:
                idx=((g[:-3]*29+g[1:-2])*29+g[2:-1])*29+g[3:]; sm+=Q[idx].sum()
            sc=int(sm/n) if sm>=0 else -int((-sm)//n) if False else int(np.trunc(sm/n))
            if sc>best: best=sc; arg=(at,s)
    return best
def eng_batch(F,m):
    """F: (N,n) int array -> best eng score per row (float, log10 per rune)"""
    F=np.asarray(F,dtype=np.int64); N,n=F.shape; best=np.full(N,-1e9)
    for at in (0,1):
        for s in range(m):
            g=((m-1-F+s) if at else (F+s))%m
            sm=U1[g[:,0]].astype(np.float64)
            if n>1: sm+=B2[g[:,0]*29+g[:,1]]
            if n>2: sm+=T3[(g[:,0]*29+g[:,1])*29+g[:,2]]
            if n>3: sm+=Q[((g[:,:-3]*29+g[:,1:-2])*29+g[:,2:-1])*29+g[:,3:]].sum(1)
            best=np.maximum(best,sm/n)
    return best/1000.
def lookup(f,m,pos=None):
    """returns list of (type, src name, off) for shift/negation-canonical matches (first 24 elements)."""
    f=list(f)[:24]
    if len(f)<4: return []
    out=[]
    for h in canon_hashes(f,m):
        h=np.uint64(h); i=np.searchsorted(H,h)
        while i<NH and H[i]==h:
            t=int(TG[i]); typ=t>>30; src=(t>>14)&65535; off=t&16383
            if not (typ==3 and pos is not None and abs(off-pos)<=len(f)+2):
                out.append((typ,SRC[{1:'kw',2:'num',3:'rec'}[typ]][src],off))
            i+=1
    return out
def decode_model(model):
    fint=(model>>28)&1; fam=(model>>24)&7; dl=(model>>27)&1; a=(model>>16)&255; b=(model>>8)&255; c=model&255
    return fint,fam,dl,a,b,c
def model_name(model):
    fint,fam,dl,a,b,c=decode_model(model)
    pre='Fint+' if fint else ''
    if fam==0: return pre+'chain[%s,%s,%s]'%(BIJ[a][0],SIG[b][0],'u-s' if c==0 else 'u+s')
    if fam==1: return pre+'gf[off%d,%s,%s]%s'%(a,'rev' if b else 'fwd','D/x' if c==0 else 'x/D','.dlog' if dl else '.raw')
    if fam==3: return pre+'%s'%('vig c-p' if a==0 else 'beau c+p')
    if fam==4: return '%s skip@%d'%('vig c-p' if a==0 else 'beau c+p',b-1)
    return '?'
def fragment(model,p,c,prev):
    """Mirror of frag.c do_crib for one model. c: cipher context from opening; prev: c[pos-1] or -1. Returns (frag, m) or None."""
    fint,fam,dl,a,b,cc=decode_model(model); L=len(p)
    intr=[(p[j]==0 and c[j]==0) for j in range(L)]
    if fint and not any(intr): return None
    pr=[];last=prev
    for j in range(L):
        pr.append(last)
        if not (fint and intr[j]): last=c[j]
    Dv=[]
    for j in range(L):
        if fint and intr[j]: Dv.append(-2); continue
        Dv.append(-1 if pr[j]<0 else (c[j]-pr[j])%29)
    f=[]
    if fam==0:
        for j in range(L):
            if Dv[j]<=0: continue
            u=BT[a][Dv[j]]; sv=SGT[b][p[j]]
            f.append((u+sv)%28 if cc else (u-sv)%28)
        return f,28
    if fam==1:
        for j in range(L):
            if Dv[j]<=0: continue
            x=0 if p[j]==28 else 1+(((a-p[j])%28) if b else (p[j]+a)%28)
            if x==0: return None
            k=(x*INV[Dv[j]])%29 if cc else (Dv[j]*INV[x])%29
            f.append(DL2[k] if dl else k)
        return f,(28 if dl else 29)
    if fam==3:
        for j in range(L):
            if fint and intr[j]: continue
            f.append((c[j]+p[j])%29 if a else (c[j]-p[j])%29)
        return f,29
    if fam==4:
        j0=b-1; pv=prev if j0==0 else c[j0-1]
        if pv<0: return None
        for j in range(L):
            if j==j0: f.append((pv+p[j])%29 if a else (pv-p[j])%29)
            f.append((c[j]+p[j])%29 if a else (c[j]-p[j])%29)
        return f,29
def all_models(L=40):
    ms=[]
    for fint in (0,1):
        for bb in range(14):
            for s in range(30):
                for fo in range(2): ms.append((fint<<28)|(bb<<16)|(s<<8)|fo)
        for off in range(28):
            for orr in range(2):
                for iv in range(2):
                    for dl in (0,1): ms.append((fint<<28)|(dl<<27)|(1<<24)|(off<<16)|(orr<<8)|iv)
        for fo in range(2): ms.append((fint<<28)|(3<<24)|(fo<<16))
    for fo in range(2):
        for j0 in range(L): ms.append((4<<24)|(fo<<16)|((j0+1)<<8))
    return ms
