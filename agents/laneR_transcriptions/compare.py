"""Lane R: is the doublet deficit and the within-word lag-5 echo robust to the choice of transcription?

Run from the repository root (lpdata reads ./dl relative paths):
    python -I agents/laneR_transcriptions/compare.py > agents/laneR_transcriptions/out_compare.txt

Pipeline
  1. Load each transcription under dl/ (transcriptions.py) and place its runes on loader pages 0-54.
  2. Reference = lp/lpdata.py, asserted to reproduce sha 023312066df4...
  3. Align each family to the reference: per page for paged files (difflib), whole stream for flat files.
     Counts: substitutions, insertions, deletions, and word-boundary disagreements on aligned runes.
  4. Statistics on the flat rune stream (reference positions unless stated):
       ref  : reference runes, reference boundaries
       subs : reference boundaries + the family's substitutions only (indels leave the reference symbol)
       bnd  : reference runes + the family's word boundaries where aligned
       own  : the family's full stream (runes + boundaries; indels included)
     (1) doublets, total / within-word / cross-word.  (2) within-word lag-5 coincidence vs 1/29 (z).
  5. Variant 'J': U+16C2 read as J (U+16C4), the convention used by henkman, rne and mortlach at J positions.
  6. Boundary-convention variants of the reference itself (which separators count as word breaks).
"""
import sys
import os
import math
import difflib
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'lp'))
import transcriptions as T  # noqa: E402

NP = 55                    # loader pages 0-54
P0 = 1.0 / 29.0            # random coincidence rate from the task
SYM_J = 11                 # J = U+16C4 in lpdata.RUNES
SYM_E2 = 29                # U+16C2 in transcriptions.SYM

WS_K = set('-.&$§')                                   # loader: word increments
WS_ALDE = {'①', '③', '④', '⑩', '⑬', '-', '.', '&', '$'}  # ① ③ ④ ⑩ ⑬ are word-start marks
WS_BULLET = {'•'}                                # • word break (henkman, rne, scream314, PAGES.json key)
WS_RNE = {'•', '.', ':', ','}
WS_C1 = {'•', '.', ':'}                       # c1cada: bullet = word break (U+2022)
WS_L = {'-'}                                          # mortlach: one token per word start

# name: (description, separator set or None for rune-only, paged?)
FAMILIES = {
    'K':   ('krisyotam_runes.txt (loader source)', WS_K, True),
    'A':   ('aldegonde data/page0-56.txt', WS_ALDE, True),
    'M':   ('aldegonde data/liber-primus__transcription--master.txt (rtkd master)', WS_ALDE, True),
    'MT':  ('Taiiwo liber_primus.txt (rtkd master, krisyotam separators)', WS_K, True),
    'M2':  ('iddqd master_218ed88.txt', WS_K, True),
    'AU':  ('aautcsh data/liber', WS_K, True),
    'S':   ('scream314_lp.md (= aautcsh translation.txt)', WS_BULLET, False),
    'L':   ('mortlach lp_section_data.py', WS_L, False),
    'S2':  ('trans_scream314.txt', None, True),
    'H':   ('henkman liberprimus.txt', WS_BULLET, True),
    'R':   ('transcriptions.rne', WS_RNE, True),
    'C':   ('trans_cicadasolvers.txt (= trans_r4nd0mD3v3l0p3r)', None, True),
    'J':   ('dataset/liber_primus.json', None, True),
    'P':   ('PAGES.json', None, True),
    'V':   ('vision_results.json (AI re-reading)', None, True),
    'T':   ('template_transcription.txt (low confidence)', None, True),
    'CL':  ('stones/classifier_transcription.txt', None, False),
    'RN':  ('thomasandfriends runes4012 (partial: pages 40-42 only)', WS_BULLET, True),
    'C1B': ('c1cada versions/page.27-32_fe9b225.txt (partial: pages 27-32)', WS_C1, 'partial'),
    'C1A': ('c1cada versions/page.27-32_f75c1de.txt (partial, other segmentation)', WS_C1, 'partial'),
    'IN':  ('solver testResources/input.txt (partial: loader page 0)', WS_K, 'partial'),
    'C1B': ('c1cada versions/page.27-32_fe9b225.txt (partial: pages 27-32)', WS_C1, 'partial'),
    'C1A': ('c1cada versions/page.27-32_f75c1de.txt (partial, other segmentation)', WS_C1, 'partial'),
    'IN':  ('solver testResources/input.txt (partial: loader page 0)', WS_K, 'partial'),
}
FLAT_LOAD = {'S', 'L', 'CL'}


