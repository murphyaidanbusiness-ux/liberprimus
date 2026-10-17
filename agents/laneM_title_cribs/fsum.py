import json, sys, numpy as np
def summ(name):
    r=json.load(open('ftest_%s.json'%name)); out={}
    for t in 'abce':
        it=[x for x in r if x['test']==t]
        if t=='a':
            fz=[x['traj'][-1][0] for x in it if x['traj'] and x['traj'][-1]]
            out[t]=dict(n=len(it),final_z_mean=round(float(np.mean(fz)),2) if fz else None,final_z_max=round(float(np.max(fz)),2) if fz else None,
                        z_by_round=[round(float(np.mean([x['traj'][k][0] for x in it if len(x['traj'])>k and x['traj'][k]])),2) for k in range(3)])
        else:
            out[t]=dict(n=len(it),survive=[sum(1 for x in it if len(x['traj'])>k and x['traj'][k]) for k in range(3)])
    return out
for nm in sys.argv[1:]: print(nm, json.dumps(summ(nm)))
