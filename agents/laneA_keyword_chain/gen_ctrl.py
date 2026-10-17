import common, ciph, json, numpy as np
J=json.load(open(common.DUK+'/SOLVED-PAGES.json'))
pt=None
for p in J['pages']:
    r=common.eng2runes(p['plaintext_transliteration']); print(p['title'],len(r),'EA',r.count(28))
koan=[p for p in J['pages'] if p['page_label']=='06.jpg'][0]
r=common.eng2runes(koan['plaintext_transliteration'])
# choose the 260-rune window with the most EA so the doublet convention is exercised
best=max(range(0,len(r)-260),key=lambda s:r[s:s+260].count(28)); P=r[best:best+260]
print('window',best,'EA',P.count(28)); print(common.tr(P)[:200])
keys=[l.split() for l in open('keys.txt')]
rng=np.random.default_rng(29)
eng=[i for i,k in enumerate(keys) if k[0]=='0' and 6<=int(k[1])<=12]
units=[];meta=[]
plan=[(1,v) for v in (0b0000000|0, (0<<3)|(0<<2)|(0<<1)|1, (0<<3)|(1<<2)|(1<<1)|0, (5<<3)|(0<<2)|(1<<1)|1, (1<<3)|(1<<2)|(0<<1)|0, (12<<3)|(1<<2)|(1<<1)|0)] \
    +[(2,v) for v in (0,0b0110,0b1011,0b1100)]+[(3,v) for v in range(5)]
uid=90000
for fam,var in plan:
    ki=int(rng.choice(eng)); key=[int(x) for x in keys[ki][2:]]
    prev=int(rng.integers(29))
    c=ciph.enc(fam,P,key,var,rng,prev)
    d=ciph.dec(fam,c,prev,key,var)
    ok = d==P
    units.append((uid,prev,c)); meta.append(dict(uid=uid,fam=fam,var=var,key=ki,keytr=common.tr(key),roundtrip=ok,
        doublets=sum(c[i]==c[i-1] for i in range(1,len(c)))))
    print(meta[-1]); uid+=1
for fam in (1,2,3):
    with open('units_ctrl%d.txt'%fam,'w') as f:
        for (u,pv,c),m in zip(units,meta):
            if m['fam']==fam: f.write('%d %d %d %s\n'%(u,pv,len(c),' '.join(map(str,c))))
json.dump(meta,open('ctrl_meta.json','w'),indent=1)
