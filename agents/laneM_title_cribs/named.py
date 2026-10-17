"""The addendum's named title hypotheses: per (opening, crib) all models; best English-ness z, longest structural hit,
and pairwise agreement of fragments between openings (key restart) for the same model."""
import json, itertools, numpy as np, collections
from common import *
import geom, vocab, pyfrag, ext
from pyfrag import fragment, engscore, lookup, all_models, model_name
C=geom.C
secpos={o['id']:o['pos'] for o in geom.openings if o['kind']=='sec'}
NAMED=[(1,'AN INSTRUCTION'),(8,'AN INSTAR'),(10,'AN EPIPHANY'),(10,'AN AWAKENING'),(7,'LOSS OF DIVINITY'),(4,'AN END'),(16,'A KOAN'),
       (0,'INTERCONNECTEDNESS'),(0,'CONSUMPTION'),(2,'THE'),(9,'THE CIRCUMFERENCE'),(11,'THE'),(13,'THE'),(14,'THE'),(15,'THE'),(12,'PARABLE'),(5,'SOME WISDOM'),(6,'SOME WISDOM'),(3,'SOME')]
ms=all_models()
res=[]; frags={}
for sec,phrase in NAMED:
    pos=secpos[sec]; lens=geom.lens_from(pos); prev=C[pos-1] if pos>0 else -1; c=C[pos:pos+80]
    for sp in itertools.product(*[vocab.spellings(w) for w in phrase.split()]):
        wl=[len(x) for x in sp]
        if wl!=lens[:len(wl)]: continue
        crib=[x for w in sp for x in w]
        best=(-99,None); longest=(0,None); nfr=0
        for mdl in ms:
            fr=fragment(mdl,crib,c,prev)
            if fr is None: continue
            f,m=fr; nfr+=1
            if len(f)>=5:
                z,s=ext.zeng(f,m)
                if z>best[0]: best=(z,mdl)
            h=lookup(f,m,pos)
            if h and len(f)>longest[0]: longest=(len(f),(mdl,h[:3]))
            if not ((mdl>>28)&1) and ((mdl>>24)&7)!=4: frags[(sec,phrase,mdl)]=(f,m)
        res.append(dict(sec=sec,phrase=phrase,spelling=vocab.tr(crib),fragments=nfr,best_eng_z=round(best[0],2),best_model=model_name(best[1]) if best[1] else None,
                        longest_hit=longest[0],hit=(model_name(longest[1][0]),longest[1][1]) if longest[1] else None))
        print(res[-1],flush=True)
# pairwise agreement (key restart): same model, fragments agree on common prefix
pairs=collections.Counter(); best_pairs=[]
keys=sorted(set((s,p) for s,p,_ in frags))
for (s1,p1),(s2,p2) in itertools.combinations(keys,2):
    if s1==s2: continue
    mx=0; mm=None
    for mdl in ms:
        a=frags.get((s1,p1,mdl)); b=frags.get((s2,p2,mdl))
        if not a or not b: continue
        k=0
        while k<min(len(a[0]),len(b[0])) and a[0][k]==b[0][k]: k+=1
        if k>mx: mx,mm=k,mdl
    best_pairs.append(((s1,p1),(s2,p2),mx,model_name(mm) if mm else None))
best_pairs.sort(key=lambda x:-x[2])
print('pairwise longest exact common-prefix agreement (top 10):')
for b in best_pairs[:10]: print(' ',b)
json.dump(dict(cribs=res,pairs=best_pairs),open(OUT+'/named.json','w'),indent=1,default=str)
