# ABOUTME: TEST DRILL of the CLAUDE.md lead protocol on two PLANTED ciphers (not LP2): a full solve (lane X attack on
# ABOUTME: a planted odometer-dodge key) and a lead (lane Y detects a planted restart key but cannot decrypt it).
"""Runs step 1 (verification) of the lead protocol for both drills and writes out/drill.json.

    python -I -X utf8 agents/drill_lead_protocol/drill.py

Drill 1 (solve): the planted cipher is lane X's layout plant 0 (seed 55000, advance) on LP2's word layout.
Drill 2 (lead):  the planted cipher is lane Y's chapter plant 0 (seed 66000, advance), restart per chapter.
Nothing here touches LP2's runes except its word, page and chapter layout.
"""
import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path[:0] = [str(REPO / "agents" / "laneY_section_reset"), str(REPO / "agents" / "laneX_general_alphabet")]
import ylib as Y  # noqa: E402
import xlib as X  # noqa: E402
import pipeline as PL  # noqa: E402
import stage2 as S2  # noqa: E402
import lpdata  # noqa: E402

NULL_X = (0.0158, 0.0029, 0.0218)        # lane X: 50 nulls, mean / sd / max (agents/laneX_general_alphabet/RESULTS.md)


def tr(p):
    return "".join(lpdata.TR[i] for i in p)


def drill1():
    words, page, _chap = Y.lp2_words_meta()
    lens = [len(w) for w in words]
    rng = random.Random(55000)
    flat = [x for w in X.english_words(sum(lens), 60000) for x in w]
    it = iter(flat)
    plain = [[next(it) for _ in range(L)] for L in lens]
    K = rng.sample(range(29), 29)
    offs = X.schedule(rng)
    dials = (rng.randrange(29), rng.randrange(29))
    cw, _ph = X.encipher_trace(plain, K, offs, dials, 0, "advance")
    truth = np.array(flat[:sum(lens)])
    a = PL.attack(cw, seed=0)                         # the "discovery"
    b = PL.attack(cw, seed=12345)                     # (1a) re-run from scratch with a new seed
    same = float(np.mean(a["plain"] == b["plain"]))
    # (1b) language on many pages independently, and the per-page null of a shuffled decrypt
    q = S2.quad_table()
    rune_page = np.array([pg for pg, w in zip(page, words) for _ in w])
    per_page = []
    for pg in sorted(set(page)):
        seg = a["plain"][rune_page == pg]
        if len(seg) >= 40:
            per_page.append((pg, S2.quad_score(seg, q)))
    shuf = a["plain"].copy()
    np.random.default_rng(1).shuffle(shuf)
    null_page = S2.quad_score(shuf[:263], q)
    english_pages = sum(s >= -5.5 for _p, s in per_page)
    # (1c) the stage-1 score against lane X's 50-null distribution
    z = (a["s1_score"] - NULL_X[0]) / NULL_X[1]
    # (1d) the independent scorer and the oracle on the recovered plaintext
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "drill1_plaintext.txt").write_text(tr(a["plain"]), encoding="utf-8")
    vc = subprocess.run([sys.executable, "lp/verify_candidate.py", str(out / "drill1_plaintext.txt")],
                        capture_output=True, text=True, cwd=REPO)
    orc = subprocess.run([sys.executable, "dl/dukotah/liber-primus/verify_solution.py", "--plaintext",
                          str(out / "drill1_plaintext.txt"), "--skip-anchor"], capture_output=True, text=True, cwd=REPO)
    return {"s1_score": a["s1_score"], "z_vs_null": z, "null_max": NULL_X[2], "quad_full": a["quad_full"],
            "rerun_same_plaintext": same, "pages_scored": len(per_page), "pages_in_english_band": english_pages,
            "shuffled_page_score": null_page, "worst_page": min(s for _p, s in per_page),
            "best_page": max(s for _p, s in per_page),
            "verify_candidate_tail": vc.stdout.strip().splitlines()[-6:],
            "oracle_tail": [l for l in orc.stdout.strip().splitlines() if l.strip()][-4:],
            "first_200": tr(a["plain"][:200]),
            "ground_truth_agreement (drill only)": float(np.mean(a["plain"] == truth))}


def drill2():
    words, _page, chap = Y.lp2_words_meta()
    segw = Y.seg_ids(chap)
    lens = [len(w) for w in words]
    rng = random.Random(66000)
    flat = [x for w in X.english_words(sum(lens), 200000) for x in w]
    it = iter(flat)
    plain = [[next(it) for _ in range(L)] for L in lens]
    K = rng.sample(range(29), 29)
    offs = X.schedule(rng)
    dials = (rng.randrange(29), rng.randrange(29))
    cw, _ph = Y.encipher_segments(plain, segw, K, offs, dials, 0, "advance")
    truth = np.array(flat[:sum(lens)])
    a = Y.attack(cw, segw, seed=0, kspaces=(0,))
    b = Y.attack(cw, segw, seed=999, kspaces=(0,), do_stage2=False)

    def half(parity):
        idx = [i for i, s in enumerate(segw) if s % 2 == parity]
        return [cw[i] for i in idx], [segw[i] for i in idx]

    def shuffled(ws, rng):
        flat_c = [x for w in ws for x in w]
        d = [(flat_c[i] - flat_c[i - 1]) % 29 for i in range(1, len(flat_c))]
        rng.shuffle(d)
        out, cur = [flat_c[0]], flat_c[0]
        for x in d:
            cur = (cur + x) % 29
            out.append(cur)
        it2 = iter(out)
        return [[next(it2) for _ in w] for w in ws]

    held = {}
    for parity in (0, 1):
        ws, sg = half(parity)
        real = Y.attack(ws, sg, seed=parity, kspaces=(0,), do_stage2=False)["s1_score"]
        nul = [Y.attack(shuffled(ws, random.Random(500 + k + 10 * parity)), sg, seed=k, kspaces=(0,),
                        do_stage2=False)["s1_score"] for k in range(5)]
        held["even chapters" if parity == 0 else "odd chapters"] = {
            "score": real, "null_mean": float(np.mean(nul)), "null_max": float(np.max(nul))}
    return {"s1_score": a["s1_score"], "rerun_s1": b["s1_score"], "S": a["S"], "quad_full": a["quad_full"],
            "held_out_halves": held, "first_120": tr(a["plain"][:120]),
            "ground_truth_agreement (drill only)": float(np.mean(a["plain"] == truth))}


if __name__ == "__main__":
    res = {"drill1_solve": drill1(), "drill2_lead": drill2()}
    (HERE / "out" / "drill.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))
