# ABOUTME: Verifies lane AA (agents/laneAA_chapter_keys): recomputes its tables from out/*.jsonl with fresh code, checks the
# ABOUTME: window layout, the 1.5T containment claim, the six misses, dead chains and the coincidence arithmetic.
"""python -I -X utf8 jobs/verify-lane/runs/laneAA_verify.py

Fresh code. It imports lp/lpdata.py only and does not import anything under agents/laneAA_chapter_keys: that lane's
out/*.jsonl, out/coincidence_probe.txt and RESULTS.md are read as data. Every line prints the lane's value next to ours.
"""
import hashlib
import json
import math
import os
import re
import statistics
import sys
from bisect import bisect_left, bisect_right
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
os.chdir(REPO)                                  # lpdata reads ./dl relative to the repository root
sys.path.insert(0, str(REPO / "lp"))
import lpdata  # noqa: E402

LANE = REPO / "agents" / "laneAA_chapter_keys"
OUT = LANE / "out"
SHA = "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
M = 29

# Numbers the RESULTS.md text states outside its tables (transcribed from the text, cited by section).
TEXT = {
    "fu_null_mean": 0.0208, "fu_null_sd": 0.0057, "fu_null_max": 0.0360,        # section 3, follow-up
    "fu_lp2": 0.0295, "fu_z": 1.53, "fu_as_high": 7, "fu_n_nulls": 100,
    "fu_shift": {-1000: (0.0174, -0.61), -500: (0.0249, 0.71), 500: (0.0203, -0.09), 1000: (0.0186, -0.38)},
    "w3_runes_recut": 4003,                                                      # section 3, follow-up text
    "chap14": 2474, "chap8": 1021, "chap15": 534,                                 # section 1
    "coinc_rate_lo": 0.051, "coinc_rate_hi": 0.057,                             # section 4
    "coinc_ch14_lo": 30, "coinc_ch14_hi": 50, "coinc_ch8_lo": 9, "coinc_ch8_hi": 21,
    "ln28fact": 68,
}


def lp2_words():
    """LP2 words from lp/lpdata.py: a word is a run of runes with one (page, word) id. Returns words and chapters."""
    pages = [p for p in lpdata.load() if p["page"] <= 54]
    idx = [x for p in pages for x in p["idx"]]
    assert hashlib.sha256(",".join(map(str, idx)).encode()).hexdigest() == SHA, "SHA pin"
    words, chap, prev = [], [], None
    for p in pages:
        for x, wid, ch in zip(p["idx"], p["word"], p["chap"]):
            key = (p["page"], wid)
            if key != prev:
                words.append([])
                chap.append(ch)
                prev = key
            words[-1].append(x)
    return words, chap


def window_layout(lens, T):
    """Lane AA's rule as we read it: starts every T/2 runes at the first word starting at or after that rune; a window
    holds the words that start before start + T; the last window is flush with the end of LP2."""
    starts = [0]
    for n in lens:
        starts.append(starts[-1] + n)
    total = starts[-1]
    wins, s = [], 0
    while True:
        if s + T >= total:
            wins.append((bisect_right(starts, total - T) - 1, len(lens)))
            return starts, wins
        wins.append((bisect_left(starts, s), bisect_left(starts, s + T)))
        s += T // 2


def containment(starts, wins, T):
    """Longest span needed, over every start x, to contain a whole window (spans of 1.5 T runes must always hold one)."""
    total = starts[-1]
    L = 3 * T // 2
    spans = [(starts[a], starts[b]) for a, b in wins]
    worst, at = 0, None
    for x in range(0, total - L + 1):
        ends = [e for s0, e in spans if s0 >= x]
        need = min(ends) - x if ends else math.inf
        if need > worst:
            worst, at = need, x
    return L, worst, at


def load(name):
    p = OUT / name
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def stats_of(nl, lp2):
    m, sd, mx = statistics.mean(nl), statistics.stdev(nl), max(nl)
    return {"n_null": len(nl), "null_mean": m, "null_sd": sd, "null_max": mx, "lp2": lp2,
            "z": (lp2 - m) / sd, "nulls_as_high": sum(x >= lp2 for x in nl)}


