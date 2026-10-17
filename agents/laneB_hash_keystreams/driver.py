import sys, os, time, heapq, pickle, random
import numpy as np
import core, gens, seeds
from core import *

TOPK=60
def new_state():
    return dict(top_w=[], top_p=[], hist={}, ntr=0, nstreams=0, pmax=np.zeros(55,dtype=np.float32), pmaxcfg=np.zeros(55,dtype=np.int64), pmaxdesc=[None]*55)

Q28 = (MAP_Q==28)
def cfg_desc(m,a,md): return (MAPS[m][0], APPS[a]['name'], ('cont','restart','perpage')[md])

def ingest(st, ow, op, meta, mode_ok):
    """ow: float32 array NTR; meta: descriptor of stream (seed_label_hex, seedbytes, gen)"""
    o=ow.reshape(NMAPS,NAPPS,3)
    valid=(o>=0)
    # histograms per group (chain vs otp): bins of 0.0001 from 0.98
    for grp,mask in (('chain',(MAP_Q==28)[:,None,None]&valid),('otp',(MAP_Q==29)[:,None,None]&valid)):
        v=o[mask]
        if v.size==0: continue
        h=np.bincount(np.clip(((v-0.98)/0.0001).astype(np.int64),0,999),minlength=1000)
        st['hist'][grp]=st['hist'].get(grp,0)+h
    st['ntr']+=int(valid.sum())
    # top lists
    flat=ow
    for name,arr,key in (('top_w',ow,'w'),('top_p',op,'p')):
        k=min(8,arr.size)
        idx=np.argpartition(arr,-k)[-k:]
        for t in idx:
            v=float(arr[t])
            if v<0: continue
            heap=st[name]
            if len(heap)<TOPK or v>heap[0][0]:
                m,a,md=trial_decode(int(t))
                item=(v,float(ow[t]),float(op[t]),meta,m,a,md)
                if len(heap)<TOPK: heapq.heappush(heap,item)
                else: heapq.heapreplace(heap,item)

def work_G(args):
    corp_pages, seedlist, genlist, koff, sub, subseed = args
    corp=Corpus(corp_pages)
    KL=corp.n+16
    st=new_state()
    rng=random.Random(subseed)
    for (lab,sd) in seedlist:
        for (gt,hn) in genlist:
            if sub<1.0 and rng.random()>sub: continue
            data,hl=gens.stream(gt,hn,sd,KL+800)
            res=make_keys(data,hl,KL)
            keys=keyarray(res,KL)
            ow,op,pm,pc=run_sweep(corp,keys,KL,koff,3,None,st['pmax'],st['pmaxcfg'],0,None)
            meta=(lab,sd,gt,hn,koff)
            ingest(st,ow,op,meta,3)
            st['nstreams']+=1
    return st

def merge(sts):
    out=new_state()
    for s in sts:
        out['ntr']+=s['ntr']; out['nstreams']+=s['nstreams']
        for g,h in s['hist'].items(): out['hist'][g]=out['hist'].get(g,0)+h
        for name in ('top_w','top_p'):
            for it in s[name]:
                heap=out[name]
                if len(heap)<TOPK: heapq.heappush(heap,it)
                elif it[0]>heap[0][0]: heapq.heapreplace(heap,it)
        out['pmax']=np.maximum(out['pmax'],s['pmax'])
    return out

def work_P(args):
    corp_pages, fidx_list, genlist, koff, sub, subseed = args
    corp=Corpus(corp_pages)
    Pf=seeds.build_P()
    st=new_state(); rng=random.Random(subseed)
    KLP=corp.KLP
    for fi in fidx_list:
        name,f=Pf[fi]
        for (gt,hn) in genlist:
            if sub<1.0 and rng.random()>sub: continue
            keys=np.zeros((NMAPS,KLP),dtype=np.uint8)
            for pg in range(corp.npages):
                L=len(corp.pages[pg])+8
                sd=f(pg)
                data,hl=gens.stream(gt,hn,sd,L*2+200)
                res=make_keys(data,hl,L)
                off=int(corp.pkoff[pg])
                for mi,(mn,_) in enumerate(MAPS): keys[mi,off:off+L]=res[mn]
            ow,op,pm,pc=run_sweep(corp,np.ascontiguousarray(keys),KLP,koff,4,corp.pkoff,st['pmax'],st['pmaxcfg'],0,None)
            ingest(st,ow,op,(name,b'',gt,hn,koff),4)
            st['nstreams']+=1
    return st

def chunks(lst,n):
    k=-(-len(lst)//n)
    return [lst[i:i+k] for i in range(0,len(lst),k)]
