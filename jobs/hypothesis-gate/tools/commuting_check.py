"""Mechanism check for quagmire_dodge_clock_commuting: how many word maps the cipher really visits.

    python jobs/hypothesis-gate/tools/commuting_check.py            (run from the repository root, with env.sh sourced)

Replays the simulator's key draws and the community encipher loop for rng seeds 1000..1002 (the gate's seeds),
recording the base at every word boundary. It checks three things the gate report relies on:
1. the ciphertext is identical to the simulator's encrypt() for the same seed (the replay is faithful);
2. the number of distinct base maps over the word sequence is at most 29 (the word map telescopes: base_0 . K . add(D_w) . K^-1);
3. how many pairs of equal plaintext words (>= 3 runes) start in the same state (base, clock phase), and how many
   ciphertext word-repeat types the cipher produced, so C3's excess can be read against the state count.
This is a diagnostic. It does not change the gate, and it reads the simulator only through its own imports.
"""
import importlib.util
import random
import sys
from collections import Counter

sys.path[:0] = ["toolbox", "lp", "jobs/hypothesis-gate/tools"]
import runes as rn  # noqa: E402
import fingerprint as fp  # noqa: E402

PATH = "jobs/hypothesis-gate/runs/quagmire_dodge_clock_commuting_cipher.py"
M = 29


def load(path):
    spec = importlib.util.spec_from_file_location("cipher_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def groups(plain, words):
    ws, cur, last = [], [], None
    for r, w in zip(plain, words):
        if w != last and cur:
            ws.append(cur)
            cur = []
        cur.append(r)
        last = w
    ws.append(cur)
    return ws


def replay(plain_words, rng):
    """The simulator's draws (same order) and the community encipher loop, with the base recorded per word."""
    from quagmire_dodge import alphabets, schedule, compose
    from quagmire_runner import conj_shift

    K = rng.sample(range(M), M)
    offsets = schedule(rng, zeros=1)
    alpha = alphabets(K, offsets)
    sigma = conj_shift(K, rng.randrange(1, M))
    base0 = rng.sample(range(M), M)
    base = list(base0)
    out, states = [], []
    clock, previous = 0, None
    for word in plain_words:
        states.append((tuple(base), clock % 5))
        cipher_word = []
        for p in word:
            c = base[alpha[clock % 5][p]]
            if c == previous:
                clock += 1
                c = base[alpha[clock % 5][p]]
            cipher_word.append(c)
            previous = c
            clock += 1
        out.append(cipher_word)
        base = compose(base, compose(alpha[(clock - 1) % 5], sigma))
    return [c for w in out for c in w], states


def main():
    sys.path[:0] = ["dl/aldegonde_port/src", "dl/aldegonde_port/experiments"]
    mod = load(PATH)
    plain, words = rn.english_stream(12956)
    plain, words = list(plain), list(words)
    pw = groups(plain, words)
    eq = Counter(tuple(w) for w in pw if len(w) >= 3)
    pairs_equal = sum(v * (v - 1) // 2 for v in eq.values())
    print("cipher: %s" % getattr(mod, "NAME", PATH))
    print("plaintext words >= 3 runes: %d, equal-word pairs among them: %d" % (sum(eq.values()), pairs_equal))
    for s in range(3):
        c_mod = mod.encrypt(list(plain), list(words), random.Random(1000 + s))
        c_rep, states = replay(pw, random.Random(1000 + s))
        same = c_mod == c_rep
        distinct_bases = len({st[0] for st in states})
        distinct_states = len(set(states))
        # pairs of equal plaintext words (>= 3 runes) that start in the same state (same base, same clock phase)
        by_word = {}
        for wi, w in enumerate(pw):
            if len(w) >= 3:
                by_word.setdefault(tuple(w), []).append(states[wi])
        same_state_pairs = 0
        for lst in by_word.values():
            cnt = Counter(lst)
            same_state_pairs += sum(v * (v - 1) // 2 for v in cnt.values())
        cw = fp._words(c_mod, words)
        rep_types = fp._repeated(cw)
        print("seed %d: replay matches encrypt: %s; distinct base maps %d (<= 29); distinct (base, phase) states %d"
              % (s, same, distinct_bases, distinct_states))
        print("  equal plaintext pairs starting in the same state: %d of %d; ciphertext repeated word types (>= 3): %d"
              % (same_state_pairs, pairs_equal, rep_types))
    return 0


if __name__ == "__main__":
    sys.exit(main())
