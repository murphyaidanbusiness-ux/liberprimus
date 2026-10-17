import sys
S='.'
sys.path.insert(0,S+'/lp'); import lpdata, numpy as np
from collections import Counter
U,C,sha=lpdata.unsolved(); assert sha.startswith('0233120')
# global ids: words are numbered globally across pages? check
words=Counter(); wordsent={}
lines=[]
for p in U:
    L=Counter(p['line']); lines+= [(p['page'],k,v) for k,v in L.items()]
print(len(lines), np.mean([v for _,_,v in lines]), np.std([v for _,_,v in lines]))
import itertools
# line length per page
for p in U[:8]:
    L=Counter(p['line']); print(p['page'],sorted(L.values()))
# fraction of line ends at word boundary
wb=0;tot=0
for p in U:
    w=p['word'];l=p['line']
    for i in range(len(w)-1):
        if l[i]!=l[i+1]:
            tot+=1; wb+= (w[i]!=w[i+1])
print('line breaks',tot,'at word boundary',wb, wb/tot)
