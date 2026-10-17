import pickle, numpy as np
d=pickle.load(open('results_main.pkl','rb')); R=d['R']
def comb(r):
    z=r['z'] if r['valid'] else r['z'][:2]
    return float(np.nanmean(z))
rows=[]
for (n,v),r in R.items():
    if v!='natural': continue
    rows.append((comb(r),n,r))
rows.sort(key=lambda x:x[0])
print('%-48s %-5s %6s %6s | JS A,B,C,D,E | z A,B,C,D,E | meanlen meansent'%('natural','lang','combZ','JSsum'))
for c,n,r in rows:
    print('%-48s %-5s %6.2f %6.4f | %s | %s | %.2f %.1f%s'%(n[:48],r['lang'],c,r['js'].sum(),' '.join('%.4f'%x for x in r['js']),' '.join('%5.1f'%x for x in r['z']),r['meanlen'],r['meansent'],'' if r['valid'] else ' (sent invalid)'))
