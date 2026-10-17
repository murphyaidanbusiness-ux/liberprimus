import sys; sys.path.insert(0,'.')
import numpy as np
from finalists import *
ok=[r for r in rows if not np.isnan(r['z_sh']) and not np.isnan(r['z_ch'])]
ok.sort(key=lambda r:-min(r['z_sh'],r['z_ch']))
seen=set(); fin=[]
for r in ok:
    key=(r['view'][:2],r['src'],r['sem'],r['b'],r['score'])
    if key in seen: continue
    seen.add(key); fin.append(r)
    if len(fin)>=10: break
# also the top by z_sh alone (distinct), to show the doublet artifact
ok2=sorted([r for r in rows if not np.isnan(r['z_sh'])],key=lambda r:-r['z_sh'])
seen2=set(); fin2=[]
for r in ok2:
    key=(r['view'][:2],r['src'],r['sem'],r['b'],r['score'])
    if key in seen2 or key in seen: continue
    seen2.add(key); fin2.append(r)
    if len(fin2)>=4: break
out=[]
for tag,lst in (('TOP by min(z_shuffle,z_chain)',fin),('TOP by z_shuffle alone (doublet artifact check)',fin2)):
    out.append('## '+tag)
    for r in lst:
        t,ioc,wh,mi,si,mw,sw,zw=finalist(r)
        real,zs,zc=refine(r,150)
        line=f"{r['view']} {r['src']} {r['sem']} b={r['b']} {r['mode']} {r['score']}: real={real:.3f} z_sh(150)={zs:.2f} z_ch(150)={zc:.2f} [grid: {r['z_sh']:.2f}/{r['z_ch']:.2f}] | IoC={ioc:.3f} (shuf-null {mi:.3f}+-{si:.3f}) wordhit={wh:.3f} (null {mw:.3f}+-{sw:.3f}, z={zw:.1f})\n    first200: {t}"
        print(line,flush=True); out.append(line)
open(HERE+'/finalists.txt','w').write('\n'.join(out))
