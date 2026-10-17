NAME = "Quagmire with clock-dependent word step and doublet dodge (community quagmire_dodge.encipher: base steps by alpha_k . sigma, one-zero schedule)"
DESCRIPTION = """Random keyed alphabet K, a random one-zero five-step schedule (quagmire_dodge.schedule(zeros=1)), the five
alphabets A_k = K . (add S_k) . K^-1, a random sigma = conj_shift(random permutation, random delta), and a random base_0.
Enciphered by the community's own function (dl/aldegonde_port/experiments/quagmire_dodge.py, encipher(plain, base0, alpha, sigma)),
which emits per word, dodges a would-be repeat by advancing the clock one step, and steps the base once per word by
alpha_(clock phase) . sigma. Its key form is the one quagmire_dodge.fit() and dodge_scorer_check.py use. The port is audited
in agents/laneO_quagmire_dodge/audit/ (quagmire_dodge.py is in the closure). Gated as quagmire_dodge_clock."""
import os
import sys

PORT = os.path.join("dl", "aldegonde_port")
sys.path[:0] = [os.path.join(PORT, "src"), os.path.join(PORT, "experiments")]

M = 29


def encrypt(plain, words, rng):
    from quagmire_dodge import alphabets, encipher, schedule
    from quagmire_runner import conj_shift

    K = rng.sample(range(M), M)
    offsets = schedule(rng, zeros=1)
    alpha = alphabets(K, offsets)
    sigma = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
    base0 = rng.sample(range(M), M)
    ws, cur, last = [], [], None
    for r, w in zip(plain, words):
        if w != last and cur:
            ws.append(cur)
            cur = []
        cur.append(r)
        last = w
    ws.append(cur)
    return [c for word in encipher(ws, base0, alpha, sigma) for c in word]
