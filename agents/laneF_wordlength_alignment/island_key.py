# Item 5 check on the only above-null island (base_mP2, s6, Imitation of Christ, cipher words 1979-1996):
# implied chain-increment key under x = Gematria index, for the exactly matched words only.
import numpy as np, core, lpdata
T,PG,CH=core.target(); U,C,sha=lpdata.unsolved(); C=np.array(C)
wid=np.concatenate([np.array(p['word']) for p in U]); uw=list(dict.fromkeys(wid.tolist()))
plain='HE LOVETH FOR HIS BELOVED FOR JESUS WILL BE LOVED ALONE ABOVE ALL THINGSTHE LOVEOF CREATED THINGS IS'.split()
cw=list(range(1979,1997))
TR=lpdata.TR
def runes(w):
    w=w.replace('K','C').replace('V','U').replace('Q','C').replace('Z','S'); out=[];i=0
    while i<len(w):
        if w.startswith('ING',i): out.append(TR.index('NG')); i+=3; continue
        two=w[i:i+2]
        if two in ('TH','NG','EA','EO','OE','AE','IA'): out.append(TR.index(two)); i+=2; continue
        if two=='IO': out.append(TR.index('IA')); i+=2; continue
        out.append(TR.index(w[i])); i+=1
    return out
ks=[];ksG=[]
for k,(c,pw) in enumerate(zip(cw,plain)):
    pos=np.where(wid==uw[c])[0]; pr=runes(pw)
    if len(pr)!=len(pos): print('skip word',c,pw,len(pr),len(pos)); continue
    for q,p in zip(pos,pr):
        if q==0: continue
        D=(C[q]-C[q-1])%29
        if D==0: continue
        ks.append((D-1-p)%28)
        ksG.append((D*pow(p,-1,29))%29 if p!=0 else None)
ks=np.array(ks); n=len(ks); f=np.bincount(ks,minlength=28)
ioc=(f*(f-1)).sum()/(n*(n-1))*28
print('runes with key value:',n,' additive key IoC (norm, 1.0 random) = %.2f'%ioc)
print('key additive:',ks.tolist())
g=[x for x in ksG if x is not None]; print('GF(29) key:',g)
