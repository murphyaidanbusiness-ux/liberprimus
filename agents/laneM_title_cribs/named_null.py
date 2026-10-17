"""Null for the named cribs: same crib, same models, at 100 random word starts -> distribution of best English-ness z."""
import random, numpy as np, json, geom, vocab, ext
from pyfrag import fragment, all_models
C=geom.C; ms=all_models(); rng=random.Random(9)
starts=[s for s in geom.starts if 1<s<len(C)-80]
out={}
for phrase in ('AN EPIPHANY','AN INSTAR','AN AWAKENING','AN INSTRUCTION'):
    crib=list(vocab.spell(phrase))
    if phrase=='AN INSTRUCTION': crib=list(vocab.spellings('AN')[0]+vocab.spell('INSTRUCTION',io=False))
    zs=[]
    for k in range(100):
        pos=rng.choice(starts); c=C[pos:pos+40]; prev=C[pos-1]; best=-99
        for mdl in ms:
            fr=fragment(mdl,crib,c,prev)
            if fr is None or len(fr[0])<5: continue
            z,_=ext.zeng(*fr); best=max(best,z)
        zs.append(best)
    zs=np.array(zs); out[phrase]=dict(mean=float(zs.mean()),sd=float(zs.std()),max=float(zs.max()),frac_ge_5_49=float((zs>=5.49).mean()))
    print(phrase,out[phrase],flush=True)
json.dump(out,open('named_null.json','w'),indent=1)
