# ABOUTME: Verify-lane checks for lane Z (dial units, 2026-10-18): LP2 unit runs from lpdata, the lane's null and plant
# ABOUTME: statistics from out/all.jsonl, our encipher cross-checked against the community's, and one fresh line-dial plant.
"""Run from the repository root:  PYTHONUTF8=1 python -I -X utf8 jobs/verify-lane/runs/laneZ_verify.py

Fresh code. It imports lp/ and toolbox/ only, and uses the community cipher doublet_phase_test.encipher as the reference
for our encipher. The lane's own attack is imported only by laneZ_replay.py, which check 3 runs as a subprocess (the same
arrangement as laneX_verify.py and laneX_replay.py), so this file imports no lane code.
"""
import ctypes
import json
import os
import random
import site
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
sys.path.append(site.getusersitepackages())  # -I hides user site-packages (numpy and scipy live there)
sys.path[:0] = [str(ROOT / "toolbox"), str(ROOT / "lp")]
import numpy as np  # noqa: E402
import lpdata  # noqa: E402
import runes  # noqa: E402

PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
M = 29
UNITS = ("line", "sent", "page", "chap")
RUN_DIR = ROOT / "jobs" / "verify-lane" / "runs"
ALL = ROOT / "agents" / "laneZ_dial_units" / "out" / "all.jsonl"
COMMUNITY_DIRS = [ROOT / "dl" / "aldegonde_port" / "experiments", ROOT / "dl" / "aldegonde_port" / "src"]
SPEC_OFFSET = 1500000   # the brief's offset; past the end of the English stream (896,471 runes), so not used
OFFSET = 800000         # fresh English: after lane Z's plant range (600000 to 712956) and inside the stream
PLANT_SEED = 20261018

# The lane's claimed values, from the orchestrator's brief (lane Z has no RESULTS.md yet).
LANE_UNITS = {"line": (594, 3, 22, 26), "sent": (175, 3, 54, 375), "page": (55, 66, 263, 277), "chap": (17, 9, 534, 2474)}
LANE_STATS = {
    "line": dict(mean=0.0171, sd=0.0022, mx=0.0200, real=0.0185, z=0.67, n_ge=11, pmin=0.105, pdet=6, pagree=4),
    "sent": dict(mean=0.0182, sd=0.0026, mx=0.0254, real=0.0203, z=0.79, n_ge=3, pmin=0.137, pdet=6, pagree=4),
    "page": dict(mean=0.0172, sd=0.0030, mx=0.0267, real=0.0195, z=0.76, n_ge=5, pmin=0.118, pdet=6, pagree=4),
    "chap": dict(mean=0.0254, sd=0.0030, mx=0.0321, real=0.0241, z=-0.44, n_ge=20, pmin=0.284, pdet=6, pagree=3),
}


def below_normal():
    if sys.platform == "win32":
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


def running(offsets):
    out, t = [], 0
    for s in offsets:
        t = (t + s) % M
        out.append(t)
    return out


def one_zero_schedule(rng):
    """Five offsets, summing to 0 mod 29, with exactly one zero (the one-zero schedule of the community)."""
    while True:
        free = [rng.randrange(1, M) for _ in range(3)]
        last = (-sum(free)) % M
        if last:
            offs = free + [last, 0]
            rng.shuffle(offs)
            return offs


