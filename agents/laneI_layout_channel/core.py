import sys, os, re, collections, pickle
import numpy as np
S='.'
HERE=S+'/agents/laneI_layout_channel'
sys.path.insert(0,S+'/lp'); import lpdata
TR=lpdata.TR
DK=S+'/dl/dukotah/liber-primus/data'

# ---------------- English resources ----------------
def _build_res():
    f=HERE+'/res.pkl'
    if os.path.exists(f): return pickle.load(open(f,'rb'))
    # quadgram log10 probs
    cnt=np.zeros(26**4)
    for ln in open(DK+'/english_quadgrams.txt'):
        q,c=ln.split(); 
        if len(q)!=4: continue
        i=0
        for ch in q: i=i*26+ord(ch)-65
        cnt[i]=int(c)
    tot=cnt.sum()
    LQ=np.log10(np.maximum(cnt,0.01)/tot).astype(np.float32)
    # dictionary from several corpora (frequency>=4, len>=5)
    import zipfile
    texts=[]
    z=zipfile.ZipFile(S+'/agents/laneE_language_id/corp/nltk_gut.zip')
    for n in ('gutenberg/austen-emma.txt','gutenberg/bible-kjv.txt','gutenberg/melville-moby_dick.txt','gutenberg/milton-paradise.txt','gutenberg/carroll-alice.txt','gutenberg/chesterton-ball.txt'):
        texts.append(z.read(n).decode('latin-1'))
    for n in ('walden','meditations','nature','emerson_conduct','imitation','mhh','bgae','frankenstein'):
        try: texts.append(open(S+'/agents/laneF_wordlength_alignment/fetched/%s.txt'%n,encoding='utf-8',errors='ignore').read())
        except Exception as e: pass
    texts.append(open(DK+'/keys/self_reliance.txt',encoding='utf-8',errors='ignore').read())
    wc=collections.Counter()
    for t in texts:
        wc.update(re.findall(r'[A-Z]+',t.upper()))
    D5=set(); D7=set()
    for w,c in wc.items():
        if c>=4 and len(w)>=5:
            if len(w)>=5: D5.add(w[:5]) if False else None
    words=[w for w,c in wc.items() if c>=4 and len(w)>=5]
    pickle.dump((LQ,words),open(f,'wb'))
    return LQ,words
LQ,WORDS=_build_res()
M7=33554467
T5=np.zeros(26**5,dtype=np.uint8); T7=np.zeros(M7,dtype=np.uint8)
def _code(w):
    c=0
    for ch in w: c=c*26+ord(ch)-65
    return c
for w in WORDS:
    if len(w)==5: T5[_code(w)]=1
    if len(w)>=7:
        # all 7-grams inside words (hashed)
        for i in range(len(w)-6): T7[_code(w[i:i+7])%M7]=1
NW5=int(T5.sum())

# ---------------- stats ----------------
W=60
def letter_stats(t, win=W):
    """t: int array 0..25. returns dict Qall,Qwin,IoC,Hall,Hwin"""
    n=len(t)
    if n<8: return dict(Qall=-9.0,Qwin=-9.0,IoC=1.0,Hall=0.0,Hwin=0.0,n=n)
    t=t.astype(np.int64)
    q=t[:-3]*17576+t[1:-2]*676+t[2:-1]*26+t[3:]
    sc=LQ[q]
    Qall=float(sc.mean())
    nq=len(sc); w=min(win-3,nq)
    cs=np.concatenate(([0.0],np.cumsum(sc,dtype=np.float64)))
    Qwin=float(((cs[w:]-cs[:-w])/w).max())
    cnt=np.bincount(t,minlength=26)
    ioc=26*float((cnt*(cnt-1)).sum())/(n*(n-1))
    # hits: 5-gram table + hashed 7-gram
    h=np.zeros(n,dtype=np.float32)
    if n>=5:
        c5=q[:-1]*26+t[4:]
        h[:len(c5)]+=T5[c5]
        if n>=7:
            c7=(c5[:-2]*26+t[5:-1])*26+t[6:]
            h[:len(c7)]+=T7[c7%M7]
    Hall=float(h.mean())
    ww=min(win,n)
    ch=np.concatenate(([0.0],np.cumsum(h,dtype=np.float64)))
    Hwin=float(((ch[ww:]-ch[:-ww])/ww).max())
    return dict(Qall=Qall,Qwin=Qwin,IoC=ioc,Hall=Hall,Hwin=Hwin,n=n)

def to_text(t): return ''.join(chr(65+int(x)) for x in t)

# ---------------- LP2 layout channels ----------------
def layout():
    U,C,sha=lpdata.unsolved()
    assert sha=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
    C=np.array(C)
    word=np.array([x for p in U for x in p['word']])
    line=np.array([x for p in U for x in p['line']])
    sent=np.array([x for p in U for x in p['sent']])
    chap=np.array([x for p in U for x in p['chap']])
    page=np.array([p['page'] for p in U for _ in p['idx']])
    return dict(C=C,word=word,line=line,sent=sent,chap=chap,page=page)

def runs(ids):
    """start indices and lengths of runs of constant id"""
    ch=np.flatnonzero(np.diff(ids))+1
    st=np.concatenate(([0],ch)); en=np.concatenate((ch,[len(ids)]))
    return st,en-st
