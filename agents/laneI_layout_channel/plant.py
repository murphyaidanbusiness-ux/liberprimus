import numpy as np, pickle, sys, json
import core, enc, channels as ch
from multiprocessing import Pool
MSG="ALLTHINGSMUSTPASSTHETRUTHISHIDDENINPLAINSIGHTSEEKANDYEWILLFINDIT"[:60]
assert len(MSG)==60
W=ch.CH['W']; marg=np.asarray(W.data)
cb=W.kw['cb']; cm=W.kw['cm']
ITA_inv={}
for code,c in enumerate(enc._ITA):
    if len(c)==1 and 'A'<=c<='Z': ITA_inv[c]=code
def bits_of(v,g,order): 
    b=[(v>>(g-1-i))&1 for i in range(g)]
    return b if order=='msb' else b[::-1]
def sample_with(rng, pred):
    pool=marg[pred(marg)]
    return int(rng.choice(pool))
def plant(kind, seed):
    rng=np.random.default_rng(5000+seed)
    x=rng.choice(marg,size=len(marg)).astype(np.int64)
    idx=[ord(c)-65 for c in MSG]
    if kind=='raw_A1Z26':
        seq=[i+1 for i in idx]; s=int(rng.integers(0,len(x)-len(seq))); x[s:s+60]=seq
        want='W|rawf'
    elif kind=='par_baudot':
        bits=[]
        for c in MSG: bits+=bits_of(ITA_inv[c],5,'msb')
        s=int(rng.integers(0,len(x)-len(bits)));
        for j,b in enumerate(bits): x[s+j]=sample_with(rng,lambda m,b=b:(m&1)==b)
        want='par|bdtf'
    elif kind=='par_ascii7_lsb_off3':
        bits=[int(rng.integers(0,2)) for _ in range(3)]
        for c in MSG: bits+=bits_of(ord(c),7,'lsb')
        s=int(rng.integers(0,len(x)-len(bits)))
        for j,b in enumerate(bits): x[s+j]=sample_with(rng,lambda m,b=b:(m&1)==b)
        want='par|bitsf g7'
    elif kind=='gt4_ascii8':
        bits=[]
        for c in MSG: bits+=bits_of(ord(c),8,'msb')
        s=int(rng.integers(0,len(x)-len(bits)))
        for j,b in enumerate(bits): x[s+j]=sample_with(rng,lambda m,b=b:(m>4)==bool(b))
        want='gt4|bitsf g8'
    elif kind=='base15_pair':
        s=int(rng.integers(0,len(x)-120)); s-= s%2
        for j,i in enumerate(idx):
            while True:
                a=sample_with(rng,lambda m:m>0); b=sample_with(rng,lambda m:m>0)
                if (a*15+b)%26==i: break
            x[s+2*j]=a; x[s+2*j+1]=b
        want='base15 g2'
    elif kind=='mod3_trits':
        s=int(rng.integers(0,len(x)-180)); s-=s%3
        for j,i in enumerate(idx):
            tr=[(i//9)%3,(i//3)%3,i%3]
            for q,t in enumerate(tr): x[s+3*j+q]=sample_with(rng,lambda m,t=t:(m%3)==t)
        want='mod3 g3'
    elif kind=='morse_t3_6':
        # dot<=3 dash 4..6 gap>=7 : use cuts (3,6)
        sym=[]
        for c in MSG:
            sym+=[0 if ch_=='.' else 1 for ch_ in enc.MORSE[c]]+[2]
        s=int(rng.integers(0,len(x)-len(sym)))
        for j,t in enumerate(sym):
            pred=(lambda m:m<=3) if t==0 else ((lambda m:(m>3)&(m<=6)) if t==1 else (lambda m:m>6))
            x[s+j]=sample_with(rng,pred)
        want='morse dot-dash-gap t3,6'
    return x,want
KINDS=['raw_A1Z26','par_baudot','par_ascii7_lsb_off3','gt4_ascii8','base15_pair','mod3_trits','morse_t3_6']
def run(a):
    kind,seed=a
    x,want=plant(kind,seed)
    labs,rows,prs=enc.stat_vec(enc.length_encodings(x,'W',cb,cm))
    l2,r2,_=enc.stat_vec(enc.bdt_encodings('len',x,'W',cb))
    return kind,seed,want,labs+l2,np.vstack([rows,r2])
if __name__=='__main__':
    nseed=int(sys.argv[1]) if len(sys.argv)>1 else 4
    d=pickle.load(open('out_W.pkl','rb')); d2=pickle.load(open('out_BDT_W.pkl','rb'))
    NA=np.concatenate([d['nulls'],d2['nulls']],axis=1)
    Nl=NA[:,:,:5].astype(np.float64); mu=Nl.mean(0); sd=Nl.std(0)
    nmed=np.median(NA[:,:,5],axis=0)
    ok=(sd>1e-9)&(nmed[:,None]>=30)
    zn=np.where(ok[None],(Nl-mu)/np.where(ok,sd,1),-99)
    nullmax=zn.max(1)    # (nrep,5)
    with Pool(4) as p: res=p.map(run,[(k,s) for k in KINDS for s in range(nseed)])
    out=[]
    S=['Qall','Qwin','IoC','Hall','Hwin']
    for kind,seed,want,labs,rows in res:
        okk=ok&(rows[:,5:6]>=30)
        rows=rows[:,:5]
        z=np.where(okk,(rows-mu)/np.where(ok,sd,1),-99)
        rec=dict(kind=kind,seed=seed)
        for j in (0,1,4):
            k=int(np.argmax(z[:,j])); rec[S[j]]=dict(z=float(z[k,j]),label=labs[k],nullmax_p95=float(np.percentile(nullmax[:,j],95)),nullmax_max=float(nullmax[:,j].max()),real=float(rows[k,j]))
        # planted cell: best z among labels containing want
        cand=[i for i,l in enumerate(labs) if want in l]
        k=max(cand,key=lambda i:z[i,1]); rec['planted_cell']=dict(label=labs[k],zQwin=float(z[k,1]),Qwin=float(rows[k,1]))
        out.append(rec)
        print(kind,seed,'bestQwin z=%.1f [%s] planted-cell z=%.1f (nullmax max %.1f)'%(rec['Qwin']['z'],rec['Qwin']['label'].split('|',1)[1],rec['planted_cell']['zQwin'],rec['Qwin']['nullmax_max']),flush=True)
    json.dump(out,open('plant_results.json','w'),indent=1)
