import pickle, numpy as np, collections
from stats import *
from variants import *
d=pickle.load(open('results_main.pkl','rb')); R=d['R']
B=pickle.load(open('boot.pkl','rb'))
keys=B['keys']; cf0=B['cf0']; cw0=B['cw0']; CF=B['CF']; CW=B['CW']; obs=B['obs']; valid=B['valid']
kidx={k:i for i,k in enumerate(keys)}
out=[]
def P(s=''): out.append(s)
def tab(sel,title,use='cf',maxn=25,note=''):
    arr,AB=(cf0,CF) if use=='cf' else (cw0,CW)
    ids=sorted([kidx[k] for k in sel if k in kidx],key=lambda i:arr[i])
    ranks=np.argsort(np.argsort(AB[:,ids],1),1)+1
    P('**'+title+'**'+note); P()
    P('| # | candidate (corpus [variant]) | words | mean len | score ± boot SE | rank 95% interval | JS A len | JS B bigram | JS C first | JS D last | JS E sent-len | z vs own-corpus window null (A,B,C,D,E) |')
    P('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for j,i in enumerate(ids[:maxn]):
        k=keys[i]; r=R[k]
        nm=k[0] if k[1]=='natural' else '%s [%s]'%(k[0],k[1])
        rl,rh=np.percentile(ranks[:,j],[2.5,97.5])
        P('| %d | %s | %dk | %.2f | %.2f ± %.2f%s | %d-%d | %.4f | %.4f | %.4f | %.4f | %.4f | %s |'%(j+1,nm,r['nw']//1000,r['meanlen'],arr[i],AB[:,i].std(),'' if (valid[i] or use=='cw') else ' (no sent. stats)',rl,rh,*obs[i],' '.join('%+.1f'%x for x in r['z'])))
    P()
# TOP overall
allk=[k for k in keys]
tab(allk,'Table 2a. Top 25 individual candidates, full score (mean of the 5 JS divergences, each divided by its median over all candidates; lower = closer)',use='cf',maxn=25)
tab(allk,'Table 2b. Top 25 individual candidates, word-level score only (A length marginal + B length bigram)',use='cw',maxn=25)
nat_nonen=[k for k in keys if k[1]=='natural' and R[k]['lang']!='en']
tab(nat_nonen,'Table 3. Best NON-English natural corpora (full score)',use='cf',maxn=14)
tab(nat_nonen,'Table 3b. Best NON-English natural corpora (word-level score)',use='cw',maxn=10)
nat_en=[k for k in keys if k[1]=='natural' and R[k]['lang']=='en']
tab(nat_en,'Table 4. Best unmodified English corpora (all registers, full score)',use='cf',maxn=12)
# marginal summary
sents=unsolved_seq(); uq=Seq(sents)
C=pickle.load(open(HERE+'/streams.pkl','rb'))
def summ(q):
    L=q.L; 
    pairs=q.cells[q.cells>=0]
    return [L.mean(),np.mean(L==1),np.mean(L==2),np.mean(L==3),np.mean(L>=8),q.slen.mean(),np.mean(q.slen<=3),(q.L[q.starts[:-1]]).mean(),(q.L[q.starts[1:]-1]).mean(),np.mean(pairs==9)]
rows=[('UNSOLVED (2,896 words, 175 sentences)',summ(uq))]
for nm,v in [('Cicero Tusculan (English tr.)','-THE/OF/TO'),('Emerson Essays I','-THE/OF/TO'),('Moby Dick','-THE/OF'),('Moby Dick','base (Cicada rules)'),('Moby Dick','letters (no digraphs)'),('Plato Republic (Jowett)','base (Cicada rules)')]:
    lab,rem,mode,arch=[x for x in VARIANTS if x[0]==v][0]
    rows.append(('%s [%s]'%(nm,v),summ(seq_from_stream(C[nm][0],rem,mode))))
for nm in ['Dutch: bible-corpus','Danish: bible-corpus','Latin: Newton Principia','Old English: Beowulf','German: Faust','Welsh: CCG treebank']:
    rows.append((nm,summ(seq_from_stream(C[nm][0]))))
P('**Table 1. Raw marginals (all as % unless noted)**'); P()
P('| text | mean word len (runes) | 1-rune | 2-rune | 3-rune | 8+ rune | mean sentence len (words) | sentences <=3 words | mean first-word len | mean last-word len | adjacent 2-2 pairs |')
P('|---|---|---|---|---|---|---|---|---|---|---|')
for nm,s in rows:
    P('| %s | %.2f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f | %.2f | %.2f | %.1f |'%(nm,s[0],100*s[1],100*s[2],100*s[3],100*s[4],s[5],100*s[6],s[7],s[8],100*s[9]))
P()
# LP1 calibrated
rng=np.random.default_rng(3)
uc=uq.counts()
txt=open(K18+'lp1_english_forward.txt',encoding='utf-8').read()
stream=[]
for l in [l for l in txt.split('\n') if l.strip()]: stream+=tokenize(l)+['.']
P('**Table 5. Cicada\'s own solved text (LP1, 729 words) vs the unsolved pages, with a size-matched noise floor**'); P()
P('| LP1 treatment | JS A (len) | floor mean ± sd for a 729-word sample of a text that truly matches (Cicero tr. -THE/OF/TO windows vs its own corpus) | JS B (bigram) |'); P('|---|---|---|---|')
q=seq_from_stream(C['Cicero Tusculan (English tr.)'][0],THEOFTO); gc=q.counts()
fl=[]
for _ in range(400):
    s0=int(rng.integers(0,q.ns)); s1=int(np.searchsorted(q.starts,q.starts[s0]+729))
    if s1>q.ns: continue
    c=q.counts(q.starts[s0],q.starts[s1],s0,s1); fl.append([js(c[0],gc[0]),js(c[1],gc[1])])
fl=np.array(fl)
for lab,rem,mode in [('as is',frozenset(),'cic'),('THE/OF/TO deleted',THEOFTO,'cic'),('letters (no digraphs)',frozenset(),'letters')]:
    qq=seq_from_stream(stream,rem,mode); g=qq.counts()
    P('| %s | %.4f | A: %.4f ± %.4f | %.4f (floor B: %.4f ± %.4f) |'%(lab,js(uc[0],g[0]),fl[:,0].mean(),fl[:,0].std(),js(uc[1],g[1]),fl[:,1].mean(),fl[:,1].std()))
P()
open('final_tables.md','w').write('\n'.join(out))
print('\n'.join(out))
