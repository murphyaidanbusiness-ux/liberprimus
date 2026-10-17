import glob, pickle, numpy as np, core, os
lib=core.lib(); names=[n.split('/')[-1].replace('.txt','') for n in lib['names']]; NT=len(names)
out=[]; P=lambda *a: out.append(' '.join(str(x) for x in a))
TGS=['s%d'%i for i in range(9)]+['whole']
cells=[]; pertext=[]
rows={}
for vn in [core.vname(v) for v in core.variant_list()]:
    fn=core.HERE+'/kmer_out/%s.pkl'%vn
    if not os.path.exists(fn): continue
    R=pickle.load(open(fn,'rb'))
    for k in (6,8):
        for tg in TGS:
            lst=R[(k,tg)]
            get=lambda lab,st:np.array([s[st] for l,s in lst if l==lab])
            for st in (('H','band','run') if k==6 else ('H','band')):
                re=get('real',st)[0]; sh=get('sh',st); he=get('he',st); pl=get('plant',st)
                z=(re-sh.mean())/max(sh.std(),1e-9); p=(sh>=re).mean()
                cells.append(dict(v=vn,k=k,tg=tg,st=st,real=re,mu=sh.mean(),sd=sh.std(),mx=sh.max(),z=z,p=p,he_mu=he.mean(),he_mx=he.max(),plant=(pl[0] if len(pl) else None)))
            # per-text hit z (k-mer hits per text vs the same text's shuffle distribution)
            M=np.array([s['pertext'] for l,s in lst if l=='sh'],float); r=np.array([s['pertext'] for l,s in lst if l=='real'][0],float)
            mu=M.mean(0); sd=M.std(0)+1e-9; ok=mu>=5
            if ok.sum()==0: continue
            zr=((r-mu)/sd)[ok]; zs=((M-mu)/sd)[:,ok]; mxs=zs.max(1)
            ti=np.where(ok)[0][zr.argmax()]
            pertext.append(dict(v=vn,k=k,tg=tg,maxz=zr.max(),text=names[ti],null_mean=mxs.mean(),null95=np.percentile(mxs,95),null_max=mxs.max(),p=(mxs>=zr.max()).mean()))
P('## k-mer index statistics (200 target shuffles per cell; 20 held-out English windows)\n')
z=np.array([c['z'] for c in cells])
P('Cells: %d (%d variants x 10 targets x {H6, band6, run6, H8, band8}). z: mean %.2f, sd %.2f, max %.2f; # z>3: %d; # real >= shuffle max: %d; min empirical p: %.3f'%(len(z),len(set(c["v"] for c in cells)),z.mean(),z.std(),z.max(),(z>3).sum(),sum(1 for c in cells if c["real"]>=c["mx"]),min(c["p"] for c in cells)))
for st in ('H','band','run'):
    for k in (6,8):
        zz=np.array([c['z'] for c in cells if c['st']==st and c['k']==k])
        if len(zz): P('- %s k=%d: n=%d, z mean %+.2f sd %.2f max %+.2f'%(st,k,len(zz),zz.mean(),zz.std(),zz.max()))
P('\nTop 15 cells by z:\n\n| z | emp. p | variant | k | target | stat | real | shuffle mean±sd (max) | held-out Eng mean (max) |\n|---|---|---|---|---|---|---|---|---|')
for c in sorted(cells,key=lambda c:-c['z'])[:15]:
    P('| %+.2f | %.3f | %s | %d | %s | %s | %d | %.1f±%.1f (%d) | %.1f (%d) |'%(c['z'],c['p'],c['v'],c['k'],c['tg'],c['st'],c['real'],c['mu'],c['sd'],c['mx'],c['he_mu'],c['he_mx']))
P('\nKey variants, all targets (band = max k-mer hits on one 64-word diagonal band; run = longest exact common run of word lengths; H = total k-mer hits):\n')
P('| variant | target | H6 real / null mu±sd z | band6 real / null max (plant) | run6 real / null mu (max) (plant) | H8 z | band8 real / null max (plant) |\n|---|---|---|---|---|---|---|')
for vn in ['base','base_mF2','base_mP2','base_drop2','base_drop3','letters','THonly','base_drop26','base_mF26']:
    for tg in TGS:
        cc={(c['k'],c['st']):c for c in cells if c['v']==vn and c['tg']==tg}
        if not cc: continue
        a=cc[(6,'H')];b=cc[(6,'band')];r=cc[(6,'run')];h8=cc[(8,'H')];b8=cc[(8,'band')]
        P('| %s | %s | %d / %.0f±%.0f %+.1f | %d / %d (%s) | %d / %.1f (%d) (%s) | %+.1f | %d / %d (%s) |'%(vn,tg,a['real'],a['mu'],a['sd'],a['z'],b['real'],b['mx'],b['plant'],r['real'],r['mu'],r['mx'],r['plant'],h8['z'],b8['real'],b8['mx'],b8['plant']))
pz=np.array([p['maxz'] for p in pertext]); pp=np.array([p['p'] for p in pertext])
P('\n### Per-text k-mer hit counts (texts with >=5 expected hits): real max-over-texts z vs the same statistic for each shuffle\n')
P('%d (variant, k, target) cells; empirical p of the real max-over-texts z: min %.3f, # p<0.01: %d, # p<0.05: %d (expected by chance ~%.1f and ~%.1f)'%(len(pp),pp.min(),(pp<0.01).sum(),(pp<0.05).sum(),0.01*len(pp),0.05*len(pp)))
P('\n| variant | k | target | real max text z | text | null mean / 95%% / max | p |\n|---|---|---|---|---|---|---|')
for p in sorted(pertext,key=lambda p:p['p'])[:12]:
    P('| %s | %d | %s | %.2f | %s | %.2f / %.2f / %.2f | %.3f |'%(p['v'],p['k'],p['tg'],p['maxz'],p['text'],p['null_mean'],p['null95'],p['null_max'],p['p']))
open(core.HERE+'/analysis_kmer.md','w').write('\n'.join(out)); print('\n'.join(out[:30]))
