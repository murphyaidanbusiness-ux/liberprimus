import sys, json, collections, numpy as np, glob
sys.path.insert(0,'.')
from common import *
from aggregate import parse, cribs, MT, CLS, load
pg=np.load(LANE+'/pg.npy'); wd=np.load(LANE+'/wd.npy')
c_real=np.array(lpdata.unsolved()[1])
keys_words=None
def get_dict():
    global keys_words
    if keys_words is None:
        ws=[]; 
        for line in open(S+'/agents/laneA_keyword_chain/keys.txt'):
            p=line.split(); src=int(p[0]); L=int(p[1])
            if src in (0,1) and L>=3: ws.append(tuple(map(int,p[2:])))
        keys_words=ws
    return keys_words
_dw=None
def dict_windows(m):
    # all 8-letter windows of cyclic words as diff arrays + word index
    global _dw
    if _dw and m in _dw: return _dw[m]
    ws=get_dict(); rows=[];wid=[]
    for i,w in enumerate(ws):
        if m==28 and 28 in w: continue
        P=len(w)
        for t in range(P):
            rows.append([w[(t+q)%P] for q in range(8)]); wid.append(i)
    A=np.array(rows,dtype=np.int16); Dd=(np.diff(A,axis=1))%m
    _dw=_dw or {}; _dw[m]=(Dd.astype(np.int8),np.array(wid))
    return _dw[m]
def dict_match(k,m):
    Dd,wid=dict_windows(m); ws=get_dict(); out=[]
    k=np.array(k)
    for j in range(len(k)-7):
        seg=k[j:j+8]
        if (seg<0).any(): continue
        d=(np.diff(seg))%m
        for o in (0,1):
            dd=d if o==0 else (m-d)%m
            hit=np.where((Dd==dd.astype(np.int8)).all(axis=1))[0]
            for h in hit[:3]: out.append((j,o,tr(ws[wid[h]])))
        if len(out)>=4: break
    return out
def where(pos):
    p=int(pg[pos]); first=int(np.argmax(pg==p)); return 'p%d+%d'%(p,pos-first)
def show(h,idx=None):
    cb=cribs[h['crib']]; m=28 if h['mt']==0 else 29
    ks=[]
    for v in h['k']:
        if v<0: ks.append('?'); continue
        a=(m-v)%m if h['orient'] else v
        ks.append(TR[(a+h['shift'])%m])
    return cb,''.join(ks)
def uniq(tops,key=lambda h:(h['crib'],h['pos'],h['mt'],h['al'],h['F'])):
    d={}
    for h in tops:
        k=key(h)
        if k not in d or h['Z']>d[k]['Z']: d[k]=h
    return list(d.values())
if __name__=='__main__':
    allt=[]
    for F in (0,1):
        try: cells,tops=parse(LANE+'/out/F%d_real.txt'%F)
        except FileNotFoundError: continue
        for h in tops: h['F']=F
        allt+= [h for h in tops if h['kind']=='TOPZ']
    z=uniq(allt); z.sort(key=lambda h:-h['Z'])
    print('| # | F | model | cls | aligned | crib | pos | L | W | Z | key fragment (best shift/orient) | cipher window |')
    for i,h in enumerate(z[:50]):
        cb,ks=show(h)
        print('| %d | %d | %s | %s | %s | %s | %s | %d | %d | %.2f | %s | %s |'%(i+1,h['F'],MT[h['mt']],CLS[h['cls']],'y' if h['al'] else 'n',' '.join(cb['words']),where(h['pos']),h['L'],h['W'],h['Z'],ks,''))
