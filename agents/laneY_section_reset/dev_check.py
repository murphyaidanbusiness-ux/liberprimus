# ABOUTME: Lane Y development check: 4 planted restart keys (chapter, page; advance, hold) attacked by lane Y and by
# ABOUTME: lane X, showing lane X is blind to restarts. Run: python -I -X utf8 agents/laneY_section_reset/dev_check.py
import random, sys, time
sys.path.insert(0, "agents/laneY_section_reset")
import numpy as np
import ylib as Y, xlib as X
words, page, chap = Y.lp2_words_meta()
print("LP2 words", len(words), "chapters", len(set(chap)), "pages", len(set(page)))
lens = [len(w) for w in words]
for label, lab in (("chapter", chap), ("page", page)):
    segw = Y.seg_ids(lab)
    for seed, variant in ((1, "advance"), (2, "hold")):
        rng = random.Random(seed)
        flat = [x for w in X.english_words(sum(lens), 100000 + 20000 * seed) for x in w]
        it = iter(flat); plain = [[next(it) for _ in range(L)] for L in lens]
        K = rng.sample(range(29), 29); offs = X.schedule(rng); dials = (rng.randrange(29), rng.randrange(29))
        cw, ph = Y.encipher_segments(plain, segw, K, offs, dials, 0, variant)
        truth = np.array(flat[:sum(lens)])
        t0 = time.time()
        rec = Y.attack(cw, segw, seed, kspaces=(0,))
        rx = None
        import pipeline as PL
        rx = PL.attack(cw, seed, kspaces=(0,))
        print("%-7s restart %-7s anchors %d: laneY s1 %+.3f agree %.3f phase %.3f | laneX (no restart) s1 %+.3f agree %.3f  (%.0fs)" % (
            label, variant, rec["anchors"], rec["s1_score"], np.mean(rec["plain"] == truth), X.phase_accuracy(rec["phase"], ph),
            rx["s1_score"], np.mean(rx["plain"] == truth), time.time() - t0))
