"""Pigeonhole lower bound on repeated cipher words (len>=3) under ANY M_K key and ANY phase choice:
a word type occurring n times has at most 2K cipher forms (K phases x first-rune skip or not), so
repeats >= sum_t max(0, n_t - 2K). Plaintext = heldout W&P (contiguous 12,956 runes) and solved LP pages."""
import kcore as k, numpy as np
from collections import Counter
tr, ho = k.wp_split()
srcs = {'W&P contig (20 samples)': [k.plain_contig(ho, seed=200 + r) for r in range(20)]}
sw = k.solved_words(); srcs['solved LP pages (%d words, %d runes)' % (len(sw), sum(len(w) for w in sw))] = [sw]
for name, samples in srcs.items():
    for K in [4, 5, 6, 7, 10, 20, 50]:
        b = []
        for P in samples:
            cnt = Counter(tuple(w) for w in P if len(w) >= 3)
            b.append(sum(max(0, v - 2 * K) for v in cnt.values()))
        print('%-40s K=%2d  min possible repeats(len>=3) = %.0f   (LP observed 16)' % (name, K, np.mean(b)))
