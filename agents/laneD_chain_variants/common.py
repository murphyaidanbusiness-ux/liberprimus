import sys, json, random
S='.'
sys.path.insert(0, S+'/lp')
import numpy as np, lpdata
U, C, sha = lpdata.unsolved()
assert sha=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
TR=lpdata.TR; PRIMES=lpdata.PRIMES
T2I={t:i for i,t in enumerate(TR)}
PAGES=[np.array(p['idx'],dtype=np.int64) for p in U]
CALL=np.array(C,dtype=np.int64)
def parse(s):
    out=[];i=0
    while i<len(s):
        if s[i:i+2] in T2I and len(s[i:i+2])==2: out.append(T2I[s[i:i+2]]); i+=2
        else: out.append(T2I[s[i]]); i+=1
    return out
_d=json.load(open(S+'/dl/dukotah/liber-primus/SOLVED-PAGES.json'))
SOLVED=[parse(p['plaintext_transliteration']) for p in _d['pages']]
PT=np.array([x for s in SOLVED for x in s],dtype=np.int64)   # concatenated solved plaintext (rune idx)
PTFREQ=np.bincount(PT,minlength=29)/len(PT)
def synth_plain(n, rng):
    """plaintext of length n by tiling solved plaintext starting at random offset"""
    o=int(rng.integers(len(PT))); reps=n//len(PT)+2
    return np.tile(PT,reps)[o:o+n].copy()
def doublets(x): 
    x=np.asarray(x); return int((x[1:]==x[:-1]).sum())
def page_doublets(pages): return sum(doublets(p) for p in pages), sum(len(p)-1 for p in pages)
def shuffled_pages(pages, rng): return [rng.permutation(p) for p in pages]
def ioc(x):
    n=len(x); c=np.bincount(x,minlength=29); return 29*(c*(c-1)).sum()/(n*(n-1))

# order-1 (rune bigram) Markov plaintext generator trained on the solved pages: no verbatim repeats from tiling
_B=np.full((29,29),0.05)
for _s in SOLVED:
    for _a,_b in zip(_s[:-1],_s[1:]): _B[_a,_b]+=1
_B=_B/_B.sum(1,keepdims=True); _CB=np.cumsum(_B,1)
def markov_plain(n, rng):
    x=np.zeros(n,dtype=np.int64); x[0]=rng.choice(29,p=PTFREQ)
    u=rng.random(n)
    for i in range(1,n): x[i]=min(int(np.searchsorted(_CB[x[i-1]],u[i])),28)
    return x
PLAIN_MODE={'f':synth_plain}
def synth_pages_m(fn, rng, lens=None):
    lens=lens or [len(p) for p in PAGES]
    return [fn(markov_plain(n,rng),rng) for n in lens]
