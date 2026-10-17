"""Family (d): keystreams from the unsolved book's own structure and from its own ciphertext (self-keyed by numbers)."""
import numpy as np
import eng, seqs
from eng import PRIMES, scan
R=500
def self_seqs(d):
    st=d.st; n=d.n; c=d.c
    pv=PRIMES[c]
    out={}
    # rune-level (len n) aligned to rune index
    out['r.prime']=('r',pv); out['r.totient']=('r',pv-1); out['r.index']=('r',c.copy())
    out['r.cumprime']=('r',np.cumsum(pv)); out['r.cumindex']=('r',np.cumsum(c))
    pw=d._pos(st.word); out['r.pos_in_word']=('r',pw)
    out['r.wordlen']=('r',d.wlen_all[st.word]); 
    out['r.pos_in_line']=('r',d._pos(st.line)); out['r.pos_in_page']=('r',d._pos(st.page))
    out['r.wordsum_cur']=('r',d.wsum[st.word])
    # word-level
    wl=d.wlen_all; ws=d.wsum
    wi=np.zeros(d.nw,dtype=np.int64)  # sum of rune indices
    np.add.at(wi,st.word,c)
    firstp=np.zeros(d.nw,dtype=np.int64); lastp=np.zeros(d.nw,dtype=np.int64)
    first_pos=np.zeros(d.nw,dtype=np.int64)
    for i in range(n-1,-1,-1): first_pos[st.word[i]]=i
    last_pos=np.zeros(d.nw,dtype=np.int64)
    for i in range(n): last_pos[st.word[i]]=i
    out['w.len']=('w',wl); out['w.sum']=('w',ws); out['w.totient']=('w',np.array([seqs.totient(int(x)) for x in ws]))
    out['w.pi']=('w',seqs.PI[ws].astype(np.int64)); out['w.primeidx']=('w',PRIMES[ws%29]); out['w.idxsum']=('w',wi)
    out['w.cumsum']=('w',np.cumsum(ws)); out['w.first']=('w',PRIMES[c[first_pos]]); out['w.last']=('w',PRIMES[c[last_pos]])
    out['w.cumlen']=('w',np.cumsum(wl)); out['w.in_page']=('w',d.word_in_page)
    # line-level
    nl=st.line.max()+1; ll=np.bincount(st.line,minlength=nl)
    lsum=np.bincount(st.line,weights=pv,minlength=nl).astype(np.int64)
    lw=np.zeros(nl,dtype=np.int64); 
    for w in range(d.nw): pass
    out['l.len']=('l',ll); out['l.sum']=('l',lsum); out['l.cumsum']=('l',np.cumsum(lsum)); out['l.id']=('l',np.arange(nl))
    # page-level
    npg=st.page.max()+1; pl=np.bincount(st.page,minlength=npg); psum=np.bincount(st.page,weights=pv,minlength=npg).astype(np.int64)
    out['p.len']=('p',pl); out['p.sum']=('p',psum); out['p.id']=('p',np.arange(npg)); out['p.cumlen']=('p',np.cumsum(pl))
    # doublets
    dpos=np.nonzero(d.D==0)[0]+1
    gaps=np.diff(dpos)
    out['dbl.pos_cyc']=('dbl_cyc',dpos); out['dbl.gap_cyc']=('dbl_cyc',gaps)
    out['dbl.count_gap']=('dbl_cnt',gaps); out['dbl.count_pos']=('dbl_cnt',dpos)
    return out

def reduce(a,red): return (a % (28 if red=='m28' else 29)).astype(np.uint8)
FORMS={'m28':[0,1],'m29':[0,1,2,3]}
def specs(d, include_raw=True):
    S=self_seqs(d)
    m=d.m
    for name,(lvl,arr) in S.items():
        for rev in (0,1):
            a=arr[::-1].copy() if rev else arr
            if lvl=='r': idx=(np.arange(m)+1); cyc=0; omin,omax=-R,R
            elif lvl=='w': idx=d.word.copy(); cyc=0; omin,omax=-R,R
            elif lvl=='l': idx=d.line.copy(); cyc=0; omin,omax=-R,R
            elif lvl=='p': idx=d.page.copy(); cyc=0; omin,omax=-R,R
            elif lvl=='dbl_cyc': idx=np.arange(m)+1; cyc=1; omin,omax=0,len(a)-1
            elif lvl=='dbl_cnt':
                # key index = number of doublets seen so far (changes at each doublet)
                idx=np.cumsum(d.D==0)-1; idx=np.maximum(idx,0); cyc=0; omin,omax=-R,R
                if len(a)<m: pass
            if rev and lvl in 'rwlp': idx=len(a)-1-idx
            idx=idx.astype(np.int32)
            for red in ('m28','m29'):
                K=reduce(a,red)
                for form in FORMS[red]:
                    yield dict(label=f'SELF:{name}|rev{rev}|{red}',form=form,X=d.D,idx=idx,K=K,cyc=cyc,omin=omin,omax=omax,rm=0)
    if include_raw:
        X=d.c[1:].astype(np.uint8)
        for name in ('r.prime','r.index','r.cumprime','r.pos_in_word','r.wordlen','r.wordsum_cur'):
            lvl,arr=S[name]
            for rev in (0,1):
                a=arr[::-1].copy() if rev else arr
                idx=(np.arange(d.m)+1); 
                if rev: idx=len(a)-1-idx
                K=reduce(a,'m29')
                for form in (4,5):
                    for (o1,o2) in ((-R,-1),(1,R)):
                        yield dict(label=f'RAW-SELF:{name}|rev{rev}|m29',form=form,X=X,idx=idx.astype(np.int32),K=K,cyc=0,omin=o1,omax=o2,rm=0)
