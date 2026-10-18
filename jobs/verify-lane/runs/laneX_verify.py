# ABOUTME: Verify-lane script for lane X (agents/laneX_general_alphabet): our own encipher of the odometer dodge,
# ABOUTME: its anchor property, the increment-shuffle nulls, the lane's stage-1 numbers and an independent DM score.
"""Checks 1-5 of the lane X verification (2026-10-18). Check 6 (the lane's own pipeline replayed on a fresh plant)
runs as laneX_replay.py in a subprocess, so this file imports no lane code.

    PYTHONUTF8=1 python -I -X utf8 jobs/verify-lane/runs/laneX_verify.py      (from the repository root)
"""
import ctypes
import json
import math
import os
import random
import site
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
os.chdir(ROOT)  # toolbox/ and lp/ use paths relative to the repository root
sys.path.append(site.getusersitepackages())  # -I hides it; the community code needs numpy/scipy
COMMUNITY = ROOT / "dl" / "aldegonde_port"
sys.path[:0] = [str(COMMUNITY / "src"), str(COMMUNITY / "experiments")]
import doublet_phase_test as community  # noqa: E402  (cipher reference only, check 1)

sys.path[:0] = [str(ROOT / "toolbox"), str(ROOT / "lp")]
import lpdata  # noqa: E402
import nulls  # noqa: E402
import runes  # noqa: E402

assert Path(lpdata.__file__).resolve() == (ROOT / "lp" / "lpdata.py").resolve()
assert Path(nulls.__file__).resolve() == (ROOT / "toolbox" / "nulls.py").resolve()
assert Path(runes.__file__).resolve() == (ROOT / "toolbox" / "runes.py").resolve()

M = 29
PIN = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
LANE_OUT = ROOT / "agents" / "laneX_general_alphabet" / "out"
ENG_LONG = 12956


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
    """Five offsets summing to 0 mod 29 with exactly one zero."""
    while True:
        free = [rng.randrange(1, M) for _ in range(3)]
        last = (-sum(free)) % M
        if last:
            offs = free + [last, 0]
            rng.shuffle(offs)
            return offs


def encipher(words, K, offsets, a0, b0, variant):
    """Our own encipher of the odometer dodge.

    c = K[pos[p] + a_w + S[phase]] + b_w; a_w +1 per word, b_w +1 when a_w wraps; clock +1 per rune. On a would-be
    repeat (c equal to the previous cipher rune) re-emit at phase clock+1 with clock step 2 ("advance") or at phase
    clock-1 with step 0 ("hold"). Returns (cipher words, phase used per rune, number of would-be repeats).
    """
    assert variant in ("advance", "hold")
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b = a0, b0
    out, phases, prev, clock, dodges = [], [], None, 0, 0
    for word in words:
        cw = []
        for p in word:
            ph = clock % 5
            c = (K[(pos[p] + a + S[ph]) % M] + b) % M
            step = 1
            if c == prev:
                dodges += 1
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
    return out, phases, dodges


def english_words(n, skip_chars):
    """n runes of English (toolbox/runes.english_stream from char skip_chars), split into words by its word ids."""
    R, W = runes.english_stream(n, skip_chars=skip_chars)
    assert len(R) == n, (len(R), n)
    words, cur, last = [], [], None
    for x, w in zip(R, W):
        if last is not None and w != last:
            words.append(cur)
            cur = []
        cur.append(x)
        last = w
    words.append(cur)
    assert sum(map(len, words)) == n
    return words


def lp2_words():
    """LP2 pages 0-54 as words (a run of runes with one page and word id), plus the flat stream and page lengths."""
    U, C, sha = lpdata.unsolved()
    assert sha == PIN
    words, cur, last = [], [], None
    for page in U:
        for x, wid in zip(page["idx"], page["word"]):
            key = (page["page"], wid)
            if last is not None and key != last:
                words.append(cur)
                cur = []
            cur.append(x)
            last = key
    words.append(cur)
    assert [x for w in words for x in w] == list(C)
    return words, list(C), [len(p["idx"]) for p in U]


def words_from_flat(flat, lens):
    """Cut a flat rune stream into words of the given lengths (the LP2 word layout)."""
    it = iter(flat)
    return [[next(it) for _ in range(L)] for L in lens]


def flatten(seqs):
    return [x for s in seqs for x in s]


def doublet_positions(seq):
    return [i for i in range(1, len(seq)) if seq[i] == seq[i - 1]]


