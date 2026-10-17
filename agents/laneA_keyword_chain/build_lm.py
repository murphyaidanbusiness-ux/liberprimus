# Rune-domain 4-gram LM from English corpora transliterated with Cicada rules (spaces removed).
import common, numpy as np, re, glob
K=common.DUK+'/data/keys/'
files=['armada18/melville_moby_dick.txt','armada18/emerson_essays_first_series.txt','armada18/emerson_essays_second_series.txt',
 'armada18/plato_republic_jowett.txt','armada18/poe_complete_works.txt','armada18/homer_odyssey_butler.txt','armada19/aristotle_nicomachean_ethics.txt',
 'armada19/bacon_novum_organum.txt','armada18/kjb_genesis.txt','armada18/kjb_psalms.txt','self_reliance.txt']
cnt=np.zeros(29**4,dtype=np.float64); uni=np.zeros(29); tot=0
for f in files:
    t=open(K+f,encoding='utf-8',errors='ignore').read()
    t=re.sub(r'[^A-Za-z]','',t)
    r=np.array(common.eng2runes(t),dtype=np.int64)
    q=((r[:-3]*29+r[1:-2])*29+r[2:-1])*29+r[3:]
    cnt+=np.bincount(q,minlength=29**4); uni+=np.bincount(r,minlength=29); tot+=len(r)
print('runes',tot)
p=uni/uni.sum()
print('unigram', ' '.join('%s:%.4f'%(common.TR[i],p[i]) for i in range(29)))
lp=np.log10((cnt+0.1)/cnt.sum()).astype(np.float32)
lp.tofile(common.LANE+'/quad29.f32'); p.astype(np.float64).tofile(common.LANE+'/uni29.f64')
# English IoC (normalised)
print('English rune IoC', 29*(p**2).sum())
