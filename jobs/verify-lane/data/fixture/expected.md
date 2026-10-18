# Expected output of `python jobs/verify-lane/data/fixture/laneQ_verify.py`

```
lag 6002: 304 6954 z=+4.18
top lags: 6002 (z +4.18), 9428 (z +3.70), 8686 (z +3.56), 2039 (z +3.50), 4908 (z +3.47)
```

This reproduces lane Q's "stream raw max z 4.184 at lag 6002" with independent code. The other worked examples of this
job from round two, written up in `REPORT_ROUND2.md` and `agents/laneO_quagmire_dodge/RESULTS.md` section 7:
- lane R's line-break effect, split directly by `lp/t7_lag5_lines.py` (32/460 vs 72/1645, length-stratified p 0.018);
- lane O's failed control, replayed on fresh plaintext (`diag_alphabet_kind.py`): a 5% scorer miss, not a port bug.