def group_check(words, cipher, phases):
    """For every group (word index mod 29, phase used) the map plaintext rune -> (c - floor(w/29)) mod 29."""
    groups, i = {}, 0
    for wi, (pw, cw) in enumerate(zip(words, cipher)):
        for p, c in zip(pw, cw):
            y = (c - wi // 29) % M
            groups.setdefault((wi % 29, phases[i]), {}).setdefault(p, set()).add(y)
            i += 1
    single = all(len(ys) == 1 for g in groups.values() for ys in g.values())
    injective = single and all(len({next(iter(ys)) for ys in g.values()}) == len(g) for g in groups.values())
    return len(groups), single, injective


def dm_per_rune(counts):
    """Dirichlet-multinomial (alpha 1 per symbol) log marginal likelihood of hard counts, minus the uniform
    model's N log(1/29), per rune. counts: dict group -> list of 29 symbol counts."""
    ll, N = 0.0, 0
    for cnt in counts.values():
        n = sum(cnt)
        N += n
        ll += math.lgamma(M) - math.lgamma(n + M) + sum(math.lgamma(c + 1) for c in cnt)
    return (ll + N * math.log(M)) / N


def grouped_counts(rows, group_of):
    """rows: (word index, global rune index, cipher rune). Symbol y = (c - floor(w/29)) mod 29."""
    counts = {}
    for wi, g, c in rows:
        counts.setdefault(group_of(wi, g), [0] * M)[(c - wi // 29) % M] += 1
    return counts


def rows_of(cipher):
    rows, g = [], 0
    for wi, cw in enumerate(cipher):
        for c in cw:
            rows.append((wi, g, c))
            g += 1
    return rows


def check1(report):
    print("== CHECK 1: cipher property (our encipher vs community encipher; group substitution)")
    for variant in ("advance", "hold"):
        for j in range(3):
            rng = random.Random(41000 + 10 * (variant == "hold") + j)
            words = english_words(ENG_LONG, 940000 + 20000 * j)
            K = rng.sample(range(M), M)
            offs = one_zero_schedule(rng)
            a0, b0 = rng.randrange(M), rng.randrange(M)
            mine, phases, dodges = encipher(words, K, offs, a0, b0, variant)
            theirs = community.encipher(words, K, offs, (a0, b0), 0, variant)
            same = mine == theirs
            n_groups, single, inj = group_check(words, mine, phases)
            line = (f"  {variant:<7} plant {j}: equal to community encipher {same}; dodges {dodges}; "
                    f"groups {n_groups}; map single-valued in every group {single}; injective {inj}")
            print(line)
            report["c1"].append((variant, j, same, dodges, n_groups, single, inj))


def check2(report):
    print("== CHECK 2: anchor property (every doublet's second rune at one phase)")
    for variant in ("advance", "hold"):
        for j in range(5):
            rng = random.Random(42000 + 10 * (variant == "hold") + j)
            words = english_words(ENG_LONG, 1000000 + 20000 * (5 * (variant == "hold") + j))
            K = rng.sample(range(M), M)
            offs = one_zero_schedule(rng)
            a0, b0 = rng.randrange(M), rng.randrange(M)
            cipher, phases, dodges = encipher(words, K, offs, a0, b0, variant)
            flat = flatten(cipher)
            dp = doublet_positions(flat)
            phs = sorted({phases[i] for i in dp})
            z = offs.index(0)
            expect = z if variant == "advance" else (z - 1) % 5
            ok = phs == [expect]
            print(f"  {variant:<7} plant {j}: doublets {len(dp)}; phases used at second runes {phs}; "
                  f"predicted {expect} (zero offset at index {z}); one phase {ok}")
            report["c2"].append((variant, j, len(dp), phs, expect, ok))


def check3(report, lp_pages, lp_lens, lp_stream):
    print("== CHECK 3: increment-shuffle null (toolbox/nulls.shuffle_increments, seeds 91000+i)")
    orig_cat = len(doublet_positions(flatten(lp_pages)))
    orig_within = sum(len(doublet_positions(p)) for p in lp_pages)
    print(f"  LP2 itself: doublets across the stream {orig_cat}, within pages {orig_within}; "
          f"page lengths {len(lp_lens)} pages")
    nulls_out = []
    for i in range(5):
        pages = nulls.shuffle_increments(nulls.lp_pages(), random.Random(91000 + i))
        lens_ok = [len(p) for p in pages] == [len(p) for p in lp_pages]
        cat = len(doublet_positions(flatten(pages)))
        within = sum(len(doublet_positions(p)) for p in pages)
        print(f"  null {i}: doublets across the stream {cat}, within pages {within}; every page length kept {lens_ok}")
        report["c3"].append((i, cat, within, lens_ok))
        nulls_out.append(flatten(pages))
    lane = {}
    for line in (LANE_OUT / "all.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["kind"] == "null":
            lane[r["idx"]] = r["anchors"]
    print(f"  lane's own null records, anchors (doublets) for seeds 0-4: {[lane[i] for i in range(5)]}; "
          f"all 20 in all.jsonl = 86: {all(v == 86 for v in lane.values())}")
    return nulls_out


def check4(report):
    print("== CHECK 4: lane X stage-1 numbers from out/all.jsonl and out/null2.jsonl")
    recs = []
    for name in ("all.jsonl", "null2.jsonl"):
        for line in (LANE_OUT / name).read_text(encoding="utf-8").splitlines():
            if line.strip():
                recs.append(json.loads(line))
    nul = [r for r in recs if r["kind"] == "null"]
    real = [r for r in recs if r["kind"] == "real"][0]
    plants = [r for r in recs if r["kind"] == "plant"]
    s = [r["s1_score"] for r in nul]
    nan_count = sum(1 for r in recs if isinstance(r["s1_score"], float) and math.isnan(r["s1_score"]))
    mean, sd0, sd1, mx = statistics.fmean(s), statistics.pstdev(s), statistics.stdev(s), max(s)
    rs = real["s1_score"]
    n_ge = sum(1 for x in s if x >= rs)
    full = [r for r in plants if r["n"] == ENG_LONG]
    full_min = min(r["s1_score"] for r in full)
    full_max = max(r["s1_score"] for r in full)
    above = sum(1 for r in full if r["s1_score"] > mx)
    print(f"  records: {len(recs)} (nulls {len(nul)}, plants {len(plants)}, real 1); NaN scores {nan_count}")
    print(f"  null s1: mean {mean:.4f}, sd (ddof 1) {sd1:.4f}, sd (ddof 0) {sd0:.4f}, max {mx:.4f}, min {min(s):.4f}")
    print(f"  real s1 {rs:.4f}; z (ddof 1) {(rs - mean) / sd1:+.2f}; z (ddof 0) {(rs - mean) / sd0:+.2f}")
    print(f"  nulls at or above real: {n_ge} of {len(s)}; empirical p (n_ge+1)/(N+1) {(n_ge + 1) / (len(s) + 1):.3f}")
    print(f"  full-length plants (n={ENG_LONG}): {len(full)}; s1 min {full_min:.4f}, max {full_max:.4f}; "
          f"above null max {above}/{len(full)}")
    cats = [
        ("12,956, skip 0, advance", [r for r in full if r["kspace_true"] == 0 and r["variant"] == "advance"]),
        ("12,956, skip 0, hold", [r for r in full if r["kspace_true"] == 0 and r["variant"] == "hold"]),
        ("12,956, skips 1-4", [r for r in full if r["kspace_true"] != 0]),
        ("6,000 runes", [r for r in plants if r["n"] == 6000]),
        ("3,000 runes", [r for r in plants if r["n"] == 3000]),
    ]
    rows4 = []
    for name, rs_ in cats:
        v = sorted(r["s1_score"] for r in rs_)
        det = sum(1 for x in v if x > mx)
        rec_ = sum(1 for r in rs_ if r.get("agree", 0) >= 0.8)
        pa = statistics.median(r["phase_acc"] for r in rs_)
        print(f"  {name:<26} n {len(rs_):>2}  s1 min/median/max {v[0]:.3f} / {statistics.median(v):.3f} / {v[-1]:.3f}"
              f"  detected {det}/{len(rs_)}  recovered(>=80%) {rec_}/{len(rs_)}  phase acc median {pa:.3f}")
        rows4.append((name, len(rs_), v[0], statistics.median(v), v[-1], det, rec_, pa))
    skip0 = [r for r in full if r["kspace_true"] == 0]
    print(f"  skip-0 full plants with >=80% of runes decrypted: {sum(1 for r in skip0 if r['agree'] >= 0.8)}/{len(skip0)}")
    misses = [(r["idx"], r["variant"], round(r["agree"], 3)) for r in skip0 if r["agree"] < 0.8]
    p3 = [r for r in plants if r["idx"] == 3][0]
    print(f"  skip-0 misses (idx, variant, runes right): {misses}; plant 3 (hold) runes right {p3['agree']:.4f}")
    lay = [json.loads(x) for x in (LANE_OUT / "layout_plants.jsonl").read_text(encoding='utf-8').splitlines() if x.strip()]
    ls = [r["s1_score"] for r in lay]
    print(f"  LP2-layout plants: n {len(lay)}, s1 min/median/max {min(ls):.3f} / {statistics.median(ls):.3f} / "
          f"{max(ls):.3f}, recovered {sum(1 for r in lay if r['agree'] >= 0.8)}/{len(lay)}")
    qn = [r["quad_full"] for r in nul]
    print(f"  stage-2 quadgram: nulls mean {statistics.fmean(qn):.3f}, sd {statistics.stdev(qn):.4f}, "
          f"max {max(qn):.3f}; real {real['quad_full']:.3f}")
    print(f"  real: schedule-S {real['S']}, space skip {real['kspace']}, s1 by skip "
          f"{ {k: round(v, 3) for k, v in sorted(real['s1_by_kspace'].items(), key=lambda kv: int(kv[0]))} }")
    report["c4"] = dict(n_null=len(s), mean=mean, sd1=sd1, sd0=sd0, mx=mx, real=rs, z1=(rs - mean) / sd1,
                        z0=(rs - mean) / sd0, n_ge=n_ge, p=(n_ge + 1) / (len(s) + 1), full_min=full_min,
                        full_max=full_max, above=above, n_full=len(full), cats=rows4, nan=nan_count,
                        qmean=statistics.fmean(qn), qsd=statistics.stdev(qn), qmax=max(qn),
                        qreal=real["quad_full"], real_S=real["S"], real_kspace=real["kspace"],
                        skip0_rec=sum(1 for r in skip0 if r["agree"] >= 0.8), skip0_n=len(skip0))


def check5(report, lp_words_, lp_stream, null_streams, lp_lens):
    print("== CHECK 5: independent DM score (alpha 1; per rune, minus N log(1/29))")
    # the true grouping on a fresh plant (English at skip 900000), advance and hold
    for variant in ("advance", "hold"):
        rng = random.Random(55000 + (variant == "hold"))
        words = english_words(ENG_LONG, 900000)
        K = rng.sample(range(M), M)
        offs = one_zero_schedule(rng)
        a0, b0 = rng.randrange(M), rng.randrange(M)
        cipher, phases, dodges = encipher(words, K, offs, a0, b0, variant)
        rows = rows_of(cipher)
        true_score = dm_per_rune(grouped_counts(rows, lambda wi, g: (wi % 29, phases[g])))
        zero_score = dm_per_rune(grouped_counts(rows, lambda wi, g: (wi % 29, g % 5)))
        print(f"  plant {variant:<7} (English skip 900000, {ENG_LONG} runes): true grouping (word mod 29 x true phase) "
              f"{true_score:+.4f}; zero-drift grouping (word mod 29 x rune index mod 5) {zero_score:+.4f}")
        report["c5_plant"].append((variant, true_score, zero_score))
    # LP2 with the zero-drift grouping, and the same statistic on the five increment-shuffle nulls
    lp_rows = rows_of(words_from_flat(lp_stream, lp_lens))
    lp_zero = dm_per_rune(grouped_counts(lp_rows, lambda wi, g: (wi % 29, g % 5)))
    null_zero = []
    for flat in null_streams:
        rws = rows_of(words_from_flat(flat, lp_lens))
        null_zero.append(dm_per_rune(grouped_counts(rws, lambda wi, g: (wi % 29, g % 5))))
    print(f"  LP2 zero-drift grouping {lp_zero:+.4f}; the five nulls {[round(x, 4) for x in null_zero]} "
          f"(mean {statistics.fmean(null_zero):+.4f}, sd {statistics.stdev(null_zero):.4f})")
    # the statistic's floor: uniform i.i.d. runes on the same word layout, zero-drift grouping (three streams)
    urng = random.Random(5599)
    unif = []
    for _ in range(3):
        flat_u = [urng.randrange(M) for _ in range(ENG_LONG)]
        unif.append(dm_per_rune(grouped_counts(rows_of(words_from_flat(flat_u, lp_lens)),
                                               lambda wi, g: (wi % 29, g % 5))))
    print(f"  uniform i.i.d. runes, same layout, zero-drift grouping: {[round(x, 4) for x in unif]} "
          f"(mean {statistics.fmean(unif):+.4f})")
    report["c5_lp"] = (lp_zero, null_zero, unif)


def main():
    below_normal()
    report = {"c1": [], "c2": [], "c3": [], "c5_plant": []}
    check1(report)
    check2(report)
    lp_words_, lp_stream, lp_lens = lp2_words()
    lp_pages = nulls.lp_pages()
    null_streams = check3(report, lp_pages, lp_lens, lp_stream)
    check4(report)
    check5(report, lp_words_, lp_stream, null_streams, lp_lens)
    print("== CHECK 6: replay of the lane's pipeline on a fresh plant (subprocess, laneX_replay.py)")
    env = dict(os.environ, PYTHONUTF8="1")
    proc = subprocess.run([sys.executable, "-I", "-X", "utf8", str(Path(__file__).with_name("laneX_replay.py"))],
                          cwd=str(ROOT), env=env, capture_output=True, text=True, encoding="utf-8")
    print(proc.stdout.rstrip())
    if proc.returncode != 0:
        print("  replay FAILED:\n" + proc.stderr[-2000:])
    report["c6_rc"] = proc.returncode
    # machine-readable summary, printed last
    print("== SUMMARY json")
    print(json.dumps({k: v for k, v in report.items() if k != "c4"}, default=str)[:4000])
    print(json.dumps(report["c4"], default=str))


if __name__ == "__main__":
    main()
