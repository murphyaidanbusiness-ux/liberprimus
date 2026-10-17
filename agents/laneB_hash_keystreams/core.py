import sys, os, ctypes, hashlib, hmac, math, json, random
import numpy as np
SCRATCH='.'
HERE=SCRATCH+'/agents/laneB_hash_keystreams'
sys.path.insert(0, SCRATCH+'/lp')
import lpdata
TR=lpdata.TR; RUNES=lpdata.RUNES
U, C, SHA = lpdata.unsolved()
assert SHA=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
lib=ctypes.CDLL(HERE+'/libsweep.so')
u8p=ctypes.POINTER(ctypes.c_uint8)
def P(a): return a.ctypes.data_as(ctypes.c_void_p)

# ---------------- corpus object
class Corpus:
    def __init__(self, pages_idx):
        self.pages=pages_idx
        self.c=np.array([x for p in pages_idx for x in p],dtype=np.uint8)
        self.n=len(self.c)
        ps=np.zeros(self.n,dtype=np.uint8); pid=np.zeros(self.n,dtype=np.int16)
        pk=[]; pos=0
        for k,p in enumerate(pages_idx):
            ps[pos]=1; pid[pos:pos+len(p)]=k; pk.append(pos+8*k); pos+=len(p)
        self.ps=ps; self.pid=pid; self.npages=len(pages_idx)
        self.pkoff=np.array([sum(len(q)+8 for q in pages_idx[:k]) for k in range(len(pages_idx))],dtype=np.int32)
        self.KLP=int(sum(len(q)+8 for q in pages_idx))
REAL=Corpus([p['idx'] for p in U])
def shuffled(corp, seed):
    rng=random.Random(seed)
    pg=[]
    for p in corp.pages:
        q=list(p); rng.shuffle(q); pg.append(q)
    return Corpus(pg)

def shuffled_D(corp, seed):
    """shuffle the chain increments D_i within each page, rebuild c by cumulative sum (preserves the D multiset: doublet deficit, EA rate)"""
    rng=random.Random(seed); pg=[]
    for p in corp.pages:
        D=[]; prev=0
        for x in p: D.append((x-prev)%29); prev=x
        rng.shuffle(D); c=[]; prev=0
        for d in D: prev=(prev+d)%29; c.append(prev)
        pg.append(c)
    return Corpus(pg)

# ---------------- tables
def primroots(p=29):
    out=[]
    for g in range(2,p):
        x=1; seen=set()
        for _ in range(p-1):
            x=x*g%p; seen.add(x)
        if len(seen)==p-1: out.append(g)
    return out
PR=primroots()   # 12
def dlog_table(g):
    t={}; x=1
    for e in range(28):
        t[x]=e; x=x*g%29
    return t
def build_apps(roots):
    """returns list of dict(name,tab(841 uint8),q,prev,conv)"""
    apps=[]
    def mk(name,fn,q,prev):
        T=np.zeros(841,dtype=np.uint8)
        for D in range(29):
            for k in range(29):
                T[D*29+k]=fn(D,k) if (k<q) else 0
        return (name,T,q,prev)
    defs=[]
    for s in (1,-1):
        defs.append(mk('chainadd%+d'%s, lambda D,k,s=s: 28 if D==0 else ((D-1)-s*k)%28, 28, 1))
    for inv in (0,1):
        def f(D,k,inv=inv):
            if D==0: return 28
            K=k+1
            if inv: K=pow(K,-1,29)
            return (D*K%29)-1
        defs.append(mk('gflin%s'%('mul' if not inv else 'div'), f, 28,1))
    for g in roots:
        lg=dlog_table(g)
        for s in (1,-1):
            defs.append(mk('gflog_g%d%+d'%(g,s), lambda D,k,lg=lg,s=s: 28 if D==0 else (lg[D]-s*k)%28, 28,1))
    for conv in (0,1):
        for (name,T,q,prev) in defs:
            apps.append(dict(name=name+('|convY' if conv else '|convX'),tab=T,q=q,prev=prev,conv=conv))
    for s in (1,-1):
        T=np.zeros(841,dtype=np.uint8)
        for D in range(29):
            for k in range(29): T[D*29+k]=(D-s*k)%29
        apps.append(dict(name='otp%+d'%s,tab=T,q=29,prev=0,conv=0))
    return apps
ROOTS=tuple(int(x) for x in os.environ.get('LANEB_ROOTS','2,3').split(','))
APPS=build_apps(ROOTS)
APP_TABS=np.concatenate([a['tab'] for a in APPS]).astype(np.uint8)
APP_Q=np.array([a['q'] for a in APPS],dtype=np.uint8)
APP_PREV=np.array([a['prev'] for a in APPS],dtype=np.uint8)
APP_CONV=np.array([a['conv'] for a in APPS],dtype=np.uint8)
NAPPS=len(APPS)

# ---------------- mappings: byte stream -> key arrays
MAPS=[('byte_mod28',28),('byte_rej28',28),('nib28',28),('bits5_mod28',28),('bits5_rej28',28),('hexascii_mod28',28),
      ('b28dig_lsd',28),('b28dig_msd',28),('b29dig_mod28_lsd',28),('b29dig_rej28_lsd',28),('b29dig_mod28_msd',28),('b29dig_rej28_msd',28),
      ('byte_mod29',29),('byte_rej29',29),('nib29',29),('bits5_mod29',29),('bits5_rej29',29),('hexascii_mod29',29),
      ('b29dig_lsd',29),('b29dig_msd',29)]
NMAPS=len(MAPS)
MAP_Q=np.array([q for _,q in MAPS],dtype=np.uint8)
NTR=NMAPS*NAPPS*3

