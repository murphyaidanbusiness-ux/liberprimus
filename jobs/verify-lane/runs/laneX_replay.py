# ABOUTME: Verify-lane check 6 for lane X: our own encipher makes a fresh English plant (advance, skip 900000), then
# ABOUTME: the lane's own pipeline.attack (imported here and only here, as the orchestrator asked) attacks it.
"""Run by laneX_verify.py in a subprocess, or by hand:  PYTHONUTF8=1 python -I -X utf8 jobs/verify-lane/runs/laneX_replay.py
"""
import ctypes
import os
import random
import site
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
sys.path.append(site.getusersitepackages())
sys.path[:0] = [str(ROOT / "toolbox"), str(ROOT / "lp")]
import runes  # noqa: E402

import numpy as np  # noqa: E402

LANE = ROOT / "agents" / "laneX_general_alphabet"
M = 29
NULL_MAX = 0.0218  # lane X's largest null stage-1 score (out/all.jsonl + out/null2.jsonl)


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
    while True:
        free = [rng.randrange(1, M) for _ in range(3)]
        last = (-sum(free)) % M
        if last:
            offs = free + [last, 0]
            rng.shuffle(offs)
            return offs


def encipher(words, K, offsets, a0, b0, variant):
    """Our own encipher, the same rule as laneX_verify.py: re-emit at clock+1 step 2 (advance) or clock-1 step 0 (hold)."""
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b = a0, b0
    out, phases, prev, clock = [], [], None, 0
    for word in words:
        cw = []
        for p in word:
            ph = clock % 5
            c = (K[(pos[p] + a + S[ph]) % M] + b) % M
            step = 1
            if c == prev:
                if variant == "advance":
                    ph, step = (clock + 1) % 5, 2
                else:
                    ph, step = (clock - 1) % 5, 0
                c = (K[(pos[p] + a + S[ph]) % M] + b) % M
            cw.append(c)
            phases.append(ph)
            prev = c
            clock += step
        out.append(cw)
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return out, phases


def english_words(n, skip_chars):
    R, W = runes.english_stream(n, skip_chars=skip_chars)
    assert len(R) == n
    words, cur, last = [], [], None
    for x, w in zip(R, W):
        if last is not None and w != last:
            words.append(cur)
            cur = []
        cur.append(x)
        last = w
    words.append(cur)
    return words


def main():
    below_normal()
    rng = random.Random(6006)
    words = english_words(12956, 900000)
    K = rng.sample(range(M), M)
    offs = one_zero_schedule(rng)
    a0, b0 = rng.randrange(M), rng.randrange(M)
    cipher, phases = encipher(words, K, offs, a0, b0, "advance")
    truth = np.array([x for w in words for x in w])

    sys.path.insert(0, str(LANE))
    import pipeline  # the lane's own attack: imported for check 6 only
    import xlib  # noqa: F401  (pulled in by pipeline; used for phase_accuracy)

    rec = pipeline.attack(cipher, seed=1)
    plain = np.asarray(rec["plain"]).ravel()
    assert plain.shape == truth.shape, (plain.shape, truth.shape)
    agree = float(np.mean(plain == truth))
    acc = xlib.phase_accuracy(rec["phase"], phases)
    print(f"  plant: our encipher, advance, space skip 0, {len(truth)} runes from English at char 900000; seed 6006")
    print(f"  pipeline.attack(seed=1): s1_score {rec['s1_score']:+.4f} "
          f"(above lane null max {NULL_MAX}: {rec['s1_score'] > NULL_MAX}); "
          f"s1 by space skip {{ {', '.join(f'{k}: {v:+.3f}' for k, v in sorted(rec['s1_by_kspace'].items()))} }}; "
          f"chosen space skip {rec['kspace']}")
    print(f"  stage 2: a0 {rec['a0']}, IoC {rec['ioc']:.3f}, quadgram {rec['quad_full']:.3f} "
          f"(lane null quadgram max -6.513)")
    print(f"  plaintext runes equal to ours: {agree:.4f}; phase accuracy {acc:.4f}; seconds {rec['seconds']:.0f}")


if __name__ == "__main__":
    main()
