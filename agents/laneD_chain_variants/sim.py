"""Cipher constructions (encoders) used as positive controls. All operate on rune-index arrays (0..28)."""
import numpy as np
from common import *
EA=28
def sym_of(p, rng):
    """flat keyed nonzero increment s in 1..28 (0 only for EA)"""
    k=rng.integers(0,28,size=len(p))
    s=1+((p+k)%28)
    s=np.where(p==EA,0,s)
    return s
def chain(p, rng, L=1):
    """c_i = c_{i-L} + s_i, s nonzero except EA"""
    s=sym_of(p,rng); n=len(p); c=np.zeros(n,dtype=np.int64)
    c[:L]=rng.integers(0,29,size=L)
    for i in range(L,n): c[i]=(c[i-L]+s[i])%29
    return c
def lagL_with_rule(p, rng, L=2, leak=0.19, mode='bump', s_includes_zero=True):
    """c_i=c_{i-L}+s_i with s flat on 0..28 (Vigenere on lag-L diffs); then repeat-avoidance rule vs c_{i-1}:
    on collision, with prob 1-leak rewrite (bump: c_{i-1}+1 ; redraw: uniform among others)."""
    n=len(p); c=np.zeros(n,dtype=np.int64); c[:L]=rng.integers(0,29,size=L)
    k=rng.integers(0,29,size=n)
    for i in range(L,n):
        v=(c[i-L]+(p[i]+k[i]))%29
        if i>=1 and v==c[i-1] and rng.random()>=leak:
            v=(c[i-1]+1)%29 if mode=='bump' else (c[i-1]+int(rng.integers(1,29)))%29
        c[i]=v
    return c
def iid_rule(n, rng, leak=0.19, mode='bump'):
    """base-29 digit stream of random bytes with a repeat-avoidance encoder"""
    d=rng.integers(0,29,size=n); c=np.zeros(n,dtype=np.int64); c[0]=d[0]
    for i in range(1,n):
        v=d[i]
        if v==c[i-1] and rng.random()>=leak:
            v=(v+1)%29 if mode=='bump' else (c[i-1]+int(rng.integers(1,29)))%29
        c[i]=v
    return c
def synth_pages(fn, rng, lens=None):
    """apply encoder fn(p,rng)->c per page with real page lengths, plaintext tiled from solved pages"""
    lens=lens or [len(p) for p in PAGES]
    return [fn(synth_plain(n,rng),rng) for n in lens]
