import sys, re, math, json
sys.path.insert(0,'.')
import numpy as np
from collections import Counter
import eng
S=eng.S; DL=S+'/dl/dukotah/liber-primus/'
st,c=eng.real_struct(); d=eng.Data(c,st)
wl_all=np.bincount(st.word)
wl_all=wl_all[wl_all>0]
print('words',len(wl_all),'runes',wl_all.sum(),'mean',wl_all.mean())
cnt=Counter(wl_all.tolist())
def dist(cnt):
    tot=sum(cnt.values()); v=[cnt.get(k,0)/tot for k in range(1,11)]; v.append(sum(x for k,x in cnt.items() if k>10)/tot); return np.array(v)
base=dist(cnt)
print('unsolved dist 1..10,11+:',np.round(100*base,1))
# ---------- per-page heterogeneity ----------
pages=[]
for p in range(st.page.max()+1):
    ids=st.word[st.page==p]
    # words entirely/partly on page: count by runes on page (words split across pages counted by on-page length)
    cc=Counter(Counter(ids.tolist()).values())
    n=sum(cc.values())
    pages.append((p,n,cc.get(2,0)/n,cc.get(3,0)/n,cc.get(1,0)/n,sum(k*v for k,v in cc.items())/n))
print('page, nwords, f2, f3, f1, mean')
for r in pages: print('%2d %3d %.3f %.3f %.3f %.2f'%r)
f2=np.array([r[2] for r in pages]); n_=np.array([r[1] for r in pages])
# chi-square heterogeneity of the 2-rune share across pages, permutation null
k2=np.array([round(r[2]*r[1]) for r in pages])
pbar=k2.sum()/n_.sum()
chi=((k2-n_*pbar)**2/(n_*pbar*(1-pbar))).sum()
rng=np.random.default_rng(0)
allw=np.concatenate([np.full(r[1],0) for r in pages])
lens=wl_all.copy()  # global word lengths in order (approximately page ordering)
nulls=[]
for _ in range(2000):
    perm=rng.permutation(len(lens)); pos=0; k=[]
    for r in pages:
        seg=lens[perm[pos:pos+r[1]]]; pos+=r[1]; k.append((seg==2).sum())
    k=np.array(k); nulls.append(((k-n_*pbar)**2/(n_*pbar*(1-pbar))).sum())
nulls=np.array(nulls)
print('hetero chi2(2-rune share across 55 pages)=%.1f  df=54  perm-null mean %.1f sd %.1f p=%.3f'%(chi,nulls.mean(),nulls.std(),(nulls>=chi).mean()))
print('pages with f2>=0.22:',[(r[0],round(r[2],3),r[1]) for r in pages if r[2]>=0.22])
print('pooled f2=%.4f, binomial 95%% range per 50-word page: %.3f..%.3f'%(pbar,pbar-1.96*math.sqrt(pbar*(1-pbar)/50),pbar+1.96*math.sqrt(pbar*(1-pbar)/50)))
# sections (leo's 9 sections)
secs=[(0,2),(3,7),(8,14),(15,22),(23,26),(27,32),(33,39),(40,53),(54,54)]
print('section: n words, f1,f2,f3, mean')
for a,b in secs:
    m=(st.page>=a)&(st.page<=b); ids=st.word[m]; l=np.array(list(Counter(ids.tolist()).values()))
    print(a,b,len(l),'%.3f %.3f %.3f %.2f'%((l==1).mean(),(l==2).mean(),(l==3).mean(),l.mean()))
# ---------- reference corpora under transliteration schemes ----------
DIGS=['TH','EO','OE','AE','EA','NG','IA']
def units(w,scheme):
    w=w.upper().replace('K','C').replace('V','U').replace('Q','C').replace('Z','S')
    w=re.sub('[^A-Z]','',w)
    i=0;n=0
    while i<len(w):
        if scheme in('cicada','ing_only') and w[i:i+3]=='ING': i+=3
        elif scheme=='cicada' and w[i:i+2]=='IO': i+=2
        elif scheme in ('cicada','digraph','ing_only') and w[i:i+2] in DIGS and not (w[i:i+2]=='IA' and scheme!='cicada'): i+=2
        elif scheme=='digraph_io' and (w[i:i+2] in DIGS+['IO']): i+=2
        elif scheme=='th_only' and w[i:i+2]=='TH': i+=2
        elif scheme=='th_ng' and w[i:i+2] in('TH','NG'): i+=2
        elif scheme=='th_ing' and (w[i:i+2]=='TH' or w[i:i+3]=='ING'):
            i+= 2 if w[i:i+2]=='TH' else 3
        else: i+=1
        n+=1
    return n
SCHEMES=['letters','th_only','th_ng','th_ing','digraph','digraph_io','ing_only','cicada']
def read(path,start=0,end=None,filt=None):
    t=open(path,encoding='utf-8',errors='ignore').read()[start:end]
    if filt: t=filt(t)
    return re.findall(r"[A-Za-zÆæŒœÞþÐðƿ]+",t)
