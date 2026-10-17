import io,contextlib,random
with contextlib.redirect_stdout(io.StringIO()):
    from eng import P
import collections
R=random.Random(11)
N=29
def rep(name,c):
    L=len(c)
    d1=sum(a==b for a,b in zip(c,c[1:]))/(L-1); d2=sum(a==b for a,b in zip(c,c[2:]))/(L-2)
    f=collections.Counter(c); ioc=sum(v*v for v in f.values())/L/L*N
    pairs=collections.Counter(zip(c,c[1:])); first=collections.Counter(c[:-1])
    cioc=sum(v*v/first[a] for (a,b),v in pairs.items())/(L-1)*N
    print(f"{name:46s} dbl={d1*100:6.3f}%  lag2={d2*N:5.3f}  IoC={ioc:5.3f} condIoC={cioc:5.3f}")
L=len(P)
rep('plaintext (runic English)',P)
rep('Vigenere period 8',[ (p+k)%N for p,k in zip(P,[R.randrange(N) for _ in range(8)]*(L//8+1))])
rep('flat random running key',[(p+R.randrange(N))%N for p in P])
rep('Trithemius c=p+i',[(p+i)%N for i,p in enumerate(P)])
rep('plaintext autokey c=p+p[i-1]',[(P[i]+P[i-1])%N for i in range(1,L)])
rep('plaintext autokey lag2 c=p+p[i-2]',[(P[i]+P[i-2])%N for i in range(2,L)])
c=[R.randrange(N)]
for p in P: c.append((p+c[-1])%N)
rep('ciphertext autokey c=p+c[i-1]',c)
rep('CT autokey + flat key c=p+k+c[i-1]',[x for x in (lambda: (lambda c: c)([0]))()] and (lambda: (lambda cc:[cc.append((p+R.randrange(N)+cc[-1])%N) for p in P] and cc)([R.randrange(N)]))())
rep('difference c=p[i]-p[i-1]',[(P[i]-P[i-1])%N for i in range(1,L)])
rep('Gronsfeld random digit key len 9',[ (p+k)%N for p,k in zip(P,[R.randrange(10) for _ in range(9)]*(L//9+1))])
# flat key with nonzero-increment feedback: c_i=c_{i-1}+s_i, s_i=p_i+k_i skipping zero (key advance)
c=[R.randrange(N)]; skips=0
for p in P:
    while True:
        s=(p+R.randrange(N))%N
        if s!=0: break
        skips+=1
    c.append((c[-1]+s)%N)
rep('chain, key-skip until s!=0 (exact)',c)
# soft key-skip: rule enforced with prob q
for q in (0.81,0.84):
    c=[R.randrange(N)]
    for p in P:
        s=(p+R.randrange(N))%N
        if s==0 and R.random()<q: s=(p+R.randrange(N))%N
        c.append((c[-1]+s)%N)
    rep(f'chain, single retry w.p. {q}',c)
# flat cipher + single-retry rule on ciphertext (advance key if c==prev)
c=[R.randrange(N)]
for p in P:
    x=(p+R.randrange(N))%N
    if x==c[-1]: x=(p+R.randrange(N))%N
    c.append(x)
rep('flat Vernam, one key-advance on repeat',c)
# Chaocipher on English
from sim2 import chao
rep('Chaocipher-29 on runic English',chao(N,P))
