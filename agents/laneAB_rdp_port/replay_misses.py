"""Lane AB, SKILL step 6: replay every scorer miss of the plant control (the found key outscored the true key) with the
same key and scorer on fresh plaintext windows of the same source and length, before blaming the port or the scorer.

    python -I agents/laneAB_rdp_port/replay_misses.py --tier hard [--fresh 5]
"""
import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import plant_control as PC  # noqa: E402  (sets cwd and paths)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tier', default='hard', choices=sorted(PC.TIERS))
    ap.add_argument('--fresh', type=int, default=5)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    t = PC.TIERS[a.tier]
    PC.OUT, PC.L, PC.PMIN, PC.PMAX = os.path.join(HERE, t['out']), t['L'], t['pmin'], t['pmax']
    rows = [json.loads(ln) for ln in open(PC.OUT, encoding='utf-8')]
    misses = [r for r in rows if not r['recovered'] and r['true_score'] < r['found_score']]
    print('tier %s: %d scorer misses (found key outscored the true key); %d fresh windows each, length %d' %
          (a.tier, len(misses), a.fresh, PC.L))
    if not misses:
        return
    lp1 = PC.solved_lp1()
    eng, wid = PC.RN.english_stream(60000)
    fns = {}
    for r in misses:
        if r['scorer'] not in fns:
            fns[r['scorer']] = PC.scorer_fn(r['scorer'])
        fn, needs_words = fns[r['scorer']]
        rng = random.Random('replay-%s-%s' % (r['scorer'], r['plant']))
        got = []
        for _ in range(a.fresh):
            if r['src'] == 'lp1':
                s = rng.randrange(0, len(lp1) - PC.L)
                pt, words = lp1[s:s + PC.L], None
            else:
                s = rng.randrange(0, len(eng) - PC.L)
                pt, words = eng[s:s + PC.L], wid[s:s + PC.L]
            ct = [(p + r['key'][i % r['period']]) % 29 for i, p in enumerate(pt)]
            key, sc, _ = PC.search(ct, r['period'], fn, words if needs_words else None, rng)
            got.append(key == r['key'])
        print('%s %s period %d key %s: original window found %.4f > true %.4f; fresh windows recovered %d/%d' %
              (r['scorer'], r['plant'], r['period'], r['key'], r['found_score'], r['true_score'], sum(got), len(got)))


if __name__ == '__main__':
    main()
