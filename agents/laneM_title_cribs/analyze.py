"""Aggregate frag.c outputs: tests (a),(b),(c),(e) real vs nulls."""
import numpy as np, glob, json, collections, sys, math
from common import *
NF=6; LM=48; NB=400
FAM=['chainAdd','gfRaw','gfDlog','vig','vigSkip','Fint']
def load(name, files=None):
    files=files or sorted(glob.glob(OUT+'/runs/%s_*.agg'%name))
    hist=collections.defaultdict(lambda: np.zeros(NB,np.int64)); cnt=collections.Counter(); hits=collections.defaultdict(lambda: np.zeros(4,np.int64))
    tops=[]
    for fn in files:
        for line in open(fn):
            t=line.split()
            if t[0]=='A':
                oid,fam,n=int(t[1]),int(t[2]),int(t[3])
                cnt[(oid,fam,n)]+=int(t[4]); hits[(oid,fam,n)][1:]+=[int(t[5]),int(t[6]),int(t[7])]
                h=hist[(oid,fam,n)]
                for kv in t[9:]:
                    b,v=kv.split(':'); h[int(b)]+=int(v)
            elif t[0]=='T':
                tops.append(dict(oid=int(t[1]),fam=int(t[2]),n=int(t[3]),sc=int(t[4]),cid=int(t[5]),model=int(t[6]),f=[int(x) for x in t[7][2:].split(',') if x]))
    return dict(hist=hist,cnt=cnt,hits=hits,tops=tops)
def pooled(D):
    H=collections.defaultdict(lambda: np.zeros(NB,np.int64))
    for (oid,fam,n),h in D['hist'].items(): H[(fam,n)]+=h
    return H
def survival(Hp):
    """(fam,n) -> array S[b] = P(score bin >= b) and totals"""
    S={}
    for k,h in Hp.items():
        tot=h.sum(); S[k]=(np.cumsum(h[::-1])[::-1]/tot, tot)
    return S
def sbin(sc): return min(NB-1,max(0,(sc+8000)//20))
def pval(S,fam,n,sc):
    s,tot=S[(fam,n)]; b=sbin(sc)
    return max(s[b] if b<NB else 0, 0.5/tot) if b<NB else 0.5/tot
def hist_stats(Hp):
    out={}
    for k,h in Hp.items():
        x=(np.arange(NB)*20-8000+10)/1000.; tot=h.sum(); mu=(h*x).sum()/tot; sd=math.sqrt(max(1e-12,(h*(x-mu)**2).sum()/tot))
        out[k]=(mu,sd,tot)
    return out
if __name__=='__main__':
    names=sys.argv[1:] if len(sys.argv)>1 else ['real','nullR','nullP1','nullP2']
    runs={nm:load(nm) for nm in names}
    Sref=survival(pooled(runs['nullR'])); HS=hist_stats(pooled(runs['nullR']))
    rep={}
    # fragment counts
    for nm,Dd in runs.items():
        rep.setdefault('fragments',{})[nm]=int(sum(Dd['cnt'].values()))
        rep.setdefault('fragments_by_family',{})[nm]={FAM[f]:int(sum(v for (o,fa,n),v in Dd['cnt'].items() if fa==f)) for f in range(NF)}
    # (a) English-ness: per opening best -log10 p (fragments n>=5), and z of top score vs null (fam,n)
    A={}
    for nm,Dd in runs.items():
        best=collections.defaultdict(lambda:(0,None))
        for t in Dd['tops']:
            if t['n']<5 or (t['fam'],t['n']) not in Sref: continue
            p=pval(Sref,t['fam'],t['n'],t['sc']); lp=-math.log10(p)
            mu,sd,_=HS[(t['fam'],t['n'])]; z=(t['sc']/1000.-mu)/sd
            if lp>best[t['oid']][0] or (lp==best[t['oid']][0] and best[t['oid']][1] and z>best[t['oid']][1]['z']): best[t['oid']]=(lp,dict(t,z=z))
        A[nm]=best
    rep['a_best_per_opening']={nm:[(o,round(v[0],2),round(v[1]['z'],2) if v[1] else None) for o,v in sorted(b.items())] for nm,b in A.items()}
    # paired: openings where real beats all three nulls
    win=sum(1 for o in A['real'] if all(A['real'][o][0]>A[nm].get(o,(0,))[0] for nm in names[1:]))
    rep['a_openings_real_beats_all_nulls']=(win,len(A['real']))
    for nm in A: rep.setdefault('a_global_best',{})[nm]=max(((v[0],round(v[1]['z'],2),v[1]['oid'],v[1]['fam'],v[1]['n'],v[1]['sc'],v[1]['cid'],v[1]['model']) for v in A[nm].values()),default=None)
    # tail counts at pooled-nullR survival thresholds
    tails={}
    for nm,Dd in runs.items():
        Hp=pooled(Dd); row={}
        for thr in (1e-4,1e-5,1e-6):
            c=0
            for (fam,n),h in Hp.items():
                if n<5 or (fam,n) not in Sref: continue
                s,tot=Sref[(fam,n)]; bs=np.nonzero(s<=thr)[0]
                if len(bs)==0: continue
                c+=int(h[bs[0]:].sum())
            row['p<=%g'%thr]=c
        tails[nm]=row
    rep['a_tail_counts']=tails
    # (b)(c)(e) hit counts by fragment-length bucket
    buckets=[(4,5),(6,7),(8,9),(10,12),(13,47)]
    H={}
    for nm,Dd in runs.items():
        for typ,tn in ((1,'b_keyword'),(2,'c_numeric'),(3,'e_recurrence')):
            for lo,hi in buckets:
                v=int(sum(h[typ] for (o,f,n),h in Dd['hits'].items() if lo<=n<=hi))
                tot=int(sum(c for (o,f,n),c in Dd['cnt'].items() if lo<=n<=hi))
                H.setdefault(tn,{}).setdefault('%d-%d'%(lo,hi),{})[nm]=(v,tot)
    rep['hits']=H
    # per-family view for the long buckets
    fam_long={}
    for nm,Dd in runs.items():
        for typ,tn in ((1,'b'),(2,'c'),(3,'e')):
            for f in range(NF):
                fam_long.setdefault(tn,{}).setdefault(FAM[f],{})[nm]=int(sum(h[typ] for (o,fa,n),h in Dd['hits'].items() if fa==f and n>=8))
    rep['hits_n>=8_by_family']=fam_long
    json.dump(rep,open(OUT+'/analysis.json','w'),indent=1,default=str)
    for k in ('fragments','fragments_by_family','a_openings_real_beats_all_nulls','a_global_best','a_tail_counts','hits','hits_n>=8_by_family'):
        print(k,json.dumps(rep[k],default=str))
