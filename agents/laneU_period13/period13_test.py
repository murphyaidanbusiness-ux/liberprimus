"""Lane U: period-13 delta-match test on the 308-rune section the community calls '54-55'.

Run from the repository root (single process, below-normal priority):
    python agents/laneU_period13/period13_test.py

Section mapping: the wiki row 'Hollow | 54-55 | 308 runes | 3 doublets' is lpdata pages 53 and 54
(232 + 76 = 308 runes). See RESULTS.md, Hypothesis, for the evidence.

Statistic (fixed before the run): delta-match count at lag k on the increment stream
    D_i = (c_i - c_(i-1)) mod 29,  i = 1..307 (zero increments kept, no interrupter removal)
    M_k = #{ j : D_j = D_(j+k) }
Fixed rule: period 13 is flagged iff M_13 > T13, where T13 is the 99th percentile of M_13 over
10,000 null draws (the increments of the section shuffled, which keeps the zero-increment count).
"""
import ctypes
import json
import os
import sys
import time

# Lower this process to BELOW_NORMAL priority (0x4000) before any work, as the job asks.
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)

import numpy as np  # noqa: E402

sys.path.insert(0, "lp")
sys.path.insert(0, "toolbox")
import lpdata  # noqa: E402
import runes  # noqa: E402

