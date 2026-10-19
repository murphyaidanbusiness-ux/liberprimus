# ABOUTME: Verify-lane check 4 for lane Y: replays the lane's attack (ylib.attack) on a fresh restart-per-page plant made by
# ABOUTME: our own encipher. Kept apart from laneY_verify.py so that file imports no lane code (lane X's precedent).
"""Check 4 of the lane Y verification (2026-10-18).

    PYTHONUTF8=1 python -I -X utf8 jobs/verify-lane/runs/laneY_replay.py     (run by laneY_verify.py; from the repo root)

A fresh plant: random K (seed 4444), one-zero drift schedule, random start dials, English from toolbox/runes.english_stream
at character 1,200,000, cut into LP2's exact word lengths, enciphered page by page with the same key restarted at each
page, advance variant. Then the lane's ylib.attack(words, segw, seed=1, kspaces=(0,)) with segw from the page labels.
The last line printed is "RESULT " followed by a JSON object.
"""
import ctypes
import json
import os
import random
import site
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)
sys.path.append(site.getusersitepackages())  # -I hides it; numpy lives there
sys.path[:0] = [str(ROOT / "toolbox"), str(ROOT / "lp")]
import lpdata  # noqa: E402
import runes  # noqa: E402

assert Path(lpdata.__file__).resolve() == (ROOT / "lp" / "lpdata.py").resolve()
assert Path(runes.__file__).resolve() == (ROOT / "toolbox" / "runes.py").resolve()

import numpy as np  # noqa: E402

M = 29
PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
LANE_JSONL = ROOT / "agents" / "laneY_section_reset" / "out" / "all.jsonl"
ENGLISH_OFFSET = 1200000


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


def inverse(K):
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    return pos


def one_zero_schedule(rng):
    while True:
        free = [rng.randrange(1, M) for _ in range(3)]
        last = (-sum(free)) % M
        if last:
            offs = free + [last, 0]
            rng.shuffle(offs)
            return offs


def encipher(words, K, offsets, start, variant):
    """Same cipher as laneY_verify.py's encipher: c = K[pos[p] + a_w + S[phase]] + b_w, re-emit on a repeat."""
    pos, S = inverse(K), running(offsets)
    a, b = start
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


def lp2_words(U):
    words, page_of = [], []
    last = None
    for pg in U:
        for x, wid in zip(pg["idx"], pg["word"]):
            key = (pg["page"], wid)
            if key != last:
                words.append([])
                page_of.append(pg["page"])
                last = key
            words[-1].append(x)
    return words, page_of


def cut(flat, lens):
    it = iter(flat)
    return [[next(it) for _ in range(n)] for n in lens]


def main():
    below_normal()
    t0 = time.time()
    rows = [json.loads(line) for line in open(LANE_JSONL, encoding="utf-8")]
    page_null_max = max(r["s1_score"] for r in rows if r["kind"] == "null" and r["seg"] == "page")
    U, C, sha = lpdata.unsolved()
    assert sha == PIN
    words, page_of = lp2_words(U)
    assert [x for w in words for x in w] == list(C)
    lens = [len(w) for w in words]
    rng = random.Random(4444)
    flat = runes.english_stream(sum(lens), skip_chars=ENGLISH_OFFSET)[0]
    assert len(flat) == sum(lens)
    plain = cut(flat, lens)
    K = rng.sample(range(M), M)
    offs = one_zero_schedule(rng)
    start = (rng.randrange(M), rng.randrange(M))
    segs, i = [], 0
    for j in range(1, len(page_of) + 1):
        if j == len(page_of) or page_of[j] != page_of[i]:
            segs.append((i, j))
            i = j
    cipher, segw = [], [0] * len(words)
    for s, (i, j) in enumerate(segs):  # the same key, offsets and dials restarted at every page
        mine, _ph = encipher(plain[i:j], K, offs, start, "advance")
        cipher += mine
        for w in range(i, j):
            segw[w] = s
    print("plant: %d runes, %d words, %d page segments, advance, offsets %s, start %s, English from char %d"
          % (len(flat), len(words), len(segs), offs, start, ENGLISH_OFFSET))
    sys.path[:0] = [str(ROOT / "agents" / "laneY_section_reset")]
    import ylib  # the lane's code: check 4 only, in this file
    t1 = time.time()
    rec = ylib.attack(cipher, segw, seed=1, kspaces=(0,))
    plain_out, truth = np.asarray(rec["plain"]), np.asarray(flat)
    assert plain_out.shape == truth.shape
    frac = float(np.mean(plain_out == truth))
    res = dict(s1_score=float(rec["s1_score"]), page_null_max=float(page_null_max),
               above_page_null_max=bool(float(rec["s1_score"]) > page_null_max), anchors=int(rec["anchors"]),
               S=list(map(int, rec["S"])), kspace=int(rec["kspace"]), quad_full=float(rec["quad_full"]),
               frac_equal=frac, equal_runes=int(np.sum(plain_out == truth)), runes=int(len(flat)))
    print("s1_score %+.4f vs page null max %.4f: above = %s; anchors %d; S %s; kspace %d; quadgram %.3f"
          % (res["s1_score"], page_null_max, res["above_page_null_max"], res["anchors"], res["S"], res["kspace"],
             res["quad_full"]))
    print("fraction of runes of its plain equal to our plaintext: %.4f (%d of %d); attack %.0f s"
          % (frac, res["equal_runes"], res["runes"], time.time() - t1))
    print("RESULT " + json.dumps(res))


if __name__ == "__main__":
    main()
