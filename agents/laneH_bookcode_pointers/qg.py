import numpy as np, math
S='.'
def load_qg(path=S+'/dl/dukotah/liber-primus/data/english_quadgrams.txt'):
    T=np.full(26**4,np.nan); tot=0; cnt={}
    for l in open(path):
        p=l.split()
        if len(p)<2: continue
        q,c=p[0].upper(),float(p[1])
        if len(q)==4 and q.isalpha(): cnt[q]=c; tot+=c
    floor=math.log10(0.01/tot)
    T[:]=floor
    for q,c in cnt.items():
        T[(((ord(q[0])-65)*26+ord(q[1])-65)*26+ord(q[2])-65)*26+ord(q[3])-65]=math.log10(c/tot)
    return T
T=load_qg()
def qscore(s):
    a=np.frombuffer(s.encode('ascii'),dtype=np.uint8).astype(np.int64)-65
    return qscore_arr(a)
def qscore_arr(a):
    if len(a)<4: return -9.0
    q=((a[:-3]*26+a[1:-2])*26+a[2:-1])*26+a[3:]
    return float(T[q].mean())
if __name__=='__main__':
    print(qscore('THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG'), qscore('XQZJKVWPLMNBVCXZASDFGHJKLQWE'))
