"""Build: lm.bin (int16 cond log10*1000 tables), htab.bin (sorted uint64 hash + uint32 tag), sources.json.
Tag = type<<30 | src<<14 | off.   type 1 = keyword window, 2 = numeric sequence window, 3 = recurrence (cipher-derived stream) window."""
import numpy as np, json, re
from common import *
import vocab
LMAXH=24
q,t,b,u=lm_tables()
with open(OUT+'/lm.bin','wb') as f:
    for a in (q,t,b,u): np.round(np.maximum(a,-30)*1000).astype(np.int16).tofile(f)
print('lm written; English-check')
FNV0=np.uint64(0xcbf29ce484222325); FP=np.uint64(0x100000001b3)
def vfnv(m, D):
    """D: (N, L-1) diffs -> hashes; prefix bytes m, len."""
    N,l=D.shape; h=np.full(N,FNV0,dtype=np.uint64)
    with np.errstate(over='ignore'):
        for v in [np.full(N,m,np.uint64),np.full(N,l,np.uint64)]+[D[:,j].astype(np.uint64) for j in range(l)]:
            h^=v; h*=FP
    return h
H=[];T=[]
sources={'kw':[],'num':[],'rec':[]}
def add_windows(typ, srcid, seq, m, offs, posmap=None):
    """seq: 1-D int array (values reduced mod m inside); windows starting at offs, lengths 4..LMAXH"""
    seq=np.asarray(seq,dtype=np.int64)%m
    offs=np.asarray(offs)
    for L in range(4,LMAXH+1):
        ok=offs[offs+L<=len(seq)]
        if len(ok)==0: continue
        W=seq[ok[:,None]+np.arange(L)[None,:]]
        D=(W[:,1:]-W[:,:-1])%m
        H.append(vfnv(m,D)); 
        o=(posmap[ok] if posmap is not None else ok)
        T.append((np.uint32(typ)<<30)|(np.uint32(srcid)<<14)|np.minimum(o,16383).astype(np.uint32))
# ---- (b) keyword windows: periodic extension of every spelling of 20k English + Cicada words (>=3 runes) ----
cicw,cicph,titlew,g20=vocab.build_vocab()
kwords=list(dict.fromkeys(list(cicw)+[t.replace(' ','') for t in vocab.SOLVED_TITLES]+g20))
kwsp=[]
for w in kwords:
    for s in vocab.spellings(w):
        if len(s)>=3 and s not in kwsp: kwsp.append(s)
kwsp=list(dict.fromkeys(kwsp))
print('keyword spellings',len(kwsp))
assert len(kwsp)<2**16
for i,s in enumerate(kwsp):
    sources['kw'].append(vocab.tr(s))
    n=len(s); ext=np.array((list(s)*(LMAXH//n+3))[:n+LMAXH])
    for m in (28,29): add_windows(1,i,ext,m,np.arange(n))
# ---- (c) numeric sequences ----
NOFF=13600; LEN=NOFF+LMAXH+2
def primes_upto(n):
    s=np.ones(n+1,bool); s[:2]=False
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=False
    return np.nonzero(s)[0]
PR=primes_upto(400000)[:LEN+5]
def modseq(gen_mod):  # returns dict m->array
    return {m:np.array(gen_mod(m),dtype=np.int64) for m in (28,29)}
def fibmod(m,a=0,b=1):
    out=[]
    for _ in range(LEN): out.append(a); a,b=b,(a+b)%m
    return out
def powmod(g,m): return [pow(g,i,m) for i in range(LEN)]
tot=np.arange(LEN+2); 
for i in range(2,LEN+2):
    if tot[i]==i: tot[i::i]-=tot[i::i]//i
pi=[3]+[int(c) for c in open(S+'/dl/leo/pi.txt').read() if c.isdigit()]
U_,C_,_=lpdata.unsolved(); PGr=[p['page'] for p in U_ for _ in p['idx']]
titles_runes=[r for t in vocab.SOLVED_TITLES for r in vocab.spell(t)]
# Gematria running streams: prime values of solved-page plaintext runes (koans file) and of the solved titles (periodic)
koans=open(S+'/dl/dukotah/liber-primus/data/keys/armada18/cicada_koans_and_lp_sections.txt').read()
kr=vocab.spell(koans)
NUMSEQ={
 'n':lambda m:[i%m for i in range(LEN)],
 'n*3301':lambda m:[(3301*i)%m for i in range(LEN)],
 'n^2':lambda m:[(i*i)%m for i in range(LEN)],
 'n^3':lambda m:[(i**3)%m for i in range(LEN)],
 'tri':lambda m:[(i*(i+1)//2)%m for i in range(LEN)],
 'primes':lambda m:list(PR[:LEN]%m),
 'primegaps':lambda m:list((PR[1:LEN+1]-PR[:LEN])%m),
 'cumprimes':lambda m:list(np.cumsum(PR[:LEN])%m),
 'fib':lambda m:fibmod(m),
 'lucas':lambda m:fibmod(m,2,1),
 'totient':lambda m:list(tot[1:LEN+1]%m),
 'totient_of_primes':lambda m:list((PR[:LEN]-1)%m),
 'pi':lambda m:[x%m for x in pi[:LEN]],
 '2^n':lambda m:powmod(2,m),'3^n':lambda m:powmod(3,m),
 'pagenum_per_rune':lambda m:[x%m for x in PGr]+[0]*(LEN-len(PGr)),
 'gematria_titles':lambda m:[PRIMES[titles_runes[i%len(titles_runes)]]%m for i in range(LEN)],
 'gematria_solvedtext':lambda m:[PRIMES[kr[i%len(kr)]]%m for i in range(LEN)],
 'solvedtext_runes':lambda m:[kr[i%len(kr)]%m for i in range(LEN)],
 'prime_index_of_n':lambda m:[(i)%m for i in PR[:LEN]],
}
for i,(name,fn) in enumerate(NUMSEQ.items()):
    sources['num'].append(name)
    for m in (28,29):
        sq=np.array(fn(m))
        add_windows(2,i,sq,m,np.arange(min(NOFF,len(sq)-4)))
# ---- (e) recurrence streams: raw cipher, increments, step-embedded increments (doublets removed) ----
C=np.array(C_); D=np.r_[0,(C[1:]-C[:-1])%29]
nz=np.nonzero(D)[0]
streams=[('raw',C,29,None),('D',D,29,None),('raw28',C,28,None)]
for bn,bt in BIJ:
    bt=np.array(bt); streams.append(('u_'+bn,bt[D[nz]],28,nz))
for i,(nm,sq,m,pm) in enumerate(streams):
    sources['rec'].append(nm)
    add_windows(3,i,sq,m,np.arange(len(sq)-4),posmap=pm)
H=np.concatenate(H); T=np.concatenate(T)
o=np.argsort(H,kind='stable'); H=H[o]; T=T[o]
print('table entries',len(H),'by type',np.bincount((T>>30).astype(np.int64)))
with open(OUT+'/htab.bin','wb') as f:
    np.array([len(H)],np.int64).tofile(f); H.tofile(f); T.tofile(f)
json.dump(sources,open(OUT+'/sources.json','w'))
