"""Lane AB cross-check: read master-v2 with RDP's own parser (rdp.data.liber_primus.lp_transcript.LPTranscript, in
the port) instead of diff_v2.py's tokenizer, and recount the pin statistics with fresh code (no lane R functions).

    dl/rdp_venv/Scripts/python.exe -I agents/laneAB_rdp_port/xcheck_rdp_parser.py > agents/laneAB_rdp_port/out_xcheck_rdp_parser.txt

RDP's parser emits every non-delimiter character as a glyph (numerals included) and assigns each glyph a word id.
Runes are kept with their word ids; numerals are dropped (RDP's rune-only extraction does the same). The LP2 stream is
RDP pages 15-64 and 66-70 of the parser's page list (main-transcript IDs; 65 is the runeless page).
"""
import hashlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'dl', 'rdp_port', 'src'))
sys.path.insert(0, os.path.join(ROOT, 'lp'))
os.chdir(ROOT)

from rdp.data.liber_primus.lp_transcript import LPTranscript  # noqa: E402
import lpdata  # noqa: E402

V2 = 'dl/rdp_port/assets/liber_primus/liber-primus__transcription--master-v2.txt'
PIN = '023312066df471005264b9cbe7997cb77d2a9a6a2dc9b3316d22674023af1585'


def lag5(C, W):
    hits = n = 0
    for a in range(len(C) - 5):
        if W[a] == W[a + 5]:
            n += 1
            hits += C[a] == C[a + 5]
    p = 1 / 29
    return hits, n, (hits / n - p) / math.sqrt(p * (1 - p) / n)


def doublets(C, W):
    d = [i for i in range(len(C) - 1) if C[i] == C[i + 1]]
    return len(d), sum(1 for i in d if W[i] == W[i + 1]), sum(1 for i in d if W[i] != W[i + 1])


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    doc = LPTranscript.from_file(V2)
    print(doc.summary())
    pages = list(range(15, 65)) + list(range(66, 71))
    C, W, per_page = [], [], []
    for pid in pages:
        pr = doc.pages[pid]
        n0 = len(C)
        for g in range(pr.g_start, pr.g_end):
            ch = doc.glyphs[g]
            if ch in lpdata.R2I:
                C.append(lpdata.R2I[ch])
                W.append(doc._glyph_to_word[g])
            elif ch == 'ᛂ':
                C.append(11)
                W.append(doc._glyph_to_word[g])
        per_page.append(len(C) - n0)
    sha = hashlib.sha256(','.join(map(str, C)).encode()).hexdigest()
    print('LP2 runes from RDP pages 15-64, 66-70: %d; comma-joined sha %s; equals pin: %s' % (len(C), sha, sha == PIN))
    U, K, _ = lpdata.unsolved()
    print('per-page rune counts equal the pin: %s' % (per_page == [len(p['idx']) for p in U]))
    KW = [w for p in U for w in p['word']]
    print('pin   : doublets %d (within %d, cross %d); lag5 %d/%d z %+.2f' % (doublets(K, KW) + lag5(K, KW)))
    print('RDP v2: doublets %d (within %d, cross %d); lag5 %d/%d z %+.2f' % (doublets(C, W) + lag5(C, W)))
    ks = [i for i in range(1, len(K)) if KW[i] != KW[i - 1]]
    vs = [i for i in range(1, len(C)) if W[i] != W[i - 1]]
    print('word starts: pin %d, RDP parser %d; only in pin %s; only in RDP %s' %
          (len(ks), len(vs), sorted(set(ks) - set(vs)), sorted(set(vs) - set(ks))))


if __name__ == '__main__':
    main()
