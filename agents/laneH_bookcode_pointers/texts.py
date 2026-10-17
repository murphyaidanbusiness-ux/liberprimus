"""Build hierarchical views (paragraph > sentence > word > letter) of the candidate pointer texts."""
import re, json, numpy as np
S='.'
DK=S+'/dl/dukotah/liber-primus'
HERE=S+'/agents/laneH_bookcode_pointers'
BK=DK+'/analysis/bookcipher/books'
KEYS=DK+'/data/keys'
WORD_RE=re.compile(r"[A-Za-z0-9']+(?:-[A-Za-z]+)*")
SENT_RE={'dot':re.compile(r'(?<=[.!?])["”]?\s+'),'dotsemi':re.compile(r'(?<=[.!?;:])["”]?\s+')}

class View:
    """doc = list of paragraphs; paragraph = list of sentences; sentence = list of words (letters-only uppercase)"""
    def __init__(self,name,doc):
        self.name=name
        doc=[[[w for w in s if w] for s in p] for p in doc]
        doc=[[s for s in p if s] for p in doc]
        doc=[p for p in doc if p]
        self.doc=doc
        ps=[0]; sw=[0]; words=[]
        for p in doc:
            for s in p:
                words.extend(s); sw.append(sw[-1]+len(s))
            ps.append(ps[-1]+len(p))
        self.ps=np.array(ps,dtype=np.int64)     # paragraph -> first sentence (len P+1)
        self.sw=np.array(sw,dtype=np.int64)     # sentence -> first word (len S+1)
        self.words=words
        wl=np.array([len(w) for w in words],dtype=np.int64)
        self.wl=wl
        self.wstart=np.r_[0,np.cumsum(wl)]      # word -> first letter (len W+1)
        self.L=np.frombuffer(''.join(words).encode('ascii'),dtype=np.uint8).astype(np.int64)-65
        self.nP=len(doc); self.nS=len(self.sw)-1; self.nW=len(words); self.nL=len(self.L)
        # derived
        self.pw=self.sw[self.ps]                # paragraph -> first word (len P+1)
        self.pl=self.wstart[self.pw]            # paragraph -> first letter
        self.sl=self.wstart[self.sw]            # sentence -> first letter
    def __repr__(self): return f'<{self.name}: P={self.nP} S={self.nS} W={self.nW} L={self.nL}>'

def letters_only(w): return re.sub(r'[^A-Za-z]','',w).upper()
def words_of(s): return [letters_only(w) for w in WORD_RE.findall(s)]
def sents_of(p,mode='dot'):
    p=' '.join(p.split()); return [s for s in SENT_RE[mode].split(p) if s.strip()]

def strip_gutenberg(t):
    a=re.split(r'\*\*\* ?START[^\n]*\*\*\*',t,flags=re.S)
    if len(a)>1: t=a[1]
    t=re.split(r'\*\*\* ?END',t,flags=re.S)[0]
    return t

def doc_from_blocks(blocks,mode='dot'):
    return [[words_of(s) for s in sents_of(b,mode)] for b in blocks]

def blocks_of(raw): return [b for b in re.split(r'\n\s*\n',raw) if b.strip()]

def load_sr():
    raw=open(KEYS+'/self_reliance.txt',encoding='utf-8').read()
    raw=re.sub(r'\[\d+\]','',raw)
    blocks=blocks_of(raw)
    paras=[re.sub(r'^\s*\d+\.\s+','',p) for p in blocks[5:]]   # drop title + epigraph blocks
    return blocks,paras

def views():
    V={}
    blocks,paras=load_sr()
    # SR doyle edition (validated by the 2014 code: decodes auqgnxjtvdbll3pv)
    nov=[p for i,p in enumerate(paras) if i!=36]
    V['SR_doyle']=View('SR_doyle',doc_from_blocks(nov,'dot'))
    V['SR_doyle_semi']=View('SR_doyle_semi',doc_from_blocks(nov,'dotsemi'))
    V['SR_withverse']=View('SR_withverse',doc_from_blocks(paras,'dot'))
    raw=open(KEYS+'/self_reliance.txt',encoding='utf-8').read(); raw=re.sub(r'\[\d+\]','',raw)
    lines=[l for l in raw.split('\n') if l.strip()]
    V['SR_lines']=View('SR_lines',[[words_of(l) for l in lines]])
    # Liber AL
    d=json.load(open(HERE+'/texts/al.json',encoding='utf-8-sig'))
    ch=[[words_of(d[f'{c}.{v}']) for v in range(1,200) if f'{c}.{v}' in d] for c in (1,2,3)]
    V['AL_verse']=View('AL_verse',ch)
    V['AL_flat']=View('AL_flat',[[ [w for v in c for w in v] ] for c in ch])    # chapter -> one sentence
    allv=[v for c in ch for v in c]
    V['AL_allverses']=View('AL_allverses',[allv])
    # Mabinogion (Guest, Gutenberg #5160): blank-line paragraphs, and physical lines
    mab=strip_gutenberg(open(BK+'/mabinogion.txt',encoding='utf-8',errors='ignore').read())
    V['Mab_para']=View('Mab_para',doc_from_blocks(blocks_of(mab),'dot'))
    mlines=[l for l in mab.split('\n') if l.strip()]
    V['Mab_lines']=View('Mab_lines',[[words_of(l) for l in mlines]])
    # Rune poem
    rp=[l for l in open(KEYS+'/runepoem_translit.txt',encoding='utf-8').read().split('\n') if l.strip()]
    V['RunePoem']=View('RunePoem',[[words_of(l) for l in rp]])
    # solved LP1 plaintext: no word boundaries -> letters as words, page = paragraph
    sp=json.load(open(DK+'/SOLVED-PAGES.json'))['pages']
    V['LP1_solved']=View('LP1_solved',[[[c for c in letters_only(p['plaintext_transliteration'])]] for p in sp])
    # Cicada PGP prose
    cp=open(KEYS+'/armada18/cicada_pgp_messages.txt',encoding='utf-8',errors='ignore').read()
    V['CicadaPGP']=View('CicadaPGP',[[words_of(l) for l in b.split('\n') if l.strip()] for b in blocks_of(cp)])
    # KJV control: chapters as paragraphs, verses as sentences
    kjv=open(BK+'/kjv.txt',encoding='utf-8',errors='ignore').read().split('\n')
    verses=[]; 
    for l in kjv[104:]:
        m=re.match(r'^(\d+):(\d+) (.*)$',l)
        if m: verses.append([int(m.group(1)),int(m.group(2)),m.group(3)])
        elif verses and l.strip() and not re.match(r'^\*\*\*',l): verses[-1][2]+=' '+l.strip()
    chap=[]; last=None
    for c,v,t in verses:
        if v==1 or last is None: chap.append([])
        chap[-1].append(words_of(t)); last=c
    V['KJV']=View('KJV',chap)
    # priors (para/sent via blank-line blocks)
    for nm,fn in (('Blake','blake.txt'),('Milton','miltonPL.txt'),('Agrippa','agrippa.txt')):
        t=strip_gutenberg(open(BK+'/'+fn,encoding='utf-8',errors='ignore').read())
        V[nm]=View(nm,doc_from_blocks(blocks_of(t),'dot'))
    return V

if __name__=='__main__':
    V=views()
    for v in V.values(): print(v)
