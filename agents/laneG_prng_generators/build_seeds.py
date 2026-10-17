# Build the seed list file for search.c / keystream.c.
#  I <int> label   : integer seed for all 19 idioms (MT-py: init_by_array(limbs(|int|)), others: native int seeding)
#  K n limbs label : MT-py key (string seeded: py2.7 hash64 / py2.7 hash32 (i386) / py3.2+ sha512)
#  J <int> label   : string->int (crc32, Java String.hashCode) fed to the non-MT-py generators
import sys, os, re, json, datetime, calendar
S='.'
L=S+'/agents/laneG_prng_generators'; sys.path.insert(0,L)
from seedfns import *
DUK=S+'/dl/dukotah/liber-primus'
ints={}
def addi(v,lab):
    if v not in ints: ints[v]=lab
for v in range(0,100001): addi(v,'int')
spec={3301:'3301',1033:'1033',509:'509',503:'503',761:'761',3301*1033:'3301*1033',509*503:'509*503',3301*3301:'3301^2',
      3301*761:'3301*761',3301*509:'3301*509',3301*503:'3301*503',1033*761:'1033*761',845145127:'845145127',1595277641:'1595277641',
      0x7A35090F:'0x7A35090F',0x181F01E5:'0x181F01E5',0x6D854CD7:'0x6D854CD7',0x181F01E57A35090F:'0x181F01E57A35090F',
      33013301:'33013301',13301:'13301',1033013301:'1033013301',2**31-1:'2^31-1',2**32-1:'2^32-1',29:'29',
      3301*29:'3301*29',3301*2:'3301*2',int('3301',16):'0x3301',int('3301',8):'0o3301',1325734783:'pgp key creation second'}
for v,l in spec.items(): addi(v,l)
for k in range(1,1001): addi(3301*k,'3301*%d'%k)
for v in range(0,3301*3): pass
# dates 2011-2015 in several formats + unix midnights (UTC) and noon
d=datetime.date(2011,1,1)
while d<=datetime.date(2015,12,31):
    Y,M,D=d.year,d.month,d.day
    for fmt,val in [('YYYYMMDD',Y*10000+M*100+D),('DDMMYYYY',D*1000000+M*10000+Y),('MMDDYYYY',M*1000000+D*10000+Y),
                    ('YYMMDD',(Y%100)*10000+M*100+D),('DDMMYY',D*10000+M*100+Y%100),('MMDDYY',M*10000+D*100+Y%100),
                    ('YYYYDDD',Y*1000+d.timetuple().tm_yday)]:
        addi(val,'date %s %s'%(fmt,d.isoformat()))
    t=calendar.timegm(d.timetuple()); addi(t,'unix %s 00:00Z'%d.isoformat()); addi(t+43200,'unix %s 12:00Z'%d.isoformat())
    d+=datetime.timedelta(days=1)
for y in range(1990,2031): addi(y,'year')
pri=json.load(open(DUK+'/analysis/round20/P3/seedprior20.json'))['order']
for o in pri: addi(int(o['seed']),'dukotah P3b timestamp rank %d'%o['rank'])
# ---- strings ----
strs={}
def adds(b,lab):
    if isinstance(b,str): b=b.encode('utf-8')
    if b not in strs: strs[b]=lab
base=['cicada','Cicada','CICADA','3301','cicada3301','Cicada3301','CICADA3301','Cicada 3301','cicada 3301','CICADA 3301',
      'liber primus','Liber Primus','LIBER PRIMUS','LiberPrimus','liberprimus','LIBERPRIMUS','instar','Instar','INSTAR','emergence','Emergence','EMERGENCE',
      'instar emergence','INSTAR EMERGENCE','divinity','Divinity','DIVINITY','primes','Primes','PRIMES','totient','Totient','TOTIENT',
      'circumference','CIRCUMFERENCE','firfumferenfe','FIRFUMFERENFE','gematria primus','Gematria Primus','GEMATRIA PRIMUS','an end','AN END',
      'parable','PARABLE','koan','KOAN','welcome','WELCOME','a warning','A WARNING','some wisdom','SOME WISDOM','an instruction','AN INSTRUCTION',
      'the loss of divinity','THE LOSS OF DIVINITY','self reliance','consumption','preservation','adherence','pilgrim','PILGRIM','3301 cicada','LP','lp','LP2','runes',
      'futhorc','FUTHORC','rune','seed','key','password','secret','test','hello','random','Random','a','abc']
