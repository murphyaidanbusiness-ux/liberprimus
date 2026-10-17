import os, glob, json, pickle, numpy as np, core
lib=core.lib(); names=[n.split('/')[-1].replace('.txt','') for n in lib['names']]; NT=len(names)
T,PG,CH=core.target(); SECS=core.sections(PG); SL=[len(s) for s in SECS]
V=core.variant_list(); VN=[core.vname(v) for v in V]
def load_sw(vn):
    fs=sorted(glob.glob(core.HERE+'/sw_out/%s__p*.npz'%vn))
    if not fs: return None
    d0=np.load(core.HERE+'/sw_out/%s__p0.npz'%vn) if os.path.exists(core.HERE+'/sw_out/%s__p0.npz'%vn) else None
    if d0 is None: return None
    R={}
    for s in range(9):
        b=d0['s%d_best'%s].astype(int); real=b[:,0]; sh=[b[:,1:24]]; he=b[:,24:28]; pl=b[:,28:32]
        for f in fs:
            if f.endswith('__p0.npz'): continue
            sh.append(np.load(f)['s%d_best'%s].astype(int))
        sh=np.concatenate(sh,1)
        R[s]=dict(real=real,sh=sh,he=he,pl=pl,meta=json.loads(str(d0['s%d_meta'%s])),j=d0['s%d_j'%s][:,0])
    return R
out=[]; P=lambda *a: out.append(' '.join(str(x) for x in a))
P('# laneF analysis output\n')
# ---------- 1. SW best-over-library per variant x section ----------
P('## SW: best local-alignment score over the whole library (max over texts), real vs shuffled-target null\n')
P('| variant | n_shuf | ' + ' | '.join('s%d (m=%d)'%(s,SL[s]) for s in range(9)) + ' | sum s0-s7 z |')
P('|---|---|' + '---|'*10)
allz=[]; plant_rows=[]; SW={}
for vn in VN:
    R=load_sw(vn)
    if R is None: continue
    SW[vn]=R; cells=[]; sr=0; ssh=0
    for s in range(9):
        r=R[s]; rm=r['real'].max(); shm=r['sh'].max(0); z=(rm-shm.mean())/shm.std(); p=(shm>=rm).mean()
        cells.append('%d / %.1f±%.1f (max %d) z=%+.1f'%(rm,shm.mean(),shm.std(),shm.max(),z)); allz.append((z,vn,s,rm,shm.max(),names[r['real'].argmax()]))
        if s<8: sr+=rm; ssh=ssh+shm
        pm=r['pl'].max(0); pt=r['pl'].argmax(0)
        plant_rows.append((vn,s,pm.tolist(),[names[k]==r['meta']['src'].split('/')[-1].replace('.txt','') for k in pt],shm.max(),r['he'].max()))
    zs=(sr-ssh.mean())/ssh.std()
    P('| %s | %d | '%(vn,R[0]['sh'].shape[1])+' | '.join(cells)+' | %+.2f |'%zs)
P('\nCell = real best / shuffle mean±sd (shuffle max) and z. Best text per cell is listed in the top-z table below.\n')
allz.sort(reverse=True)
zz=np.array([a[0] for a in allz])
P('All %d (variant, section) SW z-scores: mean %.2f, sd %.2f, max %.2f, min %.2f; # z>3: %d; # real > shuffle max: %d'%(len(zz),zz.mean(),zz.std(),zz.max(),zz.min(),(zz>3).sum(),sum(1 for a in allz if a[3]>a[4])))
P('\nTop 12 (variant, section) by z:\n\n| z | variant | section | real best | shuffle max | best text |\n|---|---|---|---|---|---|')
for a in allz[:12]: P('| %+.2f | %s | s%d | %d | %d | %s |'%(a[0],a[1],a[2],a[3],a[4],a[5]))
# held-out English
P('\n## SW held-out English windows (4 per section per variant, same length as section)\n')
he_all=[];sh_all=[];re_all=[]
for vn,R in SW.items():
    for s in range(8):
        he_all.append(R[s]['he'].max(0)-R[s]['sh'].max(0).mean()); re_all.append(R[s]['real'].max()-R[s]['sh'].max(0).mean())