K=DL+'data/keys/'
CORP={
 'Moby Dick':lambda:read(K+'armada18/melville_moby_dick.txt',5000,900000),
 'Plato Republic':lambda:read(K+'armada18/plato_republic_jowett.txt',20000,900000),
 'KJV':lambda:read(DL+'analysis/bookcipher/books/kjv.txt',5000,2000000),
 'Emerson':lambda:read(K+'armada18/emerson_essays_first_series.txt',3000,900000),
 'Poe tales':lambda:read(K+'armada18/poe_tales_vol2.txt',3000,900000),
 'Hamlet':lambda:read(K+'armada18/shakespeare_hamlet.txt',3000,900000),
 'Lovecraft CoC':lambda:read(K+'armada18/lovecraft_call_of_cthulhu.txt',2000,900000),
 'Crowley Liber777':lambda:read(K+'armada18/crowley_liber777_clean.txt',2000,900000),
 'Agrippa OP1':lambda:read(K+'armada18/agrippa_occult_philosophy_book1_1651jf.txt',3000,900000),
 'Kant CPR':lambda:read(K+'armada19/kant_critique_pure_reason.txt',20000,900000),
 'Latin Newton':lambda:read(DL+'analysis/latin/latin_28233.txt',20000,700000),
 'Latin Virgil':lambda:read(K+'armada19/virgil_aeneid_latin.txt',3000,900000),
 'Latin Cicero Tusc':lambda:read(K+'armada19/cicero_tusculan_disputations.txt',3000,900000),
 'Latin Suetonius':lambda:read(K+'armada19/suetonius_twelve_caesars.txt',3000,900000),
 'Latin Caesar':lambda:read(S+'/corp/caesar.txt',600),
 'German Faust':lambda:read(DL+'analysis/round10b/B6-non-english-plaintext/corpora/de_faust.txt',5000),
 'OE Beowulf (verse)':lambda:[w for w in read(DL+'analysis/round10b/B6-non-english-plaintext/corpora/oe_beowulf.txt') ],
}
# Cicada's own solved pages: use the actual rune counts (words as decrypted)
import pickle
P=pickle.load(open('solved.pkl','rb'))
solved_cnt=Counter(len(w) for p in P for w in p['pw'])
FUNC={'none':set(),'THE':{'THE'},'THE/OF/TO':{'THE','OF','TO'},'THE/OF/TO/A':{'THE','OF','TO','A'},'THE/OF/TO/A/AND/IN/IS/IT':{'THE','OF','TO','A','AND','IN','IS','IT'}}
def js(p,q):
    m=(p+q)/2
    kl=lambda a,b:sum(x*math.log(x/y) for x,y in zip(a,b) if x>0)
    return (kl(p,m)+kl(q,m))/2
def loglik_per_word(q):
    # mean log-likelihood of unsolved word lengths under corpus distribution q (smoothed)
    qq=np.maximum(q,1e-4)
    return float((base*np.log(qq)).sum())
rows=[]
cache={}
for name,fn in CORP.items():
    cache[name]=[w.upper() for w in fn()]
    print('loaded',name,len(cache[name]),flush=True)
print('\nSolved Cicada pages (actual runes): ',np.round(100*dist(solved_cnt),1),'JS vs unsolved %.4f'%js(base,dist(solved_cnt)))
out={}
for name,words in cache.items():
    for sch in SCHEMES:
        for fk,fs in FUNC.items():
            cc=Counter()
            for w in words:
                if w in fs: continue
                u=units(w,sch)
                if u>0: cc[u]+=1
            q=dist(cc)
            out[(name,sch,fk)]=(js(base,q),q[1],q[2],sum(k*v for k,v in cc.items())/sum(cc.values()))
res=sorted(out.items(),key=lambda kv:kv[1][0])
print('\nBest 40 (JS vs unsolved) :')
print('%-22s %-11s %-26s %7s %6s %6s %5s'%('corpus','scheme','removed','JS','f2','f3','mean'))
for (name,sch,fk),(j,f2_,f3_,mn) in res[:40]: print('%-22s %-11s %-26s %7.4f %6.3f %6.3f %5.2f'%(name,sch,fk,j,f2_,f3_,mn))
print('\nUnsolved f2=%.3f f3=%.3f mean=%.2f'%(base[1],base[2],wl_all.mean()))
print('\nPer corpus: JS under each scheme (no word removal) and cicada+THE/OF/TO removed:')
for name in CORP:
    print('%-22s '%name+' '.join('%s=%.4f'%(s,out[(name,s,'none')][0]) for s in SCHEMES)+'  | cicada-THE/OF/TO=%.4f'%out[(name,'cicada','THE/OF/TO')][0])
pickle.dump(out,open('goal2_js.pkl','wb'))
