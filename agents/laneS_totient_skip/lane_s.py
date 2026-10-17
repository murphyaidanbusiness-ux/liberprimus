"""Lane S: exhaustive sweep of the totient_fskip_skip45_nolitF key model on LP2.

Model (gate simulator jobs/hypothesis-gate/runs/totient_fskip_skip45_nolitF_cipher.py, sign +1):
    c_i = (p_i + s * PHI[k]) mod 29, with k starting at k0 and advancing once per enciphered rune;
    if c_i == c_(i-1) and i mod 5 != phase, k advances once more and c_i is re-enciphered (key advances twice).
    PHI[k] = (prime_k - 1) mod 29, prime_0 = 2. s = +1 is the simulator convention (c = p + PHI, i.e. p = c - PHI,
    the solved-page convention in docs/BRIEF_ROUND2.md). s = -1 is the reverse convention (c = p - PHI).

Two screens per key (k0, phase), both over the first NWIN runes of the LP2 stream:
  STRICT   the model as simulated: a key is consistent with the window only if every doublet in the window lies on
           the forbidden residue (i mod 5 == phase) or the prime gap is 0 mod 29. Score = quadgram mean of the best
           consistent path (exact dynamic program over (position, k)).
  RELAXED  the same dynamic program with the doublet rule dropped (a doublet on an allowed position is decoded as a
           plain non-skip). Every key gets a score, so real and null streams are ranked over the same 50,000 keys.
           This is the primary screen for the z-score. STRICT consistency counts are reported separately.

Run from anywhere; the script chdirs to the repo root. Subcommands:
    selftest | throughput | control | null [--sign -1] | real | report
"""
import importlib.util
import json
import multiprocessing as mp
import os
import random
import sys
import time

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(REPO)  # lpdata and score read ./dl and dl/... relative to the repo root
sys.path.insert(0, os.path.join(REPO, "lp"))
sys.path.insert(0, os.path.join(REPO, "toolbox"))
import lpdata  # noqa: E402
import nulls  # noqa: E402
import runes  # noqa: E402
import score  # noqa: E402

LANE = os.path.join(REPO, "agents", "laneS_totient_skip")
OUT = os.path.join(LANE, "out")
LOGS = os.path.join(LANE, "logs")

_spec = importlib.util.spec_from_file_location(
    "sim_nolitF", os.path.join(REPO, "jobs", "hypothesis-gate", "runs", "totient_fskip_skip45_nolitF_cipher.py"))
sim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sim)
PHI = sim.PHI29
M = 29
TR = lpdata.TR
LQ, FLOOR = score._table()

NK0 = 10000          # start indices k0 in 0..9999
NPH = 5              # skip phases 0..4
NKEYS = NK0 * NPH    # 50,000 keys; idx = phase * NK0 + k0
NWIN = 300           # screen window (first 300 runes of the LP2 stream)
W_CAP = 10 ** 9      # no cap: exact dynamic program over (position, k); see decode()
NPROC = 8


# ---------------------------------------------------------------- cipher (parametrised copy of the simulator)
def encrypt(plain, k0, phase, sign):
    """Same code path as the simulator's encrypt, with k0, skip phase and sign as parameters."""
    k, out, prev = k0, [], None
    for i, p in enumerate(plain):
        c = (p + sign * PHI[k]) % M
        if c == prev and i % 5 != phase:
            k += 1
            c = (p + sign * PHI[k]) % M
        k += 1
        out.append(c)
        prev = c
    return out


class _FixedRng:
    def __init__(self, k0):
        self.k0 = k0

    def randrange(self, n):
        assert n == 10000
        return self.k0


# ---------------------------------------------------------------- decoder
def _put(kids, k, sc, tail, nw, nd, p, par, rune, track):
    if track:
        par.append(nd)
        rune.append(p)
        nd = len(par) - 1
    old = kids.get(k)
    if old is None or sc > old[0]:
        kids[k] = (sc, k, tail, nw, nd)


