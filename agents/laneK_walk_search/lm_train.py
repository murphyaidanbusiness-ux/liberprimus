"""Train a word-internal rune 4-gram LM (30 symbols: 29 runes + boundary B=29) on W&P train split.
Each word is the sequence B B B x1..xL B. Interpolated ML: P = .55 P4 + .25 P3 + .13 P2 + .07 P1(+add-1).
Saves float32 log-prob (natural log) table lm4.bin indexed ((a*30+b)*30+c)*30+d."""
import kcore as k, numpy as np
tr, ho = k.wp_split()
seq = []
for w in tr:
    seq += [29, 29, 29] + list(w) + [29]
s = np.array(seq, dtype=np.int64)
V = 30
def counts(n):
    idx = np.zeros(len(s) - n + 1, dtype=np.int64)
    for i in range(n): idx = idx * V + s[i:len(s) - n + 1 + i]
    return np.bincount(idx, minlength=V ** n).astype(np.float64)
c1 = counts(1); c2 = counts(2).reshape(V, V); c3 = counts(3).reshape(V, V, V); c4 = counts(4).reshape(V, V, V, V)
c1[29] = 0  # boundary isn't predicted as unigram except via higher orders
P1 = (c1 + 1) / (c1 + 1).sum()
def cond(c):
    tot = c.sum(-1, keepdims=True); return np.where(tot > 0, c / np.maximum(tot, 1), 0.0), (tot > 0)
P2, h2 = cond(c2); P3, h3 = cond(c3); P4, h4 = cond(c4)
# interpolate with renormalisation where a context is unseen
P = 0.07 * P1[None, None, None, :] + 0.13 * P2[None, None, :, :] + 0.25 * P3[None, :, :, :] + 0.55 * P4
P = P / P.sum(-1, keepdims=True)
L = np.log(P).astype(np.float32)
L.tofile(k.OUT + '/lm4.bin')
# sanity: per-rune cross entropy on heldout and on solved pages, and on random runes
def xent(words):
    tot = 0; n = 0
    for w in words:
        a = b = c = 29
        for x in list(w) + [29]:
            tot += L[a, b, c, x]; n += 1; a, b, c = b, c, x
    return -tot / n
rng = np.random.default_rng(0)
print('nats/symbol heldout %.3f  solved-LP %.3f  random-runes %.3f' % (
    xent(ho[:20000]), xent(k.solved_words()), xent([rng.integers(0, 29, len(w)) for w in ho[:20000]])))
