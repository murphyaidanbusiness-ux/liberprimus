import sys, math
sys.path.insert(0,'.')
import numpy as np
import eng
from collections import Counter
st,c=eng.real_struct(); d=eng.Data(c,st)
D=d.D.astype(int); m=d.m
pw=d.pos_word; wl=d.wlen
first=(pw==0); last=(pw==wl-1)
def chi2_flat(vals,k=28,lo=1):
    cnt=np.bincount(vals-lo,minlength=k)[:k]; n=cnt.sum(); e=n/k
    return ((cnt-e)**2/e).sum(), n
def chi2_runes(vals):
    cnt=np.bincount(vals,minlength=29); n=cnt.sum(); e=n/29
    return ((cnt-e)**2/e).sum(), n
def report(mask,label,use='D'):
    if use=='D':
        v=D[mask]; v=v[v>0]; x,n=chi2_flat(v,28,1); df=27
    else:
        v=d.c[1:][mask]; x,n=chi2_runes(v); df=28
    z=(x-df)/math.sqrt(2*df)
    return f'{label:34s} n={n:5d} chi2={x:6.1f} df={df} z={z:+.2f}'
print('--- increments D (nonzero) by within-word position (flat expected; chi2 df=27)')
rows=[]
for nm,mask in [('word-initial (first rune of word)',first),('word-final',last),('second rune',pw==1),('third rune',pw==2),('all other',(~first)&(~last))]:
    print(report(mask,nm,'D'))
print('--- raw ciphertext runes by position (chi2 df=28)')
for nm,mask in [('word-initial',first),('word-final',last),('interior',(~first)&(~last))]:
    print(report(mask,nm,'c'))
print('--- by word length')
for L in (1,2,3,4,5,6,7,8):
    print(report(wl==L,f'D, words of length {L}','D'), '|', report((wl==L)&first,f'   first rune of len-{L} words, D','D'))
print('--- D by position-in-word x word length: pooled chi2 over cells (k=28 x cells)')
cells=0;tot=0;dfs=0
for L in range(2,9):
    for pos in range(L):
        mask=(wl==L)&(pw==pos); v=D[mask]; v=v[v>0]
        if len(v)<56: continue
        x,n=chi2_flat(v,28,1); tot+=x; dfs+=27
print('pooled chi2=%.1f df=%d z=%.2f'%(tot,dfs,(tot-dfs)/math.sqrt(2*dfs)))
# last rune of word vs first rune of next: D across boundary
bnd=first
v=D[bnd]; v=v[v>0]
print('boundary increments mean=%.2f (flat 14.5)'%v.mean())
# word-level: repeated word types vs random sim with same lengths (chain: random flat + doublet suppression)
words={}
for w in range(st.word.max()+1):
    words[w]=tuple(c[st.word==w])
from collections import Counter
cnt=Counter(words.values())
rep_real=sum(1 for k,v in cnt.items() if v>1 and len(k)>=3)
rep_by_len={L:sum(v-1 for k,v in cnt.items() if v>1 and len(k)==L) for L in range(1,7)}
rng=np.random.default_rng(0)
nul=[]
for t in range(200):
    dd=eng.shuffle_data(d,rng); cc=dd.c
    ww=Counter(tuple(cc[st.word==w]) for w in range(st.word.max()+1))
    nul.append([sum(v-1 for k,v in ww.items() if v>1 and len(k)==L) for L in range(1,7)])
nul=np.array(nul)
print('repeated word tokens (extra occurrences) by length 1..6: real',[rep_by_len[L] for L in range(1,7)])
print('  null mean',np.round(nul.mean(0),1),'sd',np.round(nul.std(0),1))
print('  z',np.round((np.array([rep_by_len[L] for L in range(1,7)])-nul.mean(0))/nul.std(0),2))
