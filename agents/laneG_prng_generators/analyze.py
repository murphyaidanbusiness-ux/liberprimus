# Aggregate search.c shard outputs: per (idiom, model, statistic) real best vs null (20 D-shuffled corpora).
import sys, glob, math, collections, json
IDI = ["PY2","PY3","PYGM","MTMOD","NPR53","NPINT","STDUID","PHP7R","PHP7M","PHP5R","PHP5M","GLMOD","GLSC","GLDIV","MSMOD","MSSC","JINT","JDBL","D48"]
MOD = ["a","b","c","d","s","e","e0"]
ST = ["exact","pattern","hamming"]
NNULL = 20
def load(pattern):
    seeds = 0; N = collections.Counter(); HR = collections.defaultdict(collections.Counter); HN = collections.defaultdict(collections.Counter)
    TOP = collections.defaultdict(list)
    for fn in sorted(glob.glob(pattern)):
        for line in open(fn):
            t = line.split()
            if not t: continue
            if t[0] == 'SEEDS': seeds += int(t[1])
            elif t[0] == 'N': N[(int(t[1]), int(t[2]))] += int(t[3])
            elif t[0] == 'H':
                k = (int(t[1]), int(t[2]), int(t[3])); v = int(t[4]); HR[k][v] += int(t[5]); HN[k][v] += int(t[6])
            elif t[0] == 'T':
                k = (int(t[1]), int(t[2]), int(t[3])); TOP[k].append((int(t[4]), int(t[5]), int(t[6]), ' '.join(t[7:])))
    for k in TOP: TOP[k].sort(key=lambda x: -x[0])
    return seeds, N, HR, HN, TOP
def summarize(pattern):
    seeds, N, HR, HN, TOP = load(pattern)
    rows = []
    for (a, m, s), hr in sorted(HR.items()):
        n = N[(a, m)]
        rmax = max(hr)
        hn = HN[(a, m, s)]
        if s == 2:   # hamming: no stored null; analytic Binomial(64,1/29) over 55 pages x (NG-64) offsets per stream
            null_exp = None; pval = None
        else:
            tot = sum(hn.values())
            # per-stream null CDF; P(global max over n streams >= rmax)
            ge = sum(c for v, c in hn.items() if v >= rmax) / tot if tot else 0
            pval = 1 - (1 - ge) ** n if ge < 1 else 1.0
            # expected null global max: smallest v with F(v)^n >= 0.5
            cum = 0; null_exp = None
            for v in sorted(hn):
                cum += hn[v]
                if (cum / tot) ** n >= 0.5: null_exp = v; break
        rows.append(dict(idiom=IDI[a], model=MOD[m], stat=ST[s], streams=n, real_max=rmax, null_median_max=null_exp, p_global=pval,
                         real_ge_max=hr[rmax], top=TOP[(a, m, s)][:3]))
    return seeds, rows, HR, HN, N, TOP
if __name__ == '__main__':
    seeds, rows, HR, HN, N, TOP = summarize(sys.argv[1])
    print('seed lines', seeds, 'streams', sum(N.values()))
    for r in rows:
        print('%-7s %-3s %-8s n=%-8d real_max=%-4d null_med_max=%-5s p=%-8s top=%s' % (r['idiom'], r['model'], r['stat'], r['streams'], r['real_max'],
              r['null_median_max'], ('%.3g' % r['p_global']) if r['p_global'] is not None else '-', r['top'][:1]))
