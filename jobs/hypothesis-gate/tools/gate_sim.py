"""Simulate a cipher hypothesis on English and grade the ciphertext against LP2's fingerprint.

    python jobs/hypothesis-gate/tools/gate_sim.py CIPHER.py [--seeds 3] [--n 12956]

CIPHER.py defines   encrypt(plain, words, rng) -> list of rune indices (same length as plain)
  plain  list of rune indices 0..28 (English, toolbox/runes.english_stream)
  words  word id per rune (so a cipher can restart or step per word)
  rng    random.Random, seeded; draw every key from it
and optionally NAME and DESCRIPTION strings.

Prints the gate table (toolbox/fingerprint.gate) per seed and a final line:
  GATE PASS                      no hard constraint (C1 C2 C2b C2c C3 C6) fails on a majority of seeds
  GATE PASS (marginal: <ids>)    as above, but these failed on a minority of seeds (key-to-key spread)
  GATE FAIL: <ids>               these failed on a majority of seeds
Each seed is a fresh random key, so the seeds sample the family's own spread; one unlucky key is not a verdict.
C4 (layout) and C5 (lag-5 echo, soft) are reported but do not decide the gate.
"""
import importlib.util
import random
import sys

sys.path[:0] = ["toolbox", "lp"]
import fingerprint as fp  # noqa: E402
import runes as rn  # noqa: E402

HARD = ("C1", "C2 ", "C2b", "C2c", "C3", "C6")


def load(path):
    spec = importlib.util.spec_from_file_location("cipher_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    args = sys.argv[1:]
    seeds, n = 3, 12956
    if "--seeds" in args:
        i = args.index("--seeds"); seeds = int(args[i + 1]); del args[i:i + 2]
    if "--n" in args:
        i = args.index("--n"); n = int(args[i + 1]); del args[i:i + 2]
    mod = load(args[0])
    plain, words = rn.english_stream(n)
    lines = [i // 22 for i in range(n)]          # LP2 lines average 21.8 runes
    pages = [i // 235 for i in range(n)]         # LP2 pages average 235.6 runes
    print("cipher: %s" % getattr(mod, "NAME", args[0]))
    fails = {}
    for s in range(seeds):
        c = mod.encrypt(list(plain), list(words), random.Random(1000 + s))
        assert len(c) == len(plain) and all(0 <= x < 29 for x in c), "encrypt must return one rune 0..28 per input rune"
        f = fp.fingerprint(c, words, lines, pages, seed=s)
        print("seed %d: doublets %d (%d within, %d cross), lag-5 %d/%d" % (
            s, f["doublets"], f["doublets_within"], f["doublets_cross"], f["lag5_hits"], f["lag5_pairs"]))
        for row in fp.gate(f):
            print("  %-36s %-10s LP2 %-8s %s" % (row[0], row[1], row[2], row[4]))
            if row[0].startswith(HARD) and row[4] == "FAIL":
                fails[row[0].split()[0]] = fails.get(row[0].split()[0], 0) + 1
    hard = sorted(k for k, v in fails.items() if v > seeds / 2)
    marginal = sorted(k for k, v in fails.items() if v <= seeds / 2)
    print("fails per constraint over %d seeds: %s" % (seeds, fails or "none"))
    if hard:
        print("GATE FAIL: " + " ".join(hard))
    else:
        print("GATE PASS" + (" (marginal: %s)" % " ".join(marginal) if marginal else ""))


if __name__ == "__main__":
    main()
