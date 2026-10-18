# ABOUTME: Lane W scorer library: dodge_aware_scorer's score path, vectorised, with its word model
# ABOUTME: either the odometer (its own) or the clock-dependent walk of quagmire_dodge.encipher.
"""Lane W: can the dodge-aware scorer see the clock-dependent Quagmire dodge?

The score path is dodge_aware_scorer.score: seed the matrix over five phases, then
alternate an assignment (cipher symbol -> base_0 image) with a per-window phase refit,
three passes. Only the WORD MODEL changes between the two variants:

  odometer (its own):  word w maps y -> K[(pos[y - b_w] - a_w)], with (a_w, b_w) closed
                       form in the word index. Nothing depends on the clock path.
  clock (quagmire_dodge.encipher): base_w = base_0 . T_w, T_w = S_0 . ... . S_(w-1),
                       S_j = alpha[ph_j] . sigma, ph_j = the phase used by the LAST rune of
                       word j. The word map depends on every earlier phase.

Stream, score_odo and score_clock are vectorised copies of das.score. verify_port.py checks
the copy against das.score on the odometer, where it must agree.
"""

from __future__ import annotations

import ctypes
import site
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PORT = REPO / "dl" / "aldegonde_port"
# Run with -I: the script's own folder and the port are added explicitly; user site is
# re-added because -I hides it (the quagmire simulator needs scipy from there).
sys.path[:0] = [str(HERE), str(PORT / "src"), str(PORT / "experiments")]
sys.path.append(site.getusersitepackages())

import dodge_aware_scorer as das  # noqa: E402
import quagmire_dodge as qd  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import compose  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

M = 29
WIN = das.WINDOW  # 18 runes per window, as the scorer
PASSES = das.PASSES  # 3, as the scorer
N_WRONG = 2000
CATEGORIES = ("alphabet", "schedule", "disk-or-dials", "everything")


def low_priority() -> None:
    """BelowNormal priority (0x4000) for this process."""
    k32 = ctypes.windll.kernel32
    k32.SetPriorityClass(k32.GetCurrentProcess(), 0x4000)


def lp_lens(n: int = 400) -> list[int]:
    """Word lengths of the LP's first n words, sliced as dodge_aware_scorer's main does."""
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    return [counts[k] for k in sorted(counts)][:n]


def register_pools():
    """Word pools from DODGE_PROSE (Moby-Dick), through the port's own loader."""
    pools, _t, _f = load_register(PROSE_CACHE)
    return pools


def inverse(p) -> np.ndarray:
    p = np.asarray(p, dtype=np.int64)
    out = np.empty(M, dtype=np.int64)
    out[p] = np.arange(M)
    return out


class Stream:
    """A cipher text as the scorer sees it: flat runes, owner word, window and in-window offset."""

    def __init__(self, words):
        flat, owner = [], []
        for w, word in enumerate(words):
            flat.extend(word)
            owner.extend([w] * len(word))
        self.words = words
        self.c = np.asarray(flat, dtype=np.int64)
        self.owner = np.asarray(owner, dtype=np.int64)
        self.N = len(flat)
        self.n_words = len(words)
        idx = np.arange(self.N)
        self.win = idx // WIN
        self.off = idx % WIN
        self.W = int(self.win.max()) + 1
        self.end = np.zeros(self.n_words, dtype=np.int64)
        np.maximum.at(self.end, self.owner, idx)  # index of each word's last rune


def odo_word_maps(K, startdials, n_words) -> np.ndarray:
    """(n_words, M): row w is the scorer's word map for word w, K[(pos[y - b] - a)]."""
    K = np.asarray(K, dtype=np.int64)
    pos = inverse(K)
    y = np.arange(M)
    G = np.empty((n_words, M), dtype=np.int64)
    for w, (a, b) in enumerate(das.word_shifts(n_words, startdials)):
        G[w] = K[(pos[(y - b) % M] - a) % M]
    return G


