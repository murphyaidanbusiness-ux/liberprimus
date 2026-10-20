"""Lane AB: an independent pure-Python reference for RDP's compiled n-gram kernel (_fastlm.FastTransitionModel).

Re-implements, from fastlm.cpp and the file format only (no RDP code is imported here): the .bin.zst table parse
(header "<4sBHIff", magic WLI0, then keys u64[2^lg], logp f32, counts u64), the smoothing (auto Good-Turing alpha =
N1/(K-N1), logp = log(c + alpha) - log(T + alpha*K)), the out-of-vocabulary floor (minimum seen logp), XXH64 seed 0
over n packed uint32 tokens (rune | pos<<5 | len<<11; pos = len = 0 for the character model) and linear probing.
The sum of joint n-gram log-probabilities over all n-gram windows is what batch_logp / batch_logp_char return.

compare_kernel() scores random and planted texts both ways (RDP's LanguageModelPrime over the compiled kernel, and
this file) and reports the largest absolute and relative difference. Run with the port's environment:
    dl/rdp_venv/Scripts/python.exe -I agents/laneAB_rdp_port/ref_fastlm.py > agents/laneAB_rdp_port/out_ref_fastlm.txt
    dl/rdp_venv/Scripts/python.exe -I agents/laneAB_rdp_port/ref_fastlm.py --orders 3,4 > agents/laneAB_rdp_port/out_ref_fastlm_lm_large.txt
"""
import math
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
LM_ROOT = os.path.join(ROOT, 'dl', 'rdp_port', 'assets', 'language_model', 'lmp')

M64 = (1 << 64) - 1
P1, P2, P3, P4, P5 = (11400714785074694791, 14029467366897019727, 1609587929392839161, 9650029242287828579,
                      2870177450012600261)


def _rotl(x, r):
    return ((x << r) | (x >> (64 - r))) & M64


def xxh64(data, seed=0):
    n, p = len(data), 0
    if n >= 32:
        v = [(seed + P1 + P2) & M64, (seed + P2) & M64, seed & M64, (seed - P1) & M64]
        while p <= n - 32:
            for i in range(4):
                v[i] = _rotl((v[i] + int.from_bytes(data[p:p + 8], 'little') * P2) & M64, 31) * P1 & M64
                p += 8
        h = (_rotl(v[0], 1) + _rotl(v[1], 7) + _rotl(v[2], 12) + _rotl(v[3], 18)) & M64
        for x in v:
            x = _rotl(x * P2 & M64, 31) * P1 & M64
            h = ((h ^ x) * P1 + P4) & M64
    else:
        h = (seed + P5) & M64
    h = (h + n) & M64
    while p + 8 <= n:
        k = _rotl(int.from_bytes(data[p:p + 8], 'little') * P2 & M64, 31) * P1 & M64
        p += 8
        h = (_rotl(h ^ k, 27) * P1 + P4) & M64
    if p + 4 <= n:
        h ^= int.from_bytes(data[p:p + 4], 'little') * P1 & M64
        p += 4
        h = (_rotl(h, 23) * P2 + P3) & M64
    while p < n:
        h ^= data[p] * P5 & M64
        p += 1
        h = _rotl(h, 11) * P1 & M64
    h ^= h >> 33
    h = h * P2 & M64
    h ^= h >> 29
    h = h * P3 & M64
    h ^= h >> 32
    return h


class RefTable:
    """One joint table, parsed with numpy views (no copy) and smoothed in float64 on demand."""

    def __init__(self, path):
        import numpy as np
        import zstandard
        buf = zstandard.ZstdDecompressor().decompress(open(path, 'rb').read())
        magic, version, lg, _z, _mu, _sd = struct.unpack_from('<4sBHIff', buf, 0)
        assert magic == b'WLI0', path
        off = struct.calcsize('<4sBHIff')
        size = 1 << lg
        self.mask = size - 1
        self.keys = np.frombuffer(buf, dtype='<u8', count=size, offset=off)
        off += 8 * size + 4 * size            # stored logp skipped: recomputed from counts as the kernel does
        self.cnts = np.frombuffer(buf, dtype='<u8', count=size, offset=off)
        seen = self.cnts[self.cnts > 0]
        T, K, N1 = int(seen.sum(dtype=np.float64)), int(seen.size), int((seen == 1).sum())
        self.alpha = N1 / (K - N1) if (K > N1 and N1 > 0) else 0.5
        self.den = math.log(T + self.alpha * max(K, 1))
        self.floor = math.log(int(seen.min()) + self.alpha) - self.den
        self.K, self.T, self.N1 = K, T, N1

    def probe(self, key):
        i = key & 0xFFFFFFFF & self.mask
        while True:
            k = int(self.keys[i])
            if k == 0:
                return self.floor
            if k == key:
                c = int(self.cnts[i])
                return math.log(c + self.alpha) - self.den if c else self.floor
            i = (i + 1) & self.mask

    def logp_sum(self, runes, n, wli=None):
        s = 0.0
        for j in range(len(runes) - n + 1):
            toks = []
            for k in range(n):
                r = runes[j + k] & 0x1F
                pos, ln = (wli[j + k] if wli is not None else (0, 0))
                toks.append(r | ((pos & 0x3F) << 5) | ((ln & 0x3F) << 11))
            s += self.probe(xxh64(struct.pack('<%dI' % n, *toks)))
        return s


