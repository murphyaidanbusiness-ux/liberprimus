"""Test (f): extend flagged cribs by the next word(s) (dictionary words of the right rune length) and check whether the
fragment keeps its structure. Reference for English-ness at any length: random uniform fragments (same m, n)."""
import numpy as np, json, collections, math, random
from common import *
import pyfrag, vocab
from pyfrag import fragment, engscore, lookup, eng_batch
_V=None
def dictionary():
    global _V
    if _V is None:
        cicw,cicph,titlew,g20=vocab.build_vocab()
        d=collections.defaultdict(set)
        for w in set(g20)|set(cicw)|{'A','I','O'}:
            for s in vocab.spellings(w): d[len(s)].add(s)
        _V={k:sorted(v) for k,v in d.items()}
    return _V
_ref={}
def ref(m,n):
    if (m,n) not in _ref:
        rng=np.random.default_rng(m*100+n)
        sc=eng_batch(rng.integers(0,m,size=(4000,n)),m); _ref[(m,n)]=(sc.mean(),sc.std(),np.sort(sc))
    return _ref[(m,n)]
def zeng(f,m):
    s=engscore(f,m)/1000.; mu,sd,_=ref(m,len(f)); return (s-mu)/sd, s
def extend(item, c, prev, pos, lens, rounds=2, beam=5):
    """item: dict(crib=tuple, nw=int, model=int, test='a'|'b'|'c'|'e'). Returns per-round best statistic."""
    D=dictionary(); cur=[(tuple(item['crib']),item['nw'])]; traj=[]
    for r in range(rounds):
        cand=[]
        for crib,nw in cur:
            if nw>=len(lens): continue
            for w in D.get(lens[nw],[]):
                cr=crib+w
                if len(cr)+2>len(c): continue
                fr=fragment(item['model'],list(cr),c,prev)
                if fr is None: continue
                f,m=fr
                if item['test']=='a':
                    z,s=zeng(f,m); cand.append((z,cr,nw+1,len(f)))
                else:
                    h=[x for x in lookup(f,m,pos) if x[0]=={'b':1,'c':2,'e':3}[item['test']]]
                    if h: cand.append((len(f),cr,nw+1,len(f)))
        if not cand: traj.append(None); break
        cand.sort(key=lambda x:-x[0]); cur=[(x[1],x[2]) for x in cand[:beam]]
        traj.append((round(float(cand[0][0]),3),cand[0][3],len(cand)))
    return traj
