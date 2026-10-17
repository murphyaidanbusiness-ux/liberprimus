import pickle, numpy as np, collections, sys
from stats import *
C=pickle.load(open(HERE+'/streams.pkl','rb'))
B=pickle.load(open('boot.pkl','rb')); S_=B['S']
pool_names=['Moby Dick','Plato Republic (Jowett)','Emerson Essays I','Gospel of Buddha (Carus)','Cicero Tusculan (English tr.)','Agrippa Occult Phil I','Paine Age of Reason','Poe Complete Works','Austen Emma','Bhagavad Gita (Arnold)']
sents=unsolved_seq(); uq=Seq(sents); uc=uq.counts()
def build_pool(names,maxw=60000):
    toks=[];sid=[]
    s=0
    for n in names:
        st=C[n][0]; cnt=0
        for t in st:
            if t=='.' : s+=1
            elif t==';': pass
            else:
                toks.append(t); sid.append(s); cnt+=1
                if cnt>=maxw: break
        s+=1
    return toks,np.array(sid)
def run(names,mode,label,steps=8,top=45):
    toks,sid=build_pool(names)
    vocab={};tid=np.empty(len(toks),int)
    for i,t in enumerate(toks):
        tid[i]=vocab.setdefault(t,len(vocab))
    inv=[None]*len(vocab)
    for w,i in vocab.items(): inv[i]=w
    lens=np.array([runelen(w,mode) for w in inv])
    freq=np.bincount(tid,minlength=len(vocab))
    cand=list(np.argsort(-freq)[:top])
    removed=np.zeros(len(vocab),bool)
    def objective(mask,detail=False):
        keep=~mask[tid]; kp=np.flatnonzero(keep)
        L=lens[tid[kp]]; s=sid[kp]
        A=np.bincount(np.minimum(L,11)-1,minlength=11)
        same=s[1:]==s[:-1]
        c=(np.minimum(L[:-1],8)-1)*8+np.minimum(L[1:],8)-1
        Bc=np.bincount(c[same],minlength=64)
        ja=js(uc[0],A);jb=js(uc[1],Bc)
        return (ja/S_[0]+jb/S_[1])/2,ja,jb,L.mean()
    path=[('(none)',)+objective(removed)]
    chosen=[]
    for step in range(steps):
        best=None
        for c in cand:
            if removed[c]: continue
            m=removed.copy(); m[c]=True
            o=objective(m)
            if best is None or o[0]<best[1][0]: best=(c,o)
        removed[best[0]]=True; chosen.append(inv[best[0]])
        path.append(('+'+inv[best[0]],)+best[1])
    print('== %s (%s), pool %d words, candidates top-%d'%(label,mode,len(toks),top))
    for p in path: print('  %-10s obj=%.3f JS_A=%.4f JS_B=%.4f meanlen=%.2f'%p)
    return path
out={}
out['cic']=run(pool_names,'cic','cic digraphs')
out['letters']=run(pool_names,'letters','letters')
out['th']=run(pool_names,'th','TH only')
for nm in ['Plato Republic (Jowett)','Moby Dick','Emerson Essays I','Cicero Tusculan (English tr.)']:
    out['cic:'+nm]=run([nm],'cic','single corpus '+nm,steps=5)
pickle.dump(out,open('greedy.pkl','wb'))