def decode(c, k0, phase, sign, W=W_CAP, track=False, relax=False):
    """Returns (alive, mean, nwin, maxpop, path).

    alive == len(c) means the key is consistent with the whole window (strict rule). With relax=True the doublet
    rule is dropped, so alive is always len(c).
    Branch A (no skip): valid unless (allowed position and c_i == c_prev) [always valid if relax];
                        p = c_i - s*PHI[k]; k -> k+1.
    Branch B (skip):    valid if allowed, c_prev exists, and c_i == c_prev + s*(PHI[k+1]-PHI[k]);
                        p = c_prev - s*PHI[k]; k -> k+2.
    States with the same k at the same position are merged (exact: they share the future), keeping the higher score.
    maxpop is the largest number of live states; W is only a safety cap and is set to infinity here.
    """
    n = len(c)
    beam = [(0.0, k0, "", 0, 0)]        # (cumulative log10 score, k, last <=3 chars, windows, node)
    par, rune = [-1], [-1]              # backpointers (node 0 = root), only used when track
    prev = -1
    alive = n
    maxpop = 1
    for i in range(n):
        ci = c[i]
        allow = (i % 5 != phase)
        kids = {}
        for sc, k, tail, nw, nd in beam:
            pk = PHI[k]
            if relax or not (allow and ci == prev):              # branch A
                p = (ci - sign * pk) % M
                s = tail + TR[p]
                add = 0.0
                for j in range(3, len(s)):
                    add += LQ.get(s[j - 3:j + 1], FLOOR)
                _put(kids, k + 1, sc + add, s[-3:], nw + max(0, len(s) - 3), nd, p, par, rune, track)
            if allow and prev >= 0:                              # branch B
                pk1 = PHI[k + 1]
                if ci == (prev + sign * (pk1 - pk)) % M:
                    p = (prev - sign * pk) % M
                    s = tail + TR[p]
                    add = 0.0
                    for j in range(3, len(s)):
                        add += LQ.get(s[j - 3:j + 1], FLOOR)
                    _put(kids, k + 2, sc + add, s[-3:], nw + max(0, len(s) - 3), nd, p, par, rune, track)
        if not kids:
            alive = i
            break
        ranked = sorted(kids.values(), key=lambda t: -t[0])
        if len(ranked) > maxpop:
            maxpop = len(ranked)
        beam = ranked[:W]
        prev = ci
    best = beam[0]
    path = None
    if track:
        path = []
        x = best[4]
        while x > 0:
            path.append(rune[x])
            x = par[x]
        path.reverse()
    mean = best[0] / best[3] if best[3] > 0 else float("nan")
    return alive, mean, best[3], maxpop, path


def _work(task):
    cipher, sign, lo, hi = task
    n = len(cipher)
    strict = np.full(hi - lo, np.nan)
    relaxed = np.full(hi - lo, np.nan)
    alive = np.zeros(hi - lo, dtype=np.int32)
    for j, idx in enumerate(range(lo, hi)):
        phase, k0 = divmod(idx, NK0)
        a, mean, _nw, _mp, _p = decode(cipher, k0, phase, sign)
        alive[j] = a
        if a == n:
            strict[j] = mean
        _a, mean_r, _nw2, _mp2, _p2 = decode(cipher, k0, phase, sign, relax=True)
        relaxed[j] = mean_r
    return lo, strict, alive, relaxed


def sweep(pool, cipher, sign, chunk=500):
    """Returns (strict_means with NaN for inconsistent keys, alive counts, relaxed_means for all keys)."""
    tasks = [(cipher, sign, lo, min(lo + chunk, NKEYS)) for lo in range(0, NKEYS, chunk)]
    strict = np.full(NKEYS, np.nan)
    alive = np.zeros(NKEYS, dtype=np.int32)
    relaxed = np.full(NKEYS, np.nan)
    for lo, s_, a_, r_ in pool.imap_unordered(_work, tasks):
        strict[lo:lo + len(s_)] = s_
        alive[lo:lo + len(a_)] = a_
        relaxed[lo:lo + len(r_)] = r_
    return strict, alive, relaxed