# ---------------------------------------------------------------- reference
def loader_reference():
    import lpdata
    U, C, sha = lpdata.unsolved()
    assert sha == '023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585', sha
    pages = [[(i, '') for i in p['idx']] for p in U]
    W = [w for p in U for w in p['word']]
    wb = [True] + [W[i] != W[i - 1] for i in range(1, len(W))]
    flat = [i for p in U for i in p['idx']]
    return pages, flat, wb


# ---------------------------------------------------------------- family streams
def normalise_tokens(toks):
    return [SYM_J if (isinstance(t, int) and t == SYM_E2) else t for t in toks]


def pages_from_units(units):
    """Units (label, tokens) -> pages of (idx, pre); separators carry across unit boundaries as in the loader."""
    pages, pending = [], ''
    for label, toks in units:
        page = []
        for t in toks:
            if isinstance(t, int):
                page.append((t, pending))
                pending = ''
            else:
                pending += t
        pages.append((label, page))
    return pages


def page_score(a, b):
    return sum(bl.size for bl in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks())


def map_paged(name, units, kpages):
    """Place a paged family's units on loader pages 0-54. Returns (pages, description)."""
    if name in ('J', 'P', 'RN'):
        out = {}
        for lab, pg in pages_from_units(units):
            if pg:
                out[int(lab)] = pg
        return [out.get(i, []) for i in range(NP)], 'label = krisyotam segment index'
    if name in ('V', 'T'):
        out = {}
        for lab, pg in pages_from_units(units):
            lp = int(lab)
            if lp <= 49:
                out[lp] = pg
            elif lp >= 51:
                out[lp - 1] = pg
        return [out.get(i, []) for i in range(NP)], 'label = LP2 page (50 runeless, 51+ shifted)'
    # separators are carried across runeless units (as the loader would); runeless pages are then dropped
    pages = [(lab, pg) for lab, pg in pages_from_units(units) if pg]
    best, bo = -1, 0
    for o in range(0, max(1, len(pages) - NP + 1)):
        sc = sum(page_score([i for i, _ in kpages[p]], [i for i, _ in pages[o + p][1]])
                 for p in range(NP) if o + p < len(pages))
        if sc > best:
            best, bo = sc, o
    return [pg for _, pg in pages[bo:bo + NP]], 'offset %d of %d non-empty units (%d runes matched)' % (bo, len(pages), best)


def flat_stream(name, norm):
    """(idx, pre) list for a flat-only family (whole-book stream)."""
    if name == 'L':
        units = T.load_L_words()
    else:
        units = T.load(name)
    if norm:
        units = [(lab, normalise_tokens(toks)) for lab, toks in units]
    out = []
    for _, pg in pages_from_units(units):
        out.extend(pg)
    return out


def flat_region(F, Kflat):
    """Find the loader-pages-0-54 region of a flat stream by anchoring on the first 80 reference runes, then
    trim to the aligned span so that trailing pages 55+ are not counted as insertions."""
    K = Kflat[:80]
    fi = [i for i, _ in F]
    best, bs = -1, 0
    limit = min(len(fi) - 80, 4000)
    for s in range(0, max(1, limit)):
        sc = page_score(K, fi[s:s + 80])
        if sc > best:
            best, bs = sc, s
            if sc == 80:
                break
    region = F[bs:bs + len(Kflat) + 200]
    ops = difflib.SequenceMatcher(None, Kflat, [i for i, _ in region], autojunk=False).get_opcodes()
    cut = 0
    for tag, i1, i2, j1, j2 in ops:
        if tag != 'insert':
            cut = j2
    return region[:cut], bs


# ---------------------------------------------------------------- statistics
def word_flags(pre_list, ws):
    wb = [any(ch in ws for ch in pre) for pre in pre_list]
    if wb:
        wb[0] = True
    return wb


