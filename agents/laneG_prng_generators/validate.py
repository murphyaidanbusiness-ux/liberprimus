import subprocess, sys, random, json, numpy as np, os
L=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,L)
from seedfns import *
V=L+'/val'
def vg(idi,mod,n,iv,key=None):
    a=[L+'/vecgen',str(idi),str(mod),str(n),str(iv)]+([str(k) for k in key] if key else [])
    return list(map(int,subprocess.check_output(a).split()))
res=[]
def chk(name,got,ref):
    ok=list(got)==list(ref); res.append((name,ok))
    if not ok: print('FAIL',name,'\n got',list(got)[:20],'\n ref',list(ref)[:20])
N=60
# 1. CPython 2.7: vectors captured from REAL CPython 2.7.3 (dukotah round19/G3 gen_py27._SELFTEST_VECTORS; validation.json gates V2/V3)
PY27={('CICADA3301','random29'):[0,17,2,22,9,22,27,11,10,13,27,11,28,5,26,22],('CICADA3301','grb5_rej'):[1,28,18,23,2,25,24,10,10,25,2,21,12,16,11,20],
('3301','random29'):[15,27,17,1,24,8,12,11,25,27,13,2,28,19,14,22],('3301','grb5_rej'):[17,26,16,19,26,1,11,27,3,9,14,13,0,12,8,27],
('DIVINITY','random29'):[8,25,16,5,22,11,8,3,3,6,5,1,8,3,16,6],('DIVINITY','grb5_rej'):[9,11,28,18,18,6,28,24,6,12,9,18,4,20,3,17],
('THE PRIMES ARE SACRED','random29'):[13,8,19,27,28,24,26,25,11,21,4,17,17,27,10,14],('THE PRIMES ARE SACRED','grb5_rej'):[14,5,9,1,21,24,5,6,26,10,27,28,1,12,1,23],
('cicada3301','random29'):[3,26,27,26,5,20,0,7,16,5,22,26,14,24,4,19],('cicada3301','grb5_rej'):[3,8,28,17,28,4,6,25,22,24,1,25,8,2,18,13],
('an end','random29'):[21,1,1,9,2,10,19,18,21,0,20,21,21,6,22,1],('an end','grb5_rej'):[23,6,1,26,1,13,10,3,24,11,28,21,27,20,19,23],
('ky2khlqdf7qdznac','random29'):[24,9,8,28,9,3,5,10,4,19,25,10,0,20,8,24],('ky2khlqdf7qdznac','grb5_rej'):[26,10,10,0,9,15,7,10,18,4,20,5,27,11,21,5]}
chk('py2 hash64 CICADA3301 == real 2.7.3 value', [py2_str_hash(b'CICADA3301')], [8810433306790406628])
for (s,m),ref in PY27.items():
    chk('py2.7 seed(%r) %s'%(s,m), vg(0 if m=='random29' else 1, -29, 16, 0, key_py2(s.encode())), ref)
# 2. CPython 3 (real interpreter here, 3.13: str seeding algorithm identical to 3.2's version-2 path; _randbelow identical for n<=29)
for sd in [0,1,42,3301,1033,123456789,2**32+5,2**40+7,'cicada','3301','Liber Primus',b'\x00\xffab','DIVINITY']:
    key=limbs(sd) if isinstance(sd,int) else key_py3(sd.encode() if isinstance(sd,str) else sd)
    r=random.Random(sd); chk('py3 randrange(29) %r'%(sd,), vg(1,-29,N,0,key), [r.randrange(29) for _ in range(N)])
    r=random.Random(sd); chk('py3 choice %r'%(sd,), vg(1,-29,N,0,key), [r.choice(range(29)) for _ in range(N)])
    r=random.Random(sd); chk('py3 getrandbits(5)%%29 %r'%(sd,), vg(2,-29,N,0,key), [r.getrandbits(5)%29 for _ in range(N)])
    r=random.Random(sd); chk('py int(random()*29) %r'%(sd,), vg(0,-29,N,0,key), [int(r.random()*29) for _ in range(N)])
    # models with real py3
    r=random.Random(sd); o=[];p=-1
    for _ in range(N):
        v=r.randrange(29)
        while v==p: v=r.randrange(29)
        o.append(v);p=v
    chk('model b py3 %r'%(sd,), vg(1,1,N,0,key), o)
    r=random.Random(sd); o=[];p=-1
    for _ in range(N):
        v=r.randrange(29)
        if v==p: v=r.randrange(29)
        o.append(v);p=v
    chk('model c py3 %r'%(sd,), vg(1,2,N,0,key), o)
    r=random.Random(sd); o=[];p=-1
    for _ in range(N):
        v=r.choice([x for x in range(29) if x!=p]) if p>=0 else r.choice(range(29)); o.append(v);p=v
    chk('model d py3 (choice of list w/o prev) %r'%(sd,), vg(1,3,N,0,key), o)
    r=random.Random(sd); o=[]
    while len(o)<N:
        l=list(range(29)); r.shuffle(l); o+=l
    chk('model s py3 shuffle %r'%(sd,), vg(1,4,N,0,key), o[:N])
    r=random.Random(sd); chk('model e py3 %r'%(sd,), vg(1,5,N,0,key), [1+r.randrange(28) for _ in range(N)])
