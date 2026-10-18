"""totient_fskip_skip45_nolitF: totient_fskip_skip45 with NO literal F (variant of the hypothesis, gated on its own).

Plaintext F (rune 0) is enciphered like any other rune and advances the key. Everything else is as in
totient_fskip_skip45: phi(prime_k) mod 29 key from k0 in range(10000), collision skip at 4 of 5 positions (i mod 5 != 0).
This variant is gated only because the literal-F rule is what breaks C1 in the three hypotheses above.
"""
NAME = "totient_fskip_skip45_nolitF"
DESCRIPTION = ("totient_fskip_skip45 without the literal-F rule: plaintext F is enciphered and advances the key; "
               "collision skip at i mod 5 != 0.")


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
    assert k + 2 * len(plain) < len(PHI29)
    out, prev = [], None
    for i, p in enumerate(plain):
        c = (p + PHI29[k]) % 29
        if c == prev and i % 5 != 0:
            k += 1
            c = (p + PHI29[k]) % 29
        k += 1
        out.append(c)
        prev = c
    return out
