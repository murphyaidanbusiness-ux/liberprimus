import sys, ctypes, os, math, random, pickle
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
S='.'
sys.path.insert(0,S+'/lp'); sys.path.insert(0,HERE)
import lpdata, translit
PRIMES=np.array(lpdata.PRIMES); TR=lpdata.TR
lib=ctypes.CDLL(HERE+'/libscan.so')
lib.scan.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
lib.condcoinc.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
def _p(a): return a.ctypes.data

def scan(X,idx,K,cyc,omin,omax,form,rm=0):
    X=np.ascontiguousarray(X,dtype=np.uint8); idx=np.ascontiguousarray(idx,dtype=np.int32); K=np.ascontiguousarray(K,dtype=np.uint8)
    no=omax-omin+1
    ioc=np.zeros(no); nv=np.zeros(no,dtype=np.int32)
    lib.scan(_p(X),_p(idx),len(X),_p(K),len(K),int(cyc),omin,omax,form,rm,_p(ioc),_p(nv))
    return ioc,nv

def condcoinc(X,V):
    """pooled within-group coincidence of nonzero X grouped by V (V<0 skipped); returns (rate, pairs)"""
    X=np.ascontiguousarray(X,dtype=np.uint8); V=np.ascontiguousarray(V,dtype=np.int32)
    c=ctypes.c_double(); p=ctypes.c_double()
    lib.condcoinc(_p(X),_p(V),len(X),int(V.max()) if len(V) else 0,ctypes.byref(c),ctypes.byref(p))
    return (c.value/p.value if p.value>0 else float('nan')), p.value

def contiguous(a):
    u,inv=np.unique(a,return_inverse=True); return inv.astype(np.int64)

class Struct:
    """per-rune page/word/line ids (length n)"""
    def __init__(self,page,word,line):
        self.page=contiguous(np.asarray(page)); self.word=contiguous(np.asarray(word)); self.line=contiguous(np.asarray(line))
        self.n=len(self.page)
def real_struct():
    U,C,sha=lpdata.unsolved()
    page=[];word=[];line=[]
    for p in U:
        page+= [p['page']]*len(p['idx']); word+=p['word']; line+=p['line']
    return Struct(page,word,line), np.array(C,dtype=np.int64)

class Data:
    """chain data: c (n runes), struct; D aligned to runes 1..n-1"""
    def __init__(self,c,st):
        self.c=np.asarray(c,dtype=np.int64); self.st=st; n=len(c); self.n=n
        self.D=((self.c[1:]-self.c[:-1])%29).astype(np.uint8)
        self.m=n-1
        self.page=st.page[1:]; self.word=st.word[1:]; self.line=st.line[1:]
        # position within page / word
        self.pos_page=self._pos(st.page)[1:]
        self.pos_word=self._pos(st.word)[1:]
        self.pos_line=self._pos(st.line)[1:]
        self.wlen_all=np.bincount(st.word)
        self.wlen=self.wlen_all[st.word][1:]
        self.nw=st.word.max()+1
        # word index within page
        wp=np.zeros(self.nw,dtype=np.int64); first_page_word={}
        wpage=np.zeros(self.nw,dtype=np.int64); wpage[st.word]=st.page
        self.wpage=wpage
        cnt=0; prev=-1; widx=np.zeros(self.nw,dtype=np.int64)
        for w in range(self.nw):
            if wpage[w]!=prev: cnt=0; prev=wpage[w]
            widx[w]=cnt; cnt+=1
        self.word_in_page=widx; self.wip=widx[st.word][1:]
        # ciphertext word prime sums (current-word and per-word array)
        pv=PRIMES[self.c]
        self.wsum=np.bincount(st.word,weights=pv,minlength=self.nw).astype(np.int64)
        self.wsum_rune=self.wsum[st.word][1:]
        self.nz=(self.D!=0)
    def _pos(self,ids):
        # position of rune within its group (ids contiguous nondecreasing)
        pos=np.zeros(len(ids),dtype=np.int64)
        start=0
        for i in range(1,len(ids)):
            if ids[i]!=ids[i-1]: start=i
            pos[i]=i-start
        return pos
    # ---- idx builders: key index per position (aligned to D) ----
    def idx_rune(self,mode,conv):
        """mode 'cont'|'page'; conv 'A' (zero increment does not consume) | 'B' (consumes)"""
        if mode=='cont':
            if conv=='B': return np.arange(self.m,dtype=np.int32)
            cs=np.cumsum(self.nz)-1
            r=cs.astype(np.int32); r[~self.nz]=-1; return r
        else:
            if conv=='B': return self.pos_page.astype(np.int32)
            # count of nonzero before within page
            r=np.zeros(self.m,dtype=np.int32); cnt=0; prev=-1
            for i in range(self.m):
                if self.page[i]!=prev: cnt=0; prev=self.page[i]
                if self.nz[i]: r[i]=cnt; cnt+=1
                else: r[i]=-1
            return r
    def idx_word(self,mode):
        return (self.word if mode=='cont' else self.wip).astype(np.int32)

