import lpdata, math, random
from collections import Counter
U,C,h=lpdata.unsolved(); N=len(C)
# global fields aligned to C
word=[w for p in U for w in p['word']]; line=[l for p in U for l in p['line']]; page=[p['page'] for p in U for _ in p['idx']]
sent=[s for p in U for s in p['sent']]; chap=[c for p in U for c in p['chap']]
D=[(C[i]-C[i-1])%29 for i in range(1,N)]   # increment stream, D[i-1] belongs to position i
def ioc(x,m=29):
    c=Counter(x); n=len(x); return sum(v*(v-1) for v in c.values())/(n*(n-1))*m
print("N=%d doublets=%d rate=%.4f  IoC(C)=%.3f IoC(D nonzero, m=28)=%.3f"%(N,D.count(0),D.count(0)/len(D),ioc(C),ioc([d for d in D if d],28)))
# --- T4: doublet positions
dpos=[i for i in range(1,N) if C[i]==C[i-1]]
gaps=[b-a for a,b in zip(dpos,dpos[1:])]
print("doublet gaps: mean %.1f sd %.1f min %d max %d (geometric expectation mean %.1f sd %.1f)"%(sum(gaps)/len(gaps),(sum((g-sum(gaps)/len(gaps))**2 for g in gaps)/len(gaps))**.5,min(gaps),max(gaps),N/86,N/86))
print("doubled runes in order:", ''.join(lpdata.TR[C[i]] for i in dpos))
print("doublet rune counts:", sorted(Counter(C[i] for i in dpos).items()))
# word position of the doublet's 2nd rune and word length
wp=[]; 
for i in dpos:
    w=word[i]; start=i
    while start>0 and word[start-1]==w: start-=1
    end=i
    while end+1<N and word[end+1]==w: end+=1
    wp.append((i-start,end-start+1))
print("doublet (pos in word, word len):", Counter(wp).most_common(12))
print("doublets at word boundary (2nd rune starts a word): %d of %d"%(sum(1 for i in dpos if word[i]!=word[i-1]),len(dpos)))
# --- T3: locality of increments: coincidence rate of D at lag k within same word / line / page vs across
def coinc(lag, same):
    a=b=0
    for i in range(1,N-lag):
        j=i+lag
        if same(i,j):
            a+=1; b+= (D[i-1]==D[j-1])
    return b/a if a else float('nan'), a
print("lag-k coincidence of increments (expect 1/29=0.0345 if key aperiodic; ~0.06 if key constant over the unit)")
for lag in range(1,9):
    rw,nw=coinc(lag, lambda i,j: word[i]==word[j]); rl,nl=coinc(lag, lambda i,j: line[i]==line[j]); rx,nx=coinc(lag, lambda i,j: word[i]!=word[j])
    print(" lag %d: within-word %.4f (n=%d)  within-line %.4f (n=%d)  across-word %.4f (n=%d)"%(lag,rw,nw,rl,nl,rx,nx))
# all pairs within same word / same line / same page: coincidence rate of D (IoC-like)
def pair_rate(unit):
    groups={}
    for i in range(1,N): groups.setdefault(unit[i],[]).append(D[i-1])
    num=den=0
    for g in groups.values():
        c=Counter(g); n=len(g); num+=sum(v*(v-1) for v in c.values()); den+=n*(n-1)
    return num/den
for name,unit in (('word',word),('line',line),('sentence',sent),('page',page),('chapter',chap)):
    print(" all-pairs coincidence of increments within same %-8s: %.4f"%(name,pair_rate(unit)))
# same for raw C (per-unit constant additive key => high)
def pair_rateC(unit):
    groups={}
    for i in range(N): groups.setdefault(unit[i],[]).append(C[i])
    num=den=0
    for g in groups.values():
        c=Counter(g); n=len(g); num+=sum(v*(v-1) for v in c.values()); den+=n*(n-1)
    return num/den
for name,unit in (('word',word),('line',line),('page',page)):
    print(" all-pairs coincidence of RAW runes within same %-8s: %.4f"%(name,pair_rateC(unit)))
# --- T1: periodic IoC on D (nonzero only, keep alignment by position) and kappa autocorr on D
print("periodic coset-IoC on increments D (m=28, zeros dropped): top periods 1..1500")
def coset_ioc(x, L):
    tot=0; cnt=0
    for j in range(L):
        col=[v for v in x[j::L] if v!=0]
        if len(col)>1:
            c=Counter(col); n=len(col); tot+=sum(v*(v-1) for v in c.values())/(n*(n-1))*28; cnt+=1
    return tot/cnt
res=sorted(((coset_ioc(D,L),L) for L in range(1,1501)),reverse=True)
print(" ",[(round(v,3),L) for v,L in res[:12]])
random.seed(3); R=[random.randrange(29) for _ in range(len(D))]
resR=sorted(((coset_ioc(R,L),L) for L in range(1,1501)),reverse=True); print("  null (random):",[(round(v,3),L) for v,L in resR[:5]])
def kappa(x,lag): n=len(x)-lag; return sum(1 for i in range(n) if x[i]==x[i+lag])/n
ks=sorted(((kappa(D,lag),lag) for lag in range(1,2001)),reverse=True); print("kappa on D top lags:",[(round(v,4),l) for v,l in ks[:10]])
ksC=sorted(((kappa(C,lag),lag) for lag in range(1,2001)),reverse=True); print("kappa on C top lags:",[(round(v,4),l) for v,l in ksC[:10]])
print("binomial sd for kappa at n~12000: %.4f"%( (1/29*28/29/12000)**.5))
