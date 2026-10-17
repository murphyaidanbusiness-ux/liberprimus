"""Pure-Python 512-bit hash functions that hashlib does not provide, plus the registry
used by hashhunt.py.  Standard library only.  Slow by design (clarity over speed).

  blake512   original BLAKE-512 (SHA-3 finalist, NOT BLAKE2)
  whirlpool  Whirlpool (final, ISO/IEC 10118-3 version)
  skein512   Skein-512-512 (v1.3, no key, no tree)

VECTORS lists (function, message, expected-hex, source note).  A function is
'verified' only if every vector for it passes at import/selftest time; hashhunt.py
reports the status and tags results from unverified functions.
"""
import hashlib

M64 = 0xFFFFFFFFFFFFFFFF

def _rotr(x, n):
    return ((x >> n) | (x << (64 - n))) & M64

def _rotl(x, n):
    return ((x << n) | (x >> (64 - n))) & M64

# ------------------------------------------------------------------ BLAKE-512
_B_C = [0x243F6A8885A308D3, 0x13198A2E03707344, 0xA4093822299F31D0, 0x082EFA98EC4E6C89,
        0x452821E638D01377, 0xBE5466CF34E90C6C, 0xC0AC29B7C97C50DD, 0x3F84D5B5B5470917,
        0x9216D5D98979FB1B, 0xD1310BA698DFB5AC, 0x2FFD72DBD01ADFB7, 0xB8E1AFED6A267E96,
        0xBA7C9045F12C7F99, 0x24A19947B3916CF7, 0x0801F2E2858EFC16, 0x636920D871574E69]
_B_IV = [0x6A09E667F3BCC908, 0xBB67AE8584CAA73B, 0x3C6EF372FE94F82B, 0xA54FF53A5F1D36F1,
         0x510E527FADE682D1, 0x9B05688C2B3E6C1F, 0x1F83D9ABFB41BD6B, 0x5BE0CD19137E2179]
_B_SIGMA = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
            [11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4],
            [7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8],
            [9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13],
            [2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9],
            [12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11],
            [13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10],
            [6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5],
            [10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0]]
_B_COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
           (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]

def _blake_compress(h, block, t):
    m = [int.from_bytes(block[i:i + 8], "big") for i in range(0, 128, 8)]
    v = h[:] + _B_C[:4] + [(t & M64) ^ _B_C[4], (t & M64) ^ _B_C[5],
                           (t >> 64) ^ _B_C[6], (t >> 64) ^ _B_C[7]]
    for r in range(16):
        s = _B_SIGMA[r % 10]
        for i, (a, b, c, d) in enumerate(_B_COLS):
            x, y = s[2 * i], s[2 * i + 1]
            v[a] = (v[a] + v[b] + (m[x] ^ _B_C[y])) & M64
            v[d] = _rotr(v[d] ^ v[a], 32)
            v[c] = (v[c] + v[d]) & M64
            v[b] = _rotr(v[b] ^ v[c], 25)
            v[a] = (v[a] + v[b] + (m[y] ^ _B_C[x])) & M64
            v[d] = _rotr(v[d] ^ v[a], 16)
            v[c] = (v[c] + v[d]) & M64
            v[b] = _rotr(v[b] ^ v[c], 11)
    return [h[i] ^ v[i] ^ v[i + 8] for i in range(8)]   # salt = 0

