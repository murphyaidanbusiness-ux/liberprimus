import numpy as np, sys, struct, re, json
sys.path.insert(0,'.')
from common import *
pg=np.load(LANE+'/pg.npy'); wd=np.load(LANE+'/wd.npy'); N=len(pg)
FD=S+'/agents/laneF_wordlength_alignment/fetched/'
def gut(path):
    t=open(path,encoding='utf-8',errors='ignore').read()
    return t[5000:-5000]
def runes_of(t):
    t=re.sub(r'[^A-Za-z]','',t)
    return np.array(eng2runes(t),dtype=np.int64)
bg=runes_of(gut(FD+'walden.txt'))[:N+5000]
kt=runes_of(gut(FD+'leviathan.txt'))[:N+5000]
# planted: koan text, own words
K=DUK+'/data/keys/armada18/lp1_english_forward.txt'
txt=open(K).read()
i0=txt.index('A KOAN\nA MAN DECIDED'); koan=txt[i0:i0+4000].split('\n\n')[0]
koan_words=[w for w in re.sub(r'[^A-Z ]',' ',koan.replace('A KOAN\n','',1)).split()]
pw=[eng2runes(w) for w in koan_words]
# take words until >=500 runes
acc=[];cum=0
for w in pw:
    if cum+len(w)>500: break
    acc.append(w); cum+=len(w)
plant=np.array([r for w in acc for r in w],dtype=np.int64); PL=len(plant)
print('planted runes',PL,'words',len(acc))
# choose region: a word start in a page with PL runes remaining on the page
page_start={}
for i in range(N):
    page_start.setdefault(int(pg[i]),i)
a=page_start[10]
pg_c=pg.copy(); endp=a+PL
while endp<N and pg[endp]==pg[a+PL-1]: endp+=1
pg_c[a-1:endp]=1000
print('plant at',a,'page',int(pg[a]),'region ends',a+PL,'page-merged to',endp)
def encrypt_chain(pl,key):
    c=np.zeros(N,dtype=np.int64); c[0]=7
    for i in range(1,N):
        p=pl[i]
        s=0 if p==28 else 1+((p+(key[i]%28))%28)
        c[i]=(c[i-1]+s)%29
    return c
KW=eng2runes('DIVINITY')
def encrypt_vig_skip(pl,kw=KW):
    c=np.zeros(N,dtype=np.int64); j=0; P=len(kw); prev=-1; ks=[]
    for i in range(N):
        while True:
            cc=(pl[i]+kw[j%P])%29; j+=1
            if cc!=prev: break
        c[i]=cc; prev=cc; ks.append(kw[(j-1)%P])
    return c,np.array(ks)
pl=bg[:N].copy(); pl[a:a+PL]=plant
wd_own=wd.copy()
wid=10**6
k=0
for w in acc:
    wd_own[a+k:a+k+len(w)]=wid; wid+=1; k+=len(w)
def write(path,cc,wdd):
    with open(path,'wb') as f:
        f.write(struct.pack('<i',len(cc))); f.write(cc.astype(np.uint8).tobytes()); f.write(pg_c.astype(np.int16).tobytes()); f.write(wdd.astype(np.int32).tobytes())
cch=encrypt_chain(pl,kt)
ccv,ks=encrypt_vig_skip(pl)
print('chain doublets',int((np.diff(cch)%29==0).sum()),'vig doublets',int((np.diff(ccv)%29==0).sum()), 'vig key advanced by skip',int(len(ks)))
import os; os.makedirs(LANE+'/ctrl',exist_ok=True)
for nm,cc in (('chain',cch),('vig',ccv)):
    write(LANE+'/ctrl/%s_A.bin'%nm,cc,wd_own)   # planted region keeps own words
    write(LANE+'/ctrl/%s_B.bin'%nm,cc,wd)       # LP2 word lengths everywhere
json.dump(dict(a=a,PL=PL,plant=plant.tolist(),words=[len(w) for w in acc]),open(LANE+'/ctrl/truth.json','w'))
np.save(LANE+'/ctrl/pl.npy',pl)
# truth positions for cribs
cribs=json.load(open(LANE+'/cribs.json'))
truth=[]
wst=[]; k=0
for w in acc: wst.append(k); k+=len(w)
wl=[len(w) for w in acc]
plantl=plant.tolist()
for cb in cribs:
    r=cb['runes']; L=len(r)
    if L<4: continue
    for s in range(0,PL-L+1):
        if plantl[s:s+L]==r:
            # aligned?
            al=0
            if s in wst:
                q=wst.index(s)
                if wl[q:q+len(cb['wl'])]==cb['wl']: al=1
            truth.append(dict(crib=cb['id'],pos=a+s,al=al,cls=cb['cls'],alonly=cb['alonly'],L=L,words=' '.join(cb['words'])))
json.dump(truth,open(LANE+'/ctrl/truth_cribs.json','w'))
print('true crib occurrences in planted region:',len(truth),'aligned:',sum(t['al'] for t in truth))
