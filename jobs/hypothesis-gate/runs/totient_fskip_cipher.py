"""totient_fskip: prime-totient keystream, literal F, collision skip (toolbox/TECHNIQUES.md entry A2).

Key: K_k = phi(prime_k) mod 29 = (prime_k - 1) mod 29, k indexing the primes 2, 3, 5, 7, ...
Enciphering: c = (p + K_k) mod 29, so the solved-page decryption is p = c - (prime_k - 1) mod 29.
Literal F (rune 0): emitted as F, k not advanced (the F is not enciphered).
Collision skip: if the enciphered rune would equal the previous output rune, k += 1 once and re-encipher.
The emitted rune then advances k by one. The only key drawn from rng is k0, in range(10000).
"""
NAME = "totient_fskip"
DESCRIPTION = ("phi(prime_k) mod 29 keystream from a random start k0 in the first 10,000 primes; plaintext F passed "
               "through literally without a key step; if the output would repeat the previous output, advance k once "
               "and re-encipher.")


def _primes(limit):
    sieve = bytearray([1]) * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, limit + 1, i)))
    return [i for i in range(limit + 1) if sieve[i]]


PHI29 = [(p - 1) % 29 for p in _primes(1000000)]  # 78,498 primes: enough for k0 + 2 per rune at n = 12,956


def encrypt(plain, words, rng):
    k = rng.randrange(10000)
    assert k + 2 * len(plain) < len(PHI29)
    out, prev = [], None
    for p in plain:
        if p == 0:                              # literal F: emitted as is, no key step
            c = 0
        else:
            c = (p + PHI29[k]) % 29
            if c == prev:                       # collision skip: one extra key step, re-encipher once
                k += 1
                c = (p + PHI29[k]) % 29
            k += 1
        out.append(c)
        prev = c
    return out
