import re
S='.'
def parse_al(path=S+'/dl/dukotah/liber-primus/data/keys/armada18/crowley_book_of_the_law_hermetic.txt', rule='noterm'):
    lines=[l.rstrip() for l in open(path,encoding='utf-8').read().split('\n') if l.strip()]
    chap=0; ch=[[],[],[]]; cur=''
    for l in lines:
        m=re.match(r'Chapter (I+)$',l)
        if m:
            if cur: ch[chap-1].append(cur); cur=''
            chap=len(m.group(1)); continue
        if chap==0: continue
        cur=(cur+' '+l).strip() if cur else l
        if re.search(r'[.!?]["”’]?$',l) or rule=='line':
            ch[chap-1].append(cur); cur=''
    if cur: ch[chap-1].append(cur)
    return ch
if __name__=='__main__':
    for r in ('noterm','line'):
        ch=parse_al(rule=r); print(r,[len(c) for c in ch])
