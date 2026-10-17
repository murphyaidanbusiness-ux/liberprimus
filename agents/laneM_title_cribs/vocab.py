"""Crib vocabulary and per-opening candidate lists."""
import re, itertools, collections, sys, os
S='.'
OUT=S+'/agents/laneM_title_cribs'
K=S+'/dl/dukotah/liber-primus/data/keys/'
sys.path.insert(0,S+'/lp'); import lpdata
TR=lpdata.TR
# spelling: Cicada convention (lane L): K/Q->C, V->U, Z->S, ING->NG, IO->IA, greedy digraphs TH EO NG OE AE IA EA.
_SP={lab:(i,) for i,lab in enumerate(TR)}
_SP.update({'ING':(21,),'IO':(27,),'QU':(5,7),'K':(5,),'Q':(5,),'V':(1,),'Z':(15,)})
def spell(w, io=True, ing=True, ea=True):
    s=re.sub('[^A-Z]','',w.upper()); out=[]; i=0
    while i<len(s):
        for L in (3,2,1):
            sp=s[i:i+L]
            if len(sp)<L or sp not in _SP: continue
            if sp=='ING' and not ing: continue
            if sp=='IO' and not io: continue
            if sp=='EA' and not ea: continue
            out.extend(_SP[sp]); i+=L; break
        else: i+=1
    return tuple(out)
def spellings(w):
    """Cicada spelling first, then variants with IO split, ING as I+NG, EA split."""
    out=[]
    for io,ing,ea in itertools.product((True,False),repeat=3):
        r=spell(w,io,ing,ea)
        if r and r not in out: out.append(r)
    return out
def tr(r): return '-'.join(TR[i] for i in r)

def words_of(text): return re.findall('[A-Z]+',text.upper())
cic_files=['armada18/cicada_koans_and_lp_sections.txt','armada18/cicada_2012_2013_puzzle_texts.txt','armada18/cicada_pgp_messages.txt']
EXTRA='''DIVINITY CIRCUMFERENCE INSTAR EMERGENCE PILGRIM PILGRIMAGE PRIMES PRIME TOTIENT SACRED CICADA LIBER PRIMUS KOAN CONSCIOUSNESS
WISDOM WARNING PARABLE MOBIUS INTUS SELF RELIANCE ENLIGHTENMENT DECEPTION PRIMALITY CONSUMPTION PRESERVATION ADHERENCE INSTRUCTION
END WELCOME LOSS INTERCONNECTEDNESS EPIPHANY AWAKENING GEMATRIA RUNES RUNE ODIN MERCURY HERMES GNOSIS ALCHEMY OUROBOROS MAGICK OCCULT
ESOTERIC FIBONACCI EULER FERMAT MERSENNE SPIRAL TORUS CUBE VOID MASTER STUDENT VOICE TRUTH REALITY PROGRAM MIND KNOWLEDGE SECRET
HIDDEN DEVOTED PATH WAY JOURNEY TUNNELING SURFACE SHED DEEP WEB HASH PAGE PILGRIMS SHADOWS AETHEREAL BUFFERS CARNAL OBSCURA FORM
ANALOG MOURNFUL CABAL'''
SOLVED_TITLES=['A WARNING','WELCOME','WISDOM','SOME WISDOM','INSTAR EMERGENCE','A KOAN','AN INSTRUCTION','THE LOSS OF DIVINITY','LOSS OF DIVINITY',
 'CONSUMPTION','PRESERVATION','ADHERENCE','A KOAN ON THE CIRCUMFERENCE','AN END','PARABLE','INTERCONNECTEDNESS','DIVINITY','THE CIRCUMFERENCE']
DETS1=['A','AN','THE','SOME']
DETS2=['LOSS OF','END OF']

def build_vocab():
    cicw=set(); cicph=set()
    for f in cic_files:
        for line in open(K+f):
            ws=words_of(line)
            for w in ws: cicw.add(w)
            for n in (1,2,3):
                for i in range(len(ws)-n+1): cicph.add(' '.join(ws[i:i+n]))
    for f in ('thematic.txt','words_expanded.txt'):
        for line in open(K+f):
            for w in words_of(line): cicw.add(w)
    cicw|=set(EXTRA.split())
    for t in SOLVED_TITLES:
        cicph.add(t)
        for w in t.split(): cicw.add(w)
    g20=[l.strip().upper() for l in open(S+'/agents/laneL_keyword_walk/dl/20k.txt') if l.strip().isalpha()]
    nouns=set(l.strip().upper() for l in open(OUT+'/dl/nouns.txt') if l.strip().isalpha())
    g20s=set(g20)
    titlew=set(w for w in g20 if w in nouns)
    absuf=('NESS','TION','SION','ITY','MENT','ANCE','ENCE','DOM','HOOD','ISM','SHIP','URE','ICS','ITUDE')
    titlew|=set(w for w in nouns if w.endswith(absuf))
    titlew|=cicw
    return cicw, cicph, titlew, g20

