"""Fixture for verify-lane: independent re-derivation of lane Q's whole-stream headline (round two, by the orchestrator).
Lane Q reported: stream raw max z 4.184 at lag 6002. This code shares nothing with lane Q's FFT pipeline."""
import math
import sys

import numpy as np

sys.path.insert(0, "lp")
import lpdata  # noqa: E402

U, C, sha = lpdata.unsolved()
assert sha == "023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585"
C = np.array(C)
f = np.bincount(C, minlength=29) / len(C)
p0 = float((f * f).sum())


def lag(k):
    n = len(C) - k
    m = int((C[:-k] == C[k:]).sum())
    return m, n, (m - n * p0) / math.sqrt(n * p0 * (1 - p0))


m, n, z = lag(6002)
print("lag 6002: %d %d z=%+.2f" % (m, n, z))
top = sorted(((lag(k)[2], k) for k in range(1, len(C) - 60)), reverse=True)[:5]
print("top lags:", ", ".join("%d (z %+.2f)" % (k, z) for z, k in top))
