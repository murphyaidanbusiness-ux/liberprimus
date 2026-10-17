"""Lane V question 2, ranking stage: weight of evidence in decibans for each mechanism against the no-echo baseline.

Input: out/mech_profiles.npz from mech_sim.py (40 training keys and 20 held-out keys per mechanism; each a 20-cell
profile, within-word lag k = 1..10 and cross-word lag k = 1..10).

Primary model (per-cell beta-binomial, cells treated as independent): for mechanism M and cell c the training rates
give a mean mu and a variance v over keys; the rate is taken as Beta(mu, tau^2) with tau^2 = (v - mu(1-mu)/n)/(1-1/n),
so the predictive count is BetaBin(n, a, b). This is a binomial whose rate carries the across-key spread, which
matters for the small high-lag cells (n = 35 to 92). The log-likelihood of LP2's counts under M is the sum over cells.
Deciban weight of M against the baseline: 10 log10 e^(lnL_M - lnL_base) = 4.3429 (lnL_M - lnL_base); Turing's
factor principle, each cell adds its own deciban factor.

Sensitivity model (multivariate normal on the 20 rates, covariance pooled within mechanisms, shrinkage-free): the
deciban weight is -2.1715 (d2_M - d2_base), d2 the Mahalanobis distance of LP2's rate vector from M's mean.

Control: each held-out simulated stream (never used to fit) is ranked against the five fitted models; the true
mechanism should be rank 1. Baseline held-out streams give the null distribution of each deciban weight.

    python -I -X utf8 agents/laneV_lag5_mechanisms/mech_rank.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import site  # noqa: E402
if os.path.isdir(site.getusersitepackages()):
    sys.path.append(site.getusersitepackages())
from scipy.special import betaln, gammaln  # noqa: E402
import common as cm  # noqa: E402

cm.lower_priority()
OUT = os.path.join(HERE, "out")
LOG = []
DB = 10 * np.log10(np.e)                              # 4.3429: nats -> decibans


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


D = np.load(os.path.join(OUT, "mech_profiles.npz"))
names = [str(x) for x in D["names"]]
tr, te = D["train"], D["test"]                        # (M, R, 20) rates
trc, tec = D["train_counts"], D["test_counts"]        # (M, R, 20) match counts
NM, R, NC = tr.shape
RT = te.shape[1]
BASE = names.index("base")
C, wid, page, sec = cm.load_lp2()
mw, nw, mx, nx = cm.lag_profile(C, wid)
n = np.concatenate([nw, nx]).astype(float)           # cell sizes, fixed by LP2's word structure
mLP2 = np.concatenate([mw, mx]).astype(float)
cells = ["w%d" % k for k in range(1, 11)] + ["x%d" % k for k in range(1, 11)]
assert np.allclose(trc / n, tr) and np.allclose(tec / n, te), "simulated counts and rates disagree"
P("LP2 cells (n, matches, rate): within lag 5 n=%d m=%d rate %.4f; cross lag 1 n=%d m=%d rate %.4f"
  % (nw[4], mw[4], mw[4] / nw[4], nx[0], mx[0], mx[0] / nx[0]))
P("models: %s; training keys %d, held-out keys %d per model" % (", ".join(names), R, RT))
assert np.allclose(mw[4] / nw[4], 104 / 2105)


# ---- primary: per-cell beta-binomial ----
def fit_bb(rates):
    mu = np.clip(rates.mean(0), 1e-4, 1 - 1e-4)
    v = rates.var(0, ddof=1)
    tau2 = (v - mu * (1 - mu) / n) / (1 - 1 / n)
    s = mu * (1 - mu) / np.maximum(tau2, 1e-300) - 1
    s = np.clip(s, 10.0, 1e6)
    return mu * s, (1 - mu) * s


A = np.zeros((NM, NC))
Bp = np.zeros((NM, NC))
for M in range(NM):
    A[M], Bp[M] = fit_bb(tr[M])


def logpmf(m, a, b):
    return gammaln(n + 1) - gammaln(m + 1) - gammaln(n - m + 1) + betaln(m + a, n - m + b) - betaln(a, b)


def ll_all(m_obs):
    return np.array([logpmf(m_obs, A[M], Bp[M]).sum() for M in range(NM)])


# ---- sensitivity: multivariate normal, covariance pooled within mechanisms ----
MU = tr.mean(1)
RES = tr - MU[:, None, :]
SIG = np.einsum("mrc,mrd->cd", RES, RES) / (NM * (R - 1))
SINV = np.linalg.inv(SIG)


def d2_all(m_obs):
    x = m_obs / n
    out = []
    for M in range(NM):
        dd = x - MU[M]
        out.append(float(dd @ SINV @ dd))
    return np.array(out)


# ---- LP2 ----
llL = ll_all(mLP2)
d2L = d2_all(mLP2)
dbL = DB * (llL - llL[BASE])
dmL = -0.5 * DB * (d2L - d2L[BASE])
P("\nLP2 WEIGHT OF EVIDENCE (decibans against the no-echo baseline; positive favours the mechanism)")
P("%-10s %12s %12s %10s %10s" % ("mechanism", "dB beta-bin", "dB MVN", "rank bb", "rank MVN"))
rk_bb = np.argsort(-llL)
rk_mv = np.argsort(d2L)
for M in range(NM):
    P("%-10s %12.2f %12.2f %10d %10d" % (names[M], dbL[M], dmL[M],
                                       int(np.where(rk_bb == M)[0][0]) + 1, int(np.where(rk_mv == M)[0][0]) + 1))
P("ranking (beta-binomial): " + " > ".join(names[i] for i in rk_bb))
P("ranking (MVN):           " + " > ".join(names[i] for i in rk_mv))

P("\nPer-cell decibans for LP2 (each mechanism against baseline, beta-binomial):")
P("%-5s %5s %6s %8s %8s  %s" % ("cell", "n", "LP2 m", "LP2 rate", "base mu", "  ".join("%9s" % x for x in names if x != "base")))
for c in range(NC):
    row = []
    for M in range(NM):
        if M == BASE:
            continue
        cont = DB * (logpmf(mLP2, A[M], Bp[M])[c] - logpmf(mLP2, A[BASE], Bp[BASE])[c])
        row.append("%+9.2f" % cont)
    P("%-5s %5d %6d %8.4f %8.4f  %s" % (cells[c], n[c], mLP2[c], mLP2[c] / n[c], tr[BASE, :, c].mean(), "  ".join(row)))
P("predicted mean rate of within lag 5 (LP2 0.0494): " +
  ", ".join("%s %.4f" % (names[M], tr[M, :, 4].mean()) for M in range(NM)))
P("predicted mean rate of cross lag 1 (LP2 0.0079): " +
  ", ".join("%s %.4f" % (names[M], tr[M, :, 10].mean()) for M in range(NM)))

# ---- sensitivity of the LP2 ranking to which cells enter (is it the noisy high-lag cells?) ----
P("\nLP2 ranking by cell subset (beta-binomial | MVN on the same cells):")
for lab, idx in [("all 20 cells", list(range(NC))), ("lags 1-5, within and cross (10 cells)",
                                                       [0, 1, 2, 3, 4, 10, 11, 12, 13, 14]),
                 ("within-word lags 1-10 (10 cells)", list(range(10)))]:
    idx = np.array(idx)
    ll_s = np.array([logpmf(mLP2, A[M], Bp[M])[idx].sum() for M in range(NM)])
    Ssub = np.einsum("mrc,mrd->cd", RES[:, :, idx], RES[:, :, idx]) / (NM * (R - 1))
    Si = np.linalg.inv(Ssub)
    d2s = np.array([float((mLP2 / n - MU[M])[idx] @ Si @ (mLP2 / n - MU[M])[idx]) for M in range(NM)])
    dbs = DB * (ll_s - ll_s[BASE])
    dms = -0.5 * DB * (d2s - d2s[BASE])
    rb = np.argsort(-ll_s)
    rm = np.argsort(d2s)
    P("  %-38s bb: %s | MVN: %s" % (lab,
                                 " > ".join("%s %+.1f" % (names[i], dbs[i]) for i in rb),
                                 " > ".join("%s %+.1f" % (names[i], dms[i]) for i in rm)))

# ---- control: held-out simulated streams as if they were LP2 ----
P("\nRANKING CONTROL: held-out simulated ciphertexts (never fitted), each ranked against the five models")
hit_bb = {names[M]: 0 for M in range(NM)}
hit_mv = {names[M]: 0 for M in range(NM)}
dB_null = {names[M]: [] for M in range(NM)}           # held-out baseline streams: deciban weight of each model
dB_self = {names[M]: [] for M in range(NM)}
for T in range(NM):
    for j in range(RT):
        m_obs = tec[T, j].astype(float)
        ll = ll_all(m_obs)
        d2 = d2_all(m_obs)
        if int(np.argmax(ll)) == T:
            hit_bb[names[T]] += 1
        if int(np.argmin(d2)) == T:
            hit_mv[names[T]] += 1
        w = DB * (ll - ll[BASE])
        if T == BASE:
            for M in range(NM):
                dB_null[names[M]].append(w[M])
        else:
            dB_self[names[T]].append(w[T])
tot_bb = sum(hit_bb.values())
tot_mv = sum(hit_mv.values())
for M in range(NM):
    P("  true model %-10s rank 1 (beta-binomial): recovered %2d/%d   (MVN: %2d/%d)"
      % (names[M], hit_bb[names[M]], RT, hit_mv[names[M]], RT))
P("  all held-out streams: recovered %d/%d (beta-binomial), %d/%d (MVN)" % (tot_bb, NM * RT, tot_mv, NM * RT))
P("\nNULL (baseline held-out streams, %d draws): deciban weight of each model against baseline, mean, sd, max"
  % RT)
for M in range(NM):
    if M == BASE:
        continue
    v = np.array(dB_null[names[M]])
    P("  %-10s mean %+7.2f  sd %6.2f  max %+7.2f   (LP2 %+.2f)" % (names[M], v.mean(), v.std(ddof=1), v.max(), dbL[M]))
P("mechanism held-out streams, own deciban weight against baseline (mean, min):")
for M in range(NM):
    if M == BASE:
        continue
    v = np.array(dB_self[names[M]])
    P("  %-10s mean %+7.2f  min %+7.2f" % (names[M], v.mean(), v.min()))

with open(os.path.join(OUT, "mech_rank_out.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(LOG) + "\n")
print("wrote", os.path.join(OUT, "mech_rank_out.txt"))
