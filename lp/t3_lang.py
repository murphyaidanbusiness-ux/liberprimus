import lpdata, re, math, unicodedata
from collections import Counter
DL=lpdata.DL
U,C,h=lpdata.unsolved()
# unsolved word lengths (runes)
wl=Counter()
for p in U:
    for w,n in Counter(p['word']).items(): wl[n]+=1
def profile(cnt, label):
    tot=sum(cnt.values()); mean=sum(k*v for k,v in cnt.items())/tot
    dist=[cnt.get(k,0)/tot for k in range(1,11)]; dist.append(sum(v for k,v in cnt.items() if k>10)/tot)
    return label,tot,mean,dist
DIG=['TH','NG','EA','EO','OE','AE','IO','IA']
def to_runes(word):
    """English/Latin word -> GP rune count using Cicada's lossy rules"""
    w=word.upper().replace('K','C').replace('V','U').replace('Q','C').replace('Z','S')
    w=w.replace('Æ','AE').replace('Œ','OE').replace('Þ','TH').replace('Ð','TH').replace('Ƿ','W')
    w=re.sub('[^A-Z]','',w)
    i=0;n=0
    while i<len(w):
        if w[i:i+2] in DIG: i+=2
        else: i+=1
        n+=1
    return n
def corpus_profile(path, label, start=0, end=None, oe=False):
    txt=open(path,encoding='utf-8',errors='ignore').read()[start:end]
    if oe:  # keep only lines containing OE-specific letters to drop English front matter
        txt='\n'.join(l for l in txt.split('\n') if re.search('[þðæÞÐÆ]',l))
    words=re.findall(r"[A-Za-zÆæŒœÞþÐðƿ]+",txt)
    cnt=Counter(to_runes(w) for w in words); cnt.pop(0,None)
    return profile(cnt,label)
rows=[profile(wl,'UNSOLVED LP2 (runes)')]
# solved LP pages from scream314 (runes with • separators)
md=open(DL+'/dukotah/liber-primus/data/scream314_lp.md',encoding='utf-8').read()
solved_words=Counter()
lp1=md[md.index('## Runes - 01.jpg'):md.index('## 17.jpg')]
for blk in re.findall(r"((?:[ᚠ-᛿•\-\s]){40,})",lp1):
    for w in re.split(r"[•\-\s]+",blk):
        n=sum(1 for ch in w if ch in lpdata.R2I)
        if n: solved_words[n]+=1
rows.append(profile(solved_words,'LP1 pages 01-16 (mostly solved, Cicada English)'))
K=DL+'/dukotah/liber-primus/data/keys/'
rows.append(corpus_profile(K+'armada18/melville_moby_dick.txt','English: Moby Dick',5000,900000))
rows.append(corpus_profile(K+'armada18/plato_republic_jowett.txt','English: Plato Republic (Jowett)',20000,900000))
rows.append(corpus_profile(DL+'/dukotah/liber-primus/analysis/bookcipher/books/kjv.txt','English: KJV Bible',5000,2000000))
rows.append(corpus_profile(K+'armada19/kant_critique_pure_reason.txt','English: Kant CPR (transl.)',20000,900000))
rows.append(corpus_profile(DL+'/dukotah/liber-primus/analysis/latin/latin_28233.txt','Latin: Newton Principia',20000,700000))
rows.append(corpus_profile('./corp/caesar.txt','Latin: Caesar BG I',600))
rows.append(corpus_profile(DL+'/dukotah/liber-primus/analysis/round10b/B6-non-english-plaintext/corpora/oe_beowulf.txt','Old English: Beowulf',0,None,oe=True))
rows.append(corpus_profile(DL+'/dukotah/liber-primus/analysis/round10b/B6-non-english-plaintext/corpora/de_faust.txt','German: Faust',5000))
def js(p,q):
    m=[(a+b)/2 for a,b in zip(p,q)]
    kl=lambda a,b: sum(x*math.log(x/y) for x,y in zip(a,b) if x>0)
    return (kl(p,m)+kl(q,m))/2
base=rows[0][3]
print("%-45s %6s %5s  "%('corpus','words','mean')+' '.join('%4d'%k for k in range(1,11))+'  11+   JS-div vs unsolved')
for label,tot,mean,dist in rows:
    print("%-45s %6d %5.2f  "%(label,tot,mean)+' '.join('%4.1f'%(100*d) for d in dist)+'   %.4f'%js(base,dist))
# Also: distribution of first-rune-of-word and last-rune-of-word in unsolved (should be flat if cipher is flat)
