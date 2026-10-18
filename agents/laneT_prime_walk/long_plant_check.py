"""Beam sufficiency check: plant full-length English (LP2 length, 12,956 runes) under a known key and decode it with
the beam widths used in the run. A true key that dies before the end, or decodes to a different path, means the beam
loses the true path and a full-length LP2 survival count is not evidence either way."""
import os, sys, random, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tdec, runes
REPO = tdec.REPO
os.chdir(REPO)
sim = tdec.load_sim()
N = 12956
out = []
rng = random.Random(4242)
for trial, W in [(t, w) for t in range(4) for w in (512, 4096)]:
    kk = rng.randrange(20000)
    kind, k0 = tdec.key_of(kk)
    plain, words = runes.english_stream(N, skip_chars=20000 + 3000 * trial)
    plain, words = list(plain), list(words)
    g, s, b = sim.keys_from(kind, k0)
    c = sim.walk(plain, words, g, s, b)
    dec = tdec.Decoder(W=W)
    t0 = time.time()
    alive, mean, sc, nw, path = dec.decode(c, words, kk, track=True)
    p = list(path)
    first_diff = next((i for i in range(min(len(p), N)) if p[i] != plain[i]), None)
    rec = dict(trial=trial, W=W, kk=kk, key=[kind, k0], planted_len=N, alive=int(alive), mean=round(float(mean), 4),
               exact=(p == plain), first_diff=first_diff, seconds=round(time.time() - t0, 1))
    out.append(rec)
    print(json.dumps(rec), flush=True)
json.dump(out, open(os.path.join(tdec.OUT, "long_plant_check.json"), "w"), indent=1)
