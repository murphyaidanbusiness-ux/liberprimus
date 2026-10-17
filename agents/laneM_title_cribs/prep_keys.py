"""Reconstruct the raw sequences behind hash-table tags (same definitions as prep_tables.py) for onward decryption."""
import numpy as np, re
from common import *
import vocab
_cache={}
def _build():
    if _cache: return _cache
    cicw,cicph,titlew,g20=vocab.build_vocab()
    kwords=list(dict.fromkeys(list(cicw)+[t.replace(' ','') for t in vocab.SOLVED_TITLES]+g20))
    kwsp=[]
    for w in kwords:
        for s in vocab.spellings(w):
            if len(s)>=3 and s not in kwsp: kwsp.append(s)
    _cache['kw']=list(dict.fromkeys(kwsp))
    LEN=13600+30
    def primes_upto(n):
        s=np.ones(n+1,bool); s[:2]=False
        for i in range(2,int(n**.5)+1):
            if s[i]: s[i*i::i]=False
        return np.nonzero(s)[0]
    PR=primes_upto(400000)[:LEN+5]
    tot=np.arange(LEN+2)
    for i in range(2,LEN+2):
        if tot[i]==i: tot[i::i]-=tot[i::i]//i
    pi=[3]+[int(c) for c in open(S+'/dl/leo/pi.txt').read() if c.isdigit()]
    U_,C_,_=lpdata.unsolved(); PGr=[p['page'] for p in U_ for _ in p['idx']]
    titles_runes=[r for t in vocab.SOLVED_TITLES for r in vocab.spell(t)]
    koans=open(S+'/dl/dukotah/liber-primus/data/keys/armada18/cicada_koans_and_lp_sections.txt').read(); kr=vocab.spell(koans)
    def fibm(m,a=0,b=1):
        o=[]
        for _ in range(LEN): o.append(a); a,b=b,(a+b)%m
        return o
    _cache['num']={
     'n':lambda m:[i%m for i in range(LEN)], 'n*3301':lambda m:[(3301*i)%m for i in range(LEN)],
     'n^2':lambda m:[(i*i)%m for i in range(LEN)], 'n^3':lambda m:[(i**3)%m for i in range(LEN)],
     'tri':lambda m:[(i*(i+1)//2)%m for i in range(LEN)], 'primes':lambda m:list(PR[:LEN]%m),
     'primegaps':lambda m:list((PR[1:LEN+1]-PR[:LEN])%m), 'cumprimes':lambda m:list(np.cumsum(PR[:LEN])%m),
     'fib':lambda m:fibm(m), 'lucas':lambda m:fibm(m,2,1), 'totient':lambda m:list(tot[1:LEN+1]%m),
     'totient_of_primes':lambda m:list((PR[:LEN]-1)%m), 'pi':lambda m:[x%m for x in pi[:LEN]],
     '2^n':lambda m:[pow(2,i,m) for i in range(LEN)], '3^n':lambda m:[pow(3,i,m) for i in range(LEN)],
     'pagenum_per_rune':lambda m:[x%m for x in PGr]+[0]*(LEN-len(PGr)),
     'gematria_titles':lambda m:[PRIMES[titles_runes[i%len(titles_runes)]]%m for i in range(LEN)],
     'gematria_solvedtext':lambda m:[PRIMES[kr[i%len(kr)]]%m for i in range(LEN)],
     'solvedtext_runes':lambda m:[kr[i%len(kr)]%m for i in range(LEN)],
     'prime_index_of_n':lambda m:[(i)%m for i in PR[:LEN]]}
    C=np.array(C_); D=np.r_[0,(C[1:]-C[:-1])%29]; nz=np.nonzero(D)[0]
    st={'raw':(list(C),None),'D':(list(D),None),'raw28':(list(C%28),None)}
    for bn,bt in BIJ:
        bt=np.array(bt); st['u_'+bn]=(list(bt[D[nz]]),list(nz))
    _cache['rec']=st
    return _cache
def raw_seq(typ,src,m,start,n):
    """typ 1: src = index into keyword list, start = offset in periodic word; typ 2: src = seq name; typ 3: src = stream name, start = original corpus position."""
    B=_build()
    if typ==1:
        import pyfrag
        nm=pyfrag.SRC['kw'][src] if isinstance(src,int) else src
        w=[TR.index(x) for x in nm.split('-')]; return [w[(start+i)%len(w)]%m for i in range(n)]
    if typ==2:
        sq=B['num'][src](m); return [sq[start+i]%m if start+i<len(sq) else None for i in range(n)]
    if typ==3:
        sq,pm=B['rec'][src]
        idx=start if pm is None else pm.index(start)
        return [sq[idx+i]%m if idx+i<len(sq) else None for i in range(n)]
def align(f,w,m):
    """find (eps,s) with f_i = eps*w_i + s mod m"""
    for eps in (1,-1):
        s=(f[0]-eps*w[0])%m
        if all((eps*w[i]+s)%m==f[i] for i in range(len(f))): return eps,s
    return None
