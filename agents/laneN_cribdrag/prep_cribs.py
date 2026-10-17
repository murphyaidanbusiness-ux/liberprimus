import re, json, collections, sys
sys.path.insert(0,'.')
from common import *
K=DUK+'/data/keys/'
words_alpha=set(w.strip().upper() for w in open(S+'/agents/laneA_keyword_chain/dl/words_alpha.txt'))
def clean(s): return re.sub(r'\s+',' ',re.sub(r"[^A-Z ]",' ',s.upper().replace("'",''))).strip()
# ---- C1 sources
srcs=[]
def addlines(path,tag):
    for line in open(path,errors='replace'):
        l=clean(line)
        if len(l.split())>=1 and l: srcs.append((l,tag))
for f,tag in [('armada18/lp1_english_forward.txt','LP1'),('armada18/cicada_koans_and_lp_sections.txt','LP1b'),
              ('armada18/cicada_pgp_messages.txt','PGPmsg'),('armada18/cicada_2012_2013_puzzle_texts.txt','PUZ')]:
    addlines(K+f,tag)
# PGP cleartext prose: join paragraph, split at sentence/clause punctuation
t=open(S+'/s4/pgp_cleartext_all.txt',errors='replace').read()
for p in t.split('#### '):
    name=p.split('\n')[0]
    if 'hex' in name or 'onion5' in name: continue
    body='\n'.join(p.split('\n')[1:])
    for para in re.split(r'\n\s*\n',body):
        para=' '.join(para.split('\n'))
        for cl in re.split(r'[.!?:;,()\n"]+',para):
            ws=re.findall(r"[A-Za-z]+",cl)
            if len(ws)>=3 and sum(1 for w in ws if w.upper() in words_alpha)>=0.85*len(ws):
                srcs.append((clean(cl),'PGPcl'))
named=["AN INSTRUCTION","COMMAND YOUR OWN SELF","AN INSTRUCTION COMMAND YOUR OWN SELF","DO FOUR UNREASONABLE THINGS EACH DAY",
"PROGRAM YOUR MIND","PROGRAM REALITY","AN INSTRUCTION PROGRAM YOUR MIND PROGRAM REALITY","THE PRIMES ARE SACRED","THE TOTIENT FUNCTION IS SACRED",
"ALL THINGS SHOULD BE ENCRYPTED","WHO ARE YOU WHO WISHES TO STUDY HERE","THE INSTAR","CIRCUMFERENCE","DIVINITY WITHIN",
"FIND THE DIVINITY WITHIN AND EMERGE","LIKE THE INSTAR TUNNELING TO THE SURFACE","WE MUST SHED OUR OWN CIRCUMFERENCES",
"A WARNING","SOME WISDOM","A KOAN","WELCOME","LOSS OF DIVINITY","THE LOSS OF DIVINITY","AN END","PARABLE","INTERCONNECTEDNESS","THREE THREE ZERO ONE",
"LIBER PRIMUS","INTUS","EMERGENCE","INSTAR EMERGENCE","DIVINITY","PILGRIM","WELCOME PILGRIM","THE KEY IS ALL AROUND YOU","GOOD LUCK","PATIENCE IS A VIRTUE"]
for n in named: srcs.append((n,'NAMED'))
lines=[]; seenl=set()
for l,tag in srcs:
    ws=l.split()
    if not ws: continue
    if tag!='NAMED' and (sum(1 for w in ws if w in words_alpha or w in ('A','I'))<0.9*len(ws) or len(ws)>30): continue
    try: r=tuple(eng2runes(l))
    except KeyError: continue
    key=(tuple(len(eng2runes(w)) for w in ws),r)
    if key in seenl: continue
    seenl.add(key); lines.append((ws,tag))
