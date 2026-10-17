import numpy as np, core, enc
Lo=core.layout()
C=Lo['C']; N=len(C)
wst,wlen=core.runs(Lo['word'])
lst,llen=core.runs(Lo['line'])
sst,slen_r=core.runs(Lo['sent'])
pst,plen=core.runs(Lo['page'])
cst,clen_r=core.runs(Lo['chap'])
# words per sentence / chap: distinct word ids
def words_per(ids):
    out=[]
    for s,l in zip(*core.runs(ids)):
        pass
def _wp(ids):
    st,ln=core.runs(ids)
    res=[]
    for a,l in zip(st,ln):
        w=Lo['word'][a:a+l]
        res.append(len(np.unique(w)))
    return np.array(res)
sw=_wp(Lo['sent'])        # words per sentence
lw=_wp(Lo['line'])        # words per line (distinct word ids touching the line)
pw=_wp(Lo['page']); cw=_wp(Lo['chap'])
# partial first / last word segment length per line
def first_last(ids_line):
    st,ln=core.runs(ids_line); F=[];T=[]
    for a,l in zip(st,ln):
        w=Lo['word'][a:a+l]
        f=np.argmax(w!=w[0]) if (w!=w[0]).any() else l
        t=l-(np.flatnonzero(w!=w[-1])[-1]+1) if (w!=w[-1]).any() else l
        F.append(f);T.append(t)
    return np.array(F),np.array(T)
lf,lt=first_last(Lo['line'])
# sentence word counts to rune starts
def sent_starts(swc, wlen_):
    ws=np.concatenate(([0],np.cumsum(wlen_)))   # word start rune index (len nw+1)
    cw_=np.concatenate(([0],np.cumsum(swc)))
    return ws[cw_[:-1]], ws[cw_[1:]]-1
def starts_from_lens(lens):
    s=np.concatenate(([0],np.cumsum(lens)))
    return s[:-1], s[1:]-1

def cuts_of(x,qs):
    c=np.unique(np.quantile(x,qs).astype(int)); c=[int(v) for v in c if (x>v).any() and (x<=v).any()]
    return c

class Ch:
    def __init__(s,name,kind,data,nullf,**kw): s.name=name;s.kind=kind;s.data=data;s.nullf=nullf;s.kw=kw
    def real(s): return s.data
    def null(s,rng): return s.nullf(rng)

def perm(x): return lambda rng: rng.permutation(x)
def mk_len(name,x):
    return Ch(name,'len',np.asarray(x),perm(np.asarray(x)),cb=cuts_of(x,[.2,.3,.4,.5,.6,.7,.8]),cm=cuts_of(x,[.15,.3,.45,.6,.75,.9]))
CH={}
for nm,x in (('W',wlen),('SW',sw),('SR',slen_r),('LR',llen),('LWd',lw),('LF',lf),('LT',lt),('PGr',plen),('PGw',pw),('CHw',cw),('CHr',clen_r)):
    CH[nm]=mk_len(nm,x)
CH['W'].kw['cb']=list(range(1,9)); CH['W'].kw['cm']=list(range(1,10))
# rune streams
def rune_ch(name, getter_real, getter_null):
    return Ch(name,'rune',getter_real, getter_null)
def fw(rng=None, lens=wlen): s,e=starts_from_lens(lens); return C[s]
def lw_(lens=wlen): s,e=starts_from_lens(lens); return C[e]
CH['FW']=Ch('FW','rune',C[starts_from_lens(wlen)[0]],lambda rng:C[starts_from_lens(rng.permutation(wlen))[0]])
CH['LWr']=Ch('LWr','rune',C[starts_from_lens(wlen)[1]],lambda rng:C[starts_from_lens(rng.permutation(wlen))[1]])
CH['FL']=Ch('FL','rune',C[starts_from_lens(llen)[0]],lambda rng:C[starts_from_lens(rng.permutation(llen))[0]])
CH['LLr']=Ch('LLr','rune',C[starts_from_lens(llen)[1]],lambda rng:C[starts_from_lens(rng.permutation(llen))[1]])
s0,e0=sent_starts(sw,wlen)
CH['FS']=Ch('FS','rune',C[s0],lambda rng:C[sent_starts(rng.permutation(sw),wlen)[0]])
CH['LS']=Ch('LS','rune',C[e0],lambda rng:C[sent_starts(rng.permutation(sw),wlen)[1]])
CH['FP']=Ch('FP','rune',C[starts_from_lens(plen)[0]],lambda rng:C[starts_from_lens(rng.permutation(plen))[0]])
CH['LP']=Ch('LP','rune',C[starts_from_lens(plen)[1]],lambda rng:C[starts_from_lens(rng.permutation(plen))[1]])
# second rune of each word / penultimate (extra)
def bnd_bits(lens, n=N):
    b=np.zeros(n-1,dtype=np.int64); b[np.cumsum(lens)[:-1]-1]=1; return b
CH['BW']=Ch('BW','bit',bnd_bits(wlen),lambda rng:bnd_bits(rng.permutation(wlen)))
CH['BL']=Ch('BL','bit',bnd_bits(llen),lambda rng:bnd_bits(rng.permutation(llen)))
def sent_bits(swc):
    b=np.zeros(len(wlen)-1,dtype=np.int64); b[np.cumsum(swc)[:-1]-1]=1; return b
CH['BS']=Ch('BS','bit',sent_bits(sw),lambda rng:sent_bits(rng.permutation(sw)))

def evaluate(ch, data):
    if ch.kind=='len': return enc.stat_vec(enc.length_encodings(data,ch.name,ch.kw['cb'],ch.kw['cm']))
    if ch.kind=='rune': return enc.stat_vec(enc.rune_encodings(data,ch.name))
    if ch.kind=='bit': return enc.stat_vec(enc.bit_channel_encodings(data,ch.name))