def _digits(data, blocklen, base):
    nb=len(data)//blocklen
    ndig_floor=int(math.floor(8*blocklen/math.log2(base)))
    ndig_ceil=int(math.ceil(8*blocklen/math.log2(base)))+1
    arr=np.frombuffer(data[:nb*blocklen],dtype=np.uint8).copy()
    out=np.zeros(nb*ndig_ceil,dtype=np.uint8); nsig=np.zeros(nb,dtype=np.uint8)
    lib.digits_blocks(P(arr),blocklen,nb,base,ndig_ceil,P(out),P(nsig))
    out=out.reshape(nb,ndig_ceil)
    lsd=out[:,:ndig_floor].ravel()
    rev=out[:,::-1]
    keep=(np.arange(ndig_ceil)[None,:] >= (ndig_ceil-nsig.astype(int))[:,None])
    msd=rev[keep]
    return lsd,msd

def make_keys(data, blocklen, KL):
    """data: bytes; returns dict name-> uint8 array of exactly KL (padded with 0)"""
    b=np.frombuffer(data,dtype=np.uint8)
    res={}
    def put(name,arr):
        a=np.zeros(KL,dtype=np.uint8); m=min(KL,len(arr)); a[:m]=arr[:m]; res[name]=a
    put('byte_mod28', b%28); put('byte_mod29', b%29)
    put('byte_rej28', (b[b<252])%28); put('byte_rej29', (b[b<232])%29)
    nib=np.empty(len(b)*2,dtype=np.uint8); nib[0::2]=b>>4; nib[1::2]=b&15
    put('nib28',nib); put('nib29',nib)
    # bits5
    bits=np.unpackbits(b)
    ng=len(bits)//5
    v=(bits[:ng*5].reshape(ng,5).astype(np.uint16)*np.array([16,8,4,2,1],dtype=np.uint16)).sum(axis=1).astype(np.uint8)
    put('bits5_mod28',v%28); put('bits5_mod29',v%29); put('bits5_rej28',v[v<28]); put('bits5_rej29',v[v<29])
    hx=np.frombuffer(data.hex().encode(),dtype=np.uint8)
    put('hexascii_mod28',hx%28); put('hexascii_mod29',hx%29)
    l28,m28=_digits(data,blocklen,28); l29,m29=_digits(data,blocklen,29)
    put('b28dig_lsd',l28); put('b28dig_msd',m28)
    put('b29dig_mod28_lsd',l29%28); put('b29dig_rej28_lsd',l29[l29<28]); put('b29dig_mod28_msd',m29%28); put('b29dig_rej28_msd',m29[m29<28])
    put('b29dig_lsd',l29); put('b29dig_msd',m29)
    return res

def keyarray(res, KL):
    return np.ascontiguousarray(np.stack([res[n] for n,_ in MAPS]))

# ---------------- sweep call
def run_sweep(corp, keys, KL, koff=0, modes=3, pkoff=None, pmax=None, pmaxcfg=None, cfg_base=0, hist=None):
    ow=np.empty(NTR,dtype=np.float32); op=np.empty(NTR,dtype=np.float32)
    if pmax is None: pmax=np.zeros(corp.npages,dtype=np.float32); pmaxcfg=np.zeros(corp.npages,dtype=np.int64)
    if pkoff is None: pkoff=np.zeros(corp.npages,dtype=np.int32)
    lib.sweep(P(corp.c),P(corp.ps),P(corp.pid),corp.n,corp.npages,P(keys),KL,NMAPS,P(MAP_Q),
              P(APP_TABS),NAPPS,P(APP_Q),P(APP_PREV),P(APP_CONV),koff,3000,modes,P(pkoff),
              P(ow),P(op),P(pmax),P(pmaxcfg),ctypes.c_int64(cfg_base),
              (P(hist) if hist is not None else None), ctypes.c_float(0.9),ctypes.c_float(0.002),1000)
    return ow,op,pmax,pmaxcfg

def decode_cfg(corp, keyvec, app_i, mode, koff=0, pkoff=None):
    out=np.empty(corp.n,dtype=np.uint8)
    if pkoff is None: pkoff=np.zeros(corp.npages,dtype=np.int32)
    a=APPS[app_i]
    kv=np.ascontiguousarray(keyvec)
    lib.decode_one(P(corp.c),P(corp.ps),P(corp.pid),corp.n,P(kv),len(kv),P(a['tab']),a['prev'],a['conv'],koff,mode,P(pkoff),P(out))
    return out

def trial_decode(t):
    m,rest=divmod(t,NAPPS*3); a,md=divmod(rest,3)
    return m,a,md

# ---------------- quadgram scoring
QG=None
def load_qg():
    global QG
    if QG is not None: return QG
    d={}; tot=0
    for line in open(SCRATCH+'/dl/dukotah/liber-primus/data/english_quadgrams.txt'):
        w,c=line.split(); d[w]=int(c); tot+=int(c)
    arr=np.full(26**4, math.log10(0.01/tot),dtype=np.float32)
    for w,c in d.items():
        if len(w)==4 and w.isalpha():
            i=0
            for ch in w.upper(): i=i*26+ord(ch)-65
            arr[i]=math.log10(c/tot)
    QG=arr; return QG
def text_of(p):
    return ''.join(TR[x] for x in p)
def qscore(p, limit=None):
    arr=load_qg()
    t=text_of(p[:limit] if limit else p)
    v=np.frombuffer(t.encode(),dtype=np.uint8).astype(np.int64)-65
    if len(v)<4: return -99
    idx=((v[:-3]*26+v[1:-2])*26+v[2:-1])*26+v[3:]
    return float(arr[idx].mean())
