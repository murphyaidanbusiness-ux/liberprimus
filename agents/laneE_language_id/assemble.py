def inc(f): return open(f).read().strip()
T=open('results_template.md').read()
import re
T=re.sub(r'\{\{(.+?)\}\}',lambda m:inc(m.group(1)),T)
open('RESULTS.md','w').write(T)
