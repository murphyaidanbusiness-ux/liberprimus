"""Sanity checks for the dynamic-substitution gate runs (dynsub_skip, dynsub_skip5).

    python jobs/hypothesis-gate/tools/dynsub_checks.py        (run from the repository root)

1. Every wheel step leaves two permutations of 0..28 (checked by wrapping _step during encryption).
2. Two seeds give different ciphertexts on the same plaintext, and one seed reproduces (the key comes from rng).
3. Discard counts: how many would-be outputs the skip rule discarded on the last call.
4. Reference: PHASE = 1 makes the skip never fire (plain Chaocipher-29). Its doublet rate is the baseline the skip must beat.
"""
import importlib.util
import random
import sys

sys.path[:0] = ["toolbox", "lp"]
import runes as rn  # noqa: E402

ROOT = "jobs/hypothesis-gate/runs/"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def checked(mod):
    orig = mod._step

    def chk(left, right, k):
        left2, right2 = orig(left, right, k)
        assert sorted(left2) == list(range(29)) and sorted(right2) == list(range(29)), "wheel is not a permutation"
        return left2, right2

    mod._step = chk
    return mod


def doublet_rate(c):
    return sum(a == b for a, b in zip(c, c[1:])) / (len(c) - 1)


def main():
    plain, words = rn.english_stream(12956)
    for name in ("dynsub_skip", "dynsub_skip5"):
        mod = checked(load(ROOT + name + "_cipher.py", name))
        c0 = mod.encrypt(list(plain), list(words), random.Random(1000))
        c1 = mod.encrypt(list(plain), list(words), random.Random(1001))
        c0b = mod.encrypt(list(plain), list(words), random.Random(1000))
        print("%s: wheels stay permutations; seeds differ: %s; seed reproducible: %s; discards (seed 1000): %d; "
              "doublet rate (seed 1000): %.5f" % (name, c0 != c1, c0 == c0b, mod.STATS["discards"],
                                                  doublet_rate(c0)))
    ref = checked(load(ROOT + "dynsub_skip5_cipher.py", "ref"))
    ref.PHASE = 1  # i % 1 == 0 always, so the skip never fires: plain Chaocipher-29
    for s in range(3):
        c = ref.encrypt(list(plain), list(words), random.Random(1000 + s))
        print("reference plain Chaocipher-29, seed %d: doublet rate %.4f" % (1000 + s, doublet_rate(c)))


if __name__ == "__main__":
    main()
