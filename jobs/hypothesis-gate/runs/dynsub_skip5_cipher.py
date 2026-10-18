NAME = "dynsub_skip5: Chaocipher-29 dynamic substitution, skip-on-repeat at 4 of every 5 letter positions (the 1/5 mechanism)"
DESCRIPTION = """Same key form and wheel step as dynsub_skip (two random 29-permutations from rng, Byrne's Chaocipher step
adapted to 29 symbols, nadir = 14). The skip fires only when the letter position i (0-based in the plaintext) is not
0 mod 5: there, a would-be output equal to the previous output is discarded, the wheels take one extra step, and the
letter is re-enciphered. At positions i = 0 mod 5 a repeat is emitted as it is, so repeats survive only at one
position in five, as in otp_dodge5.py."""

N = 29
NADIR = N // 2
PHASE = 5
MAX_DISCARDS = 100000  # guard against a non-terminating re-encipher loop; never expected to fire
STATS = {"discards": 0}


def _step(left, right, k):
    left = left[k:] + left[:k]
    x = left.pop(1)
    left.insert(NADIR, x)
    right = right[k:] + right[:k]
    right = right[1:] + right[:1]
    x = right.pop(2)
    right.insert(NADIR, x)
    return left, right


def encrypt(plain, words, rng):
    left = list(range(N))
    right = list(range(N))
    rng.shuffle(left)
    rng.shuffle(right)
    STATS["discards"] = 0
    out, prev = [], None
    for i, p in enumerate(plain):
        discards = 0
        while True:
            k = right.index(p)
            c = left[k]
            if c != prev or i % PHASE == 0:
                break
            discards += 1
            if discards > MAX_DISCARDS:
                raise RuntimeError("skip loop did not terminate")
            left, right = _step(left, right, k)
        STATS["discards"] += discards
        out.append(c)
        prev = c
        left, right = _step(left, right, k)
    return out
