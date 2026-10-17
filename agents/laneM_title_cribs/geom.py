"""Opening geometry: 17 section openings + 55 page openings (absolute rune positions, word lengths)."""
import sys
S='.'
sys.path.insert(0,S+'/lp'); import lpdata
U,C,h=lpdata.unsolved(); assert h=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
W=[w for p in U for w in p['word']]; CH=[x for p in U for x in p['chap']]; PG=[p['page'] for p in U for _ in p['idx']]
# word starts
starts=[i for i in range(len(C)) if i==0 or W[i]!=W[i-1]]
wlen={}
for k,s in enumerate(starts):
    e=starts[k+1] if k+1<len(starts) else len(C); wlen[s]=e-s
wstart_idx={s:k for k,s in enumerate(starts)}
def lens_from(pos,n=8):
    k=wstart_idx[pos]; return [wlen[starts[j]] for j in range(k,min(k+n,len(starts)))]
openings=[]
for ch in range(17):
    pos=CH.index(ch); assert pos in wstart_idx
    openings.append(dict(kind='sec',id=ch,page=PG[pos],pos=pos,lens=lens_from(pos)))
for pg in range(55):
    pos=PG.index(pg)
    midword = pos not in wstart_idx
    if midword:  # page starts mid-word: opening = next word start
        pos=min(s for s in starts if s>pos)
    openings.append(dict(kind='page',id=pg,page=pg,pos=pos,lens=lens_from(pos),midword=midword))
if __name__=='__main__':
    for o in openings: print(o)
    print(len(starts),'words')
