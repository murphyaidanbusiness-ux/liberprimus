"""Oosterhof doublet-dodge walk with g, sigma and base0 generated from the prime/totient ladder (the prime-seeded family).

The ladder is the one that reproduces the solved page 56 (AN END, dl/dukotah/analysis/reproduce/reproduce_page_56_an_end.py):
  phi stream:   t_j = (p_j - 1) mod 29        (Euler totient of the j-th prime, p_0 = 2)
  prime stream: t_j =  p_j      mod 29
A permutation of the 29 runes is the ORDER in which the 29 residues first appear in the stream read from index s:
  ordering(kind, s) = first-appearance order of stream values from index s, within a window of 1,000 primes.
Every key is then fixed by one offset k0 and one stream choice:
  g      order-5: the first 25 runes of ordering(kind, k0) form five 5-cycles in consecutive blocks; the last 4 are fixed
  sigma  = ordering(kind, k0 + 1000)
  base0  = ordering(kind, k0 + 2000)
Key space: k0 in 0..9999 times kind in {phi, prime} = 20,000 keys. The walk rule is the same as walk_dodge_random_cipher.py.
"""
import random

NAME = "walk_dodge_prime: doublet-dodge walk, g/sigma/base0 from the prime/totient ladder at offset k0"
DESCRIPTION = "Key = (k0 in 0..9999, stream in {phi, prime}); 20,000 keys. Every permutation is read from the ladder."

M = 29
WINDOW = 1000
K0_RANGE = 10000


def _primes(limit):
    s = bytearray([1]) * (limit + 1)
    s[0] = s[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(range(i * i, limit + 1, i)))
    return [i for i in range(limit + 1) if s[i]]


PR = _primes(200000)  # 17,984 primes; the largest index read is 9999 + 2 * 1000 + 1000


def stream_value(kind, j):
    p = PR[j]
    return (p - 1) % M if kind == "phi" else p % M


def ordering(kind, start):
    seen = []
    for j in range(start, start + WINDOW):
        v = stream_value(kind, j)
        if v not in seen:
            seen.append(v)
            if len(seen) == M:
                break
    if len(seen) < M:
        # The ladder never produces one residue: the only prime congruent to 0 mod 29 is 29 itself, so residue 28
        # (phi stream) or 0 (prime stream) is absent from every window after index 9. This convention places the
        # missing residue LAST, so it becomes a fixed point of g (the walk_dodge_prime_front variant places it FIRST).
        seen += [v for v in range(M) if v not in seen]
    return seen


def keys_from(kind, k0):
    o = ordering(kind, k0)
    g = list(range(M))
    for c in range(5):
        cyc = o[5 * c: 5 * c + 5]
        for t in range(5):
            g[cyc[t]] = cyc[(t + 1) % 5]
    sigma = ordering(kind, k0 + WINDOW)
    base0 = ordering(kind, k0 + 2 * WINDOW)
    return g, sigma, base0


def compose(a, b):
    return [a[b[x]] for x in range(M)]


def ppow(g, k):
    out = list(range(M))
    for _ in range(k):
        out = compose(g, out)
    return out


def walk(plain, words, g, sigma, base):
    gp = [ppow(g, k) for k in range(5)]
    out = []
    clock = 0
    prev = None
    n = len(plain)
    i = 0
    while i < n:
        j = i
        while j < n and words[j] == words[i]:
            j += 1
        for k in range(i, j):
            p = plain[k]
            c = base[gp[clock % 5][p]]
            if c == prev:
                clock += 1
                c = base[gp[clock % 5][p]]
            out.append(c)
            prev = c
            clock += 1
        base = compose(base, compose(gp[(clock - 1) % 5], sigma))
        i = j
    return out


def encrypt(plain, words, rng):
    k0 = rng.randrange(K0_RANGE)
    kind = rng.choice(["phi", "prime"])
    g, sigma, base0 = keys_from(kind, k0)
    return walk(plain, words, g, sigma, base0)
