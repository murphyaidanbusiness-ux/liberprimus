"""Task 2: multiple-testing-honest significance of the within-word lag-5 echo."""
import numpy as np, core
rng = np.random.default_rng(12345)
C, wid, chap, page = core.lp_main()
_, wr, sec = core.lp_relikd()       # 9 page-group sections (identical runes/boundaries to main)
pos, wl, starts, lens = core.word_meta(wid)
K = 12
cnt = core.lag_counts(C, wid, K); zw, zx = core.zcells(cnt)
print('== observed profile (z vs 1/29) ==')
for k in range(K):
    print('lag %2d  within %4d/%5d = %.4f z=%+.2f | across %4d/%5d = %.4f z=%+.2f' % (
        k+1, cnt[0,k], cnt[1,k], cnt[0,k]/cnt[1,k], zw[k], cnt[2,k], cnt[3,k], cnt[2,k]/cnt[3,k], zx[k]))
obs5 = zw[4]
allz = np.r_[zw, zx]

# Null A: global rune shuffle, word structure kept (destroys doublet suppression -> lag-1 z irrelevant for max-up)
B = 2000
maxA = np.zeros(B); maxA_no1 = np.zeros(B); z5A = np.zeros(B); maxAw = np.zeros(B)
for b in range(B):
    Cs = rng.permutation(C)
    c = core.lag_counts(Cs, wid, K); a, x = core.zcells(c)
    z = np.r_[a, x]
    maxA[b] = z.max(); maxAw[b] = a.max(); z5A[b] = a[4]
    maxA_no1[b] = np.r_[a[1:], x[1:]].max()
print('\nNull A (global shuffle, 2000): z5 null mean %.2f sd %.2f; P(z5>=obs) = %.4f' % (z5A.mean(), z5A.std(), (z5A >= obs5).mean()))
print('  family-wise over 24 cells (max upward z): P(max>=%.2f) = %.4f   [null max: median %.2f, 95%% %.2f]' % (
    obs5, (maxA >= obs5).mean(), np.median(maxA), np.quantile(maxA, .95)))
print('  family-wise over 22 cells excluding lag 1: P = %.4f' % (maxA_no1 >= obs5).mean())
print('  family-wise over 12 within cells: P = %.4f' % (maxAw >= obs5).mean())
print('  observed max upward z among the other 23 cells: %.2f' % np.delete(allz, 4).max())

# Null B: doublet-preserving null -- keep the rune stream byte-for-byte, permute word-length sequence within each section
B2 = 2000
maxB = np.zeros(B2); z5B = np.zeros(B2); m5B = np.zeros(B2)
seclens = []
for s in np.unique(sec):
    ws = np.unique(wid[sec == s]); seclens.append(lens[ws])
for b in range(B2):
    W = []; off = 0
    for L in seclens:
        Lp = rng.permutation(L); W.append(np.repeat(np.arange(len(Lp)) + off, Lp)); off += len(Lp)
    W = np.concatenate(W)
    c = core.lag_counts(C, W, K); a, x = core.zcells(c)
    m5B[b] = c[0, 4]
    # standardise within-cell counts against this null later; record raw counts
    if b == 0: allc = np.zeros((B2, 2, K))
    allc[b, 0] = c[0]; allc[b, 1] = c[2]
mu = allc.mean(0); sd = allc.std(0)
zobs = (np.array([cnt[0], cnt[2]]) - mu) / sd
zn = (allc - mu) / sd
maxBw = zn[:, 0, :].max(1); maxBall = zn.reshape(B2, -1).max(1)
print('\nNull B (rune stream fixed, word lengths permuted within the 9 sections, 2000):')
print('  lag5 within: obs %d, null %.1f +- %.1f, z=%+.2f, P(>=)=%.4f' % (cnt[0,4], mu[0,4], sd[0,4], zobs[0,4], (allc[:,0,4] >= cnt[0,4]).mean()))
print('  within profile z vs null B:', ' '.join('%+.2f' % v for v in zobs[0]))
print('  family-wise max over 12 within cells: P = %.4f; over 24 cells: P = %.4f' % ((maxBw >= zobs[0,4]).mean(), (maxBall >= zobs[0,4]).mean()))

# Robustness
def z5(Cv, Wv, valid=None):
    c = core.lag_counts(Cv, Wv, 5, valid); a, _ = core.zcells(c); return c[0,4], c[1,4], a[4]
print('\n== robustness ==')
for s in np.unique(sec):
    v = sec != s; m, n, z = z5(C, wid, v)
    ms, ns, zs = z5(C, wid, sec == s)
    print('  drop section %d (n=%4d runes): %d/%d = %.4f z=%+.2f   | section alone: %d/%d z=%+.2f' % (s, (sec == s).sum(), m, n, m/n, z, ms, ns, zs))
for lo, hi in [(6, 9), (6, 6), (7, 7), (8, 8), (9, 9), (10, 14), (6, 7), (8, 14)]:
    v = (wl >= lo) & (wl <= hi); m, n, z = z5(C, wid, v)
    print('  word length %d-%d: %d/%d = %.4f z=%+.2f' % (lo, hi, m, n, m/n, z))
c2, wa, ca = core.lp_aldegonde(); wa = wa[:12956]
m, n, z = z5(C, wa); print('  aldegonde page0-58 tokenisation (+32 boundaries): %d/%d = %.4f z=%+.2f' % (m, n, m/n, z))
_, wr2, _ = core.lp_relikd(); m, n, z = z5(C, wr2); print('  relikd LiberPrayground pages: %d/%d = %.4f z=%+.2f (runes and boundaries identical to main)' % (m, n, m/n, z))
# increments stream D within words (chain-model object)
D = np.full(len(C), -1); D[1:] = (C[1:] - C[:-1]) % 29
validD = np.r_[False, wid[1:] == wid[:-1]]   # increment inside a word
cD = core.lag_counts(D, wid, 10, validD)
print('\n== increments D (both increments inside the same word), within-word lag k; chance for D!=0 ~ 1/28 ==')
for k in range(10):
    p0 = 1/28; n = cD[1,k]; m = cD[0,k]
    print('  D lag %2d within: %d/%d = %.4f z=%+.2f' % (k+1, m, n, m/max(n,1), (m-p0*n)/np.sqrt(max(n,1)*p0*(1-p0))))
cDx = core.lag_counts(D, wid, 10, np.r_[False, np.ones(len(C)-1, bool)])
print('  D lag-5 across-word: %d/%d = %.4f' % (cDx[2,4], cDx[3,4], cDx[2,4]/cDx[3,4]))
np.savez(core.OUT + '/s1_null.npz', maxA=maxA, z5A=z5A, allcB=allc)
