"""Lane V question 1: is the within-word lag-5 echo localised? Burst scan with a stratum-preserving null.

Scan statistic T = max over windows of the standardised excess Z_w = (O_w - E_w) / sqrt(V_w), where O_w counts the
within-word lag-5 coincidences whose first rune lies in the window, E_w and V_w are the mean and variance of O_w when
the coincidence labels are permuted across all pairs inside each word-length stratum (hypergeometric, with the
stratum totals of the dataset being scanned). Windows: every run of k = 1..10 consecutive LP2 pages (505 windows)
and lane J's nine page-group sections (9 windows). Raw excess is also logged, but it is dominated by the largest
windows, so the standardised form is the statistic.

Null: 2,000 label permutations inside word-length strata (as lp/t7_lag5_lines.py). Threshold for "flagged" =
95th percentile of the null maximum, fixed before the plants are run.

Controls: 50 localised plants (31 extra coincidences, the real echo's excess over 1/29, placed in a random 5-page
block of a no-echo base) and 50 diffuse plants (same 31 spread uniformly over all non-matching pairs), plus a
half-size localised plant (16) for the power curve and 200 no-echo bases for the false-flag rate.

    python -I -X utf8 agents/laneV_lag5_mechanisms/burst_scan.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import common as cm  # noqa: E402

cm.lower_priority()
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
LOG = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


C, wid, page, sec = cm.load_lp2()
N = len(C)
wl = np.bincount(wid)
pa = np.nonzero(wid[:-5] == wid[5:])[0]           # within-word lag-5 pairs, stream order (page nondecreasing)
m_real = (C[pa] == C[pa + 5]).astype(np.int64)
NP = len(pa)
ustr, strata = np.unique(wl[wid[pa]], return_inverse=True)
S = len(ustr)
Ns = np.bincount(strata, minlength=S).astype(float)
pg = page[pa]
P("LP2 within-word lag-5 pairs: %d, coincidences %d (rate %.4f), 1/29 expectation %.1f, excess %.1f"
  % (NP, m_real.sum(), m_real.mean(), NP / 29, m_real.sum() - NP / 29))
P("word-length strata: %d (lengths %s)" % (S, ",".join(str(int(x)) for x in ustr)))

# windows: (pair_lo, pair_hi, first_page, last_page, label)
wins = []
for k in range(1, 11):
    for s in range(0, 55 - k + 1):
        lo = int(np.searchsorted(pg, s, "left"))
        hi = int(np.searchsorted(pg, s + k, "left"))
        wins.append((lo, hi, s, s + k - 1, "pages %d-%d" % (s, s + k - 1)))
for g, (a, b) in enumerate(cm.GROUPS):
    lo = int(np.searchsorted(pg, a, "left"))
    hi = int(np.searchsorted(pg, b + 1, "left"))
    wins.append((lo, hi, a, b, "section %d = pages %d-%d" % (g, a, b)))
LO = np.array([w[0] for w in wins])
HI = np.array([w[1] for w in wins])
NW = len(wins)
OH = np.zeros((NP + 1, S), dtype=np.int64)
OH[1:] = np.cumsum(np.eye(S, dtype=np.int64)[strata], axis=0)
NWS = OH[HI] - OH[LO]                              # windows x strata pair counts (fixed by word structure)
NWN = NWS.sum(1)


def scan(mm, return_all=False):
    """Standardised excess per window for labels mm, with expectations from mm's own stratum totals."""
    Ms = np.bincount(strata, weights=mm, minlength=S)
    q = Ms / Ns
    qv = q * (1 - q)
    E = NWS @ q
    V = (NWS * qv[None, :] * (Ns[None, :] - NWS) / np.maximum(Ns[None, :] - 1, 1)).sum(1)
    cs = np.concatenate([[0], np.cumsum(mm)])
    O = cs[HI] - cs[LO]
    Z = np.where(V > 0, (O - E) / np.sqrt(np.maximum(V, 1e-12)), 0.0)
    if return_all:
        return Z, O, E
    return Z


Z_obs, O_obs, E_obs = scan(m_real, True)
T_obs = float(Z_obs.max())
arg = int(Z_obs.argmax())
exc = O_obs - E_obs
P("\nREAL: %d windows (%d page runs k=1..10, 9 sections)" % (NW, NW - 9))
P("best window: %s   Z = %.3f   observed %d, expected %.2f, excess %+.2f" %
  (wins[arg][4], T_obs, O_obs[arg], E_obs[arg], exc[arg]))
P("largest raw excess: %s  excess %+.2f  (Z %.2f)" % (wins[int(exc.argmax())][4], exc.max(), Z_obs[int(exc.argmax())]))
order = np.argsort(-Z_obs)[:8]
P("top 8 windows by Z:")
for i in order:
    P("  %-28s Z %+.3f  observed %3d  expected %6.2f  excess %+6.2f  pairs %4d" %
      (wins[i][4], Z_obs[i], O_obs[i], E_obs[i], exc[i], NWN[i]))
P("section windows (own totals):")
for i in range(NW - 9, NW):
    P("  %-28s Z %+.3f  observed %3d  expected %6.2f  pairs %4d" % (wins[i][4], Z_obs[i], O_obs[i], E_obs[i], NWN[i]))

# ---- null: stratum-preserving label permutations ----
G = np.argsort(strata, kind="stable")
Sg = strata[G]
mG = m_real[G]
rng = np.random.default_rng(3301)
B = 2000
Tnull = np.empty(B)
for b in range(B):
    r = rng.random(NP)
    perm = np.lexsort((r, Sg))
    mm = np.empty(NP, dtype=np.int64)
    mm[G] = mG[perm]
    assert mm.sum() == m_real.sum()
    Tnull[b] = scan(mm).max()
