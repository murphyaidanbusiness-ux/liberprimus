"""Oosterhof doublet-dodge walk with every permutation drawn from rng (the random family).

Walk rule (own port of experiments/doublet_dodge_walk.py::encipher and lane K's kcore.enc_walk, checked against
the community definition in agents/laneK_walk_search/RESULTS.md section 0):
  c_j = base_w[ g^(clock mod 5)[p_j] ]
  if c_j equals the previous cipher rune (across word boundaries too): clock += 1, recompute c_j once
  clock += 1 after every rune; the clock is GLOBAL and never resets at a word
  after each word: base_(w+1) = base_w o g^((clock-1) mod 5) o sigma,   with (a o b)[x] = a[b[x]]

Keys, all drawn from rng:
  g      an order-5 permutation with exactly 4 fixed points and five 5-cycles (the community's nominal form;
         the form a uniform draw from all order-5 permutations gives with probability 0.998, see the report)
  sigma  a uniform random permutation of 29 runes
  base0  a uniform random permutation of 29 runes
"""
import random

NAME = "walk_dodge_random: doublet-dodge walk, uniform order-5 g (4 fixed points), sigma and base0 from rng"
DESCRIPTION = "Free random keys of the walk's real form. Gates the walk family before any prime seeding."

M = 29
NFIXED = 4


def compose(a, b):
    return [a[b[x]] for x in range(M)]


def ppow(g, k):
    out = list(range(M))
    for _ in range(k):
        out = compose(g, out)
    return out


def order5_with_fixed(rng, nfixed):
    """Order-5 permutation: a uniform random set of nfixed fixed points, the rest in random 5-cycles."""
    pts = list(range(M))
    rng.shuffle(pts)
    movers = pts[nfixed:]
    assert len(movers) % 5 == 0
    g = list(range(M))
    for c in range(len(movers) // 5):
        cyc = movers[5 * c: 5 * c + 5]
        for t in range(5):
            g[cyc[t]] = cyc[(t + 1) % 5]
    return g


def encrypt(plain, words, rng):
    g = order5_with_fixed(rng, NFIXED)
    sigma = rng.sample(range(M), M)
    base = rng.sample(range(M), M)
    gp = [ppow(g, k) for k in range(5)]
    out = []
    clock = 0
    prev = None
    n = len(plain)
    i = 0
    while i < n:
        j = i
        while j < n and words[j] == words[i]:
            j += 1
        for k in range(i, j):
            p = plain[k]
            c = base[gp[clock % 5][p]]
            if c == prev:
                clock += 1
                c = base[gp[clock % 5][p]]
            out.append(c)
            prev = c
            clock += 1
        base = compose(base, compose(gp[(clock - 1) % 5], sigma))
        i = j
    return out
