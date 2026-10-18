NAME = "dynsub_skip: Chaocipher-29 dynamic substitution, strict skip-on-repeat"
DESCRIPTION = """Key: two random 29-permutations drawn from rng, a cipher wheel L and a plain wheel R.
Encipher plain rune p: k = R.index(p), c = L[k]. If c equals the previous output rune, the would-be output is
discarded, the wheels take one extra step at that k, and p is re-enciphered (repeat until the output differs).
After each emitted rune both wheels step once. Wheel step (Byrne's Chaocipher adapted to 29 symbols, nadir = 14):
L: rotate so the cipher rune is at index 0, move the rune at index 1 to the nadir.
R: rotate so the plain rune is at index 0, rotate one more place, move the rune at index 2 to the nadir.
Strict skip: the output never equals the previous output, so the doublet rate is 0 by construction."""

N = 29
NADIR = N // 2
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
    for p in plain:
        discards = 0
        while True:
            k = right.index(p)
            c = left[k]
            if c != prev:
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
