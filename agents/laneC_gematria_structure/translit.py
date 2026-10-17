import re, sys
S='.'
sys.path.insert(0,S+'/lp')
import lpdata
TR=lpdata.TR
T2I={t:i for i,t in enumerate(TR)}
def word_to_idx(w, ing=True, io=True, digraphs=('TH','EO','OE','AE','EA','NG','IA')):
    """English word -> rune index list, Cicada style: K->C V->U Q->C Z->S, TH EO OE AE EA NG as digraph runes,
    ING->NG, ION/IO->IA (empirically from solved pages)."""
    w=w.upper().replace('K','C').replace('V','U').replace('Q','C').replace('Z','S')
    w=re.sub('[^A-Z]','',w)
    out=[];i=0
    while i<len(w):
        if ing and w[i:i+3]=='ING': out.append(T2I['NG']); i+=3; continue
        if io and w[i:i+2]=='IO': out.append(T2I['IA']); i+=2; continue
        if w[i:i+2] in digraphs: out.append(T2I[w[i:i+2]]); i+=2; continue
        out.append(T2I[w[i]]); i+=1
    return out
def translit_words(txt, **kw):
    return [word_to_idx(w,**kw) for w in re.findall(r"[A-Za-z']+",txt) if re.sub('[^A-Za-z]','',w)]
