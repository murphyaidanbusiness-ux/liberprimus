import numpy as np, re, json, pickle, sys, time
import core, channels as ch
from multiprocessing import Pool
S=core.S
sr=open(core.DK+'/keys/self_reliance.txt',encoding='utf-8',errors='ignore').read()
sr=re.sub(r'\[\d+\]','',sr)
SRW=re.findall(r"[A-Za-z]+",sr.replace("'",""))
SRW=[w.upper() for w in SRW]
SRL=np.array([ord(c)-65 for c in ''.join(SRW)])
d=json.load(open(core.DK+'/../SOLVED-PAGES.json'))
LP1=''.join(p['plaintext_transliteration'] for p in d['pages'])
LP1L=np.array([ord(c)-65 for c in LP1])
# LP1 word list not available (no spaces): letter-level only
TEXTS={'SR':(SRW,SRL),'LP1':(None,LP1L)}
def enc_book(nums, tag):
    nums=np.asarray(nums,dtype=np.int64)
    for tn,(words,letters) in TEXTS.items():
        nl=len(letters)
        for off in (-1,0,1,2):
            for md in ('mod','clip'):
                idx=nums+off
                idx=idx%nl if md=='mod' else idx
                if md=='clip' and ((idx<0)|(idx>=nl)).any(): ok=(idx>=0)&(idx<nl); idx=idx[ok]
                yield '%s|%s letter#n%+d %s'%(tag,tn,off,md), letters[idx], None
        # cumulative pointer
        cs=np.cumsum(nums)
        for off in (-1,0,1):
            yield '%s|%s letter#cum%+d'%(tag,tn,off), letters[(cs+off)%nl], None
        # pairs (a,b): a-th chunk? letter at a*? : use (a,b) -> letter index a*... skip; pair sum / product
        for o in (0,1):
            n=(len(nums)-o)//2
            a=nums[o:o+2*n:2]; b=nums[o+1:o+2*n:2]
            yield '%s|%s letter#a+b o%d'%(tag,tn,o), letters[(a+b)%nl], None
            yield '%s|%s letter#a*b o%d'%(tag,tn,o), letters[(a*b)%nl], None
        if words is not None:
            nw=len(words)
            first=np.array([ord(w[0])-65 for w in words]); last=np.array([ord(w[-1])-65 for w in words])
            for off in (-1,0,1,2):
                idx=(nums+off)%nw
                yield '%s|%s word#n%+d first'%(tag,tn,off), first[idx], None
                yield '%s|%s word#n%+d last'%(tag,tn,off), last[idx], None
            cs=np.cumsum(nums)
            yield '%s|%s word#cum first'%(tag,tn), first[cs%nw], None
            yield '%s|%s word#cum last'%(tag,tn), last[cs%nw], None
            for o in (0,1):
                n=(len(nums)-o)//2
                a=nums[o:o+2*n:2]; b=nums[o+1:o+2*n:2]
                # word a, letter b
                out=[]
                for aa,bb in zip(a,b):
                    w=words[aa%nw]; out.append(ord(w[bb%len(w)])-65)
                yield '%s|%s word a letter b o%d'%(tag,tn,o), np.array(out), None
                out=[]
                for aa,bb in zip(a,b):
                    w=words[(aa*7+bb)%nw]; out.append(ord(w[0])-65)
                # (placeholder variant: para/word style) 
def evalb(nums,tag):
    import enc
    return enc.stat_vec(enc_book(nums,tag))
CHS={'SW':ch.sw,'SR':ch.slen_r,'CHw':ch.cw,'CHr':ch.clen_r,'LR':ch.llen,'Wfirst400':ch.wlen[:400]}
def job(a):
    name,seed=a
    rng=np.random.default_rng(777+seed)
    labs,rows,prs=evalb(rng.permutation(CHS[name]),name)
    return rows[:,:5].astype(np.float32)
if __name__=='__main__':
    nrep=int(sys.argv[1])
    for name in CHS:
        labs,rows,prs=evalb(CHS[name],name)
        with Pool(4) as p: nulls=p.map(job,[(name,s) for s in range(nrep)],chunksize=8)
        pickle.dump(dict(labs=labs,real=rows,prs=prs,nulls=np.stack(nulls)),open('out_BK_%s.pkl'%name,'wb')); print(name,len(labs),flush=True)
