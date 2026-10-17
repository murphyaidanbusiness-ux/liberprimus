import random
R=random.Random(7)
A=26
ROT=["EKMFLGDQVZNTOWYHXUSPAIBRCJ","AJDKSIRUXBLHWTMCQGZNPYFVOE","BDFHJLCPRTXVZNYEIWGAKMUSQO"]
NOTCH=[16,4,21]
REF="YRUHQSLDPXNGOKMIEBFZCWVJAT"
def dec(s): return [ord(c)-65 for c in s]
def sim(L, ptgen):
    rot=[dec(r) for r in ROT]; inv=[[0]*26 for _ in rot]
    for k in range(3):
        for i,v in enumerate(rot[k]): inv[k][v]=i
    ref=dec(REF)
    # random plugboard
    pb=list(range(26)); letters=list(range(26)); R.shuffle(letters)
    for a,b in zip(letters[0:20:2],letters[1:20:2]): pb[a]=b; pb[b]=a
    pos=[R.randrange(26) for _ in range(3)]
    out=[]; pts=[]
    for _ in range(L):
        # step (double-stepping)
        if pos[1]==NOTCH[1]: pos[0]=(pos[0]+1)%26; pos[1]=(pos[1]+1)%26
        elif pos[2]==NOTCH[2]: pos[1]=(pos[1]+1)%26
        pos[2]=(pos[2]+1)%26
        # careful: left rotor index0, right idx2 ; fix: advance right always
        x=ptgen(); pts.append(x)
        c=pb[x]
        for k in (2,1,0): c=(rot[k][(c+pos[k])%26]-pos[k])%26
        c=ref[c]
        for k in (0,1,2): c=(inv[k][(c+pos[k])%26]-pos[k])%26
        out.append(pb[c])
    return pts,out
for name,g in [('random plaintext',lambda:R.randrange(26)),('all-A plaintext',lambda:0)]:
    tot=0;d=0;self_=0;d2=0
    for t in range(40):
        p,c=sim(20000,g)
        d+=sum(a==b for a,b in zip(c,c[1:]));tot+=len(c)-1
        d2+=sum(a==b for a,b in zip(c,c[2:]))
        self_+=sum(a==b for a,b in zip(p,c))
    print(f"Enigma I {name:18s} ct doublets {d/tot*100:.3f}% (1/26=3.846%) lag2 {d2/tot*100:.3f}% self-map {self_}")
