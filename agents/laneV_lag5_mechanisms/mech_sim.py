"""Lane V question 2, simulation stage: lag profiles of each candidate mechanism on English runes laid out as LP2.

Plaintext: the gate's English rune stream (toolbox/runes.py, Moby-Dick), cut into LP2's exact word-length sequence
(the within/cross split and the pair counts depend on word lengths, so the streams share LP2's word ids).
Each replicate uses a different English passage, so the spread includes plaintext variation as well as key variation.

Mechanisms (simulators from the hypothesis gate, unchanged):
  walk     jobs/hypothesis-gate/runs/walk_dodge_random_cipher.py        Oosterhof walk, doublet dodge, period-5 alphabets
  quagmire jobs/hypothesis-gate/runs/quagmire_odometer_dodge_cipher.py  lane O's family (community encipher, needs dl/)
  dynsub5  jobs/hypothesis-gate/runs/dynsub_skip5_cipher.py             Chaocipher-29, skip-on-repeat at 4 of 5 positions
  totient  jobs/hypothesis-gate/runs/totient_fskip_skip45_nolitF_cipher.py  phi(prime) key, skip at 4 of 5 positions
  base     jobs/hypothesis-gate/data/fixture/otp_dodge5.py              random key, dodge at 4 of 5 phases: no-echo baseline

Usage:
  python -I -X utf8 agents/laneV_lag5_mechanisms/mech_sim.py --probe          time one stream per mechanism
  python -I -X utf8 agents/laneV_lag5_mechanisms/mech_sim.py --run            train 40 + held-out 20 per mechanism
Output: out/mech_profiles.npz (train and held-out 20-cell profiles), out/mech_sim_out.txt (log).
"""
import importlib.util
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import site  # noqa: E402
# -I leaves out the user site-packages, where this machine's scipy lives; the community port's imports need it.
# Appended (not prepended) so the repo's own modules still win.
if os.path.isdir(site.getusersitepackages()):
    sys.path.append(site.getusersitepackages())
import numpy as np  # noqa: E402
import common as cm  # noqa: E402

MECHS = [
    ("walk", "jobs/hypothesis-gate/runs/walk_dodge_random_cipher.py"),
    ("quagmire", "jobs/hypothesis-gate/runs/quagmire_odometer_dodge_cipher.py"),
    ("dynsub5", "jobs/hypothesis-gate/runs/dynsub_skip5_cipher.py"),
    ("totient", "jobs/hypothesis-gate/runs/totient_fskip_skip45_nolitF_cipher.py"),
    ("base", "jobs/hypothesis-gate/data/fixture/otp_dodge5.py"),
]
NTRAIN, NTEST = 40, 20
SEG = 13000            # English runes per passage; passages are disjoint for different replicates

_MODS = {}


def module(key):
    if key not in _MODS:
        path = dict(MECHS)[key]
        spec = importlib.util.spec_from_file_location("lanev_" + key, os.path.join(cm.ROOT, path))
        mod = importlib.util.module_from_spec(spec)
        cwd = os.getcwd()
        os.chdir(cm.ROOT)          # quagmire's simulator resolves dl/aldegonde_port relative to the repo root
        try:
            spec.loader.exec_module(mod)
        finally:
            os.chdir(cwd)
        _MODS[key] = mod
    return _MODS[key]


def simulate(key, seed, start):
    """One ciphertext for mechanism `key`: returns the 20-cell profile (within k=1..10, cross k=1..10) and length."""
    C0, wid, page, sec = _LP
    plain = cm.english_segment(len(wid), start).tolist()
    words = wid.tolist()
    cipher = module(key).encrypt(plain, words, random.Random(seed))
    cipher = np.array(cipher, dtype=np.int64)
    assert len(cipher) == len(wid), (key, len(cipher))
    assert cipher.min() >= 0 and cipher.max() < cm.M
    mw, nw, mx, nx = cm.lag_profile(cipher, wid)
    return np.concatenate([mw / np.maximum(nw, 1), mx / np.maximum(nx, 1)]), np.concatenate([mw, mx])


