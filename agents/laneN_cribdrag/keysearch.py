import numpy as np, json, sys
sys.path.insert(0,'.')
from common import *
K=12
class CorpusIndex:
    def __init__(self):
        buf=np.frombuffer(open(LANE+'/corpus.bin','rb').read(),dtype=np.uint8).astype(np.int64)-65
        self.index=json.load(open(LANE+'/corpus_index.json'))
        n=len(buf); self.n=n
        valid=buf>=0
        code=np.zeros(n-K+1,dtype=np.int64); ok=np.ones(n-K+1,dtype=bool)
        for j in range(K):
            code=code*29+np.where(valid[j:n-K+1+j],buf[j:n-K+1+j],0)
            ok&=valid[j:n-K+1+j]
        pos=np.nonzero(ok)[0]; code=code[pos]
        o=np.argsort(code,kind='stable'); self.code=code[o]; self.pos=pos[o]
        del buf,valid
    def lookup(self,codes):
        i=np.searchsorted(self.code,codes); i=np.minimum(i,len(self.code)-1)
        hit=self.code[i]==codes
        return hit,self.pos[i]
    def where(self,p):
        for f,start,ln in self.index:
            if start<=p<start+ln+1: return f.split('/')[-1],p-start
        return '?',p
def variants(k,m):
    k=np.array(k)
    out=[]
    for o in (0,1):
        for s in range(m):
            a=np.where(k<0,-1,((m-k)%m if o else k)); a=np.where(k<0,-1,(a+s)%m)
            out.append((o,s,a))
    return out
def search_fragment(ci,k,m):
    res=[]
    for o,s,a in variants(k,m):
        L=len(a)
        if L<K: continue
        codes=[];offs=[]
        for j in range(L-K+1):
            w=a[j:j+K]
            if (w<0).any(): continue
            c=0
            for x in w: c=c*29+int(x)
            codes.append(c);offs.append(j)
        if not codes: continue
        hit,pos=ci.lookup(np.array(codes,dtype=np.int64))
        for h,p,j in zip(hit,pos,offs):
            if h: res.append((o,s,j,)+ci.where(int(p)))
    return res
