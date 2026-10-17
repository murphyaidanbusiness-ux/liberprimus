# Seed -> generator-input conversions (pure Python, my own implementations; validated in validate.py).
import hashlib, zlib
M64=(1<<64)-1
def py2_str_hash(b, wordsize=64):
    """CPython 2.7 Objects/stringobject.c string_hash (hash randomisation off = default). Returns signed long."""
    mod=1<<wordsize; mask=mod-1
    if len(b)==0: return 0
    x=(b[0]<<7)&mask
    for c in b: x=((1000003*x)&mask)^c
    x^=len(b)&mask
    if x>=mod>>1: x-=mod
    if x==-1: x=-2
    return x
def limbs(n):
    n=abs(n); out=[]
    while n: out.append(n&0xffffffff); n>>=32
    return out or [0]
def key_py2(b, wordsize=64):
    """random.seed(str) in CPython 2.7: n=(unsigned long)hash(str) -> init_by_array(32-bit limbs)."""
    h=py2_str_hash(b,wordsize)&((1<<wordsize)-1)
    return limbs(h)
def key_py3(b):
    """random.seed(str/bytes) in CPython >=3.2 (version 2): int.from_bytes(a + sha512(a).digest(), 'big')."""
    return limbs(int.from_bytes(b+hashlib.sha512(b).digest(),'big'))
def java_hash(s):
    """java.lang.String.hashCode over UTF-16 code units, as signed int."""
    h=0
    u=s.encode('utf-16-be')
    for i in range(0,len(u),2):
        h=(31*h+((u[i]<<8)|u[i+1]))&0xffffffff
    return h-(1<<32) if h>=1<<31 else h
def crc32(b): return zlib.crc32(b)&0xffffffff
