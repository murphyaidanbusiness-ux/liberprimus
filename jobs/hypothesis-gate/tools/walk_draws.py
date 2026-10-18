"""Key-draw census for a gate cipher: the gate's hard constraints over many key draws, not only the 3 gate seeds.

    python jobs/hypothesis-gate/tools/walk_draws.py CIPHER.py --draws 300     # rng seeds 5000..5299 (not the gate's 1000..)
    python jobs/hypothesis-gate/tools/walk_draws.py CIPHER.py --census        # every key, if the cipher defines
                                                                             # keys_from(kind, k0), KINDS and K0_RANGE

Same fingerprint and bands as gate_sim.py (toolbox/fingerprint.py). It reports, per hard constraint, how many draws
pass, how many pass all hard constraints, and the spread of the decisive values. It does not change the gate.
"""
import importlib.util
import random
import statistics
import sys
from collections import Counter

sys.path[:0] = ["toolbox", "lp"]
import fingerprint as fp  # noqa: E402
import runes as rn  # noqa: E402

HARD = ("C1", "C2 ", "C2b", "C2c", "C3", "C6")  # same hard set as gate_sim.py (C2c added 2026-10-16)


def load(path):
    spec = importlib.util.spec_from_file_location("cipher_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def score(c, words, lines, pages, seed):
    f = fp.fingerprint(c, words, lines, pages, seed=seed)
    rows = fp.gate(f)
    hard = {}
    for row in rows:
        if row[0].startswith(HARD):
            hard[row[0].split()[0]] = row[4] == "PASS"
    return f, hard


def report(label, results):
    total = len(results)
    all_pass = sum(1 for _, hard in results if all(hard.values()))
    print("%s: %d draws" % (label, total))
    for cid in ("C1", "C2", "C2b", "C2c", "C3", "C6"):
        ok = sum(1 for _, hard in results if hard.get(cid, False))
        print("  %-4s passes %4d / %d" % (cid, ok, total))
    print("  all hard constraints pass: %d / %d" % (all_pass, total))
    for key in ("ioc", "doublet_rate", "doublets_cross", "cond_ioc"):
        vals = [f[key] for f, _ in results]
        print("  %-15s min %.5f  median %.5f  max %.5f" % (key, min(vals), statistics.median(vals), max(vals)))
    return all_pass


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    path = args[0]
    draws = 300
    if "--draws" in args:
        i = args.index("--draws"); draws = int(args[i + 1])
    mod = load(path)
    plain, words = rn.english_stream(12956)
    plain, words = list(plain), list(words)
    lines = [i // 22 for i in range(12956)]
    pages = [i // 235 for i in range(12956)]
    print("cipher: %s" % getattr(mod, "NAME", path))
    if "--census" in args:
        kinds = getattr(mod, "KINDS", ("phi", "prime"))
        results, passing = [], []
        for kind in kinds:
            for k0 in range(mod.K0_RANGE):
                g, sigma, base0 = mod.keys_from(kind, k0)
                c = mod.walk(plain, words, g, sigma, base0)
                f, hard = score(c, words, lines, pages, seed=0)
                results.append((f, hard))
                if all(hard.values()):
                    passing.append((kind, k0))
        report("census over %s x K0_RANGE=%d" % (list(kinds), mod.K0_RANGE), results)
        print("  first keys passing all hard constraints:", passing[:20])
        print("  passing count:", len(passing))
    else:
        results = []
        for i in range(draws):
            c = mod.encrypt(plain, words, random.Random(5000 + i))
            f, hard = score(c, words, lines, pages, seed=i)
            results.append((f, hard))
        n_pass = report("random draws (rng seeds 5000..%d)" % (5000 + draws - 1), results)
        print("  distinct draws passing all hard constraints: %d" % n_pass)


if __name__ == "__main__":
    main()
