import numpy as np, itertools
import core
TRL1=np.array([ord(t[0])-65 for t in core.TR]); TRL2=np.array([ord(t[1])-65 if len(t)>1 else -1 for t in core.TR])

def runes_to_letters(r):
    r=np.asarray(r)%29
    a=TRL1[r]; b=TRL2[r]
    out=np.empty(2*len(r),dtype=np.int64); out[0::2]=a; out[1::2]=b
    return out[out>=0]

def map_variants(v, tag, signs=(1,-1), s26=True, s29=True):
    """yield (label, letters) for alphabet maps of integer value stream v"""
    v=np.asarray(v,dtype=np.int64)
    if s26:
        for sg in signs:
            for s in range(26):
                yield '%s|A26 %s%d'%(tag,'+' if sg>0 else '-',s), (sg*v+s)%26
    if s29:
        for sg in signs:
            for s in range(29):
                yield '%s|R29 %s%d'%(tag,'+' if sg>0 else '-',s), runes_to_letters((sg*v+s)%29)

def ascii_letters(v):
    v=np.asarray(v,dtype=np.int64)
    pr=float(((v>=32)&(v<127)).mean()) if len(v) else 0.0
    up=np.where((v>=97)&(v<=122),v-32,v)
    m=(up>=65)&(up<=90)
    return (up[m]-65), pr

# ITA2 Baudot LTRS
_ITA=['', 'E','\n','A',' ','S','I','U','\r','D','R','J','N','F','C','K','T','Z','L','W','H','Y','P','Q','O','B','G','F!','M','X','V','L!']
ITA_L=np.array([ord(c)-65 if len(c)==1 and 'A'<=c<='Z' else -1 for c in _ITA])
def baudot_letters(v):
    v=np.asarray(v,dtype=np.int64)
    n=len(v); idx=np.arange(n)
    fig=np.where(v==27,idx,-1); ltr=np.where(v==31,idx,-1)
    lf=np.maximum.accumulate(fig); ll=np.maximum.accumulate(ltr)
    inltrs=ll>=lf   # start state LTRS (both -1 -> True)
    L=ITA_L[v]
    return L[inltrs&(L>=0)]

MORSE={'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..'}
MINV={v:ord(k)-65 for k,v in MORSE.items()}
def morse_letters(sym):
    """sym: array of 0=dot 1=dash 2=gap"""
    out=[]; cur=[]
    for s in sym.tolist():
        if s==2:
            if cur:
                m=MINV.get(''.join('.' if c==0 else '-' for c in cur))
                if m is not None: out.append(m)
                cur=[]
        else:
            cur.append(s)
            if len(cur)>5: cur=[]  # overflow: reset (drop)
    if cur:
        m=MINV.get(''.join('.' if c==0 else '-' for c in cur))
        if m is not None: out.append(m)
    return np.array(out,dtype=np.int64)

def bit_decoders(b, tag):
    """b: 0/1 array. yields (label, letters, printable_frac or None)"""
    b=np.asarray(b,dtype=np.int64)
    for dirn in ('f','r'):
        bd=b if dirn=='f' else b[::-1]
        for inv in (0,1):
            bb=bd^inv
            for g in (5,7,8):
                for o in range(g):
                    n=(len(bb)-o)//g
                    if n<8: continue
                    M=bb[o:o+n*g].reshape(n,g)
                    for order in ('msb','lsb'):
                        W=(1<<np.arange(g-1,-1,-1)) if order=='msb' else (1<<np.arange(g))
                        v=M@W
                        lab='%s|bits%s g%d o%d %s inv%d'%(tag,dirn,g,o,order,inv)
                        if g==5:
                            m=(v>=1)&(v<=26)
                            yield lab+' a1z26', v[m]-1, None
                            yield lab+' baudot', baudot_letters(v), None
                        else:
                            L,pr=ascii_letters(v)
                            yield lab+' ascii', L, pr

def group_vals(d,k,g,o,big):
    n=(len(d)-o)//g
    if n<8: return None
    M=d[o:o+n*g].reshape(n,g)
    w=np.array([k**(g-1-j) for j in range(g)] if big else [k**j for j in range(g)],dtype=np.int64)
    return M@w

def morse_variants(x, cuts, tag):
    x=np.asarray(x)
    # three-class: x<=t1 dot, t1<x<=t2 dash, x>t2 gap  ; and gap-short variant: x<=t1 gap, t1<x<=t2 dot, >t2 dash ;  and dot,gap,dash orders
    for t1 in cuts:
        for t2 in cuts:
            if t2<=t1: continue
            for perm,name in (((0,1,2),'dot-dash-gap'),((2,0,1),'gap-dot-dash'),((0,2,1),'dot-gap-dash'),((1,0,2),'dash-dot-gap')):
                cls=np.where(x<=t1,perm[0],np.where(x<=t2,perm[1],perm[2]))
                for d in ('f','r'):
                    c=cls if d=='f' else cls[::-1]
                    yield '%s|morse %s t%d,%d %s'%(tag,name,t1,t2,d), morse_letters(c)

