"""Family means over N seeds from a saved gate_sim.py output, printed beside LP2.

    python jobs/hypothesis-gate/tools/family_means.py jobs/hypothesis-gate/runs/<name>_gate12.txt

Reads the per-seed lines that gate_sim.py prints (doublets, within/cross split, lag-5 hits, the C2c
chi-square row, the C5 rate row and the C6 row) and prints mean, sd, min and max for each statistic, with
the LP2 value. Cross-word share is given two ways: pooled (sum of cross / sum of doublets) and the mean of
the per-seed shares. Written 2026-10-17 for the quagmire_dodge_clock gate; it reads gate output only and
runs no cipher.
"""
import re
import statistics
import sys

LP2 = {"doublets": 86, "cross": 23, "share": 23 / 86, "lag5": 104 / 2105, "lag5_text": "0.0494"}
SEED = re.compile(r"seed (\d+): doublets (\d+) \((\d+) within, (\d+) cross\), lag-5 (\d+)/(\d+)")
C2C = re.compile(r"C2c .*?mod(\d+) chi2 ([\d.]+)\s+LP2 uniform\s+(PASS|FAIL)")
C5 = re.compile(r"C5 within-word lag-5 rate\s+([\d.]+)\s+LP2")
C6 = re.compile(r"C6 cross-word doublets \(LP2-size\)\s+([\d.]+)\s+LP2")
C2 = re.compile(r"C2 doublet rate\s+([\d.]+)\s+LP2")


def fmt(xs, nd=2):
    return "%.*f +- %.*f (%.*f to %.*f)" % (nd, statistics.mean(xs), nd, statistics.stdev(xs), nd, min(xs), nd, max(xs))


def main():
    text = open(sys.argv[1], encoding="utf-8").read()
    seeds = [m.groups() for m in SEED.finditer(text)]
    if not seeds:
        sys.exit("no seed lines found in %s" % sys.argv[1])
    dbl = [int(s[1]) for s in seeds]
    within = [int(s[2]) for s in seeds]
    cross = [int(s[3]) for s in seeds]
    lag_hits = [int(s[4]) for s in seeds]
    lag_pairs = [int(s[5]) for s in seeds]
    share_seed = [c / d for c, d in zip(cross, dbl) if d]
    pooled = sum(cross) / sum(dbl)
    lag_rate = [h / p for h, p in zip(lag_hits, lag_pairs)]
    c2c = [(int(m.group(1)), float(m.group(2)), m.group(3)) for m in C2C.finditer(text)]
    c2c_chi = [c[1] for c in c2c]
    c2c_fail = sum(1 for c in c2c if c[2] == "FAIL")
    c5_rates = [float(m.group(1)) for m in C5.finditer(text)]
    c6 = [float(m.group(1)) for m in C6.finditer(text)]
    c2_rates = [float(m.group(1)) for m in C2.finditer(text)]
    n = len(seeds)
    print("seeds: %d" % n)
    print("%-34s %-44s %s" % ("statistic", "family over %d seeds" % n, "LP2"))
    print("%-34s %-44s %s" % ("doublets", fmt(dbl, 1), LP2["doublets"]))
    print("%-34s %-44s %s" % ("cross-word doublets", fmt(cross, 1), LP2["cross"]))
    print("%-34s %-44s %s" % ("cross-word share, pooled", "%.3f" % pooled, "%.3f" % LP2["share"]))
    print("%-34s %-44s %s" % ("cross-word share, mean of seeds", "%.3f +- %.3f" % (statistics.mean(share_seed), statistics.stdev(share_seed)), "%.3f" % LP2["share"]))
    print("%-34s %-44s %s" % ("within-word lag-5 rate (hits/pairs)", "%.4f mean, pooled %.4f" % (statistics.mean(lag_rate), sum(lag_hits) / sum(lag_pairs)), LP2["lag5_text"]))
    print("%-34s %-44s %s" % ("within-word lag-5 rate (C5 row)", "%.4f mean" % statistics.mean(c5_rates) if c5_rates else "n/a", LP2["lag5_text"]))
    print("%-34s %-44s %s" % ("doublet rate (C2 row)", "%.5f mean" % statistics.mean(c2_rates) if c2_rates else "n/a", "0.00664"))
    print("%-34s %-44s %s" % ("cross-word doublets (C6 row)", fmt(c6, 1) if c6 else "n/a", "23"))
    if c2c:
        worst = max(c2c_chi)
        print("%-34s %-44s %s" % ("C2c worst chi2 (any mod 2..8)", "%.1f (max over seeds); FAIL on %d of %d" % (worst, c2c_fail, len(c2c)), "uniform"))
        print("%-34s %s" % ("C2c modulus per seed", " ".join("mod%d" % c[0] for c in c2c)))


if __name__ == "__main__":
    main()
