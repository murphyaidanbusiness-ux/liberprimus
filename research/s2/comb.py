import re,glob,numpy as np,random
txt=""
for f in glob.glob('/usr/share/common-licenses/*')+glob.glob('/usr/lib/python3*/LICENSE.txt'):
    try: txt+=open(f,errors='ignore').read()
    except: pass
t=np.array([ord(c)-65 for c in re.sub('[^A-Z]','',txt.upper())])
N=26; n=len(t); print("n",n)
def ioc(z):
    c=np.bincount(z,minlength=N); m=len(z); return (c*(c-1)).sum()/(m*(m-1))*N
print("unigram",ioc(t))
for a in (1,2,3,5,10):
    print("p_i - p_{i-%d}"%a, round(ioc((t[a:]-t[:-a])%N),3), " p_i-3p_{i-a}",round(ioc((t[a:]-3*t[:-a])%N),3))
for a,b in ((1,2),(1,3),(2,5),(3,7)):
    z=(t[b:]-t[b-a:-a if a else None][:len(t)-b]-t[:-b])%N if False else (t[b:]-t[b-a:n-a]-t[:n-b])%N
    print("p_i-p_{i-%d}-p_{i-%d}"%(a,b), round(ioc(z),3))
print("sd of null at this n ~", np.sqrt(2*(N-1)/n))
