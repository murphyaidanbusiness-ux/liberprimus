# Positive controls for model (f): English runes enciphered by the chain cipher with a PRNG key.
import sys, subprocess, numpy as np
S='.'
L=S+'/agents/laneG_prng_generators'; sys.path.insert(0,L)
import prep
def vg(idi,mod,n,iv):
    return list(map(int,subprocess.check_output([L+'/vecgen',str(idi),str(mod),str(n),str(iv)]).split()))
E=np.load(S+'/agents/laneD_chain_variants/eng_runes.npy')
ps=prep.pstart+[12956]
# F1: continuous key, glibc srand(4242) rand()%28, additive chain  D = 1 + (x + k) mod 28  (x = rune index, EA -> D=0), conv X
x=E[50000:50000+12956]; k=vg(11,-28,12956,4242)
D=np.where(x==28,0,1+(x+np.array(k))%28)
C=np.zeros(12956,dtype=np.uint8)
for p in range(55):
    s,e=ps[p],ps[p+1]; C[s:e]=np.cumsum(D[s:e])%29
C.tofile(L+'/ctrl/corpus_f1.bin')
# F2: per-page seed (900+p), py3 randrange(28) (PY3 idiom on int seed), GF(29) multiplicative D = x * K^-1, x(EA)=0, key restarts per page
INV=[0]+[pow(a,27,29) for a in range(1,29)]
x=E[80000:80000+12956]; xx=np.where(x==28,0,x+1)
C=np.zeros(12956,dtype=np.uint8)
for p in range(55):
    s,e=ps[p],ps[p+1]; k=vg(1,-28,e-s,900+p)
    Dp=np.array([(xx[s+i]*INV[k[i]+1])%29 for i in range(e-s)]); C[s:e]=np.cumsum(Dp)%29
C.tofile(L+'/ctrl/corpus_f2.bin')
lines=[l for l in open(L+'/seeds_all.txt') if l[0]=='I' and int(l.split()[1])<=5000]
open(L+'/ctrl/seeds_f.txt','w').writelines(lines); print(len(lines))