he_all=np.concatenate(he_all); re_all=np.array(re_all)
P('Best-over-library score minus shuffle mean, pooled over variants and sections s0-s7: held-out English mean %+.2f (sd %.2f, n=%d); real target mean %+.2f (sd %.2f, n=%d).'%(he_all.mean(),he_all.std(),len(he_all),re_all.mean(),re_all.std(),len(re_all)))
# plants
P('\n## SW planted positive controls inside every run (lanes 28-31: planted mF2 / drop2 / unmodified / mF2+15% noise windows of section length)\n')
P('| variant | ' + ' | '.join('s%d'%s for s in range(8)) + ' |\n|---|' + '---|'*8)
for vn in SW:
    rows=[r for r in plant_rows if r[0]==vn and r[1]<8]
    P('| %s | '%vn + ' | '.join('%s%s (null max %d)'%('/'.join(map(str,r[2])),'' if all(r[3]) else ' [text miss %s]'%''.join('1' if x else '0' for x in r[3]),r[4]) for r in rows)+' |')
# ---------- 2. per-text SW z (key variants with many shuffles) ----------
P('\n## SW per text: real score of each (text, section) vs that cell\'s own shuffle distribution (key variants)\n')
for vn,R in SW.items():
    nsh=R[0]['sh'].shape[1]
    if nsh<100: continue
    Zr=[];Zs=[]
    for s in range(8):
        sh=R[s]['sh']; mu=sh.mean(1); sd=sh.std(1)+1e-9
        Zr.append((R[s]['real']-mu)/sd); Zs.append((sh-mu[:,None])/sd[:,None])
    Zr=np.array(Zr); Zs=np.array(Zs)   # (8,NT) and (8,NT,nsh)
    mr=Zr.max(); ms=Zs.reshape(-1,nsh).max(0)
    s_,t_=np.unravel_index(Zr.argmax(),Zr.shape)
    P('- %s (%d shuffles): max per-(text,section) z = %.2f (%s, s%d, score %d); null distribution of that max: mean %.2f, 95%% %.2f, max %.2f; empirical p = %.3f'%(vn,nsh,mr,names[t_],s_,R[s_]['real'][t_],ms.mean(),np.percentile(ms,95),ms.max(),(ms>=mr).mean()))
open(core.HERE+'/analysis_sw.md','w').write('\n'.join(out)); print('\n'.join(out))
pickle.dump(dict(allz=allz),open(core.HERE+'/analysis_sw.pkl','wb'))
# ---------- 3. family-wise null over all (variant, section) cells, using the p0 shuffle replicates ----------
# The p0 shuffles are identical permutations across variants (seeded by pass and section), so replicate k
# is a coherent "fake target" over all cells; compare the real family maximum with each replicate's.
cells=[(vn,s) for vn in SW for s in range(8)]
R0=np.array([[SW[vn][s]['real'].max()]+list(SW[vn][s]['sh'][:,:23].max(0)) for vn,s in cells],float)  # (ncell, 24): col0 real
nrep=R0.shape[1]
famz=[];famex=[]
for k in range(nrep):
    others=np.delete(R0,k,axis=1); mu=others.mean(1); sd=others.std(1)+1e-9
    famz.append(((R0[:,k]-mu)/sd).max()); famex.append((R0[:,k]-others.max(1)).max())
famz=np.array(famz); famex=np.array(famex)
P('\n## Family-wise null over all %d (variant, section s0-s7) cells (p0 replicates, leave-one-out)\n'%len(cells))
P('- max z over cells: real %.2f; the 23 shuffle replicates: mean %.2f, max %.2f; rank of real among 24 = %d (1 = largest)'%(famz[0],famz[1:].mean(),famz[1:].max(),1+(famz[1:]>=famz[0]).sum()))
P('- max (score minus max of the other replicates) over cells: real %+d; replicates mean %+.2f, max %+d; rank of real = %d'%(famex[0],famex[1:].mean(),famex[1:].max(),1+(famex[1:]>=famex[0]).sum()))
open(core.HERE+'/analysis_sw.md','w').write('\n'.join(out))
# ---------- 4. whole-book SW (key variants) ----------
P('\n## SW whole book as one target (2,896 words; real + 23 shuffles + 4 held-out English + 4 planted)\n')
P('| variant | real best (text) | shuffle mean±sd (max) | z | held-out English max | planted mF2/drop2/unmod/noisy |\n|---|---|---|---|---|---|')
for fn in sorted(glob.glob(core.HERE+'/sw_out/*__whole.npz')):
    d=np.load(fn); b=d['whole_best'].astype(int); vn=os.path.basename(fn).split('__')[0]
    mx=b.max(0); sh=mx[1:24]
    P('| %s | %d (%s) | %.1f±%.1f (%d) | %+.2f | %d | %s |'%(vn,mx[0],names[b[:,0].argmax()],sh.mean(),sh.std(),sh.max(),(mx[0]-sh.mean())/sh.std(),mx[24:28].max(),'/'.join(map(str,mx[28:32]))))
open(core.HERE+'/analysis_sw.md','w').write('\n'.join(out))
