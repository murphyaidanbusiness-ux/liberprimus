import random, math, collections, sys
N=29
def stats(seq,name,n=29):
    L=len(seq)
    d=[sum(seq[i]==seq[i-k] for i in range(k,L))/(L-k) for k in (1,2,3,4,5)]
    # conditional IoC of next given prev: sum over (a,b) P(b|a)^2 weighted
    pairs=collections.Counter(zip(seq,seq[1:])); first=collections.Counter(seq[:-1])
    cioc=sum(c*c/first[a] for (a,b),c in pairs.items())/(L-1)*n
    # flatness
    f=collections.Counter(seq); ioc=sum(v*v for v in f.values())/L/L*n
    print(f"{name:42s} dbl={d[0]*100:6.3f}%  lag2={d[1]*n:5.3f} lag3={d[2]*n:5.3f} lag5={d[4]*n:5.3f}  IoC={ioc:5.3f} condIoC={cioc:5.3f}")
    return d
R=random.Random(1)
L=400000
# baseline
stats([R.randrange(N) for _ in range(L)],'iid uniform 29')
# concatenated random perms of 29
s=[]
while len(s)<L:
    p=list(range(N)); R.shuffle(p); s+=p
stats(s[:L],'concat random perms of 29')
# RC4-n
def rc4(n,key,drop=0):
    S=list(range(n)); j=0
    for i in range(n):
        j=(j+S[i]+key[i%len(key)])%n; S[i],S[j]=S[j],S[i]
    i=j=0
    while True:
        i=(i+1)%n; j=(j+S[i])%n; S[i],S[j]=S[j],S[i]
        yield S[(S[i]+S[j])%n]
def take(g,k):
    return [next(g) for _ in range(k)]
rs=[]
for t in range(40):
    key=[R.randrange(29) for _ in range(16)]
    g=rc4(29,key); rs+=take(g,10000)
stats(rs,'RC4 on Z29 (S-box size 29)')
rs=[]
for t in range(40):
    key=[R.randrange(256) for _ in range(16)]
    g=rc4(256,key); rs+=[x%29 for x in take(g,10000)]
stats(rs,'RC4-256 output mod 29')
# Spritz
def spritz(n,key):
    S=list(range(n)); st=dict(i=0,j=0,k=0,z=0,a=0,w=1)
    def gcd(a,b):
        while b:a,b=b,a%b
        return a
    # n=29 prime: w must be coprime; w odd requirement of spritz is for 256; use any coprime step
    def update():
        st['i']=(st['i']+st['w'])%n
        y=(st['j']+S[st['i']])%n
        st['j']=(st['k']+S[y])%n
        st['k']=(st['i']+st['k']+S[st['j']])%n
        S[st['i']],S[st['j']]=S[st['j']],S[st['i']]
    def shuffle():
        for _ in range(2*n): update()
        st['w']=(st['w']+2)%n or 1
        while gcd(st['w'],n)!=1: st['w']+=1
        st['a']=0
    # absorb key nibble-ish: absorb each as stop
    for b in key:
        for _ in range(1): 
            if st['a']==n//2: shuffle()
            a=S.index  # placeholder
            x=b%n
            y=st['a']
            S[y],S[(n//2+x)%n]=S[(n//2+x)%n],S[y]; st['a']+=1
    if st['a']: shuffle()
    while True:
        update()
        st['z']=S[(st['j']+S[(st['i']+S[(st['z']+st['k'])%n])%n])%n]
        yield st['z']
rs=[]
for t in range(40):
    g=spritz(29,[R.randrange(29) for _ in range(16)]); rs+=take(g,10000)
stats(rs,'Spritz-like on Z29')
# Solitaire (Pontifex) real, outputs 1..52 -> mod 26 (orig) and mod 29
def solitaire(key_deck=None, outmod=26):
    deck=list(range(1,55)); 
    if key_deck is None: R.shuffle(deck)
    else: deck=key_deck
    A,B=53,54
    while True:
        i=deck.index(A); 
        if i==53: deck=[deck[0],A]+deck[1:53]
        else: deck[i],deck[i+1]=deck[i+1],deck[i]
        i=deck.index(B)
        for _ in range(2):
            if i==53:
                deck=[deck[0],B]+deck[1:53]; i=1
            else:
                deck[i],deck[i+1]=deck[i+1],deck[i]; i+=1
        a,b=sorted((deck.index(A),deck.index(B)))
        deck=deck[b+1:]+deck[a:b+1]+deck[:a]
        c=deck[-1]; c=53 if c in (A,B) else c
        deck=deck[c:53]+deck[:c]+[deck[53]]
        t=deck[0]; t=53 if t in (A,B) else t
        o=deck[t]
        if o in (A,B): continue
        yield o
ss=[];s29=[]
for t in range(40):
    g=solitaire(); v=take(g,10000); ss+=[x%26 for x in v]; s29+=[x%29 for x in v]
stats(ss,'Solitaire keystream mod 26 (n=26)',26)
stats(s29,'Solitaire keystream mod 29 (n=29)')
# Solitaire adjacent-equal in raw 1..52
print('solitaire raw consecutive equal 1..52:', sum(a==b for a,b in zip(v,v[1:]))/len(v)*52)
