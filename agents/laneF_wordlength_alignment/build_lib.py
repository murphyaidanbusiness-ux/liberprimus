# Build the candidate-text library: word token stream (type ids) per text, deduped by content hash.
import os, re, glob, hashlib, unicodedata, pickle, sys
import numpy as np
S='.'
HERE=S+'/agents/laneF_wordlength_alignment'
DK=S+'/dl/dukotah/liber-primus'
SPECIAL={'þ':'TH','Þ':'TH','ð':'TH','Ð':'TH','æ':'AE','Æ':'AE','œ':'OE','Œ':'OE','ƿ':'W','Ƿ':'W','ß':'SS','ſ':'S'}
SPLIT=re.compile(r"[^A-Za-z'’À-ɏÞþÐðǷƿ]+")
def norm(w):
    out=[]
    for ch in w:
        if ch in SPECIAL: out.append(SPECIAL[ch]); continue
        d=unicodedata.normalize('NFKD',ch); out.append(''.join(c for c in d if not unicodedata.combining(c)))
    return re.sub('[^A-Z]','',''.join(out).upper())
def strip_gut(t):
    m=re.search(r'\*\*\* ?START OF[^\n]*\n',t)
    if m: t=t[m.end():]
    m=re.search(r'\*\*\* ?END OF',t)
    if m: t=t[:m.start()]
    m=re.search(r'End of (the )?Project Gutenberg',t)
    if m: t=t[:m.start()]
    return t
def tokens(t):
    return [w for w in (norm(x) for x in SPLIT.split(t)) if w]
files=[]
files+=sorted(glob.glob(DK+'/data/keys/*.txt'))+sorted(glob.glob(DK+'/data/keys/armada18/*.txt'))+sorted(glob.glob(DK+'/data/keys/armada19/*.txt'))
files+=sorted(glob.glob(DK+'/analysis/bookcipher/books/*.txt'))
files+=[DK+'/analysis/armada20/thomas.txt',DK+'/analysis/armada20/mhh_45315.txt',DK+'/analysis/foundation/sephir_yetzirah_westcott_key.txt']
files+=sorted(glob.glob(HERE+'/fetched/*.txt'))
NG=S+'/agents/laneE_language_id/corp/nltk/gutenberg/'
HOLD=['bryant-stories.txt','burgess-busterbrown.txt','edgeworth-parents.txt']   # held-out English for the "random English" null
files+=[NG+f for f in sorted(os.listdir(NG)) if f.endswith('.txt') and f not in HOLD]
skip=('lp1_runes_as_key','words_expanded','thematic','runepoem_translit','cicada_pgp_messages')
seen={}; names=[]; streams=[]
for f in files:
    if any(s in f for s in skip) or not os.path.exists(f): continue
    t=open(f,encoding='utf-8',errors='ignore').read()
    t=strip_gut(t)
    tk=tokens(t)
    if len(tk)<50: print('tiny',f,len(tk)); continue
    h=hashlib.md5(' '.join(tk[:20000]).encode()).hexdigest()
    if h in seen: print('dup',os.path.basename(f),'=',seen[h]); continue
    seen[h]=os.path.basename(f)
    nm=f.replace(DK+'/','dk/').replace(HERE+'/','').replace(NG,'nltk/')
    names.append(nm); streams.append(tk)
# held-out null texts
hold=[]
for f in HOLD: hold+=tokens(strip_gut(open(NG+f,encoding='utf-8',errors='ignore').read()))
EWT=S+'/agents/laneE_language_id/corp/en_ewt.conllu'
ewt=[]
for l in open(EWT,encoding='utf-8',errors='ignore'):
    if l.startswith('# text ='): ewt+=tokens(l[8:])
types={}; 
def ids(tk): return np.array([types.setdefault(w,len(types)) for w in tk],dtype=np.int32)
tok=[];starts=[0]
for tk in streams:
    a=ids(tk); tok.append(a); tok.append(np.array([-1],dtype=np.int32)); starts.append(starts[-1]+len(a)+1)
tok=np.concatenate(tok)
hold_ids=ids(hold); ewt_ids=ids(ewt)
tl=[None]*len(types)
for w,i in types.items(): tl[i]=w
pickle.dump(dict(names=names,starts=np.array(starts),tok=tok,types=tl,hold=hold_ids,ewt=ewt_ids),open(HERE+'/lib.pkl','wb'))
print('texts',len(names),'tokens',len(tok)-len(names),'types',len(tl),'heldout',len(hold_ids),'ewt',len(ewt_ids))
for n,s in zip(names,streams): print('%8d %s'%(len(s),n))
