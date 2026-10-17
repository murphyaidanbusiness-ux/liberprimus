import json, common
meta=json.load(open('ctrl_meta.json')); keys=[l.split() for l in open('keys.txt')]
def load(fn):
    R={}
    for l in open(fn):
        if l[0]=='#': continue
        t=l.rstrip('\n').split('\t'); R.setdefault((t[0],int(t[1])),[]).append(t[2:])
    return R
for fam in (1,2,3):
    R=load('res_ctrl%d.tsv'%fam)
    for m in meta:
        if m['fam']!=fam: continue
        u=m['uid']; tq=R[('TOPQ',u)]; ti=R[('TOPI',u)]; st=R[('STAT',u)][0]
        rq=[i for i,t in enumerate(tq) if int(t[3])==m['key']]
        ri=[i for i,t in enumerate(ti) if int(t[3])==m['key']]
        top=tq[0]; sec=[t for t in tq if int(t[3])!=m['key']][0]
        mq,sq,mi,si=map(float,st[1:])
        print('F%d var%3d key %-12s | top-quad key %-12s var %3s q %.3f ioc %.3f | planted rank(quad)=%s rank(ioc)=%s | best wrong q %.3f | z_q=%.1f z_ioc=%.1f'%(
          fam,m['var'],m['keytr'],common.tr(map(int,keys[int(top[3])][2:])),top[4],float(top[1]),float(top[2]),rq[:1],ri[:1],float(sec[1]),
          (float(top[1])-mq)/sq,(float(ti[0][1])-mi)/si))