_LP = None


def init_worker():
    global _LP
    cm.lower_priority()
    _LP = cm.load_lp2()


def job(args):
    key, kind, j, mi = args
    if kind == "train":
        seed = 100000 * (mi + 1) + j
        start = SEG * j
    else:
        seed = 900000 + 100000 * (mi + 1) + j
        start = SEG * (NTRAIN + j)
    t = time.time()
    rates, counts = simulate(key, seed, start)
    return key, kind, j, rates.tolist(), counts.tolist(), round(time.time() - t, 2)


def probe():
    init_worker()
    wid = _LP[1]
    E = cm.english_runes()
    print("English runes available: %d; LP2 runes: %d; passages used: %d train + %d held-out"
          % (len(E), len(wid), NTRAIN, NTEST), flush=True)
    for mi, (key, _) in enumerate(MECHS):
        simulate(key, 42 + mi, 0)                       # warm-up (imports)
        t = time.time()
        rates, counts = simulate(key, 4242 + mi, 0)
        print("%-9s one stream %.2f s   within lag-5 rate %.4f   cross lag-1 rate %.4f"
              % (key, time.time() - t, rates[4], rates[10]), flush=True)


def run():
    import math
    import multiprocessing as mp
    cm.lower_priority()
    _, wid, _, _ = cm.load_lp2()
    print("English runes available: %d; LP2 runes: %d; passages used: %d train + %d held-out (%d runes each, disjoint)"
          % (len(cm.english_runes()), len(wid), NTRAIN, NTEST, SEG), flush=True)
    lg10 = lambda x: math.lgamma(x + 1) / math.log(10)          # log10 of x!
    ks = {"walk": 2 * lg10(29) + math.log10(math.comb(29, 4)) + lg10(25) - lg10(5) - 5 * math.log10(5),
          "dynsub5": 2 * lg10(29), "quagmire (alphabet only)": lg10(29), "totient": math.log10(10000)}
    print("key spaces, log10 size: " + ", ".join("%s %.1f" % (k, v) for k, v in ks.items()), flush=True)
    tasks = []
    for mi, (key, _) in enumerate(MECHS):
        for j in range(NTRAIN):
            tasks.append((key, "train", j, mi))
        for j in range(NTEST):
            tasks.append((key, "test", j, mi))
    res = {}
    logs = []
    t0 = time.time()
    with mp.get_context("spawn").Pool(2, initializer=init_worker) as pool:
        for out in pool.imap_unordered(job, tasks, chunksize=1):
            key, kind, j, rates, counts, secs = out
            res[(key, kind, j)] = (rates, counts)
            logs.append("%s %s %2d  %.2f s" % (key, kind, j, secs))
            if len(res) % 25 == 0:
                print("done %d/%d streams, %.0f s elapsed" % (len(res), len(tasks), time.time() - t0), flush=True)
    names = [k for k, _ in MECHS]
    tr = np.array([[res[(k, "train", j)][0] for j in range(NTRAIN)] for k in names])
    te = np.array([[res[(k, "test", j)][0] for j in range(NTEST)] for k in names])
    trc = np.array([[res[(k, "train", j)][1] for j in range(NTRAIN)] for k in names])
    tec = np.array([[res[(k, "test", j)][1] for j in range(NTEST)] for k in names])
    np.savez(os.path.join(HERE, "out", "mech_profiles.npz"), names=np.array(names), train=tr, test=te,
             train_counts=trc, test_counts=tec)
    with open(os.path.join(HERE, "out", "mech_sim_timing.txt"), "w") as fh:
        fh.write("\n".join(sorted(logs)) + "\n")
    print("saved %d streams in %.0f s" % (len(res), time.time() - t0), flush=True)


if __name__ == "__main__":
    if "--probe" in sys.argv:
        probe()
    else:
        run()