def encipher_units(units, K, offsets, start, variant):
    """Our encipher: the community's doublet_phase_test rule, with the inner dial stepping once per UNIT.

    With units = words this is the community's encipher exactly (checked below); with units = lines, sentences, pages
    or chapters it is the lane Z model. A doublet re-emits at the neighbouring phase, and the clock moves by `advance`.
    Returns the cipher units and the clock phase each rune was emitted at (the truth for a phase-recovery score).
    """
    direction, advance = {"advance": (+1, 2), "hold": (-1, 0)}[variant]
    pos = [0] * M
    for i, sym in enumerate(K):
        pos[sym] = i
    S = running(offsets)
    a, b = start
    out, phases, prev, clock = [], [], None, 0
    for unit in units:
        cu = []
        for p in unit:
            ph = clock % 5
            c = (K[(pos[p] + a + S[ph]) % M] + b) % M
            step = 1
            if c == prev:
                ph = (clock + direction) % 5
                c = (K[(pos[p] + a + S[ph]) % M] + b) % M
                step = advance
            cu.append(c)
            phases.append(ph)
            prev = c
            clock += step
        out.append(cu)
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return out, phases


def rune_ids(kind):
    """LP2 (pages 0-54, SHA-pinned): one unit id per rune, for kind in line, sent, page, chap."""
    U, _idx, sha = lpdata.unsolved()
    assert sha == PIN, sha
    ids = []
    for p in U:
        ids += [p["page"]] * len(p["idx"]) if kind == "page" else list(p[kind])
    return ids


def run_lengths(seq):
    out, n, prev = [], 0, object()
    for x in seq:
        if n and x != prev:
            out.append(n)
            n = 0
        n += 1
        prev = x
    if n:
        out.append(n)
    return out


def cut(seq, ids):
    """Split seq at every change of unit id."""
    out, cur, prev = [], [], object()
    for x, u in zip(seq, ids):
        if cur and u != prev:
            out.append(cur)
            cur = []
        cur.append(x)
        prev = u
    if cur:
        out.append(cur)
    return out


def same(ours, lane, places):
    return round(ours, places) == lane


def check1():
    print("== CHECK 1: unit runs from lpdata.unsolved() (SHA pin asserted)")
    U, idx, sha = lpdata.unsolved()
    assert sha == PIN and len(idx) == 12956, (sha, len(idx))
    print(f"  LP2 pages 0-54: {len(idx)} runes, SHA-256 pin matches")
    res, ok = {}, True
    for kind in UNITS:
        lens = run_lengths(rune_ids(kind))
        assert sum(lens) == len(idx)
        n, mn, md, mx = len(lens), min(lens), statistics.median(lens), max(lens)
        res[kind] = dict(n=n, mn=mn, md=md, mx=mx)
        lane = LANE_UNITS[kind]
        match = (n, mn, md, mx) == lane
        ok &= match
        print(f"  {kind:<5} ours {n:>4} units, length min/median/max {mn}/{md:g}/{mx}   "
              f"lane {lane[0]} ({lane[1]}/{lane[2]}/{lane[3]})   {'reproduced' if match else 'differs'}")
    print(f"  CHECK 1 {'PASS' if ok else 'FAIL'}")
    return res, ok


