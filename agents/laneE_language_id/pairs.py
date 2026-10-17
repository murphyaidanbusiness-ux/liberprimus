import pickle, numpy as np, collections
from variants import VARIANTS
d=pickle.load(open('results_main.pkl','rb')); R=d['R']
B=pickle.load(open('boot.pkl','rb'))
keys=B['keys']; cf0=B['cf0']; cw0=B['cw0']; CF=B['CF']; CW=B['CW']; valid=B['valid']
kidx={k:i for i,k in enumerate(keys)}
out=[]
def P(*a):
    s=' '.join(str(x) for x in a); print(s); out.append(s)
big=[n for n in {k[0] for k in keys} if R[(n,'natural')]['lang']=='en' and R[(n,'natural')]['reg']!='verse' and R[(n,'natural')]['nw']>=30000 and (n,'base (Cicada rules)') in kidx and (n,'-THE/OF/TO') in kidx and (n,'-all function words') in kidx]
big=sorted(big)
P('## Variant comparison across %d English corpora (>=30k words), word-level combined = mean(JS_A/S_A, JS_B/S_B); lower is better'%len(big))
ref='-THE/OF/TO'
P('| variant | median over corpora (word-level) | median over corpora (all 5) | corpora where variant beats ref (-THE/OF/TO) | paired diff vs ref, word-level: median over corpora, 95% boot CI | P(variant better than ref) |')
P('|---|---|---|---|---|---|')
for lab,*_ in VARIANTS:
    ids=[kidx[(n,lab)] for n in big if (n,lab) in kidx]; rid=[kidx[(n,ref)] for n in big if (n,lab) in kidx]
    w0=np.median(cw0[ids]); f0=np.median(cf0[ids])
    dd=CW[:,ids]-CW[:,rid]        # >0 means variant worse
    stat=np.median(dd,1); obs=np.median(cw0[ids]-cw0[rid])
    wins=int(np.sum(cw0[ids]<cw0[rid]))
    lo,hi=np.percentile(stat,[2.5,97.5]); pb=float(np.mean(stat<0))
    P('| %s | %.3f | %.3f | %d/%d | %+.3f [%+.3f, %+.3f] | %.3f |'%(lab,w0,f0,wins,len(ids),obs,lo,hi,pb))
# class-level
fam={'Germanic (nl,da,sv,no,de,is,fo,ang,non,got)':['Dutch: bible-corpus','Danish: bible-corpus','Swedish: bible-corpus','Norwegian: bible-corpus','German: bible-corpus','German: Faust','Icelandic: IcePaHC (hist.)','Faroese: FarPaHC','Old English: Beowulf','Old English: Sacred-Texts corpus (poetry+psalms)','Old Norse: sagas (Perseus/CLTK)','Gothic: Wulfila Bible (PROIEL)'],
 'Romance (fr,it,es)':['French: bible-corpus','Italian: bible-corpus','Spanish: bible-corpus'],
 'Latin (5 corpora)':['Latin: Newton Principia','Latin: Caesar BG','Latin: Virgil Aeneid','Latin: Vulgate (bible-corpus)','Latin: PROIEL treebank'],
 'Celtic (cy,ga)':['Welsh: CCG treebank','Irish: IDT'],
 'Finno-Ugric/Turkic/Basque/Maori':['Finnish: bible-corpus','Hungarian: bible-corpus','Turkish: bible-corpus','Estonian: EDT','Basque: BDT','Maori: bible-corpus'],
 'Esperanto':['Esperanto: bible-corpus']}
enb=[n for n in R if False]
engnat=[(n,'natural') for n in big]+[(n,'natural') for n in ['English: bible-corpus (modern)']]
classes={}
for f,l in fam.items(): classes[f+' [natural]']=[(n,'natural') for n in l if (n,'natural') in kidx]
classes['English prose [natural, unmodified]']=[(n,'base (Cicada rules)') for n in big]
classes['English [-THE/OF/TO]']=[(n,'-THE/OF/TO') for n in big]
classes['English [-THE/OF]']=[(n,'-THE/OF') for n in big]
classes['English [-THE only]']=[(n,'-THE') for n in big]
classes['English [-THE/OF/TO/AND]']=[(n,'-THE/OF/TO/AND') for n in big]
classes['English [-THE/A/AN]']=[(n,'-THE/A/AN') for n in big if (n,'-THE/A/AN') in kidx]
classes['English [letters, no digraphs]']=[(n,'letters (no digraphs)') for n in big]
classes['English [letters, -THE/OF/TO]']=[(n,'letters -THE/OF/TO') for n in big]
classes['English [TH-only merged]']=[(n,'TH-only merged') for n in big]
classes['English [TH-only, -THE/OF/TO]']=[(n,'TH-only -THE/OF/TO') for n in big]
classes['English [-all function words]']=[(n,'-all function words') for n in big if (n,'-all function words') in kidx]
classes['English verse [natural]']=[(n,'natural') for n in ['Whitman Leaves of Grass','Milton Paradise Lost','Shakespeare Hamlet','Shakespeare Macbeth'] if (n,'natural') in kidx]
classes['English KJV-style [natural]']=[(n,'natural') for n in ['KJV Bible (whole)','Tyndale NT','Douay-Rheims','KJB Job','KJB Isaiah','KJB Psalms']]
P('\n## Class-level comparison (best member of each class; bootstrap over the unsolved sample)')
P('| class | n | best member | word-level comb. best (obs) | P(this class is best of all classes) | median-of-class word-level | all-5 combined of best | JS A | JS B |')
P('|---|---|---|---|---|---|---|---|---|')
names=list(classes)
bestcw=np.zeros((CW.shape[0],len(names))); bestid=[]
for j,c in enumerate(names):
    ids=[kidx[k] for k in classes[c]]
    bestcw[:,j]=CW[:,ids].min(1)
    bestid.append(ids[int(np.argmin(cw0[ids]))])
winner=np.argmin(bestcw,1)
obs_=B['obs']
for j in np.argsort([cw0[i] for i in bestid]):
    c=names[j]; ids=[kidx[k] for k in classes[c]]; i=bestid[j]
    P('| %s | %d | %s | %.3f | %.3f | %.3f | %.2f | %.4f | %.4f |'%(c,len(ids),keys[i][0] if keys[i][1]=='natural' else keys[i][0],cw0[i],float(np.mean(winner==j)),np.median(cw0[ids]),cf0[i],obs_[i][0],obs_[i][1]))
# pairwise: best English -THE/OF/TO vs best natural non-English family etc
def pbetter(c1,c2):
    return float(np.mean(bestcw[:,names.index(c1)]<bestcw[:,names.index(c2)]))
P('\nP(best English[-THE/OF/TO] beats best of class):')
for c in names:
    if c.startswith('English [-THE/OF/TO]'): continue
    P('  vs %-55s %.3f'%(c,pbetter('English [-THE/OF/TO]',c)))
open('pairs_out.txt','w').write('\n'.join(out))
