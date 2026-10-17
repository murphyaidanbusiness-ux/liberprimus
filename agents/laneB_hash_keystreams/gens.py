import hashlib, hmac
HASHES=['md5','sha1','sha256','sha512','sha3_256','sha3_512','blake2b']
HLEN={'md5':16,'sha1':20,'sha256':32,'sha512':64,'sha3_256':32,'sha3_512':64,'blake2b':64}
def H(name):
    return getattr(hashlib,name)
GTYPES=['ctr_be4','ctr_asc0','ctr_asc1','pre_asc0','chain','chainhex','hmac_ctr']
def stream(gtype, hname, seed, nbytes):
    if gtype.startswith('pbkdf2:'):
        _,salt,it=gtype.split(':'); return pbkdf2_stream(hname,seed,salt.encode(),int(it),nbytes)
    """returns bytes (>= nbytes, multiple of hlen)"""
    h=H(hname); hl=HLEN[hname]; nb=-(-nbytes//hl); out=[]
    if gtype=='ctr_be4':
        for i in range(nb): out.append(h(seed+i.to_bytes(4,'big')).digest())
    elif gtype=='ctr_asc0':
        for i in range(nb): out.append(h(seed+str(i).encode()).digest())
    elif gtype=='ctr_asc1':
        for i in range(1,nb+1): out.append(h(seed+str(i).encode()).digest())
    elif gtype=='pre_asc0':
        for i in range(nb): out.append(h(str(i).encode()+seed).digest())
    elif gtype=='chain':
        d=h(seed).digest()
        for i in range(nb): out.append(d); d=h(d).digest()
    elif gtype=='chainhex':
        d=h(seed).digest()
        for i in range(nb): out.append(d); d=h(d.hex().encode()).digest()
    elif gtype=='hmac_ctr':
        for i in range(nb): out.append(hmac.new(seed,i.to_bytes(4,'big'),h).digest())
    else: raise ValueError(gtype)
    return b''.join(out), hl
def pbkdf2_stream(hname, seed, salt, iters, nbytes):
    hl=HLEN[hname]; nb=-(-nbytes//hl)
    return hashlib.pbkdf2_hmac(hname, seed, salt, iters, dklen=nb*hl), hl
GEN_LIST=[(g,h) for h in HASHES for g in GTYPES]   # 49

PBKDF_LIST=[('pbkdf2:%s:%d'%(salt,it),h) for h in ('sha1','sha256','sha512') for salt in ('','3301') for it in (1,2,3,10,100,1000)]
