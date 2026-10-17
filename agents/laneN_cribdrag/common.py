import re, sys, os, numpy as np
S='.'
LANE=S+'/agents/laneN_cribdrag'
DUK=S+'/dl/dukotah/liber-primus'
sys.path.insert(0,S+'/lp')
import lpdata
TR=lpdata.TR
DIG={'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
SING={'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'Q':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,
      'T':16,'B':17,'E':18,'M':19,'L':20,'D':23,'A':24,'Y':26}
def eng2runes(s, ing=True):
    s=re.sub('[^A-Z]','',s.upper()).replace('QU','CW')
    if ing: s=s.replace('ING','#')
    out=[];i=0
    while i<len(s):
        if s[i]=='#': out.append(21); i+=1; continue
        d=s[i:i+2]
        if d in DIG: out.append(DIG[d]); i+=2
        else: out.append(SING[s[i]]); i+=1
    return out
def tr(idx): return ''.join(TR[i] for i in idx)
