"""Parse mk_sa logs; for real/null runs compute best score per symbol, IoC of decryption, quadgram score."""
import sys, glob, re, math, numpy as np, kcore as k
Q = {}; tot = 0
for line in open(k.S + '/dl/dukotah/liber-primus/data/english_quadgrams.txt'):
    a, b = line.split(); Q[a] = int(b); tot += int(b)
FLOOR = math.log10(0.01 / tot); Q = {a: math.log10(v / tot) for a, v in Q.items()}
def quad(lat):
    s = [Q.get(lat[i:i+4], FLOOR) for i in range(len(lat) - 3)]; return sum(s) / max(len(s), 1)
def read_dec(fn):
    P = []
    for line in open(fn):
        a, b = line.split(':'); P.append([int(x) for x in b.split()])
    return P
def best_of(log):
    best = None
    for line in open(log):
        m = re.match(r'RESTART \d+ score (\S+) .* acc (\S+)', line)
        if m:
            s = float(m.group(1)); best = s if best is None else max(best, s)
    return best
def nsym(inst):
    t = open(inst).read().split('\n'); nw = int(t[0]); return sum(map(int, t[1].split())) + nw
def stats(prefix, inst):
    b = best_of('runs/%s.log' % prefix); n = nsym(inst)
    P = read_dec('runs/%s.dec' % prefix); flat = np.concatenate([np.array(w) for w in P])
    lat = ''.join(k.TR[x] for x in flat)
    return b / n, k.ioc(flat), quad(lat), P
if __name__ == '__main__':
    tag = sys.argv[1]   # e.g. real_K5adv_all
    r = stats(tag + '_REAL', 'inst/%s_REAL.txt' % tag)
    nulls = []
    for f in sorted(glob.glob('runs/%s_SHUF*.log' % tag)):
        p = f[5:-4]; nulls.append(stats(p, 'inst/%s.txt' % p)[:3])
    nulls = np.array(nulls)
    z = (r[0] - nulls[:, 0].mean()) / nulls[:, 0].std(ddof=1)
    print('%-22s real nats/sym %.4f ioc %.3f quad %.2f | null(n=%d) nats/sym %.4f+-%.4f max %.4f ioc %.3f+-%.3f quad %.2f+-%.2f | z %.2f' % (
        tag, r[0], r[1], r[2], len(nulls), nulls[:, 0].mean(), nulls[:, 0].std(ddof=1), nulls[:, 0].max(),
        nulls[:, 1].mean(), nulls[:, 1].std(), nulls[:, 2].mean(), nulls[:, 2].std(), z))
    flat = [x for w in r[3] for x in w][:120]
    print('   first 120 runes:', '-'.join(k.TR[x] for x in flat))
