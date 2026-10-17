"""totient_fskip_kwshift: totient_fskip with a 7-rune keyword added to the prime key by prime index.

K_k = (phi(prime_k) + kw[k mod 7]) mod 29, where kw is 7 runes drawn from rng after k0. Literal F and the collision
skip are as in totient_fskip. The keyword is the only extra key material; the key space is 10,000 * 29^7.
"""
NAME = "totient_fskip_kwshift"
DESCRIPTION = ("totient_fskip with a period-7 keyword shift: K_k = (phi(prime_k) + kw[k mod 7]) mod 29, kw drawn "
               "from rng.")
L = 7


def _primes(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, limit + 1, i)))
    return [i for i in range(limit + 1) if sieve[i]]


PHI29 = [(p - 1) % 29 for p in _primes(1000000)]


def encrypt(plain, words, rng):
    k = rng.randrange(10000)
    kw = [rng.randrange(29) for _ in range(L)]
    assert k + 2 * len(plain) < len(PHI29)
    out, prev = [], None
    for p in plain:
        if p == 0:                              # literal F
            c = 0
        else:
            c = (p + PHI29[k] + kw[k % L]) % 29
            if c == prev:                       # collision skip, one step, re-encipher
                k += 1
                c = (p + PHI29[k] + kw[k % L]) % 29
            k += 1
        out.append(c)
        prev = c
    return out
