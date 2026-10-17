import sys, os, re, numpy as np
S='.'
LANE=S+'/agents/laneA_keyword_chain'
sys.path.insert(0, S+'/lp')
import lpdata
TR=lpdata.TR; PRIMES=lpdata.PRIMES
DUK=S+'/dl/dukotah/liber-primus'
DIG={'TH':2,'EO':12,'NG':21,'OE':22,'AE':25,'IA':27,'IO':27,'EA':28}
SING={'F':0,'U':1,'V':1,'O':3,'R':4,'C':5,'K':5,'Q':5,'G':6,'W':7,'H':8,'N':9,'I':10,'J':11,'P':13,'X':14,'S':15,'Z':15,
      'T':16,'B':17,'E':18,'M':19,'L':20,'D':23,'A':24,'Y':26}
def eng2runes(s):
    s=re.sub('[^A-Z]','',s.upper()).replace('QU','CW')
    out=[];i=0
    while i<len(s):
        d=s[i:i+2]
        if d in DIG: out.append(DIG[d]); i+=2
        else: out.append(SING[s[i]]); i+=1
    return out
def tr(idx): return ''.join(TR[i] for i in idx)
def pages():
    U,C,h=lpdata.unsolved(); assert h=='023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
    return U,C