p_scan = (1 + int((Tnull >= T_obs).sum())) / (B + 1)
mu_T, sd_T, mx_T = Tnull.mean(), Tnull.std(ddof=1), Tnull.max()
t95 = float(np.quantile(Tnull, 0.95))
t99 = float(np.quantile(Tnull, 0.99))
P("\nNULL: %d label permutations within word-length strata (totals kept): max-window Z mean %.3f, sd %.3f, max %.3f"
  % (B, mu_T, sd_T, mx_T))
P("null quantiles: 95%% %.3f   99%% %.3f" % (t95, t99))
P("REAL vs null: T_obs %.3f, z = (%.3f - %.3f)/%.3f = %+.2f; permutation p = %.4f; T_obs above null max: %s"
  % (T_obs, T_obs, mu_T, sd_T, (T_obs - mu_T) / sd_T, p_scan, T_obs > mx_T))
np.save(os.path.join(OUT, "burst_null_T.npy"), Tnull)

# ---- planted controls, threshold fixed at t95 ----
prng = np.random.default_rng(20261017)
BER = 1.0 / 29


FLAT_K = [int(round(Ns[s] * BER)) for s in range(S)]   # flat-rate matches per stratum, 73 in total


def base_labels():
    """No-echo base: exactly FLAT_K random matches inside each word-length stratum (the same permutation
    structure the scan's hypergeometric standardisation assumes; iid Bernoulli labels gave 9% false flags)."""
    mm = np.zeros(NP, dtype=np.int64)
    for s in range(S):
        idx = np.nonzero(strata == s)[0]
        mm[prng.choice(idx, size=FLAT_K[s], replace=False)] = 1
    return mm


def block_of(s, k=5):
    lo = int(np.searchsorted(pg, s, "left"))
    hi = int(np.searchsorted(pg, s + k, "left"))
    return lo, hi


E_TOTAL = int(round(m_real.sum() - NP / 29))      # the real echo's excess over the flat rate, 31
P("\nPLANTS: excess to plant = %d (real %d minus %.1f flat expectation); threshold t95 = %.3f"
  % (E_TOTAL, m_real.sum(), NP / 29, t95))


GP = np.argsort(strata, kind="stable")
SGP = strata[GP]


def own_test(mm, B_p=499):
    """A dataset's own scan and its own stratum-permutation p-value: the same test the real data gets."""
    Z = scan(mm)
    T = float(Z.max())
    mG_ = mm[GP]
    cnt = 0
    for _ in range(B_p):
        perm = np.lexsort((prng.random(NP), SGP))
        m2 = np.empty(NP, dtype=np.int64)
        m2[GP] = mG_[perm]
        cnt += scan(m2).max() >= T
    return Z, T, (1 + cnt) / (B_p + 1)


def run_localised(size, reps=50):
    found = flagged = 0
    rows = []
    for _ in range(reps):
        mm = base_labels()
        s = int(prng.integers(0, 55 - 5 + 1))
        lo, hi = block_of(s)
        non = lo + np.nonzero(mm[lo:hi] == 0)[0]
        pick = prng.choice(non, size=min(size, len(non)), replace=False)
        mm[pick] = 1
        Z, T, p = own_test(mm)
        a = int(Z.argmax())
        hit = p < 0.05
        overlap = not (wins[a][3] < s or wins[a][2] > s + 4)
        flagged += bool(hit)
        found += bool(hit and overlap)
        rows.append((s, wins[a][4], T, p, bool(hit), bool(overlap)))
    return found, flagged, rows


def run_diffuse(size, reps=50):
    flagged = 0
    for _ in range(reps):
        mm = base_labels()
        non = np.nonzero(mm == 0)[0]
        pick = prng.choice(non, size=size, replace=False)
        mm[pick] = 1
        flagged += bool(own_test(mm)[2] < 0.05)
    return flagged


f50, fl50, rows50 = run_localised(E_TOTAL)
f16, fl16, _ = run_localised(E_TOTAL // 2)
d31 = run_diffuse(E_TOTAL)
base_flag = sum(bool(own_test(base_labels())[2] < 0.05) for _ in range(200))
P("(each plant is tested against its own 499 stratum permutations; flag = p < 0.05)")
P("localised plant, same total size (%d extra in one random 5-page block): recovered %d/50 "
  "(flagged and argmax window overlaps the block); flagged at all %d/50" % (E_TOTAL, f50, fl50))
P("localised plant, half size (%d): recovered %d/50 (flagged %d/50)" % (E_TOTAL // 2, f16, fl16))
P("diffuse plant, same total size spread uniformly over non-matching pairs: flagged %d/50 (p < 0.05)" % d31)
P("no-echo bases (no plant, 200 draws): flagged %d/200 = %.3f (nominal 0.05)" % (base_flag, base_flag / 200))
P("localised plant detail (block, argmax window, T, own p, flagged, overlap), first 10:")
for r in rows50[:10]:
    P("  block %2d-%2d  argmax %-26s T %6.2f  p %.3f  flagged %s  overlap %s" % (r[0], r[0] + 4, r[1], r[2], r[3], r[4], r[5]))

with open(os.path.join(OUT, "burst_scan_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LOG) + "\n")
print("wrote", os.path.join(OUT, "burst_scan_out.txt"))
