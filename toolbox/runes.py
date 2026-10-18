"""Shared rune helpers: the alphabet, English -> runes, and an English rune stream with word ids.

    import sys; sys.path.insert(0, "toolbox"); import runes
    runes.eng2runes("THE PRIMES ARE SACRED")      # -> list of indices 0..28
    R, W = runes.english_stream(12956)           # runes + word ids from a long English text

eng2runes follows Gematria Primus transliteration (as agents/laneN_cribdrag/common.py): digraphs TH EO NG OE AE IA/IO EA,
ING -> NG, QU -> CW, K/Q -> C, V -> U, Z -> S.
"""
import re
import sys

sys.path.insert(0, "lp")
import lpdata  # noqa: E402

TR = lpdata.TR
RUNES = lpdata.RUNES
DIG = {"TH": 2, "EO": 12, "NG": 21, "OE": 22, "AE": 25, "IA": 27, "IO": 27, "EA": 28}
SING = {"F": 0, "U": 1, "V": 1, "O": 3, "R": 4, "C": 5, "K": 5, "Q": 5, "G": 6, "W": 7, "H": 8, "N": 9, "I": 10,
        "J": 11, "P": 13, "X": 14, "S": 15, "Z": 15, "T": 16, "B": 17, "E": 18, "M": 19, "L": 20, "D": 23, "A": 24,
        "Y": 26}
DEFAULT_TEXT = "dl/dukotah/liber-primus/data/keys/armada18/melville_moby_dick.txt"


def eng2runes(s, ing=True):
    s = re.sub("[^A-Z]", "", s.upper()).replace("QU", "CW")
    if ing:
        s = s.replace("ING", "#")
    out, i = [], 0
    while i < len(s):
        if s[i] == "#":
            out.append(21)
            i += 1
            continue
        d = s[i:i + 2]
        if d in DIG:
            out.append(DIG[d])
            i += 2
        else:
            out.append(SING[s[i]])
            i += 1
    return out


def tr(idx):
    return "".join(TR[i] for i in idx)


def english_stream(n, path=DEFAULT_TEXT, skip_chars=20000):
    """First n runes of an English text (after skip_chars, past any header), with a word id per rune."""
    text = open(path, encoding="utf-8", errors="replace").read()[skip_chars:]
    R, W, w = [], [], 0
    for word in re.findall(r"[A-Za-z]+", text):
        r = eng2runes(word)
        if not r:
            continue
        R.extend(r)
        W.extend([w] * len(r))
        w += 1
        if len(R) >= n:
            break
    return R[:n], W[:n]
