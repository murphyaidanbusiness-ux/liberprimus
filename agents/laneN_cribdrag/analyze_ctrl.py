import json, sys, collections, math
sys.path.insert(0,'.')
from common import *
truth=json.load(open(LANE+'/ctrl/truth_cribs.json'))
tj=json.load(open(LANE+'/ctrl/truth.json')); a=tj['a']; PL=tj['PL']
cribs=json.load(open(LANE+'/cribs.json'))
def load(name):
    rows=[]
    for line in open(LANE+'/ctrl/dump_%s.txt'%name):
        p=line.split()
        rows.append(dict(crib=int(p[0]),pos=int(p[1]),mt=int(p[2]),var=int(p[3]),shift=int(p[4]),orient=int(p[5]),W=int(p[6]),al=int(p[7]),cls=int(p[8]),L=int(p[9]),Z=float(p[10]),dict=int(p[11]),per=int(p[12]),g=int(p[13])))
    return rows
def cells(name):
    out={}
    for line in open(LANE+'/ctrl/out_%s.txt'%name):
        if line.startswith('CELL'):
            p=line.split(); out[(int(p[1]),int(p[2]),int(p[3]))]=[float(x) for x in p[4:]]
    return out
def norm_p_to_z(p):
    # one-sided normal quantile via bisection on erfc
    if p<=0: return 99.0
    lo,hi=0,40
    for _ in range(100):
        mid=(lo+hi)/2
        if 0.5*math.erfc(mid/math.sqrt(2))>p: lo=mid
        else: hi=mid
    return lo
for name,mtsel,stat in (('chain_A',(0,),'Z'),('chain_B',(0,),'Z'),('vig_A',(2,3),'PERDICT'),('vig_B',(2,3),'PERDICT')):
    rows=load(name); cl=cells(name)
    byk=collections.defaultdict(list)
    for r in rows: byk[(r['crib'],r['pos'])].append(r)
    print('=====',name,'dump rows',len(rows))
    # truth occurrences (pos within planted region); for _B truth same positions but alignment is w.r.t. LP2 words -> only unaligned
    n_true=0; hits=[]
    for t in truth:
        L=t['L']
        for al in ((0,1) if name.endswith('A') else (0,)):
            if al==1 and not t['al']: continue
            if al==0 and t['alonly']: continue
            n_true+=1
            rs=[r for r in byk.get((t['crib'],t['pos']),[]) if r['al']==al and r['mt'] in mtsel]
            if stat=='Z':
                Z=max([r['Z'] for r in rs if r['mt']==0 and r['var']==0],default=None)
            else:
                Z=max([r['Z'] for r in rs if r['mt']==3],default=None)
            per=max([r['per'] for r in rs],default=0); dc=max([r['dict'] for r in rs if r['mt']==2],default=0)
            hits.append((t,al,Z,per,dc))
    if stat=='Z':
        have=[h for h in hits if h[2] is not None]
        print('true crib-occurrences tested (aligned+unaligned views):',n_true,' in dump with Z>=3:',len(have))
        # by length bucket
        bk=collections.defaultdict(list)
        for t,al,Z,per,dc in hits:
            b='L<8' if t['L']<8 else ('8-11' if t['L']<12 else ('12-19' if t['L']<20 else ('20-39' if t['L']<40 else '40+')))
            bk[b].append(Z)
        for b in ('L<8','8-11','12-19','20-39','40+'):
            v=bk.get(b,[])
            if not v: continue
            z5=sum(1 for z in v if z is not None and z>5)
            print('  %-6s n=%3d  detected(Z>=3)=%3d  Z>5=%3d  median Z(detected)=%s  max=%s'%(b,len(v),sum(1 for z in v if z is not None),z5, (sorted([z for z in v if z is not None])[len([z for z in v if z is not None])//2] if any(z is not None for z in v) else None), max([z for z in v if z is not None],default=None)))
        # false: rows with Z>=5 and (pos,crib) not true and mt==0
        truepos=set((t['crib'],t['pos']) for t in truth)
        # background English also contains true cribs: count Z>=5 rows outside planted region
        inreg=[r for r in rows if r['mt']==0 and r['Z']>=5 and a<=r['pos']<a+PL]
        outreg=[r for r in rows if r['mt']==0 and r['Z']>=5 and not(a<=r['pos']<a+PL)]
        print('  Z>=5 chain rows: in planted region',len(inreg),' elsewhere (background English incl. true C2/C3 cribs in Walden)',len(outreg))
        # in planted region, the ones that are not true occurrence
        bad=[r for r in inreg if (r['crib'],r['pos']) not in truepos]
        print('  of in-region Z>=5 rows, not a true crib occurrence:',len(bad))
        # top true detections
        hs=sorted([h for h in hits if h[2] is not None],key=lambda h:-h[2])[:8]
        for t,al,Z,per,dc in hs: print('   top: Z=%.1f L=%d al=%d crib=%s'%(Z,t['L'],al,t['words'][:50]))
        # worst long cribs
        miss=[h for h in hits if h[0]['L']>=12 and (h[2] is None or h[2]<5)]
        print('  long (L>=12) true occurrences with Z<5 or missing:',len(miss),'of',sum(1 for h in hits if h[0]['L']>=12))
    else:
        print('keyword control: true occurrences',n_true)
        cl_=cl
        # total fragments per mt for chance prob of PER>=r
        nf=sum(v[0] for k,v in cl_.items() if k[0]==2)
        print('  raw(mt2) fragments',nf)
        bk=collections.defaultdict(list)
        for t,al,Z,per,dc in hits:
            bk[(t['L']//8)*8].append((per,dc,Z,t['L']))
        for b in sorted(bk):
            v=bk[b]
            pers=[x[0] for x in v]; dcs=[x[1] for x in v]
            print('  L in [%d,%d): n=%d  PER median %s max %s | DICT>=9: %d | rawskip Z>=5: %d'%(b,b+8,len(v),sorted(pers)[len(pers)//2],max(pers),sum(1 for d in dcs if d>=9),sum(1 for x in v if x[2] is not None and x[2]>=5)))
        # chance of per>=r: from cells counts
        print('  cell counts raw (cls,al): nfrag, maxPER, nP5, nP6, nP8')
        for k in sorted(cl_):
            if k[0]==2: print('   ',k,'nfrag %.0f maxPER %.0f nP5 %d nP6 %d nP8 %d maxDICT %.0f nD9 %d'%(cl_[k][0],cl_[k][3],cl_[k][10],cl_[k][11],cl_[k][12],cl_[k][2],cl_[k][6]))
        # false hits: per>=8 outside true positions
        truepos=set((t['crib'],t['pos']) for t in truth)
        fp=[r for r in rows if r['mt']==2 and r['per']>=8 and (r['crib'],r['pos']) not in truepos]
        print('  raw rows with PER>=8 not at a true crib occurrence:',len(fp), ' PER>=10:',sum(1 for r in fp if r['per']>=10))
