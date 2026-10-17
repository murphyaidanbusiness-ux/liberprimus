import pickle, numpy as np, collections
from scorers import symbols, C
from variants import *
from math import sqrt
names=['Moby Dick','Plato Republic (Jowett)','Emerson Essays I','Gospel of Buddha (Carus)','Cicero Tusculan (English tr.)','Agrippa Occult Phil I','Paine Age of Reason','Poe Complete Works']
def freqs(rem,mode):
    tot=collections.Counter(); n=0
    for nm in names:
        w=[t for t in C[nm][0] if t not in '.;' and t not in rem]
        s=symbols(w,mode); tot.update(s); n+=len(s)
    return {k:v/n for k,v in tot.items()}
lo=86/12955-1.96*sqrt(0.0066*0.9934/12955); hi=86/12955+1.96*sqrt(0.0066*0.9934/12955)
print('observed doublet rate 86/12955 = %.4f, 95%% CI [%.4f, %.4f]'%(86/12955,lo,hi))
out=[]
for lab,rem,mode in [('base cic',frozenset(),'cic'),('-THE/OF/TO cic',THEOFTO,'cic'),('letters',frozenset(),'letters'),('letters -THE/OF/TO',THEOFTO,'letters')]:
    f=freqs(rem,mode)
    inr=sorted([(k,v) for k,v in f.items() if lo<=v<=hi],key=lambda x:x[1])
    rare=sorted(f.items(),key=lambda x:x[1])[:8]
    print('%-20s symbols with share in CI: %s | rarest: %s | EA=%.4f'%(lab,', '.join('%s %.2f%%'%(k,100*v) for k,v in inr),', '.join('%s %.2f%%'%(k,100*v) for k,v in rare),f.get('EA',0)))
