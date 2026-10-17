"""Test (f): top-100 fragments by any test (40 by English-ness p-value, 20 longest per keyword / numeric / recurrence hit type),
extended by dictionary words of the next word's rune length (beam 5, 3 rounds). Usage: ftest.py run_name"""
import sys, json, glob, math, collections, numpy as np
from common import *
import analyze, ext, ext2, geom, pyfrag
name=sys.argv[1]
meta=json.load(open(OUT+'/cribs_meta.json')); lens={m_['oid']:m_['lens'] for m_ in meta}
nwords={m_['oid']:[x[1] for x in m_['cribs']] for m_ in meta}
cribs={}; posmap={}; cur=None
for fn in sorted(glob.glob(OUT+'/jobs/%s_*.txt'%name)):
    for line in open(fn):
        t=line.split()
        if t[0]=='OPEN': cur=int(t[1]); posmap[cur]=int(t[2]); cribs[cur]=[]; continue
        cribs[cur].append([int(x) for x in t[2:]])
Sref=analyze.survival(analyze.pooled(analyze.load('nullR')))
D=analyze.load(name)
cand=[]
for t in D['tops']:
    if t['n']<5 or (t['fam'],t['n']) not in Sref: continue
    p=analyze.pval(Sref,t['fam'],t['n'],t['sc']); cand.append((-math.log10(p),t['sc'],t))
cand.sort(key=lambda x:(-x[0],-x[1]))
items=[]; seen=set()
for lp,sc,t in cand:
    m_=28 if t['fam'] in (0,2) else 29
    k=(t['oid'],t['cid'],min(canon_hashes(t['f'],m_)))
    if k in seen: continue
    seen.add(k); items.append(dict(oid=t['oid'],cid=t['cid'],model=t['model'],test='a',stat=round(lp,2),n=t['n']))
    if len(items)>=40: break
hits={1:[],2:[],3:[]}
for fn in sorted(glob.glob(OUT+'/runs/%s_*.hits'%name)):
    for line in open(fn):
        t=line.split()
        if len(t)<9: continue
        oid,cid,model,fam,n,sc=map(int,t[1:7])
        f=[int(x) for x in t[7][2:].split(',') if x]; m_=28 if fam in (0,2) or (model>>27)&1 or (fam==5 and ((model>>24)&7)==0) else 29
        for typ in set(int(tg.split(':')[0]) for tg in t[8:]): hits[typ].append((n,sc,oid,cid,model,min(canon_hashes(f,m_))))
for typ,tn in ((1,'b'),(2,'c'),(3,'e')):
    k=0
    for n,sc,oid,cid,model,ch in sorted(hits[typ],key=lambda x:(-x[0],-x[1])):
        if (oid,cid,ch,tn) in seen: continue
        seen.add((oid,cid,ch,tn)); items.append(dict(oid=oid,cid=cid,model=model,test=tn,stat=n,n=n)); k+=1
        if k>=20: break
C=geom.C
out=[]
for it in items:
    pos=posmap[it['oid']]; prev=C[pos-1] if pos>0 else -1; c=C[pos:pos+80]
    item=dict(crib=cribs[it['oid']][it['cid']],nw=nwords[it['oid']][it['cid']],model=it['model'],test=it['test'])
    tr=ext2.extend(item,c,prev,pos,lens[it["oid"]],rounds=3)
    out.append(dict(it,model_name=pyfrag.model_name(it['model']),traj=tr))
    print(it['test'],it['oid'],it['n'],it['stat'],pyfrag.model_name(it['model']),tr,flush=True)
json.dump(out,open(OUT+'/ftest_%s.json'%name,'w'),indent=1)
