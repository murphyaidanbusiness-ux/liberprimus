# Positive controls: plant generator outputs into a copy of the corpus, build its D-shuffle nulls, write a control seed list.
import sys, subprocess, numpy as np, json
S='.'
L=S+'/agents/laneG_prng_generators'; sys.path.insert(0,L); sys.path.insert(0,S+'/lp')
import lpdata, prep
from seedfns import *
def vg(idi,mod,n,iv,key=None):
    a=[L+'/vecgen',str(idi),str(mod),str(n),str(iv)]+([str(k) for k in key] if key else [])
    return list(map(int,subprocess.check_output(a).split()))
C=prep.C.copy(); ps=prep.pstart
plants=[]
# P1 (the brief's control): py2.7 random.seed('cicada'), int(random()*29) == randrange(29), model b, 262 runes as page 0
g=vg(0,1,262,0,key_py2(b'cicada')); C[0:262]=g
plants.append(dict(name='P1 py2.7 seed("cicada") PY2 model b, page 0 (262 runes)',idiom=0,model=1,seedlab='py27h64:cicada',stat='exact',pos=0,j=0,len=262))
# P2: glibc srand(77777), GLSC, model d, gen offset 137, relabelled into Unicode code-point order -> exact search must MISS, pattern search must HIT
RU=lpdata.RUNES; perm=np.argsort([ord(c) for c in RU]); relab={i:int(np.where(perm==i)[0][0]) for i in range(29)}
s=ps[30]; n=len(lpdata.unsolved()[0][30]['idx'])
g=vg(12,3,137+n,77777)[137:]; C[s:s+n]=[relab[x] for x in g]
plants.append(dict(name='P2 glibc srand(77777) GLSC model d, gen offset 137, Unicode-order relabel, page 30',idiom=12,model=3,seedlab='int:77777',stat='pattern',pos=int(s),j=137,len=n))
# P3: Java new Random(55555) nextInt chain model e (increments), page 40, continuing from previous rune
s=ps[40]; n=len(lpdata.unsolved()[0][40]['idx'])
inc=vg(16,5,n,55555); c=int(C[s-1])
for i in range(n): c=(c+inc[i])%29; C[s+i]=c
plants.append(dict(name='P3 Java Random(55555) nextInt model e chain increments, page 40',idiom=16,model=5,seedlab='int:55555',stat='exact',pos=int(s),j=0,len=n))
# P4: numpy RandomState(66666).randint model a, gen offset 2000, page 45
s=ps[45]; n=len(lpdata.unsolved()[0][45]['idx'])
g=vg(5,0,2000+n,66666)[2000:]; C[s:s+n]=g
plants.append(dict(name='P4 numpy RandomState(66666) randint model a, gen offset 2000, page 45',idiom=5,model=0,seedlab='int:66666',stat='exact',pos=int(s),j=2000,len=n))
prep.make(C, L+'/ctrl/corpus_ctrl.bin')
json.dump(plants,open(L+'/ctrl/plants.json','w'),indent=1)
# control seed list: all string seeds + ints 50000..80000
lines=[l for l in open(L+'/seeds_all.txt') if l[0] in 'KJ' or (l[0]=='I' and 50000<=int(l.split()[1])<=80000)]
open(L+'/ctrl/seeds_ctrl.txt','w').writelines(lines); print(len(lines),'control seeds')
