NAME = "Quagmire with clock-dependent word step, doublet dodge, and sigma commuting with the letter alphabets (sigma = conj_shift(K, delta), one keyword for everything)"
DESCRIPTION = """Random keyed alphabet K, a random one-zero five-step schedule (quagmire_dodge.schedule(zeros=1)), the five
alphabets A_k = K . (add S_k) . K^-1, sigma = conj_shift(K, delta) for a random delta in 1..28 (built from the SAME keyed
alphabet K as the letter alphabets, so sigma commutes with every A_k), and a random base_0.
Enciphered by the community's own function (dl/aldegonde_port/experiments/quagmire_dodge.py, encipher(plain, base0, alpha, sigma)),
which emits per word, dodges a would-be repeat by advancing the clock one step, and steps the base once per word by
alpha_(clock phase) . sigma. The only change from quagmire_dodge_clock_cipher.py is the sigma line: the clock-dependent
word step is unchanged. Because all the word steps are powers of one 29-cycle, the word map telescopes to base_0 . K . add(D_w) . K^-1
with D_w = sum over earlier words of (delta + S at the phase of that word's last rune), so there are at most 29 distinct
word maps (times 5 clock phases). Gated as quagmire_dodge_clock_commuting."""
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
    sigma = conj_shift(K, rng.randrange(1, M))
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
