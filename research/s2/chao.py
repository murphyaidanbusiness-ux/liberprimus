import random, re, sys, glob, collections
# English-ish text source: python stdlib docs / licenses
txt=""
for f in glob.glob('/usr/share/common-licenses/*')[:6]+glob.glob('/usr/lib/python3*/LICENSE.txt'):
    try: txt+=open(f,errors='ignore').read()
    except: pass
txt=re.sub('[^A-Z]','',txt.upper())
print("plaintext len",len(txt))
def chao(pt,N=26,seed=1):
    r=random.Random(seed)
    A=[chr(65+i) for i in range(N)]
    L=A[:]; R=A[:]; r.shuffle(L); r.shuffle(R)
    out=[]
    for p in pt:
        j=R.index(p); c=L[j]; out.append(c)
        # rotate both so index j is at 0
        L=L[j:]+L[:j]; R=R[j:]+R[:j]
        # left: extract pos1 and insert at pos 13 (nadir=zenith+13)
        x=L.pop(1); L.insert(13,x)
        # right: rotate one more, then extract pos2 insert at 13
        R=R[1:]+R[:1]
        y=R.pop(2); R.insert(13,y)
    return ''.join(out)
def stats(s,N=26):
    n=len(s); cnt=collections.Counter(s)
    ioc=sum(v*(v-1) for v in cnt.values())/(n*(n-1))*N
    dbl=sum(1 for i in range(1,n) if s[i]==s[i-1])/(n-1)
    return ioc,dbl
pt=txt[:60000]
print("PT   ioc*N,dbl",stats(pt), "expect dbl random",1/26)
for seed in (1,2,3):
    ct=chao(pt,seed=seed); print("CHAO",seed,stats(ct))
# also autokey-free control: random
rnd=''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(60000)); print("RND",stats(rnd))