def stats(C, wb):
    N = len(C)
    dbl = within = cross = 0
    for i in range(N - 1):
        if C[i] == C[i + 1]:
            dbl += 1
            if wb[i + 1]:
                cross += 1
            else:
                within += 1
    W, w = [], -1
    for i in range(N):
        if wb[i]:
            w += 1
        W.append(w)
    hits = n = 0
    for a in range(N - 5):
        if W[a] == W[a + 5]:
            n += 1
            if C[a] == C[a + 5]:
                hits += 1
    rate = hits / n if n else float('nan')
    z = (rate - P0) / math.sqrt(P0 * (1 - P0) / n) if n else float('nan')
    return dict(N=N, doublets=dbl, within=within, cross=cross, lag5_hits=hits, lag5_n=n, lag5_rate=rate, z=z)


def fmt(s):
    return ('N=%d | doublets %d (within %d, cross %d) | lag5 %d/%d = %.2f%% z=%+.2f' %
            (s['N'], s['doublets'], s['within'], s['cross'], s['lag5_hits'], s['lag5_n'], 100 * s['lag5_rate'], s['z']))


# ---------------------------------------------------------------- alignment and variants
def segment_ops(Kc, Fr, kpages_bounds, fpages_bounds):
    """Return list of (segment_id, opcodes) with global offsets computed per segment."""
    segs = []
    for sid, ((k0, k1), (f0, f1)) in enumerate(zip(kpages_bounds, fpages_bounds)):
        ops = difflib.SequenceMatcher(None, Kc[k0:k1], Fr[f0:f1], autojunk=False).get_opcodes()
        segs.append((sid, k0, f0, ops))
    return segs


def count_ops(ops, kwb, fwb, k0, f0, F, Kc):
    c = Counter()
    for tag, i1, i2, j1, j2 in ops:
        if tag == 'equal':
            c['equal'] += i2 - i1
            if fwb is not None:
                for t in range(i2 - i1):
                    kb, fb = kwb[k0 + i1 + t], fwb[f0 + j1 + t]
                    if kb and not fb:
                        c['bnd_lacking'] += 1
                    elif fb and not kb:
                        c['bnd_extra'] += 1
        elif tag == 'replace':
            n = min(i2 - i1, j2 - j1)
            c['sub'] += n
            c['del'] += (i2 - i1) - n
            c['ins'] += (j2 - j1) - n
        elif tag == 'delete':
            c['del'] += i2 - i1
        elif tag == 'insert':
            c['ins'] += j2 - j1
    return c


def build_variants(Kc, Kw, Fi, Fw, segs):
    """Variant streams from segment alignments. Returns dict name -> stats."""
    sub_c = list(Kc)
    bnd_w = list(Kw)
    for sid, k0, f0, ops in segs:
        for tag, i1, i2, j1, j2 in ops:
            if tag == 'equal':
                if Fw is not None:
                    for t in range(i2 - i1):
                        bnd_w[k0 + i1 + t] = Fw[f0 + j1 + t]
            elif tag == 'replace':
                n = min(i2 - i1, j2 - j1)
                for t in range(n):
                    sub_c[k0 + i1 + t] = Fi[f0 + j1 + t]
                    if Fw is not None:
                        bnd_w[k0 + i1 + t] = Kw[k0 + i1 + t]
    out = {}
    out['ref'] = stats(Kc, Kw)
    out['subs'] = stats(sub_c, Kw)
    if Fw is not None:
        out['bnd'] = stats(Kc, bnd_w)
        out['own'] = stats(Fi, Fw)
    return out


def paged_bounds(kpages, fpages):
    kst, fst = [0], [0]
    for pg in kpages:
        kst.append(kst[-1] + len(pg))
    for pg in fpages:
        fst.append(fst[-1] + len(pg))
    return [(kst[p], kst[p + 1]) for p in range(NP)], [(fst[p], fst[p + 1]) for p in range(NP)]


