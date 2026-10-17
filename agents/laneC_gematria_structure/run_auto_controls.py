import sys, json, time
sys.path.insert(0,'.')
import numpy as np, multiprocessing as mp
import eng, ctrl, fam_auto as FA
from eng import PRIMES
PR=PRIMES
inv=[0]+[pow(a,-1,29) for a in range(1,29)]
def enc_auto(var,p,st,rng,restart):
    lab,mode,lag,tn,tab,sgn,mpp,form=var
    n=len(p); c=np.zeros(n,dtype=np.int64); c[0]=11
    D=np.zeros(n,dtype=np.int64)
    # segments over positions r=1..n-1 (D index r-1): page restarts
    seg_start=set([1])
    if restart=='page':
        for r in range(2,n):
            if st.page[r]!=st.page[r-1]: seg_start.add(r)
    sigma_ok=True
    seeds=[]
    for r in range(1,n):
        if r in seg_start:
            if mode==0:
                hist=[int(rng.integers(0,29)) for _ in range(lag)] if True else None
                seeds.append(tuple(hist))
            elif mode==1:
                curk=int(rng.integers(0,29)); wsum=0
            else:
                cum=int(rng.integers(0,29))
            if mode==0: pass
        if mode==0: k=sgn*int(tab[hist[lag-1]])
        elif mode==1:
            if st.word[r]!=st.word[r-1] and r not in seg_start:
                s=min(wsum,FA.HMAX-1); curk=sgn*int(tab[s]); wsum=0
            elif r in seg_start and mode==1 and False: pass
            k=curk
        else: k=sgn*int(tab[cum%FA.HMAX])
        pp=int(p[r])
        if pp==28: Dv=0
        elif form==0:
            x=pp if mpp==0 else 27-pp
            Dv=1+((x+k)%28)
        else:
            x=pp+1 if mpp==0 else 28-pp
            kk=k%29; kk=1 if kk==0 else kk
            Dv=(x*kk)%29
        D[r]=Dv; c[r]=(c[r-1]+Dv)%29
        if mode==0:
            hist=[pp]+hist[:-1]
        elif mode==1: wsum+=int(PR[pp])
        else: cum+=int(PR[pp])
    return c
def pick(label):
    for v in FA.variants():
        if v[0]==label: return v
    raise KeyError(label)
PLANTS=[
 ('LET lag1 g=prime%28 s=+1 map0 f0','cont'),
 ('LET lag2 g=index s=-1 map1 f0','page'),
 ('LET lag3 g=prime%29 s=+1 map0 f0','cont'),
 ('WORDSUM prev-word h=phi%28 s=+1 map0 f0','cont'),
 ('CUMSUM running-total h=sum%29 s=-1 map0 f0','page'),
 ('LET lag1 g=prime%29 s=+1 map0 f1','cont'),
]
def task(a):
    label,rm=a
    rng=np.random.default_rng(abs(hash(label))%2**32)
    words,p,st=ctrl.synth_plain(start=40000+len(label)*7)
    var=pick(label)
    c=enc_auto(var,p,st,rng,rm)
    d=eng.Data(c,st)
    res=FA.run_all(d)
    top=sorted(res.items(),key=lambda kv:-kv[1][0])[:3]
    key=f'{label} | {rm}'
    return dict(label=key,planted=res.get(key),top=top,second=sorted([v[0] for k,v in res.items() if k!=key])[-1])
if __name__=='__main__':
    with mp.Pool(2) as pool: out=pool.map(task,PLANTS)
    json.dump(out,open('ctrl_auto.json','w'),indent=1)
    for r in out: print(r['label'],'planted(meanz,maxz,bestioc)=',r['planted'],'| best other mean-z=%.1f'%r['second'],'| top:',r['top'][0][0],round(r['top'][0][1][0],1))
