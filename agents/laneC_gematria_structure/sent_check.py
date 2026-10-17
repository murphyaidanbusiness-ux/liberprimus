import sys; sys.path.insert(0,'.')
import numpy as np, eng, lpdata
from eng import condcoinc
U,C,h=lpdata.unsolved()
sent=eng.contiguous(np.array([s for p in U for s in p['sent']]))
st,c=eng.real_struct(); d=eng.Data(c,st)
v=sent[1:]
# split halves by sentence id
half=sent.max()//2
for nm,mask in (('first half',v<=half),('second half',v>half)):
    vv=np.where(mask,v,-1); r,p=condcoinc(d.D,vv); print(nm,'rate %.5f pairs %.0f'%(r,p))
# lag profile of D coincidence (nonzero both), lags 1..60
D=d.D.astype(int)
rates=[]
for lag in range(1,61):
    a=D[lag:];b=D[:-lag];ok=(a>0)&(b>0); rates.append((a[ok]==b[ok]).mean())
rates=np.array(rates)
rng=np.random.default_rng(1)
nul=[]
for t in range(50):
    dd=eng.shuffle_data(d,rng); D2=dd.D.astype(int); r=[]
    for lag in range(1,61):
        a=D2[lag:];b=D2[:-lag];ok=(a>0)&(b>0); r.append((a[ok]==b[ok]).mean())
    nul.append(r)
nul=np.array(nul); z=(rates-nul.mean(0))/nul.std(0)
print('lag 1..60 coincidence z-scores:',np.round(z,1))
print('mean z over lags 1..60: %.2f (sd of mean expected %.2f)'%(z.mean(),1/np.sqrt(60)))
print('mean z lags 1..10: %.2f ; 11..30: %.2f ; 31..60: %.2f'%(z[:10].mean(),z[10:30].mean(),z[30:].mean()))
