"""Onward decryption of every keyword / numeric / recurrence hit (fragment length >= HMIN): the hit implies a key that continues past
the crib; decrypt the next N runes under it and score the plaintext. Same procedure on null hits. Usage: step5.py run_name [HMIN]"""
import sys, json, collections, numpy as np, glob
from common import *
import prep_keys, onward, pyfrag
from pyfrag import decode_model
N=60
def ctx_for(pos,L):
    C=onward.corpus(); return (C[pos-1] if pos>0 else -1), C[pos:pos+L+N+3]
def eval_hit(model,crib,f,m,tag,pos,c,prev):
    typ,src,off=tag
    srcname=pyfrag.SRC[{1:'kw',2:'num',3:'rec'}[typ]][src]
    key=src if typ==1 else srcname
    n=len(f); w=prep_keys.raw_seq(typ,key,m,off,min(n,24))
    if None in w: return None
    al=prep_keys.align(f[:24],w,m)
    if al is None: return None
    eps,s=al
    K=prep_keys.raw_seq(typ,key,m,off,n+N+4)
    keyfn=lambda i: None if i>=len(K) or K[i] is None else int((eps*int(K[i])+s)%m)
    r=onward.decrypt_onward(model,list(crib),c,prev,keyfn,n,N=N)
    if r is None: return None
    return r[0],r[1],srcname
if __name__=='__main__':
    name=sys.argv[1]; HMIN=int(sys.argv[2]) if len(sys.argv)>2 else 8
    if name.startswith('control'):
        cm=json.load(open(OUT+'/control_meta.json')); cribs={900:[x[1] for x in cm['cribs']],910:[x[1] for x in cm['cribs']]}
        ctrl={900:cm['ctrl']['chain_runkey'],910:cm['ctrl']['vig_skip_kw']}
        for k in range(1,6): ctrl[900+k]=ctrl[900]; ctrl[910+k]=ctrl[910]
        cur=None
        for line in open(OUT+'/jobs/control.txt'):
            t=line.split()
            if t[0]=='OPEN': cur=int(t[1]); cribs[cur]=[]; continue
            cribs[cur].append([int(x) for x in t[2:]])
        posmap={o:0 for o in ctrl}
        files=[OUT+'/runs/%s_n6.hits'%name]
    else:
        cribs={}; posmap={}; cur=None
        for fn in sorted(glob.glob(OUT+'/jobs/%s_*.txt'%name)):
            for line in open(fn):
                t=line.split()
                if t[0]=='OPEN': cur=int(t[1]); posmap[cur]=int(t[2]); cribs[cur]=[]; continue
                cribs[cur].append([int(x) for x in t[2:]])
        files=sorted(glob.glob(OUT+'/runs/%s_*.hits'%name)); ctrl=None
    res=[]; seen=set()
    for fn in files:
        for line in open(fn):
            t=line.split()
            if len(t)<9: continue
            oid,cid,model,fam,n,sc=map(int,t[1:7])
            if n<HMIN: continue
            f=[int(x) for x in t[7][2:].split(',') if x]; m=28 if fam in (0,2) or (fam==5 and ((model>>24)&7)==0) or (model>>27)&1 else 29
            crib=cribs[oid][cid]; pos=posmap[oid]
            if ctrl is not None: c=ctrl[oid][:len(crib)+N+3]; prev=-1
            else: prev,c=ctx_for(pos,len(crib))
            for tg in t[8:]:
                typ,src,off=map(int,tg.split(':'))
                k=(oid,tuple(f),typ,src,off,model)
                if k in seen: continue
                seen.add(k)
                r=eval_hit(model,crib,f,m,(typ,src,off),pos,c,prev)
                if r: res.append(dict(oid=oid,cid=cid,model=model,n=n,typ=typ,src=r[2],off=off,score=r[0],pt=''.join(TR[x] for x in r[1][:40]), abs_pos=pos))
    res.sort(key=lambda r:-r['score'])
    json.dump(res,open(OUT+'/step5_%s.json'%name,'w'))
    sc=np.array([r['score'] for r in res]) if res else np.array([0.])
    print(name,'hits evaluated',len(res),'onward score mean %.3f sd %.3f max %.3f'%(sc.mean(),sc.std(),sc.max()))
    for r in res[:8]: print(' %.3f'%r['score'],r['oid'],r['n'],pyfrag.model_name(r['model']),r['typ'],r['src'],r['off'],r['pt'])
