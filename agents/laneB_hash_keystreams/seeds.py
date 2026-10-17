import json, re, hashlib, sys
import core
from core import TR, RUNES, SCRATCH, U, lpdata
PRIMES=lpdata.PRIMES
DK=SCRATCH+'/dl/dukotah/liber-primus'
SOLVED=json.load(open(DK+'/SOLVED-PAGES.json'))['pages']
ANEND="36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee09a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f45132c2a8b4"
PGP_FPR="6D854CD7933322A601C3286D181F01E57A35090F"
PGP_KEYID="7A35090F"; PGP_LONG="181F01E57A35090F"
# onion list from dukotah seeds.py (read as text, no import side effects)
_src=open(DK+'/analysis/round13/B04/seeds.py').read()
ONIONS=re.findall(r'"([a-z0-9]{10,24}\.onion)"',_src)
ONIONS=list(dict.fromkeys(ONIONS))
TRL=sorted(TR,key=len,reverse=True)
def parse_translit(s):
    out=[]; i=0
    while i<len(s):
        for t in TRL:
            if s.startswith(t,i): out.append(TR.index(t)); i+=len(t); break
        else: raise ValueError(s[i:i+5])
    return out
def runestr(idx): return ''.join(RUNES[i] for i in idx)
def idxbytes(idx): return bytes(idx)
def translit(idx): return ''.join(TR[i] for i in idx)
def gsum(idx): return sum(PRIMES[i] for i in idx)

def ftext(s):
    out=[]
    for v in (s, s.upper(), s.lower()):
        for nl in ('','\n'):
            out.append((v+nl).encode('utf-8'))
    return out
