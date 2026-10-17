"""Control: dictionary extension (test f) of the true crib/model vs random crib/model pairs at the control opening."""
import json, random, numpy as np, ext, pyfrag, sys
cm=json.load(open('control_meta.json')); lens=cm['lens']
rng=random.Random(11)
out={}
for o0,name in ((900,'chain_runkey'),(910,'vig_skip_kw')):
    c=cm['ctrl'][name]
    true=dict(crib=[24,5,3,24,9],nw=2,model=0 if o0==900 else 3<<24,test='a')
    tr=ext.extend(true,c,-1,0,lens,rounds=4)
    ms=pyfrag.all_models()
    nul=[]
    for k in range(40):
        cr=rng.choice([x for x in cm['cribs'] if len(x[0].split())==2])
        it=dict(crib=cr[1],nw=2,model=rng.choice([m for m in ms if not (m>>28)&1 and ((m>>24)&7)!=4]),test='a')
        nul.append(ext.extend(it,c,-1,0,lens,rounds=4))
    final=[t[-1][0] for t in nul if t and t[-1]]
    print(name,'true trajectory',tr)
    print(name,'null final z: mean %.2f sd %.2f max %.2f'%(np.mean(final),np.std(final),np.max(final)), ' true final z-vs-null %.1f'%((tr[-1][0]-np.mean(final))/np.std(final)))
    out[name]=dict(true=tr,null=nul)
json.dump(out,open('ctrl_ext.json','w'))
