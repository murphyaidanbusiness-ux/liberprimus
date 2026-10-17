import pickle, numpy as np, collections, re, glob
from stats import *
from variants import *
C=pickle.load(open(HERE+'/streams.pkl','rb'))
B=pickle.load(open('boot.pkl','rb')); S_=B['S']
sents=unsolved_seq(); uq=Seq(sents); uc=uq.counts()
out=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.append(s)
# ---- LP1 reference
txt=open(K18+'lp1_english_forward.txt',encoding='utf-8').read()
lines=[l for l in txt.split('\n') if l.strip()]
stream=[]
for l in lines:
    stream+=tokenize(l)+['.']
P('## LP1 solved text (lp1_english_forward.txt): %d words, %d line-sentences'%(sum(1 for t in stream if t not in '.;'),sum(1 for t in stream if t=='.')))
for lab,rem,mode in [('as is',frozenset(),'cic'),('-THE/OF/TO',THEOFTO,'cic'),('letters',frozenset(),'letters')]:
    q=seq_from_stream(stream,rem,mode); gc=q.counts()
    # noise floor for n words: resample sentences of LP1 itself? compare unsolved resample to LP1
    P('LP1 %-12s words=%d meanlen=%.2f meansent=%.1f  JS vs unsolved: A=%.4f B=%.4f C=%.4f D=%.4f E=%.4f'%(lab,q.nw,q.L.mean(),q.slen.mean(),*[js(uc[i],gc[i]) for i in range(5)]))
# size-matched noise: unsolved subsample of 729 words vs full unsolved
rng=np.random.default_rng(1)
fl=[]
for _ in range(300):
    # sample 729 words contiguous-sentence subset from unsolved
    idx=rng.integers(0,len(sents),60); sub=[sents[i] for i in idx]
    q=Seq(sub); c=q.counts(); fl.append([js(c[i],uc[i]) for i in range(2)])
P('noise floor of a ~%d-word sample of the unsolved itself vs unsolved: A=%.4f B=%.4f'%(q.nw,*np.mean(fl,0)))
# ---- segmentation sensitivity
P('\n## Sentence-segmentation sensitivity (JS C/D/E vs unsolved; strong = . ! ? only; medium = also ; :)')
names=['Moby Dick','Plato Republic (Jowett)','Emerson Essays I','Gospel of Buddha (Carus)','Cicero Tusculan (English tr.)','Agrippa Occult Phil I','Paine Age of Reason','Austen Emma','Bhagavad Gita (Arnold)','Tao Te Ching (Legge)']
for lev in ['strong','medium']:
    rows=[]
    for n in names:
        q=seq_from_stream(C[n][0],THEOFTO,'cic',lev); gc=q.counts(); rows.append([js(uc[i],gc[i]) for i in range(5)]+[q.slen.mean()])
    r=np.mean(rows,0); P('%s: mean over %d corpora (-THE/OF/TO): A=%.4f B=%.4f C=%.4f D=%.4f E=%.4f meansent=%.1f'%(lev,len(names),*r))
# ---- line structure
P('\n## Line structure')
U,Cf,sha=lpdata.unsolved()
ll=[];ends=[];perpage_cv=[]
for p in U:
    L=collections.Counter(p['line']); v=[x for x in L.values()]
    ll+=v
    w=p['word'];l=p['line']
    for i in range(len(w)-1):
        if l[i]!=l[i+1]: ends.append(w[i]!=w[i+1])
ll=np.array(ll)
P('unsolved: %d lines, mean %.2f runes, sd %.2f, CV %.3f, min %d max %d; internal line breaks %d, of which at a word boundary %.1f%% (mid-word %.1f%%)'%(len(ll),ll.mean(),ll.std(),ll.std()/ll.mean(),ll.min(),ll.max(),len(ends),100*np.mean(ends),100*(1-np.mean(ends))))
# interior lines only (exclude first/last of page)
inter=[]
for p in U:
    L=collections.Counter(p['line']); ks=sorted(L); inter+= [L[k] for k in ks[1:-1]]
inter=np.array(inter); P('interior lines only: n=%d mean %.2f sd %.2f CV %.3f'%(len(inter),inter.mean(),inter.std(),inter.std()/inter.mean()))
# expected mid-word fraction if breaks fall at a uniformly random rune position: words/runes
nr=sum(len(p['idx']) for p in U); nwd=uq.nw
P('expected word-boundary share for a break at uniformly random rune position = words/runes = %.1f%%'%(100*nwd/nr))
def verse_lines(path,regex=None,cic=True,start=0,end=None):
    t=open(path,encoding='utf-8',errors='ignore').read()[start:end]
    res=[]
    for l in t.split('\n'):
        if regex and not re.search(regex,l): continue
        ws=[w for w in tokenize(l) if w not in '.;']
        if len(ws)<2: continue
        res.append(sum(runelen(w,'cic') for w in ws))
    return np.array(res)
for nm,p,rg,s0 in [('Beowulf (OE)',DK+'/analysis/round10b/B6-non-english-plaintext/corpora/oe_beowulf.txt','[þðæÞÐÆ]',0),('Faust (de)',DK+'/analysis/round10b/B6-non-english-plaintext/corpora/de_faust.txt',None,5000),('Virgil Aeneid (la)',K19+'virgil_aeneid_latin.txt',None,5000),('Whitman',CORP+'/nltk/gutenberg/whitman-leaves.txt',None,3000),('Milton PL',CORP+'/nltk/gutenberg/milton-paradise.txt',None,3000),('Shakespeare Hamlet',CORP+'/nltk/gutenberg/shakespeare-hamlet.txt',None,3000),('Blake',CORP+'/nltk/gutenberg/blake-poems.txt',None,3000),('Dante (Longfellow)',K18+'dante_inferno_longfellow.txt',None,5000)]:
    v=verse_lines(p,rg,start=s0)
    P('natural-line corpus %-20s lines=%6d mean %.1f runes sd %.1f CV %.3f ; word-boundary line ends 100%% by construction'%(nm,len(v),v.mean(),v.std(),v.std()/v.mean()))
pickle.dump(out,open('extra_out.pkl','wb'))
open('extra_out.txt','w').write('\n'.join(out))