print('C1 phrases (unique lines/clauses/named):',len(lines))
# ---- C2/C3 from English corpora
files=['armada18/melville_moby_dick.txt','armada18/emerson_essays_first_series.txt','armada18/emerson_essays_second_series.txt',
 'armada18/plato_republic_jowett.txt','armada18/poe_complete_works.txt','armada18/homer_odyssey_butler.txt','armada19/aristotle_nicomachean_ethics.txt',
 'armada19/bacon_novum_organum.txt','armada18/kjb_genesis.txt','armada18/kjb_psalms.txt','self_reliance.txt']
uni=collections.Counter(); bi=collections.Counter(); tri=collections.Counter()
for f in files:
    txt=open(K+f,encoding='utf-8',errors='ignore').read().upper()
    toks=[x for x in re.findall(r"[A-Z]+(?:'[A-Z]+)?",txt)]
    toks=[x if "'" not in x else None for x in toks]
    for i,x in enumerate(toks):
        if x is None: continue
        uni[x]+=1
        if i+1<len(toks) and toks[i+1] and True: bi[(x,toks[i+1])]+=1
        if i+2<len(toks) and toks[i+1] and toks[i+2]: tri[(x,toks[i+1],toks[i+2])]+=1
def rl(w): return len(eng2runes(w))
c2=[]; seen=set()
for w,c in uni.most_common():
    if rl(w)>=5:
        r=tuple(eng2runes(w))
        if r in seen: continue
        seen.add(r); c2.append(w)
    if len(c2)==300: break
req=[("OF","THE"),("IN","THE"),("AND","THE"),("IT","IS"),("YOU","ARE")]
bis=[]; seenb=set()
for k,c in req+[k for k,_ in bi.most_common(400)]:
    pass
cand=[k for k in [x for x in req]+[k for k,_ in bi.most_common(600)] if sum(rl(w) for w in k)>=4]
bl=[]; 
for k in cand:
    if k not in bl: bl.append(k)
bl=bl[:130]
tl=[]
for k,_ in tri.most_common(600):
    if sum(rl(w) for w in k)>=4 and k not in tl: tl.append(k)
    if len(tl)==70: break
c3=[' '.join(k) for k in bl+tl]
print('C2',len(c2),c2[:12],'C3',len(c3),c3[:12],c3[-5:])
# ---- assemble crib table
cribs=[]  # dict(cls, alignedonly, words)
seen=set()
def add(words,cls,alonly):
    wl=tuple(len(eng2runes(w)) for w in words); r=tuple(eng2runes(' '.join(words)))
    key=(cls,wl,r)
    if key in seen: return False
    seen.add(key)
    cribs.append(dict(id=len(cribs),cls=cls,alonly=int(alonly),words=list(words),wl=list(wl),runes=list(r)))
    return True
for ws,tag in lines:
    if 4<=len(eng2runes(' '.join(ws)))<=100: add(ws,0,False)
n_full=len(cribs)
# aligned-only contiguous sub-phrases (1..6 words, >=6 runes) of C1 lines
for ws,tag in lines:
    for n in range(1,7):
        for s in range(0,len(ws)-n+1):
            sub=ws[s:s+n]
            if n==len(ws) and s==0: continue
            if sum(len(eng2runes(w)) for w in sub)>=6: add(sub,0,True)
n_c1=len(cribs)
for w in c2: add([w],1,False)
for p in c3: add(p.split(),2,False)
print('cribs total',len(cribs),'C1 full',n_full,'C1 incl subphrases',n_c1)
json.dump(cribs,open(LANE+'/cribs.json','w'))
with open(LANE+'/cribs.txt','w') as f:
    f.write('%d\n'%len(cribs))
    for c in cribs:
        f.write('%d %d %d %d %s %d %s\n'%(c['id'],c['cls'],c['alonly'],len(c['wl']),' '.join(map(str,c['wl'])),len(c['runes']),' '.join(map(str,c['runes']))))
import collections as C
print('len distribution unaligned C1:',sorted(C.Counter(len(c['runes']) for c in cribs if c['cls']==0 and not c['alonly']).items()))
print('C1 aligned-only',sum(1 for c in cribs if c['alonly']),'unaligned total',sum(1 for c in cribs if not c['alonly']))
