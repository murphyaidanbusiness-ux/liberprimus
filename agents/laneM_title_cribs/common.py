"""laneM shared: LM tables, canonical hashing (must match frag.c), sequences, streams, model tables."""
import sys, numpy as np, re, json
S='.'
OUT=S+'/agents/laneM_title_cribs'
sys.path.insert(0,S+'/lp'); sys.path.insert(0,OUT)
import lpdata
TR=lpdata.TR; PRIMES=lpdata.PRIMES
M64=(1<<64)-1
def fnv(m, d):
    h=0xcbf29ce484222325
    for b in [m,len(d)]+list(d):
        h^=b; h=(h*0x100000001b3)&M64
    return h
def diffs(f,m): return [(f[j+1]-f[j])%m for j in range(len(f)-1)]
def canon_hashes(f,m):
    d=diffs(f,m); return fnv(m,d), fnv(m,[(-x)%m for x in d])
# ---- LM: conditional log10 tables from lane A joint 4-gram (Cicada-transliterated English) ----
def lm_tables():
    J=np.fromfile(S+'/agents/laneA_keyword_chain/quad29.f32',dtype=np.float32).astype(np.float64).reshape(29,29,29,29)
    P4=10**J; P4/=P4.sum()
    P3=P4.sum(3); P2=P3.sum(2); P1=P2.sum(1)
    q=np.log10(P4/P3[...,None]); t=np.log10(P3/P2[...,None]); b=np.log10(P2/P1[:,None]); u=np.log10(P1)
    return q.astype(np.float32),t.astype(np.float32),b.astype(np.float32),u.astype(np.float32)
# ---- primitive roots / discrete logs mod 29 ----
PRIM_ROOTS=[2,3,8,10,11,14,15,18,19,21,26,27]
def dlog_table(g):
    t=[-1]*29; v=1
    for e in range(28): t[v]=e; v=v*g%29
    return t
DLOG={g:dlog_table(g) for g in PRIM_ROOTS}
# step bijections B: D in 1..28 -> Z28
BIJ=[('s-1',[-1]+[s-1 for s in range(1,29)]),('28-s',[-1]+[28-s for s in range(1,29)])]+[('dlog%d'%g,DLOG[g]) for g in PRIM_ROOTS]
# plaintext maps sigma: rune 0..28 -> Z28: 29 shifts ((p+s) mod 29) mod 28, plus Atbash (28-p) mod 28
SIG=[('sh%d'%s,[((p+s)%29)%28 for p in range(29)]) for s in range(29)]+[('atb',[(28-p)%28 for p in range(29)])]
