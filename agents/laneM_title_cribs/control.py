"""Positive controls: A KOAN text encrypted (i) chain cipher keyed by running English text, (ii) Vigenere skip-on-repeat keyed by a Cicada word.
The control replaces the cipher at section 0's slot (pos 0, as section 0: no previous rune); the crib pipeline is run on it with
the control text's own opening word lengths."""
import random, json, re
from common import *
import vocab, geom, jobs
KO=open(S+'/dl/dukotah/liber-primus/data/keys/armada18/cicada_koans_and_lp_sections.txt').read().split('\n\n')
koan=[b for b in KO if b.startswith('A KOAN\n')][0]
words=[vocab.spell(w) for w in re.findall('[A-Z]+',koan)]
P=[x for w in words for x in w]; lens=[len(w) for w in words]
emer=re.sub('[^A-Z]','',open(S+'/dl/dukotah/liber-primus/data/keys/self_reliance.txt').read().upper())
KEYTXT=vocab.spell(emer[5000:9000])
def enc_chain(P,key,c0):
    out=[]; prev=c0
    for p,k in zip(P,key):
        D=1+((p%28+k)%28); prev=(prev+D)%29; out.append(prev)
    return out
KW='PILGRIMAGE'; KWR=vocab.spell(KW)
def enc_vig_skip(P,K,cprev):
    out=[]; t=0; prev=cprev
    for p in P:
        c=(p+K[t%len(K)])%29
        if c==prev: t+=1; c=(p+K[t%len(K)])%29
        out.append(c); prev=c; t+=1
    return out
def controls():
    rng=random.Random(5)
    c0=rng.randrange(29)
    ci=enc_chain(P,[k%28 for k in KEYTXT],c0)
    cii=enc_vig_skip(P,KWR,-1)
    return {'chain_runkey':ci,'vig_skip_kw':cii}
if __name__=='__main__':
    V=vocab.load_V()
    cand=vocab.candidates(lens,V); cribs=list(cand.keys())
    true=vocab.spell('A KOAN'); assert true in cand, 'A KOAN not in candidates'
    print('control lens',lens[:3],'candidates',len(cribs),'true crib id',cribs.index(true), 'A KOAN A' , vocab.spell('A KOAN A') in cand)
    rng=random.Random(7)
    blocks=[];oid=900
    meta={}
    for name,cs in controls().items():
        clen=max(len(r) for r in cribs)+2
        blocks.append((oid,0,-1,cs[:clen],cribs)); meta[oid]=name
        for rep in range(5):
            blocks.append((oid+1+rep,0,-1,cs[:clen],[tuple(rng.randrange(29) for _ in r) for r in cribs])); meta[oid+1+rep]=name+'_nullR%d'%rep
        oid+=10
    jobs.write_job(OUT+'/jobs/control.txt',blocks)
    json.dump(dict(meta=meta,lens=lens[:12],cribs=[[cand[r][0],list(r)] for r in cribs],P=P,keytxt=KEYTXT[:60],kw=list(KWR),ctrl=controls()),open(OUT+'/control_meta.json','w'))
