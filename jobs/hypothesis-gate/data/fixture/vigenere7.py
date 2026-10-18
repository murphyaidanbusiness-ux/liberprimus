NAME = "Vigenere, period 7"
DESCRIPTION = "c_i = p_i + k_(i mod 7). Periodic, so it must fail C1; additive, so it must fail C2."


def encrypt(plain, words, rng):
    key = [rng.randrange(29) for _ in range(7)]
    return [(p + key[i % 7]) % 29 for i, p in enumerate(plain)]
