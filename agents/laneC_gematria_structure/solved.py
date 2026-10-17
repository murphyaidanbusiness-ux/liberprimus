"""Build solved-page corpus: for each solved LP1 page: cipher words, plaintext words (rune indices)."""
import sys, re
S='.'
sys.path.insert(0,S+'/lp')
import lpdata
R2I=lpdata.R2I; TR=lpdata.TR
DL=lpdata.DL
md=open(DL+'/dukotah/liber-primus/data/scream314_lp.md',encoding='utf-8').read().split('\n')
# sections
secs=[];cur=None
for ln in md:
    if ln.startswith('## '): cur=[ln[3:],[]]; secs.append(cur)
    elif cur is not None: cur[1].append(ln)
def runeblocks(lines):
    out=[]
    for ln in lines:
        s=ln.strip().replace('"','').replace("'",'').replace('“','').replace('”','').replace(',','•').replace(':','•').replace('.','•')
        if s and all((c in R2I) or c in '•- ' for c in s) and any(c in R2I for c in s):
            out.append(s)
    return out
def words_of(lines):
    ws=[]
    for s in lines:
        for w in re.split(r'[•\- ]+',s):
            if w: ws.append([R2I[c] for c in w])
        # line-break doesn't necessarily end a word; but in these blocks lines end at word ends mostly
    return ws
def getsec(prefix):
    for t,l in secs:
        if t.startswith(prefix): return runeblocks(l)
    return []

sys.path.insert(0,DL+'/dukotah/liber-primus/src')
from lp import score as _score
SC=_score.default()
def kw(s):
    s=s.replace('V','U').replace('K','C');r=[];i=0
    while i<len(s):
        for L in (2,1):
            if s[i:i+L] in TR: r.append(TR.index(s[i:i+L])); i+=L; break
        else: raise ValueError(s)
    return r
def primes(n):
    ps=[];c=2
    while len(ps)<n:
        if all(c%p for p in ps if p*p<=c): ps.append(c)
        c+=1
    return ps
PR=primes(2000)
def flat(words): return [(wi,c) for wi,w in enumerate(words) for c in w]
def decode_beam(words, keyfn, sign, atbash=False, beam=400):
    """beam over F-interrupt decisions; returns plaintext words (idx lists, with F interrupts kept as 0)."""
    seq=flat(words)
    beams=[(0,[])]  # (j, list of (wi,p))
    def tr(lst): return ''.join(TR[p] for _,p in lst)
    for wi,c in seq:
        if atbash: cc=28-c
        else: cc=c
        new=[]
        for j,dec in beams:
            p=(cc+sign*keyfn(j))%29
            new.append((j+1,dec+[(wi,p)]))
            if c==0: new.append((j,dec+[(wi,0)]))   # null F, key not consumed
        if c==0 and len(new)>beam:
            new.sort(key=lambda b:SC.score(tr(b[1][-60:])),reverse=True); new=new[:beam]
        beams=new
    beams.sort(key=lambda b:SC.score(tr(b[1])),reverse=True)
    dec=beams[0][1]
    out=[[] for _ in words]
    for wi,p in dec: out[wi].append(p)
    return out, SC.score_norm(tr(dec))
def best_simple(words):
    best=None
    for atb in (0,1):
        for sh in range(29):
            for sg in (1,-1):
                pw=[[((28-c if atb else c)+sg*sh)%29 for c in w] for w in words]
                sc=SC.score_norm(''.join(TR[i] for w in pw for i in w))
                if best is None or sc>best[0]: best=(sc,pw,(atb,sh,sg))
    return best
def build():
    pages=[]
    def add(name,blocks,mode,key=None):
        ws=words_of(blocks)
        if mode=='simple':
            sc,pw,info=best_simple(ws)
        else:
            if mode=='vig':
                kk=kw(key); fn=lambda j:kk[j%len(kk)]
            else:
                fn=lambda j:(PR[j]-1)%29
            r=None
            for sg in (-1,1):
                o=decode_beam(ws,fn,sg)
                if r is None or o[1]>r[1]: r=o
            pw,sc=r; info=mode
        pages.append(dict(name=name,cw=ws,pw=pw,score=sc,info=info))
    add('01',getsec('Runes - 01'),'simple')
    add('03-04',getsec('03.jpg')+getsec('04.jpg'),'vig','DIVINITY')
    add('05',getsec('05.jpg'),'simple')
    add('06-09',getsec('06.jpg')+getsec('07.jpg')+getsec('08.jpg')+getsec('09.jpg'),'simple')
    add('10-13',getsec('10.jpg')+getsec('11.jpg')+getsec('12.jpg')+getsec('13.jpg'),'simple')
    add('14-15',getsec('14.jpg')+getsec('15.jpg'),'vig','FIRFUMFERENFE')
    add('16',getsec('16.jpg'),'simple')
    add('73',getsec('73.jpg'),'phi')
    add('74',getsec('74.jpg'),'simple')
    return pages
if __name__=='__main__':
    import pickle
    P=build()
    pickle.dump(P,open('solved.pkl','wb'))
    for p in P:
        print(p['name'],len(p['cw']),sum(len(w) for w in p['cw']),round(p['score'],2),p['info'])
        print(' '.join(''.join(TR[i] for i in w) for w in p['pw'])[:400])
