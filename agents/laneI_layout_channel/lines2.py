import numpy as np, channels as ch, core, json
C=ch.C; Lo=ch.Lo; nl=len(ch.llen)
lid=np.repeat(np.arange(nl),ch.llen); word=Lo['word']; sent=Lo['sent']
wb=(word[1:]!=word[:-1])&(lid[1:]==lid[:-1]); sb=(sent[1:]!=sent[:-1])&(lid[1:]==lid[:-1])
dash=np.zeros(nl); dot=np.zeros(nl)
np.add.at(dash,lid[1:][wb&~sb],1); np.add.at(dot,lid[1:][sb],1)
# which lines are last lines of a page/section? line is last of its page if page changes after it
page=Lo['page']; lastpg=np.zeros(nl,bool)
ends=np.cumsum(ch.llen)-1
lastpg[:]=np.append(page[ends[:-1]]!=page[ends[:-1]+1],True)
keep=(~lastpg)&(ch.llen>=15)
print('lines',nl,'kept',keep.sum())
rng=np.random.default_rng(2)
def fit(Cs,keep):
    comp=np.zeros((nl,29)); np.add.at(comp,(lid,Cs),1)
    A=np.hstack([comp,dash[:,None],dot[:,None]])[keep]
    w,_,_,_=np.linalg.lstsq(A,np.ones(keep.sum()),rcond=None)
    return (A@w-1).std(), w
sd,w=fit(C,keep)
nulls=[fit(rng.permutation(C),keep)[0] for _ in range(300)]
print('width-fit residual sd real %.4f null %.4f +- %.4f z=%.1f'%(sd,np.mean(nulls),np.std(nulls),(sd-np.mean(nulls))/np.std(nulls)))
wr=w[:29]/w[:29].mean()
print('widths',dict(zip(core.TR,np.round(wr,2))),'dash',w[29]/w[:29].mean(),'dot',w[30]/w[:29].mean())
y=ch.llen[keep]; print('kept llen mean %.2f sd %.2f min %d max %d'%(y.mean(),y.std(),y.min(),y.max()))
# separator-only null: llen_kept vs separators
print('corr(llen,dash)=%.3f'%np.corrcoef(y,dash[keep])[0,1])
def ac(x,l): x=x-x.mean(); return float((x[:-l]*x[l:]).sum()/(x*x).sum())
x=ch.llen[keep].astype(float)
print('acf llen kept',[round(ac(x,l)*np.sqrt(len(x)),1) for l in range(1,7)],'(z units)')
# position-in-page effect
pos=np.zeros(nl,int); 
st,ln=core.runs(page[np.cumsum(ch.llen)-1])
for a,l in zip(st,ln): pos[a:a+l]=np.arange(l)
m=[ch.llen[(pos==i)&keep].mean() for i in range(12)]; print('mean runes by line-in-page',np.round(m,2))

# greedy-fill consistency: exists margin M with Wline <= M < Wline + w_next for (almost) all lines?
# lines used: kept, and not last line of page; next rune = first rune of next line
ends=np.cumsum(ch.llen)-1
comp=np.zeros((nl,29)); np.add.at(comp,(lid,C),1)
A=np.hstack([comp,dash[:,None],dot[:,None]])
Wl=A@w
nxt=np.array([C[e+1] if e+1<len(C) else 0 for e in ends])
# separator before next rune (if the break falls at a word boundary the dash is at line end/begin): ignore
wn=w[nxt]
use=keep.copy(); use[-1]=False
def cover(Wl,wn,use):
    lo=Wl[use]; hi=lo+wn[use]
    ms=np.sort(np.concatenate((lo,hi)))
    best=0;bm=0
    for m in ms:
        c=((lo<=m)&(m<hi)).sum()
        if c>best: best=c;bm=m
    return best/use.sum(), bm
cr,bm=cover(Wl,wn,use)
rng=np.random.default_rng(5)
nn=[cover(Wl,rng.permutation(wn),use)[0] for _ in range(100)]
print('greedy-fill coverage real %.3f null (shuffled next glyph) %.3f +- %.3f max %.3f; margin M=%.3f'%(cr,np.mean(nn),np.std(nn),np.max(nn),bm))
print('Wline sd %.3f, mean next-glyph width %.3f'%(Wl[use].std(),wn[use].mean()))