def analyse(name, label, ws, paged, norm, kpages, Kc, Kw, kpre, rows_out):
    """Analyse one family (optionally with J normalisation). Returns dict of results.
    rows_out: list collecting per-page rows (family, page, ...) for per_page.tsv."""
    tag = name + ('+J' if norm else '')
    print('\n== %s  [%s]' % (tag, label))
    partial = False
    kb_pages = []
    s0 = 0
    for pg in kpages:
        kb_pages.append((s0, s0 + len(pg)))
        s0 += len(pg)
    if paged:
        units = T.load(name)
        if norm:
            units = [(lab, normalise_tokens(toks)) for lab, toks in units]
        fpages, info = map_paged(name, units, kpages)
        print('   placement: %s' % info)
        kb, fb = paged_bounds(kpages, fpages)
        Fi = [i for pg in fpages for i, _ in pg]
        Fp = [p for pg in fpages for _, p in pg]
        Fw = word_flags(Fp, ws) if ws is not None else None
        page_of_k = [p for p, (a, b) in enumerate(kb_pages) for _ in range(b - a)]
        segs = segment_ops(Kc, Fi, kb, fb)
        # pages the file does not contain are left as reference symbols (not counted as deletions)
        covered = [len(pg) > 0 for pg in fpages]
        segs = [s for s in segs if covered[s[0]]]
        ncov = sum(covered)
        partial = ncov < NP
        cov_ref = sum(len(kpages[p]) for p in range(NP) if covered[p])
        if partial:
            print('   coverage: %d of %d reference pages have runes in this file; other pages keep reference symbols'
                  % (ncov, NP))
    else:
        F_all = flat_stream(name, norm)
        F_all, bs = flat_region(F_all, Kc)
        Fi = [i for i, _ in F_all]
        Fp = [p for _, p in F_all]
        Fw = word_flags(Fp, ws) if ws is not None else None
        print('   placement: flat region starting at flat index %d, %d runes' % (bs, len(Fi)))
        kb = [(0, len(Kc))]
        fb = [(0, len(Fi))]
        cov_ref = len(Kc)
        segs = segment_ops(Kc, Fi, kb, fb)
        page_of_k = [p for p, (a, b) in enumerate(kb_pages) for _ in range(b - a)]
    per_page = {}
    tot = Counter()
    bdiffs = []
    for sid, k0, f0, ops in segs:
        c = count_ops(ops, Kw, Fw, k0, f0, Fi, Kc)
        tot.update(c)
        for tag_, i1, i2, j1, j2 in ops:
            if tag_ == 'equal' and Fw is not None:
                for t in range(i2 - i1):
                    kg, fg = k0 + i1 + t, f0 + j1 + t
                    if Kw[kg] != Fw[fg]:
                        bdiffs.append((page_of_k[kg], kg - kb_pages[page_of_k[kg]][0], kpre[kg], Fp[fg], Kw[kg], Fw[fg]))
        # per-page counts, attributed to the reference page of the aligned reference position
        for tag_, i1, i2, j1, j2 in ops:
            if tag_ == 'replace':
                n = min(i2 - i1, j2 - j1)
                for t in range(n):
                    per_page.setdefault(page_of_k[k0 + i1 + t], Counter())['sub'] += 1
                for t in range(n, i2 - i1):
                    per_page.setdefault(page_of_k[k0 + i1 + t], Counter())['del'] += 1
                for t in range(n, j2 - j1):
                    per_page.setdefault(page_of_k[min(k0 + i1 + t, len(Kc) - 1)], Counter())['ins'] += 1
            elif tag_ == 'delete':
                for t in range(i2 - i1):
                    per_page.setdefault(page_of_k[k0 + i1 + t], Counter())['del'] += 1
            elif tag_ == 'insert':
                per_page.setdefault(page_of_k[min(k0 + i1, len(Kc) - 1)], Counter())['ins'] += j2 - j1
    # identity
    eq = tot.get('equal', 0)
    print('   runes placed = %d (reference %d); identical reference positions %d of %d covered (%.2f%%); substitutions %d, insertions %d, deletions %d' %
          (len(Fi), len(Kc), eq, cov_ref, 100.0 * eq / cov_ref, tot['sub'], tot['ins'], tot['del']))
    if Fw is not None:
        print('   word boundaries on aligned runes: family lacks a reference word start %d; family has an extra one %d' %
              (tot['bnd_lacking'], tot['bnd_extra']))
        for pgid, kpos, kp, fp, kb_, fb_ in bdiffs[:12]:
            print('      boundary: ref p%02d+%d pre=%s  family pre=%s  ref_wb=%d fam_wb=%d' %
                  (pgid, kpos, ascii_pre(kp), ascii_pre(fp), kb_, fb_))
        if len(bdiffs) > 12:
            print('      ... %d boundary disagreements in total' % len(bdiffs))
    variants = build_variants(Kc, Kw, Fi, Fw, segs)
    for k in ('ref', 'subs', 'bnd', 'own'):
        if k == 'own' and partial:
            print('   stat[own ] not computed: partial coverage')
            continue
        if k in variants:
            print('   stat[%-4s] %s' % (k, fmt(variants[k])))
    for pgid in sorted(per_page):
        r = per_page[pgid]
        if any(r.values()) or (Fw is not None and False):
            rows_out.append((tag, pgid, kb_pages[pgid][1] - kb_pages[pgid][0] if pgid < NP else 0,
                             r.get('sub', 0), r.get('ins', 0), r.get('del', 0)))
    return dict(tag=tag, tot=tot, variants=variants, n=len(Fi), has_bnd=Fw is not None,
                identical=eq, bdiffs=bdiffs)


