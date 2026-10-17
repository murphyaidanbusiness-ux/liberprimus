import sys, json, time
sys.path.insert(0,'.')
import numpy as np, multiprocessing as mp
import eng, ctrl, fam_self as FSELF, fam_solved as FS
from eng import PRIMES
def find(d0,label,form):
    return [s for s in FSELF.specs(d0) if s['label']==label and s['form']==form][0]
def enc_online(kind,p,st,o,rng,form):
    """sequential encryption for self-keyed key sequences. returns c"""
    n=len(p); sigma=eng.rand_sigma(rng, form in (2,3))
    inv=np.array([0]+[pow(a,-1,29) for a in range(1,29)])
    c=np.zeros(n,dtype=np.int64); c[0]=11
    cum=np.zeros(n,dtype=np.int64); cum[0]=PRIMES[c[0]]
    wsum={}  # word -> sum primes of cipher so far
    word=st.word
    wsum_done={}
    wsum[word[0]]=PRIMES[c[0]]
    for r in range(1,n):
        # key value
        if kind=='r.prime': j=r+o; kv=PRIMES[c[j]] if j>=0 else 0
        elif kind=='r.cumprime': j=r+o; kv=cum[j] if j>=0 else 0
        elif kind=='w.sum':
            wj=word[r]+o; kv=wsum[wj] if wj>=0 else 0   # word wj < current word => complete
        if form in (0,1):
            k=kv%28 if True else 0
        # apply reduction according to label: m28 for r.prime, m29 for the other two
        if kind=='r.prime': k=kv%28
        else: k=kv%29
        pp=p[r]
        if pp==28: D=0
        elif form==0: D=1+((sigma[pp]+k)%28)
        elif form==1: D=1+((sigma[pp]-k)%28)
        elif form==2:
            kk=1 if k%29==0 else k%29; D=(sigma[pp]*kk)%29
        else:
            kk=1 if k%29==0 else k%29; D=(sigma[pp]*inv[kk])%29
        c[r]=(c[r-1]+D)%29
        cum[r]=cum[r-1]+PRIMES[c[r]]
        wsum[word[r]]=wsum.get(word[r],0)+PRIMES[c[r]]
    return c
PLANTS=[
 ('SELF:r.pos_in_word|rev0|m28',0,0,'std'),
 ('SELF:l.len|rev0|m29',3,2,'std'),
 ('SELF:p.sum|rev0|m28',1,0,'std'),
 ('SELF:dbl.gap_cyc|rev0|m28',0,20,'std'),
 ('SELF:r.prime|rev0|m28',0,-3,'online'),
 ('SELF:r.cumprime|rev0|m29',1,-1,'online'),
 ('SELF:w.sum|rev0|m29',2,-1,'online'),
 ('SELF:w.sum|rev0|m29',3,-2,'online'),
 ('RAW-SELF:r.prime|rev0|m29',4,-7,'rawstd'),
]
def task(a):
    label,form,o,kind=a
    rng=np.random.default_rng(abs(hash((label,form,o)))%2**32)
    words,p,st=ctrl.synth_plain(start=9000+13*abs(o))
    d0=ctrl.dummy_data(p,st)
    if kind=='std':
        sp=find(d0,label,form); c=ctrl.encrypt_with_spec(sp,p,o,rng)
    elif kind=='rawstd':
        # raw shift with key = prime of ciphertext rune at lag: online: c_r = p_r + PRIMES[c_{r+o}] mod 29
        n=len(p); c=np.zeros(n,dtype=np.int64); c[0]=p[0]
        for r in range(1,n):
            j=r+o; kv=PRIMES[c[j]]%29 if j>=0 else 0
            c[r]=(p[r]+kv)%29
    else:
        c=enc_online(label.split(':')[1].split('|')[0],p,st,o,rng,form)
    d1=eng.Data(c,st)
    res=FS.run_specs(FSELF.specs(d1))
    top=sorted(res.items(),key=lambda kv:-kv[1][0])[:3]
    pl=res.get(label)
    others=[v[0] for k,v in res.items() if k!=label]
    return dict(label=label,form=form,o=o,kind=kind,planted=pl,top=top,max_other=max(others),med_other=float(np.median(others)))
if __name__=='__main__':
    with mp.Pool(3) as pool: out=pool.map(task,PLANTS)
    json.dump(out,open('ctrl_self.json','w'),indent=1)
    for r in out: print(r['label'],'form',r['form'],'planted o=',r['o'],'->',r['planted'],'| max other z=%.1f'%r['max_other'],'| top:',r['top'][0][0],round(r['top'][0][1][0],1))
