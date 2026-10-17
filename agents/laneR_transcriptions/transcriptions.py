"""Loaders for the Liber Primus rune transcriptions found under dl/.

Every loader returns a flat, ordered list of "units" (pages or lines as the file defines them), each unit a
list of tokens: an int is a rune (index into SYM), a str is a separator/other character that appeared between
runes. Units with no runes are dropped. compare.py maps the surviving units onto the loader's pages 0-54.
"""
import os
import re
import json

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"   # identical to lp/lpdata.py (29 runes)
EXTRA = "ᛂ"                                        # RUNIC LETTER E: used by henkman/rne, absent from lpdata
SYM = RUNES + EXTRA                                      # index 29 = U+16C2
CP2I = {c: i for i, c in enumerate(SYM)}

PATHS = {
    'K':      'dl/dukotah/liber-primus/data/krisyotam_runes.txt',
    'A':      'dl/aldegonde_clone/data/page0-56.txt',
    'M':      'dl/aldegonde_clone/data/liber-primus__transcription--master.txt',
    'MT':     'dl/dukotah/corpus/B-liber-primus/fetched/Taiiwo__cicada/cicada/liber_primus.txt',
    'M2':     'dl/dukotah/corpus/E-tooling/iddqd_versions/master_218ed88.txt',
    'AU':     'dl/dukotah/corpus/B-liber-primus/fetched/aautcsh__idkfa/data/liber',
    'S':      'dl/dukotah/liber-primus/data/scream314_lp.md',
    'S2':     'dl/dukotah/liber-primus/analysis/foundation/trans_scream314.txt',
    'H':      'dl/dukotah/corpus/B-liber-primus/fetched/henkman__liberprimus/liberprimus.txt',
    'R':      'dl/dukotah/corpus/B-liber-primus/fetched/transcriptions.rne',
    'C':      'dl/dukotah/liber-primus/analysis/foundation/trans_cicadasolvers.txt',
    'J':      'dl/dukotah/liber-primus/dataset/liber_primus.json',
    'V':      'dl/dukotah/liber-primus/analysis/vision/vision_results.json',
    'CL':     'dl/dukotah/liber-primus/analysis/stones/classifier_transcription.txt',
    'T':      'dl/dukotah/liber-primus/analysis/structure/template_transcription.txt',
    'RN':     'dl/dukotah/corpus/B-liber-primus/fetched/thomasandfriends__Cicada3301Runes/data/runes4012',
    'C1B':    'dl/dukotah/corpus/E-tooling/c1cada_versions/page.27-32_fe9b225.txt',
    'C1A':    'dl/dukotah/corpus/E-tooling/c1cada_versions/page.27-32_f75c1de.txt',
    'IN':     'dl/dukotah/corpus/B-liber-primus/fetched/r4nd0mD3v3l0p3r__LiberPrimusSolver/testResources/input.txt',
    'P':      'dl/dukotah/corpus/B-liber-primus/PAGES.json',
    'L':      'dl/aldegonde_clone/lp_section_data.py',
}


def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return f.read()


def tokenize(s):
    """Runes -> int index into SYM; other characters -> str separators.

    A maximal run of non-rune text that contains ASCII letters is treated as junk (e.g. the letter-grid art
    block that precedes runeless page 50 in dl/aldegonde_clone/data/page0-56.txt) and dropped entirely, so its
    punctuation is not read as word separators.
    """
    out = []
    run = []

    def flush():
        if run:
            txt = ''.join(run)
            if not re.search(r'[A-Za-z]', txt):
                out.extend(c for c in txt if c not in ' \t\r\n0123456789')
            run.clear()

    for ch in s:
        if ch in CP2I:
            flush()
            out.append(CP2I[ch])
        else:
            run.append(ch)
    flush()
    return out


def split_pct(text):
    return [tokenize(p) for p in text.split('%')]


def split_lines(text):
    return [tokenize(l) for l in text.replace('\r', '').split('\n')]


def split_headers(text, header_re):
    """Split at lines matching header_re; returns list of (header_text, tokens)."""
    out = []
    matches = list(re.finditer(header_re, text, flags=re.M))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.append((m.group(0), tokenize(text[m.end():end])))
    return out


def load(name):
    """Return list of (label, tokens) units in file order (labels are page/line labels where the file has them)."""
    t = read(PATHS[name])
    if name in ('K', 'A', 'M', 'MT', 'M2', 'AU'):
        return [(None, u) for u in split_pct(t)]
    if name in ('S2', 'C', 'R', 'K_rune'):
        return [(None, u) for u in split_lines(t)]
    if name == 'H':
        return split_headers(t, r'^-{5} \d+ -{5}$')
    if name == 'S':
        return split_headers(t, r'^## .*$')
    if name == 'J':
        j = json.loads(t)
        return [(p['page'], tokenize(p['runes'])) for p in j['pages']]
    if name == 'V':
        j = json.loads(t)
        return [(p['page'], tokenize(p['runes'])) for p in j]
    if name == 'P':
        j = json.loads(t)
        return [(p['segment_index'], tokenize(p['runes'])) for p in j['pages']]
    if name == 'CL':
        out = []
        ms = list(re.finditer(r'^% PAGE-IMAGE p(\d+) \(krisyotam pages \[([^\]]*)\]\)$', t, flags=re.M))
        for i, m in enumerate(ms):
            end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
            out.append((m.group(2), tokenize(t[m.end():end])))
        return out
    if name == 'T':
        return [(int(h.strip('% p')), u) for h, u in split_headers(t, r'^% p\d+$')]
    if name in ('C1A', 'C1B', 'IN'):
        return [(None, tokenize(t))]
    if name == 'RN':
        return [(int(re.search(r'\d+', h).group(0)), u)
                for h, u in split_headers(t, r'^\|\|page \d+\(Confirmed\)$')]
    raise KeyError(name)


def load_L_words():
    """mortlach/lp-decrypter (aldegonde_clone/lp_section_data.py): lp_sections_by_red_runes is 17 sections of
    word strings covering the full 13,136-rune text. Each string is one word, so every word start is a word break.
    Returns a list of tokens (one unit per section) with '-' (word break) emitted before each word."""
    import ast
    src = read(PATHS['L'])
    tree = ast.parse(src)
    value = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', None) == 'lp_sections_by_red_runes':
            value = ast.literal_eval(node.value)
    units = []
    for sec in value:
        toks = []
        for word in sec:
            toks.append('-')
            toks.extend(tokenize(word))
        units.append((None, toks))
    return units