def summarise(means, idx_true=None):
    """Best key, rank and top 5 of a vector of scores (NaN = not scored)."""
    ok = ~np.isnan(means)
    out = {"keys_scored": int(ok.sum())}
    if ok.sum() == 0:
        out.update(best=None, best_key=None, top5=[])
    else:
        filled = np.where(ok, means, -np.inf)
        order = np.argsort(-filled, kind="stable")
        b = int(order[0])
        out.update(best=float(means[b]), best_key={"phase": b // NK0, "k0": b % NK0},
                   second=float(means[int(order[1])]) if ok.sum() > 1 else None,
                   top5=[{"phase": int(j) // NK0, "k0": int(j) % NK0, "mean": float(means[j])}
                         for j in order[:5] if ok[j]])
    if idx_true is not None:
        out["true_scored"] = bool(ok[idx_true])
        out["true_mean"] = float(means[idx_true]) if ok[idx_true] else None
        out["true_rank"] = int(1 + np.sum(means[ok] > means[idx_true])) if ok[idx_true] else None
    return out


def strict_counts(alive, n):
    """Consistent keys per phase (strict rule) for a window of n runes."""
    per_phase = [int(np.sum(alive[p * NK0:(p + 1) * NK0] == n)) for p in range(NPH)]
    return {"consistent_total": int(np.sum(alive == n)), "consistent_per_phase": per_phase}


# ---------------------------------------------------------------- logging and priority
_LOG = None


def log(msg):
    global _LOG
    if _LOG is None:
        _LOG = open(os.path.join(LOGS, "lane_s_run.log"), "a", encoding="utf-8")
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    _LOG.write(line + "\n")
    _LOG.flush()


def lower_priority():
    rc = os.system("wmic process where processid=%d CALL setpriority 16384 >NUL 2>&1" % os.getpid())
    how = "wmic setpriority 16384 (exit %d)" % rc
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k32.SetPriorityClass.restype = wintypes.BOOL
        k32.GetPriorityClass.argtypes = [wintypes.HANDLE]
        k32.GetPriorityClass.restype = wintypes.DWORD
        cur = k32.GetCurrentProcess()
        if k32.GetPriorityClass(cur) != 0x4000:
            ok = k32.SetPriorityClass(cur, 0x00004000)
            how += "; ctypes SetPriorityClass(BELOW_NORMAL) ok=%s" % bool(ok)
        how += "; priority class now 0x%X" % k32.GetPriorityClass(cur)
    except Exception as e:  # noqa: BLE001
        how += "; priority check failed: %s" % e
    return how


# ---------------------------------------------------------------- drivers
def lp_stream():
    U, C, sha = lpdata.unsolved()
    assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    return C


def plants(n, seed, sign_label):
    rng = random.Random(seed)
    out = []
    for j in range(n):
        k0 = rng.randrange(NK0 - 2 * NWIN)   # keep k0 + 2*len below the simulator's assert range
        phase = rng.randrange(NPH)
        skip_chars = 20000 + 1500 * j       # different English passage per plant
        plain, _w = runes.english_stream(NWIN, skip_chars=skip_chars)
        out.append(dict(j=j, k0=k0, phase=phase, skip_chars=skip_chars, plain=plain, sign=sign_label))
    return out


def cmd_selftest():
    rng = random.Random(7)
    ok_enc = 0
    for _ in range(60):
        k0 = rng.randrange(NK0)
        plain = [rng.randrange(M) for _ in range(rng.randrange(20, 400))]
        a = encrypt(plain, k0, 0, +1)
        b = sim.encrypt(plain, None, _FixedRng(k0))
        ok_enc += (a == b)
    log("selftest encrypt(phase 0, sign +1) == simulator encrypt: %d/60" % ok_enc)
    ex = 0
    n_ex = 0
    for sign in (+1, -1):
        for pl in plants(6, 99 + sign, sign):
            c = encrypt(pl["plain"], pl["k0"], pl["phase"], sign)
            a, mean, nw, mp_, path = decode(c, pl["k0"], pl["phase"], sign, track=True)
            exact = (path == pl["plain"])
            ex += exact
            n_ex += 1
            log("selftest plant sign %+d k0 %d phase %d: consistent %s exact %s mean %.4f maxpop %d"
                % (sign, pl["k0"], pl["phase"], a == NWIN, exact, mean, mp_))
    log("selftest strict decoder recovers the planted plaintext exactly: %d/%d" % (ex, n_ex))
    cons = 0
    for t in range(30):
        k0 = rng.randrange(NK0)
        phase = rng.randrange(NPH)
        plain = [rng.randrange(M) for _ in range(300)]
        c = encrypt(plain, k0, phase, +1)
        a, mean, nw, mp_, path = decode(c, k0, phase, +1, track=True)
        cons += (a == 300)
    log("selftest true key consistent with random-plaintext windows: %d/30" % cons)


def cmd_throughput():
    C = lp_stream()
    t0 = time.time()
    for k0 in range(1000):
        decode(C[:NWIN], k0, 0, +1)
        decode(C[:NWIN], k0, 0, +1, relax=True)
    dt = time.time() - t0
    log("throughput single core: 1000 keys x (strict + relaxed) in %.2fs" % dt)


def cmd_control(pool):
    res = []
    for sign, count in ((+1, 20), (-1, 5)):
        for pl in plants(count, 20261016 + (0 if sign > 0 else 1), sign):
            c = encrypt(pl["plain"], pl["k0"], pl["phase"], sign)
            t0 = time.time()
            strict, alive, relaxed = sweep(pool, c, sign)
            idx = pl["phase"] * NK0 + pl["k0"]
            sr = summarise(relaxed, idx)
            ss = summarise(strict, idx)
            _a, _m, _nw, _mp, path = decode(c, pl["k0"], pl["phase"], sign, track=True, relax=True)
            rec = dict(sign=sign, j=pl["j"], k0=pl["k0"], phase=pl["phase"], skip_chars=pl["skip_chars"],
                       rank_relaxed=sr["true_rank"], true_mean_relaxed=sr["true_mean"],
                       best_key_relaxed=sr["best_key"], best_mean_relaxed=sr["best"],
                       second_mean_relaxed=sr.get("second"),
                       strict_true_consistent=ss["true_scored"], strict_true_rank=ss["true_rank"],
                       strict_consistent_keys=int(np.sum(alive == NWIN)),
                       exact_decode_relaxed=(path == pl["plain"]), seconds=round(time.time() - t0, 1))
            res.append(rec)
            log("control sign %+d plant %d: k0 %d phase %d -> relaxed rank %s (mean %.5f, best other %s) "
                "strict consistent %s strict rank %s exact %s (%.1fs)"
                % (sign, pl["j"], pl["k0"], pl["phase"], rec["rank_relaxed"], rec["true_mean_relaxed"],
                   sr["best_key"], rec["strict_true_consistent"], rec["strict_true_rank"],
                   rec["exact_decode_relaxed"], rec["seconds"]))
    with open(os.path.join(OUT, "control.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    fw = [r for r in res if r["sign"] > 0]
    rv = [r for r in res if r["sign"] < 0]
    log("control forward relaxed: rank 1 in %d/%d; strict true key consistent in %d/%d"
        % (sum(r["rank_relaxed"] == 1 for r in fw), len(fw), sum(r["strict_true_consistent"] for r in fw), len(fw)))
    log("control reverse relaxed: rank 1 in %d/%d; strict true key consistent in %d/%d"
        % (sum(r["rank_relaxed"] == 1 for r in rv), len(rv), sum(r["strict_true_consistent"] for r in rv), len(rv)))


def cmd_null(pool, sign, count=20):
    pages = nulls.lp_pages()
    res = []
    for seed in range(count):
        sd = 1000 + seed + (0 if sign > 0 else 500)
        rng = random.Random(sd)
        sh = nulls.shuffle_increments(pages, rng)
        stream = [x for p in sh for x in p]
        cipher = stream[:NWIN]
        t0 = time.time()
        strict, alive, relaxed = sweep(pool, cipher, sign)
        sr = summarise(relaxed)
        ss = summarise(strict)
        cnt = strict_counts(alive, NWIN)
        res.append(dict(seed=sd, relaxed_best=sr["best"], relaxed_best_key=sr["best_key"],
                        relaxed_second=sr.get("second"), strict_consistent=cnt["consistent_total"],
                        strict_best=ss["best"], strict_best_key=ss["best_key"],
                        doublets_in_window=sum(1 for i in range(1, NWIN) if cipher[i] == cipher[i - 1])))
        log("null sign %+d seed %d: doublets %d strict consistent %d relaxed best %.5f key %s (%.1fs)"
            % (sign, sd, res[-1]["doublets_in_window"], cnt["consistent_total"], sr["best"], sr["best_key"],
               time.time() - t0))
    with open(os.path.join(OUT, "null_sign%+d.json" % sign), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)


def cmd_real(pool):
    C = lp_stream()
    cipher = C[:NWIN]
    report = {"window": NWIN, "window_doublets": [i for i in range(1, NWIN) if cipher[i] == cipher[i - 1]]}
    for sign in (+1, -1):
        t0 = time.time()
        strict, alive, relaxed = sweep(pool, cipher, sign)
        np.save(os.path.join(OUT, "real_relaxed_sign%+d.npy" % sign), relaxed)
        np.save(os.path.join(OUT, "real_strict_sign%+d.npy" % sign), strict)
        sr = summarise(relaxed)
        ss = summarise(strict)
        cnt = strict_counts(alive, NWIN)
        s = dict(relaxed=sr, strict=ss, strict_counts=cnt, seconds=round(time.time() - t0, 1))
        report["sign%+d" % sign] = s
        log("real sign %+d: relaxed best %.5f key %s; strict consistent %d (per phase %s); best strict %s (%.1fs)"
            % (sign, sr["best"], sr["best_key"], cnt["consistent_total"], cnt["consistent_per_phase"],
               ss["best"], s["seconds"]))
        order = np.argsort(-np.where(~np.isnan(relaxed), relaxed, -np.inf), kind="stable")
        top = [int(j) for j in order[:50]]
        full = []
        for j in top:
            phase, k0 = divmod(j, NK0)
            a, mean, nw, mp_, path = decode(C, k0, phase, sign, track=True, relax=True)
            a_strict, _m, _nw, _mp, _p = decode(C, k0, phase, sign)
            pg0 = path[:262]
            full.append(dict(phase=phase, k0=k0, screen_relaxed=float(relaxed[j]),
                             strict_alive_full=a_strict,
                             full_len=len(path), full_ioc=round(score.ioc(path), 4),
                             full_quadgram=round(score.quadgram(path), 4),
                             page0_ioc=round(score.ioc(pg0), 4), page0_quadgram=round(score.quadgram(pg0), 4),
                             first120=runes.tr(path[:120])))
        full.sort(key=lambda r: -r["full_quadgram"])
        with open(os.path.join(OUT, "top50_sign%+d.json" % sign), "w", encoding="utf-8") as f:
            json.dump(full, f, indent=1)
        log("real sign %+d top-50 (relaxed screen) full decode over %d runes: best full-stream quadgram %.4f "
            "(key phase %d k0 %d), median %.4f, strict-consistent-to-the-end %d of 50"
            % (sign, len(C), full[0]["full_quadgram"], full[0]["phase"], full[0]["k0"],
               sorted(r["full_quadgram"] for r in full)[25],
               sum(1 for r in full if r["strict_alive_full"] == len(C))))
    with open(os.path.join(OUT, "real.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)


def cmd_report():
    """z-scores of the real relaxed best against the null (20 shuffles per convention)."""
    real = json.load(open(os.path.join(OUT, "real.json"), encoding="utf-8"))
    rep = {}
    for sign in (+1, -1):
        nl = json.load(open(os.path.join(OUT, "null_sign%+d.json" % sign), encoding="utf-8"))
        vals = np.array([r["relaxed_best"] for r in nl], dtype=float)
        mean, sd, mx = float(vals.mean()), float(vals.std(ddof=1)), float(vals.max())
        rb = real["sign%+d" % sign]["relaxed"]["best"]
        rep["sign%+d" % sign] = dict(
            nulls=len(vals), null_mean=mean, null_sd=sd, null_max=mx, null_min=float(vals.min()),
            real_best=rb, real_best_key=real["sign%+d" % sign]["relaxed"]["best_key"],
            z=(rb - mean) / sd, real_minus_null_max=rb - mx,
            real_above_null_max=bool(rb > mx),
            null_strict_consistent=[r["strict_consistent"] for r in nl],
            real_strict_consistent=real["sign%+d" % sign]["strict_counts"]["consistent_total"])
        log("report sign %+d: null mean %.5f sd %.5f max %.5f (n=%d); real %.5f z %+.2f; real above null max: %s"
            % (sign, mean, sd, mx, len(vals), rb, (rb - mean) / sd, rb > mx))
    with open(os.path.join(OUT, "report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)


if __name__ == "__main__":
    mp.freeze_support()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    sign = -1 if "--sign" in sys.argv and sys.argv[sys.argv.index("--sign") + 1] == "-1" else +1
    how = lower_priority()
    log("== lane S %s (priority: %s)" % (cmd, how))
    if cmd == "selftest":
        cmd_selftest()
    elif cmd == "throughput":
        cmd_throughput()
    elif cmd == "report":
        cmd_report()
    elif cmd == "control":
        with mp.get_context("spawn").Pool(NPROC) as pool:
            cmd_control(pool)
    elif cmd == "null":
        with mp.get_context("spawn").Pool(NPROC) as pool:
            cmd_null(pool, sign)
    elif cmd == "real":
        with mp.get_context("spawn").Pool(NPROC) as pool:
            cmd_real(pool)
    else:
        raise SystemExit("unknown subcommand %r" % cmd)
