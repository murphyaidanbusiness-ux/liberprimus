import sys, os, numpy as np, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from engine import *
MSG="THE PATH LIES EMPTY EPIPHANY SEEKS THE DEVOTED LIBER PRIMUS IS THE WAY ITS WORDS ARE THE MAP THEIR MEANING IS THE ROAD AND THEIR NUMBERS ARE THE DIRECTION BEWARE FALSE PATHS ALWAYS VERIFY THE SIGNATURE YOU HAVE DONE WELL TO COME THIS FAR PATIENCE IS A VIRTUE"
msg=np.array([ord(c)-65 for c in MSG if c.isalpha()])
print('message letters',len(msg))
Vd=views(); pmi=PMI(Vd)
rng=np.random.default_rng(7)
def zscore(V,sem,nums,b,mode,sname):
    vid=pmi.vid(V)
    kind,arr=apply_semantic(V,sem,nums,b,mode,minm=10)
    real=score_output(V,kind,arr,pmi,vid)
    out={}
    for k in real:
        nl=[]
        for rep in range(50):
            nn=rng.permutation(nums) if rep<50 else None
            r=apply_semantic(V,sem,nn,b,mode,minm=10); nl.append(score_output(V,r[0],r[1],pmi,vid)[k] if r is not None else float('nan'))
        nr=[]
        for rep in range(50):
            nn=rng.integers(nums.min(),nums.max()+1,size=len(nums))
            r=apply_semantic(V,sem,nn,b,mode,minm=10); nr.append(score_output(V,r[0],r[1],pmi,vid)[k] if r is not None else float('nan'))
        nl=np.array(nl);nr=np.array(nr)
        nl=nl[~np.isnan(nl)]; nr=nr[~np.isnan(nr)]
        out[k]=(real[k],(real[k]-nl.mean())/nl.std() if len(nl)>3 else float('nan'),(real[k]-nr.mean())/nr.std() if len(nr)>3 else float('nan'))
    return out
res=[]
def report(name,out,note=''):
    s='; '.join(f'{k}: real={v[0]:.3f} z_shuf={v[1]:.1f} z_rand={v[2]:.1f}' for k,v in out.items())
    print(f'{name}: {s} {note}',flush=True); res.append((name,out))
# 1 letter-number (SR)
V=Vd['SR_doyle']
def pos_of(V,letter): return np.flatnonzero(V.L==letter)
nums=np.array([rng.choice(pos_of(V,c))+1 for c in msg])
report('SR_doyle L b1 mod (letter number)',zscore(V,'L',nums,1,'mod','x'))
# 2 word number -> first letter
fl=V.L[V.wstart[:-1]]
nums=np.array([rng.choice(np.flatnonzero(fl==c))+1 for c in msg])
report('SR_doyle W b1 mod (word number, first letter)',zscore(V,'W',nums,1,'mod','x'))
# 3 four-tuples
def tup(V,c):
    cand=np.flatnonzero(V.L==c); pos=rng.choice(cand)
    w=np.searchsorted(V.wstart,pos,side='right')-1; l=pos-V.wstart[w]
    s=np.searchsorted(V.sw,w,side='right')-1; wi=w-V.sw[s]
    p=np.searchsorted(V.ps,s,side='right')-1; si=s-V.ps[p]
    return [p+1,si+1,wi+1,l+1]
nums=np.array([x for c in msg for x in tup(V,c)])
report('SR_doyle TPSWL b1 raw (2014 para:sent:word:letter)',zscore(V,'TPSWL',nums,1,'raw','x'))
report('SR_doyle TPSWL b1 mod',zscore(V,'TPSWL',nums,1,'mod','x'))
# 4 prime index n -> n-th prime -> letter
cands={}
for n in range(1,4000):
    m=PR[n-1]; 
    if m-1<V.nL: cands.setdefault(V.L[m-1],[]).append(n)
nums=np.array([rng.choice(cands[c]) for c in msg])
report('SR_doyle Lp b1 mod (n-th prime -> letter)',zscore(V,'Lp',nums,1,'mod','x'))
# 5 AL chapter:verse:letter
V2=Vd['AL_verse']
def tupAL(V,c):
    return tup(V,c)
# AL P=chapter S=verse, spec PSL: letter within verse
def tupPSL(V,c):
    cand=np.flatnonzero(V.L==c); pos=rng.choice(cand)
    s=np.searchsorted(V.sl,pos,side='right')-1; l=pos-V.sl[s]
    p=np.searchsorted(V.ps,s,side='right')-1; si=s-V.ps[p]
    return [p+1,si+1,l+1]
nums=np.array([x for c in msg for x in tupPSL(V2,c)])
report('AL_verse TPSL b1 raw (chapter:verse:letter)',zscore(V2,'TPSL',nums,1,'raw','x'))
# 6 2012-style line:letter on Mab_lines (S=line, P=1) -> spec SL
V3=Vd['Mab_lines']
def tupSL(V,c):
    cand=np.flatnonzero(V.L==c); pos=rng.choice(cand)
    s=np.searchsorted(V.sl,pos,side='right')-1; l=pos-V.sl[s]
    return [s+1,l+1]
nums=np.array([x for c in msg for x in tupSL(V3,c)])
report('Mab_lines TSL b1 raw (line:letter)',zscore(V3,'TSL',nums,1,'raw','x'))
# 7 embedded window in real LP2 gsum stream (whole-stream scoring, dilution test)
from sources import lp2_sources
src,idx,st=lp2_sources()
g=src['gsum'].copy()
fl=V.L[V.wstart[:-1]]
nums=np.array([rng.choice(np.flatnonzero(fl==c))+1 for c in msg])
off=1000; g[off:off+len(msg)]=nums
report('SR_doyle W b1 mod: 200-pointer message embedded in the real 2896-word gsum stream (whole-stream score)',zscore(V,'W',g,1,'mod','x'))
# word-sequence message
WM="WE MUST TRUST THE VOICE OF THE SOUL FOR EVERY MAN HAS A TRUTH WITHIN HIM AND THE WORLD IS FULL OF THOSE WHO LOOK FOR IT IN OTHER PLACES BUT NEVER FIND IT AND SO WE ARE TAUGHT TO LIVE BY THE LAW OF OUR OWN NATURE AND TO SPEAK WHAT WE KNOW"
V=Vd['SR_doyle']
ws=WM.split(); idxs={}
for i,w in enumerate(V.words): idxs.setdefault(w,[]).append(i)
miss=[w for w in ws if w not in idxs]; print('missing words',miss)
ws=[w for w in ws if w in idxs]
nums=np.array([rng.choice(idxs[w])+1 for w in ws])
report('SR_doyle W b1 mod (word-sequence message, %d words)'%len(ws),zscore(V,'W',nums,1,'mod','x'))
# windowed: score only the window
import pickle; pickle.dump(res,open('results/controls.pkl','wb'))
