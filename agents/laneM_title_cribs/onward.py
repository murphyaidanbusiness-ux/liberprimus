"""Step 5 / test (f) by key hypothesis: a keyword, numeric or recurrence hit implies a key that continues past the crib.
Decrypt onward under that key with the same model (beam over the skip-on-repeat / sigma-collision ambiguities) and score the plaintext."""
import numpy as np, json, math
from common import *
import pyfrag, vocab
from pyfrag import decode_model, BT, SGT, INV, DL2, Q, T3, B2, U1
SRC=pyfrag.SRC
C=None
def corpus():
    global C
    if C is None:
        import geom; C=list(geom.C)
    return C
def lmscore(seq):
    s=seq; n=len(s)
    if n==0: return -99
    sm=U1[s[0]]+(B2[s[0]*29+s[1]] if n>1 else 0)+(T3[(s[0]*29+s[1])*29+s[2]] if n>2 else 0)
    for j in range(3,n): sm+=Q[((s[j-3]*29+s[j-2])*29+s[j-1])*29+s[j]]
    return sm/n/1000.
def cond(hist,p):
    h=hist[-3:]
    if len(h)==3: return Q[((h[0]*29+h[1])*29+h[2])*29+p]
    if len(h)==2: return T3[(h[0]*29+h[1])*29+p]
    if len(h)==1: return B2[h[0]*29+p]
    return U1[p]
def inv_sigma(b):
    t={}
    for p in range(29): t.setdefault(SGT[b][p],[]).append(p)
    return t
def decrypt_onward(model, crib, c, prev, keyfn, nfrag, N=60, beam=12):
    """keyfn(i) -> key value for fragment element index i (0 = first crib fragment element, possibly up to a shift/negation
    which is resolved by aligning on the crib fragment). Decrypts runes c[len(crib):len(crib)+N]."""
    fint,fam,dl,a,b,cc=decode_model(model); L=len(crib)
    out_states=[(0.0,list(crib),nfrag,0)]  # (score, plaintext, next key index, skipflag)
    for j in range(L,min(L+N,len(c))):
        new=[]
        for sc,pt,ki,_ in out_states:
            pv=c[j-1]
            if fam in (0,1):
                D=(c[j]-pv)%29
                if D==0: new.append((sc,pt+[None],ki,0)); continue
                k=keyfn(ki)
                if k is None: continue
                if fam==0:
                    u=BT[a][D]; sv=(k-u)%28 if cc else (u-k)%28
                    for p in inv_sigma(b).get(sv,[]): new.append((sc+cond([x for x in pt if x is not None],p),pt+[p],ki+1,0))
                else:
                    if k is None: continue
                    kk=pow(2,int(k),29) if dl else int(k)%29
                    if kk==0: continue
                    x=(kk*D)%29 if cc else (D*INV[kk])%29
                    # x = 1+((p+a)%28) or 1+((a-p)%28)
                    for p in range(28):
                        xx=1+(((a-p)%28) if b else (p+a)%28)
                        if xx==x: new.append((sc+cond([x_ for x_ in pt if x_ is not None],p),pt+[p],ki+1,0))
            elif fam in (3,4):
                k0=keyfn(ki)
                if k0 is None: continue
                p=(k0-c[j])%29 if a else (c[j]-k0)%29
                hist=[x for x in pt if x is not None]
                # normal reading: valid iff no would-be repeat
                new.append((sc+cond(hist,p),pt+[p],ki+1,0))
                # skip reading: key ki would have produced pv; actual uses ki+1
                k1=keyfn(ki+1)
                if k1 is None: continue
                p2=(k1-c[j])%29 if a else (c[j]-k1)%29
                if ((k0-p2)%29 if a else (p2+k0)%29)==pv: new.append((sc+cond(hist,p2),pt+[p2],ki+2,1))
        new.sort(key=lambda s:-s[0]); out_states=new[:beam]
        if not out_states: return None
    best=out_states[0]; pt=[x for x in best[1][L:] if x is not None]
    return lmscore(pt), pt
