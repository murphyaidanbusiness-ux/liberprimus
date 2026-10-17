NAME = "random key, dodge on repeat except at clock phase 0 (the 1/5 mechanism)"
DESCRIPTION = """c_i = p_i + k_j; if c_i would equal c_(i-1) and the clock phase j mod 5 is not 0, consume the next key value and
re-encipher. Repeats survive only at one phase in five, so about 1/5 x 1/29 of positions are doublets."""


def encrypt(plain, words, rng):
    out, j, prev = [], 0, None
    key = [rng.randrange(29) for _ in range(3 * len(plain) + 10)]
    for p in plain:
        c = (p + key[j]) % 29
        if c == prev and j % 5 != 0:
            j += 1
            c = (p + key[j]) % 29
        out.append(c)
        prev = c
        j += 1
    return out
