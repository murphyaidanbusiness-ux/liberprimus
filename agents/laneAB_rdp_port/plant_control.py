"""Lane AB control: plant a Vigenere key on solved text and recover it by search, with RDP's scorer as the fitness.

Plants (seeded, independent of RDP): 20 windows of the solved LP1 plaintext (dl/dukotah/liber-primus/SOLVED-PAGES.json,
transliterations -> rune indices as lp/t2_multseq.py does; no word boundaries) and 20 windows of English with word
boundaries (toolbox/runes.english_stream, Moby-Dick). Each window is 260 runes (an LP2 page) enciphered as
c = (p + k[i mod period]) mod 29 with a random key of period 2-9.

Search (identical for every scorer): coordinate ascent over the key, 3 random restarts; a round tries all 29 values of
each key position in turn (one batch of 29 candidates per position) and keeps the best; a restart ends after a round
with no change or 8 rounds. The best-scoring final key over the restarts is the answer; recovered = equal to the plant.

Scorers:
  rdp_default   RDP default config (char + WLI lanes, order 2, percentile log-prob, window 10) - English plants only
  rdp_char_pct  RDP char lane only, order 2, percentile log-prob, window 10
  rdp_char_avg  RDP char lane only, order 2, average log-probability (no ECDF)
  ours_quad     toolbox/score.quadgram (our existing scorer), as the baseline
  rdp_char4_pct / rdp_char4_avg / rdp_default4  the same at order 4 (only with --lm4, needs the LM-large assets);
                rdp_default4 is RDP's default lanes (char + WLI) at order 4, English plants only
All RDP scores go through rdp.api.score_many (agents/laneAB_rdp_port/rdp_scorer.py).

    python -I agents/laneAB_rdp_port/plant_control.py [--tier easy|hard] [--limit N] [--scorers a,b] [--lm4]
Tier easy (default): 260-rune windows, periods 2-9, results in out_plants.jsonl. Tier hard: 100-rune windows, periods
6-12 (10-17 runes per key position), results in out_plants_hard.jsonl. One line per (scorer, plant); a rerun skips
finished pairs. The summary (recovered k/n per scorer, misses listed) is printed from the jsonl.
"""
import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
os.chdir(ROOT)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'toolbox'))
sys.path.insert(0, os.path.join(ROOT, 'lp'))
import lpdata  # noqa: E402
import runes as RN  # noqa: E402
import score as SC  # noqa: E402

TIERS = {'easy': dict(out='out_plants.jsonl', L=260, pmin=2, pmax=9),
         'hard': dict(out='out_plants_hard.jsonl', L=100, pmin=6, pmax=12)}
OUT = os.path.join(HERE, TIERS['easy']['out'])
SEED = 20261019
L = TIERS['easy']['L']
PMIN, PMAX = TIERS['easy']['pmin'], TIERS['easy']['pmax']
N_EACH = 20
ROUNDS = 8
RESTARTS = 3


def solved_lp1():
    sp = json.load(open('dl/dukotah/liber-primus/SOLVED-PAGES.json', encoding='utf-8'))
    out = []
    for pg in sp['pages']:
        s, i = pg['plaintext_transliteration'], 0
        while i < len(s):
            for k in (2, 1):
                if s[i:i + k] in lpdata.TR:
                    out.append(lpdata.TR.index(s[i:i + k]))
                    i += k
                    break
            else:
                i += 1
    return out


def make_plants():
    rng = random.Random(SEED)
    lp1 = solved_lp1()
    eng, wid = RN.english_stream(60000)
    plants = []
    for src in ('lp1', 'eng'):
        for j in range(N_EACH):
            period = rng.randint(PMIN, PMAX)
            key = [rng.randrange(29) for _ in range(period)]
            if src == 'lp1':
                a = rng.randrange(0, len(lp1) - L)
                pt, words = lp1[a:a + L], None
            else:
                a = rng.randrange(0, len(eng) - L)
                pt, words = eng[a:a + L], wid[a:a + L]
            ct = [(p + key[i % period]) % 29 for i, p in enumerate(pt)]
            plants.append(dict(id='%s%02d' % (src, j), src=src, start=a, period=period, key=key, pt=pt, ct=ct,
                               words=words))
    return plants, len(lp1)


def decrypt(ct, key):
    P = len(key)
    return [(c - key[i % P]) % 29 for i, c in enumerate(ct)]


def scorer_fn(name):
    """name -> (batch scoring function taking (list of rune lists, words or None), needs_words)."""
    if name == 'ours_quad':
        return (lambda seqs, words: [SC.quadgram(s) for s in seqs]), False
    import rdp_scorer as RS
    cfg = {
        'rdp_default': dict(),
        'rdp_char_pct': dict(wli=False),
        'rdp_char_avg': dict(wli=False, objective='avg_logp'),
        'rdp_char4_pct': dict(wli=False, char_order=4),
        'rdp_char4_avg': dict(wli=False, char_order=4, objective='avg_logp'),
        'rdp_default4': dict(char_order=4, wli_order=4),
    }[name]
    s = RS.RDPScorer(**cfg)
    probe = make_plants()[0][-3:]
    d = s.check_against_api([p['pt'] for p in probe] + [p['ct'] for p in probe],
                            [p['words'] for p in probe] * 2 if s.needs_words else None)
    print('%s: batch path vs rdp.api.score_many max |diff| = %g on 6 candidates' % (name, d), flush=True)
    assert d == 0.0, d
    return (lambda seqs, words: s.score_many(seqs, [words] * len(seqs) if words is not None else None)), s.needs_words


