"""Shared scorers: normalised IoC and English quadgram log-score per quadgram (as lp/verify_candidate.py).

    import sys; sys.path.insert(0, "toolbox"); import score
    score.ioc(runes)          # 1.0 random, ~1.7-1.8 English runes
    score.quadgram(runes)     # log10 per quadgram: English about -4.1..-5.0, noise about -7.5
"""
import math
import sys
from collections import Counter

sys.path.insert(0, "lp")
import lpdata  # noqa: E402

QUADS = "dl/dukotah/liber-primus/data/english_quadgrams.txt"
_LQ = None


def ioc(x):
    c = Counter(x)
    n = len(x)
    return 29 * sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) if n > 1 else 0.0


def _table():
    global _LQ
    if _LQ is None:
        q = {}
        for ln in open(QUADS):
            k, v = ln.split()
            q[k] = float(v)
        tot = sum(q.values())
        _LQ = ({k: math.log10(v / tot) for k, v in q.items()}, math.log10(0.01 / tot))
    return _LQ


def quadgram(runes):
    lq, floor = _table()
    s = "".join(lpdata.TR[i] for i in runes)
    if len(s) < 4:
        return floor
    return sum(lq.get(s[i:i + 4], floor) for i in range(len(s) - 3)) / (len(s) - 3)
