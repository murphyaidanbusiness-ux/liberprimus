import io,contextlib,random,math,collections
with contextlib.redirect_stdout(io.StringIO()):
    from sim import stats,R
N=29
L=300000
# Playfair-like 5x6 grid with 30 cells (29 symbols + 1 null), digraph rules; random plaintext digraphs of distinct letters
rows,cols=5,6
cells=list(range(30)); R.shuffle(cells)  # value 29 = null
pos={v:(i//cols,i%cols) for i,v in enumerate(cells)}
def enc(a,b):
    (r1,c1),(r2,c2)=pos[a],pos[b]
    if r1==r2: return cells[r1*cols+(c1+1)%cols],cells[r2*cols+(c2+1)%cols]
    if c1==c2: return cells[((r1+1)%rows)*cols+c1],cells[((r2+1)%rows)*cols+c2]
    return cells[r1*cols+c2],cells[r2*cols+c1]
out=[]
while len(out)<L:
    a=R.randrange(30);b=R.randrange(30)
    if a==b: continue
    x,y=enc(a,b); out+=[x,y]
d=[sum(out[i]==out[i-1] for i in range(1,len(out)) if i%2==par)/(len(out)//2) for par in (0,1)]
print(f"Playfair 5x6 (30 cells): doublets within digraph {d[1]*100:.3f}%, across digraph {d[0]*100:.3f}%, overall {(d[0]+d[1])/2*100:.3f}% (1/30={100/30:.3f}%)")
# Tetris 7-bag analog with 29 symbols = concat perms (done). TGM history-4 randomizer analog: avoid last k outputs
def hist(k,L):
    h=[];s=[]
    for _ in range(L):
        while True:
            x=R.randrange(N)
            if x not in h: break
        s.append(x); h.append(x); h=h[-k:]
    return s
stats(hist(1,L),'avoid-last-1 (exact Markov)')
stats(hist(4,L),'avoid-last-4 (TGM-style history)')
# LCGs
def lcg(m,a,c,x0,L,out=lambda x:x%29):
    x=x0; s=[]
    for _ in range(L):
        x=(a*x+c)%m; s.append(out(x))
    return s
stats(lcg(2**31,1103515245,12345,1,L),'LCG glibc-ish mod 2^31, output mod 29')
stats(lcg(2**31-1,16807,0,1,L),'MINSTD (Lehmer) mod 29')
stats(lcg(2**32,1664525,1013904223,1,L),'LCG NR mod 2^32, mod 29')
stats(lcg(2**32,1664525,1013904223,1,L,out=lambda x:(x>>16)%29),'LCG NR mod 2^32, (x>>16) mod 29')
# LCG mod 29 with a!=1: exact zero doublets but periodic
s=lcg(29,2,5,3,60); print('LCG mod 29 a=2: first 60',s[:30],'period',next(p for p in range(1,60) if s[p:p+10]==s[:10]) ,'doublets',sum(a==b for a,b in zip(s,s[1:])))
# multiplicative chain x_{n+1}=a x_n mod 29: periods
ords={a:next(k for k in range(1,29) if pow(a,k,29)==1) for a in range(2,29)}
print('multiplicative orders mod 29:',sorted(set(ords.values())))
# lagged fibonacci mod 29 (additive, lags 24,55) 
def lfg(j,k,L):
    s=[R.randrange(N) for _ in range(k)]
    for i in range(k,L+k): s.append((s[i-j]+s[i-k])%N)
    return s[k:]
stats(lfg(24,55,L),'additive LFG(24,55) mod 29')
stats(lfg(1,2,L),'Fibonacci x_n=x_{n-1}+x_{n-2} (random seed)') if False else None
# random walk on K29 with PRNG = nonzero chain, increments from random but k restricted
s=[0]
for _ in range(L): s.append((s[-1]+R.randrange(1,N))%N)
stats(s,'chain: increments uniform nonzero')
# golden-ratio additive recurrence
phi=(math.sqrt(5)-1)/2
stats([int(((i*phi)%1)*29) for i in range(L)],'Kronecker golden ratio floor(29*frac(n*phi))')
# x_{n+1}=a_n x_n multiplicative chain with a_n random !=1 (GF(29)*)
s=[R.randrange(1,N)]
for _ in range(L): s.append((s[-1]*R.randrange(2,N))%N)
stats(s,'GF(29) mult chain, a_n random !=0,1 (no zero sym)')
