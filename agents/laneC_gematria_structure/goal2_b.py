import sys, re, math, pickle
sys.path.insert(0,'.')
import numpy as np
from collections import Counter
import eng
exec(open('goal2_wl.py').read().split('# ---------- reference corpora')[0].split('# ---------- per-page heterogeneity ----------')[0])  # loads st,c,d,wl_all,cnt,dist,base
S=eng.S; DL=S+'/dl/dukotah/liber-primus/'; K=DL+'data/keys/'
rng=np.random.default_rng(5)
N=len(wl_all)
def js(p,q):
    m=(p+q)/2
    kl=lambda a,b:sum(x*math.log(x/y) for x,y in zip(a,b) if x>0)
    return (kl(p,m)+kl(q,m))/2
def mc_p(q,reps=4000):
    """p-value of observed JS(base,q) vs JS of N-word multinomial samples from q"""
    obs=js(base,q); q=np.asarray(q); q=q/q.sum()
    k=0; vals=[]
    for _ in range(reps):
        s=rng.multinomial(N,q)/N; vals.append(js(s,q))
    vals=np.array(vals)
    return obs,(vals>=obs).mean(),vals.mean()
# --- hypotheses table
DIGS=['TH','EO','OE','AE','EA','NG','IA']
def units(w,scheme):
    w=w.upper().replace('K','C').replace('V','U').replace('Q','C').replace('Z','S')
    w=re.sub('[^A-Z]','',w); i=0;n=0
    while i<len(w):
        if scheme=='cicada' and w[i:i+3]=='ING': i+=3
        elif scheme=='cicada' and w[i:i+2]=='IO': i+=2
        elif scheme=='cicada' and w[i:i+2] in DIGS: i+=2
        elif scheme=='th_only' and w[i:i+2]=='TH': i+=2
        else: i+=1
        n+=1
    return n
def read(path,start=0,end=None):
    t=open(path,encoding='utf-8',errors='ignore').read()[start:end]
    return [w.upper() for w in re.findall(r"[A-Za-z]+",t)]
ENG={'Moby Dick':read(K+'armada18/melville_moby_dick.txt',5000,900000),
 'Plato Republic':read(K+'armada18/plato_republic_jowett.txt',20000,900000),
 'Emerson':read(K+'armada18/emerson_essays_first_series.txt',3000,900000),
 'Poe tales':read(K+'armada18/poe_tales_vol2.txt',3000,900000),
 'KJV':read(DL+'analysis/bookcipher/books/kjv.txt',5000,2000000),
 'Cicero Tusc (Engl. transl.)':read(K+'armada19/cicero_tusculan_disputations.txt',3000,900000),
 'Suetonius (Engl. transl.)':read(K+'armada19/suetonius_twelve_caesars.txt',3000,900000),
 'Paine Age of Reason':read(K+'armada19/paine_age_of_reason.txt',3000,900000),
 'Mill On Liberty':read(K+'armada19/mill_on_liberty.txt',3000,900000),
 'Bacon Novum Organum':read(K+'armada19/bacon_novum_organum.txt',3000,900000),
 'Agrippa OP1':read(K+'armada18/agrippa_occult_philosophy_book1_1651jf.txt',3000,900000)}
HYP=[('Cicada rules (digraph merged, ING/IO)','cicada',set()),
     ('  ... minus THE','cicada',{'THE'}),
     ('  ... minus THE/OF/TO','cicada',{'THE','OF','TO'}),
     ('  ... minus THE/OF/TO/A','cicada',{'THE','OF','TO','A'}),
     ('  ... minus THE/OF/TO/AND','cicada',{'THE','OF','TO','AND'}),
     ('letter-by-letter (no digraph runes)','letters',set()),
     ('letters, minus THE','letters',{'THE'}),
     ('TH-only merged','th_only',set()),
     ('TH-only merged minus THE/OF/TO','th_only',{'THE','OF','TO'})]
print('%-40s %-28s %7s %7s %6s %6s %5s'%('hypothesis','corpus','JS','p(MC)','f2','f3','mean'))
tab={}
for hn,sch,fs in HYP:
    for cn,words in ENG.items():
        cc=Counter(units(w,sch) for w in words if w not in fs)
        cc.pop(0,None); q=dist(cc)
        obs,p,fl=mc_p(q,1500)
        tab[(hn,cn)]=(obs,p,fl,q[1],q[2],sum(k*v for k,v in cc.items())/sum(cc.values()))
for hn,_,_ in HYP:
    vals=[(cn,tab[(hn,cn)]) for cn in ENG]
    best=min(vals,key=lambda x:x[1][0])
    med=np.median([v[1][0] for v in vals])
    print('%-40s best: %-22s JS=%.4f p=%.3f (noise floor JS %.4f) f2=%.3f f3=%.3f mean=%.2f | median JS over %d corpora=%.4f ; #corpora p>0.05: %d'%(hn,best[0],best[1][0],best[1][1],best[1][2],best[1][3],best[1][4],best[1][5],len(ENG),med,sum(1 for v in vals if v[1][1]>0.05)))
# --- Cicada's own solved pages: function-word content
P=pickle.load(open('solved.pkl','rb'))
sw=[''.join(eng.TR[i] for i in w) for p in P for w in p['pw']]
cs=Counter(sw); tot=len(sw)
print('\nCicada solved pages: %d words; THE=%d (%.1f%%) OF=%d TO=%d A=%d AND=%d'%(tot,cs['THE'],100*cs['THE']/tot,cs['OF'],cs['TO'],cs['A'],cs['AND']))
for nm,fs in [('none',set()),('THE/OF/TO',{'THE','OF','TO'})]:
    cc=Counter(len(w) for p in P for w in p['pw'] if ''.join(eng.TR[i] for i in w) not in fs)
    q=dist(cc); print('  solved pages minus',nm,'n=',sum(cc.values()),'f2=%.3f f3=%.3f'%(q[1],q[2]),'JS vs unsolved=%.4f'%js(base,q))
# fraction of tokens in English prose that are THE/OF/TO
for cn in ('Moby Dick','Plato Republic','Emerson'):
    w=ENG[cn]; c2=Counter(w); T=len(w)
    print('  %s: THE %.1f%% OF %.1f%% TO %.1f%% (sum %.1f%%)'%(cn,100*c2['THE']/T,100*c2['OF']/T,100*c2['TO']/T,100*(c2['THE']+c2['OF']+c2['TO'])/T))
pickle.dump(tab,open('goal2_tab.pkl','wb'))
