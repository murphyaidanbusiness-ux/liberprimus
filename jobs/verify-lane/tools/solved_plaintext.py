"""Solved Liber Primus plaintext as runes, with word and sentence ids (fresh decoder, 2026-10-19).

    import sys; sys.path.insert(0, "jobs/verify-lane/tools"); import solved_plaintext as sp
    secs = sp.build()          # list of dicts: name, method, p (plaintext rune ids), word, sent (ids per rune)
    sp.sentences(secs)         # list of plaintext rune lists, one per sentence

LP1 = lines 1-187 of the aldegonde master transcription (7 '$' segments, before LP2 page 0). The two solved LP2 pages
(AN END, PARABLE) come from our pinned loader (lp/lpdata.py pages 55-56). SOLVED-PAGES.json is not used: it drops
word and sentence marks and the plaintext F of every interrupter.

Each segment is decoded by search, not by a hard-coded key: every affine map p = s*c + d (s = +-1, d = 0..28, which
covers direct, Atbash and Atbash + shift), and the two known keywords (DIVINITY, FIRFUMFERENFE) and the totient stream
phi(prime_j) as running keys, both signs, with a beam over the F interrupters (a cipher F may be a plaintext F that
does not advance the key). The best quadgram score wins. Sentences end at '.', '&' and '$' (LP2 loader: '.', '&', '$',
'§', as lp/lpdata.py). A word ends at the word mark, a sentence mark or a number.
"""
import math
import sys

sys.path.insert(0, "lp")
sys.path.insert(0, "toolbox")
import lpdata  # noqa: E402
import score  # noqa: E402

M = 29
MASTER = "dl/aldegonde_clone/data/liber-primus__transcription--master.txt"
LP1_LINES = 187
TR = lpdata.TR
R2I = lpdata.R2I


def _primes(n):
    ps, c = [], 2
    while len(ps) < n:
        if all(c % p for p in ps if p * p <= c):
            ps.append(c)
        c += 1
    return ps


PR = _primes(3000)


def kw(s):
    out, i = [], 0
    while i < len(s):
        for L in (2, 1):
            if s[i:i + L] in TR:
                out.append(TR.index(s[i:i + L]))
                i += L
                break
        else:
            raise ValueError(s)
    return out


KEYS = {"DIVINITY": kw("DIUINITY"), "FIRFUMFERENFE": kw("FIRFUMFERENFE")}


def parse_lp1():
    """Rune stream of the LP1 region, split into the 7 '$' segments; per rune: cipher id, word id, sentence id."""
    lines = open(MASTER, encoding="utf-8").read().split("\n")[:LP1_LINES]
    segs, cur = [], dict(c=[], word=[], sent=[])
    w = s = 0
    in_num = False
    for ch in "\n".join(lines):
        if ch in R2I:
            cur["c"].append(R2I[ch]); cur["word"].append(w); cur["sent"].append(s)
            in_num = False
        elif ch in "①-":
            w += 1
        elif ch == ".":
            w += 1; s += 1
        elif ch == "&":
            w += 1; s += 1
        elif ch == "$":
            w += 1; s += 1
            segs.append(cur); cur = dict(c=[], word=[], sent=[])
        elif ch.isdigit():
            if not in_num:
                w += 1
            in_num = True
        elif ch in "/%\n":
            in_num = False
        else:
            raise ValueError(repr(ch))
    assert not cur["c"], "runes after the last $"
    return segs


def _lq():
    return score._table()


def _add(tail, sc, p, lq, floor):
    s = tail + TR[p]
    for i in range(max(0, len(tail) - 3), len(s) - 3):
        sc += lq.get(s[i:i + 4], floor)
    return s[-3:], sc


def decode_affine(c):
    lq, floor = _lq()
    best = None
    for s in (1, -1):
        for d in range(M):
            p = [(s * x + d) % M for x in c]
            q = score.quadgram(p)
            if best is None or q > best[0]:
                best = (q, p, f"affine s={s:+d} d={d}", [])
    return best


def decode_stream(c, key, sign, beam=64):
    """p = c + sign*key(j) (mod 29), j advancing on every rune except a cipher F read as a plaintext F."""
    lq, floor = _lq()
    beams = [(0.0, "", 0, [], [])]
    for i, x in enumerate(c):
        new = []
        for sc, tail, j, out, sk in beams:
            p = (x + sign * key(j)) % M
            t2, s2 = _add(tail, sc, p, lq, floor)
            new.append((s2, t2, j + 1, out + [p], sk))
            if x == 0:
                t2, s2 = _add(tail, sc, 0, lq, floor)
                new.append((s2, t2, j, out + [0], sk + [i]))
        if len(new) > beam:
            new.sort(key=lambda b: b[0], reverse=True)
            new = new[:beam]
        beams = new
    beams.sort(key=lambda b: b[0], reverse=True)
    out = beams[0][3]
    return score.quadgram(out), out, beams[0][4]


def decode(c, allow_streams=True):
    best = decode_affine(c)
    if allow_streams:
        streams = {k: (lambda j, kk=v: kk[j % len(kk)]) for k, v in KEYS.items()}
        streams["phi(prime)"] = lambda j: (PR[j] - 1) % M
        for name, fn in streams.items():
            for sign in (1, -1):
                q, p, sk = decode_stream(c, fn, sign)
                if q > best[0]:
                    best = (q, p, f"stream {name} sign={sign:+d} F-skip", sk)
    return best


def build(include_lp2_solved=True):
    secs = []
    for k, sg in enumerate(parse_lp1()):
        q, p, how, sk = decode(sg["c"])
        secs.append(dict(name=f"LP1 seg{k + 1}", method=how, quad=q, c=sg["c"], p=p, skips=sk, word=sg["word"],
                         sent=sg["sent"]))
    if include_lp2_solved:
        P = lpdata.load()
        for pg, nm in ((55, "LP2 p55 AN END"), (56, "LP2 p56 PARABLE")):
            c = list(P[pg]["idx"])
            q, p, how, sk = decode(c)
            secs.append(dict(name=nm, method=how, quad=q, c=c, p=p, skips=sk,
                             word=[10 ** 6 * pg + w for w in P[pg]["word"]],
                             sent=[10 ** 6 * pg + s for s in P[pg]["sent"]]))
    return secs


def sentences(secs, which=None, drop_skips=False):
    """Plaintext rune lists per sentence; drop_skips leaves out the F interrupters (cipher F read as plaintext F)."""
    out = []
    for sc in secs:
        if which and not which(sc["name"]):
            continue
        cur, last, sk = [], None, set(sc.get("skips", []))
        for i, (p, s) in enumerate(zip(sc["p"], sc["sent"])):
            if last is not None and s != last:
                out.append(cur); cur = []
            if not (drop_skips and i in sk):
                cur.append(p)
            last = s
        if cur:
            out.append(cur)
    return out


def words_text(sc):
    out, cur, last_w, last_s = [], "", None, None
    for p, w, s in zip(sc["p"], sc["word"], sc["sent"]):
        if last_w is not None and w != last_w:
            out.append(cur + (". " if s != last_s else " ")); cur = ""
        cur += TR[p]; last_w, last_s = w, s
    out.append(cur + ".")
    return "".join(out)


if __name__ == "__main__":
    for sc in build():
        print(f"== {sc['name']}: {len(sc['p'])} runes, {sc['method']}, quadgram {sc['quad']:.3f}, "
              f"F interrupters at {sc['skips']}")
        print(words_text(sc))
