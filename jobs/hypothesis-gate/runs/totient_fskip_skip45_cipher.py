"""totient_fskip_skip45: totient_fskip with the collision skip firing at 4 of 5 positions.

Same key, literal F and skip as totient_fskip. The one change: a would-be repeat is skipped only where the plaintext
position i has i mod 5 != 0. At positions with i mod 5 == 0 the repeat is emitted as it is (the otp_dodge5 mechanism,
applied to the prime-totient keystream).
"""
NAME = "totient_fskip_skip45"
DESCRIPTION = ("totient_fskip, but the collision skip fires only at 4 of 5 positions (i mod 5 != 0); "
               "a repeat at i mod 5 == 0 is kept.")


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
        if p == 0:                              # literal F
            c = 0
        else:
            c = (p + PHI29[k]) % 29
            if c == prev and i % 5 != 0:        # skip at 4 of 5 positions only
                k += 1
                c = (p + PHI29[k]) % 29
            k += 1
        out.append(c)
        prev = c
    return out
