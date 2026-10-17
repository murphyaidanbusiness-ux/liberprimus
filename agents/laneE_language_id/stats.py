import sys, re, math, pickle, numpy as np
from corpora import *
sys.path.insert(0,S+'/lp'); import lpdata
NA,NB,NC,ND,NE=11,64,7,7,10
EDGE=np.array([3,6,9,12,16,21,28,40,60])   # sentence length bins: <=3,<=6,...,>60
STATS=['A_len','B_bigram','C_first','D_last','E_sentlen']
DIG=['TH','NG','EA','EO','OE','AE','IA']
_cache={}
def runelen(w,mode):
    k=(w,mode)
    r=_cache.get(k)
    if r is not None: return r
    x=w
    if mode=='cic':
        x=x.replace('K','C').replace('V','U').replace('Q','C').replace('Z','S')
        x=x.replace('IO','IA').replace('ING','NG')
        dg=DIG
    elif mode=='cic_ing':   # no ING->NG
        x=x.replace('K','C').replace('V','U').replace('Q','C').replace('Z','S').replace('IO','IA'); dg=DIG
    elif mode=='th': dg=['TH']
    elif mode=='letters': dg=[]
    else: raise ValueError(mode)
    i=0;n=0
    while i<len(x):
        if x[i:i+2] in dg: i+=2
        else: i+=1
        n+=1
    _cache[k]=n; return n
class Seq:
    """sentence-structured word-length sequence"""
    def __init__(self,sent_lens):
        sl=[s for s in sent_lens if len(s)>0]
        self.slen=np.array([len(s) for s in sl])
        self.L=np.array([x for s in sl for x in s])
        self.starts=np.concatenate([[0],np.cumsum(self.slen)])   # len ns+1
        self.nw=len(self.L); self.ns=len(sl)
        Lc=np.minimum(self.L,NA)
        self.Ai=Lc-1
        cells=np.full(self.nw,-1)
        if self.nw>1:
            c=(np.minimum(self.L[:-1],8)-1)*8+np.minimum(self.L[1:],8)-1
            cells[:-1]=c
        # invalidate last word of each sentence
        ends=self.starts[1:]-1
        cells[ends]=-1
        self.cells=cells
        self.first=np.minimum(self.L[self.starts[:-1]],7)-1
        self.last=np.minimum(self.L[ends],7)-1
        self.sbin=np.searchsorted(EDGE,self.slen,side='left')   # 0..9
    def counts(self,w0=0,w1=None,s0=0,s1=None):
        w1=self.nw if w1 is None else w1; s1=self.ns if s1 is None else s1
        A=np.bincount(self.Ai[w0:w1],minlength=NA)
        c=self.cells[w0:w1]; B=np.bincount(c[c>=0],minlength=NB)
        Cc=np.bincount(self.first[s0:s1],minlength=NC); D=np.bincount(self.last[s0:s1],minlength=ND)
        E=np.bincount(self.sbin[s0:s1],minlength=NE)
        return [A,B,Cc,D,E]
def seq_from_stream(stream,remove=frozenset(),mode='cic',level='strong',transform=None):
    st=[t for t in stream if (t in '.;') or t not in remove]
    sents=sentences(st,level)
    return Seq([[runelen(w,mode) for w in s] for s in sents])
def js(p,q):
    p=np.asarray(p,float);q=np.asarray(q,float)
    p=p/p.sum();q=q/q.sum();m=(p+q)/2
    def kl(a,b):
        k=a>0; return float((a[k]*np.log(a[k]/b[k])).sum())
    return (kl(p,m)+kl(q,m))/2
def unsolved_seq():
    U,Cc,sha=lpdata.unsolved(); assert sha.startswith('0233120')
    order=[];seen={}
    sent_of={}
    for p in U:
        for w,s in zip(p['word'],p['sent']):
            if w not in sent_of: order.append(w); sent_of[w]=s
    from collections import Counter, OrderedDict
    wl=Counter(w for p in U for w in p['word'])
    sents=OrderedDict()
    for w in order: sents.setdefault(sent_of[w],[]).append(wl[w])
    return list(sents.values())
if __name__=='__main__':
    ss=unsolved_seq(); q=Seq(ss)
    print('words',q.nw,'sents',q.ns,'mean len',q.L.mean(),'mean sent len',q.slen.mean())
    print(sorted(q.slen)[:20], sorted(q.slen)[-10:])
    for n,c in zip(STATS,q.counts()): print(n,c.tolist())
