# ABOUTME: Replays lane AA's checks through lane X's pipeline: exact stage-1 reproduction on two windows, the community
# ABOUTME: encipher cross-check, and one fresh odometer-dodge plant on the T 6000 window 1 layout (own encipher).
"""python -I -X utf8 jobs/verify-lane/runs/laneAA_replay.py

Three parts. (1) Determinism: lane X's pipeline (agents/laneX_general_alphabet, via lane Y's ylib, xlib.FLOOR = 1e-4)
re-attacks T 4000 window 3 and T 6000 window 0 with seed 0; stage 1 must reproduce the lane's recorded scores exactly.
(2) Our encipher equals the community doublet_phase_test.encipher (read from dl/aldegonde_port by AST) and lane X's
encipher_trace on random inputs. (3) One fresh plant: T 6000 window 1 layout, English from toolbox/runes.english_stream
at offset 850000 - n (unused by lane AA), a new random key, our encipher; attacked by the pipeline.

This file imports the lane X pipeline (not lane AA's code) and this folder's laneAA_verify.py for the word layout.
"""
import ast
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
os.chdir(REPO)                                   # toolbox/runes.py and lp/lpdata.py read repo-relative paths
M = 29
LANE = REPO / "agents" / "laneAA_chapter_keys"


def below_normal():
    if sys.platform == "win32":
        import ctypes
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


below_normal()
sys.path.insert(0, str(HERE))
import laneAA_verify as V                        # our own word layout (lp/lpdata.py), not lane AA's code
sys.path[:0] = [str(REPO / "agents" / "laneY_section_reset")]
import ylib as Y                                 # first: it puts lane X's directory on sys.path
import xlib as X
import pipeline as PL
X.FLOOR = 1e-4
sys.path.insert(0, str(REPO / "toolbox"))
import runes as rn


def running_mine(offsets):
    out, t = [], 0
    for s in offsets:
        t = (t + s) % M
        out.append(t)
    return out


def schedule_mine(rng):
    """Five offsets summing to 0 mod 29, exactly one zero (the one-zero schedule of the community's schedule(zeros=1))."""
    while True:
        free = [rng.randrange(1, M) for _ in range(3)]
        last = (-sum(free)) % M
        if last == 0:
            continue
        offs = [*free, last, 0]
        rng.shuffle(offs)
        return offs


def encipher_mine(words, K, offsets, start, space_skip, variant):
    """c = K[pos[p] + a + S[clock mod 5]] + b. A repeat of the previous cipher rune re-emits with S[(clock + d) mod 5]
    and the clock steps by `adv` (advance: d = +1, adv = 2; hold: d = -1, adv = 0). Space: clock += space_skip per word,
    a += 1 per word, b += 1 when a wraps. Returns (cipher words, number of dodges)."""
    d, adv = {"advance": (+1, 2), "hold": (-1, 0)}[variant]
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running_mine(offsets)
    a, b = start
    out, prev, clock, dodges = [], None, 0, 0
    for word in words:
        cw = []
        for p in word:
            c = (K[(pos[p] + a + S[clock % 5]) % M] + b) % M
            step = 1
            if c == prev:
                c = (K[(pos[p] + a + S[(clock + d) % 5]) % M] + b) % M
                step = adv
                dodges += 1
            cw.append(c)
            prev = c
            clock += step
        out.append(cw)
        clock += space_skip
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return out, dodges


def community_encipher():
    """The community's encipher, taken from its source by AST (its VARIANTS table and its running() are the same)."""
    src = (REPO / "dl" / "aldegonde_port" / "experiments" / "doublet_phase_test.py").read_text(encoding="utf-8")
    ns = {"M": M, "running": running_mine}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "VARIANTS" for t in node.targets):
            exec(compile(ast.Module([node], []), "VARIANTS", "exec"), ns)
        if isinstance(node, ast.FunctionDef) and node.name == "encipher":
            exec(compile(ast.Module([node], []), "encipher", "exec"), ns)
    return ns["encipher"], ns["VARIANTS"]


