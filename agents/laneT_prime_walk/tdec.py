"""Lane T: beam decoder that inverts the walk_dodge_prime simulator (jobs/hypothesis-gate/runs/walk_dodge_prime_cipher.py).

Walk (simulator, exact):  clock starts at 0, base = base0.  For each rune p in a word block:
    cA = base[gp[clock%5][p]]; if cA == prev: clock += 1 (dodge); c = base[gp[clock%5][p]]; emit c; prev = c; clock += 1.
  After each word block: base = base o gp[(clock-1)%5] o sigma   (i.e. newbase[x] = base[gp[cb][sigma[x]]], cb = (clock-1)%5).

Inverse, per observed rune c with state (e = clock%5, Binv = inverse of base, prev = previous observed rune):
  A (no dodge), valid iff prev is absent or c != prev:  p = GI[e][Binv[c]],          e' = e+1
  B (dodge),    valid iff prev is present and GP[(e+1)%5][pB] == Binv[c], where pB = GI[e][Binv[prev]];  p = pB, e' = e+2
  GI[e] = g^(-e) (inverse of gp[e]), GP[k] = g^k.  At the end of each word block: cb = (e'-1)%5 = (e'+4)%5 and
  newBinv[y] = MINV[cb][Binv[y]], where MINV[cb] is the inverse of x -> gp[cb][sigma[x]].

Only Binv is carried (the B-check uses Binv[c] too). The decoder is a beam over states (score, e, tail, Binv) ranked by the
cumulative English quadgram log-score (toolbox/score.py table). Every key decodes some plaintext; the beam keeps the
best W paths. Exact up to the beam: with W large enough that no pruning happens, the true path is the exhaustive answer.
"""
import importlib.util
import os
import sys

import numpy as np
from numba import njit

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(REPO, "lp"))
sys.path.insert(0, os.path.join(REPO, "toolbox"))
import lpdata  # noqa: E402
import score  # noqa: E402

M = 29
KINDS = ("phi", "prime")
K0_RANGE = 10000
NKEYS = 20000
OUT = os.path.join(REPO, "agents", "laneT_prime_walk", "out")
TABLES = os.path.join(OUT, "tables.npz")
SIM_PATH = os.path.join(REPO, "jobs", "hypothesis-gate", "runs", "walk_dodge_prime_cipher.py")