def summarise(rows, key):
    """Per group (chapter, size or window): the null and plant statistics, the way RESULTS.md's tables state them."""
    out = {}
    for k in sorted({r[key] for r in rows}):
        g = [r for r in rows if r[key] == k]
        nl = [r["s1_score"] for r in g if r["kind"] == "null"]
        pl = sorted((r for r in g if r["kind"] == "plant"), key=lambda r: r["idx"])
        real = [r["s1_score"] for r in g if r["kind"] == "real"]
        d = {"n_runes": g[0]["n_runes"], "n_plants": len(pl),
             "plants_above": sum(r["s1_score"] > max(nl) for r in pl),
             "decrypted": sum(r["agree"] >= 0.8 for r in pl),
             "plant_min": min(r["s1_score"] for r in pl), "plant_max": max(r["s1_score"] for r in pl),
             "plants": [(r["idx"], r["variant"], r["s1_score"], r["agree"]) for r in pl]}
        d.update(stats_of(nl, real[0]) if real else {"n_null": len(nl), "null_mean": statistics.mean(nl),
                                                      "null_sd": statistics.stdev(nl), "null_max": max(nl)})
        out[k] = d
    return out


def results_tables():
    """RESULTS.md's markdown tables as rows of cell strings (data, read only)."""
    lines = (LANE / "RESULTS.md").read_text(encoding="utf-8").splitlines()
    blocks, cur = [], []
    for ln in lines + [""]:
        if ln.startswith("|"):
            cur.append(ln)
        elif cur:
            blocks.append(cur)
            cur = []
    tabs = []
    for b in blocks:
        rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in b]
        tabs.append([r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r)])
    return tabs


def fnum(s):
    return float(s.replace(",", "").replace("+", "").strip())


def decimals(s):
    m = re.search(r"\.(\d+)", s)
    return len(m.group(1)) if m else 0


CHECKS = []   # (table, item, field, lane text, our text, ok)


def check(table, item, field, lane_txt, ours, ours_txt, ok):
    CHECKS.append((table, item, field, lane_txt, ours_txt, ok))
    return ok


def cmp_float(table, item, field, lane_txt, ours, tol_decimals=None):
    d = decimals(lane_txt) if tol_decimals is None else tol_decimals
    lane = fnum(lane_txt)
    ok = abs(lane - ours) <= 0.5 * 10 ** (-d) + 1e-9
    return check(table, item, field, lane_txt, ours, f"{ours:+.{d}f}" if field.endswith("z") else f"{ours:.{d}f}", ok)


def cmp_int(table, item, field, lane_txt, ours):
    return check(table, item, field, lane_txt, ours, str(ours), int(fnum(lane_txt)) == int(ours))