def attack_row(rec):
    return {k: rec[k] for k in ("n_runes", "anchors", "s1_score", "S", "kspace", "dead_chains", "quad_full")}


def main():
    t0 = time.time()
    words_mine, chap = V.lp2_words()
    lens = [len(w) for w in words_mine]
    words_lane, _page, _chap = Y.lp2_words_meta()
    same_words = words_mine == words_lane
    print(f"own LP2 words equal lane X/Y's loader words: {same_words} ({len(words_mine)} words)")
    rows4 = [json.loads(x) for x in (LANE / "out" / "windows_4000.jsonl").read_text(encoding="utf-8").splitlines()]
    rows6 = [json.loads(x) for x in (LANE / "out" / "windows_6000.jsonl").read_text(encoding="utf-8").splitlines()]

    # ---- (1) determinism
    print("\n## 1. Determinism: pipeline.attack(window, seed=0), FLOOR 1e-4, against the lane's recorded real records")
    det_ok = True
    for T, w, rows in ((4000, 3, rows4), (6000, 0, rows6)):
        starts, wins = V.window_layout(lens, T)
        a, b = wins[w]
        rec_lane = next(r for r in rows if r["kind"] == "real" and r["window"] == w)
        assert [a, b] == rec_lane["words"], "window layout differs from the lane's record"
        t1 = time.time()
        rec = PL.attack(words_mine[a:b], seed=0)
        plain_head = list(map(int, rec["plain"][:400]))
        ok_fields = {k: (rec[k] == rec_lane[k]) for k in ("n_runes", "anchors", "s1_score", "S", "kspace",
                                                             "dead_chains", "quad_full")}
        ok_plain = plain_head == rec_lane["plain_head"]
        ok = all(ok_fields.values()) and ok_plain
        det_ok &= ok
        print(f"T {T} window {w} words [{a}, {b}): s1 {rec['s1_score']!r} (lane {rec_lane['s1_score']!r}) "
              f"exact={ok_fields['s1_score']}; S {rec['S']} (lane {rec_lane['S']}); kspace {rec['kspace']} "
              f"(lane {rec_lane['kspace']}); anchors {rec['anchors']} (lane {rec_lane['anchors']}); "
              f"quad_full {rec['quad_full']!r} (lane {rec_lane['quad_full']!r}); dead {rec['dead_chains']}; "
              f"first 400 plain runes identical: {ok_plain}; {time.time() - t1:.0f}s")
        print("   fields equal:", ok_fields)

    # ---- (2) encipher cross-checks
    print("\n## 2. Our encipher against the community encipher (doublet_phase_test.py, by AST) and lane X's encipher_trace")
    community, VARIANTS = community_encipher()
    print("community VARIANTS (advance, hold):", {k: VARIANTS[k] for k in ("advance", "hold")})
    rng = random.Random(7331)
    trials, runes_cmp, dodges_total, mism_comm, mism_lane = 300, 0, 0, 0, 0
    for _ in range(trials):
        nw = rng.randrange(20, 120)
        plain = [[rng.randrange(M) for _ in range(rng.randrange(1, 12))] for _ in range(nw)]
        K = rng.sample(range(M), M)
        offs = schedule_mine(rng)
        start = (rng.randrange(M), rng.randrange(M))
        ss = rng.randrange(5)
        var = rng.choice(["advance", "hold"])
        mine, nd = encipher_mine(plain, K, offs, start, ss, var)
        comm = community(plain, K, offs, start, space_skip=ss, variant=var)
        lane, _ph = X.encipher_trace(plain, K, offs, start, ss, var)
        mism_comm += mine != comm
        mism_lane += mine != lane
        runes_cmp += sum(len(w) for w in plain)
        dodges_total += nd
    print(f"{trials} random cases, {runes_cmp} runes, {dodges_total} dodges exercised: "
          f"ours differs from community in {mism_comm} cases, from lane X's encipher_trace in {mism_lane} cases")
    enc_ok = mism_comm == 0 and mism_lane == 0

    # ---- (3) one fresh plant on the T 6000 window 1 layout
    print("\n## 3. Fresh plant: T 6000 window 1 layout, new English, new key, our encipher, variant hold")
    starts, wins = V.window_layout(lens, 6000)
    a, b = wins[1]
    plens = lens[a:b]
    n = sum(plens)
    offset = 850000 - n
    R, _W = rn.english_stream(850000 + 200)
    assert len(R) >= 850000, "English stream too short for the offset"
    flat = list(R[offset:offset + n])
    assert len(flat) == n
    it = iter(flat)
    plain = [[next(it) for _ in range(L)] for L in plens]
    prng = random.Random(20261018)
    K = prng.sample(range(M), M)
    offs = schedule_mine(prng)
    start = (prng.randrange(M), prng.randrange(M))
    space_skip = prng.randrange(5)
    variant = "hold"
    cw, nd = encipher_mine(plain, K, offs, start, space_skip, variant)
    lane_cw, _ph = X.encipher_trace(plain, K, offs, start, space_skip, variant)
    comm_cw = community(plain, K, offs, start, space_skip=space_skip, variant=variant)
    print(f"plant: words [{a}, {b}), {n} runes, English offset {offset} (lane AA used offsets below ~694,000 and "
          f"up to ~523,000 for chapters/coincidence), key {K[:8]}..., schedule {offs}, start {start}, "
          f"space skip {space_skip}, variant {variant}, dodges {nd}")
    print(f"our cipher equals community: {cw == comm_cw}; equals lane X encipher_trace: {cw == lane_cw}")
    t1 = time.time()
    rec = PL.attack(cw, seed=0)
    agree = float(np.mean(np.asarray(rec["plain"]) == np.asarray(flat)))
    # the window's null distribution from the lane's own out file (data only)
    nulls = [r["s1_score"] for r in rows6 if r["kind"] == "null" and r["window"] == 1]
    nmean = float(np.mean(nulls))
    nsd = float(np.std(nulls, ddof=1))
    nmax = max(nulls)
    above = rec["s1_score"] > nmax
    print(f"stage 1 score {rec['s1_score']:+.4f} against window 1's null max {nmax:.4f} (lane: 0.0245); "
          f"above the null max: {above}; z vs the 20 nulls {(rec['s1_score'] - nmean) / nsd:+.2f}; "
          f"nulls as high {sum(x >= rec['s1_score'] for x in nulls)} of {len(nulls)}")
    print(f"decrypt: {agree:.4f} of runes right (lane bar 0.8): {'decrypts' if agree >= 0.8 else 'does not decrypt'}; "
          f"S {rec['S']} kspace {rec['kspace']} anchors {rec['anchors']} quad_full {rec['quad_full']:.3f} "
          f"dead {rec['dead_chains']}; {time.time() - t1:.0f}s")
    head = 60
    print("truth   :", rn.tr(flat[:head]))
    print("decrypt :", rn.tr(list(map(int, rec["plain"][:head]))))
    out = {"det_ok": det_ok, "enc_ok": enc_ok, "same_words": same_words,
           "plant": {"words": [a, b], "n_runes": n, "offset": offset, "variant": variant, "dodges": nd,
                     "s1": rec["s1_score"], "null_max": nmax, "above_null_max": above, "agree": agree,
                     "S": rec["S"], "kspace": rec["kspace"], "quad_full": rec["quad_full"]}}
    (HERE / "laneAA_replay_out.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nwall {time.time() - t0:.0f}s; wrote {HERE / 'laneAA_replay_out.json'}")
    return 0 if (det_ok and enc_ok and same_words) else 1


if __name__ == "__main__":
    sys.exit(main())