def table_path(model, mode, n, pos='nose'):
    return os.path.join(LM_ROOT, model, mode, '%s29_joint_%s_%d_%s.bin.zst' % (model, mode, n, pos))


def wli_of(word_lengths):
    out = []
    for L in word_lengths:
        out.extend([i, L] for i in range(L))
    return out


def compare_kernel(n_texts=24, seed=20261019, orders=(1, 2)):
    """Compiled kernel (through RDP's LanguageModelPrime, a fresh one per table) against this reference."""
    sys.path.insert(0, os.path.join(ROOT, 'dl', 'rdp_port', 'src'))
    sys.path.insert(0, os.path.join(ROOT, 'toolbox'))
    os.chdir(ROOT)
    from rdp.scoring.language_model.language_model_prime import LanguageModelPrime
    import runes as TR
    rng = random.Random(seed)
    eng, wid = TR.english_stream(6000)
    import gc
    assert xxh64(b'') == 0xEF46DB3751D8E999, 'xxh64 test vector'
    worst = {}
    rows = []
    for mode in ('ltr', 'rtl'):
        for model in ('char', 'wli'):
            for n in orders:
                lm = LanguageModelPrime(lm_root=LM_ROOT)
                ref = RefTable(table_path(model, mode, n))
                mx_abs = mx_rel = 0.0
                for t in range(n_texts):
                    L = rng.randint(30, 300)
                    if t % 2 == 0:                          # random symbols, random word lengths
                        x = [rng.randrange(29) for _ in range(L)]
                        lens, tot = [], 0
                        while tot < L:
                            w = min(rng.randint(1, 9), L - tot)
                            lens.append(w)
                            tot += w
                    else:                                   # English window with its own word boundaries
                        a = rng.randrange(0, len(eng) - L)
                        x = eng[a:a + L]
                        w = wid[a:a + L]
                        lens, cur = [], 1
                        for i in range(1, L):
                            if w[i] == w[i - 1]:
                                cur += 1
                            else:
                                lens.append(cur)
                                cur = 1
                        lens.append(cur)
                    wl = wli_of(lens)
                    got = lm.score([x], [wl] if model == 'wli' else None, mode, 'nose', n, model)[0].logprob_sum
                    exp = ref.logp_sum(x, n, wl if model == 'wli' else None)
                    d = abs(got - exp)
                    mx_abs = max(mx_abs, d)
                    mx_rel = max(mx_rel, d / max(abs(exp), 1e-12))
                rows.append((mode, model, n, ref.K, ref.T, ref.alpha, n_texts, mx_abs, mx_rel))
                worst[(mode, model, n)] = mx_rel
                del lm, ref
                gc.collect()
    print('kernel vs pure-Python reference (sum of joint n-gram logp per text; %d texts per table, half random, half'
          ' English windows of 30-300 runes; seed %d)' % (n_texts, seed))
    print('mode model n | table K (seen n-grams) T (total count) alpha | texts | max |diff| | max relative diff')
    for r in rows:
        print('%s %s %d | %d %d %.6f | %d | %.3e | %.3e' % r)
    m = max(worst.values())
    print('VERDICT: %s (largest relative difference %.2e; the kernel accumulates in float32)' %
          ('PASS' if m < 1e-5 else 'FAIL', m))


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--orders', default='1,2', help='n-gram orders to check (3,4 need the LM-large assets)')
    sys.stdout.reconfigure(encoding='utf-8')
    compare_kernel(orders=tuple(int(x) for x in ap.parse_args().orders.split(',')))