def length_encodings(x, tag, cuts_bits, cuts_morse, full=True):
    """x: integer array channel. yields (label, letters, pr)"""
    x=np.asarray(x,dtype=np.int64)
    # A: raw value maps, both directions
    for d in ('f','r'):
        xx=x if d=='f' else x[::-1]
        for lab,L in map_variants(xx,tag+'|raw'+d): yield lab,L,None
    if not full: return
    # B: mod-k digit groups
    for k in range(3,11):
        d=x%k
        gs=[g for g in range(2,9) if 25<=k**g<=1100]
        for g in gs:
            for big in (True,False):
                for o in range(g):
                    v=group_vals(d,k,g,o,big)
                    if v is None: continue
                    t='%s|mod%d g%d o%d %s'%(tag,k,g,o,'BE' if big else 'LE')
                    for lab,L in map_variants(v,t): yield lab,L,None
                    if k**g>=64 and k**g<=256:
                        for off in (0,32):
                            L,pr=ascii_letters(v+off); yield t+'|ascii+%d'%off,L,pr
    # C: pairs / triples base N
    xm=x-x.min()
    for N in (10,12,14,15,16,26,29):
        for g in (2,3):
            for o in range(g):
                n=(len(x)-o)//g
                if n<8: continue
                M=xm[o:o+n*g].reshape(n,g) if N==14 else x[o:o+n*g].reshape(n,g)
                w=np.array([N**(g-1-j) for j in range(g)],dtype=np.int64)
                v=M@w
                t='%s|base%d g%d o%d'%(tag,N,g,o)
                for lab,L in map_variants(v,t): yield lab,L,None
                L,pr=ascii_letters(v); yield t+'|ascii',L,pr
    # D: bits
    bitstreams=[('par',x&1)]+[('gt%d'%c,(x>c).astype(np.int64)) for c in cuts_bits]
    for nm,b in bitstreams:
        for lab,L,pr in bit_decoders(b,'%s|%s'%(tag,nm)): yield lab,L,pr
    # E: morse
    for lab,L in morse_variants(x,cuts_morse,tag): yield lab,L,None

def rune_encodings(v, tag):
    """rune-value streams (0..28)"""
    v=np.asarray(v,dtype=np.int64)
    dv=(np.diff(v))%29
    for d in ('f','r'):
        for nm,s in (('val',v),('inc',dv)):
            ss=s if d=='f' else s[::-1]
            for lab,L in map_variants(ss,'%s|%s%s'%(tag,nm,d)): yield lab,L,None
    for nm,b in (('par',v&1),('ge14',(v>=14).astype(np.int64))):
        for lab,L,pr in bit_decoders(b,'%s|%s'%(tag,nm)): yield lab,L,pr
    for k in (3,4,5):
        d=v%k
        for g in [g for g in range(2,6) if 25<=k**g<=130]:
            for big in (True,False):
                for o in range(g):
                    vv=group_vals(d,k,g,o,big)
                    if vv is None: continue
                    for lab,L in map_variants(vv,'%s|mod%d g%d o%d %s'%(tag,k,g,o,'BE' if big else 'LE')): yield lab,L,None

def bit_channel_encodings(b, tag):
    for lab,L,pr in bit_decoders(b,tag): yield lab,L,pr
    # run-length (unary) decode to values then maps handled elsewhere

def stat_vec(gen):
    labs=[]; rows=[]; prs=[]
    for lab,L,pr in gen:
        st=core.letter_stats(np.asarray(L,dtype=np.int64))
        labs.append(lab); rows.append([st['Qall'],st['Qwin'],st['IoC'],st['Hall'],st['Hwin'],st['n']]); prs.append(-1.0 if pr is None else pr)
    return labs,np.array(rows),np.array(prs)

# ---- stateless Baudot family (shift codes ignored, always LTRS table): added after the planted control showed the stateful decoder
# loses a message whose predecessor bits happened to contain code 27 (FIGS).
def bdt_decoders(b, tag):
    b=np.asarray(b,dtype=np.int64)
    for dirn in ('f','r'):
        bd=b if dirn=='f' else b[::-1]
        for inv in (0,1):
            bb=bd^inv; g=5
            for o in range(g):
                n=(len(bb)-o)//g
                if n<8: continue
                M=bb[o:o+n*g].reshape(n,g)
                for order in ('msb','lsb'):
                    Wt=(1<<np.arange(g-1,-1,-1)) if order=='msb' else (1<<np.arange(g))
                    v=M@Wt; L=ITA_L[v]
                    yield '%s|bdt%s o%d %s inv%d'%(tag,dirn,o,order,inv), L[L>=0], None
def bdt_encodings(kind, data, tag, cb=None):
    if kind=='len':
        x=np.asarray(data,dtype=np.int64)
        streams=[('par',x&1)]+[('gt%d'%c,(x>c).astype(np.int64)) for c in cb]
    elif kind=='rune':
        v=np.asarray(data,dtype=np.int64); streams=[('par',v&1),('ge14',(v>=14).astype(np.int64))]
    else: streams=[('bit',np.asarray(data))]
    for nm,b in streams:
        for lab,L,pr in bdt_decoders(b,'%s|%s'%(tag,nm)): yield lab,L,pr
