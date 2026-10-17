s=open('fam_self.py').read()
old="""                for form in (4,5):
                    yield dict(label=f'RAW-SELF:{name}|rev{rev}|m29',form=form,X=X,idx=idx.astype(np.int32),K=K,cyc=0,omin=-R,omax=R,rm=0)"""
new="""                for form in (4,5):
                    for (o1,o2) in ((-R,-1),(1,R)):
                        yield dict(label=f'RAW-SELF:{name}|rev{rev}|m29',form=form,X=X,idx=idx.astype(np.int32),K=K,cyc=0,omin=o1,omax=o2,rm=0)"""
assert old in s
open('fam_self.py','w').write(s.replace(old,new))