OUT = "agents/laneU_period13/out"
os.makedirs(OUT, exist_ok=True)
LOG = open(os.path.join(OUT, "period13_log.txt"), "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.write(s + "\n")
    LOG.flush()


M = 29
K = np.arange(2, 41)            # periods scanned (look-elsewhere family)
I13 = int(np.where(K == 13)[0][0])
N_NULL = 10000
N_PLANT = 50
N_FRESH = 10000
SEED = 20261017
T0 = time.time()

# ---- data pin and section --------------------------------------------------------------
U, _idx, sha = lpdata.unsolved()
assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585", sha
P = lpdata.load()
SEC_PAGES = (53, 54)
sec = [i for pg in SEC_PAGES for i in P[pg]["idx"]]
sec_word = [w for pg in SEC_PAGES for w in P[pg]["word"]]
n = len(sec)
assert n == 308, n
runs = []
prev = None
for w in sec_word:
    if prev is None or w != prev:
        runs.append(0)
        prev = w
    runs[-1] += 1
log("section: lpdata pages %s, runes %d (pages: %s)" % (SEC_PAGES, n, [len(P[p]["idx"]) for p in SEC_PAGES]))
log("word lengths in section (%d words): %s" % (len(runs), runs))
log("first word of page 53 has %d rune(s), second has %d; longest word %d" % (
    runs[0], runs[1], max(runs)))
# mapping checks (see RESULTS.md, Hypothesis)
pin_idx = [i for pg in range(0, 55) for i in P[pg]["idx"]]
pin_dbl = sum(1 for i in range(1, len(pin_idx)) if pin_idx[i] == pin_idx[i - 1])
log("mapping: pin pages 0-54 doublets %d (wiki total 86); pages 54+55 runes %d (not the claim); "
    "pages 40-52 runes %d (wiki row 'Spiral/Branches 40-53' = 3008); page 55 %d, page 56 %d runes" % (
        pin_dbl, len(P[54]["idx"]) + len(P[55]["idx"]),
        sum(len(P[pg]["idx"]) for pg in range(40, 53)), len(P[55]["idx"]), len(P[56]["idx"])))

D = np.array([(sec[i] - sec[i - 1]) % M for i in range(1, n)], dtype=np.int64)  # 307 increments
n_zero = int(np.sum(D == 0))
log("increments: %d, zero increments (doublets) %d, distinct values %d" % (len(D), n_zero, len(set(D.tolist()))))


def delta_matches(d):
    return np.array([np.count_nonzero(d[:-k] == d[k:]) for k in K], dtype=np.int64)


# ---- real statistic and null -----------------------------------------------------------
obs = delta_matches(D)
rng = np.random.default_rng(SEED)
null = np.empty((N_NULL, len(K)), dtype=np.int64)
for r in range(N_NULL):
    null[r] = delta_matches(rng.permutation(D))  # shuffle increments within the section
mu = null.mean(axis=0)
sd = null.std(axis=0, ddof=1)
T13 = float(np.quantile(null[:, I13], 0.99, method="higher"))
log("null: %d shuffles of the 307 increments within the section (zero count kept)" % N_NULL)
log("period-13 null M13: mean %.3f, sd %.3f, max %d, 99th pct (fixed threshold T13) = %.0f" % (
    mu[I13], sd[I13], null[:, I13].max(), T13))

z_obs = (obs - mu) / sd
m13 = int(obs[I13])
log("REAL M13 = %d, S-style ratio M13/null mean = %.3f, z = %.3f" % (m13, m13 / mu[I13], z_obs[I13]))
log("REAL fixed rule: M13 %s T13 (%d vs %.0f) -> %s" % (
    ">" if m13 > T13 else "<=", m13, T13, "FLAGGED" if m13 > T13 else "NOT flagged"))

# fresh null draws to check the false-flag rate of the fixed rule
rng2 = np.random.default_rng(SEED + 1)
fresh = np.array([delta_matches(rng2.permutation(D))[I13] for _ in range(N_FRESH)])
log("false-flag check on %d fresh null shuffles: %d exceed T13 (%.4f)" % (
    N_FRESH, int(np.sum(fresh > T13)), float(np.mean(fresh > T13))))

# ---- look-elsewhere scan over periods 2..40 -------------------------------------------
rank13 = 1 + int(np.sum(z_obs > z_obs[I13]))
maxz_null = ((null - mu) / sd).max(axis=1)
p_corr = (1 + int(np.sum(maxz_null >= z_obs[I13]))) / (N_NULL + 1)
top_k = int(K[int(np.argmax(z_obs))])
log("scan periods 2..40: period 13 ranks %d of 39 by z; top period %d (z %.3f)" % (
    rank13, top_k, float(z_obs.max())))
log("look-elsewhere: P(max over 2..40 of null z >= z13 = %.3f) = %.4f (%d of %d draws)" % (
    z_obs[I13], p_corr, int(np.sum(maxz_null >= z_obs[I13])), N_NULL))
best_j = int(np.argmax(z_obs))
p_fw_best = (1 + int(np.sum(maxz_null >= z_obs[best_j]))) / (N_NULL + 1)
log("look-elsewhere for the strongest period overall: k=%d z=%.3f, family-wise p = %.4f" % (
    int(K[best_j]), z_obs[best_j], p_fw_best))
log("per-period table: k, M_k, null mean, null sd, z, ratio")
for j, k in enumerate(K):
    log("  k=%2d  M=%3d  mean=%7.3f  sd=%6.3f  z=%7.3f  ratio=%.3f" % (
        k, obs[j], mu[j], sd[j], z_obs[j], obs[j] / mu[j]))

# ---- planted controls --------------------------------------------------------------------
def plant(rng_k, j):
    """English plaintext runes, enciphered as the chain c_i = c_(i-1) + 1 + ((p_i + k_(i mod 13)) mod 28)."""
    p = np.array(runes.english_stream(n, skip_chars=20000 + 5000 * j)[0], dtype=np.int64)
    key = rng_k.integers(0, 28, size=13)
    c = np.empty(n, dtype=np.int64)
    c[0] = p[0]
    for i in range(1, n):
        c[i] = (c[i - 1] + 1 + ((p[i] + key[i % 13]) % 28)) % M
    return np.diff(c) % M, key


rng_p = np.random.default_rng(SEED + 2)
p_m13, p_flag, p_rank1, p_top13, p_zero, p_topk = [], [], [], [], [], []
p_keys = []
for j in range(N_PLANT):
    Dp, key = plant(rng_p, j)
    mp = delta_matches(Dp)
    zp = (mp - mu) / sd
    p_m13.append(int(mp[I13]))
    p_flag.append(bool(mp[I13] > T13))
    p_rank1.append(1 + int(np.sum(zp > zp[I13])) == 1)
    p_top13.append(int(K[int(np.argmax(zp))]) % 13 == 0)
    p_topk.append(int(K[int(np.argmax(zp))]))
    p_zero.append(int(np.sum(Dp == 0)))
    p_keys.append(key.tolist())

n_rec = int(sum(p_flag))
log("planted controls: %d plants, period-13 keyword, chain cipher, English plaintext (%d runes)" % (N_PLANT, n))
log("plant M13: mean %.3f, sd %.3f, min %d, max %d" % (
    np.mean(p_m13), np.std(p_m13, ddof=1), min(p_m13), max(p_m13)))
log("plant zero increments: mean %.2f (the chain formula cannot produce a zero increment; real section has %d)" % (
    np.mean(p_zero), n_zero))
log("PLANT recovered (flagged by the fixed rule) %d/%d" % (n_rec, N_PLANT))
log("PLANT rank-1 exact period 13 among 2..40: %d/%d; top period a multiple of 13: %d/%d" % (
    sum(p_rank1), N_PLANT, sum(p_top13), N_PLANT))
log("plant top period (z, periods 2..40): 13 in %d, 26 in %d, 39 in %d, other %d (of %d)" % (
    p_topk.count(13), p_topk.count(26), p_topk.count(39),
    N_PLANT - p_topk.count(13) - p_topk.count(26) - p_topk.count(39), N_PLANT))
log("plant M13 list: %s" % p_m13)

# Wilson 95% interval for the power
from math import sqrt  # noqa: E402
ph = n_rec / N_PLANT
zc = 1.959964
den = 1 + zc * zc / N_PLANT
cen = (ph + zc * zc / (2 * N_PLANT)) / den
half = zc * sqrt(ph * (1 - ph) / N_PLANT + zc * zc / (4 * N_PLANT * N_PLANT)) / den
log("power of the fixed rule at n=308: %.2f (Wilson 95%% CI %.2f to %.2f)" % (ph, cen - half, cen + half))

summary = dict(
    section_pages=list(SEC_PAGES), n=n, n_increments=int(len(D)), zero_increments=n_zero,
    word_lengths=runs, obs=obs.tolist(), null_mean=mu.tolist(), null_sd=sd.tolist(),
    z=z_obs.tolist(), periods=K.tolist(), T13=T13, M13=m13, z13=float(z_obs[I13]),
    ratio13=float(m13 / mu[I13]), rank13=rank13, top_period=top_k, p_corr=p_corr,
    p_fw_best=p_fw_best, z_best=float(z_obs[best_j]),
    fresh_false_flag_rate=float(np.mean(fresh > T13)),
    plant_M13=p_m13, plant_recovered=n_rec, plant_rank1=int(sum(p_rank1)),
    plant_top_multiple_of_13=int(sum(p_top13)), plant_zero_mean=float(np.mean(p_zero)),
    plant_top_period_counts={str(k): p_topk.count(k) for k in (13, 26, 39)},
    plant_keys=p_keys, seed=SEED, n_null=N_NULL, n_plant=N_PLANT,
    seconds=round(time.time() - T0, 1),
)
with open(os.path.join(OUT, "period13_results.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=1)
log("done in %.1f s" % (time.time() - T0))
LOG.close()
