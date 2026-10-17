import common, re, json, numpy as np, itertools
K=common.DUK+'/data/keys/'
cic=set()
extra='''DIVINITY CIRCUMFERENCE FIRFUMFERENFE INSTAR EMERGENCE INSTAREMERGENCE PILGRIM PILGRIMAGE PRIMES PRIME TOTIENT SACRED CICADA
LIBERPRIMUS LIBER PRIMUS KOAN CONSCIOUSNESS WISDOM WARNING PARABLE MOBIUS INTUS SELFRELIANCE SELF RELIANCE ENLIGHTENMENT DECEPTION
PRIMALITY CONSUMPTION PRESERVATION ADHERENCE INSTRUCTION AN END WELCOME LOSS OF DIVINITY THE LOSS OF DIVINITY AN INSTRUCTION A KOAN
SOME WISDOM A WARNING THREE THREETHREEZEROONE CICADATHREETHREEZEROONE TUNNELING SURFACE EMERGE SHED DEEPWEB DEEP WEB HASH PAGE PILGRIMS
GEMATRIA GEMATRIAPRIMUS RUNES RUNE ODIN YGGDRASIL MERCURY HERMES TRISMEGISTUS GNOSIS GNOSTIC ALCHEMY OUROBOROS CROWLEY THELEMA
AGRIPPA BLAKE JUNG TAO TAOISM ZEN BUDDHA ENOCH ENOCHIAN DEE KELLEY QABALAH KABBALAH SEPHIROTH ANAEL MAGICK OCCULT ESOTERIC
FIBONACCI EULER FERMAT MERSENNE PHI SQUARE MAGIC MAGICSQUARE SPIRAL ZECKENDORF TORUS CUBE VOID PRIMALITY FOUR UNREASONABLE THINGS
CIRCUMFERENCES DIVINITIES MASTER STUDENT VOICE TRUTH REALITY PROGRAM MIND KNOWLEDGE BELIEVE NOTHING ENCRYPTED SECRET HIDDEN
EPIPHANY DEVOTED PATH WAY MAP ROAD DIRECTION NUMBERS WORDS MEANING SEEK FOUND LIBERPRIMUSISTHEWAY THEPATHLIESEMPTY
ANINSTRUCTION ANEND THELOSSOFDIVINITY SOMEWISDOM AWARNING AKOAN'''
for w in extra.split(): cic.add(w)
for line in open(K+'thematic.txt'): 
    w=line.strip()
    if w: cic.add(w.upper())
txt=open(K+'armada18/cicada_koans_and_lp_sections.txt').read()+open(K+'armada18/cicada_2012_2013_puzzle_texts.txt').read()+open(K+'armada18/cicada_pgp_messages.txt').read()
for w in re.findall('[A-Za-z]+',txt): cic.add(w.upper())
# section titles as joined phrases
for line in open(K+'armada18/cicada_koans_and_lp_sections.txt'):
    l=line.strip()
    if l and len(l.split())<=6: cic.add(re.sub('[^A-Z]','',l.upper()))
for line in open(K+'words_expanded.txt'):
    w=line.strip().upper()
    if w.isalpha(): cic.add(w)
# solved-page plaintext words: the SOLVED-PAGES transliterations are unsegmented; the sections file above has all solved words.
cicr=set()
for w in cic:
    r=tuple(common.eng2runes(w))
    if 1<=len(r)<=40: cicr.add(r)
    if 'C' in w or 'K' in w:   # C/F pun: every C -> F (FIRFUMFERENFE)
        r2=tuple(0 if x==5 else x for x in r)
        if 1<=len(r2)<=40: cicr.add(r2)
eng=set()
for line in open(common.LANE+'/dl/words_alpha.txt'):
    w=line.strip()
    if w.isalpha():
        r=tuple(common.eng2runes(w))
        if 3<=len(r)<=16: eng.add(r)
short=set(itertools.product(range(29),repeat=1))|set(itertools.product(range(29),repeat=2))
allk=sorted(cicr)+sorted(eng-cicr)+sorted(short-cicr-eng)
src=[1]*len(cicr)+[0]*len(eng-cicr)+[2]*len(short-cicr-eng)
print('cicada vocab',len(cicr),'english',len(eng),'english-not-cicada',len(eng-cicr),'short exhaustive',len(short-cicr-eng),'total',len(allk))
import collections; print(sorted(collections.Counter(len(k) for k in allk).items()))
with open(common.LANE+'/keys.txt','w') as f:
    for k,s in zip(allk,src): f.write('%d %d %s\n'%(s,len(k),' '.join(map(str,k))))
