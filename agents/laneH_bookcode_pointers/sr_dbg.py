exec(open('sr_validate.py').read().split("for skip in range")[0])
paras=blocks[5:]
import re
paras=[re.sub(r'^\s*\d+\.\s+','',p) for p in paras]
def get(P,s,w,l,mode='dot'):
    try:
        return words(sents(P,mode)[s-1])[w-1][l-1].lower()
    except: return None
for t,ch in [((45,5,2,3),'q'),((48,5,14,2),'x'),((47,3,3,5),'l')]:
    c=[]
    for p in range(1,len(paras)+1):
        for ds in (-1,0,1,2):
            if get(paras[p-1],t[1]+ds,t[2],t[3])==ch: c.append((p,t[1]+ds))
    print(t,ch,c)
for i,p in enumerate(paras): print(i+1,len(sents(p,'dot')),p[:50].replace('\n',' '))
