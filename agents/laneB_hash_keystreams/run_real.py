import sys, time, pickle, random, os
import numpy as np
from multiprocessing import Pool
import core, gens, seeds, driver
from core import *
phase=sys.argv[1]
nproc=int(os.environ.get('NPROC','4'))
G=seeds.build_G()
Pf=seeds.build_P()
GL=gens.GEN_LIST
def run(fn, tasks, tag):
    t=time.time(); sts=[]
    with Pool(nproc) as pool:
        for i,r in enumerate(pool.imap_unordered(fn,tasks)):
            sts.append(r)
            print(tag,'chunk',i+1,'/',len(tasks),'streams so far',sum(s['nstreams'] for s in sts),'elapsed %.0f'%(time.time()-t),flush=True)
    st=driver.merge(sts); st['elapsed']=time.time()-t
    return st
pages_real=[list(p) for p in REAL.pages]
if phase=='G_real':
    koff=int(sys.argv[2]) if len(sys.argv)>2 else 0
    sl=list(G); random.Random(7).shuffle(sl)
    st=run(driver.work_G,[(pages_real,pp,GL,koff,1.0,i) for i,pp in enumerate(driver.chunks(sl,nproc*10))],'G_real')
    pickle.dump(st,open(HERE+'/res_G_real_k%d.pkl'%koff,'wb'))
elif phase=='P_real':
    koff=int(sys.argv[2]) if len(sys.argv)>2 else 0
    fi=list(range(len(Pf))); random.Random(7).shuffle(fi)
    st=run(driver.work_P,[(pages_real,pp,GL,koff,1.0,i) for i,pp in enumerate(driver.chunks(fi,nproc*20))],'P_real')
    pickle.dump(st,open(HERE+'/res_P_real_k%d.pkl'%koff,'wb'))
elif phase=='PB_real':
    core_labels={'word','num','title','gsum','anend','pgp','text'}
    sl=[x for x in G if x[0] in core_labels]+[x for x in G if x[0]=='pagenum' and x[1].isdigit() and int(x[1])<=58]
    random.Random(7).shuffle(sl)
    st=run(driver.work_G,[(pages_real,pp,gens.PBKDF_LIST,0,1.0,i) for i,pp in enumerate(driver.chunks(sl,nproc*10))],'PB_real')
    pickle.dump(st,open(HERE+'/res_PB_real.pkl','wb'))
elif phase=='G_null':
    sub=float(sys.argv[2]); lo=int(sys.argv[3]); hi=int(sys.argv[4])
    sl=list(G); random.Random(7).shuffle(sl)
    for s in range(lo,hi):
        corp=(shuffled_D if os.environ.get('NULLKIND','D')=='D' else shuffled)(REAL,1000+s)
        pg=[list(p) for p in corp.pages]
        st=run(driver.work_G,[(pg,pp,GL,0,sub,5000+s*100+i) for i,pp in enumerate(driver.chunks(sl,nproc*4))],'G_null%d'%s)
        pickle.dump(st,open(HERE+'/res_G_null_%d.pkl'%s,'wb'))
elif phase=='P_null':
    sub=float(sys.argv[2]); lo=int(sys.argv[3]); hi=int(sys.argv[4])
    fi=list(range(len(Pf))); random.Random(7).shuffle(fi)
    for s in range(lo,hi):
        corp=(shuffled_D if os.environ.get('NULLKIND','D')=='D' else shuffled)(REAL,1000+s)
        pg=[list(p) for p in corp.pages]
        st=run(driver.work_P,[(pg,pp,GL,0,sub,7000+s*100+i) for i,pp in enumerate(driver.chunks(fi,nproc*8))],'P_null%d'%s)
        pickle.dump(st,open(HERE+'/res_P_null_%d.pkl'%s,'wb'))
elif phase=='G_extra':
    on=[l.strip() for l in open(HERE+'/onions_all.txt') if l.strip()]
    extra=[]
    seen=set(b for _,b in G)
    def addx(lab,b):
        if b not in seen: seen.add(b); extra.append((lab,b))
    for o in on:
        for b in seeds.ftext(o)+seeds.ftext(o[:-6]): addx('onion_extra',b)
    for fp in ('67F363C61BA8FB6FDBA9C47D0670B0E57A35090F',):
        for b in seeds.fhex(fp): addx('pgp_extra',b)
    print('extra seeds',len(extra))
    for koff in (0,1):
        st=run(driver.work_G,[(pages_real,pp,GL,koff,1.0,i) for i,pp in enumerate(driver.chunks(extra,nproc*4))],'G_extra')
        pickle.dump(st,open(HERE+'/res_G_extra_k%d.pkl'%koff,'wb'))
elif phase=='G_core':
    labs={'word','num','title','gsum','anend','pgp','text','plaintext','runes','len'}
    sl=[x for x in G if x[0] in labs]
    random.Random(7).shuffle(sl)
    print('core seeds',len(sl),'roots',core.ROOTS,'apps',core.NAPPS)
    st=run(driver.work_G,[(pages_real,pp,GL,0,1.0,i) for i,pp in enumerate(driver.chunks(sl,nproc*10))],'G_core')
    pickle.dump(st,open(HERE+'/res_G_core_roots.pkl','wb'))
