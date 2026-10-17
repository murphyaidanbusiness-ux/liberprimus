import pickle, math, numpy as np, re, collections
from stats import *
from variants import *
C=pickle.load(open(HERE+'/streams.pkl','rb'))
q={};tot=0
for l in open(DK+'/data/english_quadgrams.txt'):
    a,b=l.split(); q[a]=int(b); tot+=int(b)
floor=math.log10(0.01/tot)
lq={k:math.log10(v/tot) for k,v in q.items()}
def letters(words):
    s=''.join(words)
    s=s.replace('K','C').replace('V','U').replace('Q','C').replace('Z','S').replace('IO','IA').replace('ING','NG')
    return s
def quad(s):
    n=len(s)-3
    return sum(lq.get(s[i:i+4],floor) for i in range(n))/n
def symbols(words,mode='cic'):
    out=[]
    for w in words:
        x=w
        if mode=='cic': x=x.replace('K','C').replace('V','U').replace('Q','C').replace('Z','S').replace('IO','IA').replace('ING','NG'); dg=DIG
        elif mode=='letters': dg=[]
        elif mode=='th': dg=['TH']
        i=0
        while i<len(x):
            if x[i:i+2] in dg: out.append(x[i:i+2]); i+=2
            else: out.append(x[i]); i+=1
    return out
def ioc(sym,norm=True):
    c=collections.Counter(sym); n=len(sym)
    v=sum(k*(k-1) for k in c.values())/(n*(n-1))
    return v*29
rng=np.random.default_rng(5)
def evaluate(name,stream,remove=frozenset(),mode='cic',arch=False,nwin=30):
    st=archaic(stream) if arch else stream
    words=[t for t in st if t not in '.;' and t not in remove]
    # quad on windows of ~2900 words (~13k runes)
    qs=[];ios=[]
    for _ in range(nwin):
        s0=int(rng.integers(0,max(1,len(words)-2900)))
        w=words[s0:s0+2900]
        qs.append(quad(letters(w))); ios.append(ioc(symbols(w,mode)))
    return np.mean(qs),np.std(qs),np.mean(ios),np.std(ios)
rows=[]
for name in ['Moby Dick','Plato Republic (Jowett)','Emerson Essays I','Gospel of Buddha (Carus)','Cicero Tusculan (English tr.)','Agrippa Occult Phil I','KJV Bible (whole)','Tao Te Ching (Legge)']:
    for lab,rem,mode,arch in VARIANTS:
        if lab in ('base (Cicada rules)','-THE','-THE/OF/TO','-THE/OF/TO/AND','-THE/A/AN','-all function words','letters (no digraphs)','TH-only merged','archaic (thou/thee/-eth)'):
            r=evaluate(name,C[name][0],rem,mode,arch); rows.append((name,lab)+r)
for name in ['Latin: Newton Principia','Latin: Caesar BG','German: Faust','Dutch: bible-corpus','Danish: bible-corpus','Swedish: bible-corpus','Welsh: CCG treebank','Old English: Beowulf','Old Norse: sagas (Perseus/CLTK)','Gothic: Wulfila Bible (PROIEL)','Esperanto: bible-corpus','Italian: bible-corpus','Finnish: bible-corpus','French: bible-corpus','Spanish: bible-corpus']:
    r=evaluate(name,C[name][0]); rows.append((name,'natural')+r)
pickle.dump(rows,open('scorers.pkl','wb'))
print('%-34s %-28s %8s %6s | %7s %6s'%('corpus','variant','quad/4g','sd','IoC','sd'))
for r in rows: print('%-34s %-28s %8.3f %6.3f | %7.3f %6.3f'%r)
