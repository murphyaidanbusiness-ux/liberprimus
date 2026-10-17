import sys; sys.path.insert(0,'.')
import numpy as np, eng, ctrl, lpdata
from eng import condcoinc
U,C,h=lpdata.unsolved()
sent=np.array([s for p in U for s in p['sent']]); chap=np.array([s for p in U for s in p['chap']])
st,c=eng.real_struct(); d=eng.Data(c,st)
def contig(a): return eng.contiguous(a)
units={'word':st.word,'line':st.line,'sentence':contig(sent),'chapter':contig(chap),'page':st.page}
def rate(d,ids):
    v=ids[1:]
    return condcoinc(d.D,v)
rng=np.random.default_rng(2)
print('REAL data: pooled within-unit coincidence of nonzero increments (flat = 1/28 = 0.03571)')
nul={k:[] for k in units}
for t in range(100):
    dd=eng.shuffle_data(d,rng)
    for k,v in units.items(): nul[k].append(rate(dd,v)[0])
for k,v in units.items():
    r,pairs=rate(d,v); mu=np.mean(nul[k]); sd=np.std(nul[k])
    print('  %-9s units=%5d pairs=%10.0f rate=%.5f  null %.5f+-%.5f  z=%+.2f'%(k,len(np.unique(v)),pairs,r,mu,sd,(r-mu)/sd))
# adjacent-pair (lag1,2,3) coincidences within word for sanity
for lag in (1,2,3):
    ok=(st.word[1+lag:]==st.word[1:-lag])&(d.D[lag:]!=0)&(d.D[:-lag]!=0)
    a=d.D[lag:][ok]; b=d.D[:-lag][ok]
    print('  within-word lag-%d D coincidence: %.4f (n=%d; flat 0.0357, SE %.4f)'%(lag,(a==b).mean(),ok.sum(),np.sqrt(0.0357/ok.sum())))
print('\nPOSITIVE CONTROL: Moby-Dick plaintext, chain cipher, key constant within the unit (uniform random per unit), same structure as real')
words,p,st2=ctrl.synth_plain(start=30000)
# synthetic struct has word/line/page; sentence/chapter via blocks of 12 words / 600 runes
sent2=np.cumsum(np.r_[0,(np.diff(st2.word)!=0)])//12
chap2=np.arange(len(st2.word))//1800
units2={'word':st2.word,'line':st2.line,'sentence':contig(sent2),'chapter':contig(chap2),'page':st2.page}
sigma=eng.rand_sigma(rng,False)
for k,v in units2.items():
    keys=rng.integers(0,28,size=v.max()+2)
    kk=keys[v]
    D=np.where(p==28,0,1+((sigma[p]+kk)%28))
    cc=np.zeros(len(p),dtype=np.int64); cc[1:]=(11+np.cumsum(D[1:]))%29
    d2=eng.Data(cc,st2)
    r,pairs=condcoinc(d2.D,v[1:])
    print('  key constant per %-9s -> within-unit rate %.4f (pairs %.0f)'%(k,r,pairs))
