"""Logged checks behind RESULTS.md (run from anywhere; writes logs/checks.txt via stdout redirection).
  1. Inverse self-test: random plaintexts of length 60 under random keys, decoder at W=4096 (no pruning at this length):
     every decoded path re-encrypts to the cipher, and the decoder's mean score is >= the true path's mean.
  2. The full-length survivor (prime k0 9144, key index 19144): decode over the whole of LP2 at W=512 and W=4096,
     with IoC and quadgram of the decode and a random-runes reference.
  3. Doublets in the LP2 300-rune window."""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
import tdec, runes, score, lpdata
REPO = tdec.REPO
os.chdir(REPO)
sim = tdec.load_sim()
M = 29

print("== 1. inverse self-test (W=4096, n=60, 40 random plaintexts)")
dec = tdec.Decoder(W=4096)
rng = random.Random(3)
bad_reenc = 0
below = 0
exact = 0
for trial in range(40):
    kk = rng.randrange(20000)
    kind, k0 = tdec.key_of(kk)
    n = 60
    plain = [rng.randrange(M) for _ in range(n)]
    words, w = [], 0
    while len(words) < n:
        L = rng.randrange(1, 5)
        words += [w] * L
        w += 1
    words = words[:n]
    g, sg, b0 = sim.keys_from(kind, k0)
    c = sim.walk(plain, words, g, sg, b0)
    a, mm, sc, nw, path = dec.decode(c, words, kk, track=True)
    p = list(path)
    if sim.walk(p, words, g, sg, b0) != c:
        bad_reenc += 1
    t_sc = 0.0
    t_nw = 0
    t = 0
    for q in plain:
        t_sc += dec.ADD[t, q]
        t_nw += dec.NW[t, q]
        t = dec.TNEW[t, q]
    if t_nw and mm < t_sc / t_nw - 1e-9:
        below += 1
    exact += (p == plain)
print("decoded path re-encrypts to the cipher: %d failures of 40" % bad_reenc)
print("decoder mean below the true path's mean: %d of 40 (must be 0)" % below)
print("decoded path equals the planted plaintext: %d of 40 (not a pass criterion: the walk admits alternative paths)"
      % exact)

print("\n== 2. full-length survivor, key index 19144 (prime, k0 9144)")
U, C, sha = lpdata.unsolved()
words = [w for p in U for w in p["word"]]
assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
rr = np.random.default_rng(1)
ref = [int(x) for x in rr.integers(0, M, 12956)]
print("random-runes reference (12956 runes, numpy seed 1): ioc %.4f quadgram %.4f" % (score.ioc(ref), score.quadgram(ref)))
for W in (512, 4096):
    d = tdec.Decoder(W=W)
    a, mm, sc, nw, path = d.decode(list(C), words, 19144, track=True)
    p = list(path)
    print("W=%d: decodes %d of 12956 runes; mean %.4f; ioc %.4f; quadgram %.4f; first 120 runes: %s"
          % (W, a, mm, score.ioc(p) if len(p) > 1 else 0.0, score.quadgram(p), runes.tr(p[:120])))

print("\n== 3. LP2 300-rune window")
win = list(C[:300])
dl = [i for i in range(1, 300) if win[i] == win[i - 1]]
print("doublets in the first 300 runes: %d, at positions %s" % (len(dl), dl))
print("doublets in all 12,956 runes: %d" % sum(1 for i in range(1, len(C)) if C[i] == C[i - 1]))
