import numpy as np, channels as ch, core, json
C=ch.C; nl=len(ch.llen)
exec(open('lines2.py').read().split("sd,w=fit(C,keep)")[0].split("rng=np.random.default_rng(2)")[0])
def fitw(Cs,keep):
    comp=np.zeros((nl,29)); np.add.at(comp,(lid,Cs),1)
    A=np.hstack([comp,dash[:,None],dot[:,None]])[keep]
    w,_,_,_=np.linalg.lstsq(A,np.ones(keep.sum()),rcond=None); return w
# fit widths WITHOUT using first rune of each line (exclude it from composition) to remove circularity
st=np.concatenate(([0],np.cumsum(ch.llen)[:-1]))
mask=np.ones(len(C),bool); mask[st]=False
comp=np.zeros((nl,29)); np.add.at(comp,(lid[mask],C[mask]),1)
A=np.hstack([comp,dash[:,None],dot[:,None]])[keep]
w,_,_,_=np.linalg.lstsq(A,np.ones(keep.sum()),rcond=None)
w=w[:29]/w[:29].mean()
fl=C[st]
cnt=np.bincount(fl,minlength=29); tot=np.bincount(C,minlength=29)
enr=(cnt/len(fl))/(tot/len(C))
r=np.corrcoef(w,enr)[0,1]
rng=np.random.default_rng(3)
nn=[np.corrcoef(w,np.bincount(C[np.concatenate(([0],np.cumsum(rng.permutation(ch.llen)[:-1])))],minlength=29)/len(fl)/(tot/len(C)))[0,1] for _ in range(1000)]
print('corr(fitted width [fit excludes first runes], enrichment of rune as line-first) = %.3f ; null %.3f +- %.3f ; z=%.1f'%(r,np.mean(nn),np.std(nn),(r-np.mean(nn))/np.std(nn)))
print({core.TR[i]:(round(w[i],2),round(enr[i],2)) for i in range(29)})
# chi2 of FL after regressing out width: predicted FL freq ∝ tot*w
pred=tot*w; pred=pred/pred.sum()*len(fl)
print('chi2 FL vs uniform-expected %.1f ; vs width-proportional %.1f (df 28)'%(((cnt-tot/len(C)*len(fl))**2/(tot/len(C)*len(fl))).sum(),((cnt-pred)**2/pred).sum()))
