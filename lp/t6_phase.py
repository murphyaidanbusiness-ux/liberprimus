import lpdata, numpy as np
from collections import Counter
U,C,h=lpdata.unsolved(); C=np.array(C); N=len(C)
word=np.array([w for p in U for w in p['word']]); line=np.array([l for p in U for l in p['line']]); sent=np.array([s for p in U for s in p['sent']])
page=np.array([p['page'] for p in U for _ in p['idx']])
starts={}; 
for i,w in enumerate(word): starts.setdefault(w,i)
cnt=Counter(word); pos=np.array([i-starts[w] for i,w in enumerate(word)]); wlen=np.array([cnt[w] for w in word])
wids=sorted(starts); widx_of={w:k for k,w in enumerate(wids)}; widx=np.array([widx_of[w] for w in word])
prev_last=np.zeros(N,int); prev_first=np.zeros(N,int); prev_len=np.zeros(N,int)
for k,w in enumerate(wids):
    if k==0: continue
    pw=wids[k-1]; s=starts[pw]; e=s+cnt[pw]-1
    sel=word==w; prev_last[sel]=C[e]; prev_first[sel]=C[s]; prev_len[sel]=cnt[pw]
first_rune=np.array([C[starts[w]] for w in word])
# word index within line / sentence / page
def idx_within(unit):
    out=np.zeros(N,int); seen={}
    for i in range(N):
        key=(unit[i]); 
        if i==0 or word[i]!=word[i-1]:
            seen[key]=seen.get(key,-1)+1 if (i>0 and unit[i]==unit[i-1]) else 0
        out[i]=seen.get(key,0)
    return out
w_in_line=idx_within(line); w_in_sent=idx_within(sent); w_in_page=idx_within(page)
pos_in_page=np.zeros(N,int)
for pg in np.unique(page): sel=page==pg; pos_in_page[sel]=np.arange(sel.sum())
def coset_ioc(X,key,m=29):
    tot=cnt_=0
    for g in np.unique(key):
        col=X[key==g]; n=len(col)
        if n>5: c=np.bincount(col,minlength=m); tot+=(c*(c-1)).sum()/(n*(n-1))*m; cnt_+=1
    return tot/cnt_
rng=np.random.default_rng(0)
P=5
hyps={
 'len%5':wlen%5,'len':np.minimum(wlen,12),'widx%5':widx%5,'widx%29':widx%29,'w_in_line':np.minimum(w_in_line,8),'w_in_sent%5':w_in_sent%5,'w_in_page%5':w_in_page%5,
 'line%5':line%5,'page%5':page%5,'prev_last':prev_last,'prev_first':prev_first,'prev_len%5':prev_len%5,'first_rune':first_rune,'pos_in_page%5':pos_in_page%5,
 'pos_in_page%29':pos_in_page%29,'sent%5':sent%5,'startpos%5':np.array([starts[w] for w in word])%5,'startpos%29':np.array([starts[w] for w in word])%29,
}
print("coset IoC with cosets keyed by (position-in-word mod 5, phase hypothesis g(word)); null = 50 global shuffles; random ~1.0, true phase model ~1.4-1.7")
for name,g in hyps.items():
    key=pos%P + P*g
    real=coset_ioc(C,key)
    nl=[coset_ioc(rng.permutation(C),key) for _ in range(50)]
    print("  %-16s real %.4f  null %.4f±%.4f  z=%+.2f"%(name,real,np.mean(nl),np.std(nl),(real-np.mean(nl))/np.std(nl)))
# also: alphabet keyed by position in word without modulus (alphabet = f(pos)), and by (pos, first_rune) for first few positions only
