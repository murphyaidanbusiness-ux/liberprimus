"""Control: dictionary extension keeping a keyword hit (test b + f) for every n>=6 keyword hit at the control openings (real 910 vs nulls 911-915)."""
import json, collections, ext
cm=json.load(open('control_meta.json')); lens=cm['lens']
c=cm['ctrl']['vig_skip_kw']
jobc={}; cur=None
for line in open('jobs/control.txt'):
    t=line.split()
    if t[0]=='OPEN': cur=int(t[1]); jobc[cur]=[]; continue
    jobc[cur].append([int(x) for x in t[2:]])
items=collections.defaultdict(list); seen=set()
for line in open('runs/control5_n6.hits'):
    t=line.split(); oid=int(t[1])
    if not 910<=oid<=915 or int(t[5])<6: continue
    if not any(tg.startswith('1:') for tg in t[8:]): continue
    cid,model=int(t[2]),int(t[3])
    if (oid,cid,model) in seen: continue
    seen.add((oid,cid,model)); cr=cm['cribs'][cid]
    items[oid].append(dict(crib=jobc[oid][cid],nw=len(cr[0].split()),model=model,test='b',label=cr[0]))
res={}
for oid in sorted(items):
    surv=[]
    for it in items[oid]:
        tr=ext.extend(it,c,-1,0,lens,rounds=4)
        surv.append((it['label'],it['model'],tr))
    n2=sum(1 for s in surv if len(s[2])>=2 and s[2][1] is not None); n4=sum(1 for s in surv if len(s[2])==4 and s[2][-1] is not None)
    n1=sum(1 for s in surv if s[2] and s[2][0] is not None)
    res[oid]=dict(n_kwhits=len(surv),survive1=n1,survive2=n2,survive4=n4,survivors=[s for s in surv if s[2] and s[2][0] is not None][:20])
    print(oid,'kw hits n>=6:',len(surv),'survive 1 word:',n1,'survive 2 words:',n2,'survive 4 words:',n4,flush=True)
json.dump(res,open('ctrl_extb.json','w'),indent=1)
