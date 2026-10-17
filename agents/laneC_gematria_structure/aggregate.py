import sys, pickle, numpy as np, re
files=sys.argv[1:]
out={}
for f in files: out.update(pickle.load(open(f,'rb')))
def group(fam,label):
    if fam=='solved':
        if label.startswith('RAW:'): return 'RAW shift control: '+label.split('|')[0][4:]
        p=label.split('|'); return f'{p[0]} [{p[1]}]'
    if fam=='self':
        p=label.split('|'); return p[0]
    m=re.match(r'(LET lag\d|WORDSUM|CUMSUM)[^|]*\|\s*(\w+)',label)
    return f'{m.group(1)} / restart={m.group(2)}'
def collect(fam,s):
    r=out.get((fam,s)); 
    if r is None: return None
    g={}
    for label,v in r.items():
        k=group(fam,label)
        z=v[0]
        if k not in g or z>g[k][0]: g[k]=(z,v[1],label,v)
    return g
fams=sorted(set(f for f,_ in out))
rows_all=[]
for fam in fams:
    real=collect(fam,0)
    seeds=sorted(s for f,s in out if f==fam and s>0)
    nul=[collect(fam,s) for s in seeds]
    print(f'\n=== family {fam}: {len(real)} groups, {len(seeds)} null runs ===')
    fam_real=max(v[0] for v in real.values())
    fam_nul=[max(v[0] for v in n.values()) for n in nul]
    print('family-wide max z: real %.2f | null max-z: mean %.2f sd %.2f max %.2f  => real-minus-null-mean in sd = %.2f ; real beats null max: %s'%(fam_real,np.mean(fam_nul),np.std(fam_nul),max(fam_nul),(fam_real-np.mean(fam_nul))/np.std(fam_nul),fam_real>max(fam_nul)))
    print('%-46s %8s %10s | %7s %7s %7s | %6s'%('group','real z','real IoC','nullmu','nullsd','nullmax','sd-above'))
    rows=[]
    for k,(z,ioc,lab,v) in real.items():
        nz=np.array([n[k][0] for n in nul if k in n])
        rows.append((k,z,ioc,nz.mean(),nz.std(),nz.max(),(z-nz.mean())/nz.std(),lab,v))
    rows.sort(key=lambda r:-r[6])
    for r in rows[:int(sys.argv[0] and 25)]:
        print('%-46s %8.2f %10.4f | %7.2f %7.2f %7.2f | %6.2f'%r[:7])
    rows_all.append((fam,rows))
pickle.dump(rows_all,open('aggregate_rows.pkl','wb'))
