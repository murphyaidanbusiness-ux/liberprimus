# ABOUTME: Lane AA summary: per chapter (probe), per size (power curve) and per window, the null mean, sd and max, the
# ABOUTME: plants above the null max and decrypted, and LP2's score and z; prints the tables RESULTS.md quotes.
"""python -I -X utf8 agents/laneAA_chapter_keys/summarize.py"""
import json
import statistics as st
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"


def load(name):
    p = OUT / name
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()] if p.exists() else []


def table(rows, key, label):
    print("\n## %s" % label)
    print("| %s | runes | nulls | null mean | sd | max | plants above max | decrypted (>= 80%%) | plant min / max | LP2 | z | nulls >= LP2 |" % key)
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in sorted({r[key] for r in rows}):
        nl = [r["s1_score"] for r in rows if r[key] == k and r["kind"] == "null"]
        pl = [r for r in rows if r[key] == k and r["kind"] == "plant"]
        re = [r["s1_score"] for r in rows if r[key] == k and r["kind"] == "real"]
        n = [r["n_runes"] for r in rows if r[key] == k][0]
        m, sd, mx = st.mean(nl), st.stdev(nl), max(nl)
        ps = [r["s1_score"] for r in pl]
        real = ("%.4f" % re[0], "%+.2f" % ((re[0] - m) / sd), "%d of %d" % (sum(x >= re[0] for x in nl), len(nl))) \
            if re else ("-", "-", "-")
        print("| %s | %d | %d | %.4f | %.4f | %.4f | %d/%d | %d/%d | %.3f / %.3f | %s | %s | %s |" % (
            k, n, len(nl), m, sd, mx, sum(x > mx for x in ps), len(ps), sum(r["agree"] >= 0.8 for r in pl), len(pl),
            min(ps), max(ps), *real))
    dead = sum(r["dead_chains"] for r in rows if "dead_chains" in r)
    print("dead chains: %d" % dead)


if __name__ == "__main__":
    table(load("probe.jsonl"), "chap", "Probe: one chapter, its own key")
    table(load("power.jsonl"), "size", "Power curve: prefixes of LP2's layout")
    for T in (4000, 6000):
        rows = load("windows_%d.jsonl" % T)
        if rows:
            table(rows, "window", "Windows of %d runes, stride %d" % (T, T // 2))
