import glob, re, sys, os
sys.path.insert(0,'.')
from common import *
files=[]
files+=glob.glob(DUK+'/data/keys/**/*.txt',recursive=True)
files+=glob.glob(S+'/agents/laneF_wordlength_alignment/fetched/*.txt')
files+=glob.glob(S+'/corp/*.txt')
files=[f for f in files if os.path.getsize(f)>2000 and 'lp1_' not in f and 'runes_as_key' not in f]
buf=bytearray(); index=[]
for f in sorted(set(files)):
    try: t=open(f,encoding='utf-8',errors='ignore').read()
    except Exception: continue
    t=re.sub(r'[^A-Za-z]','',t)
    if len(t)<2000: continue
    try: r=eng2runes(t)
    except KeyError: continue
    index.append((f,len(buf),len(r)))
    buf+=bytes(x+65 for x in r)+b'\x00'
open(LANE+'/corpus.bin','wb').write(bytes(buf))
import json; json.dump(index,open(LANE+'/corpus_index.json','w'))
print(len(files),'files',len(buf)/1e6,'M runes')