def load_sim():
    spec = importlib.util.spec_from_file_location("sim_walk_dodge_prime", SIM_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def key_of(kk):
    """Key index kk in 0..19999 -> (kind, k0). kk = kind_index * 10000 + k0."""
    return KINDS[kk // K0_RANGE], kk % K0_RANGE


def build_key_tables(sim):
    GP = np.zeros((NKEYS, 5, M), np.int64)   # GP[kk, k] = g^k
    GI = np.zeros((NKEYS, 5, M), np.int64)   # GI[kk, e] = g^(-e)
    MC = np.zeros((NKEYS, 5, M), np.int64)   # MC[kk, cb][x] = gp[cb][sigma[x]]
    MINV = np.zeros((NKEYS, 5, M), np.int64)
    B0INV = np.zeros((NKEYS, M), np.int64)
    for kk in range(NKEYS):
        kind, k0 = key_of(kk)
        g, sigma, base0 = sim.keys_from(kind, k0)
        gp = [list(range(M))]
        for k in range(1, 5):
            gp.append([g[x] for x in gp[k - 1]])      # compose(g, gp[k-1])
        for e in range(5):
            GP[kk, e] = gp[e]
            GI[kk, e] = gp[(5 - e) % 5]
        for cb in range(5):
            mc = [gp[cb][sigma[x]] for x in range(M)]
            inv = [0] * M
            for x in range(M):
                inv[mc[x]] = x
            MC[kk, cb] = mc
            MINV[kk, cb] = inv
        inv0 = [0] * M
        for x in range(M):
            inv0[base0[x]] = x
        B0INV[kk] = inv0
    return GP, GI, MC, MINV, B0INV


def build_quad_tables():
    """ADD[t, p]: quadgram log-score added by rune p after tail t; TNEW the new tail; NW the windows added.
    tail t encodes the last three letters base 27 (0 = no letter, 1..26 = A..Z)."""
    lq, floor = score._table()
    Q = np.full(26 ** 4, floor, dtype=np.float64)
    for key, v in lq.items():
        if len(key) == 4 and key.isalpha() and key.isupper():
            a, b, c, d = (ord(ch) - 65 for ch in key)
            Q[a * 17576 + b * 676 + c * 26 + d] = v
    TR = lpdata.TR
    TRL = [[ord(ch) - 64 for ch in TR[p]] for p in range(M)]
    NT = 27 ** 3
    ADD = np.zeros((NT, M), np.float64)
    TNEW = np.zeros((NT, M), np.int64)
    NW = np.zeros((NT, M), np.int64)
    for t in range(NT):
        t0, t1, t2 = t // 729, (t // 27) % 27, t % 27
        for p in range(M):
            a, b, c = t0, t1, t2
            sc = 0.0
            nw = 0
            for L in TRL[p]:
                if a and b and c:
                    sc += Q[(a - 1) * 17576 + (b - 1) * 676 + (c - 1) * 26 + (L - 1)]
                    nw += 1
                a, b, c = b, c, L
            ADD[t, p] = sc
            TNEW[t, p] = a * 729 + b * 27 + c
            NW[t, p] = nw
    return ADD, TNEW, NW


def load_tables():
    """Key tables and quadgram tables, cached in out/tables.npz (built once)."""
    if os.path.exists(TABLES):
        z = np.load(TABLES)
        return tuple(z[k] for k in ("GP", "GI", "MC", "MINV", "B0INV", "ADD", "TNEW", "NW"))
    sim = load_sim()
    GP, GI, MC, MINV, B0INV = build_key_tables(sim)
    ADD, TNEW, NW = build_quad_tables()
    os.makedirs(OUT, exist_ok=True)
    np.savez(TABLES, GP=GP, GI=GI, MC=MC, MINV=MINV, B0INV=B0INV, ADD=ADD, TNEW=TNEW, NW=NW)
    return GP, GI, MC, MINV, B0INV, ADD, TNEW, NW


@njit(cache=True)
def _beam(cipher, words, GP, GI, MC, MINV, Binv0, ADD, TNEW, NW, W, track):
    """Returns (alive, mean, sc, nw, path). alive < n means every state died at position alive."""
    n = cipher.shape[0]
    NCAP = 2 * W + 4
    cur_sc = np.zeros(W)
    cur_nw = np.zeros(W, np.int64)
    cur_e = np.zeros(W, np.int64)
    cur_t = np.zeros(W, np.int64)
    cur_B = np.zeros((W, M), np.int64)
    new_sc = np.zeros(W)
    new_nw = np.zeros(W, np.int64)
    new_e = np.zeros(W, np.int64)
    new_t = np.zeros(W, np.int64)
    new_B = np.zeros((W, M), np.int64)
    c_sc = np.zeros(NCAP)
    c_par = np.zeros(NCAP, np.int64)
    c_p = np.zeros(NCAP, np.int64)
    c_e = np.zeros(NCAP, np.int64)
    c_t = np.zeros(NCAP, np.int64)
    c_nw = np.zeros(NCAP, np.int64)
    for y in range(M):
        cur_B[0, y] = Binv0[y]
    nb = 1
    rows = n if track else 1
    PAR = np.zeros((rows, W), np.int32)
    RUNE = np.zeros((rows, W), np.int8)
    alive = n
    for k in range(n):
        c = cipher[k]
        prev = cipher[k - 1] if k > 0 else -1
        nc = 0
        for s in range(nb):
            e = cur_e[s]
            t = cur_t[s]
            sc0 = cur_sc[s]
            nw0 = cur_nw[s]
            if prev < 0 or c != prev:                       # A: no dodge
                p = GI[e, cur_B[s, c]]
                c_sc[nc] = sc0 + ADD[t, p]
                c_par[nc] = s
                c_p[nc] = p
                c_e[nc] = (e + 1) % 5
                c_t[nc] = TNEW[t, p]
                c_nw[nc] = nw0 + NW[t, p]
                nc += 1
            if prev >= 0:                                   # B: dodge, needs the forced check
                pB = GI[e, cur_B[s, prev]]
                if GP[(e + 1) % 5, pB] == cur_B[s, c]:
                    c_sc[nc] = sc0 + ADD[t, pB]
                    c_par[nc] = s
                    c_p[nc] = pB
                    c_e[nc] = (e + 2) % 5
                    c_t[nc] = TNEW[t, pB]
                    c_nw[nc] = nw0 + NW[t, pB]
                    nc += 1
        if nc == 0:
            alive = k
            break
        if nc <= W:
            m = nc
            sel = np.arange(nc)
        else:
            m = W
            sel = np.argsort(-c_sc[:nc])[:W]
        boundary = (k == n - 1) or (words[k + 1] != words[k])
        for j in range(m):
            q = sel[j]
            s = c_par[q]
            ee = c_e[q]
            new_sc[j] = c_sc[q]
            new_nw[j] = c_nw[q]
            new_t[j] = c_t[q]
            new_e[j] = ee
            if boundary:
                cb = (ee + 4) % 5
                for y in range(M):
                    new_B[j, y] = MINV[cb, cur_B[s, y]]
            else:
                for y in range(M):
                    new_B[j, y] = cur_B[s, y]
            if track:
                PAR[k, j] = s
                RUNE[k, j] = c_p[q]
        cur_sc, new_sc = new_sc, cur_sc
        cur_nw, new_nw = new_nw, cur_nw
        cur_e, new_e = new_e, cur_e
        cur_t, new_t = new_t, cur_t
        cur_B, new_B = new_B, cur_B
        nb = m
    # best live state by mean quadgram score
    best = -1
    bestm = -1e300
    for j in range(nb):
        if cur_nw[j] > 0:
            mm = cur_sc[j] / cur_nw[j]
            if mm > bestm:
                bestm = mm
                best = j
    last = alive - 1
    path = np.zeros(alive, np.int64)
    if best >= 0 and track:
        idx = best
        for kk in range(last, -1, -1):
            path[kk] = RUNE[kk, idx]
            idx = PAR[kk, idx]
    if best < 0:
        return alive, -1e300, 0.0, 0, path
    return alive, bestm, cur_sc[best], cur_nw[best], path


class Decoder:
    def __init__(self, W=512):
        self.W = W
        GP, GI, MC, MINV, B0INV, ADD, TNEW, NW = load_tables()
        # int32 key tables (permutations of 0..28) halve the per-worker memory; the arithmetic is int64 in _beam
        self.GP = GP.astype(np.int32)
        self.GI = GI.astype(np.int32)
        self.MC = MC.astype(np.int32)
        self.MINV = MINV.astype(np.int32)
        self.B0INV = B0INV.astype(np.int32)
        self.ADD, self.TNEW, self.NW = ADD, TNEW, NW

    def decode(self, cipher, words, kk, track=False):
        c = np.asarray(cipher, dtype=np.int64)
        w = np.asarray(words, dtype=np.int64)
        return _beam(c, w, self.GP[kk], self.GI[kk], self.MC[kk], self.MINV[kk], self.B0INV[kk],
                     self.ADD, self.TNEW, self.NW, self.W, track)

    def screen(self, cipher, words, keys):
        """(alive, mean, sc, nw) for each key index in keys, as arrays."""
        c = np.asarray(cipher, dtype=np.int64)
        w = np.asarray(words, dtype=np.int64)
        out = np.zeros((len(keys), 4))
        alive = np.zeros(len(keys), np.int64)
        for j, kk in enumerate(keys):
            a, mm, sc, nw, _p = _beam(c, w, self.GP[kk], self.GI[kk], self.MC[kk], self.MINV[kk], self.B0INV[kk],
                                      self.ADD, self.TNEW, self.NW, self.W, False)
            alive[j] = a
            out[j] = (mm, sc, nw, 0.0)
        return alive, out
