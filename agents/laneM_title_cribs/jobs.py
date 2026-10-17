"""Write job files: real openings, null R (random cribs, same length multiset, same count), null P (real cribs at random word starts)."""
import random, json, sys, collections
from common import *
import geom, vocab
C=geom.C
def unique_openings():
    d=collections.OrderedDict()
    for o in geom.openings:
        d.setdefault(o['pos'],dict(pos=o['pos'],lens=o['lens'],labels=[]))['labels'].append('%s%d'%(o['kind'],o['id']))
    return list(d.values())
def ctx(pos,clen,Cs=None):
    Cs=Cs if Cs is not None else C
    return (Cs[pos-1] if pos>0 else -1), Cs[pos:pos+clen]
def write_job(fn, blocks):
    with open(fn,'w') as f:
        for oid,pos,prev,cc,cribs in blocks:
            f.write('OPEN %d %d %d %d %s\n'%(oid,pos,prev,len(cc),' '.join(map(str,cc))))
            for cid,r in enumerate(cribs): f.write('%d %d %s\n'%(cid,len(r),' '.join(map(str,r))))
if __name__=='__main__':
    V=vocab.load_V()
    UO=unique_openings()
    meta=[]; real=[]
    for oid,o in enumerate(UO):
        cand=vocab.candidates(o['lens'],V)
        cribs=list(cand.keys())
        meta.append(dict(oid=oid,pos=o['pos'],lens=o['lens'],labels=o['labels'],cribs=[[cand[r][0],cand[r][1],cand[r][2],list(r)] for r in cribs]))
        clen=max(len(r) for r in cribs)+2
        prev,cc=ctx(o['pos'],clen)
        real.append((oid,o['pos'],prev,cc,cribs))
    json.dump(meta,open(OUT+'/cribs_meta.json','w'))
    rng=random.Random(3301)
    # null R
    nullR=[]
    for oid,pos,prev,cc,cribs in real:
        nullR.append((oid,pos,prev,cc,[tuple(rng.randrange(29) for _ in r) for r in cribs]))
    # null P: two replicates, random word starts >= 40 runes from every real opening
    opos=[o['pos'] for o in UO]
    starts=[s for s in geom.starts if all(abs(s-p)>40 for p in opos) and s+60<len(C) and s>0]
    nullP={}
    for rep in (1,2):
        bl=[]
        for oid,pos,prev,cc,cribs in real:
            q=rng.choice(starts); pv,c2=ctx(q,len(cc)); bl.append((oid,q,pv,c2,cribs))
        nullP[rep]=bl
    # balance into 4 parts by crib count
    def split(blocks,name):
        parts=[[] for _ in range(4)]; load=[0]*4
        for b in sorted(blocks,key=lambda b:-len(b[4])):
            i=load.index(min(load)); parts[i].append(b); load[i]+=len(b[4])
        for i,p in enumerate(parts): write_job(OUT+'/jobs/%s_%d.txt'%(name,i),p)
    import os; os.makedirs(OUT+'/jobs',exist_ok=True)
    split(real,'real'); split(nullR,'nullR'); split(nullP[1],'nullP1'); split(nullP[2],'nullP2')
    json.dump({'nullP%d'%k:[b[1] for b in v] for k,v in nullP.items()},open(OUT+'/nullP_positions.json','w'))
    print('unique openings',len(UO),'cribs',sum(len(b[4]) for b in real))
    # small timing job
    write_job(OUT+'/jobs/time.txt',[real[0][:4]+(real[0][4][:2000],)])
