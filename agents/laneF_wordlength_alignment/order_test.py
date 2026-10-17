# Does the ORDER of the unsolved word lengths carry English-like serial structure?
# Markov-1 / Markov-2 log-likelihood gain (vs the corpus's own unigram) of the real sequence, compared
# with 1000 permutations of itself (within section), and the same test on held-out English windows (power).
import numpy as np, core, json
T,PG,CH=core.target(); SECS=core.sections(PG)
lib=core.lib(); tok=lib['tok']
K=16
def model(L):
    L=L[L>0].astype(int)
    u=np.bincount(L,minlength=K)+0.5; u/=u.sum()
    b=np.zeros((K,K))+0.5; np.add.at(b,(L[:-1],L[1:]),1); b/=b.sum(1,keepdims=True)
    t=np.zeros((K,K,K))+0.5; np.add.at(t,(L[:-2],L[1:-1],L[2:]),1); t/=t.sum(2,keepdims=True)
    return np.log(u),np.log(b),np.log(t)
def gain(seq_list,M):
    lu,lb,lt=M; g1=g2=0.0
    for s in seq_list:
        s=np.minimum(np.asarray(s,int),15)
        g1+= (lb[s[:-1],s[1:]]-lu[s[1:]]).sum()
        g2+= (lt[s[:-2],s[1:-1],s[2:]]-lu[s[2:]]).sum()
    return g1,g2
if __name__=='__main__':
  rng=np.random.default_rng(1)
  res=[]
  for v in [('base','none',0),('base','mF',2),('base','mP',2),('base','drop',2),('base','drop',3),('base','drop',4),('letters','none',0),('letters','drop',2),('THonly','drop',2)]:
      M=model(core.variant_stream(v))
      real=[T[ix] for ix in SECS]
      g=gain(real,M)
      sh=np.array([gain([rng.permutation(x) for x in real],M) for _ in range(1000)])
      z=[(g[k]-sh[:,k].mean())/sh[:,k].std() for k in (0,1)]
      # power: held-out English windows of the same section sizes in the same variant, vs their own permutations
      hz=[]
      for rep in range(20):
          pool=lib['hold'] if rep%2==0 else lib['ewt']
          off=int(rng.integers(0,len(pool)-20000)); st=core.variant_stream(v,pool[off:off+20000])
          st=st[st>0]; segs=[];p=0
          for ix in SECS: segs.append(st[p:p+len(ix)]); p+=len(ix)
          gh=gain(segs,M); shh=np.array([gain([rng.permutation(x) for x in segs],M) for _ in range(200)])
          hz.append([(gh[k]-shh[:,k].mean())/shh[:,k].std() for k in (0,1)])
      hz=np.array(hz)
      r=dict(variant=core.vname(v),real_gain_M1=round(g[0],1),shuf_M1='%.1f±%.1f'%(sh[:,0].mean(),sh[:,0].std()),z_M1=round(z[0],2),
             real_gain_M2=round(g[1],1),shuf_M2='%.1f±%.1f'%(sh[:,1].mean(),sh[:,1].std()),z_M2=round(z[1],2),
             heldout_z_M1='%.1f (min %.1f)'%(hz[:,0].mean(),hz[:,0].min()),heldout_z_M2='%.1f (min %.1f)'%(hz[:,1].mean(),hz[:,1].min()))
      print(json.dumps(r),flush=True); res.append(r)
  json.dump(res,open(core.HERE+'/order_test.json','w'),indent=1)