def ascii_pre(s):
    return ''.join(ch if ord(ch) < 128 else 'u%04x' % ord(ch) for ch in s) or '-none-'


# ---------------------------------------------------------------- K boundary conventions (reference runes only)
def boundary_conventions(Kc, Kpre):
    out = {}
    conv = {
        'loader: - . & $ (word starts)': set('-.&$'),
        'no sentence breaks: - & $': set('-&$'),
        'hyphen only: -': set('-'),
        'loader + line breaks /': set('-.&$/'),
    }
    for label, ws in conv.items():
        wb = [any(ch in ws for ch in pre) for pre in Kpre]
        wb[0] = True
        out[label] = stats(Kc, wb)
    return out


def partial_report(name, label, ws, Kc, Kw):
    """Partial single-file transcriptions: locate the file's reference window (anchor on the first 80 runes,
    J relabelled), align the window, report identity and boundary agreement. No statistics: coverage is partial."""
    print('\n== %s  [%s]' % (name, label))
    F = flat_stream(name, False)
    Fi = [i for i, _ in F]
    Fp = [p for _, p in F]
    Fw = word_flags(Fp, ws)
    Fn = [SYM_J if i == SYM_E2 else i for i in Fi]
    s = max(range(0, len(Kc) - 80), key=lambda k: page_score(Kc[k:k + 80], Fn[:80]))
    Kwin = Kc[s:s + len(Fn)]
    Kwb = Kw[s:s + len(Fn)]
    ops = difflib.SequenceMatcher(None, Kwin, Fn, autojunk=False).get_opcodes()
    c = count_ops(ops, Kwb, Fw, 0, 0, Fn, Kwin)
    print('   reference window starts at reference rune %d (%d runes); family runes %d (U+16C2 read as J: %d)' %
          (s, len(Fn), len(Fi), Fi.count(SYM_E2)))
    print('   identical %d of %d (%.2f%%); substitutions %d, insertions %d, deletions %d; boundaries lacking %d, extra %d' %
          (c.get('equal', 0), len(Fn), 100.0 * c.get('equal', 0) / len(Fn), c.get('sub', 0), c.get('ins', 0), c.get('del', 0),
           c.get('bnd_lacking', 0), c.get('bnd_extra', 0)))
    return dict(identical=c.get('equal', 0), n=len(Fn), sub=c.get('sub', 0), ins=c.get('ins', 0), dele=c.get('del', 0),
                lack=c.get('bnd_lacking', 0), extra=c.get('bnd_extra', 0))


