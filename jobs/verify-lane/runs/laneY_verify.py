# ABOUTME: Verify-lane script for lane Y (agents/laneY_section_reset): LP2's chapter and page layout, our own encipher of
# ABOUTME: the odometer dodge with the key restarted per segment, the lane's null/real/plant statistics, one replay.
"""Checks 1-4 of the lane Y verification (2026-10-18).

    PYTHONUTF8=1 python -I -X utf8 jobs/verify-lane/runs/laneY_verify.py      (from the repository root)

Imports: lp/ and toolbox/ for the data, and the community's doublet_phase_test.encipher as the cipher reference in check 2
only. Check 4 runs jobs/verify-lane/runs/laneY_replay.py as a subprocess (that file imports the lane's ylib); this file
imports no lane code.
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
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)  # lp/lpdata.py and toolbox/runes.py read ./dl by relative path
sys.path.append(site.getusersitepackages())  # -I hides it; numpy lives there
COMMUNITY = ROOT / "dl" / "aldegonde_port"
sys.path[:0] = [str(COMMUNITY / "src"), str(COMMUNITY / "experiments")]
import doublet_phase_test as community  # noqa: E402  (cipher reference, check 2 only)

sys.path[:0] = [str(ROOT / "toolbox"), str(ROOT / "lp")]
import lpdata  # noqa: E402
import runes  # noqa: E402

assert Path(lpdata.__file__).resolve() == (ROOT / "lp" / "lpdata.py").resolve()
assert Path(runes.__file__).resolve() == (ROOT / "toolbox" / "runes.py").resolve()

import numpy as np  # noqa: E402

M = 29
PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
LANE_JSONL = ROOT / "agents" / "laneY_section_reset" / "out" / "all.jsonl"
LANE_ERR = ROOT / "agents" / "laneY_section_reset" / "logs" / "run_all.log.err"

# The lane's headline numbers as the verification brief gives them (RESULTS.md was not on disk when this ran).
LANE = {
    "chapter": dict(null_mean=0.0162, null_sd=0.0022, null_max=0.0205, real=0.0178, z=0.74, n_ge=10,
                    plant_min=0.107, detected=10, decrypted=6),
    "page": dict(null_mean=0.0183, null_sd=0.0029, null_max=0.0259, real=0.0174, z=-0.29, n_ge=31,
                 plant_min=0.131, detected=10, decrypted=6),
}


def below_normal():
    if sys.platform == "win32":
        k32 = ctypes.windll.kernel32
        k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


# ---------------------------------------------------------------- shared helpers
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
    """Five drift offsets summing to 0 mod 29, exactly one of them zero (the doublet preventer's failure condition)."""
    while True:
        free = [rng.randrange(1, M) for _ in range(3)]
        last = (-sum(free)) % M
        if last:
            offs = free + [last, 0]
            rng.shuffle(offs)
            return offs


def encipher(words, K, offsets, start, variant):
    """Our own encipher of the odometer dodge, per rune: c = K[pos[p] + a_w + S[phase]] + b_w, with a_w one step per
    word, b_w stepping when a_w wraps, and the clock one step per rune. On a would-be repeat (c equal to the previous
    cipher rune) re-emit at phase clock+1 with clock step 2 ("advance") or at phase clock-1 with step 0 ("hold").
    The key, offsets and start dials are the same for every call; a call is one segment, so a call restarts them.
    Returns (cipher words, phase used per rune)."""
    assert variant in ("advance", "hold")
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
    """LP2 words: a run of runes with one (page, word id). Returns words, the page and chapter of each word."""
    words, page_of, chap_of = [], [], []
    last = None
    for pg in U:
        for x, wid, ch in zip(pg["idx"], pg["word"], pg["chap"]):
            key = (pg["page"], wid)
            if key != last:
                words.append([])
                page_of.append(pg["page"])
                chap_of.append(ch)
                last = key
            words[-1].append(x)
    return words, page_of, chap_of


def segments(labels):
    """Contiguous runs of equal labels, as (start, end) word index ranges."""
    out, s = [], 0
    for i in range(1, len(labels) + 1):
        if i == len(labels) or labels[i] != labels[s]:
            out.append((s, i))
            s = i
    return out


def cut(flat, lens):
    it = iter(flat)
    return [[next(it) for _ in range(n)] for n in lens]


# ---------------------------------------------------------------- check 1: segmentation
def check1():
    print("== check 1: LP2 segmentation (lpdata.unsolved, SHA pin asserted) ==")
    U, C, sha = lpdata.unsolved()
    assert sha == PIN, sha
    words, page_of, chap_of = lp2_words(U)
    assert [x for w in words for x in w] == list(C)
    # a word never straddles a chapter boundary: every rune of a word carries the chapter of its first rune
    straddle, last, first_ch = 0, None, None
    for pg in U:
        for wid, ch in zip(pg["word"], pg["chap"]):
            key = (pg["page"], wid)
            if key != last:
                first_ch, last = ch, key
            elif ch != first_ch:
                straddle += 1
    runes_chap = {ch for pg in U for ch in pg["chap"]}
    pages_change = [pg["page"] for pg in U if len(set(pg["chap"])) > 1]
    inside_changes = sum(1 for pg in U for a, b in zip(pg["chap"], pg["chap"][1:]) if a != b)
    chap_size = {}
    for pg in U:
        for ch in pg["chap"]:
            chap_size[ch] = chap_size.get(ch, 0) + 1
    page_sizes = [len(pg["idx"]) for pg in U]
    res = dict(
        pages=len(U),
        pages_with_words=len(set(page_of)),
        runes=len(C),
        chapters=len(runes_chap),
        chapter_labels=(min(runes_chap), max(runes_chap)),
        chapter_runes_min_max=(min(chap_size.values()), max(chap_size.values())),
        page_runes_min_max=(min(page_sizes), max(page_sizes)),
        words=len(words),
        words_straddling_chapter=straddle,
        chapter_segments=len(segments(chap_of)),
        page_segments=len(segments(page_of)),
        pages_with_inside_chapter_change=len(pages_change),
        inside_page_chapter_changes=inside_changes,
        pages_listing=pages_change,
    )
    for k, v in res.items():
        print("  %-34s %s" % (k, v))
    return res


# ---------------------------------------------------------------- check 2: restart model
def rune_records(plain, cipher, phases, segs):
    """One record per rune: (segment, local word index, global word index, phase used, plaintext, ciphertext)."""
    recs, pos = [], 0
    for s, (i, j) in enumerate(segs):
        for wl, w in enumerate(range(i, j)):
            for p, c in zip(plain[w], cipher[w]):
                recs.append((s, wl, w, phases[pos], p, c))
                pos += 1
    return recs


def audit(recs, local=True):
    """Groups are (word index mod 29, phase used); y = (c - floor(index / 29)) mod 29 with index local (or global)."""
    within, pooled, seen_in = defaultdict(set), defaultdict(set), defaultdict(set)
    for s, wl, w, ph, p, c in recs:
        idx = wl if local else w
        g = (idx % M, ph)
        y = (c - idx // M) % M
        within[(s, g, p)].add(y)
        pooled[(g, p)].add(y)
        seen_in[(g, p)].add(s)
    gy = defaultdict(set)
    for (g, p), ys in pooled.items():
        if len(ys) == 1:
            gy[(g, next(iter(ys)))].add(p)
    return dict(
        within_bad=sum(1 for v in within.values() if len(v) > 1),
        pooled_bad=sum(1 for v in pooled.values() if len(v) > 1),
        groups=len({g for g, _p in pooled}),
        pairs=len(pooled),
        pairs_multi_segment=sum(1 for v in seen_in.values() if len(v) >= 2),
        injective_bad=sum(1 for v in gy.values() if len(v) > 1),
    )


def predicted_y(p, r, ph, K, S, start, pos):
    """Closed form for the local model: y = K[pos[p] + (a0 + r) mod 29 + S[ph]] + b0 + floor((a0 + r) / 29)."""
    a0, b0 = start
    return (K[(pos[p] + (a0 + r) % M + S[ph]) % M] + b0 + (a0 + r) // M) % M


def check2():
    print("== check 2: restart model (our encipher; community encipher as reference) ==")
    U, C, sha = lpdata.unsolved()
    assert sha == PIN
    words, page_of, chap_of = lp2_words(U)
    lens = [len(w) for w in words]
    out = []
    for kind, labels in (("chapter", chap_of), ("page", page_of)):
        segs = segments(labels)
        for k, variant in enumerate(("advance", "hold")):
            rng = random.Random(7000 + 10 * k + (kind == "page"))
            flat = runes.english_stream(sum(lens), skip_chars=600000 + 40000 * k + (kind == "page") * 200000)[0]
            assert len(flat) == sum(lens)
            plain = cut(flat, lens)
            K = rng.sample(range(M), M)
            offs = one_zero_schedule(rng)
            start = (rng.randrange(M), rng.randrange(M))
            cipher, phases, ref_equal = [], [], 0
            for i, j in segs:  # the same key, offsets and dials restarted at every segment
                mine, ph = encipher(plain[i:j], K, offs, start, variant)
                ref = community.encipher(plain[i:j], K, offs, start, space_skip=0, variant=variant)
                ref_equal += int(mine == ref)
                cipher += mine
                phases += ph
            recs = rune_records(plain, cipher, phases, segs)
            loc = audit(recs, local=True)
            glob = audit(recs, local=False)
            S, pos = running(offs), inverse(K)
            mism = sum(1 for s, wl, w, ph, p, c in recs
                       if (c - wl // M) % M != predicted_y(p, wl % M, ph, K, S, start, pos))
            row = dict(kind=kind, variant=variant, segments=len(segs), runes=len(recs), community_equal=ref_equal,
                       groups=loc["groups"], pairs=loc["pairs"], pairs_multi_segment=loc["pairs_multi_segment"],
                       within_bad=loc["within_bad"], pooled_bad=loc["pooled_bad"],
                       injective_bad=loc["injective_bad"], closed_form_mismatch=mism,
                       control_global_index_conflicts=glob["pooled_bad"])
            out.append(row)
            print("  %-7s %-7s segs %2d runes %5d | ours == community %d/%d | groups %3d pairs %5d "
                  "(in >=2 segments %4d) | within-segment conflicts %d, across-segment conflicts %d, "
                  "injective violations %d | closed form mismatches %d | control (global index) conflicts %d"
                  % (kind, variant, len(segs), len(recs), ref_equal, len(segs), loc["groups"], loc["pairs"],
                     loc["pairs_multi_segment"], loc["within_bad"], loc["pooled_bad"], loc["injective_bad"], mism,
                     glob["pooled_bad"]))
    return out


# ---------------------------------------------------------------- check 3: lane numbers from out/all.jsonl
def check3():
    print("== check 3: lane Y's numbers from out/all.jsonl ==")
    rows = [json.loads(line) for line in open(LANE_JSONL, encoding="utf-8")]
    print("  records %d: %s" % (len(rows), sorted({(r["kind"], r["seg"]) for r in rows})))
    nan = sum(1 for r in rows if not np.isfinite(r["s1_score"]))
    nan_aux = sum(1 for r in rows if not (np.isfinite(r["quad_full"]) and np.isfinite(r["ioc"])))
    err_lines = sum(1 for line in open(LANE_ERR, encoding="utf-8", errors="replace") if "RuntimeWarning" in line)
    print("  non-finite s1_score records: %d; non-finite quadgram or ioc records: %d; RuntimeWarning lines in "
          "run_all.log.err: %d" % (nan, nan_aux, err_lines))
    out = {}
    for seg in ("chapter", "page"):
        nulls = [r for r in rows if r["kind"] == "null" and r["seg"] == seg]
        real = [r for r in rows if r["kind"] == "real" and r["seg"] == seg]
        plants = [r for r in rows if r["kind"] == "plant" and r["seg"] == seg]
        assert len(nulls) == 50 and len(real) == 1 and len(plants) == 10, (seg, len(nulls), len(real), len(plants))
        assert sorted(r["idx"] for r in nulls) == list(range(50))
        s = [r["s1_score"] for r in nulls]
        mu, sd, sdp, mx = statistics.mean(s), statistics.stdev(s), statistics.pstdev(s), max(s)
        rs = real[0]["s1_score"]
        z = (rs - mu) / sd
        n_ge = sum(1 for x in s if x >= rs)
        ps = [r["s1_score"] for r in plants]
        det = sum(1 for x in ps if x > mx)
        dec = sum(1 for r in plants if r["agree"] >= 0.8)
        by_var = {v: (sum(1 for r in plants if r["variant"] == v and r["s1_score"] > mx),
                      sum(1 for r in plants if r["variant"] == v and r["agree"] >= 0.8),
                      sum(1 for r in plants if r["variant"] == v)) for v in ("advance", "hold")}
        out[seg] = dict(null_mean=mu, null_sd=sd, null_sd_pop=sdp, null_max=mx, real=rs, z=z, z_pop=(rs - mu) / sdp,
                        n_ge=n_ge, plants=len(plants), plant_min=min(ps), plant_max=max(ps), detected=det,
                        decrypted=dec, by_variant=by_var, weakest_plant_sd=(min(ps) - mu) / sd,
                        not_decrypted_agree=sorted(round(r["agree"], 3) for r in plants if r["agree"] < 0.8),
                        real_quad=real[0]["quad_full"], real_anchors=real[0]["anchors"],
                        real_agree=real[0].get("agree"))
        o = out[seg]
        print("  %-7s nulls mean %.4f sd %.4f (pop %.4f) max %.4f | real %.4f z %+.2f (pop %+.2f) | nulls >= real %d of 50"
              % (seg, mu, sd, sdp, mx, rs, z, o["z_pop"], n_ge))
        print("  %-7s plants %d, min %.3f, max %.3f, above null max %d, agree>=0.8 %d; by variant (above, decrypted, n): %s"
              % (seg, len(plants), min(ps), max(ps), det, dec, by_var))
        print("  %-7s weakest plant %.1f null sd above null mean; plants below 0.8 agree: %s; real quadgram %.3f, real anchors %d"
              % (seg, o["weakest_plant_sd"], o["not_decrypted_agree"], o["real_quad"], o["real_anchors"]))
    # the lane's null construction: increments permuted within each page keeps the doublets (run_laneY.py seeds 93000+i)
    import nulls  # toolbox; the null generator the lane calls
    U, C, _sha = lpdata.unsolved()

    def doublets(seq):
        return sum(1 for a, b in zip(seq, seq[1:]) if a == b)

    null_flat = []
    for i in range(50):
        pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(93000 + i))
        null_flat.append(doublets([x for p in pages for x in p]))
    print("  doublets (equal adjacent runes): LP2 stream %d, inside pages %d; 50 nulls (seeds 93000+i): min %d max %d, "
          "exactly 86 in %d" % (doublets(list(C)), sum(doublets(pg["idx"]) for pg in U), min(null_flat),
                                max(null_flat), sum(1 for d in null_flat if d == doublets(list(C)))))
    out["doublets"] = dict(lp2=doublets(list(C)), null_min=min(null_flat), null_max=max(null_flat))
    return out


# ---------------------------------------------------------------- check 4: replay of the lane's attack
def check4():
    """Check 4 runs in its own file (laneY_replay.py imports the lane's ylib); this file imports no lane code."""
    print("== check 4: replay the lane's attack on a fresh restart-per-page plant (runs/laneY_replay.py) ==")
    cmd = [sys.executable, "-I", "-X", "utf8", str(ROOT / "jobs" / "verify-lane" / "runs" / "laneY_replay.py")]
    cp = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT),
                        env=dict(os.environ, PYTHONUTF8="1"))
    for line in cp.stdout.splitlines():
        if not line.startswith("RESULT "):
            print("  " + line)
    if cp.returncode != 0:
        print(cp.stderr)
        raise SystemExit("check 4 replay failed")
    result_line = [l for l in cp.stdout.splitlines() if l.startswith("RESULT ")][-1]
    return json.loads(result_line[len("RESULT "):])



def main():
    below_normal()
    t0 = time.time()
    r1 = check1()
    r2 = check2()
    r3 = check3()
    r4 = check4()
    print("== summary ==")
    print("  check 1 chapters %d, pages %d, words %d, pages with inside chapter change %d"
          % (r1["chapters"], r1["pages"], r1["words"], r1["pages_with_inside_chapter_change"]))
    for seg in ("chapter", "page"):
        o = r3[seg]
        lane = LANE[seg]
        print("  check 3 %-7s null %.4f/%.4f/%.4f real %.4f z %+.2f n>=real %d | plants %d min %.3f det %d dec %d"
              % (seg, o["null_mean"], o["null_sd"], o["null_max"], o["real"], o["z"], o["n_ge"], o["plants"],
                 o["plant_min"], o["detected"], o["decrypted"]))
    print("  check 4 replay s1 %+.4f (above page null max: %s) frac %.4f"
          % (r4["s1_score"], r4["above_page_null_max"], r4["frac_equal"]))
    print("wall %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
