"""Check common.enc_walk against aldegonde's doublet_dodge_walk.encipher (source extracted with ast; the module's
imports need scipy), and check kwdec decrypts planted text exactly."""
import ast, random, subprocess, json
from common import *
src = open(S + '/dl/aldegonde_clone/aldegonde/experiments/doublet_dodge_walk.py').read()
tree = ast.parse(src); ns = {}
need = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('encipher', 'ppow', 'compose')]
names = [n.name for n in need]
code = compile(ast.Module(body=need, type_ignores=[]), 'ddw', 'exec')
ns['M'] = 29
exec(code, ns)
if 'ppow' not in names or 'compose' not in names:
    # fall back to the helpers defined in the module's imports
    for mod in ('fingerprint_battery', 'quagmire_walk_sim'):
        pass
print('extracted:', names)
if 'ppow' not in ns: ns['ppow'] = lambda g, k: ppow(list(g), k)
if 'compose' not in ns: ns['compose'] = lambda a, b: [a[x] for x in b]
rng = random.Random(5); WP = wp_words()
for trial in range(20):
    b0 = list(range(29)); rng.shuffle(b0); s = list(range(29)); rng.shuffle(s)
    g = structured_g_oosterhof(sorted(rng.sample(range(29), 4)))
    o = rng.randrange(400000); words = [list(w) for w in WP[o:o + 200]]
    assert enc_walk(words, b0, g, s) == [list(c) for c in ns['encipher'](words, b0, g, s)]
print('common.enc_walk == aldegonde encipher on 20 random keys x 200 words')
# kwdec round trip on the planted page
d = json.load(open(OUT + '/texts/plant1.json'))
open(OUT + '/runs/rt_keys.txt', 'w').write('0 %d %d %d\n' % (d['b'], d['g'], d['s']))
subprocess.run([OUT + '/kwdec', OUT + '/texts/plant1.txt', OUT + '/runs/rt_keys.txt', OUT + '/runs/rt_out.txt', '16'], check=True, cwd=OUT)
got = [int(x) for x in open(OUT + '/runs/rt_out.txt').read().split(':')[1].split()]
truth = [x for w in d['plain'] for x in w]
print('kwdec round trip on plant1 (262 runes): %d/%d runes correct' % (sum(a == b for a, b in zip(got, truth)), len(truth)))
# longer round trip: 3000 runes of W&P under a random keyword key, kwdec beam 16
A = np.fromfile(OUT + '/A.bin', dtype=np.uint8).reshape(-1, 29); G = np.fromfile(OUT + '/G.bin', dtype=np.uint8).reshape(-1, 29)
for trial in range(3):
    bi, gi, si = rng.randrange(len(A)), rng.randrange(len(G)), rng.randrange(len(A))
    o = rng.randrange(400000); words = [list(w) for w in WP[o:o + 700]]
    for mode, kw in ((0, {}), (1, {'reset': True}), (2, {'fixed': True})):
        C = enc_walk(words, list(A[bi]), list(G[gi]), list(A[si]), **kw)
        write_text(OUT + '/runs/rt_text.txt', C)
        open(OUT + '/runs/rt_keys.txt', 'w').write('%d %d %d %d\n' % (mode, bi, gi, si if mode != 2 else -1))
        subprocess.run([OUT + '/kwdec', OUT + '/runs/rt_text.txt', OUT + '/runs/rt_keys.txt', OUT + '/runs/rt_out.txt', '16'], check=True, cwd=OUT)
        got = [int(x) for x in open(OUT + '/runs/rt_out.txt').read().split(':')[1].split()]
        truth = [x for w in words for x in w]
        print('kwdec round trip mode %d, %d runes: accuracy %.4f' % (mode, len(truth), np.mean([a == b for a, b in zip(got, truth)])))
