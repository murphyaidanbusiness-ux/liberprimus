"""Lane T: exhaustive decode of the walk_dodge_prime key family (20,000 keys) on LP2.

Subcommands (run from anywhere; the script chdirs to the repo root):
    census   every key through the gate's hard constraints (C1 C2 C2b C3 C6) -> out/census.json (the 1,550 passing keys)
    control  20 planted English plants (10 from passing keys, 10 from the rest) screened over all 20,000 keys
    null     20 shuffles of LP2 (toolbox/nulls.shuffle_increments) screened with the same pipeline
    real     LP2 first 300 runes screened over all 20,000 keys; top 50 fully decoded over 12,956 runes
    report   summary numbers for RESULTS.md -> out/summary.json

Ranking: a key is ranked by (number of runes it decodes before every state dies, then the mean quadgram log10 score
of its best live path). Keys that die early are inconsistent with the cipher and rank below every full-window key.
"""
import json
import os
import random
import sys
import time
import ctypes
import multiprocessing as mp

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
os.chdir(REPO)
sys.path[:0] = [os.path.join(REPO, "toolbox"), os.path.join(REPO, "lp"), HERE,
                os.path.join(REPO, "jobs", "hypothesis-gate", "tools")]

import numpy as np  # noqa: E402
import tdec  # noqa: E402
import lpdata  # noqa: E402
import nulls  # noqa: E402
import runes  # noqa: E402
import score  # noqa: E402
import walk_draws as wd  # noqa: E402

NWIN = 300
NKEYS = 20000
W = 512          # beam width (states kept per position)
NPROC = 8
OUT = tdec.OUT
LOGS = os.path.join(HERE, "logs")
os.makedirs(OUT, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)
_LOG = None


def log(msg):
    global _LOG
    if _LOG is None:
        _LOG = open(os.path.join(LOGS, "lane_t_run.log"), "a", encoding="utf-8")
    line = "%s %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    _LOG.write(line + "\n")
    _LOG.flush()


def lower_priority():
    """BELOW_NORMAL for this process; pool workers are created after this and inherit it (lane O, lane S)."""
    try:
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        k32.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        k32.SetPriorityClass.restype = wintypes.BOOL
        k32.GetPriorityClass.argtypes = [wintypes.HANDLE]
        k32.GetPriorityClass.restype = wintypes.DWORD
        cur = k32.GetCurrentProcess()
        if k32.GetPriorityClass(cur) != 0x4000:
            k32.SetPriorityClass(cur, 0x00004000)
        return "BELOW_NORMAL class now 0x%X" % k32.GetPriorityClass(cur)
    except Exception as e:  # noqa: BLE001
        return "priority not changed: %s" % e


def lp_flat():
    """Flat LP2 stream (pages 0-54) with positional word ids, and the SHA pin check."""
    U, C, sha = lpdata.unsolved()
    assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
    words = [w for p in U for w in p["word"]]
    assert len(words) == len(C) == 12956
    return list(C), words


def sortkey(alive, mean):
    """Higher is better: full-window survivors first, then by quadgram mean."""
    return alive * 100.0 + mean


# ---------------------------------------------------------------- workers
_dec = None
_cen = None


def worker_init(w):
    global _dec
    lower_priority()
    _dec = tdec.Decoder(W=w)


def screen_chunk(args):
    cipher, words, keys = args
    alive, out = _dec.screen(cipher, words, keys)
    return keys, alive, out[:, 0]


def screen(pool, cipher, words):
    tasks = [(cipher, words, list(range(lo, min(lo + 250, NKEYS)))) for lo in range(0, NKEYS, 250)]
    alive = np.zeros(NKEYS, np.int64)
    mean = np.zeros(NKEYS)
    for keys, a, m in pool.imap_unordered(screen_chunk, tasks):
        alive[keys] = a
        mean[keys] = m
    return alive, mean


