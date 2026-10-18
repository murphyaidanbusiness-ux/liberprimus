# ABOUTME: Orchestrator's independent check of lane W: recounts measure.json, proves the two relabel symmetries
# ABOUTME: on fresh plants, and decodes the clock variant exactly with a skip-tracking decoder written from scratch.
"""Independent check of lane W's headline numbers (verify-lane style, fresh code, fresh plaintext).

    python -I -X utf8 agents/laneW_clock_dodge/orch_check.py

A  recount out/measure.json: rank 1 with ties as wins, odometer with the dials category dropped, median z.
B  odometer: shifting the start outer dial b by d adds d to every cipher rune (so those keys are equivalents).
C  clock: base_0 is an outer relabel: enciphering with base_0 = P gives P[c] of the identity-base_0 cipher, rune by rune.
D  clock: a left-to-right decoder that tracks skips, given the true key and NO phase information, recovers the
   plaintext; counts skips and forks (runes where both a skip and a no-skip reading are consistent).
Plaintext: Moby-Dick through toolbox/runes.english_stream (not lane W's matched register), new seeds.
"""
import json
import random
import site
import statistics as st
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PORT = REPO / "dl" / "aldegonde_port"
sys.path[:0] = [str(REPO / "toolbox"), str(PORT / "src"), str(PORT / "experiments")]
sys.path.append(site.getusersitepackages())

import runes as rn  # noqa: E402
import doublet_phase_test as odo  # noqa: E402
import quagmire_dodge as qd  # noqa: E402
from pure_quagmire_restart import schedule as odo_schedule  # noqa: E402
from quagmire_runner import conj_shift  # noqa: E402

M = 29


def inverse(p):
    q = [0] * M
    for i, x in enumerate(p):
        q[x] = i
    return q


def compose(a, b):
    return [a[b[x]] for x in range(M)]


def words_from(n_runes, offset):
    R, W = rn.english_stream(offset + n_runes + 100)
    R, W = R[offset:offset + n_runes], W[offset:offset + n_runes]
    out, cur, last = [], [], W[0]
    for r, w in zip(R, W):
        if w != last and cur:
            out.append(cur)
            cur = []
        cur.append(r)
        last = w
    out.append(cur)
    return out


def check_a():
    d = json.loads((HERE / "out" / "measure.json").read_text(encoding="utf-8"))
    for kind in ("odo", "clock", "literal"):
        rs = [r for r in d["results"] if r["kind"] == kind]
        strict = sum(r["true"] > max(r["wrong_scores"]) for r in rs)
        ties_win = sum(r["true"] >= max(r["wrong_scores"]) for r in rs)
        print("A %-7s n %d  strict %2d  ties-as-wins %2d  median z %+.2f" % (
            kind, len(rs), strict, ties_win, st.median(r["z"] for r in rs)))
        if kind == "odo":
            # wrong keys cycle alphabet, schedule, dials, everything (j % 4); drop the dials ones
            nodial = sum(r["true"] > max(s for j, s in enumerate(r["wrong_scores"]) if j % 4 != 2) for r in rs)
            ties = [sum(abs(s - r["true"]) < 1e-12 for s in r["wrong_scores"]) for r in rs]
            print("A odo     dials dropped, strict %2d;  exact ties per plant median %.1f (expected 500/29 = 17.2)" % (
                nodial, st.median(ties)))


def check_b(rng):
    ok = 0
    for t in range(5):
        K = rng.sample(range(M), M)
        offs = odo_schedule(rng)
        a, b, dd = rng.randrange(M), rng.randrange(M), rng.randrange(1, M)
        plain = words_from(1800, 3000 * t)
        c1 = [x for w in odo.encipher(plain, K, offs, (a, b), 0, "advance") for x in w]
        c2 = [x for w in odo.encipher(plain, K, offs, (a, (b + dd) % M), 0, "advance") for x in w]
        ok += all((x + dd) % M == y for x, y in zip(c1, c2))
    print("B odometer outer-dial shift is a constant relabel on %d/5 plants" % ok)


def clock_key(rng):
    K = rng.sample(range(M), M)
    offs = qd.schedule(rng, zeros=1)
    alpha = qd.alphabets(K, offs)
    sigma = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
    return alpha, sigma, rng.sample(range(M), M)


def check_c(rng):
    ok = 0
    ident = list(range(M))
    for t in range(5):
        alpha, sigma, P = clock_key(rng)
        plain = words_from(1800, 5000 + 3000 * t)
        c_id = [x for w in qd.encipher(plain, ident, alpha, sigma) for x in w]
        c_p = [x for w in qd.encipher(plain, P, alpha, sigma) for x in w]
        ok += all(P[x] == y for x, y in zip(c_id, c_p))
    print("C clock base_0 is an exact outer relabel on %d/5 plants" % ok)


def decode(cipher_words, alpha, sigma, base0, truth=None):
    """Skip-tracking decode. At a fork take the truth if given, else the no-skip reading."""
    ainv = [inverse(a) for a in alpha]
    base, clock, prev = list(base0), 0, None
    out, skips, forks = [], 0, 0
    flat_truth = iter([x for w in truth for x in w]) if truth else None
    for word in cipher_words:
        binv = inverse(base)
        for c in word:
            x = binv[c]
            pa = ainv[clock % 5][x]
            pb = ainv[(clock + 1) % 5][x]
            ok_a = c != prev
            ok_b = base[alpha[clock % 5][pb]] == prev
            tp = next(flat_truth) if flat_truth else None
            if ok_a and ok_b:
                forks += 1
                use_b = (tp == pb and tp != pa) if truth else False
            else:
                use_b = ok_b
            if use_b:
                clock += 1
                skips += 1
                out.append(pb)
            else:
                out.append(pa)
            prev = c
            clock += 1
        base = compose(base, compose(alpha[(clock - 1) % 5], sigma))
    return out, skips, forks


def check_d(rng, n=20):
    exact_oracle = exact_plain = 0
    skips, forks, acc = [], [], []
    for t in range(n):
        alpha, sigma, base0 = clock_key(rng)
        plain = words_from(1802, 20000 + 2500 * t)
        flat = [x for w in plain for x in w]
        cw = qd.encipher(plain, base0, alpha, sigma)
        dec_o, s, f = decode(cw, alpha, sigma, base0, truth=plain)
        dec_p, _s, _f = decode(cw, alpha, sigma, base0)
        exact_oracle += dec_o == flat
        exact_plain += dec_p == flat
        skips.append(s)
        forks.append(f)
        acc.append(sum(a == b for a, b in zip(dec_p, flat)) / len(flat))
    print("D clock, true key, no phase info: exact decode %d/%d with forks resolved by truth, %d/%d with the "
          "no-skip rule (median accuracy %.3f)" % (exact_oracle, n, exact_plain, n, st.median(acc)))
    print("D skips per ~1,802 runes: median %.0f (range %d-%d); forks: median %.0f (range %d-%d)" % (
        st.median(skips), min(skips), max(skips), st.median(forks), min(forks), max(forks)))


def main():
    rng = random.Random(330117)
    check_a()
    check_b(rng)
    check_c(rng)
    check_d(rng)


if __name__ == "__main__":
    main()
