import numpy as np, channels as ch, core, json
C=ch.C; Lo=ch.Lo
nl=len(ch.llen)
# composition per line
comp=np.zeros((nl,29))
sep_dash=np.zeros(nl); sep_dot=np.zeros(nl)
line=Lo['line']; word=Lo['word']; sent=Lo['sent']
lid=np.repeat(np.arange(nl),ch.llen)
np.add.at(comp,(lid,C),1)
# separators inside a line: word boundaries between runes in same line
wb=(word[1:]!=word[:-1])&(lid[1:]==lid[:-1])
sb=(sent[1:]!=sent[:-1])&(lid[1:]==lid[:-1])
dash=np.zeros(nl); dot=np.zeros(nl)
np.add.at(dash,lid[1:][wb&~sb],1); np.add.at(dot,lid[1:][sb],1)
X=np.hstack([comp,dash[:,None],dot[:,None]])
def r2(X,y):
    A=np.hstack([X,np.ones((len(y),1))])
    b,res,rk,sv=np.linalg.lstsq(A,y,rcond=None)
    pred=A@b; ss=((y-y.mean())**2).sum()
    return 1-((y-pred)**2).sum()/ss, pred, b
out={}
# (1) justification: model total_width = sum w_r n_r + w_dash*dash + w_dot*dot = const.  Solve A w = 1
A=X
w,res,rk,sv=np.linalg.lstsq(A,np.ones(nl),rcond=None)
pred=A@w
out['width_fit_resid_cv']=float((pred-1).std()/1.0)
# compare to null: shuffle rune identities across lines (keep line lengths and separator counts)
rng=np.random.default_rng(1)
def fitcv(Cs):
    comp2=np.zeros((nl,29)); np.add.at(comp2,(lid,Cs),1)
    A2=np.hstack([comp2,dash[:,None],dot[:,None]])
    w2,_,_,_=np.linalg.lstsq(A2,np.ones(nl),rcond=None)
    return float((A2@w2-1).std())
real=fitcv(C); nulls=[fitcv(rng.permutation(C)) for _ in range(200)]
out['width_fit_resid_sd_real']=real; out['width_fit_resid_sd_null_mean']=float(np.mean(nulls)); out['width_fit_resid_sd_null_sd']=float(np.std(nulls)); out['z']=float((real-np.mean(nulls))/np.std(nulls))
out['line_runes_mean']=float(ch.llen.mean()); out['line_runes_sd']=float(ch.llen.std()); out['line_runes_min']=int(ch.llen.min()); out['line_runes_max']=int(ch.llen.max())
out['line_runes_hist']={int(k):int(v) for k,v in zip(*np.unique(ch.llen,return_counts=True))}
# width in glyph-units: fitted w
out['rune_widths_fitted']={core.TR[i]:round(float(w[i]/w[:29].mean()),2) for i in range(29)}
out['sep_widths']=dict(dash=round(float(w[29]/w[:29].mean()),2),dot=round(float(w[30]/w[:29].mean()),2))
# R2 of line rune count predicted by (dash,dot) alone vs with composition
y=ch.llen.astype(float)
r_sep,_,_=r2(np.stack([dash,dot],1),y)
r_all,_,_=r2(X,y)
out['R2_llen_on_separators']=float(r_sep); out['R2_llen_on_comp+sep']=float(r_all)
# null R2 for comp+sep with shuffled runes
def r2null(Cs):
    comp2=np.zeros((nl,29)); np.add.at(comp2,(lid,Cs),1)
    return r2(np.hstack([comp2,dash[:,None],dot[:,None]]),y)[0]
nn=[r2null(rng.permutation(C)) for _ in range(200)]
out['R2_null_mean']=float(np.mean(nn)); out['R2_null_sd']=float(np.std(nn)); out['R2_z']=float((r_all-np.mean(nn))/np.std(nn))
# residual (slack) sequence autocorrelation
def ac(x,l): x=x-x.mean(); return float((x[:-l]*x[l:]).sum()/(x*x).sum())
for nm,x in (('llen',ch.llen.astype(float)),('lf',ch.lf.astype(float)),('lt',ch.lt.astype(float)),('lw',ch.lw.astype(float))):
    a=[ac(x,l) for l in range(1,11)]
    out['acf_%s'%nm]=[round(v,3) for v in a]; out['acf_%s_z(se=1/sqrt n)'%nm]=[round(v*np.sqrt(len(x)),2) for v in a]
# are breaks mid-word: fraction; break-after-rune chi2
brk_after=np.zeros(29); tot=np.zeros(29)
for r in C[:-1]: tot[r]+=1
ends=np.cumsum(ch.llen)[:-1]-1
for e in ends: brk_after[C[e]]+=1
exp=tot*len(ends)/tot.sum()
out['chi2_break_after_rune']=float(((brk_after-exp)**2/exp).sum()); out['chi2_df']=28
# relation LT_{i-1}+LF_i : length of word split across break
mid=(ch.Lo['word'][ends]==ch.Lo['word'][ends+1])
out['frac_breaks_midword']=float(mid.mean())
# LF distribution vs geometric / word-length distribution: LF when previous break is at a word boundary = full word len
out['LF_hist']={int(k):int(v) for k,v in zip(*np.unique(ch.lf,return_counts=True))}
json.dump(out,open('lines_out.json','w'),indent=1)
print(json.dumps({k:v for k,v in out.items() if k not in('rune_widths_fitted','line_runes_hist','LF_hist')},indent=1))
print(out['rune_widths_fitted'])