def search(ct, period, fn, words, rng):
    best_key, best_sc, evals = None, -1e300, 0
    for _ in range(RESTARTS):
        key = [rng.randrange(29) for _ in range(period)]
        cur = fn([decrypt(ct, key)], words)[0]
        evals += 1
        for _r in range(ROUNDS):
            changed = False
            for j in range(period):
                cands = []
                for v in range(29):
                    k2 = list(key)
                    k2[j] = v
                    cands.append(decrypt(ct, k2))
                scs = fn(cands, words)
                evals += 29
                v = max(range(29), key=lambda t: scs[t])
                if scs[v] > cur and v != key[j]:
                    key[j], cur, changed = v, scs[v], True
            if not changed:
                break
        if cur > best_sc:
            best_key, best_sc = list(key), cur
    return best_key, best_sc, evals


def done_pairs():
    s = set()
    if os.path.exists(OUT):
        for ln in open(OUT, encoding='utf-8'):
            r = json.loads(ln)
            s.add((r['scorer'], r['plant']))
    return s


def summary():
    rows = [json.loads(ln) for ln in open(OUT, encoding='utf-8')] if os.path.exists(OUT) else []
    by = {}
    for r in rows:
        by.setdefault(r['scorer'], []).append(r)
    print('scorer | recovered k/n (lp1, eng) | true key scores >= found (search miss, not scorer miss) | sec/plant | misses')
    for name in sorted(by):
        rs = sorted(by[name], key=lambda r: r['plant'])
        k = sum(r['recovered'] for r in rs)
        k1 = sum(r['recovered'] for r in rs if r['src'] == 'lp1')
        n1 = sum(1 for r in rs if r['src'] == 'lp1')
        k2 = sum(r['recovered'] for r in rs if r['src'] == 'eng')
        n2 = sum(1 for r in rs if r['src'] == 'eng')
        sm = sum(1 for r in rs if not r['recovered'] and r['true_score'] >= r['found_score'])
        miss = ['%s(p%d,%s)' % (r['plant'], r['period'], 'search' if r['true_score'] >= r['found_score'] else 'scorer')
                for r in rs if not r['recovered']]
        sec = sum(r['seconds'] for r in rs) / len(rs)
        print('%s | %d/%d (%d/%d, %d/%d) | %d | %.1f | %s' % (name, k, len(rs), k1, n1, k2, n2, sm, sec,
                                                            ' '.join(miss) or 'none'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0, help='stop after this many new (scorer, plant) tasks')
    ap.add_argument('--scorers', default='rdp_default,rdp_char_pct,rdp_char_avg,ours_quad')
    ap.add_argument('--lm4', action='store_true', help='add the order-4 RDP scorers')
    ap.add_argument('--summary', action='store_true')
    ap.add_argument('--tier', default='easy', choices=sorted(TIERS))
    a = ap.parse_args()
    global OUT, L, PMIN, PMAX
    t = TIERS[a.tier]
    OUT, L, PMIN, PMAX = os.path.join(HERE, t['out']), t['L'], t['pmin'], t['pmax']
    sys.stdout.reconfigure(encoding='utf-8')
    if a.summary:
        summary()
        return
    plants, nlp1 = make_plants()
    names = a.scorers.split(',') + (['rdp_char4_pct', 'rdp_char4_avg', 'rdp_default4'] if a.lm4 else [])
    done = done_pairs()
    new = 0
    print('tier %s: plants %d (solved LP1 stream %d runes; English with word ids); window %d; periods %d-%d; seed %d' %
          (a.tier, len(plants), nlp1, L, PMIN, PMAX, SEED))
    for name in names:
        fn, needs_words = scorer_fn(name)
        for pl in plants:
            if needs_words and pl['words'] is None:
                continue
            if (name, pl['id']) in done:
                print('skip %s %s (already in %s)' % (name, pl['id'], os.path.basename(OUT)))
                continue
            if a.limit and new >= a.limit:
                summary()
                return
            rng = random.Random('%d-%s-%s' % (SEED, name, pl['id']))
            words = pl['words'] if needs_words else None
            t0 = time.time()
            key, sc, evals = search(pl['ct'], pl['period'], fn, words, rng)
            dt = time.time() - t0
            true_sc = fn([pl['pt']], words)[0]
            rec = dict(scorer=name, plant=pl['id'], src=pl['src'], period=pl['period'], key=pl['key'],
                       found=key, recovered=key == pl['key'], found_score=sc, true_score=true_sc,
                       evals=evals, seconds=round(dt, 2))
            with open(OUT, 'a', encoding='utf-8') as fh:
                fh.write(json.dumps(rec) + '\n')
            new += 1
            print('%s %s p%d recovered=%s found=%.4f true=%.4f evals=%d %.1fs' %
                  (name, pl['id'], pl['period'], rec['recovered'], sc, true_sc, evals, dt), flush=True)
    summary()


def peak_mb():
    """Peak working set of this process (Windows), in MB."""
    import ctypes
    from ctypes import wintypes

    class PMC(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (f, ctypes.c_size_t) for f in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage',
                                           'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                                           'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    c = PMC()
    c.cb = ctypes.sizeof(PMC)
    k32 = ctypes.WinDLL('kernel32')
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    gpmi = ctypes.WinDLL('psapi').GetProcessMemoryInfo
    gpmi.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
    gpmi(k32.GetCurrentProcess(), ctypes.byref(c), c.cb)
    return c.PeakWorkingSetSize / 2 ** 20


if __name__ == '__main__':
    main()
    if sys.platform == 'win32':
        print('peak working set %.0f MB' % peak_mb())