def first_ints(s):
    return [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", s)]


def tables_check(s1, sizes_pow, win):
    tabs = results_tables()
    probe_rows = next(t for t in tabs if t[0][0] == "chapter")[1:]
    power_rows = next(t for t in tabs if t[0][0] == "runes")[1:]
    win_tabs = [t[1:] for t in tabs if t[0][0] == "window"]
    # Section 1: probe (per chapter; LP2 not run)
    for r in probe_rows:
        ch = int(r[0])
        g = s1[ch]
        cmp_int("probe", f"chapter {ch}", "runes", r[1], g["n_runes"])
        mean_txt, mx_txt = [x.strip() for x in r[2].split("/")]
        cmp_float("probe", f"chapter {ch}", "null mean", mean_txt, g["null_mean"])
        cmp_float("probe", f"chapter {ch}", "null max", mx_txt, g["null_max"])
        plants_txt = re.findall(r"[+-]\d+\.\d+", r[3])
        # the lane lists its three plant scores in ascending order, not by plant index: compare sorted with sorted
        ours_sorted = sorted(p[2] for p in g["plants"])
        for i, pt in enumerate(plants_txt):
            cmp_float("probe", f"chapter {ch}", f"plant score #{i + 1} (ascending)", pt, ours_sorted[i])
        dm = re.search(r"\((\d+) of (\d+) decrypted\)", r[3])
        if dm:
            check("probe", f"chapter {ch}", "decrypted", f"{dm.group(1)} of {dm.group(2)}",
                  g["decrypted"], f"{g['decrypted']} of {g['n_plants']}",
                  int(dm.group(1)) == g["decrypted"] and int(dm.group(2)) == g["n_plants"])
    # Section 2: power curve by size
    for r in power_rows:
        n = int(r[0].replace(",", ""))
        g = next(v for v in sizes_pow.values() if v["n_runes"] == n)
        mean_txt, sd_txt, mx_txt = [x.strip() for x in r[1].split("/")]
        it = f"{n} runes"
        cmp_float("power", it, "null mean", mean_txt, g["null_mean"])
        cmp_float("power", it, "null sd", sd_txt, g["null_sd"])
        cmp_float("power", it, "null max", mx_txt, g["null_max"])
        lo, hi = [x.strip() for x in r[2].split("/")]
        cmp_float("power", it, "plant min", lo, g["plant_min"])
        cmp_float("power", it, "plant max", hi, g["plant_max"])
        ab = re.match(r"(\d+)/(\d+)", r[3])
        check("power", it, "above null max", r[3], g["plants_above"], f"{g['plants_above']}/{g['n_plants']}",
              int(ab.group(1)) == g["plants_above"] and int(ab.group(2)) == g["n_plants"])
        dd = re.match(r"(\d+)/(\d+)", r[4])
        check("power", it, "decrypted", r[4], g["decrypted"], f"{g['decrypted']}/{g['n_plants']}",
              int(dd.group(1)) == g["decrypted"] and int(dd.group(2)) == g["n_plants"])
    # Section 3: windows, T 4000 then T 6000
    for T, rows, g_all in ((4000, win_tabs[0], win[4000]), (6000, win_tabs[1], win[6000])):
        for r in rows:
            w = int(r[0])
            g = g_all[w]
            it = f"T {T} window {w}"
            mean_txt, sd_txt, mx_txt = [x.strip() for x in r[2].split("/")]
            cmp_float("windows", it, "null mean", mean_txt, g["null_mean"])
            cmp_float("windows", it, "null sd", sd_txt, g["null_sd"])
            cmp_float("windows", it, "null max", mx_txt, g["null_max"])
            ab = re.match(r"(\d+)/(\d+)", r[3])
            check("windows", it, "plants above max", r[3], g["plants_above"], f"{g['plants_above']}/{g['n_plants']}",
                  int(ab.group(1)) == g["plants_above"] and int(ab.group(2)) == g["n_plants"])
            lo, hi = [x.strip() for x in r[4].split("/")]
            cmp_float("windows", it, "plant min", lo, g["plant_min"])
            cmp_float("windows", it, "plant max", hi, g["plant_max"])
            cmp_float("windows", it, "LP2", r[5], g["lp2"])
            cmp_float("windows", it, "z", r[6], g["z"], tol_decimals=2)
            na = re.match(r"(\d+) of (\d+)", r[7])
            check("windows", it, "nulls as high", r[7], g["nulls_as_high"], f"{g['nulls_as_high']} of {g['n_null']}",
                  int(na.group(1)) == g["nulls_as_high"] and int(na.group(2)) == g["n_null"])


def main():
    code = run()
    return code


def run():
    print("## Setup")
    words, chap = lp2_words()
    lens = [len(w) for w in words]
    total = sum(lens)
    print(f"LP2 (pages 0-54): {total} runes in {len(words)} words; SHA pin asserted (ok)")

    # ---- Section 1 and 2 data
    probe = load("probe.jsonl")
    power = load("power.jsonl")
    win4 = load("windows_4000.jsonl")
    win6 = load("windows_6000.jsonl")
    fu = load("followup.jsonl")

    print("\n## Section 1: chapter sizes from lp/lpdata.py (own word split)")
    ch_runes = {}
    for w, c in zip(words, chap):
        ch_runes[c] = ch_runes.get(c, 0) + len(w)
    print("chapters:", len(ch_runes), "min", min(ch_runes.values()), "max", max(ch_runes.values()),
          "largest chapter", max(ch_runes, key=ch_runes.get))
    for ch, lane_n in ((14, TEXT["chap14"]), (8, TEXT["chap8"]), (15, TEXT["chap15"])):
        check("section 1", f"chapter {ch}", "runes", f"{lane_n:,}", ch_runes[ch], str(ch_runes[ch]),
              ch_runes[ch] == lane_n)
    s1 = summarise(probe, "chap")
    print("probe chapters:", {k: v["n_runes"] for k, v in s1.items()})

    print("\n## Section 2: power curve")
    sizes_pow = summarise(power, "size")
    print("sizes:", {k: v["n_runes"] for k, v in sizes_pow.items()})

    # ---- Section 3: windows, and the layout check
    print("\n## Section 3: window layout (own code, lpdata word split) vs jsonl and RESULTS.md")
    win = {}
    layout_ok = True
    results_text = (LANE / "RESULTS.md").read_text(encoding="utf-8")
    for T, fname in ((4000, "windows_4000.jsonl"), (6000, "windows_6000.jsonl")):
        starts, wins = window_layout(lens, T)
        rows = load(fname)
        win[T] = summarise(rows, "window")
        layout_ok = True
        print(f"T {T}: {len(wins)} windows")
        for w, (a, b) in enumerate(wins):
            off = (starts[a], starts[b])
            n_mine = starts[b] - starts[a]
            real = next(r for r in rows if r["kind"] == "real" and r["window"] == w)
            jw = tuple(real["words"])
            same = (jw == (a, b)) and real["n_runes"] == n_mine
            layout_ok &= same
            res_txt = re.search(rf"\| {w} \| ([\d,]+)-([\d,]+) \|", results_text[results_text.find(f"T = {T:,}"):])
            res_ok = res_txt is not None and (int(res_txt.group(1).replace(",", "")), int(res_txt.group(2).replace(",", ""))) == off
            layout_ok &= res_ok
            print(f"  T {T} window {w}: words [{a}, {b}) runes {off[0]}-{off[1]} ({n_mine} runes); "
                  f"jsonl words {jw} runes {real['n_runes']}; RESULTS offsets "
                  f"{res_txt.group(1)}-{res_txt.group(2)} {'match' if res_ok else 'DIFFER'}; "
                  f"{'match' if same else 'DIFFER'}")
        L, worst, at = containment(starts, wins, T)
        ok = worst <= L
        print(f"  containment: spans of {L} runes ({'1.5 T'}): worst need over all start runes = {worst} runes "
              f"(at start {at}); claim {'holds' if ok else 'FAILS'}")
        check("layout", f"T {T}", "1.5T span holds a whole window", f"{L} runes", worst, str(worst), ok)
        check("layout", f"T {T}", "window offsets and run counts", "table + jsonl", "own code",
              "match" if layout_ok else "DIFFER", layout_ok)

    print("\n## Tables: lane value next to ours")
    tables_check(s1, sizes_pow, win)

    # ---- Section 3 follow-up text claims
    print("\n## Section 3: window 3 follow-up (out/followup.jsonl)")
    nulls_fu = [r["s1_score"] for r in fu if r["kind"] == "null"]
    fu_real = {r["shift"]: r for r in fu if r["kind"] == "real"}
    fm, fsd, fmx = statistics.mean(nulls_fu), statistics.stdev(nulls_fu), max(nulls_fu)
    print(f"100 fresh nulls: mean {fm:.4f} sd {fsd:.4f} max {fmx:.4f} (n {len(nulls_fu)})")
    for lab, lane_v, ours in (("null mean", TEXT["fu_null_mean"], fm), ("null sd", TEXT["fu_null_sd"], fsd),
                              ("null max", TEXT["fu_null_max"], fmx)):
        check("follow-up", "window 3 margin", lab, f"{lane_v}", ours, f"{ours:.4f}",
              abs(lane_v - ours) <= 0.00005 + 1e-9)
    r0 = fu_real[0]
    print(f"shift 0 real: words {r0['words']} runes {r0['n_runes']} (table window 3 is 3,999 runes, words "
          f"{next(r['words'] for r in win4 if r['kind']=='real' and r['window']==3)})")
    check("follow-up", "shift 0 window", "runes", f"{TEXT['w3_runes_recut']}", r0["n_runes"], str(r0["n_runes"]),
          r0["n_runes"] == TEXT["w3_runes_recut"])
    z0 = (r0["s1_score"] - fm) / fsd
    as_high = sum(x >= r0["s1_score"] for x in nulls_fu)
    check("follow-up", "shift 0 (re-cut)", "LP2", f"{TEXT['fu_lp2']}", r0["s1_score"], f"{r0['s1_score']:.4f}",
          abs(TEXT["fu_lp2"] - r0["s1_score"]) <= 0.00005 + 1e-9)
    check("follow-up", "shift 0 (re-cut)", "z", f"{TEXT['fu_z']:+.2f}", z0, f"{z0:+.2f}",
          abs(TEXT["fu_z"] - z0) <= 0.005 + 1e-9)
    check("follow-up", "shift 0 (re-cut)", "nulls as high", f"{TEXT['fu_as_high']} of {TEXT['fu_n_nulls']}", as_high,
          f"{as_high} of {len(nulls_fu)}", as_high == TEXT["fu_as_high"])
    for sh, (lv, lz) in sorted(TEXT["fu_shift"].items()):
        r = fu_real[sh]
        zz = (r["s1_score"] - fm) / fsd
        check("follow-up", f"shift {sh:+d}", "LP2", f"{lv}", r["s1_score"], f"{r['s1_score']:.4f}",
              abs(lv - r["s1_score"]) <= 0.00005 + 1e-9)
        check("follow-up", f"shift {sh:+d}", "z", f"{lz:+.2f}", zz, f"{zz:+.2f}", abs(lz - zz) <= 0.005 + 1e-9)

    # ---- Dead chains and misses
    print("\n## Dead chains and the misses")
    all_rows = probe + power + win4 + win6 + fu
    dead = sum(r.get("dead_chains", 0) for r in all_rows)
    n_rec = len(all_rows)
    check("all files", "dead chains", "count", "0", dead, str(dead), dead == 0)
    print(f"records read: {n_rec}; sum of dead_chains: {dead}")
    misses = []
    for T, rows in ((4000, win4), (6000, win6)):
        for w, g in sorted(win[T].items()):
            for idx, variant, s, ag in g["plants"]:
                if not s > g["null_max"]:
                    misses.append((T, w, idx, variant, s, g["null_max"]))
    print(f"plants at or below their window's null max: {len(misses)}")
    for m in misses:
        print(f"  T {m[0]} window {m[1]} plant {m[2]} ({m[3]}): {m[4]:+.4f} vs null max {m[5]:.4f}")
    lane_misses = [(4000, 0, 3, "hold", 0.0034, 0.0270), (4000, 1, 1, "hold", -0.0006, 0.0365),
                   (4000, 1, 2, "advance", 0.0077, 0.0365), (4000, 2, 0, "advance", 0.0040, 0.0246),
                   (4000, 5, 1, "hold", 0.0301, 0.0363), (6000, 2, 3, "hold", 0.0243, 0.0324)]
    ours_set = {(m[0], m[1], m[2]) for m in misses}
    for T, w, idx, var, s, mx in lane_misses:
        ok = (T, w, idx) in ours_set and any(abs(m[4] - s) < 0.00005 for m in misses
                                              if (m[0], m[1], m[2]) == (T, w, idx))
        check("misses", f"T {T} window {w} plant {idx} ({var})", "score vs null max", f"{s:+.4f} vs {mx:.4f}",
              None, "found" if ok else "NOT FOUND", ok)
    print(f"lane's listed six found in our misses: {sum(c[5] for c in CHECKS if c[0]=='misses')} of 6; "
          f"our misses in total: {len(misses)}")
    hold_miss = sum(1 for m in misses if m[3] == "hold")
    print(f"hold plants among our misses: {hold_miss} of {len(misses)}")

    # ---- Section 4: coincidence probe arithmetic
    print("\n## Section 4: coincidence probe (out/coincidence_probe.txt)")
    txt = (OUT / "coincidence_probe.txt").read_text(encoding="utf-8").splitlines()
    q = 1 / 29
    ln28 = math.lgamma(29)                       # ln(28!) = lgamma(29)

    def kl(p):
        return p * math.log(p / q) + (1 - p) * math.log((1 - p) / (1 - q))

    plants, rows_n = [], []
    for ln in txt:
        mp = re.match(r"ch\s+(\d+) plant (\d+) (\w+)\s+pairs\s+(\d+)\s+true\s+(\d+)\s+climbed\s+(\d+)", ln)
        if mp:
            ch, idx, var, pairs, tru = int(mp.group(1)), int(mp.group(2)), mp.group(3), int(mp.group(4)), int(mp.group(5))
            plants.append((ch, idx, var, pairs, tru, tru / pairs, pairs * kl(tru / pairs)))
        mn = re.match(r"ch\s+(\d+) null\s+(\d+)\s+pairs\s+(\d+)\s+climbed\s+(\d+)", ln)
        if mn:
            rows_n.append(("null", int(mn.group(1)), int(mn.group(3)), int(mn.group(4))))
    for ch, idx, var, pairs, tru, rate, ev in plants:
        print(f"  ch {ch} plant {idx} {var:7s}: pairs {pairs} true {tru} rate {rate:.4f} "
              f"KL {kl(rate):.5f} nats/pair evidence {ev:.1f} nats")
    rates = [p[5] for p in plants]
    print(f"  true-rho rates over all six plants: {min(rates):.4f} to {max(rates):.4f}; "
          f"1/29 = {q:.4f}")
    r14 = [p[5] for p in plants if p[0] == 14]
    r8 = [p[5] for p in plants if p[0] == 8]
    print(f"  true-rho rates, chapter 14: {min(r14):.4f} to {max(r14):.4f}; chapter 8: {min(r8):.4f} to {max(r8):.4f}")
    ch14 = [p[6] for p in plants if p[0] == 14]
    ch8 = [p[6] for p in plants if p[0] == 8]
    print(f"  evidence ch 14: {min(ch14):.1f} to {max(ch14):.1f} nats; ch 8: {min(ch8):.1f} to {max(ch8):.1f} nats")
    print(f"  ln(28!) = {ln28:.2f} nats; log10(28!) = {ln28 / math.log(10):.3f}")
    print(f"  climbed null rates (ch 14): " + ", ".join(f"{r[3] / r[2]:.4f}" for r in rows_n if r[1] == 14))
    lp_rows = []
    for ln in txt:
        ml = re.match(r"ch\s+(\d+) LP2 kspace (\d+)\s+pairs\s+(\d+)\s+climbed\s+(\d+)", ln)
        if ml:
            lp_rows.append((int(ml.group(1)), int(ml.group(3)), int(ml.group(4))))
    for ch in (14, 8):
        cl_p = [pl_c for pl_c in (int(re.search(r"climbed\s+(\d+)", ln).group(1)) / int(re.search(r"pairs\s+(\d+)", ln).group(1))
                                  for ln in txt if re.match(rf"ch\s+{ch} plant", ln))]
        cl_n = [r[3] / r[2] for r in rows_n if r[1] == ch]
        cl_l = [c / p for cc, p, c in lp_rows if cc == ch]
        print(f"  climbed rates, chapter {ch}: plants {min(cl_p):.4f}-{max(cl_p):.4f}; nulls {min(cl_n):.4f}-{max(cl_n):.4f}; "
              f"LP2 (5 kspace) {min(cl_l):.4f}-{max(cl_l):.4f}")
    lo_rate = min(rates)
    check("section 4", "true-rho rate range", "low end", f"{TEXT['coinc_rate_lo']}", lo_rate, f"{lo_rate:.4f}",
          abs(lo_rate - TEXT["coinc_rate_lo"]) <= 0.0005 + 1e-9)
    check("section 4", "true-rho rate range", "high end", f"{TEXT['coinc_rate_hi']}", max(rates), f"{max(rates):.4f}",
          abs(max(rates) - TEXT["coinc_rate_hi"]) <= 0.0005 + 1e-9)
    check("section 4", "ch 14 evidence", "range nats", f"{TEXT['coinc_ch14_lo']} to {TEXT['coinc_ch14_hi']}",
          min(ch14), f"{min(ch14):.1f} to {max(ch14):.1f}",
          round(min(ch14)) == TEXT["coinc_ch14_lo"] and round(max(ch14)) == TEXT["coinc_ch14_hi"])
    check("section 4", "ch 8 evidence", "range nats", f"{TEXT['coinc_ch8_lo']} to {TEXT['coinc_ch8_hi']}",
          min(ch8), f"{min(ch8):.1f} to {max(ch8):.1f}",
          round(min(ch8)) == TEXT["coinc_ch8_lo"] and round(max(ch8)) == TEXT["coinc_ch8_hi"])
    check("section 4", "cost of 28! cycles", "nats", f"{TEXT['ln28fact']}", ln28, f"{ln28:.2f}",
          round(ln28) == TEXT["ln28fact"])

    # ---- Summary of checks
    print("\n## Checks (lane text or table value | ours | status)")
    n_ok = 0
    for table, item, field, lane_txt, ours_txt, ok in CHECKS:
        n_ok += bool(ok)
        print(f"{table} | {item} | {field} | lane {lane_txt} | ours {ours_txt} | {'reproduced' if ok else 'DIFFERS'}")
    print(f"\n{n_ok} of {len(CHECKS)} checks reproduced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
