"""Lane AB step 1: RuneDecrypterPrime v1.0.0's transcription (master-v2) against the pin, rune by rune, per page.

Run from the repository root (reads data files only; no RDP code runs):
    python -I agents/laneAB_rdp_port/diff_v2.py > agents/laneAB_rdp_port/out_diff_v2.txt

Reuses lane R's loaders and statistics (agents/laneR_transcriptions/transcriptions.py, compare.py); lane R's files
are imported, not modified. Families added here:
  V2   RDP assets/liber_primus/liber-primus__transcription--master-v2.txt, RDP's own word-break rule
       (lp_transcript.Delimiters.word_breakers: - , . ; " ' and every [dot_N] tag; & $ section and / do not end a word)
  V2K  the same file with the loader's rule added (& $ section also start a word)
  RV1  RDP assets/liber_primus/liber-primus__transcription--master.txt (the "historical" v1 RDP ships), RDP rule
Tag handling follows RDP's README and parser: [red] and [/red] are dropped (colour only), each [dot_N...] tag becomes
one punctuation mark (written here as U+00B7), digits and letters are not runes and not separators, the delimiter
legend before the first blank line is skipped.
"""
import sys
import os
import re
import hashlib
import difflib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'agents', 'laneR_transcriptions'))
sys.path.insert(0, os.path.join(ROOT, 'lp'))
import transcriptions as T  # noqa: E402
import compare as C  # noqa: E402

PIN = '023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'
V2 = 'dl/rdp/assets/liber_primus/liber-primus__transcription--master-v2.txt'
RV1 = 'dl/rdp/assets/liber_primus/liber-primus__transcription--master.txt'
DOT = '·'
DOT_RE = re.compile(r'\[dot_[1-9][0-9]*(?:_[A-Za-z0-9]+)*\]')
WS_RDP = {'-', ',', '.', ';', '"', "'", DOT}
WS_V2K = WS_RDP | {'&', '$', '§'}


def body(text):
    """Drop the delimiter legend (RDP: the body starts after the first blank line when line 1 is 'Delimiters')."""
    lines = text.replace('\r', '').split('\n')
    if lines and lines[0].strip().lower().startswith('delimiters'):
        for i, ln in enumerate(lines):
            if i > 0 and ln.strip() == '':
                return '\n'.join(lines[i + 1:])
    return '\n'.join(lines)


def tokenize_v2(s):
    s = s.replace('[red]', '').replace('[/red]', '')
    s = DOT_RE.sub(DOT, s)
    assert '[' not in s and ']' not in s, 'unknown tag left'
    out = []
    for ch in s:
        if ch in T.CP2I:
            out.append(T.CP2I[ch])
        elif ch.isspace() or ch.isascii() and ch.isalnum():
            continue
        else:
            out.append(ch)
    return out


def load_units(rel):
    """Body (legend dropped) split at '%', labelled by unit index: unit k = RDP main-transcript page ID k, and RDP's
    canonical LP page = k - 15 (README: LP pages 0-57 are main-transcript page IDs 15-72)."""
    t = body(T.read(rel))
    return [(k, tokenize_v2(u)) for k, u in enumerate(t.split('%'))]


PATHS = {'V2': V2, 'V2K': V2, 'RV1': RV1}
_orig_load = T.load


def load_patched(name):
    if name in PATHS:
        return load_units(PATHS[name])
    return _orig_load(name)


T.load = load_patched
C.FAMILIES['V2'] = ('RDP v1.0.0 master-v2 (RDP word rule)', WS_RDP, True)
C.FAMILIES['V2K'] = ('RDP v1.0.0 master-v2 (loader word rule: & $ section added)', WS_V2K, True)
C.FAMILIES['RV1'] = ('RDP v1.0.0 historical master v1 (RDP word rule)', WS_RDP, True)


