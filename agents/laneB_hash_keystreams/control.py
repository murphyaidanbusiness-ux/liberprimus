import sys, time, json, pickle, random
import numpy as np
from multiprocessing import Pool
import core, gens, seeds, driver
from core import *

def inv_tab(app):
    T=app['tab'].reshape(29,29)
    inv=np.zeros((29,29),dtype=np.int64)-1   # inv[k][p] = D
    for D in range(29):
        for k in range(app['q']):
            inv[k][T[D][k]]=D if inv[k][T[D][k]]<0 else inv[k][T[D][k]]
    return inv

def synth_plain(corp_pages):
    idx=[]
    for p in seeds.SOLVED_IDX: idx+=p
    out=[]; j=0
    for pg in corp_pages:
        out.append([idx[(j+i)%len(idx)] for i in range(len(pg))]); j+=len(pg)
    return out

def encipher(plain_pages, keyvec, app_i, mode, koff=0, pkoff=None):
    app=APPS[app_i]; inv=inv_tab(app)
    pages=[]; j=koff
    for pg,pp in enumerate(plain_pages):
        if mode==1: j=koff
        if mode==2: j=int(pkoff[pg])+koff
        prev=0; cpage=[]
        for p in pp:
            k=int(keyvec[j]); D=int(inv[k][p])
            assert D>=0
            if app['prev']:
                c=(prev+D)%29; prev=c
            else: c=D
            cpage.append(c)
            if not (app['conv']==1 and app['prev'] and D==0): j+=1
        pages.append(cpage)
    return pages

def name_idx(appname): return [a['name'] for a in APPS].index(appname)
def map_idx(mapname): return [m for m,_ in MAPS].index(mapname)

def plant_G(seed, gt, hn, mapname, appname, mode):
    corp0=REAL
    KL=corp0.n+16
    data,hl=gens.stream(gt,hn,seed,KL+800)
    res=make_keys(data,hl,KL)
    pl=synth_plain([p for p in corp0.pages])
    ct=encipher(pl,res[mapname],name_idx(appname),mode)
    return ct,pl

def plant_P(f,gt,hn,mapname,appname):
    corp0=REAL
    pl=synth_plain(corp0.pages)
    keys=np.zeros(corp0.KLP,dtype=np.uint8)
    for pg in range(corp0.npages):
        L=len(corp0.pages[pg])+8
        data,hl=gens.stream(gt,hn,f(pg),L*2+200)
        res=make_keys(data,hl,L); off=int(corp0.pkoff[pg]); keys[off:off+L]=res[mapname]
    ct=encipher(pl,keys,name_idx(appname),2,0,corp0.pkoff)
    return ct,pl

def summarize(st, tag):
    out=[]
    for name in ('top_w',):
        top=sorted(st[name],reverse=True)[:5]
        for (v,w,p,meta,m,a,md) in top:
            out.append('%s top: IoC=%.4f prefix=%.4f seed=%r gen=%s/%s map=%s app=%s mode=%s'%(tag,w,p,meta[0],meta[2],meta[3],MAPS[m][0],APPS[a]['name'],('cont','restart','perpage')[md]))
    return out

if __name__=='__main__':
    which=sys.argv[1]
    G=seeds.build_G()
    GL=gens.GEN_LIST
    nproc=4
    if which=='G1':
        plant=(b'cicada3301','ctr_be4','sha256','byte_mod28','chainadd+1|convX',0)
    elif which=='G2':
        plant=(b'THE PRIMES ARE SACRED','hmac_ctr','sha3_512','b29dig_rej28_msd','gflog_g3-1|convY',1)
    elif which=='G3':
        plant=(b'7A35090F','chainhex','blake2b','hexascii_mod28','gflinmul|convX',0)
    elif which=='G4':
        plant=(b'3301','ctr_asc1','sha1','byte_rej29','otp-1',0)
    if which.startswith("G"):
        ct,pl=plant_G(plant[0],plant[1],plant[2],plant[3],plant[4],plant[5])
        # stats on the synthetic
        flat=[x for p in ct for x in p]
        dbl=sum(1 for a,b in zip(flat,flat[1:]) if a==b)/len(flat)
        pf=[x for p in pl for x in p]
        n=len(pf); cnt=np.bincount(pf,minlength=29); pioc=29*(cnt*(cnt-1)).sum()/(n*(n-1))
        cc=np.bincount(flat,minlength=29); cioc=29*(cc*(cc-1)).sum()/(len(flat)*(len(flat)-1))
        print(which,'synthetic: plaintext IoC %.3f ciphertext IoC %.3f doublet rate %.4f'%(pioc,cioc,dbl),flush=True)
        t=time.time()
        # dictionary: full G for G1, subset (+planted) for others
        seedlist=G if which=='G1' else (G[:150]+[('plant',plant[0])])
        # make sure planted present
        if not any(b==plant[0] for _,b in seedlist): seedlist=seedlist+[('plant',plant[0])]
        if which=='G1' and not any(b==plant[0] for _,b in G): print('planted seed not in dictionary!')
        pages=ct
        random.Random(1).shuffle(seedlist)
        parts=driver.chunks(seedlist,nproc*6)
        with Pool(nproc) as pool:
            sts=pool.map(driver.work_G,[(pages,pp,GL,0,1.0,i) for i,pp in enumerate(parts)])
        st=driver.merge(sts)
        print(which,'streams',st['nstreams'],'trials',st['ntr'],'time %.0fs'%(time.time()-t))
        for l in summarize(st,which): print(l)
        print('PLANT',plant)
        # quadgram of best decode
        v,w,p,meta,m,a,md=sorted(st['top_w'],reverse=True)[0]
        corp=Corpus(pages); KL=corp.n+16
        data,hl=gens.stream(meta[2],meta[3],meta[1],KL+800); res=make_keys(data,hl,KL)
        out=decode_cfg(corp,res[MAPS[m][0]],a,md,0)
        print('best decode quadgram %.3f  text: %s'%(qscore(list(out)),text_of(list(out[:120]))))
        hist=st['hist']['chain' if True else 'otp']
        pickle.dump(dict(top=sorted(st['top_w'],reverse=True)[:10],ntr=st['ntr']),open(HERE+'/control_%s.pkl'%which,'wb'))

    if which=='P1':
        Pf=seeds.build_P()
        names=[n for n,_ in Pf]
        target='pnum|cicada3301|\'-\'|dec|\'\'|o1'
        fi=names.index(target)
        f=Pf[fi][1]
        ct,pl=plant_P(f,'ctr_asc1','blake2b','hexascii_mod28','gflinmul|convX')
        flat=[x for p in ct for x in p]
        cc=np.bincount(flat,minlength=29); print('P1 synthetic ciphertext IoC %.3f'%(29*(cc*(cc-1)).sum()/(len(flat)*(len(flat)-1))))
        # pipeline: sample of P funcs incl. planted (100 funcs) x all 49 gens
        rng=random.Random(5); sel=rng.sample(range(len(Pf)),99)
        if fi not in sel: sel.append(fi)
        t=time.time()
        parts=driver.chunks(sel,nproc*4)
        with Pool(nproc) as pool:
            sts=pool.map(driver.work_P,[(ct,pp,GL,0,1.0,i) for i,pp in enumerate(parts)])
        st=driver.merge(sts)
        print('P1 sets',st['nstreams'],'trials',st['ntr'],'time %.0fs'%(time.time()-t))
        for l in summarize(st,'P1'): print(l)
        print('PLANT',target,'ctr_asc1/blake2b hexascii_mod28 gflinmul|convX perpage')
        print('best decode')
