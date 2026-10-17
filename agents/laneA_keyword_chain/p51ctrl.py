import sys; sys.argv=['x','28']
exec(open('p51c.py').read().split("MODES=")[0])
import json
J=json.load(open(common.DUK+'/SOLVED-PAGES.json'))
P=common.eng2runes([p for p in J['pages'] if p['page_label']=='06.jpg'][0]['plaintext_transliteration'])[300:563]
rng=np.random.default_rng(5)
for L in (7,28):
    key=list(rng.integers(28,size=L)); var=(1<<3)|(1<<1)  # tau1, EA consumes key (positional key), align0
    c=np.array(ciph.enc(1,P,key,var,rng,prev))
    s,k=climb(make_dec('tau1',c),L,28,rng,restarts=12)
    print('control L=%d tau1 planted: climb score %.3f (true plaintext %.3f) recovered %d/%d key letters'%(L,s,quad(np.array(P)),sum(int(a)==(-b)%28 or int(a)==b for a,b in zip(k,key)),L))