def place(units, kpages):
    """Non-empty units placed on pin pages 0-54 by the best offset (lane R's scoring). Returns [(label, page)]."""
    pages = [(lab, pg) for lab, pg in C.pages_from_units(units) if pg]
    best, bo = -1, 0
    for o in range(0, len(pages) - C.NP + 1):
        sc = sum(C.page_score([i for i, _ in kpages[p]], [i for i, _ in pages[o + p][1]]) for p in range(C.NP))
        if sc > best:
            best, bo = sc, o
    return pages[bo:bo + C.NP], bo, best


def ops_count(a, b):
    c = Counter()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == 'replace':
            n = min(i2 - i1, j2 - j1)
            c['sub'] += n
            c['del'] += (i2 - i1) - n
            c['ins'] += (j2 - j1) - n
        elif tag == 'delete':
            c['del'] += i2 - i1
        elif tag == 'insert':
            c['ins'] += j2 - j1
        else:
            c['eq'] += i2 - i1
    return c


def show(pre):
    return ''.join(ch if ord(ch) < 128 else ('DOT' if ch == DOT else 'u%04x' % ord(ch)) for ch in pre) or '(none)'


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    kpages, Kc, Kw = C.loader_reference()
    kraw, _ = C.map_paged('K', T.load('K'), kpages)
    Kpre = [p for pg in kraw for _, p in pg]
    print('pin (lp/lpdata.py): pages 0-54 = %d runes, sha %s (asserted)' % (len(Kc), PIN))
    print('   %s' % C.fmt(C.stats(Kc, Kw)))
    for rel in (V2, RV1, 'dl/aldegonde_clone/data/liber-primus__transcription--master.txt'):
        raw = open(os.path.join(ROOT, rel), 'rb').read()
        rn = ''.join(ch for ch in raw.decode('utf-8') if 0x16A0 <= ord(ch) <= 0x16FF)
        print('file %s: %d bytes, sha256 %s; runic chars %d, runic-stream sha12 %s' %
              (rel, len(raw), hashlib.sha256(raw).hexdigest(), len(rn), hashlib.sha256(rn.encode()).hexdigest()[:12]))

    # ---- direct per-page comparison (independent of lane R's analyse) ----
    results = {}
    for name in ('V2', 'RV1'):
        units = load_units(PATHS[name])
        placed, bo, best = place(units, kpages)
        idx = [i for _, pg in placed for i, _ in pg]
        sha = hashlib.sha256(','.join(map(str, idx)).encode()).hexdigest()
        print('\n== %s direct: placement offset %d (non-empty units skipped before pin page 0), %d runes matched;'
              ' LP2 runes %d, comma-joined sha %s, equals pin: %s' % (name, bo, best, len(idx), sha, sha == PIN))
        results[name] = placed
    # per-page table for V2, with RDP page numbers and boundary disagreements under both word rules
    placed = results['V2']
    placed1 = results['RV1']
    kstart = [0]
    for pg in kpages:
        kstart.append(kstart[-1] + len(pg))
    vpre = [x for _, pg in placed for _, x in pg]
    vflags = {rule: C.word_flags(vpre, ws) for rule, ws in (('rdp', WS_RDP), ('ldr', WS_V2K))}
    rows = []
    allb = []
    tot = Counter()
    print('\npin page | RDP page ID | RDP LP page | pin start | pin runes | v2 runes | identical | sub ins del |'
          ' word-start disagreements vs pin: RDP rule (lacking/extra), loader rule (lacking/extra) | v1->v2 runes equal')
    for p in range(C.NP):
        lab, pg = placed[p]
        k = [i for i, _ in kpages[p]]
        f = [i for i, _ in pg]
        c = ops_count(k, f)
        tot.update(c)
        same = k == f
        pre = [x for _, x in pg]
        b = {}
        for rule in ('rdp', 'ldr'):
            fw = vflags[rule][kstart[p]:kstart[p + 1]]   # flat flags: a word may continue across a page break
            kw = Kw[kstart[p]:kstart[p + 1]]
            lack = extra = 0
            if same:
                for j in range(len(k)):
                    if j == 0 and p == 0:
                        continue
                    if kw[j] and not fw[j]:
                        lack += 1
                        allb.append((rule, p, j, kstart[p] + j, 'lacking', Kpre[kstart[p] + j], pre[j]))
                    elif fw[j] and not kw[j]:
                        extra += 1
                        allb.append((rule, p, j, kstart[p] + j, 'extra', Kpre[kstart[p] + j], pre[j]))
            b[rule] = (lack, extra)
        v1same = [i for i, _ in placed1[p][1]] == f
        rows.append((p, lab, lab - 15, kstart[p], len(k), len(f), same, c['sub'], c['ins'], c['del'],
                     b['rdp'], b['ldr'], v1same))
        print('p%02d | %d | %d | %d | %d | %d | %s | %d %d %d | %d/%d, %d/%d | %s' %
              (p, lab, lab - 15, kstart[p], len(k), len(f), same, c['sub'], c['ins'], c['del'],
               b['rdp'][0], b['rdp'][1], b['ldr'][0], b['ldr'][1], v1same))
    print('total: substitutions %d, insertions %d, deletions %d; identical positions %d of %d' %
          (tot['sub'], tot['ins'], tot['del'], tot['eq'], len(Kc)))
    with open(os.path.join(HERE, 'per_page_v2.tsv'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('pin_page\trdp_page_id\trdp_lp_page\tpin_start\tpin_runes\tv2_runes\tidentical\tsub\tins\tdel\t'
                 'ws_lacking_rdp\tws_extra_rdp\tws_lacking_loader\tws_extra_loader\tv1_v2_runes_equal\n')
        for r in rows:
            fh.write('\t'.join(str(x) for x in (r[:10] + r[10] + r[11] + (r[12],))) + '\n')
    print('\nword-start disagreements on identical runes (rule, pin page, rune in page, flat index, kind, pin marks, v2 marks):')
    for rule, p, j, g, kind, kp, fp in allb:
        print('   %s p%02d+%d (flat %d): v2 %s a pin word start; pin marks %s, v2 marks %s' %
              (rule, p, j, g, 'lacks' if kind == 'lacking' else 'adds', show(kp), show(fp)))

    # ---- v1 -> v2 boundary changes inside LP2 (RDP rule) ----
    print('\nv1 -> v2 word-start changes on pin pages 0-54 (RDP rule):')
    n = 0
    v1 = [x for _, pg in placed1 for x in pg]
    v2 = [x for _, pg in placed for x in pg]
    assert [i for i, _ in v1] == [i for i, _ in v2], 'v1 and v2 rune streams differ on pin pages 0-54'
    fa = C.word_flags([x for _, x in v1], WS_RDP)
    fb = C.word_flags([x for _, x in v2], WS_RDP)
    for g in range(1, len(v1)):
        if fa[g] != fb[g]:
            n += 1
            p = max(q for q in range(C.NP) if kstart[q] <= g)
            print('   p%02d+%d (flat %d): v1 word start %d -> v2 %d; v1 marks %s, v2 marks %s' %
                  (p, g - kstart[p], g, fa[g], fb[g], show(v1[g][1]), show(v2[g][1])))
    print('   %d changes' % n)

    # ---- statistics on the v2 stream (flat, own boundaries) ----
    flat = [x for _, pg in placed for x in pg]
    V = [i for i, _ in flat]
    print('\nstatistics on the v2 LP2 stream (own runes, own word starts):')
    for rule, ws in (('RDP rule', WS_RDP), ('loader rule', WS_V2K)):
        w = C.word_flags([x for _, x in flat], ws)
        print('   %-11s %s' % (rule, C.fmt(C.stats(V, w))))
    print('   pin         %s' % C.fmt(C.stats(Kc, Kw)))

    # ---- lane R's own pipeline on the new families (same code path as lane R's table) ----
    print('\n######## lane R pipeline (compare.analyse) ########')
    rows_out = []
    for nm in ('V2', 'V2K', 'RV1'):
        label, ws, paged = C.FAMILIES[nm]
        C.analyse(nm, label, ws, paged, False, kpages, Kc, Kw, Kpre, rows_out)
    print('\nper-page rows from analyse (family, pin page, pin runes, sub, ins, del): %s' % (rows_out or 'none'))


if __name__ == '__main__':
    main()