def check2():
    print("== CHECK 2: null, real and plant statistics from agents/laneZ_dial_units/out/all.jsonl")
    rows = [json.loads(line) for line in ALL.read_text(encoding="utf-8").splitlines() if line.strip()]
    print(f"  {len(rows)} rows (expected 148 = 4 units x (6 plants + 30 nulls + 1 real))")
    assert len(rows) == 148
    res, ok = {}, True
    for unit in UNITS:
        nul = [r["s1_score"] for r in rows if r["unit"] == unit and r["kind"] == "null"]
        pl = [r for r in rows if r["unit"] == unit and r["kind"] == "plant"]
        rl = [r for r in rows if r["unit"] == unit and r["kind"] == "real"]
        assert len(nul) == 30 and len(pl) == 6 and len(rl) == 1
        n_units = {r["n_units"] for r in rows if r["unit"] == unit}
        mean, sd, sdp, mx = statistics.fmean(nul), statistics.stdev(nul), statistics.pstdev(nul), max(nul)
        real = rl[0]["s1_score"]
        z = (real - mean) / sd
        n_ge = sum(x >= real for x in nul)
        pmin = min(p["s1_score"] for p in pl)
        pdet = sum(p["s1_score"] > mx for p in pl)
        pagree = sum(p["agree"] >= 0.8 for p in pl)
        res[unit] = dict(mean=mean, sd=sd, sdp=sdp, mx=mx, real=real, z=z, zp=(real - mean) / sdp, n_ge=n_ge,
                         pmin=pmin, pdet=pdet, pagree=pagree, n_units=sorted(n_units))
        lane = LANE_STATS[unit]
        checks = [
            ("null mean", same(mean, lane["mean"], 4)), ("null sd", same(sd, lane["sd"], 4)),
            ("null max", same(mx, lane["mx"], 4)), ("real", same(real, lane["real"], 4)),
            ("z", same(z, lane["z"], 2)), ("nulls >= real", n_ge == lane["n_ge"]),
            ("plant min", same(pmin, lane["pmin"], 3)), ("plants > null max", pdet == lane["pdet"]),
            ("plants agree >= 0.8", pagree == lane["pagree"]),
        ]
        bad = [name for name, good in checks if not good]
        ok &= not bad
        print(f"  {unit:<5} null mean {mean:.4f} sd {sd:.4f} (pop sd {sdp:.4f}) max {mx:.4f} | lane "
              f"{lane['mean']:.4f}/{lane['sd']:.4f}/{lane['mx']:.4f}")
        print(f"        real {real:.4f} z {z:+.2f} (pop-sd z {(real - mean) / sdp:+.2f}) nulls>=real {n_ge} | lane "
              f"{lane['real']:.4f} z {lane['z']:+.2f} ({lane['n_ge']})")
        print(f"        plants min {pmin:.3f} >null max {pdet}/6 agree>=0.8 {pagree}/6 | lane "
              f"{lane['pmin']:.3f} {lane['pdet']}/6 {lane['pagree']}/6   "
              f"{'reproduced' if not bad else 'differs: ' + ', '.join(bad)}")
    print(f"  CHECK 2 {'PASS' if ok else 'FAIL'}")
    return res, ok


def load_community():
    sys.path[:0] = [str(d) for d in COMMUNITY_DIRS]
    import doublet_phase_test as community  # noqa: E402
    return community


def check_cipher(community):
    print("== CHECK 3a: our encipher equals the community doublet_phase_test.encipher")
    rng = random.Random(7)
    R, W = runes.english_stream(3000)
    words, cur, last = [], [], None
    for x, w in zip(R, W):
        if last is not None and w != last:
            words.append(cur)
            cur = []
        cur.append(x)
        last = w
    words.append(cur)
    results = []
    for variant in ("advance", "hold"):
        for trial in range(4):
            K = rng.sample(range(M), M)
            offs = one_zero_schedule(rng)
            start = (rng.randrange(M), rng.randrange(M))
            same_out = encipher_units(words, K, offs, start, variant)[0] == community.encipher(words, K, offs, start, 0, variant)
            results.append((f"words, {variant}, trial {trial}", same_out))
    ok = all(good for _n, good in results)
    print(f"  word-level (one step per word): {sum(g for _n, g in results)}/{len(results)} identical")
    print(f"  CHECK 3a {'PASS' if ok else 'FAIL'}")
    return ok