def blake512(data):
    n = len(data)
    if n % 128 == 111:
        padded = data + b"\x81"
    else:
        padded = data + b"\x80" + b"\0" * ((110 - n) % 128) + b"\x01"
    padded += (n * 8).to_bytes(16, "big")
    h = _B_IV[:]
    for i in range(len(padded) // 128):
        t = min(n, 128 * (i + 1)) * 8 if 128 * i < n else 0   # counter = message bits so far; 0 if block holds none
        h = _blake_compress(h, padded[128 * i:128 * i + 128], t)
    return b"".join(x.to_bytes(8, "big") for x in h)

# ------------------------------------------------------------------ Whirlpool
def _whirl_tables():
    E = [0x1, 0xB, 0x9, 0xC, 0xD, 0x6, 0xF, 0x3, 0xE, 0x8, 0x7, 0x4, 0xA, 0x2, 0x5, 0x0]
    Ei = [E.index(i) for i in range(16)]
    R = [0x7, 0xC, 0xB, 0xD, 0xE, 0x4, 0x9, 0xF, 0x6, 0x3, 0x8, 0xA, 0x2, 0x5, 0x1, 0x0]
    sbox = []
    for x in range(256):
        a, b = E[x >> 4], Ei[x & 15]
        r = R[a ^ b]
        sbox.append((E[a ^ r] << 4) | Ei[b ^ r])

    def mul(a, b):                                     # GF(2^8), x^8+x^4+x^3+x^2+1
        p = 0
        while b:
            if b & 1:
                p ^= a
            a <<= 1
            if a & 0x100:
                a ^= 0x11D
            b >>= 1
        return p
    c0 = []
    for x in range(256):
        s = sbox[x]
        w = 0
        for k in (1, 1, 4, 1, 8, 5, 2, 9):
            w = (w << 8) | mul(s, k)
        c0.append(w)
    tabs = [[_rotr(w, 8 * j) for w in c0] for j in range(8)]
    rc = []
    for r in range(10):
        w = 0
        for j in range(8):
            w = (w << 8) | sbox[8 * r + j]
        rc.append(w)
    return sbox, tabs, rc

_W_SBOX, _W_T, _W_RC = _whirl_tables()

def _whirl_round(x, i):
    t = _W_T
    return (t[0][(x[i] >> 56) & 255] ^ t[1][(x[(i - 1) & 7] >> 48) & 255] ^
            t[2][(x[(i - 2) & 7] >> 40) & 255] ^ t[3][(x[(i - 3) & 7] >> 32) & 255] ^
            t[4][(x[(i - 4) & 7] >> 24) & 255] ^ t[5][(x[(i - 5) & 7] >> 16) & 255] ^
            t[6][(x[(i - 6) & 7] >> 8) & 255] ^ t[7][x[(i - 7) & 7] & 255])

def whirlpool(data):
    n = len(data)
    data += b"\x80" + b"\0" * ((31 - n) % 64) + (n * 8).to_bytes(32, "big")
    h = [0] * 8
    for off in range(0, len(data), 64):
        blk = [int.from_bytes(data[off + 8 * i:off + 8 * i + 8], "big") for i in range(8)]
        k = h[:]
        s = [blk[i] ^ k[i] for i in range(8)]
        for r in range(10):
            k = [_whirl_round(k, i) for i in range(8)]
            k[0] ^= _W_RC[r]
            s = [_whirl_round(s, i) ^ k[i] for i in range(8)]
        h = [h[i] ^ s[i] ^ blk[i] for i in range(8)]
    return b"".join(x.to_bytes(8, "big") for x in h)

# ------------------------------------------------------------------ Skein-512-512
_S_ROT = [(46, 36, 19, 37), (33, 27, 14, 42), (17, 49, 36, 39), (44, 9, 54, 56),
          (39, 30, 34, 24), (13, 50, 10, 17), (25, 29, 39, 43), (8, 35, 56, 22)]
_S_PI = (2, 1, 4, 7, 6, 5, 0, 3)
_S_C240 = 0x1BD11BDAA9FC1A22

def _threefish512(key, tweak, block):
    k = list(key)
    k.append(_S_C240 ^ k[0] ^ k[1] ^ k[2] ^ k[3] ^ k[4] ^ k[5] ^ k[6] ^ k[7])
    t = [tweak[0], tweak[1], tweak[0] ^ tweak[1]]
    v = list(block)

    def inject(s):
        for i in range(8):
            add = k[(s + i) % 9]
            if i == 5:
                add += t[s % 3]
            elif i == 6:
                add += t[(s + 1) % 3]
            elif i == 7:
                add += s
            v[i] = (v[i] + add) & M64
    for d in range(72):
        if d % 4 == 0:
            inject(d // 4)
        rot = _S_ROT[d % 8]
        for j in range(4):
            v[2 * j] = (v[2 * j] + v[2 * j + 1]) & M64
            v[2 * j + 1] = _rotl(v[2 * j + 1], rot[j]) ^ v[2 * j]
        v = [v[p] for p in _S_PI]
    inject(18)
    return v

def _ubi(g, msg, typ):
    n = len(msg)
    nblk = max(1, (n + 63) // 64)
    msg = msg + b"\0" * (nblk * 64 - n)
    for b in range(nblk):
        pos = min(n, 64 * (b + 1))
        t1 = (pos >> 64) & 0xFFFFFFFF | (typ << 56)
        if b == 0:
            t1 |= 1 << 62
        if b == nblk - 1:
            t1 |= 1 << 63
        w = [int.from_bytes(msg[64 * b + 8 * i:64 * b + 8 * i + 8], "little") for i in range(8)]
        e = _threefish512(g, (pos & M64, t1), w)
        g = [e[i] ^ w[i] for i in range(8)]
    return g

def skein512(data):
    cfg = b"SHA3" + (1).to_bytes(2, "little") + b"\0\0" + (512).to_bytes(8, "little") + b"\0" * 16
    g = _ubi([0] * 8, cfg, 4)
    g = _ubi(g, data, 48)
    g = _ubi(g, (0).to_bytes(8, "little"), 63)
    return b"".join(x.to_bytes(8, "little") for x in g)

# ------------------------------------------------------------------ registry + vectors
def _hl(name):
    return lambda d: hashlib.new(name, d).digest()

# name -> (callable, pure_python?)
FUNCS = {
    "sha512": (_hl("sha512"), False),
    "sha3_512": (_hl("sha3_512"), False),
    "blake2b512": (lambda d: hashlib.blake2b(d, digest_size=64).digest(), False),
    "blake512": (blake512, True),
    "whirlpool": (whirlpool, True),
    "skein512": (skein512, True),
}

def Z(n):
    return b"\0" * n

VECTORS = [
    # (function, message, expected hex, source)
    ("blake512", b"", "a8cfbbd73726062df0c6864dda65defe58ef0cc52a5625090fa17601e1eecd1b628e94f396ae402a00acc9eab77b4d4c2e852aaaa25a636d80af3fc7913ef5b8", "BLAKE spec / task brief"),
    ("blake512", Z(1), "97961587f6d970faba6d2478045de6d1fabd09b61ae50932054d52bc29d31be4ff9102b9f69e2bbdb83be13d4b9c06091e5fa0b48bd081b634058be0ec49beb3", "BLAKE spec / task brief"),
    ("blake512", Z(144), "313717d608e9cf758dcb1eb0f0c3cf9fc150b2d500fb33f51c52afc99d358a2f1374b8a38bba7974e7f6ef79cab16f22ce1e649d6e01ad9589c213045d545dde", "BLAKE spec 2nd KAT, 1152-bit zero msg (recalled; exercises multi-block + counter)"),
    ("whirlpool", b"", "19fa61d75522a4669b44e39c1d2e1726c530232130d407f89afee0964997f7a73e83be698b288febcf88e3e03c4f0757ea8964e59b63d93708b138cc42a66eb3", "ISO/NESSIE"),
    ("whirlpool", b"abc", "4e2448a4c6f486bb16b6562c73b4020bf3043e3a731bce721ae1b303d97e6d4c7181eebdb6c57e277d0e34957114cbd6c797fc9d95d8b582d225292076d4eef5", "ISO/NESSIE; also cross-checked with OpenSSL legacy provider"),
    ("whirlpool", b"The quick brown fox jumps over the lazy dog", "b97de512e91e3828b40d2b0fdce9ceb3c4a71f9bea8d88e75c4fa854df36725fd2b52eb6544edcacd6f8beddfea403cb55ae31f03ad62a5ef54e42ee82c3fb35", "Wikipedia/NESSIE"),
    ("whirlpool", b"a" * 31, "698d25826e50bfd1f4e67a1ddbe0d40fac00c4b8f49bd17f706e2f4c5c813249a8a2b771acec2a7425c20406acbc672a2bc83a62150af78f0d804d382658af05", "OpenSSL legacy provider (padding edge n=31)"),
    ("whirlpool", b"a" * 100, "8cbbae13ec2d2dc76df4338be4cc4d138517033daf8b00bbdbcfe46714d4863b275461d1b94baaf3ed44d9829d70af5300209d80166964266db1e371330de73e", "OpenSSL legacy provider (3 blocks)"),
    ("skein512", b"", "bc5b4c50925519c290cc634277ae3d6257212395cba733bbad37a4af0fa06af41fca7903d06564fea7a2d3730dbdb80c1f85562dfcc070334ea4d1d9e72cba7a", "Skein 1.3 KAT, Skein-512-512 empty msg"),
    ("skein512", b"\xff", "71b7bce6fe6452227b9ced6014249e5bf9a9754c3ad618ccc4e0aae16b316cc8ca698d864307ed3e80b6ef1570812ac5272dc409b5a012df2a579102f340617a", "Skein 1.3 KAT, Skein-512-512, msg FF"),
    ("skein512", bytes(range(255, 127, -1)), "91cca510c263c4ddd010530a33073309628631f308747e1bcbaa90e451cab92e5188087af4188773a332303e6667a7a210856f742139000071f48e8ba2a5adb7", "Skein 1.3 KAT, 128-byte msg FF..80 (2 blocks; recalled, matched by independent impl)"),
]

def run_vectors():
    """Return {function: (verified:bool, [(msg_len, ok, source)])}."""
    out = {}
    for name, msg, exp, src in VECTORS:
        ok = FUNCS[name][0](msg).hex() == exp
        out.setdefault(name, [True, []])
        out[name][0] &= ok
        out[name][1].append((len(msg), ok, src))
    for name in ("sha512", "sha3_512", "blake2b512"):
        out[name] = [True, [("hashlib", True, "stdlib")]]
    return {k: (v[0], v[1]) for k, v in out.items()}
