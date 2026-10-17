import common, ciph, numpy as np, sys, json, math, re
sys.path.insert(0, common.DUK+'/src')
from lp import score as dsc
QG=dsc.default()
keys=[l.split() for l in open('keys.txt')]
def kw(i): return common.tr(map(int,keys[i][2:]))
def load(fn):
    R={}
    for l in open(fn):
        if l[0]=='#': continue
        t=l.rstrip('\n').split('\t'); R.setdefault((t[0],int(t[1])),[]).append(t[2:])
    return R
def units(fn):
    d={}
    for l in open(fn):
        t=list(map(int,l.split())); d[t[0]]=(t[1],t[3:])
    return d
def vname(fam,v):
    if fam==1: tt,sg,cv,al=ciph.f1var(v); return 'tau%d %s %s %s'%(tt,'p=u-k' if sg==0 else 'p=u+k','EAconsumes' if cv else 'EAskips','align%d'%al)
    if fam==2: kvm,d,cv,al=ciph.f2var(v); return '%s %s %s align%d'%('k=prime' if kvm else 'k=idx+1','x=D*k' if d else 'x=D/k','EAconsumes' if cv else 'EAskips',al)
    return ['vig p=c-k','beau p=k-c','varbeau p=c+k','skiprule vig','skiprule beau'][v]
SUB={49:66,32:121,15:159,2:201,27:234,51:263,29:277}
def nearest(u,n):
    return min(SUB,key=lambda p:abs(SUB[p]-n))
def run(fam,kind,real_res,null_res,unitfile,nullmap=None):
    R=load(real_res); N=load(null_res); UU=units(unitfile)
    ids=sorted({k[1] for k in R if k[0]=='STAT'})
    ids=[u for u in ids if len(UU[u][1])>=60]
    out=[]; rows=[]
    for u in ids:
        tq=R[('TOPQ',u)]; ti=R[('TOPI',u)]
        bq=float(tq[0][1]); bi=float(ti[0][1])
        nu = nullmap(u,len(UU[u][1])) if nullmap else u
        nq=np.array([float(N[('TOPQ',s*1000+nu)][0][1]) for s in range(1,21) if ('TOPQ',s*1000+nu) in N])
        ni=np.array([float(N[('TOPI',s*1000+nu)][0][1]) for s in range(1,21) if ('TOPI',s*1000+nu) in N])
        zq=(bq-nq.mean())/nq.std(); zi=(bi-ni.mean())/ni.std()
        # per key length
        lq={int(t[0]):float(t[1]) for t in R[('LEN',u)]}; li={int(t[0]):float(t[2]) for t in R[('LEN',u)]}
        lz=[]
        for L in range(1,18):
            a=np.array([float(N[('LEN',s*1000+nu)][L-1][1]) for s in range(1,21)]); b=np.array([float(N[('LEN',s*1000+nu)][L-1][2]) for s in range(1,21)])
            if lq[L]>-1e8 and a.min()>-1e8 and a.std()>0 and b.std()>0: lz.append((L,(lq[L]-a.mean())/a.std(),(li[L]-b.mean())/b.std()))
        mlq=max(lz,key=lambda x:x[1]); mli=max(lz,key=lambda x:x[2])
        # top candidate decode + dukotah quadgram on transliteration
        k=int(tq[0][3]); v=int(tq[0][4]); prev,c=UU[u]
        dec=ciph.dec(fam,c,prev,list(map(int,keys[k][2:])),v); trs=common.tr(dec)
        dq=QG.score_norm(trs)
        rows.append(dict(unit=u,n=len(c),best_q=bq,null_q_mean=nq.mean(),null_q_sd=nq.std(),null_q_max=nq.max(),z_q=zq,
            best_ioc=bi,null_i_mean=ni.mean(),null_i_sd=ni.std(),null_i_max=ni.max(),z_i=zi,key=kw(k),var=vname(fam,v),duk_q=dq,
            ioc_key=kw(int(ti[0][3])),ioc_var=vname(fam,int(ti[0][4])),len_best_zq=mlq,len_best_zi=mli,text=trs[:120]))
    return rows
if __name__=='__main__':
    allrows={}
    CFG=[(1,'pages_pruned','res_f1p_pages.tsv','res_f1p_null.tsv','units_pages.txt',None),
         (1,'pages_full(len-matched null)','res_f1_pages.tsv','res_f1_nullsub.tsv','units_pages.txt',nearest),
         (2,'pages','res_f2_pages.tsv','res_f2_null.tsv','units_pages.txt',None),
         (3,'pages','res_f3_pages.tsv','res_f3_null.tsv','units_pages.txt',None),
         (1,'sections_pruned','res_f1p_sec.tsv','res_f1p_nullsec.tsv','units_sections.txt',None),
         (2,'sections_pruned','res_f2p_sec.tsv','res_f2p_nullsec.tsv','units_sections.txt',None),
         (3,'sections_pruned','res_f3p_sec.tsv','res_f3p_nullsec.tsv','units_sections.txt',None)]
    for fam,kind,real,null,uf,nm in CFG:
            try: rows=run(fam,kind,real,null,uf,nm)
            except (FileNotFoundError,KeyError) as e: print('missing',kind,fam,e); continue
            allrows['F%d_%s'%(fam,kind)]=rows
            print('\n===== Family %d, %s ====='%(fam,kind))
            print('unit   n  best_q  null(mean+-sd,max)        z_q  | best_IoC null(mean+-sd,max)      z_i | dukQ  | key / variant')
            for r in rows:
                print('%4d %4d %7.3f %7.3f+-%.3f %7.3f %5.2f | %.3f %.3f+-%.3f %.3f %5.2f | %6.3f | %s / %s'%(r['unit'],r['n'],r['best_q'],r['null_q_mean'],r['null_q_sd'],r['null_q_max'],r['z_q'],
                    r['best_ioc'],r['null_i_mean'],r['null_i_sd'],r['null_i_max'],r['z_i'],r['duk_q'],r['key'],r['var']))
            zq=np.array([r['z_q'] for r in rows]); zi=np.array([r['z_i'] for r in rows])
            nbeat=sum(r['best_q']>r['null_q_max'] for r in rows); nbi=sum(r['best_ioc']>r['null_i_max'] for r in rows)
            print('SUMMARY F%d %s: z_q mean %.2f sd %.2f max %.2f (unit %d); z_i mean %.2f sd %.2f max %.2f (unit %d); units beating null max: quad %d/%d, IoC %d/%d (expect ~%.1f each by chance)'%(
                fam,kind,zq.mean(),zq.std(),zq.max(),rows[int(zq.argmax())]['unit'],zi.mean(),zi.std(),zi.max(),rows[int(zi.argmax())]['unit'],nbeat,len(rows),nbi,len(rows),len(rows)/21))
            lz=[(r['unit'],)+r['len_best_zq'] for r in rows]; m=max(lz,key=lambda x:x[2]); print('  best per-keylength z_q: unit %d L=%d z=%.2f'%m[:3])
            lz=[(r['unit'],)+r['len_best_zi'] for r in rows]; m=max(lz,key=lambda x:x[3]); print('  best per-keylength z_ioc: unit %d L=%d z=%.2f'%(m[0],m[1],m[3]))
            best=max(rows,key=lambda r:r['z_q']); print('  top-z unit text:',best['text'])
    json.dump(allrows,open('summary.json','w'),indent=1,default=float)
