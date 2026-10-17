# Same order test on Cicada's own solved LP1 pages (true rune word lengths, 695 words; lane C solved.pkl)
import pickle, numpy as np, core
from order_test import model, gain
d=pickle.load(open(core.S+'/agents/laneC_gematria_structure/solved.pkl','rb'))
S=np.array([len(w) for p in d for w in p['cw']]); print('LP1 solved: %d words, mean %.2f'%(len(S),S.mean()))
T,PG,CH=core.target(); rng=np.random.default_rng(3); lib=core.lib()
for v in [('base','none',0),('base','mF',2),('base','drop',3)]:
    M=model(core.variant_stream(v))
    for nm,seq in (('LP1 solved (true runes)',S),('unsolved first %d'%len(S),T[:len(S)]),('unsolved last %d'%len(S),T[-len(S):])):
        g=gain([seq],M); sh=np.array([gain([rng.permutation(seq)],M) for _ in range(2000)])
        print(core.vname(v),nm,'M1 z=%.2f M2 z=%.2f'%((g[0]-sh[:,0].mean())/sh[:,0].std(),(g[1]-sh[:,1].mean())/sh[:,1].std()))
    # unsolved in 4 disjoint blocks of 695 words
    zs=[]
    for b in range(4):
        seq=T[b*695:(b+1)*695]; g=gain([seq],M); sh=np.array([gain([rng.permutation(seq)],M) for _ in range(1000)]); zs.append(round((g[0]-sh[:,0].mean())/sh[:,0].std(),2))
    print(core.vname(v),'unsolved 4 blocks of 695 M1 z:',zs)
    hz=[]
    for rep in range(40):
        pool=lib['hold'] if rep%2==0 else lib['ewt']; off=int(rng.integers(0,len(pool)-3000))
        st=core.variant_stream(v,pool[off:off+3000]); st=st[st>0][:len(S)]
        g=gain([st],M); sh=np.array([gain([rng.permutation(st)],M) for _ in range(300)]); hz.append((g[0]-sh[:,0].mean())/sh[:,0].std())
    print(core.vname(v),'held-out English windows of %d words: M1 z mean %.2f sd %.2f'%(len(S),np.mean(hz),np.std(hz)))