def clock_word_maps(alpha: np.ndarray, sigma, ph_end) -> np.ndarray:
    """(n_words, M): row j is T_j^-1 where T_j = S_0 . ... . S_(j-1), S_i = alpha[ph_i] . sigma."""
    sig = np.asarray(sigma, dtype=np.int64)
    T = np.arange(M)
    G = np.empty((len(ph_end), M), dtype=np.int64)
    for j, ph in enumerate(ph_end):
        G[j] = inverse(T)
        T = T[alpha[int(ph)][sig]]  # T_(j+1)[x] = T_j[S_j[x]]
    return G


def _inv_rows(alpha: np.ndarray) -> np.ndarray:
    invA = np.empty_like(alpha)
    for k in range(5):
        invA[k][alpha[k]] = np.arange(M)
    return invA


def _score(st: Stream, logf, invA, G_of, phases):
    """dodge_aware_scorer.score, vectorised. phases None is the uninformed five-phase seed.

    Returns (nats per rune, final assignment v, the phases the last pass used).
    """
    rows = np.arange(st.N)
    total, v, used = 0.0, None, None
    for _ in range(PASSES):
        used = phases
        Gw = G_of(phases)
        G = Gw[st.owner]  # (N, M): the plaintext-coordinate candidate for each image y
        LP = logf[invA[:, G]]  # (5, N, M): log p of the implied plaintext under each phase
        mat = np.zeros((M, M))
        if phases is None:
            np.add.at(mat, st.c, LP.sum(axis=0))
            mat /= 5.0
        else:
            k_i = (phases[st.win] + st.off) % 5
            np.add.at(mat, st.c, LP[k_i, rows])
        total, v = das.assign(mat)
        g2 = Gw[st.owner, v[st.c]]
        LP2 = logf[invA[:, g2]]  # (5, N)
        tot = np.empty((st.W, 5))
        for p in range(5):
            tot[:, p] = np.bincount(st.win, weights=LP2[(p + st.off) % 5, rows], minlength=st.W)
        phases = np.argmax(tot, axis=1)
    return total / st.N, v, used


def score_odo(st: Stream, K, offs, startdials, logf):
    """Odometer score path for one key (K, schedule, dials): (score, v, phases of last pass)."""
    _fwd, invA = das.letter_maps(K, offs)
    fixed = odo_word_maps(K, startdials, st.n_words)
    return _score(st, logf, invA, lambda ph: fixed, None)


def clock_phase_ends(st: Stream, phases) -> np.ndarray:
    """Phase of each word's last rune under the window phases (in-window, no-fire model)."""
    return (phases[st.win[st.end]] + st.off[st.end]) % 5


def score_clock(st: Stream, K, offs, sigma, logf):
    """Clock-dependent word model in the same score path. Seed: clock equals position."""
    alpha = np.asarray(qd.alphabets(list(K), list(offs)), dtype=np.int64)
    invA = _inv_rows(alpha)

    def G_of(phases):
        return clock_word_maps(alpha, sigma, clock_phase_ends(st, phases))

    seed = (np.arange(st.W) * WIN) % 5
    return _score(st, logf, invA, G_of, seed)


def clock_trace(plain, base0, alpha, sigma):
    """quagmire_dodge.encipher, instrumented. Also returns each rune's phase, the base at
    each word start and the number of clock skips. The output must equal encipher's."""
    base = list(base0)
    out, kappa, bases = [], [], []
    clock, previous, fires = 0, None, 0
    for word in plain:
        bases.append(list(base))
        cw = []
        for p in word:
            k = clock % 5
            c = base[alpha[k][p]]
            if c == previous:
                fires += 1
                clock += 1
                k = clock % 5
                c = base[alpha[k][p]]
            cw.append(c)
            kappa.append(k)
            previous = c
            clock += 1
        out.append(cw)
        base = compose(base, compose(alpha[(clock - 1) % 5], sigma))
    return out, np.asarray(kappa, dtype=np.int64), bases, fires


def summarise(true: float, wrong: np.ndarray, cats) -> dict:
    best = int(np.argmax(wrong))
    sd = float(wrong.std())
    return {
        "true": float(true),
        "best_wrong": float(wrong[best]),
        "best_wrong_category": cats[best],
        "rank1": bool(true > wrong.max()),
        "z": float((true - wrong.mean()) / sd) if sd > 0 else float("nan"),
        "wrong_mean": float(wrong.mean()),
        "wrong_sd": sd,
    }
