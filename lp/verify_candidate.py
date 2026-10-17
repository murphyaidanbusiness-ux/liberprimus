"""Independent check of a candidate plaintext (rune indices or transliteration).
usage: python3 verify_candidate.py FILE   (FILE: comma/space-separated ints 0-28, or letters)
Reports IoC, quadgram score per quadgram, shuffle-null, and hit rate against Cicada vocabulary."""
import sys, math, random, re, json
sys.path.insert(0,'./lp')
import lpdata
from collections import Counter
DL=lpdata.DL
Q={}
for ln in open(DL+'/dukotah/liber-primus/data/english_quadgrams.txt'):
    k,v=ln.split(); Q[k]=float(v)
tot=sum(Q.values()); LQ={k:math.log10(v/tot) for k,v in Q.items()}; FLOOR=math.log10(0.01/tot)
def qscore(s):
    if len(s)<4: return FLOOR
    return sum(LQ.get(s[i:i+4],FLOOR) for i in range(len(s)-3))/(len(s)-3)
def ioc(x):
    c=Counter(x); n=len(x); return sum(v*(v-1) for v in c.values())/(n*(n-1))*29
sp=json.load(open(DL+'/dukotah/liber-primus/SOLVED-PAGES.json'))
vocab=set()
for pg in sp['pages']:
    t=pg['plaintext_transliteration']
    for w in ('THE','AND','YOU','ARE','NOT','THAT','WITH','THIS','FROM','WHAT','WHO','ALL','FOR','MASTER','STUDENT','PILGRIM','PRIMES','SACRED','TOTIENT','DIVINITY','INSTAR','CIRCUMFERENCE','EMERGE','WITHIN','JOURNEY','WISDOM','TRUTH','DEATH','BOOC','CNOW','BEING','REALITY'):
        vocab.add(w)
def hits(s):
    return sum(s.count(w)*len(w) for w in vocab)/max(1,len(s))
def load(path):
    t=open(path).read().strip()
    if re.fullmatch(r'[\d,\s]+',t):
        idx=[int(v) for v in re.split(r'[,\s]+',t) if v]; s=''.join(lpdata.TR[i] for i in idx)
    else:
        s=re.sub('[^A-Z]','',t.upper()); idx=None
        # back-convert to indices (greedy digraphs)
        idx=[];i=0
        while i<len(s):
            for L in (2,1):
                if s[i:i+L] in lpdata.TR: idx.append(lpdata.TR.index(s[i:i+L])); i+=L; break
            else: i+=1
    return idx,s
if __name__=='__main__':
    idx,s=load(sys.argv[1])
    print('runes',len(idx),'IoC %.3f'%ioc(idx),'quadgram %.3f'%qscore(s),'vocab-hit %.3f'%hits(s))
    random.seed(0); null=[]
    for _ in range(200):
        r=idx[:]; random.shuffle(r); null.append(qscore(''.join(lpdata.TR[i] for i in r)))
    print('shuffle null quadgram: mean %.3f max %.3f   (English solved pages: -4.1..-5.0)'%(sum(null)/len(null),max(null)))
    print('first 200:',s[:200])
