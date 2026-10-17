import pickle, numpy as np, collections
from variants import VARIANTS
d=pickle.load(open('results_main.pkl','rb')); R=d['R']
B=pickle.load(open('boot.pkl','rb'))
keys=B['keys']; cf0=B['cf0']; cw0=B['cw0']; CF=B['CF']; CW=B['CW']; obs=B['obs']; valid=B['valid']
kidx={k:i for i,k in enumerate(keys)}
def ci(x0,xb): 
    lo,hi=np.percentile(xb,[2.5,97.5]); return 2*x0-hi,2*x0-lo    # basic bootstrap interval
def table(sel,title,rankcol='cf',maxn=40):
    ids=[kidx[k] for k in sel if k in kidx]
    arr=cf0 if rankcol=='cf' else cw0; AB=CF if rankcol=='cf' else CW
    ids=sorted(ids,key=lambda i:arr[i])
    sub=AB[:,ids]; ranks=np.argsort(np.argsort(sub,1),1)+1
    out=['### '+title,'','| rank | candidate | lang/reg | words | mean len | combined (all 5) | 95% CI | word-level comb. (A+B) | rank 95% CI | JS A | B | C | D | E |','|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for j,i in enumerate(ids[:maxn]):
        k=keys[i]; r=R[k]
        lo,hi=ci(cf0[i],CF[:,i]); rl,rh=np.percentile(ranks[:,j],[2.5,97.5])
        nm=k[0] if k[1]=='natural' else k[0]+' ['+k[1]+']'
        out.append('| %d | %s | %s/%s | %d | %.2f | %.2f%s | %.2f-%.2f | %.2f | %d-%d | %s |'%(j+1,nm,r['lang'],r['reg'],r['nw'],r['meanlen'],cf0[i],'' if valid[i] else '*',lo,hi,cw0[i],rl,rh,' | '.join('%.4f'%x for x in obs[i])))
    return '\n'.join(out)+'\n'
if __name__=='__main__':
    nat=[k for k in keys if k[1]=='natural']
    print(table(nat,'Natural (unmodified) candidates ranked by combined normalised JS',maxn=60))
