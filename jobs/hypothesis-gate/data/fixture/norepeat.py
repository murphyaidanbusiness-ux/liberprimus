NAME = "random key, redraw until the output differs from the previous rune"
DESCRIPTION = "Strict no-repeat. Produces zero doublets, so it must fail C2 (LP2 has 86)."


def encrypt(plain, words, rng):
    out, prev = [], None
    for p in plain:
        c = (p + rng.randrange(29)) % 29
        while c == prev:
            c = (p + rng.randrange(29)) % 29
        out.append(c)
        prev = c
    return out