for w in base: adds(w,'brief/base')
for p in range(0,75):
    for f in ['%d','%02d','page %d','Page %d','page%d','p%d','%d.jpg','%02d.jpg','LP %d','lp%d']: adds(f%p,'pagenum')
# lane A Cicada vocabulary (same sources as laneA build_keys.py)
K=DUK+'/data/keys/'
cic=set()
extra=open(S+'/agents/laneA_keyword_chain/build_keys.py').read().split("extra='''")[1].split("'''")[0]
for w in extra.split(): cic.add(w)
for line in open(K+'thematic.txt'):
    w=line.strip()
    if w: cic.add(w.upper())
txt=open(K+'armada18/cicada_koans_and_lp_sections.txt').read()+open(K+'armada18/cicada_2012_2013_puzzle_texts.txt').read()+open(K+'armada18/cicada_pgp_messages.txt').read()
for w in re.findall('[A-Za-z]+',txt): cic.add(w.upper())
for line in open(K+'armada18/cicada_koans_and_lp_sections.txt'):
    l=line.strip()
    if l and len(l.split())<=6: cic.add(re.sub('[^A-Z]','',l.upper())); adds(l,'section line'); adds(l.upper(),'section line'); adds(l.lower(),'section line')
for line in open(K+'words_expanded.txt'):
    w=line.strip().upper()
    if w.isalpha(): cic.add(w)
for w in sorted(cic):
    adds(w,'cicvocab'); adds(w.lower(),'cicvocab'); adds(w.capitalize(),'cicvocab')
# lane B global seed dictionary (solved titles/plaintexts, onions, PGP ids, page numbers, AN END hash, gematria sums, ...)
sys.path.insert(0,S+'/agents/laneB_hash_keystreams')
cwd=os.getcwd(); os.chdir(S+'/agents/laneB_hash_keystreams')
import seeds as lbseeds
G=lbseeds.build_G(); os.chdir(cwd)
for lab,b in G: adds(b,'laneB:'+lab)
for l in open(S+'/agents/laneB_hash_keystreams/onions_all.txt'):
    o=l.strip()
    if o: adds(o,'onion'); adds(o.replace('.onion',''),'onion'); adds('http://'+o,'onion'); adds('http://'+o+'/','onion')
# solved page plaintexts (whole, lines) from SOLVED-PAGES.json
SP=json.load(open(DUK+'/SOLVED-PAGES.json'))['pages']
for pg in SP:
    for k,v in (pg.items() if isinstance(pg,dict) else []):
        if isinstance(v,str) and 2<=len(v)<=4000: adds(v,'solved:'+str(k)); adds(v.lower(),'solved:'+str(k)); adds(v.upper(),'solved:'+str(k))
def clean(lab): return re.sub(r'\s+','_',lab)[:60]
def show(b):
    try: s=b.decode('utf-8')
    except: s='hex:'+b.hex()
    s=re.sub(r'\s','_',s)
    if not s.isprintable() or not s.isascii(): s='hex:'+b.hex()
    return s[:40]
lines=[]
for v,l in ints.items(): lines.append('I %d int:%d[%s]'%(v,v,clean(l)))
keys=set(); jints=set()
for b,l in strs.items():
    tag=show(b)
    for kind,key in (('py27h64',key_py2(b,64)),('py27h32',key_py2(b,32)),('py32sha',key_py3(b))):
        t=tuple(key)
        if (kind,t) in keys: continue
        keys.add((kind,t)); lines.append('K %d %s %s:%s'%(len(key),' '.join(map(str,key)),kind,tag))
    try: js=java_hash(b.decode('utf-8'))
    except: js=java_hash(b.decode('latin-1'))
    for kind,v in (('crc32',crc32(b)),('javahash',js)):
        if (kind,v) in jints: continue
        jints.add((kind,v)); lines.append('J %d %s:%s'%(v,kind,tag))
open(L+'/seeds_all.txt','w').write('\n'.join(lines)+'\n')
ni=sum(1 for x in lines if x[0]=='I'); nk=sum(1 for x in lines if x[0]=='K'); nj=sum(1 for x in lines if x[0]=='J')
print('ints',ni,'strings',len(strs),'K-keys',nk,'J-ints',nj,'lines',len(lines))
json.dump({'ints':ni,'strings':len(strs),'K':nk,'J':nj},open(L+'/seeds_counts.json','w'))