def check3(community, plain_units_ok):
    print("== CHECK 3: fresh line-dial plant, our encipher, then the lane's attack (subprocess laneZ_replay.py)")
    ids = rune_ids("line")
    N = len(ids)
    avail = len(runes.english_stream(SPEC_OFFSET + N + 200)[0])
    print(f"  English stream holds {avail} runes; the brief's offset {SPEC_OFFSET} needs {SPEC_OFFSET + N}, so it is "
          f"not used. Fresh offset {OFFSET} (lane Z's plants used 600000 to 712956).")
    R, _W = runes.english_stream(OFFSET + N + 200)
    plain = R[OFFSET:OFFSET + N]
    assert len(plain) == N
    units = cut(plain, ids)
    rng = random.Random(PLANT_SEED)
    K = rng.sample(range(M), M)
    offs = one_zero_schedule(rng)
    start = (rng.randrange(M), rng.randrange(M))
    cipher, phases = encipher_units(units, K, offs, start, "advance")
    same_as_community = cipher == community.encipher(units, K, offs, start, 0, "advance")
    print(f"  plant: {len(units)} LP2 lines, {N} runes, variant advance, seed {PLANT_SEED}, true schedule "
          f"{running(offs)}, start dials {start}; our encipher == community encipher (lines as words): {same_as_community}")
    plant_path = RUN_DIR / "laneZ_replay_plant.json"
    out_path = RUN_DIR / "laneZ_replay_out.json"
    plant_path.write_text(json.dumps({"units": cipher, "plain": plain, "plain_units": units, "phases": phases,
                                      "offset": OFFSET, "K": K, "offsets": offs, "start": list(start),
                                      "variant": "advance"}), encoding="utf-8")
    t0 = time.time()
    proc = subprocess.run([sys.executable, "-I", "-X", "utf8", str(RUN_DIR / "laneZ_replay.py"), str(plant_path),
                           str(out_path)], cwd=str(ROOT), capture_output=True, text=True, timeout=1800,
                          env=dict(os.environ, PYTHONUTF8="1"))
    if proc.returncode != 0:
        print("  replay FAILED:\n" + proc.stderr[-2000:])
        return None, False
    out = json.loads(out_path.read_text(encoding="utf-8"))
    got = np.asarray(out["plain"]).ravel()
    truth = np.asarray(plain)
    assert got.shape == truth.shape, (got.shape, truth.shape)
    agree = float(np.mean(got == truth))
    found, true = np.asarray(out["phase"]), np.asarray(phases)
    # phase accuracy, maximised over a global relabel of the five phases (the lane's convention)
    acc = max(float(np.mean((found + c) % 5 == true)) for c in range(5))
    nmax = LANE_STATS["line"]["mx"]
    detect = out["s1_score"] > nmax
    decrypt = agree >= 0.8
    print(f"  pipeline.attack(seed=1): s1_score {out['s1_score']:+.4f} (above the line null max {nmax}: {detect}); "
          f"chosen space skip {out['kspace']}; anchors {out['anchors']}; dead chains {out['dead_chains']}; "
          f"quadgram {out['quad_full']:.3f}")
    print(f"  the lane's encipher_trace reproduces our plant: {out['lane_encipher_trace_equal']}")
    print(f"  stage-1 clock phase accuracy vs the true phases: {acc:.4f} (chance 0.2)")
    print(f"  plaintext runes equal to ours: {agree:.4f} (the lane's 'decrypted' bar is 0.8: {decrypt}); "
          f"recovered schedule {out['S']} vs true {running(offs)}; replay {out['seconds']:.0f} s "
          f"(wall {time.time() - t0:.0f} s)")
    print(f"  CHECK 3 detection {'PASS' if detect else 'FAIL'}; CHECK 3 decryption {'PASS' if decrypt else 'FAIL'}")
    return dict(s1=out["s1_score"], agree=agree, phase_acc=acc, kspace=out["kspace"]), detect and decrypt


def main():
    below_normal()
    print("laneZ_verify: lane Z (dial units) verification, 2026-10-18; repo", ROOT)
    _c1, ok1 = check1()
    _c2, ok2 = check2()
    community = load_community()
    ok3a = check_cipher(community)
    res3, ok3 = check3(community, ok3a)
    all_ok = ok1 and ok2 and ok3a and ok3
    print(f"SUMMARY: check1 {'PASS' if ok1 else 'FAIL'}, check2 {'PASS' if ok2 else 'FAIL'}, "
          f"check3a {'PASS' if ok3a else 'FAIL'}, check3 {'PASS' if ok3 else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
