import random, collections
from sim import stats, R
N=29
L=300000
def chao(n, pt):
    left=list(range(n)); right=list(range(n)); R.shuffle(left); R.shuffle(right)
    out=[]
    for p in pt:
        # Byrne: find plaintext in RIGHT, cipher is at same position in LEFT
        k=right.index(p); c=left[k]; out.append(c)
        # permute left: rotate so c at zenith(0); then move letter at pos1 to nadir (n//2)
        left=left[k:]+left[:k]
        x=left.pop(1); left.insert(n//2,x)
        # right: rotate so p at zenith, then rotate 1 more, then take pos 2 to nadir
        right=right[k:]+right[:k]
        right=right[1:]+right[:1]
        x=right.pop(2); right.insert(n//2,x)
    return out
pt=[R.randrange(N) for _ in range(L)]
c=chao(N,pt)
stats(c,'Chaocipher-29 (random flat plaintext)')
# with English-like plaintext doublets: plaintext with 3% doublets
pt2=[R.randrange(N)]
for _ in range(L-1):
    pt2.append(pt2[-1] if R.random()<0.03 else R.randrange(N))
stats(chao(N,pt2),'Chaocipher-29 (plaintext 3% doublets)')
# pt/ct 'hit' distances
c=chao(N,pt2)
print('pt==ct rate',sum(a==b for a,b in zip(pt2,c))/L*N)