# 3. numpy legacy RandomState(int) (init_genrand)
for sd in [0,1,42,3301,2**31+11,4294967295]:
    rs=np.random.RandomState(sd); chk('numpy randint(0,29) %d'%sd, vg(5,-29,N,sd), rs.randint(0,29,size=N))
    rs=np.random.RandomState(sd); chk('numpy random_sample*29 %d'%sd, vg(4,-29,N,sd), (rs.random_sample(N)*29).astype(int))
    rs=np.random.RandomState(sd); o=[];p=-1
    for _ in range(N):
        v=rs.randint(0,28) if p>=0 else rs.randint(0,29)
        if p>=0 and v>=p: v+=1
        o.append(v);p=v
    chk('model d numpy %d'%sd, vg(5,3,N,sd), o)
# 4. std::mt19937 (g++) u32%29
for sd in [0,1,5489,3301,4294967295]:
    chk('std::mt19937 %%29 %d'%sd, vg(3,-29,N,sd), list(map(int,subprocess.check_output([V+'/ref_mt',str(sd),str(N)]).split())))
# 5. PHP 8.3 (MT_RAND_MT19937 = PHP>=7.1 behaviour; MT_RAND_PHP = pre-7.1 buggy twist + RAND_RANGE scaling)
for sd in [0,1,42,3301,1033,123456,2**31+5]:
    out=subprocess.check_output(['php',V+'/ref.php',str(sd),str(N)]).decode().strip().split('\n')
    rows=[list(map(int,l.split())) for l in out]
    chk('PHP7 mt_rand(0,28) %d'%sd, vg(7,-29,N,sd), rows[0]); chk('PHP7 mt_rand()%%29 %d'%sd, vg(8,-29,N,sd), rows[1])
    chk('PHP5 mt_rand(0,28) %d'%sd, vg(9,-29,N,sd), rows[2]); chk('PHP5 mt_rand()%%29 %d'%sd, vg(10,-29,N,sd), rows[3])
chk('PHP5 mt_srand(1) mt_rand() first = 1244335972 (known PHP5 value)', [int(subprocess.check_output(['php',V+'/ref.php','1','1']).decode().split('\n')[4])], [1244335972])
# 6. glibc (real libc here)
for sd in [0,1,2,42,3301,1033,2**31-1,2**31+7,4294967295]:
    rows=[list(map(int,l.split())) for l in subprocess.check_output([V+'/ref_c',str(sd),str(N)]).decode().strip().split('\n')]
    chk('glibc rand()%%29 %d'%sd, vg(11,-29,N,sd), rows[0]); chk('glibc scaled %d'%sd, vg(12,-29,N,sd), rows[1])
    chk('glibc div %d'%sd, vg(13,-29,N,sd), rows[2]); chk('drand48 scaled %d'%sd, vg(18,-29,N,sd), rows[3])
    chk('glibc raw rand() %d'%sd, vg(11,-2147483647,N,sd), rows[4])
chk('glibc srand(1) rand() = 1804289383', vg(11,-2147483647,1,1), [1804289383])
# 7. MSVC: known published vector srand(1): 41 18467 6334 26500 19169 15724 11478 29358 26962 24464
chk('MSVC srand(1) raw', vg(14,-32768,10,1), [41,18467,6334,26500,19169,15724,11478,29358,26962,24464])
chk('MSVC srand(1) %29', vg(14,-29,10,1), [x%29 for x in [41,18467,6334,26500,19169,15724,11478,29358,26962,24464]])
chk('MSVC srand(1) scaled', vg(15,-29,10,1), [x*29//32768 for x in [41,18467,6334,26500,19169,15724,11478,29358,26962,24464]])
# 8. Java (real JVM)
for sd in [0,1,42,3301,-1360665919,2**40+3,-5]:
    out=[l for l in subprocess.check_output(['java','-cp',V,'Ref',str(sd),str(N),'cicada'],stderr=subprocess.DEVNULL).decode().strip().split('\n')]
    rows=[list(map(int,l.split())) for l in out[:3]]
    chk('Java nextInt(29) %d'%sd, vg(16,-29,N,sd), rows[0]); chk('Java nextDouble*29 %d'%sd, vg(17,-29,N,sd), rows[1])
    chk('Java Collections.shuffle blocks %d'%sd, vg(16,4,N,sd), rows[2])
    chk('Java String.hashCode', [java_hash('cicada')], [int(out[3])])
nok=sum(o for _,o in res); print('validation: %d/%d PASS'%(nok,len(res)))
json.dump(res,open(L+'/validation.json','w'),indent=0)
