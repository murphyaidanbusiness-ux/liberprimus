exec(open('sr_validate.py').read().split("for skip in range")[0])
paras=blocks[5:]
paras=[re.sub(r'^\s*\d+\.\s+','',p) for p in paras]
paras=[p for i,p in enumerate(paras) if i!=36]
print(decode(paras,'dot',0), score(decode(paras,'dot',0)))
print(len(paras)); print(paras[35][-200:]); print(blocks[5+36])
