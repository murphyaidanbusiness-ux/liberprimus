import pickle, glob, numpy as np, json, re
def famof(lab):
    p=lab.split('|')
    t=p[1] if len(p)>1 else ''
    if any(x.startswith('bdt') for x in p): return 'bits->Baudot (stateless)'
    if any(x.startswith('bits') for x in p):
        bp=[x for x in p if x.startswith('bits')][0]
        return 'bits->'+('A1Z26 / Baudot(stateful)' if bp.split()[-1] in ('a1z26','baudot') else 'ASCII 7/8-bit')
    if t.startswith('raw'): return 'raw (len->letter/rune)'
    if t.startswith('val'): return 'rune value'
    if t.startswith('inc'): return 'rune increments'
    if t.startswith('mod'): return 'mod-k digits grouped'
    if t.startswith('base'): return 'base-N pairs/triples'
    if t.startswith('morse'): return 'Morse'
    if t.startswith('SR') or t.startswith('LP1'): return 'book code '+t.split()[0]
    return t
def run(chname, files):
    out={}
    for f in files:
        d=pickle.load(open(f,'rb'))
        if len(d['labs'])==0: continue
        labs=d['labs']; R=d['real'][:,:5].astype(float); NL=d['nulls'][:,:,:5].astype(float)
        n=d['real'][:,5]; nm=np.median(d['nulls'][:,:,5],0) if d['nulls'].shape[2]>5 else n
        for fam in set(famof(l) for l in labs):
            idx=np.array([i for i,l in enumerate(labs) if famof(l)==fam])
            j=1
            mu=NL[:,idx,j].mean(0); sd=NL[:,idx,j].std(0)
            ok=(sd>1e-9)&(n[idx]>=30)&(nm[idx]>=30)
            if not ok.any(): out[fam]=None; continue
            z=np.where(ok,(R[idx,j]-mu)/np.where(ok,sd,1),-99)
            zn=np.where(ok[None],(NL[:,idx,j]-mu)/np.where(ok,sd,1),-99).max(1)
            k=int(np.argmax(z)); p=(1+(zn>=z[k]).sum())/(1+len(zn))
            prev=out.get(fam)
            out[fam]=(float(z[k]),float(p),float(np.percentile(zn,95)),int(ok.sum()),labs[idx[k]]) if prev is None else prev
    return out
chs=['W','SW','SR','CHw','CHr','LR','LWd','LF','LT','PGr','PGw','FW','LWr','FL','LLr','FS','LS','FP','LP','BW','BL','BS']
table={}
for c in chs:
    fl=['out_%s.pkl'%c]+glob.glob('out_BDT_%s.pkl'%c)+glob.glob('out_BK_%s.pkl'%c)
    # merge main + bdt into one by calling separately and combining dicts
    res={}
    for f in fl: res.update({k:v for k,v in run(c,[f]).items()})
    table[c]=res
fams=sorted({f for r in table.values() for f in r})
json.dump(table,open('family_table.json','w'),indent=1)
print('| channel | '+' | '.join(fams)+' |')
for c in chs:
    row=[]
    for f in fams:
        v=table[c].get(f)
        row.append('-' if v is None else 'z=%.1f p=%.3f (%d)'%(v[0],v[1],v[3]))
    print('| %s | '%c+' | '.join(row)+' |')
