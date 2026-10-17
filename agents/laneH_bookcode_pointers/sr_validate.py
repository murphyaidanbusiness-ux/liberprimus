import re,itertools
S='.'
raw=open(S+'/dl/dukotah/liber-primus/data/keys/self_reliance.txt',encoding='utf-8').read()
raw=re.sub(r'\[\d+\]','',raw)
blocks=[b for b in re.split(r'\n\s*\n',raw) if b.strip()]
print(len(blocks))
for i,b in enumerate(blocks[:8]): print(i,repr(b[:70]))
target='auqgnxjtvdbll3pv'
tuples=[(1,2,3,1),(3,3,13,5),(45,5,2,3),(20,3,20,5),(8,3,8,6),(48,5,14,2),(21,13,4,1),(25,1,7,4),(15,9,3,4),(1,1,16,3),(4,3,3,1),(8,3,26,4),(47,3,3,5),None,(13,2,5,4),(1,4,16,4)]
def sents(p, mode):
    p=' '.join(p.split())
    if mode=='dot': pat=r'(?<=[.!?])["”]?\s+'
    elif mode=='dotsemi': pat=r'(?<=[.!?;:])["”]?\s+'
    return [s for s in re.split(pat,p) if s.strip()]
def words(s): return re.findall(r"[A-Za-z0-9']+(?:-[A-Za-z]+)*",s)
def decode(paras,mode,wmode):
    out=[]; ok=0
    for t in tuples:
        if t is None: out.append('3'); continue
        try:
            P=paras[t[0]-1]; ss=sents(P,mode); s=ss[t[1]-1]
            ws=words(s) if wmode==0 else s.split()
            w=ws[t[2]-1]; w=re.sub(r'[^A-Za-z0-9]','',w) if wmode==1 else w
            ch=w[t[3]-1]; out.append(ch.lower())
        except Exception as e: out.append('?')
    return ''.join(out)
def score(o): return sum(a==b for a,b in zip(o,target))
for skip in range(0,6):
  for mode in ('dot','dotsemi'):
    for wmode in (0,1):
      paras=blocks[skip:]
      o=decode(paras,mode,wmode); print(skip,mode,wmode,o,score(o))
print('----')
paras=blocks[5:]
print(len(paras))
for t in [(45,5,2,3),(48,5,14,2),(47,3,3,5),(21,13,4,1)]:
    P=paras[t[0]-1]; ss=sents(P,'dot'); print(t,len(ss),[s[:60] for s in ss[:t[1]+1]])
for k in (44,45,46,47,48): print(k+1, paras[k][:100].replace('\n',' '))
