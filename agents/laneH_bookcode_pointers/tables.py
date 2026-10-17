import pickle, numpy as np, collections, csv
HERE='./agents/laneH_bookcode_pointers'
rows=pickle.load(open(HERE+'/results/_analyzed.pkl','rb'))
def stat(rs,key='sh'):
    zr=[r['z_'+key] for r in rs if not np.isnan(r['z_'+key])]
    if not zr: return None
    L=[r['loo_'+key] for r in rs if r['loo_'+key] is not None]
    nm=np.nanmax(np.vstack(L),axis=0)
    real=max(zr)
    p=(np.sum(nm>=real)+1)/(len(nm)+1)
    return real,nm.mean(),nm.std(),nm.max(),p,len(zr)
views=sorted({r['view'] for r in rows}); srcs=['gsum','isum','isum1','wlen','w29','rprime','ridx','ridx1','wt2_idx1','wt2_prime','wt3_idx1','wt3_prime','wt4_idx1','wt4_prime']
out=[]
out.append('| text view | '+' | '.join(srcs)+' |'); out.append('|'+'---|'*(len(srcs)+1))
for v in views:
    cells=[]
    for s in srcs:
        rs=[r for r in rows if r['view']==v and r['src']==s]
        st=stat(rs); sc=stat(rs,'ch')
        cells.append('-' if st is None else f'{st[0]:.1f} ({st[1]:.1f}) ; {sc[0]:.1f} ({sc[1]:.1f})')
    out.append(f'| {v} | '+' | '.join(cells)+' |')
open(HERE+'/table_view_src.md','w').write('\n'.join(out))
print('\n'.join(out))
fams=['letter-ptr','word-ptr','cumulative','tuple2','tuple3','tuple4']
out2=['| family | rows | real max z (shuffle null) | null max z (mean +- sd, max of 50) | emp p | real max z (chain null) | null max z | emp p |','|---|---|---|---|---|---|---|---|']
for f in fams:
    rs=[r for r in rows if r['fam']==f]; st=stat(rs)
    sc=stat(rs,'ch')
    out2.append(f'| {f} | {len(rs)} | {st[0]:.2f} | {st[1]:.2f} +- {st[2]:.2f}, max {st[3]:.2f} | {st[4]:.2f} | {sc[0]:.2f} | {sc[1]:.2f} +- {sc[2]:.2f}, max {sc[3]:.2f} | {sc[4]:.2f} |')
rs=rows; st=stat(rs); sc=stat(rs,'ch'); out2.append(f'| ALL | {len(rs)} | {st[0]:.2f} | {st[1]:.2f} +- {st[2]:.2f}, max {st[3]:.2f} | {st[4]:.2f} | {sc[0]:.2f} | {sc[1]:.2f} +- {sc[2]:.2f}, max {sc[3]:.2f} | {sc[4]:.2f} |')
# by sem
out3=['| semantic | rows | real max z (shuffle) | null max z | emp p | real max z (chain) | null max z | emp p |','|---|---|---|---|---|---|---|---|']
for sem in sorted({r['sem'] for r in rows}):
    rs=[r for r in rows if r['sem']==sem]; st=stat(rs); sc=stat(rs,'ch')
    out3.append(f'| {sem} | {len(rs)} | {st[0]:.2f} | {st[1]:.2f} | {st[4]:.2f} | {sc[0]:.2f} | {sc[1]:.2f} | {sc[4]:.2f} |')
# by score
out4=['| score | rows | real max z (shuffle) | null max z | emp p | real max z (chain) | null max z | emp p |','|---|---|---|---|---|---|---|---|']
for sc in sorted({r['score'] for r in rows}):
    rs=[r for r in rows if r['score']==sc]; st=stat(rs); sc2=stat(rs,'ch')
    out4.append(f'| {sc} | {len(rs)} | {st[0]:.2f} | {st[1]:.2f} | {st[4]:.2f} | {sc2[0]:.2f} | {sc2[1]:.2f} | {sc2[4]:.2f} |')
# by texts
out5=['| view | rows | real max z (shuffle) | null max z | emp p | real max z (chain) | null max z | emp p |','|---|---|---|---|---|---|---|---|']
for v in views:
    rs=[r for r in rows if r['view']==v]; st=stat(rs); sc=stat(rs,'ch')
    out5.append(f'| {v} | {len(rs)} | {st[0]:.2f} | {st[1]:.2f} +- {st[2]:.2f} | {st[4]:.2f} | {sc[0]:.2f} | {sc[1]:.2f} +- {sc[2]:.2f} | {sc[4]:.2f} |')
out6=['| source | rows | real max z (shuffle) | null max z | emp p | real max z (chain) | null max z | emp p |','|---|---|---|---|---|---|---|---|']
for s in srcs:
    rs=[r for r in rows if r['src']==s]; st=stat(rs); sc=stat(rs,'ch')
    out6.append(f'| {s} | {len(rs)} | {st[0]:.2f} | {st[1]:.2f} +- {st[2]:.2f} | {st[4]:.2f} | {sc[0]:.2f} | {sc[1]:.2f} +- {sc[2]:.2f} | {sc[4]:.2f} |')
for o in (out2,out3,out4,out5,out6): print('\n'.join(o)); print()
open(HERE+'/tables_other.md','w').write('\n\n'.join('\n'.join(o) for o in (out2,out3,out4,out5,out6)))
# csv
with open(HERE+'/all_configs.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['view','src','sem','b','mode','score','nout','real','z_shuffle','z_random','z_chain'])
    for r in rows: w.writerow([r['view'],r['src'],r['sem'],r['b'],r['mode'],r['score'],r['nout'],f"{r['real']:.4f}",f"{r['z_sh']:.3f}",f"{r['z_rd']:.3f}",f"{r['z_ch']:.3f}"])