def fint(n):
    out=[str(n).encode(), (str(n)+'\n').encode()]
    out.append(n.to_bytes(max(1,(n.bit_length()+7)//8),'big'))
    for L in (2,4,8):
        if n < 256**L: out.append(n.to_bytes(L,'big')); out.append(n.to_bytes(L,'little'))
    return out
def fhex(h):
    out=[]
    for v in (h.lower(),h.upper()):
        out.append(v.encode()); out.append((v+'\n').encode())
    raw=bytes.fromhex(h) if len(h)%2==0 else None
    if raw is not None:
        out+= [raw, raw[::-1], raw[:len(raw)//2], raw[len(raw)//2:]]
    out.append(h.lower()[:len(h)//2].encode()); out.append(h.lower()[len(h)//2:].encode())
    return out

SOLVED_IDX=[]
def build_G():
    seeds={}
    def add(label,b):
        if b not in seeds: seeds[b]=label
    def addt(label,s):
        for b in ftext(s): add(label,b)
    for w in ['3301','cicada','cicada3301','liberprimus','liber primus','Liber Primus','LiberPrimus','Cicada 3301','Cicada3301','CICADA 3301',
              'primus','liber','1033','pilgrim','deep web','an end','AN END','divinity','circumference','instar','emergence','parable','welcome','warning',
              'koan','wisdom','totient','primes','sacred','Liber Primus 3301','3301 Liber Primus','Cicada 3301 Liber Primus','gematria primus','Gematria Primus',
              'futhorc','runes','rune','the key','key','password','secret','one time pad','otp','pad','7A35090F','0x7A35090F','Cicada3301Liber Primus','3301cicada','cicada 3301']:
        addt('word',w)
    for n in [3301,1033,761,29,509,503,311,167,845145127,1595277641,2012,2013,2014,2017,3,13,23,2]:
        for b in fint(n): add('num',b)
    # page numbers
    for n in range(0,58):
        for b in fint(n): add('pagenum',b)
        addt('pagenum','%02d'%n); addt('pagenum','%d.jpg'%n); addt('pagenum','%02d.jpg'%n)
        addt('pagenum','page %d'%n); addt('pagenum','Page %d'%n); addt('pagenum','page%d'%n)
    for n in range(1,56): addt('pagenum','page %d'%n)
    # solved pages: titles, texts, runes, gematria sums
    sums=[]
    for p in SOLVED:
        t=p['title']; pt=p['plaintext_transliteration']
        short=re.sub(r'\s*\(.*\)','',t).strip()
        addt('title',t); addt('title',short)
        addt('plaintext',pt)
        idx=parse_translit(pt); SOLVED_IDX.append(idx)
        add('runes',runestr(idx).encode()); add('runes',(runestr(idx)+'\n').encode())
        add('runes',idxbytes(idx)); add('runes',(translit(idx)).encode())
        g=gsum(idx); sums.append(g)
        for b in fint(g): add('gsum',b)
        for b in fint(len(idx)): add('len',b)
    for b in fint(sum(sums)): add('gsum',b)
    for w in ['DIVINITY','FIRFUMFERENFE','CIRCUMFERENCE','THE PRIMES ARE SACRED','THE LOSS OF DIVINITY','AN END','WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO',
              'IT IS THE DUTY OF EUERY PILGRIM TO SEEK OUT THIS PAGE','IT IS THE DUTY OF EVERY PILGRIM TO SEEK OUT THIS PAGE',
              'LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE',
              'PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE WE MUST SHED OUR OWN CIRCUMFERENCES FIND THE DIVINITY WITHIN AND EMERGE',
              'PARABLELIKETHEINSTARTUNNELINGTOTHESURFACEWEMUSTSHEDOUROWNCIRCUMFERENCESFINDTHEDIVINITYWITHINANDEMERGE',
              'THE PATH LIES EMPTY EPIPHANY SEEKS THE DEVOTED','LIBER PRIMUS IS THE WAY','BEWARE FALSE PATHS ALWAYS VERIFY PGP SIGNATURE FROM 7A35090F',
              'WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO '+ANEND]:
        addt('text',w)
    # solved cipher-like pages 55,56 of the loader (AN END, PARABLE ciphertext runes)
    P=lpdata.load()
    for pg in P[55:]:
        i=pg['idx']; add('runes_p%d'%pg['page'],runestr(i).encode()); add('runes_p%d'%pg['page'],idxbytes(i)); add('runes_p%d'%pg['page'],translit(i).encode())
    # hex strings
    for b in fhex(ANEND): add('anend',b)
    for b in fhex(PGP_FPR): add('pgp',b)
    for b in fhex(PGP_KEYID): add('pgp',b)
    for b in fhex(PGP_LONG): add('pgp',b)
    addt('pgp','0x7A35090F'); addt('pgp','0x'+PGP_FPR); addt('pgp',' '.join(PGP_FPR[i:i+4] for i in range(0,40,4)))
    addt('pgp','Cicada 3301 (845145127)'); addt('pgp','845145127')
    for o in ONIONS:
        addt('onion',o); addt('onion',o[:-6])
    return [(lab,b) for b,lab in seeds.items()]

def core_subset(G):
    labs={'word','num','pagenum','title','gsum','len','anend','pgp','onion','text'}
    return [(l,b) for (l,b) in G if l in labs]

# ---------------- page-indexed seed functions
CT=[p['idx'] for p in U]
def build_P():
    fns=[]   # (name, f(p)->bytes)
    pre=['','cicada','cicada3301','3301','liberprimus','liber primus','page','Page','LP','p','Cicada','CICADA']
    seps=['',' ','-','_',':','.']
    for o in (0,1):
        for pr in pre:
            for sp in (seps if pr else ['']):
                for nf in ('dec','z2','jpg'):
                    for nl in ('','\n'):
                        def f(p,pr=pr,sp=sp,nf=nf,nl=nl,o=o):
                            n=p+o
                            s={'dec':str(n),'z2':'%02d'%n,'jpg':'%d.jpg'%n}[nf]
                            return (pr+sp+s+nl).encode()
                        fns.append(('pnum|%s|%s|%s|%s|o%d'%(pr,repr(sp),nf,repr(nl),o),f))
        for suf in ('3301','cicada','cicada3301'):
            for sp in ('',' ','-'):
                fns.append(('psuf|%s|%s|o%d'%(suf,repr(sp),o), (lambda p,suf=suf,sp=sp,o=o: (str(p+o)+sp+suf).encode())))
        for L in (1,2,4,8):
            for end in ('big','little'):
                fns.append(('praw|%d|%s|o%d'%(L,end,o),(lambda p,L=L,end=end,o=o:(p+o).to_bytes(L,end))))
    # ciphertext of previous page
    def prev_forms(kind, step):
        def f(p):
            q=p-step
            idx=CT[q] if q>=0 else []
            if kind=='run': return runestr(idx).encode()
            if kind=='idx': return idxbytes(idx)
            if kind=='trl': return translit(idx).encode()
            if kind=='cum_idx': return idxbytes([x for pg in CT[:p] for x in pg])
            if kind=='cum_run': return runestr([x for pg in CT[:p] for x in pg]).encode()
            if kind=='cum_trl': return translit([x for pg in CT[:p] for x in pg]).encode()
        return f
    for k in ('run','idx','trl'):
        fns.append(('prevct|'+k,prev_forms(k,1)))
        fns.append(('prev2ct|'+k,prev_forms(k,2)))
    for k in ('cum_idx','cum_run','cum_trl'):
        fns.append(('cumct|'+k,prev_forms(k,0)))
    for k in ('run','idx','trl'):
        def own(p,k=k):
            idx=CT[p]
            return {'run':runestr(idx).encode(),'idx':idxbytes(idx),'trl':translit(idx).encode()}[k]
        fns.append(('ownct|'+k,own))
    # first / last rune
    def fl(which, form, off):
        def f(p):
            q=p+off
            if q<0: return b''
            idx=CT[q]
            r=[idx[0]] if which=='first' else [idx[-1]] if which=='last' else [idx[0],idx[-1]]
            return {'run':runestr(r).encode(),'idx':idxbytes(r),'dec':','.join(map(str,r)).encode(),'trl':translit(r).encode(),'decc':''.join(map(str,r)).encode()}[form]
        return f
    for which in ('first','last','both'):
        for form in ('run','idx','dec','trl','decc'):
            for off in (0,-1):
                fns.append(('fl|%s|%s|%d'%(which,form,off),fl(which,form,off)))
    # gematria sums of page ciphertext / previous
    for off in (0,-1):
        for form in range(4):
            def g(p,off=off,form=form):
                q=p+off
                s=gsum(CT[q]) if q>=0 else 0
                return fint(s)[form] if form<2 else (s.to_bytes(4,'big') if form==2 else s.to_bytes(4,'little'))
            fns.append(('pgsum|%d|%d'%(off,form),g))
    # rune counts
    fns.append(('plen',lambda p: str(len(CT[p])).encode()))
    # hash chaining page to page
    for hn in ('md5','sha1','sha256','sha512','sha3_256','sha3_512','blake2b'):
        for init in (b'',b'3301',b'cicada3301'):
            for order in (0,1):
                cache={}
                def f(p,hn=hn,init=init,order=order,cache=cache):
                    if not cache: cache[-1]=getattr(hashlib,hn)(init).digest()
                    for q in range(len(cache)-1+0, p+1):
                        pass
                    # recompute sequentially
                    s=getattr(hashlib,hn)(init).digest()
                    for q in range(p):
                        ct=idxbytes(CT[q])
                        s=getattr(hashlib,hn)((s+ct) if order==0 else (ct+s)).digest()
                    return s
                fns.append(('hchain|%s|%s|%d'%(hn,init.decode(),order),f))
    return fns

if __name__=='__main__':
    G=build_G(); print(len(G),'G seeds'); 
    from collections import Counter
    print(Counter(l for l,_ in G))
    print(len(core_subset(G)))
    Pf=build_P(); print(len(Pf),'P funcs')
    print(len(ONIONS),'onions')
    print(Pf[0][1](5), Pf[-1][1](3)[:8])