def rune_lex(words, lo=1, hi=40):
    """word -> list of spellings, filtered by rune length"""
    d={}
    for w in words:
        sp=[r for r in spellings(w) if lo<=len(r)<=hi]
        if sp: d[w]=sp
    return d

def candidates(lens, V):
    """All crib phrases whose word-rune-lengths equal a prefix (1..3 words) of lens. Returns dict rune-tuple -> (label, nwords, src)"""
    cicw, cicph, titlew, _ = V['raw']
    bylen=V['bylen']        # source -> length -> list of (word, spelling)
    out={}
    def add(words_sp, src):
        r=tuple(x for _,s in words_sp for x in s)
        lab=' '.join(w for w,_ in words_sp)
        if r not in out: out[r]=(lab,len(words_sp),src)
    l=lens
    # T1 single title word / Cicada word (title-word list 3-12 runes; Cicada words any length)
    for w,s in bylen['title'].get(l[0],[]): add([(w,s)],'T1')
    for w,s in bylen['cic'].get(l[0],[]): add([(w,s)],'T1c')
    # Cicada phrases (n-grams of Cicada texts + solved titles)
    for ph in cicph:
        ws=ph.split()
        if len(ws)>3: continue
        for combo in itertools.product(*[V['lex_all'].get(w,[]) for w in ws]):
            if [len(s) for s in combo]==l[:len(ws)]: add(list(zip(ws,combo)),'PH')
    # T2 DET + title word
    for d in DETS1:
        for ds in V['lex_all'][d]:
            if len(ds)!=l[0]: continue
            for w,s in bylen['title'].get(l[1],[]): add([(d,ds),(w,s)],'T2')
    # T3 LOSS OF / END OF + title word
    for d in DETS2:
        a,b=d.split()
        for sa in V['lex_all'][a]:
            for sb in V['lex_all'][b]:
                if [len(sa),len(sb)]!=l[:2]: continue
                for w,s in bylen['title'].get(l[2],[]): add([(a,sa),(b,sb),(w,s)],'T3')
    # T4 Cicada word pair; T5 DET + Cicada word pair; T6 W OF/ON W (Cicada words)
    for w1,s1 in bylen['cic'].get(l[0],[]):
        for w2,s2 in bylen['cic'].get(l[1],[]): add([(w1,s1),(w2,s2)],'T4')
    for d in DETS1:
        for ds in V['lex_all'][d]:
            if len(ds)!=l[0]: continue
            for w1,s1 in bylen['cic'].get(l[1],[]):
                for w2,s2 in bylen['cic'].get(l[2],[]): add([(d,ds),(w1,s1),(w2,s2)],'T5')
    for mid in ('OF','ON'):
        ms=V['lex_all'][mid][0]
        if len(ms)!=l[1]: continue
        for w1,s1 in bylen['cic'].get(l[0],[]):
            for w2,s2 in bylen['cic'].get(l[2],[]): add([(w1,s1),(mid,ms),(w2,s2)],'T6')
    return out

def load_V():
    cicw,cicph,titlew,g20=build_vocab()
    lex_all=rune_lex(set(cicw)|set(titlew)|set(DETS1)|{'LOSS','OF','END','ON'}|set(w for ph in cicph for w in ph.split()))
    bylen={'title':collections.defaultdict(list),'cic':collections.defaultdict(list)}
    for w in titlew:
        for s in lex_all.get(w,[]):
            if 3<=len(s)<=12: bylen['title'][len(s)].append((w,s))
    for w in cicw:
        for s in lex_all.get(w,[]): bylen['cic'][len(s)].append((w,s))
    return dict(raw=(cicw,cicph,titlew,g20),lex_all=lex_all,bylen=bylen)

if __name__=='__main__':
    V=load_V(); cicw,cicph,titlew,g20=V['raw']
    print('cicada words',len(cicw),'cicada phrases',len(cicph),'title words',len(titlew))
    import geom
    tot=0
    for o in geom.openings:
        c=candidates(o['lens'],V); tot+=len(c)
        cnt=collections.Counter(v[2] for v in c.values())
        print(o['kind'],o['id'],o['lens'][:3],len(c),dict(cnt))
    print('total',tot)
