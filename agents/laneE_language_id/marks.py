import numpy as np, collections, pickle
from stats import *
from variants import *
sents=unsolved_seq()
L=[x for s in sents for x in s]; N=len(L); ns=len(sents)
starts=np.cumsum([0]+[len(s) for s in sents])
first=np.array([s[0] for s in sents]); last=np.array([s[-1] for s in sents])
L=np.array(L)
print('words',N,'sentences',ns,'overall mean',L.mean().round(3),'first mean',first.mean().round(3),'last mean',last.mean().round(3))
# permutation: random placement of ns-1 interior marks among N-1 gaps
rng=np.random.default_rng(11)
def stats_for(cuts):
    cuts=np.sort(cuts); st=np.concatenate([[0],cuts,[N]])
    f=L[st[:-1]]; l=L[st[1:]-1]
    return f.mean(),l.mean(),np.mean(f==2),np.mean(l==2),np.mean(f>=7),np.mean(l>=7)
obs=stats_for(starts[1:-1])
perm=np.array([stats_for(rng.choice(np.arange(1,N),ns-1,replace=False)) for _ in range(5000)])
print('observed first mean,last mean, first==2, last==2, first>=7, last>=7:',np.round(obs,3))
print('random-placement null mean:',np.round(perm.mean(0),3),'sd:',np.round(perm.std(0),3))
print('z:',np.round((np.array(obs)-perm.mean(0))/perm.std(0),2))
# same on English with real punctuation: z of first/last mean relative to random placement
def eng_z(name,rem,mode='cic'):
    C=pickle.load(open(HERE+'/streams.pkl','rb'))
    q=seq_from_stream(C[name][0],rem,mode)
    Lw=q.L; Nn=len(Lw); sel=[]
    zs=[]
    rng2=np.random.default_rng(2)
    for rep in range(40):
        s0=int(rng2.integers(0,q.ns-175)); a=q.starts[s0]; b=q.starts[s0+175]
        Lw_=Lw[a:b]; n=len(Lw_)
        st=q.starts[s0:s0+176]-a
        f=Lw_[st[:-1]].mean(); l=Lw_[st[1:]-1].mean()
        # null
        nl=[];nf=[]
        for _ in range(200):
            cuts=np.sort(rng2.choice(np.arange(1,n),174,replace=False)); s=np.concatenate([[0],cuts,[n]])
            nf.append(Lw_[s[:-1]].mean()); nl.append(Lw_[s[1:]-1].mean())
        zs.append(((f-np.mean(nf))/np.std(nf),(l-np.mean(nl))/np.std(nl)))
    return np.mean(zs,0)
for nm,rem in [('Cicero Tusculan (English tr.)',THEOFTO),('Emerson Essays I',THEOFTO),('Moby Dick',THEOFTO),('Plato Republic (Jowett)',THEOFTO),('Gospel of Buddha (Carus)',THEOFTO),('Dutch: bible-corpus',frozenset()),('Agrippa Occult Phil I',THEOFTO)]:
    print('%-32s mean z(first),z(last) of 175-sentence windows vs random mark placement: %s'%(nm,np.round(eng_z(nm,rem),2)))
# sentence-length: geometric fit
p=ns/N
lens=np.array([len(s) for s in sents])
edges=[1,2,4,7,11,17,26,40,60,10**6]
obsb=np.histogram(lens,bins=edges)[0]
cdf=lambda k:1-(1-p)**(k-1)   # P(len<k)... geometric on 1..: P(len>=k)=(1-p)^(k-1)
probs=[(1-p)**(edges[i]-1)-(1-p)**(edges[i+1]-1) for i in range(len(edges)-1)]
probs=np.array(probs)/np.sum(probs)
exp=probs*ns
chi=((obsb-exp)**2/exp).sum()
print('sentence length bins',edges); print('obs',obsb.tolist()); print('geometric exp',np.round(exp,1).tolist(),'chi2=%.1f df=%d'%(chi,len(exp)-1))
from math import exp as ex
# p-value via simulation
sim=[]
for _ in range(5000):
    cuts=np.sort(rng.choice(np.arange(1,N),ns-1,replace=False)); ln=np.diff(np.concatenate([[0],cuts,[N]]))
    ob=np.histogram(ln,bins=edges)[0]; sim.append(((ob-exp)**2/exp).sum())
print('p(chi2>=obs | random placement)=',np.mean(np.array(sim)>=chi))
print('variance/mean of sentence length: obs sd %.1f mean %.1f ; random-placement sd %.1f'%(lens.std(),lens.mean(),np.mean([np.std(np.diff(np.concatenate([[0],np.sort(rng.choice(np.arange(1,N),ns-1,replace=False)),[N]]))) for _ in range(500)])))
# Real English: sentence length sd/mean for 175-sentence windows of Cicero-minus
C=pickle.load(open(HERE+'/streams.pkl','rb'))
for nm in ['Cicero Tusculan (English tr.)','Moby Dick','Emerson Essays I']:
    q=seq_from_stream(C[nm][0],THEOFTO); print(nm,'sentence length mean %.1f sd %.1f (CV %.2f); random geometric CV ~ %.2f ; obs unsolved CV %.2f'%(q.slen.mean(),q.slen.std(),q.slen.std()/q.slen.mean(),1.0,lens.std()/lens.mean()))
# rune-length position of marks within line
U,Cc,sha=lpdata.unsolved()
pos=[]
for p in U:
    w=p['word'];l=p['line'];s=p['sent']
    for i in range(len(w)-1):
        if s[i]!=s[i+1]:
            # mark between rune i and i+1; position of rune i within its line
            ln=[j for j in range(len(l)) if l[j]==l[i]]
            pos.append((i-ln[0]+1,len(ln),l[i]!=l[i+1]))
pos=np.array(pos,float)
print('marks:',len(pos),'at line end:',np.mean(pos[:,2]==1).round(3),'(expected for random: ~',round(float(np.mean([1/ln for ln in pos[:,1]])),3),')')
rel=pos[:,0]/pos[:,1]; print('relative position in line mean %.3f (uniform 0.5), hist(5):'%rel.mean(),np.histogram(rel,bins=5,range=(0,1))[0])
