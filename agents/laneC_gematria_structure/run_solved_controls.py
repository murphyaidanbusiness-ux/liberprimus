import sys, json, time
sys.path.insert(0,'.')
import numpy as np, multiprocessing as mp
import eng, ctrl, fam_solved as F
PLANTS=[
 ('PT.L.prime|L|rev0|rune-contA|m28',0,431),
 ('CT.L.index|L|rev1|rune-pageB|m29',1,450),
 ('PT.W.sum|W|rev0|word-contB'.replace('contB','cont')+'|m28',0,300),
 ('CT.W.totient|Wx|rev0|rune-contB|m29',2,350),
 ('PT.W.cumsum|Wx|rev0|rune-contA|m29',3,400),
 ('CT.L.cumprime|L|rev0|rune-pageB|m28',1,440),
 ('PT.W.pi|W|rev1|word-page|m29',3,200),
 ('RAW:PT.L.index|L|rev0|rune-contB|m29',4,500),
]
def task(args):
    label,form,o=args
    rng=np.random.default_rng(abs(hash((label,form,o)))%2**32)
    words,p,st=ctrl.synth_plain(start=5000+o*13)
    d0=ctrl.dummy_data(p,st)
    sp=[s for s in F.specs(d0) if s['label']==label and s['form']==form][0]
    c=(ctrl.encrypt_raw if label.startswith('RAW') else ctrl.encrypt_with_spec)(sp,p,o,rng)
    d1=eng.Data(c,st)
    # verify the idx arrays identical (same zero pattern)
    t=time.time()
    res=F.run_specs(F.specs(d1))
    top=sorted(res.items(),key=lambda kv:-kv[1][0])[:3]
    # planted result
    pl=res.get(label)
    return dict(label=label,form=form,o=o,planted=pl,top=top,secs=time.time()-t,
                med_other=float(np.median([v[0] for k,v in res.items() if k!=label])),max_other=max(v[0] for k,v in res.items() if k!=label))
if __name__=='__main__':
    with mp.Pool(4) as pool:
        out=pool.map(task,PLANTS)
    json.dump(out,open('ctrl_solved.json','w'),indent=1)
    for r in out:
        print(r['label'],r['form'],r['o'],'planted=',r['planted'],'max_other_z=%.1f'%r['max_other'],'top=',r['top'][0][0] if r['top'] else None)