def census_init():
    lower_priority()
    global _cen
    plain, words = runes.english_stream(12956)
    _cen = dict(sim=tdec.load_sim(), plain=list(plain), words=list(words),
                lines=[i // 22 for i in range(12956)], pages=[i // 235 for i in range(12956)])


def census_one(kk):
    kind, k0 = tdec.key_of(kk)
    sim = _cen["sim"]
    g, s, b = sim.keys_from(kind, k0)
    c = sim.walk(_cen["plain"], _cen["words"], g, s, b)
    f, hard = wd.score(c, _cen["words"], _cen["lines"], _cen["pages"], seed=0)
    return kk, hard, f["ioc"]


def pool_of(init, args=()):
    ctx = mp.get_context("spawn")
    return ctx.Pool(NPROC, initializer=init, initargs=args)


# ---------------------------------------------------------------- subcommands
def cmd_census(pool):
    t0 = time.time()
    passing, counts = [], {"C1": 0, "C2": 0, "C2b": 0, "C3": 0, "C6": 0}
    all_pass = 0
    for kk, hard, ioc in pool.imap(census_one, range(NKEYS), chunksize=50):
        for k in counts:
            counts[k] += int(hard.get(k, False))
        if all(hard.values()):
            all_pass += 1
            passing.append(kk)
    kinds = {kk: tdec.key_of(kk) for kk in passing}
    res = dict(passing=passing, passing_keys=[list(kinds[kk]) for kk in passing], counts=counts,
               all_hard_pass=all_pass, seconds=round(time.time() - t0, 1))
    with open(os.path.join(OUT, "census.json"), "w", encoding="utf-8") as f:
        json.dump(res, f)
    log("census: per-constraint passes %s; all hard constraints %d / 20000 (gate census: C1 9332, C2 8159, C2b 19476, "
        "C3 18331, C6 6082, all 1550); %.0fs" % (counts, all_pass, res["seconds"]))


def cmd_control(pool, dec):
    census = json.load(open(os.path.join(OUT, "census.json"), encoding="utf-8"))
    passing = census["passing"]
    pset = set(passing)
    nonpass = [kk for kk in range(NKEYS) if kk not in pset]
    rng = random.Random(2026101601)
    picks = rng.sample(passing, 10) + rng.sample(nonpass, 10)
    sim = tdec.load_sim()
    recs = []
    for j, kt in enumerate(picks):
        plain, words = runes.english_stream(NWIN, skip_chars=20000 + 1500 * j)
        plain, words = list(plain), list(words)
        kind, k0 = tdec.key_of(kt)
        g, s, b = sim.keys_from(kind, k0)
        c = sim.walk(plain, words, g, s, b)
        t0 = time.time()
        alive, mean = screen(pool, c, words)
        dt = time.time() - t0
        sk = sortkey(alive, mean)
        order = np.argsort(-sk, kind="stable")
        rank = int(np.where(order == kt)[0][0]) + 1
        _a, _m, _sc, _nw, path = dec.decode(c, words, kt, track=True)
        other = int(order[0]) if order[0] != kt else int(order[1])
        rec = dict(j=j, pool="passing" if j < 10 else "rest", kk=kt, kind=kind, k0=k0, skip_chars=20000 + 1500 * j,
                   rank=rank, rank1=(rank == 1), true_alive=int(alive[kt]), true_mean=float(mean[kt]),
                   true_path_exact=bool(list(path) == plain),
                   best_other_kk=other, best_other_alive=int(alive[other]), best_other_mean=float(mean[other]),
                   full_alive_keys=int(np.sum(alive == NWIN)), seconds=round(dt, 1))
        recs.append(rec)
        log("control plant %2d (%s) key %s/%d k0 %d: rank %d; true alive %d mean %.4f exact %s; best other %s "
            "(alive %d, mean %.4f); full-window keys %d (%.0fs)"
            % (j, rec["pool"], kind, k0, kt, rank, rec["true_alive"], rec["true_mean"], rec["true_path_exact"],
               tdec.key_of(other), rec["best_other_alive"], rec["best_other_mean"], rec["full_alive_keys"], dt))
    with open(os.path.join(OUT, "control.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, indent=1)
    r1 = sum(r["rank1"] for r in recs)
    log("control: rank 1 in %d/%d plants (passing-pool %d/10, rest %d/10); exact true-path recovery %d/%d"
        % (r1, len(recs), sum(r["rank1"] for r in recs[:10]), sum(r["rank1"] for r in recs[10:]),
           sum(r["true_path_exact"] for r in recs), len(recs)))


def cmd_null(pool, count=20):
    pages = nulls.lp_pages()
    _C, lpw = lp_flat()
    recs = []
    for seed in range(count):
        sd = 7000 + seed
        sh = nulls.shuffle_increments(pages, random.Random(sd))
        cipher = [x for p in sh for x in p][:NWIN]
        words = lpw[:NWIN]
        t0 = time.time()
        alive, mean = screen(pool, cipher, words)
        order = np.argsort(-sortkey(alive, mean), kind="stable")
        b = int(order[0])
        rec = dict(seed=sd, best_kk=b, best_kind_k0=list(tdec.key_of(b)), best_alive=int(alive[b]),
                   best_mean=float(mean[b]), full_alive_keys=int(np.sum(alive == NWIN)),
                   doublets_in_window=int(sum(1 for i in range(1, NWIN) if cipher[i] == cipher[i - 1])),
                   seconds=round(time.time() - t0, 1))
        recs.append(rec)
        log("null seed %d: doublets %d; best key %s (alive %d) mean %.4f; full-window keys %d (%.0fs)"
            % (sd, rec["doublets_in_window"], rec["best_kind_k0"], rec["best_alive"], rec["best_mean"],
               rec["full_alive_keys"], rec["seconds"]))
    with open(os.path.join(OUT, "null.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, indent=1)
    vals = np.array([r["best_mean"] for r in recs])
    log("null: %d shuffles; best mean mean %.5f sd %.5f max %.5f" % (len(vals), vals.mean(), vals.std(ddof=1),
                                                                    vals.max()))


def cmd_real(pool, dec):
    C, lpw = lp_flat()
    cipher, words = C[:NWIN], lpw[:NWIN]
    t0 = time.time()
    alive, mean = screen(pool, cipher, words)
    np.save(os.path.join(OUT, "real_alive.npy"), alive)
    np.save(os.path.join(OUT, "real_mean.npy"), mean)
    order = np.argsort(-sortkey(alive, mean), kind="stable")
    top = [int(j) for j in order[:50]]
    full = []
    for kk in top:
        a, mm, _sc, _nw, path = dec.decode(C, lpw, kk, track=True)
        p = list(path)
        full.append(dict(kk=kk, kind_k0=list(tdec.key_of(kk)), screen_alive=int(alive[kk]),
                         screen_mean=float(mean[kk]), full_alive=int(a), full_mean=float(mm),
                         full_quadgram=round(score.quadgram(p), 4) if len(p) >= 4 else None,
                         full_ioc=round(score.ioc(p), 4) if len(p) > 1 else None,
                         first120=runes.tr(p[:120])))
    full.sort(key=lambda r: -(r["full_mean"] if r["full_alive"] == len(C) else -99))
    with open(os.path.join(OUT, "real_top50.json"), "w", encoding="utf-8") as f:
        json.dump(full, f, indent=1)
    b = top[0]
    log("real screen (LP2 first %d runes): full-window keys %d; best kk %d %s alive %d mean %.5f; %.0fs"
        % (NWIN, int(np.sum(alive == NWIN)), b, tdec.key_of(b), alive[b], mean[b], time.time() - t0))
    log("real top-50 full decode over %d runes: full-length survivors %d; best %s mean %.5f ioc %s"
        % (len(C), sum(r["full_alive"] == len(C) for r in full), full[0]["kind_k0"], full[0]["full_mean"],
           full[0]["full_ioc"]))


def cmd_fulllp(pool):
    """Every key decoded over the whole of LP2 (12,956 runes). A planted true key survives the full length
    (long_plant_check.py); a key that dies before the end is inconsistent with LP2 at this beam width."""
    C, lpw = lp_flat()
    t0 = time.time()
    alive, mean = screen(pool, C, lpw)
    np.save(os.path.join(OUT, "fulllp_alive.npy"), alive)
    np.save(os.path.join(OUT, "fulllp_mean.npy"), mean)
    surv = np.where(alive == len(C))[0]
    order = surv[np.argsort(-mean[surv], kind="stable")] if len(surv) else []
    res = dict(n=len(C), full_length_survivors=int(len(surv)),
               survivors=[dict(kk=int(k), key=list(tdec.key_of(int(k))), mean=float(mean[k])) for k in order[:50]],
               death_position_quartiles=[int(x) for x in np.percentile(alive[alive < len(C)], [25, 50, 75])]
               if np.any(alive < len(C)) else [],
               max_alive_dying_key=int(alive[alive < len(C)].max()) if np.any(alive < len(C)) else None,
               seconds=round(time.time() - t0, 1))
    with open(os.path.join(OUT, "fulllp.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    log("fulllp: %d of 20000 keys survive all %d LP2 runes at W=%d; death position quartiles %s; furthest dying key "
        "reaches %s; %.0fs" % (len(surv), len(C), W, res["death_position_quartiles"], res["max_alive_dying_key"],
                              res["seconds"]))


def cmd_report():
    null = json.load(open(os.path.join(OUT, "null.json"), encoding="utf-8"))
    ctl = json.load(open(os.path.join(OUT, "control.json"), encoding="utf-8"))
    alive = np.load(os.path.join(OUT, "real_alive.npy"))
    mean = np.load(os.path.join(OUT, "real_mean.npy"))
    order = np.argsort(-sortkey(alive, mean), kind="stable")
    b = int(order[0])
    nv = np.array([r["best_mean"] for r in null])
    rb = float(mean[b])
    summ = dict(
        control_rank1=sum(r["rank1"] for r in ctl), control_n=len(ctl),
        control_exact=sum(r["true_path_exact"] for r in ctl),
        null_n=len(nv), null_mean=float(nv.mean()), null_sd=float(nv.std(ddof=1)), null_max=float(nv.max()),
        null_min=float(nv.min()),
        real_best_kk=b, real_best_kind_k0=list(tdec.key_of(b)), real_best_alive=int(alive[b]),
        real_best_mean=rb, real_z=float((rb - nv.mean()) / nv.std(ddof=1)),
        real_minus_null_max=rb - float(nv.max()),
        real_full_window_keys=int(np.sum(alive == NWIN)),
        null_full_window_keys=[r["full_alive_keys"] for r in null],
    )
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summ, f, indent=1)
    log("report: " + json.dumps(summ))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    how = lower_priority()
    log("== lane T %s (priority: %s, beam W=%d)" % (cmd, how, W))
    if cmd == "report":
        cmd_report()
        return
    dec = None
    if cmd in ("control", "real", "null", "fulllp"):
        dec = tdec.Decoder(W=W)
        dec.decode([0, 1, 2, 0, 1], [0, 0, 1, 1, 2], 0, True)   # compile (and cache) in the parent first
        dec.decode([0, 1, 2, 0, 1], [0, 0, 1, 1, 2], 0, False)
    if cmd == "census":
        pool = pool_of(census_init)
        try:
            cmd_census(pool)
        finally:
            pool.close()
            pool.join()
        return
    pool = pool_of(worker_init, (W,))
    try:
        if cmd == "control":
            cmd_control(pool, dec)
        elif cmd == "null":
            cmd_null(pool)
        elif cmd == "real":
            cmd_real(pool, dec)
        elif cmd == "fulllp":
            cmd_fulllp(pool)
        else:
            raise SystemExit("unknown subcommand %r" % cmd)
    finally:
        pool.close()
        pool.join()


if __name__ == "__main__":
    mp.freeze_support()
    main()
