import glob, sys, json, math, collections, numpy as np
sys.path.insert(0,'.')
from common import *
MT=['chain-Z28','chain-GF29','raw Vig/Beau','raw+skip']
CLS=['C1 phrases','C2 words','C3 n-grams']
cribs=json.load(open(LANE+'/cribs.json'))
def parse(path):
    cells={}; tops=[]
    for line in open(path):
        p=line.split()
        if p[0]=='CELL':
            cells[(int(p[1]),int(p[2]),int(p[3]))]=[float(x) for x in p[4:]]
        elif p[0].startswith('TOP'):
            tops.append(dict(kind=p[0],mt=int(p[1]),Z=float(p[2]),crib=int(p[3]),pos=int(p[4]),var=int(p[5]),shift=int(p[6]),orient=int(p[7]),W=int(p[8]),al=int(p[9]),cls=int(p[10]),dict=int(p[11]),per=int(p[12]),L=int(p[13]),k=[int(x) for x in p[14].strip(',').split(',')]))
    return cells,tops
def load(F):
    real=parse(LANE+'/out/F%d_real.txt'%F)
    nulls=[parse(f)[0] for f in sorted(glob.glob(LANE+'/out/F%d_null*.txt'%F)) if not f.endswith('.tmp')]
    return real,nulls
# cell vector index: 0 nfrag,1 maxZ,2 maxD,3 maxP,4 nZ3,5 nZ4,6 nZ5,7 nD9,8 nD10,9 nD12,10 nP5,11 nP6,12 nP8
def fwtable(F,out):
    (rc,rt),nulls=load(F)
    out.append('\n### F-interrupt variant = %s  (null shuffles: %d)\n'%('F-runes deleted from stream' if F else 'stream as given',len(nulls)))
    for stat,idx,name in ((1,1,'running-text Z (quadgram, best of 29 shifts x 2 orientations)'),(2,2,'dictionary-keyword hit length (letters, >= 8)'),(3,3,'periodicity (longest run of k[i]=k[i+p], p<=12)')):
        out.append('\n**%s**\n'%name)
        out.append('| model | class | aligned | #fragments (real) | real max | null mean | null sd | null max | z(real vs null) | nulls >= real |')
        out.append('|---|---|---|---|---|---|---|---|---|---|')
        for mt in range(4):
            if idx==2 and mt==3: continue
            for cls in range(3):
                for al in (0,1):
                    key=(mt,cls,al)
                    if key not in rc: continue
                    r=rc[key][idx]; nv=np.array([n[key][idx] for n in nulls if key in n])
                    if len(nv)==0: continue
                    sd=nv.std(ddof=1) if len(nv)>1 else float('nan')
                    z=(r-nv.mean())/sd if sd>0 else float('nan')
                    out.append('| %s | %s | %s | %.3g | %.3f | %.3f | %.3f | %.3f | %s | %d/%d |'%(MT[mt],CLS[cls],'yes' if al else 'no',rc[key][0],r,nv.mean(),sd,nv.max(),('%+.2f'%z) if z==z else 'n/a',int((nv>=r).sum()),len(nv)))
    # tail counts
    out.append('\n**Tail counts (real vs null mean), running-text Z>=4 / Z>=5 and PER>=5 / DICT>=10 counts**\n')
    out.append('| model | class | aligned | real nZ>=4 | null mean | real nZ>=5 | null mean | real nPER>=5 | null mean | real nDICT>=10 | null mean |')
    out.append('|---|---|---|---|---|---|---|---|---|---|---|')
    for mt in range(4):
        for cls in range(3):
            for al in (0,1):
                key=(mt,cls,al)
                if key not in rc: continue
                def col(i): return rc[key][i], np.mean([n[key][i] for n in nulls if key in n]) if nulls else float('nan')
                a=col(5);b=col(6);c_=col(10);d=col(8)
                out.append('| %s | %s | %s | %d | %.1f | %d | %.1f | %d | %.1f | %d | %.1f |'%(MT[mt],CLS[cls],'yes' if al else 'no',a[0],a[1],b[0],b[1],c_[0],c_[1],d[0],d[1]))
    return rt
def pos_desc(pos):
    pg=np.load(LANE+'/pg.npy'); wd=np.load(LANE+'/wd.npy')
    p=int(pg[pos]); first=int(np.argmax(pg==p)); 
    return 'p%d+%d'%(p,pos-first)
def hit_row(h):
    cb=cribs[h['crib']]; m=28 if h['mt']==0 else 29
    ks=[]
    for v in h['k']:
        if v<0: ks.append('?'); continue
        a=(m-v)%m if h['orient'] else v
        a=(a+h['shift'])%m
        ks.append(TR[a])
    return cb,''.join(ks)
if __name__=='__main__':
    out=[]
    res={}
    for F in (0,1):
        try: rt=fwtable(F,out)
        except FileNotFoundError: continue
        res[F]=rt
    open(LANE+'/agg_tables.md','w').write('\n'.join(out))
    print('\n'.join(out))
