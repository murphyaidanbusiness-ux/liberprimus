"""Fair planted control: dictionary = relikd general dictionary only (no W&P, no solved pages);
planted plaintext = War&Peace words in LP lengths. Reports dictionary coverage and hit rates."""
import numpy as np, core
from collections import defaultdict
import s3_attack as A
rng=np.random.default_rng(5)
DR={}
for L in range(9,15):
    ws=set()
    for line in open(core.S+'/dl/transcr/LiberPrayground/data/dictionary_%d.txt'%L,encoding='utf-8'):
        w=tuple(core.R2I[c] for c in line.strip() if c in core.R2I)
        if len(w)==L: ws.add(w)
    t=defaultdict(list)
    for w in ws: t[A.sig_vig(w)].append(w)
    DR[L]=(ws,t)
A.TAB.update({L:DR[L][1] for L in DR})
for L in range(9,15):
    toks=[tuple(w) for w in A.BYL.get(L,[])]
    print('L=%d relikd dict %d words; W&P token coverage %.2f'%(L,len(DR[L][0]),np.mean([w in DR[L][0] for w in toks])))
A.report('REAL LP (relikd dict)',A.LPW,9,'vig',nnull=100)
for q in [1.0,0.6]:
    P,w=core.matched_plain(A.lens0,A.BYL,rng); p=core.word_meta(w)[0]
    Cs=A.vig5_partial(P,w,p,q); PW=[Cs[w==k] for k in range(w.max()+1)]
    A.report('PLANTED W&P q=%.1f (relikd dict)'%q,PW,9,'vig',nnull=30)
# solved-page plaintext planted (Cicada register): only words>=9 available
sol=[np.array(x) for x in A.sol if len(x)>=9]
print('solved-LP words >=9 runes:',len(sol),' in relikd dict:',np.mean([tuple(x) in DR[len(x)][0] for x in sol if len(x)<=14]))
