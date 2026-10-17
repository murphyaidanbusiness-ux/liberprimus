# Python reference implementations (encrypt + decrypt) mirroring kc.c variant numbering.
import numpy as np
P=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
INV={a:pow(a,27,29) for a in range(1,29)}
TAU=[]; TAU.append({D:D-1 for D in range(1,29)}); TAU.append({D:28-D for D in range(1,29)})
for g in range(2,29):
    x=1;o=0
    while True:
        x=x*g%29;o+=1
        if x==1: break
    if o!=28: continue
    d={};x=1
    for e in range(28): d[x]=e; x=x*g%29
    TAU.append(d)
assert len(TAU)==14
TINV=[{v:D for D,v in t.items()} for t in TAU]
def f1var(v): al=v&1; conv=(v>>1)&1; sg=(v>>2)&1; tt=v>>3; return tt,sg,conv,al
def f2var(v): al=v&1; conv=(v>>1)&1; d=(v>>2)&1; kvm=v>>3; return kvm,d,conv,al
def f2keys(key,kvm):
    k=[(P[x]%29 if kvm else (x+1)%29) for x in key]; return [x for x in k if x]
def dec(fam,c,prev,key,var):
    n=len(c); out=[]
    if fam in (1,2):
        D=[(c[i]-(c[i-1] if i else prev))%29 for i in range(n)]
    if fam==1:
        tt,sg,conv,al=f1var(var); k=[x%28 for x in key]; L=len(k); j=0
        for i in range(al,n):
            if D[i]==0:
                out.append(28)
                if conv: j=(j+1)%L
            else:
                t=TAU[tt][D[i]]; out.append((t+k[j])%28 if sg else (t-k[j])%28); j=(j+1)%L
    elif fam==2:
        kvm,d,conv,al=f2var(var); k=f2keys(key,kvm); L=len(k); mul=[x if d else INV[x] for x in k]; j=0
        for i in range(al,n):
            if D[i]==0:
                out.append(28)
                if conv: j=(j+1)%L
            else:
                out.append((D[i]*mul[j]-1)%29); j=(j+1)%L
    else:
        L=len(key); j=0
        for i in range(n):
            k=key[j]
            f=lambda cc,kk: (cc-kk)%29 if var in (0,3) else (kk-cc)%29 if var in (1,4) else (cc+kk)%29
            p=f(c[i],k)
            if var>=3 and i>0:
                if c[i]==c[i-1]:
                    j=(j+1)%L; out.append(f(c[i],key[j])); j=(j+1)%L; continue
                j1=(j+1)%L
                if (c[i]-c[i-1])%29==(key[j1]-key[j])%29:
                    ps=f(c[i-1],k)
                    sc=[]
                    for cand,jn in ((p,(j+1)%L),(ps,(j+2)%L)):
                        w=[(out[-b] if len(out)>=b else 18) for b in (3,2,1)]+[cand]; jj=jn
                        for a in range(1,6):
                            if i+a<n: w.append(f(c[i+a],key[jj])); jj=(jj+1)%L
                        sc.append(sum(QT[((w[b]*29+w[b+1])*29+w[b+2])*29+w[b+3]] for b in range(len(w)-3)))
                    if sc[1]>sc[0]: out.append(ps); j=(j+2)%L; continue
            out.append(p); j=(j+1)%L
    return out
UNI=np.fromfile('./agents/laneA_keyword_chain/uni29.f64')
QT=np.fromfile('./agents/laneA_keyword_chain/quad29.f32',dtype=np.float32)
def enc(fam,p,key,var,rng,prev=0):
    """returns ciphertext list; for al=1 variants a random junk rune is prepended."""
    c=[]
    if fam==1:
        tt,sg,conv,al=f1var(var); k=[x%28 for x in key]; L=len(k); j=0
        last=prev
        if al: last=int(rng.integers(29)); c.append(last)
        for x in p:
            if x==28:
                D=0
                if conv: j=(j+1)%L
            else:
                tv=(x-k[j])%28 if sg else (x+k[j])%28; D=TINV[tt][tv]; j=(j+1)%L
            last=(last+D)%29; c.append(last)
    elif fam==2:
        kvm,d,conv,al=f2var(var); k=f2keys(key,kvm); L=len(k); j=0; last=prev
        if al: last=int(rng.integers(29)); c.append(last)
        for x in p:
            if x==28:
                D=0
                if conv: j=(j+1)%L
            else:
                xx=(x+1)%29; D= xx*INV[k[j]]%29 if d else xx*k[j]%29; j=(j+1)%L
            last=(last+D)%29; c.append(last)
    else:
        L=len(key); j=0
        f=lambda pp,kk: (pp+kk)%29 if var in (0,3) else (kk-pp)%29 if var in (1,4) else (pp-kk)%29
        for i,x in enumerate(p):
            cc=f(x,key[j])
            if var>=3 and i>0 and cc==c[-1]:
                j=(j+1)%L; cc=f(x,key[j])
            c.append(cc); j=(j+1)%L
    return c
