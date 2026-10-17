# Print the aligned candidate words next to the cipher word lengths for the best real SW hits (illustration).
import sys, numpy as np, core, glob, os
lib=core.lib(); tok=lib['tok']; types=lib['types']; names=[n.split('/')[-1] for n in lib['names']]
T,PG,CH=core.target(); SECS=core.sections(PG)
def groups(v):
    sc,mdl,s=v; sep=tok<0
    if mdl=='none': return np.arange(len(tok)), None
    stp=np.zeros(len(tok),bool); sm=core.stopmask(s); stp[~sep]=sm[tok[~sep]]
    if mdl=='drop': return np.where(~stp)[0], None
    ns=~stp; g=np.cumsum(ns)-ns if mdl=='mF' else np.maximum(np.cumsum(ns)-1,0)
    return None, g
def words_at(v,positions):
    first,g=groups(v)
    if g is None: return [types[tok[first[p]]] if tok[first[p]]>=0 else '|' for p in positions]
    out=[]
    for p in positions:
        lo=np.searchsorted(g,p,'left'); hi=np.searchsorted(g,p,'right'); out.append('+'.join(types[t] if t>=0 else '|' for t in tok[lo:hi]))
    return out
def show(vn_tuple, s, maxrows=60):
    vn=core.vname(vn_tuple); d=np.load(core.HERE+'/sw_out/%s__p0.npz'%vn)
    b=d['s%d_best'%s][:,0]; j=d['s%d_j'%s][:,0]; t=int(b.argmax()); jend=int(j[t])
    L=core.variant_stream(vn_tuple); tgt=T[SECS[s]]
    lo=max(0,jend-3*len(tgt)); W=L[lo:jend+1]; sc,path=core.traceback(W,tgt)
    js=[q+lo for p,q in path if q is not None]; ws=dict(zip(js,words_at(vn_tuple,js)))
    print('\n### %s, section s%d: best text %s, SW score %d, %d aligned columns'%(vn,s,names[t],sc,len(path)))
    print('| cipher word # (page) | cipher len | candidate len | candidate word(s) |\n|---|---|---|---|')
    for p,q in path[:maxrows]:
        cw='%d (p%d)'%(SECS[s][p],PG[SECS[s][p]]) if p is not None else '-'
        cl=str(tgt[p]) if p is not None else '-'
        ll=str(L[q+lo]) if q is not None else '-'
        wd=ws.get(q+lo,'') if q is not None else ''
        mark='' if (p is None or q is None or tgt[p]!=L[q+lo]) else ''
        print('| %s | %s | %s | %s |'%(cw,cl,ll,wd))
if __name__=='__main__':
    import pickle
    allz=pickle.load(open(core.HERE+'/analysis_sw.pkl','rb'))['allz']
    done=set()
    for z,vn,s,rm,shm,txt in allz[:3]:
        v=[v for v in core.variant_list() if core.vname(v)==vn][0]
        show(v,s)
