"""Robustness check: the LP2 300-rune screen at beam width 4096 (the null used W=512). A wider beam can only raise
each key's score, so a real best that stays below the W=512 null max is not a beam-width artifact."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import multiprocessing as mp
import numpy as np
import lane_t as L

if __name__ == "__main__":
    mp.freeze_support()
    L.lower_priority()
    W = 4096
    L.log("== lane T real screen at W=%d (robustness)" % W)
    C, lpw = L.lp_flat()
    pool = L.pool_of(L.worker_init, (W,))
    try:
        alive, mean = L.screen(pool, C[:L.NWIN], lpw[:L.NWIN])
    finally:
        pool.close()
        pool.join()
    order = np.argsort(-L.sortkey(alive, mean), kind="stable")
    b = int(order[0])
    res = dict(W=W, full_window_keys=int(np.sum(alive == L.NWIN)), best_kk=b, best_kind_k0=list(L.tdec.key_of(b)),
               best_alive=int(alive[b]), best_mean=float(mean[b]))
    json.dump(res, open(os.path.join(L.OUT, "real_wide_W4096.json"), "w"), indent=1)
    L.log("real screen at W=4096: full-window keys %d; best %s alive %d mean %.5f" % (
        res["full_window_keys"], res["best_kind_k0"], res["best_alive"], res["best_mean"]))