def main(argv):
    sys.stdout.reconfigure(encoding='utf-8')
    kpages, Kc, Kw = loader_reference()
    print('reference (lpdata): pages 0-54 = %d runes' % len(Kc))
    print('   %s' % fmt(stats(Kc, Kw)))
    # K's own separators, for boundary-convention variants
    kraw, _ = map_paged(
        'K', T.load('K'), kpages)
    Kpre = [p for pg in kraw for _, p in pg]
    print('\n== reference boundary conventions (reference runes, only the set of separators that count changes)')
    for label, s in boundary_conventions(Kc, Kpre).items():
        print('   %-34s %s' % (label, fmt(s)))
    names = argv or list(FAMILIES.keys())
    results = {}
    rows = []
    for nm in names:
        if nm.endswith('+J'):
            base = nm[:-2]
            norm = True
        else:
            base = nm
            norm = False
        label, ws, paged = FAMILIES[base]
        if paged == 'partial':
            results[nm] = partial_report(base, label, ws, Kc, Kw)
            continue
        results[nm] = analyse(base, label, ws, paged, norm, kpages, Kc, Kw, Kpre, rows)
    with open(os.path.join(HERE, 'per_page.tsv'), 'w', encoding='utf-8') as f:
        f.write('family\treference_page\treference_runes\tsubstitutions\tinsertions\tdeletions\n')
        for row in rows:
            f.write('%s\t%d\t%d\t%d\t%d\t%d\n' % row)
    return results


def lineage_scan():
    """Every text file under dl/ with >= 100 runic characters (U+16A0-U+16FF), grouped by the sha256 of its
    runic-character sequence (line breaks, separators and prose removed). Equal sha = same rune stream."""
    import hashlib
    rows = []
    for root, dirs, files in os.walk(os.path.join(T.ROOT, 'dl')):
        if '.git' in root.split(os.sep):
            continue
        for f in files:
            p = os.path.join(root, f)
            try:
                txt = open(p, 'rb').read().decode('utf-8')
            except Exception:
                continue
            rn = ''.join(c for c in txt if 0x16A0 <= ord(c) <= 0x16FF)
            if len(rn) >= 100:
                n16c2 = rn.count('ᛂ')
                h = hashlib.sha256(rn.encode('utf-8')).hexdigest()[:12]
                rows.append((h, len(rn), n16c2, os.path.relpath(p, T.ROOT).replace(os.sep, '/')))
    rows.sort(key=lambda r: (-r[1], r[0], r[3]))
    print('runic-stream sha12, runic count, U+16C2 count, file  (dl/ scan)')
    for h, n, n2, path in rows:
        print('%s %6d %4d  %s' % (h, n, n2, path))
    groups = Counter(r[0] for r in rows)
    print('\n%d files, %d distinct runic streams' % (len(rows), len(groups)))


def corruption_curve(reps=60):
    """Control: corrupt a fraction r of the reference runes (K boundaries kept) with a different symbol drawn
    uniformly from the other 28 symbols; report doublets and lag-5 z over repeated draws."""
    import random
    import statistics
    sys.stdout.reconfigure(encoding='utf-8')
    _, Kc, Kw = loader_reference()
    print('corruption control (random replacement of a fraction r of the reference runes; boundaries = reference)')
    print('   r      doublets (mean, sd)    lag5 rate (mean)   z (mean, sd)    z>2 in %d draws' % reps)
    for r in (0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.35, 1.0):
        rng = random.Random(12345)
        dbl, zs, rates = [], [], []
        for _ in range(reps):
            C = list(Kc)
            for i in range(len(C)):
                if rng.random() < r:
                    C[i] = rng.choice([s for s in range(29) if s != C[i]] + [SYM_E2])
            s = stats(C, Kw)
            dbl.append(s['doublets'])
            zs.append(s['z'])
            rates.append(s['lag5_rate'])
        print('   %4.2f   %8.1f (%5.1f)        %6.2f%%          %+.2f (%.2f)     %d' %
              (r, statistics.mean(dbl), statistics.pstdev(dbl), 100 * statistics.mean(rates),
               statistics.mean(zs), statistics.pstdev(zs), sum(1 for z in zs if z > 2)))


if __name__ == '__main__':
    if sys.argv[1:] == ['lineage']:
        sys.stdout.reconfigure(encoding='utf-8')
        lineage_scan()
    elif sys.argv[1:] == ['corruption']:
        corruption_curve()
    else:
        main(sys.argv[1:])