def shuffle_data(d,rng):
    """chain-consistent null: permute the increments (all D incl. zeros), rebuild c; structure kept"""
    Dfull=np.concatenate([[0],d.D.astype(np.int64)])  # D[0]=0 placeholder for rune 0
    perm=rng.permutation(len(d.D))
    Dn=d.D[perm].astype(np.int64)
    c=np.zeros(d.n,dtype=np.int64); c[0]=d.c[0]
    c[1:]=(c[0]+np.cumsum(Dn))%29
    return Data(c,d.st)
def shuffle_raw(d,rng):
    c=d.c.copy(); rng.shuffle(c); return Data(c,d.st)

# ---------- synthetic plaintext / chain encryption for positive controls ----------
def english_plain(path_text, nrunes, start=0):
    """returns list of words (rune idx lists) totalling >=nrunes"""
    txt=open(path_text,encoding='utf-8',errors='ignore').read()[start:]
    import re
    words=[]
    tot=0
    for w in re.findall(r"[A-Za-z]+",txt):
        iw=translit.word_to_idx(w)
        if not iw: continue
        words.append(iw); tot+=len(iw)
        if tot>=nrunes: break
    return words
def struct_from_words(words, page_sizes, words_per_line=7):
    page=[];word=[];line=[]
    pi=0;cur=0;lcount=0;lid=0
    for wi,w in enumerate(words):
        for _ in w:
            page.append(pi); word.append(wi); line.append(lid)
        cur+=len(w); lcount+=1
        if lcount>=words_per_line: lid+=1; lcount=0
        if pi<len(page_sizes)-1 and cur>=page_sizes[pi]: pi+=1; cur=0
    return Struct(page,word,line)

def chain_encrypt(p, keyfn_add=None, sigma=None, form='add', c0=0):
    """p: plaintext rune idx array (EA=28 -> zero increment). keys supplied by array k (len n, int) per position.
    form 'add': D=1+((sigma[p]+k)%28) ; 'addm': D=1+((sigma[p]-k)%28); 'mul': D=sigma1[p]*k%29 (k!=0 assumed)."""
    raise NotImplementedError

def enc_chain(p, k, sigma, form):
    p=np.asarray(p); n=len(p)
    D=np.zeros(n,dtype=np.int64)
    ea=(p==28)
    if form=='add': D=1+((sigma[p]+k)%28)
    elif form=='addm': D=1+((sigma[p]-k)%28)
    elif form=='mul': D=(sigma[p]*k)%29
    elif form=='mulinv':
        inv=np.array([0]+[pow(a,-1,29) for a in range(1,29)])
        D=(sigma[p]*inv[k%29])%29
    D=np.where(ea,0,D)
    c=np.zeros(n,dtype=np.int64)
    c[0]=7
    c[1:]=(7+np.cumsum(D[1:]))%29
    return c

def rand_sigma(rng, mult=False):
    if mult:
        s=np.zeros(29,dtype=np.int64); s[:28]=rng.permutation(np.arange(1,29)); s[28]=0; return s
    s=np.zeros(29,dtype=np.int64); s[:28]=rng.permutation(28); s[28]=0; return s
