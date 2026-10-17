# Aggregate keystream.c (model f) outputs: real vs D-shuffle null.
import sys, glob, math, collections
IDI = ["PY2","PY3","PYGM","MTMOD","NPR53","NPINT","STDUID","PHP7R","PHP7M","PHP5R","PHP5M","GLMOD","GLSC","GLDIV","MSMOD","MSSC","JINT","JDBL","D48"]
APP = ["A+","A-","M*","M/"]; CONV = ["X,C","Y,C","X,R","Y,R"]
def vname(v): return APP[v // 4] + " " + CONV[v % 4]
def load(pat):
    S = collections.defaultdict(lambda: [0, 0.0, 0.0]); H = collections.defaultdict(collections.Counter); T = collections.defaultdict(list); seeds = 0
    for fn in glob.glob(pat):
        for l in open(fn):
            t = l.split()
            if t[0] == 'SEEDS': seeds += int(t[1])
            elif t[0] == 'S':
                k = (int(t[1]), int(t[2])); S[k][0] += int(t[3]); S[k][1] += float(t[4]); S[k][2] += float(t[5])
            elif t[0] == 'H': H[(int(t[1]), int(t[2]))][int(t[3])] += int(t[4])
            elif t[0] == 'T': T[(int(t[1]), int(t[2]))].append((float(t[3]), ' '.join(t[4:])))
    for k in T: T[k].sort(reverse=True)
    return seeds, S, H, T
def report(prefix, label):
    rs, RS, RH, RT = load(prefix + '_real_*.txt')
    ns, NS, NH, NT = load(prefix + '_null_*_*.txt')
    out = []
    ntr = sum(v[0] for v in RS.values()); nnu = sum(v[0] for v in NS.values())
    out.append('### %s\nreal: %d seed lines, %d (seed x idiom x decode) trials; null: %d trials on 20 D-shuffled corpora\n' % (label, rs, ntr, nnu))
    # null per-stream mean/sd pooled
    n = sum(v[0] for v in NS.values()); m = sum(v[1] for v in NS.values()) / n; sd = math.sqrt(sum(v[2] for v in NS.values()) / n - m * m)
    rbest = max(((T[0][0], k, T[0][1]) for k, T in RT.items()), default=None)
    nbest = max(((T[0][0], k, T[0][1]) for k, T in NT.items()), default=None)
    out.append('null per-trial IoC mean %.5f sd %.5f; real overall max %.5f (%s, %s, seed %s) z=%.2f; null overall max %.5f z=%.2f\n' % (
        m, sd, rbest[0], IDI[rbest[1][0]], vname(rbest[1][1]), rbest[2], (rbest[0] - m) / sd, nbest[0], (nbest[0] - m) / sd))
    # expected max scaling: compare at equal trial counts via tail fractions
    for thr in (1.030, 1.032, 1.034, 1.036, 1.040, 1.050):
        b = int(math.floor((thr - 0.95) / 0.0005))
        rf = sum(c for H in RH.values() for bb, c in H.items() if bb >= b) / ntr
        nf = sum(c for H in NH.values() for bb, c in H.items() if bb >= b) / nnu
        out.append('  fraction of trials with IoC >= %.3f: real %.3g, null %.3g\n' % (thr, rf, nf))
    out.append('\n| idiom | best decode | real max IoC | seed | null max (same idiom, all decodes) |\n|---|---|---|---|---|\n')
    for a in range(len(IDI)):
        ks = [k for k in RT if k[0] == a]
        if not ks: continue
        b = max(((RT[k][0][0], k, RT[k][0][1]) for k in ks))
        nb = max((NT[k][0][0] for k in NT if k[0] == a), default=float('nan'))
        out.append('| %s | %s | %.5f | %s | %.5f |\n' % (IDI[a], vname(b[1][1]), b[0], b[2], nb))
    return ''.join(out), rbest, nbest, m, sd
if __name__ == '__main__':
    d = sys.argv[1]
    for pre, lab in ((d + '/f', 'model f: one key stream per seed (continuous and per-page restart)'), (d + '/fpp', 'model f, fresh seed per page (seed = s + page index)')):
        print(report(pre, lab)[0])
