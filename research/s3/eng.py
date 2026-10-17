import re, glob, random, collections
TR=["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
IDX={t:i for i,t in enumerate(TR)}
sub={'K':'C','Q':'C','V':'U','Z':'S'}
def runes(text):
    t=re.sub('[^A-Z]','',text.upper())
    t=''.join(sub.get(c,c) for c in t)
    out=[];i=0
    while i<len(t):
        d=t[i:i+2]
        if d in IDX and len(d)==2: out.append(IDX[d]); i+=2
        else:
            out.append(IDX[t[i]]); i+=1
    return out
# English text sources: python docs / licenses
texts=[]
import os
for f in ['/usr/share/common-licenses/GPL-3','/usr/share/common-licenses/Apache-2.0','/usr/share/common-licenses/LGPL-3']:
    if os.path.exists(f): texts.append(open(f,errors='ignore').read())
if not texts:
    import sysconfig
    for f in glob.glob(sysconfig.get_paths()['stdlib']+'/*.py')[:300]:
        texts.append(' '.join(re.findall(r'"""(.*?)"""',open(f,errors='ignore').read(),re.S)))
t=' '.join(texts)
P=runes(t)
print('len',len(P))
