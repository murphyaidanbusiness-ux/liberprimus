import hashlib, json, re, os
DL='./dl'
RUNES="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
TR=["F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X","S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"]
PRIMES=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
R2I={r:i for i,r in enumerate(RUNES)}
assert len(RUNES)==29

def load():
    """Returns list of pages; each page: dict(page=int, idx=[...], word=[word id per rune], line=[line id], sent=[...], chapter=[...])"""
    txt=open(DL+'/dukotah/liber-primus/data/krisyotam_runes.txt',encoding='utf-8').read()
    pages=[]; cur=dict(page=0,idx=[],word=[],line=[],sent=[],chap=[])
    w=l=s=ch=0
    for c in txt:
        if c in R2I:
            cur['idx'].append(R2I[c]); cur['word'].append(w); cur['line'].append(l); cur['sent'].append(s); cur['chap'].append(ch)
        elif c=='-': w+=1
        elif c=='.': w+=1; s+=1
        elif c=='/': l+=1
        elif c=='&': w+=1; s+=1; ch+=1
        elif c=='%':
            pages.append(cur); cur=dict(page=len(pages),idx=[],word=[],line=[],sent=[],chap=[]); l+=1
        elif c in '$§': w+=1; s+=1
        elif c in '\n0123456789': pass
        else: raise ValueError(repr(c))
    pages.append(cur)
    return pages

def unsolved():
    P=load()
    U=[p for p in P if p['page']<=54]
    idx=[i for p in U for i in p['idx']]
    h=hashlib.sha256(','.join(map(str,idx)).encode()).hexdigest()
    return U, idx, h

if __name__=='__main__':
    P=load(); print(len(P),'pages', [len(p['idx']) for p in P][:12])
    U,idx,h=unsolved(); print(len(idx), h, h=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585')
